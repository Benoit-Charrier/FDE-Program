"""
HITL (Human-in-the-Loop) queue interface and mock implementation.
Routes flagged cases to Tom's review queue with structured payloads.
Derived from D4 §5/§6, D5 §3 (Gap G-1), CLAUDE.md §6.

HITLQueue is the abstract interface.
MockHITLQueue is an in-memory implementation (stdout + stored list) for testing.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from .models import ClauseReview, TaskUnitType
from .escalation import EscalationTrigger


@dataclass
class HITLPayload:
    """Structured payload delivered to Tom's review queue for each escalation trigger."""
    contract_id: UUID
    ironclad_case_id: str
    trigger_id: str                          # ET-1 through ET-6
    condition_description: str               # human-readable trigger condition
    clause_review: Optional[ClauseReview]    # None for ET-6 (vendor history trigger)
    additional_context: dict
    response_sla_hours: int
    created_at: datetime = field(default_factory=datetime.utcnow)


class HITLQueue(abc.ABC):
    @abc.abstractmethod
    def enqueue(self, payload: HITLPayload) -> None:
        """Routes a flagged case item to Tom's review queue."""

    @abc.abstractmethod
    def pending(self, contract_id: UUID) -> list[HITLPayload]:
        """Returns all pending HITL items for a contract."""


class MockHITLQueue(HITLQueue):
    """
    In-memory mock: stores payloads in a list and prints them to stdout.
    Suitable for local development and tests.
    """

    def __init__(self) -> None:
        self._queue: list[HITLPayload] = []

    def enqueue(self, payload: HITLPayload) -> None:
        self._queue.append(payload)
        clause_type = (
            payload.clause_review.task_unit_type.value
            if payload.clause_review
            else "N/A"
        )
        print(
            f"\n[HITL → Tom] {payload.trigger_id} | Contract {payload.contract_id}\n"
            f"  Clause    : {clause_type}\n"
            f"  Condition : {payload.condition_description}\n"
            f"  SLA       : {payload.response_sla_hours}h\n"
            f"  Case      : {payload.ironclad_case_id}\n"
        )

    def pending(self, contract_id: UUID) -> list[HITLPayload]:
        return [p for p in self._queue if p.contract_id == contract_id]

    def all_items(self) -> list[HITLPayload]:
        return list(self._queue)

    def clear(self) -> None:
        self._queue.clear()


# ---------------------------------------------------------------------------
# Helper: build HITL payloads from escalation triggers
# ---------------------------------------------------------------------------

_SLA_MAP: dict[str, int] = {
    "ET-1": 2,
    "ET-2": 4,
    "ET-3": 2,
    "ET-4": 8,
    "ET-5": 2,
    "ET-6": 2,
}


def build_hitl_payloads(
    contract_id: UUID,
    ironclad_case_id: str,
    triggers: list[EscalationTrigger],
) -> list[HITLPayload]:
    """Converts EscalationTrigger list into HITLPayload list for queue delivery."""
    return [
        HITLPayload(
            contract_id=contract_id,
            ironclad_case_id=ironclad_case_id,
            trigger_id=t.trigger_id,
            condition_description=t.condition,
            clause_review=t.clause_review,
            additional_context=t.additional_context,
            response_sla_hours=_SLA_MAP.get(t.trigger_id, 2),
        )
        for t in triggers
    ]
