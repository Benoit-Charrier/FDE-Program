"""
Hard stop enforcement for the Clause Classification Agent.
Derived from D4 §8 (Out-of-Scope) and CLAUDE.md §5.

Every public function raises HardStopViolation if a forbidden action is attempted.
Call these functions at the point of the action — before any write, dispatch, or state change.
"""
from __future__ import annotations

from .models import ClauseReview, ContractStatus, DecisionType, ReviewDecision, TaskUnitType, ALL_TASK_UNIT_TYPES


class HardStopViolation(Exception):
    """Raised when the agent attempts an action that violates a hard stop."""


# ---------------------------------------------------------------------------
# Hard stop 1: No redline, counteroffer, or negotiating language
# ---------------------------------------------------------------------------

_REDLINE_KEYWORDS = frozenset([
    "redline", "counteroffer", "counter-offer", "counter offer",
    "negotiate", "negotiating position", "redraft", "mark up",
    "amend language", "revised language", "suggest language",
    "propose language", "draft response",
])


def assert_no_redline_generation(requested_action: str) -> None:
    """Raises if the requested action would generate redline or negotiating content."""
    action_lower = requested_action.lower()
    for keyword in _REDLINE_KEYWORDS:
        if keyword in action_lower:
            raise HardStopViolation(
                f"Hard stop 1: agent must not generate redline, counteroffer, or negotiating "
                f"language. Forbidden keyword '{keyword}' in action: '{requested_action}'. "
                "Agent scope is classification and triage routing only."
            )


# ---------------------------------------------------------------------------
# Hard stop 2: No write to sign-off or approval fields
# ---------------------------------------------------------------------------

_PROTECTED_FIELDS = frozenset([
    "approval_token",
    "lawyer_signoff_name",
    "lawyer_signoff_timestamp",
])


def assert_no_signoff_field_write(field_name: str) -> None:
    """Raises if the agent attempts to write any sign-off or approval field."""
    if field_name in _PROTECTED_FIELDS:
        raise HardStopViolation(
            f"Hard stop 2/3: agent must never write '{field_name}'. "
            "This field is set exclusively by a named-lawyer action in Ironclad. "
            "Any attempt to write this field is a governance violation."
        )


# ---------------------------------------------------------------------------
# Hard stop 3: No APPROVED state transition
# ---------------------------------------------------------------------------

def assert_no_approved_transition(target: ContractStatus) -> None:
    """Raises if the agent attempts to transition Contract.status to APPROVED."""
    if target == ContractStatus.APPROVED:
        raise HardStopViolation(
            "Hard stop 3: agent must never transition Contract.status to APPROVED. "
            "This transition requires a named-lawyer action in Ironclad. "
            "The agent's highest permitted autonomous transition is REVIEWED_STANDARD."
        )


# ---------------------------------------------------------------------------
# Hard stop 4: No routing without complete classification
# ---------------------------------------------------------------------------

def assert_complete_classification_before_routing(reviews: list[ClauseReview]) -> None:
    """Raises if any of the 7 clause types is missing a ClauseReview record."""
    reviewed_types = {r.task_unit_type for r in reviews}
    missing = ALL_TASK_UNIT_TYPES - reviewed_types
    if missing:
        raise HardStopViolation(
            "Hard stop 4: routing_classification cannot be set until all 7 clause types "
            f"have been assessed. Missing ClauseReview for: "
            f"{', '.join(t.value for t in sorted(missing, key=lambda t: t.value))}"
        )


# ---------------------------------------------------------------------------
# Hard stop 5: No dispatch without Ironclad case record
# ---------------------------------------------------------------------------

def assert_ironclad_case_exists(contract_id, ironclad_case_id: str | None) -> None:
    """Raises if classification is attempted without a confirmed Ironclad case record."""
    if not ironclad_case_id:
        raise HardStopViolation(
            f"Hard stop 5: classification must not begin without a confirmed Ironclad case record. "
            f"Contract {contract_id}: Ironclad case creation has not been confirmed. "
            "Halt processing and flag intake failure to Tom."
        )


# ---------------------------------------------------------------------------
# Hard stop 6: No DPA classification committed without DPDI staleness flag
# ---------------------------------------------------------------------------

def assert_dpa_flag_present(reviews: list[ClauseReview]) -> None:
    """
    Raises if a DPA ClauseReview exists with agent_reasoning_summary that does NOT contain
    the mandatory DPDI staleness annotation.
    Call before writing any DPA ClauseReview to Ironclad.
    """
    _DPDI_MARKER = "DPDI Act updates not reflected"
    for r in reviews:
        if r.task_unit_type == TaskUnitType.DATA_PROCESSING_AGREEMENT:
            if _DPDI_MARKER not in r.agent_reasoning_summary:
                raise HardStopViolation(
                    "Hard stop 6: DATA_PROCESSING_AGREEMENT ClauseReview is missing the "
                    "mandatory DPDI Act staleness annotation in agent_reasoning_summary. "
                    "The annotation must be present on every DPA classification regardless "
                    "of confidence or match status."
                )


# ---------------------------------------------------------------------------
# Hard stop 7: No outbound communication to vendors
# ---------------------------------------------------------------------------

_OUTBOUND_KEYWORDS = frozenset([
    "send email", "email vendor", "dispatch to vendor", "notify vendor",
    "reply to vendor", "send to procurement", "send counteroffer",
    "send redline", "email procurement",
])


def assert_no_outbound_communication(action: str) -> None:
    """Raises if the action would send communication to a vendor or external party."""
    action_lower = action.lower()
    for phrase in _OUTBOUND_KEYWORDS:
        if phrase in action_lower:
            raise HardStopViolation(
                f"Hard stop 7: agent must never communicate with vendors or external parties. "
                f"Forbidden phrase '{phrase}' in action: '{action}'. "
                "All outbound communication is scoped to C-7/C-8 only."
            )


# ---------------------------------------------------------------------------
# Hard stop 8: No SEND_REDLINE/REJECT_CONTRACT without approval_token
# ---------------------------------------------------------------------------

def assert_no_send_redline_without_approval_token(decision: ReviewDecision) -> None:
    """
    Raises if a SEND_REDLINE or REJECT_CONTRACT ReviewDecision has no approval_token.
    This check is for the downstream execution gate (C-7/C-8), not the agent's own write.
    The agent produces the ReviewDecision with approval_token=None;
    the downstream system must check this before dispatching.
    """
    if decision.decision_type in (DecisionType.SEND_REDLINE, DecisionType.REJECT_CONTRACT):
        if decision.approval_token is None:
            raise HardStopViolation(
                f"Hard stop 8: {decision.decision_type.value} action cannot proceed without "
                "a named-lawyer approval_token on the ReviewDecision. "
                "Route the sign-off package to the named lawyer before dispatch."
            )
