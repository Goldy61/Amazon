#!/usr/bin/env python3
"""
Test script to verify the e-commerce platform setup
"""

import sys
import os
import importlib.util

def test_python_version():
    """Test if Python version is compatible"""
    print("Testing Python version...")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def test_dependencies():
    """Test if required packages are installed"""
    print("\nTesting dependencies...")
    required_packages = [
        'flask', 'pymysql', 'bcrypt', 'razorpay', 
        'pillow', 'werkzeug', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'pillow':
                import PIL
            elif package == 'python-dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def test_file_structure():
    """Test if required files and directories exist"""
    print("\nTesting file structure...")
    required_files = [
        'app.py', 'config.py', 'requirements.txt',
        'database/schema.sql', 'templates/base.html',
        'static/css/style.css', 'static/js/main.js'
    ]
    
    required_dirs = [
        'routes', 'templates', 'static', 'database',
        'templates/auth', 'templates/customer', 
        'templates/seller', 'templates/admin'
    ]
    
    missing_items = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            missing_items.append(file_path)
    
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - Missing")
            missing_items.append(dir_path)
    
    # Create upload directory if it doesn't exist
    upload_dir = 'static/uploads/products'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
        print(f"✅ Created {upload_dir}/")
    else:
        print(f"✅ {upload_dir}/")
    
    return len(missing_items) == 0

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found (optional)")
        print("   Copy .env.example to .env and configure your settings")
    
    # Test config import
    try:
        from config import Config
        print("✅ Configuration loaded successfully")
        
        # Check critical settings
        if hasattr(Config, 'SECRET_KEY') and Config.SECRET_KEY:
            print("✅ SECRET_KEY configured")
        else:
            print("⚠️  SECRET_KEY not configured")
        
        if hasattr(Config, 'RAZORPAY_KEY_ID') and Config.RAZORPAY_KEY_ID:
            print("✅ RAZORPAY_KEY_ID configured")
        else:
            print("⚠️  RAZORPAY_KEY_ID not configured")
            
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database_schema():
    """Test database schema file"""
    print("\nTesting database schema...")
    
    schema_file = 'database/schema.sql'
    if not os.path.exists(schema_file):
        print(f"❌ {schema_file} not found")
        return False
    
    try:
        with open(schema_file, 'r') as f:
            content = f.read()
            
        # Check for essential tables
        required_tables = [
            'users', 'customers', 'sellers', 'products', 
            'categories', 'cart', 'orders', 'order_items', 'payments'
        ]
        
        missing_tables = []
        for table in required_tables:
            if f'CREATE TABLE {table}' in content or f'CREATE TABLE IF NOT EXISTS {table}' in content:
                print(f"✅ Table: {table}")
            else:
                print(f"❌ Table: {table} - Not found in schema")
                missing_tables.append(table)
        
        return len(missing_tables) == 0
        
    except Exception as e:
        print(f"❌ Error reading schema file: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 E-Commerce Platform Setup Test")
    print("=" * 40)
    
    tests = [
        test_python_version,
        test_dependencies,
        test_file_structure,
        test_config,
        test_database_schema
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your setup looks good.")
        print("\nNext steps:")
        print("1. Start XAMPP (Apache + MySQL)")
        print("2. Create database 'amazon_db' in phpMyAdmin")
        print("3. Import database/schema.sql")
        print("4. Configure .env file with your settings")
        print("5. Run: python app.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())