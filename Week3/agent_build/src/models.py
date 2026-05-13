"""
MedFlex WS1 Intake Agent — Data Models
Source: D4a_capability_spec_WS1_lean.md §3
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enums — all values SCREAMING_SNAKE_CASE, exhaustive (D4a §3)
# ---------------------------------------------------------------------------

class SpecialtyRequired(str, Enum):
    RN_GENERAL = "RN_GENERAL"
    RN_ICU     = "RN_ICU"
    RN_ED      = "RN_ED"
    RN_PACU    = "RN_PACU"
    RN_OR      = "RN_OR"
    LPN        = "LPN"
    CNA        = "CNA"
    RN_TELE    = "RN_TELE"
    UNRESOLVED = "UNRESOLVED"


class CredentialLevel(str, Enum):
    RN         = "RN"
    LPN        = "LPN"
    CNA        = "CNA"
    NP         = "NP"
    UNRESOLVED = "UNRESOLVED"


class UrgencyLevel(str, Enum):
    EXPLICIT_URGENT = "EXPLICIT_URGENT"
    IMPLICIT_URGENT = "IMPLICIT_URGENT"
    STANDARD        = "STANDARD"


class MessageType(str, Enum):
    STANDARD_SHIFT_REQUEST = "STANDARD_SHIFT_REQUEST"
    MULTI_SHIFT_BLOCK      = "MULTI_SHIFT_BLOCK"
    CANCELLATION           = "CANCELLATION"
    MODIFICATION           = "MODIFICATION"
    UNCLASSIFIABLE         = "UNCLASSIFIABLE"


class BriefStatus(str, Enum):
    READY_FOR_REVIEW       = "READY_FOR_REVIEW"
    NEEDS_COORDINATOR_INPUT = "NEEDS_COORDINATOR_INPUT"
    ADVANCED_TO_WS2        = "ADVANCED_TO_WS2"
    CANCELLED              = "CANCELLED"


class HITLGapType(str, Enum):
    MISSING_REQUIRED_FIELD       = "MISSING_REQUIRED_FIELD"
    UNCLASSIFIABLE_MESSAGE       = "UNCLASSIFIABLE_MESSAGE"
    IMPLICIT_URGENCY_CONFIRMATION = "IMPLICIT_URGENCY_CONFIRMATION"
    SPECIALTY_AMBIGUITY          = "SPECIALTY_AMBIGUITY"


class HITLStatus(str, Enum):
    OPEN      = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    RESOLVED  = "RESOLVED"
    EXPIRED   = "EXPIRED"


# ---------------------------------------------------------------------------
# MatchingBrief entity (D4a §3)
# ---------------------------------------------------------------------------

class MatchingBrief(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_message_id: str = Field(..., max_length=128)
    facility_id: Optional[str] = None                        # UUID string
    unit_type: Optional[str] = Field(None, max_length=64)
    specialty_required: SpecialtyRequired = SpecialtyRequired.UNRESOLVED
    credential_level: CredentialLevel = CredentialLevel.UNRESOLVED
    shift_datetime_start: Optional[datetime] = None
    shift_datetime_end: Optional[datetime] = None
    urgency: Optional[UrgencyLevel] = None
    message_type: Optional[MessageType] = None
    special_notes: Optional[str] = Field(None, max_length=1000)
    brief_status: BriefStatus = BriefStatus.NEEDS_COORDINATOR_INPUT
    confidence_scores: dict[str, float] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "AGENT"

    @field_validator("source_message_id")
    @classmethod
    def source_message_id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("source_message_id must not be blank")
        return v

    @model_validator(mode="after")
    def end_after_start(self) -> "MatchingBrief":
        if self.shift_datetime_start and self.shift_datetime_end:
            if self.shift_datetime_end <= self.shift_datetime_start:
                raise ValueError("shift_datetime_end must be after shift_datetime_start")
        return self

    # State machine guard: ADVANCED_TO_WS2 requires no UNRESOLVED fields (D4a §10)
    def can_advance_to_ws2(self) -> bool:
        required = [
            self.facility_id,
            self.unit_type,
            self.shift_datetime_start,
            self.shift_datetime_end,
        ]
        no_none = all(f is not None for f in required)
        no_unresolved = (
            self.specialty_required != SpecialtyRequired.UNRESOLVED
            and self.credential_level != CredentialLevel.UNRESOLVED
        )
        return no_none and no_unresolved

    def transition_to(self, new_status: BriefStatus) -> None:
        """Enforce state machine transitions (D4a §10 invalid transitions)."""
        forbidden: dict[tuple[BriefStatus, BriefStatus], str] = {
            (BriefStatus.NEEDS_COORDINATOR_INPUT, BriefStatus.ADVANCED_TO_WS2):
                "Brief must pass READY_FOR_REVIEW before WS2 advance",
            (BriefStatus.ADVANCED_TO_WS2, BriefStatus.READY_FOR_REVIEW):
                "WS2 pipeline already initiated; cancel and resubmit required",
            (BriefStatus.CANCELLED, BriefStatus.READY_FOR_REVIEW):
                "CANCELLED is a terminal state",
            (BriefStatus.CANCELLED, BriefStatus.NEEDS_COORDINATOR_INPUT):
                "CANCELLED is a terminal state",
            (BriefStatus.CANCELLED, BriefStatus.ADVANCED_TO_WS2):
                "CANCELLED is a terminal state",
        }
        key = (self.brief_status, new_status)
        if key in forbidden:
            raise ValueError(f"Invalid transition {self.brief_status} → {new_status}: {forbidden[key]}")
        if new_status == BriefStatus.ADVANCED_TO_WS2 and not self.can_advance_to_ws2():
            raise ValueError("Cannot advance to WS2: required fields are missing or UNRESOLVED")
        self.brief_status = new_status
        self.updated_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# HITLQueueItem entity (D4a §3)
# ---------------------------------------------------------------------------

HITL_SLA_MINUTES = 30  # D4a §7: 30-minute SLA for most escalations


class HITLQueueItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    matching_brief_id: str                                   # FK to MatchingBrief
    gap_type: HITLGapType
    missing_fields: list[str] = Field(default_factory=list)
    agent_note: Optional[str] = Field(None, max_length=500)
    assigned_to: Optional[str] = None                        # coordinator UUID
    status: HITLStatus = HITLStatus.OPEN
    sla_deadline: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return self.status in (HITLStatus.OPEN, HITLStatus.IN_REVIEW) and now > self.sla_deadline

    def transition_to(self, new_status: HITLStatus) -> None:
        forbidden: dict[tuple[HITLStatus, HITLStatus], str] = {
            (HITLStatus.RESOLVED, HITLStatus.IN_REVIEW):
                "Create a new HITLQueueItem if re-work is needed",
            (HITLStatus.EXPIRED, HITLStatus.RESOLVED):
                "Must be re-activated to OPEN first",
            (HITLStatus.OPEN, HITLStatus.RESOLVED):
                "Must pass through IN_REVIEW",
        }
        key = (self.status, new_status)
        if key in forbidden:
            raise ValueError(f"Invalid HITL transition {self.status} → {new_status}: {forbidden[key]}")
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
        if new_status == HITLStatus.RESOLVED:
            self.resolved_at = datetime.now(timezone.utc)
