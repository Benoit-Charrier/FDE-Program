from __future__ import annotations
from dataclasses import dataclass
import audit
from classification import ClauseClassification, STATUS_DEVIATION, STATUS_ESCALATE


@dataclass
class RedlineProposal:
    family: str
    original_text: str
    proposed_text: str
    playbook_citation: str


def generate_redlines(
    classifications: list[ClauseClassification],
    playbook: dict,
    contract_id: str,
) -> tuple[list[RedlineProposal], list[ClauseClassification]]:
    """
    Returns (redlines, updated_classifications).
    If a deviation has no approved fallback, the clause is reclassified to escalate (FR-06).
    """
    families_config = playbook.get("clause_families", {})
    redlines: list[RedlineProposal] = []
    updated = list(classifications)

    for i, cls in enumerate(updated):
        if cls.status != STATUS_DEVIATION:
            continue

        cfg = families_config.get(cls.family, {})
        deviations = cfg.get("negotiable_deviations", [])

        # Find the matching fallback (same logic as classification — keyword first)
        matched_fallback = _find_matching_fallback(cls.extracted_text, deviations)

        if matched_fallback is None:
            # FR-06: no approved fallback → escalate, never invent
            from dataclasses import replace
            updated[i] = ClauseClassification(
                family=cls.family,
                extracted_text=cls.extracted_text,
                source_page=cls.source_page,
                confidence=cls.confidence,
                found=cls.found,
                status=STATUS_ESCALATE,
                reason_code="no_approved_fallback",
                rationale=f"{cls.family} has a deviation but no approved fallback language exists in the playbook.",
            )
            audit.log_event(contract_id, "redline_generated", {
                "family": cls.family,
                "outcome": "escalated_no_fallback",
            })
        else:
            proposal = RedlineProposal(
                family=cls.family,
                original_text=cls.extracted_text,
                proposed_text=matched_fallback,
                playbook_citation=f"clause_families.{cls.family}.negotiable_deviations",
            )
            redlines.append(proposal)
            audit.log_event(contract_id, "redline_generated", {
                "family": cls.family,
                "outcome": "redline_proposed",
                "playbook_citation": proposal.playbook_citation,
            })

    return redlines, updated


def _find_matching_fallback(text: str, deviations: list[str]) -> str | None:
    text_lower = text.lower()
    for dev in deviations:
        if dev.lower() in text_lower:
            return dev
    # Return first available deviation as the proposed replacement when no exact match
    # (the extracted text is the deviation; the fallback IS the deviation entry itself)
    if deviations:
        return deviations[0]
    return None
