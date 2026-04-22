from __future__ import annotations
from dataclasses import dataclass
import audit
from classification import ClauseClassification, STATUS_ESCALATE, STATUS_DEVIATION

QUEUE_STANDARD = "standard"
QUEUE_NEGOTIABLE = "playbook_negotiable"
QUEUE_ESCALATION = "senior_lawyer_escalation"


@dataclass
class RoutingDecision:
    queue: str
    clause_rationale: list[dict]
    routing_reason: str


def route(classifications: list[ClauseClassification], contract_id: str) -> RoutingDecision:
    escalations = [c for c in classifications if c.status == STATUS_ESCALATE]
    deviations = [c for c in classifications if c.status == STATUS_DEVIATION]

    if escalations:
        triggers = ", ".join(c.family for c in escalations)
        reason = f"Escalation required: {triggers} triggered must-escalate conditions."
        queue = QUEUE_ESCALATION
    elif deviations:
        devs = ", ".join(c.family for c in deviations)
        reason = f"Playbook-negotiable deviations in: {devs}. All map to approved fallback language."
        queue = QUEUE_NEGOTIABLE
    else:
        reason = "All clause families match accepted playbook positions."
        queue = QUEUE_STANDARD

    clause_rationale = [
        {
            "family": c.family,
            "status": c.status,
            "reason_code": c.reason_code,
            "rationale": c.rationale,
        }
        for c in classifications
    ]

    decision = RoutingDecision(queue=queue, clause_rationale=clause_rationale, routing_reason=reason)

    audit.log_event(contract_id, "routing", {
        "queue": queue,
        "routing_reason": reason,
        "escalation_count": len(escalations),
        "deviation_count": len(deviations),
    })

    return decision
