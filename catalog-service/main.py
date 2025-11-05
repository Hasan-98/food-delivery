from fastapi import FastAPI
from app.routes import router
from config.settings import settings
from database import Base, engine

app = FastAPI(
    title="Catalog Service",
    version="1.0.0",
    description="Restaurant and menu catalog service for the food delivery system"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "catalog-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.SERVICE_HOST, port=settings.SERVICE_PORT)
