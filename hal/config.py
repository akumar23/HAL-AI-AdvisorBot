"""
HAL Advisor Bot Configuration

This module handles configuration for the RAG-based advisor chatbot,
including LLM provider selection (Claude, OpenAI, or Ollama).

Supports multi-model architecture:
- Fast model: For intent classification (quick, cheap)
- Main model: For RAG response generation (quality)
"""
import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class LLMProvider(Enum):
    """Supported LLM providers"""
    CLAUDE = "claude"
    OPENAI = "openai"
    OLLAMA = "ollama"


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: LLMProvider
    model: str
    temperature: float = 0.3
    max_tokens: int = 1024
    api_key: Optional[str] = None
    base_url: Optional[str] = None  # For Ollama custom endpoints


# Recommended models per provider (from claude-agent-expert research)
# Main models - for RAG response generation (quality focus)
MAIN_MODELS = {
    LLMProvider.CLAUDE: {
        "default": "claude-sonnet-4-20250514",
        "fast": "claude-3-5-haiku-20241022",
        "best": "claude-sonnet-4-20250514",
    },
    LLMProvider.OPENAI: {
        "default": "gpt-4o",
        "fast": "gpt-4o-mini",
        "best": "gpt-4o",
    },
    LLMProvider.OLLAMA: {
        "default": os.environ.get("OLLAMA_MODEL", "llama3.1:8b"),
        "fast": os.environ.get("OLLAMA_MODEL", "llama3.1:8b"),
        "best": os.environ.get("OLLAMA_MODEL", "llama3.1:8b"),
    },
}

# Classifier models - for intent classification (speed focus)
CLASSIFIER_MODELS = {
    LLMProvider.CLAUDE: "claude-3-5-haiku-20241022",  # Fast and cheap
    LLMProvider.OPENAI: "gpt-4o-mini",  # Very fast, 15x cheaper than gpt-4o
    LLMProvider.OLLAMA: os.environ.get("OLLAMA_CLASSIFIER_MODEL", os.environ.get("OLLAMA_MODEL", "llama3.1:8b")),
}

# Embedding models per provider
EMBEDDING_MODELS = {
    LLMProvider.CLAUDE: "text-embedding-3-small",  # Uses OpenAI for embeddings
    LLMProvider.OPENAI: "text-embedding-3-small",
    LLMProvider.OLLAMA: "nomic-embed-text",
}


class Config:
    """Application configuration"""

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "hal-advisor-secret-key-change-in-production")

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///hal_advisor.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session settings
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    # LLM Provider settings
    LLM_PROVIDER = LLMProvider(os.environ.get("LLM_PROVIDER", "ollama"))

    # API Keys (set via environment variables)
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    # Ollama settings
    OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    # ChromaDB settings
    CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")
    CHROMA_COLLECTION_NAME = "hal_advising"

    # RAG settings
    RAG_TOP_K = int(os.environ.get("RAG_TOP_K", "5"))
    RAG_SIMILARITY_THRESHOLD = float(os.environ.get("RAG_SIMILARITY_THRESHOLD", "0.7"))

    # Confidence thresholds for response handling
    CONFIDENCE_HIGH = 0.8
    CONFIDENCE_MEDIUM = 0.5
    CONFIDENCE_ESCALATION = 0.4  # Below this, escalate to human

    # Escalation settings
    ENABLE_HUMAN_HANDOFF = os.environ.get("ENABLE_HUMAN_HANDOFF", "true").lower() == "true"
    ADVISOR_BOOKING_URL = os.environ.get(
        "ADVISOR_BOOKING_URL",
        "https://sjsu.campus.eab.com/student/appointments/new"
    )

    # Admin settings
    FLASK_ADMIN_SWATCH = "cerulean"
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")

    # Multi-model pipeline settings
    USE_FAST_CLASSIFIER = os.environ.get("USE_FAST_CLASSIFIER", "true").lower() == "true"

    # Temperature settings by task type
    TEMPERATURE_CLASSIFICATION = 0.0  # Deterministic for classification
    TEMPERATURE_FACTUAL = 0.2  # Low for factual responses (prerequisites)
    TEMPERATURE_CONVERSATIONAL = 0.4  # Slightly higher for natural dialogue

    @classmethod
    def get_llm_config(cls, quality: str = "default") -> LLMConfig:
        """
        Get LLM configuration for main response generation.

        Args:
            quality: One of "default", "fast", or "best"

        Returns:
            LLMConfig instance for the selected provider/quality
        """
        provider = cls.LLM_PROVIDER
        model = MAIN_MODELS[provider].get(quality, MAIN_MODELS[provider]["default"])

        api_key = None
        base_url = None

        if provider == LLMProvider.CLAUDE:
            api_key = cls.ANTHROPIC_API_KEY
        elif provider == LLMProvider.OPENAI:
            api_key = cls.OPENAI_API_KEY
        elif provider == LLMProvider.OLLAMA:
            base_url = cls.OLLAMA_BASE_URL

        return LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=cls.TEMPERATURE_FACTUAL,
        )

    @classmethod
    def get_classifier_config(cls) -> LLMConfig:
        """
        Get LLM configuration for fast intent classification.

        Returns:
            LLMConfig instance optimized for classification
        """
        provider = cls.LLM_PROVIDER
        model = CLASSIFIER_MODELS.get(provider, CLASSIFIER_MODELS[LLMProvider.OLLAMA])

        api_key = None
        base_url = None

        if provider == LLMProvider.CLAUDE:
            api_key = cls.ANTHROPIC_API_KEY
        elif provider == LLMProvider.OPENAI:
            api_key = cls.OPENAI_API_KEY
        elif provider == LLMProvider.OLLAMA:
            base_url = cls.OLLAMA_BASE_URL

        return LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=cls.TEMPERATURE_CLASSIFICATION,
            max_tokens=500,  # Classification doesn't need many tokens
        )

    @classmethod
    def get_embedding_model(cls) -> str:
        """Get the embedding model for the current provider"""
        return EMBEDDING_MODELS.get(cls.LLM_PROVIDER, "nomic-embed-text")

    @classmethod
    def get_model_info(cls) -> dict:
        """Get information about configured models"""
        main_config = cls.get_llm_config()
        classifier_config = cls.get_classifier_config()

        return {
            "provider": cls.LLM_PROVIDER.value,
            "main_model": main_config.model,
            "classifier_model": classifier_config.model,
            "embedding_model": cls.get_embedding_model(),
            "use_fast_classifier": cls.USE_FAST_CLASSIFIER,
        }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LLM_PROVIDER = LLMProvider.OLLAMA  # Free for development


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # In production, prefer Claude for accuracy
    LLM_PROVIDER = LLMProvider(os.environ.get("LLM_PROVIDER", "claude"))


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LLM_PROVIDER = LLMProvider.OLLAMA
    USE_FAST_CLASSIFIER = False  # Use rule-based only for testing


# Config mapping
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)
