from flask import render_template, request, redirect, url_for, session, flash
from app import app, get_db_connection, hash_password, check_password, login_required

# Import email service functions
from services.email_service import (
    send_registration_email, 
    send_seller_approval_email, 
    send_seller_rejection_email
)

# Import OTP service functions
from services.otp_service import create_otp, verify_otp as verify_user_otp, get_user_otp_status

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get featured products
        cursor.execute("""
            SELECT p.*, c.name as category_name, s.business_name 
            FROM products p 
            JOIN categories c ON p.category_id = c.id 
            JOIN sellers s ON p.seller_id = s.id 
            WHERE p.is_active = 1 AND s.is_approved = 1 
            ORDER BY p.created_at DESC 
            LIMIT 8
        """)
        featured_products = cursor.fetchall()
        
        # Get categories
        cursor.execute("SELECT * FROM categories WHERE is_active = 1")
        categories = cursor.fetchall()
        
        conn.close()
        return render_template('index.html', products=featured_products, categories=categories)
    
    except Exception as e:
        print(f"Error in index route: {e}")
        # Return a simple response if there's an error
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE is_active = 1")
            categories = cursor.fetchall()
            conn.close()
            return render_template('index.html', products=[], categories=categories)
        except:
            # If even categories fail, return with empty data
            return render_template('index.html', products=[], categories=[])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        print(f"🔍 Login attempt: {email}")  # Debug log
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND is_active = 1", (email,))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User found: {user['email']}, Role: {user['role']}")  # Debug log
            if check_password(password, user['password_hash']):
                print("✅ Password verified successfully")  # Debug log
                
                # Get user name for OTP email
                user_name = "User"
                if user['role'] == 'customer':
                    cursor.execute("SELECT first_name, last_name FROM customers WHERE user_id = %s", (user['id'],))
                    customer = cursor.fetchone()
                    if customer:
                        user_name = f"{customer['first_name']} {customer['last_name']}"
                elif user['role'] == 'seller':
                    cursor.execute("SELECT owner_name FROM sellers WHERE user_id = %s", (user['id'],))
                    seller = cursor.fetchone()
                    if seller:
                        user_name = seller['owner_name']
                elif user['role'] == 'admin':
                    user_name = "Admin"
                
                # Store user info in session for OTP verification
                session['pending_login'] = {
                    'user_id': user['id'],
                    'email': user['email'],
                    'role': user['role'],
                    'user_name': user_name
                }
                
                # Create and send OTP
                otp_created = create_otp(user['id'], user['email'], user_name)
                
                conn.close()
                
                if otp_created:
                    flash('Verification code sent to your email. Please check your inbox.', 'info')
                    return redirect(url_for('verify_otp'))
                else:
                    flash('Failed to send verification code. Please try again.', 'error')
                    return render_template('auth/login.html')
                    
            else:
                print("❌ Password verification failed")  # Debug log
                flash('Invalid email or password.', 'error')
        else:
            print(f"❌ User not found: {email}")  # Debug log
            flash('Invalid email or password.', 'error')
        
        conn.close()
    
    return render_template('auth/login.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    # Check if user has pending login
    if 'pending_login' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    pending_login = session['pending_login']
    
    if request.method == 'POST':
        otp_code = request.form['otp_code'].strip()
        
        if not otp_code or len(otp_code) != 6:
            flash('Please enter a valid 6-digit verification code.', 'error')
            return render_template('auth/verify_otp.html', user_email=pending_login['email'])
        
        # Verify OTP
        verification_result = verify_user_otp(pending_login['user_id'], otp_code)
        
        if verification_result['valid']:
            # OTP verified successfully - complete login
            conn = get_db_connection()
            cursor = conn.cursor()
            
            session['user_id'] = pending_login['user_id']
            session['email'] = pending_login['email']
            session['role'] = pending_login['role']
            
            # Get additional user info based on role
            if pending_login['role'] == 'customer':
                cursor.execute("SELECT * FROM customers WHERE user_id = %s", (pending_login['user_id'],))
                customer = cursor.fetchone()
                if customer:
                    session['customer_id'] = customer['id']
                    session['name'] = f"{customer['first_name']} {customer['last_name']}"
            elif pending_login['role'] == 'seller':
                cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (pending_login['user_id'],))
                seller = cursor.fetchone()
                if seller:
                    session['seller_id'] = seller['id']
                    session['name'] = seller['business_name']
                    if not seller['is_approved']:
                        flash('Your seller account is pending approval.', 'warning')
            
            conn.close()
            
            # Clear pending login
            session.pop('pending_login', None)
            
            flash('Login successful! Welcome back.', 'success')
            
            # Redirect based on role
            print(f"🔄 Redirecting {pending_login['role']} to dashboard")  # Debug log
            if pending_login['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif pending_login['role'] == 'seller':
                return redirect(url_for('seller_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash(verification_result['message'], 'error')
    
    return render_template('auth/verify_otp.html', user_email=pending_login['email'])

@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    # Check if user has pending login
    if 'pending_login' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    pending_login = session['pending_login']
    
    # Create and send new OTP
    otp_created = create_otp(
        pending_login['user_id'], 
        pending_login['email'], 
        pending_login['user_name']
    )
    
    if otp_created:
        flash('New verification code sent to your email.', 'success')
    else:
        flash('Failed to send verification code. Please try again.', 'error')
    
    return redirect(url_for('verify_otp'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Email already registered.', 'error')
            conn.close()
            return render_template('auth/register.html')
        
        # Create user account
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
            (email, password_hash, role)
        )
        user_id = cursor.lastrowid
        
        # Create role-specific profile
        user_name = ""
        if role == 'customer':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            user_name = f"{first_name} {last_name}"
            cursor.execute(
                "INSERT INTO customers (user_id, first_name, last_name, phone) VALUES (%s, %s, %s, %s)",
                (user_id, first_name, last_name, request.form.get('phone', ''))
            )
        elif role == 'seller':
            user_name = request.form['owner_name']
            cursor.execute(
                """INSERT INTO sellers (user_id, business_name, owner_name, phone, address, city, state, pincode, gst_number) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (user_id, request.form['business_name'], request.form['owner_name'], 
                 request.form['phone'], request.form['address'], request.form['city'], 
                 request.form['state'], request.form['pincode'], request.form.get('gst_number', ''))
            )
        
        conn.commit()
        conn.close()
        
        # Send registration email
        try:
            send_registration_email(email, user_name, role)
            print(f"✅ Registration email sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send registration email: {e}")
        
        flash('Registration successful! Please check your email for confirmation.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required()
def profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        print(f"🔍 Profile POST request received")
        print(f"📝 Form data: {dict(request.form)}")
        print(f"📁 Files: {dict(request.files)}")
        print(f"👤 User ID: {session.get('user_id')}")
        print(f"🎭 Role: {session.get('role')}")
        
        # Handle profile update
        try:
            # Handle profile picture upload
            profile_picture_url = None
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename != '':
                    from werkzeug.utils import secure_filename
                    import uuid
                    import os
                    from PIL import Image
                    
                    # Validate file type
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    if '.' not in file.filename or \
                       file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                        flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF images only.', 'error')
                        return redirect(url_for('profile'))
                    
                    # Validate file size (5MB max)
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    if file_size > 5 * 1024 * 1024:
                        flash('File too large. Please upload an image smaller than 5MB.', 'error')
                        return redirect(url_for('profile'))
                    
                    filename = secure_filename(file.filename)
                    filename = f"profile_{uuid.uuid4().hex}_{filename}"
                    
                    # Create profile pictures directory if it doesn't exist
                    profile_upload_dir = 'static/uploads/profiles'
                    if not os.path.exists(profile_upload_dir):
                        os.makedirs(profile_upload_dir, exist_ok=True)
                    
                    filepath = os.path.join(profile_upload_dir, filename)
                    
                    try:
                        # Resize and save image
                        image = Image.open(file)
                        image = image.convert('RGB')
                        
                        # Resize to 300x300 for profile pictures
                        image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                        image.save(filepath, optimize=True, quality=90)
                        
                        profile_picture_url = f"uploads/profiles/{filename}"
                    except Exception as img_error:
                        flash(f'Error processing image: {str(img_error)}', 'error')
                        return redirect(url_for('profile'))
            
            # Only update profile if we're not just uploading a picture
            if profile_picture_url or 'first_name' in request.form or 'business_name' in request.form:
                if session['role'] == 'customer':
                    update_query = """
                        UPDATE customers SET 
                        first_name = %s, last_name = %s, phone = %s, 
                        address = %s, city = %s, state = %s, pincode = %s
                    """
                    params = [
                        request.form.get('first_name', ''), request.form.get('last_name', ''), 
                        request.form.get('phone', ''), request.form.get('address', ''),
                        request.form.get('city', ''), request.form.get('state', ''),
                        request.form.get('pincode', '')
                    ]
                    
                    if profile_picture_url:
                        update_query += ", profile_picture = %s"
                        params.append(profile_picture_url)
                    
                    update_query += " WHERE user_id = %s"
                    params.append(session['user_id'])
                    
                    cursor.execute(update_query, params)
                    
                    # Update session name if form data exists
                    if 'first_name' in request.form and 'last_name' in request.form:
                        session['name'] = f"{request.form['first_name']} {request.form['last_name']}"
                    
                elif session['role'] == 'seller':
                    update_query = """
                        UPDATE sellers SET 
                        business_name = %s, owner_name = %s, phone = %s,
                        address = %s, city = %s, state = %s, pincode = %s, gst_number = %s
                    """
                    params = [
                        request.form.get('business_name', ''), request.form.get('owner_name', ''),
                        request.form.get('phone', ''), request.form.get('address', ''),
                        request.form.get('city', ''), request.form.get('state', ''),
                        request.form.get('pincode', ''), request.form.get('gst_number', '')
                    ]
                    
                    if profile_picture_url:
                        update_query += ", profile_picture = %s"
                        params.append(profile_picture_url)
                    
                    update_query += " WHERE user_id = %s"
                    params.append(session['user_id'])
                    
                    cursor.execute(update_query, params)
                    
                    # Update session name if form data exists
                    if 'business_name' in request.form:
                        session['name'] = request.form['business_name']
                
                # Update email if changed (only if not uploading profile picture)
                if 'email' in request.form and not profile_picture_url:
                    new_email = request.form['email']
                    if new_email != session['email']:
                        # Check if new email already exists
                        cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", 
                                     (new_email, session['user_id']))
                        if cursor.fetchone():
                            flash('Email already exists. Please choose a different email.', 'error')
                        else:
                            cursor.execute("UPDATE users SET email = %s WHERE id = %s", 
                                         (new_email, session['user_id']))
                            session['email'] = new_email
                
                conn.commit()
                if profile_picture_url:
                    flash('Profile picture updated successfully!', 'success')
                else:
                    flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            conn.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
            print(f"Profile update error: {e}")  # Debug log
    
    # Get current profile data
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    profile_data = None
    stats = None
    
    if session['role'] == 'customer':
        cursor.execute("SELECT * FROM customers WHERE user_id = %s", (session['user_id'],))
        profile_data = cursor.fetchone()
        
        # Get customer stats
        if 'customer_id' in session:
            cursor.execute("""
                SELECT 
                    COUNT(o.id) as total_orders,
                    COALESCE(SUM(o.total_amount), 0) as total_spent
                FROM orders o 
                WHERE o.customer_id = %s AND o.payment_status = 'completed'
            """, (session['customer_id'],))
            stats = cursor.fetchone()
            
    elif session['role'] == 'seller':
        cursor.execute("SELECT * FROM sellers WHERE user_id = %s", (session['user_id'],))
        profile_data = cursor.fetchone()
        
        # Get seller stats
        if 'seller_id' in session:
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT p.id) as total_products,
                    COALESCE(SUM(oi.total), 0) as total_sales
                FROM products p 
                LEFT JOIN order_items oi ON p.id = oi.product_id
                LEFT JOIN orders o ON oi.order_id = o.id
                WHERE p.seller_id = %s AND (o.payment_status = 'completed' OR o.payment_status IS NULL)
            """, (session['seller_id'],))
            stats = cursor.fetchone()
    
    conn.close()
    return render_template('profile.html', user=user, profile=profile_data, stats=stats)