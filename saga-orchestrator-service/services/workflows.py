"""
Saga Workflow Definitions
Defines the steps and compensation logic for different saga types
"""
from services.saga_orchestrator import SagaStepDefinition
import os

# Service URLs (should be from config/env)
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8003")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8004")
CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8002")
RESTAURANT_SERVICE_URL = os.getenv("RESTAURANT_SERVICE_URL", "http://localhost:8005")
DISPATCH_SERVICE_URL = os.getenv("DISPATCH_SERVICE_URL", "http://localhost:8006")

def get_order_processing_saga_steps() -> list[SagaStepDefinition]:
    """
    Order Processing Saga Steps:
    1. Create Order (order-service) - Returns order_id
    2. Process Payment (payment-service) - Uses order_id, returns payment_id
    3. Confirm Order (order-service) - Uses order_id
    
    Compensation:
    - If payment fails: Cancel order
    - If confirmation fails: Refund payment, cancel order
    """
    return [
        SagaStepDefinition(
            step_name="create_order",
            service_name="order-service",
            service_url=ORDER_SERVICE_URL,
            request_path="/orders/internal",
            request_method="POST",
            compensation_path="/orders/{order_id}/compensate",
            compensation_method="POST"
        ),
        SagaStepDefinition(
            step_name="process_payment",
            service_name="payment-service",
            service_url=PAYMENT_SERVICE_URL,
            request_path="/payments/internal",
            request_method="POST",
            compensation_path="/payments/{payment_id}/compensate",
            compensation_method="POST"
        ),
        SagaStepDefinition(
            step_name="confirm_order",
            service_name="order-service",
            service_url=ORDER_SERVICE_URL,
            request_path="/orders/{order_id}/confirm",
            request_method="PUT",
            compensation_path="/orders/{order_id}/compensate",
            compensation_method="POST"
        )
    ]

def get_order_fulfillment_saga_steps() -> list[SagaStepDefinition]:
    """
    Order Fulfillment Saga Steps:
    1. Accept Order (restaurant-service)
    2. Assign Driver (dispatch-service)
    3. Update Order Status (order-service)
    
    Compensation:
    - If any step fails: Cancel previous steps
    """
    return [
        SagaStepDefinition(
            step_name="accept_order",
            service_name="restaurant-service",
            service_url=RESTAURANT_SERVICE_URL,
            request_path="/orders/{order_id}/accept",
            request_method="POST",
            compensation_path="/orders/{order_id}/cancel",
            compensation_method="POST"
        ),
        SagaStepDefinition(
            step_name="assign_driver",
            service_name="dispatch-service",
            service_url=DISPATCH_SERVICE_URL,
            request_path="/orders/{order_id}/assign",
            request_method="POST",
            compensation_path="/deliveries/{order_id}/cancel",
            compensation_method="POST"
        ),
        SagaStepDefinition(
            step_name="update_order_status",
            service_name="order-service",
            service_url=ORDER_SERVICE_URL,
            request_path="/orders/{order_id}/status",
            request_method="PUT",
            compensation_path="/orders/{order_id}/compensate",
            compensation_method="POST"
        )
    ]

