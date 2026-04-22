#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def check_api_key():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is not set. Add it to your .env file or environment.")
        sys.exit(1)


def load_playbook(config_path: str = "config/playbook.json") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def process_contract(file_path: str, playbook: dict) -> dict | None:
    import ingestion
    import extraction
    import classification
    import routing
    import redlines
    import approval

    contract_id = Path(file_path).name

    # FR-01: Ingest
    ingest_result = ingestion.ingest(file_path)
    if isinstance(ingest_result, ingestion.IngestionError):
        print(f"[ERR] {contract_id} -> {ingest_result.reason}")
        return {"error": True, "filename": contract_id, "reason": ingest_result.reason}

    # FR-02: Extract
    clauses = extraction.extract(ingest_result, contract_id)

    # FR-03: Classify
    classifications = classification.classify(clauses, playbook, contract_id)

    # FR-04: Route
    decision = routing.route(classifications, contract_id)

    # FR-05/06: Redlines (playbook_negotiable only)
    redline_proposals = []
    if decision.queue == routing.QUEUE_NEGOTIABLE:
        redline_proposals, classifications = redlines.generate_redlines(
            classifications, playbook, contract_id
        )
        # Re-route in case FR-06 reclassified any clause
        decision = routing.route(classifications, contract_id)

        # FR-07: Initialise approval packet
        redlined_families = [rl.family for rl in redline_proposals]
        if redlined_families:
            approval.initialise_approval_packet(contract_id, redlined_families)

    result = {
        "error": False,
        "contract_id": contract_id,
        "queue": decision.queue,
        "routing_reason": decision.routing_reason,
        "classifications": [
            {
                "family": c.family,
                "extracted_text": c.extracted_text,
                "source_page": c.source_page,
                "confidence": c.confidence,
                "found": c.found,
                "status": c.status,
                "reason_code": c.reason_code,
                "rationale": c.rationale,
            }
            for c in classifications
        ],
        "redlines": [
            {
                "family": rl.family,
                "original_text": rl.original_text,
                "proposed_text": rl.proposed_text,
                "playbook_citation": rl.playbook_citation,
            }
            for rl in redline_proposals
        ],
        "clause_rationale": decision.clause_rationale,
    }

    print(f"[OK] {contract_id} -> {decision.queue}")
    return result


def persist_results(all_results: list[dict]) -> None:
    from pathlib import Path
    Path("data").mkdir(exist_ok=True)
    with open("data/analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)


def main():
    check_api_key()

    parser = argparse.ArgumentParser(description="Vendor Contract Review Agent")
    parser.add_argument("--input", default="Input Contracts", help="Folder containing contracts")
    parser.add_argument("--output", default="Output/report.html", help="Path for HTML report")
    args = parser.parse_args()

    input_folder = Path(args.input)
    if not input_folder.exists():
        print(f"ERROR: Input folder '{input_folder}' does not exist.")
        sys.exit(1)

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    playbook = load_playbook()

    files = sorted(
        [f for f in input_folder.iterdir() if f.suffix.lower() in (".pdf", ".docx")]
    )

    if not files:
        print(f"No .pdf or .docx files found in '{input_folder}'.")
        sys.exit(0)

    print(f"Processing {len(files)} contract(s) from '{input_folder}'...\n")

    ok_results = []
    error_results = []

    for file_path in files:
        result = process_contract(str(file_path), playbook)
        if result and result.get("error"):
            error_results.append({"filename": result["filename"], "reason": result["reason"]})
        elif result:
            ok_results.append(result)

    persist_results(ok_results)

    import metrics as metrics_module
    import report

    m = metrics_module.compute()
    report.generate(ok_results, error_results, m, str(output_path))

    print(f"\nReport written to: {output_path}")
    print(f"Summary: {len(ok_results)} processed, {len(error_results)} errors.")


if __name__ == "__main__":
    main()
