"""Event handlers for notification service"""
from sqlalchemy.orm import Session
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import SessionLocal
from models.notification import Notification
from services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

async def handle_order_created(event_data):
    """Handle order created event - send confirmation to customer"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    customer_id = order_data["customer_id"]
    
    db = SessionLocal()
    try:
        notification_service = NotificationService()
        
        # Save notification to database
        notification = notification_service.create_notification(
            db,
            customer_id,
            "PUSH",
            "Order Confirmed",
            f"Your order #{order_id} has been placed successfully!"
        )
        
        # Update to sent status
        notification.status = "SENT"
        notification.sent_at = datetime.utcnow()
        db.commit()
        
        # Send order confirmation
        await notification_service.send_push_notification(
            customer_id,
            "Order Confirmed",
            f"Your order #{order_id} has been placed successfully!"
        )
        
        logger.info(f"Order confirmation sent for order {order_id}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
    finally:
        db.close()

async def handle_payment_succeeded(event_data):
    """Handle payment succeeded event - notify customer"""
    payment_data = event_data["data"]
    order_id = payment_data["order_id"]
    customer_id = payment_data.get("customer_id")
    
    if customer_id:
        notification_service = NotificationService()
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
    customer_id = payment_data.get("customer_id")
    
    if customer_id:
        notification_service = NotificationService()
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
    customer_id = order_data.get("customer_id")
    
    if customer_id:
        notification_service = NotificationService()
        await notification_service.send_push_notification(
            customer_id,
            "Order Accepted",
            f"Your order #{order_id} has been accepted by the restaurant!"
        )
    
    logger.info(f"Order acceptance notification sent for order {order_id}")

async def handle_order_ready_for_delivery(event_data):
    """Handle order ready for delivery event - notify customer"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    customer_id = order_data.get("customer_id")
    
    if customer_id:
        notification_service = NotificationService()
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
    customer_id = driver_data.get("customer_id")
    
    if customer_id:
        notification_service = NotificationService()
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
    customer_id = order_data.get("customer_id")
    
    if customer_id:
        notification_service = NotificationService()
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
    customer_id = order_data.get("customer_id")
    
    if customer_id:
        notification_service = NotificationService()
        await notification_service.send_push_notification(
            customer_id,
            "Delivery Delay",
            f"No drivers are currently available for order #{order_id}. We'll find one soon!"
        )
    
    logger.info(f"No driver available notification sent for order {order_id}")

async def handle_order_confirmed(event_data):
    """Handle order confirmed event - notify customer that payment succeeded and order is confirmed"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    customer_id = order_data["customer_id"]
    
    db = SessionLocal()
    try:
        notification_service = NotificationService()
        
        # Save notification to database
        notification = notification_service.create_notification(
            db,
            customer_id,
            "PUSH",
            "Order Confirmed",
            f"Your order #{order_id} has been confirmed! Payment received successfully."
        )
        
        # Update to sent status
        notification.status = "SENT"
        notification.sent_at = datetime.utcnow()
        db.commit()
        
        # Send push notification
        await notification_service.send_push_notification(
            customer_id,
            "Order Confirmed",
            f"Your order #{order_id} has been confirmed! Payment received successfully."
        )
        
        logger.info(f"Order confirmation sent for order {order_id}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
    finally:
        db.close()

async def handle_all_notification_events(event_data):
    """Handle all notification events"""
    event_type = event_data.get("event_type", "")
    
    if event_type == "order.created":
        await handle_order_created(event_data)
    elif event_type == "order.confirmed":
        await handle_order_confirmed(event_data)
    elif event_type == "payment.succeeded":
        await handle_payment_succeeded(event_data)
    elif event_type == "payment.failed":
        await handle_payment_failed(event_data)
    elif event_type == "order.accepted":
        await handle_order_accepted(event_data)
    elif event_type == "order.ready_for_delivery":
        await handle_order_ready_for_delivery(event_data)
    elif event_type == "driver.assigned":
        await handle_driver_assigned(event_data)
    elif event_type == "order.delivered":
        await handle_order_delivered(event_data)
    elif event_type == "no.driver.available":
        await handle_no_driver_available(event_data)

