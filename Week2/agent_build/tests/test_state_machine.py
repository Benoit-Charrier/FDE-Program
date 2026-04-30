"""Tests for the Contract state machine."""
import pytest
from datetime import datetime

from src.models import Contract, ContractStatus
from src.state_machine import StateMachineError, transition, assert_not_approved_transition


def make_contract(status: ContractStatus = ContractStatus.PENDING_REVIEW) -> Contract:
    c = Contract(
        vendor_name="VendorCo",
        vendor_email="v@v.com",
        date_received=datetime.utcnow(),
        document_filename="test.docx",
    )
    return c.model_copy(update={"status": status})


class TestValidTransitions:
    def test_pending_to_in_review(self):
        c = make_contract(ContractStatus.PENDING_REVIEW)
        c2 = transition(c, ContractStatus.IN_REVIEW)
        assert c2.status == ContractStatus.IN_REVIEW

    def test_in_review_to_reviewed_standard(self):
        c = make_contract(ContractStatus.IN_REVIEW)
        c2 = transition(c, ContractStatus.REVIEWED_STANDARD)
        assert c2.status == ContractStatus.REVIEWED_STANDARD

    def test_in_review_to_awaiting_approval(self):
        c = make_contract(ContractStatus.IN_REVIEW)
        c2 = transition(c, ContractStatus.AWAITING_APPROVAL)
        assert c2.status == ContractStatus.AWAITING_APPROVAL

    def test_awaiting_approval_to_redline_draft(self):
        c = make_contract(ContractStatus.AWAITING_APPROVAL)
        c2 = transition(c, ContractStatus.REDLINE_DRAFT)
        assert c2.status == ContractStatus.REDLINE_DRAFT

    def test_any_status_can_escalate(self):
        for status in (
            ContractStatus.IN_REVIEW,
            ContractStatus.AWAITING_APPROVAL,
            ContractStatus.REVIEWED_STANDARD,
            ContractStatus.REDLINE_DRAFT,
        ):
            c = make_contract(status)
            c2 = transition(c, ContractStatus.ESCALATED)
            assert c2.status == ContractStatus.ESCALATED

    def test_transition_returns_new_object(self):
        c = make_contract(ContractStatus.PENDING_REVIEW)
        c2 = transition(c, ContractStatus.IN_REVIEW)
        assert c is not c2
        assert c.status == ContractStatus.PENDING_REVIEW  # original unchanged


class TestInvalidTransitions:
    def test_pending_cannot_jump_to_reviewed_standard(self):
        c = make_contract(ContractStatus.PENDING_REVIEW)
        with pytest.raises(StateMachineError, match="Invalid state transition"):
            transition(c, ContractStatus.REVIEWED_STANDARD)

    def test_terminal_escalated_has_no_valid_transitions(self):
        c = make_contract(ContractStatus.ESCALATED)
        with pytest.raises(StateMachineError, match="terminal state"):
            transition(c, ContractStatus.IN_REVIEW)

    def test_closed_is_terminal(self):
        c = make_contract(ContractStatus.CLOSED)
        with pytest.raises(StateMachineError, match="terminal state"):
            transition(c, ContractStatus.REVIEWED_STANDARD)


class TestLawyerOnlyTransitions:
    def test_agent_cannot_transition_to_approved(self):
        c = make_contract(ContractStatus.AWAITING_APPROVAL)
        with pytest.raises(StateMachineError, match="lawyer-only action"):
            transition(c, ContractStatus.APPROVED)

    def test_assert_not_approved_raises_for_approved(self):
        with pytest.raises(StateMachineError, match="must never transition"):
            assert_not_approved_transition(ContractStatus.APPROVED)

    def test_assert_not_approved_passes_for_other_statuses(self):
        # Should not raise for any status other than APPROVED
        for status in ContractStatus:
            if status != ContractStatus.APPROVED:
                assert_not_approved_transition(status)  # no exception
