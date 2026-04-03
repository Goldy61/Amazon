# 🚚 Delivery System with OTP Verification

## Overview

Complete delivery management system with OTP verification for secure order delivery. Delivery personnel can verify deliveries using customer OTP, and both customer and seller receive confirmation emails upon successful delivery.

## Features Implemented

✅ Delivery personnel role and authentication  
✅ Delivery dashboard with order assignments  
✅ OTP generation for delivery verification  
✅ OTP-based delivery confirmation  
✅ Automatic email notifications to customer and seller  
✅ Delivery tracking and history  
✅ Order status updates  
✅ Secure verification process  

## Database Setup

### 1. Run Migration

```bash
mysql -u root -p amazon_db < database/add_delivery_system.sql
```

This creates:
- `delivery_personnel` table
- `delivery_tracking` table
- Adds delivery fields to `orders` table
- Creates 2 sample delivery accounts
- Creates `active_deliveries` view

### 2. Sample Delivery Accounts

| Email | Password | Name | Vehicle |
|-------|----------|------|---------|
| delivery1@shophub.com | delivery123 | Rajesh Kumar | Bike MH-01-AB-1234 |
| delivery2@shophub.com | delivery123 | Amit Sharma | Bike MH-01-CD-5678 |

## How It Works

### Workflow

1. **Order Placed** → Customer places order
2. **Order Shipped** → Seller marks order as shipped
3. **Assign Delivery** → Admin assigns order to delivery personnel
4. **Generate OTP** → Delivery person generates 6-digit OTP
5. **Out for Delivery** → Status automatically updated
6. **Customer Receives OTP** → Customer gets OTP (via SMS/call/app)
7. **Delivery Verification** → Delivery person asks customer for OTP
8. **Enter OTP** → Delivery person enters OTP in app
9. **Verify** → System verifies OTP
10. **Delivery Complete** → Order marked as delivered
11. **Email Notifications** → Customer and seller receive confirmation emails

### OTP Generation

```python
# 6-digit random OTP
OTP: 123456

# Stored in orders table
delivery_otp: "123456"
delivery_otp_generated_at: 2026-03-05 18:00:00
```

### OTP Verification

- Delivery person enters OTP from customer
- System validates OTP against database
- If valid: Order marked as delivered
- If invalid: Error message shown
- Emails sent automatically on success

## For Delivery Personnel

### Login

1. Go to login page
2. Enter email: `delivery1@shophub.com`
3. Enter password: `delivery123`
4. Verify OTP sent to email
5. Redirected to delivery dashboard

### Dashboard

- View assigned orders
- See today's deliveries count
- Check pending deliveries
- View total deliveries completed
- Generate OTP for orders
- Quick access to verify delivery

### Verify Delivery

1. Click "Verify" button on order
2. View order and customer details
3. Ask customer for 6-digit OTP
4. Enter OTP in verification form
5. Click "Verify & Complete Delivery"
6. Success! Order marked as delivered

### Generate OTP

1. Click "Generate" button next to order
2. OTP displayed in popup
3. Share OTP with customer (call/SMS)
4. OTP also visible in dashboard
5. Customer provides OTP at delivery

## For Admins

### Assign Delivery Personnel

```sql
-- Assign order to delivery person
UPDATE orders 
SET delivery_person_id = 1,  -- Delivery person ID
    status = 'shipped'
WHERE id = 123;  -- Order ID
```

### View Active Deliveries

```sql
SELECT * FROM active_deliveries;
```

### Add New Delivery Personnel

```sql
-- 1. Create user account
INSERT INTO users (email, password, role) VALUES
('newdelivery@shophub.com', 'hashed_password', 'delivery');

-- 2. Create delivery personnel profile
INSERT INTO delivery_personnel (user_id, full_name, phone, vehicle_type, vehicle_number) VALUES
((SELECT id FROM users WHERE email = 'newdelivery@shophub.com'), 
 'John Doe', '9876543210', 'Bike', 'MH-01-XY-9999');
```

## For Customers

### Receiving Delivery

1. Order status changes to "Out for Delivery"
2. Delivery person calls/messages with OTP
3. Customer notes down the 6-digit OTP
4. When delivery person arrives, provide OTP
5. Delivery person verifies OTP
6. Receive confirmation email
7. Order marked as delivered

### Delivery Confirmation Email

Customer receives email with:
- Order number
- Delivery confirmation
- Order details
- Thank you message
- Support contact

## For Sellers

### Delivery Notification

Seller receives email when:
- Order is delivered to customer
- Includes order number
- Delivery confirmation
- Payment processing info

## API Endpoints

### Generate OTP

```
POST /delivery/generate_otp/<order_id>

Response:
{
    "success": true,
    "message": "OTP generated successfully",
    "otp": "123456"
}
```

### Verify Delivery

```
POST /delivery/verify/<order_id>
Form Data: otp=123456

Success: Redirects to dashboard with success message
Error: Shows error message
```

### Update Delivery Status

```
POST /delivery/update_status/<order_id>
JSON: {
    "status": "in_transit",
    "notes": "On the way"
}

Response:
{
    "success": true,
    "message": "Status updated successfully"
}
```

## Database Schema

### delivery_personnel Table

```sql
- id: Primary key
- user_id: Reference to users table
- full_name: Delivery person name
- phone: Contact number
- vehicle_type: Bike/Car/Van
- vehicle_number: Vehicle registration
- is_active: Active status
- created_at: Registration date
```

### orders Table (New Fields)

```sql
- delivery_otp: 6-digit OTP (VARCHAR(6))
- delivery_otp_generated_at: OTP generation timestamp
- delivery_person_id: Assigned delivery person
- delivered_at: Delivery completion timestamp
```

### delivery_tracking Table

```sql
- id: Primary key
- order_id: Reference to order
- delivery_person_id: Delivery person
- status: assigned/picked_up/in_transit/delivered/failed
- notes: Additional notes
- location: Current location
- updated_at: Last update time
```

## Security Features

- OTP is 6-digit random number
- OTP stored securely in database
- OTP required for delivery completion
- Only assigned delivery person can verify
- Delivery person authentication required
- Email confirmations for audit trail
- Delivery tracking for accountability

## Email Templates

### Customer Delivery Confirmation

- Subject: "✅ Order Delivered - [ORDER_NUMBER]"
- Content: Delivery confirmation, order details, thank you message
- Template: `templates/emails/delivery_confirmation.html`

### Seller Delivery Notification

- Subject: "📦 Order Delivered - [ORDER_NUMBER]"
- Content: Delivery confirmation, payment info
- Template: `templates/emails/delivery_confirmation.html`

## Testing

### Test Delivery Flow

1. Login as admin
2. Assign order to delivery person:
   ```sql
   UPDATE orders SET delivery_person_id = 1, status = 'shipped' WHERE id = 1;
   ```
3. Login as delivery person (delivery1@shophub.com)
4. Go to dashboard
5. Click "Generate" OTP for order
6. Note the OTP (e.g., 123456)
7. Click "Verify" button
8. Enter OTP
9. Click "Verify & Complete Delivery"
10. Check emails sent to customer and seller

### Test OTP Validation

- Valid OTP: Order marked as delivered
- Invalid OTP: Error message shown
- No OTP generated: Error message
- Wrong delivery person: Access denied

## Troubleshooting

### OTP Not Generated

- Check if order is assigned to delivery person
- Verify order status is 'shipped' or 'out_for_delivery'
- Check database connection

### Email Not Sent

- Verify email configuration in `.env`
- Check email service logs
- Ensure customer/seller email exists

### Delivery Person Can't Login

- Verify account exists in `users` table
- Check role is set to 'delivery'
- Verify profile exists in `delivery_personnel` table

## Files Created

1. `database/add_delivery_system.sql` - Database schema
2. `routes/delivery.py` - Delivery routes and logic
3. `templates/delivery/dashboard.html` - Delivery dashboard
4. `templates/delivery/verify.html` - OTP verification page
5. `templates/delivery/orders.html` - Delivery history
6. `templates/emails/delivery_confirmation.html` - Email template
7. `services/email_service.py` - Added delivery email function

## Future Enhancements

- [ ] Real-time GPS tracking
- [ ] SMS OTP delivery
- [ ] Customer app for OTP display
- [ ] Delivery route optimization
- [ ] Proof of delivery (photo/signature)
- [ ] Delivery time slots
- [ ] Customer rating for delivery
- [ ] Delivery analytics dashboard

## Support

For issues or questions:
- Check application logs
- Verify database migration completed
- Test with sample delivery accounts
- Contact support team

---

**Implementation Date**: March 5, 2026  
**Status**: Production Ready ✅  
**Version**: 1.0
