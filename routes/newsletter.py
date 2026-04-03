from flask import request, flash, redirect, url_for, jsonify
from app import app, get_db_connection
import re

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@app.route('/subscribe_newsletter', methods=['POST'])
def subscribe_newsletter():
    """Subscribe to newsletter"""
    email = request.form.get('email', '').strip()
    name = request.form.get('name', '').strip()
    
    if not email:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Email is required.'})
        flash('Email is required.', 'error')
        return redirect(url_for('index'))
    
    if not is_valid_email(email):
        if request.is_json:
            return jsonify({'success': False, 'message': 'Invalid email format.'})
        flash('Invalid email format.', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if already subscribed
    cursor.execute("SELECT id, is_active FROM newsletter_subscriptions WHERE email = %s", (email,))
    existing = cursor.fetchone()
    
    if existing:
        if existing['is_active']:
            conn.close()
            if request.is_json:
                return jsonify({'success': False, 'message': 'You are already subscribed!'})
            flash('You are already subscribed to our newsletter!', 'info')
            return redirect(url_for('index'))
        else:
            # Reactivate subscription
            cursor.execute("""
                UPDATE newsletter_subscriptions 
                SET is_active = TRUE, subscribed_at = NOW(), unsubscribed_at = NULL, name = %s
                WHERE email = %s
            """, (name, email))
            conn.commit()
            conn.close()
            if request.is_json:
                return jsonify({'success': True, 'message': 'Welcome back! You have been resubscribed.'})
            flash('Welcome back! You have been resubscribed to our newsletter.', 'success')
            return redirect(url_for('index'))
    
    # New subscription
    try:
        cursor.execute("""
            INSERT INTO newsletter_subscriptions (email, name) 
            VALUES (%s, %s)
        """, (email, name))
        conn.commit()
        conn.close()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Thank you for subscribing!'})
        flash('Thank you for subscribing to our newsletter!', 'success')
    except Exception as e:
        conn.close()
        if request.is_json:
            return jsonify({'success': False, 'message': 'Subscription failed. Please try again.'})
        flash('Subscription failed. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/unsubscribe_newsletter/<email>')
def unsubscribe_newsletter(email):
    """Unsubscribe from newsletter"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE newsletter_subscriptions 
        SET is_active = FALSE, unsubscribed_at = NOW()
        WHERE email = %s
    """, (email,))
    
    if cursor.rowcount > 0:
        conn.commit()
        flash('You have been unsubscribed from our newsletter.', 'info')
    else:
        flash('Email not found in our subscription list.', 'error')
    
    conn.close()
    return redirect(url_for('index'))
