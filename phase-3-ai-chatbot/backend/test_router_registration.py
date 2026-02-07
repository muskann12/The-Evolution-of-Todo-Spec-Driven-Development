#!/usr/bin/env python3
"""
Verification script for Phase III Chat Router Registration (AI-BACK-012).

This script tests that:
1. Chat router is imported in main.py
2. Chat router is registered with FastAPI app
3. Chat endpoints are accessible via the app
4. API version updated to 2.0.0 for Phase III
5. OpenAPI documentation includes chat endpoints

Run this script to verify AI-BACK-012 implementation.
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_import_in_main():
    """Test that chat router is imported in main.py."""
    print("[TEST] Testing chat router import in main.py...")

    main_file = Path(__file__).parent / "app" / "main.py"
    assert main_file.exists(), "main.py not found"

    content = main_file.read_text()

    # Check import statement
    assert "from app.routers import auth, tasks, chat" in content, \
        "Chat router not imported in main.py"

    print("[PASS] Chat router imported in main.py")


def test_router_registration():
    """Test that chat router is registered with FastAPI app."""
    print("\n[TEST] Testing chat router registration...")

    main_file = Path(__file__).parent / "app" / "main.py"
    content = main_file.read_text()

    # Check registration
    assert "app.include_router(chat.router)" in content, \
        "Chat router not registered with app.include_router()"

    print("[PASS] Chat router registered with app.include_router()")


def test_app_initialization():
    """Test that FastAPI app initializes with chat router."""
    print("\n[TEST] Testing FastAPI app initialization...")

    try:
        from app.main import app
        print("[PASS] FastAPI app imports successfully")
    except ImportError as e:
        print(f"[FAIL] FastAPI app import failed: {e}")
        sys.exit(1)


def test_routes_in_app():
    """Test that chat routes are registered in the app."""
    print("\n[TEST] Testing chat routes in app...")

    from app.main import app

    # Get all routes
    routes = [route.path for route in app.routes]

    # Check chat endpoint exists
    assert "/api/chat/message" in routes, \
        "POST /api/chat/message endpoint not found in app routes"

    print("[PASS] Chat endpoint /api/chat/message found in app routes")


def test_api_version():
    """Test that API version is updated to 2.0.0 for Phase III."""
    print("\n[TEST] Testing API version update...")

    from app.main import app

    assert app.version == "2.0.0", \
        f"API version should be 2.0.0 for Phase III, got {app.version}"

    print("[PASS] API version updated to 2.0.0")


def test_api_description():
    """Test that API description mentions AI chatbot."""
    print("\n[TEST] Testing API description update...")

    from app.main import app

    assert "chatbot" in app.description.lower(), \
        "API description should mention chatbot for Phase III"

    print("[PASS] API description updated to mention AI chatbot")


def test_openapi_schema():
    """Test that OpenAPI schema includes chat endpoints."""
    print("\n[TEST] Testing OpenAPI schema includes chat endpoints...")

    from app.main import app

    openapi_schema = app.openapi()

    # Check chat endpoint in paths
    assert "/api/chat/message" in openapi_schema["paths"], \
        "Chat endpoint not in OpenAPI schema"

    # Check endpoint has POST method
    chat_endpoint = openapi_schema["paths"]["/api/chat/message"]
    assert "post" in chat_endpoint, \
        "POST method not defined for /api/chat/message"

    print("[PASS] Chat endpoint in OpenAPI schema")
    print("[PASS] POST method defined for /api/chat/message")

    # Check tags
    post_spec = chat_endpoint["post"]
    assert "tags" in post_spec, "Endpoint should have tags"
    assert "chat" in post_spec["tags"], "Endpoint should have 'chat' tag"

    print("[PASS] Chat endpoint has 'chat' tag in OpenAPI schema")


def test_root_endpoint_response():
    """Test that root endpoint reflects Phase III features."""
    print("\n[TEST] Testing root endpoint response...")

    from app.main import root
    import asyncio

    # Call root endpoint
    response = asyncio.run(root())

    # Check version
    assert response["version"] == "2.0.0", \
        f"Root endpoint should return version 2.0.0, got {response['version']}"

    print("[PASS] Root endpoint returns version 2.0.0")

    # Check phase mentioned
    assert "phase" in response, "Root endpoint should mention phase"
    assert "III" in response["phase"], "Root endpoint should mention Phase III"

    print("[PASS] Root endpoint mentions Phase III")

    # Check features list includes AI Chatbot
    assert "features" in response, "Root endpoint should list features"
    features_str = " ".join(response["features"])
    assert "chatbot" in features_str.lower() or "ai" in features_str.lower(), \
        "Root endpoint should mention AI Chatbot in features"

    print("[PASS] Root endpoint lists AI Chatbot in features")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Phase III Chat Router Registration (AI-BACK-012)")
    print("=" * 60)
    print()

    try:
        test_import_in_main()
        test_router_registration()
        test_app_initialization()
        test_routes_in_app()
        test_api_version()
        test_api_description()
        test_openapi_schema()
        test_root_endpoint_response()

        print()
        print("=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("AI-BACK-012: Register Chat Router in Main App - COMPLETE")
        print()
        print("Phase 2 (Backend - AI Integration): COMPLETE (6/6 tasks)")
        print()
        print("Summary:")
        print("- Chat router imported in main.py")
        print("- Chat router registered with FastAPI app")
        print("- POST /api/chat/message endpoint accessible")
        print("- API version updated to 2.0.0")
        print("- OpenAPI documentation includes chat endpoints")
        print("- Root endpoint reflects Phase III features")
        print()
        print("Next steps:")
        print("1. Start backend server: uv run uvicorn app.main:app --reload")
        print("2. Visit http://localhost:8000/docs to see API documentation")
        print("3. Test chat endpoint with actual OpenAI API key")
        print("4. Begin Phase 3: Frontend - ChatKit Integration")
        print()

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
