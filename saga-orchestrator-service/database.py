from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.database import Base, engine, SessionLocal
from models.saga_instance import SagaInstance
from models.saga_step import SagaStep

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

