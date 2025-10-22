from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import sys
import os
import asyncio
import json
import math

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from database import get_db, Driver, Delivery
from models import Driver as DriverModel, DriverCreate, DriverStatus, UserRole
from auth import get_current_user, require_role
from message_broker import get_message_broker

app = FastAPI(title="Dispatch Service", version="1.0.0")

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

@app.post("/drivers", response_model=DriverModel)
async def create_driver(
    driver: DriverCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.DRIVER))
):
    # Check if driver already exists
    existing_driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if existing_driver:
        raise HTTPException(status_code=400, detail="Driver profile already exists")
    
    db_driver = Driver(
        user_id=current_user.id,
        vehicle_type=driver.vehicle_type,
        license_plate=driver.license_plate,
        status=driver.status,
        current_latitude=driver.current_latitude,
        current_longitude=driver.current_longitude
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

@app.get("/drivers", response_model=List[DriverModel])
async def get_drivers(
    status: DriverStatus = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Driver)
    if status:
        query = query.filter(Driver.status == status)
    drivers = query.all()
    return drivers

@app.put("/drivers/{driver_id}/location")
async def update_driver_location(
    driver_id: int,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.DRIVER))
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    if driver.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this driver")
    
    driver.current_latitude = latitude
    driver.current_longitude = longitude
    db.commit()
    
    return {"message": "Location updated successfully"}

@app.put("/drivers/{driver_id}/status")
async def update_driver_status(
    driver_id: int,
    status: DriverStatus,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.DRIVER))
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    if driver.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this driver")
    
    driver.status = status
    db.commit()
    
    return {"message": f"Driver status updated to {status}"}

@app.get("/drivers/available")
async def get_available_drivers(
    latitude: float,
    longitude: float,
    radius: float = 10.0,  # 10km radius
    db: Session = Depends(get_db)
):
    """Get available drivers within radius"""
    available_drivers = db.query(Driver).filter(Driver.status == DriverStatus.AVAILABLE).all()
    
    nearby_drivers = []
    for driver in available_drivers:
        if driver.current_latitude and driver.current_longitude:
            distance = calculate_distance(
                latitude, longitude,
                driver.current_latitude, driver.current_longitude
            )
            if distance <= radius:
                nearby_drivers.append({
                    "driver": driver,
                    "distance": distance
                })
    
    # Sort by distance
    nearby_drivers.sort(key=lambda x: x["distance"])
    
    return nearby_drivers

@app.post("/deliveries/{order_id}/assign")
async def assign_driver(
    order_id: int,
    driver_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    """Assign a driver to an order"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    if driver.status != DriverStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Driver is not available")
    
    # Create delivery record
    delivery = Delivery(
        order_id=order_id,
        driver_id=driver_id,
        status="ASSIGNED"
    )
    db.add(delivery)
    
    # Update driver status
    driver.status = DriverStatus.BUSY
    db.commit()
    
    # Publish driver assigned event
    message_broker = await get_message_broker()
    await message_broker.publish_event(
        "driver.assigned",
        {
            "order_id": order_id,
            "driver_id": driver_id,
            "assigned_at": str(asyncio.get_event_loop().time())
        }
    )
    
    return {"message": f"Driver {driver_id} assigned to order {order_id}"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dispatch-service"}

# Event handlers for async communication
async def handle_order_ready_for_delivery(event_data):
    """Handle order ready for delivery event - assign driver"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    restaurant_id = order_data["restaurant_id"]
    
    # Get restaurant location (would typically come from catalog service)
    # For now, use mock coordinates
    restaurant_lat = 40.7128
    restaurant_lon = -74.0060
    
    # Find available drivers near restaurant
    db = next(get_db())
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
            distance = calculate_distance(
                restaurant_lat, restaurant_lon,
                driver.current_latitude, driver.current_longitude
            )
            if distance < min_distance:
                min_distance = distance
                closest_driver = driver
    
    if closest_driver:
        # Assign driver
        delivery = Delivery(
            order_id=order_id,
            driver_id=closest_driver.id,
            status="ASSIGNED"
        )
        db.add(delivery)
        
        closest_driver.status = DriverStatus.BUSY
        db.commit()
        
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

# Start event listeners on startup
@app.on_event("startup")
async def startup_event():
    message_broker = await get_message_broker()
    await message_broker.subscribe_to_events(
        ["order.ready_for_delivery"],
        handle_order_ready_for_delivery
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
