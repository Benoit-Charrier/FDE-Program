import pytest
from agent_build.src.confidence_router import (
    route_by_confidence,
    RoutingDecision,
    DEFAULT_CONFIDENCE_THRESHOLD,
)


def test_default_threshold_is_spec_value():
    """D4 §3 specifies 0.85 — any change requires COO sign-off."""
    assert DEFAULT_CONFIDENCE_THRESHOLD == 0.85


def test_at_threshold_routes_autonomous():
    """Boundary: confidence == threshold → autonomous (≥ condition)."""
    result = route_by_confidence(0.85)
    assert result.decision == RoutingDecision.AUTONOMOUS


def test_above_threshold_autonomous():
    result = route_by_confidence(0.95)
    assert result.decision == RoutingDecision.AUTONOMOUS


def test_one_below_threshold_hitl():
    result = route_by_confidence(0.849)
    assert result.decision == RoutingDecision.HITL


def test_zero_confidence_hitl():
    result = route_by_confidence(0.0)
    assert result.decision == RoutingDecision.HITL


def test_full_confidence_autonomous():
    result = route_by_confidence(1.0)
    assert result.decision == RoutingDecision.AUTONOMOUS


def test_recalibrated_threshold_090_applied():
    """After a recalibration event, threshold is raised to 0.90 per D4 §3."""
    result_at_085 = route_by_confidence(0.85, current_threshold=0.90)
    assert result_at_085.decision == RoutingDecision.HITL

    result_at_090 = route_by_confidence(0.90, current_threshold=0.90)
    assert result_at_090.decision == RoutingDecision.AUTONOMOUS


def test_routing_result_carries_threshold_applied():
    result = route_by_confidence(0.92, current_threshold=0.90)
    assert result.threshold_applied == 0.90
    assert result.confidence_score == 0.92


def test_out_of_range_high_raises():
    with pytest.raises(ValueError, match=r"\[0\.0, 1\.0\]"):
        route_by_confidence(1.01)


def test_out_of_range_low_raises():
    with pytest.raises(ValueError):
        route_by_confidence(-0.01)


def test_rationale_present_autonomous():
    result = route_by_confidence(0.90)
    assert "autonomous" in result.rationale.lower()


def test_rationale_present_hitl():
    result = route_by_confidence(0.70)
    assert "ET-001" in result.rationale
