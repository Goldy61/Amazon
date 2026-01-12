#!/usr/bin/env python3
"""
Database setup script for the e-commerce platform
"""

import pymysql
import sys
from config import Config

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect without specifying database
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        
        # Create database
        print(f"Creating database '{Config.MYSQL_DB}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        print(f"✅ Database '{Config.MYSQL_DB}' created successfully!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def import_schema():
    """Import the database schema"""
    try:
        # Connect to the database
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        
        # Read and execute schema file
        print("Importing database schema...")
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            schema_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in schema_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement.upper().startswith(('CREATE DATABASE', 'USE')):
                continue  # Skip database creation and use statements
            if statement:
                cursor.execute(statement)
        
        conn.commit()
        conn.close()
        
        print("✅ Database schema imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error importing schema: {e}")
        return False

def verify_setup():
    """Verify the database setup"""
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"\n📊 Database '{Config.MYSQL_DB}' contains {len(tables)} tables:")
        for table in tables:
            table_name = list(table.values())[0]
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"  ✅ {table_name} ({count} records)")
        
        # Check if admin user exists
        cursor.execute("SELECT * FROM users WHERE role = 'admin'")
        admin_users = cursor.fetchall()
        
        if admin_users:
            print(f"\n👤 Found {len(admin_users)} admin user(s):")
            for admin in admin_users:
                print(f"  📧 {admin['email']}")
        else:
            print("\n⚠️  No admin users found!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("🗄️  Database Setup for E-Commerce Platform")
    print("=" * 50)
    
    # Check if MySQL is running
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        conn.close()
        print("✅ MySQL connection successful!")
    except Exception as e:
        print("❌ Cannot connect to MySQL!")
        print("Please start MySQL in XAMPP Control Panel")
        return 1
    
    # Create database
    if not create_database():
        return 1
    
    # Import schema
    if not import_schema():
        return 1
    
    # Verify setup
    if not verify_setup():
        return 1
    
    print("\n🎉 Database setup completed successfully!")
    print("You can now run the application with: python run_app.py")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())