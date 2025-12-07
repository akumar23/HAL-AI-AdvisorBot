"""
LLM Provider Abstraction Layer

Provides a unified interface for Claude (Anthropic), OpenAI, and Ollama.
Users can switch between providers via configuration.
"""
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass

from hal.config import LLMProvider, LLMConfig, Config


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider"""
    content: str
    model: str
    provider: str
    usage: Optional[Dict] = None
    confidence: Optional[float] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """Default system prompt for HAL advisor"""
        return """You are HAL, an academic advisor assistant for SJSU CMPE (Computer Engineering) and SE (Software Engineering) students.

RULES:
1. Only answer using information from the provided CONTEXT
2. If the answer is not in the context, say: "I don't have that specific information. Please contact your academic advisor."
3. For prerequisites, always cite the exact course code and requirements
4. Never guess or make up information not explicitly stated in the context
5. Be helpful, concise, and accurate
6. If asked about course prerequisites, mention if requirements differ for CMPE vs SE majors

Always prioritize accuracy over being helpful. It's better to say you don't know than to give incorrect academic advice."""

    @abstractmethod
    def generate(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> LLMResponse:
        """Generate a response given a query and context"""
        pass

    @abstractmethod
    def generate_simple(
        self,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a simple response without RAG context.
        Used for quick tasks like generating quick replies.
        """
        pass

    def _build_messages(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """Build the message list for the LLM"""
        messages = []

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # Add current query with context
        user_message = f"""CONTEXT:
{context}

STUDENT QUESTION: {query}

Please answer based only on the context provided above."""

        messages.append({"role": "user", "content": user_message})

        return messages


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=config.api_key)
        except ImportError:
            raise ImportError("Please install anthropic: pip install anthropic")

    def generate(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> LLMResponse:
        messages = self._build_messages(query, context, conversation_history)

        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=self.system_prompt,
            messages=messages
        )

        return LLMResponse(
            content=response.content[0].text,
            model=self.config.model,
            provider="claude",
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        )

    def generate_simple(
        self,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> str:
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=max_tokens or 200,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=config.api_key)
        except ImportError:
            raise ImportError("Please install openai: pip install openai")

    def generate(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> LLMResponse:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self._build_messages(query, context, conversation_history))

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=self.config.model,
            provider="openai",
            usage={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            }
        )

    def generate_simple(
        self,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens or 200,
            temperature=0.3,
        )
        return response.choices[0].message.content


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
        try:
            import ollama
            self.client = ollama
        except ImportError:
            raise ImportError("Please install ollama: pip install ollama")

    def generate(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> LLMResponse:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self._build_messages(query, context, conversation_history))

        response = self.client.chat(
            model=self.config.model,
            messages=messages,
            options={
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            }
        )

        return LLMResponse(
            content=response["message"]["content"],
            model=self.config.model,
            provider="ollama",
            usage={
                "total_duration": response.get("total_duration"),
                "eval_count": response.get("eval_count"),
            }
        )

    def generate_simple(
        self,
        prompt: str,
        max_tokens: Optional[int] = None
    ) -> str:
        response = self.client.chat(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.3,
                "num_predict": max_tokens or 200,
            }
        )
        return response["message"]["content"]


def get_llm_provider(config: Optional[LLMConfig] = None, use_classifier: bool = False) -> BaseLLMProvider:
    """
    Factory function to get the appropriate LLM provider.

    Args:
        config: Optional LLMConfig. If not provided, uses default from Config.
        use_classifier: If True, use the fast classifier model instead of main model.

    Returns:
        Configured LLM provider instance
    """
    if config is None:
        if use_classifier:
            config = Config.get_classifier_config()
        else:
            config = Config.get_llm_config()

    providers = {
        LLMProvider.CLAUDE: ClaudeProvider,
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.OLLAMA: OllamaProvider,
    }

    provider_class = providers.get(config.provider)
    if not provider_class:
        raise ValueError(f"Unknown LLM provider: {config.provider}")

    return provider_class(config)


def get_embeddings_provider():
    """
    Get the embeddings provider based on configuration.

    For Claude, we use OpenAI embeddings.
    For OpenAI, we use OpenAI embeddings.
    For Ollama, we use local Ollama embeddings.
    """
    provider = Config.LLM_PROVIDER

    if provider in [LLMProvider.CLAUDE, LLMProvider.OPENAI]:
        # Use OpenAI embeddings
        try:
            from langchain_openai import OpenAIEmbeddings
            api_key = Config.OPENAI_API_KEY or Config.ANTHROPIC_API_KEY
            return OpenAIEmbeddings(
                model=Config.get_embedding_model(),
                openai_api_key=api_key
            )
        except ImportError:
            raise ImportError("Please install langchain-openai: pip install langchain-openai")
    else:
        # Use Ollama embeddings for local
        try:
            from langchain_ollama import OllamaEmbeddings
            return OllamaEmbeddings(
                model=Config.get_embedding_model(),
                base_url=Config.OLLAMA_BASE_URL
            )
        except ImportError:
            raise ImportError("Please install langchain-ollama: pip install langchain-ollama")
