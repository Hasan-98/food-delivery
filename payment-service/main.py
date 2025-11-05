from fastapi import FastAPI
from app.routes import router
from config.settings import settings
from database import Base, engine
from services.event_handlers import handle_order_created
from shared.message_broker import get_message_broker

app = FastAPI(
    title="Payment Service",
    version="1.0.0",
    description="Payment processing service for the food delivery system"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    print("Payment Service database tables created successfully!")
    
    # Start event listeners (optional)
    try:
        message_broker = await get_message_broker()
        await message_broker.subscribe_to_events(
            ["order.created"],
            handle_order_created
        )
    except Exception as e:
        print(f"Message broker startup error: {e}")
        # Continue without message broker

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.SERVICE_HOST, port=settings.SERVICE_PORT)
