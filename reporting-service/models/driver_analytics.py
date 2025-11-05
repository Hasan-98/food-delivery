from sqlalchemy import Column, Integer, DateTime, Float
from datetime import datetime
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class DriverAnalytics(Base):
    __tablename__ = "driver_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, index=True)
    total_deliveries = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    last_delivery_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

