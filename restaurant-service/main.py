from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import sys
import os
import asyncio
import json

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.models import UserRole, OrderStatus
from shared.auth import get_current_user, require_role
from shared.message_broker import get_message_broker
from database import get_db

app = FastAPI(title="Restaurant Service", version="1.0.0")

@app.get("/orders/pending")
async def get_pending_orders(
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Get pending orders for the restaurant"""
    # This would typically query the order service
    # For now, return mock data
    return {
        "message": "This would return pending orders for the restaurant",
        "restaurant_id": current_user.id
    }

@app.post("/orders/{order_id}/accept")
async def accept_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Accept an order"""
    # Publish order accepted event
    try:
        message_broker = await get_message_broker()
        await message_broker.publish_event(
            "order.accepted",
            {
                "order_id": order_id,
                "restaurant_id": current_user.id,
                "accepted_at": str(asyncio.get_event_loop().time())
            }
        )
    except Exception as e:
        print(f"Message broker error: {e}")
    
    return {"message": f"Order {order_id} accepted"}

@app.post("/orders/{order_id}/start-preparing")
async def start_preparing_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Start preparing an order"""
    # Publish order preparing event
    try:
        message_broker = await get_message_broker()
        await message_broker.publish_event(
            "order.preparing",
            {
                "order_id": order_id,
                "restaurant_id": current_user.id,
                "started_at": str(asyncio.get_event_loop().time())
            }
        )
    except Exception as e:
        print(f"Message broker error: {e}")
    
    return {"message": f"Order {order_id} preparation started"}

@app.post("/orders/{order_id}/ready")
async def mark_order_ready(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Mark order as ready for delivery"""
    # Publish order ready event
    try:
        message_broker = await get_message_broker()
        await message_broker.publish_event(
            "order.ready_for_delivery",
            {
                "order_id": order_id,
                "restaurant_id": current_user.id,
                "ready_at": str(asyncio.get_event_loop().time())
            }
        )
    except Exception as e:
        print(f"Message broker error: {e}")
    
    return {"message": f"Order {order_id} is ready for delivery"}

@app.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Cancel an order"""
    # Publish order cancelled event
    try:
        message_broker = await get_message_broker()
        await message_broker.publish_event(
            "order.cancelled",
            {
                "order_id": order_id,
                "restaurant_id": current_user.id,
                "cancelled_at": str(asyncio.get_event_loop().time()),
                "reason": reason
            }
        )
    except Exception as e:
        print(f"Message broker error: {e}")
    
    return {"message": f"Order {order_id} cancelled"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "restaurant-service"}

# Event handlers for async communication
async def handle_order_confirmed(event_data):
    """Handle order confirmed event - notify restaurant"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    restaurant_id = order_data["restaurant_id"]
    
    # Log the order confirmation
    print(f"Order {order_id} confirmed for restaurant {restaurant_id}")
    
    # In a real system, this would send a notification to the restaurant
    # For now, we'll just log it

# Start event listeners on startup
@app.on_event("startup")
async def startup_event():
    try:
        message_broker = await get_message_broker()
        await message_broker.subscribe_to_events(
            ["order.confirmed"],
            handle_order_confirmed
        )
    except Exception as e:
        print(f"Message broker subscription error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
