"""
Analytics Module for HAL Advisor Bot

Provides:
- Usage statistics and metrics
- Feedback analysis
- Conversation insights
- LLM-powered feedback summarization
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter
import json

from sqlalchemy import func, desc, and_

from models import db, Conversation, Feedback, Course
from config import Config


class AnalyticsEngine:
    """
    Analytics engine for HAL Advisor Bot.

    Computes various metrics and insights from conversation
    and feedback data.
    """

    def get_overview_stats(self, days: int = 30) -> Dict:
        """
        Get high-level overview statistics.

        Args:
            days: Number of days to include in stats

        Returns:
            Dict with key metrics
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Total conversations (unique sessions)
        total_sessions = db.session.query(
            func.count(func.distinct(Conversation.session_id))
        ).filter(Conversation.created_at >= cutoff).scalar() or 0

        # Total messages
        total_messages = db.session.query(
            func.count(Conversation.id)
        ).filter(Conversation.created_at >= cutoff).scalar() or 0

        # User messages only
        user_messages = db.session.query(
            func.count(Conversation.id)
        ).filter(
            and_(
                Conversation.created_at >= cutoff,
                Conversation.role == "user"
            )
        ).scalar() or 0

        # Total feedback
        total_feedback = db.session.query(
            func.count(Feedback.id)
        ).filter(Feedback.created_at >= cutoff).scalar() or 0

        # Positive feedback
        positive_feedback = db.session.query(
            func.count(Feedback.id)
        ).filter(
            and_(
                Feedback.created_at >= cutoff,
                Feedback.rating == 2
            )
        ).scalar() or 0

        # Calculate satisfaction rate
        satisfaction_rate = (
            (positive_feedback / total_feedback * 100)
            if total_feedback > 0 else 0
        )

        # Average messages per session
        avg_messages = (
            total_messages / total_sessions
            if total_sessions > 0 else 0
        )

        return {
            "period_days": days,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "total_feedback": total_feedback,
            "positive_feedback": positive_feedback,
            "negative_feedback": total_feedback - positive_feedback,
            "satisfaction_rate": round(satisfaction_rate, 1),
            "avg_messages_per_session": round(avg_messages, 1),
        }

    def get_daily_usage(self, days: int = 30) -> List[Dict]:
        """
        Get daily usage statistics for charting.

        Returns:
            List of daily stats with date, sessions, messages
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Query daily message counts
        daily_stats = db.session.query(
            func.date(Conversation.created_at).label("date"),
            func.count(func.distinct(Conversation.session_id)).label("sessions"),
            func.count(Conversation.id).label("messages")
        ).filter(
            Conversation.created_at >= cutoff
        ).group_by(
            func.date(Conversation.created_at)
        ).order_by(
            func.date(Conversation.created_at)
        ).all()

        result = []
        for row in daily_stats:
            result.append({
                "date": str(row.date),
                "sessions": row.sessions,
                "messages": row.messages
            })

        return result

    def get_feedback_breakdown(self, days: int = 30) -> Dict:
        """
        Get feedback breakdown with comments.

        Returns:
            Dict with positive/negative counts and recent comments
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get counts by rating
        feedback_counts = db.session.query(
            Feedback.rating,
            func.count(Feedback.id)
        ).filter(
            Feedback.created_at >= cutoff
        ).group_by(Feedback.rating).all()

        counts = {str(r): c for r, c in feedback_counts}

        # Get recent negative feedback with comments
        negative_with_comments = Feedback.query.filter(
            and_(
                Feedback.created_at >= cutoff,
                Feedback.rating == 1,
                Feedback.comment.isnot(None),
                Feedback.comment != ""
            )
        ).order_by(desc(Feedback.created_at)).limit(10).all()

        recent_issues = []
        for fb in negative_with_comments:
            recent_issues.append({
                "date": fb.created_at.strftime("%Y-%m-%d %H:%M"),
                "query": fb.user_query[:100] if fb.user_query else "",
                "comment": fb.comment
            })

        return {
            "positive": counts.get("2", 0),
            "negative": counts.get("1", 0),
            "recent_issues": recent_issues
        }

    def get_popular_topics(self, days: int = 30, limit: int = 10) -> List[Dict]:
        """
        Identify popular topics from user messages.

        Uses keyword extraction to find common themes.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get user messages
        messages = Conversation.query.filter(
            and_(
                Conversation.created_at >= cutoff,
                Conversation.role == "user"
            )
        ).all()

        # Extract keywords and count
        topic_keywords = {
            "prerequisites": ["prerequisite", "prereq", "before taking", "need to take"],
            "enrollment": ["enroll", "register", "sign up", "add class"],
            "drop_class": ["drop", "withdraw", "remove class"],
            "advisor": ["advisor", "adviser", "appointment", "meet with"],
            "deadlines": ["deadline", "last day", "when", "date"],
            "gpa": ["gpa", "grade", "transcript"],
            "graduation": ["graduate", "graduation", "degree"],
            "units": ["units", "credits", "hours"],
            "waitlist": ["waitlist", "wait list", "waiting"],
        }

        topic_counts = Counter()

        for msg in messages:
            content = msg.content.lower()
            for topic, keywords in topic_keywords.items():
                if any(kw in content for kw in keywords):
                    topic_counts[topic] += 1

        # Format results
        results = []
        for topic, count in topic_counts.most_common(limit):
            results.append({
                "topic": topic.replace("_", " ").title(),
                "count": count,
                "percentage": round(count / len(messages) * 100, 1) if messages else 0
            })

        return results

    def get_session_details(self, session_id: str) -> Dict:
        """
        Get detailed information about a specific session.
        """
        messages = Conversation.query.filter_by(
            session_id=session_id
        ).order_by(Conversation.created_at).all()

        feedback = Feedback.query.filter_by(
            session_id=session_id
        ).all()

        conversation = []
        for msg in messages:
            conversation.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        feedback_list = []
        for fb in feedback:
            feedback_list.append({
                "rating": "Positive" if fb.rating == 2 else "Negative",
                "query": fb.user_query,
                "comment": fb.comment,
                "timestamp": fb.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        return {
            "session_id": session_id,
            "message_count": len(messages),
            "conversation": conversation,
            "feedback": feedback_list,
            "start_time": messages[0].created_at.strftime("%Y-%m-%d %H:%M") if messages else None,
            "end_time": messages[-1].created_at.strftime("%Y-%m-%d %H:%M") if messages else None,
        }

    def get_course_query_stats(self, days: int = 30) -> List[Dict]:
        """
        Get statistics on which courses are most queried about.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get user messages
        messages = Conversation.query.filter(
            and_(
                Conversation.created_at >= cutoff,
                Conversation.role == "user"
            )
        ).all()

        # Get all course codes
        courses = Course.query.all()
        course_codes = {c.code.lower(): c.code for c in courses}

        # Count mentions
        course_counts = Counter()
        for msg in messages:
            content = msg.content.lower()
            for code_lower, code in course_codes.items():
                # Check for variations like "cs 149", "cs149", "CS 149"
                variations = [
                    code_lower,
                    code_lower.replace(" ", ""),
                    code_lower.replace("-", ""),
                ]
                if any(v in content for v in variations):
                    course_counts[code] += 1

        # Format results
        results = []
        for code, count in course_counts.most_common(15):
            course = Course.query.filter_by(code=code).first()
            results.append({
                "code": code,
                "name": course.name if course else "Unknown",
                "count": count
            })

        return results

    def export_analytics_json(self, days: int = 30) -> Dict:
        """
        Export all analytics data as JSON.
        """
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "period_days": days,
            "overview": self.get_overview_stats(days),
            "daily_usage": self.get_daily_usage(days),
            "feedback": self.get_feedback_breakdown(days),
            "popular_topics": self.get_popular_topics(days),
            "course_queries": self.get_course_query_stats(days),
        }


# Singleton instance
_analytics: Optional[AnalyticsEngine] = None


def get_analytics_engine() -> AnalyticsEngine:
    """Get or create the analytics engine singleton"""
    global _analytics
    if _analytics is None:
        _analytics = AnalyticsEngine()
    return _analytics
