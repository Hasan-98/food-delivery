"""Event handlers for restaurant service"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

async def handle_order_confirmed(event_data):
    """Handle order confirmed event - notify restaurant"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    restaurant_id = order_data["restaurant_id"]
    
    # Log the order confirmation
    print(f"Order {order_id} confirmed for restaurant {restaurant_id}")
    
    # In a real system, this would send a notification to the restaurant
    # For now, we'll just log it

