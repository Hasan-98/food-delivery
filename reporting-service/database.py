from sqlalchemy.orm import sessionmaker
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.database import Base, engine, SessionLocal
from models.event_log import EventLog
from models.order_analytics import OrderAnalytics
from models.customer_analytics import CustomerAnalytics
from models.restaurant_analytics import RestaurantAnalytics
from models.driver_analytics import DriverAnalytics

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
