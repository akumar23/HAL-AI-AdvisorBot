"""
LLM-Powered Feedback Analyzer for HAL Advisor Bot

Provides:
- Batch analysis of negative feedback
- Theme extraction and categorization
- Actionable recommendations generation
- Periodic insight summaries
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import re

from sqlalchemy import and_, desc

from hal.models import db, Feedback
from hal.config import Config
from hal.services.llm_providers import get_llm_provider


@dataclass
class FeedbackInsight:
    """Result from feedback analysis"""
    summary: str
    themes: List[str]
    recommendations: List[str]
    sample_issues: List[Dict]
    analyzed_count: int
    analysis_date: str


class FeedbackAnalyzer:
    """
    LLM-powered feedback analyzer.

    Analyzes batches of user feedback to extract themes,
    identify common issues, and generate actionable recommendations.
    """

    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        """Lazy-load LLM provider (uses main model for better analysis)"""
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

    def analyze_recent_feedback(
        self,
        days: int = 30,
        min_feedback: int = 5,
        focus_negative: bool = True
    ) -> Optional[FeedbackInsight]:
        """
        Analyze recent feedback using LLM.

        Args:
            days: Number of days to analyze
            min_feedback: Minimum feedback count required
            focus_negative: Focus primarily on negative feedback

        Returns:
            FeedbackInsight with analysis results, or None if insufficient data
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Query feedback
        query = Feedback.query.filter(Feedback.created_at >= cutoff)
        if focus_negative:
            query = query.filter(Feedback.rating == 1)

        feedback_items = query.order_by(desc(Feedback.created_at)).limit(50).all()

        if len(feedback_items) < min_feedback:
            return None

        # Prepare feedback data for analysis
        feedback_data = []
        for fb in feedback_items:
            feedback_data.append({
                "query": fb.user_query[:200] if fb.user_query else "",
                "response": fb.bot_response[:300] if fb.bot_response else "",
                "comment": fb.comment or "",
                "date": fb.created_at.strftime("%Y-%m-%d")
            })

        # Generate analysis using LLM
        analysis = self._analyze_with_llm(feedback_data)

        return FeedbackInsight(
            summary=analysis.get("summary", ""),
            themes=analysis.get("themes", []),
            recommendations=analysis.get("recommendations", []),
            sample_issues=feedback_data[:5],
            analyzed_count=len(feedback_items),
            analysis_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        )

    def _analyze_with_llm(self, feedback_data: List[Dict]) -> Dict:
        """Use LLM to analyze feedback patterns"""

        # Format feedback for LLM
        feedback_text = ""
        for i, fb in enumerate(feedback_data[:20], 1):  # Limit to 20 for context
            feedback_text += f"\n--- Feedback #{i} ---\n"
            feedback_text += f"User Query: {fb['query']}\n"
            if fb['comment']:
                feedback_text += f"User Comment: {fb['comment']}\n"
            feedback_text += f"Bot Response (truncated): {fb['response'][:200]}...\n"

        prompt = f"""Analyze this collection of negative user feedback from an academic advising chatbot for SJSU Computer Engineering and Software Engineering students.

{feedback_text}

Provide your analysis in the following JSON format:
{{
    "summary": "A 2-3 sentence summary of the main issues users are experiencing",
    "themes": ["theme1", "theme2", "theme3"],
    "recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2",
        "Specific actionable recommendation 3"
    ]
}}

Focus on:
1. Common patterns in what users were asking about
2. Where the bot's responses fell short
3. Specific improvements that could be made to the knowledge base or response quality

Return ONLY valid JSON, no other text."""

        try:
            response = self.llm.generate_simple(prompt, max_tokens=800)
            return self._parse_analysis(response)
        except Exception as e:
            print(f"Error in LLM feedback analysis: {e}")
            return {
                "summary": "Unable to generate analysis",
                "themes": [],
                "recommendations": []
            }

    def _parse_analysis(self, response: str) -> Dict:
        """Parse LLM response to extract analysis"""
        try:
            # Find JSON in response
            response = response.strip()

            # Try to find JSON object
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                return json.loads(match.group())

        except json.JSONDecodeError:
            pass

        # Fallback: try to extract structured data manually
        result = {
            "summary": "",
            "themes": [],
            "recommendations": []
        }

        # Extract summary (first paragraph)
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('-', '*', '1', '2', '3')):
                result["summary"] = line
                break

        return result

    def get_improvement_suggestions(self, topic: str) -> List[str]:
        """
        Get specific improvement suggestions for a topic.

        Args:
            topic: Topic to get suggestions for (e.g., "prerequisites", "enrollment")

        Returns:
            List of improvement suggestions
        """
        prompt = f"""As an expert in academic advising chatbots, provide 3-5 specific, actionable suggestions to improve responses about "{topic}" for SJSU CMPE/SE students.

Focus on:
- What information students typically need
- Common misunderstandings to address
- How to make responses more helpful

Format as a numbered list. Be specific and practical."""

        try:
            response = self.llm.generate_simple(prompt, max_tokens=400)

            # Parse numbered list
            suggestions = []
            for line in response.split('\n'):
                line = line.strip()
                # Remove numbering
                line = re.sub(r'^[\d\.\)\-\*]+\s*', '', line)
                if line and len(line) > 10:
                    suggestions.append(line)

            return suggestions[:5]
        except Exception as e:
            print(f"Error getting improvement suggestions: {e}")
            return []

    def categorize_feedback(self, feedback_text: str) -> Dict:
        """
        Categorize a single piece of feedback.

        Args:
            feedback_text: The feedback comment to categorize

        Returns:
            Dict with category, sentiment, and priority
        """
        if not feedback_text or len(feedback_text) < 10:
            return {
                "category": "uncategorized",
                "sentiment": "neutral",
                "priority": "low"
            }

        prompt = f"""Categorize this user feedback from an academic advising chatbot:

"{feedback_text}"

Return JSON with:
- category: one of [accuracy, clarity, completeness, relevance, technical, other]
- sentiment: one of [frustrated, confused, disappointed, neutral]
- priority: one of [high, medium, low] based on impact

Return ONLY valid JSON."""

        try:
            response = self.llm.generate_simple(prompt, max_tokens=100)
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                return json.loads(match.group())
        except Exception:
            pass

        return {
            "category": "other",
            "sentiment": "neutral",
            "priority": "medium"
        }

    def generate_weekly_report(self) -> Dict:
        """
        Generate a weekly feedback report.

        Returns:
            Dict with weekly statistics and insights
        """
        insight = self.analyze_recent_feedback(days=7)

        if not insight:
            return {
                "status": "insufficient_data",
                "message": "Not enough feedback in the past week for analysis"
            }

        # Get comparison with previous week
        prev_week_start = datetime.utcnow() - timedelta(days=14)
        prev_week_end = datetime.utcnow() - timedelta(days=7)

        current_negative = Feedback.query.filter(
            and_(
                Feedback.created_at >= datetime.utcnow() - timedelta(days=7),
                Feedback.rating == 1
            )
        ).count()

        prev_negative = Feedback.query.filter(
            and_(
                Feedback.created_at >= prev_week_start,
                Feedback.created_at < prev_week_end,
                Feedback.rating == 1
            )
        ).count()

        trend = "improving" if current_negative < prev_negative else (
            "stable" if current_negative == prev_negative else "declining"
        )

        return {
            "status": "success",
            "report_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "insight": {
                "summary": insight.summary,
                "themes": insight.themes,
                "recommendations": insight.recommendations,
                "analyzed_count": insight.analyzed_count
            },
            "comparison": {
                "current_week_negative": current_negative,
                "previous_week_negative": prev_negative,
                "trend": trend
            }
        }


# Singleton instance
_analyzer: Optional[FeedbackAnalyzer] = None


def get_feedback_analyzer() -> FeedbackAnalyzer:
    """Get or create the feedback analyzer singleton"""
    global _analyzer
    if _analyzer is None:
        _analyzer = FeedbackAnalyzer()
    return _analyzer
