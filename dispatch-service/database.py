from sqlalchemy.orm import sessionmaker
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.database import Base, engine, SessionLocal
from models.driver import Driver
from models.delivery import Delivery

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
