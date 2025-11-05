from sqlalchemy import Column, Integer, String, DateTime, Float, Enum
from datetime import datetime
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True)
    amount = Column(Float)
    payment_method = Column(String)
    status = Column(Enum("PENDING", "SUCCEEDED", "FAILED", "REFUNDED", name="payment_status"))
    transaction_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

