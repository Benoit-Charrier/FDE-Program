"""T-006: Aurum real-time invoice correction constraint check.

Confirms that real-time invoice line-item correction is not possible via Aurum.
This is a hardcoded constraint — no external data or API call is required.

This function exists so the constraint is explicit and testable in the workflow
rather than embedded as an undocumented assumption in calling code.

Spec source: D4 §4 T-006; scenario_context.md §6 (Aurum: "No real-time API.
Invoice modifications require a manual ticket to the Aurum support team,
typical turnaround 48 hours.").
"""


def aurum_realtime_correction_possible() -> bool:
    """Always returns False.

    Aurum Billing (on-prem Oracle, in production since 2008) has no real-time
    API. Any invoice line-item modification requires a manual ticket to the
    Aurum support team with a 48-hour typical turnaround.

    This constraint is universal — it applies to all invoices, all dispute types,
    and all agent-initiated actions. It cannot be overridden at runtime.
    """
    return False
