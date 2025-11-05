from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import random
import asyncio
from models.payment import Payment
from shared.models import PaymentCreate, PaymentStatus
from shared.message_broker import get_message_broker

class PaymentService:
    """Service for payment processing"""
    
    async def process_payment(self, payment_data: dict) -> dict:
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
    
    def create_payment(
        self,
        db: Session,
        payment: PaymentCreate
    ) -> Payment:
        """Create a payment record"""
        db_payment = Payment(
            order_id=payment.order_id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            status=payment.status
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment
    
    def update_payment_status(
        self,
        db: Session,
        payment_id: int,
        status: PaymentStatus,
        transaction_id: Optional[str] = None
    ) -> Payment:
        """Update payment status"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")
        
        payment.status = status
        if transaction_id:
            payment.transaction_id = transaction_id
        payment.processed_at = datetime.utcnow()
        db.commit()
        db.refresh(payment)
        return payment
    
    def get_payments(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """Get all payments"""
        return db.query(Payment).offset(skip).limit(limit).all()
    
    def get_payment_by_id(self, db: Session, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        return db.query(Payment).filter(Payment.id == payment_id).first()
    
    def refund_payment(self, db: Session, payment_id: int) -> Payment:
        """Refund a payment"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError("Payment not found")
        
        if payment.status != PaymentStatus.SUCCEEDED:
            raise ValueError("Can only refund successful payments")
        
        payment.status = PaymentStatus.REFUNDED
        db.commit()
        db.refresh(payment)
        return payment
    
    async def publish_payment_event(self, event_type: str, payment_data: dict):
        """Publish payment event"""
        try:
            message_broker = await get_message_broker()
            await message_broker.publish_event(event_type, payment_data)
        except Exception as e:
            print(f"Message broker error: {e}")

