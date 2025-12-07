#!/usr/bin/env python3
"""
HAL Advisor Bot - Application Entry Point

Run this file to start the Flask development server.
For production deployment, use a WSGI server like Gunicorn:
    gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
"""
import os
from hal import create_app
from hal.config import Config
from hal.utils import init_scheduler, get_scheduler

# Create the Flask application instance
app = create_app()

# Initialize scheduler (only when not in debug reload)
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    init_scheduler(app)


def print_startup_info():
    """Print startup information to console"""
    print("=" * 50)
    print("HAL Advisor Bot")
    print("=" * 50)
    print(f"LLM Provider: {Config.LLM_PROVIDER.value}")
    print(f"Model: {Config.get_llm_config().model}")
    print(f"Database: {Config.SQLALCHEMY_DATABASE_URI}")
    print()
    print("Endpoints:")
    print("  Chat:  http://localhost:5000/")
    print("  Admin: http://localhost:5000/admin")
    print("  API:   http://localhost:5000/api/chat")
    print()
    print("Background Jobs:")
    scheduler = get_scheduler()
    for job in scheduler.get_jobs():
        print(f"  - {job['name']}: {job['trigger']}")
    print("=" * 50)


if __name__ == "__main__":
    print_startup_info()
    app.run(debug=True, port=5000)
