import pytest
from backend.engine import WorkflowEngine
from backend.models import RunStatus
from backend.mcp_server import AVAILABLE_TOOLS, execute_mcp_tool, MCPCallRequest

def test_workflow_registration_and_audit():
    engine = WorkflowEngine()
    wf_id = engine.register_workflow(
        title="Materiaalverzoek Bouwbedrijf",
        description="Verwerkt materiaalorders met voorraadvalidatie",
        category="Operations",
        requires_approval=True
    )
    assert wf_id in engine.workflows
    assert len(engine.audit_logs) >= 1
    assert engine.audit_logs[0]["action"] == "CREATE"

def test_high_risk_run_demands_approval():
    engine = WorkflowEngine()
    wf_id = engine.register_workflow(
        title="Financiële Overboeking",
        description="Grote betalingen",
        category="Finance",
        requires_approval=False
    )
    
    # Bedrag > 10.000 triggert risicoscore >= 0.85 en forceert goedkeuring
    run = engine.trigger_run(wf_id, "user-123", {"amount": 25000, "recipient": "Leverancier A"})
    assert run.status == RunStatus.NEEDS_APPROVAL
    assert run.risk_score >= 0.80

def test_approval_flow_completes_workflow():
    engine = WorkflowEngine()
    wf_id = engine.register_workflow(
        title="Inkooporder",
        description="Ordergoedkeuring",
        category="Procurement",
        requires_approval=True
    )
    run = engine.trigger_run(wf_id, "operator-1", {"item": "Staalplaten", "amount": 4000})
    assert run.status == RunStatus.NEEDS_APPROVAL

    # Reviewer keurt goed
    updated = engine.record_decision(run.id, "manager-99", "APPROVED", reason="Budget geverifieerd")
    assert updated.status == RunStatus.COMPLETED
    assert updated.output_result["execution_status"] == "SUCCESS"
    assert len(updated.steps) == 2

def test_rejection_halts_execution_cleanly():
    engine = WorkflowEngine()
    wf_id = engine.register_workflow(
        title="Hardware Verzoek",
        description="Nieuwe laptops",
        category="IT",
        requires_approval=True
    )
    run = engine.trigger_run(wf_id, "employee-4", {"item": "MacBook Pro", "amount": 3500})
    
    updated = engine.record_decision(run.id, "manager-99", "REJECTED", reason="Buiten kwartaalbudget")
    assert updated.status == RunStatus.REJECTED
    assert "Afgekeurd" in updated.output_result["error"]
    assert len(updated.steps) == 1

def test_mcp_platform_extension():
    """Valideert Level 5 Master Builder: Platform Extensie via MCP tools."""
    assert len(AVAILABLE_TOOLS) >= 2
    tool_names = [t.name for t in AVAILABLE_TOOLS]
    assert "trigger_governed_workflow" in tool_names
    assert "query_audit_trail" in tool_names
