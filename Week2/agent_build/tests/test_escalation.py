"""Tests for escalation trigger evaluation — ET-1 through ET-6."""
import pytest
from uuid import uuid4

from src.models import ClauseReview, PlaybookMatchStatus, TaskUnitType
from src.escalation import (
    evaluate_escalation_triggers,
    has_dpa_flag,
    has_escalation_required,
)
from src.config import CONFIDENCE_THRESHOLD


def make_review(
    clause_type: TaskUnitType,
    status: PlaybookMatchStatus = PlaybookMatchStatus.COMPLIANT,
    confidence: float = 0.90,
    extracted: str = "Clause text here.",
) -> ClauseReview:
    return ClauseReview(
        contract_id=uuid4(),
        task_unit_type=clause_type,
        extracted_text=None if status == PlaybookMatchStatus.MISSING else extracted,
        playbook_match_status=status,
        agent_confidence_score=confidence,
        agent_reasoning_summary="Test reasoning.",
        playbook_section_retrieved="section",
    )


class TestET1ConfidenceThreshold:
    def test_fires_when_confidence_below_threshold(self):
        reviews = [make_review(TaskUnitType.LIABILITY_CAP, confidence=0.70)]
        triggers = evaluate_escalation_triggers(reviews)
        et1 = [t for t in triggers if t.trigger_id == "ET-1"]
        assert len(et1) == 1
        assert "0.70" in et1[0].condition

    def test_does_not_fire_at_threshold(self):
        reviews = [make_review(TaskUnitType.LIABILITY_CAP, confidence=CONFIDENCE_THRESHOLD)]
        triggers = evaluate_escalation_triggers(reviews)
        assert not any(t.trigger_id == "ET-1" for t in triggers)

    def test_fires_once_per_low_confidence_clause(self):
        reviews = [
            make_review(TaskUnitType.LIABILITY_CAP, confidence=0.70),
            make_review(TaskUnitType.GOVERNING_LAW, confidence=0.60),
        ]
        triggers = evaluate_escalation_triggers(reviews)
        et1 = [t for t in triggers if t.trigger_id == "ET-1"]
        assert len(et1) == 2


class TestET2DPAMandatory:
    def test_fires_for_any_dpa_clause(self):
        reviews = [make_review(TaskUnitType.DATA_PROCESSING_AGREEMENT, confidence=0.95)]
        triggers = evaluate_escalation_triggers(reviews)
        assert has_dpa_flag(triggers)

    def test_fires_even_when_dpa_is_compliant_with_high_confidence(self):
        reviews = [make_review(
            TaskUnitType.DATA_PROCESSING_AGREEMENT,
            status=PlaybookMatchStatus.COMPLIANT,
            confidence=0.99,
        )]
        triggers = evaluate_escalation_triggers(reviews)
        assert has_dpa_flag(triggers), "ET-2 must fire unconditionally for any DPA clause"

    def test_does_not_fire_for_non_dpa_clauses(self):
        reviews = [make_review(TaskUnitType.LIABILITY_CAP, confidence=0.95)]
        triggers = evaluate_escalation_triggers(reviews)
        assert not has_dpa_flag(triggers)


class TestET3MissingClause:
    def test_fires_when_missing_with_low_absence_confidence(self):
        reviews = [make_review(
            TaskUnitType.GOVERNING_LAW,
            status=PlaybookMatchStatus.MISSING,
            confidence=0.50,
        )]
        triggers = evaluate_escalation_triggers(reviews)
        et3 = [t for t in triggers if t.trigger_id == "ET-3"]
        assert len(et3) == 1

    def test_does_not_fire_when_missing_with_high_absence_confidence(self):
        reviews = [make_review(
            TaskUnitType.GOVERNING_LAW,
            status=PlaybookMatchStatus.MISSING,
            confidence=0.92,
        )]
        triggers = evaluate_escalation_triggers(reviews)
        et3 = [t for t in triggers if t.trigger_id == "ET-3"]
        assert len(et3) == 0


class TestET4EscalationRequired:
    def test_fires_for_major_deviation(self):
        reviews = [make_review(
            TaskUnitType.IP_OWNERSHIP,
            status=PlaybookMatchStatus.MAJOR_DEVIATION,
        )]
        triggers = evaluate_escalation_triggers(reviews)
        assert has_escalation_required(triggers)

    def test_fires_for_requires_senior_review(self):
        reviews = [make_review(
            TaskUnitType.INDEMNITY_SCOPE,
            status=PlaybookMatchStatus.REQUIRES_SENIOR_REVIEW,
        )]
        triggers = evaluate_escalation_triggers(reviews)
        assert has_escalation_required(triggers)

    def test_does_not_fire_for_minor_deviation(self):
        reviews = [make_review(
            TaskUnitType.TERMINATION_CLAUSE,
            status=PlaybookMatchStatus.MINOR_DEVIATION,
        )]
        triggers = evaluate_escalation_triggers(reviews)
        assert not has_escalation_required(triggers)


class TestET6VendorHistory:
    def test_fires_when_vendor_has_prior_escalation(self):
        history = [{"contract_id": "old-1", "routing_classification": "ESCALATION_REQUIRED"}]
        reviews = [make_review(TaskUnitType.LIABILITY_CAP)]
        triggers = evaluate_escalation_triggers(reviews, history, "VendorCo")
        et6 = [t for t in triggers if t.trigger_id == "ET-6"]
        assert len(et6) == 1

    def test_does_not_fire_when_no_prior_escalation(self):
        history = [{"contract_id": "old-1", "routing_classification": "STANDARD"}]
        reviews = [make_review(TaskUnitType.LIABILITY_CAP)]
        triggers = evaluate_escalation_triggers(reviews, history, "VendorCo")
        assert not any(t.trigger_id == "ET-6" for t in triggers)

    def test_does_not_fire_with_no_history(self):
        reviews = [make_review(TaskUnitType.LIABILITY_CAP)]
        triggers = evaluate_escalation_triggers(reviews, [], "VendorCo")
        assert not any(t.trigger_id == "ET-6" for t in triggers)


class TestNoTriggersForCleanContract:
    def test_all_compliant_high_confidence_no_dpa_produces_no_triggers(self):
        reviews = [
            make_review(t, status=PlaybookMatchStatus.COMPLIANT, confidence=0.90)
            for t in TaskUnitType
            if t != TaskUnitType.DATA_PROCESSING_AGREEMENT
        ]
        triggers = evaluate_escalation_triggers(reviews, [], "CleanVendor")
        assert triggers == [], f"Expected no triggers, got: {[t.trigger_id for t in triggers]}"
