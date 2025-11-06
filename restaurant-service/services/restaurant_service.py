from sqlalchemy.orm import Session
from typing import List
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import SessionLocal
from shared.models import OrderStatus, Order
from shared.message_broker import get_message_broker
import asyncio

class RestaurantService:
    """Service for restaurant order management"""
    
    def get_pending_orders(self, db: Session, restaurant_id: int) -> List[Order]:
        """Get pending orders for a restaurant"""
        return db.query(Order).filter(
            Order.restaurant_id == restaurant_id, 
            Order.status == OrderStatus.PENDING
        ).all()
    
    def accept_order(self, db: Session, order_id: int, restaurant_id: int) -> Order:
        """Accept an order"""
        order = db.query(Order).filter(
            Order.id == order_id, 
            Order.restaurant_id == restaurant_id
        ).first()
        
        if not order:
            raise ValueError("Order not found")
        
        order.status = OrderStatus.ACCEPTED
        db.commit()
        db.refresh(order)
        return order
    
    def accept_order_internal(self, db: Session, order_id: int) -> Order:
        """Accept an order (internal endpoint for saga orchestrator)"""
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            raise ValueError("Order not found")
        
        if not order.restaurant_id:
            raise ValueError("Order has no restaurant_id")
        
        order.status = OrderStatus.ACCEPTED
        db.commit()
        db.refresh(order)
        return order
    
    def start_preparing(self, db: Session, order_id: int, restaurant_id: int) -> Order:
        """Start preparing an order"""
        order = db.query(Order).filter(
            Order.id == order_id, 
            Order.restaurant_id == restaurant_id
        ).first()
        
        if not order:
            raise ValueError("Order not found")
        
        order.status = OrderStatus.PREPARING
        db.commit()
        db.refresh(order)
        return order
    
    def mark_ready(self, db: Session, order_id: int, restaurant_id: int) -> Order:
        """Mark order as ready for delivery"""
        order = db.query(Order).filter(
            Order.id == order_id, 
            Order.restaurant_id == restaurant_id
        ).first()
        
        if not order:
            raise ValueError("Order not found")
        
        order.status = OrderStatus.READY_FOR_DELIVERY
        db.commit()
        db.refresh(order)
        return order
    
    def cancel_order(self, db: Session, order_id: int, restaurant_id: int, reason: str) -> Order:
        """Cancel an order"""
        order = db.query(Order).filter(
            Order.id == order_id, 
            Order.restaurant_id == restaurant_id
        ).first()
        
        if not order:
            raise ValueError("Order not found")
        
        order.status = OrderStatus.CANCELLED
        db.commit()
        db.refresh(order)
        return order
    
    async def publish_order_event(self, event_type: str, order_id: int, restaurant_id: int, **kwargs):
        """Publish order event"""
        try:
            message_broker = await get_message_broker()
            event_data = {
                "order_id": order_id,
                "restaurant_id": restaurant_id,
                **kwargs
            }
            await message_broker.publish_event(event_type, event_data)
        except Exception as e:
            print(f"Message broker error: {e}")

