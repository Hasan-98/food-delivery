from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict
from datetime import datetime
from models.event_log import EventLog
from models.order_analytics import OrderAnalytics
from models.customer_analytics import CustomerAnalytics
from models.restaurant_analytics import RestaurantAnalytics
from models.driver_analytics import DriverAnalytics
import json

class ReportingService:
    """Service for analytics and reporting"""
    
    def get_active_counts(self, db: Session) -> Dict[str, int]:
        """Get total active customers, restaurants, and drivers"""
        customers = db.execute(
            text("SELECT COUNT(*) FROM users WHERE role = 'CUSTOMER' AND is_active = true")
        ).scalar() or 0
        
        restaurants = db.execute(
            text("SELECT COUNT(*) FROM restaurants")
        ).scalar() or 0
        
        drivers = db.execute(
            text("SELECT COUNT(*) FROM drivers")
        ).scalar() or 0
        
        return {
            "active_customers": int(customers),
            "active_restaurants": int(restaurants),
            "active_drivers": int(drivers)
        }
    
    def get_customer_history(
        self,
        db: Session,
        customer_id: int,
        skip: int = 0,
        limit: int = 100,
        customer_name: Optional[str] = None
    ) -> Dict:
        """Get detailed history of all orders placed by a customer"""
        if customer_name:
            user_row = db.execute(
                text("SELECT id FROM users WHERE id = :cid AND name ILIKE :name"),
                {"cid": customer_id, "name": f"%{customer_name}%"}
            ).fetchone()
            if not user_row:
                return {"customer_id": customer_id, "orders": [], "total_orders": 0}
        
        orders_rows = db.execute(text("""
            SELECT id, restaurant_id, total_amount, status, created_at, delivery_address
            FROM orders 
            WHERE customer_id = :customer_id 
            ORDER BY created_at DESC 
            OFFSET :skip LIMIT :limit
        """), {"customer_id": customer_id, "skip": skip, "limit": limit}).fetchall()
        
        total_count = db.execute(text("""
            SELECT COUNT(*) FROM orders WHERE customer_id = :customer_id
        """), {"customer_id": customer_id}).scalar()
        
        orders = [
            {
                "id": row.id,
                "restaurant_id": row.restaurant_id,
                "total_amount": float(row.total_amount),
                "status": row.status,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "delivery_address": row.delivery_address
            }
            for row in orders_rows
        ]
        
        return {
            "customer_id": customer_id,
            "orders": orders,
            "total_orders": int(total_count) if total_count else 0
        }
    
    def get_top_customers(self, db: Session, limit: int = 5) -> Dict:
        """Get top customers with highest order frequency"""
        rows = db.execute(text("""
            SELECT customer_id, 
                   COUNT(*) as total_orders,
                   SUM(total_amount) as total_spent,
                   MAX(created_at) as last_order_date
            FROM orders 
            GROUP BY customer_id 
            ORDER BY COUNT(*) DESC 
            LIMIT :limit
        """), {"limit": limit}).fetchall()
        
        top_customers = [
            {
                "customer_id": row.customer_id,
                "total_orders": int(row.total_orders),
                "total_spent": float(row.total_spent) if row.total_spent else 0.0,
                "last_order_date": row.last_order_date.isoformat() if row.last_order_date else None
            }
            for row in rows
        ]
        
        return {"top_customers": top_customers, "limit": limit}
    
    def get_restaurant_orders(
        self,
        db: Session,
        restaurant_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get number of orders received and fulfilled by a restaurant"""
        query = db.query(OrderAnalytics).filter(OrderAnalytics.restaurant_id == restaurant_id)
        
        if start_date:
            query = query.filter(OrderAnalytics.created_at >= start_date)
        if end_date:
            query = query.filter(OrderAnalytics.created_at <= end_date)
        
        orders = query.all()
        
        total_orders = len(orders)
        fulfilled_orders = len([o for o in orders if o.status == "DELIVERED"])
        
        return {
            "restaurant_id": restaurant_id,
            "period": {"start_date": start_date, "end_date": end_date},
            "total_orders": total_orders,
            "fulfilled_orders": fulfilled_orders,
            "fulfillment_rate": (fulfilled_orders / total_orders * 100) if total_orders > 0 else 0
        }
    
    def get_restaurant_revenue(
        self,
        db: Session,
        restaurant_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get breakdown of total revenue generated by a restaurant"""
        query = db.query(OrderAnalytics).filter(
            OrderAnalytics.restaurant_id == restaurant_id,
            OrderAnalytics.status == "DELIVERED"
        )
        
        if start_date:
            query = query.filter(OrderAnalytics.created_at >= start_date)
        if end_date:
            query = query.filter(OrderAnalytics.created_at <= end_date)
        
        orders = query.all()
        total_revenue = sum(order.total_amount for order in orders)
        
        return {
            "restaurant_id": restaurant_id,
            "period": {"start_date": start_date, "end_date": end_date},
            "total_revenue": total_revenue,
            "order_count": len(orders)
        }
    
    def get_popular_menu_items(self, db: Session, limit: int = 10) -> Dict:
        """Get most ordered menu items across all restaurants"""
        rows = db.execute(text("""
            SELECT mi.name AS item_name,
                   COUNT(oi.id) AS order_count,
                   r.name AS restaurant
            FROM order_items oi
            JOIN menu_items mi ON mi.id = oi.menu_item_id
            JOIN restaurants r ON r.id = mi.restaurant_id
            GROUP BY mi.name, r.name
            ORDER BY COUNT(oi.id) DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()
        
        popular = [
            {"item_name": row.item_name, "order_count": int(row.order_count), "restaurant": row.restaurant}
            for row in rows
        ]
        return {"popular_items": popular, "limit": limit}
    
    def get_order_status_distribution(self, db: Session) -> Dict:
        """Get distribution of order statuses"""
        rows = db.execute(text("SELECT status, COUNT(*) AS c FROM orders GROUP BY status")).fetchall()
        return {"status_distribution": {row.status: int(row.c) for row in rows}}
    
    def get_driver_deliveries(self, db: Session, driver_id: int) -> Dict:
        """Get number of deliveries completed by a driver"""
        row = db.execute(text(
            "SELECT COUNT(*) AS deliveries FROM deliveries WHERE driver_id = :did AND status = 'DELIVERED'"
        ), {"did": driver_id}).fetchone()
        
        deliveries = int(row.deliveries) if row and row.deliveries is not None else 0
        return {"driver_id": driver_id, "total_deliveries": deliveries}
    
    def get_cancelled_orders(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get details of cancelled orders and total amount"""
        query = db.query(OrderAnalytics).filter(OrderAnalytics.status == "CANCELLED")
        
        if start_date:
            query = query.filter(OrderAnalytics.created_at >= start_date)
        if end_date:
            query = query.filter(OrderAnalytics.created_at <= end_date)
        
        cancelled_orders = query.all()
        total_cancelled_amount = sum(order.total_amount for order in cancelled_orders)
        
        return {
            "cancelled_orders": cancelled_orders,
            "total_cancelled_amount": total_cancelled_amount,
            "order_count": len(cancelled_orders)
        }
    
    def get_average_order_value(
        self,
        db: Session,
        customer_id: Optional[int] = None,
        restaurant_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Calculate average order value"""
        query = db.query(OrderAnalytics).filter(OrderAnalytics.status == "DELIVERED")
        
        if customer_id:
            query = query.filter(OrderAnalytics.customer_id == customer_id)
        if restaurant_id:
            query = query.filter(OrderAnalytics.restaurant_id == restaurant_id)
        if start_date:
            query = query.filter(OrderAnalytics.created_at >= start_date)
        if end_date:
            query = query.filter(OrderAnalytics.created_at <= end_date)
        
        orders = query.all()
        
        if not orders:
            return {"average_order_value": 0.0, "order_count": 0}
        
        total_amount = sum(order.total_amount for order in orders)
        average_value = total_amount / len(orders)
        
        return {
            "average_order_value": average_value,
            "order_count": len(orders),
            "total_amount": total_amount
        }
    
    def get_peak_times(self, db: Session, granularity: str = "day") -> Dict:
        """Get peak times for orders"""
        if granularity == "day":
            rows = db.execute(text("""
                SELECT to_char(date_trunc('hour', created_at), 'HH24:00') AS hour,
                       COUNT(*) AS order_count
                FROM orders
                GROUP BY 1
                ORDER BY order_count DESC
                LIMIT 5
            """)).fetchall()
            return {
                "granularity": "day",
                "peak_times": [{"time": r.hour, "order_count": int(r.order_count)} for r in rows]
            }
        elif granularity == "week":
            rows = db.execute(text(
                "SELECT to_char(created_at, 'Day') AS day, COUNT(*) AS order_count FROM orders GROUP BY 1 ORDER BY order_count DESC LIMIT 3"
            )).fetchall()
            return {
                "granularity": "week",
                "peak_days": [{"day": r.day.strip(), "order_count": int(r.order_count)} for r in rows]
            }
        elif granularity == "month":
            rows = db.execute(text(
                "SELECT to_char(date_trunc('week', created_at), 'YYYY-MM-DD') AS week, COUNT(*) AS order_count FROM orders GROUP BY 1 ORDER BY order_count DESC LIMIT 3"
            )).fetchall()
            return {
                "granularity": "month",
                "peak_weeks": [{"week": r.week, "order_count": int(r.order_count)} for r in rows]
            }
        elif granularity == "year":
            rows = db.execute(text(
                "SELECT to_char(created_at, 'Mon') AS month, COUNT(*) AS order_count FROM orders GROUP BY 1 ORDER BY order_count DESC LIMIT 5"
            )).fetchall()
            return {
                "granularity": "year",
                "peak_months": [{"month": r.month, "order_count": int(r.order_count)} for r in rows]
            }
        return {"granularity": granularity, "data": []}
    
    def log_event(
        self,
        db: Session,
        event_type: str,
        data: dict
    ):
        """Log an event"""
        event_log = EventLog(
            event_type=event_type,
            order_id=data.get("order_id"),
            user_id=data.get("customer_id"),
            restaurant_id=data.get("restaurant_id"),
            driver_id=data.get("driver_id"),
            data=json.dumps(data)
        )
        db.add(event_log)
        db.commit()
    
    def update_analytics(
        self,
        db: Session,
        event_type: str,
        data: dict
    ):
        """Update analytics based on event type"""
        if event_type == "order.created":
            # Update order analytics
            order_analytics = OrderAnalytics(
                order_id=data["order_id"],
                customer_id=data["customer_id"],
                restaurant_id=data["restaurant_id"],
                total_amount=data["total_amount"],
                status="PENDING_PAYMENT"
            )
            db.add(order_analytics)
            db.commit()
            
            # Update customer analytics
            customer_analytics = db.query(CustomerAnalytics).filter(
                CustomerAnalytics.customer_id == data["customer_id"]
            ).first()
            
            if not customer_analytics:
                customer_analytics = CustomerAnalytics(customer_id=data["customer_id"])
                db.add(customer_analytics)
            
            customer_analytics.total_orders += 1
            customer_analytics.total_spent += data.get("total_amount", 0)
            customer_analytics.last_order_date = datetime.utcnow()
            db.commit()
            
            # Update restaurant analytics
            restaurant_analytics = db.query(RestaurantAnalytics).filter(
                RestaurantAnalytics.restaurant_id == data["restaurant_id"]
            ).first()
            
            if not restaurant_analytics:
                restaurant_analytics = RestaurantAnalytics(restaurant_id=data["restaurant_id"])
                db.add(restaurant_analytics)
            
            restaurant_analytics.total_orders += 1
            restaurant_analytics.total_revenue += data.get("total_amount", 0)
            restaurant_analytics.last_order_date = datetime.utcnow()
            db.commit()
        
        elif event_type == "order.delivered":
            # Update completed order analytics
            order_analytics = db.query(OrderAnalytics).filter(
                OrderAnalytics.order_id == data["order_id"]
            ).first()
            if order_analytics:
                order_analytics.status = "DELIVERED"
                order_analytics.completed_at = datetime.utcnow()
                db.commit()
            
            # Update driver analytics
            if "driver_id" in data:
                driver_analytics = db.query(DriverAnalytics).filter(
                    DriverAnalytics.driver_id == data["driver_id"]
                ).first()
                
                if not driver_analytics:
                    driver_analytics = DriverAnalytics(driver_id=data["driver_id"])
                    db.add(driver_analytics)
                
                driver_analytics.total_deliveries += 1
                driver_analytics.total_earnings += data.get("delivery_fee", 0)
                driver_analytics.last_delivery_date = datetime.utcnow()
                db.commit()

