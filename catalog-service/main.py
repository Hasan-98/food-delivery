from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from database import get_db, Restaurant, MenuItem
from models import (
    Restaurant as RestaurantModel, RestaurantCreate, 
    MenuItem as MenuItemModel, MenuItemCreate
)
from auth import get_current_user, require_role, UserRole

app = FastAPI(title="Catalog Service", version="1.0.0")

@app.post("/restaurants", response_model=RestaurantModel)
async def create_restaurant(
    restaurant: RestaurantCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    db_restaurant = Restaurant(
        name=restaurant.name,
        description=restaurant.description,
        address=restaurant.address,
        phone=restaurant.phone,
        latitude=restaurant.latitude,
        longitude=restaurant.longitude,
        owner_id=current_user.id
    )
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

@app.get("/restaurants", response_model=List[RestaurantModel])
async def get_restaurants(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Restaurant).filter(Restaurant.is_active == True)
    
    if search:
        query = query.filter(Restaurant.name.ilike(f"%{search}%"))
    
    restaurants = query.offset(skip).limit(limit).all()
    return restaurants

@app.get("/restaurants/{restaurant_id}", response_model=RestaurantModel)
async def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@app.put("/restaurants/{restaurant_id}", response_model=RestaurantModel)
async def update_restaurant(
    restaurant_id: int,
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    db_restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if db_restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this restaurant")
    
    for field, value in restaurant.dict().items():
        setattr(db_restaurant, field, value)
    
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

@app.delete("/restaurants/{restaurant_id}")
async def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    db_restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if db_restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this restaurant")
    
    db_restaurant.is_active = False
    db.commit()
    return {"message": "Restaurant deactivated"}

@app.post("/restaurants/{restaurant_id}/menu-items", response_model=MenuItemModel)
async def create_menu_item(
    restaurant_id: int,
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    # Verify restaurant ownership
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add menu items to this restaurant")
    
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

@app.get("/restaurants/{restaurant_id}/menu-items", response_model=List[MenuItemModel])
async def get_menu_items(
    restaurant_id: int,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id)
    
    if category:
        query = query.filter(MenuItem.category == category)
    
    menu_items = query.all()
    return menu_items

@app.get("/menu-items/{menu_item_id}", response_model=MenuItemModel)
async def get_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item

@app.put("/menu-items/{menu_item_id}", response_model=MenuItemModel)
async def update_menu_item(
    menu_item_id: int,
    menu_item: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    db_menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Verify restaurant ownership
    restaurant = db.query(Restaurant).filter(Restaurant.id == db_menu_item.restaurant_id).first()
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this menu item")
    
    for field, value in menu_item.dict().items():
        setattr(db_menu_item, field, value)
    
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

@app.delete("/menu-items/{menu_item_id}")
async def delete_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.RESTAURANT))
):
    db_menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Verify restaurant ownership
    restaurant = db.query(Restaurant).filter(Restaurant.id == db_menu_item.restaurant_id).first()
    if restaurant.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this menu item")
    
    db_menu_item.is_available = False
    db.commit()
    return {"message": "Menu item deactivated"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "catalog-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
