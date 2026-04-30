"""
Clause locator: identifies which section of a contract corresponds to each
of the 7 playbook clause types using heading pattern matching.
Derived from D4 T-04, D5 §5 (clause heading taxonomy), CLAUDE.md §6.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .models import TaskUnitType
from .document_parser import ParsedDocument, DocumentSection
from .config import CONFIDENCE_THRESHOLD

# Ordered by specificity: more specific patterns first → higher match confidence.
HEADING_PATTERNS: dict[TaskUnitType, list[str]] = {
    TaskUnitType.LIABILITY_CAP: [
        r"limitation\s+of\s+liabilit",
        r"cap\s+on\s+liabilit",
        r"maximum\s+liabilit",
        r"liabilit",
        r"damages",
    ],
    TaskUnitType.DATA_PROCESSING_AGREEMENT: [
        r"data\s+processing\s+agreement",
        r"\bdpa\b",
        r"data\s+protection",
        r"processing\s+of\s+personal\s+data",
        r"personal\s+data",
        r"gdpr",
        r"data\s+privacy",
    ],
    TaskUnitType.TERMINATION_CLAUSE: [
        r"terminat(?:ion|e)",
        r"right\s+to\s+terminat",
        r"cancellat",
        r"end\s+of\s+(?:agreement|contract|term)",
        r"notice\s+(?:period|of\s+terminat)",
    ],
    TaskUnitType.IP_OWNERSHIP: [
        r"intellectual\s+propert",
        r"ip\s+own",
        r"ownership\s+of\s+ip",
        r"copyright",
        r"proprietary\s+rights",
        r"work\s+product",
        r"invention",
    ],
    TaskUnitType.SLA_COMMITMENTS: [
        r"service\s+level\s+agreement",
        r"\bsla\b",
        r"uptime",
        r"availability\s+(?:guarantee|commitment|target)",
        r"performance\s+(?:standard|guarantee|commitment)",
        r"response\s+time",
    ],
    TaskUnitType.GOVERNING_LAW: [
        r"governing\s+law",
        r"choice\s+of\s+law",
        r"applicable\s+law",
        r"governing\s+jurisdiction",
        r"jurisdiction",
        r"dispute\s+resolution",
    ],
    TaskUnitType.INDEMNITY_SCOPE: [
        r"indemnif(?:y|ication|ies)",
        r"indemnit",
        r"hold\s+harmless",
        r"defend(?:.*)\s+claim",
        r"third.party\s+claim",
    ],
}


@dataclass
class LocatedClause:
    task_unit_type: TaskUnitType
    heading: str
    extracted_text: str
    match_confidence: float
    matched_pattern: str
    section_index: int


@dataclass
class ClauseLocationResult:
    located: list[LocatedClause]
    # (clause_type, confidence_that_clause_is_absent)
    missing: list[tuple[TaskUnitType, float]]
    headings_searched: list[str]


def locate_clauses(doc: ParsedDocument) -> ClauseLocationResult:
    """
    Searches all document sections for each of the 7 clause types.
    Returns located clauses and missing clause types with absence confidence.
    """
    located: list[LocatedClause] = []
    found_types: set[TaskUnitType] = set()

    for clause_type, patterns in HEADING_PATTERNS.items():
        best: Optional[tuple[int, DocumentSection, float, str]] = None  # (idx, section, conf, pattern)

        for i, section in enumerate(doc.sections):
            for j, pattern in enumerate(patterns):
                # Try heading first (higher confidence)
                if re.search(pattern, section.heading, re.IGNORECASE):
                    confidence = _pattern_confidence(j, source="heading")
                    if best is None or confidence > best[2]:
                        best = (i, section, confidence, pattern)
                    break
                # Fall back to first 200 chars of body (lower confidence)
                if re.search(pattern, section.body[:200], re.IGNORECASE):
                    confidence = _pattern_confidence(j, source="body")
                    if best is None or confidence > best[2]:
                        best = (i, section, confidence, pattern)
                    break

        if best:
            idx, section, confidence, pattern = best
            located.append(LocatedClause(
                task_unit_type=clause_type,
                heading=section.heading,
                extracted_text=section.body,
                match_confidence=confidence,
                matched_pattern=pattern,
                section_index=idx,
            ))
            found_types.add(clause_type)

    missing: list[tuple[TaskUnitType, float]] = []
    for clause_type in TaskUnitType:
        if clause_type not in found_types:
            missing.append((clause_type, _absence_confidence(doc, clause_type)))

    return ClauseLocationResult(
        located=located,
        missing=missing,
        headings_searched=doc.raw_headings,
    )


def _pattern_confidence(pattern_index: int, source: str) -> float:
    """
    More specific patterns (lower index) → higher confidence.
    Heading match → higher confidence than body match.
    """
    base = 0.95 if source == "heading" else 0.70
    penalty = pattern_index * 0.04
    return max(0.60, base - penalty)


def _absence_confidence(doc: ParsedDocument, clause_type: TaskUnitType) -> float:
    """
    Confidence that the clause is genuinely absent (not just under an atypical heading).
    Searches full document text; if any keyword found in body, confidence on absence drops.
    """
    patterns = HEADING_PATTERNS[clause_type]
    full_lower = doc.full_text.lower()
    for pattern in patterns:
        if re.search(pattern, full_lower, re.IGNORECASE):
            # Keyword found somewhere in the document — likely embedded under atypical heading
            return 0.40
    # No keyword at all → clause is probably genuinely absent
    return 0.92
