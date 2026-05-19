# agent_build/tests/test_email_parser.py
"""
Tests for Contract 6 LLM email parsing and post-parse validation.
NOTE: Example 1 from the spec uses shift_date = 2026-05-15, which is in the past (today = 2026-05-19).
Per Contract 6 post-parse validation, past shift dates are rejected and routed to coordinator queue.
All test fixtures use T+14 from test run date. See signal S-5 in D7 build loop analysis.
"""
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from agent_build.src.email_parser import parse_email, PostParseValidationError

MEDFLEX_STATES = ["IL", "NY", "TX", "CA", "FL"]
TODAY = date(2026, 5, 19)
FUTURE_DATE = (TODAY + timedelta(days=14)).isoformat()  # T+14; replaces spec's hardcoded past dates


def _mock_llm(content: str) -> MagicMock:
    client = MagicMock()
    client.chat.completions.create.return_value.choices[0].message.content = content
    return client


def test_complete_new_request_parses_all_fields():
    # Example 1 adapted: FUTURE_DATE replaces spec's 2026-05-15 (past date — see S-5)
    payload = (
        f'{{"request_type":"NEW_REQUEST","specialty_text":"ICU","shift_date":"{FUTURE_DATE}",'
        '"shift_start_time":"07:00","shift_end_time":"19:00","facility_name":"City General",'
        '"facility_state":"IL","nurse_preference":"Sarah M.","ambiguity_notes":null}}'
    )
    result = parse_email("email body", "2026-05-19T10:00:00Z", _mock_llm(payload), "gpt-4o-mini", MEDFLEX_STATES, TODAY)
    assert result.request_type == "NEW_REQUEST"
    assert result.specialty_text == "ICU"
    assert result.shift_date == FUTURE_DATE
    assert result.shift_start_time == "07:00"
    assert result.shift_end_time == "19:00"
    assert result.facility_state == "IL"
    assert result.nurse_preference == "Sarah M."
    assert result.ambiguity_notes is None


def test_past_shift_date_raises_validation_error():
    payload = (
        '{"request_type":"NEW_REQUEST","specialty_text":"ICU","shift_date":"2026-05-15",'
        '"shift_start_time":"07:00","shift_end_time":"19:00","facility_name":"City General",'
        '"facility_state":"IL","nurse_preference":null,"ambiguity_notes":null}'
    )
    with pytest.raises(PostParseValidationError) as exc_info:
        parse_email("email body", "2026-05-19T10:00:00Z", _mock_llm(payload), "gpt-4o-mini", MEDFLEX_STATES, TODAY)
    assert exc_info.value.reason == "shift_date_in_past"


def test_out_of_network_state_raises_validation_error():
    payload = (
        f'{{"request_type":"NEW_REQUEST","specialty_text":"ICU","shift_date":"{FUTURE_DATE}",'
        '"shift_start_time":"07:00","shift_end_time":"19:00","facility_name":"City General",'
        '"facility_state":"WY","nurse_preference":null,"ambiguity_notes":null}}'
    )
    with pytest.raises(PostParseValidationError) as exc_info:
        parse_email("email body", "2026-05-19T10:00:00Z", _mock_llm(payload), "gpt-4o-mini", MEDFLEX_STATES, TODAY)
    assert exc_info.value.reason == "facility_state_out_of_network"


def test_zero_duration_shift_raises_validation_error():
    payload = (
        f'{{"request_type":"NEW_REQUEST","specialty_text":"ICU","shift_date":"{FUTURE_DATE}",'
        '"shift_start_time":"07:00","shift_end_time":"07:00","facility_name":"City General",'
        '"facility_state":"IL","nurse_preference":null,"ambiguity_notes":null}}'
    )
    with pytest.raises(PostParseValidationError) as exc_info:
        parse_email("email body", "2026-05-19T10:00:00Z", _mock_llm(payload), "gpt-4o-mini", MEDFLEX_STATES, TODAY)
    assert exc_info.value.reason == "invalid_shift_window"


def test_midnight_crossing_shift_is_valid():
    # Night shift default: 23:00–07:00 (next day) per spec system prompt rules
    payload = (
        f'{{"request_type":"NEW_REQUEST","specialty_text":"ICU","shift_date":"{FUTURE_DATE}",'
        '"shift_start_time":"23:00","shift_end_time":"07:00","facility_name":"City General",'
        '"facility_state":"IL","nurse_preference":null,"ambiguity_notes":null}}'
    )
    result = parse_email("email body", "2026-05-19T10:00:00Z", _mock_llm(payload), "gpt-4o-mini", MEDFLEX_STATES, TODAY)
    assert result.shift_start_time == "23:00"
    assert result.shift_end_time == "07:00"


def test_invalid_json_raises_value_error():
    with pytest.raises(ValueError, match="invalid JSON"):
        parse_email("email body", "2026-05-19T10:00:00Z", _mock_llm("not json"), "gpt-4o-mini", MEDFLEX_STATES, TODAY)


def test_missing_required_field_raises_value_error():
    with pytest.raises(ValueError, match="missing required fields"):
        parse_email(
            "email body", "2026-05-19T10:00:00Z",
            _mock_llm('{"request_type":"NEW_REQUEST"}'),
            "gpt-4o-mini", MEDFLEX_STATES, TODAY,
        )
