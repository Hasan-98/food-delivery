from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import sys
import os
import asyncio
import json
import uuid
import random
from datetime import datetime

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from database import get_db, Payment
from shared.models import (
    Payment as PaymentModel, PaymentCreate, PaymentStatus, UserRole
)
from shared.auth import get_current_user, require_role
from shared.message_broker import get_message_broker

app = FastAPI(title="Payment Service", version="1.0.0")

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
    print("Payment Service database tables created successfully!")
    
    # Start event listeners (optional)
    try:
        message_broker = await get_message_broker()
        await message_broker.subscribe_to_events(
            ["order.created"],
            handle_order_created
        )
    except Exception as e:
        print(f"Message broker startup error: {e}")
        # Continue without message broker

# Simulate payment gateway
async def process_payment(payment_data: dict) -> dict:
    """Simulate payment processing with random success/failure"""
    # Simulate network delay
    await asyncio.sleep(1)
    
    # Randomly succeed or fail (90% success rate)
    success = random.random() < 0.9
    
    transaction_id = str(uuid.uuid4())
    
    return {
        "success": success,
        "transaction_id": transaction_id,
        "message": "Payment processed successfully" if success else "Payment failed"
    }

@app.post("/payments", response_model=PaymentModel)
async def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.CUSTOMER))
):
    # Create payment record
    db_payment = Payment(
        order_id=payment.order_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
        status=payment.status
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    # Process payment
    payment_result = await process_payment({
        "order_id": payment.order_id,
        "amount": payment.amount,
        "payment_method": payment.payment_method
    })
    
    # Update payment status
    if payment_result["success"]:
        db_payment.status = PaymentStatus.SUCCEEDED
        db_payment.transaction_id = payment_result["transaction_id"]
        db_payment.processed_at = datetime.utcnow()
    else:
        db_payment.status = PaymentStatus.FAILED
        db_payment.transaction_id = payment_result["transaction_id"]
        db_payment.processed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_payment)
    
    # Publish payment event (optional)
    try:
        message_broker = await get_message_broker()
        if payment_result["success"]:
            await message_broker.publish_event(
                "payment.succeeded",
                {
                    "order_id": payment.order_id,
                    "payment_id": db_payment.id,
                    "amount": payment.amount,
                    "transaction_id": payment_result["transaction_id"]
                }
            )
        else:
            await message_broker.publish_event(
                "payment.failed",
                {
                    "order_id": payment.order_id,
                    "payment_id": db_payment.id,
                    "amount": payment.amount,
                    "transaction_id": payment_result["transaction_id"]
                }
            )
    except Exception as e:
        print(f"Message broker error: {e}")
        # Continue without message broker
    
    return db_payment

@app.get("/payments", response_model=List[PaymentModel])
async def get_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    payments = db.query(Payment).offset(skip).limit(limit).all()
    return payments

@app.get("/payments/{payment_id}", response_model=PaymentModel)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.post("/payments/{payment_id}/refund")
async def refund_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status != PaymentStatus.SUCCEEDED:
        raise HTTPException(status_code=400, detail="Can only refund successful payments")
    
    # Simulate refund processing
    await asyncio.sleep(1)
    
    payment.status = PaymentStatus.REFUNDED
    db.commit()
    
    # Publish refund event (optional)
    try:
        message_broker = await get_message_broker()
        await message_broker.publish_event(
            "payment.refunded",
            {
                "order_id": payment.order_id,
                "payment_id": payment.id,
                "amount": payment.amount,
                "transaction_id": payment.transaction_id
            }
        )
    except Exception as e:
        print(f"Message broker error: {e}")
        # Continue without message broker
    
    return {"message": "Payment refunded successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}

# Event handlers for async communication
async def handle_order_created(event_data):
    """Handle order created event - process payment automatically"""
    order_data = event_data["data"]
    order_id = order_data["order_id"]
    amount = order_data["total_amount"]
    
    # Create and process payment automatically
    payment = PaymentCreate(
        order_id=order_id,
        amount=amount,
        payment_method="credit_card",
        status=PaymentStatus.PENDING
    )
    
    # Process payment
    payment_result = await process_payment({
        "order_id": order_id,
        "amount": amount,
        "payment_method": "credit_card"
    })
    
    # Create payment record
    db = next(get_db())
    db_payment = Payment(
        order_id=order_id,
        amount=amount,
        payment_method="credit_card",
        status=PaymentStatus.SUCCEEDED if payment_result["success"] else PaymentStatus.FAILED,
        transaction_id=payment_result["transaction_id"],
        processed_at=datetime.utcnow()
    )
    db.add(db_payment)
    db.commit()
    
    # Publish payment event (optional)
    try:
        message_broker = await get_message_broker()
        if payment_result["success"]:
            await message_broker.publish_event(
                "payment.succeeded",
                {
                    "order_id": order_id,
                    "payment_id": db_payment.id,
                    "amount": amount,
                    "transaction_id": payment_result["transaction_id"]
                }
            )
        else:
            await message_broker.publish_event(
                "payment.failed",
                {
                    "order_id": order_id,
                    "payment_id": db_payment.id,
                    "amount": amount,
                    "transaction_id": payment_result["transaction_id"]
                }
            )
    except Exception as e:
        print(f"Message broker error: {e}")
        # Continue without message broker


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
