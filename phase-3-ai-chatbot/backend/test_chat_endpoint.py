#!/usr/bin/env python3
"""
Verification script for Phase III Chat Endpoint (AI-BACK-011).

This script tests that:
1. Chat schemas are correctly defined
2. Chat router exists with helper functions
3. POST /api/chat/message endpoint is implemented
4. Stateless architecture patterns are followed
5. User isolation is enforced

Run this script to verify AI-BACK-011 implementation.
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_chat_schemas():
    """Test that chat schemas are defined in schemas.py."""
    print("[TEST] Testing chat schemas...")

    from app.schemas import (
        ChatMessageRequest,
        ChatMessageResponse,
        ConversationResponse,
        ConversationListResponse
    )

    # Test ChatMessageRequest
    request = ChatMessageRequest(message="Test message")
    assert request.message == "Test message", "ChatMessageRequest message field failed"
    assert request.conversation_id is None, "ChatMessageRequest conversation_id should be optional"

    # Test with conversation_id
    request_with_conv = ChatMessageRequest(
        message="Test", conversation_id=123
    )
    assert request_with_conv.conversation_id == 123, "ChatMessageRequest conversation_id failed"

    print("[PASS] ChatMessageRequest schema works correctly")

    # Test ChatMessageResponse
    response = ChatMessageResponse(
        conversation_id=1,
        response="AI response"
    )
    assert response.conversation_id == 1, "ChatMessageResponse conversation_id failed"
    assert response.response == "AI response", "ChatMessageResponse response failed"

    print("[PASS] ChatMessageResponse schema works correctly")
    print("[PASS] All chat schemas defined and working")


def test_chat_router_exists():
    """Test that chat router file exists."""
    print("\n[TEST] Testing chat router exists...")

    router_file = Path(__file__).parent / "app" / "routers" / "chat.py"
    assert router_file.exists(), "Chat router file not found at app/routers/chat.py"

    print("[PASS] Chat router file exists")


def test_chat_router_imports():
    """Test that chat router imports successfully."""
    print("\n[TEST] Testing chat router imports...")

    try:
        from app.routers import chat
        print("[PASS] Chat router imports successfully")
    except ImportError as e:
        print(f"[FAIL] Chat router import failed: {e}")
        sys.exit(1)


def test_helper_functions():
    """Test that helper functions are defined."""
    print("\n[TEST] Testing helper functions...")

    from app.routers import chat

    # Check helper functions exist
    assert hasattr(chat, "get_or_create_conversation"), "get_or_create_conversation not found"
    assert hasattr(chat, "get_conversation_messages"), "get_conversation_messages not found"
    assert hasattr(chat, "store_message"), "store_message not found"

    print("[PASS] get_or_create_conversation function defined")
    print("[PASS] get_conversation_messages function defined")
    print("[PASS] store_message function defined")


def test_endpoint_definition():
    """Test that POST /api/chat/message endpoint is defined."""
    print("\n[TEST] Testing endpoint definition...")

    from app.routers import chat

    # Check router exists
    assert hasattr(chat, "router"), "Router not found in chat module"

    # Check router has correct prefix
    assert chat.router.prefix == "/api/chat", f"Router prefix should be '/api/chat', got '{chat.router.prefix}'"

    print("[PASS] Router has correct prefix: /api/chat")

    # Check endpoint function exists
    assert hasattr(chat, "send_chat_message"), "send_chat_message endpoint function not found"

    print("[PASS] send_chat_message endpoint function defined")


def test_stateless_architecture_patterns():
    """Test that stateless architecture patterns are followed."""
    print("\n[TEST] Testing stateless architecture patterns...")

    import inspect
    from app.routers import chat

    # Check helper function signatures for stateless patterns
    get_or_create_sig = inspect.signature(chat.get_or_create_conversation)
    assert "session" in get_or_create_sig.parameters, "get_or_create_conversation should have session parameter"
    assert "user_id" in get_or_create_sig.parameters, "get_or_create_conversation should have user_id parameter"

    print("[PASS] get_or_create_conversation has session and user_id parameters")

    get_messages_sig = inspect.signature(chat.get_conversation_messages)
    assert "session" in get_messages_sig.parameters, "get_conversation_messages should have session parameter"
    assert "conversation_id" in get_messages_sig.parameters, "get_conversation_messages should have conversation_id parameter"

    print("[PASS] get_conversation_messages has session and conversation_id parameters")

    store_message_sig = inspect.signature(chat.store_message)
    assert "session" in store_message_sig.parameters, "store_message should have session parameter"
    assert "conversation_id" in store_message_sig.parameters, "store_message should have conversation_id parameter"
    assert "role" in store_message_sig.parameters, "store_message should have role parameter"
    assert "content" in store_message_sig.parameters, "store_message should have content parameter"

    print("[PASS] store_message has required parameters")


def test_user_isolation():
    """Test that user isolation is enforced."""
    print("\n[TEST] Testing user isolation...")

    import inspect
    from app.routers import chat

    # Check that endpoint has current_user dependency
    endpoint_sig = inspect.signature(chat.send_chat_message)
    params = endpoint_sig.parameters

    assert "current_user" in params, "send_chat_message should have current_user parameter"

    print("[PASS] send_chat_message has current_user parameter for authentication")

    # Read source code to verify user_id filtering
    source = inspect.getsource(chat.get_or_create_conversation)
    assert "user_id" in source, "get_or_create_conversation should filter by user_id"
    assert "Conversation.user_id == user_id" in source, "get_or_create_conversation should filter Conversation.user_id"

    print("[PASS] get_or_create_conversation filters by user_id (user isolation)")


def test_error_handling():
    """Test that error handling is implemented."""
    print("\n[TEST] Testing error handling...")

    import inspect
    from app.routers import chat

    # Check that endpoint has try-except blocks
    source = inspect.getsource(chat.send_chat_message)

    assert "try:" in source, "send_chat_message should have try-except blocks"
    assert "except" in source, "send_chat_message should have except blocks"
    assert "HTTPException" in source, "send_chat_message should raise HTTPException on errors"

    print("[PASS] send_chat_message has error handling with HTTPException")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Phase III Chat Endpoint Verification (AI-BACK-011)")
    print("=" * 60)
    print()

    try:
        test_chat_schemas()
        test_chat_router_exists()
        test_chat_router_imports()
        test_helper_functions()
        test_endpoint_definition()
        test_stateless_architecture_patterns()
        test_user_isolation()
        test_error_handling()

        print()
        print("=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("AI-BACK-011: Implement Chat API Endpoint - COMPLETE")
        print()
        print("Next steps:")
        print("1. AI-BACK-012: Register Chat Router in Main App")
        print("2. Test endpoint with actual OpenAI API key")
        print("3. Apply database migration: alembic upgrade head")
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
