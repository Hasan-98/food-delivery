from fastapi import FastAPI
from app.routes import router
from config.settings import settings
from database import Base, engine
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Saga Orchestrator Service",
    version="1.0.0",
    description="Orchestrates distributed transactions using Saga pattern"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(router, prefix="", tags=["saga"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "saga-orchestrator-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.SERVICE_HOST, port=settings.SERVICE_PORT)

