"""
Data contracts: Pydantic models for all inputs, outputs, and internal state.
Maps to docs/data-contracts.md.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RouteDecision(str, Enum):
    STANDARD = "standard"
    PLAYBOOK_NEGOTIABLE = "playbook_negotiable"
    SENIOR_LAWYER_ESCALATION = "senior_lawyer_escalation"


class ClauseStatus(str, Enum):
    MATCH = "match"
    NEGOTIABLE_DEVIATION = "negotiable_deviation"
    ESCALATE = "escalate"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExtractedClause(BaseModel):
    """A single extracted clause with location, extracted text, and confidence."""
    family: str  # e.g. "liability", "dpa", "termination"
    source_text: str  # Raw text from contract
    page_number: int
    confidence_score: float = Field(ge=0.0, le=1.0)
    status: ClauseStatus
    variance_reason: Optional[str] = None  # Why it differs from playbook if status != MATCH
    escalation_reason: Optional[str] = None  # Why it triggered escalation if status == ESCALATE


class RedlineProposal(BaseModel):
    """A proposed redline using only approved fallback language."""
    clause_family: str
    current_language: str
    proposed_language: str  # Must match playbook fallback exactly
    playbook_fallback_reference: str  # Which playbook entry allows this
    rationale: str  # Why this redline is proposed


class ContractReviewResult(BaseModel):
    """Output of contract analysis: routing decision + evidence."""
    contract_id: str
    filename: str
    file_size_bytes: int
    page_count: int
    ingestion_timestamp: datetime
    
    route_decision: RouteDecision
    routing_confidence: float = Field(ge=0.0, le=1.0)
    
    extracted_clauses: List[ExtractedClause]
    variance_summary: str  # Human-readable summary of deviations
    
    redline_proposals: List[RedlineProposal]  # Empty if route is STANDARD
    escalation_reasons: List[str]  # Why escalated if route is ESCALATION
    
    analysis_timestamp: datetime


class ApprovalRecord(BaseModel):
    """Approval record for a negotiated clause."""
    clause_family: str
    proposed_redline_id: str
    approved_by_lawyer_name: str
    approved_by_lawyer_email: str
    approval_timestamp: datetime
    approval_status: ApprovalStatus
    notes: Optional[str] = None


class ReleasablePackage(BaseModel):
    """A contract review package ready (or not) for release to vendor."""
    contract_review_result: ContractReviewResult
    clause_approvals: List[ApprovalRecord]
    
    is_releasable: bool  # True only if all proposed redlines have lawyer approvals
    release_block_reason: Optional[str] = None
    prepared_for_release_timestamp: Optional[datetime] = None


class AuditEvent(BaseModel):
    """Audit log entry for full compliance trail."""
    event_type: str  # e.g. "extraction", "routing", "redline_proposal", "approval_granted", "release_attempted", "release_blocked"
    timestamp: datetime
    contract_id: str
    actor: Optional[str] = None  # Human or agent name
    event_details: Dict[str, Any]
    outcome: str  # "success", "warning", "blocked"
