"""Event handlers for dispatch service"""
from sqlalchemy.orm import Session
from datetime import datetime
import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import SessionLocal
from models.driver import Driver
from models.delivery import Delivery
from shared.models import DriverStatus
from services.dispatch_service import DispatchService
from shared.message_broker import get_message_broker

async def handle_order_ready_for_delivery(event_data):
    """Handle order ready for delivery event - assign driver"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    restaurant_id = order_data["restaurant_id"]
    
    # Get restaurant location (would typically come from catalog service)
    # For now, use mock coordinates
    restaurant_lat = 40.7128
    restaurant_lon = -74.0060
    
    db = SessionLocal()
    try:
        dispatch_service = DispatchService()
        
        # Find available drivers near restaurant
        available_drivers = db.query(Driver).filter(Driver.status == DriverStatus.AVAILABLE).all()
        
        if not available_drivers:
            # No drivers available - publish event
            message_broker = await get_message_broker()
            await message_broker.publish_event(
                "no.driver.available",
                {
                    "order_id": order_id,
                    "restaurant_id": restaurant_id
                }
            )
            return
        
        # Find closest driver
        closest_driver = None
        min_distance = float('inf')
        
        for driver in available_drivers:
            if driver.current_latitude and driver.current_longitude:
                distance = dispatch_service.calculate_distance(
                    restaurant_lat, restaurant_lon,
                    driver.current_latitude, driver.current_longitude
                )
                if distance < min_distance:
                    min_distance = distance
                    closest_driver = driver
        
        if closest_driver:
            # Assign driver
            dispatch_service.assign_driver(db, order_id, closest_driver.id)
            
            # Publish driver assigned event
            message_broker = await get_message_broker()
            await message_broker.publish_event(
                "driver.assigned",
                {
                    "order_id": order_id,
                    "driver_id": closest_driver.id,
                    "assigned_at": str(asyncio.get_event_loop().time())
                }
            )
    except Exception as e:
        print(f"Error handling order ready for delivery: {e}")
    finally:
        db.close()

