"""
Core entity models for the Clause Classification Agent.
Derived from CLAUDE.md §2 (Core Entities).
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ContractStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    IN_REVIEW = "IN_REVIEW"
    REVIEWED_STANDARD = "REVIEWED_STANDARD"
    REDLINE_DRAFT = "REDLINE_DRAFT"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"


class RoutingClassification(str, Enum):
    STANDARD = "STANDARD"
    NEGOTIABLE = "NEGOTIABLE"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"


class TaskUnitType(str, Enum):
    LIABILITY_CAP = "LIABILITY_CAP"
    DATA_PROCESSING_AGREEMENT = "DATA_PROCESSING_AGREEMENT"
    TERMINATION_CLAUSE = "TERMINATION_CLAUSE"
    IP_OWNERSHIP = "IP_OWNERSHIP"
    SLA_COMMITMENTS = "SLA_COMMITMENTS"
    GOVERNING_LAW = "GOVERNING_LAW"
    INDEMNITY_SCOPE = "INDEMNITY_SCOPE"


class PlaybookMatchStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    MINOR_DEVIATION = "MINOR_DEVIATION"
    MAJOR_DEVIATION = "MAJOR_DEVIATION"
    MISSING = "MISSING"
    REQUIRES_SENIOR_REVIEW = "REQUIRES_SENIOR_REVIEW"


class DecisionType(str, Enum):
    ACCEPT_AS_IS = "ACCEPT_AS_IS"
    SEND_REDLINE = "SEND_REDLINE"
    ESCALATE = "ESCALATE"
    REJECT_CONTRACT = "REJECT_CONTRACT"


ALL_TASK_UNIT_TYPES: frozenset[TaskUnitType] = frozenset(TaskUnitType)


# ---------------------------------------------------------------------------
# Contract
# ---------------------------------------------------------------------------

class Contract(BaseModel):
    """
    Primary entity: one inbound vendor contract from receipt through closure.
    State machine defined in CLAUDE.md §2.
    """
    contract_id: UUID = Field(default_factory=uuid4)
    vendor_name: str = Field(min_length=1)
    vendor_email: str = Field(min_length=3)
    date_received: datetime
    document_filename: str
    document_page_count: Optional[int] = None
    salesforce_opportunity_id: Optional[str] = None
    routing_classification: Optional[RoutingClassification] = None
    status: ContractStatus = ContractStatus.PENDING_REVIEW
    assigned_reviewer_id: Optional[str] = None
    playbook_version_used: Optional[str] = None

    # Sign-off fields: set exclusively by named-lawyer action in Ironclad; never by the agent.
    lawyer_signoff_name: Optional[str] = None
    lawyer_signoff_timestamp: Optional[datetime] = None

    agent_processing_start: Optional[datetime] = None
    agent_processing_end: Optional[datetime] = None

    @field_validator("document_filename")
    @classmethod
    def filename_must_be_docx(cls, v: str) -> str:
        if not v.lower().endswith(".docx"):
            raise ValueError("document_filename must end in .docx")
        return v

    @field_validator("document_page_count")
    @classmethod
    def page_count_in_range(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (1 <= v <= 200):
            raise ValueError("document_page_count must be between 1 and 200")
        return v

    @model_validator(mode="after")
    def signoff_timestamp_requires_name(self) -> "Contract":
        if self.lawyer_signoff_timestamp is not None and self.lawyer_signoff_name is None:
            raise ValueError(
                "lawyer_signoff_timestamp requires lawyer_signoff_name to be non-null"
            )
        return self


# ---------------------------------------------------------------------------
# ClauseReview
# ---------------------------------------------------------------------------

class ClauseReview(BaseModel):
    """
    One record per clause type per contract (exactly 7 per contract).
    Derived from CLAUDE.md §2.
    """
    clause_review_id: UUID = Field(default_factory=uuid4)
    contract_id: UUID
    task_unit_type: TaskUnitType
    extracted_text: Optional[str] = None
    playbook_match_status: PlaybookMatchStatus
    agent_confidence_score: float = Field(ge=0.0, le=1.0)
    agent_reasoning_summary: str = Field(max_length=500)
    playbook_section_retrieved: str
    human_override: Optional[str] = None

    @model_validator(mode="after")
    def extracted_text_required_unless_missing(self) -> "ClauseReview":
        if (
            self.extracted_text is None
            and self.playbook_match_status != PlaybookMatchStatus.MISSING
        ):
            raise ValueError(
                "extracted_text may only be null when playbook_match_status is MISSING"
            )
        return self


# ---------------------------------------------------------------------------
# ReviewDecision
# ---------------------------------------------------------------------------

class ReviewDecision(BaseModel):
    """
    Routing decision record after clause review is complete.
    approval_token is NEVER set by the agent — it is set exclusively
    by a named-lawyer action in Ironclad.
    Derived from CLAUDE.md §2.
    """
    decision_id: UUID = Field(default_factory=uuid4)
    contract_id: UUID
    clause_review_ids: list[UUID]
    decision_type: DecisionType
    decision_made_by: str
    decision_timestamp: datetime = Field(default_factory=datetime.utcnow)
    requires_lawyer_approval: bool

    # Hard constraint: agent must never write this field.
    # It exists here for the downstream Ironclad read path only.
    approval_token: Optional[str] = None

    @model_validator(mode="after")
    def approval_required_for_send_redline_and_reject(self) -> "ReviewDecision":
        if self.decision_type in (DecisionType.SEND_REDLINE, DecisionType.REJECT_CONTRACT):
            if not self.requires_lawyer_approval:
                raise ValueError(
                    "requires_lawyer_approval must be True for SEND_REDLINE and REJECT_CONTRACT"
                )
        return self

    @model_validator(mode="after")
    def approval_token_must_be_null_at_agent_creation(self) -> "ReviewDecision":
        # The agent must never set approval_token. This validator does not prevent
        # a human/lawyer from setting it via Ironclad — it documents the constraint.
        # The hard_stops module enforces this at the call site.
        return self
