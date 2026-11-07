from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from .engine import WorkflowEngine

mcp_router = APIRouter(prefix="/mcp", tags=["Model Context Protocol - Level 5 Capability"])

class MCPToolDefinition(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class MCPCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

AVAILABLE_TOOLS: List[MCPToolDefinition] = [
    MCPToolDefinition(
        name="trigger_governed_workflow",
        description="Triggert een geauditeerde bedrijfs-workflow met automatische risicoscore en optionele menselijke goedkeuring.",
        inputSchema={
            "type": "object",
            "properties": {
                "workflow_id": {"type": "string", "description": "ID van de doelworkflow"},
                "recipient": {"type": "string", "description": "Leverancier of begunstigde"},
                "amount": {"type": "number", "description": "Financieel bedrag in EUR"}
            },
            "required": ["workflow_id", "recipient", "amount"]
        }
    ),
    MCPToolDefinition(
        name="query_audit_trail",
        description="Vraagt onveranderlijke SHA-256 logs op voor compliancy-audits.",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Aantal recente logs (max 50)", "default": 10}
            }
        }
    )
]

@mcp_router.get("/tools")
def list_mcp_tools():
    """Geeft de officiële Model Context Protocol (MCP) tools terug voor AI Agents."""
    return {"tools": [t.dict() for t in AVAILABLE_TOOLS]}

@mcp_router.post("/execute")
def execute_mcp_tool(req: MCPCallRequest):
    """Voert een geregistreerde MCP-tool actie uit."""
    from .api import engine
    if req.tool_name == "trigger_governed_workflow":
        wf_id = req.arguments.get("workflow_id")
        recipient = req.arguments.get("recipient")
        amount = req.arguments.get("amount", 0)
        run = engine.trigger_run(wf_id, "mcp-agent", {"recipient": recipient, "amount": amount})
        return {"status": "SUCCESS", "run_id": run.id, "run_status": run.status.value, "risk_score": run.risk_score}
    elif req.tool_name == "query_audit_trail":
        limit = req.arguments.get("limit", 10)
        return {"audit_trail": engine.audit_logs[-limit:]}
    else:
        raise HTTPException(status_code=404, detail=f"Onbekende MCP tool: {req.tool_name}")
