-- Add Delivery System to Database
USE amazon_db;

-- Step 1: Create delivery personnel table first
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

-- Step 2: Add delivery columns to orders table (without foreign key first)
ALTER TABLE orders 
ADD COLUMN IF NOT EXISTS delivery_otp VARCHAR(6) DEFAULT NULL AFTER status,
ADD COLUMN IF NOT EXISTS delivery_otp_generated_at TIMESTAMP NULL AFTER delivery_otp,
ADD COLUMN IF NOT EXISTS delivery_person_id INT DEFAULT NULL AFTER delivery_otp_generated_at,
ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP NULL AFTER delivery_person_id;

-- Step 3: Add foreign key constraint (after both tables exist)
-- Note: If you get an error about duplicate constraint, it means the migration was already run
ALTER TABLE orders 
ADD CONSTRAINT fk_orders_delivery_person 
FOREIGN KEY (delivery_person_id) REFERENCES delivery_personnel(id) ON DELETE SET NULL;

-- Step 4: Create delivery tracking table
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

-- Step 5: Insert sample delivery personnel
-- Note: Use INSERT IGNORE to avoid duplicate entry errors
INSERT IGNORE INTO users (email, password, role) VALUES
('delivery1@shophub.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'delivery'),
('delivery2@shophub.com', 'scrypt:32768:8:1$vZ8qYxKjL9mN3pRt$a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', 'delivery');

-- Insert delivery personnel details (only if user exists and not already added)
INSERT INTO delivery_personnel (user_id, full_name, phone, vehicle_type, vehicle_number)
SELECT id, 'Rajesh Kumar', '9876543210', 'Bike', 'MH-01-AB-1234'
FROM users 
WHERE email = 'delivery1@shophub.com'
AND NOT EXISTS (SELECT 1 FROM delivery_personnel dp WHERE dp.user_id = users.id)
LIMIT 1;

INSERT INTO delivery_personnel (user_id, full_name, phone, vehicle_type, vehicle_number)
SELECT id, 'Amit Sharma', '9876543211', 'Bike', 'MH-01-CD-5678'
FROM users 
WHERE email = 'delivery2@shophub.com'
AND NOT EXISTS (SELECT 1 FROM delivery_personnel dp WHERE dp.user_id = users.id)
LIMIT 1;

-- Step 6: Create view for active deliveries
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

