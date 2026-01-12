from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, get_db_connection, login_required, allowed_file
from werkzeug.utils import secure_filename
from PIL import Image
import os
import uuid

@app.route('/seller/dashboard')
@login_required('seller')
def seller_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if seller is approved
    cursor.execute("SELECT is_approved FROM sellers WHERE id = %s", (session['seller_id'],))
    seller = cursor.fetchone()
    
    if not seller['is_approved']:
        flash('Your account is pending approval from admin.', 'warning')
        return render_template('seller/pending_approval.html')
    
    # Get dashboard stats
    cursor.execute("SELECT COUNT(*) as count FROM products WHERE seller_id = %s", (session['seller_id'],))
    total_products = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM order_items WHERE seller_id = %s", (session['seller_id'],))
    total_orders = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT COALESCE(SUM(total), 0) as revenue 
        FROM order_items 
        WHERE seller_id = %s AND status IN ('confirmed', 'shipped', 'delivered')
    """, (session['seller_id'],))
    total_revenue = cursor.fetchone()['revenue']
    
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM order_items 
        WHERE seller_id = %s AND status = 'pending'
    """, (session['seller_id'],))
    pending_orders = cursor.fetchone()['count']
    
    # Get recent orders
    cursor.execute("""
        SELECT oi.*, p.name as product_name, o.order_number, o.created_at as order_date,
               JSON_EXTRACT(o.shipping_address, '$.name') as customer_name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE oi.seller_id = %s
        ORDER BY o.created_at DESC
        LIMIT 5
    """, (session['seller_id'],))
    recent_orders = cursor.fetchall()
    
    conn.close()
    return render_template('seller/dashboard.html', 
                         total_products=total_products,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         pending_orders=pending_orders,
                         recent_orders=recent_orders)

@app.route('/seller/products')
@login_required('seller')
def seller_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.*, c.name as category_name 
        FROM products p 
        JOIN categories c ON p.category_id = c.id 
        WHERE p.seller_id = %s 
        ORDER BY p.created_at DESC
    """, (session['seller_id'],))
    products = cursor.fetchall()
    
    conn.close()
    return render_template('seller/products.html', products=products)

@app.route('/seller/add_product', methods=['GET', 'POST'])
@login_required('seller')
def add_product():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Handle image upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generate unique filename
                filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Resize and save image
                image = Image.open(file)
                image.thumbnail((800, 800), Image.Resampling.LANCZOS)
                image.save(filepath, optimize=True, quality=85)
                
                image_url = f"uploads/products/{filename}"
        
        # Generate SKU
        sku = f"SKU{uuid.uuid4().hex[:8].upper()}"
        
        # Insert product
        cursor.execute("""
            INSERT INTO products (seller_id, category_id, name, description, price, discount_price, 
                                quantity, sku, brand, weight, dimensions, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session['seller_id'],
            request.form['category_id'],
            request.form['name'],
            request.form['description'],
            request.form['price'],
            request.form['discount_price'] if request.form['discount_price'] else None,
            request.form['quantity'],
            sku,
            request.form.get('brand', ''),
            request.form.get('weight', None),
            request.form.get('dimensions', ''),
            image_url
        ))
        
        conn.commit()
        conn.close()
        flash('Product added successfully!', 'success')
        return redirect(url_for('seller_products'))
    
    # GET request - show form
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE is_active = 1")
    categories = cursor.fetchall()
    conn.close()
    
    return render_template('seller/add_product.html', categories=categories)

@app.route('/seller/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required('seller')
def edit_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product belongs to seller
    cursor.execute("SELECT * FROM products WHERE id = %s AND seller_id = %s", 
                   (product_id, session['seller_id']))
    product = cursor.fetchone()
    
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('seller_products'))
    
    if request.method == 'POST':
        # Handle image upload
        image_url = product['image_url']  # Keep existing image by default
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Resize and save image
                image = Image.open(file)
                image.thumbnail((800, 800), Image.Resampling.LANCZOS)
                image.save(filepath, optimize=True, quality=85)
                
                # Delete old image
                if product['image_url']:
                    old_filepath = os.path.join('static', product['image_url'])
                    if os.path.exists(old_filepath):
                        os.remove(old_filepath)
                
                image_url = f"uploads/products/{filename}"
        
        # Update product
        cursor.execute("""
            UPDATE products SET 
            category_id = %s, name = %s, description = %s, price = %s, discount_price = %s,
            quantity = %s, brand = %s, weight = %s, dimensions = %s, image_url = %s
            WHERE id = %s AND seller_id = %s
        """, (
            request.form['category_id'],
            request.form['name'],
            request.form['description'],
            request.form['price'],
            request.form['discount_price'] if request.form['discount_price'] else None,
            request.form['quantity'],
            request.form.get('brand', ''),
            request.form.get('weight', None),
            request.form.get('dimensions', ''),
            image_url,
            product_id,
            session['seller_id']
        ))
        
        conn.commit()
        conn.close()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('seller_products'))
    
    # GET request - show form
    cursor.execute("SELECT * FROM categories WHERE is_active = 1")
    categories = cursor.fetchall()
    conn.close()
    
    return render_template('seller/edit_product.html', product=product, categories=categories)

@app.route('/seller/delete_product/<int:product_id>')
@login_required('seller')
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product belongs to seller
    cursor.execute("SELECT image_url FROM products WHERE id = %s AND seller_id = %s", 
                   (product_id, session['seller_id']))
    product = cursor.fetchone()
    
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('seller_products'))
    
    # Delete image file
    if product['image_url']:
        filepath = os.path.join('static', product['image_url'])
        if os.path.exists(filepath):
            os.remove(filepath)
    
    # Delete product
    cursor.execute("DELETE FROM products WHERE id = %s AND seller_id = %s", 
                   (product_id, session['seller_id']))
    conn.commit()
    conn.close()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('seller_products'))

@app.route('/seller/orders')
@login_required('seller')
def seller_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT oi.*, p.name as product_name, o.order_number, o.created_at as order_date,
               JSON_EXTRACT(o.shipping_address, '$.name') as customer_name,
               JSON_EXTRACT(o.shipping_address, '$.phone') as customer_phone
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE oi.seller_id = %s
        ORDER BY o.created_at DESC
    """, (session['seller_id'],))
    orders = cursor.fetchall()
    
    conn.close()
    return render_template('seller/orders.html', orders=orders)

@app.route('/seller/update_order_status', methods=['POST'])
@login_required('seller')
def update_order_status():
    order_item_id = request.form['order_item_id']
    status = request.form['status']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update order item status
    cursor.execute("""
        UPDATE order_items SET status = %s 
        WHERE id = %s AND seller_id = %s
    """, (status, order_item_id, session['seller_id']))
    
    conn.commit()
    conn.close()
    
    flash('Order status updated successfully!', 'success')
    return redirect(url_for('seller_orders'))