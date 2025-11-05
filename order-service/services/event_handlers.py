"""Event handlers for order service"""
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import SessionLocal
from models.order import Order
from shared.models import OrderStatus
from services.order_service import OrderService

async def handle_payment_succeeded(event_data):
    """Handle payment succeeded event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing payment.succeeded for order {order_id}")
    
    db = SessionLocal()
    try:
        order_service = OrderService()
        order = order_service.get_order_by_id(db, order_id)
        if order:
            # Only update if still in PENDING_PAYMENT status
            if order.status == OrderStatus.PENDING_PAYMENT:
                order_service.update_order_status(db, order_id, OrderStatus.CONFIRMED)
                print(f"DEBUG: Order {order_id} status updated to CONFIRMED")
            else:
                print(f"DEBUG: Order {order_id} already processed (status: {order.status})")
        else:
            print(f"DEBUG: Order {order_id} not found")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_payment_failed(event_data):
    """Handle payment failed event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing payment.failed for order {order_id}")
    
    db = SessionLocal()
    try:
        order_service = OrderService()
        order_service.update_order_status(db, order_id, OrderStatus.CANCELLED)
        print(f"DEBUG: Order {order_id} status updated to CANCELLED")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_order_accepted(event_data):
    """Handle order accepted event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing order.accepted for order {order_id}")
    
    db = SessionLocal()
    try:
        order_service = OrderService()
        order_service.update_order_status(db, order_id, OrderStatus.ACCEPTED)
        print(f"DEBUG: Order {order_id} status updated to ACCEPTED")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_order_preparing(event_data):
    """Handle order preparing event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing order.preparing for order {order_id}")
    
    db = SessionLocal()
    try:
        order_service = OrderService()
        order_service.update_order_status(db, order_id, OrderStatus.PREPARING)
        print(f"DEBUG: Order {order_id} status updated to PREPARING")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_order_ready_for_delivery(event_data):
    """Handle order ready for delivery event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing order.ready_for_delivery for order {order_id}")
    
    db = SessionLocal()
    try:
        order_service = OrderService()
        order_service.update_order_status(db, order_id, OrderStatus.READY_FOR_DELIVERY)
        print(f"DEBUG: Order {order_id} status updated to READY_FOR_DELIVERY")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_order_cancelled(event_data):
    """Handle order cancelled event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing order.cancelled for order {order_id}")
    
    db = SessionLocal()
    try:
        order_service = OrderService()
        order_service.update_order_status(db, order_id, OrderStatus.CANCELLED)
        print(f"DEBUG: Order {order_id} status updated to CANCELLED")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_driver_assigned(event_data):
    """Handle driver assigned event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing driver.assigned for order {order_id}")
    
    db = SessionLocal()
    try:
        order_service = OrderService()
        order_service.update_order_status(db, order_id, OrderStatus.PICKED_UP)
        print(f"DEBUG: Order {order_id} status updated to PICKED_UP")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_delivery_status_changed(event_data):
    """Handle delivery status changed event"""
    order_id = event_data["data"]["order_id"]
    delivery_status = event_data["data"]["status"]
    print(f"DEBUG: Processing delivery status change for order {order_id}: {delivery_status}")
    
    status_mapping = {
        "PICKED_UP": OrderStatus.IN_TRANSIT,
        "DELIVERED": OrderStatus.DELIVERED,
        "CANCELLED": OrderStatus.CANCELLED
    }
    
    new_order_status = status_mapping.get(delivery_status)
    if not new_order_status:
        print(f"DEBUG: Unknown delivery status: {delivery_status}")
        return
    
    db = SessionLocal()
    try:
        order_service = OrderService()
        order_service.update_order_status(db, order_id, new_order_status)
        print(f"DEBUG: Order {order_id} status updated to {new_order_status}")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_order_events(event_data):
    """Generic handler for order events"""
    event_type = event_data.get("event_type", "")
    print(f"DEBUG: Processing {event_type} event")
    
    if event_type == "order.accepted":
        await handle_order_accepted(event_data)
    elif event_type == "order.preparing":
        await handle_order_preparing(event_data)
    elif event_type == "order.ready_for_delivery":
        await handle_order_ready_for_delivery(event_data)
    elif event_type == "order.cancelled":
        await handle_order_cancelled(event_data)
    else:
        print(f"DEBUG: Unknown order event type: {event_type}")

