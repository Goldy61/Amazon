"""
Product Comparison Routes
Handles product comparison functionality
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, get_db_connection

@app.route('/compare')
def compare_products():
    """Product comparison page"""
    # Get product IDs from query string first, fallback to session
    product_ids = request.args.getlist('products')
    
    if not product_ids:
        # Fall back to session comparison list
        product_ids = [str(pid) for pid in session.get('comparison_list', [])]
    
    # Limit to 3 products
    product_ids = product_ids[:3]
    
    products = []
    
    if product_ids:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            placeholders = ','.join(['%s'] * len(product_ids))
            query = f"""
                SELECT 
                    p.id, p.name, p.description, p.price, p.discount_price,
                    p.image_url, p.quantity, p.specifications,
                    c.name as category_name,
                    s.business_name, s.owner_name,
                    COALESCE(AVG(pr.rating), 0) as avg_rating,
                    COUNT(DISTINCT pr.id) as review_count
                FROM products p
                JOIN categories c ON p.category_id = c.id
                JOIN sellers s ON p.seller_id = s.id
                LEFT JOIN product_reviews pr ON p.id = pr.product_id
                WHERE p.id IN ({placeholders}) AND p.is_active = 1
                GROUP BY p.id, p.name, p.description, p.price, p.discount_price,
                         p.image_url, p.quantity, p.specifications, c.name,
                         s.business_name, s.owner_name
            """
            cursor.execute(query, product_ids)
            results = cursor.fetchall()
            conn.close()
            
            for row in results:
                products.append({
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'] or '',
                    'price': float(row['price']),
                    'discount_price': float(row['discount_price']) if row['discount_price'] else None,
                    'image_url': row['image_url'],
                    'quantity': row['quantity'],
                    'specifications': row['specifications'] or '',
                    'category_name': row['category_name'],
                    'business_name': row['business_name'],
                    'owner_name': row['owner_name'],
                    'avg_rating': float(row['avg_rating']),
                    'review_count': row['review_count'],
                    'in_stock': row['quantity'] > 0
                })
                
        except Exception as e:
            flash(f'Error loading products: {str(e)}', 'error')
    
    return render_template('comparison.html', products=products)

@app.route('/api/compare/add', methods=['POST'])
def add_to_comparison():
    """
    Add product to comparison list (stored in session)
    """
    try:
        data = request.get_json()
        product_id = str(data.get('product_id'))  # always store as string
        
        if not product_id or product_id == 'None':
            return jsonify({'success': False, 'message': 'Product ID is required'}), 400
        
        comparison_list = session.get('comparison_list', [])
        comparison_list = [str(x) for x in comparison_list]  # normalize existing
        
        if product_id in comparison_list:
            return jsonify({'success': False, 'message': 'Product already in comparison list'})
        
        if len(comparison_list) >= 3:
            return jsonify({'success': False, 'message': 'Maximum 3 products can be compared'})
        
        comparison_list.append(product_id)
        session['comparison_list'] = comparison_list
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Product added to comparison',
            'count': len(comparison_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/compare/remove', methods=['POST'])
def remove_from_comparison():
    """
    Remove product from comparison list
    """
    try:
        data = request.get_json()
        product_id = str(data.get('product_id'))
        
        if not product_id or product_id == 'None':
            return jsonify({'success': False, 'message': 'Product ID is required'}), 400
        
        comparison_list = [str(x) for x in session.get('comparison_list', [])]
        
        if product_id in comparison_list:
            comparison_list.remove(product_id)
            session['comparison_list'] = comparison_list
            session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Product removed from comparison',
            'count': len(comparison_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/compare/list')
def get_comparison_list():
    """Get current comparison list"""
    comparison_list = [str(x) for x in session.get('comparison_list', [])]
    
    products = []
    
    if comparison_list:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            placeholders = ','.join(['%s'] * len(comparison_list))
            query = f"""
                SELECT 
                    p.id,
                    p.name,
                    p.image_url,
                    p.price,
                    p.discount_price
                FROM products p
                WHERE p.id IN ({placeholders})
            """
            
            cursor.execute(query, comparison_list)
            results = cursor.fetchall()
            conn.close()
            
            for row in results:
                products.append({
                    'id': row['id'],
                    'name': row['name'],
                    'image_url': row['image_url'],
                    'price': float(row['price']),
                    'discount_price': float(row['discount_price']) if row['discount_price'] else None
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    return jsonify({
        'success': True,
        'products': products,
        'count': len(products)
    })

@app.route('/api/compare/clear', methods=['POST'])
def clear_comparison():
    """
    Clear comparison list
    """
    session['comparison_list'] = []
    
    return jsonify({
        'success': True,
        'message': 'Comparison list cleared'
    })
