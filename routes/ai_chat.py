"""
AI Chat Routes
Handles AI shopping assistant chatbot endpoints
"""

from flask import render_template, request, jsonify, session
from app import app, get_db_connection
from services.ai_shopping_assistant import AIShoppingAssistant
import os

# Initialize AI assistant with database config
db_config = {
    'host': app.config.get('MYSQL_HOST', 'localhost'),
    'user': app.config.get('MYSQL_USER', 'root'),
    'password': app.config.get('MYSQL_PASSWORD', ''),
    'database': app.config.get('MYSQL_DB', 'amazon_db')
}

# Initialize OpenAI API key from environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Create AI assistant instance
ai_assistant = AIShoppingAssistant(api_key=OPENAI_API_KEY, db_config=db_config)

@app.route('/chat')
def chat_page():
    """
    AI Chat page
    """
    suggestions = ai_assistant.get_quick_suggestions()
    return render_template('chat.html', suggestions=suggestions)

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """
    Process chat message and return AI response
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        # Get customer ID if logged in
        customer_id = session.get('customer_id') if session.get('role') == 'customer' else None
        
        # Process message with AI assistant
        response = ai_assistant.chat(user_message, customer_id)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': 'I apologize, but I encountered an error. Please try again.'
        }), 500

@app.route('/api/chat/suggestions')
def chat_suggestions():
    """
    Get quick suggestion prompts
    """
    suggestions = ai_assistant.get_quick_suggestions()
    return jsonify({
        'success': True,
        'suggestions': suggestions
    })

@app.route('/api/chat/product/<int:product_id>')
def chat_product_details(product_id):
    """
    Get product details for chat
    """
    try:
        product = ai_assistant.get_product_details(product_id)
        
        if product:
            return jsonify({
                'success': True,
                'product': product
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat_history():
    """
    Clear chat conversation history
    """
    try:
        ai_assistant.clear_history()
        return jsonify({
            'success': True,
            'message': 'Chat history cleared'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/search', methods=['POST'])
def chat_search():
    """
    Direct product search from chat
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        # Extract criteria and search
        criteria = ai_assistant._extract_criteria(query)
        products = ai_assistant._search_products(criteria)
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products),
            'criteria': criteria
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
