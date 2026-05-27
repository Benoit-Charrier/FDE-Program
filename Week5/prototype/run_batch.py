"""
Batch runner: feed a Claims Pack format directory through the WS1 pipeline.

Usage:
  # Dry-run with heuristic classifier (no API calls, default):
  python run_batch.py --dir ../Capstone-A-Claims-Pack/portal-json
  python run_batch.py --dir ../Capstone-A-Claims-Pack/edi-837p --limit 50
  python run_batch.py --dir ../Capstone-A-Claims-Pack/edi-837i --limit 0  # all 200

  # Live run with Sonnet 4.6 classifier (requires ANTHROPIC_API_KEY, incurs cost):
  python run_batch.py --dir ../Capstone-A-Claims-Pack/portal-json --live --limit 20

Classifier modes:
  default (heuristic mock): CPT-range heuristic — no API calls, deterministic.
  --live: real Sonnet 4.6 call per claim. ~$0.004/claim; 400 portal-JSON ≈ $1.60.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))

from agents.ws1_agent import process_claim
from tools.intake.cms1500_ocr_parser import parse_cms1500_ocr
from tools.intake.edi_parser import parse_edi_837
from tools.intake.portal_json_adapter import adapt_portal_json


# ---------------------------------------------------------------------------
# Heuristic mock classifier — no API calls
# ---------------------------------------------------------------------------

def _mock_classifier(claim: dict) -> dict:
    """
    CPT-range heuristic for batch dry-runs.
    Distribution approximates real-world claims mix for demo purposes.
    """
    codes = claim.get("procedure_codes", [])
    first = codes[0] if codes else ""
    try:
        num = int(first)
        # Surgery (10000–69999) → clinical review required
        if 10000 <= num <= 69999:
            return {
                "classification": "clinical",
                "confidence": 0.88,
                "reasoning": (
                    f"Surgical procedure {first} — medical necessity determination "
                    f"required (heuristic)."
                ),
            }
        # Radiology / Pathology / Lab (70000–89999) → administrative
        if 70000 <= num <= 89999:
            return {
                "classification": "admin",
                "confidence": 0.86,
                "reasoning": (
                    f"Diagnostic/lab code {first} — routine administrative "
                    f"processing (heuristic)."
                ),
            }
        # E&M office visits (99200–99499) → administrative
        if 99200 <= num <= 99499:
            return {
                "classification": "admin",
                "confidence": 0.89,
                "reasoning": (
                    f"Office visit / E&M code {first} — routine administrative "
                    f"processing (heuristic)."
                ),
            }
    except ValueError:
        pass
    # Everything else (therapy codes 97XXX, medicine 90XXX, etc.) → uncertain
    return {
        "classification": "uncertain",
        "confidence": 0.51,
        "reasoning": (
            f"Procedure {first} is used in both administrative and clinical "
            f"workflows — signals insufficient for determination (heuristic)."
        ),
    }


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

_FORMAT_LABELS = {
    "edi_837p":    "EDI 837P (Professional)",
    "edi_837i":    "EDI 837I (Institutional)",
    "portal_json": "Portal JSON",
    "cms1500_ocr": "CMS-1500 OCR",
    "normalized":  "Pre-normalized (NormalizedClaimInput JSON cache)",
}


def _detect_format(dir_path: Path) -> str:
    name = dir_path.name.lower()
    if "normalized" in name:
        return "normalized"
    if "837p" in name:
        return "edi_837p"
    if "837i" in name:
        return "edi_837i"
    if "portal" in name or ("json" in name and "fhir" not in name):
        return "portal_json"
    if "cms1500" in name or "ocr" in name:
        return "cms1500_ocr"
    raise ValueError(
        f"Cannot detect format from directory name '{dir_path.name}'. "
        f"Expected: normalized-tier1, edi-837p, edi-837i, portal-json, or cms1500-ocr."
    )


def _load_and_normalise(filepath: Path, fmt: str) -> dict:
    if fmt == "normalized":
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    if fmt.startswith("edi"):
        raw = filepath.read_text(encoding="utf-8")
        return parse_edi_837(raw, source_file=filepath.name)
    if fmt == "cms1500_ocr":
        raw = filepath.read_text(encoding="utf-8")
        return parse_cms1500_ocr(raw, source_file=filepath.name)
    with open(filepath, encoding="utf-8") as f:
        raw = json.load(f)
    return adapt_portal_json(raw, source_file=filepath.name)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Claims Pack files through the WS1 pipeline."
    )
    parser.add_argument(
        "--dir", required=True,
        help="Path to a Claims Pack format directory (edi-837p, edi-837i, or portal-json).",
    )
    parser.add_argument(
        "--limit", type=int, default=20,
        help="Max claims to process. 0 = all files in the directory (default: 20).",
    )
    parser.add_argument(
        "--live", action="store_true",
        help=(
            "Use the real Sonnet 4.6 classifier (requires ANTHROPIC_API_KEY). "
            "Default: heuristic mock (no API calls)."
        ),
    )
    parser.add_argument(
        "--save-normalized", metavar="DIR",
        help=(
            "Save each successfully parsed claim as a NormalizedClaimInput JSON file to DIR. "
            "Directory is created if it does not exist. "
            "Use to cache parsed claims for WS1-only testing without re-parsing raw files."
        ),
    )
    args = parser.parse_args()

    dir_path = Path(args.dir).resolve()
    if not dir_path.is_dir():
        print(f"Error: '{args.dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    try:
        fmt = _detect_format(dir_path)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if fmt.startswith("edi"):
        ext = "*.edi"
    elif fmt == "cms1500_ocr":
        ext = "*.txt"
    else:
        ext = "*.json"  # covers both portal_json and normalized
    all_files = sorted(dir_path.glob(ext))
    limit = args.limit if args.limit > 0 else len(all_files)
    files = all_files[:limit]

    save_dir = Path(args.save_normalized).resolve() if args.save_normalized else None
    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)

    fmt_label = _FORMAT_LABELS.get(fmt, fmt)
    classifier_label = "Sonnet 4.6 (live)" if args.live else "heuristic mock (no API calls)"

    print(f"\nWS1 Batch Runner")
    print(f"  Directory : {dir_path.name}")
    print(f"  Format    : {fmt_label}")
    print(f"  Claims    : {len(files):,} of {len(all_files):,} available")
    print(f"  Classifier: {classifier_label}")
    if args.live:
        est_cost = len(files) * 0.004
        print(f"  Est. cost : ~${est_cost:.2f} USD")
    if save_dir:
        print(f"  Save dir  : {save_dir}")
    print()

    approved: list = []
    escalated: list = []
    errors: list = []
    saved_count: list = [0]

    def _run_one(fp: Path) -> None:
        try:
            claim = _load_and_normalise(fp, fmt)
        except Exception as exc:
            errors.append({"file": fp.name, "stage": "parse", "error": str(exc)})
            return
        if save_dir:
            out = save_dir / (fp.stem + ".json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump(claim, f, indent=2)
            saved_count[0] += 1
        try:
            result = process_claim(claim)
            if result.get("status") == "approved":
                approved.append(result)
            else:
                escalated.append(result)
        except Exception as exc:
            errors.append({"file": fp.name, "stage": "pipeline", "error": str(exc)})

    start = time.monotonic()

    if args.live:
        for i, fp in enumerate(files, 1):
            print(f"  [{i:4d}/{len(files)}] {fp.name}", end="\r", flush=True)
            _run_one(fp)
    else:
        with patch("agents.ws1_agent.classify_clinical_content",
                   side_effect=_mock_classifier):
            for i, fp in enumerate(files, 1):
                print(f"  [{i:4d}/{len(files)}] {fp.name}", end="\r", flush=True)
                _run_one(fp)

    elapsed = time.monotonic() - start
    total = len(approved) + len(escalated) + len(errors)

    print(" " * 72, end="\r")  # clear progress line

    def pct(n: int) -> str:
        return f"{100 * n / max(total, 1):.1f}%"

    print("-" * 52)
    print(f"  {'approved':<16} {len(approved):>5}  ({pct(len(approved))})")
    print(f"  {'escalated':<16} {len(escalated):>5}  ({pct(len(escalated))})")
    if errors:
        print(f"  {'parse/error':<16} {len(errors):>5}  ({pct(len(errors))})")
    print("-" * 52)
    print(f"  {'total':<16} {total:>5}  in {elapsed:.1f}s")
    if save_dir:
        print(f"  {'normalized saved':<16} {saved_count[0]:>5}  -> {save_dir}")
    print()

    # Escalation breakdown
    clinical_esc  = sum(1 for r in escalated if r.get("classification") == "clinical")
    uncertain_esc = sum(1 for r in escalated if r.get("classification") == "uncertain")
    other_esc     = len(escalated) - clinical_esc - uncertain_esc
    if escalated:
        print(f"  Escalation breakdown:")
        if clinical_esc:
            print(f"    clinical (physician HITL)  : {clinical_esc}")
        if uncertain_esc:
            print(f"    uncertain (physician HITL) : {uncertain_esc}")
        if other_esc:
            print(f"    other (elig/codes/etc)     : {other_esc}")
        print()

    if errors:
        print(f"  Parse/pipeline errors ({len(errors)}):")
        for e in errors[:5]:
            print(f"    {e['file']} [{e['stage']}]: {e['error']}")
        if len(errors) > 5:
            print(f"    ... and {len(errors) - 5} more")
        print()


if __name__ == "__main__":
    main()
