"""
Contract state machine for the Clause Classification Agent.
Derived from CLAUDE.md §2 (Contract state machine).

Valid transitions are determined by VALID_AGENT_TRANSITIONS.
The AWAITING_APPROVAL → APPROVED transition is intentionally excluded:
it is a lawyer-only action and the agent must never initiate it.
"""
from __future__ import annotations

from .models import Contract, ContractStatus

# Transitions the agent is permitted to initiate.
# AWAITING_APPROVAL → APPROVED is NOT here — it is lawyer-only.
VALID_AGENT_TRANSITIONS: dict[ContractStatus, set[ContractStatus]] = {
    ContractStatus.PENDING_REVIEW: {
        ContractStatus.IN_REVIEW,
    },
    ContractStatus.IN_REVIEW: {
        ContractStatus.REVIEWED_STANDARD,   # all clauses COMPLIANT, confidence ≥ 0.85
        ContractStatus.AWAITING_APPROVAL,   # any HITL condition triggered
        ContractStatus.ESCALATED,           # any team member can escalate at any time
    },
    ContractStatus.AWAITING_APPROVAL: {
        # Tom's decisions are recorded in Ironclad and committed here:
        ContractStatus.REVIEWED_STANDARD,
        ContractStatus.REDLINE_DRAFT,
        ContractStatus.ESCALATED,
    },
    ContractStatus.REVIEWED_STANDARD: {
        ContractStatus.CLOSED,
        ContractStatus.ESCALATED,
    },
    ContractStatus.REDLINE_DRAFT: {
        ContractStatus.AWAITING_APPROVAL,   # WS2 redline complete; sign-off package ready
        ContractStatus.ESCALATED,
    },
    ContractStatus.APPROVED: {
        ContractStatus.CLOSED,              # C-7/C-8 dispatches the counteroffer
    },
    ContractStatus.ESCALATED: set(),        # terminal within CCA scope
    ContractStatus.CLOSED: set(),           # terminal
}

# Transitions that are exclusively lawyer-initiated (agent must never trigger these)
LAWYER_ONLY_TRANSITIONS: frozenset[tuple[ContractStatus, ContractStatus]] = frozenset({
    (ContractStatus.AWAITING_APPROVAL, ContractStatus.APPROVED),
})


class StateMachineError(Exception):
    """Raised when an invalid or forbidden state transition is attempted."""


def transition(
    contract: Contract,
    target: ContractStatus,
) -> Contract:
    """
    Returns a new Contract with status updated to target.
    Raises StateMachineError if the transition is invalid or lawyer-only.
    """
    current = contract.status

    if (current, target) in LAWYER_ONLY_TRANSITIONS:
        raise StateMachineError(
            f"Transition {current.value} → {target.value} is a lawyer-only action. "
            "The agent must never initiate this transition. "
            "A named-lawyer action in Ironclad is required."
        )

    allowed = VALID_AGENT_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise StateMachineError(
            f"Invalid state transition: {current.value} → {target.value}. "
            f"Allowed from {current.value}: "
            f"{', '.join(s.value for s in allowed) or 'none (terminal state)'}"
        )

    return contract.model_copy(update={"status": target})


def assert_not_approved_transition(target: ContractStatus) -> None:
    """Hard-stop guard: call before any status write to prevent APPROVED transition by agent."""
    if target == ContractStatus.APPROVED:
        raise StateMachineError(
            "Hard stop: the agent must never transition Contract.status to APPROVED. "
            "This requires a named-lawyer action in Ironclad."
        )
