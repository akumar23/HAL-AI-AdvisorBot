"""
Service layer for HAL Advisor Bot.

Provides business logic for LLM interactions, RAG pipeline,
intent classification, conversation management, and more.
"""

from hal.services.llm_providers import (
    get_llm_provider,
    get_embeddings_provider,
    LLMResponse,
    BaseLLMProvider,
)
from hal.services.rag_engine import get_rag_engine, query_advisor, RAGEngine
from hal.services.intent_classifier import classify_intent, Intent
from hal.services.conversation_manager import get_conversation_manager
from hal.services.confidence_scoring import get_confidence_scorer, get_human_handoff
from hal.services.quick_replies import generate_quick_replies

__all__ = [
    "get_llm_provider",
    "get_embeddings_provider",
    "LLMResponse",
    "BaseLLMProvider",
    "get_rag_engine",
    "query_advisor",
    "RAGEngine",
    "classify_intent",
    "Intent",
    "get_conversation_manager",
    "get_confidence_scorer",
    "get_human_handoff",
    "generate_quick_replies",
]
