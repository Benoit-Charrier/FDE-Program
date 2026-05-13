"""
MedFlex WS1 Intake Agent — Deterministic Classifiers
Source: D4a_capability_spec_WS1_lean.md §6 Decision Logic

Covers:
  - Message type classification  (D4a §6, Decision 1)
  - Urgency classification        (D4a §6, Decision 3)
  - Confidence gate               (D4a §6, Decision 2)
  - Brief completeness gate       (D4a §6, Decision 4)

All thresholds and keyword lists trace to D4a spec.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta
from typing import Optional

from .models import (
    MatchingBrief,
    BriefStatus,
    HITLGapType,
    HITLQueueItem,
    MessageType,
    SpecialtyRequired,
    CredentialLevel,
    UrgencyLevel,
)

# ---------------------------------------------------------------------------
# Constants — all values trace to D4a §6 or §7
# ---------------------------------------------------------------------------

# D4a §6 Decision 3: explicit urgency keywords
URGENCY_KEYWORDS: frozenset[str] = frozenset([
    "urgent", "asap", "immediately", "emergency", "same day", "today",
])

# D4a §6 Decision 3: IMPLICIT_URGENT threshold — 4 hours
IMPLICIT_URGENT_HOURS: int = 4

# D4a §6 Decision 2: confidence gate thresholds
CONFIDENCE_AUTO_ACCEPT: float = 0.70   # ≥ this → accept
CONFIDENCE_FLAGGED_ACCEPT: float = 0.50  # ≥ this AND < AUTO_ACCEPT → flagged accept
# < FLAGGED_ACCEPT → UNRESOLVED

# D4a §9: facility fuzzy match threshold
# NOTE [assumption — A-D5B-1]: Algorithm not specified in spec (§14 A-4).
# Using threshold value from spec (0.80) but algorithm is a design gap.
FACILITY_FUZZY_THRESHOLD: float = 0.80

# D4a §7: SLA for IMPLICIT_URGENT HITL — 10 minutes
IMPLICIT_URGENT_SLA_MINUTES: int = 10

# D4a §7: SLA for all other HITL escalations — 30 minutes
DEFAULT_HITL_SLA_MINUTES: int = 30


# ---------------------------------------------------------------------------
# Message type classification (D4a §6, Decision 1)
# ---------------------------------------------------------------------------

# Patterns derived from spec decision logic.
# NOTE [assumption — A-D5B-2]: "Prior shift ID" pattern assumed to follow ServiceNow
# sys_id format (alphanumeric, length 32) or a pattern like #SN-NNNN.
# The spec says "references a prior shift ID" without specifying the ID format.
_PRIOR_SHIFT_ID_PATTERN = re.compile(r"(?:#SN-\d+|[a-f0-9]{32})", re.IGNORECASE)


def classify_message_type(
    text: str,
    prior_shift_id_present: bool = False,
) -> MessageType:
    """
    Classify inbound message using the rules from D4a §6 Decision 1.

    Args:
        text: Raw inbound message body.
        prior_shift_id_present: Pre-resolved flag — caller checks if the message
            references a known existing shift record (resolves the "prior shift ID"
            requirement without embedding DB logic here).
    """
    lower = text.lower()

    cancellation_keywords = {"cancel", "cancellation", "no longer need"}
    if any(kw in lower for kw in cancellation_keywords) and prior_shift_id_present:
        return MessageType.CANCELLATION

    modification_keywords = {"change", "update", "modify"}
    if any(kw in lower for kw in modification_keywords) and prior_shift_id_present:
        return MessageType.MODIFICATION

    # "block" or "multiple shifts" with a parseable shift count > 1
    # NOTE [assumption — A-D5B-3]: Spec says "shift count > 1 parseable" but does not
    # specify how to count shifts from unstructured text. Using keyword heuristic only.
    block_keywords = {"block", "multiple shifts", "recurring"}
    if any(kw in lower for kw in block_keywords):
        return MessageType.MULTI_SHIFT_BLOCK

    # STANDARD requires resolvable facility AND parseable datetime — caller must
    # supply these signals; this function receives them as arguments.
    # Default to UNCLASSIFIABLE; caller upgrades to STANDARD when facility resolves.
    return MessageType.UNCLASSIFIABLE


def classify_message_type_full(
    text: str,
    facility_resolved: bool,
    datetime_parseable: bool,
    prior_shift_id_present: bool = False,
) -> MessageType:
    """
    Full classification including STANDARD_SHIFT_REQUEST upgrade.
    Separated from classify_message_type to keep facility-resolution
    concerns out of the text-pattern logic.
    """
    base = classify_message_type(text, prior_shift_id_present)
    if base == MessageType.UNCLASSIFIABLE and facility_resolved and datetime_parseable:
        return MessageType.STANDARD_SHIFT_REQUEST
    return base


# ---------------------------------------------------------------------------
# Urgency classification (D4a §6, Decision 3)
# ---------------------------------------------------------------------------

def classify_urgency(
    text: str,
    shift_datetime_start: Optional[datetime],
    now: Optional[datetime] = None,
) -> UrgencyLevel:
    """
    Classify urgency per D4a §6 Decision 3.

    Args:
        text: Raw message body.
        shift_datetime_start: Parsed shift start (None if not extractable).
        now: Current time — injectable for testing; defaults to UTC now.
    """
    lower = text.lower()
    if any(kw in lower for kw in URGENCY_KEYWORDS):
        return UrgencyLevel.EXPLICIT_URGENT

    if shift_datetime_start is not None:
        now = now or datetime.now(timezone.utc)
        delta: timedelta = shift_datetime_start - now
        if delta.total_seconds() / 3600 <= IMPLICIT_URGENT_HOURS:
            return UrgencyLevel.IMPLICIT_URGENT

    return UrgencyLevel.STANDARD


# ---------------------------------------------------------------------------
# Confidence gate (D4a §6, Decision 2)
# ---------------------------------------------------------------------------

REQUIRED_FIELDS: tuple[str, ...] = (
    "facility_id",
    "unit_type",
    "specialty_required",
    "credential_level",
    "shift_datetime_start",
    "shift_datetime_end",
    "urgency",
)


def apply_confidence_gate(
    extracted_fields: dict[str, object],
    confidence_scores: dict[str, float],
) -> tuple[dict[str, object], list[str], list[str]]:
    """
    Apply the three-tier confidence gate from D4a §6 Decision 2.

    Returns:
        accepted_fields: Fields whose values are accepted (score ≥ 0.50).
        review_flags:    Field names where 0.50 ≤ score < 0.70 (flagged for coordinator).
        missing_fields:  Field names where score < 0.50 or absent (set to UNRESOLVED/None).
    """
    accepted_fields: dict[str, object] = {}
    review_flags: list[str] = []
    missing_fields: list[str] = []

    for field in REQUIRED_FIELDS:
        score = confidence_scores.get(field, 0.0)
        value = extracted_fields.get(field)

        if score >= CONFIDENCE_AUTO_ACCEPT:
            accepted_fields[field] = value
        elif score >= CONFIDENCE_FLAGGED_ACCEPT:
            accepted_fields[field] = value
            review_flags.append(field)
        else:
            accepted_fields[field] = _unresolved_for_field(field)
            missing_fields.append(field)

    return accepted_fields, review_flags, missing_fields


def _unresolved_for_field(field: str) -> object:
    """Return the UNRESOLVED sentinel appropriate for each field type."""
    enum_fields = {
        "specialty_required": SpecialtyRequired.UNRESOLVED,
        "credential_level": CredentialLevel.UNRESOLVED,
    }
    return enum_fields.get(field, None)


# ---------------------------------------------------------------------------
# Brief completeness gate (D4a §6, Decision 4 / REQ-A-2)
# ---------------------------------------------------------------------------

def evaluate_completeness(brief: MatchingBrief) -> tuple[BriefStatus, list[str]]:
    """
    Determine brief_status based on required-field completeness.

    Returns:
        (BriefStatus, missing_fields_list)

    Governance hard stop (REQ-A-2): specialty_required = UNRESOLVED or any
    required field absent → NEEDS_COORDINATOR_INPUT; WS2 must not be triggered.
    """
    missing: list[str] = []

    if brief.facility_id is None:
        missing.append("facility_id")
    if brief.unit_type is None:
        missing.append("unit_type")
    if brief.specialty_required == SpecialtyRequired.UNRESOLVED:
        missing.append("specialty_required")
    if brief.credential_level == CredentialLevel.UNRESOLVED:
        missing.append("credential_level")
    if brief.shift_datetime_start is None:
        missing.append("shift_datetime_start")
    if brief.shift_datetime_end is None:
        missing.append("shift_datetime_end")

    if missing:
        return BriefStatus.NEEDS_COORDINATOR_INPUT, missing
    return BriefStatus.READY_FOR_REVIEW, []


# ---------------------------------------------------------------------------
# HITL queue item factory
# ---------------------------------------------------------------------------

def make_hitl_item(
    brief: MatchingBrief,
    gap_type: HITLGapType,
    agent_note: Optional[str] = None,
    sla_minutes: int = DEFAULT_HITL_SLA_MINUTES,
    now: Optional[datetime] = None,
) -> HITLQueueItem:
    """
    Create a HITLQueueItem for the given brief and gap type (D4a §3).
    sla_deadline is set to now + sla_minutes (D4a §7).
    """
    now = now or datetime.now(timezone.utc)
    return HITLQueueItem(
        matching_brief_id=brief.id,
        gap_type=gap_type,
        missing_fields=brief.missing_fields,
        agent_note=agent_note,
        sla_deadline=now + timedelta(minutes=sla_minutes),
        created_at=now,
        updated_at=now,
    )
