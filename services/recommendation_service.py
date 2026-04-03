"""
Product Recommendation Service
Provides intelligent product recommendations based on multiple strategies
"""

from app import get_db_connection
from datetime import datetime, timedelta
import random

class RecommendationService:
    """
    Handles all product recommendation logic
    """
    
    def __init__(self):
        self.max_recommendations = 5
        
    def get_recommendations(self, product_id, customer_id=None, limit=5):
        """
        Get product recommendations using multiple strategies
        
        Args:
            product_id: Current product being viewed
            customer_id: Optional customer ID for personalized recommendations
            limit: Number of recommendations to return (default: 5)
            
        Returns:
            List of recommended products with scores
        """
        recommendations = []
        
        # Strategy 1: Same Category (40% weight)
        category_recs = self._get_category_recommendations(product_id, limit * 2)
        for rec in category_recs:
            rec['score'] = rec.get('score', 0) * 0.4
            recommendations.append(rec)
        
        # Strategy 2: Collaborative Filtering (35% weight)
        if customer_id:
            collab_recs = self._get_collaborative_recommendations(product_id, customer_id, limit * 2)
            for rec in collab_recs:
                rec['score'] = rec.get('score', 0) * 0.35
                recommendations.append(rec)
        
        # Strategy 3: Recently Viewed (25% weight)
        if customer_id:
            viewed_recs = self._get_recently_viewed_recommendations(customer_id, product_id, limit * 2)
            for rec in viewed_recs:
                rec['score'] = rec.get('score', 0) * 0.25
                recommendations.append(rec)
        
        # Merge and deduplicate recommendations
        merged_recs = self._merge_recommendations(recommendations, product_id)
        
        # Return top N recommendations
        return merged_recs[:limit]
    
    def _get_category_recommendations(self, product_id, limit=10):
        """
        Recommend products from the same category
        Prioritizes products with higher ratings and more sales
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                p.id,
                p.name,
                p.price,
                p.discount_price,
                p.image_url,
                p.category_id,
                c.name as category_name,
                s.business_name,
                COALESCE(AVG(pr.rating), 0) as avg_rating,
                COUNT(DISTINCT pr.id) as review_count,
                COUNT(DISTINCT oi.id) as sales_count,
                (
                    COALESCE(AVG(pr.rating), 0) * 0.4 +
                    (COUNT(DISTINCT oi.id) / 10.0) * 0.3 +
                    (COUNT(DISTINCT pr.id) / 5.0) * 0.3
                ) as relevance_score
            FROM products p
            JOIN categories c ON p.category_id = c.id
            JOIN sellers s ON p.seller_id = s.id
            LEFT JOIN product_reviews pr ON p.id = pr.product_id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            WHERE p.category_id = (
                SELECT category_id FROM products WHERE id = %s
            )
            AND p.id != %s
            AND p.is_active = 1
            AND p.quantity > 0
            GROUP BY p.id, p.name, p.price, p.discount_price, p.image_url, 
                     p.category_id, c.name, s.business_name
            ORDER BY relevance_score DESC, avg_rating DESC
            LIMIT %s
        """
        
        cursor.execute(query, (product_id, product_id, limit))
        results = cursor.fetchall()
        conn.close()
        
        recommendations = []
        for row in results:
            recommendations.append({
                'id': row['id'],
                'name': row['name'],
                'price': float(row['price']),
                'discount_price': float(row['discount_price']) if row['discount_price'] else None,
                'image_url': row['image_url'],
                'category_name': row['category_name'],
                'business_name': row['business_name'],
                'avg_rating': float(row['avg_rating']),
                'review_count': row['review_count'],
                'sales_count': row['sales_count'],
                'score': float(row['relevance_score']),
                'reason': 'Similar products in ' + row['category_name']
            })
        
        return recommendations
    
    def _get_collaborative_recommendations(self, product_id, customer_id, limit=10):
        """
        Collaborative filtering: "Customers who bought this also bought..."
        Uses order history to find related products
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                p.id,
                p.name,
                p.price,
                p.discount_price,
                p.image_url,
                c.name as category_name,
                s.business_name,
                COALESCE(AVG(pr.rating), 0) as avg_rating,
                COUNT(DISTINCT pr.id) as review_count,
                COUNT(DISTINCT co_purchase.order_id) as co_purchase_count,
                (
                    COUNT(DISTINCT co_purchase.order_id) * 0.5 +
                    COALESCE(AVG(pr.rating), 0) * 0.3 +
                    (COUNT(DISTINCT pr.id) / 5.0) * 0.2
                ) as relevance_score
            FROM products p
            JOIN categories c ON p.category_id = c.id
            JOIN sellers s ON p.seller_id = s.id
            LEFT JOIN product_reviews pr ON p.id = pr.product_id
            JOIN order_items co_purchase ON p.id = co_purchase.product_id
            WHERE co_purchase.order_id IN (
                -- Find orders that contain the current product
                SELECT DISTINCT order_id 
                FROM order_items 
                WHERE product_id = %s
            )
            AND p.id != %s
            AND p.is_active = 1
            AND p.quantity > 0
            GROUP BY p.id, p.name, p.price, p.discount_price, p.image_url, 
                     c.name, s.business_name
            HAVING co_purchase_count > 0
            ORDER BY relevance_score DESC, co_purchase_count DESC
            LIMIT %s
        """
        
        cursor.execute(query, (product_id, product_id, limit))
        results = cursor.fetchall()
        conn.close()
        
        recommendations = []
        for row in results:
            recommendations.append({
                'id': row['id'],
                'name': row['name'],
                'price': float(row['price']),
                'discount_price': float(row['discount_price']) if row['discount_price'] else None,
                'image_url': row['image_url'],
                'category_name': row['category_name'],
                'business_name': row['business_name'],
                'avg_rating': float(row['avg_rating']),
                'review_count': row['review_count'],
                'co_purchase_count': row['co_purchase_count'],
                'score': float(row['relevance_score']),
                'reason': 'Customers who bought this also bought'
            })
        
        return recommendations
    
    def _get_recently_viewed_recommendations(self, customer_id, current_product_id, limit=10):
        """
        Recommend products based on user's recently viewed items
        Finds products similar to what the user has been browsing
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                p.id,
                p.name,
                p.price,
                p.discount_price,
                p.image_url,
                c.name as category_name,
                s.business_name,
                COALESCE(AVG(pr.rating), 0) as avg_rating,
                COUNT(DISTINCT pr.id) as review_count,
                MAX(rv.viewed_at) as last_viewed,
                (
                    TIMESTAMPDIFF(HOUR, MAX(rv.viewed_at), NOW()) * -0.1 +
                    COALESCE(AVG(pr.rating), 0) * 0.4 +
                    (COUNT(DISTINCT pr.id) / 5.0) * 0.2
                ) as relevance_score
            FROM products p
            JOIN categories c ON p.category_id = c.id
            JOIN sellers s ON p.seller_id = s.id
            LEFT JOIN product_reviews pr ON p.id = pr.product_id
            JOIN recently_viewed rv ON p.id = rv.product_id
            WHERE rv.customer_id = %s
            AND p.id != %s
            AND p.is_active = 1
            AND p.quantity > 0
            AND rv.viewed_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY p.id, p.name, p.price, p.discount_price, p.image_url, 
                     c.name, s.business_name
            ORDER BY relevance_score DESC, last_viewed DESC
            LIMIT %s
        """
        
        cursor.execute(query, (customer_id, current_product_id, limit))
        results = cursor.fetchall()
        conn.close()
        
        recommendations = []
        for row in results:
            recommendations.append({
                'id': row['id'],
                'name': row['name'],
                'price': float(row['price']),
                'discount_price': float(row['discount_price']) if row['discount_price'] else None,
                'image_url': row['image_url'],
                'category_name': row['category_name'],
                'business_name': row['business_name'],
                'avg_rating': float(row['avg_rating']),
                'review_count': row['review_count'],
                'score': float(row['relevance_score']),
                'reason': 'Based on your browsing history'
            })
        
        return recommendations
    
    def _merge_recommendations(self, recommendations, exclude_product_id):
        """
        Merge recommendations from different strategies
        Remove duplicates and sort by combined score
        """
        # Group by product ID and sum scores
        product_scores = {}
        
        for rec in recommendations:
            product_id = rec['id']
            
            if product_id == exclude_product_id:
                continue
            
            if product_id not in product_scores:
                product_scores[product_id] = rec
                product_scores[product_id]['combined_score'] = rec['score']
                product_scores[product_id]['reasons'] = [rec['reason']]
            else:
                # Add scores from multiple strategies
                product_scores[product_id]['combined_score'] += rec['score']
                if rec['reason'] not in product_scores[product_id]['reasons']:
                    product_scores[product_id]['reasons'].append(rec['reason'])
        
        # Convert to list and sort by combined score
        merged = list(product_scores.values())
        merged.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Format reasons
        for rec in merged:
            rec['reason'] = ' • '.join(rec['reasons'][:2])  # Show top 2 reasons
            del rec['reasons']
        
        return merged
    
    def get_trending_products(self, limit=10):
        """
        Get trending products based on recent sales and views
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                p.id,
                p.name,
                p.price,
                p.discount_price,
                p.image_url,
                c.name as category_name,
                s.business_name,
                COALESCE(AVG(pr.rating), 0) as avg_rating,
                COUNT(DISTINCT pr.id) as review_count,
                COUNT(DISTINCT oi.id) as recent_sales,
                COALESCE(p.view_count, 0) as view_count,
                (
                    COUNT(DISTINCT oi.id) * 0.4 +
                    COALESCE(p.view_count, 0) / 100.0 * 0.3 +
                    COALESCE(AVG(pr.rating), 0) * 0.3
                ) as trending_score
            FROM products p
            JOIN categories c ON p.category_id = c.id
            JOIN sellers s ON p.seller_id = s.id
            LEFT JOIN product_reviews pr ON p.id = pr.product_id
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id
            WHERE p.is_active = 1
            AND p.quantity > 0
            AND (o.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) OR o.created_at IS NULL)
            GROUP BY p.id, p.name, p.price, p.discount_price, p.image_url, 
                     c.name, s.business_name, p.view_count
            HAVING trending_score > 0
            ORDER BY trending_score DESC, recent_sales DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        conn.close()
        
        trending = []
        for row in results:
            trending.append({
                'id': row['id'],
                'name': row['name'],
                'price': float(row['price']),
                'discount_price': float(row['discount_price']) if row['discount_price'] else None,
                'image_url': row['image_url'],
                'category_name': row['category_name'],
                'business_name': row['business_name'],
                'avg_rating': float(row['avg_rating']),
                'review_count': row['review_count'],
                'recent_sales': row['recent_sales'],
                'view_count': row['view_count'],
                'trending_score': float(row['trending_score'])
            })
        
        return trending
    
    def get_personalized_homepage_recommendations(self, customer_id, limit=20):
        """
        Get personalized recommendations for homepage
        Based on user's purchase history, wishlist, and browsing behavior
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT DISTINCT
                p.id,
                p.name,
                p.price,
                p.discount_price,
                p.image_url,
                c.name as category_name,
                s.business_name,
                COALESCE(AVG(pr.rating), 0) as avg_rating,
                COUNT(DISTINCT pr.id) as review_count,
                (
                    -- User's category preference
                    CASE WHEN p.category_id IN (
                        SELECT DISTINCT category_id 
                        FROM products 
                        WHERE id IN (
                            SELECT product_id FROM order_items oi
                            JOIN orders o ON oi.order_id = o.id
                            WHERE o.customer_id = %s
                        )
                    ) THEN 2.0 ELSE 0 END +
                    -- Wishlist category
                    CASE WHEN p.category_id IN (
                        SELECT DISTINCT category_id 
                        FROM products 
                        WHERE id IN (
                            SELECT product_id FROM wishlist WHERE customer_id = %s
                        )
                    ) THEN 1.5 ELSE 0 END +
                    -- Product rating
                    COALESCE(AVG(pr.rating), 0) * 0.5 +
                    -- Review count
                    (COUNT(DISTINCT pr.id) / 10.0) * 0.3
                ) as personalization_score
            FROM products p
            JOIN categories c ON p.category_id = c.id
            JOIN sellers s ON p.seller_id = s.id
            LEFT JOIN product_reviews pr ON p.id = pr.product_id
            WHERE p.is_active = 1
            AND p.quantity > 0
            AND p.id NOT IN (
                -- Exclude already purchased products
                SELECT product_id FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.customer_id = %s
            )
            GROUP BY p.id, p.name, p.price, p.discount_price, p.image_url, 
                     c.name, s.business_name, p.category_id
            HAVING personalization_score > 0
            ORDER BY personalization_score DESC, avg_rating DESC
            LIMIT %s
        """
        
        cursor.execute(query, (customer_id, customer_id, customer_id, limit))
        results = cursor.fetchall()
        conn.close()
        
        recommendations = []
        for row in results:
            recommendations.append({
                'id': row['id'],
                'name': row['name'],
                'price': float(row['price']),
                'discount_price': float(row['discount_price']) if row['discount_price'] else None,
                'image_url': row['image_url'],
                'category_name': row['category_name'],
                'business_name': row['business_name'],
                'avg_rating': float(row['avg_rating']),
                'review_count': row['review_count'],
                'personalization_score': float(row['personalization_score'])
            })
        
        return recommendations
    
    def track_product_view(self, product_id, customer_id=None, session_id=None):
        """
        Track when a product is viewed for recommendation purposes
        """
        if not customer_id and not session_id:
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert or update view record
        query = """
            INSERT INTO recently_viewed (customer_id, product_id, session_id, viewed_at)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE viewed_at = NOW()
        """
        
        cursor.execute(query, (customer_id, product_id, session_id))
        
        # Update product view count
        cursor.execute("""
            UPDATE products 
            SET view_count = COALESCE(view_count, 0) + 1 
            WHERE id = %s
        """, (product_id,))
        
        conn.commit()
        conn.close()
    
    def get_similar_products_by_price(self, product_id, limit=5):
        """
        Get products with similar price range
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                p2.id,
                p2.name,
                p2.price,
                p2.discount_price,
                p2.image_url,
                c.name as category_name,
                s.business_name,
                COALESCE(AVG(pr.rating), 0) as avg_rating,
                ABS(p2.price - p1.price) as price_diff
            FROM products p1
            CROSS JOIN products p2
            JOIN categories c ON p2.category_id = c.id
            JOIN sellers s ON p2.seller_id = s.id
            LEFT JOIN product_reviews pr ON p2.id = pr.product_id
            WHERE p1.id = %s
            AND p2.id != %s
            AND p2.is_active = 1
            AND p2.quantity > 0
            AND p2.price BETWEEN (p1.price * 0.7) AND (p1.price * 1.3)
            GROUP BY p2.id, p2.name, p2.price, p2.discount_price, p2.image_url, 
                     c.name, s.business_name, p1.price
            ORDER BY price_diff ASC, avg_rating DESC
            LIMIT %s
        """
        
        cursor.execute(query, (product_id, product_id, limit))
        results = cursor.fetchall()
        conn.close()
        
        similar = []
        for row in results:
            similar.append({
                'id': row['id'],
                'name': row['name'],
                'price': float(row['price']),
                'discount_price': float(row['discount_price']) if row['discount_price'] else None,
                'image_url': row['image_url'],
                'category_name': row['category_name'],
                'business_name': row['business_name'],
                'avg_rating': float(row['avg_rating'])
            })
        
        return similar


# Create singleton instance
recommendation_service = RecommendationService()
