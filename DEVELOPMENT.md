# Development Guide

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd food-delivery-system

# Run the setup script
./setup.sh

# Test the system
python3 test_system.py
```

## Project Structure

Each microservice follows this structure:
```
service-name/
├── .env                    # Environment variables
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
├── main.py               # Application entry point
├── app/                  # Application layer
│   ├── routes.py         # API routes
│   ├── schemas.py        # Pydantic models
│   └── dependencies.py   # FastAPI dependencies
├── models/               # Database models
├── services/             # Business logic
├── config/               # Configuration
└── utils/                # Utilities
```

## Environment Configuration

### Service-specific .env files
Each service has its own `.env` file with service-specific configuration.

### Root .env.example
Template for environment variables that can be copied to `.env`.

## Development Workflow

### 1. Local Development
```bash
# Start only infrastructure services
docker-compose up -d postgres redis rabbitmq

# Run a specific service locally
cd auth-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 2. Adding New Features

#### Adding a New Endpoint
1. Add route in `app/routes.py`
2. Add schema in `app/schemas.py` if needed
3. Add business logic in `services/`
4. Update tests

#### Adding a New Model
1. Create model in `models/`
2. Update `models/__init__.py`
3. Create migration if needed
4. Update schemas

#### Adding a New Service
1. Create service directory structure
2. Add to `docker-compose.yml`
3. Update documentation

### 3. Database Changes
```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### 4. Testing
```bash
# Run all tests
pytest

# Run tests for specific service
pytest auth-service/tests/

# Run with coverage
pytest --cov=app
```

## Service Development

### Auth Service
- **Purpose**: User authentication and authorization
- **Key Files**: `models/user.py`, `services/auth_service.py`
- **Dependencies**: JWT, bcrypt

### Catalog Service
- **Purpose**: Restaurant and menu management
- **Key Files**: `models/restaurant.py`, `models/menu_item.py`
- **Dependencies**: None

### Order Service
- **Purpose**: Order lifecycle management
- **Key Files**: `models/order.py`, `services/order_service.py`
- **Dependencies**: Message broker

### Payment Service
- **Purpose**: Payment processing
- **Key Files**: `models/payment.py`, `services/payment_service.py`
- **Dependencies**: Message broker

### Restaurant Service
- **Purpose**: Restaurant operations
- **Key Files**: `services/restaurant_operation_service.py`
- **Dependencies**: Message broker

### Dispatch Service
- **Purpose**: Driver and delivery management
- **Key Files**: `models/driver.py`, `services/dispatch_service.py`
- **Dependencies**: Message broker

### Notification Service
- **Purpose**: Multi-channel notifications
- **Key Files**: `services/notification_service.py`
- **Dependencies**: Message broker

### Reporting Service
- **Purpose**: Analytics and reporting
- **Key Files**: `models/analytics.py`, `services/analytics_service.py`
- **Dependencies**: Message broker

## API Development

### Adding New Endpoints
```python
# In app/routes.py
@router.post("/new-endpoint")
async def new_endpoint(
    data: NewEndpointSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Implementation
    pass
```

### Adding Authentication
```python
# In app/dependencies.py
def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker
```

### Adding Business Logic
```python
# In services/service_name.py
class ServiceName:
    def __init__(self):
        pass
    
    def business_method(self, data):
        # Implementation
        pass
```

## Message Queue Development

### Publishing Events
```python
from shared.message_broker import get_message_broker

# In your service
message_broker = await get_message_broker()
await message_broker.publish_event(
    "event.type",
    {"key": "value"}
)
```

### Consuming Events
```python
# In main.py
@app.on_event("startup")
async def startup_event():
    message_broker = await get_message_broker()
    await message_broker.subscribe_to_events(
        ["event.type"],
        handle_event
    )
```

## Database Development

### Adding New Models
```python
# In models/new_model.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NewModel(Base):
    __tablename__ = "new_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Add new model"

# Apply migration
alembic upgrade head
```

## Configuration Management

### Environment Variables
```python
# In config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "default_value")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
```

### Service Configuration
```python
# In main.py
from config.settings import settings

app = FastAPI(
    title="Service Name",
    version="1.0.0"
)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.SERVICE_HOST, port=settings.SERVICE_PORT)
```

## Testing

### Unit Tests
```python
# In tests/test_service.py
import pytest
from services.service_name import ServiceName

def test_service_method():
    service = ServiceName()
    result = service.method("input")
    assert result == "expected_output"
```

### Integration Tests
```python
# In tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_endpoint():
    response = client.get("/endpoint")
    assert response.status_code == 200
```

## Deployment

### Docker Development
```bash
# Build specific service
docker-compose build auth-service

# Run specific service
docker-compose up auth-service

# View logs
docker-compose logs -f auth-service
```

### Production Deployment
1. Update environment variables
2. Use production secrets
3. Configure load balancers
4. Set up monitoring
5. Configure backups

## Debugging

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service

# Last 100 lines
docker-compose logs --tail=100 auth-service
```

### Database Access
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d food_delivery

# Or use Adminer at http://localhost:8080
```

### Message Queue Access
- RabbitMQ Management: http://localhost:15672
- Username: admin
- Password: admin

## Common Issues

### Service Not Starting
1. Check Docker logs: `docker-compose logs service-name`
2. Verify environment variables
3. Check database connectivity
4. Verify message queue connectivity

### Database Connection Issues
1. Check if PostgreSQL is running
2. Verify connection string
3. Check network connectivity

### Message Queue Issues
1. Check if RabbitMQ is running
2. Verify connection string
3. Check queue status in management interface

## Best Practices

### Code Organization
- Keep business logic in services
- Keep data models in models
- Keep API routes in app/routes.py
- Use dependency injection

### Error Handling
- Use appropriate HTTP status codes
- Provide meaningful error messages
- Log errors appropriately
- Handle exceptions gracefully

### Security
- Validate all inputs
- Use proper authentication
- Sanitize data
- Use HTTPS in production

### Performance
- Use database indexes
- Implement caching
- Optimize queries
- Monitor performance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
