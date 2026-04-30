"""
Escalation trigger evaluator — ET-1 through ET-6.
All triggers are pure logic derived from D4 §6 and CLAUDE.md §6.
No external I/O; testable without dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .models import ClauseReview, TaskUnitType, PlaybookMatchStatus
from .config import CONFIDENCE_THRESHOLD, VENDOR_NAME_FUZZY_THRESHOLD


@dataclass
class EscalationTrigger:
    trigger_id: str        # ET-1 through ET-6
    condition: str         # human-readable description for HITL payload
    clause_review: Optional[ClauseReview]
    additional_context: dict = field(default_factory=dict)
    response_sla_hours: int = 2


def evaluate_escalation_triggers(
    reviews: list[ClauseReview],
    ironclad_vendor_history: Optional[list[dict]] = None,
    vendor_name: Optional[str] = None,
) -> list[EscalationTrigger]:
    """
    Evaluates all applicable escalation triggers against the completed ClauseReview set.
    Returns a list of triggers that fired; empty list means autonomous standard path.
    """
    triggers: list[EscalationTrigger] = []
    seen_et4: set[str] = set()  # prevent duplicate ET-4 per clause type

    for review in reviews:

        # ET-1: confidence below threshold on any clause classification
        if review.agent_confidence_score < CONFIDENCE_THRESHOLD:
            triggers.append(EscalationTrigger(
                trigger_id="ET-1",
                condition=(
                    f"Confidence {review.agent_confidence_score:.2f} < {CONFIDENCE_THRESHOLD} "
                    f"on {review.task_unit_type.value} classification"
                ),
                clause_review=review,
                additional_context={
                    "confidence_score": review.agent_confidence_score,
                    "threshold": CONFIDENCE_THRESHOLD,
                    "agents_best_classification": review.playbook_match_status.value,
                    "reasoning": review.agent_reasoning_summary,
                },
                response_sla_hours=2,
            ))

        # ET-2: DPA clause — mandatory HITL regardless of confidence (CLAUDE.md §3)
        if review.task_unit_type == TaskUnitType.DATA_PROCESSING_AGREEMENT:
            triggers.append(EscalationTrigger(
                trigger_id="ET-2",
                condition=(
                    "DATA_PROCESSING_AGREEMENT clause present — mandatory HITL. "
                    "Playbook v3.4 does not incorporate DPDI Act Q1 updates "
                    "(legitimate interests test, data subject access changes). "
                    "Classification reflects UK GDPR / DPA 2018 only. "
                    "Escalate to Amelia (GC) if this clause is subject to negotiation."
                ),
                clause_review=review,
                additional_context={
                    "dpdi_staleness_flag": True,
                    "playbook_version": review.playbook_section_retrieved,
                    "agents_classification": review.playbook_match_status.value,
                },
                response_sla_hours=4,
            ))

        # ET-3: clause not found with low absence confidence
        if (
            review.playbook_match_status == PlaybookMatchStatus.MISSING
            and review.agent_confidence_score < CONFIDENCE_THRESHOLD
        ):
            triggers.append(EscalationTrigger(
                trigger_id="ET-3",
                condition=(
                    f"{review.task_unit_type.value} not found — confidence on absence "
                    f"{review.agent_confidence_score:.2f} < {CONFIDENCE_THRESHOLD}. "
                    "Clause may be embedded under a non-standard heading. "
                    "Manual keyword verification required before routing."
                ),
                clause_review=review,
                additional_context={
                    "confidence_absent": review.agent_confidence_score,
                    "action": (
                        "Tom: run keyword search for clause before approving routing. "
                        "Headings searched are listed in the ClauseReview record."
                    ),
                },
                response_sla_hours=2,
            ))

        # ET-4: escalation-required classification
        if review.playbook_match_status in (
            PlaybookMatchStatus.MAJOR_DEVIATION,
            PlaybookMatchStatus.REQUIRES_SENIOR_REVIEW,
        ):
            key = review.task_unit_type.value
            if key not in seen_et4:
                seen_et4.add(key)
                triggers.append(EscalationTrigger(
                    trigger_id="ET-4",
                    condition=(
                        f"{review.task_unit_type.value} is {review.playbook_match_status.value} — "
                        "contract-level routing is ESCALATION_REQUIRED. "
                        "Route to WS3 (senior lawyer review)."
                    ),
                    clause_review=review,
                    additional_context={
                        "match_status": review.playbook_match_status.value,
                        "reasoning": review.agent_reasoning_summary,
                    },
                    response_sla_hours=8,
                ))

    # ET-5 is evaluated by the classifier when a numeric deviation > 50% is detected.
    # The classifier sets playbook_match_status to MAJOR_DEVIATION in that case,
    # which triggers ET-4. ET-5 is a specialised annotation added by the classifier
    # to the agent_reasoning_summary — it does not require separate trigger logic here.

    # ET-6: vendor history shows prior escalation
    if ironclad_vendor_history and vendor_name:
        prior_escalations = [
            c for c in ironclad_vendor_history
            if c.get("routing_classification") == "ESCALATION_REQUIRED"
        ]
        if prior_escalations:
            triggers.append(EscalationTrigger(
                trigger_id="ET-6",
                condition=(
                    f"Vendor '{vendor_name}' has {len(prior_escalations)} "
                    "escalation-required case(s) in Ironclad history "
                    "(past 2 quarters). Review current contract for the same "
                    "clause types before confirming routing."
                ),
                clause_review=None,
                additional_context={
                    "prior_case_ids": [c.get("contract_id") for c in prior_escalations],
                    "action": "Confirm vendor identity and review prior escalation clause types.",
                },
                response_sla_hours=2,
            ))

    return triggers


def has_dpa_flag(triggers: list[EscalationTrigger]) -> bool:
    """True if ET-2 (mandatory DPA flag) fired."""
    return any(t.trigger_id == "ET-2" for t in triggers)


def has_escalation_required(triggers: list[EscalationTrigger]) -> bool:
    """True if ET-4 (escalation-required routing) fired."""
    return any(t.trigger_id == "ET-4" for t in triggers)


def _levenshtein(a: str, b: str) -> int:
    """Simple Levenshtein distance for ET-6 vendor name fuzzy matching."""
    a, b = a.lower(), b.lower()
    if len(a) < len(b):
        a, b = b, a
    row = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        new_row = [i]
        for j, cb in enumerate(b, 1):
            new_row.append(min(new_row[j - 1] + 1, row[j] + 1, row[j - 1] + (ca != cb)))
        row = new_row
    return row[-1]
