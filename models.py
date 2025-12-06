"""
Database Models for HAL Advisor Bot

SQLAlchemy models for storing advising data, replacing the static
trainingData.py dictionaries with a proper database structure.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Course(db.Model):
    """Course information including prerequisites and descriptions"""
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    prerequisites = db.Column(db.Text)  # Prerequisites description
    prerequisites_cmpe = db.Column(db.Text)  # CMPE-specific prerequisites
    prerequisites_se = db.Column(db.Text)  # SE-specific prerequisites
    units = db.Column(db.Integer, default=3)
    department = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Course {self.code}: {self.name}>"

    def get_prerequisites(self, major=None):
        """Get prerequisites, optionally specific to a major"""
        if major == "cmpe" and self.prerequisites_cmpe:
            return self.prerequisites_cmpe
        elif major == "se" and self.prerequisites_se:
            return self.prerequisites_se
        return self.prerequisites

    def to_document(self):
        """Convert to document format for RAG indexing"""
        parts = [f"Course: {self.code} - {self.name}"]
        if self.description:
            parts.append(f"Description: {self.description}")
        if self.prerequisites:
            parts.append(f"Prerequisites: {self.prerequisites}")
        if self.prerequisites_cmpe:
            parts.append(f"Prerequisites for CMPE majors: {self.prerequisites_cmpe}")
        if self.prerequisites_se:
            parts.append(f"Prerequisites for SE majors: {self.prerequisites_se}")
        return "\n".join(parts)


class Advisor(db.Model):
    """Advisor assignments by last name initial"""
    __tablename__ = "advisors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200))
    booking_url = db.Column(db.String(500))
    last_name_start = db.Column(db.String(1), nullable=False)  # Starting letter
    last_name_end = db.Column(db.String(1), nullable=False)  # Ending letter
    department = db.Column(db.String(100), default="CMPE/SE")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Advisor {self.name} ({self.last_name_start}-{self.last_name_end})>"

    def to_document(self):
        """Convert to document format for RAG indexing"""
        return (
            f"Advisor: {self.name}\n"
            f"Handles students with last names starting with {self.last_name_start} through {self.last_name_end}\n"
            f"Department: {self.department}\n"
            f"Booking URL: {self.booking_url}"
        )


class Policy(db.Model):
    """Academic policies and general advising Q&A"""
    __tablename__ = "policies"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text)  # Comma-separated keywords for matching
    url = db.Column(db.String(500))  # Related URL if any
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Categories for organizing policies
    CATEGORIES = [
        "enrollment",
        "grades",
        "graduation",
        "refunds",
        "transfer",
        "waitlist",
        "units",
        "general",
    ]

    def __repr__(self):
        return f"<Policy [{self.category}] {self.question[:50]}...>"

    def to_document(self):
        """Convert to document format for RAG indexing"""
        doc = f"Category: {self.category}\nQuestion: {self.question}\nAnswer: {self.answer}"
        if self.url:
            doc += f"\nMore info: {self.url}"
        return doc


class Deadline(db.Model):
    """Important academic deadlines"""
    __tablename__ = "deadlines"

    id = db.Column(db.Integer, primary_key=True)
    semester = db.Column(db.String(20), nullable=False)  # e.g., "Spring 2025"
    deadline_type = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    DEADLINE_TYPES = [
        "add_classes",
        "drop_classes",
        "late_add",
        "withdrawal",
        "grade_change",
        "graduation_application",
    ]

    def __repr__(self):
        return f"<Deadline {self.deadline_type} - {self.date}>"

    def to_document(self):
        """Convert to document format for RAG indexing"""
        return (
            f"Deadline: {self.deadline_type}\n"
            f"Semester: {self.semester}\n"
            f"Date: {self.date.strftime('%B %d, %Y')}\n"
            f"Description: {self.description}"
        )


class Conversation(db.Model):
    """Conversation history for context retention"""
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # "user" or "assistant"
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Conversation {self.session_id} - {self.role}>"


class Feedback(db.Model):
    """User feedback on responses for continuous improvement"""
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), index=True)
    user_query = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1 = thumbs down, 2 = thumbs up
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback {self.id} - Rating: {self.rating}>"


class AdminUser(db.Model):
    """Admin users for the Flask-Admin interface"""
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<AdminUser {self.username}>"


def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Create default admin user if none exists
        if not AdminUser.query.first():
            from config import Config
            admin = AdminUser(username=Config.ADMIN_USERNAME)
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
