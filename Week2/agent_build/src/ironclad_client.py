"""
Ironclad CLM integration interface and mock implementation.
Derived from D4 T-02/T-12, D5 §2 (Ironclad system entry), CLAUDE.md §2.

IroncladClient is the abstract interface.
MockIroncladClient is an in-memory implementation for development and testing.
The real REST client (requiring tenant URL + API token + custom field schema)
is a TODO pending Gap G-4 resolution (D5 §3).
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from .models import Contract, ClauseReview, ReviewDecision


@dataclass
class IroncladCaseRecord:
    """In-memory representation of an Ironclad case record."""
    case_id: str
    contract_id: str
    status: str
    vendor_name: str
    created_at: datetime
    playbook_version: Optional[str] = None
    routing_classification: Optional[str] = None
    clause_reviews: list[dict] = field(default_factory=list)
    review_decision: Optional[dict] = None
    # Sign-off fields — written only by named-lawyer action; never by the agent
    lawyer_signoff_name: Optional[str] = None
    lawyer_signoff_timestamp: Optional[datetime] = None


class IroncladClient(abc.ABC):
    """Abstract interface for the Ironclad CLM integration."""

    @abc.abstractmethod
    def create_case(self, contract: Contract) -> str:
        """Creates a case record for the contract. Returns the Ironclad case ID."""

    @abc.abstractmethod
    def write_clause_reviews(self, contract_id: UUID, reviews: list[ClauseReview]) -> None:
        """Writes all 7 per-clause classification outputs to the case record (T-12)."""

    @abc.abstractmethod
    def write_routing_decision(self, contract_id: UUID, decision: ReviewDecision) -> None:
        """Writes the routing decision to the case record."""

    @abc.abstractmethod
    def get_vendor_case_history(
        self,
        vendor_name: str,
        last_n_quarters: int = 2,
    ) -> list[dict]:
        """Returns prior case summaries for the vendor (ET-6 historical check)."""

    @abc.abstractmethod
    def read_lawyer_signoff(self, contract_id: UUID) -> Optional[str]:
        """
        Returns the lawyer_signoff_name if present — read-only for the agent.
        The agent must never write this field.
        """

    @abc.abstractmethod
    def get_case(self, contract_id: UUID) -> Optional[IroncladCaseRecord]:
        """Returns the full case record, or None if not found."""


class MockIroncladClient(IroncladClient):
    """
    In-memory mock for development and testing.
    All writes are stored in a dict; no HTTP calls are made.
    """

    def __init__(self) -> None:
        self._cases: dict[str, IroncladCaseRecord] = {}
        self._next_id = 1

    def create_case(self, contract: Contract) -> str:
        case_id = f"IRONCLAD-MOCK-{self._next_id:04d}"
        self._next_id += 1
        self._cases[str(contract.contract_id)] = IroncladCaseRecord(
            case_id=case_id,
            contract_id=str(contract.contract_id),
            status=contract.status.value,
            vendor_name=contract.vendor_name,
            created_at=datetime.utcnow(),
            playbook_version=contract.playbook_version_used,
        )
        return case_id

    def write_clause_reviews(self, contract_id: UUID, reviews: list[ClauseReview]) -> None:
        case = self._require_case(contract_id)
        case.clause_reviews = [
            {
                "clause_review_id": str(r.clause_review_id),
                "task_unit_type": r.task_unit_type.value,
                "playbook_match_status": r.playbook_match_status.value,
                "agent_confidence_score": r.agent_confidence_score,
                "extracted_text": r.extracted_text,
                "agent_reasoning_summary": r.agent_reasoning_summary,
                "playbook_section_retrieved": r.playbook_section_retrieved,
                "human_override": r.human_override,
            }
            for r in reviews
        ]

    def write_routing_decision(self, contract_id: UUID, decision: ReviewDecision) -> None:
        case = self._require_case(contract_id)
        case.routing_classification = decision.decision_type.value
        case.review_decision = {
            "decision_id": str(decision.decision_id),
            "decision_type": decision.decision_type.value,
            "decision_made_by": decision.decision_made_by,
            "requires_lawyer_approval": decision.requires_lawyer_approval,
            "approval_token": decision.approval_token,  # always None when written by agent
        }

    def get_vendor_case_history(
        self,
        vendor_name: str,
        last_n_quarters: int = 2,
    ) -> list[dict]:
        name_lower = vendor_name.lower().strip()
        return [
            {
                "contract_id": c.contract_id,
                "case_id": c.case_id,
                "routing_classification": c.routing_classification,
                "vendor_name": c.vendor_name,
            }
            for c in self._cases.values()
            if c.vendor_name.lower().strip() == name_lower
        ]

    def read_lawyer_signoff(self, contract_id: UUID) -> Optional[str]:
        case = self._cases.get(str(contract_id))
        if case is None:
            return None
        return case.lawyer_signoff_name  # always None in mock — set by lawyers only

    def get_case(self, contract_id: UUID) -> Optional[IroncladCaseRecord]:
        return self._cases.get(str(contract_id))

    # Test helper: simulate a lawyer recording sign-off (never called by agent code)
    def _simulate_lawyer_signoff(
        self,
        contract_id: UUID,
        lawyer_name: str,
        timestamp: Optional[datetime] = None,
    ) -> None:
        case = self._require_case(contract_id)
        case.lawyer_signoff_name = lawyer_name
        case.lawyer_signoff_timestamp = timestamp or datetime.utcnow()

    def _require_case(self, contract_id: UUID) -> IroncladCaseRecord:
        case = self._cases.get(str(contract_id))
        if case is None:
            raise ValueError(
                f"No Ironclad case record found for contract {contract_id}. "
                "Case must be created via create_case() before any write operation."
            )
        return case
