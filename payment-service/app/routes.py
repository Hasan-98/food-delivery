from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database import get_db
from app.schemas import PaymentSchema, PaymentCreate, PaymentStatus
from shared.auth import get_current_user, require_role, UserRole
from services.payment_service import PaymentService

router = APIRouter()

@router.post("/payments/internal", response_model=PaymentSchema)
async def create_payment_internal(
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    """
    Internal endpoint for saga orchestrator
    Creates and processes payment (no auth required)
    MUST be defined before /payments/{payment_id} to avoid route conflicts
    """
    payment_service = PaymentService()
    
    # Create payment record
    db_payment = payment_service.create_payment(db, payment)
    
    # Process payment
    payment_result = await payment_service.process_payment({
        "order_id": payment.order_id,
        "amount": payment.amount,
        "payment_method": payment.payment_method
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
    
    # Publish payment event (optional, can fail silently)
    try:
        if payment_result["success"]:
            await payment_service.publish_payment_event(
                "payment.succeeded",
                {
                    "order_id": payment.order_id,
                    "payment_id": db_payment.id,
                    "amount": payment.amount,
                    "transaction_id": payment_result["transaction_id"]
                }
            )
        else:
            await payment_service.publish_payment_event(
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

@router.post("/payments", response_model=PaymentSchema)
async def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.CUSTOMER))
):
    """Create and process a payment"""
    payment_service = PaymentService()
    
    # Create payment record
    db_payment = payment_service.create_payment(db, payment)
    
    # Process payment
    payment_result = await payment_service.process_payment({
        "order_id": payment.order_id,
        "amount": payment.amount,
        "payment_method": payment.payment_method
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
                "order_id": payment.order_id,
                "payment_id": db_payment.id,
                "amount": payment.amount,
                "transaction_id": payment_result["transaction_id"]
            }
        )
    else:
        await payment_service.publish_payment_event(
            "payment.failed",
            {
                "order_id": payment.order_id,
                "payment_id": db_payment.id,
                "amount": payment.amount,
                "transaction_id": payment_result["transaction_id"]
            }
        )
    
    return db_payment

@router.get("/payments", response_model=List[PaymentSchema])
async def get_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all payments"""
    payment_service = PaymentService()
    payments = payment_service.get_payments(db, skip, limit)
    return payments

@router.get("/payments/{payment_id}", response_model=PaymentSchema)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get payment by ID"""
    payment_service = PaymentService()
    payment = payment_service.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post("/payments/{payment_id}/refund")
async def refund_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    """Refund a payment"""
    payment_service = PaymentService()
    
    try:
        payment = payment_service.refund_payment(db, payment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Publish refund event
    await payment_service.publish_payment_event(
        "payment.refunded",
        {
            "order_id": payment.order_id,
            "payment_id": payment.id,
            "amount": payment.amount,
            "transaction_id": payment.transaction_id
        }
    )
    
    return {"message": "Payment refunded successfully"}

@router.post("/payments/{payment_id}/compensate")
async def compensate_payment(
    payment_id: int,
    compensation_data: dict,
    db: Session = Depends(get_db)
):
    """
    Compensation endpoint for saga transactions
    Refunds the payment if it was successful
    """
    payment_service = PaymentService()
    
    try:
        payment = payment_service.compensate_payment(db, payment_id)
        return {
            "message": f"Payment {payment_id} compensated",
            "payment_id": payment.id,
            "status": payment.status
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}

