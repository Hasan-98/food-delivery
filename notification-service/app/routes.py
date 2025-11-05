from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database import get_db
from app.schemas import NotificationResponse
from shared.auth import get_current_user, require_role, UserRole
from services.notification_service import NotificationService

router = APIRouter()

@router.get("/notifications", response_model=NotificationResponse)
async def get_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get notification history for user"""
    notification_service = NotificationService()
    notifications, total_count = notification_service.get_notifications(
        db, current_user.id, skip, limit
    )
    
    return {
        "notifications": notifications,
        "total_count": total_count,
        "user_id": current_user.id
    }

@router.post("/notifications/send")
async def send_notification(
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    """Send a notification to a specific user"""
    if notification_type not in ["sms", "email", "push"]:
        raise HTTPException(status_code=400, detail="Invalid notification type")
    
    notification_service = NotificationService()
    
    try:
        notification = await notification_service.send_notification(
            db, user_id, notification_type, title, message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")
    
    return {
        "notification_id": notification.id,
        "status": "sent",
        "provider": "simulated"
    }

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service"}

