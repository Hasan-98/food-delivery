# Auth Service - Postman Testing Guide

## 🚀 **Getting Started**

### **1. Start the Auth Service**
```bash
# Option 1: Use the startup script
./start_auth_service.sh

# Option 2: Manual startup
cd auth-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **2. Verify Service is Running**
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Service Status**: Should return `{"status": "healthy", "service": "auth-service"}`

---

## 📋 **Postman API Endpoints**

### **Base URL**: `http://localhost:8000`

---

## 🔐 **1. User Registration**

### **Endpoint**: `POST /register`
**URL**: `http://localhost:8000/register`

### **Request Body** (JSON):
```json
{
  "email": "customer@example.com",
  "name": "John Doe",
  "password": "password123",
  "role": "CUSTOMER"
}
```

### **Available Roles**:
- `CUSTOMER` - Food delivery customers
- `RESTAURANT` - Restaurant owners
- `DRIVER` - Delivery drivers
- `ADMIN` - System administrators

### **Expected Response** (200 OK):
```json
{
  "id": 1,
  "email": "customer@example.com",
  "name": "John Doe",
  "role": "CUSTOMER",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### **Test Different User Types**:
```json
// Restaurant Owner
{
  "email": "restaurant@example.com",
  "name": "Pizza Palace",
  "password": "password123",
  "role": "RESTAURANT"
}

// Delivery Driver
{
  "email": "driver@example.com",
  "name": "Mike Johnson",
  "password": "password123",
  "role": "DRIVER"
}

// Admin User
{
  "email": "admin@example.com",
  "name": "System Admin",
  "password": "password123",
  "role": "ADMIN"
}
```

---

## 🔑 **2. User Login**

### **Endpoint**: `POST /login`
**URL**: `http://localhost:8000/login`

### **Request Body** (Form Data):
```
username: customer@example.com
password: password123
```

### **Expected Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### **Save the Token**: Copy the `access_token` for use in authenticated requests.

---

## 👤 **3. Get User Profile**

### **Endpoint**: `GET /me`
**URL**: `http://localhost:8000/me`

### **Headers**:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

### **Expected Response** (200 OK):
```json
{
  "id": 1,
  "email": "customer@example.com",
  "name": "John Doe",
  "role": "CUSTOMER",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 👥 **4. Get All Users (Admin Only)**

### **Endpoint**: `GET /users`
**URL**: `http://localhost:8000/users`

### **Headers**:
```
Authorization: Bearer ADMIN_ACCESS_TOKEN_HERE
```

### **Query Parameters** (Optional):
- `skip`: Number of users to skip (default: 0)
- `limit`: Maximum number of users to return (default: 100)

### **Example**: `GET /users?skip=0&limit=10`

### **Expected Response** (200 OK):
```json
[
  {
    "id": 1,
    "email": "customer@example.com",
    "name": "John Doe",
    "role": "CUSTOMER",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "email": "restaurant@example.com",
    "name": "Pizza Palace",
    "role": "RESTAURANT",
    "is_active": true,
    "created_at": "2024-01-15T10:35:00Z"
  }
]
```

---

## 🔍 **5. Get User by ID**

### **Endpoint**: `GET /users/{user_id}`
**URL**: `http://localhost:8000/users/1`

### **Expected Response** (200 OK):
```json
{
  "id": 1,
  "email": "customer@example.com",
  "name": "John Doe",
  "role": "CUSTOMER",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 🏥 **6. Health Check**

### **Endpoint**: `GET /health`
**URL**: `http://localhost:8000/health`

### **Expected Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "auth-service"
}
```

---

## 📚 **7. API Documentation**

### **Endpoint**: `GET /docs`
**URL**: `http://localhost:8000/docs`

### **Description**: Interactive Swagger/OpenAPI documentation
- Visit in browser for interactive API testing
- View all endpoints with request/response examples
- Test endpoints directly from the browser

---

## 🧪 **Testing Scenarios**

### **Scenario 1: Complete User Flow**
1. **Register** a new customer
2. **Login** with the credentials
3. **Get Profile** using the token
4. **Verify** the user data matches

### **Scenario 2: Multiple User Types**
1. Register a **CUSTOMER**
2. Register a **RESTAURANT** owner
3. Register a **DRIVER**
4. Register an **ADMIN**
5. Login with each user type
6. Verify role-based access

### **Scenario 3: Error Handling**
1. Try to register with **duplicate email**
2. Try to login with **wrong password**
3. Try to access `/me` **without token**
4. Try to access `/users` **without admin token**

### **Scenario 4: Token Validation**
1. Login and get token
2. Use token in multiple requests
3. Wait for token expiration (30 minutes)
4. Try to use expired token

---

## 🔧 **Postman Collection Setup**

### **Environment Variables**:
Create a Postman environment with:
```
base_url: http://localhost:8000
customer_token: (will be set after login)
restaurant_token: (will be set after login)
driver_token: (will be set after login)
admin_token: (will be set after login)
```

### **Pre-request Scripts**:
```javascript
// Set authorization header if token exists
if (pm.environment.get("customer_token")) {
    pm.request.headers.add({
        key: "Authorization",
        value: "Bearer " + pm.environment.get("customer_token")
    });
}
```

### **Test Scripts**:
```javascript
// Save token after login
if (pm.response.code === 200) {
    const response = pm.response.json();
    if (response.access_token) {
        pm.environment.set("customer_token", response.access_token);
    }
}
```

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: Service Not Starting**
**Error**: `Connection refused`
**Solution**: 
- Check if service is running: `curl http://localhost:8000/health`
- Restart service: `./start_auth_service.sh`

### **Issue 2: Database Connection Error**
**Error**: `Database connection failed`
**Solution**:
- Ensure PostgreSQL is running
- Check database URL in `.env` file
- Verify database credentials

### **Issue 3: Token Validation Error**
**Error**: `401 Unauthorized`
**Solution**:
- Check if token is correctly formatted: `Bearer <token>`
- Verify token hasn't expired
- Re-login to get fresh token

### **Issue 4: Role-based Access Error**
**Error**: `403 Forbidden`
**Solution**:
- Ensure user has correct role
- Use admin token for admin-only endpoints
- Check user permissions

---

## 🎯 **Success Criteria**

### **✅ All Tests Should Pass**:
1. Service health check returns 200
2. User registration works for all roles
3. User login returns valid JWT token
4. Profile retrieval works with valid token
5. Role-based access control works
6. Error handling works correctly
7. API documentation is accessible

### **📊 Expected Results**:
- **Registration**: 200 OK with user data
- **Login**: 200 OK with JWT token
- **Profile**: 200 OK with user profile
- **Health**: 200 OK with service status
- **Errors**: Appropriate HTTP status codes

---

## 🚀 **Next Steps**

Once Auth Service is working:
1. **Test all endpoints** with Postman
2. **Verify JWT tokens** work correctly
3. **Test role-based access** control
4. **Move to next service** (Catalog Service)
5. **Build complete workflow** across services

**The Auth Service is the foundation - once it's working, all other services can be tested!** 🍕✨
