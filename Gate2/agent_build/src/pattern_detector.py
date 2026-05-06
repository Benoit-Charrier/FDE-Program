"""T-008: Repeat dispute pattern detection.

Checks whether a customer has ≥2 open disputes of the same type in
APEX_DISPUTES_OPEN. If so, the case must be escalated via ET-005 before
validity assessment proceeds.

Per D4 §8 Hard Stop 6: the agent must never close a case for a customer with
≥2 open disputes of the same type without triggering ET-005 and receiving
acknowledgement from the senior billing agent.

Per D4 §7 FM-6: this check (T-008) must execute BEFORE T-007 (validity
assessment) in all cases. If T-008 is skipped or fails silently, the case
must be blocked from proceeding to validity assessment.

Open status values derived from APEX_DISPUTES_OPEN artefact:
  PENDING_CLAIM — dispute received; awaiting Apex review
  AWAITING_CUST — awaiting customer response; dispute still open

RESOLVED is explicitly excluded — closed disputes do not count toward
the repeat pattern threshold.

Spec source: D4 §4 T-008; D4 §6 ET-005; D4 §8 Hard Stop 6; D4 §7 FM-6.
"""

from dataclasses import dataclass, field
from typing import Sequence


OPEN_STATUSES: frozenset[str] = frozenset({"PENDING_CLAIM", "AWAITING_CUST"})


@dataclass
class DisputeRecord:
    dispute_id: str
    customer_id: str
    dispute_type: str
    status: str


@dataclass
class PatternDetectionResult:
    has_repeat_pattern: bool
    matching_disputes: list[DisputeRecord] = field(default_factory=list)
    repeat_count: int = 0


def detect_repeat_pattern(
    customer_id: str,
    dispute_type: str,
    all_open_disputes: Sequence[DisputeRecord],
) -> PatternDetectionResult:
    """Return whether the customer has ≥2 open disputes of the given type.

    Counts only disputes with a status in OPEN_STATUSES. RESOLVED disputes
    are excluded (they do not indicate an unresolved systemic pattern).

    If has_repeat_pattern is True, ET-005 must be triggered before T-007.
    The matching_disputes list provides the escalation context package.
    """
    matching = [
        d for d in all_open_disputes
        if d.customer_id == customer_id
        and d.dispute_type == dispute_type
        and d.status in OPEN_STATUSES
    ]

    return PatternDetectionResult(
        has_repeat_pattern=len(matching) >= 2,
        matching_disputes=matching,
        repeat_count=len(matching),
    )
