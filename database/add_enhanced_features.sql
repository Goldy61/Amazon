-- ============================================================================
-- ENHANCED E-COMMERCE FEATURES
-- ============================================================================
-- Add these features to enhance the shopping experience:
-- 1. Product Reviews & Ratings
-- 2. Wishlist/Favorites
-- 3. Newsletter Subscriptions
-- 4. Product Views Tracking
-- ============================================================================

USE amazon_db;

-- Product Reviews Table
CREATE TABLE IF NOT EXISTS product_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    order_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_title VARCHAR(200),
    review_text TEXT,
    is_verified_purchase BOOLEAN DEFAULT TRUE,
    helpful_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    UNIQUE KEY unique_review (product_id, customer_id, order_id),
    INDEX idx_product (product_id),
    INDEX idx_customer (customer_id),
    INDEX idx_rating (rating)
);

-- Wishlist Table
CREATE TABLE IF NOT EXISTS wishlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_wishlist_item (customer_id, product_id),
    INDEX idx_customer (customer_id)
);

-- Newsletter Subscriptions Table
CREATE TABLE IF NOT EXISTS newsletter_subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unsubscribed_at TIMESTAMP NULL,
    INDEX idx_email (email),
    INDEX idx_active (is_active)
);

-- Product Views Tracking
CREATE TABLE IF NOT EXISTS product_views (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    customer_id INT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    INDEX idx_product (product_id),
    INDEX idx_customer (customer_id),
    INDEX idx_viewed (viewed_at)
);

-- Add average rating and review count to products table
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS average_rating DECIMAL(3,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS review_count INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS view_count INT DEFAULT 0;

-- Create view for product statistics
CREATE OR REPLACE VIEW product_stats AS
SELECT 
    p.id,
    p.name,
    p.price,
    p.discount_price,
    COALESCE(AVG(pr.rating), 0) as avg_rating,
    COUNT(DISTINCT pr.id) as total_reviews,
    COUNT(DISTINCT w.id) as wishlist_count,
    COUNT(DISTINCT pv.id) as total_views
FROM products p
LEFT JOIN product_reviews pr ON p.id = pr.product_id
LEFT JOIN wishlist w ON p.id = w.product_id
LEFT JOIN product_views pv ON p.id = pv.product_id
GROUP BY p.id;

-- ============================================================================
-- Sample Data
-- ============================================================================

-- Add some sample reviews (assuming customer_id 1 and 2 exist, and they have orders)
INSERT IGNORE INTO product_reviews (product_id, customer_id, order_id, rating, review_title, review_text) VALUES
(1, 1, 1, 5, 'Excellent Product!', 'This product exceeded my expectations. Highly recommended!'),
(1, 2, 2, 4, 'Good quality', 'Very satisfied with the purchase. Fast delivery too.'),
(2, 1, 1, 5, 'Amazing!', 'Best purchase I have made this year. Worth every penny.'),
(3, 2, 2, 4, 'Great value', 'Good product for the price. Would buy again.');

-- Update product ratings based on reviews
UPDATE products p
SET 
    average_rating = (SELECT COALESCE(AVG(rating), 0) FROM product_reviews WHERE product_id = p.id),
    review_count = (SELECT COUNT(*) FROM product_reviews WHERE product_id = p.id);

-- ============================================================================
-- Useful Queries
-- ============================================================================

-- Get top rated products
-- SELECT * FROM products WHERE average_rating >= 4.0 ORDER BY average_rating DESC, review_count DESC LIMIT 10;

-- Get trending products (most viewed in last 7 days)
-- SELECT p.*, COUNT(pv.id) as recent_views 
-- FROM products p 
-- JOIN product_views pv ON p.id = pv.product_id 
-- WHERE pv.viewed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
-- GROUP BY p.id 
-- ORDER BY recent_views DESC 
-- LIMIT 10;

-- Get most wishlisted products
-- SELECT p.*, COUNT(w.id) as wishlist_count 
-- FROM products p 
-- JOIN wishlist w ON p.id = w.product_id 
-- GROUP BY p.id 
-- ORDER BY wishlist_count DESC 
-- LIMIT 10;
