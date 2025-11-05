from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import sys
import os
import asyncio

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database import get_db
from shared.auth import require_role, UserRole
from shared.models import OrderStatus
from services.restaurant_service import RestaurantService

router = APIRouter()

@router.get("/orders/pending")
async def get_pending_orders(
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Get pending orders for the restaurant"""
    restaurant_service = RestaurantService()
    orders = restaurant_service.get_pending_orders(db, current_user.id)
    return orders

@router.post("/orders/{order_id}/accept")
async def accept_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Accept an order"""
    restaurant_service = RestaurantService()
    
    try:
        order = restaurant_service.accept_order(db, order_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Publish order accepted event
    await restaurant_service.publish_order_event(
        "order.accepted",
        order_id,
        current_user.id,
        accepted_at=str(asyncio.get_event_loop().time())
    )
    
    return {"message": f"Order {order_id} accepted"}

@router.post("/orders/{order_id}/start-preparing")
async def start_preparing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Start preparing an order"""
    restaurant_service = RestaurantService()
    
    try:
        order = restaurant_service.start_preparing(db, order_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Publish order preparing event
    await restaurant_service.publish_order_event(
        "order.preparing",
        order_id,
        current_user.id,
        started_at=str(asyncio.get_event_loop().time())
    )
    
    return {"message": f"Order {order_id} preparation started"}

@router.post("/orders/{order_id}/ready")
async def mark_order_ready(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Mark order as ready for delivery"""
    restaurant_service = RestaurantService()
    
    try:
        order = restaurant_service.mark_ready(db, order_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Publish order ready event
    await restaurant_service.publish_order_event(
        "order.ready_for_delivery",
        order_id,
        current_user.id,
        ready_at=str(asyncio.get_event_loop().time())
    )
    
    return {"message": f"Order {order_id} is ready for delivery"}

@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Cancel an order"""
    restaurant_service = RestaurantService()
    
    try:
        order = restaurant_service.cancel_order(db, order_id, current_user.id, reason)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Publish order cancelled event
    await restaurant_service.publish_order_event(
        "order.cancelled",
        order_id,
        current_user.id,
        cancelled_at=str(asyncio.get_event_loop().time()),
        reason=reason
    )
    
    return {"message": f"Order {order_id} cancelled"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "restaurant-service"}

