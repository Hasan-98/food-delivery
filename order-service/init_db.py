import sys
import os
sys.path.append('../shared')

from database import engine, Base, Order, OrderItem
from shared.database import engine as shared_engine, Base as SharedBase

# Create all tables using the shared engine (same database)
# All tables are now in the same metadata
Base.metadata.create_all(bind=shared_engine)

print("Order Service database tables created successfully!")
