from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class SagaInstance(Base):
    __tablename__ = "saga_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    saga_id = Column(String, unique=True, index=True)  # Unique identifier for the saga
    saga_type = Column(String, index=True)  # e.g., "order_processing"
    entity_id = Column(Integer, index=True)  # e.g., order_id
    status = Column(Enum("PENDING", "IN_PROGRESS", "COMPLETED", "COMPENSATING", "FAILED", name="saga_status"))
    current_step = Column(Integer, default=0)  # Current step index
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    compensation_data = Column(Text)  # JSON data for compensation
    error_message = Column(Text)

