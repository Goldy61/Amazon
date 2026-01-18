from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql
import bcrypt
import os
from werkzeug.utils import secure_filename
from PIL import Image
import razorpay
from datetime import datetime
import uuid
import json
from config import Config

# Import email service
from services.email_service import mail

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Mail
mail.init_app(app)

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(app.config['RAZORPAY_KEY_ID'], app.config['RAZORPAY_KEY_SECRET']))

# Database connection
def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login_required(role=None):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('Access denied.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# Create upload directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Add a simple test route
@app.route('/test')
def test_route():
    return "Flask app is working! Routes are registered."

# Debug route to list all registered routes
@app.route('/routes')
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return jsonify(routes)

# API route for cart count
@app.route('/api/cart_count')
def api_cart_count():
    if 'customer_id' not in session:
        return jsonify({'count': 0})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantity) as count FROM cart WHERE customer_id = %s", 
                      (session['customer_id'],))
        result = cursor.fetchone()
        conn.close()
        
        count = result['count'] if result['count'] else 0
        return jsonify({'count': count})
    except:
        return jsonify({'count': 0})

# Import routes after app initialization to register them with the app
try:
    # Import all route modules to register their routes
    import routes.auth
    import routes.customer
    import routes.checkout
    import routes.seller
    import routes.admin
    import routes.ai_chat
    print("✅ All routes imported successfully")
except ImportError as e:
    print(f"❌ Warning: Could not import all routes: {e}")
    print("Make sure all route files exist in the routes/ directory")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)