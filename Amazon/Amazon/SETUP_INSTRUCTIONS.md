# Multi-Vendor E-Commerce Platform - Setup Instructions

## Prerequisites

1. **XAMPP** - Download and install from https://www.apachefriends.org/
2. **Python 3.7+** - Download from https://www.python.org/
3. **Razorpay Account** - Sign up at https://razorpay.com/

## Step-by-Step Setup

### 1. Start XAMPP Services
- Open XAMPP Control Panel
- Start **Apache** and **MySQL** services
- Ensure both services are running (green status)

### 2. Create Database
- Open phpMyAdmin: http://localhost/phpmyadmin/
- Create a new database named `amazon_db`
- Import the SQL schema:
  - Go to the `amazon_db` database
  - Click on "Import" tab
  - Choose file: `database/schema.sql`
  - Click "Go" to execute

### 3. Install Python Dependencies
```bash
# Navigate to project directory
cd path/to/ecommerce

# Install required packages
pip install -r requirements.txt
```

### 4. Configure Environment Variables
- Copy `.env.example` to `.env`
- Update the following values in `.env`:
  ```
  SECRET_KEY=your-unique-secret-key-here
  RAZORPAY_KEY_ID=your_razorpay_key_id
  RAZORPAY_KEY_SECRET=your_razorpay_key_secret
  ```

### 5. Get Razorpay Credentials
- Login to Razorpay Dashboard
- Go to Settings → API Keys
- Generate API Keys (Test Mode for development)
- Copy Key ID and Key Secret to `.env` file

### 6. Create Upload Directory
```bash
mkdir -p static/uploads/products
```

### 7. Run the Application
```bash
python app.py
```

The application will start on: http://localhost:5000

## Default Login Credentials

### Admin Account
- **Email:** admin@ecommerce.com
- **Password:** admin123

## Testing the Application

### 1. Register as Customer
- Go to http://localhost:5000/register
- Select "Customer" role
- Fill in required details
- Login and browse products

### 2. Register as Seller
- Go to http://localhost:5000/register
- Select "Seller" role
- Fill in business details
- Wait for admin approval

### 3. Admin Functions
- Login as admin
- Approve pending sellers
- Manage categories
- View orders and analytics

## Project Structure

```
ecommerce/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── database/
│   └── schema.sql        # Database schema
├── routes/               # Route handlers
│   ├── auth.py          # Authentication routes
│   ├── customer.py      # Customer routes
│   ├── checkout.py      # Checkout & payment
│   ├── seller.py        # Seller dashboard
│   └── admin.py         # Admin panel
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Homepage
│   ├── auth/            # Authentication pages
│   ├── customer/        # Customer pages
│   ├── seller/          # Seller dashboard
│   └── admin/           # Admin panel
├── static/              # Static files
│   ├── css/
│   │   └── style.css    # Custom styles
│   ├── js/
│   │   └── main.js      # JavaScript functions
│   └── uploads/         # Uploaded images
└── .env                 # Environment variables
```

## Key Features Implemented

### User Management
- ✅ Multi-role authentication (Admin, Seller, Customer)
- ✅ Registration with role-specific fields
- ✅ Password hashing with bcrypt
- ✅ Session management

### Seller Features
- ✅ Seller dashboard with statistics
- ✅ Product management (CRUD operations)
- ✅ Image upload with resizing
- ✅ Order management
- ✅ Order status updates

### Customer Features
- ✅ Product browsing with filters
- ✅ Product search functionality
- ✅ Shopping cart management
- ✅ Checkout process
- ✅ Razorpay payment integration
- ✅ Order history and tracking

### Admin Features
- ✅ Admin dashboard with analytics
- ✅ Seller approval system
- ✅ User management
- ✅ Category management
- ✅ Order monitoring
- ✅ Sales analytics

### Payment Integration
- ✅ Razorpay payment gateway
- ✅ Payment verification
- ✅ Transaction logging
- ✅ Order status updates

## Security Features

- Password hashing with bcrypt
- SQL injection prevention with parameterized queries
- File upload validation
- Session-based authentication
- Role-based access control
- CSRF protection (Flask built-in)

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MySQL is running in XAMPP
   - Check database credentials in `config.py`
   - Verify database `amazon_db` exists

2. **Import Error for Routes**
   - Ensure all route files are in the `routes/` directory
   - Check for syntax errors in route files

3. **Image Upload Issues**
   - Ensure `static/uploads/products/` directory exists
   - Check file permissions
   - Verify file size limits

4. **Razorpay Payment Errors**
   - Verify API keys in `.env` file
   - Use test keys for development
   - Check Razorpay dashboard for transaction logs

### Development Tips

1. **Enable Debug Mode**
   - Set `debug=True` in `app.py` for development
   - Disable in production

2. **Database Changes**
   - After schema changes, restart the application
   - Clear browser cache if needed

3. **Static Files**
   - Use Ctrl+F5 to force refresh CSS/JS changes
   - Check browser developer tools for errors

## Production Deployment

For production deployment:

1. Set `debug=False` in `app.py`
2. Use strong secret keys
3. Use production Razorpay keys
4. Configure proper web server (Apache/Nginx)
5. Set up SSL certificates
6. Configure database backups
7. Set up monitoring and logging

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Flask and Razorpay documentation
3. Check browser developer console for errors
4. Verify database connections and queries