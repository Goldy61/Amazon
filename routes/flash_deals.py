from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, get_db_connection, login_required
from datetime import datetime, timedelta
from decimal import Decimal

@app.route('/flash-deals')
def flash_deals():
    """Display all active flash deals"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get active flash deals
    cursor.execute("""
        SELECT 
            fd.*,
            p.name,
            p.description,
            p.image_url,
            p.category_id,
            c.name as category_name,
            s.business_name,
            (fd.quantity_limit - fd.quantity_sold) as remaining_quantity
        FROM flash_deals fd
        JOIN products p ON fd.product_id = p.id
        JOIN categories c ON p.category_id = c.id
        JOIN sellers s ON p.seller_id = s.id
        WHERE fd.is_active = 1
        AND fd.start_time <= NOW()
        AND fd.end_time > NOW()
        ORDER BY fd.end_time ASC
    """)
    deals = cursor.fetchall()
    
    conn.close()
    return render_template('flash_deals.html', deals=deals)

@app.route('/daily-deals')
def daily_deals():
    """Display daily deals"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get today's deals
    cursor.execute("""
        SELECT 
            fd.*,
            p.name,
            p.description,
            p.image_url,
            p.category_id,
            c.name as category_name,
            s.business_name,
            (fd.quantity_limit - fd.quantity_sold) as remaining_quantity
        FROM flash_deals fd
        JOIN products p ON fd.product_id = p.id
        JOIN categories c ON p.category_id = c.id
        JOIN sellers s ON p.seller_id = s.id
        WHERE fd.is_active = 1
        AND fd.deal_type = 'daily'
        AND DATE(fd.start_time) = CURDATE()
        AND fd.end_time > NOW()
        ORDER BY fd.discount_percentage DESC
    """)
    deals = cursor.fetchall()
    
    conn.close()
    return render_template('daily_deals.html', deals=deals)

@app.route('/api/flash_deals/active')
def get_active_flash_deals():
    """API endpoint for active flash deals"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            fd.id,
            fd.product_id,
            fd.original_price,
            fd.deal_price,
            fd.discount_percentage,
            fd.quantity_limit,
            fd.quantity_sold,
            fd.end_time,
            p.name,
            p.image_url,
            (fd.quantity_limit - fd.quantity_sold) as remaining_quantity
        FROM flash_deals fd
        JOIN products p ON fd.product_id = p.id
        WHERE fd.is_active = 1
        AND fd.start_time <= NOW()
        AND fd.end_time > NOW()
        ORDER BY fd.end_time ASC
        LIMIT 10
    """)
    deals = cursor.fetchall()
    
    conn.close()
    
    # Convert to JSON-serializable format
    deals_list = []
    for deal in deals:
        deals_list.append({
            'id': deal['id'],
            'product_id': deal['product_id'],
            'name': deal['name'],
            'image_url': deal['image_url'],
            'original_price': float(deal['original_price']),
            'deal_price': float(deal['deal_price']),
            'discount_percentage': deal['discount_percentage'],
            'quantity_limit': deal['quantity_limit'],
            'quantity_sold': deal['quantity_sold'],
            'remaining_quantity': deal['remaining_quantity'],
            'end_time': deal['end_time'].isoformat()
        })
    
    return jsonify({'deals': deals_list})

@app.route('/admin/flash-deals')
@login_required('admin')
def admin_flash_deals():
    """Admin page to manage flash deals"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all flash deals
    cursor.execute("""
        SELECT 
            fd.*,
            p.name as product_name,
            p.image_url,
            s.business_name,
            (fd.quantity_limit - fd.quantity_sold) as remaining_quantity
        FROM flash_deals fd
        JOIN products p ON fd.product_id = p.id
        JOIN sellers s ON p.seller_id = s.id
        ORDER BY fd.created_at DESC
    """)
    deals = cursor.fetchall()
    
    # Get all products for creating new deals
    cursor.execute("""
        SELECT p.id, p.name, p.price, s.business_name
        FROM products p
        JOIN sellers s ON p.seller_id = s.id
        WHERE p.is_active = 1
        ORDER BY p.name
    """)
    products = cursor.fetchall()
    
    conn.close()
    return render_template('admin/flash_deals.html', deals=deals, products=products)

@app.route('/admin/flash-deals/create', methods=['POST'])
@login_required('admin')
def create_flash_deal():
    """Create a new flash deal"""
    product_id = request.form['product_id']
    deal_price = Decimal(request.form['deal_price'])
    quantity_limit = int(request.form['quantity_limit'])
    deal_type = request.form['deal_type']
    duration_hours = int(request.form['duration_hours'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get product original price
    cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('admin_flash_deals'))
    
    original_price = product['price']
    discount_percentage = int(((original_price - deal_price) / original_price) * 100)
    
    # Set start and end times
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=duration_hours)
    
    # Create flash deal
    cursor.execute("""
        INSERT INTO flash_deals 
        (product_id, original_price, deal_price, discount_percentage, 
         quantity_limit, start_time, end_time, deal_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (product_id, original_price, deal_price, discount_percentage,
          quantity_limit, start_time, end_time, deal_type))
    
    conn.commit()
    conn.close()
    
    flash('Flash deal created successfully!', 'success')
    return redirect(url_for('admin_flash_deals'))

@app.route('/admin/flash-deals/<int:deal_id>/toggle', methods=['POST'])
@login_required('admin')
def toggle_flash_deal(deal_id):
    """Activate or deactivate a flash deal"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE flash_deals 
        SET is_active = NOT is_active 
        WHERE id = %s
    """, (deal_id,))
    
    conn.commit()
    conn.close()
    
    flash('Flash deal status updated!', 'success')
    return redirect(url_for('admin_flash_deals'))

@app.route('/admin/flash-deals/<int:deal_id>/delete', methods=['POST'])
@login_required('admin')
def delete_flash_deal(deal_id):
    """Delete a flash deal"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM flash_deals WHERE id = %s", (deal_id,))
    
    conn.commit()
    conn.close()
    
    flash('Flash deal deleted!', 'success')
    return redirect(url_for('admin_flash_deals'))

@app.route('/api/check_flash_deal/<int:product_id>')
def check_flash_deal(product_id):
    """Check if product has an active flash deal"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id,
            deal_price,
            discount_percentage,
            end_time,
            (quantity_limit - quantity_sold) as remaining_quantity
        FROM flash_deals
        WHERE product_id = %s
        AND is_active = 1
        AND start_time <= NOW()
        AND end_time > NOW()
        AND quantity_sold < quantity_limit
        LIMIT 1
    """, (product_id,))
    
    deal = cursor.fetchone()
    conn.close()
    
    if deal:
        return jsonify({
            'has_deal': True,
            'deal_price': float(deal['deal_price']),
            'discount_percentage': deal['discount_percentage'],
            'end_time': deal['end_time'].isoformat(),
            'remaining_quantity': deal['remaining_quantity']
        })
    else:
        return jsonify({'has_deal': False})
