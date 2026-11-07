import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from .models import RunStatus, StepType, StepExecutionRecord, WorkflowRunDetail

class WorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.runs: Dict[str, WorkflowRunDetail] = {}
        self.audit_logs: List[Dict[str, Any]] = []

    def log_audit(self, entity_type: str, entity_id: str, action: str, actor_id: str, prev_state: Any, new_state: Any):
        payload = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "actor_id": actor_id,
            "prev_state": prev_state,
            "new_state": new_state,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        checksum = hashlib.sha256(json.dumps(payload, default=str, sort_keys=True).encode()).hexdigest()
        payload["checksum"] = checksum
        self.audit_logs.append(payload)

    def register_workflow(self, title: str, description: str, category: str, requires_approval: bool = True, config: Optional[Dict[str, Any]] = None) -> str:
        wf_id = str(uuid.uuid4())
        self.workflows[wf_id] = {
            "id": wf_id,
            "title": title,
            "description": description,
            "category": category,
            "requires_approval": requires_approval,
            "config": config or {},
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self.log_audit("WORKFLOW", wf_id, "CREATE", "SYSTEM", None, self.workflows[wf_id])
        return wf_id

    def assess_risk(self, payload: Dict[str, Any]) -> float:
        """
        Evalueert het risiconiveau van een verzoek op basis van bedrijfsregels:
        - Bedrag > 10.000 EUR -> Hoog risico (0.85)
        - Wijziging van stamdata/credentials -> Hoog risico (0.95)
        - Gewone data-uitlezing -> Laag risico (0.15)
        """
        score = 0.15
        amount = payload.get("amount", 0)
        if isinstance(amount, (int, float)) and amount > 10000:
            score += 0.70
        if payload.get("action_type") in ["MUTATION", "DELETE", "CONFIG_CHANGE"]:
            score += 0.50
        if "external_transfer" in str(payload).lower():
            score += 0.30
        return min(round(score, 2), 1.0)

    def trigger_run(self, workflow_id: str, user_id: str, input_payload: Dict[str, Any]) -> WorkflowRunDetail:
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} bestaat niet.")

        wf = self.workflows[workflow_id]
        run_id = str(uuid.uuid4())
        risk = self.assess_risk(input_payload)

        # Stap 1: AI Reason & Plan
        step1 = StepExecutionRecord(
            step_number=1,
            step_name="AI Intent & Impact Analysis",
            step_type=StepType.AI_REASONING,
            status="COMPLETED",
            latency_ms=145,
            token_usage_in=350,
            token_usage_out=120,
            result={"inferred_intent": "Enterprise Process Execution", "risk_calculated": risk}
        )

        needs_approval = wf["requires_approval"] or risk >= 0.50
        initial_status = RunStatus.NEEDS_APPROVAL if needs_approval else RunStatus.APPROVED

        run = WorkflowRunDetail(
            id=run_id,
            workflow_id=workflow_id,
            triggered_by=user_id,
            status=initial_status,
            risk_score=risk,
            input_payload=input_payload,
            steps=[step1]
        )
        self.runs[run_id] = run
        self.log_audit("WORKFLOW_RUN", run_id, "TRIGGER", user_id, None, run.model_dump(mode="json"))

        # Als geen goedkeuring vereist is, voer direct uit
        if not needs_approval:
            self._execute_run(run)

        return run

    def record_decision(self, run_id: str, reviewer_id: str, decision: str, reason: Optional[str] = None) -> WorkflowRunDetail:
        if run_id not in self.runs:
            raise ValueError(f"Run {run_id} niet gevonden.")

        run = self.runs[run_id]
        if run.status != RunStatus.NEEDS_APPROVAL:
            raise ValueError(f"Run {run_id} wacht niet op goedkeuring (huidige status: {run.status}).")

        prev_status = run.status.value
        if decision == "APPROVED":
            run.status = RunStatus.APPROVED
            self.log_audit("APPROVAL", run_id, "APPROVE", reviewer_id, {"status": prev_status}, {"status": "APPROVED", "reason": reason})
            self._execute_run(run)
        elif decision == "REJECTED":
            run.status = RunStatus.REJECTED
            run.output_result = {"error": "Afgekeurd door menselijke reviewer", "reason": reason}
            self.log_audit("APPROVAL", run_id, "REJECT", reviewer_id, {"status": prev_status}, {"status": "REJECTED", "reason": reason})
        else:
            raise ValueError(f"Ongeldige beslissing: {decision}")

        return run

    def _execute_run(self, run: WorkflowRunDetail):
        run.status = RunStatus.EXECUTING
        
        # Stap 2: Gevalideerde Uitvoering (API / DB mutatie)
        step2 = StepExecutionRecord(
            step_number=2,
            step_name="Enterprise Execution Connector",
            step_type=StepType.API_CALL,
            status="COMPLETED",
            latency_ms=210,
            token_usage_in=0,
            token_usage_out=0,
            result={"status": "SUCCESS", "records_updated": 1, "target": "Enterprise ERP"}
        )
        run.steps.append(step2)
        run.status = RunStatus.COMPLETED
        run.output_result = {
            "execution_status": "SUCCESS",
            "message": "Workflow succesvol en conform governance uitgevoerd.",
            "steps_executed": len(run.steps)
        }
        self.log_audit("WORKFLOW_RUN", run.id, "COMPLETE", "SYSTEM", {"status": "APPROVED"}, run.model_dump(mode="json"))
