"""
Database seeding script to populate the database with sample data
Run this script to add test data to your amazon_db
"""

import pymysql
from config import Config
from app import hash_password
from datetime import datetime, timedelta
import random

def get_db_connection():
    """Get database connection"""
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )

def seed_data():
    """Insert sample data into the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("Starting database seeding...")
        
        # 1. Add Categories
        print("\n1. Adding Categories...")
        categories = [
            ("Electronics", "Electronic devices and gadgets"),
            ("Fashion", "Clothing, shoes, and accessories"),
            ("Books", "Physical and digital books"),
            ("Home & Kitchen", "Household items and kitchen appliances"),
            ("Sports & Outdoors", "Sports equipment and outdoor gear"),
            ("Toys & Games", "Toys, games, and entertainment"),
            ("Beauty & Personal Care", "Cosmetics and personal care products"),
            ("Furniture", "Home furniture and decor")
        ]
        
        for name, description in categories:
            try:
                cursor.execute(
                    "INSERT INTO categories (name, description) VALUES (%s, %s)",
                    (name, description)
                )
            except pymysql.Error as e:
                if "Duplicate entry" in str(e):
                    print(f"  Category '{name}' already exists, skipping...")
                else:
                    raise
        conn.commit()
        print(f"  ✓ Inserted {len(categories)} categories")
        
        # 2. Add Admin User
        print("\n2. Adding Admin User...")
        admin_email = "admin@amazon.com"
        admin_password = hash_password("admin123")
        
        try:
            cursor.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
                (admin_email, admin_password, 'admin')
            )
            conn.commit()
            print(f"  ✓ Admin user created: {admin_email}")
        except pymysql.Error as e:
            if "Duplicate entry" in str(e):
                print(f"  Admin user already exists, skipping...")
            else:
                raise
        
        # 3. Add Seller Users
        print("\n3. Adding Seller Users...")
        sellers_data = [
            {
                "email": "seller1@amazon.com",
                "password": "seller123",
                "business_name": "Tech Haven",
                "owner_name": "Rajesh Kumar",
                "phone": "9876543210",
                "address": "123 Electronics Street",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "gst_number": "18AABCT1234A1Z0",
                "bank_account": "1234567890",
                "ifsc_code": "SBIN0001234"
            },
            {
                "email": "seller2@amazon.com",
                "password": "seller123",
                "business_name": "Fashion Plus",
                "owner_name": "Priya Singh",
                "phone": "9876543211",
                "address": "456 Fashion Road",
                "city": "Delhi",
                "state": "Delhi",
                "pincode": "110001",
                "gst_number": "07AABCT5678A1Z0",
                "bank_account": "0987654321",
                "ifsc_code": "HDFC0000001"
            },
            {
                "email": "seller3@amazon.com",
                "password": "seller123",
                "business_name": "Book World",
                "owner_name": "Amit Patel",
                "phone": "9876543212",
                "address": "789 Literature Lane",
                "city": "Bangalore",
                "state": "Karnataka",
                "pincode": "560001",
                "gst_number": "29AABCT9012A1Z0",
                "bank_account": "1122334455",
                "ifsc_code": "ICIC0000002"
            }
        ]
        
        seller_ids = []
        for seller in sellers_data:
            try:
                password_hash = hash_password(seller["password"])
                cursor.execute(
                    "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
                    (seller["email"], password_hash, 'seller')
                )
                user_id = cursor.lastrowid
                
                cursor.execute(
                    """INSERT INTO sellers 
                    (user_id, business_name, owner_name, phone, address, city, state, pincode, gst_number, bank_account, ifsc_code, is_approved) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (user_id, seller["business_name"], seller["owner_name"], seller["phone"], 
                     seller["address"], seller["city"], seller["state"], seller["pincode"], 
                     seller["gst_number"], seller["bank_account"], seller["ifsc_code"], True)
                )
                seller_ids.append(cursor.lastrowid)
                conn.commit()
                print(f"  ✓ Seller created: {seller['business_name']}")
            except pymysql.Error as e:
                if "Duplicate entry" in str(e):
                    print(f"  Seller '{seller['email']}' already exists, skipping...")
                else:
                    raise
        
        # 4. Add Customer Users
        print("\n4. Adding Customer Users...")
        customers_data = [
            {
                "email": "customer1@gmail.com",
                "password": "customer123",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "9123456789",
                "address": "123 Main Street, Apt 4B",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400002"
            },
            {
                "email": "customer2@gmail.com",
                "password": "customer123",
                "first_name": "Sarah",
                "last_name": "Khan",
                "phone": "9123456790",
                "address": "456 Second Avenue",
                "city": "Delhi",
                "state": "Delhi",
                "pincode": "110002"
            },
            {
                "email": "customer3@gmail.com",
                "password": "customer123",
                "first_name": "Mike",
                "last_name": "Johnson",
                "phone": "9123456791",
                "address": "789 Third Road",
                "city": "Bangalore",
                "state": "Karnataka",
                "pincode": "560002"
            },
            {
                "email": "customer4@gmail.com",
                "password": "customer123",
                "first_name": "Emma",
                "last_name": "Wilson",
                "phone": "9123456792",
                "address": "321 Fourth Lane",
                "city": "Pune",
                "state": "Maharashtra",
                "pincode": "411002"
            },
            {
                "email": "customer5@gmail.com",
                "password": "customer123",
                "first_name": "David",
                "last_name": "Brown",
                "phone": "9123456793",
                "address": "654 Fifth Street",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "pincode": "600002"
            }
        ]
        
        customer_ids = []
        for customer in customers_data:
            try:
                password_hash = hash_password(customer["password"])
                cursor.execute(
                    "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
                    (customer["email"], password_hash, 'customer')
                )
                user_id = cursor.lastrowid
                
                cursor.execute(
                    """INSERT INTO customers 
                    (user_id, first_name, last_name, phone, address, city, state, pincode) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (user_id, customer["first_name"], customer["last_name"], customer["phone"],
                     customer["address"], customer["city"], customer["state"], customer["pincode"])
                )
                customer_ids.append(cursor.lastrowid)
                conn.commit()
                print(f"  ✓ Customer created: {customer['first_name']} {customer['last_name']}")
            except pymysql.Error as e:
                if "Duplicate entry" in str(e):
                    print(f"  Customer '{customer['email']}' already exists, skipping...")
                else:
                    raise
        
        # 5. Add Products
        print("\n5. Adding Products...")
        products_data = [
            # Electronics (seller 1)
            {"name": "Wireless Bluetooth Headphones", "category_id": 1, "seller_id": 1, "price": 2999, "discount_price": 2499, "quantity": 50, "sku": "WBH001", "brand": "SoundMax", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&h=500&fit=crop"},
            {"name": "USB-C Fast Charger", "category_id": 1, "seller_id": 1, "price": 899, "discount_price": 699, "quantity": 100, "sku": "UFC001", "brand": "PowerTech", "image": "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=500&h=500&fit=crop"},
            {"name": "Portable Power Bank 20000mAh", "category_id": 1, "seller_id": 1, "price": 1499, "discount_price": 1199, "quantity": 75, "sku": "PPB001", "brand": "EnergyMax", "image": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500&h=500&fit=crop"},
            {"name": "4K Webcam", "category_id": 1, "seller_id": 1, "price": 3999, "discount_price": 3499, "quantity": 30, "sku": "WEB001", "brand": "VisualPro", "image": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500&h=500&fit=crop"},
            
            # Fashion (seller 2)
            {"name": "Men's Cotton T-Shirt", "category_id": 2, "seller_id": 2, "price": 499, "discount_price": 399, "quantity": 200, "sku": "MTS001", "brand": "ComfortWear", "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&h=500&fit=crop"},
            {"name": "Women's Casual Jeans", "category_id": 2, "seller_id": 2, "price": 1299, "discount_price": 999, "quantity": 150, "sku": "WCJ001", "brand": "FashionPlus", "image": "https://images.unsplash.com/photo-1542272604-787c62d465d1?w=500&h=500&fit=crop"},
            {"name": "Sports Running Shoes", "category_id": 2, "seller_id": 2, "price": 2499, "discount_price": 1999, "quantity": 100, "sku": "SRS001", "brand": "AthleticGear", "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&h=500&fit=crop"},
            {"name": "Summer Collection Dress", "category_id": 2, "seller_id": 2, "price": 1599, "discount_price": 1299, "quantity": 80, "sku": "SCD001", "brand": "ElegantStyle", "image": "https://images.unsplash.com/photo-1595777707802-a9f1dd37d6b0?w=500&h=500&fit=crop"},
            
            # Books (seller 3)
            {"name": "Python Programming Guide", "category_id": 3, "seller_id": 3, "price": 599, "discount_price": 499, "quantity": 120, "sku": "PPG001", "brand": "TechBooks", "image": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500&h=500&fit=crop"},
            {"name": "Web Development Mastery", "category_id": 3, "seller_id": 3, "price": 799, "discount_price": 649, "quantity": 90, "sku": "WDM001", "brand": "DevPress", "image": "https://images.unsplash.com/photo-1507842217343-583f20270319?w=500&h=500&fit=crop"},
            {"name": "Business Strategy Guide", "category_id": 3, "seller_id": 3, "price": 699, "discount_price": 579, "quantity": 110, "sku": "BSG001", "brand": "BusinessBooks", "image": "https://images.unsplash.com/photo-1552820728-8ac41f1ce891?w=500&h=500&fit=crop"},
            {"name": "Fiction Bestseller", "category_id": 3, "seller_id": 3, "price": 399, "discount_price": 299, "quantity": 150, "sku": "FBS001", "brand": "StoryPress", "image": "https://images.unsplash.com/photo-1543002588-d83cedbc4bac?w=500&h=500&fit=crop"},
        ]
        
        product_ids = []
        for product in products_data:
            try:
                cursor.execute(
                    """INSERT INTO products 
                    (seller_id, category_id, name, price, discount_price, quantity, sku, brand, image_url, is_active) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (product["seller_id"], product["category_id"], product["name"], product["price"],
                     product["discount_price"], product["quantity"], product["sku"], product["brand"], 
                     product["image"], True)
                )
                product_ids.append(cursor.lastrowid)
            except pymysql.Error as e:
                if "Duplicate entry" in str(e):
                    print(f"  Product SKU '{product['sku']}' already exists, skipping...")
                else:
                    raise
        conn.commit()
        print(f"  ✓ Inserted {len(product_ids)} products")
        
        # 6. Add Orders
        print("\n6. Adding Orders...")
        if customer_ids and product_ids and seller_ids:
            for i in range(5):
                customer_id = random.choice(customer_ids)
                product_id = random.choice(product_ids)
                seller_id = random.choice(seller_ids)
                quantity = random.randint(1, 3)
                
                # Get product price
                cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
                result = cursor.fetchone()
                product_price = result['price']
                
                total_amount = product_price * quantity
                order_number = f"ORD{datetime.now().strftime('%Y%m%d')}{1000 + i}"
                
                try:
                    cursor.execute(
                        """INSERT INTO orders 
                        (customer_id, order_number, total_amount, shipping_address, payment_status, order_status) 
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                        (customer_id, order_number, total_amount, "123 Delivery Address", "completed", "shipped")
                    )
                    order_id = cursor.lastrowid
                    
                    # Add order items
                    cursor.execute(
                        """INSERT INTO order_items 
                        (order_id, product_id, seller_id, quantity, price, total, status) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (order_id, product_id, seller_id, quantity, product_price, total_amount, "shipped")
                    )
                    
                    # Add payment
                    cursor.execute(
                        """INSERT INTO payments 
                        (order_id, amount, status) 
                        VALUES (%s, %s, %s)""",
                        (order_id, total_amount, "captured")
                    )
                    
                    conn.commit()
                    print(f"  ✓ Order created: {order_number}")
                except pymysql.Error as e:
                    print(f"  Error creating order: {e}")
        
        print("\n✓ Database seeding completed successfully!")
        print("\nSample Login Credentials:")
        print("  Admin: admin@amazon.com / admin123")
        print("  Seller 1: seller1@amazon.com / seller123 (Tech Haven)")
        print("  Seller 2: seller2@amazon.com / seller123 (Fashion Plus)")
        print("  Seller 3: seller3@amazon.com / seller123 (Book World)")
        print("  Customer 1: customer1@gmail.com / customer123 (John Doe)")
        print("  Customer 2: customer2@gmail.com / customer123 (Sarah Khan)")
        print("  Customer 3: customer3@gmail.com / customer123 (Mike Johnson)")
        print("  Customer 4: customer4@gmail.com / customer123 (Emma Wilson)")
        print("  Customer 5: customer5@gmail.com / customer123 (David Brown)")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_data()
