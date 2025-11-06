# Saga Orchestrator Service

## Overview

The Saga Orchestrator Service implements the **Orchestration-based Saga Pattern** for managing distributed transactions across multiple microservices. It ensures consistency and provides rollback capabilities through compensation transactions.

## Features

- ✅ **Orchestration Pattern**: Central orchestrator manages transaction flow
- ✅ **Compensation Logic**: Automatic rollback on failures
- ✅ **State Persistence**: Saga state tracked in database
- ✅ **Idempotent Operations**: Safe to retry
- ✅ **Error Handling**: Comprehensive error handling and logging

## How It Works

### 1. Saga Execution Flow

```
Client Request
    ↓
Saga Orchestrator
    ↓
Step 1: Create Order (order-service)
    ↓ (if success)
Step 2: Process Payment (payment-service)
    ↓ (if success)
Step 3: Confirm Order (order-service)
    ↓
Saga Completed
```

### 2. Compensation Flow (on failure)

```
Step 2 Fails (Payment)
    ↓
Compensate Step 1: Cancel Order
    ↓
Saga Failed
```

## Usage Example

### Starting an Order Processing Saga

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8009/sagas/start",
        json={
            "saga_type": "order_processing",
            "entity_id": 123,
            "step_data": [
                {
                    "customer_id": 1,
                    "restaurant_id": 2,
                    "total_amount": 50.00,
                    "delivery_address": "123 Main St",
                    "delivery_latitude": 40.7128,
                    "delivery_longitude": -74.0060,
                    "status": "PENDING_PAYMENT",
                    "items": [
                        {
                            "menu_item_id": 1,
                            "quantity": 2,
                            "price": 25.00
                        }
                    ]
                },
                {
                    "order_id": 123,  # Will be replaced by actual order_id
                    "amount": 50.00,
                    "payment_method": "credit_card",
                    "status": "PENDING"
                },
                {
                    "order_id": 123  # Will be replaced by actual order_id
                }
            ]
        }
    )
    
    result = response.json()
    if result["success"]:
        print(f"Saga completed: {result['saga_id']}")
    else:
        print(f"Saga failed: {result['error']}")
```

### Checking Saga Status

```python
response = await client.get(
    f"http://localhost:8009/sagas/{saga_id}/status"
)
status = response.json()
print(f"Saga Status: {status['status']}")
print(f"Current Step: {status['current_step']}")
```

## API Endpoints

- `POST /sagas/start` - Start a new saga transaction
- `GET /sagas/{saga_id}/status` - Get saga status and step details
- `POST /sagas/{saga_id}/compensate` - Manually trigger compensation
- `GET /health` - Health check

## Configuration

Set environment variables:

```bash
ORDER_SERVICE_URL=http://localhost:8003
PAYMENT_SERVICE_URL=http://localhost:8004
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/food_delivery
SERVICE_PORT=8009
```

## Running the Service

```bash
cd saga-orchestrator-service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8009
```

## Integration with Services

Each service needs to expose compensation endpoints:

- **Order Service**: `POST /orders/{order_id}/compensate`
- **Payment Service**: `POST /payments/{payment_id}/compensate`

These endpoints are called automatically by the orchestrator when compensation is needed.

