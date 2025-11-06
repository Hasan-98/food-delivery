from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class SagaStartRequest(BaseModel):
    saga_type: str
    entity_id: int
    step_data: List[Dict]

class SagaResponse(BaseModel):
    success: bool
    saga_id: str
    data: Optional[Dict] = None
    error: Optional[str] = None
    failed_step: Optional[str] = None

class SagaStatusResponse(BaseModel):
    saga_id: str
    saga_type: str
    entity_id: int
    status: str
    current_step: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    steps: List[Dict]

