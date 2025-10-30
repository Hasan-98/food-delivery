## Food Delivery System – Complete Guide

This guide documents the complete architecture, operations, configuration, and key flows of the Food Delivery System. It includes event-driven messaging details, service responsibilities, endpoints, and troubleshooting.

Generated for the codebase at this repository root. All paths referenced use repository-relative locations (e.g., `order-service/main.py`).

---

### 1. System Overview

The platform is a microservices-based system built with FastAPI, SQLAlchemy, PostgreSQL, Docker Compose, and RabbitMQ. Services communicate asynchronously via events published to a topic exchange and consumed via service-specific queues.

- Language/Framework: Python 3.11, FastAPI
- Persistence: PostgreSQL
- Messaging: RabbitMQ (aio-pika client)
- Auth: JWT
- Containerization: Docker Compose

---

### 2. High-Level Architecture

```mermaid
flowchart LR
  subgraph Client
    A[Postman / Frontend]
  end

  subgraph API Services
    AUTH[auth-service]
    CAT[catalog-service]
    ORD[order-service]
    PAY[payment-service]
    REST[restaurant-service]
    DISP[dispatch-service]
    NOTIF[notification-service]
    REPT[reporting-service]
  end

  DB[(PostgreSQL)]
  MQ[(RabbitMQ: food_delivery_events)]

  A --> AUTH
  A --> CAT
  A --> ORD
  A --> PAY
  A --> REST
  A --> DISP
  A --> NOTIF
  A --> REPT

  AUTH <--> DB
  CAT <--> DB
  ORD <--> DB
  PAY <--> DB
  REST <--> DB
  DISP <--> DB
  NOTIF <--> DB
  REPT <--> DB

  ORD <-- events --> MQ
  PAY <-- events --> MQ
  REST <-- events --> MQ
  DISP <-- events --> MQ
  NOTIF <-- events --> MQ
  REPT <-- events --> MQ
```

---

### 3. Services and Responsibilities

- auth-service (8001): Users, roles, authentication, JWT issuance.
- catalog-service (8002): Restaurants and menu items.
- order-service (8003): Creates orders, manages lifecycle via events.
- payment-service (8004): Processes payments; publishes `payment.succeeded`/`payment.failed`.
- restaurant-service (8005): Accepts orders; emits `order.accepted`/`order.preparing`/`order.ready_for_delivery`/`order.cancelled`.
- dispatch-service (8006): Driver management, assignment; emits `driver.assigned`, `delivery.status_changed`.
- notification-service (8007): Persists and returns notifications; reacts to events.
- reporting-service (8008): Real-time aggregations from operational tables.

Key shared modules:
- `shared/models.py`: Pydantic models, enums (e.g., `OrderStatus`, `UserRole`).
- `shared/message_broker.py`: RabbitMQ publish/subscribe client.

---

### 4. Messaging and Queues

- Exchange: `food_delivery_events` (type: topic, durable: true)
- Queue naming: `{SERVICE_NAME}_queue` (durable)
- Routing key = `event_type` (e.g., `order.created`)

Registration code (excerpt from `shared/message_broker.py`):

```text
declare_exchange("food_delivery_events", TOPIC, durable=True)
declare_queue(f"{SERVICE_NAME}_queue", durable=True)
bind(queue, exchange, routing_key=<event_type>)
consume(queue, callback)
publish(exchange, routing_key=<event_type>, message)
```

Event reliability:
- Persistent messages (`DeliveryMode.PERSISTENT`)
- Durable exchange and queues
- Robust connection handling

---

### 5. Core Event Flows

#### 5.1 Order Creation → Payment → Order Confirmation

```mermaid
sequenceDiagram
  participant Client as Client Application
  participant OrderService as order-service
  participant RabbitMQ as RabbitMQ (Exchange: food_delivery_events)
  participant PaymentService as payment-service

  Client->>OrderService: POST /orders
  OrderService->>RabbitMQ: publish("order.created", payload)
  PaymentService->>RabbitMQ: subscribe(order.created)
  RabbitMQ-->>PaymentService: order.created
  PaymentService->>PaymentService: process payment
  alt success
    PaymentService->>RabbitMQ: publish("payment.succeeded", payload)
  else failure
    PaymentService->>RabbitMQ: publish("payment.failed", error)
  end
  OrderService->>RabbitMQ: subscribe(payment.*)
  RabbitMQ-->>OrderService: payment.succeeded / payment.failed
  OrderService->>OrderService: update order status
```

#### 5.2 Restaurant Lifecycle

```mermaid
sequenceDiagram
  participant RestaurantService as restaurant-service
  participant RabbitMQ as RabbitMQ (Exchange: food_delivery_events)
  participant OrderService as order-service

  RestaurantService->>RabbitMQ: publish(order.accepted)
  RestaurantService->>RabbitMQ: publish(order.preparing)
  RestaurantService->>RabbitMQ: publish(order.ready_for_delivery)
  RestaurantService->>RabbitMQ: publish(order.cancelled)
  OrderService->>RabbitMQ: subscribe(order.*)
  RabbitMQ-->>OrderService: events
  OrderService->>OrderService: update status accordingly
```


#### 5.3 Dispatch & Delivery

sequenceDiagram
  participant DispatchService as dispatch-service
  participant RabbitMQ as RabbitMQ (Exchange: food_delivery_events)
  participant OrderService as order-service

  DispatchService->>RabbitMQ: publish(driver.assigned)
  DispatchService->>RabbitMQ: publish(delivery.status_changed)
  OrderService->>RabbitMQ: subscribe(driver.assigned, delivery.status_changed)
  RabbitMQ-->>OrderService: events
  OrderService->>OrderService: update delivery-related status


#### 5.4 Notifications

sequenceDiagram
  participant NotificationService as notification-service
  participant RabbitMQ as RabbitMQ (Exchange: food_delivery_events)
  participant Database as PostgreSQL Database
  participant EndUser as End User

  NotificationService->>RabbitMQ: subscribe(order.created, payment.succeeded, ...)
  RabbitMQ-->>NotificationService: events
  NotificationService->>Database: persist Notification
  NotificationService->>EndUser: send push notification (simulated)


---

### 6. Setup and Operations

Prerequisites: Docker, Docker Compose

Start the stack:
docker compose up -d --build
docker compose ps

Endpoints (localhost):
- Auth: 8001, Catalog: 8002, Order: 8003, Payment: 8004
- Restaurant: 8005, Dispatch: 8006, Notification: 8007, Reporting: 8008
- RabbitMQ UI: 15673, Postgres: 5433

Service health checks: Each service exposes FastAPI docs at `/docs`.

Environment variables (per service):
- `DATABASE_URL=postgresql://postgres:postgres@postgres:5432/food_delivery`
- `RABBITMQ_URL=amqp://admin:admin@rabbitmq:5672`
- `SERVICE_NAME=<service-name>`

RabbitMQ configuration:
- Exchange/queue declared at runtime by `shared/message_broker.py`.
- Docker Compose sets credentials and management UI.

---

### 7. Key Endpoints (Overview)

Authentication Service (8001):
- `POST /register`, `POST /login`

Catalog Service (8002):
- Restaurants CRUD, `GET /restaurants/{id}`
- Menu items CRUD

Order Service (8003):
- `POST /orders`
- `GET /orders`, `GET /orders/{id}`
- Status updates (internal via events)

Payment Service (8004):
- Subscribes to `order.created`
- Emits `payment.succeeded` / `payment.failed`

Restaurant Service (8005):
- `POST /orders/{order_id}/accept`
- `POST /orders/{order_id}/preparing`
- `POST /orders/{order_id}/ready-for-delivery`
- `POST /orders/{order_id}/cancel`

Dispatch Service (8006):
- `POST /drivers` (create)
- `POST /orders/{order_id}/assign`
- `POST /deliveries/{order_id}/pickup`
- `POST /deliveries/{order_id}/deliver`

Notification Service (8007):
- `GET /notifications?user_id=<id>`
- Receives events and stores notifications

Reporting Service (8008):
- Active counts, customer history, top customers, popular items, status distribution, peak times

Note: See `/docs` per service for full schemas.

---

### 8. Data and Models

- SQLAlchemy models per service in their `database.py`.
- Shared Pydantic models and enums in `shared/models.py`.
- Order items stored in `order-service/database.py` (`Order`, `OrderItem`).
- Dispatch models in `dispatch-service/database.py` (`Driver`, `Delivery`).
- Notification models in `notification-service/database.py`.

DB migrations: Simplified via `Base.metadata.create_all` on startup.

---

### 9. Security and Auth

- JWT-based auth via `auth-service`.
- `require_role` and `get_current_user` used to protect endpoints.
- Drivers, restaurants, customers, admins have permission-scoped actions.

---

### 10. Testing the Full Flow (Quick Walkthrough)

1) Register/login users (admin, customer, restaurant, driver) via auth-service.
2) Create restaurant and menu items via catalog-service.
3) Customer POST `/orders` with menu items.
4) payment-service handles `order.created`, emits `payment.succeeded`.
5) order-service updates status to `CONFIRMED` (if `PENDING_PAYMENT`).
6) restaurant-service posts accept/preparing/ready-for-delivery.
7) dispatch-service assigns driver and updates delivery.
8) notification-service receives events and persists notifications.
9) reporting-service aggregates real data.

---

### 11. Troubleshooting

- RabbitMQ ACCESS_REFUSED: Ensure publishing uses the named exchange `food_delivery_events` (fixed in `shared/message_broker.py`).
- Empty notifications: Verify `user_id` alignment with login; check `notification-service` DB.
- Status not updating: Confirm event subscriptions in `order-service` startup and that services are connected to RabbitMQ.
- Missing tables: Ensure each service calls `Base.metadata.create_all` on startup.

---

### 12. File Map of Interest

- `shared/message_broker.py`: Exchange/queue setup, publish/subscribe.
- `shared/models.py`: Shared Pydantic models/enums.
- `order-service/main.py`: Order lifecycle handlers and subscriptions.
- `payment-service/main.py`: Payment processing and event publishing.
- `restaurant-service/main.py`: Restaurant status publishing and event handling.
- `dispatch-service/main.py`, `dispatch-service/database.py`: Driver and delivery.
- `notification-service/main.py`, `notification-service/database.py`: Notification storage and event handlers.
- `reporting-service/main.py`: Real data aggregations.
- `docker-compose.yml`: Runtime wiring, ports, shared volume, broker config.

---

### 13. Operations Reference

Start:
docker compose up -d --build

Inspect:

docker compose ps
docker logs <service-container-name> --tail 200


RabbitMQ UI:
http://localhost:15673



---

### 14. Notes on Scalability and Reliability

- Services are decoupled via events, enabling independent scaling.
- Topic exchange allows selective binding per routing key.
- Durable entities and persistent messages provide resilience to restarts.
- Idempotent state transitions (e.g., guarding against overwrites) reduce race conditions.

---


