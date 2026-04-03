-- ============================================
-- FAKE ORDERS FOR ANALYTICS
-- Add sample orders for testing analytics dashboard
-- ============================================

-- Part 1: Insert Orders
INSERT INTO orders (customer_id, order_number, total_amount, shipping_address, 
                    payment_method, payment_status, status, created_at, updated_at) VALUES

-- Week 1 (7 days ago)
(1, 'ORD2026031301', 2499.00, '123 MG Road, Mumbai, Maharashtra - 400001', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),

(1, 'ORD2026031302', 15999.00, '456 Park Street, Kolkata, West Bengal - 700016', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),

(1, 'ORD2026031303', 899.00, '789 Brigade Road, Bangalore, Karnataka - 560001', 
 'cod', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),

-- Week 2 (14 days ago)
(1, 'ORD2026031304', 45999.00, '321 Connaught Place, Delhi, Delhi - 110001', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 14 DAY), DATE_SUB(NOW(), INTERVAL 12 DAY)),

(1, 'ORD2026031305', 3499.00, '654 Anna Salai, Chennai, Tamil Nadu - 600002', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 13 DAY), DATE_SUB(NOW(), INTERVAL 11 DAY)),

(1, 'ORD2026031306', 1299.00, '987 FC Road, Pune, Maharashtra - 411004', 
 'cod', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 12 DAY), DATE_SUB(NOW(), INTERVAL 10 DAY)),

(1, 'ORD2026031307', 8999.00, '147 MG Road, Ahmedabad, Gujarat - 380009', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 11 DAY), DATE_SUB(NOW(), INTERVAL 9 DAY)),

-- Week 3 (21 days ago)
(1, 'ORD2026031308', 25999.00, '258 Residency Road, Hyderabad, Telangana - 500001', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 21 DAY), DATE_SUB(NOW(), INTERVAL 19 DAY)),

(1, 'ORD2026031309', 1899.00, '369 Mall Road, Jaipur, Rajasthan - 302001', 
 'cod', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 20 DAY), DATE_SUB(NOW(), INTERVAL 18 DAY)),

(1, 'ORD2026031310', 5499.00, '741 Park Street, Lucknow, Uttar Pradesh - 226001', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 19 DAY), DATE_SUB(NOW(), INTERVAL 17 DAY)),

(1, 'ORD2026031311', 12999.00, '852 Station Road, Chandigarh, Chandigarh - 160001', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 18 DAY), DATE_SUB(NOW(), INTERVAL 16 DAY)),

-- Week 4 (28 days ago)
(1, 'ORD2026031312', 3299.00, '963 Civil Lines, Indore, Madhya Pradesh - 452001', 
 'cod', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 28 DAY), DATE_SUB(NOW(), INTERVAL 26 DAY)),

(1, 'ORD2026031313', 7899.00, '159 Hazratganj, Kanpur, Uttar Pradesh - 208001', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 27 DAY), DATE_SUB(NOW(), INTERVAL 25 DAY)),

(1, 'ORD2026031314', 19999.00, '357 MG Road, Surat, Gujarat - 395001', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 26 DAY), DATE_SUB(NOW(), INTERVAL 24 DAY)),

(1, 'ORD2026031315', 2799.00, '486 Linking Road, Mumbai, Maharashtra - 400050', 
 'cod', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 25 DAY), DATE_SUB(NOW(), INTERVAL 23 DAY)),

-- Recent orders (last 7 days)
(1, 'ORD2026031316', 4999.00, '123 Sector 17, Noida, Uttar Pradesh - 201301', 
 'razorpay', 'completed', 'shipped', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),

(1, 'ORD2026031317', 9999.00, '456 Whitefield, Bangalore, Karnataka - 560066', 
 'razorpay', 'completed', 'shipped', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),

(1, 'ORD2026031318', 1599.00, '789 Banjara Hills, Hyderabad, Telangana - 500034', 
 'pending', 'pending', 'confirmed', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY)),

(1, 'ORD2026031319', 6499.00, '321 Koramangala, Bangalore, Karnataka - 560034', 
 'razorpay', 'completed', 'confirmed', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),

(1, 'ORD2026031320', 3999.00, '654 Powai, Mumbai, Maharashtra - 400076', 
 'razorpay', 'completed', 'pending', DATE_SUB(NOW(), INTERVAL 1 DAY), NOW()),

-- Orders from 2-3 months ago
(1, 'ORD2026031321', 15999.00, '123 Salt Lake, Kolkata, West Bengal - 700091', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 60 DAY), DATE_SUB(NOW(), INTERVAL 58 DAY)),

(1, 'ORD2026031322', 8999.00, '456 Indiranagar, Bangalore, Karnataka - 560038', 
 'razorpay', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 75 DAY), DATE_SUB(NOW(), INTERVAL 73 DAY)),

(1, 'ORD2026031323', 12999.00, '789 Jubilee Hills, Hyderabad, Telangana - 500033', 
 'cod', 'completed', 'delivered', DATE_SUB(NOW(), INTERVAL 90 DAY), DATE_SUB(NOW(), INTERVAL 88 DAY));

-- Part 2: Insert Order Items
-- Note: This assumes you have products with IDs 1-10 in your database
-- If you don't have products yet, add some products first before running this

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 1, 1, 1, 2499.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031301' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 2, 1, 1, 15999.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031302' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 3, 1, 1, 899.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031303' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 4, 1, 1, 45999.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031304' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 5, 1, 1, 3499.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031305' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 6, 1, 1, 1299.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031306' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 7, 1, 1, 8999.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031307' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 8, 1, 1, 25999.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031308' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 9, 1, 1, 1899.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031309' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 10, 1, 1, 5499.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031310' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 1, 1, 1, 12999.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031311' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 2, 1, 1, 3299.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031312' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 3, 1, 1, 7899.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031313' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 4, 1, 1, 19999.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031314' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 5, 1, 1, 2799.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031315' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 6, 1, 1, 4999.00, 'shipped' FROM orders o WHERE o.order_number = 'ORD2026031316' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 7, 1, 1, 9999.00, 'shipped' FROM orders o WHERE o.order_number = 'ORD2026031317' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 8, 1, 1, 1599.00, 'confirmed' FROM orders o WHERE o.order_number = 'ORD2026031318' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 9, 1, 1, 6499.00, 'confirmed' FROM orders o WHERE o.order_number = 'ORD2026031319' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 10, 1, 1, 3999.00, 'pending' FROM orders o WHERE o.order_number = 'ORD2026031320' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 1, 1, 1, 15999.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031321' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 2, 1, 1, 8999.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031322' LIMIT 1;

INSERT INTO order_items (order_id, product_id, seller_id, quantity, price, status)
SELECT o.id, 3, 1, 1, 12999.00, 'delivered' FROM orders o WHERE o.order_number = 'ORD2026031323' LIMIT 1;

-- Success message
SELECT 'Fake orders added successfully!' as message,
       COUNT(*) as total_orders,
       SUM(total_amount) as total_revenue
FROM orders 
WHERE order_number LIKE 'ORD202603%';
