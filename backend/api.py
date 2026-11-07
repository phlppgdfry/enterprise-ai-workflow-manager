from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
from typing import List, Dict, Any
from .models import WorkflowCreate, WorkflowRunRequest, ApprovalDecisionRequest, WorkflowRunDetail
from .engine import WorkflowEngine
from .mcp_server import mcp_router

app = FastAPI(
    title="Enterprise AI Workflow Manager API",
    description="Productieklare orchestrator voor AI-bedrijfsprocessen met Human-in-the-Loop governance.",
    version="1.0.0"
)

app.include_router(mcp_router)

engine = WorkflowEngine()
FRONTEND_FILE = Path(__file__).parent.parent / "frontend" / "index.html"

# Seed een initiële workflow
_seed_id = engine.register_workflow(
    title="Factuurvalidatie & Betalingsfiattering",
    description="Automatische extractie en audit van inkomende leveranciersfacturen met menselijke goedkeuring boven drempelwaarden.",
    category="Finance & Procurement",
    requires_approval=True
)

@app.get("/", response_class=HTMLResponse)
def index():
    if FRONTEND_FILE.exists():
        return FileResponse(FRONTEND_FILE)
    return HTMLResponse("<h1>Enterprise AI Workflow Manager</h1><p>Frontend file missing.</p>")

@app.get("/health")
def health_check():
    return {
        "service": "Enterprise AI Workflow Manager",
        "status": "HEALTHY",
        "version": "1.0.0",
        "architecture": "HITL + Cryptographic Audit Trail"
    }

@app.get("/api/workflows")
def list_workflows():
    return list(engine.workflows.values())

@app.post("/api/workflows")
def create_workflow(payload: WorkflowCreate):
    wf_id = engine.register_workflow(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        requires_approval=payload.requires_approval,
        config=payload.config
    )
    return engine.workflows[wf_id]

@app.post("/api/runs", response_model=WorkflowRunDetail)
def trigger_workflow_run(req: WorkflowRunRequest):
    try:
        return engine.trigger_run(req.workflow_id, req.user_id, req.input_payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/runs", response_model=List[WorkflowRunDetail])
def list_runs():
    return list(engine.runs.values())

@app.get("/api/runs/{run_id}", response_model=WorkflowRunDetail)
def get_run(run_id: str):
    if run_id not in engine.runs:
        raise HTTPException(status_code=404, detail="Run niet gevonden")
    return engine.runs[run_id]

@app.post("/api/runs/{run_id}/approval", response_model=WorkflowRunDetail)
def decide_approval(run_id: str, req: ApprovalDecisionRequest):
    try:
        return engine.record_decision(run_id, req.reviewer_id, req.decision, req.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/audit-logs")
def get_audit_logs():
    return engine.audit_logs
