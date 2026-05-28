"""
Interactive HITL reviewer — display escalation packet and record determination.

For ET-01/ET-02 (physician review): ADMIN_CONFIRMED re-enters WS1 at T-09
via the PHYSICIAN_REVIEWING -> ADMIN_CLEARED path (D4a §10, GAP-15).

Usage:
  python review_claim.py --claim-id CLM-2026-1001201
"""

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

_DIVIDER = "=" * 60
_THIN    = "-" * 60


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _load_escalation(claim_id: str) -> dict:
    path = os.path.join(os.path.dirname(__file__), "escalations", f"{claim_id}.json")
    if not os.path.exists(path):
        print(
            f"Error: no escalation record for '{claim_id}'.\n"
            f"Run the claim first: python run_claim.py --fixture {claim_id}",
            file=sys.stderr,
        )
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_escalation(claim_id: str, escalation: dict) -> None:
    path = os.path.join(os.path.dirname(__file__), "escalations", f"{claim_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(escalation, f, indent=2)


def _wrap(text: str, width: int = 66, indent: str = "    ") -> str:
    words = text.split()
    lines, line = [], []
    for w in words:
        if sum(len(x) + 1 for x in line) + len(w) > width:
            lines.append(indent + " ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        lines.append(indent + " ".join(line))
    return "\n".join(lines)


def _prompt_choice(options: list) -> int:
    print()
    for i, (label, desc) in enumerate(options, 1):
        print(f"  {i}. {label}")
        print(f"     {desc}")
    print()
    while True:
        raw = input(f"  Choice (1-{len(options)}): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw)
        print(f"  Enter a number between 1 and {len(options)}.")


# ---------------------------------------------------------------------------
# Packet display — one renderer per escalation type
# ---------------------------------------------------------------------------

def _display_physician_packet(e: dict) -> None:
    ctx    = e.get("claim_context", {})
    trigger = e.get("escalation_trigger_id", "?")
    print(f"\n  Claim         : {e['claim_id']}")
    print(f"  Trigger       : {trigger} -- {e.get('trigger_type', '?')}")
    print(f"  Procedure     : {ctx.get('procedure_code', '?')}")
    print(f"  Diagnosis     : {ctx.get('diagnosis_code', '?')}")
    print(f"  Provider      : {ctx.get('provider_specialty', '?')}")
    print(f"  Classification: {e.get('classification', '?')}  |  "
          f"Confidence: {e.get('confidence', '?')}")
    if e.get("borderline_confidence_flag"):
        print(f"  Threshold     : {e.get('threshold_applied', '?')}  (borderline)")
    print(f"\n  Escalation reason:")
    print(_wrap(e.get("escalation_reason", "No reason recorded.")))
    print(f"\n  Agent pre-work completed (all steps COMMITTED):")
    for step in e.get("audit_trail", []):
        print(f"    [+] {step}")


def _display_eligibility_packet(e: dict) -> None:
    ctx     = e.get("claim_context", {})
    signals = e.get("trigger_signal_values", {})
    print(f"\n  Claim     : {e['claim_id']}")
    print(f"  Trigger   : ET-03 -- ELIGIBILITY_DISCREPANCY")
    print(f"  Member ID : {signals.get('member_id', '?')}")
    print(f"  Payer ID  : {signals.get('payer_id', '?')}")
    print(f"  Status    : {signals.get('eligibility_status', '?')}")
    print(f"  Procedure : {ctx.get('procedure_code', '?')}")
    print(f"\n  Escalation reason:")
    print(_wrap(e.get("escalation_reason", "?")))
    print(f"\n  Agent pre-work completed:")
    for step in e.get("audit_trail", []):
        print(f"    [+] {step}")


def _display_governance_packet(e: dict) -> None:
    signals = e.get("trigger_signal_values", {})
    print(f"\n  Claim          : {e['claim_id']}")
    print(f"  Trigger        : ET-07 -- {e.get('trigger_type', '?')}")
    print(f"  State at esc.  : {e.get('claim_state_at_escalation', '?')}")
    print(f"  Actual state   : {signals.get('actual_state', '?')}")
    print(f"  Expected state : {signals.get('expected_state', '?')}")
    print(f"\n  Agent steps before hard stop:")
    for step in e.get("audit_trail", []):
        print(f"    [+] {step}")


# ---------------------------------------------------------------------------
# Decision handlers — one per escalation type
# ---------------------------------------------------------------------------

def _handle_physician_review(escalation: dict, claim_id: str) -> None:
    options = [
        ("ADMIN_CONFIRMED",
         "Confirm as administrative -- re-enter WS1 T-09 and issue payment"),
        ("CLINICAL_CONFIRMED",
         "Confirm as clinical -- route for medical necessity determination (WS2)"),
        ("NEEDS_ADDITIONAL_INFO",
         "Request additional documentation from provider"),
    ]
    choice = _prompt_choice(options)
    decision = options[choice - 1][0]

    escalation["reviewer_decision"] = decision
    escalation["reviewed_at"] = datetime.now(timezone.utc).isoformat()

    if decision == "ADMIN_CONFIRMED":
        original_claim = escalation.get("original_claim")
        if not original_claim:
            print(
                "\n  Error: escalation record missing original_claim field.\n"
                "  Re-run the claim to regenerate the escalation record.",
                file=sys.stderr,
            )
            sys.exit(1)

        print(f"\n  Decision: ADMIN_CONFIRMED")
        print(f"  Transitioning: PENDING_PHYSICIAN_REVIEW -> ADMIN_CLEARED "
              f"(authorized_by: PHYSICIAN_DETERMINATION)")
        print(f"  Re-entering WS1 at T-09...\n")

        from agents.ws1_agent import process_physician_approved_claim
        result = process_physician_approved_claim(
            original_claim,
            physician_id="DR-REVIEWER-001",
            prior_audit_trail=escalation.get("audit_trail", []),
        )
        escalation["ws1_result"] = result
        _save_escalation(claim_id, escalation)

        print(_THIN)
        print(f"  OUTCOME: APPROVED")
        print(f"  payment_amount  : {result.get('payment_amount')}")
        print(f"  authorized_by   : {result.get('authorized_by')}")
        print(f"  calibration_id  : {result.get('calibration_record_id')}")
        print(f"\n  Full audit trail:")
        for step in result.get("audit_trail", []):
            print(f"    [+] {step}")
        print(_THIN)

    elif decision == "CLINICAL_CONFIRMED":
        escalation["claim_status"] = "pending_medical_necessity_review"
        _save_escalation(claim_id, escalation)
        print(f"\n  Decision recorded: CLINICAL_CONFIRMED")
        print(f"  Claim routed to medical necessity review queue.")
        print(f"  WS2 will assemble the full clinical packet for physician determination.")

    else:
        escalation["claim_status"] = "pending_additional_info"
        _save_escalation(claim_id, escalation)
        print(f"\n  Decision recorded: NEEDS_ADDITIONAL_INFO")
        print(f"  Additional information request will be drafted and sent to provider.")


def _handle_eligibility_review(escalation: dict, claim_id: str) -> None:
    options = [
        ("APPROVE_OVERRIDE",
         "Override eligibility discrepancy and proceed to adjudication"),
        ("REJECT",
         "Reject claim -- eligibility cannot be confirmed"),
        ("REQUEST_RESUBMISSION",
         "Return to provider for eligibility correction and resubmission"),
    ]
    choice = _prompt_choice(options)
    decision = options[choice - 1][0]

    escalation["reviewer_decision"] = decision
    escalation["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    escalation["claim_status"] = {
        "APPROVE_OVERRIDE":     "approved_eligibility_override",
        "REJECT":               "rejected",
        "REQUEST_RESUBMISSION": "returned_to_submitter",
    }[decision]
    _save_escalation(claim_id, escalation)
    print(f"\n  Decision recorded: {decision}")
    print(f"  Claim status: {escalation['claim_status']}")


def _handle_governance_review(escalation: dict, claim_id: str) -> None:
    options = [
        ("INVESTIGATE",
         "Route to compliance team for state machine investigation"),
        ("REJECT_CLAIM",
         "Reject the claim -- governance violation cannot be resolved"),
        ("ESCALATE_TO_COMPLIANCE",
         "Escalate to compliance officer for review and sign-off"),
    ]
    choice = _prompt_choice(options)
    decision = options[choice - 1][0]

    escalation["reviewer_decision"] = decision
    escalation["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    escalation["claim_status"] = decision.lower().replace("_", "-")
    _save_escalation(claim_id, escalation)
    print(f"\n  Decision recorded: {decision}")
    print(f"  Claim status: {escalation['claim_status']}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(
        description="Interactive HITL reviewer -- display escalation packet and record determination."
    )
    parser.add_argument("--claim-id", required=True, help="Claim ID to review")
    args = parser.parse_args()

    escalation = _load_escalation(args.claim_id)
    trigger = escalation.get("escalation_trigger_id", "")

    if trigger in ("ET-01", "ET-02"):
        print(f"\n{_DIVIDER}")
        print(f"  PHYSICIAN REVIEW PACKET -- {args.claim_id}")
        print(_DIVIDER)
        _display_physician_packet(escalation)
        print(f"\n  Your determination:")
        _handle_physician_review(escalation, args.claim_id)

    elif trigger == "ET-03":
        print(f"\n{_DIVIDER}")
        print(f"  ELIGIBILITY EXCEPTION -- {args.claim_id}")
        print(_DIVIDER)
        _display_eligibility_packet(escalation)
        print(f"\n  Your determination:")
        _handle_eligibility_review(escalation, args.claim_id)

    elif trigger == "ET-07":
        print(f"\n{_DIVIDER}")
        print(f"  GOVERNANCE EXCEPTION -- {args.claim_id}")
        print(_DIVIDER)
        _display_governance_packet(escalation)
        print(f"\n  Your determination:")
        _handle_governance_review(escalation, args.claim_id)

    else:
        print(f"Unknown escalation trigger '{trigger}' -- displaying raw record:")
        print(json.dumps(escalation, indent=2))

    print()


if __name__ == "__main__":
    main()
