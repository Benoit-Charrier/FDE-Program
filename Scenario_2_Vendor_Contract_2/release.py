#!/usr/bin/env python3
import argparse
import sys

from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Attempt outbound release of a negotiated contract package.")
    parser.add_argument("--contract", required=True, help="Contract filename (e.g. sample_negotiable.docx)")
    args = parser.parse_args()

    import approval
    import audit

    contract_id = args.contract
    status, unapproved = approval.check_release(contract_id)

    if status == "cleared":
        approval.set_release_status(contract_id, "cleared")
        audit.log_event(contract_id, "release_cleared", {"triggered_by": "release.py"})
        print(f"[CLEARED] {contract_id} — approved for release.")
    else:
        audit.log_event(contract_id, "release_blocked", {
            "triggered_by": "release.py",
            "unapproved_clauses": unapproved,
        })
        print(f"[BLOCKED] {contract_id} — missing approvals for: {', '.join(unapproved)}")
        print("Use approve.py to record named-lawyer sign-off for each clause before releasing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
