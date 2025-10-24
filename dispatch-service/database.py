from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/food_delivery")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vehicle_type = Column(String)
    license_plate = Column(String)
    status = Column(Enum("AVAILABLE", "BUSY", "OFFLINE", name="driver_status"))
    current_latitude = Column(Float)
    current_longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Delivery(Base):
    __tablename__ = "deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    status = Column(Enum("ASSIGNED", "PICKED_UP", "IN_TRANSIT", "DELIVERED", "CANCELLED", name="delivery_status"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    picked_up_at = Column(DateTime)
    delivered_at = Column(DateTime)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
