"""
Admin interface for HAL Advisor Bot.

Provides Flask-Admin interface for content management, analytics dashboard,
and AI-powered feedback analysis.
"""

from hal.admin.admin import init_admin
from hal.admin.analytics import get_analytics_engine
from hal.admin.feedback_analyzer import get_feedback_analyzer

__all__ = ["init_admin", "get_analytics_engine", "get_feedback_analyzer"]
