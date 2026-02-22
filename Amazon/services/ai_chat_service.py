#!/usr/bin/env python3
"""
AI Chat Service for E-Commerce Platform
Provides intelligent assistance for customers and sellers using OpenAI GPT
"""

from openai import OpenAI
import json
from datetime import datetime
from flask import current_app, session
import pymysql
import traceback

def get_db_connection():
    """Get database connection"""
    return pymysql.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

def get_user_context():
    """Get current user context for personalized responses"""
    context = {
        'user_type': 'guest',
        'user_name': 'Guest',
        'user_id': None
    }
    
    if 'user_id' in session:
        context['user_id'] = session['user_id']
        context['user_type'] = session.get('role', 'customer')
        context['user_name'] = session.get('name', session.get('email', 'User'))
    
    return context

def get_platform_data():
    """Get relevant platform data for AI context"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic platform stats
        cursor.execute("SELECT COUNT(*) as total FROM products WHERE is_active = 1")
        product_count = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM categories WHERE is_active = 1")
        category_count = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM sellers WHERE is_approved = 1")
        seller_count = cursor.fetchone()['total']
        
        # Get popular categories
        cursor.execute("""
            SELECT c.name, COUNT(p.id) as product_count 
            FROM categories c 
            LEFT JOIN products p ON c.id = p.category_id AND p.is_active = 1
            WHERE c.is_active = 1
            GROUP BY c.id, c.name 
            ORDER BY product_count DESC 
            LIMIT 5
        """)
        popular_categories = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_products': product_count,
            'total_categories': category_count,
            'total_sellers': seller_count,
            'popular_categories': [cat['name'] for cat in popular_categories]
        }
    except Exception as e:
        print(f"Error getting platform data: {e}")
        return {
            'total_products': 0,
            'total_categories': 0,
            'total_sellers': 0,
            'popular_categories': []
        }

def create_system_prompt(user_context, platform_data):
    """Create system prompt based on user type and platform data"""
    
    base_prompt = f"""You are an AI assistant for a multi-vendor e-commerce platform similar to Amazon. 
    
Platform Information:
- Total Products: {platform_data['total_products']}
- Total Categories: {platform_data['total_categories']} 
- Total Sellers: {platform_data['total_sellers']}
- Popular Categories: {', '.join(platform_data['popular_categories'])}

Current User: {user_context['user_name']} ({user_context['user_type']})

Your role is to help users with:
1. Product inquiries and recommendations
2. Order support and tracking
3. Account management
4. Platform navigation
5. Seller guidance (for sellers)
6. General shopping assistance

Guidelines:
- Be helpful, friendly, and professional
- Provide accurate information about the platform
- If you don't know something specific, suggest contacting support
- Keep responses concise but informative
- Use emojis appropriately to make conversations engaging
- For technical issues, provide step-by-step guidance
"""

    if user_context['user_type'] == 'seller':
        base_prompt += """
        
Additional Seller Support:
- Help with product listing and optimization
- Explain seller dashboard features
- Assist with order management
- Provide selling tips and best practices
- Guide through seller policies and procedures
"""
    elif user_context['user_type'] == 'customer':
        base_prompt += """
        
Additional Customer Support:
- Help find products and compare options
- Assist with checkout and payment issues
- Explain shipping and return policies
- Guide through order tracking
- Provide shopping recommendations
"""
    elif user_context['user_type'] == 'admin':
        base_prompt += """
        
Additional Admin Support:
- Help with platform management
- Explain admin dashboard features
- Assist with seller and customer management
- Provide analytics insights
- Guide through administrative tasks
"""
    
    return base_prompt

def get_chat_response(user_message, conversation_history=None):
    """
    Get AI response for user message
    
    Args:
        user_message: User's message
        conversation_history: Previous conversation context
    
    Returns:
        dict: Response with message and metadata
    """
    try:
        # Initialize OpenAI client
        api_key = current_app.config['OPENAI_API_KEY']
        
        if not api_key or api_key == 'your-openai-api-key-here':
            return {
                'success': False,
                'message': "AI chat is currently unavailable. Please contact support for assistance.",
                'error': 'API key not configured'
            }
        
        client = OpenAI(api_key=api_key)
        
        # Get user context and platform data
        user_context = get_user_context()
        platform_data = get_platform_data()
        
        # Create system prompt
        system_prompt = create_system_prompt(user_context, platform_data)
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-6:]:  # Keep last 6 messages for context
                messages.append({
                    "role": "user" if msg['sender'] == 'user' else "assistant",
                    "content": msg['message']
                })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model=current_app.config['AI_CHAT_MODEL'],
            messages=messages,
            max_tokens=current_app.config['AI_CHAT_MAX_TOKENS'],
            temperature=current_app.config['AI_CHAT_TEMPERATURE'],
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        ai_message = response.choices[0].message.content.strip()
        
        return {
            'success': True,
            'message': ai_message,
            'tokens_used': response.usage.total_tokens,
            'model': current_app.config['AI_CHAT_MODEL']
        }
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if 'authentication' in error_msg or 'api key' in error_msg:
            return {
                'success': False,
                'message': "AI chat authentication failed. Please contact support.",
                'error': 'Authentication error'
            }
        elif 'rate limit' in error_msg or 'quota' in error_msg:
            return {
                'success': False,
                'message': "AI chat is temporarily busy. Please try again in a moment.",
                'error': 'Rate limit exceeded'
            }
        elif 'api' in error_msg:
            return {
                'success': False,
                'message': "AI chat is temporarily unavailable. Please try again later.",
                'error': f'API error: {str(e)}'
            }
        else:
            print(f"AI Chat Error: {e}")
            print(traceback.format_exc())
            return {
                'success': False,
                'message': "Sorry, I'm having trouble right now. Please contact support for assistance.",
                'error': f'Unexpected error: {str(e)}'
            }

def get_quick_suggestions(user_type='guest'):
    """Get quick suggestion buttons based on user type"""
    
    base_suggestions = [
        "How do I search for products?",
        "What are your shipping policies?",
        "How do I track my order?",
        "What payment methods do you accept?"
    ]
    
    if user_type == 'customer':
        return [
            "Help me find a product",
            "Track my recent order",
            "How do I return an item?",
            "Update my account information",
            "What are the shipping charges?"
        ]
    elif user_type == 'seller':
        return [
            "How do I add a new product?",
            "Check my sales performance",
            "How do I update inventory?",
            "Manage my orders",
            "Seller fee structure"
        ]
    elif user_type == 'admin':
        return [
            "Platform analytics overview",
            "Manage seller applications",
            "Customer support issues",
            "System performance metrics",
            "Revenue reports"
        ]
    
    return base_suggestions

def log_chat_interaction(user_message, ai_response, user_context):
    """Log chat interaction for analytics and improvement"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_logs (user_id, user_type, user_message, ai_response, tokens_used, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_context.get('user_id'),
            user_context.get('user_type', 'guest'),
            user_message,
            ai_response.get('message', ''),
            ai_response.get('tokens_used', 0),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error logging chat interaction: {e}")

def get_chat_analytics():
    """Get chat usage analytics for admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_chats,
                COUNT(DISTINCT user_id) as unique_users,
                AVG(tokens_used) as avg_tokens,
                DATE(created_at) as chat_date
            FROM chat_logs 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAYS)
            GROUP BY DATE(created_at)
            ORDER BY chat_date DESC
        """)
        daily_stats = cursor.fetchall()
        
        # Get popular queries
        cursor.execute("""
            SELECT user_message, COUNT(*) as frequency
            FROM chat_logs 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAYS)
            GROUP BY user_message
            ORDER BY frequency DESC
            LIMIT 10
        """)
        popular_queries = cursor.fetchall()
        
        conn.close()
        
        return {
            'daily_stats': daily_stats,
            'popular_queries': popular_queries
        }
        
    except Exception as e:
        print(f"Error getting chat analytics: {e}")
        return {'daily_stats': [], 'popular_queries': []}