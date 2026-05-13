"""
MedFlex WS1 Intake Agent — Field Extractor (Stub)
Source: D4a_capability_spec_WS1_lean.md §4 (WS1-T3), §5 (REQ-A-1), §6 (Decision 2)

DESIGN GAP [DG-1]: The spec defines WHAT to extract (8 required fields) and
the confidence gate thresholds (0.70 / 0.50), but does NOT specify:
  - Which LLM model to call
  - The extraction prompt template
  - How per-field confidence scores are generated (LLM logprobs? self-report?
    a separate calibration pass?)
  - The specialty synonym mapping (spec lists canonical enum values but not
    the synonym-to-canonical mapping — see §14 A-5)

This module provides the extraction interface the rest of the pipeline depends on.
The actual LLM call is a stub that must be replaced with a real implementation
once the above design gaps are resolved (see D5B questions Q-1 through Q-3).

Caller contract: extractor returns ExtractionResult; caller feeds it into
apply_confidence_gate() in classifier.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol

from .models import SpecialtyRequired, CredentialLevel


@dataclass
class ExtractionResult:
    """
    Raw output from the LLM extraction pass.
    All fields are Optional — the extractor may fail to parse any of them.
    confidence_scores keys match REQUIRED_FIELDS in classifier.py.
    """
    facility_name: Optional[str] = None        # Raw extracted name; resolver maps to facility_id
    unit_type: Optional[str] = None
    specialty_raw: Optional[str] = None        # Pre-normalisation; classifier maps to enum
    credential_raw: Optional[str] = None       # Pre-normalisation
    shift_datetime_start: Optional[datetime] = None
    shift_datetime_end: Optional[datetime] = None
    urgency_text: Optional[str] = None         # Raw text that triggered urgency signal
    special_notes: Optional[str] = None
    confidence_scores: dict[str, float] = field(default_factory=dict)


class LLMExtractorProtocol(Protocol):
    """
    Interface contract for the LLM extraction backend.
    Concrete implementations (OpenAI, Claude, etc.) must satisfy this signature.
    The spec does not name a model — this is DESIGN GAP [DG-1].
    """
    def extract(self, message_text: str) -> ExtractionResult:
        ...


class StubExtractor:
    """
    Stub implementation for development and testing.
    Returns deterministic low-confidence results so the confidence gate
    always triggers HITL — safe default for an unimplemented extractor.

    Replace with a real LLM-backed extractor before production deployment.
    """

    def extract(self, message_text: str) -> ExtractionResult:
        # All confidence scores set to 0.0 — forces NEEDS_COORDINATOR_INPUT
        # for every field. This is intentionally conservative for the stub.
        return ExtractionResult(
            confidence_scores={
                "facility_id":          0.0,
                "unit_type":            0.0,
                "specialty_required":   0.0,
                "credential_level":     0.0,
                "shift_datetime_start": 0.0,
                "shift_datetime_end":   0.0,
                "urgency":              0.0,
            }
        )


# ---------------------------------------------------------------------------
# Specialty normalisation (D4a §1 in-scope: "normalise extracted specialty
# string to canonical enum value")
#
# NOTE [assumption A-D5B-4]: The specialty taxonomy synonym list is referenced
# in §1 as "Static config (agent procedural memory)" but the actual synonym
# mappings are not provided in the spec (see §14 A-5). The mapping below is
# a placeholder using obvious synonyms only. Must be replaced with the client-
# confirmed taxonomy before production.
# ---------------------------------------------------------------------------

_SPECIALTY_SYNONYMS: dict[str, SpecialtyRequired] = {
    # Canonical
    "rn_general":   SpecialtyRequired.RN_GENERAL,
    "rn_icu":       SpecialtyRequired.RN_ICU,
    "rn_ed":        SpecialtyRequired.RN_ED,
    "rn_er":        SpecialtyRequired.RN_ED,       # synonym
    "rn_pacu":      SpecialtyRequired.RN_PACU,
    "rn_or":        SpecialtyRequired.RN_OR,
    "lpn":          SpecialtyRequired.LPN,
    "cna":          SpecialtyRequired.CNA,
    "rn_tele":      SpecialtyRequired.RN_TELE,
    "telemetry":    SpecialtyRequired.RN_TELE,     # synonym
    # Common shorthand
    "icu":          SpecialtyRequired.RN_ICU,
    "ed":           SpecialtyRequired.RN_ED,
    "er":           SpecialtyRequired.RN_ED,
    "or":           SpecialtyRequired.RN_OR,
    "pacu":         SpecialtyRequired.RN_PACU,
    "tele":         SpecialtyRequired.RN_TELE,
    "general":      SpecialtyRequired.RN_GENERAL,
    "med surg":     SpecialtyRequired.RN_GENERAL,
    "med/surg":     SpecialtyRequired.RN_GENERAL,
}

_CREDENTIAL_SYNONYMS: dict[str, CredentialLevel] = {
    "rn":            CredentialLevel.RN,
    "registered nurse": CredentialLevel.RN,
    "lpn":           CredentialLevel.LPN,
    "licensed practical nurse": CredentialLevel.LPN,
    "cna":           CredentialLevel.CNA,
    "certified nursing assistant": CredentialLevel.CNA,
    "np":            CredentialLevel.NP,
    "nurse practitioner": CredentialLevel.NP,
}


def normalise_specialty(raw: Optional[str]) -> SpecialtyRequired:
    if not raw:
        return SpecialtyRequired.UNRESOLVED
    key = raw.strip().lower()
    return _SPECIALTY_SYNONYMS.get(key, SpecialtyRequired.UNRESOLVED)


def normalise_credential(raw: Optional[str]) -> CredentialLevel:
    if not raw:
        return CredentialLevel.UNRESOLVED
    key = raw.strip().lower()
    return _CREDENTIAL_SYNONYMS.get(key, CredentialLevel.UNRESOLVED)
