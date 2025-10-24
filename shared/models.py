from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    RESTAURANT = "RESTAURANT"
    DRIVER = "DRIVER"
    ADMIN = "ADMIN"

class OrderStatus(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    ACCEPTED = "ACCEPTED"
    PREPARING = "PREPARING"
    READY_FOR_DELIVERY = "READY_FOR_DELIVERY"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class DriverStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"

# User Models
class UserBase(BaseModel):
    email: str
    name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True

# Restaurant Models
class RestaurantBase(BaseModel):
    name: str
    description: str
    address: str
    phone: str
    latitude: float
    longitude: float
    is_active: bool = True

class RestaurantCreate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Menu Models
class MenuItemBase(BaseModel):
    name: str
    description: str
    price: float
    category: str
    is_available: bool = True

class MenuItemCreate(MenuItemBase):
    restaurant_id: int

class MenuItem(MenuItemBase):
    id: int
    restaurant_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Order Models
class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_id: int
    restaurant_id: int
    delivery_address: str
    delivery_latitude: float
    delivery_longitude: float
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING_PAYMENT

class OrderCreateRequest(BaseModel):
    restaurant_id: int
    delivery_address: str
    delivery_latitude: float
    delivery_longitude: float
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING_PAYMENT
    items: List[OrderItemCreate]

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []

    class Config:
        from_attributes = True

# Payment Models
class PaymentBase(BaseModel):
    order_id: int
    amount: float
    payment_method: str
    status: PaymentStatus = PaymentStatus.PENDING

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    transaction_id: str
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Driver Models
class DriverBase(BaseModel):
    user_id: int
    vehicle_type: str
    license_plate: str
    status: DriverStatus = DriverStatus.AVAILABLE
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None

class DriverCreate(DriverBase):
    pass

class Driver(DriverBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Event Models
class EventBase(BaseModel):
    event_type: str
    data: dict
    timestamp: datetime

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int

    class Config:
        from_attributes = True

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[UserRole] = None
