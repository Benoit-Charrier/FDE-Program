"""Confidence threshold routing — HITL vs. autonomous path.

Routes a validity assessment to the autonomous path or HITL escalation based
on the agent's confidence score for a given case.

The 0.85 default threshold is sourced directly from D4 §3 KPI (confidence
threshold validation methodology). This value must not be changed in code
without an explicit COO-approved policy update logged in the policy version
control register.

Post-deployment recalibration (D4 §3): if rolling 7-day precision drops below
90%, the threshold is raised to 0.90 and held until two consecutive weeks of
≥90% precision are achieved. The current_threshold parameter accepts the live
threshold value from the policy register — callers must not hardcode 0.85 in
production; they must retrieve the current threshold from the register.

Spec source: D4 §3 KPI; D4 §5 Autonomy matrix (≥0.85 → autonomous; <0.85 → HITL).
"""

from dataclasses import dataclass
from enum import Enum


# Pre-deployment default. Must be validated against the 150-case calibration set
# before deployment. If calibration shows precision < 90% at 0.85, raise this value.
# Assumption (D4 A — pre-deployment calibration assumption): 0.85 achieves ≥90%
# precision on domain-specific historical data.
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.85


class RoutingDecision(str, Enum):
    AUTONOMOUS = "AUTONOMOUS"   # agent proceeds without human review
    HITL = "HITL"               # escalate to human reviewer per ET-001


@dataclass
class RoutingResult:
    decision: RoutingDecision
    confidence_score: float
    threshold_applied: float
    rationale: str


def route_by_confidence(
    confidence_score: float,
    current_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> RoutingResult:
    """Return the routing decision for a given confidence score.

    confidence_score must be in [0.0, 1.0]; raises ValueError otherwise.
    current_threshold should be retrieved from the live policy register in
    production — it may differ from DEFAULT_CONFIDENCE_THRESHOLD after a
    recalibration event.

    Boundary: confidence_score == current_threshold routes to AUTONOMOUS
    (≥ threshold is the autonomous condition per D4 §3).
    """
    if not 0.0 <= confidence_score <= 1.0:
        raise ValueError(
            f"confidence_score must be in [0.0, 1.0], got {confidence_score!r}"
        )

    if confidence_score >= current_threshold:
        return RoutingResult(
            decision=RoutingDecision.AUTONOMOUS,
            confidence_score=confidence_score,
            threshold_applied=current_threshold,
            rationale=(
                f"Confidence {confidence_score:.3f} ≥ threshold {current_threshold:.3f} "
                "— autonomous path."
            ),
        )

    return RoutingResult(
        decision=RoutingDecision.HITL,
        confidence_score=confidence_score,
        threshold_applied=current_threshold,
        rationale=(
            f"Confidence {confidence_score:.3f} < threshold {current_threshold:.3f} "
            "— escalate to human reviewer per ET-001."
        ),
    )
