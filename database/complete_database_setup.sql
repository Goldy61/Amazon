-- ============================================================================
-- SHOPHUB E-COMMERCE - COMPLETE DATABASE SETUP
-- ============================================================================
-- This file contains the complete database schema including:
-- 1. Main e-commerce tables (users, products, orders, etc.)
-- 2. Coupon system
-- 3. Delivery system with OTP verification
-- 4. Sample data
-- ============================================================================

-- Create and use database
CREATE DATABASE IF NOT EXISTS amazon_db;
USE amazon_db;

-- ============================================================================
-- SECTION 1: CORE E-COMMERCE TABLES
-- ============================================================================

-- Users table (for authentication)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'seller', 'customer', 'delivery') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    profile_image VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
);

-- Sellers table
CREATE TABLE IF NOT EXISTS sellers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    owner_name VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    gst_number VARCHAR(15),
    bank_account VARCHAR(20),
    ifsc_code VARCHAR(11),
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_approved (is_approved)
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_active (is_active)
);

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seller_id INT NOT NULL,
    category_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    discount_price DECIMAL(10, 2) DEFAULT NULL,
    quantity INT NOT NULL DEFAULT 0,
    sku VARCHAR(100) UNIQUE,
    brand VARCHAR(100),
    weight DECIMAL(8, 2),
    dimensions VARCHAR(100),
    image_url VARCHAR(500),
    additional_images TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES sellers(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_category (category_id),
    INDEX idx_seller (seller_id),
    INDEX idx_active (is_active)
);

-- Cart table
CREATE TABLE IF NOT EXISTS cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_cart_item (customer_id, product_id)
);

-- ============================================================================
-- SECTION 2: COUPON SYSTEM
-- ============================================================================

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
    applicable_ids TEXT,
    created_by INT,
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
    INDEX idx_coupon (coupon_id),
    INDEX idx_customer (customer_id),
    INDEX idx_order (order_id)
);

-- ============================================================================
-- SECTION 3: DELIVERY SYSTEM
-- ============================================================================

-- Delivery personnel table
CREATE TABLE IF NOT EXISTS delivery_personnel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    vehicle_type VARCHAR(50),
    vehicle_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_active (is_active)
);

-- Orders table (with coupon and delivery fields)
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    coupon_id INT DEFAULT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    final_amount DECIMAL(10, 2) DEFAULT NULL,
    shipping_address TEXT NOT NULL,
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    status ENUM('pending', 'confirmed', 'shipped', 'out_for_delivery', 'delivered', 'cancelled') DEFAULT 'pending',
    delivery_otp VARCHAR(6) DEFAULT NULL,
    delivery_otp_generated_at TIMESTAMP NULL,
    delivery_person_id INT DEFAULT NULL,
    delivered_at TIMESTAMP NULL,
    payment_method VARCHAR(50),
    razorpay_order_id VARCHAR(100),
    razorpay_payment_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE SET NULL,
    FOREIGN KEY (delivery_person_id) REFERENCES delivery_personnel(id) ON DELETE SET NULL,
    INDEX idx_customer (customer_id),
    INDEX idx_status (status),
    INDEX idx_delivery_person (delivery_person_id)
);

-- Add foreign key for coupon_usage (after orders table is created)
ALTER TABLE coupon_usage 
ADD FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    seller_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (seller_id) REFERENCES sellers(id),
    INDEX idx_order (order_id),
    INDEX idx_seller (seller_id)
);

-- Delivery tracking table
CREATE TABLE IF NOT EXISTS delivery_tracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    delivery_person_id INT NOT NULL,
    status ENUM('assigned', 'picked_up', 'in_transit', 'delivered', 'failed') DEFAULT 'assigned',
    notes TEXT,
    location VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (delivery_person_id) REFERENCES delivery_personnel(id) ON DELETE CASCADE,
    INDEX idx_order (order_id),
    INDEX idx_delivery_person (delivery_person_id),
    INDEX idx_status (status)
);

-- ============================================================================
-- SECTION 4: ADDITIONAL TABLES
-- ============================================================================

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    razorpay_order_id VARCHAR(100),
    razorpay_payment_id VARCHAR(100),
    razorpay_signature VARCHAR(500),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    status ENUM('created', 'authorized', 'captured', 'refunded', 'failed') DEFAULT 'created',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_order (order_id),
    INDEX idx_razorpay_order (razorpay_order_id)
);

-- Email logs table
CREATE TABLE IF NOT EXISTS email_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipient_email VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    email_type ENUM('registration', 'seller_approval', 'seller_rejection', 'product_added', 'order_placed', 'payment_success', 'payment_failed', 'order_status_update', 'password_reset', 'login_otp', 'delivery_confirmation') NOT NULL,
    status ENUM('sent', 'failed', 'pending') DEFAULT 'pending',
    error_message TEXT,
    user_id INT,
    order_id INT,
    product_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
    INDEX idx_recipient (recipient_email),
    INDEX idx_type (email_type),
    INDEX idx_status (status)
);

-- OTP table for login verification
CREATE TABLE IF NOT EXISTS login_otps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_otp (otp_code),
    INDEX idx_expires (expires_at)
);

-- Chat logs table for AI chat interactions
CREATE TABLE IF NOT EXISTS chat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    user_type ENUM('guest', 'customer', 'seller', 'admin', 'delivery') NOT NULL DEFAULT 'guest',
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    tokens_used INT DEFAULT 0,
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_type (user_type),
    INDEX idx_created (created_at)
);

-- ============================================================================
-- SECTION 5: VIEWS
-- ============================================================================

-- Active coupons view
CREATE OR REPLACE VIEW active_coupons AS
SELECT 
    c.*,
    (c.usage_limit - c.used_count) as remaining_uses
FROM coupons c
WHERE c.is_active = TRUE
AND (c.valid_until IS NULL OR c.valid_until > NOW())
AND (c.usage_limit IS NULL OR c.used_count < c.usage_limit);

-- Active deliveries view
CREATE OR REPLACE VIEW active_deliveries AS
SELECT 
    o.id as order_id,
    o.order_number,
    o.status as order_status,
    o.delivery_otp,
    o.delivery_otp_generated_at,
    o.delivery_person_id,
    dp.full_name as delivery_person_name,
    dp.phone as delivery_person_phone,
    c.first_name,
    c.last_name,
    u.email as customer_email,
    o.shipping_address,
    o.final_amount,
    o.created_at as order_date
FROM orders o
LEFT JOIN delivery_personnel dp ON o.delivery_person_id = dp.id
JOIN customers c ON o.customer_id = c.id
JOIN users u ON c.user_id = u.id
WHERE o.status IN ('shipped', 'out_for_delivery')
ORDER BY o.created_at DESC;

-- ============================================================================
-- SECTION 6: SAMPLE DATA
-- ============================================================================

-- Insert default admin user (password: admin123)
INSERT IGNORE INTO users (email, password, role) VALUES 
('admin@shophub.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'admin');

-- Insert delivery personnel accounts (password: delivery123)
INSERT IGNORE INTO users (email, password, role) VALUES
('delivery1@shophub.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'delivery'),
('delivery2@shophub.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'delivery');

-- Insert delivery personnel profiles
INSERT INTO delivery_personnel (user_id, full_name, phone, vehicle_type, vehicle_number)
SELECT id, 'Rajesh Kumar', '9876543210', 'Bike', 'MH-01-AB-1234'
FROM users WHERE email = 'delivery1@shophub.com'
AND NOT EXISTS (SELECT 1 FROM delivery_personnel dp WHERE dp.user_id = users.id);

INSERT INTO delivery_personnel (user_id, full_name, phone, vehicle_type, vehicle_number)
SELECT id, 'Amit Sharma', '9876543211', 'Bike', 'MH-01-CD-5678'
FROM users WHERE email = 'delivery2@shophub.com'
AND NOT EXISTS (SELECT 1 FROM delivery_personnel dp WHERE dp.user_id = users.id);

-- Insert default categories
INSERT IGNORE INTO categories (name, description) VALUES 
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Fashion and apparel'),
('Books', 'Books and educational materials'),
('Home & Kitchen', 'Home appliances and kitchen items'),
('Sports', 'Sports and fitness equipment'),
('Beauty', 'Beauty and personal care products'),
('Toys', 'Toys and games'),
('Automotive', 'Car and bike accessories');

-- Insert sample coupons
INSERT IGNORE INTO coupons (code, description, discount_type, discount_value, min_order_amount, max_discount_amount, usage_limit, valid_until, applicable_to) VALUES
('WELCOME20', 'Welcome offer - 20% off on first order', 'percentage', 20.00, 500.00, 500.00, 1000, DATE_ADD(NOW(), INTERVAL 30 DAY), 'all'),
('SAVE100', 'Flat ₹100 off on orders above ₹1000', 'fixed', 100.00, 1000.00, NULL, NULL, DATE_ADD(NOW(), INTERVAL 60 DAY), 'all'),
('MEGA50', 'Mega sale - 50% off (max ₹1000)', 'percentage', 50.00, 2000.00, 1000.00, 500, DATE_ADD(NOW(), INTERVAL 15 DAY), 'all'),
('FLASH15', 'Flash sale - 15% off', 'percentage', 15.00, 300.00, 300.00, NULL, DATE_ADD(NOW(), INTERVAL 7 DAY), 'all'),
('FIRST500', 'First order special - ₹500 off', 'fixed', 500.00, 2500.00, NULL, 1000, DATE_ADD(NOW(), INTERVAL 90 DAY), 'all');

-- ============================================================================
-- SECTION 7: SAMPLE SELLERS, CUSTOMERS & PRODUCTS
-- ============================================================================

-- Sample Sellers
INSERT IGNORE INTO users (email, password, role) VALUES
('techworld@example.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'seller'),
('fashionhub@example.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'seller'),
('bookparadise@example.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'seller');

INSERT INTO sellers (user_id, business_name, owner_name, phone, address, city, state, pincode, gst_number, is_approved)
SELECT id, 'TechWorld Electronics', 'Rajesh Sharma', '9876543210', '123 Tech Street', 'Mumbai', 'Maharashtra', '400001', '27AABCT1234F1Z5', TRUE
FROM users WHERE email = 'techworld@example.com' AND NOT EXISTS (SELECT 1 FROM sellers s WHERE s.user_id = users.id);

INSERT INTO sellers (user_id, business_name, owner_name, phone, address, city, state, pincode, gst_number, is_approved)
SELECT id, 'Fashion Hub', 'Priya Patel', '9876543211', '456 Fashion Avenue', 'Delhi', 'Delhi', '110001', '07AABCT5678G1Z9', TRUE
FROM users WHERE email = 'fashionhub@example.com' AND NOT EXISTS (SELECT 1 FROM sellers s WHERE s.user_id = users.id);

INSERT INTO sellers (user_id, business_name, owner_name, phone, address, city, state, pincode, gst_number, is_approved)
SELECT id, 'Book Paradise', 'Amit Kumar', '9876543212', '789 Book Lane', 'Bangalore', 'Karnataka', '560001', '29AABCT9012H1Z3', TRUE
FROM users WHERE email = 'bookparadise@example.com' AND NOT EXISTS (SELECT 1 FROM sellers s WHERE s.user_id = users.id);

-- Sample Customers
INSERT IGNORE INTO users (email, password, role) VALUES
('john.doe@example.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'customer'),
('sarah.smith@example.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'customer');

INSERT INTO customers (user_id, first_name, last_name, phone, address, city, state, pincode)
SELECT id, 'John', 'Doe', '9123456780', '101 Main Street', 'Mumbai', 'Maharashtra', '400002'
FROM users WHERE email = 'john.doe@example.com' AND NOT EXISTS (SELECT 1 FROM customers c WHERE c.user_id = users.id);

INSERT INTO customers (user_id, first_name, last_name, phone, address, city, state, pincode)
SELECT id, 'Sarah', 'Smith', '9123456781', '202 Park Avenue', 'Delhi', 'Delhi', '110002'
FROM users WHERE email = 'sarah.smith@example.com' AND NOT EXISTS (SELECT 1 FROM customers c WHERE c.user_id = users.id);

-- Sample Products (20+ products with images)
-- Electronics
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Electronics'), 'Apple iPhone 15 Pro', 'Latest iPhone with A17 Pro chip, 6.1-inch Super Retina XDR display', 129900.00, 119900.00, 50, 'IPHONE15PRO-128', 'Apple', 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500', TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'IPHONE15PRO-128');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Electronics'), 'Samsung Galaxy S24 Ultra', 'Premium Android smartphone with 200MP camera, S Pen', 124999.00, 114999.00, 45, 'SAMSUNG-S24-ULTRA', 'Samsung', 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500', TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'SAMSUNG-S24-ULTRA');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Electronics'), 'Sony WH-1000XM5 Headphones', 'Industry-leading noise canceling wireless headphones', 29990.00, 24990.00, 100, 'SONY-WH1000XM5', 'Sony', 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500', TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'SONY-WH1000XM5');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Electronics'), 'MacBook Pro 14-inch M3', 'Powerful laptop with M3 chip, 16GB RAM, 512GB SSD', 199900.00, 189900.00, 30, 'MACBOOK-PRO-M3-14', 'Apple', 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500', TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'MACBOOK-PRO-M3-14');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Electronics'), 'iPad Air 11-inch', 'Powerful tablet with M2 chip, Apple Pencil support', 59900.00, 54900.00, 60, 'IPAD-AIR-11-M2', 'Apple', 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500', TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'IPAD-AIR-11-M2');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Electronics'), 'Canon EOS R6 Mark II', 'Professional mirrorless camera with 24.2MP sensor', 249900.00, 234900.00, 20, 'CANON-R6-MKII', 'Canon', 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500', TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'CANON-R6-MKII');

-- Clothing
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Clothing'), 'Men''s Casual Denim Jacket', 'Classic blue denim jacket, comfortable fit', 2499.00, 1999.00, 150, 'DENIM-JACKET-M-BLUE', 'Levi''s', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'DENIM-JACKET-M-BLUE');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Clothing'), 'Women''s Summer Dress', 'Elegant floral print summer dress', 1899.00, 1499.00, 200, 'SUMMER-DRESS-W-FLORAL', 'Zara', 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'SUMMER-DRESS-W-FLORAL');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Clothing'), 'Men''s Formal Shirt', 'Premium cotton formal shirt, wrinkle-free', 1299.00, 999.00, 180, 'FORMAL-SHIRT-M-WHITE', 'Van Heusen', 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'FORMAL-SHIRT-M-WHITE');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Clothing'), 'Women''s Leather Handbag', 'Genuine leather handbag with multiple compartments', 3499.00, 2999.00, 80, 'HANDBAG-W-LEATHER-BLK', 'Michael Kors', 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'HANDBAG-W-LEATHER-BLK');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Clothing'), 'Men''s Running Shoes', 'Lightweight running shoes with cushioned sole', 3999.00, 3499.00, 120, 'RUNNING-SHOES-M-BLK', 'Nike', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'RUNNING-SHOES-M-BLK');

-- Books
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Books'), 'The Psychology of Money', 'Timeless lessons on wealth by Morgan Housel', 399.00, 299.00, 500, 'BOOK-PSYCH-MONEY', 'Penguin', 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Book Paradise' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'BOOK-PSYCH-MONEY');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Books'), 'Atomic Habits', 'Build Good Habits & Break Bad Ones by James Clear', 599.00, 449.00, 450, 'BOOK-ATOMIC-HABITS', 'Penguin', 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Book Paradise' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'BOOK-ATOMIC-HABITS');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Books'), 'Think Like a Monk', 'Train Your Mind for Peace by Jay Shetty', 499.00, 349.00, 400, 'BOOK-THINK-MONK', 'HarperCollins', 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Book Paradise' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'BOOK-THINK-MONK');

-- Home & Kitchen
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Home & Kitchen'), 'Philips Air Fryer', 'Digital air fryer with rapid air technology, 4.1L', 8999.00, 7499.00, 75, 'AIRFRYER-PHILIPS-4L', 'Philips', 'https://images.unsplash.com/photo-1585515320310-259814833e62?w=500', TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'AIRFRYER-PHILIPS-4L');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Home & Kitchen'), 'Dyson V15 Vacuum Cleaner', 'Cordless vacuum with laser dust detection', 54900.00, 49900.00, 40, 'DYSON-V15-CORDLESS', 'Dyson', 'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=500', TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'DYSON-V15-CORDLESS');

-- Sports
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Sports'), 'Yoga Mat Premium', 'Non-slip yoga mat with extra cushioning', 1499.00, 1199.00, 200, 'YOGA-MAT-PREMIUM', 'Reebok', 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'YOGA-MAT-PREMIUM');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Sports'), 'Adjustable Dumbbells Set', 'Space-saving adjustable dumbbells, 5-25kg', 8999.00, 7999.00, 50, 'DUMBBELL-ADJ-25KG', 'Bowflex', 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'DUMBBELL-ADJ-25KG');

-- Beauty
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Beauty'), 'Lakme Absolute Makeup Kit', 'Complete makeup kit for daily use', 2999.00, 2499.00, 150, 'MAKEUP-KIT-LAKME', 'Lakme', 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'MAKEUP-KIT-LAKME');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT s.id, (SELECT id FROM categories WHERE name = 'Beauty'), 'Neutrogena Skincare Set', 'Complete skincare routine set', 1999.00, 1699.00, 180, 'SKINCARE-NEUTROGENA', 'Neutrogena', 'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=500', TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub' AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'SKINCARE-NEUTROGENA');

-- ============================================================================
-- SETUP COMPLETE
-- ============================================================================

SELECT '✅ Database setup completed successfully!' AS status;
SELECT 'Database: amazon_db' AS info;
SELECT 'Tables created: 20+' AS info;
SELECT 'Sample data inserted' AS info;
SELECT '' AS '';
SELECT '👥 Default Accounts:' AS accounts;
SELECT 'Admin: admin@shophub.com / admin123' AS admin_account;
SELECT 'Delivery 1: delivery1@shophub.com / delivery123' AS delivery_account_1;
SELECT 'Delivery 2: delivery2@shophub.com / delivery123' AS delivery_account_2;
SELECT '' AS '';
SELECT '🏪 Sample Sellers (password: seller123):' AS sellers;
SELECT 'TechWorld: techworld@example.com' AS seller_1;
SELECT 'Fashion Hub: fashionhub@example.com' AS seller_2;
SELECT 'Book Paradise: bookparadise@example.com' AS seller_3;
SELECT '' AS '';
SELECT '�️ Sample Customers (password: customer123):' AS customers;
SELECT 'John Doe: john.doe@example.com' AS customer_1;
SELECT 'Sarah Smith: sarah.smith@example.com' AS customer_2;
SELECT '' AS '';
SELECT '📦 Products Added: 20+ with images' AS products;
SELECT 'Electronics: 6 | Clothing: 5 | Books: 3' AS product_categories_1;
SELECT 'Home & Kitchen: 2 | Sports: 2 | Beauty: 2' AS product_categories_2;
SELECT '' AS '';
SELECT '🎟️ Sample Coupons: WELCOME20, SAVE100, MEGA50, FLASH15, FIRST500' AS coupons;
SELECT '' AS '';
SELECT '🚀 Ready to start the application!' AS ready;
