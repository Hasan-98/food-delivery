# Reporting Service uses custom schemas for reports
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ActiveCounts(BaseModel):
    active_customers: int
    active_restaurants: int
    active_drivers: int

class OrderHistoryItem(BaseModel):
    id: int
    restaurant_id: int
    total_amount: float
    status: str
    created_at: Optional[datetime]
    delivery_address: Optional[str]

class CustomerHistory(BaseModel):
    customer_id: int
    orders: List[OrderHistoryItem]
    total_orders: int

class TopCustomer(BaseModel):
    customer_id: int
    total_orders: int
    total_spent: float
    last_order_date: Optional[datetime]

class TopCustomers(BaseModel):
    top_customers: List[TopCustomer]
    limit: int

class RestaurantOrders(BaseModel):
    restaurant_id: int
    period: Dict[str, Optional[datetime]]
    total_orders: int
    fulfilled_orders: int
    fulfillment_rate: float

class RestaurantRevenue(BaseModel):
    restaurant_id: int
    period: Dict[str, Optional[datetime]]
    total_revenue: float
    order_count: int

class PopularMenuItem(BaseModel):
    item_name: str
    order_count: int
    restaurant: str

class PopularMenuItems(BaseModel):
    popular_items: List[PopularMenuItem]
    limit: int

class StatusDistribution(BaseModel):
    status_distribution: Dict[str, int]

class DriverDeliveries(BaseModel):
    driver_id: int
    total_deliveries: int

class CancelledOrders(BaseModel):
    cancelled_orders: List
    total_cancelled_amount: float
    order_count: int

class AverageOrderValue(BaseModel):
    average_order_value: float
    order_count: int
    total_amount: float

class PeakTime(BaseModel):
    time: str
    order_count: int

class PeakTimes(BaseModel):
    granularity: str
    peak_times: Optional[List[PeakTime]] = None
    peak_days: Optional[List[Dict]] = None
    peak_weeks: Optional[List[Dict]] = None
    peak_months: Optional[List[Dict]] = None

