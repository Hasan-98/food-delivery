"""
Saga Orchestrator Service
Implements the Orchestration-based Saga pattern for distributed transactions
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Callable
from datetime import datetime
import json
import uuid
import asyncio
import httpx
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from models.saga_instance import SagaInstance
from models.saga_step import SagaStep
import logging

logger = logging.getLogger(__name__)

class SagaStepDefinition:
    """Definition of a saga step"""
    def __init__(
        self,
        step_name: str,
        service_name: str,
        service_url: str,
        request_path: str,
        request_method: str = "POST",
        compensation_path: Optional[str] = None,
        compensation_method: str = "POST"
    ):
        self.step_name = step_name
        self.service_name = service_name
        self.service_url = service_url
        self.request_path = request_path
        self.request_method = request_method
        self.compensation_path = compensation_path
        self.compensation_method = compensation_method

class SagaOrchestrator:
    """Orchestrates distributed transactions using Saga pattern"""
    
    def __init__(self, db: Session):
        self.db = db
        self.timeout = 30  # seconds
        
    def create_saga_instance(
        self,
        saga_type: str,
        entity_id: int,
        steps: List[SagaStepDefinition]
    ) -> SagaInstance:
        """Create a new saga instance"""
        saga_id = f"{saga_type}_{entity_id}_{uuid.uuid4().hex[:8]}"
        
        saga_instance = SagaInstance(
            saga_id=saga_id,
            saga_type=saga_type,
            entity_id=entity_id,
            status="PENDING",
            current_step=0
        )
        self.db.add(saga_instance)
        self.db.flush()
        
        # Create saga steps
        for idx, step_def in enumerate(steps):
            saga_step = SagaStep(
                saga_instance_id=saga_instance.id,
                step_index=idx,
                step_name=step_def.step_name,
                service_name=step_def.service_name,
                status="PENDING"
            )
            self.db.add(saga_step)
        
        self.db.commit()
        self.db.refresh(saga_instance)
        return saga_instance
    
    async def execute_saga(
        self,
        saga_instance: SagaInstance,
        steps: List[SagaStepDefinition],
        step_data: List[Dict]
    ) -> Dict:
        """
        Execute a saga transaction
        Returns: {"success": bool, "saga_id": str, "data": dict}
        """
        try:
            # Update saga status
            saga_instance.status = "IN_PROGRESS"
            self.db.commit()
            
            compensation_data = []
            
            # Execute each step sequentially
            for idx, (step_def, data) in enumerate(zip(steps, step_data)):
                saga_step = self.db.query(SagaStep).filter(
                    SagaStep.saga_instance_id == saga_instance.id,
                    SagaStep.step_index == idx
                ).first()
                
                if not saga_step:
                    raise Exception(f"Step {idx} not found for saga {saga_instance.saga_id}")
                
                try:
                    # Update step status
                    saga_step.status = "IN_PROGRESS"
                    saga_step.started_at = datetime.utcnow()
                    saga_step.request_data = json.dumps(data)
                    saga_instance.current_step = idx
                    self.db.commit()
                    
                    # Execute step
                    result = await self._execute_step(step_def, data)
                    
                    # Update step status
                    saga_step.status = "COMPLETED"
                    saga_step.completed_at = datetime.utcnow()
                    saga_step.response_data = json.dumps(result)
                    
                    # Store compensation data
                    compensation_info = {
                        "step_name": step_def.step_name,
                        "step_index": idx,
                        "compensation_data": result.get("compensation_data", {}),
                        "service_name": step_def.service_name,
                        "compensation_path": step_def.compensation_path
                    }
                    compensation_data.append(compensation_info)
                    saga_step.compensation_data = json.dumps(compensation_info)
                    
                    # Update subsequent step data with IDs from current step
                    if idx < len(step_data) - 1:
                        # Extract ID from response and update next step's data
                        response_data = result.get("data", {})
                        entity_id = response_data.get("id")
                        if entity_id:
                            # Update next step data with the ID
                            next_step_data = step_data[idx + 1]
                            # For order creation, propagate order_id to payment step
                            if step_def.step_name == "create_order":
                                next_step_data["order_id"] = entity_id
                                # Also propagate customer_id if it exists
                                if "customer_id" in data:
                                    next_step_data["customer_id"] = data["customer_id"]
                            # For payment, propagate order_id to confirmation step
                            elif step_def.step_name == "process_payment":
                                # Keep order_id from current step data
                                if "order_id" in data:
                                    next_step_data["order_id"] = data["order_id"]
                    
                    self.db.commit()
                    
                    logger.info(f"Saga {saga_instance.saga_id}: Step {step_def.step_name} completed")
                    
                except Exception as e:
                    # Step failed - initiate compensation
                    logger.error(f"Saga {saga_instance.saga_id}: Step {step_def.step_name} failed: {e}")
                    saga_step.status = "FAILED"
                    saga_step.error_message = str(e)
                    saga_step.completed_at = datetime.utcnow()
                    self.db.commit()
                    
                    # Compensate all previous steps
                    await self._compensate_saga(saga_instance, compensation_data)
                    
                    saga_instance.status = "FAILED"
                    saga_instance.error_message = f"Step {step_def.step_name} failed: {str(e)}"
                    self.db.commit()
                    
                    return {
                        "success": False,
                        "saga_id": saga_instance.saga_id,
                        "error": str(e),
                        "failed_step": step_def.step_name
                    }
            
            # All steps completed successfully
            saga_instance.status = "COMPLETED"
            saga_instance.completed_at = datetime.utcnow()
            saga_instance.compensation_data = json.dumps(compensation_data)
            self.db.commit()
            
            logger.info(f"Saga {saga_instance.saga_id} completed successfully")
            
            # Extract order_id and payment_id from compensation data
            order_id = None
            payment_id = None
            for comp_info in compensation_data:
                comp_data = comp_info.get("compensation_data", {})
                if comp_info["step_name"] == "create_order":
                    order_id = comp_data.get("id") or comp_data.get("entity_id")
                elif comp_info["step_name"] == "process_payment":
                    payment_id = comp_data.get("id") or comp_data.get("entity_id")
            
            return {
                "success": True,
                "saga_id": saga_instance.saga_id,
                "data": {
                    "order_id": order_id,
                    "payment_id": payment_id,
                    "status": "completed"
                }
            }
            
        except Exception as e:
            logger.error(f"Saga {saga_instance.saga_id} execution error: {e}")
            saga_instance.status = "FAILED"
            saga_instance.error_message = str(e)
            self.db.commit()
            
            return {
                "success": False,
                "saga_id": saga_instance.saga_id,
                "error": str(e)
            }
    
    async def _execute_step(self, step_def: SagaStepDefinition, data: Dict) -> Dict:
        """Execute a single saga step"""
        # Replace placeholders in request path
        request_path = step_def.request_path
        if "{order_id}" in request_path and "order_id" in data:
            request_path = request_path.replace("{order_id}", str(data["order_id"]))
        if "{payment_id}" in request_path and "payment_id" in data:
            request_path = request_path.replace("{payment_id}", str(data["payment_id"]))
        
        url = f"{step_def.service_url}{request_path}"
        
        # Prepare request data
        request_data = data.copy()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if step_def.request_method == "POST":
                    # For internal order endpoint, add customer_id as query param
                    if step_def.request_path == "/orders/internal" and "customer_id" in data:
                        customer_id = request_data.pop("customer_id", None)
                        logger.info(f"Calling {url} with customer_id={customer_id} as query param")
                        if customer_id:
                            response = await client.post(url, json=request_data, params={"customer_id": customer_id})
                        else:
                            logger.warning(f"No customer_id found in data for order creation")
                            response = await client.post(url, json=request_data)
                    else:
                        logger.info(f"Calling {url} with POST")
                        response = await client.post(url, json=request_data)
                elif step_def.request_method == "PUT":
                    logger.info(f"Calling {url} with PUT")
                    # For PUT requests, send empty body or minimal data
                    if request_data and len(request_data) > 0:
                        response = await client.put(url, json=request_data)
                    else:
                        response = await client.put(url)
                elif step_def.request_method == "DELETE":
                    logger.info(f"Calling {url} with DELETE")
                    response = await client.delete(url)
                else:
                    logger.info(f"Calling {url} with GET")
                    response = await client.get(url, params=request_data)
                
                response.raise_for_status()
                result = response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error calling {url}: {e.response.status_code} - {e.response.text}")
                raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
            except httpx.RequestError as e:
                logger.error(f"Request error calling {url}: {str(e)}")
                raise Exception(f"Request failed: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error calling {url}: {str(e)}")
                raise
            
            # Extract compensation data from response
            # For order creation, result is the order object
            # For payment, result is the payment object
            entity_id = result.get("id") or result.get("order_id") or result.get("payment_id")
            
            compensation_data = {
                "id": entity_id,
                "entity_id": entity_id,
                "data": result
            }
            
            return {
                "success": True,
                "data": result,
                "compensation_data": compensation_data
            }
    
    async def _compensate_saga(
        self,
        saga_instance: SagaInstance,
        compensation_data: List[Dict]
    ):
        """Compensate all completed steps in reverse order"""
        logger.info(f"Starting compensation for saga {saga_instance.saga_id}")
        
        saga_instance.status = "COMPENSATING"
        self.db.commit()
        
        # Compensate in reverse order
        for comp_info in reversed(compensation_data):
            step_name = comp_info["step_name"]
            step_index = comp_info["step_index"]
            
            saga_step = self.db.query(SagaStep).filter(
                SagaStep.saga_instance_id == saga_instance.id,
                SagaStep.step_index == step_index
            ).first()
            
            if saga_step and saga_step.status == "COMPLETED":
                try:
                    await self._compensate_step(comp_info)
                    saga_step.status = "COMPENSATED"
                    saga_step.compensated_at = datetime.utcnow()
                    self.db.commit()
                    logger.info(f"Compensated step {step_name} for saga {saga_instance.saga_id}")
                except Exception as e:
                    logger.error(f"Failed to compensate step {step_name}: {e}")
                    saga_step.error_message = f"Compensation failed: {str(e)}"
                    self.db.commit()
                    # Continue with other compensations even if one fails
    
    async def _compensate_step(self, comp_info: Dict):
        """Execute compensation for a single step"""
        import os
        service_name = comp_info["service_name"]
        compensation_path = comp_info.get("compensation_path")
        compensation_data = comp_info.get("compensation_data", {})
        
        if not compensation_path:
            logger.warning(f"No compensation path for step {comp_info['step_name']}")
            return
        
        # Get service URL from config
        service_urls = {
            "order-service": os.getenv("ORDER_SERVICE_URL", "http://localhost:8003"),
            "payment-service": os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8004"),
            "catalog-service": os.getenv("CATALOG_SERVICE_URL", "http://localhost:8002"),
            "restaurant-service": os.getenv("RESTAURANT_SERVICE_URL", "http://localhost:8005"),
            "dispatch-service": os.getenv("DISPATCH_SERVICE_URL", "http://localhost:8006"),
        }
        
        service_url = service_urls.get(service_name)
        if not service_url:
            raise Exception(f"Service URL not found for {service_name}")
        
        # Replace placeholders in compensation path
        entity_id = compensation_data.get("entity_id") or compensation_data.get("id")
        if entity_id and "{order_id}" in compensation_path:
            compensation_path = compensation_path.replace("{order_id}", str(entity_id))
        if entity_id and "{payment_id}" in compensation_path:
            compensation_path = compensation_path.replace("{payment_id}", str(entity_id))
        
        url = f"{service_url}{compensation_path}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=compensation_data)
            response.raise_for_status()
            logger.info(f"Compensation successful for {comp_info['step_name']}")

