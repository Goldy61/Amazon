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
    
    # Check for applied coupon
    coupon_id = None
    discount_amount = 0
    final_amount = total_amount
    
    if 'applied_coupon' in session:
        applied_coupon = session['applied_coupon']
        coupon_id = applied_coupon['id']
        discount_amount = float(applied_coupon['discount'])  # Convert to float
        final_amount = float(total_amount) - discount_amount  # Convert total_amount to float
        print(f"💰 Coupon applied: {applied_coupon['code']} - Discount: ₹{discount_amount:.2f}")
    
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
        # Create Razorpay order (use final_amount if coupon applied)
        razorpay_order = razorpay_client.order.create({
            'amount': int(final_amount * 100),  # Amount in paise
            'currency': 'INR',
            'receipt': order_number,
            'payment_capture': 1
        })
    except Exception as e:
        conn.close()
        flash(f'Payment gateway error: {str(e)}. Please check your Razorpay configuration.', 'error')
        return redirect(url_for('checkout'))
    
    # Create order in database with coupon information
    cursor.execute("""
        INSERT INTO orders (customer_id, order_number, total_amount, shipping_address, razorpay_order_id, coupon_id, discount_amount, final_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (session['customer_id'], order_number, total_amount, json.dumps(shipping_address), razorpay_order['id'], coupon_id, discount_amount, final_amount))
    
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
    
    # If coupon was used, record usage and increment count
    if coupon_id:
        try:
            # Record coupon usage
            cursor.execute("""
                INSERT INTO coupon_usage (coupon_id, customer_id, order_id, discount_amount)
                VALUES (%s, %s, %s, %s)
            """, (coupon_id, session['customer_id'], order_id, discount_amount))
            
            # Increment coupon used count
            cursor.execute("""
                UPDATE coupons SET used_count = used_count + 1 WHERE id = %s
            """, (coupon_id,))
            
            print(f"✅ Coupon usage recorded for order {order_number}")
            
            # Clear coupon from session
            session.pop('applied_coupon', None)
        except Exception as e:
            print(f"❌ Failed to record coupon usage: {e}")
    
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
    
    # Award loyalty points (1 point per ₹1 spent)
    try:
        from routes.loyalty import award_points
        points_earned = int(total_amount)
        award_points(session['customer_id'], points_earned, f'Points earned on order {order_number}', order_id)
        print(f"✅ Awarded {points_earned} loyalty points for order {order_number}")
    except Exception as e:
        print(f"❌ Failed to award loyalty points: {e}")
    
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
                         total_amount=final_amount,  # Use final_amount for payment
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
            status = 'confirmed',
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
    
    # Check for applied coupon
    coupon_id = None
    discount_amount = 0
    final_amount = total_amount
    
    if 'applied_coupon' in session:
        applied_coupon = session['applied_coupon']
        coupon_id = applied_coupon['id']
        discount_amount = applied_coupon['discount']
        final_amount = total_amount - discount_amount
        print(f"💰 Coupon applied: {applied_coupon['code']} - Discount: ₹{discount_amount:.2f}")
    
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
        # Create Razorpay order (use final_amount if coupon applied)
        razorpay_order = razorpay_client.order.create({
            'amount': int(final_amount * 100),  # Amount in paise
            'currency': 'INR',
            'receipt': order_number,
            'payment_capture': 1
        })
    except Exception as e:
        conn.close()
        flash(f'Payment gateway error: {str(e)}. Please check your Razorpay configuration.', 'error')
        return redirect(url_for('buy_now_checkout'))
    
    # Create order in database with coupon information
    cursor.execute("""
        INSERT INTO orders (customer_id, order_number, total_amount, shipping_address, razorpay_order_id, coupon_id, discount_amount, final_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (session['customer_id'], order_number, total_amount, json.dumps(shipping_address), razorpay_order['id'], coupon_id, discount_amount, final_amount))
    
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
    
    # If coupon was used, record usage and increment count
    if coupon_id:
        try:
            # Record coupon usage
            cursor.execute("""
                INSERT INTO coupon_usage (coupon_id, customer_id, order_id, discount_amount)
                VALUES (%s, %s, %s, %s)
            """, (coupon_id, session['customer_id'], order_id, discount_amount))
            
            # Increment coupon used count
            cursor.execute("""
                UPDATE coupons SET used_count = used_count + 1 WHERE id = %s
            """, (coupon_id,))
            
            print(f"✅ Coupon usage recorded for order {order_number}")
            
            # Clear coupon from session
            session.pop('applied_coupon', None)
        except Exception as e:
            print(f"❌ Failed to record coupon usage: {e}")
    
    conn.commit()
    conn.close()
    
    # Send order placed email to customer
    try:
        from services.email_service import send_order_placed_email, send_seller_order_notification
        import pymysql
        conn2 = get_db_connection()
        c2 = conn2.cursor()
        c2.execute("""
            SELECT cu.first_name, cu.last_name, u.email
            FROM customers cu JOIN users u ON cu.user_id = u.id
            WHERE cu.id = %s
        """, (session['customer_id'],))
        cust = c2.fetchone()
        if cust:
            send_order_placed_email(cust['email'], f"{cust['first_name']} {cust['last_name']}", order_number, total_amount, order_id)
            print(f"✅ Order placed email sent to {cust['email']}")
        # Award loyalty points
        from routes.loyalty import award_points
        award_points(session['customer_id'], int(total_amount), f'Points earned on order {order_number}', order_id)
        print(f"✅ Awarded {int(total_amount)} loyalty points for order {order_number}")
        conn2.close()
    except Exception as e:
        print(f"❌ Post-order tasks error: {e}")
    
    return render_template('customer/payment.html', 
                         order=razorpay_order, 
                         order_id=order_id,
                         total_amount=final_amount,  # Use final_amount for payment
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


# Coupon Routes
@app.route('/api/validate_coupon', methods=['POST'])
@login_required('customer')
def validate_coupon():
    """Validate and apply coupon code"""
    from decimal import Decimal
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        coupon_code = request.json.get('coupon_code', '').strip().upper()
        cart_total = Decimal(str(request.json.get('cart_total', 0)))
        
        if not coupon_code:
            return jsonify({'success': False, 'message': 'Please enter a coupon code'})
        
        # Check if coupon exists and is valid
        cursor.execute("""
            SELECT * FROM coupons 
            WHERE code = %s 
            AND is_active = TRUE
            AND (valid_until IS NULL OR valid_until > NOW())
            AND (usage_limit IS NULL OR used_count < usage_limit)
        """, (coupon_code,))
        
        coupon = cursor.fetchone()
        
        if not coupon:
            return jsonify({'success': False, 'message': 'Invalid or expired coupon code'})
        
        # Check minimum order amount
        if cart_total < coupon['min_order_amount']:
            return jsonify({
                'success': False, 
                'message': f'Minimum order amount of ₹{float(coupon["min_order_amount"]):.2f} required'
            })
        
        # Check if customer already used this coupon
        cursor.execute("""
            SELECT COUNT(*) as usage_count 
            FROM coupon_usage 
            WHERE coupon_id = %s AND customer_id = %s
        """, (coupon['id'], session['customer_id']))
        
        usage = cursor.fetchone()
        
        # Check per-customer usage limit (assuming 1 use per customer for most coupons)
        if usage['usage_count'] > 0 and coupon['usage_limit'] is not None:
            return jsonify({
                'success': False, 
                'message': 'You have already used this coupon'
            })
        
        # Calculate discount - convert all to Decimal for consistent math
        discount_value = Decimal(str(coupon['discount_value']))
        
        if coupon['discount_type'] == 'percentage':
            discount = (cart_total * discount_value) / Decimal('100')
            if coupon['max_discount_amount']:
                max_discount = Decimal(str(coupon['max_discount_amount']))
                discount = min(discount, max_discount)
        else:  # fixed
            discount = discount_value
        
        # Ensure discount doesn't exceed cart total
        discount = min(discount, cart_total)
        final_amount = cart_total - discount
        
        # Store coupon in session (convert Decimal to float for JSON serialization)
        session['applied_coupon'] = {
            'id': coupon['id'],
            'code': coupon['code'],
            'discount': float(discount),
            'description': coupon['description']
        }
        
        return jsonify({
            'success': True,
            'message': 'Coupon applied successfully!',
            'coupon': {
                'code': coupon['code'],
                'description': coupon['description'],
                'discount': float(discount),
                'final_amount': float(final_amount)
            }
        })
        
    except Exception as e:
        print(f"Error validating coupon: {e}")
        return jsonify({'success': False, 'message': 'Error applying coupon'})
    finally:
        conn.close()

@app.route('/api/remove_coupon', methods=['POST'])
@login_required('customer')
def remove_coupon():
    """Remove applied coupon"""
    if 'applied_coupon' in session:
        session.pop('applied_coupon')
    return jsonify({'success': True, 'message': 'Coupon removed'})

@app.route('/api/get_coupons', methods=['GET'])
@login_required('customer')
def get_available_coupons():
    """Get list of available coupons"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT code, description, discount_type, discount_value, 
                   min_order_amount, max_discount_amount, valid_until,
                   (usage_limit - used_count) as remaining_uses
            FROM coupons
            WHERE is_active = TRUE
            AND (valid_until IS NULL OR valid_until > NOW())
            AND (usage_limit IS NULL OR used_count < usage_limit)
            ORDER BY discount_value DESC
            LIMIT 10
        """)
        
        coupons = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'coupons': coupons
        })
        
    except Exception as e:
        print(f"Error fetching coupons: {e}")
        return jsonify({'success': False, 'message': 'Error fetching coupons'})
    finally:
        conn.close()
