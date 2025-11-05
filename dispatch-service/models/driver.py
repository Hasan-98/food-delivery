from sqlalchemy import Column, Integer, String, DateTime, Float, Enum
from datetime import datetime
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    vehicle_type = Column(String)
    license_plate = Column(String)
    status = Column(Enum("AVAILABLE", "BUSY", "OFFLINE", name="driver_status"))
    current_latitude = Column(Float)
    current_longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

