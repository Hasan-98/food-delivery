from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class SagaStep(Base):
    __tablename__ = "saga_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    saga_instance_id = Column(Integer, ForeignKey("saga_instances.id"), index=True)
    step_index = Column(Integer)  # Order of execution
    step_name = Column(String)  # e.g., "create_order", "process_payment"
    service_name = Column(String)  # e.g., "order-service", "payment-service"
    status = Column(Enum("PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "COMPENSATED", name="step_status"))
    request_data = Column(Text)  # JSON data sent to service
    response_data = Column(Text)  # JSON response from service
    compensation_data = Column(Text)  # Data needed for compensation
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    compensated_at = Column(DateTime)

