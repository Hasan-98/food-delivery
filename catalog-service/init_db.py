from database import engine, Base, Restaurant, MenuItem
from shared.database import engine as shared_engine, Base as SharedBase
from shared.models import User

# Create all tables using the shared engine (same database)
# All tables are now in the same metadata
Base.metadata.create_all(bind=shared_engine)

print("Database tables created successfully!")
