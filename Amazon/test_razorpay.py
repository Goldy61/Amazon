#!/usr/bin/env python3
"""
Test script to verify Razorpay credentials and connection
"""

import os
import razorpay
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_razorpay_connection():
    """Test Razorpay API connection and credentials"""
    
    # Get credentials from environment
    key_id = os.environ.get('RAZORPAY_KEY_ID')
    key_secret = os.environ.get('RAZORPAY_KEY_SECRET')
    
    print("Testing Razorpay Connection...")
    print(f"Key ID: {key_id}")
    print(f"Key Secret: {'*' * len(key_secret) if key_secret else 'Not set'}")
    
    if not key_id or not key_secret:
        print("❌ ERROR: Razorpay credentials not found in environment variables")
        print("Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in your .env file")
        return False
    
    try:
        # Initialize Razorpay client
        client = razorpay.Client(auth=(key_id, key_secret))
        
        # Test connection by creating a test order
        test_order = client.order.create({
            'amount': 100,  # 1 rupee in paise
            'currency': 'INR',
            'receipt': 'test_receipt_123',
            'payment_capture': 1
        })
        
        print("✅ SUCCESS: Razorpay connection successful!")
        print(f"Test order created: {test_order['id']}")
        return True
        
    except razorpay.errors.BadRequestError as e:
        print(f"❌ ERROR: Authentication failed - {str(e)}")
        print("Please check your Razorpay credentials")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error - {str(e)}")
        return False

if __name__ == "__main__":
    test_razorpay_connection()