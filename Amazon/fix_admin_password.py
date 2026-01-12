#!/usr/bin/env python3
"""
Fix admin password in the database
"""

import pymysql
import bcrypt
from config import Config

def fix_admin_password():
    """Update admin password to 'admin123'"""
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        
        # Generate new password hash
        new_password = 'admin123'
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        print(f"🔧 Updating admin password...")
        print(f"🔐 New hash: {password_hash[:50]}...")
        
        # Update admin password
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE email = 'admin@ecommerce.com'",
            (password_hash,)
        )
        conn.commit()
        
        # Verify the update
        cursor.execute("SELECT * FROM users WHERE email = 'admin@ecommerce.com'")
        admin = cursor.fetchone()
        
        if admin:
            # Test the new password
            is_valid = bcrypt.checkpw(new_password.encode('utf-8'), admin['password_hash'].encode('utf-8'))
            print(f"✅ Admin password updated successfully!")
            print(f"🔑 Password 'admin123' verification: {is_valid}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    fix_admin_password()