"""
Quick Replies Generator for HAL Advisor Bot

Generates contextual quick reply suggestions using LLM
based on conversation history and current context.
"""
from typing import List, Dict, Optional
import json
import re

from hal.config import Config, LLMProvider
from hal.services.llm_providers import get_llm_provider


# Default quick replies by category
DEFAULT_REPLIES = {
    "greeting": [
        "What are the prerequisites for CS 146?",
        "How do I find my academic advisor?",
        "What's the deadline to add classes?"
    ],
    "course": [
        "What are the prerequisites?",
        "When is this course offered?",
        "Who teaches this course?"
    ],
    "advisor": [
        "How do I schedule an appointment?",
        "What are office hours?",
        "Can I change my advisor?"
    ],
    "enrollment": [
        "When is the last day to add?",
        "How do I get a permission number?",
        "What's the waitlist process?"
    ],
    "general": [
        "Tell me about course prerequisites",
        "Help me find my advisor",
        "What are important deadlines?"
    ]
}


class QuickReplyGenerator:
    """
    Generates contextual quick reply suggestions.

    Uses a fast LLM model to analyze conversation context
    and suggest relevant follow-up questions.
    """

    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        """Lazy-load LLM provider"""
        if self._llm is None:
            # Use the classifier config (fast model)
            self._llm = get_llm_provider(use_classifier=True)
        return self._llm

    def generate(
        self,
        last_response: Optional[str] = None,
        last_query: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        intent: Optional[str] = None,
        use_llm: bool = True
    ) -> List[str]:
        """
        Generate quick reply suggestions.

        Args:
            last_response: The bot's last response
            last_query: The user's last query
            conversation_history: Full conversation history
            intent: Detected intent from last query
            use_llm: Whether to use LLM for dynamic generation

        Returns:
            List of 3-4 suggested quick replies
        """
        # If no context, return greeting defaults
        if not last_response and not conversation_history:
            return DEFAULT_REPLIES["greeting"]

        # Try LLM generation if enabled
        if use_llm and Config.USE_FAST_CLASSIFIER:
            try:
                suggestions = self._generate_with_llm(
                    last_response,
                    last_query,
                    conversation_history,
                    intent
                )
                if suggestions and len(suggestions) >= 2:
                    return suggestions[:4]  # Max 4 suggestions
            except Exception as e:
                print(f"LLM quick reply generation failed: {e}")

        # Fall back to rule-based suggestions
        return self._generate_rule_based(last_response, intent)

    def _generate_with_llm(
        self,
        last_response: Optional[str],
        last_query: Optional[str],
        conversation_history: Optional[List[Dict]],
        intent: Optional[str]
    ) -> List[str]:
        """Generate suggestions using LLM"""

        # Build context for the LLM
        context_parts = []

        if intent:
            context_parts.append(f"Current topic: {intent}")

        if last_query:
            context_parts.append(f"User's question: {last_query}")

        if last_response:
            # Truncate long responses
            truncated = last_response[:500] + "..." if len(last_response) > 500 else last_response
            context_parts.append(f"Bot's response: {truncated}")

        context = "\n".join(context_parts)

        prompt = f"""Based on this academic advising conversation context, suggest 3-4 natural follow-up questions a student might ask.

{context}

Requirements:
- Questions should be relevant to CMPE/SE advising at SJSU
- Keep questions short (under 50 characters each)
- Make them natural conversation continuations
- Focus on course prerequisites, registration, advisors, or deadlines

Return ONLY a JSON array of strings, no other text. Example:
["What are the prerequisites?", "When is this course offered?", "Can I take this online?"]

JSON array:"""

        try:
            # Use the fast classifier model
            response = self.llm.generate_simple(prompt, max_tokens=200)

            # Parse JSON from response
            suggestions = self._parse_suggestions(response)
            return suggestions

        except Exception as e:
            print(f"Error generating quick replies: {e}")
            return []

    def _parse_suggestions(self, response: str) -> List[str]:
        """Parse LLM response to extract suggestions"""
        try:
            # Try to find JSON array in response
            response = response.strip()

            # Find array pattern
            match = re.search(r'\[.*?\]', response, re.DOTALL)
            if match:
                arr = json.loads(match.group())
                if isinstance(arr, list):
                    # Filter and clean suggestions
                    suggestions = []
                    for s in arr:
                        if isinstance(s, str) and len(s) > 5 and len(s) < 80:
                            suggestions.append(s.strip())
                    return suggestions
        except json.JSONDecodeError:
            pass

        # Try line-by-line parsing if JSON fails
        lines = response.split('\n')
        suggestions = []
        for line in lines:
            line = line.strip()
            # Remove common prefixes
            line = re.sub(r'^[\d\.\-\*\•]+\s*', '', line)
            line = re.sub(r'^["\'`]|["\'`]$', '', line)
            if len(line) > 5 and len(line) < 80 and '?' in line:
                suggestions.append(line)

        return suggestions[:4]

    def _generate_rule_based(
        self,
        last_response: Optional[str],
        intent: Optional[str]
    ) -> List[str]:
        """Generate suggestions using rules"""

        # Map intents to categories
        intent_category_map = {
            "prerequisite": "course",
            "course_info": "course",
            "advisor_lookup": "advisor",
            "enrollment": "enrollment",
            "drop_class": "enrollment",
            "waitlist": "enrollment",
        }

        # Get category from intent
        category = "general"
        if intent:
            intent_lower = intent.lower().replace(" ", "_")
            category = intent_category_map.get(intent_lower, "general")

        # If response mentions specific topics, adjust category
        if last_response:
            response_lower = last_response.lower()
            if "prerequisite" in response_lower or "before taking" in response_lower:
                category = "course"
            elif "advisor" in response_lower or "appointment" in response_lower:
                category = "advisor"
            elif "deadline" in response_lower or "last day" in response_lower:
                category = "enrollment"

        return DEFAULT_REPLIES.get(category, DEFAULT_REPLIES["general"])

    def get_escalation_replies(self) -> List[str]:
        """Get quick replies for escalation scenarios"""
        return [
            "Schedule an appointment",
            "Find my advisor's contact",
            "Start a new question"
        ]


# Singleton instance
_generator: Optional[QuickReplyGenerator] = None


def get_quick_reply_generator() -> QuickReplyGenerator:
    """Get or create the quick reply generator singleton"""
    global _generator
    if _generator is None:
        _generator = QuickReplyGenerator()
    return _generator


def generate_quick_replies(
    last_response: Optional[str] = None,
    last_query: Optional[str] = None,
    conversation_history: Optional[List[Dict]] = None,
    intent: Optional[str] = None
) -> List[str]:
    """
    Convenience function to generate quick replies.

    Args:
        last_response: The bot's last response
        last_query: The user's last query
        conversation_history: Full conversation history
        intent: Detected intent from last query

    Returns:
        List of suggested quick replies
    """
    generator = get_quick_reply_generator()
    return generator.generate(
        last_response=last_response,
        last_query=last_query,
        conversation_history=conversation_history,
        intent=intent
    )
