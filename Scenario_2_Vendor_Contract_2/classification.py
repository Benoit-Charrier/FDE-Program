from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import anthropic
import audit
from extraction import ClauseResult

STATUS_MATCH = "match"
STATUS_DEVIATION = "negotiable_deviation"
STATUS_ESCALATE = "escalate"


@dataclass
class ClauseClassification:
    family: str
    extracted_text: str
    source_page: Optional[int]
    confidence: float
    found: bool
    status: str
    reason_code: str
    rationale: str


def classify(clause_results: list[ClauseResult], playbook: dict, contract_id: str) -> list[ClauseClassification]:
    client = anthropic.Anthropic()
    threshold = playbook.get("min_confidence_threshold", 0.70)
    families_config = playbook.get("clause_families", {})

    classifications = []
    for cr in clause_results:
        cfg = families_config.get(cr.family, {})
        cls = _classify_clause(cr, cfg, threshold, client)
        classifications.append(cls)

    audit.log_event(contract_id, "classification", {
        "results": [{"family": c.family, "status": c.status, "reason_code": c.reason_code} for c in classifications]
    })
    return classifications


def _classify_clause(cr: ClauseResult, cfg: dict, threshold: float, client: anthropic.Anthropic) -> ClauseClassification:
    required = cfg.get("required", False)

    # Gate 1: confidence (FR-11)
    if cr.confidence < threshold:
        return ClauseClassification(
            **_base(cr), status=STATUS_ESCALATE,
            reason_code="low_confidence",
            rationale=f"Confidence {cr.confidence:.2f} is below threshold {threshold}.",
        )

    # Gate 2: missing mandatory clause
    if not cr.found:
        if required:
            return ClauseClassification(
                **_base(cr), status=STATUS_ESCALATE,
                reason_code="missing_mandatory_clause",
                rationale=f"{cr.family} is required but was not found in the document.",
            )
        else:
            return ClauseClassification(
                **_base(cr), status=STATUS_MATCH,
                reason_code="optional_clause_absent",
                rationale=f"{cr.family} is optional and not present.",
            )

    text = cr.extracted_text

    # Step 3: jurisdiction check (governing_law only)
    if cr.family == "governing_law":
        accepted_j = cfg.get("accepted_jurisdictions", [])
        if accepted_j and not _semantic_match(text, accepted_j, client):
            return ClauseClassification(
                **_base(cr), status=STATUS_ESCALATE,
                reason_code="unapproved_jurisdiction",
                rationale="Governing law names a jurisdiction not in the approved list.",
            )
        return ClauseClassification(
            **_base(cr), status=STATUS_MATCH,
            reason_code="playbook_match",
            rationale="Governing law is within an approved jurisdiction.",
        )

    # Step 4: accepted positions (checked before escalation triggers to avoid false positives)
    accepted = cfg.get("accepted_positions", [])
    if accepted and _semantic_match(text, accepted, client):
        return ClauseClassification(
            **_base(cr), status=STATUS_MATCH,
            reason_code="playbook_match",
            rationale=f"{cr.family} matches an accepted playbook position.",
        )

    # Step 5: escalation trigger check
    triggers = cfg.get("escalation_triggers", [])
    if triggers and _semantic_match(text, triggers, client):
        return ClauseClassification(
            **_base(cr), status=STATUS_ESCALATE,
            reason_code="escalation_trigger_matched",
            rationale=f"Clause text matches an escalation trigger for {cr.family}.",
        )

    # Step 6: negotiable deviations
    deviations = cfg.get("negotiable_deviations", [])
    if deviations and _semantic_match(text, deviations, client):
        return ClauseClassification(
            **_base(cr), status=STATUS_DEVIATION,
            reason_code="approved_fallback_available",
            rationale=f"{cr.family} deviates from preferred but maps to an approved fallback.",
        )

    # Step 7: no playbook entry
    return ClauseClassification(
        **_base(cr), status=STATUS_ESCALATE,
        reason_code="no_playbook_entry",
        rationale=f"{cr.family} does not match any accepted or negotiable playbook position.",
    )


def _base(cr: ClauseResult) -> dict:
    return {
        "family": cr.family,
        "extracted_text": cr.extracted_text,
        "source_page": cr.source_page,
        "confidence": cr.confidence,
        "found": cr.found,
    }


def _semantic_match(text: str, candidates: list[str], client: anthropic.Anthropic) -> bool:
    # Fast keyword pass first
    text_lower = text.lower()
    for candidate in candidates:
        if candidate.lower() in text_lower:
            return True

    # LLM semantic similarity fallback
    candidates_str = "\n".join(f"- {c}" for c in candidates)
    prompt = f"""Does the following contract clause text substantially match any of the candidate phrases listed below?

A match means the clause is legally equivalent — same obligations, same thresholds, same scope. A clause that is merely related or in the same topic area does NOT qualify as a match. For example, a liability cap of 3x annual fees does NOT match a cap of 1x annual fees, even though both are fee-based caps.

Contract clause text:
\"\"\"{text}\"\"\"

Candidate phrases:
{candidates_str}

Answer with a single word: YES or NO."""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=5,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = response.content[0].text.strip().upper()
        return answer.startswith("YES")
    except Exception:
        return False
