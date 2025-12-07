"""
RAG (Retrieval-Augmented Generation) Engine

Uses ChromaDB for vector storage and semantic search to find
relevant context for answering student questions.

Pipeline Architecture:
1. Intent Classification (fast model) -> Route query
2. Context Resolution -> Resolve references
3. RAG Retrieval -> Find relevant documents
4. Confidence Scoring -> Assess response quality
5. Response Generation (main model) -> Generate answer
6. Human Handoff (if needed) -> Escalate to advisor
"""
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

import chromadb

from hal.config import Config, LLMProvider
from hal.models import Course, Advisor, Policy, Deadline, db
from hal.services.llm_providers import get_llm_provider, get_embeddings_provider, LLMResponse


@dataclass
class RetrievalResult:
    """Result from RAG retrieval"""
    content: str
    source: str
    score: float
    metadata: Dict


@dataclass
class PipelineResult:
    """Complete result from the RAG pipeline"""
    response: str
    confidence_score: float
    confidence_level: str
    intent: str
    sources: List[Dict]
    model: str
    provider: str
    escalate_to_human: bool
    escalation_reason: Optional[str]
    escalation_message: Optional[str]
    context_resolved: bool
    original_query: str
    resolved_query: str


class RAGEngine:
    """
    RAG engine for the HAL Advisor Bot.

    Handles:
    - Document indexing from database
    - Semantic search using ChromaDB
    - Response generation using configured LLM
    """

    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_directory = persist_directory or Config.CHROMA_PERSIST_DIR

        # Initialize ChromaDB with new PersistentClient API
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_directory
        )

        self.collection_name = Config.CHROMA_COLLECTION_NAME
        self._collection = None
        self._embeddings = None
        self._llm_provider = None

    @property
    def collection(self):
        """Lazy-load the ChromaDB collection"""
        if self._collection is None:
            self._collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "HAL Advisor knowledge base"}
            )
        return self._collection

    @property
    def embeddings(self):
        """Lazy-load the embeddings provider"""
        if self._embeddings is None:
            self._embeddings = get_embeddings_provider()
        return self._embeddings

    @property
    def llm(self):
        """Lazy-load the LLM provider"""
        if self._llm_provider is None:
            self._llm_provider = get_llm_provider()
        return self._llm_provider

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text string"""
        return self.embeddings.embed_query(text)

    def index_all_documents(self, app=None):
        """
        Index all documents from the database into ChromaDB.

        Should be called after data migration or when updating the index.
        """
        if app:
            with app.app_context():
                self._do_index()
        else:
            self._do_index()

    def _do_index(self):
        """Internal method to perform indexing"""
        documents = []
        metadatas = []
        ids = []

        # Index courses
        for course in Course.query.all():
            doc = course.to_document()
            documents.append(doc)
            metadatas.append({
                "type": "course",
                "code": course.code,
                "name": course.name
            })
            ids.append(f"course_{course.id}")

        # Index advisors
        for advisor in Advisor.query.all():
            doc = advisor.to_document()
            documents.append(doc)
            metadatas.append({
                "type": "advisor",
                "name": advisor.name,
                "range": f"{advisor.last_name_start}-{advisor.last_name_end}"
            })
            ids.append(f"advisor_{advisor.id}")

        # Index policies
        for policy in Policy.query.all():
            doc = policy.to_document()
            documents.append(doc)
            metadatas.append({
                "type": "policy",
                "category": policy.category,
            })
            ids.append(f"policy_{policy.id}")

        # Index deadlines
        for deadline in Deadline.query.all():
            doc = deadline.to_document()
            documents.append(doc)
            metadatas.append({
                "type": "deadline",
                "deadline_type": deadline.deadline_type,
                "semester": deadline.semester
            })
            ids.append(f"deadline_{deadline.id}")

        if documents:
            # Clear existing collection and re-add
            try:
                self.chroma_client.delete_collection(self.collection_name)
            except Exception:
                pass

            self._collection = None  # Reset collection reference
            collection = self.collection

            # Get embeddings for all documents
            embeddings = [self._get_embedding(doc) for doc in documents]

            # Add to collection
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

            print(f"Indexed {len(documents)} documents into ChromaDB")

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_type: Optional[str] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: The user's question
            top_k: Number of results to return (default from config)
            filter_type: Optional filter by document type (course, advisor, policy, deadline)

        Returns:
            List of RetrievalResult objects
        """
        top_k = top_k or Config.RAG_TOP_K

        # Get query embedding
        query_embedding = self._get_embedding(query)

        # Build where filter if type specified
        where_filter = None
        if filter_type:
            where_filter = {"type": filter_type}

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        # Convert to RetrievalResult objects
        retrieval_results = []
        if results and results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                # Convert distance to similarity score (ChromaDB uses L2 distance)
                # Lower distance = higher similarity
                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1 / (1 + distance)  # Convert to 0-1 similarity

                metadata = results["metadatas"][0][i] if results["metadatas"] else {}

                retrieval_results.append(RetrievalResult(
                    content=doc,
                    source=metadata.get("type", "unknown"),
                    score=score,
                    metadata=metadata
                ))

        return retrieval_results

    def generate_response(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
        filter_type: Optional[str] = None,
        context_summary: Optional[str] = None
    ) -> Tuple[LLMResponse, List[RetrievalResult]]:
        """
        Generate a response using RAG.

        Args:
            query: The user's question
            conversation_history: Previous conversation messages
            filter_type: Optional filter for document retrieval
            context_summary: Optional context summary to include

        Returns:
            Tuple of (LLMResponse, list of retrieved documents)
        """
        # Retrieve relevant context
        retrieved_docs = self.retrieve(query, filter_type=filter_type)

        # Build context string
        if retrieved_docs:
            context_parts = []
            for i, doc in enumerate(retrieved_docs, 1):
                context_parts.append(f"[Source {i} - {doc.source}]\n{doc.content}")
            context = "\n\n".join(context_parts)
        else:
            context = "No relevant information found in the knowledge base."

        # Add context summary if provided
        if context_summary:
            context = f"[Conversation Context: {context_summary}]\n\n{context}"

        # Generate response
        response = self.llm.generate(
            query=query,
            context=context,
            conversation_history=conversation_history
        )

        # Add confidence based on retrieval scores
        if retrieved_docs:
            avg_score = sum(d.score for d in retrieved_docs) / len(retrieved_docs)
            response.confidence = avg_score
        else:
            response.confidence = 0.0

        return response, retrieved_docs

    def get_confidence_message(self, confidence: float) -> Optional[str]:
        """
        Get a confidence-based message to append to responses.

        Args:
            confidence: Confidence score (0-1)

        Returns:
            Optional message about confidence level
        """
        if confidence < Config.CONFIDENCE_MEDIUM:
            return (
                "\n\n---\n"
                "I'm not very confident about this answer. "
                "Please verify with your academic advisor: "
                "https://sjsu.campus.eab.com/student/appointments/new"
            )
        elif confidence < Config.CONFIDENCE_HIGH:
            return (
                "\n\n---\n"
                "If this doesn't fully answer your question, "
                "consider booking an appointment with your advisor."
            )
        return None


# Singleton instance
_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get or create the RAG engine singleton"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine


def query_advisor(
    query: str,
    session_id: Optional[str] = None,
    conversation_history: Optional[List[Dict]] = None
) -> Dict:
    """
    Main entry point for querying the advisor bot.

    This implements the full pipeline:
    1. Intent Classification
    2. Context Resolution
    3. RAG Retrieval
    4. Confidence Scoring
    5. Response Generation
    6. Human Handoff (if needed)

    Args:
        query: User's question
        session_id: Optional session ID for conversation tracking
        conversation_history: Previous messages in the conversation

    Returns:
        Dict with response, confidence, sources, and escalation info
    """
    from hal.services.intent_classifier import classify_intent, Intent
    from hal.services.conversation_manager import get_conversation_manager
    from hal.services.confidence_scoring import get_confidence_scorer, get_human_handoff

    rag = get_rag_engine()
    conv_manager = get_conversation_manager()
    confidence_scorer = get_confidence_scorer()
    handoff = get_human_handoff()

    # Step 1: Intent Classification
    classification = classify_intent(query, conversation_history)

    # Step 2: Context Resolution
    resolved_query = query
    context_resolved = True

    if session_id and classification.requires_context:
        resolved_query, was_modified = conv_manager.resolve_references(session_id, query)
        context_resolved = was_modified or not classification.requires_context

    # Update conversation context
    if session_id:
        conv_manager.add_user_message(session_id, query)
        conv_manager.set_intent(session_id, classification.intent.value)

    # Step 3: Determine filter type based on intent
    intent_to_filter = {
        Intent.PREREQUISITE: "course",
        Intent.COURSE_INFO: "course",
        Intent.ADVISOR_LOOKUP: "advisor",
        Intent.ENROLLMENT: "policy",
        Intent.DROP_CLASS: "policy",
        Intent.REFUND: "policy",
        Intent.GRADES: "policy",
        Intent.GRADUATION: "policy",
        Intent.UNITS: "policy",
        Intent.WAITLIST: "policy",
    }
    filter_type = intent_to_filter.get(classification.intent)

    # Step 4: RAG Retrieval and Response Generation
    context_summary = None
    if session_id:
        context = conv_manager.get_context(session_id)
        context_summary = context.get_context_summary()

    response, retrieved_docs = rag.generate_response(
        query=resolved_query,
        conversation_history=conversation_history,
        filter_type=filter_type,
        context_summary=context_summary
    )

    # Update conversation with response
    if session_id:
        conv_manager.add_assistant_message(session_id, response.content)

    # Step 5: Confidence Scoring
    retrieval_results = [
        {"content": d.content, "score": d.score, "metadata": d.metadata}
        for d in retrieved_docs
    ]

    confidence = confidence_scorer.calculate_confidence(
        query=query,
        retrieval_results=retrieval_results,
        intent_confidence=classification.confidence_score,
        context_resolved=context_resolved,
        conversation_history=conversation_history
    )

    # Step 6: Determine if handoff is needed
    escalate = confidence.should_escalate or classification.escalate_to_human
    escalation_reason = None
    escalation_message = None

    if escalate:
        escalation_reason = (
            confidence.escalation_reason.value if confidence.escalation_reason
            else classification.escalation_reason
        )

        if confidence.escalation_reason:
            escalation_message = handoff.generate_handoff_message(
                confidence.escalation_reason,
                include_booking_link=True
            )

    # Build final result
    result = {
        "response": response.content,
        "confidence": confidence.overall_score,
        "confidence_level": confidence.level,
        "intent": classification.intent.value,
        "model": response.model,
        "provider": response.provider,
        "sources": [
            {
                "type": s.source,
                "score": s.score,
                "metadata": s.metadata
            }
            for s in retrieved_docs
        ],
        "escalate_to_human": escalate,
        "escalation_reason": escalation_reason,
        "escalation_message": escalation_message,
        "context_resolved": context_resolved,
        "original_query": query,
        "resolved_query": resolved_query if resolved_query != query else None,
    }

    # Add confidence message if needed (but not if escalating)
    if not escalate and confidence.level == "low":
        confidence_msg = rag.get_confidence_message(confidence.overall_score)
        if confidence_msg:
            result["response"] += confidence_msg
            result["low_confidence"] = True

    # If escalating, append or replace response with escalation message
    if escalate and escalation_message:
        if confidence.overall_score < 0.3:
            # Very low confidence - just show escalation message
            result["response"] = escalation_message
        else:
            # Some confidence - show both
            result["response"] += f"\n\n{escalation_message}"

    return result
