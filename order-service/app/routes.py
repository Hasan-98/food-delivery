from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database import get_db
from app.schemas import OrderSchema, OrderCreateRequest, OrderItemSchema, OrderStatus
from shared.auth import get_current_user, require_role, UserRole
from services.order_service import OrderService
from shared.message_broker import get_message_broker

router = APIRouter()

@router.post("/orders", response_model=OrderSchema)
async def create_order(
    order: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.CUSTOMER))
):
    """Create a new order"""
    order_service = OrderService()
    
    try:
        db_order = order_service.create_order(
            db=db,
            order=order,
            customer_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
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

@router.get("/orders", response_model=List[OrderSchema])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get orders"""
    order_service = OrderService()
    
    if current_user.role == UserRole.CUSTOMER:
        orders = order_service.get_orders(db, skip, limit, customer_id=current_user.id)
    elif current_user.role == UserRole.RESTAURANT:
        orders = order_service.get_orders(db, skip, limit, restaurant_id=current_user.id)
    else:  # ADMIN
        orders = order_service.get_orders(db, skip, limit)
    
    return orders

@router.get("/orders/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get order by ID"""
    order_service = OrderService()
    order = order_service.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check authorization
    if (current_user.role == UserRole.CUSTOMER and order.customer_id != current_user.id) or \
       (current_user.role == UserRole.RESTAURANT and order.restaurant_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return order

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update order status"""
    order_service = OrderService()
    order = order_service.get_order_by_id(db, order_id)
    
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
    order_service.update_order_status(db, order_id, status)
    
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

@router.get("/orders/{order_id}/items", response_model=List[OrderItemSchema])
async def get_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get order items"""
    order_service = OrderService()
    order = order_service.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check authorization
    if (current_user.role == UserRole.CUSTOMER and order.customer_id != current_user.id) or \
       (current_user.role == UserRole.RESTAURANT and order.restaurant_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    items = order_service.get_order_items(db, order_id)
    return items

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}

