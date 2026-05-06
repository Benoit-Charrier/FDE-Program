from datetime import date
from agent_build.src.staleness_checker import is_invoice_stale


def test_same_day_invoice_is_stale():
    """Invoice dated same as batch export is not in the T-1 batch."""
    assert is_invoice_stale(date(2026, 4, 14), date(2026, 4, 14)) is True


def test_future_dated_invoice_is_stale():
    """Invoice dated after batch export is also not in the T-1 batch."""
    assert is_invoice_stale(date(2026, 4, 15), date(2026, 4, 14)) is True


def test_previous_day_invoice_not_stale():
    """Invoice dated one day before batch export is in the T-1 batch."""
    assert is_invoice_stale(date(2026, 4, 13), date(2026, 4, 14)) is False


def test_two_days_old_not_stale():
    """Invoice clearly in prior batch — not stale."""
    assert is_invoice_stale(date(2026, 4, 12), date(2026, 4, 14)) is False


def test_week_old_invoice_not_stale():
    assert is_invoice_stale(date(2026, 4, 7), date(2026, 4, 14)) is False


def test_artefact_case_invoice_not_stale():
    """INV-2026-04318 dated 2026-04-14; batch export also 2026-04-14 → stale (same day)."""
    assert is_invoice_stale(date(2026, 4, 14), date(2026, 4, 14)) is True
