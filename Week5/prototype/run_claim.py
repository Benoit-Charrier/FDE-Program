"""
Usage:
  # Named fixture from fixtures/:
  python run_claim.py --fixture CLAIM-ADMIN-01

  # Any pre-normalized JSON file (e.g. from normalized-tier1/):
  python run_claim.py --file normalized-tier1/CLM-2026-1000001.json

Loads a NormalizedClaimInput JSON, runs it through the WS1 pipeline,
and prints the result as formatted JSON.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from agents.ws1_agent import process_claim


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a claim through the WS1 pipeline.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixture", help="Fixture ID from fixtures/ (e.g. CLAIM-ADMIN-01)")
    group.add_argument("--file", help="Path to any NormalizedClaimInput JSON file")
    args = parser.parse_args()

    if args.fixture:
        claim_path = os.path.join(os.path.dirname(__file__), "fixtures", f"{args.fixture}.json")
    else:
        claim_path = args.file

    if not os.path.exists(claim_path):
        print(f"Error: file not found: {claim_path}", file=sys.stderr)
        sys.exit(1)

    with open(claim_path, encoding="utf-8") as f:
        claim = json.load(f)

    result = process_claim(claim)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
