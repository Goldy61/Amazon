# AI Coding Guidelines for Multi-Vendor E-Commerce Platform

## Architecture Overview
This is a Flask-based multi-vendor e-commerce platform with MySQL database, supporting admin/seller/customer roles. Core components:
- **Routes** (`routes/`): Endpoint handlers (auth, customer, seller, admin, checkout, ai_chat)
- **Services** (`services/`): Business logic (email_service, otp_service, ai_chat_service)
- **Templates** (`templates/`): Jinja2 views with role-specific subdirs
- **Static** (`static/`): Assets with uploads/products for user images

Data flows: User requests → Routes → Services → MySQL DB. Integrations: Razorpay (payments), Flask-Mail (emails), OpenAI (AI chat).

## Critical Workflows
- **Start app**: `python run_app.py` (auto-checks DB connection)
- **Setup**: Install XAMPP, create `amazon_db`, import `database/schema.sql`, `pip install -r requirements.txt`, copy `.env` and configure
- **Test**: `python test_setup.py`, `python test_email.py`, `python test_ai_chat.py`
- **Debug**: Use `/routes` endpoint to list all registered routes

## Key Conventions & Patterns

### Authentication & Sessions
- Role-based access: `session['role']` in `{'admin', 'seller', 'customer'}`
- Decorator: `@login_required('seller')` for role enforcement
- Passwords: `hash_password()` and `check_password()` with bcrypt

### Database Operations
- Connection: `conn = get_db_connection()` (defined in app.py)
- Always use parameterized queries: `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))`
- Close connections: `conn.close()` after operations

### File Uploads
- Validate: `allowed_file(filename)` checks extensions `{'png', 'jpg', 'jpeg', 'gif'}`
- Secure: `secure_filename()` then save to `UPLOAD_FOLDER`
- Resize images: Use PIL `Image.open().resize().save()` for thumbnails

### Email System
- Templates in `templates/emails/` (e.g., `order_placed.html`)
- Send via `from services.email_service import send_order_placed_email`
- Context: Pass user/order data as dict to template rendering

### AI Chat Integration
- Service: `from services.ai_chat_service import get_chat_response`
- Context: `get_user_context()` provides role/name for personalization
- History: Store conversation in `session['chat_history']` as list of dicts

### API Endpoints
- JSON responses: `return jsonify({'success': True, 'data': result})`
- Cart count: `/api/cart_count` returns `{'count': int}`
- Error handling: Return 400/500 with `{'error': 'message'}`

### Route Registration
- Define routes in `routes/*.py` with `@app.route()` decorators
- Import routes after app init in `app.py`: `from routes import auth, customer, seller, admin, checkout, ai_chat`

### Common Patterns
- Flash messages: `flash('Success message', 'success')` for user feedback
- Redirects: `return redirect(url_for('route_name'))`
- Template rendering: `render_template('customer/products.html', products=products)`

## Examples
- **Add product route**: In `routes/seller.py`, query DB, validate form, `flash()` success, `redirect()`
- **Email notification**: `send_order_placed_email(order_data)` after payment success
- **AI response**: `response = get_chat_response(message, history); return jsonify(response)`
- **Image upload**: `if file and allowed_file(file.filename): filename = secure_filename(file.filename); file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))`