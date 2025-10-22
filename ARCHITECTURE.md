# Food Delivery System Architecture

## System Overview

This food delivery system is built using a microservices architecture with 8 core services, each handling a specific domain of the business. The system uses both synchronous (HTTP REST) and asynchronous (event-driven) communication patterns.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Customer App  │    │ Restaurant App  │    │   Driver App    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway / Load Balancer                  │
└─────────────────────────────────────────────────────────────────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Auth Service   │    │ Catalog Service │    │  Order Service │
│   (Port 8001)   │    │   (Port 8002)  │    │   (Port 8003)  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Payment Service │    │Restaurant Service│    │Dispatch Service │
│   (Port 8004)   │    │   (Port 8005)  │    │   (Port 8006)  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Notification Svc │    │ Reporting Svc   │    │   Message Queue │
│   (Port 8007)   │    │   (Port 8008)  │    │   (RabbitMQ)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Shared Infrastructure                       │
│  ┌─────────────┐  ┌─────────────┐            │
│  │ PostgreSQL  │  │   RabbitMQ  │            │
│  │  Database   │  │   Message   │            │
│  │             │  │   Broker    │            │
│  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## Service Responsibilities

### 1. Auth Service (Port 8001)
- **Purpose**: User authentication and authorization
- **Responsibilities**:
  - User registration and login
  - JWT token generation and validation
  - Role-based access control
  - User profile management
- **Database**: PostgreSQL (users table)
- **Communication**: Synchronous HTTP REST

### 2. Catalog Service (Port 8002)
- **Purpose**: Restaurant and menu management
- **Responsibilities**:
  - Restaurant registration and management
  - Menu item creation and updates
  - Restaurant and menu browsing
  - Restaurant search and filtering
- **Database**: PostgreSQL (restaurants, menu_items tables)
- **Communication**: Synchronous HTTP REST

### 3. Order Service (Port 8003)
- **Purpose**: Order lifecycle management
- **Responsibilities**:
  - Order creation and validation
  - Order status tracking
  - Order history and retrieval
  - Order cancellation
- **Database**: PostgreSQL (orders, order_items tables)
- **Communication**: Synchronous HTTP REST + Asynchronous events

### 4. Payment Service (Port 8004)
- **Purpose**: Payment processing and management
- **Responsibilities**:
  - Payment processing (simulated)
  - Payment status tracking
  - Refund processing
  - Payment history
- **Database**: PostgreSQL (payments table)
- **Communication**: Asynchronous events (consumes order.created)

### 5. Restaurant Service (Port 8005)
- **Purpose**: Restaurant order management
- **Responsibilities**:
  - Order acceptance/rejection
  - Kitchen workflow management
  - Order preparation status updates
  - Restaurant notifications
- **Database**: None (stateless)
- **Communication**: Asynchronous events (consumes order.confirmed)

### 6. Dispatch Service (Port 8006)
- **Purpose**: Driver management and assignment
- **Responsibilities**:
  - Driver registration and management
  - Driver location tracking
  - Driver assignment algorithm
  - Delivery tracking
- **Database**: PostgreSQL (drivers, deliveries tables)
- **Communication**: Asynchronous events (consumes order.ready_for_delivery)

### 7. Notification Service (Port 8007)
- **Purpose**: Multi-channel notifications
- **Responsibilities**:
  - SMS notifications (simulated)
  - Email notifications (simulated)
  - Push notifications (simulated)
  - Notification history
- **Database**: None (stateless)
- **Communication**: Asynchronous events (consumes all events)

### 8. Reporting Service (Port 8008)
- **Purpose**: Analytics and business intelligence
- **Responsibilities**:
  - Event aggregation and analytics
  - Business metrics calculation
  - Report generation
  - Data visualization APIs
- **Database**: PostgreSQL (analytics tables)
- **Communication**: Asynchronous events (consumes all events)

## Communication Patterns

### Synchronous Communication (HTTP REST)
Used for immediate responses and CRUD operations:

1. **User Authentication**: Auth Service ↔ All Services
2. **Menu Browsing**: Customer ↔ Catalog Service
3. **Order Creation**: Customer ↔ Order Service
4. **Order Management**: Restaurant ↔ Order Service
5. **Driver Management**: Driver ↔ Dispatch Service

### Asynchronous Communication (Event-Driven)
Used for workflow coordination and decoupling:

1. **Order Workflow**:
   - `order.created` → Payment Service
   - `payment.succeeded` → Order Service
   - `order.confirmed` → Restaurant Service
   - `order.accepted` → Dispatch Service
   - `order.ready_for_delivery` → Dispatch Service
   - `driver.assigned` → Notification Service
   - `order.delivered` → Reporting Service

2. **Event Types**:
   - Order events: created, confirmed, accepted, preparing, ready, delivered, cancelled
   - Payment events: succeeded, failed, refunded
   - Driver events: assigned, available, busy
   - System events: notification_sent, analytics_updated

## Data Flow

### 1. Order Placement Flow
```
Customer → Order Service → Payment Service (async) → Order Service (async) → Restaurant Service (async)
```

### 2. Order Fulfillment Flow
```
Restaurant → Order Service → Dispatch Service (async) → Notification Service (async) → Reporting Service (async)
```

### 3. Analytics Flow
```
All Services → Event Log → Reporting Service → Analytics Database
```

## Database Design

### Core Tables
- **users**: User accounts and authentication
- **restaurants**: Restaurant information and location
- **menu_items**: Restaurant menu items
- **orders**: Order records and status
- **order_items**: Order line items
- **payments**: Payment transactions
- **drivers**: Driver profiles and status
- **deliveries**: Delivery assignments
- **event_logs**: Event tracking for analytics

### Analytics Tables
- **order_analytics**: Order performance metrics
- **customer_analytics**: Customer behavior data
- **restaurant_analytics**: Restaurant performance data
- **driver_analytics**: Driver performance data

## Security Architecture

### Authentication
- JWT tokens with expiration
- Role-based access control (RBAC)
- Secure password hashing (bcrypt)

### Authorization
- Service-level authorization
- Endpoint-level permissions
- Data access controls

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- HTTPS in production
- Secrets management

## Scalability Considerations

### Horizontal Scaling
- Each service can be scaled independently
- Load balancers for high availability
- Service discovery for dynamic scaling
- Database read replicas

### Performance Optimization
- Database connection pooling
- Message queue optimization
- CDN for static content

### Monitoring and Observability
- Health checks for all services
- Centralized logging
- Metrics collection
- Distributed tracing

## Deployment Architecture

### Development Environment
- Docker Compose for local development
- Single PostgreSQL instance
- Single RabbitMQ instance

### Production Environment
- Kubernetes orchestration
- Database clustering
- Message queue clustering
- Load balancers and ingress controllers

## Technology Stack

### Backend Framework
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: Python ORM for database operations
- **Pydantic**: Data validation and serialization

### Database
- **PostgreSQL**: Primary database for all services

### Message Queue
- **RabbitMQ**: Message broker for asynchronous communication
- **aio-pika**: Async Python client for RabbitMQ

### Authentication
- **PyJWT**: JWT token handling
- **Passlib**: Password hashing

### Containerization
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Event-Driven Architecture Benefits

### 1. Decoupling
- Services are loosely coupled
- Independent deployment and scaling
- Fault isolation

### 2. Scalability
- Each service can scale independently
- Event-driven processing
- Asynchronous operations

### 3. Reliability
- Event replay capabilities
- Dead letter queues
- Circuit breaker patterns

### 4. Maintainability
- Clear service boundaries
- Single responsibility principle
- Easy testing and debugging

## Future Enhancements

### 1. Advanced Features
- Real-time tracking
- Machine learning recommendations
- Advanced analytics
- Multi-language support

### 2. Infrastructure
- Service mesh (Istio)
- API gateway
- Distributed tracing
- Advanced monitoring

### 3. Security
- OAuth 2.0 integration
- API rate limiting
- Advanced threat detection
- Compliance features

This architecture provides a solid foundation for a scalable, maintainable, and reliable food delivery system that can handle high traffic and complex business requirements.
