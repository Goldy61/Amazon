from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, get_db_connection, login_required
import json

@app.route('/products')
def products():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get filters
    category_id = request.args.get('category')
    search = request.args.get('search', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort', 'newest')
    
    # Build query
    query = """
        SELECT p.*, c.name as category_name, s.business_name 
        FROM products p 
        JOIN categories c ON p.category_id = c.id 
        JOIN sellers s ON p.seller_id = s.id 
        WHERE p.is_active = 1 AND s.is_approved = 1
    """
    params = []
    
    if category_id:
        query += " AND p.category_id = %s"
        params.append(category_id)
    
    if search:
        query += " AND (p.name LIKE %s OR p.description LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    if min_price:
        query += " AND p.price >= %s"
        params.append(min_price)
    
    if max_price:
        query += " AND p.price <= %s"
        params.append(max_price)
    
    # Add sorting
    if sort_by == 'price_low':
        query += " ORDER BY p.price ASC"
    elif sort_by == 'price_high':
        query += " ORDER BY p.price DESC"
    elif sort_by == 'name':
        query += " ORDER BY p.name ASC"
    else:
        query += " ORDER BY p.created_at DESC"
    
    cursor.execute(query, params)
    products = cursor.fetchall()
    
    # Get categories for filter
    cursor.execute("SELECT * FROM categories WHERE is_active = 1")
    categories = cursor.fetchall()
    
    conn.close()
    return render_template('customer/products.html', products=products, categories=categories)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.*, c.name as category_name, s.business_name, s.city as seller_city 
        FROM products p 
        JOIN categories c ON p.category_id = c.id 
        JOIN sellers s ON p.seller_id = s.id 
        WHERE p.id = %s AND p.is_active = 1 AND s.is_approved = 1
    """, (product_id,))
    product = cursor.fetchone()
    
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('products'))
    
    # Get related products
    cursor.execute("""
        SELECT p.*, s.business_name 
        FROM products p 
        JOIN sellers s ON p.seller_id = s.id 
        WHERE p.category_id = %s AND p.id != %s AND p.is_active = 1 AND s.is_approved = 1 
        LIMIT 4
    """, (product['category_id'], product_id))
    related_products = cursor.fetchall()
    
    conn.close()
    return render_template('customer/product_detail.html', product=product, related_products=related_products)

@app.route('/add_to_cart', methods=['POST'])
@login_required('customer')
def add_to_cart():
    product_id = request.form['product_id']
    quantity = int(request.form.get('quantity', 1))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product exists and is available
    cursor.execute("SELECT quantity FROM products WHERE id = %s AND is_active = 1", (product_id,))
    product = cursor.fetchone()
    
    if not product:
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and 'XMLHttpRequest' in request.headers.get('X-Requested-With', ''):
            return jsonify({'success': False, 'message': 'Product not found.'})
        flash('Product not found.', 'error')
        return redirect(url_for('products'))
    
    if product['quantity'] < quantity:
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and 'XMLHttpRequest' in request.headers.get('X-Requested-With', ''):
            return jsonify({'success': False, 'message': 'Insufficient stock.'})
        flash('Insufficient stock.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    
    # Check if item already in cart
    cursor.execute("SELECT * FROM cart WHERE customer_id = %s AND product_id = %s", 
                   (session['customer_id'], product_id))
    cart_item = cursor.fetchone()
    
    if cart_item:
        # Update quantity
        new_quantity = cart_item['quantity'] + quantity
        if new_quantity > product['quantity']:
            if request.is_json or 'fetch' in request.headers.get('User-Agent', '').lower():
                return jsonify({'success': False, 'message': 'Cannot add more items. Insufficient stock.'})
            flash('Cannot add more items. Insufficient stock.', 'error')
        else:
            cursor.execute("UPDATE cart SET quantity = %s WHERE id = %s", 
                          (new_quantity, cart_item['id']))
            conn.commit()
            if request.is_json or 'fetch' in request.headers.get('User-Agent', '').lower():
                return jsonify({'success': True, 'message': 'Cart updated successfully!'})
            flash('Cart updated successfully!', 'success')
    else:
        # Add new item
        cursor.execute("INSERT INTO cart (customer_id, product_id, quantity) VALUES (%s, %s, %s)",
                      (session['customer_id'], product_id, quantity))
        conn.commit()
        if request.is_json or 'fetch' in request.headers.get('User-Agent', '').lower():
            return jsonify({'success': True, 'message': 'Item added to cart!'})
        flash('Item added to cart!', 'success')
    
    conn.close()
    
    # For AJAX requests, return JSON
    if request.is_json or 'fetch' in request.headers.get('User-Agent', '').lower():
        return jsonify({'success': True, 'message': 'Item added to cart!'})
    
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/cart')
@login_required('customer')
def cart():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.*, p.name, p.price, p.image_url, p.quantity as stock, s.business_name
        FROM cart c
        JOIN products p ON c.product_id = p.id
        JOIN sellers s ON p.seller_id = s.id
        WHERE c.customer_id = %s AND p.is_active = 1
    """, (session['customer_id'],))
    cart_items = cursor.fetchall()
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    conn.close()
    return render_template('customer/cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart', methods=['POST'])
@login_required('customer')
def update_cart():
    cart_id = request.form['cart_id']
    quantity = int(request.form['quantity'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if quantity <= 0:
        cursor.execute("DELETE FROM cart WHERE id = %s AND customer_id = %s", 
                      (cart_id, session['customer_id']))
    else:
        cursor.execute("UPDATE cart SET quantity = %s WHERE id = %s AND customer_id = %s",
                      (quantity, cart_id, session['customer_id']))
    
    conn.commit()
    conn.close()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:cart_id>')
@login_required('customer')
def remove_from_cart(cart_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE id = %s AND customer_id = %s", 
                  (cart_id, session['customer_id']))
    conn.commit()
    conn.close()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))