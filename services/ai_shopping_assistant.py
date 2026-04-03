"""
AI Shopping Assistant Service
Intelligent chatbot for product recommendations and queries
"""

import openai
import json
import re
import pymysql
from datetime import datetime

class AIShoppingAssistant:
    """
    AI-powered shopping assistant using OpenAI GPT
    """
    
    def __init__(self, api_key=None, db_config=None):
        """Initialize with OpenAI API key and database config"""
        if api_key:
            openai.api_key = api_key
        
        self.db_config = db_config or {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'amazon_db',
            'cursorclass': pymysql.cursors.DictCursor
        }
        
        self.conversation_history = []
        self.max_history = 10
        
    def chat(self, user_message, customer_id=None):
        """
        Process user message and return AI response
        
        Args:
            user_message: User's question/message
            customer_id: Optional customer ID for personalization
            
        Returns:
            dict with response, products, and metadata
        """
        try:
            # Analyze user intent
            intent = self._analyze_intent(user_message)
            
            # Extract product criteria from message
            criteria = self._extract_criteria(user_message)
            
            # Query database for relevant products
            products = self._search_products(criteria)
            
            # Generate AI response
            ai_response = self._generate_response(
                user_message, 
                products, 
                intent,
                customer_id
            )
            
            # Add to conversation history
            self._add_to_history(user_message, ai_response)
            
            return {
                'success': True,
                'response': ai_response,
                'products': products[:5],  # Top 5 products
                'intent': intent,
                'criteria': criteria,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'response': f"I apologize, but I encountered an error: {str(e)}",
                'products': [],
                'error': str(e)
            }
    
    def _analyze_intent(self, message):
        """
        Analyze user intent from message
        """
        message_lower = message.lower()
        
        # Product search intents
        if any(word in message_lower for word in ['suggest', 'recommend', 'show', 'find', 'looking for', 'need', 'want']):
            return 'product_search'
        
        # Comparison intent
        if any(word in message_lower for word in ['compare', 'difference', 'vs', 'versus', 'better']):
            return 'product_comparison'
        
        # Price inquiry
        if any(word in message_lower for word in ['price', 'cost', 'how much', 'cheap', 'expensive']):
            return 'price_inquiry'
        
        # Availability check
        if any(word in message_lower for word in ['available', 'in stock', 'stock']):
            return 'availability_check'
        
        # Order tracking
        if any(word in message_lower for word in ['order', 'track', 'delivery', 'shipping']):
            return 'order_tracking'
        
        # General inquiry
        return 'general_inquiry'
    
    def _extract_criteria(self, message):
        """
        Extract search criteria from user message
        """
        criteria = {
            'keywords': [],
            'category': None,
            'min_price': None,
            'max_price': None,
            'brand': None,
            'features': []
        }
        
        message_lower = message.lower()
        
        # Extract price range
        price_patterns = [
            r'under (?:rs\.?|₹)?\s*(\d+(?:,\d+)*)',
            r'below (?:rs\.?|₹)?\s*(\d+(?:,\d+)*)',
            r'less than (?:rs\.?|₹)?\s*(\d+(?:,\d+)*)',
            r'between (?:rs\.?|₹)?\s*(\d+(?:,\d+)*)\s*(?:and|to|-)\s*(?:rs\.?|₹)?\s*(\d+(?:,\d+)*)',
            r'(?:rs\.?|₹)?\s*(\d+(?:,\d+)*)\s*to\s*(?:rs\.?|₹)?\s*(\d+(?:,\d+)*)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, message_lower)
            if match:
                groups = [g for g in match.groups() if g]
                if len(groups) == 1:
                    # Remove commas and convert to int
                    criteria['max_price'] = int(groups[0].replace(',', ''))
                elif len(groups) == 2:
                    criteria['min_price'] = int(groups[0].replace(',', ''))
                    criteria['max_price'] = int(groups[1].replace(',', ''))
                break
        
        # Extract category keywords
        categories = {
            'phone': ['phone', 'mobile', 'smartphone'],
            'laptop': ['laptop', 'notebook', 'computer'],
            'headphone': ['headphone', 'earphone', 'earbuds', 'airpods'],
            'watch': ['watch', 'smartwatch'],
            'camera': ['camera', 'dslr'],
            'tablet': ['tablet', 'ipad'],
            'tv': ['tv', 'television'],
            'speaker': ['speaker', 'bluetooth speaker'],
            'gaming': ['gaming', 'game', 'playstation', 'xbox'],
            'clothing': ['shirt', 'tshirt', 't-shirt', 'jeans', 'dress', 'clothes'],
            'shoes': ['shoes', 'sneakers', 'footwear'],
            'book': ['book', 'novel', 'ebook']
        }
        
        for category, keywords in categories.items():
            if any(keyword in message_lower for keyword in keywords):
                criteria['category'] = category
                criteria['keywords'].extend(keywords)
                break
        
        # Extract feature keywords
        features = ['gaming', 'wireless', 'bluetooth', '5g', '4g', 'waterproof', 
                   'fast charging', 'long battery', 'lightweight', 'portable']
        
        for feature in features:
            if feature in message_lower:
                criteria['features'].append(feature)
        
        # Extract general keywords (remove common words)
        stop_words = {'suggest', 'show', 'find', 'me', 'a', 'an', 'the', 'for', 
                     'under', 'below', 'best', 'good', 'looking', 'want', 'need',
                     'rs', 'rupees', 'price', 'range'}
        
        words = message_lower.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        criteria['keywords'].extend(keywords)
        
        # Remove duplicates
        criteria['keywords'] = list(set(criteria['keywords']))
        
        return criteria
    
    def _get_db_connection(self):
        """Get database connection"""
        return pymysql.connect(**self.db_config)
    
    def _search_products(self, criteria):
        """
        Search products in database based on criteria
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic query
        query = """
            SELECT 
                p.id,
                p.name,
                p.description,
                p.price,
                p.discount_price,
                p.image_url,
                p.quantity,
                c.name as category_name,
                s.business_name,
                COALESCE(AVG(pr.rating), 0) as avg_rating,
                COUNT(DISTINCT pr.id) as review_count,
                (
                    COALESCE(AVG(pr.rating), 0) * 0.3 +
                    (COUNT(DISTINCT pr.id) / 10.0) * 0.2 +
                    CASE WHEN p.discount_price IS NOT NULL THEN 0.2 ELSE 0 END +
                    (p.quantity > 0) * 0.3
                ) as relevance_score
            FROM products p
            JOIN categories c ON p.category_id = c.id
            JOIN sellers s ON p.seller_id = s.id
            LEFT JOIN product_reviews pr ON p.id = pr.product_id
            WHERE p.is_active = 1
        """
        
        params = []
        
        # Add price filters
        if criteria['min_price']:
            query += " AND p.price >= %s"
            params.append(criteria['min_price'])
        
        if criteria['max_price']:
            query += " AND p.price <= %s"
            params.append(criteria['max_price'])
        
        # Add keyword search
        if criteria['keywords']:
            keyword_conditions = []
            for keyword in criteria['keywords'][:5]:  # Limit to 5 keywords
                keyword_conditions.append(
                    "(p.name LIKE %s OR p.description LIKE %s OR c.name LIKE %s)"
                )
                keyword_pattern = f"%{keyword}%"
                params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
            
            if keyword_conditions:
                query += " AND (" + " OR ".join(keyword_conditions) + ")"
        
        query += """
            GROUP BY p.id, p.name, p.description, p.price, p.discount_price, 
                     p.image_url, p.quantity, c.name, s.business_name
            ORDER BY relevance_score DESC, avg_rating DESC
            LIMIT 10
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        products = []
        for row in results:
            products.append({
                'id': row['id'],
                'name': row['name'],
                'description': row['description'][:200] if row['description'] else '',
                'price': float(row['price']),
                'discount_price': float(row['discount_price']) if row['discount_price'] else None,
                'image_url': row['image_url'],
                'quantity': row['quantity'],
                'category_name': row['category_name'],
                'business_name': row['business_name'],
                'avg_rating': float(row['avg_rating']),
                'review_count': row['review_count'],
                'in_stock': row['quantity'] > 0
            })
        
        return products
    
    def _generate_response(self, user_message, products, intent, customer_id=None):
        """
        Generate AI response using OpenAI GPT
        """
        try:
            # Prepare context for GPT
            context = self._prepare_context(products, intent)
            
            # Create system message
            system_message = """You are a helpful shopping assistant for an e-commerce website called ShopHub. 
            Your role is to help customers find products, answer questions, and provide recommendations.
            Be friendly, concise, and helpful. Always mention specific product names and prices when available.
            If products are found, describe them briefly and highlight their key features.
            If no products match, suggest alternatives or ask clarifying questions."""
            
            # Create messages for GPT
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{user_message}\n\nAvailable products:\n{context}"}
            ]
            
            # Add conversation history
            for msg in self.conversation_history[-4:]:  # Last 4 messages
                messages.append({"role": "user", "content": msg['user']})
                messages.append({"role": "assistant", "content": msg['assistant']})
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return ai_response
            
        except Exception as e:
            # Fallback response if OpenAI fails
            return self._generate_fallback_response(products, intent)
    
    def _prepare_context(self, products, intent):
        """
        Prepare product context for GPT
        """
        if not products:
            return "No products found matching the criteria."
        
        context = f"Found {len(products)} products:\n\n"
        
        for i, product in enumerate(products[:5], 1):
            price = product['discount_price'] or product['price']
            context += f"{i}. {product['name']}\n"
            context += f"   Price: ₹{price:,.2f}\n"
            context += f"   Category: {product['category_name']}\n"
            context += f"   Rating: {product['avg_rating']:.1f}/5 ({product['review_count']} reviews)\n"
            context += f"   In Stock: {'Yes' if product['in_stock'] else 'No'}\n"
            if product['description']:
                context += f"   Description: {product['description'][:100]}...\n"
            context += "\n"
        
        return context
    
    def _generate_fallback_response(self, products, intent):
        """
        Generate fallback response without OpenAI
        """
        if not products:
            return "I couldn't find any products matching your criteria. Could you please provide more details or try different search terms?"
        
        response = f"I found {len(products)} great options for you:\n\n"
        
        for i, product in enumerate(products[:3], 1):
            price = product['discount_price'] or product['price']
            response += f"{i}. **{product['name']}**\n"
            response += f"   💰 Price: ₹{price:,.2f}\n"
            response += f"   ⭐ Rating: {product['avg_rating']:.1f}/5\n"
            
            if product['discount_price']:
                savings = product['price'] - product['discount_price']
                response += f"   🎉 Save ₹{savings:,.2f}!\n"
            
            response += "\n"
        
        if len(products) > 3:
            response += f"\n...and {len(products) - 3} more options available!"
        
        response += "\n\nWould you like to know more about any of these products?"
        
        return response
    
    def _add_to_history(self, user_message, ai_response):
        """
        Add conversation to history
        """
        self.conversation_history.append({
            'user': user_message,
            'assistant': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_quick_suggestions(self):
        """
        Get quick suggestion prompts for users
        """
        return [
            "Suggest phones under ₹20,000",
            "Best laptops for gaming",
            "Wireless headphones under ₹5,000",
            "Show me smartwatches",
            "Trending products this week",
            "Cameras for photography",
            "Budget-friendly tablets",
            "Gaming accessories"
        ]
    
    def get_product_details(self, product_id):
        """
        Get detailed information about a specific product
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                p.*,
                c.name as category_name,
                s.business_name,
                s.owner_name,
                COALESCE(AVG(pr.rating), 0) as avg_rating,
                COUNT(DISTINCT pr.id) as review_count
            FROM products p
            JOIN categories c ON p.category_id = c.id
            JOIN sellers s ON p.seller_id = s.id
            LEFT JOIN product_reviews pr ON p.id = pr.product_id
            WHERE p.id = %s
            GROUP BY p.id
        """
        
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result['id'],
                'name': result['name'],
                'description': result['description'],
                'price': float(result['price']),
                'discount_price': float(result['discount_price']) if result['discount_price'] else None,
                'image_url': result['image_url'],
                'quantity': result['quantity'],
                'category_name': result['category_name'],
                'business_name': result['business_name'],
                'avg_rating': float(result['avg_rating']),
                'review_count': result['review_count']
            }
        
        return None


# Note: ai_assistant instance is created in routes/ai_chat.py with proper config
