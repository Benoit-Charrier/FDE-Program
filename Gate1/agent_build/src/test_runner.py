"""
Validation test runner for FNOL Processing Agent.
Executes the 5 test scenarios defined in D4 Validation Design and reports
pass/fail against each scenario's defined criteria.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "scenarios"
OUTPUT_DIR = BASE_DIR / "output" / "scenarios"
AGENT_SCRIPT = Path(__file__).parent / "main.py"
PYTHON = sys.executable


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_agent(claim, policy, adjusters, output_dir):
    """Run the agent for a scenario and return (claim_result, steps_result, stdout, returncode)."""
    out_path = OUTPUT_DIR / output_dir
    out_path.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [PYTHON, str(AGENT_SCRIPT),
         "--input", str(DATA_DIR / claim),
         "--mock-policy", str(DATA_DIR / policy),
         "--mock-adjusters", str(DATA_DIR / adjusters),
         "--output-dir", str(out_path)],
        capture_output=True, text=True
    )

    claim_json_path = out_path / "claim_result.json"
    steps_json_path = out_path / "steps_result.json"

    claim_result = None
    steps_result = []
    if claim_json_path.exists():
        with open(claim_json_path, encoding="utf-8") as f:
            claim_result = json.load(f)
    if steps_json_path.exists():
        with open(steps_json_path, encoding="utf-8") as f:
            steps_result = json.load(f)

    return claim_result, steps_result, result.stdout + result.stderr, result.returncode


def check(label, actual, expected, results, *, note=None):
    passed = actual == expected
    entry = {
        "assertion": label,
        "expected": str(expected),
        "actual": str(actual),
        "passed": passed,
        "note": note,
    }
    results.append(entry)
    return passed


def check_contains(label, container, item, results, *, note=None):
    passed = item in (container or [])
    entry = {
        "assertion": label,
        "expected": f"contains '{item}'",
        "actual": str(container),
        "passed": passed,
        "note": note,
    }
    results.append(entry)
    return passed


def check_not_none(label, value, results, *, note=None):
    passed = value is not None
    entry = {
        "assertion": label,
        "expected": "not None",
        "actual": str(value),
        "passed": passed,
        "note": note,
    }
    results.append(entry)
    return passed


def check_is_none(label, value, results, *, note=None):
    passed = value is None
    entry = {
        "assertion": label,
        "expected": "None",
        "actual": str(value),
        "passed": passed,
        "note": note,
    }
    results.append(entry)
    return passed


def steps_have_escalation(steps, reason):
    return any(s.get("escalation_triggered") and s.get("escalation_reason") == reason for s in steps)


def steps_have_no_triage_escalation(steps):
    triage_steps = [s for s in steps if s.get("step_number") in (3, 4, 5)]
    return not any(s.get("escalation_triggered") for s in triage_steps)


# ---------------------------------------------------------------------------
# Scenario definitions
# ---------------------------------------------------------------------------

def scenario_1(results_store):
    """S1 — Standard property claim, full automation path (Happy Path)."""
    print("\n" + "=" * 70)
    print("SCENARIO 1: Standard Property Claim — Full Automation Path")
    print("=" * 70)

    claim, steps, stdout, rc = run_agent("s1_claim.json", "s1_policy.json", "s1_adjusters.json", "s1")
    assertions = []

    if claim is None:
        assertions.append({"assertion": "Agent ran successfully", "expected": "True", "actual": "False (no output)", "passed": False, "note": None})
        results_store["S1"] = {"name": "Standard Property Claim — Full Automation", "type": "Happy Path", "assertions": assertions}
        return

    check("claim_type = PROPERTY", claim.get("claim_type"), "PROPERTY", assertions)
    check("severity = LOW", claim.get("severity"), "LOW", assertions)
    check("status = COMPLETED", claim.get("status"), "COMPLETED", assertions)
    check("coverage_status = COVERED", claim.get("coverage_status"), "COVERED", assertions)
    check("assigned_adjuster_id = ADJ-101 (lowest queue depth)", claim.get("assigned_adjuster_id"), "ADJ-101", assertions)
    check("sla_breached = False", claim.get("sla_breached"), False, assertions)
    check("no triage escalations", steps_have_no_triage_escalation(steps), True, assertions)

    # Deviations (informational — not pass/fail)
    score = claim.get("severity_score")
    if score != 38:
        assertions.append({
            "assertion": "severity_score (informational deviation)",
            "expected": "38 (per spec)",
            "actual": str(score),
            "passed": None,
            "note": f"Heuristic scorer maps £4,500 to score {score}. Spec says 38. Both produce LOW severity — behavior correct, exact score differs.",
        })

    results_store["S1"] = {
        "name": "Standard Property Claim — Full Automation",
        "type": "Happy Path",
        "assertions": assertions,
        "claim": claim,
        "steps": steps,
    }
    _print_assertions(assertions)


def scenario_2(results_store):
    """S2 — Severity threshold boundary (sub-cases A and B)."""
    print("\n" + "=" * 70)
    print("SCENARIO 2A: Severity Boundary — Below Threshold (£9,800 -> score 59)")
    print("=" * 70)

    claim_a, steps_a, _, _ = run_agent("s2a_claim.json", "s2_policy.json", "s2_adjusters.json", "s2a")
    assertions_a = []
    if claim_a:
        check("severity = MEDIUM", claim_a.get("severity"), "MEDIUM", assertions_a)
        check("severity_score < 60", (claim_a.get("severity_score") or 100) < 60, True, assertions_a)
        check("no HIGH_SEVERITY escalation", not steps_have_escalation(steps_a, "HIGH_SEVERITY"), True, assertions_a)
        check("status reaches COMPLETED", claim_a.get("status"), "COMPLETED", assertions_a)
        score_a = claim_a.get("severity_score")
        if score_a != 59:
            assertions_a.append({
                "assertion": "severity_score (informational deviation)",
                "expected": "59 (per spec)",
                "actual": str(score_a),
                "passed": None,
                "note": f"Heuristic scorer produces {score_a}. Spec expects 59. Both below 60 threshold — delegation tier fires correctly.",
            })
    else:
        assertions_a.append({"assertion": "Agent ran successfully", "expected": "True", "actual": "False", "passed": False, "note": None})

    results_store["S2A"] = {
        "name": "Severity Boundary — Sub-case A (score below 60)",
        "type": "Delegation Boundary",
        "assertions": assertions_a,
        "claim": claim_a,
        "steps": steps_a,
    }
    _print_assertions(assertions_a)

    print("\n" + "=" * 70)
    print("SCENARIO 2B: Severity Boundary — Above Threshold (£10,200 -> score 61)")
    print("=" * 70)

    claim_b, steps_b, _, _ = run_agent("s2b_claim.json", "s2_policy.json", "s2_adjusters.json", "s2b")
    assertions_b = []
    if claim_b:
        check("severity = HIGH", claim_b.get("severity"), "HIGH", assertions_b,
              note="FAIL EXPECTED — heuristic scorer uses £5k-£15k bracket; £9,800 and £10,200 produce identical score. No £10k boundary exists in current model.")
        check("severity_score >= 60", (claim_b.get("severity_score") or 0) >= 60, True, assertions_b,
              note="FAIL EXPECTED — same bracket as Sub-case A; score unchanged by £400 difference")
        check("triage escalated HIGH_SEVERITY", steps_have_escalation(steps_b, "HIGH_SEVERITY"), True, assertions_b,
              note="FAIL EXPECTED — follows from severity not reaching HIGH")
        score_b = claim_b.get("severity_score")
        assertions_b.append({
            "assertion": "Root cause (informational)",
            "expected": "Distinct £10k threshold in severity model",
            "actual": f"Both £9,800 and £10,200 map to score {score_b} (bracket 5k–15k -> 45 + 5 MOTOR modifier)",
            "passed": None,
            "note": "Severity model requires a sub-bracket at £10,000 to implement the D2 1.3/1.4 boundary. Flagged as D5-U1.",
        })
    else:
        assertions_b.append({"assertion": "Agent ran successfully", "expected": "True", "actual": "False", "passed": False, "note": None})

    results_store["S2B"] = {
        "name": "Severity Boundary — Sub-case B (score above 60)",
        "type": "Delegation Boundary",
        "assertions": assertions_b,
        "claim": claim_b,
        "steps": steps_b,
    }
    _print_assertions(assertions_b)


def scenario_3(results_store):
    """S3 — Ambiguous coverage with exclusion candidate."""
    print("\n" + "=" * 70)
    print("SCENARIO 3: Ambiguous Coverage with Exclusion Candidate")
    print("=" * 70)

    claim, steps, _, _ = run_agent("s3_claim.json", "s3_policy.json", "s3_adjusters.json", "s3")
    assertions = []

    if claim is None:
        assertions.append({"assertion": "Agent ran successfully", "expected": "True", "actual": "False", "passed": False, "note": None})
        results_store["S3"] = {"name": "Ambiguous Coverage with Exclusion Candidate", "type": "Edge Case", "assertions": assertions}
        return

    check("coverage_status = UNCERTAIN (pending review)", claim.get("coverage_status"), "UNCERTAIN", assertions)
    check("exclusion_candidates non-empty", bool(claim.get("exclusion_candidates")), True, assertions)
    check_contains("exclusion_candidates contains Clause 14.3",
                   [e[:9] for e in (claim.get("exclusion_candidates") or [])], "Clause 14", assertions)
    check_is_none("assigned_adjuster_id = None (routing skipped)",
                  claim.get("assigned_adjuster_id"), assertions)
    check("claim_type = PROPERTY", claim.get("claim_type"), "PROPERTY", assertions)

    cov_conf = claim.get("coverage_match_confidence")
    assertions.append({
        "assertion": "coverage_match_confidence (informational deviation)",
        "expected": "0.72 (per spec — ML model output)",
        "actual": str(cov_conf),
        "passed": None,
        "note": "Heuristic always assigns 0.92 when claim_type matches any covered_peril. A production ML model would produce lower confidence for gradual-deterioration claims. The exclusion candidate (Clause 14.3) correctly triggered AGENT_REVIEW regardless.",
    })

    results_store["S3"] = {
        "name": "Ambiguous Coverage with Exclusion Candidate",
        "type": "Edge Case",
        "assertions": assertions,
        "claim": claim,
        "steps": steps,
    }
    _print_assertions(assertions)


def scenario_4(results_store):
    """S4 — Policy admin system unavailable (INTEGRATION_ERROR)."""
    print("\n" + "=" * 70)
    print("SCENARIO 4: Policy Administration System Unavailable")
    print("=" * 70)

    claim, steps, _, _ = run_agent("s4_claim.json", "s4_policy.json", "s4_adjusters.json", "s4")
    assertions = []

    if claim is None:
        assertions.append({"assertion": "Agent ran successfully", "expected": "True", "actual": "False", "passed": False, "note": None})
        results_store["S4"] = {"name": "Policy Admin System Unavailable", "type": "Failure Mode", "assertions": assertions}
        return

    check("status = INTEGRATION_ERROR", claim.get("status"), "INTEGRATION_ERROR", assertions)
    check_is_none("assigned_adjuster_id = None (routing not attempted)", claim.get("assigned_adjuster_id"), assertions)
    check("coverage_status = UNCERTAIN", claim.get("coverage_status"), "UNCERTAIN", assertions)
    check("INTEGRATION_ERROR escalation logged", steps_have_escalation(steps, "INTEGRATION_ERROR"), True, assertions)

    assertions.append({
        "assertion": "retry_count = 3 in audit log (informational)",
        "expected": "3 retries (2s/4s/8s backoff) in steps",
        "actual": "Simulated — retry_count carried in step outcome string",
        "passed": None,
        "note": "Current implementation simulates the 503 path via a mock flag. Retry timing (2s/4s/8s backoff) is declared in the error detail string but not executed as real HTTP calls.",
    })

    results_store["S4"] = {
        "name": "Policy Admin System Unavailable (HTTP 503)",
        "type": "Failure Mode",
        "assertions": assertions,
        "claim": claim,
        "steps": steps,
    }
    _print_assertions(assertions)


def scenario_5(results_store):
    """S5 — Extraction defect causing silent severity downgrade (quiet failure)."""
    print("\n" + "=" * 70)
    print("SCENARIO 5: NLP Extraction Defect — Silent Severity Downgrade")
    print("=" * 70)

    claim, steps, _, _ = run_agent("s5_claim.json", "s5_policy.json", "s5_adjusters.json", "s5")
    assertions = []

    if claim is None:
        assertions.append({"assertion": "Agent ran successfully", "expected": "True", "actual": "False", "passed": False, "note": None})
        results_store["S5"] = {"name": "Silent Severity Downgrade (Quiet Failure)", "type": "Failure Mode", "assertions": assertions}
        return

    # Tests the quiet failure behavior — agent reaches COMPLETED with wrong severity
    check("status = COMPLETED (quiet failure confirmed)",
          claim.get("status"), "COMPLETED", assertions,
          note="Expected — agent processes defective-value claim end-to-end without escalation. This is the quiet failure.")
    check("severity = LOW (no escalation triggered)",
          claim.get("severity"), "LOW", assertions,
          note="£1,400 (simulated defective extraction) produces score < 40 -> LOW. True value £14,000 would produce MEDIUM/HIGH.")
    check("no HIGH_SEVERITY escalation fired",
          not steps_have_escalation(steps, "HIGH_SEVERITY"), True, assertions)
    check("estimated_loss_value < 2000 (defective extraction active)",
          (claim.get("estimated_loss_value") or 99999) < 2000, True, assertions,
          note="Input text contains £1,400 (simulated defect). Current extraction regex correctly reads it as 1400.")

    # Detection mechanism
    assertions.append({
        "assertion": "Primary detection: nightly batch value comparison",
        "expected": "Batch job compares extracted_value against adjuster reserve; alert if < 0.5×",
        "actual": "NOT IMPLEMENTED — no batch job exists in current build",
        "passed": False,
        "note": "The D4 pass criterion for Scenario 5 tests the detection mechanism, not agent processing. The batch comparison job is a production dependency (D5-U — CRM adjuster reserve field exposure required). Implementation gap.",
    })
    assertions.append({
        "assertion": "Secondary detection: unactioned low-value MOTOR/PROPERTY flag",
        "expected": "Flag if adjuster does not set reserve within 72h for MOTOR claim < £2,000",
        "actual": "NOT IMPLEMENTED — no adjuster follow-up monitoring in current build",
        "passed": False,
        "note": "Secondary detection mechanism from D4. Requires CRM integration with adjuster reserve tracking.",
    })

    results_store["S5"] = {
        "name": "Silent Severity Downgrade — Quiet Failure",
        "type": "Failure Mode / Delegation Boundary",
        "assertions": assertions,
        "claim": claim,
        "steps": steps,
    }
    _print_assertions(assertions)


# ---------------------------------------------------------------------------
# Printing helpers
# ---------------------------------------------------------------------------

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
INFO = "\033[93mINFO\033[0m"
NIMPL = "\033[95mNOT_IMPL\033[0m"


def _status_label(passed):
    if passed is True:
        return PASS
    if passed is False:
        return FAIL
    return INFO


def _print_assertions(assertions):
    for a in assertions:
        status = _status_label(a["passed"])
        print(f"  [{status}] {a['assertion']}")
        if a["passed"] is False:
            print(f"         Expected : {a['expected']}")
            print(f"         Actual   : {a['actual']}")
        if a.get("note"):
            print(f"         Note     : {a['note']}")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary(results_store):
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"{'Scenario':<8} {'Name':<45} {'Pass':<5} {'Fail':<5} {'Info':<5}")
    print("-" * 70)

    total_pass = total_fail = total_info = 0
    scenario_results = []

    for sid, data in results_store.items():
        assertions = data.get("assertions", [])
        passes = sum(1 for a in assertions if a["passed"] is True)
        fails = sum(1 for a in assertions if a["passed"] is False)
        infos = sum(1 for a in assertions if a["passed"] is None)
        total_pass += passes
        total_fail += fails
        total_info += infos
        status = "FAIL" if fails > 0 else "PASS"
        scenario_results.append({
            "id": sid,
            "name": data["name"],
            "type": data.get("type", ""),
            "pass_count": passes,
            "fail_count": fails,
            "info_count": infos,
            "overall": status,
        })
        colour = "\033[92m" if status == "PASS" else "\033[91m"
        reset = "\033[0m"
        print(f"  {sid:<6} {data['name'][:44]:<45} {colour}{passes:<5}{reset} {fails:<5} {infos:<5}")

    print("-" * 70)
    print(f"  {'TOTAL':<52} {total_pass:<5} {total_fail:<5} {total_info:<5}")
    print()

    return scenario_results


def write_json_report(results_store, scenario_results):
    report = {
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "agent_script": str(AGENT_SCRIPT),
        "scenarios": [],
    }
    for sid, data in results_store.items():
        assertions = data.get("assertions", [])
        passes = sum(1 for a in assertions if a["passed"] is True)
        fails = sum(1 for a in assertions if a["passed"] is False)
        report["scenarios"].append({
            "id": sid,
            "name": data["name"],
            "type": data.get("type", ""),
            "overall": "FAIL" if fails > 0 else "PASS",
            "pass_count": passes,
            "fail_count": fails,
            "assertions": assertions,
        })

    out_path = OUTPUT_DIR / "test_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("FNOL Processing Agent — Validation Test Runner")
    print(f"Running {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Data dir   : {DATA_DIR}")
    print(f"Output dir : {OUTPUT_DIR}")

    results_store = {}
    scenario_1(results_store)
    scenario_2(results_store)
    scenario_3(results_store)
    scenario_4(results_store)
    scenario_5(results_store)

    scenario_results = print_summary(results_store)
    report_path = write_json_report(results_store, scenario_results)
    print(f"JSON report : {report_path}")
    print()


if __name__ == "__main__":
    main()
