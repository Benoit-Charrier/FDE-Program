# Architecture Document - Vendor Contract Review Agent

## System Overview

The Vendor Contract Review Agent is a rule-first AI-assisted system for automating first-pass legal review of inbound vendor contracts against a structured negotiation playbook. The system enforces deterministic routing logic and human control gates to ensure legal accountability.

## Core Design Principles

1. **Rule-First**: Legal routing and approval gates are enforced by deterministic rules, not probabilistic LLM outputs.
2. **Human Control**: Humans retain final approval authority over all negotiated outbound language.
3. **Auditability**: Every extraction, routing decision, redline, and approval is logged for compliance.
4. **Config-Driven Policies**: Legal thresholds and playbook terms are externalized; no hardcoded legal values.
5. **Safe Failure**: When uncertain, escalate rather than auto-approve.

## Architectural Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Server (Port 8000)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  POST /analyze              POST /approve-redline                 │
│    ↓                          ↓                                    │
│  [Ingestion Module]         [Audit Logger]                        │
│    ├─ ingest_pdf                                                  │
│    ├─ ingest_docx                                                 │
│    └─ page tracking                                               │
│      ↓                                                             │
│  [Extraction & Routing]                                           │
│    ├─ Claude API call                                             │
│    ├─ extract_clauses_with_claude()                               │
│    ├─ classify_clause() [Deterministic]                           │
│    ├─ route_contract() [Deterministic Rules]                      │
│    └─ audit_log (extraction_complete)                             │
│      ↓                                                             │
│  [Redline & Approval Gate]                                        │
│    ├─ generate_redlines() [Playbook-bounded only]                 │
│    ├─ check_release_eligibility() [Hard control]                  │
│    └─ audit_log (redline_generation)                              │
│      ↓                                                             │
│  [Response]                                                        │
│    ├─ routing_decision                                            │
│    ├─ extracted_clauses                                           │
│    ├─ redline_proposals                                           │
│    ├─ is_releasable (false if escalated/unapproved)               │
│    └─ approval_packet_ready                                       │
│                                                                   │
│  POST /check-releasable ← [Release Gate Enforcer]                 │
│  GET /audit-trail/{contract_id}                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         ↓                              ↓
    [SQLite DB]                   [Anthropic API]
   audit.db                     (Claude 3.5 Sonnet)
```

## Module Responsibilities

### `ingestion.py`
- **Purpose**: Parse contracts from PDF/DOCX into normalized text with page references
- **Functions**:
  - `ingest_pdf()`: Extract text from PDFs using PyPDF2
  - `ingest_docx()`: Extract text from DOCX files
  - `ingest_contract()`: Router that detects file type and delegates
- **Outputs**: Normalized text + page count

### `extraction_and_routing.py`
- **Purpose**: Extract clauses using Claude, then apply deterministic routing logic
- **Functions**:
  - `extract_clauses_with_claude()`: Call Claude API to extract clause families
  - `classify_clause()`: Deterministic rules-based classification (MATCH / NEGOTIABLE / ESCALATE)
  - `route_contract()`: Deterministic rules for routing decision
  - `analyze_contract()`: Orchestrates full extraction pipeline
- **Outputs**: `ContractReviewResult` with routing decision and extracted clauses

### `redline_and_approval.py`
- **Purpose**: Generate redlines from approved fallback language, enforce approval gate
- **Functions**:
  - `generate_redlines()`: Create redlines ONLY from playbook fallback language
  - `check_release_eligibility()`: Hard control gate—enforce lawyer sign-off requirement
  - `create_releasable_package()`: Wrap result with release gate status
- **Key Control**: Never generates novel language; never releases without approvals

### `audit.py`
- **Purpose**: Full compliance audit trail using SQLite
- **Functions**:
  - `AuditLogger.log()`: Record audit event
  - `AuditLogger.get_audit_trail()`: Retrieve contract audit history
- **Events Logged**:
  - ingestion_started / ingestion_complete
  - extraction_complete
  - redline_generation
  - approval_recorded
  - release_attempted / release_blocked

### `app.py`
- **Purpose**: FastAPI REST API orchestrating the full workflow
- **Endpoints**:
  - `POST /analyze`: Ingest and analyze contract
  - `POST /approve-redline`: Record lawyer approval
  - `POST /check-releasable`: Enforce release gate
  - `GET /audit-trail/{contract_id}`: Retrieve audit history

## Decision Rules (Deterministic)

### Clause Classification

```
IF extraction_confidence < threshold:
  → ESCALATE
ELSE IF mandatory_clause_missing:
  → ESCALATE
ELSE IF must_escalate_keyword in text:
  → ESCALATE
ELSE IF matches_approved_pattern:
  → MATCH
ELSE:
  → NEGOTIABLE_DEVIATION
```

### Contract Routing

```
IF any clause == ESCALATE:
  → SENIOR_LAWYER_ESCALATION (confidence = 0.5)
ELSE IF all clauses == MATCH:
  → STANDARD (confidence = 0.95)
ELSE IF any clause == NEGOTIABLE_DEVIATION:
  → PLAYBOOK_NEGOTIABLE (confidence = 0.85)
```

### Release Gate (Hard Control)

```
IF route == SENIOR_LAWYER_ESCALATION:
  → NOT RELEASABLE (stays with lawyer)
ELSE IF route == STANDARD and no_redlines:
  → RELEASABLE immediately
ELSE IF route == PLAYBOOK_NEGOTIABLE:
  IF all_redlines_approved_by_lawyer:
    → RELEASABLE
  ELSE:
    → BLOCKED (missing/rejected approvals)
```

## Data Flow

1. **Ingestion**: PDF/DOCX uploaded → normalized text with page refs
2. **Extraction**: Text → Claude → raw extraction with confidence
3. **Classification**: Extraction + playbook rules → clause status
4. **Routing**: Clause statuses → contract route (standard/negotiable/escalation)
5. **Redlines**: PLAYBOOK_NEGOTIABLE → fallback language redlines (never novel)
6. **Approval Gate**: Redlines → lawyer approval(s) required before release
7. **Release**: All approvals present + no escalations → releasable package

## Escalation Triggers (from playbook)

- Uncapped liability
- Missing/non-compliant DPA
- IP ownership transfer outside standards
- Over-broad indemnity scope
- Governing law outside approved jurisdictions
- Extraction confidence below 0.75
- Missing mandatory clause
- Novel clause type not in playbook
- Conflicting clause signals

## Integration Points

1. **Contract Intake**: Expects PDF/DOCX files
2. **Document Storage**: Stores originals + redline versions
3. **Matter Management**: Routes to paralegal/lawyer queues
4. **Approval System**: Records lawyer sign-offs electronically
5. **Reporting Dashboard**: Consumes audit events for metrics

## Non-Functional Requirements

- **Determinism**: Same input → same routing every time (no randomness in rules)
- **Auditability**: 100% event logging for compliance
- **Safety**: Defaults to escalation when uncertain
- **Performance**: <3s analysis time per 25-page contract
- **Scalability**: Can run 300 contracts/quarter (8.3/day)
