from sqlalchemy.orm import Session
from typing import Optional, List
from database import Restaurant, MenuItem
from app.schemas import RestaurantCreate, MenuItemCreate

class CatalogService:
    """Service for managing restaurants and menu items"""
    
    def create_restaurant(
        self, 
        db: Session, 
        restaurant: RestaurantCreate, 
        owner_id: int
    ) -> Restaurant:
        """Create a new restaurant"""
        db_restaurant = Restaurant(
            name=restaurant.name,
            description=restaurant.description,
            address=restaurant.address,
            phone=restaurant.phone,
            latitude=restaurant.latitude,
            longitude=restaurant.longitude,
            owner_id=owner_id
        )
        db.add(db_restaurant)
        db.commit()
        db.refresh(db_restaurant)
        return db_restaurant
    
    def get_restaurants(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Restaurant]:
        """Get all active restaurants"""
        query = db.query(Restaurant).filter(Restaurant.is_active == True)
        
        if search:
            query = query.filter(Restaurant.name.ilike(f"%{search}%"))
        
        return query.offset(skip).limit(limit).all()
    
    def get_restaurant_by_id(self, db: Session, restaurant_id: int) -> Optional[Restaurant]:
        """Get restaurant by ID"""
        return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    def update_restaurant(
        self, 
        db: Session, 
        restaurant_id: int, 
        restaurant: RestaurantCreate
    ) -> Optional[Restaurant]:
        """Update restaurant"""
        db_restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not db_restaurant:
            return None
        
        for field, value in restaurant.dict().items():
            setattr(db_restaurant, field, value)
        
        db.commit()
        db.refresh(db_restaurant)
        return db_restaurant
    
    def delete_restaurant(self, db: Session, restaurant_id: int) -> bool:
        """Deactivate restaurant"""
        db_restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not db_restaurant:
            return False
        
        db_restaurant.is_active = False
        db.commit()
        return True
    
    def create_menu_item(
        self, 
        db: Session, 
        restaurant_id: int, 
        menu_item: MenuItemCreate
    ) -> Optional[MenuItem]:
        """Create a new menu item"""
        # Verify restaurant exists
        restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not restaurant:
            return None
        
        db_menu_item = MenuItem(
            name=menu_item.name,
            description=menu_item.description,
            price=menu_item.price,
            category=menu_item.category,
            restaurant_id=restaurant_id,
            is_available=menu_item.is_available
        )
        db.add(db_menu_item)
        db.commit()
        db.refresh(db_menu_item)
        return db_menu_item
    
    def get_menu_items(
        self, 
        db: Session, 
        restaurant_id: int, 
        category: Optional[str] = None
    ) -> List[MenuItem]:
        """Get menu items for a restaurant"""
        query = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id)
        
        if category:
            query = query.filter(MenuItem.category == category)
        
        return query.all()
    
    def get_menu_item_by_id(self, db: Session, menu_item_id: int) -> Optional[MenuItem]:
        """Get menu item by ID"""
        return db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    
    def update_menu_item(
        self, 
        db: Session, 
        menu_item_id: int, 
        menu_item: MenuItemCreate
    ) -> Optional[MenuItem]:
        """Update menu item"""
        db_menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
        if not db_menu_item:
            return None
        
        for field, value in menu_item.dict().items():
            setattr(db_menu_item, field, value)
        
        db.commit()
        db.refresh(db_menu_item)
        return db_menu_item
    
    def delete_menu_item(self, db: Session, menu_item_id: int) -> bool:
        """Deactivate menu item"""
        db_menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
        if not db_menu_item:
            return False
        
        db_menu_item.is_available = False
        db.commit()
        return True

