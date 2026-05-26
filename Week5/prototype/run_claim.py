"""
Usage: python run_claim.py --fixture <FIXTURE_ID>

Loads the named fixture from fixtures/, runs it through the WS1 pipeline,
and prints the result as formatted JSON.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from agents.ws1_agent import process_claim


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a claim fixture through the WS1 pipeline.")
    parser.add_argument("--fixture", required=True, help="Fixture ID (e.g. CLAIM-ADMIN-01)")
    args = parser.parse_args()

    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", f"{args.fixture}.json")
    if not os.path.exists(fixture_path):
        print(f"Error: fixture '{args.fixture}' not found at {fixture_path}", file=sys.stderr)
        sys.exit(1)

    with open(fixture_path, encoding="utf-8") as f:
        claim = json.load(f)

    result = process_claim(claim)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
