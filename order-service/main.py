from fastapi import FastAPI
from app.routes import router
from config.settings import settings
from database import Base, engine
from services.event_handlers import (
    handle_payment_succeeded,
    handle_payment_failed,
    handle_order_events,
    handle_driver_assigned,
    handle_delivery_status_changed
)
from shared.message_broker import get_message_broker

app = FastAPI(
    title="Order Service",
    version="1.0.0",
    description="Order management service for the food delivery system"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    print("Order Service database tables created successfully!")
    
    # Start event listeners
    try:
        message_broker = await get_message_broker()
        
        # Subscribe to payment events
        await message_broker.subscribe_to_events(
            ["payment.succeeded", "payment.failed"],
            handle_payment_succeeded
        )
        
        # Subscribe to order events
        await message_broker.subscribe_to_events(
            ["order.accepted", "order.preparing", "order.ready_for_delivery", "order.cancelled"],
            handle_order_events
        )
        
        # Subscribe to driver and delivery events
        await message_broker.subscribe_to_events(
            ["driver.assigned"],
            handle_driver_assigned
        )
        
        await message_broker.subscribe_to_events(
            ["delivery.status_changed"],
            handle_delivery_status_changed
        )
        
        print("Order Service connected to RabbitMQ successfully!")
    except Exception as e:
        print(f"Message broker startup error: {e}")
        print("Continuing without RabbitMQ - some features may not work")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.SERVICE_HOST, port=settings.SERVICE_PORT)
