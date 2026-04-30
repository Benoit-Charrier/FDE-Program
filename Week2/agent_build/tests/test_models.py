"""Tests for core Pydantic models — Contract, ClauseReview, ReviewDecision."""
import pytest
from datetime import datetime
from uuid import uuid4

from src.models import (
    Contract,
    ClauseReview,
    ReviewDecision,
    ContractStatus,
    DecisionType,
    PlaybookMatchStatus,
    TaskUnitType,
    RoutingClassification,
)


def make_contract(**kwargs) -> Contract:
    defaults = dict(
        vendor_name="VendorCo Ltd",
        vendor_email="procurement@vendorco.com",
        date_received=datetime(2024, 4, 1, 9, 0, 0),
        document_filename="vendorco_msa.docx",
    )
    defaults.update(kwargs)
    return Contract(**defaults)


class TestContract:
    def test_valid_contract_creates(self):
        c = make_contract()
        assert c.status == ContractStatus.PENDING_REVIEW
        assert c.routing_classification is None
        assert c.lawyer_signoff_name is None

    def test_filename_must_be_docx(self):
        with pytest.raises(ValueError, match="docx"):
            make_contract(document_filename="contract.pdf")

    def test_page_count_out_of_range(self):
        with pytest.raises(ValueError, match="page_count"):
            make_contract(document_page_count=0)
        with pytest.raises(ValueError, match="page_count"):
            make_contract(document_page_count=201)

    def test_signoff_timestamp_requires_name(self):
        with pytest.raises(ValueError, match="lawyer_signoff_timestamp requires"):
            make_contract(lawyer_signoff_timestamp=datetime.utcnow())

    def test_signoff_name_without_timestamp_is_valid(self):
        c = make_contract(lawyer_signoff_name="Sarah Mitchell")
        assert c.lawyer_signoff_name == "Sarah Mitchell"
        assert c.lawyer_signoff_timestamp is None


class TestClauseReview:
    def test_valid_compliant_review(self):
        r = ClauseReview(
            contract_id=uuid4(),
            task_unit_type=TaskUnitType.LIABILITY_CAP,
            extracted_text="Liability is capped at £300,000.",
            playbook_match_status=PlaybookMatchStatus.COMPLIANT,
            agent_confidence_score=0.92,
            agent_reasoning_summary="Exceeds £250k floor.",
            playbook_section_retrieved="LIABILITY_CAP — playbook_v3_4.md (v3.4)",
        )
        assert r.playbook_match_status == PlaybookMatchStatus.COMPLIANT

    def test_extracted_text_null_only_for_missing(self):
        # MISSING with null extracted_text is valid
        r = ClauseReview(
            contract_id=uuid4(),
            task_unit_type=TaskUnitType.GOVERNING_LAW,
            extracted_text=None,
            playbook_match_status=PlaybookMatchStatus.MISSING,
            agent_confidence_score=0.91,
            agent_reasoning_summary="Clause not found.",
            playbook_section_retrieved="GOVERNING_LAW — playbook_v3_4.md (v3.4)",
        )
        assert r.extracted_text is None

    def test_extracted_text_null_for_non_missing_raises(self):
        with pytest.raises(ValueError, match="extracted_text may only be null"):
            ClauseReview(
                contract_id=uuid4(),
                task_unit_type=TaskUnitType.LIABILITY_CAP,
                extracted_text=None,
                playbook_match_status=PlaybookMatchStatus.COMPLIANT,
                agent_confidence_score=0.90,
                agent_reasoning_summary="Reason.",
                playbook_section_retrieved="LIABILITY_CAP",
            )

    def test_confidence_score_bounds(self):
        with pytest.raises(ValueError):
            ClauseReview(
                contract_id=uuid4(),
                task_unit_type=TaskUnitType.LIABILITY_CAP,
                extracted_text="text",
                playbook_match_status=PlaybookMatchStatus.COMPLIANT,
                agent_confidence_score=1.1,
                agent_reasoning_summary="out of range",
                playbook_section_retrieved="section",
            )


class TestReviewDecision:
    def _make_decision(self, decision_type: DecisionType, requires_approval: bool, token=None):
        return ReviewDecision(
            contract_id=uuid4(),
            clause_review_ids=[uuid4()],
            decision_type=decision_type,
            decision_made_by="AGENT",
            requires_lawyer_approval=requires_approval,
            approval_token=token,
        )

    def test_accept_as_is_no_approval_required(self):
        d = self._make_decision(DecisionType.ACCEPT_AS_IS, requires_approval=False)
        assert not d.requires_lawyer_approval

    def test_send_redline_must_require_approval(self):
        with pytest.raises(ValueError, match="requires_lawyer_approval must be True"):
            self._make_decision(DecisionType.SEND_REDLINE, requires_approval=False)

    def test_reject_contract_must_require_approval(self):
        with pytest.raises(ValueError, match="requires_lawyer_approval must be True"):
            self._make_decision(DecisionType.REJECT_CONTRACT, requires_approval=False)

    def test_approval_token_null_at_agent_creation(self):
        d = self._make_decision(DecisionType.SEND_REDLINE, requires_approval=True)
        assert d.approval_token is None
