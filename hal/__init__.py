"""
HAL Advisor Bot - AI-powered academic advising for SJSU CMPE/SE students.

This package provides a RAG-based chatbot with pluggable LLM providers
(Claude, OpenAI, Ollama) for answering questions about courses, prerequisites,
registration deadlines, and advisor information.
"""

__version__ = "0.5.0"
__author__ = "HAL Development Team"

from hal.app import create_app

__all__ = ["create_app"]
