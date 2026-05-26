"""
HITL reviewer CLI. Displays an escalated claim's reason and context,
then records the reviewer's decision.

Usage: python review_claim.py --claim-id <CLAIM_ID> --decision <DECISION>

Valid decisions: approve, reject, escalate-to-physician, return-to-submitter
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

_VALID_DECISIONS = {
    "approve",
    "reject",
    "escalate-to-physician",
    "return-to-submitter",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a reviewer decision on an escalated claim.")
    parser.add_argument("--claim-id", required=True)
    parser.add_argument("--decision", required=True, choices=sorted(_VALID_DECISIONS))
    args = parser.parse_args()

    escalation_path = os.path.join(
        os.path.dirname(__file__), "escalations", f"{args.claim_id}.json"
    )
    if not os.path.exists(escalation_path):
        print(
            f"Error: no escalation record found for claim '{args.claim_id}'.\n"
            f"Run 'python run_claim.py --fixture {args.claim_id}' first.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(escalation_path, encoding="utf-8") as f:
        escalation = json.load(f)

    print(f"\nClaim {escalation['claim_id']} — escalation record")
    print("-" * 60)
    print(f"Classification : {escalation.get('classification', 'n/a')}")
    print(f"Confidence     : {escalation.get('confidence', 'n/a')}")
    print(f"Reason         : {escalation['escalation_reason']}")
    print()
    print("Claim context:")
    for key, value in escalation.get("claim_context", {}).items():
        print(f"  {key}: {value}")
    print()
    print("Audit trail:")
    for step in escalation.get("audit_trail", []):
        print(f"  {step}")
    print("-" * 60)

    escalation["reviewer_decision"] = args.decision
    escalation["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    escalation["claim_status"] = _derive_claim_status(args.decision)

    with open(escalation_path, "w", encoding="utf-8") as f:
        json.dump(escalation, f, indent=2)

    print(
        f"\nClaim {args.claim_id} — reviewer decision recorded: {args.decision}\n"
        f"Escalation reason: {escalation['escalation_reason']}\n"
        f"Audit record written. Claim status: {escalation['claim_status']}."
    )


def _derive_claim_status(decision: str) -> str:
    return {
        "approve": "approved",
        "reject": "rejected",
        "escalate-to-physician": "pending-physician-review",
        "return-to-submitter": "returned-to-submitter",
    }[decision]


if __name__ == "__main__":
    main()
