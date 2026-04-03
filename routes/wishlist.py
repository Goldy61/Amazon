from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, get_db_connection, login_required

@app.route('/wishlist')
@login_required('customer')
def wishlist():
    """Display customer's wishlist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT w.*, p.name, p.price, p.discount_price, p.image_url, 
                   p.quantity as stock, 
                   COALESCE(p.average_rating, 0) as average_rating, 
                   COALESCE(p.review_count, 0) as review_count,
                   s.business_name, c.name as category_name
            FROM wishlist w
            JOIN products p ON w.product_id = p.id
            JOIN sellers s ON p.seller_id = s.id
            JOIN categories c ON p.category_id = c.id
            WHERE w.customer_id = %s AND p.is_active = 1
            ORDER BY w.created_at DESC
        """, (session['customer_id'],))
        wishlist_items = cursor.fetchall()
    except Exception as e:
        print(f"Wishlist error: {e}")
        # If wishlist table doesn't exist or columns missing, show empty wishlist
        flash('Wishlist feature is being set up. Please run the database migration.', 'info')
        wishlist_items = []
    
    conn.close()
    return render_template('customer/wishlist.html', wishlist_items=wishlist_items)

@app.route('/add_to_wishlist', methods=['POST'])
@login_required('customer')
def add_to_wishlist():
    """Add product to wishlist"""
    product_id = request.form.get('product_id') or request.json.get('product_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product exists
    cursor.execute("SELECT id FROM products WHERE id = %s AND is_active = 1", (product_id,))
    if not cursor.fetchone():
        conn.close()
        if request.is_json:
            return jsonify({'success': False, 'message': 'Product not found.'})
        flash('Product not found.', 'error')
        return redirect(url_for('products'))
    
    # Check if already in wishlist
    cursor.execute("SELECT id FROM wishlist WHERE customer_id = %s AND product_id = %s", 
                   (session['customer_id'], product_id))
    if cursor.fetchone():
        conn.close()
        if request.is_json:
            return jsonify({'success': False, 'message': 'Already in wishlist.'})
        flash('Product already in wishlist.', 'info')
        return redirect(url_for('product_detail', product_id=product_id))
    
    # Add to wishlist
    cursor.execute("INSERT INTO wishlist (customer_id, product_id) VALUES (%s, %s)",
                  (session['customer_id'], product_id))
    conn.commit()
    conn.close()
    
    if request.is_json:
        return jsonify({'success': True, 'message': 'Added to wishlist!'})
    flash('Added to wishlist!', 'success')
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/remove_from_wishlist/<int:wishlist_id>')
@login_required('customer')
def remove_from_wishlist(wishlist_id):
    """Remove product from wishlist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wishlist WHERE id = %s AND customer_id = %s", 
                  (wishlist_id, session['customer_id']))
    conn.commit()
    conn.close()
    flash('Removed from wishlist.', 'info')
    return redirect(url_for('wishlist'))

@app.route('/api/wishlist_check/<int:product_id>')
@login_required('customer')
def wishlist_check(product_id):
    """Check if product is in wishlist (for AJAX)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM wishlist WHERE customer_id = %s AND product_id = %s", 
                   (session['customer_id'], product_id))
    in_wishlist = cursor.fetchone() is not None
    conn.close()
    return jsonify({'in_wishlist': in_wishlist})

@app.route('/api/wishlist_count')
@login_required('customer')
def wishlist_count():
    """Get wishlist item count (for navbar badge)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM wishlist WHERE customer_id = %s", 
                   (session['customer_id'],))
    count = cursor.fetchone()['count']
    conn.close()
    return jsonify({'count': count})


# API endpoints for wishlist (used by product cards)
@app.route('/api/wishlist/add', methods=['POST'])
@login_required('customer')
def api_add_to_wishlist():
    """Add product to wishlist via API"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({
                'success': False,
                'message': 'Product ID is required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if product exists
        cursor.execute("SELECT id FROM products WHERE id = %s AND is_active = 1", (product_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404
        
        # Check if already in wishlist
        cursor.execute("""
            SELECT id FROM wishlist 
            WHERE customer_id = %s AND product_id = %s
        """, (session['customer_id'], product_id))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Already in wishlist'
            })
        
        # Add to wishlist
        cursor.execute("""
            INSERT INTO wishlist (customer_id, product_id) 
            VALUES (%s, %s)
        """, (session['customer_id'], product_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Added to wishlist!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/wishlist/remove', methods=['POST'])
@login_required('customer')
def api_remove_from_wishlist():
    """Remove product from wishlist via API"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({
                'success': False,
                'message': 'Product ID is required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM wishlist 
            WHERE customer_id = %s AND product_id = %s
        """, (session['customer_id'], product_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Removed from wishlist'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/wishlist/list')
@login_required('customer')
def api_wishlist_list():
    """Get wishlist items via API"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT w.id, w.product_id, p.name, p.image_url
            FROM wishlist w
            JOIN products p ON w.product_id = p.id
            WHERE w.customer_id = %s AND p.is_active = 1
            ORDER BY w.created_at DESC
        """, (session['customer_id'],))
        
        items = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'items': [
                {
                    'id': item['id'],
                    'product_id': item['product_id'],
                    'name': item['name'],
                    'image_url': item['image_url']
                }
                for item in items
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
