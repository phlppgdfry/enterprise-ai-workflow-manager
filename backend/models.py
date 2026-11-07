from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    AUDITOR = "AUDITOR"
    VIEWER = "VIEWER"

class RunStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    ANALYZING = "ANALYZING"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class StepType(str, Enum):
    AI_REASONING = "AI_REASONING"
    API_CALL = "API_CALL"
    DATABASE_MUTATION = "DATABASE_MUTATION"
    USER_PROMPT = "USER_PROMPT"

class WorkflowCreate(BaseModel):
    title: str
    description: str
    category: str
    requires_approval: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)

class WorkflowRunRequest(BaseModel):
    workflow_id: str
    input_payload: Dict[str, Any]
    user_id: str

class ApprovalDecisionRequest(BaseModel):
    reviewer_id: str
    decision: str  # "APPROVED" or "REJECTED"
    reason: Optional[str] = None

class StepExecutionRecord(BaseModel):
    step_number: int
    step_name: str
    step_type: StepType
    status: str
    latency_ms: int = 0
    token_usage_in: int = 0
    token_usage_out: int = 0
    result: Optional[Dict[str, Any]] = None

class WorkflowRunDetail(BaseModel):
    id: str
    workflow_id: str
    triggered_by: str
    status: RunStatus
    risk_score: float
    input_payload: Dict[str, Any]
    output_result: Optional[Dict[str, Any]] = None
    steps: List[StepExecutionRecord] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
