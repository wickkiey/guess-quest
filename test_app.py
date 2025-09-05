#!/usr/bin/env python3
"""
Simple test script to validate the core functionality of the interview application
"""

import sys
import traceback
from ollama_client import OllamaClient
from agents import InterviewCrew


def test_ollama_client():
    """Test OllamaClient basic functionality"""
    print("🧪 Testing OllamaClient...")
    
    try:
        # Test instantiation
        client = OllamaClient()
        print("✅ OllamaClient instantiated successfully")
        
        # Test connection checking (should fail gracefully)
        is_available = client.is_available()
        print(f"✅ Connection check completed (available: {is_available})")
        
        return True
    except Exception as e:
        print(f"❌ OllamaClient test failed: {e}")
        traceback.print_exc()
        return False


def test_interview_crew():
    """Test InterviewCrew basic functionality"""
    print("\n🧪 Testing InterviewCrew...")
    
    try:
        # Test instantiation (without actual LLM connection)
        client = OllamaClient()
        crew = InterviewCrew(client, "llama2")
        print("✅ InterviewCrew instantiated successfully")
        
        # Test basic configuration
        crew.set_topic("Python Programming")
        print("✅ Topic set successfully")
        
        crew.add_to_history("What is Python?", "Python is a programming language")
        print("✅ History management works")
        
        crew.increase_difficulty()
        print(f"✅ Difficulty increased to level {crew.difficulty_level}")
        
        crew.reset_interview()
        print(f"✅ Interview reset, difficulty back to {crew.difficulty_level}")
        
        return True
    except Exception as e:
        print(f"❌ InterviewCrew test failed: {e}")
        traceback.print_exc()
        return False


def test_streamlit_import():
    """Test that Streamlit app can be imported"""
    print("\n🧪 Testing Streamlit app import...")
    
    try:
        # Test importing the main app module
        import app
        print("✅ Streamlit app imported successfully")
        
        # Test that main functions exist
        assert hasattr(app, 'main'), "main() function not found"
        assert hasattr(app, 'init_session_state'), "init_session_state() function not found"
        assert hasattr(app, 'check_ollama_connection'), "check_ollama_connection() function not found"
        print("✅ Required functions found in app module")
        
        return True
    except Exception as e:
        print(f"❌ Streamlit app import test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🚀 Running Interview Application Tests\n")
    
    tests = [
        test_ollama_client,
        test_interview_crew,
        test_streamlit_import,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to use.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())