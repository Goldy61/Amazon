from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, get_db_connection, login_required
import random
import json
from datetime import datetime

# Import email service
from services.email_service import send_delivery_confirmation_email

@app.route('/delivery/dashboard')
@login_required('delivery')
def delivery_dashboard():
    """Delivery personnel dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get delivery person details
    cursor.execute("""
        SELECT dp.* FROM delivery_personnel dp
        WHERE dp.user_id = %s
    """, (session['user_id'],))
    delivery_person = cursor.fetchone()
    
    if not delivery_person:
        flash('Delivery personnel profile not found.', 'error')
        return redirect(url_for('login'))
    
    session['delivery_person_id'] = delivery_person['id']
    
    # Get assigned orders
    cursor.execute("""
        SELECT 
            o.id,
            o.order_number,
            o.status,
            o.delivery_otp,
            o.shipping_address,
            o.final_amount,
            o.created_at,
            c.first_name,
            c.last_name,
            u.email as customer_email,
            c.phone as customer_phone
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        WHERE o.delivery_person_id = %s
        AND o.status IN ('shipped', 'out_for_delivery')
        ORDER BY o.created_at DESC
    """, (delivery_person['id'],))
    assigned_orders = cursor.fetchall()
    
    # Parse shipping addresses
    for order in assigned_orders:
        try:
            order['shipping_address'] = json.loads(order['shipping_address'])
        except:
            order['shipping_address'] = {}
    
    # Get completed deliveries today
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM orders
        WHERE delivery_person_id = %s
        AND status = 'delivered'
        AND DATE(delivered_at) = CURDATE()
    """, (delivery_person['id'],))
    today_deliveries = cursor.fetchone()['count']
    
    # Get total deliveries
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM orders
        WHERE delivery_person_id = %s
        AND status = 'delivered'
    """, (delivery_person['id'],))
    total_deliveries = cursor.fetchone()['count']
    
    conn.close()
    
    return render_template('delivery/dashboard.html',
                         delivery_person=delivery_person,
                         assigned_orders=assigned_orders,
                         today_deliveries=today_deliveries,
                         total_deliveries=total_deliveries)

@app.route('/delivery/orders')
@login_required('delivery')
def delivery_orders():
    """View all assigned orders"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get delivery person ID
    cursor.execute("""
        SELECT id FROM delivery_personnel WHERE user_id = %s
    """, (session['user_id'],))
    delivery_person = cursor.fetchone()
    
    if not delivery_person:
        flash('Delivery personnel profile not found.', 'error')
        return redirect(url_for('login'))
    
    # Get all orders (active and completed)
    cursor.execute("""
        SELECT 
            o.id,
            o.order_number,
            o.status,
            o.delivery_otp,
            o.shipping_address,
            o.final_amount,
            o.created_at,
            o.delivered_at,
            c.first_name,
            c.last_name,
            u.email as customer_email,
            c.phone as customer_phone
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        WHERE o.delivery_person_id = %s
        ORDER BY 
            CASE 
                WHEN o.status IN ('shipped', 'out_for_delivery') THEN 0
                ELSE 1
            END,
            o.created_at DESC
    """, (delivery_person['id'],))
    orders = cursor.fetchall()
    
    # Parse shipping addresses
    for order in orders:
        try:
            order['shipping_address'] = json.loads(order['shipping_address'])
        except:
            order['shipping_address'] = {}
    
    conn.close()
    
    return render_template('delivery/orders.html', orders=orders)

@app.route('/delivery/verify/<int:order_id>', methods=['GET', 'POST'])
@login_required('delivery')
def verify_delivery(order_id):
    """Verify delivery with OTP"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get delivery person ID
    cursor.execute("""
        SELECT id FROM delivery_personnel WHERE user_id = %s
    """, (session['user_id'],))
    delivery_person = cursor.fetchone()
    
    if not delivery_person:
        flash('Delivery personnel profile not found.', 'error')
        return redirect(url_for('login'))
    
    # Get order details
    cursor.execute("""
        SELECT 
            o.*,
            c.first_name,
            c.last_name,
            u.email as customer_email,
            c.phone as customer_phone
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        WHERE o.id = %s AND o.delivery_person_id = %s
    """, (order_id, delivery_person['id']))
    order = cursor.fetchone()
    
    if not order:
        flash('Order not found or not assigned to you.', 'error')
        conn.close()
        return redirect(url_for('delivery_dashboard'))
    
    # Parse shipping address
    try:
        order['shipping_address'] = json.loads(order['shipping_address'])
    except:
        order['shipping_address'] = {}
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        
        if not order['delivery_otp']:
            flash('No OTP generated for this order. Please contact support.', 'error')
            conn.close()
            return redirect(url_for('verify_delivery', order_id=order_id))
        
        if entered_otp == order['delivery_otp']:
            # OTP verified - mark as delivered
            cursor.execute("""
                UPDATE orders 
                SET status = 'delivered', 
                    delivered_at = NOW()
                WHERE id = %s
            """, (order_id,))
            
            # Add delivery tracking entry
            cursor.execute("""
                INSERT INTO delivery_tracking (order_id, delivery_person_id, status, notes)
                VALUES (%s, %s, 'delivered', 'Delivery completed with OTP verification')
            """, (order_id, delivery_person['id']))
            
            conn.commit()
            
            # Send delivery confirmation emails
            try:
                # Get seller details
                cursor.execute("""
                    SELECT DISTINCT s.owner_name, u.email as seller_email
                    FROM order_items oi
                    JOIN sellers s ON oi.seller_id = s.id
                    JOIN users u ON s.user_id = u.id
                    WHERE oi.order_id = %s
                """, (order_id,))
                sellers = cursor.fetchall()
                
                customer_name = f"{order['first_name']} {order['last_name']}"
                
                # Send to customer
                send_delivery_confirmation_email(
                    order['customer_email'],
                    customer_name,
                    order['order_number'],
                    'customer'
                )
                print(f"✅ Delivery confirmation sent to customer: {order['customer_email']}")
                
                # Send to sellers
                for seller in sellers:
                    send_delivery_confirmation_email(
                        seller['seller_email'],
                        seller['owner_name'],
                        order['order_number'],
                        'seller'
                    )
                    print(f"✅ Delivery confirmation sent to seller: {seller['seller_email']}")
                    
            except Exception as e:
                print(f"❌ Failed to send delivery confirmation emails: {e}")
            
            conn.close()
            flash('✅ Delivery verified successfully! Order marked as delivered.', 'success')
            return redirect(url_for('delivery_dashboard'))
        else:
            flash('❌ Invalid OTP. Please try again.', 'error')
    
    conn.close()
    return render_template('delivery/verify.html', order=order)

@app.route('/delivery/generate_otp/<int:order_id>', methods=['POST'])
@login_required('delivery')
def generate_delivery_otp(order_id):
    """Generate OTP for delivery (if not already generated)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get delivery person ID
    cursor.execute("""
        SELECT id FROM delivery_personnel WHERE user_id = %s
    """, (session['user_id'],))
    delivery_person = cursor.fetchone()
    
    if not delivery_person:
        return jsonify({'success': False, 'message': 'Delivery personnel not found'})
    
    # Check if order exists and is assigned to this delivery person
    cursor.execute("""
        SELECT id, delivery_otp FROM orders 
        WHERE id = %s AND delivery_person_id = %s
    """, (order_id, delivery_person['id']))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        return jsonify({'success': False, 'message': 'Order not found'})
    
    if order['delivery_otp']:
        conn.close()
        return jsonify({'success': True, 'message': 'OTP already generated', 'otp': order['delivery_otp']})
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Update order with OTP
    cursor.execute("""
        UPDATE orders 
        SET delivery_otp = %s, 
            delivery_otp_generated_at = NOW(),
            status = 'out_for_delivery'
        WHERE id = %s
    """, (otp, order_id))
    
    conn.commit()
    conn.close()
    
    print(f"🔐 Delivery OTP generated for order #{order_id}: {otp}")
    
    return jsonify({'success': True, 'message': 'OTP generated successfully', 'otp': otp})

@app.route('/delivery/update_status/<int:order_id>', methods=['POST'])
@login_required('delivery')
def update_delivery_status(order_id):
    """Update delivery status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get delivery person ID
    cursor.execute("""
        SELECT id FROM delivery_personnel WHERE user_id = %s
    """, (session['user_id'],))
    delivery_person = cursor.fetchone()
    
    if not delivery_person:
        return jsonify({'success': False, 'message': 'Delivery personnel not found'})
    
    status = request.json.get('status')
    notes = request.json.get('notes', '')
    
    # Update order status
    cursor.execute("""
        UPDATE orders 
        SET status = %s
        WHERE id = %s AND delivery_person_id = %s
    """, (status, order_id, delivery_person['id']))
    
    # Add tracking entry
    cursor.execute("""
        INSERT INTO delivery_tracking (order_id, delivery_person_id, status, notes)
        VALUES (%s, %s, %s, %s)
    """, (order_id, delivery_person['id'], status, notes))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Status updated successfully'})
