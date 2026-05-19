# agent_build/src/email_parser.py
"""
Contract 6 — LLM email parsing.
System prompt is exact per spec; do not modify without re-testing (spec instruction).
Post-parse validation runs after every successful LLM parse — WS4 owns this, not the LLM.
Q-3: MEDFLEX_OPERATING_STATES list is not defined in the spec; passed as parameter pending confirmation.
"""
import json
from dataclasses import dataclass
from datetime import date
from typing import Optional

import openai

# Exact system prompt per spec — do not modify without re-testing
SYSTEM_PROMPT = """You are an intake parser for a healthcare staffing agency. Extract structured fields from the hospital email below.

Return a JSON object with exactly these fields. Use null for any field you cannot extract with confidence.

{
  "request_type": "NEW_REQUEST" | "CANCELLATION" | "MODIFICATION" | "AMBIGUOUS",
  "specialty_text": string | null,
  "shift_date": "YYYY-MM-DD" | null,
  "shift_start_time": "HH:MM" | null,
  "shift_end_time": "HH:MM" | null,
  "facility_name": string | null,
  "facility_state": "XX" | null,
  "nurse_preference": string | null,
  "ambiguity_notes": string | null
}

Rules:
- received_at date is provided in the user message as ISO 8601 UTC. Resolve "today", "tomorrow", "next Tuesday" relative to this date.
- "Morning shift" = 07:00–15:00; "afternoon shift" = 15:00–23:00; "night shift" = 23:00–07:00 (next day). Use these defaults only if no explicit times are given.
- If the email is ambiguous between request types, set request_type to AMBIGUOUS and explain in ambiguity_notes.
- Never include patient names, case numbers, or clinical details in any field.
- Return only the JSON object — no commentary."""

REQUIRED_FIELDS = frozenset({
    "request_type", "specialty_text", "shift_date", "shift_start_time",
    "shift_end_time", "facility_name", "facility_state", "nurse_preference",
    "ambiguity_notes",
})

VALID_REQUEST_TYPES = frozenset({"NEW_REQUEST", "CANCELLATION", "MODIFICATION", "AMBIGUOUS"})


@dataclass
class ParseResult:
    request_type: str
    specialty_text: Optional[str]
    shift_date: Optional[str]
    shift_start_time: Optional[str]
    shift_end_time: Optional[str]
    facility_name: Optional[str]
    facility_state: Optional[str]
    nurse_preference: Optional[str]
    ambiguity_notes: Optional[str]


class PostParseValidationError(Exception):
    """Raised when post-parse validation fails. Caller routes to coordinator queue."""
    def __init__(self, reason: str, note: str):
        self.reason = reason
        self.note = note
        super().__init__(note)


def parse_email(
    email_body: str,
    received_at: str,
    llm_client: openai.OpenAI,
    model: str,
    medflex_operating_states: list[str],  # TODO (Q-3): source from MEDFLEX_OPERATING_STATES env var — list undefined in spec
    today_utc: date,
) -> ParseResult:
    """
    Parse a hospital shift request email using the LLM (Contract 6).
    Raises ValueError on invalid JSON or missing required fields — caller retries once per spec.
    Raises PostParseValidationError on validation failure — caller routes to coordinator queue.
    """
    user_message = f"received_at: {received_at}\n\n{email_body}"
    response = llm_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON: {exc}") from exc

    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        raise ValueError(f"LLM response missing required fields: {missing}")
    if data["request_type"] not in VALID_REQUEST_TYPES:
        raise ValueError(f"Invalid request_type value: {data['request_type']!r}")

    result = ParseResult(
        request_type=data["request_type"],
        specialty_text=data["specialty_text"],
        shift_date=data["shift_date"],
        shift_start_time=data["shift_start_time"],
        shift_end_time=data["shift_end_time"],
        facility_name=data["facility_name"],
        facility_state=data["facility_state"],
        nurse_preference=data["nurse_preference"],
        ambiguity_notes=data["ambiguity_notes"],
    )
    _post_parse_validate(result, medflex_operating_states, today_utc)
    return result


def _post_parse_validate(
    result: ParseResult,
    medflex_operating_states: list[str],
    today_utc: date,
) -> None:
    """Post-parse validation per Contract 6. WS4 owns this step — not the LLM."""
    if result.shift_date is not None:
        try:
            parsed_date = date.fromisoformat(result.shift_date)
        except ValueError as exc:
            raise PostParseValidationError(
                reason="invalid_shift_date_format",
                note=f"shift_date '{result.shift_date}' is not a valid YYYY-MM-DD date",
            ) from exc
        if parsed_date < today_utc:
            raise PostParseValidationError(
                reason="shift_date_in_past",
                note=f"shift_date {result.shift_date} is before today {today_utc.isoformat()}",
            )

    if result.facility_state is not None:
        if result.facility_state not in medflex_operating_states:
            raise PostParseValidationError(
                reason="facility_state_out_of_network",
                note=f"facility_state '{result.facility_state}' is not in MedFlex operating states",
            )

    if result.shift_start_time is not None and result.shift_end_time is not None:
        start_min = _hhmm_to_minutes(result.shift_start_time)
        end_min = _hhmm_to_minutes(result.shift_end_time)
        # end < start = midnight-crossing (valid per spec: "Shifts crossing midnight: shift_end_time is on the following date")
        # end == start = zero-duration (invalid)
        # end > start = normal same-day (valid)
        if end_min == start_min:
            raise PostParseValidationError(
                reason="invalid_shift_window",
                note=f"shift_end_time {result.shift_end_time} equals shift_start_time {result.shift_start_time}",
            )


def _hhmm_to_minutes(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)
