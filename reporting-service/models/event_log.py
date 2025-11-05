from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class EventLog(Base):
    __tablename__ = "event_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    order_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    restaurant_id = Column(Integer, index=True)
    driver_id = Column(Integer, index=True)
    data = Column(Text)  # JSON data
    timestamp = Column(DateTime, default=datetime.utcnow)

