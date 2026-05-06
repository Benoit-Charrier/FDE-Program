from agent_build.src.audit_scanner import scan_credits, KNOWN_REASON_CODES


# Artefact-derived valid record (APEX_CREDITS_20260414.csv)
VALID_RECORD = {
    "CREDIT_ID": "CR-2026-00813",
    "INVOICE_NO": "INV-2026-04211",
    "CUSTOMER_ID": "C-09120",
    "CREDIT_AMT": "45.00",
    "REASON_CODE": "FUEL_RECALC",
    "APPROVER_ID": "U-0042",
    "AUDIT_REF": "AUD-2026-00211",
    "APPLIED_DT": "2026-04-13",
}


def test_valid_artefact_record_no_violations():
    result = scan_credits([VALID_RECORD])
    assert result.total_records == 1
    assert result.violations == []
    assert result.compliance_rate == 1.0


def test_all_artefact_records_valid():
    records = [
        {**VALID_RECORD, "CREDIT_ID": "CR-2026-00813", "REASON_CODE": "FUEL_RECALC", "APPROVER_ID": "U-0042", "AUDIT_REF": "AUD-2026-00211"},
        {**VALID_RECORD, "CREDIT_ID": "CR-2026-00814", "REASON_CODE": "GOODWILL",    "APPROVER_ID": "U-0089", "AUDIT_REF": "AUD-2026-00212"},
        {**VALID_RECORD, "CREDIT_ID": "CR-2026-00815", "REASON_CODE": "INV_CORR",    "APPROVER_ID": "U-0042", "AUDIT_REF": "AUD-2026-00213"},
        {**VALID_RECORD, "CREDIT_ID": "CR-2026-00816", "REASON_CODE": "GOODWILL",    "APPROVER_ID": "U-0089", "AUDIT_REF": "AUD-2026-00214"},
    ]
    result = scan_credits(records)
    assert result.violations == []
    assert result.compliance_rate == 1.0


def test_null_approver_id_flagged():
    record = {**VALID_RECORD, "APPROVER_ID": ""}
    result = scan_credits([record])
    types = [v.violation_type for v in result.violations]
    assert "NULL_APPROVER_ID" in types


def test_missing_approver_id_key_flagged():
    record = {k: v for k, v in VALID_RECORD.items() if k != "APPROVER_ID"}
    result = scan_credits([record])
    types = [v.violation_type for v in result.violations]
    assert "NULL_APPROVER_ID" in types


def test_system_approver_bdra_flagged():
    """BDRA-SYSTEM-01 is FM-5 — approval gate bypass."""
    record = {**VALID_RECORD, "APPROVER_ID": "BDRA-SYSTEM-01"}
    result = scan_credits([record])
    types = [v.violation_type for v in result.violations]
    assert "SYSTEM_APPROVER_ID" in types


def test_system_approver_auto_flagged():
    record = {**VALID_RECORD, "APPROVER_ID": "AUTO-12345"}
    result = scan_credits([record])
    types = [v.violation_type for v in result.violations]
    assert "SYSTEM_APPROVER_ID" in types


def test_system_approver_case_insensitive():
    record = {**VALID_RECORD, "APPROVER_ID": "bdra-system-99"}
    result = scan_credits([record])
    types = [v.violation_type for v in result.violations]
    assert "SYSTEM_APPROVER_ID" in types


def test_missing_audit_ref_flagged():
    record = {**VALID_RECORD, "AUDIT_REF": ""}
    result = scan_credits([record])
    types = [v.violation_type for v in result.violations]
    assert "MISSING_AUDIT_REF" in types


def test_unknown_reason_code_flagged():
    record = {**VALID_RECORD, "REASON_CODE": "PARTIAL_REFUND"}
    result = scan_credits([record])
    types = [v.violation_type for v in result.violations]
    assert "UNKNOWN_REASON_CODE" in types


def test_empty_reason_code_flagged():
    record = {**VALID_RECORD, "REASON_CODE": ""}
    result = scan_credits([record])
    types = [v.violation_type for v in result.violations]
    assert "UNKNOWN_REASON_CODE" in types


def test_all_three_known_reason_codes_accepted():
    for code in KNOWN_REASON_CODES:
        record = {**VALID_RECORD, "REASON_CODE": code}
        result = scan_credits([record])
        types = [v.violation_type for v in result.violations]
        assert "UNKNOWN_REASON_CODE" not in types, f"Code {code!r} should not be flagged"


def test_empty_scan_full_compliance():
    result = scan_credits([])
    assert result.total_records == 0
    assert result.compliance_rate == 1.0


def test_compliance_rate_one_violation_of_two():
    records = [
        VALID_RECORD,
        {**VALID_RECORD, "CREDIT_ID": "CR-BAD", "APPROVER_ID": ""},
    ]
    result = scan_credits(records)
    assert result.compliance_rate == 0.5


def test_multiple_violations_on_same_record_counted_once_for_rate():
    """A record with both null APPROVER_ID and missing AUDIT_REF is still one non-compliant record."""
    record = {**VALID_RECORD, "CREDIT_ID": "CR-MULTI", "APPROVER_ID": "", "AUDIT_REF": ""}
    result = scan_credits([record])
    assert result.total_records == 1
    assert len(result.violations) == 2  # two violation entries
    assert result.compliance_rate == 0.0  # 0 compliant records out of 1
