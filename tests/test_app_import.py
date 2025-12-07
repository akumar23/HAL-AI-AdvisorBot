#!/usr/bin/env python3
"""
Test script to check application components without requiring ChromaDB.
This allows testing other parts of the application despite ChromaDB compatibility issues.
"""

import sys
import os

# Add project directory to path
sys.path.insert(0, '/Users/aryankumar/Documents/personal-projects/HAL-AI-AdvisorBot')

print("=" * 60)
print("HAL AI AdvisorBot - Component Testing")
print("=" * 60)
print()

# Test 1: Configuration
print("[TEST 1] Testing Configuration Module...")
try:
    from config import Config, LLMProvider, get_config
    print(f"✓ Config module imported successfully")
    print(f"  - LLM Provider: {Config.LLM_PROVIDER.value}")
    print(f"  - Database URI: {Config.SQLALCHEMY_DATABASE_URI}")
    print(f"  - Secret Key configured: {'Yes' if Config.SECRET_KEY else 'No'}")
    test1_pass = True
except Exception as e:
    print(f"✗ Config module failed: {e}")
    test1_pass = False
print()

# Test 2: Database Models
print("[TEST 2] Testing Database Models...")
try:
    from models import Course, Advisor, Policy, Deadline, Conversation, Feedback, AdminUser
    print(f"✓ Models module imported successfully")
    print(f"  - Course model: {Course.__name__}")
    print(f"  - Advisor model: {Advisor.__name__}")
    print(f"  - Policy model: {Policy.__name__}")
    print(f"  - Deadline model: {Deadline.__name__}")
    test2_pass = True
except Exception as e:
    print(f"✗ Models module failed: {e}")
    test2_pass = False
print()

# Test 3: LLM Providers (without actual API calls)
print("[TEST 3] Testing LLM Provider Classes...")
try:
    from llm_providers import BaseLLMProvider, LLMResponse, get_llm_provider
    from config import LLMConfig, LLMProvider as LP
    print(f"✓ LLM providers module imported successfully")
    print(f"  - LLMResponse dataclass: {LLMResponse.__name__}")
    print(f"  - BaseLLMProvider: {BaseLLMProvider.__name__}")
    test3_pass = True
except Exception as e:
    print(f"✗ LLM providers module failed: {e}")
    test3_pass = False
print()

# Test 4: Intent Classifier
print("[TEST 4] Testing Intent Classifier...")
try:
    from intent_classifier import Intent, IntentClassifier, get_classifier
    print(f"✓ Intent classifier imported successfully")
    print(f"  - Intent enum: {Intent.__name__}")
    print(f"  - Available intents: {len(Intent.__members__)}")

    # Test rule-based classification
    classifier = get_classifier()
    result = classifier._rule_based_classify("What are the prerequisites for CS 149?")
    if result:
        print(f"  - Rule-based test: {result.intent.value} (confidence: {result.confidence_score})")
    test4_pass = True
except Exception as e:
    print(f"✗ Intent classifier failed: {e}")
    test4_pass = False
print()

# Test 5: Conversation Manager
print("[TEST 5] Testing Conversation Manager...")
try:
    from conversation_manager import ConversationManager, get_conversation_manager
    print(f"✓ Conversation manager imported successfully")
    manager = get_conversation_manager()
    print(f"  - Manager instance created: {manager.__class__.__name__}")
    test5_pass = True
except Exception as e:
    print(f"✗ Conversation manager failed: {e}")
    test5_pass = False
print()

# Test 6: Confidence Scoring
print("[TEST 6] Testing Confidence Scoring...")
try:
    from confidence_scoring import ConfidenceScorer, get_confidence_scorer
    print(f"✓ Confidence scorer imported successfully")
    scorer = get_confidence_scorer()
    print(f"  - Scorer instance created: {scorer.__class__.__name__}")
    test6_pass = True
except Exception as e:
    print(f"✗ Confidence scoring failed: {e}")
    test6_pass = False
print()

# Test 7: Quick Replies
print("[TEST 7] Testing Quick Replies...")
try:
    from quick_replies import generate_quick_replies
    print(f"✓ Quick replies module imported successfully")
    test7_pass = True
except Exception as e:
    print(f"✗ Quick replies failed: {e}")
    test7_pass = False
print()

# Test 8: Analytics
print("[TEST 8] Testing Analytics...")
try:
    from analytics import AnalyticsEngine
    print(f"✓ Analytics module imported successfully")
    test8_pass = True
except Exception as e:
    print(f"✗ Analytics failed: {e}")
    test8_pass = False
print()

# Test 9: Scheduler
print("[TEST 9] Testing Scheduler...")
try:
    from scheduler import HALScheduler
    print(f"✓ Scheduler module imported successfully")
    test9_pass = True
except Exception as e:
    print(f"✗ Scheduler failed: {e}")
    test9_pass = False
print()

# Test 10: Admin Module
print("[TEST 10] Testing Admin Module...")
try:
    from admin import init_admin
    print(f"✓ Admin module imported successfully")
    test10_pass = True
except Exception as e:
    print(f"✗ Admin module failed: {e}")
    test10_pass = False
print()

# Note about ChromaDB
print("[NOTE] ChromaDB/RAG Engine Tests...")
print("⚠ ChromaDB has compatibility issues with Python 3.14.1")
print("  - chromadb 0.3.x requires old pydantic BaseSettings")
print("  - chromadb 0.4.x requires pulsar-client (not available for Python 3.14)")
print("  - Recommendation: Use Python 3.10-3.12 for RAG functionality")
print()

# Test 11: Flask App Creation (without running)
print("[TEST 11] Testing Flask App Creation...")
try:
    # Temporarily skip RAG engine by mocking it
    import sys
    from unittest.mock import MagicMock

    # Mock chromadb before importing rag_engine
    sys.modules['chromadb'] = MagicMock()

    from app import create_app
    test_app = create_app()
    print(f"✓ Flask app created successfully")
    print(f"  - App name: {test_app.name}")
    print(f"  - Debug mode: {test_app.debug}")

    # Check routes
    routes = [str(rule) for rule in test_app.url_map.iter_rules()]
    print(f"  - Number of routes: {len(routes)}")
    print(f"  - Sample routes: {routes[:5]}")
    test11_pass = True
except Exception as e:
    print(f"✗ Flask app creation failed: {e}")
    import traceback
    traceback.print_exc()
    test11_pass = False
print()

# Summary
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
results = {
    "Configuration": test1_pass,
    "Database Models": test2_pass,
    "LLM Providers": test3_pass,
    "Intent Classifier": test4_pass,
    "Conversation Manager": test5_pass,
    "Confidence Scoring": test6_pass,
    "Quick Replies": test7_pass,
    "Analytics": test8_pass,
    "Scheduler": test9_pass,
    "Admin Module": test10_pass,
    "Flask App Creation": test11_pass,
}

passed = sum(1 for v in results.values() if v)
total = len(results)

for test_name, result in results.items():
    status = "PASS" if result else "FAIL"
    symbol = "✓" if result else "✗"
    print(f"{symbol} {test_name}: {status}")

print()
print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
print("=" * 60)
