"""Event handlers for reporting service"""
from sqlalchemy.orm import Session
from datetime import datetime
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import SessionLocal
from services.reporting_service import ReportingService

async def handle_all_events(event_data):
    """Handle all events for analytics"""
    event_type = event_data["event_type"]
    data = event_data["data"]
    
    db = SessionLocal()
    try:
        reporting_service = ReportingService()
        
        # Log the event
        reporting_service.log_event(db, event_type, data)
        
        # Update analytics
        reporting_service.update_analytics(db, event_type, data)
    except Exception as e:
        print(f"Error processing analytics event: {e}")
    finally:
        db.close()

