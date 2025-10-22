# Food Delivery Microservices System

A comprehensive microservices-based food delivery system built with FastAPI, PostgreSQL, RabbitMQ, and Docker.

## Architecture Overview

This system implements a microservices architecture with the following services:

### Core Services

1. **Auth Service** (Port 8001)
   - User authentication and authorization
   - JWT token management
   - Role-based access control (Customer, Restaurant, Driver, Admin)

2. **Catalog Service** (Port 8002)
   - Restaurant management
   - Menu item management
   - Restaurant and menu browsing

3. **Order Service** (Port 8003)
   - Order creation and management
   - Order status tracking
   - Order history

4. **Payment Service** (Port 8004)
   - Payment processing
   - Payment status management
   - Refund handling

5. **Restaurant Service** (Port 8005)
   - Order acceptance/rejection
   - Kitchen workflow management
   - Order preparation status

6. **Dispatch Service** (Port 8006)
   - Driver management
   - Driver assignment
   - Delivery tracking

7. **Notification Service** (Port 8007)
   - SMS, Email, and Push notifications
   - Event-driven notifications

8. **Reporting Service** (Port 8008)
   - Analytics and reporting
   - Business intelligence
   - Performance metrics

### Infrastructure

- **PostgreSQL**: Primary database for all services
- **RabbitMQ**: Message broker for asynchronous communication
- **Docker Compose**: Container orchestration

## Communication Patterns

### Synchronous Communication (HTTP REST)
- User authentication
- Menu browsing
- Order creation
- Payment confirmation

### Asynchronous Communication (Event-Driven)
- Order workflow events
- Payment processing
- Restaurant notifications
- Driver assignments
- Analytics data collection

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
- Adminer (Database GUI): http://localhost:8080

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

```bash
curl -X POST "http://localhost:8003/orders" \
  -H "Authorization: Bearer <customer_token>" \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id": 1, "delivery_address": "456 Customer St", "delivery_latitude": 40.7589, "delivery_longitude": -73.9851, "total_amount": 25.99, "items": [{"menu_item_id": 1, "quantity": 2, "price": 12.99}]}'
```

## Monitoring and Logs

### View Service Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service
```

### Health Checks
```bash
# Check service health
curl http://localhost:8001/health
curl http://localhost:8002/health
# ... etc for all services
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

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `RABBITMQ_URL`: RabbitMQ connection string
- `SECRET_KEY`: JWT secret key

## Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker logs and ensure all dependencies are running
2. **Database connection errors**: Verify PostgreSQL is running and accessible
3. **Message queue issues**: Check RabbitMQ management interface at http://localhost:15672
4. **Authentication errors**: Verify JWT secret key is consistent across services

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
# food-delivery
