#!/usr/bin/env python3
"""
AI Chat Routes for E-Commerce Platform
Handles AI chat interactions and API endpoints
"""

from flask import render_template, request, jsonify, session
from app import app, get_db_connection
from services.ai_chat_service import (
    get_chat_response, 
    get_quick_suggestions, 
    log_chat_interaction,
    get_user_context,
    get_chat_analytics
)
import json
from datetime import datetime

@app.route('/chat')
def chat_page():
    """Render the AI chat interface"""
    user_context = get_user_context()
    suggestions = get_quick_suggestions(user_context['user_type'])
    
    return render_template('chat/chat.html', 
                         user_context=user_context,
                         suggestions=suggestions)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint for chat interactions"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        # Get conversation history from session
        conversation_history = session.get('chat_history', [])
        
        # Get AI response
        ai_response = get_chat_response(user_message, conversation_history)
        
        if ai_response['success']:
            # Update conversation history
            conversation_history.append({
                'sender': 'user',
                'message': user_message,
                'timestamp': datetime.now().isoformat()
            })
            conversation_history.append({
                'sender': 'ai',
                'message': ai_response['message'],
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 20 messages
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
            
            session['chat_history'] = conversation_history
            
            # Log interaction
            user_context = get_user_context()
            log_chat_interaction(user_message, ai_response, user_context)
            
            return jsonify({
                'success': True,
                'message': ai_response['message'],
                'tokens_used': ai_response.get('tokens_used', 0)
            })
        else:
            return jsonify({
                'success': False,
                'message': ai_response['message'],
                'error': ai_response.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Sorry, I encountered an error. Please try again.',
            'error': str(e)
        }), 500

@app.route('/api/chat/suggestions')
def chat_suggestions():
    """Get quick suggestion buttons"""
    user_context = get_user_context()
    suggestions = get_quick_suggestions(user_context['user_type'])
    
    return jsonify({
        'success': True,
        'suggestions': suggestions,
        'user_type': user_context['user_type']
    })

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    session.pop('chat_history', None)
    return jsonify({'success': True, 'message': 'Chat history cleared'})

@app.route('/admin/chat_analytics')
def chat_analytics():
    """Admin page for chat analytics"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    analytics = get_chat_analytics()
    return render_template('admin/chat_analytics.html', analytics=analytics)

@app.route('/api/chat/history')
def chat_history():
    """Get chat history for current session"""
    history = session.get('chat_history', [])
    return jsonify({
        'success': True,
        'history': history
    })