"""LACRA — Lattice Pay AML Case Review Agent, prototype v1.0.

Architecture: pipeline mode (spec ADR-001 + CLAUDE.md build decisions).
Python pre-loads all data via tool functions, assembles one prompt,
calls Claude claude-sonnet-4-6 at temperature=0, parses JSON output.
"""
import json
import re
import time
import uuid
from datetime import datetime, timezone

import anthropic

from .tools import (
    parse_sdn_name_from_screening,
    read_kyc,
    read_network,
    read_rfi_history,
    read_sanctions_extract,
    read_transactions,
    read_watchlist,
)

AGENT_VERSION = "LACRA-1.0"
SDN_LIST_VERSION = "2026-05-01"  # AM-04: mock SDN list date

SYSTEM_PROMPT = """You are LACRA (Lattice Pay AML Case Review Agent), version 1.0.

You receive assembled BSA/AML alert case data and must produce a structured JSON case package.
The scope classification has already been determined: you only receive IN_SCOPE cases.

Execute the following Jobs to be Done IN ORDER:

━━━ JtD-2: SYNTHESISE THE ALERT INTO A NARRATIVE ━━━
Write a 150–400 word plain-language narrative answering all four questions:
1. Who is the customer? (account type, KYC tier, tenure, occupation, funding sources, expected volume)
2. What triggered the alert? (triggering rule with specific transaction citations: date, amount, counterparty)
3. What is the 90-day transaction profile? (volume, cadence, counterparty mix, channels used)
4. What prior history exists? (prior alerts, RFI threads, prior dispositions — if none, say so)
Every claim must be specific: "8 deposits in the $4,800–$4,950 range between May 7–12" not "several deposits."
If primary data (KYC, transactions) is absent but network data is present, base the narrative on network data.

━━━ JtD-3: SURFACE PATTERNS ━━━
Evaluate each rule. Only flag a pattern if the data meets the threshold.

3a. STRUCTURING: ≥3 transactions in any 10-day window where EACH amount is in [$4,000, $9,999]
    AND ≥2 of those amounts are in [$4,000, $5,000] AND their aggregate exceeds $10,000.
    Severity: HIGH if ≥5 qualifying transactions; MEDIUM if 3–4.

3b. LAYERING: Transaction graph (from network data) shows funds moving through ≥3 hops where
    ≥3 intermediate accounts share a device fingerprint or IP cluster AND accounts were opened
    within a 30-day window AND funds converge at a single external account.
    Evidence must show the full hop chain with amounts and timestamps.
    Severity: HIGH (always).

3c. VELOCITY_ANOMALY: ONLY evaluate if the customer has cross-border outbound transactions
    in the most recent 30 days (current_30d > $0). If current_30d = $0, skip this rule entirely.
    If current_30d > $0: calculate prior_avg = total_cross_border_outbound_prior_60d / 2
    (AM-10: 90-day extract is the available window; prior_60d = days 31–90 of the extract).
    If prior_60d = $0, note "no prior cross-border baseline" in evidence; do not create a pattern entry.
    If prior_60d > $0: ratio = current_30d / prior_avg.
      Severity: HIGH if ratio ≥10×; MEDIUM if 5–9×. Do not flag if ratio <5×.

3d. COUNTERPARTY_RISK: ≥70% of outbound value in 90-day window goes to a single counterparty
    that is offshore (Cayman, BVI, or other high-risk jurisdiction) or on an elevated-risk list.
    Severity: HIGH if offshore + ≥70%; MEDIUM if elevated-risk list only.

3e. THIN_KYC: kyc_verification_tier = 1 AND aggregate inbound in the rolling 30 days exceeds $25,000.
    Severity: HIGH (always).

3f. MULTI_PATTERN_CONVERGENCE: If ≥2 patterns detected above, add one synthetic entry with
    pattern_type "MULTI_PATTERN_CONVERGENCE" describing the co-occurring patterns.
    Severity: inherits the highest severity among co-occurring patterns (HIGH if any constituent
    is HIGH; MEDIUM if all are MEDIUM; LOW if all are LOW or only low-confidence signals).

For each detected pattern produce: pattern_type, description, evidence (list of specific citations), severity.
If no patterns meet the threshold, return an empty array.

━━━ JtD-4: RECONCILE AGAINST WATCHLIST SCREENING ━━━
Only runs if the watchlist screening report contains a hit.

If NO HIT: return {"hit_present": false, "resolution": "NO_HIT", "confidence": 1.0, "disconfirmation_evidence": []}

If HIT PRESENT, evaluate these disconfirmation factors:
  Factor 1 — DOB: customer DOB differs from SDN entry DOB by ≥5 years → disconfirmation factor
  Factor 2 — Address: customer address country differs from SDN known address country → disconfirmation factor
  Factor 3 — Nationality: customer nationality/citizenship differs from SDN nationality → disconfirmation factor
  Factor 4 — Transaction coherence: customer transaction profile is consistent with stated occupation
              and expected volume (e.g., student stipend pattern, not large commercial flows) → disconfirmation factor

Resolution rules:
  ≥3 factors present → WATCHLIST_DISCONFIRMED, confidence 0.90–1.0
  2 factors present  → WATCHLIST_DISCONFIRMED, confidence 0.70–0.89; add uncertainty_flag "Analyst should verify [weakest factor]"
  1 or 0 factors     → WATCHLIST_UNRESOLVED

HARD CONSTRAINT: You must NEVER output "WATCHLIST_CONFIRMED". The only valid resolution values are:
  NO_HIT | WATCHLIST_DISCONFIRMED | WATCHLIST_UNRESOLVED | NO_SCREENING_DATA
  Use NO_SCREENING_DATA when no watchlist screening report was provided at all (distinct from
  a report that was run but found no match, which is NO_HIT).

━━━ JtD-5: RECOMMEND A DISPOSITION ━━━
Evaluate in PRIORITY ORDER — stop at the first matching condition:

  1. watchlist_status.resolution = WATCHLIST_UNRESOLVED → FURTHER_INFO_NEEDED
  2. Pattern LAYERING or MULTI_PATTERN_CONVERGENCE with severity HIGH → ESCALATE_SAR
  3. Pattern STRUCTURING with severity HIGH (≥5 qualifying transactions) → ESCALATE_SAR
  4. Pattern THIN_KYC with kyc_verification_tier=1 and over the $25K limit → ACCOUNT_FREEZE
     (note in reasoning: freeze itself requires analyst → supervisor two-level approval)
  5. Pattern COUNTERPARTY_RISK with severity HIGH (offshore + ≥70%) → ESCALATE_SAR
  6. Pattern STRUCTURING MEDIUM or COUNTERPARTY_RISK MEDIUM → CUSTOMER_RFI
  7. No patterns AND watchlist WATCHLIST_DISCONFIRMED AND no critical data gaps → CLEAR
  8. Both KYC and transaction history unavailable from ALL sources (including network data) → FURTHER_INFO_NEEDED
  9. Default (patterns present but below escalation threshold) → CUSTOMER_RFI

Confidence scoring:
  CLEAR with full data + ≥3 disconfirmation factors: 0.95
  ESCALATE_SAR with HIGH severity pattern: 0.85–0.95
  CUSTOMER_RFI with MEDIUM severity: 0.65–0.80
  FURTHER_INFO_NEEDED (any): 0.50
  Subtract 0.10 for each critical data gap; add gap to uncertainty_flags

Reasoning must name the pattern(s), cite ≥2 specific transaction amounts/dates, and reference watchlist resolution.

━━━ OUTPUT FORMAT ━━━
Return ONLY a valid JSON object matching this schema exactly.
No preamble. No explanation. No markdown fencing. Raw JSON only.

{
  "case_id": "<alert_id value from case data>",
  "customer_id": "<customer_id value>",
  "alert_id": "<alert_id value>",
  "generated_at_utc": "<use the Current UTC timestamp provided in case data>",
  "agent_version": "LACRA-1.0",
  "scope_classification": "IN_SCOPE",
  "sdn_list_version": "<use the SDN list version provided in case data>",
  "alert_status": "OPEN",
  "narrative": "<150–400 word narrative>",
  "patterns_detected": [
    {
      "pattern_type": "STRUCTURING|LAYERING|VELOCITY_ANOMALY|COUNTERPARTY_RISK|THIN_KYC|MULTI_PATTERN_CONVERGENCE",
      "description": "<string>",
      "evidence": ["<specific transaction or hop citation>"],
      "severity": "LOW|MEDIUM|HIGH"
    }
  ],
  "watchlist_status": {
    "hit_present": true|false,
    "resolution": "NO_HIT|WATCHLIST_DISCONFIRMED|WATCHLIST_UNRESOLVED|NO_SCREENING_DATA",
    "disconfirmation_evidence": ["<string>"],
    "confidence": 0.0
  },
  "disposition": {
    "recommendation": "CLEAR|ESCALATE_SAR|CUSTOMER_RFI|ACCOUNT_FREEZE|FURTHER_INFO_NEEDED",
    "reasoning": "<specific evidence citations>",
    "confidence": 0.0,
    "supporting_transactions": ["<transaction identifier>"],
    "uncertainty_flags": ["<string>"]
  },
  "data_gaps": ["<string>"],
  "routing": null,
  "sar_clock_start_utc": null
}
"""


def _detect_scope(
    alert_type_code: str | None, transactions: list | None
) -> tuple[str, str | None]:
    """JtD-1a: deterministic scope detection. Returns (scope, remittance_note).

    AM-01: remittance detection uses substring match, not exact equality.
    AM-11: mixed-case rule — if >50% of transactions are remittance-channel the
    alert is OOS; if only a minority are remittance-channel the customer is
    IN_SCOPE and the remittance transactions are noted in data_gaps.
    """
    if alert_type_code:
        code = alert_type_code.upper()
        if "REMIT" in code:
            return "OUT_OF_SCOPE_REMITTANCE", None
        if any(x in code for x in ("BROKER", "DEALER", "FINRA", "SECURITIES")):
            return "OUT_OF_SCOPE_BROKER_DEALER", None
    if transactions:
        remit_out = [
            tx for tx in transactions
            if "remittance" in tx.get("Channel", "").lower()
            and tx.get("Direction", "").upper() == "OUT"
        ]
        remit_in = [
            tx for tx in transactions
            if "remittance" in tx.get("Channel", "").lower()
            and tx.get("Direction", "").upper() == "IN"
        ]
        # Customer's own outbound remittance transactions → alert is OOS
        if remit_out:
            return "OUT_OF_SCOPE_REMITTANCE", None
        # Only inbound remittance (counterparty used remittance product) → IN_SCOPE with note
        if remit_in:
            n = len(remit_in)
            note = (
                f"{n} inbound remittance-channel transaction(s) present but customer "
                f"is primarily in-scope; those transaction(s) excluded from analysis "
                f"— refer to Cross-Border Remittance Review Team."
            )
            return "IN_SCOPE", note
    return "IN_SCOPE", None


def _fmt_csv(rows: list[dict]) -> str:
    if not rows:
        return "NOT AVAILABLE"
    headers = list(rows[0].keys())
    lines = [",".join(headers)]
    for r in rows:
        lines.append(",".join(str(r.get(h, "")) for h in headers))
    return "\n".join(lines)


def _build_user_prompt(
    alert_id, customer_id, triggered_at_utc, alert_type_code,
    kyc, transactions, watchlist, sdn_extract, network, rfi,
) -> str:
    availability = [
        ("KYC profile", kyc),
        ("Transaction history (90-day CSV)", transactions),
        ("Watchlist screening", watchlist),
        ("OFAC SDN extract", sdn_extract),
        ("Counterparty network data", network),
        ("Prior RFI history", rfi),
    ]
    avail_lines = "\n".join(
        f"  - {label}: {'available' if data is not None else 'NOT AVAILABLE'}"
        for label, data in availability
    )

    network_note = ""
    if network and not kyc and not transactions:
        network_note = (
            "\nNOTE: KYC profile and transaction CSV are absent for this customer. "
            "The network data file contains KYC-equivalent account data and internal "
            "transfer records — use it as the primary source for pattern analysis.\n"
        )

    return f"""CASE DATA FOR PROCESSING:

ALERT METADATA:
  Alert ID: {alert_id}
  Customer ID: {customer_id}
  Triggered at: {triggered_at_utc}
  Alert type code: {alert_type_code or "not provided"}
  Scope: IN_SCOPE
  SDN list version: {SDN_LIST_VERSION}
{network_note}
DATA AVAILABILITY:
{avail_lines}

--- KYC PROFILE ---
{json.dumps(kyc, indent=2) if kyc else "NOT AVAILABLE"}

--- TRANSACTION HISTORY (90-DAY CSV) ---
{_fmt_csv(transactions)}

--- WATCHLIST SCREENING REPORT ---
{watchlist or "NOT AVAILABLE — set watchlist_status.resolution to NO_SCREENING_DATA"}

--- OFAC SDN EXTRACT ---
{sdn_extract or "NOT AVAILABLE"}

--- COUNTERPARTY NETWORK DATA ---
{json.dumps(network, indent=2) if network else "NOT AVAILABLE"}

--- PRIOR RFI HISTORY ---
{rfi or "NOT AVAILABLE"}
"""


def _extract_json(text: str) -> dict:
    """Parse JSON from model output; tolerates markdown fencing."""
    stripped = text.strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", stripped)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    match = re.search(r"\{[\s\S]+\}", stripped)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"Could not extract JSON from model output:\n{text[:400]}")


def _write_audit_log(
    case_package: dict,
    duration_ms: int,
    data_sources_accessed: list[str],
    data_gaps: list[str],
) -> dict:
    """Audit log per spec Section 5.1 + AM-03 (Req 1 enhancements)."""
    patterns_summary = [
        {"pattern_type": p["pattern_type"], "severity": p["severity"]}
        for p in (case_package.get("patterns_detected") or [])
    ]
    return {
        "audit_id": str(uuid.uuid4()),
        "case_id": case_package["case_id"],
        "customer_id": case_package["customer_id"],
        "alert_id": case_package["alert_id"],
        "processed_at_utc": case_package["generated_at_utc"],
        "agent_version": case_package["agent_version"],
        "sdn_list_version": case_package.get("sdn_list_version", SDN_LIST_VERSION),
        "disposition_recommendation": case_package["disposition"]["recommendation"],
        "confidence": case_package["disposition"]["confidence"],
        "processing_duration_ms": duration_ms,
        "data_sources_accessed": data_sources_accessed,
        "data_gaps": data_gaps,
        # AM-03: FIN-2026-A-008 Req 1 fields
        "patterns_detected_summary": patterns_summary,
        "watchlist_resolution": (case_package.get("watchlist_status") or {}).get("resolution"),
        "supporting_transactions": case_package["disposition"].get("supporting_transactions", []),
        # Written null here; case management system updates on analyst sign-off
        "analyst_action": None,
        "analyst_action_timestamp_utc": None,
        "analyst_id": None,
    }


def run_lacra(
    alert_id: str,
    customer_id: str,
    triggered_at_utc: str,
    alert_type_code: str | None = None,
    monetary_scope_usd: float | None = None,
    analyst_queue_tag: str | None = None,
) -> dict:
    """Run LACRA pipeline for one alert. Returns case package dict."""
    t0 = time.time()

    # 1. Input validation
    missing = [f for f, v in [("alert_id", alert_id), ("customer_id", customer_id)] if not v]
    if missing:
        return {"error": "MISSING_REQUIRED_FIELD", "fields": missing}

    # 2. Load primary data (needed for scope detection)
    kyc = read_kyc(customer_id)
    transactions = read_transactions(customer_id)

    # 3. Scope detection — JtD-1a (Python, deterministic)
    scope, remittance_note = _detect_scope(alert_type_code, transactions)

    # 4. Out-of-scope: return routing package immediately, halt pipeline
    if scope != "IN_SCOPE":
        dest = (
            "Cross-Border Remittance Review Team"
            if scope == "OUT_OF_SCOPE_REMITTANCE"
            else "Broker-Dealer Compliance Team"
        )
        reason = (
            "Alert involves Lattice Pay remittance product transactions"
            if scope == "OUT_OF_SCOPE_REMITTANCE"
            else "Alert involves broker-dealer or securities activity (FINRA jurisdiction)"
        )
        return {
            "case_id": alert_id,
            "customer_id": customer_id,
            "alert_id": alert_id,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "agent_version": AGENT_VERSION,
            "scope_classification": scope,
            "sdn_list_version": SDN_LIST_VERSION,
            "alert_status": "OPEN",
            "routing": {"destination": dest, "reason": reason},
            "disposition": {"recommendation": "ROUTE_OUT_OF_SCOPE"},
            "narrative": None,
            "patterns_detected": None,
            "watchlist_status": None,
            "data_gaps": [],
            "sar_clock_start_utc": None,
        }

    # 5. Load remaining data sources — JtD-1b
    watchlist = read_watchlist(customer_id)
    network = read_network(customer_id)
    rfi = read_rfi_history(customer_id)
    sdn_extract = None
    if watchlist:
        sdn_name = parse_sdn_name_from_screening(watchlist)
        if sdn_name:
            sdn_extract = read_sanctions_extract(sdn_name)

    # 6. Track data sources and gaps
    data_sources_accessed: list[str] = []
    data_gaps: list[str] = []
    for label, data, source in [
        ("KYC profile", kyc, f"kyc-profiles/{customer_id}_kyc.json"),
        ("Transaction history", transactions, f"transaction-history/{customer_id}_90day.csv"),
        ("Watchlist screening", watchlist, f"watchlist-screenings/{customer_id}"),
        ("Counterparty network", network, f"counterparty-network/{customer_id}_linked_network.json"),
        ("Prior RFI", rfi, f"customer-rfi-emails/{customer_id}"),
    ]:
        if data is not None:
            data_sources_accessed.append(source)
        else:
            data_gaps.append(f"{label}: not found for {customer_id}")

    # AM-11: note any minority-remittance transactions that were excluded from analysis
    if remittance_note:
        data_gaps.append(remittance_note)

    # 7. Call Claude — single prompt, single API call (ADR-001)
    user_prompt = _build_user_prompt(
        alert_id, customer_id, triggered_at_utc, alert_type_code,
        kyc, transactions, watchlist, sdn_extract, network, rfi,
    )
    client = anthropic.Anthropic()
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = message.content[0].text
    except anthropic.APIError as e:
        # Retry once with 5-second backoff (spec Section 6)
        time.sleep(5)
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                temperature=0,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw = message.content[0].text
        except anthropic.APIError:
            return {
                "error": "AGENT_PROCESSING_FAILURE",
                "case_id": alert_id,
                "retry_recommended": True,
                "detail": str(e),
            }

    # 8. Parse JSON output
    try:
        case_package = _extract_json(raw)
    except (ValueError, json.JSONDecodeError) as e:
        return {
            "error": "AGENT_PROCESSING_FAILURE",
            "case_id": alert_id,
            "retry_recommended": True,
            "detail": str(e),
        }

    # 9. Apply curveball field amendments (AM-04, AM-06)
    case_package.setdefault("sdn_list_version", SDN_LIST_VERSION)
    case_package.setdefault("alert_status", "OPEN")
    rec = (case_package.get("disposition") or {}).get("recommendation", "")
    # AM-06: SAR clock T0 = triggered_at_utc (the alert trigger time, not agent run time)
    case_package["sar_clock_start_utc"] = triggered_at_utc if rec == "ESCALATE_SAR" else None

    # 10. Merge infrastructure-tracked data_gaps with any Claude noted
    claude_gaps = case_package.get("data_gaps") or []
    for gap in data_gaps:
        if gap not in claude_gaps:
            claude_gaps.append(gap)
    case_package["data_gaps"] = claude_gaps

    # 11. Write audit log
    duration_ms = int((time.time() - t0) * 1000)
    case_package["_audit_log"] = _write_audit_log(
        case_package, duration_ms, data_sources_accessed, case_package["data_gaps"]
    )

    return case_package
