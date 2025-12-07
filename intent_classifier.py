"""
Intent Classifier for HAL Advisor Bot

Uses a fast, lightweight model to classify user intents and assess confidence.
This runs BEFORE the main RAG pipeline to enable smart routing and escalation.

Recommended models:
- Claude: claude-3-5-haiku-20241022 (fast, accurate)
- OpenAI: gpt-4o-mini (very fast, cheap)
- Ollama: phi3:3.8b or qwen2.5:3b (local, free)
"""
import json
import re
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from config import Config, LLMProvider, LLMConfig, CLASSIFIER_MODELS


class Intent(Enum):
    """Supported user intents"""
    PREREQUISITE = "prerequisite"
    COURSE_INFO = "course_info"
    ADVISOR_LOOKUP = "advisor_lookup"
    ENROLLMENT = "enrollment"
    DROP_CLASS = "drop_class"
    REFUND = "refund"
    GRADES = "grades"
    GRADUATION = "graduation"
    TRANSFER = "transfer"
    UNITS = "units"
    WAITLIST = "waitlist"
    GREETING = "greeting"
    GENERAL_QUESTION = "general_question"
    OUT_OF_SCOPE = "out_of_scope"
    UNCLEAR = "unclear"


class ConfidenceLevel(Enum):
    """Confidence levels for responses"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ClassificationResult:
    """Result from intent classification"""
    intent: Intent
    confidence_level: ConfidenceLevel
    confidence_score: float  # 0.0 to 1.0
    entities: Dict  # Extracted entities (course codes, names, etc.)
    requires_context: bool  # Needs conversation history
    escalate_to_human: bool
    escalation_reason: Optional[str]
    raw_response: Optional[str] = None


class IntentClassifier:
    """
    Fast intent classifier that runs before RAG generation.

    Uses a smaller model for quick classification and confidence scoring.
    """

    CLASSIFICATION_PROMPT = """You are an intent classifier for HAL, an academic advising chatbot for SJSU CMPE/SE students.

Analyze the student's query and classify it. Return ONLY valid JSON (no markdown, no explanation).

Available intents:
- prerequisite: Questions about course prerequisites
- course_info: Questions about what a course covers
- advisor_lookup: Finding who their advisor is
- enrollment: How to add/enroll in classes
- drop_class: How to drop classes
- refund: Questions about refunds
- grades: Questions about grades, GPA, transcripts
- graduation: Graduation requirements and applications
- transfer: Transferring credits or majors
- units: Questions about unit limits
- waitlist: Waitlist questions
- greeting: Simple greetings (hi, hello)
- general_question: Other advising questions we can answer
- out_of_scope: Questions we cannot answer (not about CMPE/SE advising)
- unclear: Ambiguous or incomplete questions

Escalation rules - set escalate_to_human=true if:
- Query is about a specific personal situation we can't generalize
- Student seems distressed or mentions academic probation
- Query requires access to student records
- Confidence is very low (< 0.5)
- Query is about appeals, exceptions, or special circumstances

Extract entities:
- course_codes: List of course codes mentioned (e.g., ["CS 149", "CMPE 131"])
- last_name_initial: If asking about advisor by name

JSON format:
{
  "intent": "prerequisite",
  "confidence_score": 0.95,
  "entities": {"course_codes": ["CS 149"]},
  "requires_context": false,
  "escalate_to_human": false,
  "escalation_reason": null
}

Student query: """

    def __init__(self):
        self._client = None
        self._provider = Config.LLM_PROVIDER

    def _get_classifier_model(self) -> str:
        """Get the fast classifier model for current provider"""
        return CLASSIFIER_MODELS.get(self._provider, CLASSIFIER_MODELS[LLMProvider.OLLAMA])

    def _init_client(self):
        """Lazy-initialize the LLM client using centralized provider"""
        if self._client is not None:
            return

        from llm_providers import get_llm_provider
        provider_wrapper = get_llm_provider(use_classifier=True)
        # Extract the raw client for direct API access
        self._client = provider_wrapper.client

    def classify(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> ClassificationResult:
        """
        Classify user intent and assess confidence.

        Args:
            query: The user's message
            conversation_history: Previous messages for context

        Returns:
            ClassificationResult with intent, confidence, and escalation info
        """
        # First, try rule-based classification for common patterns
        rule_result = self._rule_based_classify(query)
        if rule_result and rule_result.confidence_score >= 0.9:
            return rule_result

        # Fall back to LLM classification
        try:
            return self._llm_classify(query, conversation_history)
        except Exception as e:
            print(f"LLM classification failed: {e}")
            # Return a safe default
            return ClassificationResult(
                intent=Intent.GENERAL_QUESTION,
                confidence_level=ConfidenceLevel.LOW,
                confidence_score=0.3,
                entities={},
                requires_context=True,
                escalate_to_human=False,
                escalation_reason=None
            )

    def _rule_based_classify(self, query: str) -> Optional[ClassificationResult]:
        """Fast rule-based classification for common patterns"""
        query_lower = query.lower().strip()

        # Greeting patterns
        if query_lower in ["hi", "hello", "hey", "hi!", "hello!", "hey there"]:
            return ClassificationResult(
                intent=Intent.GREETING,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.99,
                entities={},
                requires_context=False,
                escalate_to_human=False,
                escalation_reason=None
            )

        # Course code extraction
        course_pattern = r'\b(cs|cmpe|engr|ise|math)\s*(\d{2,3}[a-z]?)\b'
        course_matches = re.findall(course_pattern, query_lower)
        course_codes = [f"{m[0].upper()} {m[1].upper()}" for m in course_matches]

        # Prerequisite patterns
        prereq_keywords = ["prereq", "prerequisite", "before i take", "need to take before",
                          "required before", "what do i need for"]
        if any(kw in query_lower for kw in prereq_keywords):
            return ClassificationResult(
                intent=Intent.PREREQUISITE,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.95,
                entities={"course_codes": course_codes},
                requires_context=len(course_codes) == 0,  # Need context if no course specified
                escalate_to_human=False,
                escalation_reason=None
            )

        # Advisor patterns
        advisor_keywords = ["who is my advisor", "my advisor", "advisor for", "book.*advisor",
                          "appointment.*advisor", "advisor.*appointment"]
        if any(re.search(kw, query_lower) for kw in advisor_keywords):
            # Try to extract last name initial
            last_name_match = re.search(r"last name.*?([a-z])\b|starts? with ([a-z])\b", query_lower)
            initial = None
            if last_name_match:
                initial = (last_name_match.group(1) or last_name_match.group(2)).upper()

            return ClassificationResult(
                intent=Intent.ADVISOR_LOOKUP,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.95,
                entities={"last_name_initial": initial},
                requires_context=False,
                escalate_to_human=False,
                escalation_reason=None
            )

        # Enrollment patterns
        if any(kw in query_lower for kw in ["add a class", "add class", "enroll", "how do i add"]):
            return ClassificationResult(
                intent=Intent.ENROLLMENT,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.95,
                entities={"course_codes": course_codes},
                requires_context=False,
                escalate_to_human=False,
                escalation_reason=None
            )

        # Drop patterns
        if any(kw in query_lower for kw in ["drop a class", "drop class", "how do i drop"]):
            return ClassificationResult(
                intent=Intent.DROP_CLASS,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.95,
                entities={"course_codes": course_codes},
                requires_context=False,
                escalate_to_human=False,
                escalation_reason=None
            )

        # Refund patterns
        if "refund" in query_lower:
            return ClassificationResult(
                intent=Intent.REFUND,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.95,
                entities={},
                requires_context=False,
                escalate_to_human=False,
                escalation_reason=None
            )

        # Units patterns
        if any(kw in query_lower for kw in ["how many units", "max units", "maximum units",
                                            "unit limit", "units can i take"]):
            return ClassificationResult(
                intent=Intent.UNITS,
                confidence_level=ConfidenceLevel.HIGH,
                confidence_score=0.95,
                entities={},
                requires_context=False,
                escalate_to_human=False,
                escalation_reason=None
            )

        # Context-dependent queries (follow-ups)
        context_indicators = ["that class", "that course", "it", "those", "the same",
                             "what about", "and also", "another question"]
        if any(kw in query_lower for kw in context_indicators):
            return ClassificationResult(
                intent=Intent.GENERAL_QUESTION,
                confidence_level=ConfidenceLevel.MEDIUM,
                confidence_score=0.7,
                entities={"course_codes": course_codes},
                requires_context=True,
                escalate_to_human=False,
                escalation_reason=None
            )

        # If we found course codes but no clear intent, it's likely a course info request
        if course_codes:
            return ClassificationResult(
                intent=Intent.COURSE_INFO,
                confidence_level=ConfidenceLevel.MEDIUM,
                confidence_score=0.75,
                entities={"course_codes": course_codes},
                requires_context=False,
                escalate_to_human=False,
                escalation_reason=None
            )

        # No rule matched
        return None

    def _llm_classify(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> ClassificationResult:
        """Use LLM for classification when rules don't match"""
        self._init_client()

        # Build prompt with context if available
        prompt = self.CLASSIFICATION_PROMPT + query

        if conversation_history and len(conversation_history) > 0:
            context_str = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history[-4:]  # Last 4 messages
            ])
            prompt = f"Recent conversation:\n{context_str}\n\n{prompt}"

        # Call the appropriate provider
        model = self._get_classifier_model()
        raw_response = ""

        try:
            if self._provider == LLMProvider.CLAUDE:
                response = self._client.messages.create(
                    model=model,
                    max_tokens=500,
                    temperature=0.0,
                    messages=[{"role": "user", "content": prompt}]
                )
                raw_response = response.content[0].text

            elif self._provider == LLMProvider.OPENAI:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                raw_response = response.choices[0].message.content

            elif self._provider == LLMProvider.OLLAMA:
                response = self._client.chat(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.0},
                    format="json"
                )
                raw_response = response["message"]["content"]

            # Parse JSON response
            return self._parse_classification_response(raw_response)

        except Exception as e:
            print(f"Classification error: {e}")
            raise

    def _parse_classification_response(self, response: str) -> ClassificationResult:
        """Parse LLM JSON response into ClassificationResult"""
        try:
            # Clean up response (remove markdown if present)
            response = response.strip()
            if response.startswith("```"):
                response = re.sub(r"```json?\n?", "", response)
                response = response.rstrip("`")

            data = json.loads(response)

            # Map intent string to enum
            intent_str = data.get("intent", "general_question").lower()
            try:
                intent = Intent(intent_str)
            except ValueError:
                intent = Intent.GENERAL_QUESTION

            # Calculate confidence level from score
            score = float(data.get("confidence_score", 0.5))
            if score >= 0.8:
                level = ConfidenceLevel.HIGH
            elif score >= 0.5:
                level = ConfidenceLevel.MEDIUM
            else:
                level = ConfidenceLevel.LOW

            return ClassificationResult(
                intent=intent,
                confidence_level=level,
                confidence_score=score,
                entities=data.get("entities", {}),
                requires_context=data.get("requires_context", False),
                escalate_to_human=data.get("escalate_to_human", False),
                escalation_reason=data.get("escalation_reason"),
                raw_response=response
            )

        except json.JSONDecodeError as e:
            print(f"Failed to parse classification JSON: {e}")
            print(f"Response was: {response}")

            # Return safe default
            return ClassificationResult(
                intent=Intent.GENERAL_QUESTION,
                confidence_level=ConfidenceLevel.MEDIUM,
                confidence_score=0.5,
                entities={},
                requires_context=True,
                escalate_to_human=False,
                escalation_reason=None,
                raw_response=response
            )


# Singleton instance
_classifier: Optional[IntentClassifier] = None


def get_classifier() -> IntentClassifier:
    """Get or create the intent classifier singleton"""
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier


def classify_intent(
    query: str,
    conversation_history: Optional[List[Dict]] = None
) -> ClassificationResult:
    """
    Convenience function to classify a query.

    Args:
        query: User's message
        conversation_history: Previous messages

    Returns:
        ClassificationResult
    """
    classifier = get_classifier()
    return classifier.classify(query, conversation_history)
