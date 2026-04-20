# Data Contracts Specification

## Overview

This document defines the JSON schemas for all inputs, outputs, and internal state used by the Vendor Contract Review Agent.

## Input: Contract File

```json
{
  "file": "binary (PDF or DOCX)",
  "filename": "string",
  "content_type": "application/pdf | application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "metadata": {
    "vendor_name": "string (optional)",
    "contract_type": "string (optional)",
    "requester": "string (optional)"
  }
}
```

## Internal: ExtractedClause

Each clause extracted from the contract.

```json
{
  "family": "liability | dpa | termination | ip_ownership | sla | governing_law | indemnity",
  "source_text": "string (raw clause text from contract)",
  "page_number": "integer",
  "confidence_score": "float [0.0 - 1.0]",
  "status": "match | negotiable_deviation | escalate",
  "variance_reason": "string (why it differs, if applicable)",
  "escalation_reason": "string (why escalated, if applicable)"
}
```

## Internal: RedlineProposal

A proposed redline using ONLY approved fallback language from the playbook.

```json
{
  "clause_family": "liability | dpa | termination | ip_ownership | sla | governing_law | indemnity",
  "current_language": "string (original text from contract)",
  "proposed_language": "string (fallback language from playbook)",
  "playbook_fallback_reference": "string (ID linking to playbook entry)",
  "rationale": "string (why this redline is proposed)"
}
```

**Critical Rule**: `proposed_language` MUST match a playbook entry exactly. Never invented.

## Internal: ContractReviewResult

Main output from analysis pipeline.

```json
{
  "contract_id": "uuid",
  "filename": "string",
  "file_size_bytes": "integer",
  "page_count": "integer",
  "ingestion_timestamp": "ISO 8601 datetime",
  
  "route_decision": "standard | playbook_negotiable | senior_lawyer_escalation",
  "routing_confidence": "float [0.0 - 1.0]",
  
  "extracted_clauses": [ExtractedClause],
  "variance_summary": "string (human-readable summary)",
  
  "redline_proposals": [RedlineProposal],
  "escalation_reasons": ["string", "string"],
  
  "analysis_timestamp": "ISO 8601 datetime"
}
```

## Internal: ApprovalRecord

A lawyer's approval (or rejection) of a proposed redline.

```json
{
  "clause_family": "liability | dpa | termination | ip_ownership | sla | governing_law | indemnity",
  "proposed_redline_id": "string",
  "approved_by_lawyer_name": "string",
  "approved_by_lawyer_email": "string",
  "approval_timestamp": "ISO 8601 datetime",
  "approval_status": "pending | approved | rejected",
  "notes": "string (optional)"
}
```

## Output: ReleasablePackage

The final wrapped package showing whether a contract is eligible for release.

```json
{
  "contract_review_result": ContractReviewResult,
  "clause_approvals": [ApprovalRecord],
  
  "is_releasable": "boolean",
  "release_block_reason": "string (if not releasable)",
  "prepared_for_release_timestamp": "ISO 8601 datetime (if releasable)"
}
```

**Releasability Rules**:
- `is_releasable = true` ONLY IF:
  - route_decision == `standard` AND no redlines, OR
  - route_decision == `playbook_negotiable` AND all redlines are approved
- Escalated contracts are NEVER releasable (must stay with lawyer)

## Internal: AuditEvent

Compliance audit trail entry.

```json
{
  "event_type": "ingestion_started | ingestion_complete | extraction_complete | redline_generation | approval_recorded | release_attempted | release_blocked | analysis_error",
  "timestamp": "ISO 8601 datetime",
  "contract_id": "uuid",
  "actor": "string (human or system name)",
  "event_details": {
    "...": "context-specific details"
  },
  "outcome": "success | warning | error | blocked"
}
```

## Configuration: PlaybookSchema

The playbook defines approved language and escalation rules.

```yaml
version: "1.0.0"
last_updated: "2026-04-20T00:00:00Z"

clause_families:
  liability:
    mandatory: true
    approved_patterns:
      - pattern: "regex pattern for acceptable language"
        description: "What this pattern means"
    fallback_language:
      - id: "liability_cap_1x"
        name: "Standard 1x ARR Cap"
        language: "Full approved fallback text"
        rationale: "Why this is approved"
        legal_risk_level: "low | medium | high"
    must_escalate_keywords:
      - "unlimited liability"
      - "uncapped"

global_escalation_triggers:
  - rule: "extraction_confidence_below_threshold"
    description: "Any clause confidence < 0.75 escalates"
  - rule: "missing_mandatory_clause_family"
    description: "If mandatory clause absent, escalate contract"

extraction_confidence_threshold: 0.75

approved_governing_laws:
  - "Delaware"
  - "California"
  - "New York"
```

## API Responses

### POST /analyze

```json
{
  "contract_id": "uuid",
  "filename": "string",
  "route_decision": "standard | playbook_negotiable | senior_lawyer_escalation",
  "routing_confidence": 0.95,
  "page_count": 25,
  "extracted_clauses": [
    {
      "family": "liability",
      "confidence": 0.98,
      "status": "match",
      "page": 5
    }
  ],
  "variance_summary": "All clauses match playbook.",
  "redline_count": 0,
  "escalation_reasons": [],
  "approval_packet_ready": false
}
```

### POST /approve-redline

```json
{
  "status": "approval_recorded",
  "approval": {
    "clause_family": "liability",
    "proposed_redline_id": "...",
    "approved_by_lawyer_name": "Jane Doe",
    "approved_by_lawyer_email": "jane@company.com",
    "approval_timestamp": "2026-04-20T14:30:00Z",
    "approval_status": "approved"
  }
}
```

### POST /check-releasable

```json
{
  "contract_id": "uuid",
  "is_releasable": true | false,
  "block_reason": "string (if false)",
  "message": "string"
}
```

### GET /audit-trail/{contract_id}

```json
{
  "contract_id": "uuid",
  "audit_trail": [
    {
      "event_type": "ingestion_started",
      "timestamp": "2026-04-20T14:00:00Z",
      "actor": "system",
      "event_details": { "filename": "...", "size_bytes": 150000 },
      "outcome": "success"
    },
    {
      "event_type": "extraction_complete",
      "timestamp": "2026-04-20T14:02:15Z",
      "actor": "system",
      "event_details": { "route_decision": "standard", "clause_count": 7 },
      "outcome": "success"
    }
  ]
}
```
