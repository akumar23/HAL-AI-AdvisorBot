"""
Conversation Context Manager for HAL Advisor Bot

Handles multi-turn dialogue by:
- Tracking conversation history with smart summarization
- Resolving pronouns and references ("that class", "it", etc.)
- Maintaining context across follow-up questions
- Managing session state efficiently
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque

from models import db, Conversation


@dataclass
class ConversationContext:
    """Represents the current conversation context"""
    session_id: str
    messages: List[Dict] = field(default_factory=list)
    current_topic: Optional[str] = None  # e.g., "CS 149"
    mentioned_courses: List[str] = field(default_factory=list)
    mentioned_entities: Dict = field(default_factory=dict)
    last_intent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, role: str, content: str):
        """Add a message to the conversation"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.last_activity = datetime.utcnow()

        # Extract and track mentioned courses
        if role == "user":
            courses = self._extract_courses(content)
            if courses:
                self.mentioned_courses.extend(courses)
                self.current_topic = courses[-1]  # Most recent course is the topic

    def _extract_courses(self, text: str) -> List[str]:
        """Extract course codes from text"""
        pattern = r'\b(CS|CMPE|ENGR|ISE|MATH)\s*(\d{2,3}[A-Za-z]?)\b'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [f"{m[0].upper()} {m[1].upper()}" for m in matches]

    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        """Get the most recent messages"""
        return self.messages[-limit:] if self.messages else []

    def get_context_summary(self) -> str:
        """Generate a summary of the current context for the LLM"""
        parts = []

        if self.current_topic:
            parts.append(f"Current topic: {self.current_topic}")

        if self.mentioned_courses:
            unique_courses = list(dict.fromkeys(self.mentioned_courses[-5:]))
            parts.append(f"Recently discussed courses: {', '.join(unique_courses)}")

        if self.last_intent:
            parts.append(f"Last question type: {self.last_intent}")

        return " | ".join(parts) if parts else "No prior context"


class ConversationManager:
    """
    Manages conversation state and context resolution.

    Features:
    - Pronoun resolution ("that class" -> "CS 149")
    - Context carryover for follow-up questions
    - Intelligent message history truncation
    - Session management with timeout
    """

    # Reference patterns that need context resolution
    REFERENCE_PATTERNS = [
        (r'\bthat class\b', 'course'),
        (r'\bthat course\b', 'course'),
        (r'\bthe class\b', 'course'),
        (r'\bthe course\b', 'course'),
        (r'\bit\b', 'topic'),
        (r'\bthis\b', 'topic'),
        (r'\bthem\b', 'courses'),
        (r'\bthose\b', 'courses'),
        (r'\bsame one\b', 'topic'),
        (r'\bthe same\b', 'topic'),
    ]

    # Session timeout in minutes
    SESSION_TIMEOUT = 30

    def __init__(self):
        self._contexts: Dict[str, ConversationContext] = {}

    def get_context(self, session_id: str) -> ConversationContext:
        """Get or create conversation context for a session"""
        if session_id not in self._contexts:
            self._contexts[session_id] = ConversationContext(session_id=session_id)
        else:
            # Check for session timeout
            context = self._contexts[session_id]
            if datetime.utcnow() - context.last_activity > timedelta(minutes=self.SESSION_TIMEOUT):
                # Session expired, create new context
                self._contexts[session_id] = ConversationContext(session_id=session_id)

        return self._contexts[session_id]

    def add_user_message(self, session_id: str, content: str) -> ConversationContext:
        """Add a user message and return updated context"""
        context = self.get_context(session_id)
        context.add_message("user", content)
        return context

    def add_assistant_message(self, session_id: str, content: str) -> ConversationContext:
        """Add an assistant message and return updated context"""
        context = self.get_context(session_id)
        context.add_message("assistant", content)
        return context

    def set_intent(self, session_id: str, intent: str):
        """Set the last detected intent"""
        context = self.get_context(session_id)
        context.last_intent = intent

    def resolve_references(self, session_id: str, query: str) -> Tuple[str, bool]:
        """
        Resolve pronoun references in a query using conversation context.

        Args:
            session_id: The session ID
            query: The user's query

        Returns:
            Tuple of (resolved_query, was_modified)
        """
        context = self.get_context(session_id)
        original_query = query
        was_modified = False

        for pattern, ref_type in self.REFERENCE_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                if ref_type == 'course' and context.current_topic:
                    # Replace "that class" with the actual course
                    query = re.sub(pattern, context.current_topic, query, flags=re.IGNORECASE)
                    was_modified = True
                elif ref_type == 'topic' and context.current_topic:
                    query = re.sub(pattern, context.current_topic, query, flags=re.IGNORECASE)
                    was_modified = True
                elif ref_type == 'courses' and context.mentioned_courses:
                    # For plural references, use the last few mentioned courses
                    courses_str = ", ".join(context.mentioned_courses[-3:])
                    query = re.sub(pattern, courses_str, query, flags=re.IGNORECASE)
                    was_modified = True

        return query, was_modified

    def needs_context(self, query: str) -> bool:
        """Check if a query needs conversation context to be understood"""
        query_lower = query.lower()

        # Check for reference patterns
        for pattern, _ in self.REFERENCE_PATTERNS:
            if re.search(pattern, query_lower):
                return True

        # Check for follow-up indicators
        follow_up_indicators = [
            r'^what about\b',
            r'^how about\b',
            r'^and\b',
            r'^also\b',
            r'^another\b',
            r'^same\b',
            r'^can i\b',
            r"^what's",
            r'^is there\b',
        ]

        for indicator in follow_up_indicators:
            if re.search(indicator, query_lower):
                return True

        # Very short queries often need context
        if len(query.split()) <= 3:
            return True

        return False

    def build_context_prompt(self, session_id: str, current_query: str) -> str:
        """
        Build a context-aware prompt for the LLM.

        Includes relevant conversation history and context summary.
        """
        context = self.get_context(session_id)

        parts = []

        # Add context summary
        summary = context.get_context_summary()
        if summary != "No prior context":
            parts.append(f"[Context: {summary}]")

        # Add recent conversation history
        recent = context.get_recent_messages(6)  # Last 3 exchanges
        if recent:
            parts.append("Recent conversation:")
            for msg in recent:
                role = "Student" if msg["role"] == "user" else "HAL"
                parts.append(f"{role}: {msg['content']}")

        # Add current query
        parts.append(f"\nCurrent question: {current_query}")

        return "\n".join(parts)

    def get_messages_for_llm(
        self,
        session_id: str,
        max_messages: int = 10,
        max_tokens: int = 2000
    ) -> List[Dict]:
        """
        Get formatted messages for LLM context.

        Intelligently truncates to stay within token limits while
        preserving the most relevant context.
        """
        context = self.get_context(session_id)
        messages = context.get_recent_messages(max_messages)

        # Simple token estimation (rough: 4 chars = 1 token)
        total_chars = sum(len(m["content"]) for m in messages)
        estimated_tokens = total_chars // 4

        # If over limit, summarize older messages
        if estimated_tokens > max_tokens and len(messages) > 4:
            # Keep first message (for topic) and last few messages
            older_messages = messages[:-4]
            recent_messages = messages[-4:]

            # Summarize older messages
            older_summary = self._summarize_messages(older_messages)

            return [
                {"role": "system", "content": f"Earlier in this conversation: {older_summary}"}
            ] + [{"role": m["role"], "content": m["content"]} for m in recent_messages]

        return [{"role": m["role"], "content": m["content"]} for m in messages]

    def _summarize_messages(self, messages: List[Dict]) -> str:
        """Create a brief summary of older messages"""
        topics = []
        for msg in messages:
            if msg["role"] == "user":
                # Extract key topics
                courses = re.findall(r'\b(CS|CMPE|ENGR|ISE)\s*\d+[A-Za-z]?\b', msg["content"], re.IGNORECASE)
                topics.extend(courses)

        if topics:
            unique_topics = list(dict.fromkeys(topics))
            return f"Discussed: {', '.join(unique_topics[:5])}"
        return "General advising questions"

    def clear_context(self, session_id: str):
        """Clear conversation context for a session"""
        if session_id in self._contexts:
            del self._contexts[session_id]

    def persist_conversation(self, session_id: str):
        """Persist conversation to database for analytics"""
        context = self.get_context(session_id)

        for msg in context.messages:
            # Check if already persisted (has a timestamp but no db record)
            existing = Conversation.query.filter_by(
                session_id=session_id,
                content=msg["content"]
            ).first()

            if not existing:
                conv = Conversation(
                    session_id=session_id,
                    role=msg["role"],
                    content=msg["content"]
                )
                db.session.add(conv)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error persisting conversation: {e}")


# Singleton instance
_manager: Optional[ConversationManager] = None


def get_conversation_manager() -> ConversationManager:
    """Get or create the conversation manager singleton"""
    global _manager
    if _manager is None:
        _manager = ConversationManager()
    return _manager
