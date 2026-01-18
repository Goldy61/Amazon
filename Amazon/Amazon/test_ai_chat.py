#!/usr/bin/env python3
"""
Test AI Chat functionality
"""
import os
import sys
from flask import Flask
from config import Config

# Create Flask app for testing
app = Flask(__name__)
app.config.from_object(Config)

def test_ai_chat_config():
    """Test AI chat configuration"""
    print("🧪 Testing AI Chat Configuration")
    print("=" * 40)
    
    # Check OpenAI API key
    api_key = app.config.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in configuration")
        print("📝 Please add OPENAI_API_KEY to your .env file")
        return False
    elif api_key == 'your-openai-api-key':
        print("❌ OPENAI_API_KEY is still set to placeholder value")
        print("📝 Please update OPENAI_API_KEY in your .env file with your actual OpenAI API key")
        return False
    else:
        print(f"✅ OPENAI_API_KEY configured (ends with: ...{api_key[-4:]})")
    
    # Check other AI settings
    print(f"✅ AI Model: {app.config.get('AI_CHAT_MODEL', 'gpt-3.5-turbo')}")
    print(f"✅ Max Tokens: {app.config.get('AI_CHAT_MAX_TOKENS', 500)}")
    print(f"✅ Temperature: {app.config.get('AI_CHAT_TEMPERATURE', 0.7)}")
    
    return True

def test_ai_chat_service():
    """Test AI chat service functionality"""
    print("\n🤖 Testing AI Chat Service")
    print("=" * 40)
    
    try:
        with app.app_context():
            from services.ai_chat_service import get_chat_response, get_quick_suggestions
            
            # Test quick suggestions
            suggestions = get_quick_suggestions('customer')
            print(f"✅ Quick suggestions for customer: {len(suggestions)} items")
            
            suggestions = get_quick_suggestions('seller')
            print(f"✅ Quick suggestions for seller: {len(suggestions)} items")
            
            # Test chat response with request context
            print("\n🔄 Testing AI response (this will use your OpenAI API credits)...")
            
            with app.test_request_context():
                response = get_chat_response("Hello, can you help me?")
                
                if response['success']:
                    print("✅ AI Chat Response Test Successful!")
                    print(f"📝 Response: {response['message'][:100]}...")
                    print(f"🔢 Tokens used: {response.get('tokens_used', 'N/A')}")
                else:
                    print(f"❌ AI Chat Response Test Failed: {response.get('error', 'Unknown error')}")
                    print(f"📝 Message: {response['message']}")
                    return False
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing AI chat service: {e}")
        return False
    
    return True

def test_database_setup():
    """Test database setup for chat logs"""
    print("\n🗄️ Testing Database Setup")
    print("=" * 40)
    
    try:
        from services.ai_chat_service import get_db_connection
        
        with app.app_context():
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if chat_logs table exists
            cursor.execute("SHOW TABLES LIKE 'chat_logs'")
            if cursor.fetchone():
                print("✅ chat_logs table exists")
                
                # Check table structure
                cursor.execute("DESCRIBE chat_logs")
                columns = cursor.fetchall()
                print(f"✅ chat_logs table has {len(columns)} columns")
                
            else:
                print("❌ chat_logs table not found")
                print("📝 Please run: python update_database_chat.py")
                return False
            
            conn.close()
            
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🤖 AI Chat System Test")
    print("=" * 50)
    
    # Test configuration
    config_ok = test_ai_chat_config()
    
    # Test database
    db_ok = test_database_setup()
    
    # Test AI service (only if config is OK)
    service_ok = False
    if config_ok:
        service_ok = test_ai_chat_service()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"AI Service: {'✅ PASS' if service_ok else '❌ FAIL' if config_ok else '⏭️ SKIPPED'}")
    
    if config_ok and db_ok and service_ok:
        print("\n🎉 All tests passed! AI Chat is ready to use.")
        print("🌐 Start your server and visit: http://localhost:5000/chat")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
        
        if not config_ok:
            print("💡 Fix: Add your OpenAI API key to .env file")
        if not db_ok:
            print("💡 Fix: Run database update script")

if __name__ == '__main__':
    main()