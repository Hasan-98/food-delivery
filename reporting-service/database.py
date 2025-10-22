from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/food_delivery")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

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

class CustomerAnalytics(Base):
    __tablename__ = "customer_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    last_order_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class RestaurantAnalytics(Base):
    __tablename__ = "restaurant_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, index=True)
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    last_order_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class DriverAnalytics(Base):
    __tablename__ = "driver_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, index=True)
    total_deliveries = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    last_delivery_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
