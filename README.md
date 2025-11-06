# Food Delivery Microservices System

A comprehensive microservices-based food delivery system built with FastAPI, PostgreSQL, RabbitMQ, and Docker. The system implements **MVC (Model-View-Controller) architecture** and **Saga Orchestration Pattern** for distributed transaction management.

## Architecture Overview

This system implements a microservices architecture with the following services:

### Core Services

1. **Auth Service** (Port 8001)
   - User authentication and authorization
   - JWT token management
   - Role-based access control (Customer, Restaurant, Driver, Admin)
   - **Architecture**: MVC pattern with services layer

2. **Catalog Service** (Port 8002)
   - Restaurant management
   - Menu item management
   - Restaurant and menu browsing
   - **Architecture**: MVC pattern with services layer

3. **Order Service** (Port 8003)
   - Order creation and management
   - Order status tracking
   - Order history
   - Compensation endpoints for saga transactions
   - **Architecture**: MVC pattern with services layer

4. **Payment Service** (Port 8004)
   - Payment processing
   - Payment status management
   - Refund handling
   - Compensation endpoints for saga transactions
   - **Architecture**: MVC pattern with services layer

5. **Restaurant Service** (Port 8005)
   - Order acceptance/rejection
   - Kitchen workflow management
   - Order preparation status
   - **Architecture**: MVC pattern with services layer

6. **Dispatch Service** (Port 8006)
   - Driver management
   - Driver assignment
   - Delivery tracking
   - **Architecture**: MVC pattern with services layer

7. **Notification Service** (Port 8007)
   - SMS, Email, and Push notifications
   - Event-driven notifications
   - **Architecture**: MVC pattern with services layer

8. **Reporting Service** (Port 8008)
   - Analytics and reporting
   - Business intelligence
   - Performance metrics
   - **Architecture**: MVC pattern with services layer

9. **Saga Orchestrator Service** (Port 8009)
   - Distributed transaction orchestration
   - Saga pattern implementation
   - Automatic compensation on failures
   - Transaction state management
   - **Architecture**: MVC pattern with services layer

### Infrastructure

- **PostgreSQL**: Primary database for all services
- **RabbitMQ**: Message broker for asynchronous communication
- **Docker Compose**: Container orchestration

## Architecture Pattern

### MVC (Model-View-Controller) Pattern

All services follow a consistent MVC architecture:

```
Service Structure:
├── app/
│   ├── routes.py          # Controllers (API endpoints)
│   ├── schemas.py         # Request/Response models (Pydantic)
│   └── dependencies.py    # Shared dependencies (auth, etc.)
├── services/
│   └── [service_name]_service.py  # Business logic
├── models/
│   └── [model].py         # Database models (SQLAlchemy)
├── config/
│   └── settings.py        # Configuration
└── main.py                # Application entry point
```

**Benefits:**
- Separation of concerns
- Testability
- Maintainability
- Consistency across services

## Communication Patterns

### Synchronous Communication (HTTP REST)
- User authentication
- Menu browsing
- Order creation
- Payment confirmation
- Saga orchestration (via Saga Orchestrator)

### Asynchronous Communication (Event-Driven)
- Order workflow events
- Payment processing
- Restaurant notifications
- Driver assignments
- Analytics data collection

## Distributed Transaction Management

### Saga Orchestration Pattern

The system uses the **Saga Orchestration Pattern** to handle distributed transactions across multiple microservices. This ensures eventual consistency and provides rollback capabilities.

#### How It Works

1. **Saga Orchestrator** manages the transaction flow
2. **Sequential Execution** of steps
3. **State Persistence** in database
4. **Automatic Compensation** on failures

#### Example: Order Processing Saga

```
1. Create Order (order-service)
   ↓ Success
2. Process Payment (payment-service)
   ↓ Success
3. Confirm Order (order-service)
   ↓ Success
Saga Completed

If Payment Fails:
   ↓
Compensate: Cancel Order
   ↓
Saga Failed
```

#### Saga API Endpoints

- `POST /sagas/start` - Start a new saga transaction
- `GET /sagas/{saga_id}/status` - Get saga status and step details
- `POST /sagas/{saga_id}/compensate` - Manually trigger compensation

**Example Request:**
```json
POST /sagas/start
{
  "saga_type": "order_processing",
  "entity_id": 123,
  "step_data": [
    {
      "customer_id": 1,
      "restaurant_id": 2,
      "total_amount": 50.00,
      "items": [...]
    },
    {
      "order_id": 123,  // Auto-populated from step 1
      "amount": 50.00,
      "payment_method": "credit_card"
    },
    {
      "order_id": 123  // Auto-populated from step 1
    }
  ]
}
```
## Event Flow

1. **Customer places order** → Order Service
2. **Order created event** → Payment Service (async)
3. **Payment processed** → Order Service (async)
4. **Order confirmed** → Restaurant Service (async)
5. **Order accepted** → Dispatch Service (async)
6. **Driver assigned** → Notification Service (async)
7. **Order delivered** → Reporting Service (async)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd food-delivery-system
```

2. Start all services:
```bash
docker-compose up -d
```

3. Wait for all services to be healthy (check logs):
```bash
docker-compose logs -f
```

### Service URLs

- Auth Service: http://localhost:8001
- Catalog Service: http://localhost:8002
- Order Service: http://localhost:8003
- Payment Service: http://localhost:8004
- Restaurant Service: http://localhost:8005
- Dispatch Service: http://localhost:8006
- Notification Service: http://localhost:8007
- Reporting Service: http://localhost:8008
- **Saga Orchestrator Service**: http://localhost:8009
- Adminer (Database GUI): http://localhost:8080
- RabbitMQ Management: http://localhost:15672

## API Documentation

Each service provides interactive API documentation at:
- `http://localhost:800X/docs` (where X is the service port)

## Authentication

The system uses JWT tokens for authentication. To access protected endpoints:

1. Register a user via Auth Service
2. Login to get a JWT token
3. Include the token in the Authorization header: `Bearer <token>`

### User Roles

- **CUSTOMER**: Can place orders, view order history
- **RESTAURANT**: Can manage menu, accept/reject orders
- **DRIVER**: Can update location, accept deliveries
- **ADMIN**: Full system access

## Database Schema

### Key Tables

- `users`: User accounts and authentication
- `restaurants`: Restaurant information
- `menu_items`: Restaurant menu items
- `orders`: Order records
- `order_items`: Order line items
- `payments`: Payment transactions
- `drivers`: Driver profiles and status
- `deliveries`: Delivery assignments
- `event_logs`: Event tracking for analytics
- `saga_instances`: Saga transaction state (Saga Orchestrator)
- `saga_steps`: Individual step execution tracking (Saga Orchestrator)

## Event Types

### Order Events
- `order.created`
- `order.confirmed`
- `order.accepted`
- `order.preparing`
- `order.ready_for_delivery`
- `order.delivered`
- `order.cancelled`

### Payment Events
- `payment.succeeded`
- `payment.failed`
- `payment.refunded`

### Driver Events
- `driver.assigned`
- `driver.available`
- `driver.busy`

## Reporting Features

The Reporting Service provides comprehensive analytics:

### Customer Analytics
- Total active customers
- Customer order history
- Top customers by order frequency
- Average order value

### Restaurant Analytics
- Orders received and fulfilled
- Revenue breakdown
- Popular menu items
- Performance metrics

### Driver Analytics
- Deliveries completed
- Earnings tracking
- Performance metrics

### System Analytics
- Order status distribution
- Peak times analysis
- Cancelled orders tracking
- Revenue analytics

## Testing the System

### 1. Create Test Data

```bash
# Register users
curl -X POST "http://localhost:8001/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "customer@test.com", "name": "Test Customer", "password": "password", "role": "CUSTOMER"}'

curl -X POST "http://localhost:8001/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "restaurant@test.com", "name": "Test Restaurant", "password": "password", "role": "RESTAURANT"}'

curl -X POST "http://localhost:8001/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "driver@test.com", "name": "Test Driver", "password": "password", "role": "DRIVER"}'
```

### 2. Login and Get Token

```bash
curl -X POST "http://localhost:8001/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=customer@test.com&password=password"
```

### 3. Create Restaurant and Menu

```bash
# Login as restaurant owner first
# Then create restaurant
curl -X POST "http://localhost:8002/restaurants" \
  -H "Authorization: Bearer <restaurant_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Restaurant", "description": "A test restaurant", "address": "123 Test St", "phone": "555-0123", "latitude": 40.7128, "longitude": -74.0060}'
```

### 4. Place an Order

**Option A: Direct Order Creation (Event-Driven)**
```bash
curl -X POST "http://localhost:8003/orders" \
  -H "Authorization: Bearer <customer_token>" \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id": 1, "delivery_address": "456 Customer St", "delivery_latitude": 40.7589, "delivery_longitude": -73.9851, "total_amount": 25.99, "items": [{"menu_item_id": 1, "quantity": 2, "price": 12.99}]}'
```

**Option B: Using Saga Orchestrator (Transaction Guaranteed)**
```bash
curl -X POST "http://localhost:8009/sagas/start" \
  -H "Content-Type: application/json" \
  -d '{
    "saga_type": "order_processing",
    "entity_id": 1,
    "step_data": [
      {
        "customer_id": 1,
        "restaurant_id": 1,
        "delivery_address": "456 Customer St",
        "delivery_latitude": 40.7589,
        "delivery_longitude": -73.9851,
        "total_amount": 25.99,
        "status": "PENDING_PAYMENT",
        "items": [{"menu_item_id": 1, "quantity": 2, "price": 12.99}]
      },
      {
        "order_id": 0,
        "amount": 25.99,
        "payment_method": "credit_card",
        "status": "PENDING"
      },
      {
        "order_id": 0
      }
    ]
  }'
```

**Check Saga Status:**
```bash
curl "http://localhost:8009/sagas/{saga_id}/status"
```

## Monitoring and Logs

### View Service Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service
docker-compose logs -f saga-orchestrator-service
```

### Health Checks
```bash
# Check service health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
curl http://localhost:8006/health
curl http://localhost:8007/health
curl http://localhost:8008/health
curl http://localhost:8009/health  # Saga Orchestrator
```

### Saga Monitoring
```bash
# Check saga status
curl http://localhost:8009/sagas/{saga_id}/status

# View all saga instances (via database)
# Access Adminer at http://localhost:8080
# Query: SELECT * FROM saga_instances ORDER BY created_at DESC;
```

## Database Access

Access the database via Adminer at http://localhost:8080:
- Server: postgres
- Username: postgres
- Password: postgres
- Database: food_delivery

## Scaling Considerations

### Horizontal Scaling
- Each service can be scaled independently
- Use load balancers for high availability
- Implement service discovery for dynamic scaling

### Database Scaling
- Consider read replicas for reporting queries
- Implement database sharding for large datasets
- Use connection pooling

### Message Queue Scaling
- RabbitMQ clustering for high availability
- Implement dead letter queues for failed messages
- Monitor queue depths and processing rates

## Security Considerations

### Authentication
- JWT tokens with expiration
- Role-based access control
- Secure password hashing (bcrypt)

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- HTTPS in production

### Network Security
- Service-to-service authentication
- Network segmentation
- Rate limiting

## Deployment

### Production Deployment
1. Use environment variables for configuration
2. Implement proper logging and monitoring
3. Set up health checks and auto-restart
4. Use secrets management for sensitive data
5. Implement backup strategies
6. Monitor saga execution and compensation rates

### Environment Variables

**Common Variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `RABBITMQ_URL`: RabbitMQ connection string
- `SECRET_KEY`: JWT secret key

**Service-Specific URLs (for Saga Orchestrator):**
- `ORDER_SERVICE_URL`: http://order-service:8003
- `PAYMENT_SERVICE_URL`: http://payment-service:8004
- `CATALOG_SERVICE_URL`: http://catalog-service:8002
- `RESTAURANT_SERVICE_URL`: http://restaurant-service:8005
- `DISPATCH_SERVICE_URL`: http://dispatch-service:8006

## Key Features

### ✅ Distributed Transaction Management
- **Saga Orchestration Pattern** for ACID-like guarantees across services
- Automatic compensation on failures
- Transaction state persistence
- Idempotent operations

### ✅ Consistent Architecture
- **MVC Pattern** across all services
- Separation of concerns (Routes, Services, Models)
- Centralized configuration
- Standardized error handling

### ✅ Event-Driven Communication
- Asynchronous message processing
- Loose coupling between services
- Scalable architecture

### ✅ Comprehensive Analytics
- Real-time reporting
- Business intelligence
- Performance metrics

## Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker logs and ensure all dependencies are running
2. **Database connection errors**: Verify PostgreSQL is running and accessible
3. **Message queue issues**: Check RabbitMQ management interface at http://localhost:15672
4. **Authentication errors**: Verify JWT secret key is consistent across services
5. **Saga failures**: Check saga status via API and review compensation logs
6. **Transaction inconsistencies**: Use saga orchestrator for critical operations

### Saga-Specific Troubleshooting

```bash
# Check saga status
curl http://localhost:8009/sagas/{saga_id}/status

# Manually trigger compensation
curl -X POST http://localhost:8009/sagas/{saga_id}/compensate

# View saga logs
docker-compose logs -f saga-orchestrator-service
```

### Debug Commands
```bash
# Check service status
docker-compose ps

# View specific service logs
docker-compose logs <service-name>

# Restart a service
docker-compose restart <service-name>

# Rebuild a service
docker-compose build <service-name>
```

## Credentials

### RabbitMQ Management
- **URL**: http://localhost:15672
- **Username**: admin
- **Password**: admin

### PostgreSQL Database
- **Host**: localhost:5432
- **Database**: food_delivery
- **Username**: postgres
- **Password**: postgres

### Adminer (Database GUI)
- **URL**: http://localhost:8080
- **Server**: postgres
- **Username**: postgres
- **Password**: postgres
- **Database**: food_delivery
