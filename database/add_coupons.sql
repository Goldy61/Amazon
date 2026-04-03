-- Add Coupon System to Database
USE amazon_db;

-- Coupons table
CREATE TABLE IF NOT EXISTS coupons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    discount_type ENUM('percentage', 'fixed') NOT NULL,
    discount_value DECIMAL(10, 2) NOT NULL,
    min_order_amount DECIMAL(10, 2) DEFAULT 0,
    max_discount_amount DECIMAL(10, 2) DEFAULT NULL,
    usage_limit INT DEFAULT NULL,
    used_count INT DEFAULT 0,
    valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    applicable_to ENUM('all', 'category', 'product', 'seller') DEFAULT 'all',
    applicable_ids TEXT, -- JSON array of category/product/seller IDs
    created_by INT, -- Admin or seller who created it
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_code (code),
    INDEX idx_active (is_active),
    INDEX idx_valid (valid_from, valid_until)
);

-- Coupon usage tracking
CREATE TABLE IF NOT EXISTS coupon_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    coupon_id INT NOT NULL,
    customer_id INT NOT NULL,
    order_id INT NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_coupon (coupon_id),
    INDEX idx_customer (customer_id),
    INDEX idx_order (order_id)
);

-- Add coupon fields to orders table
ALTER TABLE orders 
ADD COLUMN coupon_id INT DEFAULT NULL AFTER total_amount,
ADD COLUMN discount_amount DECIMAL(10, 2) DEFAULT 0 AFTER coupon_id,
ADD COLUMN final_amount DECIMAL(10, 2) DEFAULT NULL AFTER discount_amount,
ADD FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE SET NULL;

-- Insert sample coupons
INSERT INTO coupons (code, description, discount_type, discount_value, min_order_amount, max_discount_amount, usage_limit, valid_until, applicable_to) VALUES
('WELCOME20', 'Welcome offer - 20% off on first order', 'percentage', 20.00, 500.00, 500.00, 1000, DATE_ADD(NOW(), INTERVAL 30 DAY), 'all'),
('SAVE100', 'Flat ₹100 off on orders above ₹1000', 'fixed', 100.00, 1000.00, NULL, NULL, DATE_ADD(NOW(), INTERVAL 60 DAY), 'all'),
('MEGA50', 'Mega sale - 50% off (max ₹1000)', 'percentage', 50.00, 2000.00, 1000.00, 500, DATE_ADD(NOW(), INTERVAL 15 DAY), 'all'),
('FLASH15', 'Flash sale - 15% off', 'percentage', 15.00, 300.00, 300.00, NULL, DATE_ADD(NOW(), INTERVAL 7 DAY), 'all'),
('FIRST500', 'First order special - ₹500 off', 'fixed', 500.00, 2500.00, NULL, 1000, DATE_ADD(NOW(), INTERVAL 90 DAY), 'all');

-- Create view for active coupons
CREATE OR REPLACE VIEW active_coupons AS
SELECT 
    c.*,
    (c.usage_limit - c.used_count) as remaining_uses
FROM coupons c
WHERE c.is_active = TRUE
AND (c.valid_until IS NULL OR c.valid_until > NOW())
AND (c.usage_limit IS NULL OR c.used_count < c.usage_limit);
