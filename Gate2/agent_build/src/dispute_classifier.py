"""T-005: Dispute type classification.

Classifies a dispute into the confirmed taxonomy. Taxonomy values are sourced
from the APEX_DISPUTES_OPEN artefact (Gate2-Artefacts/APEX_DISPUTES_OPEN_20260414.csv).

Confirmed taxonomy:
  FUEL_SURCH_DAMAGE  — fuel surcharge dispute arising from a damaged delivery
  DIM_WEIGHT         — dimensional weight charge dispute
  REDELIVERY_FEE     — redelivery fee dispute

Any dispute type outside this set returns UNKNOWN (confidence 0.0) and must
trigger ET-002 (unknown dispute type → senior billing agent). Per D4 §8 Hard
Stop 2, the agent must not attempt to reason by analogy to a similar known type.

DESIGN GAP — NLP path (classify_from_contact_text):
The D4 spec states T-005 also classifies from unstructured customer contact text
(T-001 output) but provides no rules or confidence mechanism. The NLP path raises
NotImplementedError until the spec is resolved (see Build_loop_analysis.md Q-5).

Spec source: D4 §4 T-005; D4 §8 Hard Stop 2; APEX_DISPUTES_OPEN artefact.
"""

from dataclasses import dataclass
from enum import Enum


class DisputeType(str, Enum):
    FUEL_SURCH_DAMAGE = "FUEL_SURCH_DAMAGE"
    DIM_WEIGHT = "DIM_WEIGHT"
    REDELIVERY_FEE = "REDELIVERY_FEE"
    UNKNOWN = "UNKNOWN"


@dataclass
class ClassificationResult:
    dispute_type: DisputeType
    confidence: float       # 1.0 for structured known types; 0.0 for UNKNOWN
    source_field: str       # "DISPUTE_TYPE" (structured) or "NLP_EXTRACTED" (contact text)


def classify_from_structured_field(dispute_type_value: str) -> ClassificationResult:
    """Classify using the structured DISPUTE_TYPE field from APEX_DISPUTES_OPEN.

    Structured classification is deterministic — confidence is 1.0 for known
    types and 0.0 for UNKNOWN. An UNKNOWN result must trigger ET-002.
    """
    try:
        dtype = DisputeType(dispute_type_value.strip().upper())
        confidence = 0.0 if dtype == DisputeType.UNKNOWN else 1.0
    except ValueError:
        dtype = DisputeType.UNKNOWN
        confidence = 0.0

    return ClassificationResult(
        dispute_type=dtype,
        confidence=confidence,
        source_field="DISPUTE_TYPE",
    )


def classify_from_contact_text(contact_text: str) -> ClassificationResult:  # noqa: ARG001
    """NOT IMPLEMENTED — spec gap (Build_loop_analysis.md Q-5).

    NLP classification from unstructured customer contact text requires defined
    rules mapping contact language to dispute types, plus a confidence mechanism.
    Neither is specified in D4.
    """
    raise NotImplementedError(
        "T-005 NLP classification from contact text is not specified in D4. "
        "See Build_loop_analysis.md Q-5: define the rules that map customer "
        "contact language to each dispute type before implementing this path."
    )
