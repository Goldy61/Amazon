from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, get_db_connection, login_required
from datetime import datetime

# Import email service functions
from services.email_service import (
    send_seller_approval_email, 
    send_seller_rejection_email
)

@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Summary stats ---
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='customer'")
    total_customers = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM users")
    total_users = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM sellers")
    total_sellers = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM sellers WHERE is_approved=0")
    pending_sellers = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM products WHERE is_active=1")
    total_products = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM orders")
    total_orders = cursor.fetchone()['count']

    cursor.execute("SELECT COALESCE(SUM(total_amount),0) as revenue FROM orders WHERE payment_status='completed'")
    total_revenue = cursor.fetchone()['revenue']

    # --- Daily sales (last 7 days) ---
    cursor.execute("""
        SELECT DATE(created_at) as day,
               COUNT(*) as orders,
               COALESCE(SUM(total_amount),0) as revenue
        FROM orders
        WHERE payment_status='completed'
          AND created_at >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
        GROUP BY DATE(created_at)
        ORDER BY day ASC
    """)
    daily_rows = cursor.fetchall()

    # --- Monthly sales (last 6 months) ---
    cursor.execute("""
        SELECT DATE_FORMAT(created_at,'%b %Y') as month,
               DATE_FORMAT(created_at,'%Y-%m') as month_key,
               COUNT(*) as orders,
               COALESCE(SUM(total_amount),0) as revenue
        FROM orders
        WHERE payment_status='completed'
          AND created_at >= DATE_SUB(CURDATE(), INTERVAL 5 MONTH)
        GROUP BY month_key, month
        ORDER BY month_key ASC
    """)
    monthly_rows = cursor.fetchall()

    # Build chart data — fill missing days with 0
    from datetime import date, timedelta
    import json as _json

    today = date.today()
    daily_map = {str(r['day']): {'orders': r['orders'], 'revenue': float(r['revenue'])} for r in daily_rows}
    daily_labels, daily_orders, daily_revenue = [], [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        label = d.strftime('%d %b')
        key = str(d)
        daily_labels.append(label)
        daily_orders.append(daily_map.get(key, {}).get('orders', 0))
        daily_revenue.append(daily_map.get(key, {}).get('revenue', 0))

    monthly_labels = [r['month'] for r in monthly_rows]
    monthly_orders = [r['orders'] for r in monthly_rows]
    monthly_revenue = [float(r['revenue']) for r in monthly_rows]

    # --- Recent orders ---
    cursor.execute("""
        SELECT o.*, c.first_name, c.last_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        ORDER BY o.created_at DESC LIMIT 5
    """)
    recent_orders = cursor.fetchall()

    # --- Pending sellers ---
    cursor.execute("""
        SELECT s.*, u.email FROM sellers s
        JOIN users u ON s.user_id = u.id
        WHERE s.is_approved=0 ORDER BY s.created_at DESC LIMIT 5
    """)
    pending_seller_list = cursor.fetchall()

    conn.close()

    return render_template('admin/dashboard_enhanced.html',
        total_customers=total_customers,
        total_users=total_users,
        total_sellers=total_sellers,
        pending_sellers=pending_sellers,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        pending_seller_list=pending_seller_list,
        daily_labels=_json.dumps(daily_labels),
        daily_orders=_json.dumps(daily_orders),
        daily_revenue=_json.dumps(daily_revenue),
        monthly_labels=_json.dumps(monthly_labels),
        monthly_orders=_json.dumps(monthly_orders),
        monthly_revenue=_json.dumps(monthly_revenue),
        now=datetime.now()
    )

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
    
    # Get seller details before approval
    cursor.execute("""
        SELECT s.*, u.email 
        FROM sellers s 
        JOIN users u ON s.user_id = u.id 
        WHERE s.id = %s
    """, (seller_id,))
    seller = cursor.fetchone()
    
    if seller:
        cursor.execute("UPDATE sellers SET is_approved = 1 WHERE id = %s", (seller_id,))
        conn.commit()
        
        # Send approval email
        try:
            send_seller_approval_email(
                seller['email'], 
                seller['owner_name'], 
                seller['business_name']
            )
            print(f"✅ Seller approval email sent to {seller['email']}")
        except Exception as e:
            print(f"❌ Failed to send seller approval email: {e}")
        
        flash('Seller approved successfully! Approval email sent.', 'success')
    else:
        flash('Seller not found!', 'error')
    
    conn.close()
    return redirect(url_for('admin_sellers'))

@app.route('/admin/block_seller/<int:seller_id>')
@login_required('admin')
def block_seller(seller_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get seller details before blocking
    cursor.execute("""
        SELECT s.*, u.email 
        FROM sellers s 
        JOIN users u ON s.user_id = u.id 
        WHERE s.id = %s
    """, (seller_id,))
    seller = cursor.fetchone()
    
    if seller:
        cursor.execute("UPDATE users SET is_active = 0 WHERE id = %s", (seller['user_id'],))
        cursor.execute("UPDATE sellers SET is_approved = 0 WHERE id = %s", (seller_id,))
        conn.commit()
        
        # Send rejection email
        try:
            send_seller_rejection_email(
                seller['email'], 
                seller['owner_name'], 
                seller['business_name'],
                "Your seller account has been suspended due to policy violations. Please contact support for more information."
            )
            print(f"✅ Seller rejection email sent to {seller['email']}")
        except Exception as e:
            print(f"❌ Failed to send seller rejection email: {e}")
        
        flash('Seller blocked successfully! Notification email sent.', 'success')
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
    
    # Get time period filter (default: all time)
    period = request.args.get('period', 'all')
    
    # Date filter based on period
    date_filter = ""
    chart_date_filter = ""
    
    if period == 'daily':
        date_filter = "AND DATE(o.created_at) = CURDATE()"
        chart_date_filter = "AND created_at >= CURDATE()"
    elif period == 'weekly':
        date_filter = "AND o.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        chart_date_filter = "AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
    elif period == 'monthly':
        date_filter = "AND o.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
        chart_date_filter = "AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
    elif period == 'yearly':
        date_filter = "AND o.created_at >= DATE_SUB(NOW(), INTERVAL 365 DAY)"
        chart_date_filter = "AND created_at >= DATE_SUB(NOW(), INTERVAL 365 DAY)"
    # 'all' means no filter
    
    # Sales Overview
    cursor.execute(f"""
        SELECT 
            COUNT(DISTINCT o.id) as total_orders,
            COUNT(DISTINCT o.customer_id) as total_customers,
            COALESCE(SUM(o.total_amount), 0) as total_revenue,
            COALESCE(AVG(o.total_amount), 0) as avg_order_value
        FROM orders o
        WHERE o.payment_status = 'completed' {date_filter}
    """)
    overview = cursor.fetchone()
    
    # Daily Sales - respects period filter
    if period == 'daily':
        # Show hourly data for today
        cursor.execute(f"""
            SELECT 
                HOUR(created_at) as hour,
                COUNT(*) as orders,
                COALESCE(SUM(total_amount), 0) as revenue
            FROM orders
            WHERE payment_status = 'completed' {chart_date_filter}
            GROUP BY HOUR(created_at)
            ORDER BY hour ASC
        """)
    else:
        # Show daily data based on period
        interval = 7 if period == 'weekly' else (30 if period == 'monthly' else (365 if period == 'yearly' else 30))
        cursor.execute(f"""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as orders,
                COALESCE(SUM(total_amount), 0) as revenue
            FROM orders
            WHERE payment_status = 'completed' {chart_date_filter}
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        """)
    daily_sales = cursor.fetchall()
    
    # Monthly Sales - respects period filter
    if period == 'yearly':
        # Show monthly data for this year
        cursor.execute(f"""
            SELECT 
                DATE_FORMAT(created_at, '%Y-%m') as month,
                DATE_FORMAT(created_at, '%b %Y') as month_name,
                COUNT(*) as orders,
                COALESCE(SUM(total_amount), 0) as revenue
            FROM orders
            WHERE payment_status = 'completed' {chart_date_filter}
            GROUP BY DATE_FORMAT(created_at, '%Y-%m')
            ORDER BY month ASC
        """)
    else:
        # Show last 12 months or filtered period
        cursor.execute(f"""
            SELECT 
                DATE_FORMAT(created_at, '%Y-%m') as month,
                DATE_FORMAT(created_at, '%b %Y') as month_name,
                COUNT(*) as orders,
                COALESCE(SUM(total_amount), 0) as revenue
            FROM orders
            WHERE payment_status = 'completed' {chart_date_filter}
            GROUP BY DATE_FORMAT(created_at, '%Y-%m')
            ORDER BY month ASC
        """)
    monthly_sales = cursor.fetchall()
    
    # Yearly Sales - respects period filter
    cursor.execute(f"""
        SELECT 
            YEAR(created_at) as year,
            COUNT(*) as orders,
            COALESCE(SUM(total_amount), 0) as revenue
        FROM orders
        WHERE payment_status = 'completed' {chart_date_filter}
        GROUP BY YEAR(created_at)
        ORDER BY year ASC
    """)
    yearly_sales = cursor.fetchall()
    
    # Top Products
    cursor.execute(f"""
        SELECT 
            p.name,
            p.image_url,
            COUNT(oi.id) as sales_count,
            SUM(oi.quantity) as total_quantity,
            COALESCE(SUM(oi.price * oi.quantity), 0) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.payment_status = 'completed' {date_filter}
        GROUP BY p.id, p.name, p.image_url
        ORDER BY sales_count DESC
        LIMIT 10
    """)
    top_products = cursor.fetchall()
    
    # Top Categories
    cursor.execute(f"""
        SELECT 
            c.name,
            COUNT(oi.id) as sales_count,
            COALESCE(SUM(oi.price * oi.quantity), 0) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN categories c ON p.category_id = c.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.payment_status = 'completed' {date_filter}
        GROUP BY c.id, c.name
        ORDER BY sales_count DESC
        LIMIT 10
    """)
    top_categories = cursor.fetchall()
    
    # Top Sellers
    cursor.execute(f"""
        SELECT 
            s.business_name,
            COUNT(oi.id) as orders,
            COALESCE(SUM(oi.price * oi.quantity), 0) as revenue
        FROM order_items oi
        JOIN sellers s ON oi.seller_id = s.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.payment_status = 'completed' {date_filter}
        GROUP BY s.id, s.business_name
        ORDER BY revenue DESC
        LIMIT 10
    """)
    top_sellers = cursor.fetchall()
    
    # Geographic Analysis - Extract city and state from TEXT field
    # Format: "Street Address, City, State - Pincode"
    # Using Python to parse addresses for reliability
    cursor.execute(f"""
        SELECT 
            o.shipping_address,
            COUNT(*) as orders,
            COALESCE(SUM(o.total_amount), 0) as revenue
        FROM orders o
        WHERE o.payment_status = 'completed' 
        AND o.shipping_address IS NOT NULL 
        AND o.shipping_address != '' {date_filter}
        GROUP BY o.shipping_address
    """)
    address_data = cursor.fetchall()
    
    # Parse addresses in Python
    city_stats = {}
    state_stats = {}
    
    for row in address_data:
        address = row['shipping_address']
        orders = row['orders']
        revenue = row['revenue']
        
        # Parse: "Street, City, State - Pincode"
        try:
            # Split by ' - ' to remove pincode
            address_without_pincode = address.split(' - ')[0] if ' - ' in address else address
            # Split by comma
            parts = [p.strip() for p in address_without_pincode.split(',')]
            
            if len(parts) >= 3:
                city = parts[-2]  # Second last part is city
                state = parts[-1]  # Last part is state
            elif len(parts) == 2:
                city = parts[-1]
                state = parts[-1]
            else:
                continue
            
            # Aggregate by city
            if city not in city_stats:
                city_stats[city] = {'city': city, 'state': state, 'orders': 0, 'revenue': 0}
            city_stats[city]['orders'] += orders
            city_stats[city]['revenue'] += revenue
            
            # Aggregate by state
            if state not in state_stats:
                state_stats[state] = {'state': state, 'orders': 0, 'revenue': 0}
            state_stats[state]['orders'] += orders
            state_stats[state]['revenue'] += revenue
        except:
            continue
    
    # Convert to list and sort
    top_cities = sorted(city_stats.values(), key=lambda x: x['orders'], reverse=True)[:10]
    top_states = sorted(state_stats.values(), key=lambda x: x['orders'], reverse=True)[:10]
    
    # Order Status Distribution
    cursor.execute(f"""
        SELECT 
            status,
            COUNT(*) as count
        FROM orders o
        WHERE 1=1 {date_filter}
        GROUP BY status
    """)
    status_distribution = cursor.fetchall()
    
    # Payment Method Distribution
    cursor.execute(f"""
        SELECT 
            COALESCE(payment_method, 'razorpay') as method,
            COUNT(*) as count,
            COALESCE(SUM(total_amount), 0) as revenue
        FROM orders o
        WHERE payment_status = 'completed' {date_filter}
        GROUP BY payment_method
    """)
    payment_methods = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin/analytics.html',
                         period=period,
                         overview=overview,
                         daily_sales=daily_sales,
                         monthly_sales=monthly_sales,
                         yearly_sales=yearly_sales,
                         top_products=top_products,
                         top_categories=top_categories,
                         top_sellers=top_sellers,
                         top_cities=top_cities,
                         top_states=top_states,
                         status_distribution=status_distribution,
                         payment_methods=payment_methods)