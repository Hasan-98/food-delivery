from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RestaurantBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    phone: str
    latitude: float
    longitude: float

class RestaurantCreate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    id: int
    owner_id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True
