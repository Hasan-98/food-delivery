from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from datetime import datetime
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    type = Column(Enum("SMS", "EMAIL", "PUSH", name="notification_type"))
    title = Column(String)
    message = Column(Text)
    status = Column(Enum("PENDING", "SENT", "FAILED", name="notification_status"))
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)

