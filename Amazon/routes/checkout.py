from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, get_db_connection, login_required, razorpay_client
import uuid
import json

# Import email service functions
from services.email_service import (
    send_order_placed_email,
    send_payment_success_email,
    send_payment_failed_email,
    send_order_status_email,
    send_seller_order_notification
)

@app.route('/checkout')
@login_required('customer')
def checkout():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get cart items
    cursor.execute("""
        SELECT c.*, p.name, p.price, p.image_url, s.business_name
        FROM cart c
        JOIN products p ON c.product_id = p.id
        JOIN sellers s ON p.seller_id = s.id
        WHERE c.customer_id = %s AND p.is_active = 1
    """, (session['customer_id'],))
    cart_items = cursor.fetchall()
    
    if not cart_items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart'))
    
    # Get customer details
    cursor.execute("SELECT * FROM customers WHERE id = %s", (session['customer_id'],))
    customer = cursor.fetchone()
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    conn.close()
    return render_template('customer/checkout.html', cart_items=cart_items, customer=customer, total=total)

@app.route('/place_order', methods=['POST'])
@login_required('customer')
def place_order():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get cart items
    cursor.execute("""
        SELECT c.*, p.name, p.price, p.seller_id, p.quantity as stock
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.customer_id = %s AND p.is_active = 1
    """, (session['customer_id'],))
    cart_items = cursor.fetchall()
    
    if not cart_items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart'))
    
    # Check stock availability
    for item in cart_items:
        if item['quantity'] > item['stock']:
            flash(f'Insufficient stock for {item["name"]}', 'error')
            return redirect(url_for('cart'))
    
    # Calculate total
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    
    # Get shipping address
    shipping_address = {
        'name': f"{request.form['first_name']} {request.form['last_name']}",
        'phone': request.form['phone'],
        'address': request.form['address'],
        'city': request.form['city'],
        'state': request.form['state'],
        'pincode': request.form['pincode']
    }
    
    # Generate order number
    order_number = f"ORD{uuid.uuid4().hex[:8].upper()}"
    
    try:
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': int(total_amount * 100),  # Amount in paise
            'currency': 'INR',
            'receipt': order_number,
            'payment_capture': 1
        })
    except Exception as e:
        conn.close()
        flash(f'Payment gateway error: {str(e)}. Please check your Razorpay configuration.', 'error')
        return redirect(url_for('checkout'))
    
    # Create order in database
    cursor.execute("""
        INSERT INTO orders (customer_id, order_number, total_amount, shipping_address, razorpay_order_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (session['customer_id'], order_number, total_amount, json.dumps(shipping_address), razorpay_order['id']))
    
    order_id = cursor.lastrowid
    
    # Create order items
    for item in cart_items:
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, total)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (order_id, item['product_id'], item['seller_id'], item['quantity'], 
              item['price'], item['price'] * item['quantity']))
        
        # Update product quantity
        cursor.execute("UPDATE products SET quantity = quantity - %s WHERE id = %s",
                      (item['quantity'], item['product_id']))
    
    # Clear cart
    cursor.execute("DELETE FROM cart WHERE customer_id = %s", (session['customer_id'],))
    
    # Get customer details for email
    cursor.execute("""
        SELECT c.first_name, c.last_name, u.email 
        FROM customers c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.id = %s
    """, (session['customer_id'],))
    customer = cursor.fetchone()
    
    conn.commit()
    
    # Send order placed email to customer
    if customer:
        try:
            customer_name = f"{customer['first_name']} {customer['last_name']}"
            send_order_placed_email(
                customer['email'], 
                customer_name, 
                order_number, 
                total_amount, 
                order_id
            )
            print(f"✅ Order placed email sent to {customer['email']}")
        except Exception as e:
            print(f"❌ Failed to send order placed email: {e}")
    
    # Send order notifications to sellers
    try:
        cursor.execute("""
            SELECT DISTINCT oi.seller_id, s.owner_name, u.email, p.name, oi.quantity
            FROM order_items oi
            JOIN sellers s ON oi.seller_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order_id,))
        sellers = cursor.fetchall()
        
        for seller in sellers:
            send_seller_order_notification(
                seller['email'],
                seller['owner_name'],
                order_number,
                seller['name'],
                seller['quantity'],
                order_id
            )
            print(f"✅ Seller order notification sent to {seller['email']}")
    except Exception as e:
        print(f"❌ Failed to send seller notifications: {e}")
    
    conn.close()
    
    return render_template('customer/payment.html', 
                         order=razorpay_order, 
                         order_id=order_id,
                         total_amount=total_amount,
                         razorpay_key_id=app.config['RAZORPAY_KEY_ID'])

@app.route('/payment_success', methods=['POST'])
@login_required('customer')
def payment_success():
    razorpay_order_id = request.form['razorpay_order_id']
    razorpay_payment_id = request.form['razorpay_payment_id']
    razorpay_signature = request.form['razorpay_signature']
    order_id = request.form['order_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verify payment signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        
        # Update order status
        cursor.execute("""
            UPDATE orders SET 
            payment_status = 'completed', 
            order_status = 'confirmed',
            razorpay_payment_id = %s
            WHERE id = %s AND customer_id = %s
        """, (razorpay_payment_id, order_id, session['customer_id']))
        
        # Create payment record
        cursor.execute("""
            INSERT INTO payments (order_id, razorpay_order_id, razorpay_payment_id, razorpay_signature, amount, status)
            SELECT %s, %s, %s, %s, total_amount, 'captured'
            FROM orders WHERE id = %s
        """, (order_id, razorpay_order_id, razorpay_payment_id, razorpay_signature, order_id))
        
        # Get order and customer details for email
        cursor.execute("""
            SELECT o.order_number, o.total_amount, c.first_name, c.last_name, u.email
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN users u ON c.user_id = u.id
            WHERE o.id = %s
        """, (order_id,))
        order_details = cursor.fetchone()
        
        conn.commit()
        
        # Send payment success email
        if order_details:
            try:
                customer_name = f"{order_details['first_name']} {order_details['last_name']}"
                send_payment_success_email(
                    order_details['email'],
                    customer_name,
                    order_details['order_number'],
                    order_details['total_amount'],
                    order_id
                )
                print(f"✅ Payment success email sent to {order_details['email']}")
            except Exception as e:
                print(f"❌ Failed to send payment success email: {e}")
        
        flash('Payment successful! Your order has been confirmed.', 'success')
        
    except Exception as e:
        # Payment verification failed
        cursor.execute("UPDATE orders SET payment_status = 'failed' WHERE id = %s", (order_id,))
        
        # Get order and customer details for failed payment email
        cursor.execute("""
            SELECT o.order_number, c.first_name, c.last_name, u.email
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN users u ON c.user_id = u.id
            WHERE o.id = %s
        """, (order_id,))
        order_details = cursor.fetchone()
        
        conn.commit()
        
        # Send payment failed email
        if order_details:
            try:
                customer_name = f"{order_details['first_name']} {order_details['last_name']}"
                send_payment_failed_email(
                    order_details['email'],
                    customer_name,
                    order_details['order_number'],
                    order_id
                )
                print(f"✅ Payment failed email sent to {order_details['email']}")
            except Exception as e:
                print(f"❌ Failed to send payment failed email: {e}")
        
        flash('Payment verification failed. Please contact support.', 'error')
    
    conn.close()
    return redirect(url_for('order_history'))

@app.route('/buy_now', methods=['POST'])
@login_required('customer')
def buy_now():
    product_id = request.form['product_id']
    quantity = int(request.form.get('quantity', 1))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product exists and is available
    cursor.execute("""
        SELECT p.*, s.business_name 
        FROM products p 
        JOIN sellers s ON p.seller_id = s.id 
        WHERE p.id = %s AND p.is_active = 1 AND s.is_approved = 1
    """, (product_id,))
    product = cursor.fetchone()
    
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('products'))
    
    if product['quantity'] < quantity:
        flash('Insufficient stock.', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    
    # Store buy now item in session for checkout
    session['buy_now_item'] = {
        'product_id': product_id,
        'quantity': quantity,
        'product_name': product['name'],
        'price': float(product['discount_price']) if product['discount_price'] else float(product['price']),
        'seller_id': product['seller_id'],
        'business_name': product['business_name']
    }
    
    conn.close()
    return redirect(url_for('buy_now_checkout'))

@app.route('/buy_now_checkout')
@login_required('customer')
def buy_now_checkout():
    if 'buy_now_item' not in session:
        flash('No item selected for purchase.', 'error')
        return redirect(url_for('products'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get customer details
    cursor.execute("SELECT * FROM customers WHERE id = %s", (session['customer_id'],))
    customer = cursor.fetchone()
    
    buy_now_item = session['buy_now_item']
    total = buy_now_item['price'] * buy_now_item['quantity']
    
    conn.close()
    return render_template('customer/buy_now_checkout.html', 
                         item=buy_now_item, 
                         customer=customer, 
                         total=total)

@app.route('/place_buy_now_order', methods=['POST'])
@login_required('customer')
def place_buy_now_order():
    if 'buy_now_item' not in session:
        flash('No item selected for purchase.', 'error')
        return redirect(url_for('products'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    buy_now_item = session['buy_now_item']
    
    # Check stock availability again
    cursor.execute("SELECT quantity FROM products WHERE id = %s AND is_active = 1", 
                   (buy_now_item['product_id'],))
    product = cursor.fetchone()
    
    if not product or product['quantity'] < buy_now_item['quantity']:
        flash('Product is no longer available in the requested quantity.', 'error')
        return redirect(url_for('products'))
    
    # Calculate total
    total_amount = buy_now_item['price'] * buy_now_item['quantity']
    
    # Get shipping address
    shipping_address = {
        'name': f"{request.form['first_name']} {request.form['last_name']}",
        'phone': request.form['phone'],
        'address': request.form['address'],
        'city': request.form['city'],
        'state': request.form['state'],
        'pincode': request.form['pincode']
    }
    
    # Generate order number
    order_number = f"ORD{uuid.uuid4().hex[:8].upper()}"
    
    try:
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': int(total_amount * 100),  # Amount in paise
            'currency': 'INR',
            'receipt': order_number,
            'payment_capture': 1
        })
    except Exception as e:
        conn.close()
        flash(f'Payment gateway error: {str(e)}. Please check your Razorpay configuration.', 'error')
        return redirect(url_for('buy_now_checkout'))
    
    # Create order in database
    cursor.execute("""
        INSERT INTO orders (customer_id, order_number, total_amount, shipping_address, razorpay_order_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (session['customer_id'], order_number, total_amount, json.dumps(shipping_address), razorpay_order['id']))
    
    order_id = cursor.lastrowid
    
    # Create order item
    cursor.execute("""
        INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, total)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (order_id, buy_now_item['product_id'], buy_now_item['seller_id'], 
          buy_now_item['quantity'], buy_now_item['price'], total_amount))
    
    # Update product quantity
    cursor.execute("UPDATE products SET quantity = quantity - %s WHERE id = %s",
                  (buy_now_item['quantity'], buy_now_item['product_id']))
    
    # Clear buy now item from session
    session.pop('buy_now_item', None)
    
    conn.commit()
    conn.close()
    
    return render_template('customer/payment.html', 
                         order=razorpay_order, 
                         order_id=order_id,
                         total_amount=total_amount,
                         razorpay_key_id=app.config['RAZORPAY_KEY_ID'])

@app.route('/orders')
@login_required('customer')
def order_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT o.*, COUNT(oi.id) as item_count
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.customer_id = %s
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """, (session['customer_id'],))
    orders = cursor.fetchall()
    
    conn.close()
    return render_template('customer/orders.html', orders=orders)

@app.route('/order/<int:order_id>')
@login_required('customer')
def order_detail(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get order details
    cursor.execute("SELECT * FROM orders WHERE id = %s AND customer_id = %s", 
                   (order_id, session['customer_id']))
    order = cursor.fetchone()
    
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('order_history'))
    
    # Get order items
    cursor.execute("""
        SELECT oi.*, p.name, p.image_url, s.business_name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN sellers s ON oi.seller_id = s.id
        WHERE oi.order_id = %s
    """, (order_id,))
    order_items = cursor.fetchall()
    
    # Parse shipping address with error handling
    try:
        if order['shipping_address']:
            order['shipping_address'] = json.loads(order['shipping_address'])
        else:
            order['shipping_address'] = {
                'name': 'N/A',
                'address': 'N/A',
                'city': 'N/A',
                'state': 'N/A',
                'pincode': 'N/A',
                'phone': 'N/A'
            }
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing shipping address: {e}")
        order['shipping_address'] = {
            'name': 'N/A',
            'address': 'N/A',
            'city': 'N/A',
            'state': 'N/A',
            'pincode': 'N/A',
            'phone': 'N/A'
        }
    
    conn.close()
    return render_template('customer/order_detail.html', order=order, order_items=order_items)

@app.route('/payment_failed')
@login_required('customer')
def payment_failed():
    flash('Payment failed. Please try again.', 'error')
    return redirect(url_for('cart'))