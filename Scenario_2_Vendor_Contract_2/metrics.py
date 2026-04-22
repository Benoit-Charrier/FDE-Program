from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import audit
import approval


@dataclass
class MetricsSummary:
    total_contracts: int = 0
    route_distribution: dict = field(default_factory=dict)
    escalation_rate: Optional[float] = None
    mean_turnaround_by_queue: dict = field(default_factory=dict)
    override_rate: Optional[float] = None
    approval_latency_seconds: Optional[float] = None


def compute() -> MetricsSummary:
    events = audit.query_all()
    approvals = approval.get_all_approvals()

    # Group events by contract
    by_contract: dict[str, list[dict]] = {}
    for ev in events:
        cid = ev.get("contract_id", "")
        by_contract.setdefault(cid, []).append(ev)

    # Only count contracts that reached routing
    routed = {
        cid: evs for cid, evs in by_contract.items()
        if any(e["event_type"] == "routing" for e in evs)
    }

    total = len(routed)
    if total == 0:
        return MetricsSummary(total_contracts=0)

    # Route distribution
    queue_counts: dict[str, int] = {}
    turnaround_by_queue: dict[str, list[float]] = {}

    for cid, evs in routed.items():
        routing_ev = next((e for e in evs if e["event_type"] == "routing"), None)
        if not routing_ev:
            continue
        queue = routing_ev["payload"].get("queue", "unknown")
        queue_counts[queue] = queue_counts.get(queue, 0) + 1

        ingestion_ev = next((e for e in evs if e["event_type"] == "ingestion"), None)
        if ingestion_ev:
            try:
                t_start = datetime.fromisoformat(ingestion_ev["timestamp"])
                t_end = datetime.fromisoformat(routing_ev["timestamp"])
                elapsed = (t_end - t_start).total_seconds()
                turnaround_by_queue.setdefault(queue, []).append(elapsed)
            except Exception:
                pass

    route_distribution = {
        q: {"count": c, "pct": round(c / total * 100, 1)}
        for q, c in queue_counts.items()
    }

    mean_turnaround = {
        q: round(sum(ts) / len(ts), 2)
        for q, ts in turnaround_by_queue.items()
        if ts
    }

    escalation_count = queue_counts.get("senior_lawyer_escalation", 0)
    escalation_rate = round(escalation_count / total * 100, 1) if total else None

    # Override rate
    override_events = [e for e in events if e["event_type"] == "override"]
    override_rate = round(len(override_events) / total * 100, 1) if total else None

    # Approval latency
    latencies: list[float] = []
    for cid, evs in by_contract.items():
        redline_evs = [e for e in evs if e["event_type"] == "redline_generated"]
        approval_evs = [e for e in evs if e["event_type"] == "approval_recorded"]
        if redline_evs and approval_evs:
            try:
                t_redline = datetime.fromisoformat(redline_evs[0]["timestamp"])
                t_approval = datetime.fromisoformat(approval_evs[-1]["timestamp"])
                latencies.append((t_approval - t_redline).total_seconds())
            except Exception:
                pass

    approval_latency = round(sum(latencies) / len(latencies), 2) if latencies else None

    return MetricsSummary(
        total_contracts=total,
        route_distribution=route_distribution,
        escalation_rate=escalation_rate,
        mean_turnaround_by_queue=mean_turnaround,
        override_rate=override_rate,
        approval_latency_seconds=approval_latency,
    )
