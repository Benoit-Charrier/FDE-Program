"""Tests for routing classification aggregation logic."""
import pytest
from uuid import uuid4

from src.aggregator import (
    aggregate_routing_classification,
    determine_decision_type,
    requires_lawyer_approval_for,
)
from src.models import (
    ClauseReview,
    DecisionType,
    PlaybookMatchStatus,
    RoutingClassification,
    TaskUnitType,
)


def make_review(
    clause_type: TaskUnitType,
    status: PlaybookMatchStatus = PlaybookMatchStatus.COMPLIANT,
    confidence: float = 0.90,
) -> ClauseReview:
    return ClauseReview(
        contract_id=uuid4(),
        task_unit_type=clause_type,
        extracted_text=None if status == PlaybookMatchStatus.MISSING else "text",
        playbook_match_status=status,
        agent_confidence_score=confidence,
        agent_reasoning_summary="reason",
        playbook_section_retrieved="section",
    )


def all_compliant_reviews(confidence: float = 0.90) -> list[ClauseReview]:
    return [make_review(t, PlaybookMatchStatus.COMPLIANT, confidence) for t in TaskUnitType]


class TestAggregateRoutingClassification:
    def test_all_compliant_high_confidence_is_standard(self):
        reviews = all_compliant_reviews(confidence=0.90)
        assert aggregate_routing_classification(reviews) == RoutingClassification.STANDARD

    def test_one_minor_deviation_is_negotiable(self):
        reviews = all_compliant_reviews()
        reviews[0] = make_review(TaskUnitType.LIABILITY_CAP, PlaybookMatchStatus.MINOR_DEVIATION)
        assert aggregate_routing_classification(reviews) == RoutingClassification.NEGOTIABLE

    def test_one_major_deviation_is_escalation_required(self):
        reviews = all_compliant_reviews()
        reviews[0] = make_review(TaskUnitType.IP_OWNERSHIP, PlaybookMatchStatus.MAJOR_DEVIATION)
        assert aggregate_routing_classification(reviews) == RoutingClassification.ESCALATION_REQUIRED

    def test_requires_senior_review_is_escalation_required(self):
        reviews = all_compliant_reviews()
        reviews[0] = make_review(TaskUnitType.INDEMNITY_SCOPE, PlaybookMatchStatus.REQUIRES_SENIOR_REVIEW)
        assert aggregate_routing_classification(reviews) == RoutingClassification.ESCALATION_REQUIRED

    def test_major_deviation_overrides_minor_deviation(self):
        reviews = [
            make_review(TaskUnitType.LIABILITY_CAP, PlaybookMatchStatus.MINOR_DEVIATION),
            make_review(TaskUnitType.IP_OWNERSHIP, PlaybookMatchStatus.MAJOR_DEVIATION),
        ] + [
            make_review(t, PlaybookMatchStatus.COMPLIANT)
            for t in TaskUnitType
            if t not in (TaskUnitType.LIABILITY_CAP, TaskUnitType.IP_OWNERSHIP)
        ]
        assert aggregate_routing_classification(reviews) == RoutingClassification.ESCALATION_REQUIRED

    def test_low_confidence_prevents_standard_autonomous_routing(self):
        reviews = all_compliant_reviews(confidence=0.80)  # below threshold
        result = aggregate_routing_classification(reviews)
        assert result != RoutingClassification.STANDARD, (
            "Low confidence on COMPLIANT clauses should not produce autonomous STANDARD routing"
        )

    def test_empty_reviews_raises(self):
        with pytest.raises(ValueError, match="empty"):
            aggregate_routing_classification([])


class TestDecisionType:
    def test_standard_maps_to_accept_as_is(self):
        assert determine_decision_type(RoutingClassification.STANDARD) == DecisionType.ACCEPT_AS_IS

    def test_negotiable_maps_to_send_redline(self):
        assert determine_decision_type(RoutingClassification.NEGOTIABLE) == DecisionType.SEND_REDLINE

    def test_escalation_required_maps_to_escalate(self):
        assert determine_decision_type(RoutingClassification.ESCALATION_REQUIRED) == DecisionType.ESCALATE


class TestRequiresLawyerApproval:
    def test_send_redline_requires_approval(self):
        assert requires_lawyer_approval_for(DecisionType.SEND_REDLINE) is True

    def test_reject_contract_requires_approval(self):
        assert requires_lawyer_approval_for(DecisionType.REJECT_CONTRACT) is True

    def test_accept_as_is_does_not_require_approval(self):
        assert requires_lawyer_approval_for(DecisionType.ACCEPT_AS_IS) is False

    def test_escalate_does_not_require_approval_token(self):
        assert requires_lawyer_approval_for(DecisionType.ESCALATE) is False
