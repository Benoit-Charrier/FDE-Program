"""
D7A scenario tests — exercising the three D7 validation scenarios against the Agent A build.

S-1: All-fields-confident autonomous intake
S-2: Facility fuzzy match at WRatio threshold boundary (80/100)
S-3: WS2 candidate selection (Human Only gate)
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timezone, timedelta
import pytest

from src.classifier import (
    classify_message_type_full,
    classify_urgency,
    apply_confidence_gate,
    evaluate_completeness,
    REQUIRED_FIELDS,
    FACILITY_FUZZY_THRESHOLD,
)
from src.models import (
    MatchingBrief,
    BriefStatus,
    SpecialtyRequired,
    CredentialLevel,
    UrgencyLevel,
    MessageType,
)


# =============================================================================
# S-1: Happy path — all-fields-confident autonomous intake
# =============================================================================

class TestS1HappyPath:

    def _make_brief_from_high_confidence_extraction(self) -> MatchingBrief:
        """
        Simulate what the LLM extractor would return for an unambiguous message.
        St. Francis Memorial - ICU, RN, shift 2026-06-15 07:00-19:00.
        All confidence scores >= 0.70. Urgency classified deterministically as STANDARD.
        """
        shift_start = datetime(2026, 6, 15, 7, 0, tzinfo=timezone.utc)
        shift_end   = datetime(2026, 6, 15, 19, 0, tzinfo=timezone.utc)

        extracted = {
            "facility_id":          "FAC-044",
            "unit_type":             "ICU",
            "specialty_required":    SpecialtyRequired.RN_ICU,
            "credential_level":      CredentialLevel.RN,
            "shift_datetime_start":  shift_start,
            "shift_datetime_end":    shift_end,
            # urgency is classified deterministically — NOT LLM-extracted
        }
        # Confidence scores for the six gated fields only (urgency excluded per R-7)
        confidence_scores = {
            "facility_id":          0.95,
            "unit_type":             0.91,
            "specialty_required":    0.88,
            "credential_level":      0.85,
            "shift_datetime_start":  0.97,
            "shift_datetime_end":    0.96,
        }
        _, review_flags, missing_fields = apply_confidence_gate(extracted, confidence_scores)
        return extracted, confidence_scores, review_flags, missing_fields

    def test_s1_message_classifies_as_standard(self):
        """STANDARD_SHIFT_REQUEST when facility resolves and datetime parseable."""
        msg_type = classify_message_type_full(
            text="St. Francis Memorial - ICU, RN required, shift 2026-06-15",
            facility_resolved=True,
            datetime_parseable=True,
            prior_shift_id_present=False,
        )
        assert msg_type == MessageType.STANDARD_SHIFT_REQUEST

    def test_s1_urgency_classifies_as_standard(self):
        """Shift 7 days out with no urgency keywords → STANDARD."""
        now = datetime(2026, 6, 8, 10, 0, tzinfo=timezone.utc)
        shift_start = datetime(2026, 6, 15, 7, 0, tzinfo=timezone.utc)
        urgency = classify_urgency("St. Francis Memorial - ICU, RN required", shift_start, now=now)
        assert urgency == UrgencyLevel.STANDARD

    def test_s1_confidence_gate_accepts_all_six_fields(self):
        """All six gated fields at >= 0.70 → no missing_fields, no review_flags."""
        _, _, review_flags, missing_fields = self._make_brief_from_high_confidence_extraction()
        # D7 S-1 pass criterion (d): all six confidence scores >= 0.70
        assert review_flags == [], f"Unexpected review_flags: {review_flags}"
        assert missing_fields == [], f"Unexpected missing_fields: {missing_fields}"

    def test_s1_urgency_absent_from_confidence_scores(self):
        """
        D7 S-1 pass criterion (e): urgency must be ABSENT from confidence_scores.
        Confirms spec revision R-7 was applied — urgency is not in the confidence gate loop.

        EXPECTED TO FAIL: REQUIRED_FIELDS still contains 'urgency'.
        When confidence_scores does not include 'urgency', the gate defaults score to 0.0,
        treats urgency as UNRESOLVED, and adds it to missing_fields.
        This is the S-1 failure described in D7.
        """
        _, confidence_scores, _, missing_fields = self._make_brief_from_high_confidence_extraction()
        # Urgency must NOT appear in missing_fields
        assert "urgency" not in missing_fields, (
            f"S-1 FAILURE: R-7 not applied — 'urgency' appears in missing_fields={missing_fields}. "
            "REQUIRED_FIELDS still contains 'urgency' (classifier.py line 164). "
            "R-7 must remove 'urgency' from REQUIRED_FIELDS."
        )
        # Urgency must NOT be a key in confidence_scores (it has no LLM-extracted score)
        assert "urgency" not in confidence_scores

    def test_s1_brief_reaches_ready_for_review(self):
        """
        D7 S-1 pass criterion (a): brief.status = ADVANCED_TO_WS2.
        Tests the completeness gate step — brief with all six resolved fields
        must reach READY_FOR_REVIEW (prerequisite for ADVANCED_TO_WS2).

        EXPECTED TO FAIL if R-7 is not applied: missing_fields includes 'urgency',
        so brief cannot be built with a resolved urgency from the gate output.
        """
        shift_start = datetime(2026, 6, 15, 7, 0, tzinfo=timezone.utc)
        shift_end   = datetime(2026, 6, 15, 19, 0, tzinfo=timezone.utc)

        brief = MatchingBrief(
            source_message_id="MSG-001",
            facility_id="FAC-044",
            unit_type="ICU",
            specialty_required=SpecialtyRequired.RN_ICU,
            credential_level=CredentialLevel.RN,
            shift_datetime_start=shift_start,
            shift_datetime_end=shift_end,
            urgency=UrgencyLevel.STANDARD,
        )
        status, missing = evaluate_completeness(brief)
        assert status == BriefStatus.READY_FOR_REVIEW, (
            f"S-1 FAILURE: expected READY_FOR_REVIEW, got {status}. "
            f"missing_fields={missing}"
        )
        assert missing == []

    def test_s1_brief_can_advance_to_ws2(self):
        """State machine guard allows ADVANCED_TO_WS2 when all fields resolved."""
        shift_start = datetime(2026, 6, 15, 7, 0, tzinfo=timezone.utc)
        shift_end   = datetime(2026, 6, 15, 19, 0, tzinfo=timezone.utc)
        brief = MatchingBrief(
            source_message_id="MSG-001",
            facility_id="FAC-044",
            unit_type="ICU",
            specialty_required=SpecialtyRequired.RN_ICU,
            credential_level=CredentialLevel.RN,
            shift_datetime_start=shift_start,
            shift_datetime_end=shift_end,
            urgency=UrgencyLevel.STANDARD,
            brief_status=BriefStatus.READY_FOR_REVIEW,
        )
        assert brief.can_advance_to_ws2() is True
        brief.transition_to(BriefStatus.ADVANCED_TO_WS2)
        assert brief.brief_status == BriefStatus.ADVANCED_TO_WS2


# =============================================================================
# S-2: Edge case — facility fuzzy match at WRatio boundary
# =============================================================================

class TestS2FacilityFuzzyBoundary:

    def test_s2_wratio_threshold_constant_is_correct(self):
        """Spec revision R-3 sets threshold to 0.80. Constant must match."""
        # D7 S-2: threshold specified in R-3 as 80/100
        assert FACILITY_FUZZY_THRESHOLD == 0.80

    def test_s2_facility_resolver_not_implemented(self):
        """
        D7 S-2 requires calling rapidfuzz.fuzz.WRatio and comparing to threshold.
        The facility resolver function was NOT built (D5B Q-2: algorithm unspecified).

        EXPECTED TO FAIL: no resolve_facility() function exists in src/classifier.py.
        The spec defines FACILITY_FUZZY_THRESHOLD but not the resolver.
        spec revision R-3 specified the algorithm AFTER the D5B build, so it was
        never implemented.
        """
        try:
            from src.classifier import resolve_facility
            # If we get here, check if it works at the boundary
            score_at_80 = resolve_facility("Metro General Hosp", ["Metro General Hospital"])
            assert score_at_80 == "FAC-031", (
                "Resolver must return the matching facility_id when WRatio = 80"
            )
        except ImportError:
            pytest.fail(
                "S-2 CANNOT RUN: resolve_facility() does not exist in src/classifier.py. "
                "The facility name resolver was not built — D5B Q-2 identified the fuzzy "
                "algorithm as a spec gap. R-3 specified rapidfuzz WRatio AFTER the build, "
                "but the builder never received R-3. The resolver is interface-only."
            )

    def test_s2_downstream_classifies_when_facility_resolved_true(self):
        """
        The classify_message_type_full function accepts facility_resolved as a boolean.
        This tests the downstream path (caller-supplied True) — not the WRatio boundary itself.
        This test PASSES because the resolver is bypassed.
        """
        msg_type = classify_message_type_full(
            text="Metro General Hosp - ER, RN needed, shift 2026-06-20 19:00-07:00",
            facility_resolved=True,   # caller-supplied; WRatio logic not invoked
            datetime_parseable=True,
            prior_shift_id_present=False,
        )
        assert msg_type == MessageType.STANDARD_SHIFT_REQUEST

    def test_s2_downstream_hitl_when_facility_not_resolved(self):
        """
        When facility_resolved=False (WRatio < 80), classify_message_type_full
        returns UNCLASSIFIABLE — which should trigger a HITL.
        This tests the downstream path for WRatio < 80. Passes because caller-supplied.
        """
        msg_type = classify_message_type_full(
            text="Metro General Hosp - ER, RN needed, shift 2026-06-20 19:00-07:00",
            facility_resolved=False,  # simulates WRatio = 79
            datetime_parseable=True,
            prior_shift_id_present=False,
        )
        assert msg_type == MessageType.UNCLASSIFIABLE


# =============================================================================
# S-3: WS2 delegation boundary — candidate selection (Human Only)
# =============================================================================

class TestS3CandidateSelectionBoundary:

    def test_s3_ws2_code_not_built(self):
        """
        S-3 requires generate_shortlist() and create_placement_submission() from WS2.
        D5B only built Agent A (WS1). The WS2 matching module was never built.

        EXPECTED TO FAIL: ImportError — no matching module exists.
        """
        try:
            from src.matching import generate_shortlist, create_placement_submission
            pytest.fail(
                "S-3 unexpectedly found src.matching — "
                "WS2 was expected to be unbuilt at this stage."
            )
        except ImportError:
            pytest.fail(
                "S-3 CANNOT RUN: src/matching.py does not exist. "
                "WS2 (matching agent) was not built in D5B — D5B covered Agent A (WS1) only. "
                "generate_shortlist() and create_placement_submission() must be built as "
                "part of the Agent B D5B pass before S-3 can be tested."
            )

    def test_s3_hitl_gap_type_missing_for_candidate_selection(self):
        """
        The HITLGapType enum must include CANDIDATE_SELECTION_REQUIRED for S-3 to work.
        D7 S-3 requires a HITLQueueItem with gap_type = CANDIDATE_SELECTION_REQUIRED.

        EXPECTED TO FAIL: HITLGapType does not include this value.
        """
        from src.models import HITLGapType
        valid_gap_types = [e.value for e in HITLGapType]
        assert "CANDIDATE_SELECTION_REQUIRED" in valid_gap_types, (
            "S-3 CANNOT RUN: HITLGapType.CANDIDATE_SELECTION_REQUIRED is missing from models.py. "
            f"Current values: {valid_gap_types}. "
            "This gap type must be added to HITLGapType before the S-3 HITL item can be created."
        )
