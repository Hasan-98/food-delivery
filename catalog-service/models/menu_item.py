from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    is_available: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItem(MenuItemBase):
    id: int
    restaurant_id: int
    created_at: datetime

    class Config:
        from_attributes = True
