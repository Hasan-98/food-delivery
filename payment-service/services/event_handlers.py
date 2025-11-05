"""Event handlers for payment service"""
from sqlalchemy.orm import Session
from datetime import datetime
import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.database import SessionLocal
from models.payment import Payment
from shared.models import PaymentCreate, PaymentStatus
from services.payment_service import PaymentService

async def handle_order_created(event_data):
    """Handle order created event - process payment automatically"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    amount = order_data["total_amount"]
    
    db = SessionLocal()
    try:
        payment_service = PaymentService()
        
        # Create and process payment automatically
        payment_create = PaymentCreate(
            order_id=order_id,
            amount=amount,
            payment_method="credit_card",
            status=PaymentStatus.PENDING
        )
        
        db_payment = payment_service.create_payment(db, payment_create)
        
        # Process payment
        payment_result = await payment_service.process_payment({
            "order_id": order_id,
            "amount": amount,
            "payment_method": "credit_card"
        })
        
        # Update payment status
        if payment_result["success"]:
            payment_service.update_payment_status(
                db, db_payment.id, PaymentStatus.SUCCEEDED, payment_result["transaction_id"]
            )
        else:
            payment_service.update_payment_status(
                db, db_payment.id, PaymentStatus.FAILED, payment_result["transaction_id"]
            )
        
        # Publish payment event
        if payment_result["success"]:
            await payment_service.publish_payment_event(
                "payment.succeeded",
                {
                    "order_id": order_id,
                    "payment_id": db_payment.id,
                    "amount": amount,
                    "transaction_id": payment_result["transaction_id"]
                }
            )
        else:
            await payment_service.publish_payment_event(
                "payment.failed",
                {
                    "order_id": order_id,
                    "payment_id": db_payment.id,
                    "amount": amount,
                    "transaction_id": payment_result["transaction_id"]
                }
            )
    except Exception as e:
        print(f"Error processing payment for order {order_id}: {e}")
    finally:
        db.close()

