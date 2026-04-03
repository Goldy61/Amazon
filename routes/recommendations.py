"""
Recommendation Routes
Handles all recommendation-related endpoints
"""

from flask import render_template, request, jsonify, session
from app import app, get_db_connection
from services.recommendation_service import recommendation_service

@app.route('/api/recommendations/<int:product_id>')
def get_product_recommendations(product_id):
    """
    API endpoint to get recommendations for a specific product
    """
    customer_id = session.get('customer_id') if session.get('role') == 'customer' else None
    limit = request.args.get('limit', 5, type=int)
    
    try:
        recommendations = recommendation_service.get_recommendations(
            product_id=product_id,
            customer_id=customer_id,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations/trending')
def get_trending_recommendations():
    """
    Get trending products
    """
    limit = request.args.get('limit', 10, type=int)
    
    try:
        trending = recommendation_service.get_trending_products(limit=limit)
        
        return jsonify({
            'success': True,
            'trending': trending,
            'count': len(trending)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations/personalized')
def get_personalized_recommendations():
    """
    Get personalized recommendations for logged-in user
    """
    if session.get('role') != 'customer':
        return jsonify({
            'success': False,
            'error': 'User not logged in'
        }), 401
    
    customer_id = session.get('customer_id')
    limit = request.args.get('limit', 20, type=int)
    
    try:
        recommendations = recommendation_service.get_personalized_homepage_recommendations(
            customer_id=customer_id,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommendations/similar-price/<int:product_id>')
def get_similar_price_recommendations(product_id):
    """
    Get products with similar price range
    """
    limit = request.args.get('limit', 5, type=int)
    
    try:
        similar = recommendation_service.get_similar_products_by_price(
            product_id=product_id,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'similar': similar,
            'count': len(similar)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/track-view/<int:product_id>', methods=['POST'])
def track_product_view(product_id):
    """
    Track product view for recommendation purposes
    """
    customer_id = session.get('customer_id') if session.get('role') == 'customer' else None
    session_id = session.get('session_id', request.cookies.get('session_id'))
    
    try:
        recommendation_service.track_product_view(
            product_id=product_id,
            customer_id=customer_id,
            session_id=session_id
        )
        
        return jsonify({
            'success': True,
            'message': 'View tracked successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/recommendations')
def recommendations_page():
    """
    Dedicated recommendations page
    """
    customer_id = session.get('customer_id') if session.get('role') == 'customer' else None
    
    # Get trending products
    trending = recommendation_service.get_trending_products(limit=12)
    
    # Get personalized recommendations if user is logged in
    personalized = []
    if customer_id:
        personalized = recommendation_service.get_personalized_homepage_recommendations(
            customer_id=customer_id,
            limit=12
        )
    
    return render_template('recommendations.html',
                         trending=trending,
                         personalized=personalized,
                         has_personalized=len(personalized) > 0)
