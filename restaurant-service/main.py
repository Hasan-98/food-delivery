from fastapi import FastAPI
from app.routes import router
from config.settings import settings
from services.event_handlers import handle_order_confirmed
from shared.message_broker import get_message_broker

app = FastAPI(
    title="Restaurant Service",
    version="1.0.0",
    description="Restaurant order management service for the food delivery system"
)

# Include routes
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "restaurant-service"}

# Start event listeners on startup
@app.on_event("startup")
async def startup_event():
    try:
        message_broker = await get_message_broker()
        await message_broker.subscribe_to_events(
            ["order.confirmed"],
            handle_order_confirmed
        )
    except Exception as e:
        print(f"Message broker subscription error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.SERVICE_HOST, port=settings.SERVICE_PORT)
