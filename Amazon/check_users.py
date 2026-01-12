#!/usr/bin/env python3
"""
Check users in the database and verify admin password
"""

import pymysql
import bcrypt
from config import Config

def check_users():
    """Check all users in the database"""
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        print("👥 Users in database:")
        for user in users:
            print(f"  📧 {user['email']} | Role: {user['role']} | Active: {user['is_active']}")
            
            # Test admin password
            if user['email'] == 'admin@ecommerce.com':
                test_password = 'admin123'
                is_valid = bcrypt.checkpw(test_password.encode('utf-8'), user['password_hash'].encode('utf-8'))
                print(f"    🔑 Password 'admin123' valid: {is_valid}")
                
                # Show hash for debugging
                print(f"    🔐 Stored hash: {user['password_hash'][:50]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def create_admin_if_missing():
    """Create admin user if missing"""
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = 'admin@ecommerce.com'")
        admin = cursor.fetchone()
        
        if not admin:
            print("🔧 Creating admin user...")
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
                ('admin@ecommerce.com', password_hash, 'admin')
            )
            conn.commit()
            print("✅ Admin user created successfully!")
        else:
            print("✅ Admin user already exists")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")

if __name__ == '__main__':
    print("🔍 Checking database users...")
    check_users()
    print("\n🔧 Ensuring admin user exists...")
    create_admin_if_missing()
    print("\n🔍 Final user check...")
    check_users()