"""
Aggregates 7 ClauseReview records into a Contract-level routing classification.
Derived from CLAUDE.md §3 (Classification Rules — contract-level).
Pure logic; no external dependencies.
"""
from __future__ import annotations

from .models import (
    ClauseReview,
    DecisionType,
    PlaybookMatchStatus,
    RoutingClassification,
)
from .config import CONFIDENCE_THRESHOLD


def aggregate_routing_classification(reviews: list[ClauseReview]) -> RoutingClassification:
    """
    Determines Contract.routing_classification from all 7 ClauseReview records.

    Precedence rule (CLAUDE.md §3):
        ESCALATION_REQUIRED > NEGOTIABLE > STANDARD

    A single MAJOR_DEVIATION or REQUIRES_SENIOR_REVIEW clause makes the entire
    contract ESCALATION_REQUIRED regardless of other clauses.
    """
    if not reviews:
        raise ValueError("Cannot aggregate routing classification from empty reviews list")

    statuses = {r.playbook_match_status for r in reviews}

    # Escalation-required: any MAJOR_DEVIATION or REQUIRES_SENIOR_REVIEW
    if (
        PlaybookMatchStatus.MAJOR_DEVIATION in statuses
        or PlaybookMatchStatus.REQUIRES_SENIOR_REVIEW in statuses
    ):
        return RoutingClassification.ESCALATION_REQUIRED

    # If any confidence is below threshold, do not commit to STANDARD autonomously.
    # Conservative: treat as NEGOTIABLE so Tom reviews — he may downgrade to STANDARD.
    low_confidence = any(r.agent_confidence_score < CONFIDENCE_THRESHOLD for r in reviews)
    if low_confidence:
        return RoutingClassification.NEGOTIABLE

    # Negotiable: at least one MINOR_DEVIATION, no MAJOR or REQUIRES_SENIOR
    if PlaybookMatchStatus.MINOR_DEVIATION in statuses:
        return RoutingClassification.NEGOTIABLE

    # Standard: all COMPLIANT (or MISSING with Tom-confirmed absence via HITL flow)
    return RoutingClassification.STANDARD


def determine_decision_type(classification: RoutingClassification) -> DecisionType:
    """Maps routing classification to the ReviewDecision type."""
    return {
        RoutingClassification.STANDARD: DecisionType.ACCEPT_AS_IS,
        RoutingClassification.NEGOTIABLE: DecisionType.SEND_REDLINE,
        RoutingClassification.ESCALATION_REQUIRED: DecisionType.ESCALATE,
    }[classification]


def requires_lawyer_approval_for(decision_type: DecisionType) -> bool:
    """
    Returns True for decisions that require named-lawyer sign-off before dispatch.
    ESCALATE routes to WS3 (senior lawyer review), not to dispatch — no approval token needed.
    """
    return decision_type in (DecisionType.SEND_REDLINE, DecisionType.REJECT_CONTRACT)
