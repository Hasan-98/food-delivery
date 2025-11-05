from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import sys
import os
import asyncio

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database import get_db
from app.schemas import DriverSchema, DriverCreateRequest, DriverStatus
from shared.auth import get_current_user, require_role, UserRole
from services.dispatch_service import DispatchService

router = APIRouter()

@router.post("/drivers", response_model=DriverSchema)
async def create_driver(
    driver: DriverCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.DRIVER))
):
    """Create a new driver profile"""
    dispatch_service = DispatchService()
    
    try:
        db_driver = dispatch_service.create_driver(db, driver, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return db_driver

@router.get("/drivers", response_model=List[DriverSchema])
async def get_drivers(
    status: DriverStatus = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all drivers"""
    dispatch_service = DispatchService()
    drivers = dispatch_service.get_drivers(db, status)
    return drivers

@router.put("/drivers/{driver_id}/location")
async def update_driver_location(
    driver_id: int,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.DRIVER))
):
    """Update driver location"""
    dispatch_service = DispatchService()
    
    try:
        driver = dispatch_service.update_driver_location(db, driver_id, latitude, longitude)
        
        # Verify ownership
        if driver.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this driver")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"message": "Location updated successfully"}

@router.put("/drivers/{driver_id}/status")
async def update_driver_status(
    driver_id: int,
    status: DriverStatus,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.DRIVER))
):
    """Update driver status"""
    dispatch_service = DispatchService()
    
    try:
        driver = dispatch_service.update_driver_status(db, driver_id, status)
        
        # Verify ownership
        if driver.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this driver")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"message": f"Driver status updated to {status}"}

@router.get("/drivers/available")
async def get_available_drivers(
    latitude: float,
    longitude: float,
    radius: float = 10.0,
    db: Session = Depends(get_db)
):
    """Get available drivers within radius"""
    dispatch_service = DispatchService()
    nearby_drivers = dispatch_service.get_available_drivers(db, latitude, longitude, radius)
    return nearby_drivers

@router.post("/deliveries/{order_id}/assign")
async def assign_driver(
    order_id: int,
    driver_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    """Assign a driver to an order"""
    dispatch_service = DispatchService()
    
    try:
        delivery = dispatch_service.assign_driver(db, order_id, driver_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Publish driver assigned event
    await dispatch_service.publish_driver_event(
        "driver.assigned",
        {
            "order_id": order_id,
            "driver_id": driver_id,
            "assigned_at": str(asyncio.get_event_loop().time())
        }
    )
    
    return {"message": f"Driver {driver_id} assigned to order {order_id}"}

@router.post("/orders/{order_id}/assign")
async def self_assign_driver(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.DRIVER))
):
    """Driver self-assigns to an order"""
    dispatch_service = DispatchService()
    
    # Check if driver profile exists
    driver = dispatch_service.get_driver_by_user_id(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    try:
        delivery = dispatch_service.assign_driver(db, order_id, driver.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Publish driver assigned event
    await dispatch_service.publish_driver_event(
        "driver.assigned",
        {
            "order_id": order_id,
            "driver_id": driver.id,
            "assigned_at": str(asyncio.get_event_loop().time())
        }
    )
    
    return {"message": f"Driver {driver.id} assigned to order {order_id}"}

@router.post("/deliveries/{order_id}/pickup")
async def mark_pickup(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.DRIVER))
):
    """Driver marks order as picked up"""
    dispatch_service = DispatchService()
    
    # Check if driver profile exists
    driver = dispatch_service.get_driver_by_user_id(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    try:
        delivery = dispatch_service.mark_pickup(db, order_id, driver.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Publish delivery status changed event
    await dispatch_service.publish_driver_event(
        "delivery.status_changed",
        {
            "order_id": order_id,
            "driver_id": driver.id,
            "status": "PICKED_UP",
            "updated_at": str(asyncio.get_event_loop().time())
        }
    )
    
    return {"message": f"Order {order_id} marked as picked up"}

@router.post("/deliveries/{order_id}/deliver")
async def mark_delivered(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.DRIVER))
):
    """Driver marks order as delivered"""
    dispatch_service = DispatchService()
    
    # Check if driver profile exists
    driver = dispatch_service.get_driver_by_user_id(db, current_user.id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    
    try:
        delivery = dispatch_service.mark_delivered(db, order_id, driver.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Publish delivery status changed event
    await dispatch_service.publish_driver_event(
        "delivery.status_changed",
        {
            "order_id": order_id,
            "driver_id": driver.id,
            "status": "DELIVERED",
            "updated_at": str(asyncio.get_event_loop().time())
        }
    )
    
    return {"message": f"Order {order_id} marked as delivered"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dispatch-service"}

