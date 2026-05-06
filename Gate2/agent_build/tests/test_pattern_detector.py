from agent_build.src.pattern_detector import detect_repeat_pattern, DisputeRecord


# Artefact-derived test data (APEX_DISPUTES_OPEN_20260414.csv)
ARTEFACT_DISPUTES = [
    DisputeRecord("D-2026-00342", "C-04451", "FUEL_SURCH_DAMAGE", "PENDING_CLAIM"),  # Hayes & Sons
    DisputeRecord("D-2026-00339", "C-08213", "DIM_WEIGHT",         "AWAITING_CUST"),  # Aldgate
    DisputeRecord("D-2026-00337", "C-04451", "REDELIVERY_FEE",     "AWAITING_CUST"),  # Hayes & Sons
    DisputeRecord("D-2026-00328", "C-09120", "FUEL_SURCH_DAMAGE",  "PENDING_CLAIM"),  # Northstar
    DisputeRecord("D-2026-00318", "C-04451", "FUEL_SURCH_DAMAGE",  "PENDING_CLAIM"),  # Hayes & Sons
    DisputeRecord("D-2026-00301", "C-08841", "DIM_WEIGHT",         "RESOLVED"),       # Travis - resolved
]


def test_hayes_sons_fuel_surch_repeat_detected():
    """C-04451 has 2 open FUEL_SURCH_DAMAGE disputes — ET-005 must trigger."""
    result = detect_repeat_pattern("C-04451", "FUEL_SURCH_DAMAGE", ARTEFACT_DISPUTES)
    assert result.has_repeat_pattern is True
    assert result.repeat_count == 2


def test_hayes_sons_matching_disputes_returned():
    result = detect_repeat_pattern("C-04451", "FUEL_SURCH_DAMAGE", ARTEFACT_DISPUTES)
    ids = {d.dispute_id for d in result.matching_disputes}
    assert ids == {"D-2026-00342", "D-2026-00318"}


def test_hayes_sons_redelivery_fee_no_repeat():
    """C-04451 has only 1 open REDELIVERY_FEE dispute — no pattern."""
    result = detect_repeat_pattern("C-04451", "REDELIVERY_FEE", ARTEFACT_DISPUTES)
    assert result.has_repeat_pattern is False
    assert result.repeat_count == 1


def test_different_customer_no_pattern():
    """C-09120 has only 1 FUEL_SURCH_DAMAGE dispute — no pattern."""
    result = detect_repeat_pattern("C-09120", "FUEL_SURCH_DAMAGE", ARTEFACT_DISPUTES)
    assert result.has_repeat_pattern is False
    assert result.repeat_count == 1


def test_unknown_customer_no_pattern():
    result = detect_repeat_pattern("C-99999", "FUEL_SURCH_DAMAGE", ARTEFACT_DISPUTES)
    assert result.has_repeat_pattern is False
    assert result.repeat_count == 0


def test_resolved_disputes_excluded():
    """RESOLVED disputes must not count toward the ≥2 threshold."""
    result = detect_repeat_pattern("C-08841", "DIM_WEIGHT", ARTEFACT_DISPUTES)
    assert result.repeat_count == 0  # only 1 record and it's RESOLVED


def test_resolved_plus_open_counts_only_open():
    disputes = ARTEFACT_DISPUTES + [
        DisputeRecord("D-OLD", "C-04451", "FUEL_SURCH_DAMAGE", "RESOLVED"),
    ]
    result = detect_repeat_pattern("C-04451", "FUEL_SURCH_DAMAGE", disputes)
    # 2 open + 1 resolved = still only 2 open
    assert result.repeat_count == 2


def test_empty_disputes_no_pattern():
    result = detect_repeat_pattern("C-04451", "FUEL_SURCH_DAMAGE", [])
    assert result.has_repeat_pattern is False
    assert result.repeat_count == 0


def test_awaiting_cust_counts_as_open():
    """AWAITING_CUST is an open status and must count toward the threshold."""
    disputes = [
        DisputeRecord("D-001", "C-X", "DIM_WEIGHT", "AWAITING_CUST"),
        DisputeRecord("D-002", "C-X", "DIM_WEIGHT", "AWAITING_CUST"),
    ]
    result = detect_repeat_pattern("C-X", "DIM_WEIGHT", disputes)
    assert result.has_repeat_pattern is True
