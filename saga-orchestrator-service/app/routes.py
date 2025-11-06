from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from database import get_db
from app.schemas import SagaStartRequest, SagaResponse, SagaStatusResponse
from services.saga_orchestrator import SagaOrchestrator
from services.workflows import get_order_processing_saga_steps, get_order_fulfillment_saga_steps
from models.saga_instance import SagaInstance
from models.saga_step import SagaStep
import json

router = APIRouter()

# Saga workflow registry
SAGA_WORKFLOWS = {
    "order_processing": get_order_processing_saga_steps,
    "order_fulfillment": get_order_fulfillment_saga_steps
}

@router.post("/sagas/start", response_model=SagaResponse)
async def start_saga(
    request: SagaStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start a new saga transaction
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Starting saga: type={request.saga_type}, entity_id={request.entity_id}")
        logger.info(f"Step data count: {len(request.step_data)}")
        
        # Get workflow steps
        workflow_func = SAGA_WORKFLOWS.get(request.saga_type)
        if not workflow_func:
            logger.error(f"Unknown saga type: {request.saga_type}")
            raise HTTPException(
                status_code=400,
                detail=f"Unknown saga type: {request.saga_type}"
            )
        
        steps = workflow_func()
        logger.info(f"Workflow steps count: {len(steps)}")
        
        if len(steps) != len(request.step_data):
            logger.error(f"Step data count mismatch: {len(request.step_data)} vs {len(steps)}")
            raise HTTPException(
                status_code=400,
                detail=f"Step data count ({len(request.step_data)}) doesn't match workflow steps ({len(steps)})"
            )
        
        # Create saga instance
        orchestrator = SagaOrchestrator(db)
        saga_instance = orchestrator.create_saga_instance(
            saga_type=request.saga_type,
            entity_id=request.entity_id,
            steps=steps
        )
        logger.info(f"Created saga instance: {saga_instance.saga_id}")
        
        # Execute saga
        result = await orchestrator.execute_saga(
            saga_instance=saga_instance,
            steps=steps,
            step_data=request.step_data
        )
        
        logger.info(f"Saga execution completed: success={result.get('success')}")
        return SagaResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting saga: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/sagas/{saga_id}/status", response_model=SagaStatusResponse)
async def get_saga_status(
    saga_id: str,
    db: Session = Depends(get_db)
):
    """Get the status of a saga instance"""
    saga_instance = db.query(SagaInstance).filter(
        SagaInstance.saga_id == saga_id
    ).first()
    
    if not saga_instance:
        raise HTTPException(status_code=404, detail="Saga not found")
    
    # Get steps
    steps = db.query(SagaStep).filter(
        SagaStep.saga_instance_id == saga_instance.id
    ).order_by(SagaStep.step_index).all()
    
    steps_data = [
        {
            "step_name": step.step_name,
            "service_name": step.service_name,
            "status": step.status,
            "step_index": step.step_index,
            "error_message": step.error_message,
            "started_at": step.started_at.isoformat() if step.started_at else None,
            "completed_at": step.completed_at.isoformat() if step.completed_at else None,
            "compensated_at": step.compensated_at.isoformat() if step.compensated_at else None
        }
        for step in steps
    ]
    
    return SagaStatusResponse(
        saga_id=saga_instance.saga_id,
        saga_type=saga_instance.saga_type,
        entity_id=saga_instance.entity_id,
        status=saga_instance.status,
        current_step=saga_instance.current_step,
        created_at=saga_instance.created_at,
        updated_at=saga_instance.updated_at,
        completed_at=saga_instance.completed_at,
        error_message=saga_instance.error_message,
        steps=steps_data
    )

@router.post("/sagas/{saga_id}/compensate")
async def compensate_saga(
    saga_id: str,
    db: Session = Depends(get_db)
):
    """Manually trigger compensation for a saga"""
    saga_instance = db.query(SagaInstance).filter(
        SagaInstance.saga_id == saga_id
    ).first()
    
    if not saga_instance:
        raise HTTPException(status_code=404, detail="Saga not found")
    
    if saga_instance.status not in ["COMPLETED", "IN_PROGRESS", "FAILED"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot compensate saga in status: {saga_instance.status}"
        )
    
    # Get compensation data
    compensation_data = json.loads(saga_instance.compensation_data) if saga_instance.compensation_data else []
    
    # Execute compensation
    orchestrator = SagaOrchestrator(db)
    await orchestrator._compensate_saga(saga_instance, compensation_data)
    
    return {"message": f"Saga {saga_id} compensation initiated"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "saga-orchestrator-service"}

