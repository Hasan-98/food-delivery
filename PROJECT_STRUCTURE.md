# Food Delivery System - Project Structure

## Overview
This document outlines the proper folder structure for each microservice in the food delivery system. Each service follows a consistent organizational pattern for maintainability and scalability.

## Root Directory Structure
```
food-delivery-system/
├── .env.example                 # Environment variables template
├── docker-compose.yml          # Docker orchestration
├── README.md                   # Main documentation
├── ARCHITECTURE.md             # System architecture
├── PROJECT_STRUCTURE.md        # This file
├── start.sh                    # Startup script
├── test_system.py              # System test script
├── shared/                     # Shared libraries
│   ├── __init__.py
│   ├── models.py               # Shared Pydantic models
│   ├── database.py             # Database configuration
│   ├── auth.py                 # Authentication utilities
│   └── message_broker.py       # Message queue utilities
├── auth-service/               # Authentication Service
├── catalog-service/            # Restaurant & Menu Service
├── order-service/              # Order Management Service
├── payment-service/            # Payment Processing Service
├── restaurant-service/         # Restaurant Operations Service
├── dispatch-service/           # Driver & Delivery Service
├── notification-service/       # Notification Service
└── reporting-service/          # Analytics & Reporting Service
```

## Microservice Structure
Each microservice follows this consistent structure:

```
service-name/
├── .env                       # Environment variables
├── Dockerfile                 # Container configuration
├── requirements.txt           # Python dependencies
├── main.py                    # Application entry point
├── app/                       # Application layer
│   ├── __init__.py
│   ├── routes.py              # API routes
│   ├── schemas.py              # Pydantic models
│   └── dependencies.py         # FastAPI dependencies
├── models/                    # Database models
│   ├── __init__.py
│   └── *.py                   # SQLAlchemy models
├── services/                  # Business logic
│   ├── __init__.py
│   └── *.py                   # Service classes
├── config/                    # Configuration
│   ├── __init__.py
│   └── settings.py             # Settings management
└── utils/                     # Utilities
    ├── __init__.py
    └── *.py                   # Helper functions
```

## Detailed Service Structure

### 1. Auth Service (`auth-service/`)
```
auth-service/
├── .env
├── Dockerfile
├── requirements.txt
├── main.py
├── app/
│   ├── __init__.py
│   ├── routes.py              # Auth endpoints
│   ├── schemas.py              # User schemas
│   └── dependencies.py         # Auth dependencies
├── models/
│   ├── __init__.py
│   └── user.py                 # User model
├── services/
│   ├── __init__.py
│   └── auth_service.py         # Authentication logic
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration
└── utils/
    ├── __init__.py
    └── database.py             # Database connection
```

### 2. Catalog Service (`catalog-service/`)
```
catalog-service/
├── .env
├── Dockerfile
├── requirements.txt
├── main.py
├── app/
│   ├── __init__.py
│   ├── routes.py              # Restaurant & menu endpoints
│   ├── schemas.py              # Restaurant schemas
│   └── dependencies.py         # Auth dependencies
├── models/
│   ├── __init__.py
│   ├── restaurant.py           # Restaurant model
│   └── menu_item.py            # Menu item model
├── services/
│   ├── __init__.py
│   ├── restaurant_service.py   # Restaurant logic
│   └── menu_service.py         # Menu logic
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration
└── utils/
    ├── __init__.py
    └── database.py             # Database connection
```

### 3. Order Service (`order-service/`)
```
order-service/
├── .env
├── Dockerfile
├── requirements.txt
├── main.py
├── app/
│   ├── __init__.py
│   ├── routes.py              # Order endpoints
│   ├── schemas.py              # Order schemas
│   └── dependencies.py         # Auth dependencies
├── models/
│   ├── __init__.py
│   ├── order.py                # Order model
│   └── order_item.py           # Order item model
├── services/
│   ├── __init__.py
│   └── order_service.py        # Order logic
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration
└── utils/
    ├── __init__.py
    └── database.py             # Database connection
```

### 4. Payment Service (`payment-service/`)
```
payment-service/
├── .env
├── Dockerfile
├── requirements.txt
├── main.py
├── app/
│   ├── __init__.py
│   ├── routes.py              # Payment endpoints
│   ├── schemas.py              # Payment schemas
│   └── dependencies.py         # Auth dependencies
├── models/
│   ├── __init__.py
│   └── payment.py              # Payment model
├── services/
│   ├── __init__.py
│   └── payment_service.py      # Payment logic
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration
└── utils/
    ├── __init__.py
    └── database.py             # Database connection
```

### 5. Restaurant Service (`restaurant-service/`)
```
restaurant-service/
├── .env
├── Dockerfile
├── requirements.txt
├── main.py
├── app/
│   ├── __init__.py
│   ├── routes.py              # Restaurant operation endpoints
│   ├── schemas.py              # Restaurant operation schemas
│   └── dependencies.py         # Auth dependencies
├── models/
│   ├── __init__.py
│   └── restaurant_operation.py # Restaurant operation model
├── services/
│   ├── __init__.py
│   └── restaurant_operation_service.py # Restaurant operation logic
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration
└── utils/
    ├── __init__.py
    └── database.py             # Database connection
```

### 6. Dispatch Service (`dispatch-service/`)
```
dispatch-service/
├── .env
├── Dockerfile
├── requirements.txt
├── main.py
├── app/
│   ├── __init__.py
│   ├── routes.py              # Driver & delivery endpoints
│   ├── schemas.py              # Driver schemas
│   └── dependencies.py         # Auth dependencies
├── models/
│   ├── __init__.py
│   ├── driver.py                # Driver model
│   └── delivery.py              # Delivery model
├── services/
│   ├── __init__.py
│   ├── driver_service.py       # Driver logic
│   └── dispatch_service.py     # Dispatch logic
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration
└── utils/
    ├── __init__.py
    └── database.py             # Database connection
```

### 7. Notification Service (`notification-service/`)
```
notification-service/
├── .env
├── Dockerfile
├── requirements.txt
├── main.py
├── app/
│   ├── __init__.py
│   ├── routes.py              # Notification endpoints
│   ├── schemas.py              # Notification schemas
│   └── dependencies.py         # Auth dependencies
├── models/
│   ├── __init__.py
│   └── notification.py         # Notification model
├── services/
│   ├── __init__.py
│   └── notification_service.py # Notification logic
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration
└── utils/
    ├── __init__.py
    └── database.py             # Database connection
```

### 8. Reporting Service (`reporting-service/`)
```
reporting-service/
├── .env
├── Dockerfile
├── requirements.txt
├── main.py
├── app/
│   ├── __init__.py
│   ├── routes.py              # Reporting endpoints
│   ├── schemas.py              # Report schemas
│   └── dependencies.py         # Auth dependencies
├── models/
│   ├── __init__.py
│   ├── analytics.py            # Analytics models
│   └── report.py               # Report models
├── services/
│   ├── __init__.py
│   ├── analytics_service.py    # Analytics logic
│   └── report_service.py       # Report logic
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration
└── utils/
    ├── __init__.py
    └── database.py             # Database connection
```

## Environment Configuration

### Root .env.example
Contains template environment variables for the entire system.

### Service-specific .env
Each service has its own `.env` file with service-specific configuration.

## Key Benefits of This Structure

### 1. **Separation of Concerns**
- Clear separation between routes, business logic, and data models
- Each layer has a specific responsibility

### 2. **Maintainability**
- Easy to locate and modify specific functionality
- Consistent structure across all services
- Clear dependencies between components

### 3. **Scalability**
- Services can be developed and deployed independently
- Easy to add new features without affecting other services
- Clear boundaries for team ownership

### 4. **Testing**
- Each layer can be tested independently
- Clear interfaces between components
- Easy to mock dependencies

### 5. **Configuration Management**
- Environment-specific configuration
- Centralized settings management
- Easy to override for different environments

## Development Guidelines

### 1. **Adding New Features**
- Add routes in `app/routes.py`
- Add business logic in `services/`
- Add data models in `models/`
- Update schemas in `app/schemas.py`

### 2. **Database Changes**
- Update models in `models/`
- Create migrations if needed
- Update schemas accordingly

### 3. **Configuration Changes**
- Update `config/settings.py`
- Update `.env` files
- Update Docker configurations if needed

### 4. **Testing**
- Add tests in appropriate directories
- Follow the same structure for test files
- Use consistent naming conventions

This structure ensures that the food delivery system is maintainable, scalable, and follows industry best practices for microservices architecture.
