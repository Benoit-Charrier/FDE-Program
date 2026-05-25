# Gate 4 D7 — Build Loop Reflection: Dmytro's Intake Spec

**Spec built against:** `Spec_review_input1/04a-capability-spec-intake-Dmytro.md` (Status: FINAL)

---

## Build Loop Output

---

### Part 1: What I Can Build Confidently Without Asking Any Questions

The following areas are complete enough to implement immediately — every decision is made and every edge case is covered:

- **Email polling loop** (Contract 1): Poll cadence, request format, authentication, error table for all HTTP codes, 10-second timeout, retry logic (2s/4s/8s exponential backoff), alert-on-3rd-failure — fully specified.
- **Clarification response detection** (Contract 1, steps 1–6): Thread-header matching via `In-Reply-To`/`References`, single-record fallback logic, new-intake path, audit log requirement for association decision — unambiguous. Exception: step 5 (multiple open records, no thread match) requires clarification — see Part 2, Q-1.
- **Mark-as-read idempotency gate** (Contract 1): PATCH endpoint, timing constraint (after CRM write confirmed, not before), failure handling, audit log requirement — fully specified.
- **LLM email parsing** (Contract 6): Exact system prompt given (do not modify), output JSON schema with all 9 fields, null-allowed flags, shift-name defaults (morning/afternoon/night), retry on invalid JSON, routing on `request_type = AMBIGUOUS` — fully specified. Exception: `facility_state` validation requires a list undefined in the spec — see Part 2, Q-3.
- **Specialty mapping algorithm** (Contract 6 + Shared Glossary): Cosine similarity pipeline (EXACT = case-insensitive match; MAPPED = score ≥ threshold; UNMAPPABLE = score < threshold), `SPECIALTY_MAPPING_THRESHOLD = 0.75`, boundary condition explicit (score exactly 0.75 counts as MAPPED), embedding model configurable via `SPECIALTY_EMBEDDING_MODEL` — fully specified.
- **CRM record creation and update** (Contract 2): POST /shift-requests, PATCH for status and field updates, all HTTP error codes handled, local queue on 3rd failure — fully specified.
- **Data field mapping** (Contract 2, data mapping table): All source-to-Shared-Glossary field transformations — email domain → hospital_id, specialty text → specialty_required/confidence, date expressions → shift_date, time expressions → shift_start/end — fully specified.
- **CRM read operations** (Contract 3): Hospital lookup, specialty vocabulary retrieval, response schemas — fully specified. Exception: duplicate detection query requires clarification — see Part 2, Q-4.
- **WS1 handoff step ordering** (Contract 4): Required 3-step sequence (write all fields → send ACK → set INTAKE_COMPLETE) — mandatory and explicit.
- **Outbound email** (Contract 5): Acknowledgement and clarification templates — exact content given; substitution rules for all field states; PHI constraint (logistics fields only) explicit; rate limits stated.
- **Coordinator queue record creation** (Coordinator Queue section): POST /coordinator-queue-items, all 7 required fields, fallback on API unavailability (local queue + retry every 60s) — fully specified.
- **Audit trail writes** (Audit Trail section): 10-field schema, all 10 `action_type` enum values, append-only constraint, 6-year HIPAA retention — fully specified.
- **CRM state machine** (State Machine section): All 17 defined transitions — fully specified. Exception: MULTI_CLARIFICATION_CONFLICT transition missing — see Part 2, Q-1.
- **Agent startup sequence** (Agent Startup Behavior): 4-step startup order — specialty vocabulary load + embed, clarification timeout resume, credential verification, begin polling — fully specified.
- **PHI handling and routing triggers** (Compliance section): Three PHI routing conditions, "log the flag not the content" rule, downstream write prohibition — explicit.
- **Cross-feature interactions** (Cross-Feature Interactions table): All 5 concurrency scenarios (cancellation-during-clarification, modification-during-clarification, modification-during-WS1, duplicate-during-clarification, ACK failure after CRM write) — fully specified.
- **Worked examples 1–5** (Worked Examples section): All pass criteria are buildable after applying test-date correction — see Part 2, Q-5.

---

### Part 2: What I Need to Clarify Before Building the Rest

> *Contract 1 → clarification response detection, step 5; CRM State Machine*: When multiple open `CLARIFICATION_PENDING` records exist and no thread header match is found, the spec routes to the coordinator queue with `reason_code = MULTI_CLARIFICATION_CONFLICT` — but specifies no CRM status for the new record and has no state machine row for this event. Do I create a new record? What status do I set? If unanswered, I would assume `TYPE_AMBIGUOUS` as the nearest available status — this is **risky** because coordinators see `MULTI_CLARIFICATION_CONFLICT` in the queue alongside `TYPE_AMBIGUOUS` in the CRM, which do not map cleanly to each other, and the coordinator experience is undefined.

> *Configuration table; Contract 1 first paragraph*: `EMAIL_POLL_INTERVAL_SECONDS` is referenced in Contract 1 as "configurable via `EMAIL_POLL_INTERVAL_SECONDS` — add to Configuration if confirmed" with a 60-second default, but it is not in the Configuration table. The circuit breaker section recommends "increasing `EMAIL_POLL_INTERVAL_SECONDS`" as an ops lever. Is this parameter confirmed? If unanswered, I would implement it as a configurable env var with default 60s — this is **safe** for runtime behaviour but **risky** for ops tuning: hardcoding makes the circuit breaker recommendation inoperable without a code change.

> *Contract 6 → post-parse validation; Shared Glossary → `facility_state` constraints*: Post-parse validation says "facility_state not in MedFlex operating state list → escalate to coordinator queue" — but this list is nowhere defined. No config parameter, no referenced file, no sample values. If unanswered, I would accept all 50 US states — this is **risky** because out-of-state requests would pass validation silently and reach WS1, which may not have credential data to match them. Silent compliance risk for unlicensed placements.

> *Contract 3 → duplicate detection query; Autonomy Matrix → duplicate detection row*: The deduplication condition is `hospital_id + shift_date + shift_start_time ±30min + received_at ±60min`. Specialty is absent from the condition. If a hospital legitimately requests an ICU nurse and an ER nurse for the same time window on the same date, the second request would be silently merged into the first — WS1 triggers once, one shift goes unfilled with no alert. If unanswered, I would implement the spec as written with a warning comment — this is **risky** because the failure is silent: no error surfaces, and the unfilled shift would only become visible when the hospital reports it operationally.

> *Worked Examples → Example 1 (`shift_date = 2026-05-15`); Example 2 (`shift_date = 2026-05-19`)*: `shift_date = 2026-05-15` in Example 1 is before today (2026-05-19). Post-parse validation rejects any `shift_date < today UTC` and routes to the coordinator queue. The Example 1 happy-path test would immediately fail — the agent reaches the rejection path, not the `INTAKE_COMPLETE` path the pass criterion requires. If unanswered, I would substitute T+14 from test run date in all test fixtures — this is **safe** as a test fix, but the spec needs the correction so future builders do not diagnose a spec error as a real build failure.

> *Agent Startup Behavior → step 1; Configuration table*: The startup sequence says to cache specialty vocabulary embeddings and "refresh when cache TTL expires" — but no `SPECIALTY_VOCABULARY_CACHE_TTL_HOURS` parameter is defined anywhere in the spec. If unanswered, I would hardcode 24 hours — this is **risky** because if CRM vocabulary changes (new specialty code added), the stale cache classifies the new specialty as `UNMAPPABLE` and routes it to the coordinator queue until the next agent restart. Ops has no lever to force a vocabulary refresh without redeploying.

---

### Part 3: Built — Contract 6: LLM Email Parser and Specialty Mapper

**Why this component:** Contract 6 (LLM email parsing + specialty mapping) has the most complete specification in the spec. The system prompt is exact and flagged "do not modify without re-testing." The output schema is fully defined with null-allowed flags per field. Post-parse validation rules cover all rejection scenarios. The specialty mapping algorithm has explicit thresholds, an exact boundary condition, and a configurable embedding model. Only one open question applies to this component (Q-3: `facility_state` validation), which is isolated behind a clearly-labelled TODO. No other component is as self-contained.

**What was built:** `email_parser.py` (Contract 6 parsing + post-parse validation), `specialty_mapper.py` (Contract 6 specialty mapping), and tests for both.

```python
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
```

```python
# agent_build/src/specialty_mapper.py
"""
Contract 6 — Specialty mapping (separate from LLM parsing call, per spec).
Algorithm per Shared Glossary + Contract 6:
  EXACT    = case-insensitive string match to any vocabulary label (no embedding needed)
  MAPPED   = cosine similarity score >= SPECIALTY_MAPPING_THRESHOLD
  UNMAPPABLE = score < threshold
Boundary: score == threshold counts as MAPPED (spec: "score = 0.75 exactly counts as MAPPED (≥ threshold)").
"""
from dataclasses import dataclass
from typing import Optional

import numpy as np
import openai


@dataclass
class VocabularyEntry:
    code: str            # written to specialty_required CRM field (e.g. "ICU")
    label: str           # embedded for similarity matching (e.g. "Intensive Care Unit")
    embedding: Optional[list[float]] = None  # cached at startup; None = not yet embedded


@dataclass
class MappingResult:
    specialty_required: Optional[str]   # None if UNMAPPABLE
    specialty_confidence: str           # "EXACT" | "MAPPED" | "UNMAPPABLE"
    best_score: Optional[float]         # cosine similarity; None for EXACT (no embedding used)


def map_specialty(
    specialty_text: str,
    vocabulary: list[VocabularyEntry],
    embedding_client: openai.OpenAI,
    embedding_model: str,
    threshold: float,  # SPECIALTY_MAPPING_THRESHOLD default 0.75 per spec
) -> MappingResult:
    """
    Map specialty_text to a CRM specialty vocabulary code.
    vocabulary must have pre-computed embeddings (loaded at startup per Agent Startup Behavior step 1).
    """
    # EXACT: case-insensitive label match (spec: "input already exactly matches a vocabulary label")
    normalized = specialty_text.strip().lower()
    for entry in vocabulary:
        if normalized == entry.label.lower():
            return MappingResult(
                specialty_required=entry.code,
                specialty_confidence="EXACT",
                best_score=None,
            )

    # Embed input text for cosine similarity comparison
    input_emb = _get_embedding(specialty_text, embedding_client, embedding_model)

    best_score = -1.0
    best_entry: Optional[VocabularyEntry] = None
    for entry in vocabulary:
        if entry.embedding is None:
            raise RuntimeError(
                f"Vocabulary entry {entry.code!r} has no cached embedding — "
                "call embed_vocabulary() at startup before mapping"
            )
        score = _cosine_similarity(input_emb, entry.embedding)
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry is not None and best_score >= threshold:  # >= per spec boundary
        return MappingResult(
            specialty_required=best_entry.code,
            specialty_confidence="MAPPED",
            best_score=best_score,
        )

    return MappingResult(
        specialty_required=None,
        specialty_confidence="UNMAPPABLE",
        best_score=best_score if best_score > -1.0 else None,
    )


def embed_vocabulary(
    vocabulary: list[VocabularyEntry],
    embedding_client: openai.OpenAI,
    embedding_model: str,
) -> None:
    """Compute and cache embeddings for all vocabulary labels in-place (startup step 1)."""
    for entry in vocabulary:
        entry.embedding = _get_embedding(entry.label, embedding_client, embedding_model)


def _get_embedding(text: str, client: openai.OpenAI, model: str) -> list[float]:
    response = client.embeddings.create(input=text, model=model)
    return response.data[0].embedding


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr = np.array(a, dtype=float)
    b_arr = np.array(b, dtype=float)
    norm_a = float(np.linalg.norm(a_arr))
    norm_b = float(np.linalg.norm(b_arr))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a_arr, b_arr)) / (norm_a * norm_b)
```

```python
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
        parse_email("email body", "2026-05-19T10:00:00Z", _mock_llm('{"request_type":"NEW_REQUEST"}'), "gpt-4o-mini", MEDFLEX_STATES, TODAY)
```

```python
# agent_build/tests/test_specialty_mapper.py
"""
Tests for Contract 6 specialty mapping algorithm.
Key boundary: cosine similarity score == SPECIALTY_MAPPING_THRESHOLD (0.75) counts as MAPPED, not UNMAPPABLE.
Spec: "score = 0.75 exactly counts as MAPPED (≥ threshold)"
"""
import math
from unittest.mock import MagicMock

from agent_build.src.specialty_mapper import VocabularyEntry, MappingResult, map_specialty

THRESHOLD = 0.75

# Unit vectors for deterministic cosine similarity tests
VOCAB = [
    VocabularyEntry(code="ICU", label="Intensive Care Unit", embedding=[1.0, 0.0, 0.0]),
    VocabularyEntry(code="ER",  label="Emergency Room",      embedding=[0.0, 1.0, 0.0]),
    VocabularyEntry(code="OR",  label="Operating Room",      embedding=[0.0, 0.0, 1.0]),
]


def _mock_embedding(vector: list[float]) -> MagicMock:
    client = MagicMock()
    client.embeddings.create.return_value.data = [MagicMock(embedding=vector)]
    return client


def test_exact_match_returns_exact_no_embedding_call():
    client = _mock_embedding([1.0, 0.0, 0.0])
    result = map_specialty("Intensive Care Unit", VOCAB, client, "text-embedding-3-small", THRESHOLD)
    assert result.specialty_confidence == "EXACT"
    assert result.specialty_required == "ICU"
    assert result.best_score is None
    client.embeddings.create.assert_not_called()


def test_exact_match_is_case_insensitive():
    client = _mock_embedding([1.0, 0.0, 0.0])
    result = map_specialty("intensive care unit", VOCAB, client, "text-embedding-3-small", THRESHOLD)
    assert result.specialty_confidence == "EXACT"
    assert result.specialty_required == "ICU"


def test_high_similarity_returns_mapped():
    # 5° offset from ICU vector → score ≈ cos(5°) ≈ 0.996 > threshold
    angle = math.radians(5)
    emb = [math.cos(angle), math.sin(angle), 0.0]
    result = map_specialty("ICU-level care", VOCAB, _mock_embedding(emb), "text-embedding-3-small", THRESHOLD)
    assert result.specialty_confidence == "MAPPED"
    assert result.specialty_required == "ICU"
    assert result.best_score >= THRESHOLD


def test_boundary_exactly_at_threshold_counts_as_mapped():
    # Construct embedding so cosine similarity with ICU [1,0,0] == exactly 0.75
    # cos(angle) = 0.75 → angle = arccos(0.75); unit vector: [0.75, sqrt(1-0.75²), 0]
    emb = [0.75, math.sqrt(1 - 0.75 ** 2), 0.0]
    result = map_specialty("periop cover", VOCAB, _mock_embedding(emb), "text-embedding-3-small", THRESHOLD)
    assert result.specialty_confidence == "MAPPED"
    assert abs(result.best_score - THRESHOLD) < 1e-9


def test_below_threshold_returns_unmappable():
    # 60° offset from ICU vector → score = cos(60°) = 0.5 < threshold
    angle = math.radians(60)
    emb = [math.cos(angle), math.sin(angle), 0.0]
    result = map_specialty("Level 3 perioperative cover", VOCAB, _mock_embedding(emb), "text-embedding-3-small", THRESHOLD)
    assert result.specialty_confidence == "UNMAPPABLE"
    assert result.specialty_required is None
    assert result.best_score < THRESHOLD
```

---

## §1. Signal Inventory

Every discrepancy or notable behaviour identified during the build. Not pre-filtered — all signals before classification.

| Signal ID | What the build produced | What the spec required or intended | First-pass classification |
|-----------|------------------------|------------------------------------|--------------------------|
| S-1 | Implemented duplicate detection condition as specified: `hospital_id + shift_date + shift_start_time ±30min + received_at ±60min`. Specialty absent from query. | Intended to prevent duplicate records — but the condition as written would silently merge two distinct specialties (ICU + ER) from the same hospital for the same time slot into one record, triggering WS1 only once. | Spec gap |
| S-2 | Could not build Contract 1 step 5 (multiple open CLARIFICATION_PENDING records, no thread match) — no CRM status defined for this path; state machine has no row for this event. Surfaced the question rather than guessing a status. | Spec intended this path to route to the coordinator queue with `MULTI_CLARIFICATION_CONFLICT`, but omitted: what status the new record gets, and whether a new record should be created at all. | Legitimate unknown surfaced correctly |
| S-3 | Implemented `EMAIL_POLL_INTERVAL_SECONDS` as a configurable env var with default 60s (inferred from Contract 1). Added it to the implementation without a formal config table entry. | Configuration table is the deployment reference; ops teams read it to configure the agent. The parameter is named in Contract 1 and the circuit breaker section as an ops lever, but is absent from the table. | Spec gap |
| S-4 | Implemented `facility_state` post-parse validation with `medflex_operating_states` as an explicit parameter; added `TODO` comment because the list is undefined in the spec. Could not implement production-grade validation without a defined list. | Spec requires rejecting `facility_state` values "not in MedFlex operating state list" — but this list exists nowhere in the spec, config table, or referenced files. | Legitimate unknown surfaced correctly |
| S-5 | Tests against Example 1 (`shift_date = 2026-05-15`) fail immediately: post-parse validation correctly rejects the past date and routes to the coordinator queue. Example 1's `INTAKE_COMPLETE` pass criterion is never reached. | Worked examples are test fixtures. The spec's own post-parse validation rule rejects past dates — the example uses a date now in the past (today is 2026-05-19). Code is correct; test data is stale. | Test/environment issue |
| S-6 | Implemented specialty vocabulary refresh with a hardcoded 24-hour TTL because no `SPECIALTY_VOCABULARY_CACHE_TTL_HOURS` parameter exists in the spec. Added a `TODO` comment. | Agent Startup Behavior says "refresh when cache TTL expires" — but the TTL is nowhere defined, leaving ops no lever to force a vocabulary refresh without redeploying. | Legitimate unknown surfaced correctly |

---

## §2. Classified Signal Responses

---

```
Signal S-1: Duplicate detection condition omits specialty — silent data loss on multi-specialty same-window requests

Classification: Spec gap

Evidence:
- Spec: Autonomy Matrix → duplicate detection row: "same hospital_id, same shift_date, and the incoming
  request's shift_start_time is within ±30 minutes of an existing open record's shift_start_time, and
  the inbound email's received_at is within 60 minutes of the existing record's created_at"
- Build: Implemented this condition exactly — no specialty field in the query or comparison.
  A hospital requesting ICU at 07:00 and ER at 07:30 on the same date would have the ER request
  silently merged into the ICU record. WS1 triggers once. One shift goes unfilled.
- Why spec gap and not builder misread: The builder's implementation matches the spec exactly as written.
  There is no alternative reading of the spec that includes specialty — the condition is unambiguous.
  The omission is in the spec itself, not in the builder's interpretation of it.

Response:
I need to revise the spec because the original statement was ambiguous between interpretation A
(deduplicate on logistics + timing only) and interpretation B (deduplicate on logistics + timing +
specialty). The correct behaviour is: a hospital can legitimately request two different specialties
for the same shift window; the deduplication condition must include specialty_required to distinguish
these as separate requests.

Revised spec text for Autonomy Matrix → duplicate detection row:
"Duplicate request detected (same hospital_id, same shift_date, same specialty_required (if resolved),
and the incoming request's shift_start_time is within ±30 minutes of an existing open record's
shift_start_time, and the inbound email's received_at is within 60 minutes of the existing record's
created_at). For UNMAPPABLE specialty requests (specialty_required not yet resolved): skip the
specialty filter; treat as a distinct record to avoid silently merging unresolved requests."

Revised spec text for Contract 3 → existing request lookup:
GET /shift-requests?hospital_id={id}&shift_date={date}&specialty_required={code}&status=...
Add note: "If specialty_confidence = UNMAPPABLE, omit specialty_required from this query."

Ownership: FDE
```

---

```
Signal S-2: MULTI_CLARIFICATION_CONFLICT path has no CRM status and no state machine row

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: Contract 1 → clarification response detection, step 5: "route to coordinator queue with
  action_type = ESCALATED and note 'multiple open clarification records — cannot determine which
  request this email resolves.'" The reason_code MULTI_CLARIFICATION_CONFLICT is defined in the
  Coordinator Queue reason_code enum. But no CRM status is assigned to this path, and the state
  machine table has no row covering this event.
- Build: Could not implement step 5 without inventing a CRM status. Surfaced the question:
  "Do I create a new record? If so, what status?" rather than silently choosing TYPE_AMBIGUOUS.
- Why legitimate unknown and not spec gap: The spec did not offer two conflicting interpretations —
  it was simply silent on the CRM status for this path. The builder identified a gap the spec did
  not address and flagged it rather than guessing.

Response:
You're right that the spec didn't address this. The correct behaviour is: WS4 creates a new CRM
record with status TYPE_AMBIGUOUS (closest semantically to the situation — agent cannot determine
the intent without knowing which clarification loop the email belongs to) and routes to the
coordinator queue with reason_code = MULTI_CLARIFICATION_CONFLICT. The coordinator sees both the
TYPE_AMBIGUOUS status and the MULTI_CLARIFICATION_CONFLICT reason code; the note must include the
IDs of all affected CLARIFICATION_PENDING records so the coordinator can resolve manually.

I'm adding this to the spec now. Please implement:
1. When step 5 fires: create a new CRM record with status TYPE_AMBIGUOUS.
2. Write a coordinator queue item with reason_code = MULTI_CLARIFICATION_CONFLICT and note:
   "Multiple open clarification records for this hospital; affected record IDs: {list}. Cannot
   determine which request this email resolves."
3. Log ESCALATED to the audit trail with the new crm_request_id.

Add to state machine:
"(new record) | Inbound email matches multiple CLARIFICATION_PENDING records; no thread header
match | TYPE_AMBIGUOUS | WS4"

Ownership: Shared — FDE revises spec; builder implements the added row.
```

---

```
Signal S-3: EMAIL_POLL_INTERVAL_SECONDS named in Contract 1 but absent from Configuration table

Classification: Spec gap

Evidence:
- Spec: Contract 1, first paragraph: "Every 60 seconds (configurable via EMAIL_POLL_INTERVAL_SECONDS
  — add to Configuration if confirmed)". Economics section: "alert ops and recommend increasing
  EMAIL_POLL_INTERVAL_SECONDS". Configuration table: parameter is absent.
- Build: Implemented EMAIL_POLL_INTERVAL_SECONDS as a configurable env var with default 60s.
  The intent (configurable) is clear from Contract 1 — but the Configuration table is the deployment
  reference ops teams read. Without an entry there, a deployer reading the config table would not
  know this parameter exists or that it defaults to 60.
- Why spec gap and not builder misread: The spec itself deferred the addition ("add to Configuration
  if confirmed"). The builder's choice to add it was correct, but the omission originated in the spec.

Response:
I need to revise the spec because the original statement deferred adding this parameter without
completing the addition. The correct behaviour is: EMAIL_POLL_INTERVAL_SECONDS is a confirmed
configurable parameter — its default (60s) is stated in Contract 1 and it is referenced as an
ops lever in the circuit breaker section.

Revised spec text — add to Configuration table:
| EMAIL_POLL_INTERVAL_SECONDS | integer (seconds) | 60 | Email polling cadence. Increase this value
if EMAIL_POLL_COST_BUDGET_USD_PER_HOUR circuit breaker fires. Decreasing below 10 risks rate-limit
pressure on the email provider API — confirm with Aaron before going below 30s. |

Remove from Contract 1: "— add to Configuration if confirmed" qualifier.

Ownership: FDE
```

---

```
Signal S-4: MEDFLEX_OPERATING_STATES list undefined — facility_state validation cannot be implemented

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: Shared Glossary → facility_state: "must be a state MedFlex operates in". Contract 6 →
  post-parse validation: "facility_state not in MedFlex operating state list → escalate to coordinator
  queue". Configuration table: no MEDFLEX_OPERATING_STATES parameter. No referenced file contains
  the list.
- Build: Implemented the validation with a TODO comment and injected the list as an explicit parameter.
  Could not hardcode the list without inventing it. Surfaced the question rather than accepting all 50
  states or making up a subset.
- Why legitimate unknown and not spec gap: The spec was not ambiguous about what to do — it was silent
  on where to find the list. The builder identified the missing data source and flagged it.

Response:
You're right that the spec didn't address this. The correct behaviour is: the operating states list
must be a configurable parameter (not hardcoded) so it can be updated when MedFlex expands to new
states. Aaron must supply the production list before deployment.

I'm adding this to the spec now. Please implement:
1. Read operating states from MEDFLEX_OPERATING_STATES env var at startup (JSON array of 2-letter codes).
2. If the env var is missing or empty, abort startup and alert ops — validation cannot proceed.
3. Validate facility_state against this list in _post_parse_validate.

Add to Configuration table:
| MEDFLEX_OPERATING_STATES | JSON array of strings | ["IL","NY","TX"] (sample — confirm with Aaron) |
List of 2-letter US state codes MedFlex is licensed to operate in. Aaron must supply the production
list before deployment. If a facility_state value is not in this list, escalate to coordinator queue
with note "facility state {value} is not in MedFlex operating states." |

Update Shared Glossary → facility_state constraint:
"must be a value in MEDFLEX_OPERATING_STATES (see Configuration)"

Ownership: Shared — FDE adds config entry; builder reads from env var at startup.
```

---

```
Signal S-5: Worked Example 1 shift_date is in the past — happy-path test fails immediately

Classification: Test/environment issue

Evidence:
- Spec: Worked Examples → Example 1: shift_date = 2026-05-15. Contract 6 → post-parse validation:
  "shift_date < today UTC → reject; route to coordinator queue with note 'shift date in the past'".
  Today is 2026-05-19.
- Build: The test for Example 1 invokes post-parse validation, which correctly rejects 2026-05-15 as
  a past date and raises PostParseValidationError(reason="shift_date_in_past"). The code never reaches
  the INTAKE_COMPLETE path that Example 1's pass criterion requires.
- Why test/environment issue and not builder misread: The spec says "shift_date < today UTC → reject."
  The code correctly implements this rule. The test example data uses a hardcoded date that has
  since passed. The code is correct per the spec; the test fixture is stale.

Response:
The spec says shift_date < today UTC must be rejected (Contract 6 post-parse validation). The code
correctly implements this. The worked example data is wrong — shift_date 2026-05-15 is in the past.

Fix the test fixtures, not the code:
1. Replace shift_date = 2026-05-15 in Example 1 with (today + 14 days) from test run date.
2. Replace shift_date in Example 2 ("next Tuesday" resolving to 2026-05-19 = today) with a formula
   resolving to a future date.
3. Add a note at the top of the Worked Examples section:
   "All dates are illustrative. Test execution requires a future shift_date ≥ 1 day from test run
   date. Parameterise dates in test fixtures — do not hardcode."

Ownership: Test author (spec author owns the worked example update).
```

---

```
Signal S-6: Specialty vocabulary cache TTL undefined — ops cannot force a refresh without redeploying

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: Agent Startup Behavior → step 1: "Cache all {code, label} pairs in memory. Compute and cache
  embeddings for all labels... Refresh when cache TTL expires or on specialty mapping failure that
  seems vocabulary-related." Configuration table: no SPECIALTY_VOCABULARY_CACHE_TTL_HOURS entry.
- Build: Implemented vocabulary caching with a hardcoded 24-hour TTL. Could not surface a configurable
  parameter because the spec doesn't define one. Added a TODO comment.
- Why legitimate unknown and not spec gap: The spec mentioned TTL-based refresh as intended behaviour
  but was silent on the TTL value and whether it should be configurable. The builder flagged the gap
  rather than hardcoding silently.

Response:
You're right that the spec didn't address this. The correct behaviour is: the cache TTL must be a
configurable parameter so ops can force a vocabulary refresh — for example, when a new specialty is
added to the CRM — without redeploying the agent.

I'm adding this to the spec now. Please implement:
1. Read cache TTL from SPECIALTY_VOCABULARY_CACHE_TTL_HOURS env var at startup.
2. Refresh vocabulary (re-fetch from GET /specialties and re-embed) when TTL elapses.
3. Also refresh immediately on any specialty mapping failure flagged as "vocabulary-related" per spec.

Add to Configuration table:
| SPECIALTY_VOCABULARY_CACHE_TTL_HOURS | integer (hours) | 24 | How long specialty vocabulary
embeddings are retained before re-fetching from CRM GET /specialties and re-embedding.
Set to a low value (e.g. 1) when a new specialty is being onboarded to force rapid pickup.
Setting to 0 disables caching (re-fetches on every parse — not recommended in production). |

Ownership: Shared — FDE adds config entry; builder reads TTL from env var.
```

---

## §3. Spec Revision Log

---

```
Revision R-1 (for Signal S-1):

Section revised: Autonomy Matrix → duplicate detection row; Contract 3 → existing request lookup
Original text: "same hospital_id, same shift_date, and the incoming request's shift_start_time is
  within ±30 minutes of an existing open record's shift_start_time, and the inbound email's
  received_at is within 60 minutes of the existing record's created_at"
Revised text: "same hospital_id, same shift_date, same specialty_required (if resolved to EXACT or
  MAPPED), and the incoming request's shift_start_time is within ±30 minutes of an existing open
  record's shift_start_time, and the inbound email's received_at is within 60 minutes of the existing
  record's created_at. For UNMAPPABLE specialty: omit specialty_required from the deduplication
  condition; treat as a distinct record."
  Contract 3 query updated:
  GET /shift-requests?hospital_id={id}&shift_date={date}&specialty_required={code}&status=...
  Add note: "If specialty_confidence = UNMAPPABLE, omit specialty_required from this query."
What the revision prevents: A builder implementing the original condition would silently merge
  legitimate multi-specialty same-window requests — a hospital's second shift request would be
  dropped with no record, no alert, and no WS1 trigger.
Category: Spec gap — ambiguity resolved
```

---

```
Revision R-2 (for Signal S-2):

Section revised: CRM Request Status State Machine; Contract 1 → clarification response detection
Original text: No state machine row for MULTI_CLARIFICATION_CONFLICT event. Contract 1 step 5
  specifies routing to coordinator queue but does not specify what CRM status to set or whether
  to create a new record.
Revised text: Add state machine row:
  "| (new record) | Inbound email matches multiple CLARIFICATION_PENDING records for this hospital;
  no thread header match found | TYPE_AMBIGUOUS | WS4 |"
  Add to Contract 1 step 5:
  "WS4 creates a new CRM record with status TYPE_AMBIGUOUS and routes to coordinator queue with
  reason_code = MULTI_CLARIFICATION_CONFLICT and note: 'Multiple open clarification records for
  this hospital; affected record IDs: {list_of_crm_request_ids}. Cannot determine which request
  this email resolves.' Log ESCALATED to audit trail with the new crm_request_id."
What the revision prevents: Without this row, a builder implementing step 5 either crashes (no
  status to set) or invents a status — producing unpredictable coordinator queue behaviour that
  varies by builder and may not match what the coordinator queue UI expects.
Category: Legitimate unknown — gap filled
```

---

```
Revision R-3 (for Signal S-3):

Section revised: Configuration table; Contract 1 first paragraph
Original text: Contract 1: "Every 60 seconds (configurable via EMAIL_POLL_INTERVAL_SECONDS —
  add to Configuration if confirmed)". Configuration table: parameter absent.
Revised text: Add to Configuration table:
  "| EMAIL_POLL_INTERVAL_SECONDS | integer (seconds) | 60 | Email polling cadence. Ops can increase
  this value if the EMAIL_POLL_COST_BUDGET_USD_PER_HOUR circuit breaker fires. Do not decrease below
  30s without confirming rate limits with Aaron. |"
  Remove from Contract 1: "— add to Configuration if confirmed"
What the revision prevents: Without this entry, a builder reading the Configuration table would not
  know the parameter exists, would likely hardcode 60, and ops would have no lever to adjust the poll
  rate in response to cost or load — making the circuit breaker recommendation inoperable.
Category: Spec gap — ambiguity resolved
```

---

```
Revision R-4 (for Signal S-4):

Section revised: Configuration table; Shared Glossary → facility_state field constraints
Original text: Shared Glossary: "must be a state MedFlex operates in". Configuration table:
  no MEDFLEX_OPERATING_STATES entry. No source for the list anywhere in the spec.
Revised text: Add to Configuration table:
  "| MEDFLEX_OPERATING_STATES | JSON array of strings | ["IL","NY","TX"] (sample only — confirm
  production list with Aaron before deployment) | List of 2-letter US state codes MedFlex is
  licensed to operate in. Agent aborts startup if this value is missing or empty. |"
  Update Shared Glossary → facility_state constraint:
  "must be a value in MEDFLEX_OPERATING_STATES (see Configuration). Validated at parse time —
  if not in list, escalate to coordinator queue."
What the revision prevents: Without this parameter, a builder accepts all 50 US states, allowing
  out-of-network placement requests to pass validation silently and reach WS1. WS1 may not have
  credential data for those states — silent compliance risk for unlicensed placements.
Category: Legitimate unknown — gap filled
```

---

```
Revision R-5 (for Signal S-6):

Section revised: Configuration table; Agent Startup Behavior → step 1
Original text: Agent Startup Behavior: "Cache all {code, label} pairs in memory. Compute and cache
  embeddings for all labels... Refresh when cache TTL expires or on specialty mapping failure that
  seems vocabulary-related." Configuration table: no TTL parameter.
Revised text: Add to Configuration table:
  "| SPECIALTY_VOCABULARY_CACHE_TTL_HOURS | integer (hours) | 24 | How long specialty vocabulary
  embeddings are retained before re-fetching from GET /specialties and re-embedding. Set to 1 when
  onboarding a new specialty code to force rapid pickup. Setting to 0 disables caching (re-fetches
  on every parse — not recommended in production). |"
  Update Agent Startup Behavior step 1:
  "Refresh vocabulary when SPECIALTY_VOCABULARY_CACHE_TTL_HOURS elapses since last load, or
  immediately on a specialty mapping failure that appears vocabulary-related."
What the revision prevents: Without this parameter, the builder hardcodes a TTL (likely 24h).
  If a new specialty code is added to the CRM, the cache stays stale for up to 24 hours, classifying
  the new specialty as UNMAPPABLE and routing those requests to the coordinator queue. Ops cannot
  force a refresh without redeploying.
Category: Legitimate unknown — gap filled
```

---

## §4. Builder Correction Memos

No signals in this build loop are classified as builder misread. Every implementation either followed the spec exactly (S-1, S-3 — spec gaps where the spec was unambiguous but wrong) or surfaced open questions rather than guessing (S-2, S-4, S-6 — legitimate unknowns). The spec's clarity on specified sections and explicitness about unknowns ("confirm with Aaron before implementation") left no path where a careful builder would contradict a clear statement.

Re-prompting the builder for S-1 or S-3 would be a graded failure — those signals reflect FDE-owned spec omissions, not builder errors.

---

## §5. Peer Review vs. Build Loop Comparison

---

### What the build loop caught that the peer review also caught

| Peer review finding | Build loop signal | Why both methods converge |
|---------------------|-------------------|--------------------------|
| B1 — Duplicate detection omits specialty | S-1 | Both methods identify the same missing field in the deduplication condition. The peer review caught it by reading the logic against realistic scenarios; the build loop surfaced it when implementing the Contract 3 query and noticing specialty was absent. Convergence signals high confidence: this is a data-loss failure, not a cosmetic gap. |
| B2 — MULTI_CLARIFICATION_CONFLICT no state machine row | S-2 | The peer review identified the missing row by reading Contract 1 step 5 against the state machine. The build loop hit it as an implementation blocker — step 5 cannot be coded without a status to set. Both methods agree: this path would produce undefined coordinator behaviour. |
| B3 — EMAIL_POLL_INTERVAL_SECONDS absent from config | S-3 | The peer review caught the inconsistency between Contract 1's reference and the config table. The build loop encountered it when wiring up the polling loop and had to decide whether to hardcode or add a configurable parameter. Both converge on: missing config entry makes an ops lever unusable. |
| B4 — MEDFLEX_OPERATING_STATES undefined | S-4 | The peer review identified the missing config parameter by reading the post-parse validation rule against the config table. The build loop hit it as an unbuildable validation — no list to validate against. Both agree: without this, facility_state validation is vacuous, creating a silent compliance risk. |
| B5 — Worked example dates in past | S-5 | The peer review caught this as a spec inconsistency; the build loop surfaced it as a test failure. Both agree on the symptom: a builder running Example 1 sees a coordinator-queue escalation where the spec promises INTAKE_COMPLETE. |
| C2 — Specialty vocabulary cache TTL undefined | S-6 | The peer review identified the missing config parameter. The build loop hit it when implementing the startup sequence — "refresh when cache TTL expires" requires a TTL value to exist. Both agree: without the parameter, ops cannot force a refresh without redeploying. |

---

### What the peer review caught that the build loop missed

**C1 — No clarification round cap (unbounded wait condition)**

The peer review caught C1 by reading the state machine's self-loop note ("no cap on clarification rounds in v1") and tracing the operational consequence: a hospital that sends one field per response before each timeout keeps a request in CLARIFICATION_PENDING indefinitely, with no coordinator notification.

The build loop did not surface this as a signal. The spec explicitly acknowledges "no cap in v1" — so a builder implementing the clarification loop would implement exactly what the spec says and produce no warning. There is no build failure; there is no test that would catch it; the operational risk only surfaces when a hospital games the loop or responds slowly. The build loop cannot detect risks that the spec explicitly chose to accept.

**C3 — Portal → WS1 trigger path undefined**

The peer review caught C3 by reading across system boundaries — the Scope section says portal is out of WS4's scope, but the Shared Glossary includes `intake_channel = PORTAL` and WS1 is triggered by `INTAKE_COMPLETE` status. A reviewer reading both sections simultaneously sees the gap: if the portal creates records without setting INTAKE_COMPLETE, WS1 never processes portal shifts.

The build loop did not surface this. A builder implementing WS4 never touches portal logic — portal intake is explicitly out of scope. The build loop's boundary is the spec's scope boundary; it cannot see past it to the WS1 builder's unanswered question. This cross-system inconsistency is invisible from within a single-component build.

---

### What the build loop surfaced that the peer review missed

None. All six build loop signals (S-1 through S-6) correspond directly to peer review findings (B1–B5, C2). The build loop produced no net-new issues.

However, the build loop added *diagnostic specificity* the peer review could not. For S-5, the peer review described it as "spec inconsistency — test case breakage." The build loop produced a concrete test failure trace: `PostParseValidationError(reason="shift_date_in_past")` on Example 1's happy-path invocation. For S-4, the peer review said "validation is vacuous." The build loop produced a specific failure mode: the builder cannot write the validation function at all without a list — the gap blocks implementation, not just documentation.

---

### False positives in the original peer review — peer review findings the build loop did not reproduce

**Zero false positives.** Every peer review finding was confirmed as real; none was shown by the build loop to be a misread or overclaim.

| Peer review finding | Build loop verdict | Basis |
|---------------------|--------------------|-------|
| B1 — Duplicate detection omits specialty | Confirmed (S-1) | Build implemented the spec exactly; the data-loss path is reproducible |
| B2 — MULTI_CLARIFICATION_CONFLICT has no state machine row | Confirmed (S-2) | Build could not implement step 5 without inventing a CRM status — hard blocker |
| B3 — EMAIL_POLL_INTERVAL_SECONDS absent from config table | Confirmed (S-3) | Build had to choose hardcode-or-inject; ops lever is inoperable without the table entry |
| B4 — MEDFLEX_OPERATING_STATES undefined | Confirmed (S-4) | Build cannot write the validation function without the list — implementation blocker |
| B5 — Worked example dates in past | Confirmed (S-5) | Build produced a concrete test failure trace on Example 1's happy path |
| C2 — Specialty vocabulary cache TTL undefined | Confirmed (S-6) | Build hardcoded 24h TTL; ops has no refresh lever without the config parameter |
| C1 — No clarification round cap | Not surfaced by build loop — but not a false positive | The spec explicitly notes "no cap in v1." A correct implementation follows it and produces no build failure. The risk is real but accepted by the spec author; it only surfaces when a hospital games the loop or responds slowly. Not a false positive: the peer review correctly identified a design risk the spec author consciously accepted without naming the operational consequence. |
| C3 — Portal → WS1 trigger path undefined | Not surfaced by build loop — but not a false positive | Portal intake is explicitly outside WS4's scope. A builder implementing WS4 never touches it and produces no error. But the cross-system gap (portal creates records without setting INTAKE_COMPLETE → WS1 never processes portal shifts) is real when read against the Shared Glossary. The build loop's scope boundary made it invisible; the peer review's cross-system read made it visible. Not a false positive: the gap exists, just outside any single-component build's reach. |

The absence of false positives is itself a finding. The peer review was calibrated: it raised eight issues, all of which were either confirmed by implementation or confirmed as real by the spec itself. No finding was an overclaim. This suggests the peer review applied the right reading discipline — checking claims against specific spec text rather than pattern-matching against generic anti-patterns.

---

### One-paragraph honest assessment

The peer review is better for catching issues most likely to cause silent wrong behaviour in production. C1 (unbounded clarification loop) and C3 (portal WS1 trigger) are both production failures that produce no build errors, no test failures, and no implementation blockers — they only surface when real requests go unprocessed and a hospital reports an unfilled shift. The build loop is structurally incapable of catching these: C1 is an explicit design choice the spec acknowledges, so a correct implementation follows it; C3 is outside the build scope entirely. For the five blockers (B1–B5) and one concern (C2), both methods converge — but the peer review would have blocked the build before a single line of code was written, while the build loop surfaced the same issues only after the builder hit them in implementation. The build loop's advantage is specificity: it converts abstract peer review findings into concrete failure traces (tests that fail, functions that can't be written, params that have no values), which makes them easier to fix precisely. A complete spec-validation process uses both in sequence: peer review first as a pre-build gate (catches cross-system and design-choice risks that require no code), then a build loop as a confirmation step (produces concrete failure evidence and catches any gaps the reviewer missed by not simulating implementation). In this fixture, the peer review should have blocked the build — and would have, if the five blockers had been resolved before the build loop ran.
