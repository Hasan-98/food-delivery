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

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
    print("Order Service database tables created successfully!")

@app.post("/orders", response_model=OrderModel)
async def create_order(
    order: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.CUSTOMER))
):
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

# Event handlers for async communication
async def handle_payment_succeeded(event_data):
    """Handle payment succeeded event"""
    order_id = event_data["data"]["order_id"]
    # Update order status to confirmed
    # This would typically be done in a separate async task
    pass

async def handle_payment_failed(event_data):
    """Handle payment failed event"""
    order_id = event_data["data"]["order_id"]
    # Update order status to cancelled
    # This would typically be done in a separate async task
    pass

# Start event listeners on startup (optional)
@app.on_event("startup")
async def startup_event():
    try:
        message_broker = await get_message_broker()
        await message_broker.subscribe_to_events(
            ["payment.succeeded", "payment.failed"],
            handle_payment_succeeded if "payment.succeeded" else handle_payment_failed
        )
    except Exception as e:
        print(f"Message broker startup error: {e}")
        # Continue without message broker

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
