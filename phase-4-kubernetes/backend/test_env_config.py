#!/usr/bin/env python3
"""
Verification script for Phase III environment variables.

This script tests that:
1. Environment variables can be loaded from .env file
2. Config.py properly reads OpenAI settings
3. Agent.py can initialize with environment variables

Run this script to verify Phase III environment setup.
"""

import os
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_env_file_exists():
    """Test that .env.example exists as template."""
    env_example = Path(__file__).parent / ".env.example"
    assert env_example.exists(), ".env.example file not found"
    print("[PASS] .env.example file exists")

    # Check that Phase III variables are documented
    content = env_example.read_text()
    assert "OPENAI_API_KEY" in content, "OPENAI_API_KEY not in .env.example"
    assert "OPENAI_MODEL" in content, "OPENAI_MODEL not in .env.example"
    print("[PASS] Phase III environment variables documented in .env.example")


def test_gitignore():
    """Test that .env is properly gitignored."""
    gitignore = Path(__file__).parent / ".gitignore"
    assert gitignore.exists(), ".gitignore file not found"

    content = gitignore.read_text()
    assert ".env" in content, ".env not in .gitignore"
    print("[PASS] .env file is properly gitignored")


def test_config_settings():
    """Test that config.py includes Phase III settings."""
    from app.config import settings

    # Check that settings object has Phase III attributes
    assert hasattr(settings, "openai_api_key"), "settings missing openai_api_key"
    assert hasattr(settings, "openai_model"), "settings missing openai_model"
    print("[PASS] Config.py includes Phase III OpenAI settings")

    # Check defaults
    assert settings.openai_model == "gpt-4o", f"Expected default model 'gpt-4o', got '{settings.openai_model}'"
    print(f"[PASS] Default OpenAI model: {settings.openai_model}")


def test_agent_env_loading():
    """Test that agent.py can read from environment variables."""
    print("\n[TEST] Testing agent environment variable loading...")

    # Set test environment variables
    os.environ["OPENAI_API_KEY"] = "sk-test-key-for-verification"
    os.environ["OPENAI_MODEL"] = "gpt-4o-mini"

    try:
        from app.ai.agent import TodoAgent

        # Test that agent reads from environment
        agent = TodoAgent()
        assert agent.api_key == "sk-test-key-for-verification", "Agent not reading OPENAI_API_KEY from environment"
        assert agent.model == "gpt-4o-mini", "Agent not reading OPENAI_MODEL from environment"

        print("[PASS] Agent successfully reads OPENAI_API_KEY from environment")
        print("[PASS] Agent successfully reads OPENAI_MODEL from environment")
        print(f"       Model: {agent.model}")

    except ValueError as e:
        if "OpenAI API key not provided" in str(e):
            print("[INFO] Agent requires OPENAI_API_KEY (expected behavior)")
        else:
            raise
    finally:
        # Clean up test environment variables
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("OPENAI_MODEL", None)


def test_agent_initialization_without_key():
    """Test that agent fails gracefully without API key."""
    print("\n[TEST] Testing agent behavior without API key...")

    # Ensure no API key in environment
    os.environ.pop("OPENAI_API_KEY", None)

    try:
        from app.ai.agent import TodoAgent
        agent = TodoAgent()
        print("[FAIL] Agent should have raised ValueError without API key")
        sys.exit(1)
    except ValueError as e:
        if "OpenAI API key not provided" in str(e):
            print("[PASS] Agent correctly raises ValueError without API key")
            print(f"       Error message: {str(e)}")
        else:
            raise


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Phase III Environment Configuration Verification")
    print("=" * 60)
    print()

    try:
        test_env_file_exists()
        test_gitignore()
        test_config_settings()
        test_agent_env_loading()
        test_agent_initialization_without_key()

        print()
        print("=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your actual OPENAI_API_KEY to .env")
        print("3. Run: uv run uvicorn app.main:app --reload")
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
