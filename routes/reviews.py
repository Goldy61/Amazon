from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, get_db_connection, login_required

@app.route('/product/<int:product_id>/reviews')
def product_reviews(product_id):
    """Display all reviews for a product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get product info
    cursor.execute("SELECT name, average_rating, review_count FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('products'))
    
    # Get all reviews
    cursor.execute("""
        SELECT pr.*, c.first_name, c.last_name
        FROM product_reviews pr
        JOIN customers c ON pr.customer_id = c.id
        WHERE pr.product_id = %s
        ORDER BY pr.created_at DESC
    """, (product_id,))
    reviews = cursor.fetchall()
    
    # Get rating distribution
    cursor.execute("""
        SELECT rating, COUNT(*) as count
        FROM product_reviews
        WHERE product_id = %s
        GROUP BY rating
        ORDER BY rating DESC
    """, (product_id,))
    rating_distribution = {row['rating']: row['count'] for row in cursor.fetchall()}
    
    conn.close()
    return render_template('customer/product_reviews.html', 
                         product=product, 
                         reviews=reviews,
                         rating_distribution=rating_distribution,
                         product_id=product_id)

@app.route('/add_review/<int:order_id>/<int:product_id>', methods=['GET', 'POST'])
@login_required('customer')
def add_review(order_id, product_id):
    """Add a review for a purchased product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify customer purchased this product
    cursor.execute("""
        SELECT oi.*, p.name as product_name, o.status
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = %s AND oi.product_id = %s 
        AND o.customer_id = %s AND o.payment_status = 'completed'
    """, (order_id, product_id, session['customer_id']))
    order_item = cursor.fetchone()
    
    if not order_item:
        flash('You can only review products you have purchased.', 'error')
        conn.close()
        return redirect(url_for('order_history'))
    
    # Check if already reviewed
    cursor.execute("""
        SELECT id FROM product_reviews 
        WHERE product_id = %s AND customer_id = %s AND order_id = %s
    """, (product_id, session['customer_id'], order_id))
    if cursor.fetchone():
        flash('You have already reviewed this product.', 'info')
        conn.close()
        return redirect(url_for('order_detail', order_id=order_id))
    
    if request.method == 'POST':
        rating = int(request.form['rating'])
        review_title = request.form['review_title']
        review_text = request.form['review_text']
        
        # Validate rating
        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5.', 'error')
        else:
            # Insert review
            cursor.execute("""
                INSERT INTO product_reviews 
                (product_id, customer_id, order_id, rating, review_title, review_text)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (product_id, session['customer_id'], order_id, rating, review_title, review_text))
            
            # Update product average rating and review count
            cursor.execute("""
                UPDATE products 
                SET average_rating = (
                    SELECT AVG(rating) FROM product_reviews WHERE product_id = %s
                ),
                review_count = (
                    SELECT COUNT(*) FROM product_reviews WHERE product_id = %s
                )
                WHERE id = %s
            """, (product_id, product_id, product_id))
            
            conn.commit()
            flash('Thank you for your review!', 'success')
            conn.close()
            return redirect(url_for('order_detail', order_id=order_id))
    
    conn.close()
    return render_template('customer/add_review.html', 
                         order_item=order_item, 
                         order_id=order_id,
                         product_id=product_id)

@app.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
@login_required('customer')
def edit_review(review_id):
    """Edit an existing review"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get review
    cursor.execute("""
        SELECT pr.*, p.name as product_name
        FROM product_reviews pr
        JOIN products p ON pr.product_id = p.id
        WHERE pr.id = %s AND pr.customer_id = %s
    """, (review_id, session['customer_id']))
    review = cursor.fetchone()
    
    if not review:
        flash('Review not found.', 'error')
        conn.close()
        return redirect(url_for('order_history'))
    
    if request.method == 'POST':
        rating = int(request.form['rating'])
        review_title = request.form['review_title']
        review_text = request.form['review_text']
        
        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5.', 'error')
        else:
            # Update review
            cursor.execute("""
                UPDATE product_reviews 
                SET rating = %s, review_title = %s, review_text = %s
                WHERE id = %s AND customer_id = %s
            """, (rating, review_title, review_text, review_id, session['customer_id']))
            
            # Update product average rating
            cursor.execute("""
                UPDATE products 
                SET average_rating = (
                    SELECT AVG(rating) FROM product_reviews WHERE product_id = %s
                )
                WHERE id = %s
            """, (review['product_id'], review['product_id']))
            
            conn.commit()
            flash('Review updated successfully!', 'success')
            conn.close()
            return redirect(url_for('order_detail', order_id=review['order_id']))
    
    conn.close()
    return render_template('customer/edit_review.html', review=review)

@app.route('/delete_review/<int:review_id>')
@login_required('customer')
def delete_review(review_id):
    """Delete a review"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get review to get product_id
    cursor.execute("""
        SELECT product_id, order_id FROM product_reviews 
        WHERE id = %s AND customer_id = %s
    """, (review_id, session['customer_id']))
    review = cursor.fetchone()
    
    if not review:
        flash('Review not found.', 'error')
        conn.close()
        return redirect(url_for('order_history'))
    
    # Delete review
    cursor.execute("DELETE FROM product_reviews WHERE id = %s", (review_id,))
    
    # Update product stats
    cursor.execute("""
        UPDATE products 
        SET average_rating = COALESCE((
            SELECT AVG(rating) FROM product_reviews WHERE product_id = %s
        ), 0),
        review_count = (
            SELECT COUNT(*) FROM product_reviews WHERE product_id = %s
        )
        WHERE id = %s
    """, (review['product_id'], review['product_id'], review['product_id']))
    
    conn.commit()
    conn.close()
    flash('Review deleted.', 'info')
    return redirect(url_for('order_detail', order_id=review['order_id']))

@app.route('/api/mark_review_helpful/<int:review_id>', methods=['POST'])
def mark_review_helpful(review_id):
    """Mark a review as helpful"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE product_reviews 
        SET helpful_count = helpful_count + 1 
        WHERE id = %s
    """, (review_id,))
    
    conn.commit()
    
    cursor.execute("SELECT helpful_count FROM product_reviews WHERE id = %s", (review_id,))
    result = cursor.fetchone()
    
    conn.close()
    return jsonify({'success': True, 'helpful_count': result['helpful_count']})
