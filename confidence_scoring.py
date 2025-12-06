"""
Confidence Scoring & Human Handoff System for HAL Advisor Bot

Provides:
- Multi-factor confidence scoring
- Dynamic threshold calibration
- Human handoff decision logic
- Escalation tracking and analytics
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from config import Config


class EscalationReason(Enum):
    """Reasons for escalating to human advisor"""
    LOW_CONFIDENCE = "low_confidence"
    NO_RELEVANT_DOCS = "no_relevant_documents"
    PERSONAL_SITUATION = "personal_situation"
    APPEALS_EXCEPTIONS = "appeals_or_exceptions"
    ACADEMIC_STANDING = "academic_standing"
    OUT_OF_SCOPE = "out_of_scope"
    COMPLEX_QUERY = "complex_multi_part_query"
    USER_REQUESTED = "user_requested_human"
    REPEATED_LOW_RATINGS = "repeated_low_ratings"


@dataclass
class ConfidenceScore:
    """Detailed confidence scoring result"""
    overall_score: float  # 0.0 to 1.0
    retrieval_score: float  # How well docs matched the query
    relevance_score: float  # How relevant the top docs are
    intent_score: float  # How confident we are about intent
    context_score: float  # How well we understand context

    # Qualitative assessment
    level: str  # "high", "medium", "low"

    # Factors that reduced confidence
    concerns: List[str]

    # Whether to escalate
    should_escalate: bool
    escalation_reason: Optional[EscalationReason]


class ConfidenceScorer:
    """
    Multi-factor confidence scoring system.

    Combines multiple signals to determine response confidence:
    - RAG retrieval similarity scores
    - Intent classification confidence
    - Context resolution success
    - Document relevance
    """

    # Threshold configuration
    THRESHOLDS = {
        "high": 0.8,
        "medium": 0.5,
        "escalation": 0.4,
    }

    # Weights for different confidence factors
    WEIGHTS = {
        "retrieval": 0.35,
        "relevance": 0.25,
        "intent": 0.25,
        "context": 0.15,
    }

    def __init__(self):
        self.escalation_keywords = [
            "academic probation",
            "expelled",
            "dismissed",
            "appeal",
            "exception",
            "waiver",
            "petition",
            "special circumstance",
            "disability",
            "accommodation",
            "emergency",
            "urgent",
            "crisis",
            "mental health",
            "financial aid",
            "scholarship",
        ]

        self.human_request_patterns = [
            "talk to a human",
            "speak to someone",
            "real person",
            "human advisor",
            "talk to advisor",
            "contact advisor",
            "not helpful",
            "you're not helping",
            "actual help",
        ]

    def calculate_confidence(
        self,
        query: str,
        retrieval_results: List[Dict],
        intent_confidence: float,
        context_resolved: bool = True,
        conversation_history: Optional[List[Dict]] = None
    ) -> ConfidenceScore:
        """
        Calculate overall confidence score for a response.

        Args:
            query: The user's query
            retrieval_results: Results from RAG retrieval
            intent_confidence: Confidence from intent classifier
            context_resolved: Whether context references were resolved
            conversation_history: Previous messages

        Returns:
            ConfidenceScore with detailed breakdown
        """
        concerns = []

        # 1. Retrieval score - average of top document scores
        if retrieval_results:
            retrieval_score = sum(r.get("score", 0) for r in retrieval_results[:3]) / min(3, len(retrieval_results))
        else:
            retrieval_score = 0.0
            concerns.append("No relevant documents found")

        # 2. Relevance score - how relevant are the top docs
        relevance_score = self._calculate_relevance(query, retrieval_results)
        if relevance_score < 0.5:
            concerns.append("Retrieved documents may not be relevant")

        # 3. Intent score
        intent_score = intent_confidence
        if intent_score < 0.6:
            concerns.append("Unclear what type of question this is")

        # 4. Context score
        context_score = 1.0 if context_resolved else 0.5
        if not context_resolved:
            concerns.append("Unable to resolve context references")

        # Calculate weighted overall score
        overall_score = (
            self.WEIGHTS["retrieval"] * retrieval_score +
            self.WEIGHTS["relevance"] * relevance_score +
            self.WEIGHTS["intent"] * intent_score +
            self.WEIGHTS["context"] * context_score
        )

        # Determine confidence level
        if overall_score >= self.THRESHOLDS["high"]:
            level = "high"
        elif overall_score >= self.THRESHOLDS["medium"]:
            level = "medium"
        else:
            level = "low"

        # Check for escalation triggers
        should_escalate, escalation_reason = self._check_escalation(
            query,
            overall_score,
            retrieval_results,
            conversation_history
        )

        if should_escalate and not concerns:
            concerns.append(f"Escalation triggered: {escalation_reason.value if escalation_reason else 'unknown'}")

        return ConfidenceScore(
            overall_score=overall_score,
            retrieval_score=retrieval_score,
            relevance_score=relevance_score,
            intent_score=intent_score,
            context_score=context_score,
            level=level,
            concerns=concerns,
            should_escalate=should_escalate,
            escalation_reason=escalation_reason
        )

    def _calculate_relevance(self, query: str, retrieval_results: List[Dict]) -> float:
        """Calculate how relevant retrieved docs are to the query"""
        if not retrieval_results:
            return 0.0

        # Simple heuristic: check if query keywords appear in top docs
        query_words = set(query.lower().split())
        query_words -= {"what", "is", "the", "for", "a", "an", "to", "how", "do", "i", "can"}

        if not query_words:
            return 0.5  # Generic query

        relevance_scores = []
        for result in retrieval_results[:3]:
            content = result.get("content", "").lower()
            matches = sum(1 for word in query_words if word in content)
            relevance_scores.append(matches / len(query_words) if query_words else 0)

        return max(relevance_scores) if relevance_scores else 0.0

    def _check_escalation(
        self,
        query: str,
        confidence_score: float,
        retrieval_results: List[Dict],
        conversation_history: Optional[List[Dict]]
    ) -> Tuple[bool, Optional[EscalationReason]]:
        """Determine if the query should be escalated to a human"""
        query_lower = query.lower()

        # Check for explicit human request
        for pattern in self.human_request_patterns:
            if pattern in query_lower:
                return True, EscalationReason.USER_REQUESTED

        # Check for sensitive topics
        for keyword in self.escalation_keywords:
            if keyword in query_lower:
                if any(k in keyword for k in ["probation", "expelled", "dismissed"]):
                    return True, EscalationReason.ACADEMIC_STANDING
                elif any(k in keyword for k in ["appeal", "exception", "waiver", "petition"]):
                    return True, EscalationReason.APPEALS_EXCEPTIONS
                else:
                    return True, EscalationReason.PERSONAL_SITUATION

        # Check confidence threshold
        if confidence_score < self.THRESHOLDS["escalation"]:
            return True, EscalationReason.LOW_CONFIDENCE

        # Check for no relevant documents
        if not retrieval_results or all(r.get("score", 0) < 0.3 for r in retrieval_results):
            return True, EscalationReason.NO_RELEVANT_DOCS

        # Check conversation history for repeated issues
        if conversation_history and len(conversation_history) >= 6:
            # If there have been many exchanges, might be a complex issue
            return True, EscalationReason.COMPLEX_QUERY

        return False, None


class HumanHandoff:
    """
    Manages handoff to human advisors when needed.

    Provides:
    - Escalation message generation
    - Advisor routing information
    - Context packaging for handoff
    """

    ADVISOR_BOOKING_URL = "https://sjsu.campus.eab.com/student/appointments/new"

    ESCALATION_MESSAGES = {
        EscalationReason.LOW_CONFIDENCE: (
            "I'm not confident I can answer this accurately. "
            "For reliable information, please schedule an appointment with your advisor."
        ),
        EscalationReason.NO_RELEVANT_DOCS: (
            "I don't have specific information about this in my knowledge base. "
            "Your academic advisor can help you with this question."
        ),
        EscalationReason.PERSONAL_SITUATION: (
            "This seems like a personal situation that requires individual attention. "
            "An advisor can provide personalized guidance for your specific circumstances."
        ),
        EscalationReason.APPEALS_EXCEPTIONS: (
            "Questions about appeals, exceptions, or petitions require direct advisor assistance. "
            "They can guide you through the process and review your specific case."
        ),
        EscalationReason.ACADEMIC_STANDING: (
            "Questions about academic standing are sensitive and best discussed directly with an advisor. "
            "They can review your records and provide appropriate guidance."
        ),
        EscalationReason.OUT_OF_SCOPE: (
            "This question is outside my area of expertise as a CMPE/SE advisor. "
            "Please contact the appropriate department or your general academic advisor."
        ),
        EscalationReason.COMPLEX_QUERY: (
            "This seems like a complex situation that would benefit from a detailed discussion. "
            "An advisor can give you the time and attention your question deserves."
        ),
        EscalationReason.USER_REQUESTED: (
            "I understand you'd like to speak with a human advisor. "
            "You can schedule an appointment using the link below."
        ),
        EscalationReason.REPEATED_LOW_RATINGS: (
            "I apologize that my responses haven't been helpful. "
            "Please speak with an advisor who can better assist you."
        ),
    }

    def generate_handoff_message(
        self,
        reason: EscalationReason,
        include_booking_link: bool = True,
        advisor_name: Optional[str] = None
    ) -> str:
        """Generate a handoff message for the user"""
        message = self.ESCALATION_MESSAGES.get(reason, self.ESCALATION_MESSAGES[EscalationReason.LOW_CONFIDENCE])

        if include_booking_link:
            message += f"\n\nBook an appointment: {self.ADVISOR_BOOKING_URL}"

        if advisor_name:
            message += f"\n\nYour advisor: {advisor_name}"

        return message

    def get_handoff_context(
        self,
        session_id: str,
        query: str,
        conversation_history: List[Dict],
        confidence_score: ConfidenceScore
    ) -> Dict:
        """
        Package context for human advisor handoff.

        This could be used to pre-populate a support ticket or
        provide context when a human takes over.
        """
        return {
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "original_query": query,
            "conversation_summary": self._summarize_conversation(conversation_history),
            "escalation_reason": confidence_score.escalation_reason.value if confidence_score.escalation_reason else None,
            "confidence_details": {
                "overall": confidence_score.overall_score,
                "concerns": confidence_score.concerns,
            },
            "suggested_action": self._suggest_action(confidence_score.escalation_reason),
        }

    def _summarize_conversation(self, history: List[Dict]) -> str:
        """Create a brief summary of the conversation for handoff"""
        if not history:
            return "No prior conversation"

        # Get the last few exchanges
        recent = history[-6:] if len(history) > 6 else history
        summary_parts = []

        for msg in recent:
            role = "Student" if msg.get("role") == "user" else "Bot"
            content = msg.get("content", "")[:100]  # Truncate long messages
            summary_parts.append(f"{role}: {content}...")

        return "\n".join(summary_parts)

    def _suggest_action(self, reason: Optional[EscalationReason]) -> str:
        """Suggest what action the human advisor should take"""
        suggestions = {
            EscalationReason.ACADEMIC_STANDING: "Review student's academic record",
            EscalationReason.APPEALS_EXCEPTIONS: "Discuss petition process",
            EscalationReason.PERSONAL_SITUATION: "Schedule extended consultation",
            EscalationReason.COMPLEX_QUERY: "Clarify requirements and options",
            EscalationReason.LOW_CONFIDENCE: "Answer student's question directly",
            EscalationReason.NO_RELEVANT_DOCS: "Provide accurate information",
        }
        return suggestions.get(reason, "Review and respond to student inquiry")


# Singleton instances
_scorer: Optional[ConfidenceScorer] = None
_handoff: Optional[HumanHandoff] = None


def get_confidence_scorer() -> ConfidenceScorer:
    """Get or create the confidence scorer singleton"""
    global _scorer
    if _scorer is None:
        _scorer = ConfidenceScorer()
    return _scorer


def get_human_handoff() -> HumanHandoff:
    """Get or create the human handoff singleton"""
    global _handoff
    if _handoff is None:
        _handoff = HumanHandoff()
    return _handoff
