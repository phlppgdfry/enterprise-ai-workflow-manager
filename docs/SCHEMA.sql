-- ====================================================================
-- Enterprise AI Workflow Manager: PostgreSQL Relational Database Schema
-- Ondersteunt RBAC, persistente workflows, HITL goedkeuringen en audit-logging
-- ====================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Gebruikers & Rollen (RBAC)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN', 'OPERATOR', 'AUDITOR', 'VIEWER')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Workflow Definities
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    requires_approval BOOLEAN DEFAULT TRUE,
    config JSONB DEFAULT '{}'::jsonb,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Workflow Uitvoeringen (State Machine)
CREATE TABLE workflow_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
    triggered_by UUID REFERENCES users(id),
    status VARCHAR(50) NOT NULL CHECK (
        status IN ('SUBMITTED', 'ANALYZING', 'NEEDS_APPROVAL', 'APPROVED', 'REJECTED', 'EXECUTING', 'COMPLETED', 'FAILED')
    ),
    input_payload JSONB NOT NULL,
    output_result JSONB,
    risk_score NUMERIC(3, 2) DEFAULT 0.00,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 4. Individuele Stappen binnen een Uitvoering
CREATE TABLE step_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
    step_number INT NOT NULL,
    step_name VARCHAR(150) NOT NULL,
    step_type VARCHAR(50) NOT NULL CHECK (step_type IN ('AI_REASONING', 'API_CALL', 'DATABASE_MUTATION', 'USER_PROMPT')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'SKIPPED')),
    input_data JSONB,
    output_data JSONB,
    token_usage_in INT DEFAULT 0,
    token_usage_out INT DEFAULT 0,
    latency_ms INT DEFAULT 0,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Human-in-the-Loop Goedkeuringsverzoeken
CREATE TABLE approval_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
    decision VARCHAR(50) CHECK (decision IN ('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED')),
    reviewer_id UUID REFERENCES users(id),
    reason TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Onveranderlijk Audit Log (Tamper-evident)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL,
    actor_id UUID REFERENCES users(id),
    previous_state JSONB,
    new_state JSONB,
    checksum VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexen voor performantie
CREATE INDEX idx_workflow_runs_status ON workflow_runs(status);
CREATE INDEX idx_workflow_runs_started ON workflow_runs(started_at);
CREATE INDEX idx_step_executions_run ON step_executions(run_id);
CREATE INDEX idx_approval_requests_decision ON approval_requests(decision);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
