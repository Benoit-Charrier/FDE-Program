import pytest
from pathlib import Path
from agent_build.src.aurum_ingestion import load_csv, SchemaChangeAlert, CANONICAL_SCHEMAS


def _make_csv(tmp_path: Path, filename: str, headers: list[str], rows: list[list[str]]) -> Path:
    content = ",".join(headers) + "\n"
    for row in rows:
        content += ",".join(row) + "\n"
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return p


def test_load_bill_daily_valid_schema(tmp_path):
    headers = CANONICAL_SCHEMAS["APEX_BILL_DAILY"]
    p = _make_csv(tmp_path, "bill.csv", headers, [
        ["INV-2026-04316", "C-08841", "Travis & Mason Ltd", "2026-04-14",
         "1240.00", "124.50", "272.90", "1637.40", "R-014", "BHM"],
    ])
    records = load_csv("APEX_BILL_DAILY", p)
    assert len(records) == 1
    assert records[0]["INVOICE_NO"] == "INV-2026-04316"
    assert records[0]["AMT_FUEL_SURCH"] == "124.50"
    assert records[0]["CUSTOMER_ID"] == "C-08841"


def test_load_disputes_open_valid_schema(tmp_path):
    headers = CANONICAL_SCHEMAS["APEX_DISPUTES_OPEN"]
    p = _make_csv(tmp_path, "disputes.csv", headers, [
        ["D-2026-00342", "INV-2026-04318", "C-04451", "2026-04-15",
         "FUEL_SURCH_DAMAGE", "340.00", "Sandra W.", "PENDING_CLAIM", "2026-04-15"],
    ])
    records = load_csv("APEX_DISPUTES_OPEN", p)
    assert records[0]["DISPUTE_TYPE"] == "FUEL_SURCH_DAMAGE"
    assert records[0]["CUSTOMER_ID"] == "C-04451"


def test_load_credits_valid_schema(tmp_path):
    headers = CANONICAL_SCHEMAS["APEX_CREDITS"]
    p = _make_csv(tmp_path, "credits.csv", headers, [
        ["CR-2026-00813", "INV-2026-04211", "C-09120", "45.00",
         "FUEL_RECALC", "U-0042", "AUD-2026-00211", "2026-04-13"],
    ])
    records = load_csv("APEX_CREDITS", p)
    assert records[0]["APPROVER_ID"] == "U-0042"
    assert records[0]["REASON_CODE"] == "FUEL_RECALC"


def test_schema_change_extra_column_raises_alert(tmp_path):
    broken = CANONICAL_SCHEMAS["APEX_BILL_DAILY"] + ["EXTRA_COL"]
    p = _make_csv(tmp_path, "broken.csv", broken, [
        ["INV-X", "C-X", "Name", "2026-04-14", "1.00", "1.00", "1.00", "1.00", "R-X", "BHM", "extra"],
    ])
    with pytest.raises(SchemaChangeAlert, match="schema has changed"):
        load_csv("APEX_BILL_DAILY", p)


def test_schema_change_missing_column_raises_alert(tmp_path):
    truncated = CANONICAL_SCHEMAS["APEX_BILL_DAILY"][:-1]  # drop DEPOT
    p = _make_csv(tmp_path, "truncated.csv", truncated, [
        ["INV-X", "C-X", "Name", "2026-04-14", "1.00", "1.00", "1.00", "1.00", "R-X"],
    ])
    with pytest.raises(SchemaChangeAlert):
        load_csv("APEX_BILL_DAILY", p)


def test_unknown_file_type_raises_value_error(tmp_path):
    p = tmp_path / "dummy.csv"
    p.write_text("COL1\nval1\n")
    with pytest.raises(ValueError, match="Unknown Aurum file type"):
        load_csv("APEX_UNKNOWN", p)


def test_empty_file_valid_schema_returns_no_rows(tmp_path):
    headers = CANONICAL_SCHEMAS["APEX_RECON"]
    p = _make_csv(tmp_path, "empty.csv", headers, [])
    records = load_csv("APEX_RECON", p)
    assert records == []


def test_multiple_rows_loaded(tmp_path):
    headers = CANONICAL_SCHEMAS["APEX_DISPUTES_OPEN"]
    p = _make_csv(tmp_path, "multi.csv", headers, [
        ["D-001", "INV-001", "C-001", "2026-04-15", "FUEL_SURCH_DAMAGE", "100.00", "Sandra W.", "PENDING_CLAIM", "2026-04-15"],
        ["D-002", "INV-002", "C-001", "2026-03-28", "DIM_WEIGHT", "50.00", "Tom J.", "AWAITING_CUST", "2026-04-08"],
    ])
    records = load_csv("APEX_DISPUTES_OPEN", p)
    assert len(records) == 2
    assert records[1]["DISPUTE_TYPE"] == "DIM_WEIGHT"
