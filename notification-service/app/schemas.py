from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    SMS = "SMS"
    EMAIL = "EMAIL"
    PUSH = "PUSH"

class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"

class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str

class Notification(NotificationBase):
    id: int
    user_id: int
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    notifications: list[Notification]
    total_count: int
    user_id: int

