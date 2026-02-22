#!/usr/bin/env python3
"""
Email Testing Script for Multi-Vendor E-Commerce Platform
Tests all email notification functions
"""

import os
import sys
from flask import Flask
from config import Config

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create Flask app for testing
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Mail
from services.email_service import mail
mail.init_app(app)

# Import email functions
from services.email_service import (
    send_registration_email,
    send_seller_approval_email,
    send_seller_rejection_email,
    send_product_added_email,
    send_order_placed_email,
    send_payment_success_email,
    send_payment_failed_email,
    send_order_status_email,
    send_seller_order_notification,
    send_password_reset_email
)

def test_email_configuration():
    """Test basic email configuration"""
    print("🔧 Testing Email Configuration...")
    
    required_configs = ['MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_SERVER', 'MAIL_PORT']
    missing_configs = []
    
    for config in required_configs:
        if not app.config.get(config):
            missing_configs.append(config)
    
    if missing_configs:
        print(f"❌ Missing configurations: {', '.join(missing_configs)}")
        print("📝 Please update your .env file with email credentials")
        return False
    
    print("✅ Email configuration looks good!")
    return True

def test_all_emails():
    """Test all email notification functions"""
    
    if not test_email_configuration():
        return
    
    # Get test email from config or use default
    test_email = app.config.get('MAIL_USERNAME', 'test@example.com')
    
    print(f"📧 Sending test emails to: {test_email}")
    print("=" * 50)
    
    with app.app_context():
        
        # Test 1: Registration Email
        print("1️⃣ Testing Registration Email...")
        try:
            result = send_registration_email(test_email, "John Doe", "customer")
            print(f"   {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Seller Approval Email
        print("2️⃣ Testing Seller Approval Email...")
        try:
            result = send_seller_approval_email(test_email, "Jane Smith", "Smith Electronics")
            print(f"   {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Seller Rejection Email
        print("3️⃣ Testing Seller Rejection Email...")
        try:
            result = send_seller_rejection_email(test_email, "Bob Wilson", "Wilson Store", "Missing GST documentation")
            print(f"   {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Product Added Email
        print("4️⃣ Testing Product Added Email...")
        try:
            result = send_product_added_email(test_email, "Alice Johnson", "Smartphone XYZ", 123)
            print(f"   {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Order Placed Email
        print("5️⃣ Testing Order Placed Email...")
        try:
            result = send_order_placed_email(test_email, "Mike Brown", "ORD12345678", 2999.99, 456)
            print(f"   {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 6: Payment Success Email
        print("6️⃣ Testing Payment Success Email...")
        try:
            result = send_payment_success_email(test_email, "Sarah Davis", "ORD12345678", 2999.99, 456)
            print(f"   {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 7: Payment Failed Email
        print("7️⃣ Testing Payment Failed Email...")
        try:
            result = send_payment_failed_email(test_email, "Tom Wilson", "ORD87654321", 789)
            print(f"   {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 8: Order Status Update Email
        print("8️⃣ Testing Order Status Update Email...")
        try:
            result = send_order_status_email(test_email, "Lisa Garcia", "ORD12345678", "shipped", 456)
            print(f"   {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 9: Seller Order Notification Email
        print("9️⃣ Testing Seller Order Notification Email...")
        try:
            result = send_seller_order_notification(test_email, "David Lee", "ORD12345678", "Laptop ABC", 2, 456)
            print(f"   {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 10: Password Reset Email
        print("🔟 Testing Password Reset Email...")
        try:
            result = send_password_reset_email(test_email, "Emma Taylor", "reset_token_123456")
            print(f"   {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 11: Login OTP Email
        print("1️⃣1️⃣ Testing Login OTP Email...")
        try:
            from services.email_service import send_login_otp_email
            result = send_login_otp_email(test_email, "Test User", "123456", 1)
            print(f"   {'✅ Success' if result else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("=" * 50)
    print("🎉 Email testing completed!")
    print(f"📬 Check your inbox at {test_email} for test emails")

def interactive_test():
    """Interactive email testing"""
    print("🧪 Interactive Email Testing")
    print("=" * 30)
    
    if not test_email_configuration():
        return
    
    email = input("Enter email address to test: ").strip()
    if not email:
        email = app.config.get('MAIL_USERNAME', 'test@example.com')
        print(f"Using default email: {email}")
    
    print("\nSelect email type to test:")
    print("1. Registration Email")
    print("2. Seller Approval Email")
    print("3. Product Added Email")
    print("4. Order Placed Email")
    print("5. Payment Success Email")
    print("6. All Emails")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    with app.app_context():
        if choice == "1":
            result = send_registration_email(email, "Test User", "customer")
        elif choice == "2":
            result = send_seller_approval_email(email, "Test Seller", "Test Business")
        elif choice == "3":
            result = send_product_added_email(email, "Test Seller", "Test Product", 123)
        elif choice == "4":
            result = send_order_placed_email(email, "Test Customer", "ORD123", 999.99, 456)
        elif choice == "5":
            result = send_payment_success_email(email, "Test Customer", "ORD123", 999.99, 456)
        elif choice == "6":
            test_all_emails()
            return
        else:
            print("❌ Invalid choice")
            return
        
        print(f"📧 Email sent: {'✅ Success' if result else '❌ Failed'}")

def main():
    """Main function"""
    print("📧 E-Commerce Platform Email Testing Tool")
    print("=" * 45)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        test_all_emails()

if __name__ == '__main__':
    main()