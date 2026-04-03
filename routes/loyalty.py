"""
Loyalty & Rewards Program Routes
Handles points, tiers, and referrals
"""

from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, get_db_connection, login_required
from datetime import datetime
import random
import string

# Tier thresholds
TIER_THRESHOLDS = {
    'Bronze': 0,
    'Silver': 1000,
    'Gold': 5000,
    'Platinum': 10000
}

# Points earning rules
POINTS_PER_RUPEE = 1  # 1 point per ₹1 spent
REFERRAL_REWARD = 100  # Points for successful referral
REVIEW_REWARD = 50  # Points for writing a review
BIRTHDAY_BONUS = 200  # Birthday bonus points

@app.route('/loyalty')
@login_required('customer')
def loyalty_dashboard():
    """Loyalty program dashboard"""
    customer_id = session.get('customer_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get loyalty points
    cursor.execute("""
        SELECT * FROM loyalty_points 
        WHERE customer_id = %s
    """, (customer_id,))
    loyalty = cursor.fetchone()
    
    if not loyalty:
        # Create loyalty account
        cursor.execute("""
            INSERT INTO loyalty_points (customer_id, points, tier)
            VALUES (%s, 0, 'Bronze')
        """, (customer_id,))
        conn.commit()
        
        cursor.execute("""
            SELECT * FROM loyalty_points 
            WHERE customer_id = %s
        """, (customer_id,))
        loyalty = cursor.fetchone()
    
    # Get recent transactions
    cursor.execute("""
        SELECT * FROM loyalty_transactions
        WHERE customer_id = %s
        ORDER BY created_at DESC
        LIMIT 20
    """, (customer_id,))
    transactions = cursor.fetchall()
    
    # Get referral code
    cursor.execute("""
        SELECT referral_code FROM customers
        WHERE id = %s
    """, (customer_id,))
    customer = cursor.fetchone()
    referral_code = customer['referral_code'] if customer else None
    
    if not referral_code:
        # Generate referral code
        referral_code = generate_referral_code()
        cursor.execute("""
            UPDATE customers 
            SET referral_code = %s 
            WHERE id = %s
        """, (referral_code, customer_id))
        conn.commit()
    
    # Get referral stats
    cursor.execute("""
        SELECT COUNT(*) as total_referrals,
               SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_referrals
        FROM referrals
        WHERE referrer_id = %s
    """, (customer_id,))
    referral_stats = cursor.fetchone()
    
    # Calculate next tier
    current_points = loyalty['total_earned']
    next_tier = get_next_tier(loyalty['tier'])
    points_to_next = TIER_THRESHOLDS.get(next_tier, 0) - current_points if next_tier else 0
    
    conn.close()
    
    return render_template('loyalty/dashboard.html',
                         loyalty=loyalty,
                         transactions=transactions,
                         referral_code=referral_code,
                         referral_stats=referral_stats,
                         tier_thresholds=TIER_THRESHOLDS,
                         next_tier=next_tier,
                         points_to_next=points_to_next)

@app.route('/loyalty/redeem', methods=['POST'])
@login_required('customer')
def redeem_points():
    """Redeem loyalty points for discount"""
    customer_id = session.get('customer_id')
    points_to_redeem = int(request.form['points'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current points
    cursor.execute("""
        SELECT points FROM loyalty_points
        WHERE customer_id = %s
    """, (customer_id,))
    loyalty = cursor.fetchone()
    
    if not loyalty or loyalty['points'] < points_to_redeem:
        flash('Insufficient points!', 'error')
        return redirect(url_for('loyalty_dashboard'))
    
    # Minimum redemption: 100 points
    if points_to_redeem < 100:
        flash('Minimum redemption is 100 points!', 'error')
        return redirect(url_for('loyalty_dashboard'))
    
    # Deduct points
    cursor.execute("""
        UPDATE loyalty_points
        SET points = points - %s,
            total_redeemed = total_redeemed + %s
        WHERE customer_id = %s
    """, (points_to_redeem, points_to_redeem, customer_id))
    
    # Record transaction
    cursor.execute("""
        INSERT INTO loyalty_transactions 
        (customer_id, points, type, description)
        VALUES (%s, %s, 'redeemed', %s)
    """, (customer_id, -points_to_redeem, f'Redeemed {points_to_redeem} points'))
    
    # Generate discount coupon (1 point = ₹0.10)
    discount_amount = points_to_redeem * 0.10
    coupon_code = generate_coupon_code()
    
    cursor.execute("""
        INSERT INTO coupons 
        (code, discount_type, discount_value, min_order_amount, usage_limit, valid_from, valid_until)
        VALUES (%s, 'fixed', %s, 0, 1, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY))
    """, (coupon_code, discount_amount))
    
    conn.commit()
    conn.close()
    
    flash(f'Successfully redeemed {points_to_redeem} points! Your coupon code: {coupon_code}', 'success')
    return redirect(url_for('loyalty_dashboard'))

@app.route('/loyalty/refer')
@login_required('customer')
def referral_page():
    """Referral program page"""
    customer_id = session.get('customer_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get referral code
    cursor.execute("""
        SELECT referral_code, first_name, last_name
        FROM customers
        WHERE id = %s
    """, (customer_id,))
    customer = cursor.fetchone()
    
    # Get referral history
    cursor.execute("""
        SELECT r.*, c.first_name, c.last_name, u.email
        FROM referrals r
        JOIN customers c ON r.referred_id = c.id
        JOIN users u ON c.user_id = u.id
        WHERE r.referrer_id = %s
        ORDER BY r.created_at DESC
    """, (customer_id,))
    referrals = cursor.fetchall()
    
    conn.close()
    
    return render_template('loyalty/referral.html',
                         customer=customer,
                         referrals=referrals,
                         referral_reward=REFERRAL_REWARD)

@app.route('/api/loyalty/apply-referral', methods=['POST'])
def apply_referral_code():
    """Apply referral code during registration"""
    data = request.get_json()
    referral_code = data.get('referral_code')
    new_customer_id = data.get('customer_id')
    
    if not referral_code or not new_customer_id:
        return jsonify({'success': False, 'error': 'Missing data'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find referrer
    cursor.execute("""
        SELECT id FROM customers
        WHERE referral_code = %s
    """, (referral_code,))
    referrer = cursor.fetchone()
    
    if not referrer:
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid referral code'}), 404
    
    referrer_id = referrer['id']
    
    # Create referral record
    cursor.execute("""
        INSERT INTO referrals (referrer_id, referred_id, referral_code, status)
        VALUES (%s, %s, %s, 'pending')
    """, (referrer_id, new_customer_id, referral_code))
    
    # Update referred_by
    cursor.execute("""
        UPDATE customers
        SET referred_by = %s
        WHERE id = %s
    """, (referrer_id, new_customer_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Referral code applied!'})

def award_points(customer_id, points, description, order_id=None):
    """Award loyalty points to customer"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update points
    cursor.execute("""
        INSERT INTO loyalty_points (customer_id, points, total_earned)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            points = points + %s,
            total_earned = total_earned + %s
    """, (customer_id, points, points, points, points))
    
    # Record transaction
    cursor.execute("""
        INSERT INTO loyalty_transactions
        (customer_id, points, type, description, order_id)
        VALUES (%s, %s, 'earned', %s, %s)
    """, (customer_id, points, description, order_id))
    
    # Check for tier upgrade
    cursor.execute("""
        SELECT total_earned, tier FROM loyalty_points
        WHERE customer_id = %s
    """, (customer_id,))
    loyalty = cursor.fetchone()
    
    if loyalty:
        new_tier = calculate_tier(loyalty['total_earned'])
        if new_tier != loyalty['tier']:
            cursor.execute("""
                UPDATE loyalty_points
                SET tier = %s
                WHERE customer_id = %s
            """, (new_tier, customer_id))
            
            # Award tier upgrade bonus
            tier_bonus = get_tier_bonus(new_tier)
            if tier_bonus > 0:
                cursor.execute("""
                    UPDATE loyalty_points
                    SET points = points + %s,
                        total_earned = total_earned + %s
                    WHERE customer_id = %s
                """, (tier_bonus, tier_bonus, customer_id))
                
                cursor.execute("""
                    INSERT INTO loyalty_transactions
                    (customer_id, points, type, description)
                    VALUES (%s, %s, 'earned', %s)
                """, (customer_id, tier_bonus, f'Tier upgrade bonus: {new_tier}'))
    
    conn.commit()
    conn.close()

def complete_referral(referred_customer_id):
    """Complete referral when referred customer makes first purchase"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find pending referral
    cursor.execute("""
        SELECT * FROM referrals
        WHERE referred_id = %s
        AND status = 'pending'
    """, (referred_customer_id,))
    referral = cursor.fetchone()
    
    if referral:
        # Mark as completed
        cursor.execute("""
            UPDATE referrals
            SET status = 'completed',
                completed_at = NOW()
            WHERE id = %s
        """, (referral['id'],))
        
        # Award points to referrer
        award_points(
            referral['referrer_id'],
            REFERRAL_REWARD,
            f'Referral reward for inviting customer #{referred_customer_id}'
        )
        
        # Award welcome bonus to referred customer
        award_points(
            referred_customer_id,
            50,
            'Welcome bonus for joining via referral'
        )
        
        conn.commit()
    
    conn.close()

def calculate_tier(total_points):
    """Calculate tier based on total points earned"""
    if total_points >= TIER_THRESHOLDS['Platinum']:
        return 'Platinum'
    elif total_points >= TIER_THRESHOLDS['Gold']:
        return 'Gold'
    elif total_points >= TIER_THRESHOLDS['Silver']:
        return 'Silver'
    else:
        return 'Bronze'

def get_next_tier(current_tier):
    """Get next tier"""
    tiers = ['Bronze', 'Silver', 'Gold', 'Platinum']
    try:
        current_index = tiers.index(current_tier)
        if current_index < len(tiers) - 1:
            return tiers[current_index + 1]
    except ValueError:
        pass
    return None

def get_tier_bonus(tier):
    """Get bonus points for tier upgrade"""
    bonuses = {
        'Silver': 100,
        'Gold': 250,
        'Platinum': 500
    }
    return bonuses.get(tier, 0)

def generate_referral_code():
    """Generate unique referral code"""
    return 'REF' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_coupon_code():
    """Generate unique coupon code"""
    return 'LOYALTY' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
