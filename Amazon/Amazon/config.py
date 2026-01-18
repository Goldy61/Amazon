import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # MySQL Configuration
    # Use environment variables for production (Vercel), fallback to localhost for development
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')  # Default XAMPP MySQL password is empty
    MYSQL_DB = os.environ.get('MYSQL_DB', 'amazon_db')
    
    # Upload Configuration
    UPLOAD_FOLDER = 'static/uploads/products'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Razorpay Configuration
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID') or 'rzp_test_S29syTllQCrTsO'
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET') or 'kR3BDGvZGM0R5gCCOLNueIh4'
    
    # Email Configuration (Flask-Mail)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Your Gmail address
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Your Gmail app password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # AI Chat Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    AI_CHAT_MODEL = 'gpt-3.5-turbo'
    AI_CHAT_MAX_TOKENS = 500
    AI_CHAT_TEMPERATURE = 0.7
    
    # Pagination
    PRODUCTS_PER_PAGE = 12
    ORDERS_PER_PAGE = 10