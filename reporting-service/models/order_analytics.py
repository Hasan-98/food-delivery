from sqlalchemy import Column, Integer, DateTime, Float, String
from datetime import datetime
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class OrderAnalytics(Base):
    __tablename__ = "order_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    customer_id = Column(Integer, index=True)
    restaurant_id = Column(Integer, index=True)
    driver_id = Column(Integer, index=True)
    total_amount = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

