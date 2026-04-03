"""
Loyalty & Rewards Service
Manages customer loyalty points, tiers, and rewards
"""

from app import get_db_connection
from datetime import datetime
import random
import string

class LoyaltyService:
    """
    Handles all loyalty program logic
    """
    
    # Tier thresholds
    TIERS = {
        'Bronze': {'min_points': 0, 'multiplier': 1.0, 'benefits': ['Basic rewards']},
        'Silver': {'min_points': 1000, 'multiplier': 1.5, 'benefits': ['1.5x points', 'Birthday bonus']},
        'Gold': {'min_points': 5000, 'multiplier': 2.0, 'benefits': ['2x points', 'Free shipping', 'Priority support']},
        'Platinum': {'min_points': 10000, 'multiplier': 3.0, 'benefits': ['3x points', 'Exclusive deals', 'VIP access']}
    }
    
    # Points earning rules
    POINTS_PER_RUPEE = 1  # 1 point per ₹1 spent
    SIGNUP_BONUS = 100
    REFERRAL_BONUS = 500
    REVIEW_BONUS = 50
    BIRTHDAY_BONUS = 200
    
    def __init__(self):
        pass
    
    def initialize_customer_loyalty(self, customer_id):
        """
        Initialize loyalty account for new customer
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Create loyalty account with signup bonus
            cursor.execute("""
                INSERT INTO loyalty_points (customer_id, points, tier, total_earned)
                VALUES (%s, %s, 'Bronze', %s)
            """, (customer_id, self.SIGNUP_BONUS, self.SIGNUP_BONUS))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO loyalty_transactions 
                (customer_id, points, type, description)
                VALUES (%s, %s, 'earned', 'Welcome bonus')
            """, (customer_id, self.SIGNUP_BONUS))
            
            # Generate referral code
            referral_code = self._generate_referral_code()
            cursor.execute("""
                UPDATE customers 
                SET referral_code = %s 
                WHERE id = %s
            """, (referral_code, customer_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error initializing loyalty: {e}")
            return False
        finally:
            conn.close()
    
    def get_customer_loyalty(self, customer_id):
        """
        Get customer's loyalty information
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                lp.*,
                c.referral_code,
                (SELECT COUNT(*) FROM referrals WHERE referrer_id = %s AND status = 'completed') as referral_count
            FROM loyalty_points lp
            JOIN customers c ON lp.customer_id = c.id
            WHERE lp.customer_id = %s
        """, (customer_id, customer_id))
        
        loyalty = cursor.fetchone()
        
        if loyalty:
            # Get tier info
            tier_info = self.TIERS.get(loyalty['tier'], self.TIERS['Bronze'])
            
            # Get next tier
            next_tier = self._get_next_tier(loyalty['tier'])
            points_to_next = 0
            if next_tier:
                points_to_next = self.TIERS[next_tier]['min_points'] - loyalty['points']
            
            # Get recent transactions
            cursor.execute("""
                SELECT * FROM loyalty_transactions
                WHERE customer_id = %s
                ORDER BY created_at DESC
                LIMIT 10
            """, (customer_id,))
            transactions = cursor.fetchall()
            
            conn.close()
            
            return {
                'points': loyalty['points'],
                'tier': loyalty['tier'],
                'total_earned': loyalty['total_earned'],
                'total_redeemed': loyalty['total_redeemed'],
                'tier_info': tier_info,
                'next_tier': next_tier,
                'points_to_next': points_to_next,
                'referral_code': loyalty['referral_code'],
                'referral_count': loyalty['referral_count'],
                'transactions': transactions
            }
        
        conn.close()
        return None
    
    def award_points_for_purchase(self, customer_id, order_id, order_amount):
        """
        Award points for a purchase
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get customer's current tier
            cursor.execute("""
                SELECT tier FROM loyalty_points WHERE customer_id = %s
            """, (customer_id,))
            result = cursor.fetchone()
            
            if not result:
                # Initialize if doesn't exist
                self.initialize_customer_loyalty(customer_id)
                tier = 'Bronze'
            else:
                tier = result['tier']
            
            # Calculate points with tier multiplier
            multiplier = self.TIERS[tier]['multiplier']
            base_points = int(order_amount * self.POINTS_PER_RUPEE)
            points = int(base_points * multiplier)
            
            # Update loyalty points
            cursor.execute("""
                UPDATE loyalty_points
                SET points = points + %s,
                    total_earned = total_earned + %s
                WHERE customer_id = %s
            """, (points, points, customer_id))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO loyalty_transactions
                (customer_id, points, type, description, order_id)
                VALUES (%s, %s, 'earned', %s, %s)
            """, (customer_id, points, f'Purchase reward (₹{order_amount:.2f})', order_id))
            
            # Check for tier upgrade
            self._check_tier_upgrade(customer_id, cursor)
            
            conn.commit()
            return points
        except Exception as e:
            conn.rollback()
            print(f"Error awarding points: {e}")
            return 0
        finally:
            conn.close()
    
    def redeem_points(self, customer_id, points, description='Points redemption'):
        """
        Redeem loyalty points
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if customer has enough points
            cursor.execute("""
                SELECT points FROM loyalty_points WHERE customer_id = %s
            """, (customer_id,))
            result = cursor.fetchone()
            
            if not result or result['points'] < points:
                return False, "Insufficient points"
            
            # Deduct points
            cursor.execute("""
                UPDATE loyalty_points
                SET points = points - %s,
                    total_redeemed = total_redeemed + %s
                WHERE customer_id = %s
            """, (points, points, customer_id))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO loyalty_transactions
                (customer_id, points, type, description)
                VALUES (%s, %s, 'redeemed', %s)
            """, (customer_id, -points, description))
            
            conn.commit()
            return True, "Points redeemed successfully"
        except Exception as e:
            conn.rollback()
            print(f"Error redeeming points: {e}")
            return False, str(e)
        finally:
            conn.close()
    
    def award_review_bonus(self, customer_id, product_id):
        """
        Award bonus points for writing a review
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if already awarded for this product
            cursor.execute("""
                SELECT id FROM loyalty_transactions
                WHERE customer_id = %s
                AND description LIKE %s
            """, (customer_id, f'%Review bonus%product {product_id}%'))
            
            if cursor.fetchone():
                conn.close()
                return 0  # Already awarded
            
            # Award points
            cursor.execute("""
                UPDATE loyalty_points
                SET points = points + %s,
                    total_earned = total_earned + %s
                WHERE customer_id = %s
            """, (self.REVIEW_BONUS, self.REVIEW_BONUS, customer_id))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO loyalty_transactions
                (customer_id, points, type, description)
                VALUES (%s, %s, 'earned', %s)
            """, (customer_id, self.REVIEW_BONUS, f'Review bonus for product {product_id}'))
            
            conn.commit()
            return self.REVIEW_BONUS
        except Exception as e:
            conn.rollback()
            print(f"Error awarding review bonus: {e}")
            return 0
        finally:
            conn.close()
    
    def process_referral(self, referrer_code, new_customer_id):
        """
        Process referral when new customer signs up
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Find referrer
            cursor.execute("""
                SELECT id FROM customers WHERE referral_code = %s
            """, (referrer_code,))
            referrer = cursor.fetchone()
            
            if not referrer:
                conn.close()
                return False
            
            referrer_id = referrer['id']
            
            # Create referral record
            cursor.execute("""
                INSERT INTO referrals
                (referrer_id, referred_id, referral_code, status)
                VALUES (%s, %s, %s, 'pending')
            """, (referrer_id, new_customer_id, referrer_code))
            
            # Update new customer's referred_by
            cursor.execute("""
                UPDATE customers
                SET referred_by = %s
                WHERE id = %s
            """, (referrer_id, new_customer_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error processing referral: {e}")
            return False
        finally:
            conn.close()
    
    def complete_referral(self, referred_customer_id):
        """
        Complete referral after first purchase
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Find pending referral
            cursor.execute("""
                SELECT * FROM referrals
                WHERE referred_id = %s
                AND status = 'pending'
            """, (referred_customer_id,))
            referral = cursor.fetchone()
            
            if not referral:
                conn.close()
                return False
            
            # Award points to referrer
            cursor.execute("""
                UPDATE loyalty_points
                SET points = points + %s,
                    total_earned = total_earned + %s
                WHERE customer_id = %s
            """, (self.REFERRAL_BONUS, self.REFERRAL_BONUS, referral['referrer_id']))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO loyalty_transactions
                (customer_id, points, type, description)
                VALUES (%s, %s, 'earned', 'Referral bonus')
            """, (referral['referrer_id'], self.REFERRAL_BONUS))
            
            # Update referral status
            cursor.execute("""
                UPDATE referrals
                SET status = 'completed',
                    completed_at = NOW()
                WHERE id = %s
            """, (referral['id'],))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error completing referral: {e}")
            return False
        finally:
            conn.close()
    
    def award_birthday_bonus(self, customer_id):
        """
        Award birthday bonus points
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if already awarded this year
            cursor.execute("""
                SELECT id FROM loyalty_transactions
                WHERE customer_id = %s
                AND description = 'Birthday bonus'
                AND YEAR(created_at) = YEAR(NOW())
            """, (customer_id,))
            
            if cursor.fetchone():
                conn.close()
                return 0  # Already awarded this year
            
            # Award points
            cursor.execute("""
                UPDATE loyalty_points
                SET points = points + %s,
                    total_earned = total_earned + %s
                WHERE customer_id = %s
            """, (self.BIRTHDAY_BONUS, self.BIRTHDAY_BONUS, customer_id))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO loyalty_transactions
                (customer_id, points, type, description)
                VALUES (%s, %s, 'earned', 'Birthday bonus')
            """, (customer_id, self.BIRTHDAY_BONUS))
            
            conn.commit()
            return self.BIRTHDAY_BONUS
        except Exception as e:
            conn.rollback()
            print(f"Error awarding birthday bonus: {e}")
            return 0
        finally:
            conn.close()
    
    def _check_tier_upgrade(self, customer_id, cursor):
        """
        Check and upgrade customer tier if eligible
        """
        cursor.execute("""
            SELECT points, tier FROM loyalty_points WHERE customer_id = %s
        """, (customer_id,))
        result = cursor.fetchone()
        
        if not result:
            return
        
        current_points = result['points']
        current_tier = result['tier']
        
        # Determine new tier
        new_tier = 'Bronze'
        for tier, info in sorted(self.TIERS.items(), key=lambda x: x[1]['min_points'], reverse=True):
            if current_points >= info['min_points']:
                new_tier = tier
                break
        
        # Update if tier changed
        if new_tier != current_tier:
            cursor.execute("""
                UPDATE loyalty_points
                SET tier = %s
                WHERE customer_id = %s
            """, (new_tier, customer_id))
            
            # Record tier upgrade
            cursor.execute("""
                INSERT INTO loyalty_transactions
                (customer_id, points, type, description)
                VALUES (%s, 0, 'earned', %s)
            """, (customer_id, f'Tier upgraded to {new_tier}'))
    
    def _get_next_tier(self, current_tier):
        """
        Get the next tier above current
        """
        tiers = ['Bronze', 'Silver', 'Gold', 'Platinum']
        try:
            current_index = tiers.index(current_tier)
            if current_index < len(tiers) - 1:
                return tiers[current_index + 1]
        except ValueError:
            pass
        return None
    
    def _generate_referral_code(self):
        """
        Generate unique referral code
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def get_leaderboard(self, limit=10):
        """
        Get top customers by points
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.first_name,
                c.last_name,
                lp.points,
                lp.tier,
                lp.total_earned
            FROM loyalty_points lp
            JOIN customers c ON lp.customer_id = c.id
            ORDER BY lp.points DESC
            LIMIT %s
        """, (limit,))
        
        leaderboard = cursor.fetchall()
        conn.close()
        
        return leaderboard
    
    def points_to_currency(self, points):
        """
        Convert points to currency value
        100 points = ₹10
        """
        return points / 10


# Create singleton instance
loyalty_service = LoyaltyService()
