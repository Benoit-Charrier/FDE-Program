"""Tests for hard stop enforcement — all 8 hard stops from D4 §8."""
import pytest
from uuid import uuid4

from src.hard_stops import (
    HardStopViolation,
    assert_no_redline_generation,
    assert_no_signoff_field_write,
    assert_no_approved_transition,
    assert_complete_classification_before_routing,
    assert_ironclad_case_exists,
    assert_dpa_flag_present,
    assert_no_outbound_communication,
    assert_no_send_redline_without_approval_token,
)
from src.models import (
    ClauseReview,
    ContractStatus,
    DecisionType,
    PlaybookMatchStatus,
    ReviewDecision,
    TaskUnitType,
)


def make_review(clause_type: TaskUnitType, status=PlaybookMatchStatus.COMPLIANT, reasoning="ok") -> ClauseReview:
    return ClauseReview(
        contract_id=uuid4(),
        task_unit_type=clause_type,
        extracted_text="text" if status != PlaybookMatchStatus.MISSING else None,
        playbook_match_status=status,
        agent_confidence_score=0.90,
        agent_reasoning_summary=reasoning[:500],
        playbook_section_retrieved="section",
    )


class TestHardStop1NoRedline:
    def test_redline_keyword_raises(self):
        with pytest.raises(HardStopViolation, match="redline"):
            assert_no_redline_generation("generate redline for liability clause")

    def test_counteroffer_keyword_raises(self):
        with pytest.raises(HardStopViolation, match="counteroffer"):
            assert_no_redline_generation("draft counteroffer for DPA clause")

    def test_neutral_action_passes(self):
        assert_no_redline_generation("classify liability clause against playbook")

    def test_negotiate_keyword_raises(self):
        with pytest.raises(HardStopViolation):
            assert_no_redline_generation("propose negotiating position on IP ownership")


class TestHardStop2NoSignoffWrite:
    def test_approval_token_write_raises(self):
        with pytest.raises(HardStopViolation, match="approval_token"):
            assert_no_signoff_field_write("approval_token")

    def test_lawyer_signoff_name_write_raises(self):
        with pytest.raises(HardStopViolation, match="lawyer_signoff_name"):
            assert_no_signoff_field_write("lawyer_signoff_name")

    def test_lawyer_signoff_timestamp_write_raises(self):
        with pytest.raises(HardStopViolation):
            assert_no_signoff_field_write("lawyer_signoff_timestamp")

    def test_other_field_passes(self):
        assert_no_signoff_field_write("routing_classification")


class TestHardStop3NoApprovedTransition:
    def test_approved_raises(self):
        with pytest.raises(HardStopViolation, match="APPROVED"):
            assert_no_approved_transition(ContractStatus.APPROVED)

    def test_other_statuses_pass(self):
        for status in ContractStatus:
            if status != ContractStatus.APPROVED:
                assert_no_approved_transition(status)


class TestHardStop4CompleteClassification:
    def test_all_7_types_passes(self):
        reviews = [make_review(t) for t in TaskUnitType]
        assert_complete_classification_before_routing(reviews)  # no exception

    def test_missing_one_type_raises(self):
        reviews = [make_review(t) for t in TaskUnitType if t != TaskUnitType.GOVERNING_LAW]
        with pytest.raises(HardStopViolation, match="GOVERNING_LAW"):
            assert_complete_classification_before_routing(reviews)

    def test_empty_reviews_raises(self):
        with pytest.raises(HardStopViolation):
            assert_complete_classification_before_routing([])


class TestHardStop5IroncladCaseExists:
    def test_none_case_id_raises(self):
        with pytest.raises(HardStopViolation, match="confirmed Ironclad case record"):
            assert_ironclad_case_exists(uuid4(), None)

    def test_empty_string_raises(self):
        with pytest.raises(HardStopViolation):
            assert_ironclad_case_exists(uuid4(), "")

    def test_valid_case_id_passes(self):
        assert_ironclad_case_exists(uuid4(), "IRONCLAD-MOCK-0001")


class TestHardStop6DPAFlag:
    def test_dpa_without_dpdi_annotation_raises(self):
        dpa_review = make_review(
            TaskUnitType.DATA_PROCESSING_AGREEMENT,
            reasoning="Clause matches UK GDPR standard position.",
        )
        with pytest.raises(HardStopViolation, match="missing the mandatory DPDI Act staleness annotation"):
            assert_dpa_flag_present([dpa_review])

    def test_dpa_with_dpdi_annotation_passes(self):
        dpa_review = make_review(
            TaskUnitType.DATA_PROCESSING_AGREEMENT,
            reasoning=(
                "Matches UK GDPR / DPA 2018. "
                "DPDI Act updates not reflected in playbook v3.4 — "
                "classification reflects UK GDPR / DPA 2018 only."
            ),
        )
        assert_dpa_flag_present([dpa_review])  # no exception

    def test_non_dpa_clauses_without_annotation_pass(self):
        reviews = [make_review(t) for t in TaskUnitType if t != TaskUnitType.DATA_PROCESSING_AGREEMENT]
        assert_dpa_flag_present(reviews)  # no exception


class TestHardStop7NoOutbound:
    def test_send_email_raises(self):
        with pytest.raises(HardStopViolation, match="send email"):
            assert_no_outbound_communication("send email to vendor with counteroffer")

    def test_email_vendor_raises(self):
        with pytest.raises(HardStopViolation):
            assert_no_outbound_communication("email vendor procurement team")

    def test_internal_notification_passes(self):
        assert_no_outbound_communication("write classification report to Ironclad")


class TestHardStop8NoDispatchWithoutToken:
    def _make_decision(self, token=None):
        return ReviewDecision(
            contract_id=uuid4(),
            clause_review_ids=[uuid4()],
            decision_type=DecisionType.SEND_REDLINE,
            decision_made_by="AGENT",
            requires_lawyer_approval=True,
            approval_token=token,
        )

    def test_send_redline_without_token_raises(self):
        decision = self._make_decision(token=None)
        with pytest.raises(HardStopViolation, match="approval_token"):
            assert_no_send_redline_without_approval_token(decision)

    def test_send_redline_with_token_passes(self):
        decision = self._make_decision(token="LAWYER-TOKEN-001")
        assert_no_send_redline_without_approval_token(decision)  # no exception

    def test_accept_as_is_without_token_passes(self):
        decision = ReviewDecision(
            contract_id=uuid4(),
            clause_review_ids=[uuid4()],
            decision_type=DecisionType.ACCEPT_AS_IS,
            decision_made_by="AGENT",
            requires_lawyer_approval=False,
        )
        assert_no_send_redline_without_approval_token(decision)  # no exception
