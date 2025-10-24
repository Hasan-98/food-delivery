from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from datetime import datetime
import os
import sys

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.database import Base, engine, SessionLocal

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer)  # Remove foreign key for now
    restaurant_id = Column(Integer)  # Remove foreign key for now
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

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer)  # Remove foreign key for now
    quantity = Column(Integer)
    price = Column(Float)
    
    # Relationships
    order = relationship("Order", back_populates="items")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
