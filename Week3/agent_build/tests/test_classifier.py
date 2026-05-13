"""
Tests for deterministic classifiers — message type, urgency, confidence gate,
and completeness gate.

All decision logic traces to D4a_capability_spec_WS1_lean.md §6.
Worked examples from the spec are used as test cases directly.
"""
import pytest
from datetime import datetime, timezone, timedelta

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.models import (
    MatchingBrief,
    BriefStatus,
    HITLStatus,
    HITLGapType,
    MessageType,
    SpecialtyRequired,
    CredentialLevel,
    UrgencyLevel,
)
from src.classifier import (
    classify_message_type,
    classify_message_type_full,
    classify_urgency,
    apply_confidence_gate,
    evaluate_completeness,
    make_hitl_item,
    CONFIDENCE_AUTO_ACCEPT,
    CONFIDENCE_FLAGGED_ACCEPT,
    IMPLICIT_URGENT_HOURS,
)


# =============================================================================
# Message type classification (D4a §6 Decision 1)
# =============================================================================

class TestMessageTypeClassification:
    def test_cancellation_with_prior_shift_id(self):
        text = "Hi, we need to cancel shift request #SN-2891 for Saturday night ICU."
        # Spec worked example: contains "cancel" + prior shift ID → CANCELLATION
        result = classify_message_type(text, prior_shift_id_present=True)
        assert result == MessageType.CANCELLATION

    def test_cancellation_without_prior_shift_id_is_unclassifiable(self):
        text = "Please cancel our Saturday night shift."
        result = classify_message_type(text, prior_shift_id_present=False)
        # "cancel" present but no prior shift ID → does not meet CANCELLATION rule
        assert result == MessageType.UNCLASSIFIABLE

    def test_modification_with_prior_shift_id(self):
        text = "Please update shift #SN-1001 to start at 7pm instead of 7am."
        result = classify_message_type(text, prior_shift_id_present=True)
        assert result == MessageType.MODIFICATION

    def test_multi_shift_block_keyword(self):
        text = "We need multiple shifts covered this weekend — Friday, Saturday, Sunday nights."
        result = classify_message_type(text)
        assert result == MessageType.MULTI_SHIFT_BLOCK

    def test_standard_shift_request_upgraded_by_caller(self):
        text = "We need an ICU nurse Thursday 7pm to 7am."
        result = classify_message_type_full(
            text,
            facility_resolved=True,
            datetime_parseable=True,
            prior_shift_id_present=False,
        )
        assert result == MessageType.STANDARD_SHIFT_REQUEST

    def test_unclassifiable_when_facility_not_resolved(self):
        text = "We need a nurse for Thursday night."
        result = classify_message_type_full(
            text,
            facility_resolved=False,
            datetime_parseable=True,
        )
        assert result == MessageType.UNCLASSIFIABLE

    def test_cancellation_keywords_case_insensitive(self):
        text = "CANCEL the ICU nurse for this Saturday #SN-5555"
        result = classify_message_type(text, prior_shift_id_present=True)
        assert result == MessageType.CANCELLATION


# =============================================================================
# Urgency classification (D4a §6 Decision 3)
# =============================================================================

class TestUrgencyClassification:
    _NOW = datetime(2026, 5, 13, 16, 10, 0, tzinfo=timezone.utc)

    def test_explicit_urgent_keyword_urgent(self):
        result = classify_urgency("We urgently need a tele nurse tonight", None, self._NOW)
        assert result == UrgencyLevel.EXPLICIT_URGENT

    def test_explicit_urgent_keyword_asap(self):
        result = classify_urgency("Need someone ASAP for the ER", None, self._NOW)
        assert result == UrgencyLevel.EXPLICIT_URGENT

    def test_explicit_urgent_keyword_today(self):
        result = classify_urgency("Looking for a CNA today", None, self._NOW)
        assert result == UrgencyLevel.EXPLICIT_URGENT

    def test_implicit_urgent_within_4_hours(self):
        # shift starts 3 hours from now
        shift_start = self._NOW + timedelta(hours=3)
        result = classify_urgency("We need an OR nurse", shift_start, self._NOW)
        assert result == UrgencyLevel.IMPLICIT_URGENT

    def test_implicit_urgent_boundary_exactly_4_hours(self):
        shift_start = self._NOW + timedelta(hours=IMPLICIT_URGENT_HOURS)
        result = classify_urgency("Need a nurse", shift_start, self._NOW)
        assert result == UrgencyLevel.IMPLICIT_URGENT  # ≤ 4 hours

    def test_standard_when_shift_more_than_4_hours_away(self):
        # Spec worked example: Thursday 7am submitted Tuesday 4:10pm → ~38hrs → STANDARD
        shift_start = self._NOW + timedelta(hours=38)
        result = classify_urgency(
            "We need a tele nurse for Thursday 7am",
            shift_start,
            self._NOW,
        )
        assert result == UrgencyLevel.STANDARD

    def test_standard_when_no_urgency_signal_and_no_datetime(self):
        result = classify_urgency("We need a nurse for next week", None, self._NOW)
        assert result == UrgencyLevel.STANDARD

    def test_explicit_beats_implicit(self):
        # If "urgent" keyword present, should be EXPLICIT even if datetime also within 4h
        shift_start = self._NOW + timedelta(hours=2)
        result = classify_urgency("This is urgent, please help", shift_start, self._NOW)
        assert result == UrgencyLevel.EXPLICIT_URGENT


# =============================================================================
# Confidence gate (D4a §6 Decision 2)
# =============================================================================

class TestConfidenceGate:
    def test_high_confidence_all_fields_accepted(self):
        scores = {f: 0.95 for f in [
            "facility_id", "unit_type", "specialty_required",
            "credential_level", "shift_datetime_start", "shift_datetime_end", "urgency"
        ]}
        extracted = {f: f"value_{f}" for f in scores}
        accepted, flags, missing = apply_confidence_gate(extracted, scores)
        assert flags == []
        assert missing == []
        assert len(accepted) == 7

    def test_low_confidence_field_becomes_unresolved(self):
        scores = {"specialty_required": 0.45}
        extracted = {"specialty_required": "ER or maybe trauma"}
        accepted, flags, missing = apply_confidence_gate(extracted, scores)
        # Spec worked example: 0.45 < 0.50 → UNRESOLVED, added to missing_fields
        assert accepted["specialty_required"] == SpecialtyRequired.UNRESOLVED
        assert "specialty_required" in missing
        assert "specialty_required" not in flags

    def test_mid_confidence_field_flagged_accept(self):
        scores = {"unit_type": 0.60}
        extracted = {"unit_type": "ICU"}
        accepted, flags, missing = apply_confidence_gate(extracted, scores)
        # 0.50 ≤ 0.60 < 0.70 → accept value but flag for coordinator
        assert accepted["unit_type"] == "ICU"
        assert "unit_type" in flags
        assert "unit_type" not in missing

    def test_boundary_at_auto_accept_threshold(self):
        scores = {"facility_id": CONFIDENCE_AUTO_ACCEPT}  # exactly 0.70
        extracted = {"facility_id": "FAC-0042"}
        accepted, flags, missing = apply_confidence_gate(extracted, scores)
        assert accepted["facility_id"] == "FAC-0042"
        assert "facility_id" not in flags
        assert "facility_id" not in missing

    def test_boundary_just_below_auto_accept(self):
        scores = {"facility_id": 0.699}
        extracted = {"facility_id": "FAC-0042"}
        accepted, flags, missing = apply_confidence_gate(extracted, scores)
        assert "facility_id" in flags  # flagged, not rejected

    def test_missing_score_treated_as_zero(self):
        # No score for a field → treated as 0.0 → UNRESOLVED
        accepted, flags, missing = apply_confidence_gate({}, {})
        assert "facility_id" in missing


# =============================================================================
# Brief completeness gate (D4a §6 Decision 4 / REQ-A-2)
# =============================================================================

class TestCompletenessGate:
    def _complete_brief(self) -> MatchingBrief:
        return MatchingBrief(
            source_message_id="msg-001",
            facility_id="FAC-0042",
            unit_type="ICU",
            specialty_required=SpecialtyRequired.RN_ICU,
            credential_level=CredentialLevel.RN,
            shift_datetime_start=datetime(2026, 5, 15, 19, 0, tzinfo=timezone.utc),
            shift_datetime_end=datetime(2026, 5, 16, 7, 0, tzinfo=timezone.utc),
            urgency=UrgencyLevel.STANDARD,
            message_type=MessageType.STANDARD_SHIFT_REQUEST,
        )

    def test_complete_brief_is_ready_for_review(self):
        # Spec worked example: all fields populated → READY_FOR_REVIEW
        brief = self._complete_brief()
        status, missing = evaluate_completeness(brief)
        assert status == BriefStatus.READY_FOR_REVIEW
        assert missing == []

    def test_unresolved_specialty_blocks_advance(self):
        brief = self._complete_brief()
        brief.specialty_required = SpecialtyRequired.UNRESOLVED
        status, missing = evaluate_completeness(brief)
        assert status == BriefStatus.NEEDS_COORDINATOR_INPUT
        assert "specialty_required" in missing

    def test_missing_facility_id_blocks_advance(self):
        brief = self._complete_brief()
        brief.facility_id = None
        status, missing = evaluate_completeness(brief)
        assert status == BriefStatus.NEEDS_COORDINATOR_INPUT
        assert "facility_id" in missing

    def test_multiple_missing_fields_all_reported(self):
        brief = MatchingBrief(source_message_id="msg-002")
        status, missing = evaluate_completeness(brief)
        assert status == BriefStatus.NEEDS_COORDINATOR_INPUT
        assert len(missing) >= 4


# =============================================================================
# State machine — invalid transitions (D4a §10)
# =============================================================================

class TestStateMachine:
    def test_cannot_advance_incomplete_brief_to_ws2(self):
        brief = MatchingBrief(source_message_id="msg-003")
        # brief has UNRESOLVED fields → should raise
        with pytest.raises(ValueError, match="NEEDS_COORDINATOR_INPUT"):
            brief.transition_to(BriefStatus.ADVANCED_TO_WS2)

    def test_cannot_return_from_advanced_to_ws2_to_ready(self):
        brief = MatchingBrief(
            source_message_id="msg-004",
            facility_id="FAC-0042",
            unit_type="ICU",
            specialty_required=SpecialtyRequired.RN_ICU,
            credential_level=CredentialLevel.RN,
            shift_datetime_start=datetime(2026, 5, 15, 19, 0, tzinfo=timezone.utc),
            shift_datetime_end=datetime(2026, 5, 16, 7, 0, tzinfo=timezone.utc),
            brief_status=BriefStatus.ADVANCED_TO_WS2,
        )
        with pytest.raises(ValueError, match="WS2 pipeline already initiated"):
            brief.transition_to(BriefStatus.READY_FOR_REVIEW)

    def test_cancelled_is_terminal(self):
        brief = MatchingBrief(
            source_message_id="msg-005",
            brief_status=BriefStatus.CANCELLED,
        )
        for target in (BriefStatus.READY_FOR_REVIEW, BriefStatus.NEEDS_COORDINATOR_INPUT):
            with pytest.raises(ValueError, match="terminal"):
                brief.transition_to(target)

    def test_valid_transition_needs_input_to_ready(self):
        brief = MatchingBrief(
            source_message_id="msg-006",
            facility_id="FAC-0042",
            unit_type="ICU",
            specialty_required=SpecialtyRequired.RN_ICU,
            credential_level=CredentialLevel.RN,
            shift_datetime_start=datetime(2026, 5, 15, 19, 0, tzinfo=timezone.utc),
            shift_datetime_end=datetime(2026, 5, 16, 7, 0, tzinfo=timezone.utc),
            brief_status=BriefStatus.NEEDS_COORDINATOR_INPUT,
        )
        brief.transition_to(BriefStatus.READY_FOR_REVIEW)
        assert brief.brief_status == BriefStatus.READY_FOR_REVIEW


# =============================================================================
# HITL queue item SLA (D4a §7)
# =============================================================================

class TestHITLQueueItem:
    _NOW = datetime(2026, 5, 13, 12, 0, 0, tzinfo=timezone.utc)

    def _brief(self) -> MatchingBrief:
        return MatchingBrief(source_message_id="msg-007")

    def test_hitl_item_sla_set_to_30_minutes_default(self):
        brief = self._brief()
        item = make_hitl_item(brief, HITLGapType.MISSING_REQUIRED_FIELD, now=self._NOW)
        expected_deadline = self._NOW + __import__("datetime").timedelta(minutes=30)
        assert item.sla_deadline == expected_deadline

    def test_implicit_urgent_hitl_uses_10_minute_sla(self):
        from src.classifier import IMPLICIT_URGENT_SLA_MINUTES
        brief = self._brief()
        item = make_hitl_item(
            brief,
            HITLGapType.IMPLICIT_URGENCY_CONFIRMATION,
            sla_minutes=IMPLICIT_URGENT_SLA_MINUTES,
            now=self._NOW,
        )
        expected_deadline = self._NOW + __import__("datetime").timedelta(minutes=10)
        assert item.sla_deadline == expected_deadline

    def test_is_expired_after_deadline(self):
        brief = self._brief()
        item = make_hitl_item(brief, HITLGapType.UNCLASSIFIABLE_MESSAGE, now=self._NOW)
        future = self._NOW + __import__("datetime").timedelta(minutes=31)
        assert item.is_expired(now=future) is True

    def test_not_expired_before_deadline(self):
        brief = self._brief()
        item = make_hitl_item(brief, HITLGapType.UNCLASSIFIABLE_MESSAGE, now=self._NOW)
        just_before = self._NOW + __import__("datetime").timedelta(minutes=29)
        assert item.is_expired(now=just_before) is False

    def test_cannot_resolve_from_open_directly(self):
        brief = self._brief()
        item = make_hitl_item(brief, HITLGapType.MISSING_REQUIRED_FIELD, now=self._NOW)
        with pytest.raises(ValueError, match="Must pass through IN_REVIEW"):
            item.transition_to(HITLStatus.RESOLVED)
