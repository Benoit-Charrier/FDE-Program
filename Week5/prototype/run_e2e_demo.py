"""
End-to-end demo: raw claim file → Intake parser → WS1 adjudication.

Shows three stages:
  Stage 1 — Raw claim as received from provider/clearinghouse
  Stage 2 — Intake Agent normalizes to NormalizedClaimInput
  Stage 3 — WS1 adjudication result

Usage:
  # Portal JSON (no API key needed if classifier returns uncertain/clinical):
  python run_e2e_demo.py --file "../Capstone-A-Claims-Pack/portal-json/CLM-2026-1001201.json"

  # EDI 837P:
  python run_e2e_demo.py --file "../Capstone-A-Claims-Pack/edi-837p/CLM-2026-1000001.edi"

Format is auto-detected from file extension (.edi → EDI 837P/I, .json → Portal JSON).
API key required for Stage 3 live classifier. Use --skip-ws1 to show Stage 1 + 2 only.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from tools.intake.edi_parser import parse_edi_837
from tools.intake.portal_json_adapter import adapt_portal_json


_DIVIDER = "=" * 60


def _print_stage(n: int, title: str) -> None:
    print(f"\n{_DIVIDER}")
    print(f"  STAGE {n}: {title}")
    print(_DIVIDER)


def _summarise_raw_edi(raw: str) -> str:
    lines = [l for l in raw.splitlines() if l.strip()]
    preview = lines[:8]
    suffix = f"\n  ... ({len(lines)} segments total)" if len(lines) > 8 else ""
    return "\n".join(f"  {l}" for l in preview) + suffix


def main() -> None:
    parser = argparse.ArgumentParser(
        description="End-to-end demo: raw claim → Intake parse → WS1 adjudication."
    )
    parser.add_argument("--file", required=True, help="Path to raw claim file (.edi or .json)")
    parser.add_argument(
        "--skip-ws1", action="store_true",
        help="Stop after Stage 2 (no API key required)"
    )
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(args.file)[1].lower()
    source_file = os.path.basename(args.file)

    with open(args.file, encoding="utf-8") as f:
        raw = f.read()

    # ------------------------------------------------------------------
    # Stage 1 — Raw claim
    # ------------------------------------------------------------------
    _print_stage(1, "Raw claim received from provider / clearinghouse")
    print(f"\n  File   : {source_file}")
    if ext == ".edi":
        print(f"  Format : EDI X12 837 (electronic structured)")
        print(f"\n  Content (first 8 segments):\n")
        print(_summarise_raw_edi(raw))
    elif ext == ".json":
        print(f"  Format : Portal JSON (structured submission)")
        print(f"\n  Content:\n")
        try:
            parsed_raw = json.loads(raw)
            print("  " + json.dumps(parsed_raw, indent=2).replace("\n", "\n  "))
        except json.JSONDecodeError:
            print(f"  {raw[:500]}")
    else:
        print(f"  Format : unknown extension '{ext}' — attempting portal JSON parse")

    # ------------------------------------------------------------------
    # Stage 2 — Intake Agent normalizes
    # ------------------------------------------------------------------
    _print_stage(2, "Intake Agent normalizes to NormalizedClaimInput")

    try:
        if ext == ".edi":
            claim = parse_edi_837(raw, source_file=source_file)
        else:
            claim = adapt_portal_json(json.loads(raw), source_file=source_file)
    except Exception as exc:
        print(f"\n  PARSE_FAILED: {exc}", file=sys.stderr)
        sys.exit(1)

    if claim.get("status") == "PARSE_FAILED":
        print(f"\n  PARSE_FAILED — {claim.get('error', 'unknown error')}")
        print("  Claim would be routed to the PARSE_FAILED exception queue.")
        sys.exit(1)

    print(f"\n  Normalized claim record:\n")
    print("  " + json.dumps(claim, indent=2).replace("\n", "\n  "))

    if claim.get("intake_warnings"):
        print(f"\n  Intake warnings: {claim['intake_warnings']}")

    if args.skip_ws1:
        print(f"\n{_DIVIDER}")
        print("  (--skip-ws1: stopping after Stage 2)")
        print(_DIVIDER)
        return

    # ------------------------------------------------------------------
    # Stage 3 — WS1 adjudication
    # ------------------------------------------------------------------
    _print_stage(3, "WS1 Administrative Adjudication Agent")
    print("\n  Running pipeline: eligibility -> codes -> prior auth -> classifier -> payment...\n")

    from agents.ws1_agent import process_claim
    result = process_claim(claim)

    print("  Result:\n")
    print("  " + json.dumps(result, indent=2).replace("\n", "\n  "))

    status = result.get("status", "unknown")
    if status == "approved":
        print(f"\n  OUTCOME: APPROVED — payment_amount {result.get('payment_amount')}")
    elif status == "escalated":
        trigger = result.get("escalation_trigger_id", "?")
        queue = result.get("routing_queue", "?")
        print(f"\n  OUTCOME: ESCALATED -- {trigger} -> {queue}")
    print()


if __name__ == "__main__":
    main()
