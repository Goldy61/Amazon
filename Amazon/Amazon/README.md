# Multi-Vendor E-Commerce Platform

A comprehensive e-commerce platform similar to Amazon/Flipkart where multiple vendors can sell their products with complete email notification system.

## 🚀 Features

### User Roles
- **Admin**: Manage sellers, customers, categories, and monitor platform
- **Seller**: Add products, manage inventory, process orders
- **Customer**: Browse products, add to cart, make purchases

### Core Functionality
- Multi-vendor product marketplace
- Shopping cart and checkout system
- Razorpay payment integration
- Order tracking and management
- Admin dashboard with analytics
- **📧 Complete email notification system**
- Responsive web design with dark/light mode

### 📧 Email Notifications
- **User Registration**: Welcome emails with role-specific instructions
- **Seller Management**: Approval/rejection notifications
- **Product Management**: Product added confirmations
- **Order Management**: Order placed, status updates, delivery notifications
- **Payment Processing**: Success/failure notifications with transaction details
- **Password Reset**: Secure reset links with security guidelines
- **🔐 Login OTP**: Two-factor authentication with email verification codes

## 🛠 Tech Stack
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Python Flask
- **Database**: MySQL
- **Server**: XAMPP (Apache + MySQL)
- **Payment**: Razorpay Gateway
- **Email**: Flask-Mail with Gmail SMTP
- **Image Processing**: Pillow (PIL)

## 📁 Project Structure
```
ecommerce/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── test_setup.py         # Setup verification script
├── test_email.py         # Email testing script
├── SETUP_INSTRUCTIONS.md # Detailed setup guide
├── EMAIL_SETUP_GUIDE.md  # Email configuration guide
├── OTP_LOGIN_GUIDE.md    # OTP login system guide
├── database/
│   └── schema.sql        # Complete database schema
├── services/             # Business logic services
│   ├── __init__.py
│   ├── email_service.py  # Email notification service
│   └── otp_service.py    # OTP verification service
├── routes/               # Route handlers
│   ├── __init__.py
│   ├── auth.py          # Authentication & registration
│   ├── customer.py      # Product browsing & cart
│   ├── checkout.py      # Checkout & payment
│   ├── seller.py        # Seller dashboard & products
│   └── admin.py         # Admin panel & management
├── templates/            # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Homepage
│   ├── auth/            # Login & registration
│   │   ├── login.html
│   │   ├── register.html
│   │   └── verify_otp.html  # OTP verification page
│   ├── customer/        # Product pages & cart
│   ├── seller/          # Seller dashboard
│   ├── admin/           # Admin panel
│   └── emails/          # Email templates
│       ├── base_email.html
│       ├── registration_success.html
│       ├── seller_approved.html
│       ├── product_added.html
│       ├── order_placed.html
│       ├── payment_success.html
│       ├── login_otp.html       # OTP verification email
│       └── ... (more email templates)
├── static/              # Static assets
│   ├── css/style.css    # Custom styles with animations
│   ├── js/main.js       # JavaScript functions
│   ├── images/          # Static images
│   └── uploads/         # User uploaded images
└── .env.example         # Environment variables template
```

## 🔧 Quick Setup

1. **Prerequisites**
   ```bash
   # Install XAMPP and Python 3.7+
   # Get Razorpay account credentials
   # Set up Gmail App Password for email notifications
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   - Start XAMPP (Apache + MySQL)
   - Create database `amazon_db`
   - Import `database/schema.sql`
   - Run: `python update_database_email.py`

4. **Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials:
   # - Razorpay keys
   # - Gmail SMTP credentials
   ```

5. **Email Setup** (See EMAIL_SETUP_GUIDE.md for details)
   ```bash
   # Test email configuration
   python test_email.py
   ```

6. **Run Application**
   ```bash
   python app.py
   ```

7. **Test Setup**
   ```bash
   python test_setup.py
   ```

## 🔐 Default Credentials

**Admin Login:**
- Email: admin@ecommerce.com
- Password: admin123

## 💡 Key Features Implemented

### 📧 Email Notification System
- ✅ User registration welcome emails
- ✅ Seller approval/rejection notifications
- ✅ Product added confirmations
- ✅ Order placed notifications
- ✅ Payment success/failure alerts
- ✅ Order status updates (shipped, delivered)
- ✅ Password reset emails
- ✅ Login OTP verification emails
- ✅ Professional HTML email templates
- ✅ Email logging and tracking

### 🔐 Login Security & OTP System
- ✅ Two-factor authentication with email OTP
- ✅ 6-digit verification codes with 10-minute expiry
- ✅ Professional OTP email templates
- ✅ User-friendly verification interface
- ✅ Automatic OTP cleanup and security
- ✅ Mobile-responsive OTP entry
- ✅ Resend functionality with rate limiting

### Authentication & Security
- ✅ Role-based authentication (Admin/Seller/Customer)
- ✅ Password hashing with bcrypt
- ✅ Session management
- ✅ SQL injection prevention
- ✅ File upload validation

### Seller Features
- ✅ Business registration with approval workflow
- ✅ Product management (CRUD operations)
- ✅ Image upload with automatic resizing
- ✅ Inventory tracking
- ✅ Order management and status updates
- ✅ Sales dashboard with statistics

### Customer Features
- ✅ Product browsing with search and filters
- ✅ Category-based navigation
- ✅ Shopping cart management
- ✅ Secure checkout process
- ✅ Razorpay payment integration
- ✅ Order history and tracking
- ✅ Responsive design for mobile

### Admin Features
- ✅ Comprehensive admin dashboard
- ✅ Seller approval and management
- ✅ Customer management
- ✅ Category management
- ✅ Order monitoring
- ✅ Sales analytics and reporting

### Payment Integration
- ✅ Razorpay payment gateway
- ✅ Multiple payment methods (Cards, UPI, Wallets)
- ✅ Payment verification and security
- ✅ Transaction logging
- ✅ Automatic order status updates

## 📊 Database Schema

Complete MySQL schema with 11 tables:
- `users` - Authentication data
- `customers` - Customer profiles
- `sellers` - Seller business information
- `categories` - Product categories
- `products` - Product catalog
- `cart` - Shopping cart items
- `orders` - Order information
- `order_items` - Individual order items
- `payments` - Payment transactions
- `email_logs` - Email notification tracking
- `login_otps` - OTP verification codes

## 🎨 UI/UX Features

- Modern Bootstrap 5 design
- Responsive layout for all devices
- Intuitive navigation and user flows
- Real-time form validation
- Image preview for uploads
- Loading states and feedback
- Professional admin and seller dashboards

## 🔒 Security Measures

- Password hashing with bcrypt
- Parameterized SQL queries
- File upload restrictions
- Session-based authentication
- Role-based access control
- Input validation and sanitization

## 📱 Responsive Design

- Mobile-first approach
- Bootstrap 5 grid system
- Touch-friendly interfaces
- Optimized images
- Fast loading times

## 🚀 Production Ready

- Environment-based configuration
- Error handling and logging
- Database connection pooling
- Image optimization
- Security best practices
- Scalable architecture

## 📖 Documentation

- Comprehensive setup instructions
- Code comments and documentation
- Database schema documentation
- API endpoint documentation
- Troubleshooting guide

## 🧪 Testing

- Setup verification script
- Manual testing procedures
- Error handling validation
- Payment flow testing
- Security testing guidelines

## 🔄 Future Enhancements

Potential improvements for production:
- Advanced search with Elasticsearch
- Product reviews and ratings
- Wishlist functionality
- Coupon and discount system
- Multi-language support
- API for mobile apps
- Advanced analytics
- Inventory alerts
- SMS notifications
- Push notifications
- Social media integration

## 📞 Support

For setup issues or questions:
1. Run `python test_setup.py` to verify setup
2. Check `SETUP_INSTRUCTIONS.md` for detailed guide
3. Review browser console for JavaScript errors
4. Verify database connections and queries
5. Check Razorpay dashboard for payment issues

---

**Built with ❤️ for learning and development purposes**