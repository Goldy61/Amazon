# 📧 Email Notification Setup Guide

## Overview
This guide will help you set up email notifications for your multi-vendor e-commerce platform using Gmail SMTP and Flask-Mail.

## 🚀 Quick Setup

### 1. Gmail App Password Setup

**Step 1: Enable 2-Factor Authentication**
1. Go to your Google Account settings: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", click "2-Step Verification"
4. Follow the setup process to enable 2FA

**Step 2: Generate App Password**
1. Go back to Security settings
2. Under "Signing in to Google", click "App passwords"
3. Select "Mail" as the app and "Other" as the device
4. Enter "E-Commerce Platform" as the device name
5. Click "Generate"
6. **Copy the 16-character password** (you'll need this for configuration)

### 2. Environment Configuration

**Create/Update your `.env` file:**
```bash
# Copy from .env.example
cp .env.example .env
```

**Edit `.env` file with your email credentials:**
```bash
# Email Configuration (Gmail SMTP)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password

# Other configurations...
SECRET_KEY=your-secret-key-here
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
```

### 3. Test Email Configuration

**Run the test script:**
```bash
python test_email.py
```

## 📋 Email Notification Features

### ✅ Implemented Email Notifications

1. **User Registration**
   - Welcome email with account details
   - Role-specific instructions
   - Next steps guidance

2. **Seller Account Management**
   - Approval notification with dashboard access
   - Rejection notification with feedback
   - Account status updates

3. **Product Management**
   - Product added confirmation
   - Success tips and guidelines
   - Performance tracking info

4. **Order Management**
   - Order placed confirmation
   - Order status updates (confirmed, shipped, delivered)
   - Seller order notifications

5. **Payment Processing**
   - Payment success confirmation
   - Payment failure notifications
   - Transaction details

6. **Password Reset**
   - Secure reset links
   - Security guidelines
   - Account protection tips

### 📧 Email Templates

All email templates are located in `templates/emails/`:
- `base_email.html` - Base template with styling
- `registration_success.html` - Welcome emails
- `seller_approved.html` - Seller approval
- `seller_rejected.html` - Seller rejection
- `product_added.html` - Product confirmation
- `order_placed.html` - Order confirmation
- `payment_success.html` - Payment success
- `payment_failed.html` - Payment failure
- `order_status_update.html` - Status updates
- `seller_order_notification.html` - Seller notifications
- `password_reset.html` - Password reset

## 🔧 Configuration Details

### Flask-Mail Settings
```python
# In config.py
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
```

### Email Service Functions
```python
# Available in services/email_service.py
send_registration_email(email, name, role)
send_seller_approval_email(email, name, business)
send_product_added_email(email, name, product, id)
send_order_placed_email(email, name, order_num, total, id)
send_payment_success_email(email, name, order_num, amount, id)
send_order_status_email(email, name, order_num, status, id)
```

## 🛠️ Troubleshooting

### Common Issues

**1. "Authentication failed" Error**
- Ensure 2FA is enabled on your Gmail account
- Use App Password, not your regular Gmail password
- Check that MAIL_USERNAME and MAIL_PASSWORD are correct in .env

**2. "Connection refused" Error**
- Check your internet connection
- Verify MAIL_SERVER and MAIL_PORT settings
- Ensure firewall isn't blocking SMTP connections

**3. Emails not being sent**
- Check the email logs in database: `SELECT * FROM email_logs ORDER BY created_at DESC`
- Look for error messages in the console output
- Verify recipient email addresses are valid

**4. Emails going to spam**
- Use a professional sender name
- Include unsubscribe links
- Avoid spam trigger words
- Consider using a custom domain

### Debug Mode
Enable debug logging by adding to your app:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Email Logging

All email activities are logged in the `email_logs` table:
- Recipient email
- Subject and type
- Status (sent/failed/pending)
- Error messages
- Timestamps

**View email logs:**
```sql
SELECT * FROM email_logs 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)
ORDER BY created_at DESC;
```

## 🔒 Security Best Practices

1. **Never commit credentials to version control**
2. **Use environment variables for sensitive data**
3. **Regularly rotate app passwords**
4. **Monitor email logs for suspicious activity**
5. **Implement rate limiting for email sending**
6. **Use HTTPS for all email-related endpoints**

## 📈 Performance Optimization

1. **Async Email Sending** (Future Enhancement)
   - Use Celery for background email processing
   - Prevent blocking web requests

2. **Email Templates Caching**
   - Cache compiled templates for better performance

3. **Batch Email Processing**
   - Group similar emails for bulk sending

## 🎯 Testing Email Functionality

### Manual Testing
1. Register a new user account
2. Add a product as a seller
3. Place an order as a customer
4. Update order status as a seller
5. Check your email inbox for notifications

### Automated Testing
```bash
# Run email tests
python -m pytest tests/test_email.py -v
```

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review email logs in the database
3. Verify your Gmail app password setup
4. Test with a different email provider if needed

## 🚀 Production Deployment

For production environments:
1. Use a dedicated email service (SendGrid, Mailgun, AWS SES)
2. Implement proper error handling and retries
3. Set up email monitoring and alerts
4. Configure proper DNS records (SPF, DKIM, DMARC)
5. Use a professional email domain

---

**🎉 Congratulations!** Your e-commerce platform now has a complete email notification system that will keep your users informed and engaged throughout their shopping journey.