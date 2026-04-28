"""
FNOL Processing Agent — Console Demonstration Application
Spec: Capability Specification §11 (agent_build/src/main.py)
"""

import argparse
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

AGENT_ID = "fnol-agent-v1.0.0"

CLAIM_TYPE_KEYWORDS = {
    "MOTOR": [
        "vehicle", "car", "motorbike", "motorcycle", "collision", "crash",
        "accident", "road", "driver", "driving", "traffic", "van", "truck",
        "lorry", "auto", "automobile", "wheel", "tyre", "tire",
    ],
    "PROPERTY": [
        "house", "home", "building", "property", "roof", "flood", "fire",
        "subsidence", "burst pipe", "water damage", "break-in", "burglary",
        "theft", "window", "door", "flat", "apartment",
        "damp", "leak", "leaking", "ceiling", "pipe", "plumbing", "wall damage",
    ],
    "LIABILITY": [
        "liability", "negligence", "injury", "slipped", "fell", "tripped",
        "public", "employer", "third party", "sued", "lawsuit", "compensation",
    ],
    "HEALTH": [
        "medical", "hospital", "surgery", "treatment", "illness", "disease",
        "health", "dental", "prescription", "gp", "doctor", "diagnosis",
    ],
}

SPECIAL_FLAG_KEYWORDS = {
    "FATALITY": ["fatal", "fatality", "death", "deceased", "died", "killed", "dead body"],
    "LEGAL_REPRESENTATION": ["solicitor", "lawyer", "legal representative", "my attorney", "barrister"],
    "VULNERABLE_CLAIMANT": ["elderly", "disabled", "mental health", "carer", "dementia", "vulnerable"],
    "FRAUD_INDICATOR": ["previously claimed", "identical claim", "suspicious", "staged", "inflated"],
}

SPECIALTY_MAP = {
    "MOTOR": "MOTOR",
    "PROPERTY": "PROPERTY",
    "LIABILITY": "LIABILITY",
    "HEALTH": "HEALTH",
    "OTHER": "GENERAL",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def generate_external_ref() -> str:
    import random
    import string
    letters = "".join(random.choices(string.ascii_uppercase, k=2))
    digits = "".join(random.choices(string.digits, k=8))
    return f"{letters}-{digits}"


# ---------------------------------------------------------------------------
# Step implementations
# ---------------------------------------------------------------------------

def step_parse(claim_input: dict) -> dict:
    """
    REQ-1: Extract structured attributes from raw_input.
    Returns extracted fields + parse_confidence.
    Simulates NLP extraction with heuristic scoring.
    """
    raw = claim_input.get("raw_input", "")
    policy_id = claim_input.get("policy_id", "")
    loss_date = claim_input.get("loss_date", "")

    # Count successfully extracted fields
    fields_found = 0
    total_fields = 6  # policy_id, loss_date, loss_description, claimant_email, estimated_value, narrative

    # policy_id: provided as input field or extracted from text
    if policy_id and re.match(r"[A-Z]{2}-[0-9]{8}", policy_id):
        fields_found += 1
    elif re.search(r"[A-Z]{2}-[0-9]{8}", raw):
        policy_id = re.search(r"[A-Z]{2}-[0-9]{8}", raw).group(0)
        fields_found += 1

    # loss_date: provided as input field
    if loss_date:
        fields_found += 1

    # claimant_email
    email_match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", raw)
    claimant_email = email_match.group(0) if email_match else None
    if claimant_email:
        fields_found += 1

    # estimated_loss_value — look for currency amounts
    value_match = re.search(r"[£$€][\s]?([0-9,]+(?:\.[0-9]{1,2})?)", raw)
    if not value_match:
        value_match = re.search(r"([0-9,]+(?:\.[0-9]{1,2})?)\s*(?:pounds|dollars|euros|GBP|USD)", raw, re.I)
    estimated_loss_value = None
    if value_match:
        raw_val = value_match.group(1).replace(",", "")
        estimated_loss_value = float(raw_val)
        fields_found += 1
    else:
        # ASSUMED: always estimable — use default
        estimated_loss_value = 5000.0

    # loss_description — first 300 chars of raw after stripping salutation
    loss_description = raw[:300].strip()
    if loss_description:
        fields_found += 1

    # claim_narrative — full cleaned text
    claim_narrative = raw.strip()
    if claim_narrative:
        fields_found += 1

    # parse_confidence: proportion of fields found, penalised if narrative < 100 chars
    parse_confidence = round(min(fields_found / total_fields, 1.0), 3)
    if len(raw) < 100:
        parse_confidence = min(parse_confidence, 0.55)

    assumptions = []
    if not claimant_email:
        assumptions.append("[ASSUMED] claimant_contact_email not found in raw_input; agent cannot send receipt ACK")
        claimant_email = "unknown@placeholder.invalid"
    if not estimated_loss_value:
        assumptions.append("[ASSUMED] estimated_loss_value not extractable; defaulted to £5,000")
    if not loss_date:
        assumptions.append("[ASSUMED] loss_date not provided in input; using today's date")
        loss_date = datetime.now(timezone.utc).date().isoformat()

    return {
        "policy_id": policy_id,
        "loss_date": loss_date,
        "loss_description": loss_description,
        "claim_narrative": claim_narrative,
        "claimant_contact_email": claimant_email,
        "estimated_loss_value": estimated_loss_value,
        "parse_confidence": parse_confidence,
        "assumptions": assumptions,
    }


def step_classify(claim_narrative: str) -> dict:
    """
    REQ-2: Classify claim type from narrative keywords.
    Returns claim_type + classification_confidence.
    """
    narrative_lower = claim_narrative.lower()
    scores = {}
    for claim_type, keywords in CLAIM_TYPE_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in narrative_lower)
        scores[claim_type] = hits

    if not any(scores.values()):
        return {
            "claim_type": "OTHER",
            "classification_confidence": 0.50,
            "scores": scores,
        }

    total_hits = sum(scores.values())
    best_type = max(scores, key=scores.get)
    best_hits = scores[best_type]

    # Confidence = dominant type's proportion of all keyword hits, scaled
    raw_conf = best_hits / total_hits if total_hits > 0 else 0.5
    # Penalise if very few hits (ambiguous text)
    if best_hits < 2:
        raw_conf *= 0.7
    classification_confidence = round(min(raw_conf, 1.0), 3)

    # Minimum floor of 0.50 if we found something
    classification_confidence = max(classification_confidence, 0.50)

    return {
        "claim_type": best_type,
        "classification_confidence": classification_confidence,
        "scores": scores,
    }


def step_severity(claim_type: str, estimated_loss_value: float, claim_narrative: str) -> dict:
    """
    REQ-3: Assess severity as LOW/MEDIUM/HIGH/CRITICAL.
    severity_score: 0–100 based on estimated loss value and claim type.
    TODO: scoring thresholds to be validated with client (D5-U1)
    """
    narrative_lower = claim_narrative.lower()
    score = 0

    # Value-based scoring (assumed thresholds — D5-U1)
    if estimated_loss_value < 1000:
        score += 10
    elif estimated_loss_value < 5000:
        score += 25
    elif estimated_loss_value < 15000:
        score += 45
    elif estimated_loss_value < 50000:
        score += 65
    else:
        score += 80

    # Claim-type modifier
    type_modifiers = {"MOTOR": 5, "PROPERTY": 5, "LIABILITY": 10, "HEALTH": 15, "OTHER": 0}
    score += type_modifiers.get(claim_type, 0)

    # Narrative severity signals
    high_severity_words = ["serious", "critical", "urgent", "emergency", "hospitalised", "hospitalized",
                           "surgery", "significant damage", "total loss", "write-off"]
    score += sum(5 for w in high_severity_words if w in narrative_lower)

    score = min(score, 100)

    if score >= 80:
        severity = "CRITICAL"
    elif score >= 60:
        severity = "HIGH"
    elif score >= 40:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    assumptions = ["[ASSUMED] severity_score thresholds are illustrative (D5-U1); requires validation with client against historical data"]

    return {
        "severity": severity,
        "severity_score": score,
        "assumptions": assumptions,
    }


def step_detect_flags(claim_narrative: str, claim_type: str) -> dict:
    """
    REQ-4: Detect special handling flags.
    ASSUMED: fraud_score and sentiment_score not available — heuristic keyword-only.
    """
    narrative_lower = claim_narrative.lower()
    flags_detected = []
    details = {}
    assumptions = []

    for flag, keywords in SPECIAL_FLAG_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in narrative_lower]
        if hits:
            flags_detected.append(flag)
            details[flag] = {"matched_keywords": hits, "confidence": 0.80}

    # Extra rule: MOTOR + fatality keywords
    if claim_type == "MOTOR" and any(kw in narrative_lower for kw in ["fatal", "death", "deceased"]):
        if "FATALITY" not in flags_detected:
            flags_detected.append("FATALITY")
            details["FATALITY"] = {"matched_keywords": ["motor+fatality_keyword"], "confidence": 0.85}

    assumptions.append("[ASSUMED] VULNERABLE_CLAIMANT detection via sentiment_score not available (D5-U2); keyword-only heuristic used")
    assumptions.append("[ASSUMED] FRAUD_INDICATOR detection via fraud_score model not available (D5-U2); keyword-only heuristic used")
    assumptions.append("[ASSUMED] Full keyword sets for FATALITY and LEGAL_REPRESENTATION to be confirmed with legal/compliance team (D5-U9)")

    return {
        "special_handling_flags": flags_detected,
        "flag_details": details,
        "assumptions": assumptions,
    }


def step_validate_coverage(claim_type: str, loss_date: str, mock_policy: dict) -> dict:
    """
    REQ-5: Validate policy coverage against mock policy record.
    """
    assumptions = []

    # Simulate policy admin system unavailability (Scenario 4 test support)
    if mock_policy.get("simulate_unavailable"):
        return {
            "policy_status": "UNAVAILABLE",
            "coverage_match_confidence": 0.0,
            "exclusion_candidates": [],
            "policy_tier": "UNKNOWN",
            "assumptions": [],
            "integration_error": True,
            "error_detail": "Policy admin system returned HTTP 503; 3 retries exhausted (2s/4s/8s backoff)",
            "retry_count": 3,
        }

    # Map policy_status field name: mock uses ACTIVE, spec expects IN_FORCE
    raw_status = mock_policy.get("policy_status", "UNKNOWN")
    status_map = {"ACTIVE": "IN_FORCE", "IN_FORCE": "IN_FORCE", "LAPSED": "LAPSED",
                  "CANCELLED": "LAPSED", "SUSPENDED": "LAPSED"}
    policy_status = status_map.get(raw_status, "UNCERTAIN")

    policy_start = mock_policy.get("policy_start_date")
    policy_end = mock_policy.get("policy_end_date")

    # Check in-force at loss_date
    if policy_status == "IN_FORCE" and policy_start and policy_end:
        try:
            ld = datetime.strptime(loss_date, "%Y-%m-%d").date()
            ps = datetime.strptime(policy_start, "%Y-%m-%d").date()
            pe = datetime.strptime(policy_end, "%Y-%m-%d").date()
            if not (ps <= ld <= pe):
                policy_status = "LAPSED"
        except ValueError:
            assumptions.append("[ASSUMED] Could not parse dates for in-force check; treating as IN_FORCE")

    covered_perils = mock_policy.get("covered_perils", [])
    exclusions = mock_policy.get("exclusions", [])

    # Check if claim_type is in covered perils
    covered = any(claim_type in p.upper() for p in covered_perils)

    if not covered_perils:
        coverage_match_confidence = 0.0
        assumptions.append("[ASSUMED] covered_perils field empty; defaulting coverage_match_confidence to 0.0 (D5-U)")
    elif covered:
        coverage_match_confidence = 0.92
    else:
        coverage_match_confidence = 0.40

    # All policy exclusions are potentially applicable; specialist must evaluate each one
    exclusion_candidates = list(exclusions) if exclusions else []

    return {
        "policy_status": policy_status,
        "coverage_match_confidence": round(coverage_match_confidence, 3),
        "exclusion_candidates": exclusion_candidates,
        "policy_tier": mock_policy.get("policy_tier", "UNKNOWN"),
        "assumptions": assumptions,
    }


def step_route_adjuster(claim_type: str, mock_adjusters: list) -> dict:
    """
    REQ-6: Select adjuster with matching specialty and lowest queue depth.
    """
    specialty_required = SPECIALTY_MAP.get(claim_type, "GENERAL")
    candidates = [
        a for a in mock_adjusters
        if a.get("adjuster_specialty") == specialty_required and a.get("is_available", False)
    ]

    if not candidates:
        return {
            "status": "QUEUE_OVERFLOW",
            "specialty_required": specialty_required,
            "selected_adjuster_id": None,
            "queue_depth_at_assignment": None,
        }

    # Sort by current_queue_depth ascending; pick lowest
    candidates_sorted = sorted(candidates, key=lambda a: a["current_queue_depth"])
    selected = candidates_sorted[0]

    return {
        "status": "ROUTED",
        "specialty_required": specialty_required,
        "selected_adjuster_id": selected["adjuster_id"],
        "adjuster_specialty": selected["adjuster_specialty"],
        "queue_depth_at_assignment": selected["current_queue_depth"],
    }


# ---------------------------------------------------------------------------
# HTML Report Generator
# ---------------------------------------------------------------------------

def generate_html_report(claim_record: dict, steps: list, assumptions_all: list, output_path: str) -> None:
    """Generate an inline-CSS HTML report from the processing run."""

    def esc(v) -> str:
        return str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    total_ms = sum(s["duration_ms"] for s in steps)
    sla_status = "BREACHED" if claim_record.get("sla_breached") else "MET"
    sla_color = "#dc3545" if sla_status == "BREACHED" else "#28a745"
    run_ts = claim_record.get("created_at", now_utc())

    # Build rows for processing summary table
    step_rows = ""
    for s in steps:
        esc_trigger = "Y" if s.get("escalation_triggered") else "N"
        esc_cell_style = "background:#fff3cd;font-weight:bold;" if s.get("escalation_triggered") else ""
        step_rows += f"""
        <tr>
          <td style="padding:8px 12px;border-bottom:1px solid #dee2e6;">{esc(s['step_number'])}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #dee2e6;">{esc(s['action'])}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #dee2e6;">{esc(s['duration_ms'])} ms</td>
          <td style="padding:8px 12px;border-bottom:1px solid #dee2e6;">{esc(s['outcome'])}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #dee2e6;">{esc(s['delegation_tier'])}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #dee2e6;{esc_cell_style}">{esc_trigger}</td>
        </tr>"""

    # Assumptions list
    assumptions_html = ""
    seen = set()
    for a in assumptions_all:
        if a not in seen:
            seen.add(a)
            assumptions_html += f'<li style="margin-bottom:6px;">{esc(a)}</li>\n'

    # Escalation log
    escalation_html = ""
    for s in steps:
        if s.get("escalation_triggered"):
            reason = s.get("escalation_reason", "UNKNOWN")
            window = s.get("review_window_minutes", "?")
            escalation_html += f"""
            <div style="background:#fff3cd;border-left:4px solid #ffc107;padding:10px 16px;margin-bottom:8px;border-radius:4px;">
              <strong>Step {esc(s['step_number'])} — {esc(s['action'])}</strong><br/>
              Reason: <code>{esc(reason)}</code> &nbsp;|&nbsp; Review window: {esc(window)} min<br/>
              <em style="color:#6c757d;">Simulated: specialist confirmed agent recommendation (happy path)</em>
            </div>"""
    if not escalation_html:
        escalation_html = '<p style="color:#6c757d;">No escalations triggered.</p>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FNOL Processing Agent — Run Report</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         margin: 0; padding: 0; background: #f8f9fa; color: #212529; }}
  .header {{ background: #1a2332; color: #fff; padding: 28px 40px; }}
  .header h1 {{ margin: 0 0 4px 0; font-size: 22px; font-weight: 600; }}
  .header .meta {{ font-size: 13px; opacity: 0.75; }}
  .badge {{ display:inline-block; padding:3px 10px; border-radius:12px;
            font-size:12px; font-weight:600; }}
  .badge-green {{ background:#d4edda; color:#155724; }}
  .badge-red   {{ background:#f8d7da; color:#721c24; }}
  .badge-yellow {{ background:#fff3cd; color:#856404; }}
  .badge-blue  {{ background:#d1ecf1; color:#0c5460; }}
  .container {{ max-width: 1100px; margin: 32px auto; padding: 0 24px; }}
  .card {{ background:#fff; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,.1);
           margin-bottom:24px; overflow:hidden; }}
  .card-header {{ background:#f1f3f5; padding:14px 20px; font-weight:600;
                  font-size:14px; border-bottom:1px solid #dee2e6; }}
  .card-body {{ padding:20px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th {{ background:#f8f9fa; padding:10px 12px; text-align:left;
        border-bottom:2px solid #dee2e6; font-size:12px; text-transform:uppercase;
        letter-spacing:.04em; color:#6c757d; }}
  .kv-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
  .kv {{ padding:12px 16px; background:#f8f9fa; border-radius:6px; }}
  .kv .label {{ font-size:11px; color:#6c757d; text-transform:uppercase;
                letter-spacing:.04em; margin-bottom:4px; }}
  .kv .value {{ font-size:15px; font-weight:600; }}
  code {{ background:#f1f3f5; padding:2px 6px; border-radius:4px; font-size:12px; }}
  ul {{ margin:0; padding-left:20px; }}
  footer {{ text-align:center; font-size:12px; color:#6c757d; padding:24px; }}
</style>
</head>
<body>

<div class="header">
  <h1>FNOL Processing Agent — Run Report</h1>
  <div class="meta">
    Agent ID: {esc(AGENT_ID)} &nbsp;|&nbsp;
    Claim Reference: <strong>{esc(claim_record.get('external_reference','N/A'))}</strong> &nbsp;|&nbsp;
    Channel: {esc(claim_record.get('source_channel','N/A'))} &nbsp;|&nbsp;
    Processed: {esc(run_ts)} &nbsp;|&nbsp;
    Total time: <strong>{esc(total_ms)} ms</strong>
  </div>
</div>

<div class="container">

  <!-- Claim Outcome -->
  <div class="card">
    <div class="card-header">Claim Outcome</div>
    <div class="card-body">
      <div class="kv-grid">
        <div class="kv">
          <div class="label">External Reference</div>
          <div class="value"><code>{esc(claim_record.get('external_reference','N/A'))}</code></div>
        </div>
        <div class="kv">
          <div class="label">Final Status</div>
          <div class="value">
            <span class="badge badge-green">{esc(claim_record.get('status','N/A'))}</span>
          </div>
        </div>
        <div class="kv">
          <div class="label">Claim Type</div>
          <div class="value">{esc(claim_record.get('claim_type','N/A'))}</div>
        </div>
        <div class="kv">
          <div class="label">Severity</div>
          <div class="value">{esc(claim_record.get('severity','N/A'))} (score: {esc(claim_record.get('severity_score','N/A'))})</div>
        </div>
        <div class="kv">
          <div class="label">Coverage Status</div>
          <div class="value">{esc(claim_record.get('coverage_status','N/A'))}</div>
        </div>
        <div class="kv">
          <div class="label">Assigned Adjuster</div>
          <div class="value"><code>{esc(claim_record.get('assigned_adjuster_id','N/A'))}</code></div>
        </div>
        <div class="kv">
          <div class="label">SLA Deadline</div>
          <div class="value">{esc(claim_record.get('sla_deadline','N/A'))}</div>
        </div>
        <div class="kv">
          <div class="label">SLA Status</div>
          <div class="value">
            <span style="color:{esc(sla_color)};font-weight:700;">{esc(sla_status)}</span>
          </div>
        </div>
        <div class="kv">
          <div class="label">Special Handling Flags</div>
          <div class="value">{esc(', '.join(claim_record.get('special_handling_flags',[])) or 'None')}</div>
        </div>
        <div class="kv">
          <div class="label">Policy Status</div>
          <div class="value">{esc(claim_record.get('policy_status','N/A'))}</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Processing Summary -->
  <div class="card">
    <div class="card-header">Processing Summary — {esc(len(steps))} steps &nbsp;|&nbsp; {esc(total_ms)} ms total</div>
    <div class="card-body" style="padding:0;">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Action</th>
            <th>Duration</th>
            <th>Outcome</th>
            <th>Delegation Tier</th>
            <th>Escalation</th>
          </tr>
        </thead>
        <tbody>{step_rows}</tbody>
      </table>
    </div>
  </div>

  <!-- Escalations -->
  <div class="card">
    <div class="card-header">Escalation Log</div>
    <div class="card-body">
      {escalation_html}
    </div>
  </div>

  <!-- Assumptions -->
  <div class="card">
    <div class="card-header">Assumptions Flagged During Run</div>
    <div class="card-body">
      <ul>{assumptions_html}</ul>
    </div>
  </div>

  <!-- Raw Claim Record -->
  <div class="card">
    <div class="card-header">Final Claim Record (JSON)</div>
    <div class="card-body">
      <pre style="background:#f8f9fa;padding:16px;border-radius:6px;font-size:12px;
                  overflow-x:auto;margin:0;">{esc(json.dumps(claim_record, indent=2, default=str))}</pre>
    </div>
  </div>

</div>

<footer>
  FNOL Processing Agent &mdash; Closed Build Loop Demonstration &mdash; {esc(AGENT_ID)}
</footer>

</body>
</html>"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def run(input_path: str, mock_policy_path: str, mock_adjusters_path: str, output_dir: str) -> None:
    # Load inputs
    with open(input_path, encoding="utf-8") as f:
        claim_input = json.load(f)
    with open(mock_policy_path, encoding="utf-8") as f:
        mock_policy = json.load(f)
    with open(mock_adjusters_path, encoding="utf-8") as f:
        mock_adjusters = json.load(f)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    created_at = datetime.now(timezone.utc)
    sla_deadline = (created_at + timedelta(seconds=7200)).isoformat(timespec="seconds").replace("+00:00", "Z")
    claim_id = str(uuid.uuid4())
    external_ref = generate_external_ref()

    # Initialise claim record
    claim_record = {
        "id": claim_id,
        "external_reference": external_ref,
        "source_channel": claim_input.get("source_channel", "EMAIL"),
        "raw_input": claim_input.get("raw_input", ""),
        "policy_id": claim_input.get("policy_id", ""),
        "loss_date": claim_input.get("loss_date", ""),
        "status": "RECEIVED",
        "sla_deadline": sla_deadline,
        "sla_breached": False,
        "agent_id": AGENT_ID,
        "created_at": created_at.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "updated_at": created_at.isoformat(timespec="seconds").replace("+00:00", "Z"),
    }

    steps = []
    assumptions_all = []

    def log_step(num, action, outcome, tier, escalation=False, reason=None, window=None, duration_ms=0):
        steps.append({
            "step_number": num,
            "action": action,
            "outcome": outcome,
            "delegation_tier": tier,
            "escalation_triggered": escalation,
            "escalation_reason": reason,
            "review_window_minutes": window,
            "duration_ms": duration_ms,
        })
        esc_tag = ""
        if escalation:
            esc_tag = f"\n  [ESCALATION] reason: {reason}, review_window: {window} min"
            esc_tag += "\n  [ESCALATION RESOLVED] Simulating specialist confirmed agent recommendation (happy path)"
        print(f"\nStep {num}: {action}")
        print(f"  Outcome       : {outcome}")
        print(f"  Delegation    : {tier}")
        print(f"  Duration      : {duration_ms} ms")
        if escalation:
            print(esc_tag)

    print("=" * 68)
    print(f"FNOL Processing Agent — {AGENT_ID}")
    print(f"Claim ID     : {claim_id}")
    print(f"External Ref : {external_ref}")
    print(f"SLA Deadline : {sla_deadline}")
    print(f"Source       : {claim_record['source_channel']}")
    print("=" * 68)

    # -----------------------------------------------------------------------
    # Step 1: Load input claim
    # -----------------------------------------------------------------------
    t0 = time.perf_counter()
    claim_record["status"] = "PARSING"
    duration = int((time.perf_counter() - t0) * 1000) + 1
    log_step(1, "Load and ingest claim", f"ClaimRecord created | source={claim_record['source_channel']}", "AGENT_ONLY (REQ-1)", duration_ms=duration)

    # -----------------------------------------------------------------------
    # Step 2: Parse and extract attributes
    # -----------------------------------------------------------------------
    t0 = time.perf_counter()
    parsed = step_parse(claim_input)
    duration = int((time.perf_counter() - t0) * 1000) + 1

    claim_record.update({
        "loss_date": parsed["loss_date"],
        "loss_description": parsed["loss_description"],
        "claim_narrative": parsed["claim_narrative"],
        "claimant_contact_email": parsed["claimant_contact_email"],
        "estimated_loss_value": parsed["estimated_loss_value"],
        "parse_confidence": parsed["parse_confidence"],
    })
    assumptions_all.extend(parsed["assumptions"])

    parse_conf = parsed["parse_confidence"]
    escalated = parse_conf < 0.70
    if not escalated:
        claim_record["status"] = "PARSED"

    log_step(2, "Parse & extract attributes (REQ-1)",
             f"parse_confidence={parse_conf} | email={parsed['claimant_contact_email']} | est_loss=£{parsed['estimated_loss_value']}",
             "AGENT_ONLY (1.1)",
             escalation=escalated,
             reason="LOW_PARSE_CONFIDENCE" if escalated else None,
             window=60 if escalated else None,
             duration_ms=duration)

    # -----------------------------------------------------------------------
    # Step 3: Classify claim type
    # -----------------------------------------------------------------------
    t0 = time.perf_counter()
    classified = step_classify(parsed["claim_narrative"])
    duration = int((time.perf_counter() - t0) * 1000) + 1

    claim_record["claim_type"] = classified["claim_type"]
    claim_record["classification_confidence"] = classified["classification_confidence"]

    class_conf = classified["classification_confidence"]
    escalated_class = class_conf < 0.85
    log_step(3, "Classify claim type (REQ-2)",
             f"claim_type={classified['claim_type']} | classification_confidence={class_conf}",
             "AGENT_LOG (1.2)" if not escalated_class else "AGENT_REVIEW (1.2)",
             escalation=escalated_class,
             reason="LOW_CLASSIFICATION_CONFIDENCE" if escalated_class else None,
             window=30 if escalated_class else None,
             duration_ms=duration)

    # -----------------------------------------------------------------------
    # Step 4: Assess severity
    # -----------------------------------------------------------------------
    t0 = time.perf_counter()
    severity_result = step_severity(
        claim_record["claim_type"],
        parsed["estimated_loss_value"],
        parsed["claim_narrative"],
    )
    duration = int((time.perf_counter() - t0) * 1000) + 1

    claim_record["severity"] = severity_result["severity"]
    claim_record["severity_score"] = severity_result["severity_score"]
    assumptions_all.extend(severity_result["assumptions"])

    sev = severity_result["severity"]
    high_sev = sev in ("HIGH", "CRITICAL")
    log_step(4, "Assess severity (REQ-3)",
             f"severity={sev} | severity_score={severity_result['severity_score']}",
             "AGENT_LOG (1.3)" if not high_sev else "AGENT_REVIEW (1.4)",
             escalation=high_sev,
             reason="HIGH_SEVERITY" if high_sev else None,
             window=30 if high_sev else None,
             duration_ms=duration)

    # -----------------------------------------------------------------------
    # Step 5: Detect special handling flags
    # -----------------------------------------------------------------------
    t0 = time.perf_counter()
    flag_result = step_detect_flags(parsed["claim_narrative"], claim_record["claim_type"])
    duration = int((time.perf_counter() - t0) * 1000) + 1

    claim_record["special_handling_flags"] = flag_result["special_handling_flags"]
    assumptions_all.extend(flag_result["assumptions"])

    flags_found = flag_result["special_handling_flags"]
    flag_escalated = bool(flags_found)

    if not high_sev and not flag_escalated:
        claim_record["status"] = "TRIAGED"

    log_step(5, "Detect special handling flags (REQ-4)",
             f"flags={flags_found if flags_found else 'None'}",
             "AGENT_REVIEW (1.5)" if flag_escalated else "AGENT_LOG (1.3)",
             escalation=flag_escalated,
             reason="SPECIAL_FLAG_DETECTED" if flag_escalated else None,
             window=15 if flag_escalated else None,
             duration_ms=duration)

    # Mark TRIAGED after triage steps complete (including any specialist sim)
    claim_record["status"] = "TRIAGED"

    # -----------------------------------------------------------------------
    # Step 6: Validate policy coverage
    # -----------------------------------------------------------------------
    t0 = time.perf_counter()
    claim_record["status"] = "VALIDATING"
    coverage_result = step_validate_coverage(
        claim_record["claim_type"],
        claim_record["loss_date"],
        mock_policy,
    )
    duration = int((time.perf_counter() - t0) * 1000) + 1

    claim_record["policy_status"] = coverage_result["policy_status"]
    claim_record["coverage_match_confidence"] = coverage_result["coverage_match_confidence"]
    claim_record["exclusion_candidates"] = coverage_result["exclusion_candidates"]
    assumptions_all.extend(coverage_result["assumptions"])

    # Handle integration error before normal coverage logic
    if coverage_result.get("integration_error"):
        claim_record["coverage_status"] = "UNCERTAIN"
        claim_record["status"] = "INTEGRATION_ERROR"
        log_step(6, "Validate policy coverage (REQ-5)",
                 f"INTEGRATION_ERROR: {coverage_result['error_detail']}",
                 "AGENT_REVIEW (escalate to specialist)",
                 escalation=True,
                 reason="INTEGRATION_ERROR",
                 window=5,
                 duration_ms=duration)

        # Write outputs and stop — do not proceed to routing
        claim_record["updated_at"] = now_utc()
        output_json_path = os.path.join(output_dir, "claim_result.json")
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(claim_record, f, indent=2, default=str)
        output_steps_path = os.path.join(output_dir, "steps_result.json")
        with open(output_steps_path, "w", encoding="utf-8") as f:
            json.dump(steps, f, indent=2, default=str)
        html_path = os.path.join(output_dir, "report.html")
        generate_html_report(claim_record, steps, assumptions_all, html_path)
        total_ms = sum(s["duration_ms"] for s in steps)
        print("\n" + "=" * 68)
        print("PROCESSING HALTED — INTEGRATION_ERROR")
        print(f"  Final status  : {claim_record['status']}")
        print(f"  Error         : {coverage_result['error_detail']}")
        print(f"  Retry count   : {coverage_result.get('retry_count', 'N/A')}")
        print(f"  HTML report   : {html_path}")
        print(f"  Claim JSON    : {output_json_path}")
        print("=" * 68)
        return

    cov_conf = coverage_result["coverage_match_confidence"]
    pol_status = coverage_result["policy_status"]

    if pol_status != "IN_FORCE":
        claim_record["coverage_status"] = "NOT_COVERED"
        claim_record["status"] = "COVERAGE_LAPSED"
        cov_tier = "HUMAN_ONLY (2.6)"
        cov_escalated = True
        cov_reason = "COVERAGE_LAPSED"
        cov_window = None
    elif cov_conf < 0.70:
        claim_record["coverage_status"] = "DISPUTED"
        claim_record["status"] = "COVERAGE_DISPUTED"
        cov_tier = "HUMAN_ONLY (2.6)"
        cov_escalated = True
        cov_reason = "COVERAGE_DISPUTE"
        cov_window = None
    elif cov_conf < 0.85 or coverage_result["exclusion_candidates"]:
        claim_record["coverage_status"] = "UNCERTAIN"
        claim_record["status"] = "COVERAGE_PENDING_REVIEW"
        cov_tier = "AGENT_REVIEW (2.4/2.5)"
        cov_escalated = True
        cov_reason = "AMBIGUOUS_COVERAGE"
        cov_window = 30
    else:
        claim_record["coverage_status"] = "COVERED"
        claim_record["status"] = "COVERAGE_CONFIRMED"
        cov_tier = "AGENT_LOG (2.3)"
        cov_escalated = False
        cov_reason = None
        cov_window = None

    log_step(6, "Validate policy coverage (REQ-5)",
             f"policy_status={pol_status} | coverage_match_confidence={cov_conf} | coverage_status={claim_record['coverage_status']}",
             cov_tier,
             escalation=cov_escalated,
             reason=cov_reason,
             window=cov_window,
             duration_ms=duration)

    # -----------------------------------------------------------------------
    # Step 7: Route to adjuster (only if coverage confirmed)
    # -----------------------------------------------------------------------
    t0 = time.perf_counter()
    if claim_record.get("coverage_status") != "COVERED":
        duration = int((time.perf_counter() - t0) * 1000) + 1
        claim_record["assigned_adjuster_id"] = None
        claim_record["queue_depth_at_assignment"] = None
        route_escalated = False
        log_step(7, "Route to adjuster (REQ-6)",
                 f"SKIPPED — coverage_status={claim_record.get('coverage_status')}; awaiting specialist review",
                 "N/A",
                 duration_ms=duration)
    else:
        claim_record["status"] = "ROUTING"
        routing_result = step_route_adjuster(claim_record["claim_type"], mock_adjusters)
        duration = int((time.perf_counter() - t0) * 1000) + 1
        route_escalated = routing_result["status"] == "QUEUE_OVERFLOW"
        if not route_escalated:
            claim_record["status"] = "ROUTED"
            claim_record["assigned_adjuster_id"] = routing_result["selected_adjuster_id"]
            claim_record["queue_depth_at_assignment"] = routing_result["queue_depth_at_assignment"]
            route_outcome = (f"assigned={routing_result['selected_adjuster_id']} | "
                             f"specialty={routing_result.get('adjuster_specialty')} | "
                             f"queue_depth={routing_result['queue_depth_at_assignment']}")
        else:
            claim_record["status"] = "QUEUE_OVERFLOW"
            claim_record["assigned_adjuster_id"] = None
            route_outcome = f"QUEUE_OVERFLOW: no available {routing_result['specialty_required']} adjuster"
        log_step(7, "Route to adjuster (REQ-6)",
                 route_outcome,
                 "AGENT_ONLY (3.1/3.2)",
                 escalation=route_escalated,
                 reason="QUEUE_OVERFLOW" if route_escalated else None,
                 window=60 if route_escalated else None,
                 duration_ms=duration)

    # -----------------------------------------------------------------------
    # Step 8: Output final Claim state as JSON
    # -----------------------------------------------------------------------
    t0 = time.perf_counter()
    if not route_escalated:
        claim_record["status"] = "COMPLETED"
    claim_record["updated_at"] = now_utc()

    output_json_path = os.path.join(output_dir, "claim_result.json")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(claim_record, f, indent=2, default=str)
    output_steps_path = os.path.join(output_dir, "steps_result.json")
    with open(output_steps_path, "w", encoding="utf-8") as f:
        json.dump(steps, f, indent=2, default=str)
    duration = int((time.perf_counter() - t0) * 1000) + 1

    log_step(8, "Output final Claim state as JSON",
             f"status={claim_record['status']} | written to {output_json_path}",
             "AGENT_ONLY",
             duration_ms=duration)

    # -----------------------------------------------------------------------
    # Step 9: Generate HTML report
    # -----------------------------------------------------------------------
    t0 = time.perf_counter()
    html_path = os.path.join(output_dir, "report.html")
    generate_html_report(claim_record, steps, assumptions_all, html_path)
    duration = int((time.perf_counter() - t0) * 1000) + 1

    log_step(9, "Generate HTML report",
             f"written to {html_path}",
             "AGENT_ONLY",
             duration_ms=duration)

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    total_ms = sum(s["duration_ms"] for s in steps)
    print("\n" + "=" * 68)
    print("PROCESSING COMPLETE")
    print(f"  Final status  : {claim_record['status']}")
    print(f"  Claim type    : {claim_record.get('claim_type','N/A')}")
    print(f"  Severity      : {claim_record.get('severity','N/A')} (score={claim_record.get('severity_score','N/A')})")
    print(f"  Coverage      : {claim_record.get('coverage_status','N/A')}")
    print(f"  Adjuster      : {claim_record.get('assigned_adjuster_id','N/A')}")
    print(f"  SLA Status    : {'BREACHED' if claim_record.get('sla_breached') else 'MET'}")
    print(f"  Total time    : {total_ms} ms")
    print(f"  HTML report   : {html_path}")
    print(f"  Claim JSON    : {output_json_path}")
    print("=" * 68)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="FNOL Processing Agent — closed-loop demonstration"
    )
    parser.add_argument("--input", required=True, help="Path to claim input JSON file")
    parser.add_argument("--mock-policy", required=True, help="Path to mock policy JSON file")
    parser.add_argument("--mock-adjusters", required=True, help="Path to mock adjuster pool JSON file")
    parser.add_argument("--output-dir", default="./output", help="Output directory for report and JSON (default: ./output)")
    args = parser.parse_args()

    run(
        input_path=args.input,
        mock_policy_path=args.mock_policy,
        mock_adjusters_path=args.mock_adjusters,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
