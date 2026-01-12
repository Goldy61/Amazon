from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, get_db_connection, login_required

@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get dashboard stats
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'customer'")
    total_customers = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM sellers")
    total_sellers = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM sellers WHERE is_approved = 0")
    pending_sellers = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM products WHERE is_active = 1")
    total_products = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM orders")
    total_orders = cursor.fetchone()['count']
    
    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) as revenue FROM orders WHERE payment_status = 'completed'")
    total_revenue = cursor.fetchone()['revenue']
    
    # Get recent orders
    cursor.execute("""
        SELECT o.*, c.first_name, c.last_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        ORDER BY o.created_at DESC
        LIMIT 5
    """)
    recent_orders = cursor.fetchall()
    
    # Get pending sellers
    cursor.execute("""
        SELECT s.*, u.email
        FROM sellers s
        JOIN users u ON s.user_id = u.id
        WHERE s.is_approved = 0
        ORDER BY s.created_at DESC
        LIMIT 5
    """)
    pending_seller_list = cursor.fetchall()
    
    conn.close()
    return render_template('admin/dashboard.html',
                         total_customers=total_customers,
                         total_sellers=total_sellers,
                         pending_sellers=pending_sellers,
                         total_products=total_products,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders,
                         pending_seller_list=pending_seller_list)

@app.route('/admin/sellers')
@login_required('admin')
def admin_sellers():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.*, u.email, u.is_active
        FROM sellers s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.created_at DESC
    """)
    sellers = cursor.fetchall()
    
    conn.close()
    return render_template('admin/sellers.html', sellers=sellers)

@app.route('/admin/approve_seller/<int:seller_id>')
@login_required('admin')
def approve_seller(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE sellers SET is_approved = 1 WHERE id = %s", (seller_id,))
    conn.commit()
    conn.close()
    
    flash('Seller approved successfully!', 'success')
    return redirect(url_for('admin_sellers'))

@app.route('/admin/block_seller/<int:seller_id>')
@login_required('admin')
def block_seller(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user_id for the seller
    cursor.execute("SELECT user_id FROM sellers WHERE id = %s", (seller_id,))
    seller = cursor.fetchone()
    
    if seller:
        cursor.execute("UPDATE users SET is_active = 0 WHERE id = %s", (seller['user_id'],))
        cursor.execute("UPDATE sellers SET is_approved = 0 WHERE id = %s", (seller_id,))
        conn.commit()
        flash('Seller blocked successfully!', 'success')
    else:
        flash('Seller not found!', 'error')
    
    conn.close()
    return redirect(url_for('admin_sellers'))

@app.route('/admin/customers')
@login_required('admin')
def admin_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.*, u.email, u.is_active
        FROM customers c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
    """)
    customers = cursor.fetchall()
    
    conn.close()
    return render_template('admin/customers.html', customers=customers)

@app.route('/admin/toggle_user_status/<int:user_id>')
@login_required('admin')
def toggle_user_status(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE users SET is_active = NOT is_active WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
    
    flash('User status updated successfully!', 'success')
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/admin/categories')
@login_required('admin')
def admin_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM categories ORDER BY name")
    categories = cursor.fetchall()
    
    conn.close()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/add_category', methods=['POST'])
@login_required('admin')
def add_category():
    name = request.form['name']
    description = request.form.get('description', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO categories (name, description) VALUES (%s, %s)", 
                      (name, description))
        conn.commit()
        flash('Category added successfully!', 'success')
    except Exception as e:
        flash('Category name already exists!', 'error')
    
    conn.close()
    return redirect(url_for('admin_categories'))

@app.route('/admin/toggle_category_status/<int:category_id>')
@login_required('admin')
def toggle_category_status(category_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE categories SET is_active = NOT is_active WHERE id = %s", (category_id,))
    conn.commit()
    conn.close()
    
    flash('Category status updated successfully!', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/orders')
@login_required('admin')
def admin_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT o.*, c.first_name, c.last_name, c.phone
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        ORDER BY o.created_at DESC
    """)
    orders = cursor.fetchall()
    
    conn.close()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/order/<int:order_id>')
@login_required('admin')
def admin_order_detail(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get order details
    cursor.execute("""
        SELECT o.*, c.first_name, c.last_name, c.phone
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.id = %s
    """, (order_id,))
    order = cursor.fetchone()
    
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin_orders'))
    
    # Get order items
    cursor.execute("""
        SELECT oi.*, p.name, p.image_url, s.business_name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN sellers s ON oi.seller_id = s.id
        WHERE oi.order_id = %s
    """, (order_id,))
    order_items = cursor.fetchall()
    
    # Parse shipping address
    import json
    order['shipping_address'] = json.loads(order['shipping_address'])
    
    conn.close()
    return render_template('admin/order_detail.html', order=order, order_items=order_items)

@app.route('/admin/analytics')
@login_required('admin')
def admin_analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Monthly sales data
    cursor.execute("""
        SELECT DATE_FORMAT(created_at, '%Y-%m') as month, 
               COUNT(*) as orders, 
               SUM(total_amount) as revenue
        FROM orders 
        WHERE payment_status = 'completed'
        GROUP BY DATE_FORMAT(created_at, '%Y-%m')
        ORDER BY month DESC
        LIMIT 12
    """)
    monthly_sales = cursor.fetchall()
    
    # Top selling categories
    cursor.execute("""
        SELECT c.name, COUNT(oi.id) as sales_count, SUM(oi.total) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN categories c ON p.category_id = c.id
        WHERE oi.status IN ('confirmed', 'shipped', 'delivered')
        GROUP BY c.id, c.name
        ORDER BY sales_count DESC
        LIMIT 10
    """)
    top_categories = cursor.fetchall()
    
    # Top sellers
    cursor.execute("""
        SELECT s.business_name, COUNT(oi.id) as orders, SUM(oi.total) as revenue
        FROM order_items oi
        JOIN sellers s ON oi.seller_id = s.id
        WHERE oi.status IN ('confirmed', 'shipped', 'delivered')
        GROUP BY s.id, s.business_name
        ORDER BY revenue DESC
        LIMIT 10
    """)
    top_sellers = cursor.fetchall()
    
    conn.close()
    return render_template('admin/analytics.html',
                         monthly_sales=monthly_sales,
                         top_categories=top_categories,
                         top_sellers=top_sellers)