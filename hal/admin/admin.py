"""
Flask-Admin Interface for HAL Advisor Bot

Provides a web-based admin interface for managing:
- Courses and prerequisites
- Advisor assignments
- Policies and Q&A
- Deadlines
- Viewing feedback
- Analytics dashboard
"""
from functools import wraps
import json

from flask import redirect, url_for, request, flash, session, jsonify
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from wtforms import TextAreaField, SelectField, PasswordField
from wtforms.validators import DataRequired

from hal.models import db, Course, Advisor, Policy, Deadline, Feedback, Conversation, AdminUser
from hal.config import Config
from hal.admin.analytics import get_analytics_engine
from hal.admin.feedback_analyzer import get_feedback_analyzer


class AuthMixin:
    """Mixin for admin authentication"""

    def is_authenticated(self):
        return session.get("admin_logged_in", False)

    def is_accessible(self):
        return self.is_authenticated()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin.login"))


class SecureAdminIndexView(AuthMixin, AdminIndexView):
    """Secured admin index view with login"""

    @expose("/")
    def index(self):
        if not self.is_authenticated():
            return redirect(url_for(".login"))
        return super().index()

    @expose("/login", methods=["GET", "POST"])
    def login(self):
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            user = AdminUser.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session["admin_logged_in"] = True
                session["admin_user"] = username
                flash("Logged in successfully!", "success")
                return redirect(url_for(".index"))
            else:
                flash("Invalid credentials", "error")

        return self.render("admin/login.html")

    @expose("/logout")
    def logout(self):
        session.pop("admin_logged_in", None)
        session.pop("admin_user", None)
        flash("Logged out successfully", "info")
        return redirect(url_for(".login"))


class SecureModelView(AuthMixin, ModelView):
    """Base secure model view"""
    page_size = 50
    can_export = True
    can_view_details = True


class CourseView(SecureModelView):
    """Admin view for courses"""
    column_list = ["code", "name", "prerequisites", "units", "department", "updated_at"]
    column_searchable_list = ["code", "name", "description", "prerequisites"]
    column_filters = ["department", "units"]
    column_sortable_list = ["code", "name", "units", "updated_at"]
    column_default_sort = "code"

    form_overrides = {
        "description": TextAreaField,
        "prerequisites": TextAreaField,
        "prerequisites_cmpe": TextAreaField,
        "prerequisites_se": TextAreaField,
    }

    form_args = {
        "code": {"validators": [DataRequired()]},
        "name": {"validators": [DataRequired()]},
    }

    column_labels = {
        "code": "Course Code",
        "prerequisites_cmpe": "Prerequisites (CMPE)",
        "prerequisites_se": "Prerequisites (SE)",
    }

    column_descriptions = {
        "prerequisites": "General prerequisites for all majors",
        "prerequisites_cmpe": "Specific prerequisites for CMPE majors (if different)",
        "prerequisites_se": "Specific prerequisites for SE majors (if different)",
    }


class AdvisorView(SecureModelView):
    """Admin view for advisors"""
    column_list = ["name", "email", "last_name_start", "last_name_end", "department", "booking_url"]
    column_searchable_list = ["name", "email"]
    column_filters = ["department"]
    column_sortable_list = ["name", "last_name_start"]
    column_default_sort = "last_name_start"

    column_labels = {
        "last_name_start": "Last Name Start",
        "last_name_end": "Last Name End",
        "booking_url": "Booking URL",
    }


class PolicyView(SecureModelView):
    """Admin view for policies"""
    column_list = ["category", "question", "answer", "url", "updated_at"]
    column_searchable_list = ["question", "answer", "keywords"]
    column_filters = ["category"]
    column_sortable_list = ["category", "updated_at"]
    column_default_sort = "category"

    form_overrides = {
        "question": TextAreaField,
        "answer": TextAreaField,
        "keywords": TextAreaField,
    }

    form_args = {
        "category": {
            "validators": [DataRequired()],
        },
        "question": {"validators": [DataRequired()]},
        "answer": {"validators": [DataRequired()]},
    }

    column_descriptions = {
        "keywords": "Comma-separated keywords to help with matching",
    }


class DeadlineView(SecureModelView):
    """Admin view for deadlines"""
    column_list = ["semester", "deadline_type", "date", "description"]
    column_searchable_list = ["description"]
    column_filters = ["semester", "deadline_type"]
    column_sortable_list = ["date", "semester", "deadline_type"]
    column_default_sort = ("date", True)

    form_overrides = {
        "description": TextAreaField,
    }


class FeedbackView(SecureModelView):
    """Admin view for feedback (read-only)"""
    can_create = False
    can_edit = False
    can_delete = True

    column_list = ["created_at", "rating", "user_query", "bot_response", "comment"]
    column_filters = ["rating", "created_at"]
    column_sortable_list = ["created_at", "rating"]
    column_default_sort = ("created_at", True)

    column_labels = {
        "rating": "Rating (1=Bad, 2=Good)",
    }


class ConversationView(SecureModelView):
    """Admin view for conversations (read-only for analysis)"""
    can_create = False
    can_edit = False
    can_delete = True

    column_list = ["created_at", "session_id", "role", "content"]
    column_filters = ["role", "session_id", "created_at"]
    column_sortable_list = ["created_at", "session_id"]
    column_default_sort = ("created_at", True)


class AnalyticsDashboardView(AuthMixin, BaseView):
    """Analytics dashboard with charts and insights"""

    @expose("/")
    def index(self):
        if not self.is_authenticated():
            return redirect(url_for("admin.login"))

        analytics = get_analytics_engine()
        days = request.args.get("days", 30, type=int)

        # Get all analytics data
        overview = analytics.get_overview_stats(days)
        daily_usage = analytics.get_daily_usage(days)
        feedback = analytics.get_feedback_breakdown(days)
        topics = analytics.get_popular_topics(days)
        course_queries = analytics.get_course_query_stats(days)

        return self.render(
            "admin/analytics_dashboard.html",
            overview=overview,
            daily_usage=json.dumps(daily_usage),
            feedback=feedback,
            topics=topics,
            course_queries=course_queries,
            selected_days=days
        )

    @expose("/export")
    def export_data(self):
        if not self.is_authenticated():
            return redirect(url_for("admin.login"))

        analytics = get_analytics_engine()
        days = request.args.get("days", 30, type=int)
        data = analytics.export_analytics_json(days)

        return jsonify(data)

    @expose("/session/<session_id>")
    def session_detail(self, session_id):
        if not self.is_authenticated():
            return redirect(url_for("admin.login"))

        analytics = get_analytics_engine()
        session_data = analytics.get_session_details(session_id)

        return self.render(
            "admin/session_detail.html",
            session_data=session_data
        )


class FeedbackAnalysisView(AuthMixin, BaseView):
    """LLM-powered feedback analysis view"""

    @expose("/")
    def index(self):
        if not self.is_authenticated():
            return redirect(url_for("admin.login"))

        analyzer = get_feedback_analyzer()
        days = request.args.get("days", 30, type=int)

        # Get analysis
        insight = analyzer.analyze_recent_feedback(days=days)

        return self.render(
            "admin/feedback_analysis.html",
            insight=insight,
            selected_days=days
        )

    @expose("/weekly-report")
    def weekly_report(self):
        if not self.is_authenticated():
            return redirect(url_for("admin.login"))

        analyzer = get_feedback_analyzer()
        report = analyzer.generate_weekly_report()

        return jsonify(report)

    @expose("/suggestions/<topic>")
    def get_suggestions(self, topic):
        if not self.is_authenticated():
            return redirect(url_for("admin.login"))

        analyzer = get_feedback_analyzer()
        suggestions = analyzer.get_improvement_suggestions(topic)

        return jsonify({"topic": topic, "suggestions": suggestions})


def init_admin(app):
    """Initialize Flask-Admin with the app"""
    admin = Admin(
        app,
        name="HAL Admin",
        index_view=SecureAdminIndexView()
    )

    # Add model views
    admin.add_view(CourseView(Course, db.session, name="Courses", category="Content"))
    admin.add_view(AdvisorView(Advisor, db.session, name="Advisors", category="Content"))
    admin.add_view(PolicyView(Policy, db.session, name="Policies", category="Content"))
    admin.add_view(DeadlineView(Deadline, db.session, name="Deadlines", category="Content"))

    # Analytics views
    admin.add_view(AnalyticsDashboardView(name="Dashboard", endpoint="analytics", category="Analytics"))
    admin.add_view(FeedbackAnalysisView(name="AI Analysis", endpoint="feedback_analysis", category="Analytics"))
    admin.add_view(FeedbackView(Feedback, db.session, name="Raw Feedback", category="Analytics"))
    admin.add_view(ConversationView(Conversation, db.session, name="Conversations", category="Analytics"))

    return admin
