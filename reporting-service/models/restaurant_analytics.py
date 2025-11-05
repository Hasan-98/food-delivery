from sqlalchemy import Column, Integer, DateTime, Float
from datetime import datetime
import sys
import os

# Add shared directory to path
sys.path.append(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class RestaurantAnalytics(Base):
    __tablename__ = "restaurant_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, index=True)
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    last_order_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

