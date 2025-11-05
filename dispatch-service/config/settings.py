import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/food_delivery")
    
    # Service Configuration
    SERVICE_NAME = os.getenv("SERVICE_NAME", "dispatch-service")
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8006"))
    SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()

