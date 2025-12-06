"""
Migration Script for HAL Advisor Bot

Imports existing training data from trainingData.py into the SQLite database.
Run this once after setting up the new architecture.
"""
import re
import sys
from datetime import datetime

# Import the Flask app to get the application context
from app import create_app
from models import db, Course, Advisor, Policy, Deadline, AdminUser
from rag_engine import get_rag_engine

# Import the old training data
import trainingData


def parse_course_code(tag: str) -> str:
    """Normalize course code (e.g., 'cs149' -> 'CS 149')"""
    # Remove spaces and convert to uppercase
    tag = tag.strip().upper()
    # Add space between letters and numbers if missing
    match = re.match(r'([A-Z]+)\s*(\d+[A-Z]?)', tag)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return tag


def migrate_courses():
    """Migrate course data from overallPrereq"""
    print("Migrating courses...")
    courses_added = 0
    seen_codes = set()

    for item in trainingData.overallPrereq:
        tag = item.get("tag", "")
        code = parse_course_code(tag)

        # Skip duplicates (entries like 'cs149' and 'cs 149' are the same)
        if code in seen_codes:
            continue
        seen_codes.add(code)

        # Skip the special "how many units" entry
        if "units" in tag.lower():
            continue

        responses = item.get("responses", [])
        prerequisites = responses[0] if len(responses) > 0 else None
        description = responses[1] if len(responses) > 1 else None

        # Extract course name from description if available
        name = None
        if description and "called" in description.lower():
            # Try to extract name like "This class is called Operating Systems and..."
            match = re.search(r'called\s+([^\.]+?)(?:\s+and\s+it|\s+which|\s+that|\.)', description, re.IGNORECASE)
            if match:
                name = match.group(1).strip()

        if not name:
            name = code  # Fallback to code as name

        # Check for major-specific prerequisites
        prereq_cmpe = None
        prereq_se = None
        if prerequisites:
            lower_prereq = prerequisites.lower()
            if "cmpe major" in lower_prereq or "for cmpe" in lower_prereq:
                prereq_cmpe = prerequisites
                prereq_se = prerequisites
                prerequisites = None  # Will be extracted per-major

        # Determine department
        if code.startswith("CS"):
            department = "Computer Science"
        elif code.startswith("CMPE"):
            department = "Computer Engineering"
        elif code.startswith("ISE"):
            department = "Industrial Systems Engineering"
        elif code.startswith("ENGR"):
            department = "Engineering"
        else:
            department = "Other"

        course = Course(
            code=code,
            name=name,
            description=description,
            prerequisites=prerequisites,
            prerequisites_cmpe=prereq_cmpe,
            prerequisites_se=prereq_se,
            department=department
        )
        db.session.add(course)
        courses_added += 1

    db.session.commit()
    print(f"  Added {courses_added} courses")


def migrate_advisors():
    """Migrate advisor data"""
    print("Migrating advisors...")

    # From the training data, we know:
    # A-L: Christine Watson
    # M-Z: Monica Serna
    advisors = [
        {
            "name": "Christine Watson",
            "last_name_start": "A",
            "last_name_end": "L",
            "booking_url": "https://sjsu.campus.eab.com/student/appointments/new",
            "department": "CMPE/SE"
        },
        {
            "name": "Monica Serna",
            "last_name_start": "M",
            "last_name_end": "Z",
            "booking_url": "https://sjsu.campus.eab.com/student/appointments/new",
            "department": "CMPE/SE"
        }
    ]

    for adv_data in advisors:
        advisor = Advisor(**adv_data)
        db.session.add(advisor)

    db.session.commit()
    print(f"  Added {len(advisors)} advisors")


def migrate_policies():
    """Migrate policies from basicAdvice and other training data"""
    print("Migrating policies...")
    policies_added = 0

    # Parse basicAdvice (question/answer pairs)
    basic_advice = trainingData.basicAdvice
    i = 0
    while i < len(basic_advice) - 1:
        question = basic_advice[i]
        answer = basic_advice[i + 1]

        # Skip if this is a duplicate question (lowercase variations)
        if i > 0 and question.lower() == basic_advice[i - 2].lower():
            i += 2
            continue

        # Determine category
        question_lower = question.lower()
        if any(word in question_lower for word in ["gpa", "grade"]):
            category = "grades"
        elif any(word in question_lower for word in ["graduation", "graduate"]):
            category = "graduation"
        elif any(word in question_lower for word in ["refund", "drop"]):
            category = "refunds"
        elif any(word in question_lower for word in ["add", "enroll", "waitlist"]):
            category = "enrollment"
        elif any(word in question_lower for word in ["unit"]):
            category = "units"
        elif any(word in question_lower for word in ["transfer", "community college"]):
            category = "transfer"
        elif any(word in question_lower for word in ["fail", "retake"]):
            category = "grades"
        else:
            category = "general"

        # Extract URL if present in answer
        url = None
        url_match = re.search(r'https?://[^\s]+', answer)
        if url_match:
            url = url_match.group(0).rstrip('.')

        policy = Policy(
            category=category,
            question=question,
            answer=answer,
            url=url
        )
        db.session.add(policy)
        policies_added += 1
        i += 2

    # Add policies from addAndDrop
    for item in trainingData.addAndDrop:
        tag = item.get("tag", "")
        responses = item.get("responses", [])
        patterns = item.get("patterns", [])

        if responses and patterns:
            question = patterns[0]
            answer = responses[0]

            policy = Policy(
                category="enrollment",
                question=question,
                answer=answer,
                keywords=tag
            )
            db.session.add(policy)
            policies_added += 1

    db.session.commit()
    print(f"  Added {policies_added} policies")


def migrate_casual_conversation():
    """Migrate casual conversation as general policies"""
    print("Migrating casual conversation...")
    # Skip these for now - RAG handles general conversation differently
    print("  Skipped (handled by LLM naturally)")


def index_documents():
    """Index all documents into ChromaDB for RAG"""
    print("Indexing documents for RAG...")
    rag = get_rag_engine()
    rag.index_all_documents()
    print("  Indexing complete")


def create_admin_user():
    """Ensure admin user exists"""
    print("Checking admin user...")
    if not AdminUser.query.first():
        from config import Config
        admin = AdminUser(username=Config.ADMIN_USERNAME)
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"  Created admin user: {Config.ADMIN_USERNAME}")
    else:
        print("  Admin user already exists")


def run_migration():
    """Run the full migration"""
    app = create_app()

    with app.app_context():
        print("=" * 50)
        print("HAL Advisor Bot - Data Migration")
        print("=" * 50)
        print()

        # Create tables
        print("Creating database tables...")
        db.create_all()
        print("  Done")
        print()

        # Check if migration already ran
        existing_courses = Course.query.count()
        if existing_courses > 0:
            response = input(f"Found {existing_courses} existing courses. Clear and re-migrate? [y/N]: ")
            if response.lower() != 'y':
                print("Migration cancelled.")
                return

            # Clear existing data
            print("Clearing existing data...")
            Course.query.delete()
            Advisor.query.delete()
            Policy.query.delete()
            Deadline.query.delete()
            db.session.commit()

        # Run migrations
        migrate_courses()
        migrate_advisors()
        migrate_policies()
        migrate_casual_conversation()
        create_admin_user()

        print()
        print("Indexing documents for semantic search...")
        index_documents()

        print()
        print("=" * 50)
        print("Migration complete!")
        print("=" * 50)
        print()
        print("Summary:")
        print(f"  Courses: {Course.query.count()}")
        print(f"  Advisors: {Advisor.query.count()}")
        print(f"  Policies: {Policy.query.count()}")
        print()
        print("You can now run the app with: python3 app.py")
        print("Access admin at: http://localhost:5000/admin")


if __name__ == "__main__":
    run_migration()
