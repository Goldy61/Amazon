# 🗄️ Complete Database Setup Guide

## One-Command Setup

Run this single command to set up the entire database:

```bash
mysql -u root -p < database/complete_database_setup.sql
```

Enter your MySQL root password when prompted.

## What This Creates

### ✅ Complete E-Commerce System

**Core Tables:**
- users (admin, seller, customer, delivery roles)
- customers
- sellers
- categories
- products
- cart
- orders
- order_items
- payments

**Coupon System:**
- coupons
- coupon_usage
- active_coupons view

**Delivery System:**
- delivery_personnel
- delivery_tracking
- active_deliveries view

**Additional:**
- email_logs
- login_otps
- chat_logs

### 📦 Sample Data Included

**Admin Account:**
- Email: `admin@shophub.com`
- Password: `admin123`

**Delivery Accounts:**
- Email: `delivery1@shophub.com` / Password: `delivery123`
- Email: `delivery2@shophub.com` / Password: `delivery123`

**Categories:**
- Electronics, Clothing, Books, Home & Kitchen, Sports, Beauty, Toys, Automotive

**Sample Coupons:**
- WELCOME20 - 20% off (min ₹500)
- SAVE100 - ₹100 off (min ₹1000)
- MEGA50 - 50% off (min ₹2000)
- FLASH15 - 15% off (min ₹300)
- FIRST500 - ₹500 off (min ₹2500)

## Verification

After running the setup, verify everything is created:

```sql
-- Login to MySQL
mysql -u root -p amazon_db

-- Check tables
SHOW TABLES;

-- Check admin account
SELECT email, role FROM users WHERE role = 'admin';

-- Check delivery accounts
SELECT email, role FROM users WHERE role = 'delivery';

-- Check categories
SELECT name FROM categories;

-- Check coupons
SELECT code, description FROM coupons;

-- Check delivery personnel
SELECT full_name, phone FROM delivery_personnel;
```

Expected output:
- 20+ tables created
- 1 admin account
- 2 delivery accounts
- 8 categories
- 5 sample coupons
- 2 delivery personnel

## Fresh Start (Reset Database)

If you need to start over:

```sql
-- WARNING: This will delete all data!
DROP DATABASE IF EXISTS amazon_db;
```

Then run the setup again:
```bash
mysql -u root -p < database/complete_database_setup.sql
```

## Individual Migrations (Alternative)

If you prefer to run migrations separately:

```bash
# 1. Main schema
mysql -u root -p amazon_db < database/schema.sql

# 2. Coupon system
mysql -u root -p amazon_db < database/add_coupons.sql

# 3. Delivery system
mysql -u root -p amazon_db < database/add_delivery_system.sql
```

## Troubleshooting

### Error: "Database exists"
The script uses `CREATE DATABASE IF NOT EXISTS`, so it's safe to run multiple times.

### Error: "Table already exists"
The script uses `CREATE TABLE IF NOT EXISTS`, so it's safe to run multiple times.

### Error: "Duplicate entry"
Sample data uses `INSERT IGNORE`, so duplicates are skipped automatically.

### Error: "Access denied"
Make sure you're using the correct MySQL root password.

### Error: "Unknown database"
The script creates the database automatically. Just run it.

## What's Different from Individual Files?

This complete setup file:
- ✅ Creates everything in one go
- ✅ Handles dependencies automatically
- ✅ Includes all features (coupons + delivery)
- ✅ Adds sample data
- ✅ Creates views
- ✅ Shows success message

Individual files:
- ⚠️ Must be run in order
- ⚠️ May have dependency issues
- ⚠️ Requires multiple commands

## Next Steps

After database setup:

1. **Configure Environment**
   ```bash
   # Edit .env file
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=amazon_db
   ```

2. **Start Application**
   ```bash
   python run_app.py
   ```

3. **Login as Admin**
   - Go to: http://localhost:5000/login
   - Email: admin@shophub.com
   - Password: admin123

4. **Test Delivery System**
   - Login as: delivery1@shophub.com / delivery123

5. **Test Coupons**
   - Use code: WELCOME20 at checkout

## Database Structure

```
amazon_db/
├── Core Tables (9)
│   ├── users
│   ├── customers
│   ├── sellers
│   ├── categories
│   ├── products
│   ├── cart
│   ├── orders
│   ├── order_items
│   └── payments
│
├── Coupon System (2)
│   ├── coupons
│   └── coupon_usage
│
├── Delivery System (2)
│   ├── delivery_personnel
│   └── delivery_tracking
│
├── Additional (3)
│   ├── email_logs
│   ├── login_otps
│   └── chat_logs
│
└── Views (2)
    ├── active_coupons
    └── active_deliveries
```

## File Comparison

| File | Purpose | When to Use |
|------|---------|-------------|
| `complete_database_setup.sql` | Everything in one file | ⭐ First time setup |
| `schema.sql` | Main tables only | Existing database |
| `add_coupons.sql` | Add coupon system | After main schema |
| `add_delivery_system.sql` | Add delivery system | After main schema |

## Success Indicators

After running the setup, you should see:

```
✅ Database setup completed successfully!
Database: amazon_db
Tables created: 20+
Sample data inserted

Default Accounts:
Admin: admin@shophub.com / admin123
Delivery 1: delivery1@shophub.com / delivery123
Delivery 2: delivery2@shophub.com / delivery123

Sample Coupons: WELCOME20, SAVE100, MEGA50, FLASH15, FIRST500

🚀 Ready to start the application!
```

---

**Ready to go!** Your complete ShopHub database is set up and ready to use. 🎉
