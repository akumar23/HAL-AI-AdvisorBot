"""
Admin interface for HAL Advisor Bot.

Provides analytics engine and AI-powered feedback analysis.
Admin UI is available through the Next.js frontend at /control-panel-x7k9m2
"""

from hal.admin.analytics import get_analytics_engine
from hal.admin.feedback_analyzer import get_feedback_analyzer

__all__ = ["get_analytics_engine", "get_feedback_analyzer"]
