"""
Admin API Endpoints for HAL Advisor Bot

REST API endpoints for the Next.js admin frontend.
Provides authentication, CRUD operations, and analytics.
"""
from functools import wraps
from flask import Blueprint, request, jsonify, session
from hal.models import db, Course, Advisor, Policy, Deadline, Feedback, Conversation, AdminUser
from hal.admin.analytics import get_analytics_engine
from hal.admin.feedback_analyzer import get_feedback_analyzer

admin_api = Blueprint("admin_api", __name__, url_prefix="/api/admin")


def admin_required(f):
    """Decorator to require admin authentication for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# Authentication Endpoints
# =============================================================================

@admin_api.route("/login", methods=["POST"])
def login():
    """Admin login endpoint"""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = AdminUser.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session["admin_logged_in"] = True
        session["admin_user"] = username
        return jsonify({
            "success": True,
            "message": "Logged in successfully",
            "user": username
        })
    
    return jsonify({"error": "Invalid credentials"}), 401


@admin_api.route("/logout", methods=["POST"])
def logout():
    """Admin logout endpoint"""
    session.pop("admin_logged_in", None)
    session.pop("admin_user", None)
    return jsonify({"success": True, "message": "Logged out successfully"})


@admin_api.route("/check-auth", methods=["GET"])
def check_auth():
    """Check if user is authenticated"""
    if session.get("admin_logged_in"):
        return jsonify({
            "authenticated": True,
            "user": session.get("admin_user")
        })
    return jsonify({"authenticated": False})


# =============================================================================
# Analytics Endpoints
# =============================================================================

@admin_api.route("/analytics/overview", methods=["GET"])
@admin_required
def analytics_overview():
    """Get overview statistics"""
    days = request.args.get("days", 30, type=int)
    analytics = get_analytics_engine()
    return jsonify(analytics.get_overview_stats(days))


@admin_api.route("/analytics/daily-usage", methods=["GET"])
@admin_required
def analytics_daily_usage():
    """Get daily usage statistics"""
    days = request.args.get("days", 30, type=int)
    analytics = get_analytics_engine()
    return jsonify(analytics.get_daily_usage(days))


@admin_api.route("/analytics/feedback-breakdown", methods=["GET"])
@admin_required
def analytics_feedback_breakdown():
    """Get feedback breakdown"""
    days = request.args.get("days", 30, type=int)
    analytics = get_analytics_engine()
    return jsonify(analytics.get_feedback_breakdown(days))


@admin_api.route("/analytics/popular-topics", methods=["GET"])
@admin_required
def analytics_popular_topics():
    """Get popular topics"""
    days = request.args.get("days", 30, type=int)
    analytics = get_analytics_engine()
    return jsonify(analytics.get_popular_topics(days))


@admin_api.route("/analytics/course-queries", methods=["GET"])
@admin_required
def analytics_course_queries():
    """Get course query statistics"""
    days = request.args.get("days", 30, type=int)
    analytics = get_analytics_engine()
    return jsonify(analytics.get_course_query_stats(days))


@admin_api.route("/analytics/export", methods=["GET"])
@admin_required
def analytics_export():
    """Export all analytics data"""
    days = request.args.get("days", 30, type=int)
    analytics = get_analytics_engine()
    return jsonify(analytics.export_analytics_json(days))


@admin_api.route("/analytics/session/<session_id>", methods=["GET"])
@admin_required
def analytics_session_detail(session_id):
    """Get session details"""
    analytics = get_analytics_engine()
    return jsonify(analytics.get_session_details(session_id))


# =============================================================================
# AI Feedback Analysis Endpoints
# =============================================================================

@admin_api.route("/feedback-analysis", methods=["GET"])
@admin_required
def feedback_analysis():
    """Get AI-powered feedback analysis"""
    days = request.args.get("days", 30, type=int)
    analyzer = get_feedback_analyzer()
    insight = analyzer.analyze_recent_feedback(days=days)
    
    return jsonify({
        "summary": insight.summary,
        "themes": insight.themes,
        "recommendations": insight.recommendations,
        "sample_issues": insight.sample_issues,
        "analyzed_count": insight.analyzed_count,
        "analysis_date": insight.analysis_date
    })


@admin_api.route("/feedback-analysis/weekly-report", methods=["GET"])
@admin_required
def feedback_weekly_report():
    """Get weekly feedback report"""
    analyzer = get_feedback_analyzer()
    return jsonify(analyzer.generate_weekly_report())


@admin_api.route("/feedback-analysis/suggestions/<topic>", methods=["GET"])
@admin_required
def feedback_suggestions(topic):
    """Get improvement suggestions for a topic"""
    analyzer = get_feedback_analyzer()
    suggestions = analyzer.get_improvement_suggestions(topic)
    return jsonify({"topic": topic, "suggestions": suggestions})


# =============================================================================
# Course CRUD Endpoints
# =============================================================================

@admin_api.route("/courses", methods=["GET"])
@admin_required
def list_courses():
    """List all courses with pagination and search"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    search = request.args.get("search", "").strip()
    department = request.args.get("department", "").strip()

    query = Course.query

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                Course.code.ilike(search_filter),
                Course.name.ilike(search_filter),
                Course.description.ilike(search_filter)
            )
        )

    if department:
        query = query.filter(Course.department == department)

    query = query.order_by(Course.code)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [_course_to_dict(c) for c in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    })


@admin_api.route("/courses/<int:course_id>", methods=["GET"])
@admin_required
def get_course(course_id):
    """Get a single course"""
    course = Course.query.get_or_404(course_id)
    return jsonify(_course_to_dict(course))


@admin_api.route("/courses", methods=["POST"])
@admin_required
def create_course():
    """Create a new course"""
    data = request.get_json() or {}
    
    if not data.get("code") or not data.get("name"):
        return jsonify({"error": "Code and name are required"}), 400

    if Course.query.filter_by(code=data["code"]).first():
        return jsonify({"error": "Course code already exists"}), 400

    course = Course(
        code=data["code"],
        name=data["name"],
        description=data.get("description"),
        prerequisites=data.get("prerequisites"),
        prerequisites_cmpe=data.get("prerequisites_cmpe"),
        prerequisites_se=data.get("prerequisites_se"),
        units=data.get("units", 3),
        department=data.get("department")
    )
    db.session.add(course)
    db.session.commit()

    return jsonify(_course_to_dict(course)), 201


@admin_api.route("/courses/<int:course_id>", methods=["PUT"])
@admin_required
def update_course(course_id):
    """Update a course"""
    course = Course.query.get_or_404(course_id)
    data = request.get_json() or {}

    if "code" in data:
        existing = Course.query.filter_by(code=data["code"]).first()
        if existing and existing.id != course_id:
            return jsonify({"error": "Course code already exists"}), 400
        course.code = data["code"]

    if "name" in data:
        course.name = data["name"]
    if "description" in data:
        course.description = data["description"]
    if "prerequisites" in data:
        course.prerequisites = data["prerequisites"]
    if "prerequisites_cmpe" in data:
        course.prerequisites_cmpe = data["prerequisites_cmpe"]
    if "prerequisites_se" in data:
        course.prerequisites_se = data["prerequisites_se"]
    if "units" in data:
        course.units = data["units"]
    if "department" in data:
        course.department = data["department"]

    db.session.commit()
    return jsonify(_course_to_dict(course))


@admin_api.route("/courses/<int:course_id>", methods=["DELETE"])
@admin_required
def delete_course(course_id):
    """Delete a course"""
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return jsonify({"success": True})


def _course_to_dict(course):
    return {
        "id": course.id,
        "code": course.code,
        "name": course.name,
        "description": course.description,
        "prerequisites": course.prerequisites,
        "prerequisites_cmpe": course.prerequisites_cmpe,
        "prerequisites_se": course.prerequisites_se,
        "units": course.units,
        "department": course.department,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "updated_at": course.updated_at.isoformat() if course.updated_at else None
    }


# =============================================================================
# Advisor CRUD Endpoints
# =============================================================================

@admin_api.route("/advisors", methods=["GET"])
@admin_required
def list_advisors():
    """List all advisors"""
    advisors = Advisor.query.order_by(Advisor.last_name_start).all()
    return jsonify({
        "items": [_advisor_to_dict(a) for a in advisors]
    })


@admin_api.route("/advisors/<int:advisor_id>", methods=["GET"])
@admin_required
def get_advisor(advisor_id):
    """Get a single advisor"""
    advisor = Advisor.query.get_or_404(advisor_id)
    return jsonify(_advisor_to_dict(advisor))


@admin_api.route("/advisors", methods=["POST"])
@admin_required
def create_advisor():
    """Create a new advisor"""
    data = request.get_json() or {}
    
    if not data.get("name") or not data.get("last_name_start") or not data.get("last_name_end"):
        return jsonify({"error": "Name, last_name_start, and last_name_end are required"}), 400

    advisor = Advisor(
        name=data["name"],
        email=data.get("email"),
        booking_url=data.get("booking_url"),
        last_name_start=data["last_name_start"].upper(),
        last_name_end=data["last_name_end"].upper(),
        department=data.get("department", "CMPE/SE")
    )
    db.session.add(advisor)
    db.session.commit()

    return jsonify(_advisor_to_dict(advisor)), 201


@admin_api.route("/advisors/<int:advisor_id>", methods=["PUT"])
@admin_required
def update_advisor(advisor_id):
    """Update an advisor"""
    advisor = Advisor.query.get_or_404(advisor_id)
    data = request.get_json() or {}

    if "name" in data:
        advisor.name = data["name"]
    if "email" in data:
        advisor.email = data["email"]
    if "booking_url" in data:
        advisor.booking_url = data["booking_url"]
    if "last_name_start" in data:
        advisor.last_name_start = data["last_name_start"].upper()
    if "last_name_end" in data:
        advisor.last_name_end = data["last_name_end"].upper()
    if "department" in data:
        advisor.department = data["department"]

    db.session.commit()
    return jsonify(_advisor_to_dict(advisor))


@admin_api.route("/advisors/<int:advisor_id>", methods=["DELETE"])
@admin_required
def delete_advisor(advisor_id):
    """Delete an advisor"""
    advisor = Advisor.query.get_or_404(advisor_id)
    db.session.delete(advisor)
    db.session.commit()
    return jsonify({"success": True})


def _advisor_to_dict(advisor):
    return {
        "id": advisor.id,
        "name": advisor.name,
        "email": advisor.email,
        "booking_url": advisor.booking_url,
        "last_name_start": advisor.last_name_start,
        "last_name_end": advisor.last_name_end,
        "department": advisor.department,
        "created_at": advisor.created_at.isoformat() if advisor.created_at else None,
        "updated_at": advisor.updated_at.isoformat() if advisor.updated_at else None
    }


# =============================================================================
# Policy CRUD Endpoints
# =============================================================================

@admin_api.route("/policies", methods=["GET"])
@admin_required
def list_policies():
    """List all policies"""
    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()

    query = Policy.query

    if category:
        query = query.filter(Policy.category == category)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                Policy.question.ilike(search_filter),
                Policy.answer.ilike(search_filter),
                Policy.keywords.ilike(search_filter)
            )
        )

    policies = query.order_by(Policy.category, Policy.id).all()
    return jsonify({
        "items": [_policy_to_dict(p) for p in policies],
        "categories": Policy.CATEGORIES
    })


@admin_api.route("/policies/<int:policy_id>", methods=["GET"])
@admin_required
def get_policy(policy_id):
    """Get a single policy"""
    policy = Policy.query.get_or_404(policy_id)
    return jsonify(_policy_to_dict(policy))


@admin_api.route("/policies", methods=["POST"])
@admin_required
def create_policy():
    """Create a new policy"""
    data = request.get_json() or {}
    
    if not data.get("category") or not data.get("question") or not data.get("answer"):
        return jsonify({"error": "Category, question, and answer are required"}), 400

    policy = Policy(
        category=data["category"],
        question=data["question"],
        answer=data["answer"],
        keywords=data.get("keywords"),
        url=data.get("url")
    )
    db.session.add(policy)
    db.session.commit()

    return jsonify(_policy_to_dict(policy)), 201


@admin_api.route("/policies/<int:policy_id>", methods=["PUT"])
@admin_required
def update_policy(policy_id):
    """Update a policy"""
    policy = Policy.query.get_or_404(policy_id)
    data = request.get_json() or {}

    if "category" in data:
        policy.category = data["category"]
    if "question" in data:
        policy.question = data["question"]
    if "answer" in data:
        policy.answer = data["answer"]
    if "keywords" in data:
        policy.keywords = data["keywords"]
    if "url" in data:
        policy.url = data["url"]

    db.session.commit()
    return jsonify(_policy_to_dict(policy))


@admin_api.route("/policies/<int:policy_id>", methods=["DELETE"])
@admin_required
def delete_policy(policy_id):
    """Delete a policy"""
    policy = Policy.query.get_or_404(policy_id)
    db.session.delete(policy)
    db.session.commit()
    return jsonify({"success": True})


def _policy_to_dict(policy):
    return {
        "id": policy.id,
        "category": policy.category,
        "question": policy.question,
        "answer": policy.answer,
        "keywords": policy.keywords,
        "url": policy.url,
        "created_at": policy.created_at.isoformat() if policy.created_at else None,
        "updated_at": policy.updated_at.isoformat() if policy.updated_at else None
    }


# =============================================================================
# Deadline CRUD Endpoints
# =============================================================================

@admin_api.route("/deadlines", methods=["GET"])
@admin_required
def list_deadlines():
    """List all deadlines"""
    semester = request.args.get("semester", "").strip()
    deadline_type = request.args.get("deadline_type", "").strip()

    query = Deadline.query

    if semester:
        query = query.filter(Deadline.semester == semester)

    if deadline_type:
        query = query.filter(Deadline.deadline_type == deadline_type)

    deadlines = query.order_by(Deadline.date.desc()).all()
    
    # Get unique semesters for filter dropdown
    semesters = db.session.query(Deadline.semester).distinct().all()
    
    return jsonify({
        "items": [_deadline_to_dict(d) for d in deadlines],
        "deadline_types": Deadline.DEADLINE_TYPES,
        "semesters": [s[0] for s in semesters]
    })


@admin_api.route("/deadlines/<int:deadline_id>", methods=["GET"])
@admin_required
def get_deadline(deadline_id):
    """Get a single deadline"""
    deadline = Deadline.query.get_or_404(deadline_id)
    return jsonify(_deadline_to_dict(deadline))


@admin_api.route("/deadlines", methods=["POST"])
@admin_required
def create_deadline():
    """Create a new deadline"""
    data = request.get_json() or {}
    
    if not data.get("semester") or not data.get("deadline_type") or not data.get("date"):
        return jsonify({"error": "Semester, deadline_type, and date are required"}), 400

    from datetime import datetime
    try:
        date = datetime.strptime(data["date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    deadline = Deadline(
        semester=data["semester"],
        deadline_type=data["deadline_type"],
        date=date,
        description=data.get("description"),
        url=data.get("url")
    )
    db.session.add(deadline)
    db.session.commit()

    return jsonify(_deadline_to_dict(deadline)), 201


@admin_api.route("/deadlines/<int:deadline_id>", methods=["PUT"])
@admin_required
def update_deadline(deadline_id):
    """Update a deadline"""
    deadline = Deadline.query.get_or_404(deadline_id)
    data = request.get_json() or {}

    if "semester" in data:
        deadline.semester = data["semester"]
    if "deadline_type" in data:
        deadline.deadline_type = data["deadline_type"]
    if "date" in data:
        from datetime import datetime
        try:
            deadline.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    if "description" in data:
        deadline.description = data["description"]
    if "url" in data:
        deadline.url = data["url"]

    db.session.commit()
    return jsonify(_deadline_to_dict(deadline))


@admin_api.route("/deadlines/<int:deadline_id>", methods=["DELETE"])
@admin_required
def delete_deadline(deadline_id):
    """Delete a deadline"""
    deadline = Deadline.query.get_or_404(deadline_id)
    db.session.delete(deadline)
    db.session.commit()
    return jsonify({"success": True})


def _deadline_to_dict(deadline):
    return {
        "id": deadline.id,
        "semester": deadline.semester,
        "deadline_type": deadline.deadline_type,
        "date": deadline.date.isoformat() if deadline.date else None,
        "description": deadline.description,
        "url": deadline.url,
        "created_at": deadline.created_at.isoformat() if deadline.created_at else None,
        "updated_at": deadline.updated_at.isoformat() if deadline.updated_at else None
    }


# =============================================================================
# Feedback Read-Only Endpoints
# =============================================================================

@admin_api.route("/feedback", methods=["GET"])
@admin_required
def list_feedback():
    """List all feedback with pagination"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    rating = request.args.get("rating", type=int)

    query = Feedback.query

    if rating:
        query = query.filter(Feedback.rating == rating)

    query = query.order_by(Feedback.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [_feedback_to_dict(f) for f in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    })


@admin_api.route("/feedback/<int:feedback_id>", methods=["DELETE"])
@admin_required
def delete_feedback(feedback_id):
    """Delete a feedback entry"""
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    return jsonify({"success": True})


def _feedback_to_dict(feedback):
    return {
        "id": feedback.id,
        "session_id": feedback.session_id,
        "user_query": feedback.user_query,
        "bot_response": feedback.bot_response,
        "rating": feedback.rating,
        "comment": feedback.comment,
        "created_at": feedback.created_at.isoformat() if feedback.created_at else None
    }


# =============================================================================
# Conversation Read-Only Endpoints
# =============================================================================

@admin_api.route("/conversations", methods=["GET"])
@admin_required
def list_conversations():
    """List conversation sessions with pagination"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    # Get distinct sessions with their message counts
    from sqlalchemy import func
    
    subquery = db.session.query(
        Conversation.session_id,
        func.count(Conversation.id).label("message_count"),
        func.max(Conversation.created_at).label("last_message")
    ).group_by(Conversation.session_id).subquery()

    query = db.session.query(subquery).order_by(subquery.c.last_message.desc())
    
    # Manual pagination
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        "items": [{
            "session_id": item.session_id,
            "message_count": item.message_count,
            "last_message": item.last_message.isoformat() if item.last_message else None
        } for item in items],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    })


@admin_api.route("/conversations/<session_id>", methods=["GET"])
@admin_required
def get_conversation(session_id):
    """Get all messages in a conversation session"""
    messages = Conversation.query.filter_by(
        session_id=session_id
    ).order_by(Conversation.created_at).all()

    return jsonify({
        "session_id": session_id,
        "messages": [{
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat() if m.created_at else None
        } for m in messages]
    })


@admin_api.route("/conversations/<session_id>", methods=["DELETE"])
@admin_required
def delete_conversation(session_id):
    """Delete all messages in a conversation session"""
    Conversation.query.filter_by(session_id=session_id).delete()
    db.session.commit()
    return jsonify({"success": True})
