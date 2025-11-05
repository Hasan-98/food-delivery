from fastapi import FastAPI
from app.routes import router
from config.settings import settings
from database import Base, engine
from services.event_handlers import handle_all_events
from shared.message_broker import get_message_broker

app = FastAPI(
    title="Reporting Service",
    version="1.0.0",
    description="Analytics and reporting service for the food delivery system"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "reporting-service"}

# Start event listeners on startup
@app.on_event("startup")
async def startup_event():
    print("Reporting Service database tables created successfully!")
    
    # Start message broker subscription
    try:
        message_broker = await get_message_broker()
        await message_broker.subscribe_to_events(
            [
                "order.created",
                "order.confirmed",
                "order.accepted",
                "order.preparing",
                "order.ready_for_delivery",
                "order.delivered",
                "order.cancelled",
                "payment.succeeded",
                "payment.failed",
                "driver.assigned"
            ],
            handle_all_events
        )
        print("Reporting Service connected to RabbitMQ successfully!")
    except Exception as e:
        print(f"Message broker startup error: {e}")
        print("Continuing without RabbitMQ - some features may not work")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.SERVICE_HOST, port=settings.SERVICE_PORT)
