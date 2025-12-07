"""
HAL Advisor Bot - Main Application

A RAG-based academic advising chatbot for SJSU CMPE/SE students.
Supports multiple LLM providers: Claude, OpenAI, and Ollama.
"""
import os
import uuid
from datetime import datetime

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from flask_cors import CORS

from hal.config import get_config, Config
from hal.models import db, init_db, Conversation, Feedback
from hal.api.admin_api import admin_api
from hal.services import query_advisor, get_rag_engine, generate_quick_replies
from hal.utils import init_scheduler, get_scheduler


def create_app(config_class=None):
    """Application factory"""
    # Get the project root directory (parent of hal package)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, 'templates'),
        static_folder=os.path.join(project_root, 'static')
    )

    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Initialize extensions
    Session(app)
    # Allow CORS from Next.js frontend (local dev and Docker)
    CORS(app, origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5001",  # Docker exposed port
    ], supports_credentials=True)
    init_db(app)

    # Register blueprints
    app.register_blueprint(admin_api)

    # Register routes
    register_routes(app)

    return app


def register_routes(app):
    """Register application routes"""

    @app.route("/")
    def index():
        """Render the chat interface"""
        # Create session ID if not exists
        if "session_id" not in session:
            session["session_id"] = str(uuid.uuid4())
        return render_template("base.html")

    @app.route("/get")
    def get_response():
        """
        Handle chat requests (legacy endpoint for compatibility).
        Returns plain text response.
        """
        user_message = request.args.get("msg", "").strip()
        if not user_message:
            return "Please enter a message."

        try:
            # Create session ID if not exists
            if "session_id" not in session:
                session["session_id"] = str(uuid.uuid4())

            # Get conversation history from session
            history = session.get("conversation_history", [])

            # Query the RAG system
            result = query_advisor(
                query=user_message,
                session_id=session.get("session_id"),
                conversation_history=history
            )

            response = result.get("response", "I'm sorry, I couldn't process that request.")

            # Update conversation history
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": response})

            # Keep only last 20 messages
            session["conversation_history"] = history[-20:]

            # Store conversation in database
            _store_conversation(
                session.get("session_id"),
                user_message,
                response
            )

            return response

        except Exception as e:
            app.logger.error(f"Error processing request: {e}")
            return "I encountered an error processing your request. Please try again."

    @app.route("/api/chat", methods=["POST"])
    def chat():
        """
        Modern chat API endpoint.
        Returns JSON with response, confidence, and sources.
        """
        data = request.get_json() or {}
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        try:
            # Create session ID if not exists (needed for API-first clients like Next.js)
            if "session_id" not in session:
                session["session_id"] = str(uuid.uuid4())

            # Get conversation history
            history = session.get("conversation_history", [])

            # Query the RAG system
            result = query_advisor(
                query=user_message,
                session_id=session.get("session_id"),
                conversation_history=history
            )

            # Update conversation history
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": result["response"]})
            session["conversation_history"] = history[-20:]

            # Store conversation
            _store_conversation(
                session.get("session_id"),
                user_message,
                result["response"]
            )

            # Check if we should include course cards
            course_cards = _extract_course_cards(result.get("sources", []))

            return jsonify({
                "response": result["response"],
                "confidence": result.get("confidence", 0),
                "sources": result.get("sources", []),
                "model": result.get("model"),
                "provider": result.get("provider"),
                "low_confidence": result.get("low_confidence", False),
                "intent": result.get("intent"),
                "escalate": result.get("escalate_to_human", False),
                "escalation_message": result.get("escalation_message"),
                "course_cards": course_cards
            })

        except Exception as e:
            app.logger.error(f"Error in chat API: {e}")
            return jsonify({
                "error": "An error occurred processing your request",
                "response": "I'm sorry, I encountered an error. Please try again."
            }), 500

    @app.route("/api/feedback", methods=["POST"])
    def submit_feedback():
        """Submit feedback on a response"""
        data = request.get_json() or {}
        rating = data.get("rating")  # 1 = thumbs down, 2 = thumbs up
        query = data.get("query", "")
        response = data.get("response", "")
        comment = data.get("comment", "")

        if rating not in [1, 2]:
            return jsonify({"error": "Rating must be 1 or 2"}), 400

        feedback = Feedback(
            session_id=session.get("session_id"),
            user_query=query,
            bot_response=response,
            rating=rating,
            comment=comment
        )
        db.session.add(feedback)
        db.session.commit()

        return jsonify({"status": "success"})

    @app.route("/api/clear-history", methods=["POST"])
    def clear_history():
        """Clear conversation history"""
        session["conversation_history"] = []
        return jsonify({"status": "success"})

    @app.route("/api/status")
    def status():
        """Get system status"""
        config = Config
        return jsonify({
            "status": "ok",
            "provider": config.LLM_PROVIDER.value,
            "model": config.get_llm_config().model,
            "session_id": session.get("session_id")
        })

    @app.route("/api/quick-replies", methods=["POST"])
    def quick_replies():
        """
        Generate contextual quick reply suggestions.
        Uses LLM to generate relevant follow-up questions.
        """
        data = request.get_json() or {}

        # Input validation - limit string lengths to prevent abuse
        MAX_INPUT_LENGTH = 1000
        last_response = str(data.get("lastResponse", ""))[:MAX_INPUT_LENGTH]
        last_query = str(data.get("lastQuery", ""))[:MAX_INPUT_LENGTH]
        intent = str(data.get("intent", ""))[:100]

        # Get conversation history from session
        conversation_history = session.get("conversation_history", [])

        try:
            suggestions = generate_quick_replies(
                last_response=last_response,
                last_query=last_query,
                conversation_history=conversation_history,
                intent=intent
            )
            return jsonify({"suggestions": suggestions})
        except Exception as e:
            app.logger.error(f"Error generating quick replies: {e}")
            # Return default suggestions on error
            return jsonify({
                "suggestions": [
                    "Tell me about course prerequisites",
                    "Help me find my advisor",
                    "What are important deadlines?"
                ]
            })

    @app.route("/health")
    def health():
        """Health check endpoint"""
        return jsonify({"status": "healthy"})

    @app.route("/api/scheduler/jobs")
    def scheduler_jobs():
        """Get list of scheduled jobs (admin only)"""
        if not session.get("admin_logged_in"):
            return jsonify({"error": "Unauthorized"}), 401

        scheduler = get_scheduler()
        return jsonify({"jobs": scheduler.get_jobs()})

    @app.route("/api/scheduler/run/<job_id>", methods=["POST"])
    def run_scheduler_job(job_id):
        """Manually run a scheduled job (admin only)"""
        if not session.get("admin_logged_in"):
            return jsonify({"error": "Unauthorized"}), 401

        scheduler = get_scheduler()
        success = scheduler.run_job_now(job_id)

        if success:
            return jsonify({"status": "success", "message": f"Job {job_id} executed"})
        return jsonify({"error": f"Job {job_id} not found"}), 404


def _extract_course_cards(sources: list) -> list:
    """
    Extract course card data from RAG sources.

    Returns structured course information for rich display.
    """
    from hal.models import Course

    course_cards = []
    seen_codes = set()

    for source in sources:
        if source.get("type") == "course":
            code = source.get("metadata", {}).get("code")
            if code and code not in seen_codes:
                seen_codes.add(code)

                # Fetch full course data
                course = Course.query.filter_by(code=code).first()
                if course:
                    course_cards.append({
                        "code": course.code,
                        "name": course.name,
                        "units": course.units,
                        "description": course.description[:200] + "..." if course.description and len(course.description) > 200 else course.description,
                        "prerequisites": course.prerequisites,
                        "prerequisites_cmpe": course.prerequisites_cmpe,
                        "prerequisites_se": course.prerequisites_se,
                        "department": course.department
                    })

    return course_cards[:3]  # Limit to 3 cards


def _store_conversation(session_id: str, user_message: str, bot_response: str):
    """Store conversation messages in database"""
    try:
        # Store user message
        user_conv = Conversation(
            session_id=session_id,
            role="user",
            content=user_message
        )
        db.session.add(user_conv)

        # Store bot response
        bot_conv = Conversation(
            session_id=session_id,
            role="assistant",
            content=bot_response
        )
        db.session.add(bot_conv)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Log but don't fail the request
        print(f"Error storing conversation: {e}")
