from sqlalchemy.orm import Session
from typing import List, Optional
import math
import asyncio
from models.driver import Driver
from models.delivery import Delivery
from shared.models import DriverCreateRequest, DriverStatus
from shared.message_broker import get_message_broker

class DispatchService:
    """Service for driver and delivery management"""
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def create_driver(
        self,
        db: Session,
        driver: DriverCreateRequest,
        user_id: int
    ) -> Driver:
        """Create a new driver profile"""
        # Check if driver already exists
        existing_driver = db.query(Driver).filter(Driver.user_id == user_id).first()
        if existing_driver:
            raise ValueError("Driver profile already exists")
        
        db_driver = Driver(
            user_id=user_id,
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
    
    def get_drivers(
        self,
        db: Session,
        status: Optional[DriverStatus] = None
    ) -> List[Driver]:
        """Get all drivers, optionally filtered by status"""
        query = db.query(Driver)
        if status:
            query = query.filter(Driver.status == status)
        return query.all()
    
    def get_driver_by_id(self, db: Session, driver_id: int) -> Optional[Driver]:
        """Get driver by ID"""
        return db.query(Driver).filter(Driver.id == driver_id).first()
    
    def get_driver_by_user_id(self, db: Session, user_id: int) -> Optional[Driver]:
        """Get driver by user ID"""
        return db.query(Driver).filter(Driver.user_id == user_id).first()
    
    def update_driver_location(
        self,
        db: Session,
        driver_id: int,
        latitude: float,
        longitude: float
    ) -> Driver:
        """Update driver location"""
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            raise ValueError("Driver not found")
        
        driver.current_latitude = latitude
        driver.current_longitude = longitude
        db.commit()
        db.refresh(driver)
        return driver
    
    def update_driver_status(
        self,
        db: Session,
        driver_id: int,
        status: DriverStatus
    ) -> Driver:
        """Update driver status"""
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            raise ValueError("Driver not found")
        
        driver.status = status
        db.commit()
        db.refresh(driver)
        return driver
    
    def get_available_drivers(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius: float = 10.0
    ) -> List[dict]:
        """Get available drivers within radius"""
        available_drivers = db.query(Driver).filter(Driver.status == DriverStatus.AVAILABLE).all()
        
        nearby_drivers = []
        for driver in available_drivers:
            if driver.current_latitude and driver.current_longitude:
                distance = self.calculate_distance(
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
    
    def assign_driver(
        self,
        db: Session,
        order_id: int,
        driver_id: int
    ) -> Delivery:
        """Assign a driver to an order"""
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if not driver:
            raise ValueError("Driver not found")
        
        if driver.status != DriverStatus.AVAILABLE:
            raise ValueError("Driver is not available")
        
        # Check if order is already assigned
        existing_delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
        if existing_delivery:
            raise ValueError("Order already assigned to a driver")
        
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
        db.refresh(delivery)
        return delivery
    
    def mark_pickup(
        self,
        db: Session,
        order_id: int,
        driver_id: int
    ) -> Delivery:
        """Mark order as picked up"""
        delivery = db.query(Delivery).filter(
            Delivery.order_id == order_id,
            Delivery.driver_id == driver_id
        ).first()
        
        if not delivery:
            raise ValueError("Delivery not found or not assigned to this driver")
        
        if delivery.status != "ASSIGNED":
            raise ValueError("Delivery is not in ASSIGNED status")
        
        from datetime import datetime
        delivery.status = "PICKED_UP"
        delivery.picked_up_at = datetime.utcnow()
        db.commit()
        db.refresh(delivery)
        return delivery
    
    def mark_delivered(
        self,
        db: Session,
        order_id: int,
        driver_id: int
    ) -> Delivery:
        """Mark order as delivered"""
        delivery = db.query(Delivery).filter(
            Delivery.order_id == order_id,
            Delivery.driver_id == driver_id
        ).first()
        
        if not delivery:
            raise ValueError("Delivery not found or not assigned to this driver")
        
        if delivery.status != "PICKED_UP":
            raise ValueError("Delivery is not in PICKED_UP status")
        
        from datetime import datetime
        delivery.status = "DELIVERED"
        delivery.delivered_at = datetime.utcnow()
        
        # Update driver status back to available
        driver = db.query(Driver).filter(Driver.id == driver_id).first()
        if driver:
            driver.status = DriverStatus.AVAILABLE
        
        db.commit()
        db.refresh(delivery)
        return delivery
    
    async def publish_driver_event(self, event_type: str, event_data: dict):
        """Publish driver/delivery event"""
        try:
            message_broker = await get_message_broker()
            await message_broker.publish_event(event_type, event_data)
        except Exception as e:
            print(f"Message broker error: {e}")

