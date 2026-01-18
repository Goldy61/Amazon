#!/usr/bin/env python3
"""
OTP Service Module for Login Verification
Handles OTP generation, validation, and cleanup
"""

import random
import string
from datetime import datetime, timedelta
import pymysql
from flask import current_app
from services.email_service import send_login_otp_email

def get_db_connection():
    """Get database connection"""
    return pymysql.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def create_otp(user_id, user_email, user_name):
    """
    Create and send OTP for user login
    
    Args:
        user_id: User ID from database
        user_email: User's email address
        user_name: User's display name
    
    Returns:
        bool: True if OTP created and sent successfully
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clean up expired OTPs for this user
        cursor.execute("""
            DELETE FROM login_otps 
            WHERE user_id = %s AND (expires_at < NOW() OR is_used = TRUE)
        """, (user_id,))
        
        # Generate new OTP
        otp_code = generate_otp()
        expires_at = datetime.now() + timedelta(minutes=10)  # OTP expires in 10 minutes
        
        # Store OTP in database
        cursor.execute("""
            INSERT INTO login_otps (user_id, otp_code, expires_at)
            VALUES (%s, %s, %s)
        """, (user_id, otp_code, expires_at))
        
        conn.commit()
        conn.close()
        
        # Send OTP email
        email_sent = send_login_otp_email(user_email, user_name, otp_code, user_id)
        
        if email_sent:
            print(f"✅ OTP sent successfully to {user_email}")
            return True
        else:
            print(f"❌ Failed to send OTP email to {user_email}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating OTP: {e}")
        return False

def verify_otp(user_id, otp_code):
    """
    Verify OTP for user login
    
    Args:
        user_id: User ID from database
        otp_code: OTP code entered by user
    
    Returns:
        dict: {'valid': bool, 'message': str}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find valid OTP for user
        cursor.execute("""
            SELECT id, expires_at, is_used 
            FROM login_otps 
            WHERE user_id = %s AND otp_code = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (user_id, otp_code))
        
        otp_record = cursor.fetchone()
        
        if not otp_record:
            conn.close()
            return {'valid': False, 'message': 'Invalid OTP code. Please check and try again.'}
        
        # Check if OTP is already used
        if otp_record['is_used']:
            conn.close()
            return {'valid': False, 'message': 'OTP code has already been used. Please request a new one.'}
        
        # Check if OTP is expired
        if datetime.now() > otp_record['expires_at']:
            conn.close()
            return {'valid': False, 'message': 'OTP code has expired. Please request a new one.'}
        
        # Mark OTP as used
        cursor.execute("""
            UPDATE login_otps 
            SET is_used = TRUE 
            WHERE id = %s
        """, (otp_record['id'],))
        
        conn.commit()
        conn.close()
        
        return {'valid': True, 'message': 'OTP verified successfully!'}
        
    except Exception as e:
        print(f"❌ Error verifying OTP: {e}")
        return {'valid': False, 'message': 'An error occurred during verification. Please try again.'}

def cleanup_expired_otps():
    """Clean up expired OTPs from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete expired OTPs
        cursor.execute("""
            DELETE FROM login_otps 
            WHERE expires_at < NOW() OR is_used = TRUE
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            print(f"🧹 Cleaned up {deleted_count} expired OTPs")
        
        return deleted_count
        
    except Exception as e:
        print(f"❌ Error cleaning up OTPs: {e}")
        return 0

def get_user_otp_status(user_id):
    """
    Get OTP status for user
    
    Args:
        user_id: User ID from database
    
    Returns:
        dict: OTP status information
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get latest OTP for user
        cursor.execute("""
            SELECT otp_code, expires_at, is_used, created_at
            FROM login_otps 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (user_id,))
        
        otp_record = cursor.fetchone()
        conn.close()
        
        if not otp_record:
            return {'has_otp': False, 'message': 'No OTP found'}
        
        now = datetime.now()
        is_expired = now > otp_record['expires_at']
        is_used = otp_record['is_used']
        
        if is_used:
            return {'has_otp': False, 'message': 'OTP already used'}
        elif is_expired:
            return {'has_otp': False, 'message': 'OTP expired'}
        else:
            time_left = otp_record['expires_at'] - now
            minutes_left = int(time_left.total_seconds() / 60)
            return {
                'has_otp': True, 
                'message': f'OTP valid for {minutes_left} more minutes',
                'expires_at': otp_record['expires_at'],
                'created_at': otp_record['created_at']
            }
            
    except Exception as e:
        print(f"❌ Error getting OTP status: {e}")
        return {'has_otp': False, 'message': 'Error checking OTP status'}