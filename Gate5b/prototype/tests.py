"""LACRA test suite — T1 through T13.

T1–T5:  Required build paths (primary flow, SAR escalation, OOS routing,
        missing-data graceful degradation, reproducibility).
T6–T8:  Synthetic-data disposition paths (ACCOUNT_FREEZE, CUSTOMER_RFI,
        WATCHLIST_UNRESOLVED) using unittest.mock.patch.
T9–T13: Full real mock-data cases — all 5 untested customers from the queue
        (C-CON-7714290, C-CON-3318822, C-CON-2207715, C-BIZ-4408821, C-CON-7720338).

Run with: pytest prototype/tests.py -v
"""
import pytest
from unittest.mock import patch
from prototype.agent import run_lacra


# ── T1: Primary flow — watchlist false-positive → CLEAR ─────────────────────

def test_t1_watchlist_fp_clear():
    """AML-1208: Mohammed Khan (DOB 1993) matches SDN KHAN Muhammad (DOB 1972).
    DOB delta 21 years + address + nationality + transaction coherence = WATCHLIST_DISCONFIRMED → CLEAR."""
    result = run_lacra(
        alert_id="CASE-2026-05-13-AML-1208",
        customer_id="C-CON-9923441",
        triggered_at_utc="2026-05-13T09:38:00Z",
    )

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["scope_classification"] == "IN_SCOPE"

    ws = result["watchlist_status"]
    assert ws["hit_present"] is True
    assert ws["resolution"] == "WATCHLIST_DISCONFIRMED", (
        f"Expected WATCHLIST_DISCONFIRMED, got {ws['resolution']}"
    )
    assert ws["confidence"] >= 0.9, f"Confidence too low: {ws['confidence']}"
    assert len(ws.get("disconfirmation_evidence", [])) >= 3, (
        "Expected ≥3 disconfirmation evidence items"
    )

    disp = result["disposition"]
    assert disp["recommendation"] == "CLEAR", (
        f"Expected CLEAR, got {disp['recommendation']}"
    )
    assert disp["confidence"] >= 0.85

    narrative = result.get("narrative", "")
    assert len(narrative) >= 150, "Narrative too short"
    assert result.get("sar_clock_start_utc") is None


# ── T2: Failure-mode escalation — layering → ESCALATE_SAR ───────────────────

def test_t2_layering_escalate_sar():
    """AML-1408: 4 linked accounts (shared device dev-android-7011), funds hop to
    Eastside FCU → Tyrone Ostrander Personal. LAYERING HIGH → ESCALATE_SAR."""
    result = run_lacra(
        alert_id="CASE-2026-05-15-AML-1408",
        customer_id="C-CON-6611442",
        triggered_at_utc="2026-05-15T02:55:00Z",
    )

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["scope_classification"] == "IN_SCOPE"

    patterns = result.get("patterns_detected") or []
    pattern_types = [p["pattern_type"] for p in patterns]
    assert "LAYERING" in pattern_types, f"LAYERING not detected; patterns: {pattern_types}"

    layering = next(p for p in patterns if p["pattern_type"] == "LAYERING")
    assert layering["severity"] == "HIGH"
    assert len(layering.get("evidence", [])) >= 1, "LAYERING pattern has no evidence"

    disp = result["disposition"]
    assert disp["recommendation"] == "ESCALATE_SAR", (
        f"Expected ESCALATE_SAR, got {disp['recommendation']}"
    )
    # Base 0.85–0.95 for ESCALATE_SAR, minus 0.10 per critical data gap.
    # C-CON-6611442 has 2 critical gaps (KYC + tx CSV both absent) → floor ~0.75.
    assert disp["confidence"] >= 0.70

    # Graceful degradation: KYC and transaction CSV absent for C-CON-6611442
    gaps = result.get("data_gaps", [])
    assert any("KYC" in g or "Transaction" in g or "6611442" in g for g in gaps), (
        f"Expected data gaps for missing KYC/transactions, got: {gaps}"
    )

    # AM-06: SAR clock start must be set
    assert result.get("sar_clock_start_utc") is not None, "sar_clock_start_utc must be set for ESCALATE_SAR"


# ── T3: Edge case — OOS remittance routing ───────────────────────────────────

def test_t3_oos_routing():
    """AML-1322: C-CON-5530118 transaction CSV has channel=cross-border-remittance.
    Scope detection (substring match AM-01) classifies as OUT_OF_SCOPE_REMITTANCE.
    Pipeline halts; no narrative or pattern analysis produced."""
    result = run_lacra(
        alert_id="CASE-2026-05-14-AML-1322",
        customer_id="C-CON-5530118",
        triggered_at_utc="2026-05-14T18:08:00Z",
    )

    assert result["scope_classification"] == "OUT_OF_SCOPE_REMITTANCE", (
        f"Expected OUT_OF_SCOPE_REMITTANCE, got {result['scope_classification']}"
    )
    assert result["disposition"]["recommendation"] == "ROUTE_OUT_OF_SCOPE"

    routing = result.get("routing")
    assert routing is not None, "routing field must be present for OOS case"
    assert "remittance" in (routing.get("destination", "") + routing.get("reason", "")).lower()

    # Pipeline halted: no analysis produced
    assert result.get("narrative") is None
    assert result.get("patterns_detected") is None
    assert result.get("sar_clock_start_utc") is None


# ── T4: Edge case — missing data graceful degradation ───────────────────────

def test_t4_missing_data():
    """Synthetic customer C-CON-0000001 has no mock data files.
    Both KYC and transaction history absent → FURTHER_INFO_NEEDED.
    Agent must not crash; data_gaps must be populated."""
    result = run_lacra(
        alert_id="CASE-TEST-MISSING-DATA",
        customer_id="C-CON-0000001",
        triggered_at_utc="2026-05-15T00:00:00Z",
    )

    assert "error" not in result, f"Agent crashed: {result.get('error')}"
    assert result["disposition"]["recommendation"] == "FURTHER_INFO_NEEDED", (
        f"Expected FURTHER_INFO_NEEDED, got {result['disposition']['recommendation']}"
    )
    gaps = result.get("data_gaps", [])
    assert len(gaps) >= 2, f"Expected ≥2 data gaps, got: {gaps}"


# ── T5: Reproducibility ──────────────────────────────────────────────────────

def test_t5_reproducibility():
    """Same inputs must yield identical outputs on re-run (temperature=0).
    Only generated_at_utc, sar_clock_start_utc, and _audit_log are excluded from comparison."""
    kwargs = dict(
        alert_id="CASE-2026-05-13-AML-1208",
        customer_id="C-CON-9923441",
        triggered_at_utc="2026-05-13T09:38:00Z",
    )
    r1 = run_lacra(**kwargs)
    r2 = run_lacra(**kwargs)

    def key_fields(d: dict) -> dict:
        return {
            "scope_classification": d.get("scope_classification"),
            "disposition_recommendation": d.get("disposition", {}).get("recommendation"),
            "watchlist_resolution": (d.get("watchlist_status") or {}).get("resolution"),
            "pattern_types": sorted([p["pattern_type"] for p in (d.get("patterns_detected") or [])]),
            "pattern_severities": {
                p["pattern_type"]: p["severity"] for p in (d.get("patterns_detected") or [])
            },
        }

    assert key_fields(r1) == key_fields(r2), (
        "Reproducibility failure: decision fields differ between runs.\n"
        f"Run 1: {key_fields(r1)}\n"
        f"Run 2: {key_fields(r2)}"
    )


# ── T6: ACCOUNT_FREEZE — thin-KYC tier-1 aggregate breach ───────────────────

def test_t6_account_freeze():
    """Synthetic C-TEST-T6-FREEZE: kyc_verification_tier=1, 7 × $3,800 deposits
    in 30 days (total $26,600 > $25K limit). Amounts below $4K floor → no STRUCTURING.
    THIN_KYC HIGH fires at JtD-5 priority 4 → ACCOUNT_FREEZE."""
    synthetic_kyc = {
        "customer_id": "C-TEST-T6-FREEZE",
        "full_name": "Sandra Okonkwo",
        "kyc_verification_tier": 1,
        "tier1_aggregate_inbound_limit_30d": 25000,
        "date_of_birth": "1995-04-12",
        "nationality": "US",
        "address": {"city": "Detroit", "state": "MI", "country": "US"},
        "account_open_date": "2026-01-15",
        "stated_occupation": "Student",
        "funding_sources": ["peer transfers"],
    }
    synthetic_txns = [
        {
            "Transaction_ID": f"TX-T6-{i:03d}",
            "Date": f"2026-05-{d:02d}",
            "Amount_USD": "3800.00",
            "Direction": "IN",
            "Channel": "cashapp",
            "Counterparty": f"PEER-{i:03d}",
            "Type": "TRANSFER",
        }
        for i, d in enumerate([1, 3, 5, 7, 9, 11, 13], start=1)
    ]

    with patch("prototype.agent.read_kyc", return_value=synthetic_kyc), \
         patch("prototype.agent.read_transactions", return_value=synthetic_txns), \
         patch("prototype.agent.read_watchlist", return_value=None), \
         patch("prototype.agent.read_network", return_value=None), \
         patch("prototype.agent.read_rfi_history", return_value=None):
        result = run_lacra(
            alert_id="CASE-TEST-T6-FREEZE",
            customer_id="C-TEST-T6-FREEZE",
            triggered_at_utc="2026-05-20T10:00:00Z",
        )

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["scope_classification"] == "IN_SCOPE"

    patterns = result.get("patterns_detected") or []
    pattern_types = [p["pattern_type"] for p in patterns]
    assert "THIN_KYC" in pattern_types, f"THIN_KYC not detected; patterns: {pattern_types}"

    thin = next(p for p in patterns if p["pattern_type"] == "THIN_KYC")
    assert thin["severity"] == "HIGH"

    disp = result["disposition"]
    assert disp["recommendation"] == "ACCOUNT_FREEZE", (
        f"Expected ACCOUNT_FREEZE, got {disp['recommendation']}"
    )
    assert disp["confidence"] >= 0.50
    reasoning = disp.get("reasoning", "").lower()
    assert any(
        kw in reasoning for kw in ("thin", "kyc", "tier", "25000", "25,000", "limit", "aggregate")
    ), f"Reasoning should mention thin KYC limit: {reasoning[:200]}"


# ── T7: CUSTOMER_RFI — structuring MEDIUM ────────────────────────────────────

def test_t7_customer_rfi():
    """Synthetic C-TEST-T7-RFI: tier-2 KYC, 3 deposits in [$4,700–$4,900]
    within a 7-day window (May 5–12), sum $14,400 > $10K → STRUCTURING MEDIUM (count 3–4).
    JtD-5 priority 6 → CUSTOMER_RFI."""
    synthetic_kyc = {
        "customer_id": "C-TEST-T7-RFI",
        "full_name": "Marcus Tillman",
        "kyc_verification_tier": 2,
        "date_of_birth": "1988-07-22",
        "nationality": "US",
        "address": {"city": "Charlotte", "state": "NC", "country": "US"},
        "account_open_date": "2025-08-10",
        "stated_occupation": "Sales Associate",
        "funding_sources": ["payroll", "peer transfers"],
    }
    synthetic_txns = [
        # Regular payroll — not in structuring range
        {"Transaction_ID": "TX-T7-000", "Date": "2026-05-03", "Amount_USD": "1200.00",
         "Direction": "IN", "Channel": "direct-deposit", "Counterparty": "EMPLOYER-T7", "Type": "PAYROLL"},
        # 3 near-threshold deposits in [$4K-$5K] within 10-day window → STRUCTURING MEDIUM
        {"Transaction_ID": "TX-T7-001", "Date": "2026-05-05", "Amount_USD": "4800.00",
         "Direction": "IN", "Channel": "ach", "Counterparty": "PEER-T7-A", "Type": "TRANSFER"},
        {"Transaction_ID": "TX-T7-002", "Date": "2026-05-10", "Amount_USD": "4900.00",
         "Direction": "IN", "Channel": "ach", "Counterparty": "PEER-T7-B", "Type": "TRANSFER"},
        {"Transaction_ID": "TX-T7-003", "Date": "2026-05-12", "Amount_USD": "4700.00",
         "Direction": "IN", "Channel": "ach", "Counterparty": "PEER-T7-C", "Type": "TRANSFER"},
    ]

    with patch("prototype.agent.read_kyc", return_value=synthetic_kyc), \
         patch("prototype.agent.read_transactions", return_value=synthetic_txns), \
         patch("prototype.agent.read_watchlist", return_value=None), \
         patch("prototype.agent.read_network", return_value=None), \
         patch("prototype.agent.read_rfi_history", return_value=None):
        result = run_lacra(
            alert_id="CASE-TEST-T7-RFI",
            customer_id="C-TEST-T7-RFI",
            triggered_at_utc="2026-05-15T12:00:00Z",
        )

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["scope_classification"] == "IN_SCOPE"

    patterns = result.get("patterns_detected") or []
    pattern_types = [p["pattern_type"] for p in patterns]
    assert "STRUCTURING" in pattern_types, f"STRUCTURING not detected; patterns: {pattern_types}"

    structuring = next(p for p in patterns if p["pattern_type"] == "STRUCTURING")
    assert structuring["severity"] == "MEDIUM", (
        f"Expected MEDIUM severity, got {structuring['severity']}"
    )

    disp = result["disposition"]
    assert disp["recommendation"] == "CUSTOMER_RFI", (
        f"Expected CUSTOMER_RFI, got {disp['recommendation']}"
    )
    assert disp["confidence"] >= 0.50


# ── T8: WATCHLIST_UNRESOLVED — 1 disconfirmation factor ─────────────────────

def test_t8_watchlist_unresolved():
    """Synthetic C-TEST-T8-UNRESOLVED: SDN hit on GARCIA, Roberto.
    DOB delta only ~2y 3mo (< 5-year threshold) → no DOB factor.
    Address and nationality both match SDN entry → no address or nationality factor.
    Transaction coherence (restaurant server, small payroll) = 1 factor total.
    1 factor → WATCHLIST_UNRESOLVED (JtD-4) → FURTHER_INFO_NEEDED (JtD-5 priority 1)."""
    synthetic_kyc = {
        "customer_id": "C-TEST-T8-UNRESOLVED",
        "full_name": "Roberto Garcia",
        "kyc_verification_tier": 2,
        "date_of_birth": "1987-03-15",
        "nationality": "Mexican",
        "address": {"city": "Mexico City", "state": "CDMX", "country": "Mexico"},
        "account_open_date": "2026-02-01",
        "stated_occupation": "Restaurant Server",
        "funding_sources": ["payroll"],
    }
    synthetic_txns = [
        {"Transaction_ID": "TX-T8-001", "Date": "2026-05-01", "Amount_USD": "450.00",
         "Direction": "IN", "Channel": "direct-deposit", "Counterparty": "TAQUERIA-MX", "Type": "PAYROLL"},
        {"Transaction_ID": "TX-T8-002", "Date": "2026-05-08", "Amount_USD": "320.00",
         "Direction": "OUT", "Channel": "debit", "Counterparty": "GROCERY-001", "Type": "PURCHASE"},
        {"Transaction_ID": "TX-T8-003", "Date": "2026-05-15", "Amount_USD": "460.00",
         "Direction": "IN", "Channel": "direct-deposit", "Counterparty": "TAQUERIA-MX", "Type": "PAYROLL"},
    ]
    # Screening report contains a hit; parse_sdn_name_from_screening extracts "GARCIA, Roberto"
    synthetic_screening = (
        "LACRA Watchlist Screening Report\n"
        "Customer ID: C-TEST-T8-UNRESOLVED\n"
        "Screening Date: 2026-05-16\n"
        "Result: HIT\n"
        'SDN List Entry: "GARCIA, Roberto"\n'
        "Match Score: 0.74\n"
        "Match Basis: Name + Nationality\n"
    )
    # SDN DOB 1989-06-20 → delta ~2y 3mo from customer DOB 1987-03-15 (below 5-year threshold)
    # Address and nationality identical to customer → both non-factors
    synthetic_sdn = (
        "OFAC SDN List — Consolidated Sanctions List Extract\n"
        "Entry Name: GARCIA, Roberto\n"
        "Date of Birth: 20 Jun 1989\n"
        "Nationality: Mexican\n"
        "Last Known Address: Mexico City, CDMX, Mexico\n"
        "Programs: SDGT\n"
        "Remarks: Designated for sanctions-related activity.\n"
    )

    with patch("prototype.agent.read_kyc", return_value=synthetic_kyc), \
         patch("prototype.agent.read_transactions", return_value=synthetic_txns), \
         patch("prototype.agent.read_watchlist", return_value=synthetic_screening), \
         patch("prototype.agent.read_sanctions_extract", return_value=synthetic_sdn), \
         patch("prototype.agent.read_network", return_value=None), \
         patch("prototype.agent.read_rfi_history", return_value=None):
        result = run_lacra(
            alert_id="CASE-TEST-T8-UNRESOLVED",
            customer_id="C-TEST-T8-UNRESOLVED",
            triggered_at_utc="2026-05-16T09:00:00Z",
        )

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["scope_classification"] == "IN_SCOPE"

    ws = result.get("watchlist_status")
    assert ws is not None, "watchlist_status must be present"
    assert ws["hit_present"] is True
    assert ws["resolution"] == "WATCHLIST_UNRESOLVED", (
        f"Expected WATCHLIST_UNRESOLVED, got {ws['resolution']}"
    )

    disp = result["disposition"]
    assert disp["recommendation"] == "FURTHER_INFO_NEEDED", (
        f"Expected FURTHER_INFO_NEEDED (WATCHLIST_UNRESOLVED → priority 1), "
        f"got {disp['recommendation']}"
    )
    assert result.get("sar_clock_start_utc") is None


# ══════════════════════════════════════════════════════════════════════════════
# T9–T13: Full mock-data cases — all 5 untested real customers from the queue
# ══════════════════════════════════════════════════════════════════════════════

# ── T9: Real mock — structuring HIGH, owner-operator trucking → ESCALATE_SAR ─

def test_t9_structuring_high_trucking():
    """AML-1109: C-CON-7714290 Reuben Tate, owner-operator trucker.
    7 cash deposits ($4,810–$4,940) over 6-day window May 6–12 → STRUCTURING HIGH.
    Prior 2024 no-SAR disposition on same pattern is in KYC; agent must still flag.
    No watchlist screening file → NO_SCREENING_DATA.
    STRUCTURING HIGH at JtD-5 priority 3 → ESCALATE_SAR."""
    result = run_lacra(
        alert_id="CASE-2026-05-12-AML-1109",
        customer_id="C-CON-7714290",
        triggered_at_utc="2026-05-12T03:14:00Z",
    )

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["scope_classification"] == "IN_SCOPE"

    patterns = result.get("patterns_detected") or []
    pattern_types = [p["pattern_type"] for p in patterns]
    assert "STRUCTURING" in pattern_types, (
        f"STRUCTURING not detected; patterns: {pattern_types}"
    )

    structuring = next(p for p in patterns if p["pattern_type"] == "STRUCTURING")
    assert structuring["severity"] == "HIGH", (
        f"Expected HIGH (7 qualifying transactions), got {structuring['severity']}"
    )

    disp = result["disposition"]
    assert disp["recommendation"] == "ESCALATE_SAR", (
        f"Expected ESCALATE_SAR, got {disp['recommendation']}"
    )
    assert disp["confidence"] >= 0.75
    assert result.get("sar_clock_start_utc") is not None, (
        "sar_clock_start_utc must be set for ESCALATE_SAR"
    )

    ws = result.get("watchlist_status") or {}
    assert ws.get("resolution") == "NO_SCREENING_DATA", (
        f"No screening file for C-CON-7714290; expected NO_SCREENING_DATA, "
        f"got {ws.get('resolution')}"
    )


# ── T10: Real mock — counterparty risk, vape shop, prior RFI → CUSTOMER_RFI ─

def test_t10_counterparty_risk_customer_rfi():
    """AML-1117: C-CON-3318822 Brendan Killeen, bar manager.
    4 P2P transfers to Stonebridge Premier LLC (elevated-risk merchant per alert trigger),
    92% outbound concentration. Prior RFI thread explains Stonebridge = online vape shop.
    Amounts below $4K floor → no STRUCTURING. No watchlist screening file.
    Pattern detection marginal (counterparty risk signal, not offshore) → CUSTOMER_RFI."""
    result = run_lacra(
        alert_id="CASE-2026-05-12-AML-1117",
        customer_id="C-CON-3318822",
        triggered_at_utc="2026-05-12T11:02:00Z",
    )

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["scope_classification"] == "IN_SCOPE"

    # Amounts are all below $4K structuring floor — STRUCTURING must not fire
    patterns = result.get("patterns_detected") or []
    pattern_types = [p["pattern_type"] for p in patterns]
    assert "STRUCTURING" not in pattern_types, (
        f"STRUCTURING should not fire (all amounts < $4K): {pattern_types}"
    )

    disp = result["disposition"]
    assert disp["recommendation"] == "CUSTOMER_RFI", (
        f"Expected CUSTOMER_RFI (counterparty signal + prior RFI), "
        f"got {disp['recommendation']}"
    )
    assert disp["confidence"] >= 0.50
    assert result.get("sar_clock_start_utc") is None


# ── T11: Real mock — watchlist FP Gonzalez/Alava, Tampa nurse → CLEAR ────────

def test_t11_watchlist_fp_gonzalez_clear():
    """AML-1219: C-CON-2207715 Maria Gonzalez, registered nurse Tampa FL.
    SDN hit on GONZALEZ-ALAVA Maria de los Angeles (Venezuelan, Caracas).
    DOB delta 17 months (< 5yr threshold - no DOB factor), but address (Tampa vs Caracas)
    + nationality (US vs Venezuelan) + transaction coherence = 3+ factors
    -> WATCHLIST_DISCONFIRMED confidence >=0.90 -> CLEAR.
    Distinct from T1 (Mohammed Khan): different SDN entity, different disconfirmation pattern."""
    result = run_lacra(
        alert_id="CASE-2026-05-13-AML-1219",
        customer_id="C-CON-2207715",
        triggered_at_utc="2026-05-13T15:55:00Z",
    )

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["scope_classification"] == "IN_SCOPE"

    patterns = result.get("patterns_detected") or []
    assert patterns == [] or all(
        p["pattern_type"] == "MULTI_PATTERN_CONVERGENCE" for p in patterns
    ), f"No AML patterns expected for normal nurse transactions; got: {patterns}"

    ws = result.get("watchlist_status")
    assert ws is not None, "watchlist_status must be present"
    assert ws["hit_present"] is True
    assert ws["resolution"] == "WATCHLIST_DISCONFIRMED", (
        f"Expected WATCHLIST_DISCONFIRMED (address + nationality + coherence), "
        f"got {ws['resolution']}"
    )
    assert ws["confidence"] >= 0.90, f"Confidence too low: {ws['confidence']}"
    assert len(ws.get("disconfirmation_evidence") or []) >= 2

    disp = result["disposition"]
    assert disp["recommendation"] == "CLEAR", (
        f"Expected CLEAR, got {disp['recommendation']}"
    )
    assert disp["confidence"] >= 0.80
    assert result.get("sar_clock_start_utc") is None


# ── T12: Real mock — Cayman wire-outs, offshore counterparty → ESCALATE_SAR ──

def test_t12_counterparty_high_offshore_sar():
    """AML-1304: C-BIZ-4408821 Calloway Custom Carpentry LLC.
    High-velocity merchant inflows immediately wired to Cayman National Bank -
    100% of outbound to offshore Cayman account -> COUNTERPARTY_RISK HIGH.
    Clean watchlist screening (NO_HIT). Delaware shell, Nassau IP sessions.
    COUNTERPARTY_RISK HIGH at JtD-5 priority 5 -> ESCALATE_SAR."""
    result = run_lacra(
        alert_id="CASE-2026-05-14-AML-1304",
        customer_id="C-BIZ-4408821",
        triggered_at_utc="2026-05-14T04:21:00Z",
    )

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["scope_classification"] == "IN_SCOPE"

    patterns = result.get("patterns_detected") or []
    pattern_types = [p["pattern_type"] for p in patterns]
    assert "COUNTERPARTY_RISK" in pattern_types, (
        f"COUNTERPARTY_RISK not detected for 100% Cayman wire-outs; "
        f"patterns: {pattern_types}"
    )

    cp = next(p for p in patterns if p["pattern_type"] == "COUNTERPARTY_RISK")
    assert cp["severity"] == "HIGH", (
        f"Expected HIGH (offshore Cayman + >=70% concentration), got {cp['severity']}"
    )

    ws = result.get("watchlist_status") or {}
    assert ws.get("resolution") in ("NO_HIT", "NO_SCREENING_DATA"), (
        f"Screening was clean; expected NO_HIT or NO_SCREENING_DATA, "
        f"got {ws.get('resolution')}"
    )

    disp = result["disposition"]
    assert disp["recommendation"] == "ESCALATE_SAR", (
        f"Expected ESCALATE_SAR (COUNTERPARTY_RISK HIGH offshore), "
        f"got {disp['recommendation']}"
    )
    assert disp["confidence"] >= 0.80
    assert result.get("sar_clock_start_utc") is not None, (
        "sar_clock_start_utc must be set for ESCALATE_SAR"
    )


# ── T13: Real mock — thin KYC + structuring HIGH, multi-pattern → ESCALATE_SAR

def test_t13_thin_kyc_structuring_mpc_sar():
    """AML-1419: C-CON-7720338 Devonte Asher, tier-1 KYC (no address, no SSN, ID unverified).
    6 inbound transactions in [$4K-$9K] within 10-day window May 4-13 -> STRUCTURING HIGH.
    Tier-1 + 30-day aggregate well over $25K limit -> THIN_KYC HIGH.
    Both HIGH patterns -> MULTI_PATTERN_CONVERGENCE HIGH.
    MPC HIGH at JtD-5 priority 2 -> ESCALATE_SAR (before THIN_KYC at priority 4)."""
    result = run_lacra(
        alert_id="CASE-2026-05-15-AML-1419",
        customer_id="C-CON-7720338",
        triggered_at_utc="2026-05-15T14:32:00Z",
    )

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["scope_classification"] == "IN_SCOPE"

    patterns = result.get("patterns_detected") or []
    pattern_types = [p["pattern_type"] for p in patterns]

    assert "STRUCTURING" in pattern_types, (
        f"STRUCTURING not detected (6 transactions in [$4K-$9K] in 10-day window); "
        f"patterns: {pattern_types}"
    )
    assert "THIN_KYC" in pattern_types, (
        f"THIN_KYC not detected (tier-1 KYC, $61K+ inbound in 60d); "
        f"patterns: {pattern_types}"
    )
    assert "MULTI_PATTERN_CONVERGENCE" in pattern_types, (
        f"MPC expected when >=2 HIGH patterns co-occur; patterns: {pattern_types}"
    )

    structuring = next(p for p in patterns if p["pattern_type"] == "STRUCTURING")
    thin = next(p for p in patterns if p["pattern_type"] == "THIN_KYC")
    mpc = next(p for p in patterns if p["pattern_type"] == "MULTI_PATTERN_CONVERGENCE")
    assert structuring["severity"] == "HIGH"
    assert thin["severity"] == "HIGH"
    assert mpc["severity"] == "HIGH", (
        f"MPC severity should inherit HIGH from constituents, got {mpc['severity']}"
    )

    disp = result["disposition"]
    assert disp["recommendation"] == "ESCALATE_SAR", (
        f"Expected ESCALATE_SAR (MPC HIGH at priority 2), got {disp['recommendation']}"
    )
    assert disp["confidence"] >= 0.75
    assert result.get("sar_clock_start_utc") is not None, (
        "sar_clock_start_utc must be set for ESCALATE_SAR"
    )
