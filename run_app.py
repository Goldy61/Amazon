#!/usr/bin/env python3
"""
Startup script for the e-commerce application with better error handling
"""

import sys
import os

def check_database_connection():
    """Test database connection before starting the app"""
    try:
        from config import Config
        import pymysql
        
        print("🔍 Testing database connection...")
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        conn.close()
        
        print(f"✅ Database connection successful! Found {result['count']} users.")
        return True
        
    except pymysql.err.OperationalError as e:
        error_code = e.args[0]
        if error_code == 1049:  # Database doesn't exist
            print(f"❌ Database '{Config.MYSQL_DB}' doesn't exist!")
            print("Please create the database and import the schema:")
            print("1. Open phpMyAdmin: http://localhost/phpmyadmin/")
            print(f"2. Create database: {Config.MYSQL_DB}")
            print("3. Import: database/schema.sql")
            return False
        elif error_code == 2003:  # Can't connect to MySQL server
            print("❌ Can't connect to MySQL server!")
            print("Please start MySQL in XAMPP Control Panel")
            return False
        else:
            print(f"❌ Database error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_enhanced_features():
    """Check if enhanced features are installed"""
    try:
        from config import Config
        import pymysql
        
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # Check if wishlist table exists
        cursor.execute("SHOW TABLES LIKE 'wishlist'")
        wishlist_exists = cursor.fetchone() is not None
        
        # Check if average_rating column exists
        cursor.execute("SHOW COLUMNS FROM products LIKE 'average_rating'")
        rating_column_exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        
        if not wishlist_exists or not rating_column_exists:
            print("\n" + "⚠️ " * 25)
            print("⚠️  ENHANCED FEATURES NOT INSTALLED")
            print("⚠️ " * 25)
            print("\n📦 New features available but not yet set up:")
            print("   • Product Reviews & Ratings ⭐")
            print("   • Wishlist/Favorites ❤️")
            print("   • Newsletter Subscriptions 📧")
            print("   • Product Views Tracking 👁️")
            print("\n🔧 To install, run:")
            print("   python setup_enhanced_features.py")
            print("\n📖 Or see: SETUP_INSTRUCTIONS_ENHANCED.md")
            print("=" * 70 + "\n")
            return False
        
        return True
        
    except Exception as e:
        # Silently fail - don't block app startup
        return True

def start_app():
    """Start the Flask application"""
    print("🚀 Starting Flask application...")
    
    # Import and run the app
    from app import app
    
    print("📋 Registered routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"  {rule.rule} [{methods}] -> {rule.endpoint}")
    
    print("\n🌐 Starting server on http://localhost:5000")
    print("🌐 Also accessible on http://0.0.0.0:5000")
    print("Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

def main():
    """Main function"""
    print("=" * 50)
    print("🛒 Multi-Vendor E-Commerce Platform - ShopHub")
    print("=" * 50)
    
    # Check database connection first
    if not check_database_connection():
        print("\n❌ Cannot start application due to database issues.")
        print("Please fix the database connection and try again.")
        return 1
    
    # Check if enhanced features are installed
    check_enhanced_features()
    
    # Start the application
    try:
        start_app()
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())