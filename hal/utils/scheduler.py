"""
Background Job Scheduler for HAL Advisor Bot

Handles periodic tasks like:
- Weekly feedback analysis reports
- Analytics aggregation
- Database cleanup
- RAG index updates
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable
import json
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HALScheduler:
    """
    Background job scheduler for HAL Advisor Bot.

    Manages periodic tasks for analytics, maintenance, and reporting.
    """

    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        self._initialized = False

    def init_app(self, app):
        """Initialize scheduler with Flask app context"""
        self.app = app
        self._setup_jobs()
        self._initialized = True

    def _setup_jobs(self):
        """Set up all scheduled jobs"""

        # Weekly feedback analysis - every Monday at 6 AM
        self.scheduler.add_job(
            func=self._run_with_context(self._weekly_feedback_analysis),
            trigger=CronTrigger(day_of_week='mon', hour=6, minute=0),
            id='weekly_feedback_analysis',
            name='Weekly Feedback Analysis',
            replace_existing=True
        )

        # Daily analytics aggregation - every day at 2 AM
        self.scheduler.add_job(
            func=self._run_with_context(self._daily_analytics_aggregation),
            trigger=CronTrigger(hour=2, minute=0),
            id='daily_analytics',
            name='Daily Analytics Aggregation',
            replace_existing=True
        )

        # Hourly RAG index check - every hour
        self.scheduler.add_job(
            func=self._run_with_context(self._check_rag_index),
            trigger=IntervalTrigger(hours=1),
            id='rag_index_check',
            name='RAG Index Health Check',
            replace_existing=True
        )

        # Weekly cleanup - every Sunday at 3 AM
        self.scheduler.add_job(
            func=self._run_with_context(self._weekly_cleanup),
            trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
            id='weekly_cleanup',
            name='Weekly Database Cleanup',
            replace_existing=True
        )

        logger.info("Scheduled jobs configured")

    def _run_with_context(self, func: Callable) -> Callable:
        """Wrap function to run within Flask app context"""
        def wrapper(*args, **kwargs):
            if self.app:
                with self.app.app_context():
                    return func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper

    def _weekly_feedback_analysis(self):
        """Generate weekly feedback analysis report"""
        logger.info("Running weekly feedback analysis...")

        try:
            from hal.admin.feedback_analyzer import get_feedback_analyzer

            analyzer = get_feedback_analyzer()
            report = analyzer.generate_weekly_report()

            # Save report to file
            report_dir = os.path.join(
                os.path.dirname(__file__),
                'reports'
            )
            os.makedirs(report_dir, exist_ok=True)

            report_path = os.path.join(
                report_dir,
                f"weekly_report_{datetime.utcnow().strftime('%Y%m%d')}.json"
            )

            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)

            logger.info(f"Weekly report saved to {report_path}")

            # Could also send email notification here
            if report.get('status') == 'success':
                insight = report.get('insight', {})
                logger.info(f"Analysis: {insight.get('summary', 'No summary')}")
                logger.info(f"Themes: {insight.get('themes', [])}")

        except Exception as e:
            logger.error(f"Error in weekly feedback analysis: {e}")

    def _daily_analytics_aggregation(self):
        """Aggregate daily analytics data"""
        logger.info("Running daily analytics aggregation...")

        try:
            from hal.admin.analytics import get_analytics_engine

            analytics = get_analytics_engine()

            # Get yesterday's stats
            stats = analytics.get_overview_stats(days=1)

            # Log summary
            logger.info(f"Yesterday's stats: {stats['total_sessions']} sessions, "
                       f"{stats['user_messages']} questions, "
                       f"{stats['satisfaction_rate']}% satisfaction")

            # Could store in a daily_stats table for historical tracking

        except Exception as e:
            logger.error(f"Error in daily analytics: {e}")

    def _check_rag_index(self):
        """Check RAG index health"""
        logger.info("Checking RAG index health...")

        try:
            from hal.services.rag_engine import get_rag_engine

            rag = get_rag_engine()

            # Check collection exists and has documents
            collection = rag.collection
            count = collection.count()

            if count == 0:
                logger.warning("RAG index is empty! Consider re-indexing.")
            else:
                logger.info(f"RAG index healthy: {count} documents indexed")

        except Exception as e:
            logger.error(f"Error checking RAG index: {e}")

    def _weekly_cleanup(self):
        """Clean up old data"""
        logger.info("Running weekly cleanup...")

        try:
            from hal.models import db, Conversation
            from datetime import datetime, timedelta

            # Delete conversations older than 90 days
            cutoff = datetime.utcnow() - timedelta(days=90)
            deleted = Conversation.query.filter(
                Conversation.created_at < cutoff
            ).delete()

            db.session.commit()
            logger.info(f"Deleted {deleted} old conversation records")

        except Exception as e:
            logger.error(f"Error in weekly cleanup: {e}")

    def start(self):
        """Start the scheduler"""
        if not self._initialized:
            logger.warning("Scheduler not initialized with app context")

        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Background scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Background scheduler stopped")

    def get_jobs(self):
        """Get list of scheduled jobs"""
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            for job in self.scheduler.get_jobs()
        ]

    def run_job_now(self, job_id: str):
        """Manually trigger a job to run immediately"""
        job = self.scheduler.get_job(job_id)
        if job:
            job.func()
            return True
        return False


# Singleton instance
_scheduler: Optional[HALScheduler] = None


def get_scheduler() -> HALScheduler:
    """Get or create the scheduler singleton"""
    global _scheduler
    if _scheduler is None:
        _scheduler = HALScheduler()
    return _scheduler


def init_scheduler(app):
    """Initialize and start the scheduler with Flask app"""
    scheduler = get_scheduler()
    scheduler.init_app(app)
    scheduler.start()
    return scheduler
