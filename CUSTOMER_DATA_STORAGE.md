# Customer Data Storage in Food Delivery System

## 🏗️ **Customer Data Architecture Overview**

Customer data in this food delivery system is distributed across multiple services following a **domain-driven design** approach. Here's where and how customer data is stored:

---

## 📍 **Primary Customer Data Storage**

### **1. Auth Service - Core Customer Information**
**Location**: `auth-service/models/user.py`

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(Enum("CUSTOMER", "RESTAURANT", "DRIVER", "ADMIN", name="user_role"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**What's Stored Here:**
- ✅ **Customer Identity**: ID, email, name
- ✅ **Authentication**: Hashed password, JWT tokens
- ✅ **Authorization**: Role (CUSTOMER, RESTAURANT, DRIVER, ADMIN)
- ✅ **Account Status**: Active/inactive status
- ✅ **Registration Date**: When customer joined

**Why Auth Service:**
- **Single Source of Truth**: All user authentication data
- **Security**: Centralized password management
- **Authorization**: Role-based access control
- **JWT Management**: Token generation and validation

---

## 📦 **Customer Order Data Storage**

### **2. Order Service - Customer Order History**
**Location**: `order-service/database.py`

```python
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))  # References Auth Service
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    delivery_address = Column(String)
    delivery_latitude = Column(Float)
    delivery_longitude = Column(Float)
    total_amount = Column(Float)
    status = Column(Enum("PENDING_PAYMENT", "CONFIRMED", "ACCEPTED", ...))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**What's Stored Here:**
- ✅ **Order History**: All orders placed by customer
- ✅ **Order Status**: Current status of each order
- ✅ **Delivery Information**: Address, coordinates
- ✅ **Order Items**: What customer ordered
- ✅ **Timestamps**: When orders were created/updated

**Why Order Service:**
- **Order Management**: Complete order lifecycle
- **Status Tracking**: Real-time order status
- **History**: Customer order history
- **Business Logic**: Order validation and processing

---

## 💳 **Customer Payment Data Storage**

### **3. Payment Service - Customer Payment History**
**Location**: `payment-service/database.py`

```python
class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    amount = Column(Float)
    payment_method = Column(String)
    status = Column(Enum("PENDING", "SUCCEEDED", "FAILED", "REFUNDED"))
    transaction_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
```

**What's Stored Here:**
- ✅ **Payment History**: All payment transactions
- ✅ **Payment Methods**: Credit card, digital wallet, etc.
- ✅ **Transaction Status**: Success, failure, refund status
- ✅ **Financial Records**: Amount, transaction IDs
- ✅ **Refund History**: Refunded payments

**Why Payment Service:**
- **Financial Security**: Isolated payment data
- **Compliance**: PCI DSS requirements
- **Audit Trail**: Complete payment history
- **Refund Management**: Payment reversals

---

## 📊 **Customer Analytics Data Storage**

### **4. Reporting Service - Customer Analytics**
**Location**: `reporting-service/database.py`

```python
class CustomerAnalytics(Base):
    __tablename__ = "customer_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    last_order_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrderAnalytics(Base):
    __tablename__ = "order_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    customer_id = Column(Integer, index=True)
    restaurant_id = Column(Integer, index=True)
    driver_id = Column(Integer, index=True)
    total_amount = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
```

**What's Stored Here:**
- ✅ **Customer Metrics**: Total orders, spending, frequency
- ✅ **Behavioral Data**: Order patterns, preferences
- ✅ **Performance Analytics**: Customer lifetime value
- ✅ **Trend Analysis**: Order history trends
- ✅ **Business Intelligence**: Customer insights

**Why Reporting Service:**
- **Analytics**: Customer behavior analysis
- **Business Intelligence**: Data-driven decisions
- **Performance Metrics**: Customer value tracking
- **Reporting**: Customer reports and insights

---

## 🔄 **Customer Data Flow Across Services**

### **Data Flow Diagram:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth Service  │    │  Order Service  │    │Payment Service  │
│                 │    │                 │    │                 │
│ • User Profile  │◄──►│ • Order History │◄──►│ • Payment Data  │
│ • Authentication│    │ • Order Status  │    │ • Transaction   │
│ • Authorization │    │ • Delivery Info │    │ • Refund Data   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Reporting Service                            │
│                                                                 │
│ • Customer Analytics                                            │
│ • Order Analytics                                               │
│ • Payment Analytics                                             │
│ • Business Intelligence                                         │
└─────────────────────────────────────────────────────────────────┘
```

### **Customer Data Relationships:**
```sql
-- Customer data is linked across services via customer_id
Auth Service:     users.id = 123
Order Service:     orders.customer_id = 123
Payment Service:   payments.order_id → orders.id → orders.customer_id = 123
Reporting Service: customer_analytics.customer_id = 123
```

---

## 🎯 **Customer Data Access Patterns**

### **1. Customer Profile Management**
```python
# Auth Service - Customer profile
GET /auth/me                    # Get current customer profile
PUT /auth/me                    # Update customer profile
POST /auth/register             # Register new customer
POST /auth/login                # Customer login
```

### **2. Customer Order Management**
```python
# Order Service - Customer orders
GET /orders                     # Get customer's orders
POST /orders                    # Create new order
GET /orders/{order_id}          # Get specific order
PUT /orders/{order_id}/status   # Update order status
```

### **3. Customer Payment History**
```python
# Payment Service - Customer payments
GET /payments                   # Get payment history
POST /payments                  # Process payment
POST /payments/{id}/refund      # Request refund
```

### **4. Customer Analytics**
```python
# Reporting Service - Customer analytics
GET /reports/customer-history/{customer_id}    # Order history
GET /reports/top-customers                     # Top customers
GET /reports/average-order-value               # Customer metrics
```

---

## 🔐 **Customer Data Security & Privacy**

### **Data Protection Measures:**
- ✅ **Authentication**: JWT tokens for secure access
- ✅ **Authorization**: Role-based access control
- ✅ **Data Encryption**: Passwords hashed with bcrypt
- ✅ **Input Validation**: All customer data validated
- ✅ **Audit Trail**: Complete data access logging

### **Privacy Considerations:**
- ✅ **Data Minimization**: Only necessary data stored
- ✅ **Access Control**: Customer can only access their data
- ✅ **Data Retention**: Configurable data retention policies
- ✅ **GDPR Compliance**: Right to access, delete, modify data

---

## 📈 **Customer Data Scalability**

### **Database Design for Scale:**
```sql
-- Optimized indexes for customer queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_customer_analytics_customer_id ON customer_analytics(customer_id);
```

### **Service Scaling:**
- **Auth Service**: Scales with user growth
- **Order Service**: Scales with order volume
- **Payment Service**: Scales with transaction volume
- **Reporting Service**: Scales with analytics queries

---

## 🚀 **Customer Data API Examples**

### **Complete Customer Profile:**
```python
# Get customer profile from Auth Service
customer_profile = auth_service.get_user(customer_id)

# Get customer orders from Order Service
customer_orders = order_service.get_orders(customer_id=customer_id)

# Get customer payments from Payment Service
customer_payments = payment_service.get_payments(customer_id=customer_id)

# Get customer analytics from Reporting Service
customer_analytics = reporting_service.get_customer_analytics(customer_id)
```

### **Customer Data Aggregation:**
```python
# Combine data from multiple services
customer_data = {
    "profile": customer_profile,
    "orders": customer_orders,
    "payments": customer_payments,
    "analytics": customer_analytics
}
```

---

## 🎯 **Summary: Customer Data Storage**

### **Primary Storage:**
- **Auth Service**: Core customer identity and authentication
- **Order Service**: Customer order history and status
- **Payment Service**: Customer payment and transaction data
- **Reporting Service**: Customer analytics and business intelligence

### **Data Relationships:**
- All services reference customer via `customer_id`
- Data is linked through foreign key relationships
- Event-driven updates keep data synchronized

### **Benefits of This Architecture:**
- ✅ **Separation of Concerns**: Each service owns its domain
- ✅ **Scalability**: Services scale independently
- ✅ **Security**: Isolated sensitive data (payments)
- ✅ **Performance**: Optimized queries per service
- ✅ **Maintainability**: Clear data ownership

**Customer data is distributed across services but remains consistent and accessible through well-defined APIs and relationships!** 🍕✨
