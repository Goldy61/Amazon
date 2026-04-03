-- ============================================
-- PREMIUM FEATURES DATABASE SCHEMA
-- ============================================

-- 1. PRODUCT COMPARISON
CREATE TABLE IF NOT EXISTS product_comparisons (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    product_ids JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- 2. LOYALTY & REWARDS PROGRAM
CREATE TABLE IF NOT EXISTS loyalty_points (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    points INT DEFAULT 0,
    tier VARCHAR(20) DEFAULT 'Bronze',
    total_earned INT DEFAULT 0,
    total_redeemed INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    UNIQUE KEY (customer_id)
);

CREATE TABLE IF NOT EXISTS loyalty_transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    points INT NOT NULL,
    type ENUM('earned', 'redeemed', 'expired') NOT NULL,
    description VARCHAR(255),
    order_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS referrals (
    id INT PRIMARY KEY AUTO_INCREMENT,
    referrer_id INT NOT NULL,
    referred_id INT NOT NULL,
    referral_code VARCHAR(50) UNIQUE NOT NULL,
    status ENUM('pending', 'completed') DEFAULT 'pending',
    reward_points INT DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    FOREIGN KEY (referrer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (referred_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- 3. FLASH DEALS & DAILY DEALS
CREATE TABLE IF NOT EXISTS flash_deals (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    original_price DECIMAL(10, 2) NOT NULL,
    deal_price DECIMAL(10, 2) NOT NULL,
    discount_percentage INT,
    quantity_limit INT,
    quantity_sold INT DEFAULT 0,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    deal_type ENUM('flash', 'daily', 'weekly') DEFAULT 'flash',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 4. PRODUCT RECOMMENDATIONS
CREATE TABLE IF NOT EXISTS product_recommendations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    recommended_product_id INT NOT NULL,
    recommendation_type ENUM('also_bought', 'similar', 'trending') NOT NULL,
    score DECIMAL(5, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (recommended_product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 5. RECENTLY VIEWED PRODUCTS
CREATE TABLE IF NOT EXISTS recently_viewed (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    product_id INT NOT NULL,
    session_id VARCHAR(255),
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_customer_viewed (customer_id, viewed_at),
    INDEX idx_session_viewed (session_id, viewed_at)
);

-- 6. LIVE NOTIFICATIONS (Social Proof)
CREATE TABLE IF NOT EXISTS live_notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    notification_type ENUM('purchase', 'review', 'stock_alert', 'deal') NOT NULL,
    customer_name VARCHAR(100),
    product_name VARCHAR(255),
    location VARCHAR(100),
    message TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NULL
);

-- 7. STOCK ALERTS
CREATE TABLE IF NOT EXISTS stock_alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    is_notified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notified_at DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_alert (customer_id, product_id)
);

-- 8. GIFT CARDS
CREATE TABLE IF NOT EXISTS gift_cards (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL,
    buyer_id INT,
    recipient_email VARCHAR(255),
    recipient_name VARCHAR(100),
    message TEXT,
    status ENUM('active', 'used', 'expired') DEFAULT 'active',
    expires_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at DATETIME NULL,
    FOREIGN KEY (buyer_id) REFERENCES customers(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS gift_card_transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    gift_card_id INT NOT NULL,
    order_id INT,
    amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (gift_card_id) REFERENCES gift_cards(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
);

-- 9. PRE-ORDERS & WAITLIST
CREATE TABLE IF NOT EXISTS pre_orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1,
    expected_date DATE,
    status ENUM('pending', 'confirmed', 'fulfilled', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS waitlist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    is_notified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notified_at DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_waitlist (customer_id, product_id)
);

-- 10. LIVE CHAT SUPPORT
CREATE TABLE IF NOT EXISTS chat_conversations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    session_id VARCHAR(255),
    status ENUM('active', 'closed', 'pending') DEFAULT 'active',
    assigned_to INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    conversation_id INT NOT NULL,
    sender_type ENUM('customer', 'support', 'bot') NOT NULL,
    sender_id INT,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES chat_conversations(id) ON DELETE CASCADE
);

-- 11. PRODUCT BUNDLES
CREATE TABLE IF NOT EXISTS product_bundles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    discount_percentage INT DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bundle_products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    bundle_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT DEFAULT 1,
    FOREIGN KEY (bundle_id) REFERENCES product_bundles(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 12. ABANDONED CART TRACKING
CREATE TABLE IF NOT EXISTS abandoned_carts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    session_id VARCHAR(255),
    cart_data JSON NOT NULL,
    total_amount DECIMAL(10, 2),
    email_sent BOOLEAN DEFAULT 0,
    recovered BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email_sent_at DATETIME NULL,
    recovered_at DATETIME NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- 13. SOCIAL MEDIA SHARES
CREATE TABLE IF NOT EXISTS social_shares (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    platform ENUM('facebook', 'twitter', 'instagram', 'whatsapp', 'pinterest') NOT NULL,
    share_count INT DEFAULT 0,
    last_shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 14. PRODUCT QUESTIONS & ANSWERS
CREATE TABLE IF NOT EXISTS product_questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    question TEXT NOT NULL,
    is_answered BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS product_answers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question_id INT NOT NULL,
    answerer_type ENUM('seller', 'admin', 'customer') NOT NULL,
    answerer_id INT NOT NULL,
    answer TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT 0,
    helpful_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES product_questions(id) ON DELETE CASCADE
);

-- 15. PRICE DROP ALERTS
CREATE TABLE IF NOT EXISTS price_alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    target_price DECIMAL(10, 2) NOT NULL,
    current_price DECIMAL(10, 2) NOT NULL,
    is_triggered BOOLEAN DEFAULT 0,
    is_notified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggered_at TIMESTAMP NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Add columns to existing tables
ALTER TABLE customers ADD COLUMN IF NOT EXISTS referral_code VARCHAR(50) UNIQUE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS referred_by INT;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS birthday DATE;

ALTER TABLE products ADD COLUMN IF NOT EXISTS stock_alert_threshold INT DEFAULT 5;
ALTER TABLE products ADD COLUMN IF NOT EXISTS is_pre_order BOOLEAN DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS expected_date DATE;
ALTER TABLE products ADD COLUMN IF NOT EXISTS view_count INT DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS share_count INT DEFAULT 0;

-- Indexes for performance
CREATE INDEX idx_flash_deals_active ON flash_deals(is_active, start_time, end_time);
CREATE INDEX idx_loyalty_customer ON loyalty_points(customer_id);
CREATE INDEX idx_recently_viewed_customer ON recently_viewed(customer_id, viewed_at);
CREATE INDEX idx_live_notifications_active ON live_notifications(is_active, created_at);
CREATE INDEX idx_chat_conversations_status ON chat_conversations(status, created_at);
