from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import sys
import os
import asyncio
import json

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from database import get_db, Order, OrderItem
from shared.models import (
    Order as OrderModel, OrderCreate, OrderCreateRequest, OrderItem as OrderItemModel,
    OrderStatus, UserRole
)
from shared.auth import get_current_user, require_role
from shared.message_broker import get_message_broker

app = FastAPI(title="Order Service", version="1.0.0")

# Event handlers for async communication
async def handle_payment_succeeded(event_data):
    """Handle payment succeeded event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing payment.succeeded for order {order_id}")
    
    # Update order status to confirmed only if still pending payment
    from database import get_db, Order
    from shared.models import OrderStatus
    
    db = next(get_db())
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            # Only update if still in PENDING_PAYMENT status
            if order.status == OrderStatus.PENDING_PAYMENT:
                order.status = OrderStatus.CONFIRMED
                db.commit()
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
    
    # Update order status to cancelled
    from database import get_db, Order
    from shared.models import OrderStatus
    
    db = next(get_db())
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = OrderStatus.CANCELLED
            db.commit()
            print(f"DEBUG: Order {order_id} status updated to CANCELLED")
        else:
            print(f"DEBUG: Order {order_id} not found")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_order_accepted(event_data):
    """Handle order accepted event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing order.accepted for order {order_id}")
    
    # Update order status to accepted
    from database import get_db, Order
    from shared.models import OrderStatus
    
    db = next(get_db())
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = OrderStatus.ACCEPTED
            db.commit()
            print(f"DEBUG: Order {order_id} status updated to ACCEPTED")
        else:
            print(f"DEBUG: Order {order_id} not found")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_order_preparing(event_data):
    """Handle order preparing event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing order.preparing for order {order_id}")
    
    # Update order status to preparing
    from database import get_db, Order
    from shared.models import OrderStatus
    
    db = next(get_db())
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = OrderStatus.PREPARING
            db.commit()
            print(f"DEBUG: Order {order_id} status updated to PREPARING")
        else:
            print(f"DEBUG: Order {order_id} not found")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_order_ready_for_delivery(event_data):
    """Handle order ready for delivery event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing order.ready_for_delivery for order {order_id}")
    
    # Update order status to ready for delivery
    from database import get_db, Order
    from shared.models import OrderStatus
    
    db = next(get_db())
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = OrderStatus.READY_FOR_DELIVERY
            db.commit()
            print(f"DEBUG: Order {order_id} status updated to READY_FOR_DELIVERY")
        else:
            print(f"DEBUG: Order {order_id} not found")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_order_cancelled(event_data):
    """Handle order cancelled event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing order.cancelled for order {order_id}")
    
    # Update order status to cancelled
    from database import get_db, Order
    from shared.models import OrderStatus
    
    db = next(get_db())
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = OrderStatus.CANCELLED
            db.commit()
            print(f"DEBUG: Order {order_id} status updated to CANCELLED")
        else:
            print(f"DEBUG: Order {order_id} not found")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_driver_assigned(event_data):
    """Handle driver assigned event"""
    order_id = event_data["data"]["order_id"]
    print(f"DEBUG: Processing driver.assigned for order {order_id}")
    
    # Update order status to picked up (driver assigned)
    from database import get_db, Order
    from shared.models import OrderStatus
    
    db = next(get_db())
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = OrderStatus.PICKED_UP
            db.commit()
            print(f"DEBUG: Order {order_id} status updated to PICKED_UP")
        else:
            print(f"DEBUG: Order {order_id} not found")
    except Exception as e:
        print(f"DEBUG: Error updating order {order_id}: {e}")
    finally:
        db.close()

async def handle_delivery_status_changed(event_data):
    """Handle delivery status changed event"""
    order_id = event_data["data"]["order_id"]
    delivery_status = event_data["data"]["status"]
    print(f"DEBUG: Processing delivery status change for order {order_id}: {delivery_status}")
    
    # Map delivery status to order status
    from database import get_db, Order
    from shared.models import OrderStatus
    
    status_mapping = {
        "PICKED_UP": OrderStatus.IN_TRANSIT,
        "DELIVERED": OrderStatus.DELIVERED,
        "CANCELLED": OrderStatus.CANCELLED
    }
    
    new_order_status = status_mapping.get(delivery_status)
    if not new_order_status:
        print(f"DEBUG: Unknown delivery status: {delivery_status}")
        return
    
    db = next(get_db())
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = new_order_status
            db.commit()
            print(f"DEBUG: Order {order_id} status updated to {new_order_status}")
        else:
            print(f"DEBUG: Order {order_id} not found")
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

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
    print("Order Service database tables created successfully!")
    
    # Start event listeners
    try:
        message_broker = await get_message_broker()
        
        # Subscribe to payment events
        await message_broker.subscribe_to_events(
            ["payment.succeeded", "payment.failed"],
            handle_payment_succeeded
        )
        
        # Subscribe to order events
        await message_broker.subscribe_to_events(
            ["order.accepted", "order.preparing", "order.ready_for_delivery", "order.cancelled"],
            handle_order_events
        )
        
        # Subscribe to driver and delivery events
        await message_broker.subscribe_to_events(
            ["driver.assigned"],
            handle_driver_assigned
        )
        
        await message_broker.subscribe_to_events(
            ["delivery.status_changed"],
            handle_delivery_status_changed
        )
        
        print("Order Service connected to RabbitMQ successfully!")
    except Exception as e:
        print(f"Message broker startup error: {e}")
        print("Continuing without RabbitMQ - some features may not work")

@app.post("/orders", response_model=OrderModel)
async def create_order(
    order: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.CUSTOMER))
):
    # Validate restaurant exists
    from shared.database import engine
    from sqlalchemy import text
    
    # Check if restaurant exists
    result = db.execute(text("SELECT id FROM restaurants WHERE id = :restaurant_id"), 
                       {"restaurant_id": order.restaurant_id})
    restaurant = result.fetchone()
    
    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail=f"Restaurant with ID {order.restaurant_id} not found"
        )
    
    # Create order
    db_order = Order(
        customer_id=current_user.id,
        restaurant_id=order.restaurant_id,
        delivery_address=order.delivery_address,
        delivery_latitude=order.delivery_latitude,
        delivery_longitude=order.delivery_longitude,
        total_amount=order.total_amount,
        status=order.status
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items
    for item in order.items:
        # Validate menu item exists and belongs to the restaurant
        result = db.execute(text("SELECT id FROM menu_items WHERE id = :menu_item_id AND restaurant_id = :restaurant_id"), 
                           {"menu_item_id": item.menu_item_id, "restaurant_id": order.restaurant_id})
        menu_item = result.fetchone()
        
        if not menu_item:
            raise HTTPException(
                status_code=404,
                detail=f"Menu item with ID {item.menu_item_id} not found for restaurant {order.restaurant_id}"
            )
        
        db_item = OrderItem(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(db_item)
    
    db.commit()
    
    # Publish order created event (optional)
    try:
        message_broker = await get_message_broker()
        await message_broker.publish_event(
            "order.created",
            {
                "order_id": db_order.id,
                "customer_id": db_order.customer_id,
                "restaurant_id": db_order.restaurant_id,
                "total_amount": db_order.total_amount,
                "items": [item.dict() for item in order.items]
            }
        )
    except Exception as e:
        print(f"Message broker error: {e}")
        # Continue without message broker
    
    return db_order

@app.get("/orders", response_model=List[OrderModel])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role == UserRole.CUSTOMER:
        orders = db.query(Order).filter(Order.customer_id == current_user.id).offset(skip).limit(limit).all()
    elif current_user.role == UserRole.RESTAURANT:
        orders = db.query(Order).filter(Order.restaurant_id == current_user.id).offset(skip).limit(limit).all()
    else:  # ADMIN
        orders = db.query(Order).offset(skip).limit(limit).all()
    
    return orders

@app.get("/orders/{order_id}", response_model=OrderModel)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check authorization
    if (current_user.role == UserRole.CUSTOMER and order.customer_id != current_user.id) or \
       (current_user.role == UserRole.RESTAURANT and order.restaurant_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return order

@app.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check authorization based on role
    if current_user.role == UserRole.CUSTOMER:
        if order.customer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this order")
        # Customers can only cancel orders
        if status != OrderStatus.CANCELLED:
            raise HTTPException(status_code=403, detail="Customers can only cancel orders")
    elif current_user.role == UserRole.RESTAURANT:
        if order.restaurant_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this order")
        # Restaurants can accept, start preparing, or mark as ready
        if status not in [OrderStatus.ACCEPTED, OrderStatus.PREPARING, OrderStatus.READY_FOR_DELIVERY, OrderStatus.CANCELLED]:
            raise HTTPException(status_code=403, detail="Invalid status for restaurant")
    
    old_status = order.status
    order.status = status
    db.commit()
    
    # Publish status update event (optional)
    try:
        message_broker = await get_message_broker()
        await message_broker.publish_event(
            f"order.{status.lower()}",
            {
                "order_id": order.id,
                "old_status": old_status,
                "new_status": status,
                "customer_id": order.customer_id,
                "restaurant_id": order.restaurant_id
            }
        )
    except Exception as e:
        print(f"Message broker error: {e}")
        # Continue without message broker
    
    return {"message": f"Order status updated to {status}"}

@app.get("/orders/{order_id}/items", response_model=List[OrderItemModel])
async def get_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check authorization
    if (current_user.role == UserRole.CUSTOMER and order.customer_id != current_user.id) or \
       (current_user.role == UserRole.RESTAURANT and order.restaurant_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    return items

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}

# Event handlers are now defined at the top of the file

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
