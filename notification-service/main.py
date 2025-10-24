from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import sys
import os
import asyncio
import json
import logging

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.models import UserRole
from shared.auth import get_current_user, require_role
from shared.message_broker import get_message_broker

app = FastAPI(title="Notification Service", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationService:
    """Simulated notification service for SMS, Email, and Push notifications"""
    
    @staticmethod
    async def send_sms(phone_number: str, message: str):
        """Simulate SMS sending"""
        logger.info(f"SMS to {phone_number}: {message}")
        # In a real system, this would integrate with SMS providers like Twilio
        return {"status": "sent", "provider": "simulated"}
    
    @staticmethod
    async def send_email(email: str, subject: str, message: str):
        """Simulate email sending"""
        logger.info(f"Email to {email} - {subject}: {message}")
        # In a real system, this would integrate with email providers like SendGrid
        return {"status": "sent", "provider": "simulated"}
    
    @staticmethod
    async def send_push_notification(user_id: int, title: str, message: str):
        """Simulate push notification"""
        logger.info(f"Push notification to user {user_id} - {title}: {message}")
        # In a real system, this would integrate with push notification services
        return {"status": "sent", "provider": "simulated"}

notification_service = NotificationService()

@app.get("/notifications")
async def get_notifications(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user)
):
    """Get notification history for user"""
    # In a real system, this would query a notifications table
    return {
        "message": "Notification history would be returned here",
        "user_id": current_user.id
    }

@app.post("/notifications/send")
async def send_notification(
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    current_user = Depends(require_role(UserRole.ADMIN))
):
    """Send a notification to a specific user"""
    if notification_type == "sms":
        result = await notification_service.send_sms("+1234567890", message)
    elif notification_type == "email":
        result = await notification_service.send_email("user@example.com", title, message)
    elif notification_type == "push":
        result = await notification_service.send_push_notification(user_id, title, message)
    else:
        raise HTTPException(status_code=400, detail="Invalid notification type")
    
    return result

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service"}

# Event handlers for async communication
async def handle_order_created(event_data):
    """Handle order created event - send confirmation to customer"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    customer_id = order_data["customer_id"]
    
    # Send order confirmation
    await notification_service.send_push_notification(
        customer_id,
        "Order Confirmed",
        f"Your order #{order_id} has been placed successfully!"
    )
    
    logger.info(f"Order confirmation sent for order {order_id}")

async def handle_payment_succeeded(event_data):
    """Handle payment succeeded event - notify customer"""
    payment_data = event_data["data"]
    order_id = payment_data["order_id"]
    customer_id = payment_data.get("customer_id")  # Would need to get from order
    
    if customer_id:
        await notification_service.send_push_notification(
            customer_id,
            "Payment Successful",
            f"Payment for order #{order_id} has been processed successfully!"
        )
    
    logger.info(f"Payment success notification sent for order {order_id}")

async def handle_payment_failed(event_data):
    """Handle payment failed event - notify customer"""
    payment_data = event_data["data"]
    order_id = payment_data["order_id"]
    customer_id = payment_data.get("customer_id")  # Would need to get from order
    
    if customer_id:
        await notification_service.send_push_notification(
            customer_id,
            "Payment Failed",
            f"Payment for order #{order_id} failed. Please try again."
        )
    
    logger.info(f"Payment failure notification sent for order {order_id}")

async def handle_order_accepted(event_data):
    """Handle order accepted event - notify customer"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    customer_id = order_data.get("customer_id")  # Would need to get from order
    
    if customer_id:
        await notification_service.send_push_notification(
            customer_id,
            "Order Accepted",
            f"Your order #{order_id} has been accepted by the restaurant!"
        )
    
    logger.info(f"Order acceptance notification sent for order {order_id}")

async def handle_order_ready_for_delivery(event_data):
    """Handle order ready for delivery event - notify customer and find driver"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    customer_id = order_data.get("customer_id")  # Would need to get from order
    
    if customer_id:
        await notification_service.send_push_notification(
            customer_id,
            "Order Ready",
            f"Your order #{order_id} is ready for delivery!"
        )
    
    logger.info(f"Order ready notification sent for order {order_id}")

async def handle_driver_assigned(event_data):
    """Handle driver assigned event - notify customer"""
    driver_data = event_data["data"]
    order_id = driver_data["order_id"]
    driver_id = driver_data["driver_id"]
    customer_id = driver_data.get("customer_id")  # Would need to get from order
    
    if customer_id:
        await notification_service.send_push_notification(
            customer_id,
            "Driver Assigned",
            f"Driver has been assigned to your order #{order_id}!"
        )
    
    logger.info(f"Driver assignment notification sent for order {order_id}")

async def handle_order_delivered(event_data):
    """Handle order delivered event - notify customer"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    customer_id = order_data.get("customer_id")  # Would need to get from order
    
    if customer_id:
        await notification_service.send_push_notification(
            customer_id,
            "Order Delivered",
            f"Your order #{order_id} has been delivered! Enjoy your meal!"
        )
    
    logger.info(f"Order delivery notification sent for order {order_id}")

async def handle_no_driver_available(event_data):
    """Handle no driver available event - notify customer"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    customer_id = order_data.get("customer_id")  # Would need to get from order
    
    if customer_id:
        await notification_service.send_push_notification(
            customer_id,
            "Delivery Delay",
            f"No drivers are currently available for order #{order_id}. We'll find one soon!"
        )
    
    logger.info(f"No driver available notification sent for order {order_id}")

# Start event listeners on startup
@app.on_event("startup")
async def startup_event():
    message_broker = await get_message_broker()
    await message_broker.subscribe_to_events(
        [
            "order.created",
            "payment.succeeded", 
            "payment.failed",
            "order.accepted",
            "order.ready_for_delivery",
            "driver.assigned",
            "order.delivered",
        "no.driver.available"
    ],
    # This is a simplified approach - in reality, you'd have separate handlers
    handle_order_created
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
