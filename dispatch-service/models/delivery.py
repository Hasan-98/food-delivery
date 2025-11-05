from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey
from datetime import datetime
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class Delivery(Base):
    __tablename__ = "deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    status = Column(Enum("ASSIGNED", "PICKED_UP", "IN_TRANSIT", "DELIVERED", "CANCELLED", name="delivery_status"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    picked_up_at = Column(DateTime)
    delivered_at = Column(DateTime)

