# 🚀 Quick Start Guide - Food Delivery System

## 🎯 **Easiest Way: Use Docker Compose**

### **Start Everything at Once:**
```bash
# Start all services with Docker
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### **Service URLs (Docker):**
- **Auth Service**: http://localhost:8001
- **Catalog Service**: http://localhost:8002  
- **Order Service**: http://localhost:8003
- **Payment Service**: http://localhost:8004
- **Restaurant Service**: http://localhost:8005
- **Dispatch Service**: http://localhost:8006
- **Notification Service**: http://localhost:8007
- **Reporting Service**: http://localhost:8008

---

## 🔧 **Manual Setup (If Docker Not Available)**

### **Prerequisites:**
```bash
# Start PostgreSQL
sudo systemctl start postgresql
createdb food_delivery

# Start RabbitMQ
sudo systemctl start rabbitmq-server
```

### **Start Services One by One:**

#### **1. Auth Service (Working!)**
```bash
cd auth-service
source venv/bin/activate
python main.py
```
- **URL**: http://localhost:8000
- **Status**: ✅ Working

#### **2. Other Services (Start as needed)**
```bash
# For each service:
cd catalog-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## 🧪 **Testing the System**

### **1. Test Auth Service (Currently Working)**
```bash
# Health Check
curl http://localhost:8000/health

# API Documentation
# Visit: http://localhost:8000/docs
```

### **2. Test with Postman**
- **Base URL**: http://localhost:8000
- **Register User**: POST /register
- **Login**: POST /login
- **Get Profile**: GET /me (with token)

### **3. Test Other Services**
```bash
# Check if services are running
curl http://localhost:8002/health  # Catalog
curl http://localhost:8003/health  # Order
# ... etc
```

---

## 🎯 **Recommended Approach**

### **Option 1: Docker Compose (Best)**
```bash
docker compose up -d
```
- ✅ Handles all dependencies
- ✅ No import issues
- ✅ Easy to manage
- ✅ Production-ready

### **Option 2: Individual Services (For Development)**
```bash
# Start Auth Service (already working)
cd auth-service && source venv/bin/activate && python main.py

# Start other services as needed
cd catalog-service && python main.py
cd order-service && python main.py
# ... etc
```

---

## 🔍 **Current Status**

### **✅ Working:**
- **Auth Service**: Running on http://localhost:8000
- **Health Check**: Working
- **API Documentation**: Available

### **⚠️ Issues:**
- **Database**: Need PostgreSQL running
- **Other Services**: Import issues (use Docker Compose)

### **🎯 Next Steps:**
1. **Start PostgreSQL** or use Docker Compose
2. **Test Auth Service** with Postman
3. **Start other services** as needed

---

## 📚 **Complete Documentation**

- **HOW_TO_RUN_SERVICES.md** - Detailed service setup
- **POSTMAN_TESTING_GUIDE.md** - API testing guide
- **DESIGN_DECISIONS.md** - Architecture explanations

**The Auth Service is working perfectly - just need the database!** 🍕✨

