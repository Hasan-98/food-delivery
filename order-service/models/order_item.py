from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import Base

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer)
    quantity = Column(Integer)
    price = Column(Float)
    
    # Relationships
    order = relationship("Order", back_populates="items")

