"""
Clause classifier: compares extracted clause text against the playbook position
and returns a PlaybookMatchStatus with confidence score.

ClauseClassifier is an abstract interface.
ClaudeClauseClassifier is the production implementation using the Anthropic API.
StubClauseClassifier is a deterministic stub for testing without API credentials.

Derived from D4 T-07/T-08/T-09 and CLAUDE.md §3.
"""
from __future__ import annotations

import abc
import json
import re
from dataclasses import dataclass
from typing import Optional

from .models import PlaybookMatchStatus, TaskUnitType
from .config import ANTHROPIC_MODEL, CONFIDENCE_THRESHOLD


@dataclass
class ClassificationResult:
    task_unit_type: TaskUnitType
    playbook_match_status: PlaybookMatchStatus
    agent_confidence_score: float          # 0.0–1.0
    agent_reasoning_summary: str           # max 500 chars
    playbook_section_retrieved: str        # section title for audit log


# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------

class ClauseClassifier(abc.ABC):
    @abc.abstractmethod
    def classify(
        self,
        task_unit_type: TaskUnitType,
        extracted_text: str,
        playbook_section: str,
    ) -> ClassificationResult:
        """
        Classifies a single extracted clause against its playbook section.
        Must not perform any Ironclad write or outbound communication.
        """


# ---------------------------------------------------------------------------
# Production implementation: Claude API
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a clause classification engine for a legal contract review system.
Compare the vendor clause text against the playbook position and classify it.

Classification rules:
- COMPLIANT: clause substantially matches playbook position; numeric values meet or exceed playbook floor
- MINOR_DEVIATION: clause partially matches playbook; numeric values below floor by ≤50%
- MAJOR_DEVIATION: clause substantially differs from playbook; numeric values below floor by >50%
- REQUIRES_SENIOR_REVIEW: clause references regulatory frameworks outside playbook coverage,
  or the deviation is ambiguous and requires senior-lawyer judgment
- MISSING: the clause text provided is empty or the clause type is genuinely absent

For DATA_PROCESSING_AGREEMENT clauses: always append to your reasoning:
"DPDI Act updates not reflected in playbook v3.4 — classification reflects UK GDPR / DPA 2018 only."

Respond with JSON only (no markdown fences):
{
  "playbook_match_status": "<COMPLIANT|MINOR_DEVIATION|MAJOR_DEVIATION|MISSING|REQUIRES_SENIOR_REVIEW>",
  "confidence_score": <float 0.0-1.0>,
  "reasoning": "<explanation ≤400 chars citing the specific playbook position and deviation>"
}"""


class ClaudeClauseClassifier(ClauseClassifier):
    """
    Production classifier using the Anthropic Claude API.
    Requires ANTHROPIC_API_KEY in the environment or passed explicitly.
    """

    def __init__(
        self,
        model: str = ANTHROPIC_MODEL,
        api_key: Optional[str] = None,
    ) -> None:
        import anthropic
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def classify(
        self,
        task_unit_type: TaskUnitType,
        extracted_text: str,
        playbook_section: str,
    ) -> ClassificationResult:
        if not extracted_text or not extracted_text.strip():
            return ClassificationResult(
                task_unit_type=task_unit_type,
                playbook_match_status=PlaybookMatchStatus.MISSING,
                agent_confidence_score=0.95,
                agent_reasoning_summary="No clause text extracted — clause is absent from document.",
                playbook_section_retrieved=f"{task_unit_type.value} (not retrieved — absent)",
            )

        user_message = (
            f"Clause type: {task_unit_type.value}\n\n"
            f"PLAYBOOK POSITION:\n{playbook_section}\n\n"
            f"VENDOR CLAUSE TEXT:\n{extracted_text}"
        )

        response = self._client.messages.create(
            model=self._model,
            max_tokens=512,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw = response.content[0].text
        result = _parse_json_response(raw)

        reasoning = result.get("reasoning", "")[:500]

        # Enforce mandatory DPDI annotation for DPA clauses
        if task_unit_type == TaskUnitType.DATA_PROCESSING_AGREEMENT:
            _DPDI_MARKER = "DPDI Act updates not reflected"
            if _DPDI_MARKER not in reasoning:
                reasoning = (
                    reasoning.rstrip(". ") + ". "
                    "DPDI Act updates not reflected in playbook v3.4 — "
                    "classification reflects UK GDPR / DPA 2018 only."
                )[:500]

        return ClassificationResult(
            task_unit_type=task_unit_type,
            playbook_match_status=PlaybookMatchStatus(result["playbook_match_status"]),
            agent_confidence_score=float(result["confidence_score"]),
            agent_reasoning_summary=reasoning,
            playbook_section_retrieved=f"{task_unit_type.value} section — playbook v3.4",
        )


# ---------------------------------------------------------------------------
# Stub classifier for tests (no API key required)
# ---------------------------------------------------------------------------

class StubClauseClassifier(ClauseClassifier):
    """
    Deterministic stub for unit tests and local development.
    Returns configurable results without calling the Anthropic API.
    Default: returns COMPLIANT with confidence 0.90 for all clauses.
    Override via per-type results dict.
    """

    def __init__(
        self,
        results: Optional[dict[TaskUnitType, ClassificationResult]] = None,
        default_status: PlaybookMatchStatus = PlaybookMatchStatus.COMPLIANT,
        default_confidence: float = 0.90,
    ) -> None:
        self._results = results or {}
        self._default_status = default_status
        self._default_confidence = default_confidence

    def classify(
        self,
        task_unit_type: TaskUnitType,
        extracted_text: str,
        playbook_section: str,
    ) -> ClassificationResult:
        if task_unit_type in self._results:
            return self._results[task_unit_type]

        reasoning = (
            f"Stub: {task_unit_type.value} classified as {self._default_status.value} "
            f"with confidence {self._default_confidence:.2f}."
        )

        # Always inject DPDI annotation for DPA clauses
        if task_unit_type == TaskUnitType.DATA_PROCESSING_AGREEMENT:
            reasoning = (
                reasoning + " DPDI Act updates not reflected in playbook v3.4 — "
                "classification reflects UK GDPR / DPA 2018 only."
            )[:500]

        return ClassificationResult(
            task_unit_type=task_unit_type,
            playbook_match_status=self._default_status,
            agent_confidence_score=self._default_confidence,
            agent_reasoning_summary=reasoning,
            playbook_section_retrieved=f"{task_unit_type.value} section — playbook v3.4 (stub)",
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_json_response(raw: str) -> dict:
    """Extracts the JSON object from a model response (handles markdown fences)."""
    # Strip markdown code blocks if present
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Classifier returned non-JSON response: {raw!r}"
        ) from exc
