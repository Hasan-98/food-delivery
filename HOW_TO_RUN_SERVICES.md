# How to Run Each Service - Complete Guide

## 🚀 **Quick Start - Run All Services**

### **Option 1: Docker Compose (Recommended)**
```bash
# Start all services at once
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

### **Option 2: Individual Service Setup**
Follow the steps below to run each service individually.

---

## 🔧 **Individual Service Setup**

### **Prerequisites**
- Python 3.8+
- PostgreSQL (running on localhost:5432)
- RabbitMQ (running on localhost:5672)

### **Database Setup**
```bash
# Create database
createdb food_delivery

# Or using psql
psql -U postgres -c "CREATE DATABASE food_delivery;"
```

---

## 🔐 **1. Auth Service**

### **Start Auth Service:**
```bash
cd auth-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **Service Details:**
- **URL**: http://localhost:8000
- **Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Port**: 8000

### **Test with Postman:**
```bash
# Health Check
GET http://localhost:8000/health

# Register User
POST http://localhost:8000/register
{
  "email": "customer@example.com",
  "name": "John Doe",
  "password": "password123",
  "role": "CUSTOMER"
}

# Login
POST http://localhost:8000/login
username=customer@example.com&password=password123
```

---

## 🏪 **2. Catalog Service**

### **Start Catalog Service:**
```bash
cd catalog-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **Service Details:**
- **URL**: http://localhost:8002
- **Health**: http://localhost:8002/health
- **API Docs**: http://localhost:8002/docs
- **Port**: 8002

### **Test with Postman:**
```bash
# Health Check
GET http://localhost:8002/health

# Get Restaurants
GET http://localhost:8002/restaurants

# Get Menu Items
GET http://localhost:8002/restaurants/1/menu
```

---

## 📦 **3. Order Service**

### **Start Order Service:**
```bash
cd order-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **Service Details:**
- **URL**: http://localhost:8003
- **Health**: http://localhost:8003/health
- **API Docs**: http://localhost:8003/docs
- **Port**: 8003

### **Test with Postman:**
```bash
# Health Check
GET http://localhost:8003/health

# Create Order (with auth token)
POST http://localhost:8003/orders
Authorization: Bearer YOUR_TOKEN
{
  "restaurant_id": 1,
  "items": [{"menu_item_id": 1, "quantity": 2}],
  "delivery_address": "123 Main St"
}
```

---

## 💳 **4. Payment Service**

### **Start Payment Service:**
```bash
cd payment-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **Service Details:**
- **URL**: http://localhost:8004
- **Health**: http://localhost:8004/health
- **API Docs**: http://localhost:8004/docs
- **Port**: 8004

---

## 🍽️ **5. Restaurant Service**

### **Start Restaurant Service:**
```bash
cd restaurant-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **Service Details:**
- **URL**: http://localhost:8005
- **Health**: http://localhost:8005/health
- **API Docs**: http://localhost:8005/docs
- **Port**: 8005

---

## 🚗 **6. Dispatch Service**

### **Start Dispatch Service:**
```bash
cd dispatch-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **Service Details:**
- **URL**: http://localhost:8006
- **Health**: http://localhost:8006/health
- **API Docs**: http://localhost:8006/docs
- **Port**: 8006

---

## 📱 **7. Notification Service**

### **Start Notification Service:**
```bash
cd notification-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **Service Details:**
- **URL**: http://localhost:8007
- **Health**: http://localhost:8007/health
- **API Docs**: http://localhost:8007/docs
- **Port**: 8007

---

## 📊 **8. Reporting Service**

### **Start Reporting Service:**
```bash
cd reporting-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### **Service Details:**
- **URL**: http://localhost:8008
- **Health**: http://localhost:8008/health
- **API Docs**: http://localhost:8008/docs
- **Port**: 8008

---

## 🐳 **Docker Compose Setup (All Services)**

### **Start All Services:**
```bash
# Build and start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

### **Service URLs (Docker):**
- Auth Service: http://localhost:8001
- Catalog Service: http://localhost:8002
- Order Service: http://localhost:8003
- Payment Service: http://localhost:8004
- Restaurant Service: http://localhost:8005
- Dispatch Service: http://localhost:8006
- Notification Service: http://localhost:8007
- Reporting Service: http://localhost:8008

### **Infrastructure Services:**
- PostgreSQL: localhost:5432
- RabbitMQ: localhost:5672
- Adminer (DB GUI): http://localhost:8080
- RabbitMQ Management: http://localhost:15672

---

## 🧪 **Testing Each Service**

### **1. Health Check All Services:**
```bash
curl http://localhost:8001/health  # Auth
curl http://localhost:8002/health  # Catalog
curl http://localhost:8003/health  # Order
curl http://localhost:8004/health  # Payment
curl http://localhost:8005/health  # Restaurant
curl http://localhost:8006/health  # Dispatch
curl http://localhost:8007/health  # Notification
curl http://localhost:8008/health  # Reporting
```

### **2. API Documentation:**
- Auth: http://localhost:8001/docs
- Catalog: http://localhost:8002/docs
- Order: http://localhost:8003/docs
- Payment: http://localhost:8004/docs
- Restaurant: http://localhost:8005/docs
- Dispatch: http://localhost:8006/docs
- Notification: http://localhost:8007/docs
- Reporting: http://localhost:8008/docs

---

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **1. Port Already in Use:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 PID
```

#### **2. Database Connection Error:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql
```

#### **3. RabbitMQ Connection Error:**
```bash
# Check RabbitMQ is running
sudo systemctl status rabbitmq-server

# Start RabbitMQ
sudo systemctl start rabbitmq-server
```

#### **4. Virtual Environment Issues:**
```bash
# Remove and recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📋 **Service Dependencies**

### **Start Order:**
1. **PostgreSQL** (Database)
2. **RabbitMQ** (Message Broker)
3. **Auth Service** (Authentication)
4. **Catalog Service** (Restaurants/Menus)
5. **Order Service** (Order Management)
6. **Payment Service** (Payment Processing)
7. **Restaurant Service** (Kitchen Operations)
8. **Dispatch Service** (Driver Management)
9. **Notification Service** (Alerts)
10. **Reporting Service** (Analytics)

### **Service Communication:**
```
Auth Service ← All Services (Authentication)
Catalog Service ← Order Service (Menu Data)
Order Service → Payment Service (Payment Events)
Order Service → Restaurant Service (Order Events)
Restaurant Service → Dispatch Service (Ready Events)
Dispatch Service → Notification Service (Status Updates)
All Services → Reporting Service (Analytics)
```

---

## 🎯 **Quick Test Workflow**

### **1. Start Infrastructure:**
```bash
# Start PostgreSQL and RabbitMQ
sudo systemctl start postgresql
sudo systemctl start rabbitmq-server
```

### **2. Start Core Services:**
```bash
# Start Auth Service
cd auth-service && source venv/bin/activate && python main.py &

# Start Catalog Service
cd catalog-service && source venv/bin/activate && python main.py &

# Start Order Service
cd order-service && source venv/bin/activate && python main.py &
```

### **3. Test Basic Flow:**
1. **Register User** (Auth Service)
2. **Login** (Auth Service)
3. **Get Restaurants** (Catalog Service)
4. **Create Order** (Order Service)
5. **Check Order Status** (Order Service)

---

## 🚀 **Production Deployment**

### **Using Docker Compose:**
```bash
# Production deployment
docker compose -f docker-compose.prod.yml up -d

# Scale services
docker compose up -d --scale order-service=3
```

### **Using Kubernetes:**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check pods
kubectl get pods

# Check services
kubectl get services
```

---

## 📊 **Monitoring & Logs**

### **View Service Logs:**
```bash
# Individual service logs
docker compose logs -f auth-service
docker compose logs -f order-service

# All services logs
docker compose logs -f
```

### **Service Health:**
```bash
# Check all service health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
curl http://localhost:8006/health
curl http://localhost:8007/health
curl http://localhost:8008/health
```

**Now you can run each service individually or all together with Docker Compose!** 🍕✨
