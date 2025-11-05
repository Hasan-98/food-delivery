from sqlalchemy.orm import sessionmaker
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.database import Base, engine, SessionLocal
from models.restaurant import Restaurant
from models.menu_item import MenuItem

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
