from sqlalchemy import Column, Integer, String, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer)
    restaurant_id = Column(Integer)
    delivery_address = Column(String)
    delivery_latitude = Column(Float)
    delivery_longitude = Column(Float)
    total_amount = Column(Float)
    status = Column(Enum("PENDING_PAYMENT", "CONFIRMED", "ACCEPTED", "PREPARING", 
                        "READY_FOR_DELIVERY", "PICKED_UP", "IN_TRANSIT", 
                        "DELIVERED", "CANCELLED", name="order_status"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship("OrderItem", back_populates="order")

