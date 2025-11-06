import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/food_delivery")
    
    # Service URLs (use service names in Docker, localhost for local development)
    ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8000")
    PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8000")
    CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:8000")
    RESTAURANT_SERVICE_URL = os.getenv("RESTAURANT_SERVICE_URL", "http://restaurant-service:8000")
    DISPATCH_SERVICE_URL = os.getenv("DISPATCH_SERVICE_URL", "http://dispatch-service:8000")
    
    # Service Configuration
    SERVICE_NAME = os.getenv("SERVICE_NAME", "saga-orchestrator-service")
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))  # Default 8000 for Docker, 8009 for local dev
    SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
    
    # Saga Configuration
    SAGA_TIMEOUT = int(os.getenv("SAGA_TIMEOUT", "30"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()

