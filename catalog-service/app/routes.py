from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database import get_db
from app.schemas import Restaurant, RestaurantCreate, MenuItem, MenuItemCreate
from shared.auth import require_role, UserRole
from services.catalog_service import CatalogService

router = APIRouter()

@router.post("/restaurants", response_model=Restaurant)
async def create_restaurant(
    restaurant: RestaurantCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Create a new restaurant"""
    catalog_service = CatalogService()
    db_restaurant = catalog_service.create_restaurant(
        db=db,
        restaurant=restaurant,
        owner_id=current_user.id
    )
    return db_restaurant

@router.get("/restaurants", response_model=List[Restaurant])
async def get_restaurants(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all active restaurants"""
    catalog_service = CatalogService()
    restaurants = catalog_service.get_restaurants(
        db=db,
        skip=skip,
        limit=limit,
        search=search
    )
    return restaurants

@router.get("/restaurants/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """Get restaurant by ID"""
    catalog_service = CatalogService()
    restaurant = catalog_service.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@router.put("/restaurants/{restaurant_id}", response_model=Restaurant)
async def update_restaurant(
    restaurant_id: int,
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Update restaurant"""
    catalog_service = CatalogService()
    
    # Verify ownership
    db_restaurant = catalog_service.get_restaurant_by_id(db, restaurant_id)
    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if db_restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this restaurant")
    
    updated_restaurant = catalog_service.update_restaurant(
        db=db,
        restaurant_id=restaurant_id,
        restaurant=restaurant
    )
    return updated_restaurant

@router.delete("/restaurants/{restaurant_id}")
async def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Deactivate restaurant"""
    catalog_service = CatalogService()
    
    # Verify ownership
    db_restaurant = catalog_service.get_restaurant_by_id(db, restaurant_id)
    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if db_restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this restaurant")
    
    catalog_service.delete_restaurant(db, restaurant_id)
    return {"message": "Restaurant deactivated"}

@router.post("/restaurants/{restaurant_id}/menu-items", response_model=MenuItem)
async def create_menu_item(
    restaurant_id: int,
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Create a new menu item"""
    catalog_service = CatalogService()
    
    # Verify restaurant ownership
    restaurant = catalog_service.get_restaurant_by_id(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add menu items to this restaurant")
    
    db_menu_item = catalog_service.create_menu_item(
        db=db,
        restaurant_id=restaurant_id,
        menu_item=menu_item
    )
    return db_menu_item

@router.get("/restaurants/{restaurant_id}/menu-items", response_model=List[MenuItem])
async def get_menu_items(
    restaurant_id: int,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get menu items for a restaurant"""
    catalog_service = CatalogService()
    menu_items = catalog_service.get_menu_items(
        db=db,
        restaurant_id=restaurant_id,
        category=category
    )
    return menu_items

@router.get("/menu-items/{menu_item_id}", response_model=MenuItem)
async def get_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    """Get menu item by ID"""
    catalog_service = CatalogService()
    menu_item = catalog_service.get_menu_item_by_id(db, menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@router.put("/menu-items/{menu_item_id}", response_model=MenuItem)
async def update_menu_item(
    menu_item_id: int,
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Update menu item"""
    catalog_service = CatalogService()
    
    db_menu_item = catalog_service.get_menu_item_by_id(db, menu_item_id)
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Verify restaurant ownership
    restaurant = catalog_service.get_restaurant_by_id(db, db_menu_item.restaurant_id)
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this menu item")
    
    updated_item = catalog_service.update_menu_item(
        db=db,
        menu_item_id=menu_item_id,
        menu_item=menu_item
    )
    return updated_item

@router.delete("/menu-items/{menu_item_id}")
async def delete_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    """Deactivate menu item"""
    catalog_service = CatalogService()
    
    db_menu_item = catalog_service.get_menu_item_by_id(db, menu_item_id)
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Verify restaurant ownership
    restaurant = catalog_service.get_restaurant_by_id(db, db_menu_item.restaurant_id)
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this menu item")
    
    catalog_service.delete_menu_item(db, menu_item_id)
    return {"message": "Menu item deactivated"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "catalog-service"}

