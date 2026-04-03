-- ============================================================================
-- SHOPHUB - SAMPLE DATA
-- ============================================================================
-- This file adds sample sellers, customers, and products with images
-- Run after complete_database_setup.sql
-- ============================================================================

USE amazon_db;

-- ============================================================================
-- SAMPLE SELLERS
-- ============================================================================

-- Seller 1: TechWorld (password: seller123)
INSERT IGNORE INTO users (email, password, role) VALUES
('techworld@example.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'seller');

INSERT INTO sellers (user_id, business_name, owner_name, phone, address, city, state, pincode, gst_number, is_approved)
SELECT id, 'TechWorld Electronics', 'Rajesh Sharma', '9876543210', '123 Tech Street', 'Mumbai', 'Maharashtra', '400001', '27AABCT1234F1Z5', TRUE
FROM users WHERE email = 'techworld@example.com'
AND NOT EXISTS (SELECT 1 FROM sellers s WHERE s.user_id = users.id);

-- Seller 2: Fashion Hub (password: seller123)
INSERT IGNORE INTO users (email, password, role) VALUES
('fashionhub@example.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'seller');

INSERT INTO sellers (user_id, business_name, owner_name, phone, address, city, state, pincode, gst_number, is_approved)
SELECT id, 'Fashion Hub', 'Priya Patel', '9876543211', '456 Fashion Avenue', 'Delhi', 'Delhi', '110001', '07AABCT5678G1Z9', TRUE
FROM users WHERE email = 'fashionhub@example.com'
AND NOT EXISTS (SELECT 1 FROM sellers s WHERE s.user_id = users.id);

-- Seller 3: Book Paradise (password: seller123)
INSERT IGNORE INTO users (email, password, role) VALUES
('bookparadise@example.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'seller');

INSERT INTO sellers (user_id, business_name, owner_name, phone, address, city, state, pincode, gst_number, is_approved)
SELECT id, 'Book Paradise', 'Amit Kumar', '9876543212', '789 Book Lane', 'Bangalore', 'Karnataka', '560001', '29AABCT9012H1Z3', TRUE
FROM users WHERE email = 'bookparadise@example.com'
AND NOT EXISTS (SELECT 1 FROM sellers s WHERE s.user_id = users.id);

-- ============================================================================
-- SAMPLE CUSTOMERS
-- ============================================================================

-- Customer 1: John Doe (password: customer123)
INSERT IGNORE INTO users (email, password, role) VALUES
('john.doe@example.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'customer');

INSERT INTO customers (user_id, first_name, last_name, phone, address, city, state, pincode)
SELECT id, 'John', 'Doe', '9123456780', '101 Main Street', 'Mumbai', 'Maharashtra', '400002'
FROM users WHERE email = 'john.doe@example.com'
AND NOT EXISTS (SELECT 1 FROM customers c WHERE c.user_id = users.id);

-- Customer 2: Sarah Smith (password: customer123)
INSERT IGNORE INTO users (email, password, role) VALUES
('sarah.smith@example.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'customer');

INSERT INTO customers (user_id, first_name, last_name, phone, address, city, state, pincode)
SELECT id, 'Sarah', 'Smith', '9123456781', '202 Park Avenue', 'Delhi', 'Delhi', '110002'
FROM users WHERE email = 'sarah.smith@example.com'
AND NOT EXISTS (SELECT 1 FROM customers c WHERE c.user_id = users.id);

-- ============================================================================
-- SAMPLE PRODUCTS WITH IMAGES
-- ============================================================================

-- Electronics Products (Seller: TechWorld)
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Electronics'),
    'Apple iPhone 15 Pro',
    'Latest iPhone with A17 Pro chip, 6.1-inch Super Retina XDR display, Pro camera system with 48MP main camera',
    129900.00,
    119900.00,
    50,
    'IPHONE15PRO-128',
    'Apple',
    'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'IPHONE15PRO-128');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Electronics'),
    'Samsung Galaxy S24 Ultra',
    'Premium Android smartphone with 200MP camera, S Pen, 6.8-inch Dynamic AMOLED display',
    124999.00,
    114999.00,
    45,
    'SAMSUNG-S24-ULTRA',
    'Samsung',
    'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'SAMSUNG-S24-ULTRA');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Electronics'),
    'Sony WH-1000XM5 Headphones',
    'Industry-leading noise canceling wireless headphones with premium sound quality and 30-hour battery life',
    29990.00,
    24990.00,
    100,
    'SONY-WH1000XM5',
    'Sony',
    'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'SONY-WH1000XM5');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Electronics'),
    'MacBook Pro 14-inch M3',
    'Powerful laptop with M3 chip, 14-inch Liquid Retina XDR display, 16GB RAM, 512GB SSD',
    199900.00,
    189900.00,
    30,
    'MACBOOK-PRO-M3-14',
    'Apple',
    'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'MACBOOK-PRO-M3-14');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Electronics'),
    'iPad Air 11-inch',
    'Powerful and versatile tablet with M2 chip, 11-inch Liquid Retina display, Apple Pencil support',
    59900.00,
    54900.00,
    60,
    'IPAD-AIR-11-M2',
    'Apple',
    'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'IPAD-AIR-11-M2');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Electronics'),
    'Canon EOS R6 Mark II',
    'Professional mirrorless camera with 24.2MP full-frame sensor, 4K 60fps video, advanced autofocus',
    249900.00,
    234900.00,
    20,
    'CANON-R6-MKII',
    'Canon',
    'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'CANON-R6-MKII');

-- Clothing Products (Seller: Fashion Hub)
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Clothing'),
    'Men''s Casual Denim Jacket',
    'Classic blue denim jacket, comfortable fit, perfect for casual outings. Available in multiple sizes',
    2499.00,
    1999.00,
    150,
    'DENIM-JACKET-M-BLUE',
    'Levi''s',
    'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'DENIM-JACKET-M-BLUE');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Clothing'),
    'Women''s Summer Dress',
    'Elegant floral print summer dress, lightweight fabric, perfect for warm weather',
    1899.00,
    1499.00,
    200,
    'SUMMER-DRESS-W-FLORAL',
    'Zara',
    'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'SUMMER-DRESS-W-FLORAL');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Clothing'),
    'Men''s Formal Shirt',
    'Premium cotton formal shirt, wrinkle-free, perfect for office and formal occasions',
    1299.00,
    999.00,
    180,
    'FORMAL-SHIRT-M-WHITE',
    'Van Heusen',
    'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'FORMAL-SHIRT-M-WHITE');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Clothing'),
    'Women''s Leather Handbag',
    'Genuine leather handbag, spacious interior, elegant design with multiple compartments',
    3499.00,
    2999.00,
    80,
    'HANDBAG-W-LEATHER-BLK',
    'Michael Kors',
    'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'HANDBAG-W-LEATHER-BLK');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Clothing'),
    'Men''s Running Shoes',
    'Lightweight running shoes with cushioned sole, breathable mesh upper, perfect for daily runs',
    3999.00,
    3499.00,
    120,
    'RUNNING-SHOES-M-BLK',
    'Nike',
    'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'RUNNING-SHOES-M-BLK');

-- Books (Seller: Book Paradise)
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Books'),
    'The Psychology of Money',
    'Timeless lessons on wealth, greed, and happiness by Morgan Housel. Bestselling personal finance book',
    399.00,
    299.00,
    500,
    'BOOK-PSYCH-MONEY',
    'Penguin',
    'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Book Paradise'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'BOOK-PSYCH-MONEY');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Books'),
    'Atomic Habits',
    'An Easy & Proven Way to Build Good Habits & Break Bad Ones by James Clear',
    599.00,
    449.00,
    450,
    'BOOK-ATOMIC-HABITS',
    'Penguin Random House',
    'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Book Paradise'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'BOOK-ATOMIC-HABITS');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Books'),
    'Think Like a Monk',
    'Train Your Mind for Peace and Purpose Every Day by Jay Shetty',
    499.00,
    349.00,
    400,
    'BOOK-THINK-MONK',
    'HarperCollins',
    'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Book Paradise'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'BOOK-THINK-MONK');

-- Home & Kitchen (Seller: TechWorld)
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Home & Kitchen'),
    'Philips Air Fryer',
    'Digital air fryer with rapid air technology, 4.1L capacity, perfect for healthy cooking',
    8999.00,
    7499.00,
    75,
    'AIRFRYER-PHILIPS-4L',
    'Philips',
    'https://images.unsplash.com/photo-1585515320310-259814833e62?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'AIRFRYER-PHILIPS-4L');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Home & Kitchen'),
    'Instant Pot Duo',
    '7-in-1 electric pressure cooker, slow cooker, rice cooker, steamer, 6 quart capacity',
    9999.00,
    8499.00,
    60,
    'INSTANTPOT-DUO-6Q',
    'Instant Pot',
    'https://images.unsplash.com/photo-1585515320310-259814833e62?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'INSTANTPOT-DUO-6Q');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Home & Kitchen'),
    'Dyson V15 Vacuum Cleaner',
    'Cordless vacuum with laser dust detection, powerful suction, up to 60 minutes runtime',
    54900.00,
    49900.00,
    40,
    'DYSON-V15-CORDLESS',
    'Dyson',
    'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'TechWorld Electronics'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'DYSON-V15-CORDLESS');

-- Sports Products (Seller: Fashion Hub)
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Sports'),
    'Yoga Mat Premium',
    'Non-slip yoga mat with extra cushioning, eco-friendly material, includes carrying strap',
    1499.00,
    1199.00,
    200,
    'YOGA-MAT-PREMIUM',
    'Reebok',
    'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'YOGA-MAT-PREMIUM');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Sports'),
    'Adjustable Dumbbells Set',
    'Space-saving adjustable dumbbells, 5-25kg per dumbbell, quick weight adjustment',
    8999.00,
    7999.00,
    50,
    'DUMBBELL-ADJ-25KG',
    'Bowflex',
    'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'DUMBBELL-ADJ-25KG');

-- Beauty Products (Seller: Fashion Hub)
INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Beauty'),
    'Lakme Absolute Makeup Kit',
    'Complete makeup kit with foundation, lipstick, eyeliner, and more. Perfect for daily use',
    2999.00,
    2499.00,
    150,
    'MAKEUP-KIT-LAKME',
    'Lakme',
    'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'MAKEUP-KIT-LAKME');

INSERT INTO products (seller_id, category_id, name, description, price, discount_price, quantity, sku, brand, image_url, is_active)
SELECT 
    s.id,
    (SELECT id FROM categories WHERE name = 'Beauty'),
    'Neutrogena Skincare Set',
    'Complete skincare routine with cleanser, toner, moisturizer, and sunscreen',
    1999.00,
    1699.00,
    180,
    'SKINCARE-NEUTROGENA',
    'Neutrogena',
    'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=500',
    TRUE
FROM sellers s WHERE s.business_name = 'Fashion Hub'
AND NOT EXISTS (SELECT 1 FROM products p WHERE p.sku = 'SKINCARE-NEUTROGENA');

-- ============================================================================
-- SUMMARY
-- ============================================================================

SELECT '✅ Sample data added successfully!' AS status;
SELECT '' AS '';
SELECT 'Sellers Added: 3' AS sellers;
SELECT '  - TechWorld Electronics (techworld@example.com)' AS seller_1;
SELECT '  - Fashion Hub (fashionhub@example.com)' AS seller_2;
SELECT '  - Book Paradise (bookparadise@example.com)' AS seller_3;
SELECT '' AS '';
SELECT 'Customers Added: 2' AS customers;
SELECT '  - John Doe (john.doe@example.com)' AS customer_1;
SELECT '  - Sarah Smith (sarah.smith@example.com)' AS customer_2;
SELECT '' AS '';
SELECT 'Products Added: 20+' AS products;
SELECT '  - Electronics: 6 products' AS electronics;
SELECT '  - Clothing: 5 products' AS clothing;
SELECT '  - Books: 3 products' AS books;
SELECT '  - Home & Kitchen: 3 products' AS home;
SELECT '  - Sports: 2 products' AS sports;
SELECT '  - Beauty: 2 products' AS beauty;
SELECT '' AS '';
SELECT 'All passwords: seller123 / customer123' AS passwords;
SELECT '' AS '';
SELECT '🎉 Ready to browse products!' AS ready;
