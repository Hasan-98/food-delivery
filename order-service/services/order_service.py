from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from sqlalchemy import text
from models.order import Order
from models.order_item import OrderItem
from shared.models import OrderCreateRequest, OrderStatus

class OrderService:
    """Service for managing orders"""
    
    def create_order(
        self,
        db: Session,
        order: OrderCreateRequest,
        customer_id: int
    ) -> Order:
        """Create a new order"""
        # Validate restaurant exists
        result = db.execute(
            text("SELECT id FROM restaurants WHERE id = :restaurant_id"), 
            {"restaurant_id": order.restaurant_id}
        )
        restaurant = result.fetchone()
        
        if not restaurant:
            raise ValueError(f"Restaurant with ID {order.restaurant_id} not found")
        
        # Create order
        db_order = Order(
            customer_id=customer_id,
            restaurant_id=order.restaurant_id,
            delivery_address=order.delivery_address,
            delivery_latitude=order.delivery_latitude,
            delivery_longitude=order.delivery_longitude,
            total_amount=order.total_amount,
            status=order.status
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Create order items
        for item in order.items:
            # Validate menu item exists and belongs to the restaurant
            result = db.execute(
                text("SELECT id FROM menu_items WHERE id = :menu_item_id AND restaurant_id = :restaurant_id"), 
                {"menu_item_id": item.menu_item_id, "restaurant_id": order.restaurant_id}
            )
            menu_item = result.fetchone()
            
            if not menu_item:
                raise ValueError(f"Menu item with ID {item.menu_item_id} not found for restaurant {order.restaurant_id}")
            
            db_item = OrderItem(
                order_id=db_order.id,
                menu_item_id=item.menu_item_id,
                quantity=item.quantity,
                price=item.price
            )
            db.add(db_item)
        
        db.commit()
        return db_order
    
    def get_orders(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        restaurant_id: Optional[int] = None
    ) -> List[Order]:
        """Get orders with optional filtering"""
        query = db.query(Order).options(selectinload(Order.items))
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        if restaurant_id:
            query = query.filter(Order.restaurant_id == restaurant_id)
        
        return query.offset(skip).limit(limit).all()
    
    def get_order_by_id(self, db: Session, order_id: int) -> Optional[Order]:
        """Get order by ID with items"""
        return db.query(Order).options(selectinload(Order.items)).filter(Order.id == order_id).first()
    
    def update_order_status(
        self,
        db: Session,
        order_id: int,
        status: OrderStatus
    ) -> Optional[Order]:
        """Update order status"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        
        order.status = status
        db.commit()
        db.refresh(order)
        return order
    
    def get_order_items(self, db: Session, order_id: int) -> List[OrderItem]:
        """Get order items for an order"""
        return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

