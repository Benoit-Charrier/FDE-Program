"""
EDI X12 837P and 837I parser.

Extracts the normalized WS1 claim record from a single-transaction 837 file.

Segment conventions (per Claims Pack README):
  element separator : '*'
  segment terminator: '~'
  component separator: ':'

Supported transaction sets:
  005010X222A1  →  EDI_837P (Professional)
  005010X223A2  →  EDI_837I (Institutional)
"""

from datetime import datetime


def _parse_segments(raw: str) -> list:
    """Split raw EDI text into list of element-lists, one per segment."""
    if not raw.lstrip().startswith("ISA"):
        raise ValueError("EDI file does not begin with ISA segment")
    # Element separator is always the character at index 3
    elem_sep = raw.lstrip()[3]
    # Segment terminator: strip trailing whitespace then take last char
    raw_stripped = raw.replace("\r", "").replace("\n", "")
    seg_term = raw.rstrip()[-1]
    result = []
    for seg in raw_stripped.split(seg_term):
        seg = seg.strip()
        if seg:
            result.append(seg.split(elem_sep))
    return result


def _yyyymmdd(s: str) -> str:
    """Convert YYYYMMDD → YYYY-MM-DD. Return input unchanged if unrecognised."""
    try:
        return datetime.strptime(s, "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        return s


# Provider name → specialty heuristics (checked in order; first match wins)
_SPECIALTY_HINTS = [
    (" MD",           "Physician (MD)"),
    (", MD",          "Physician (MD)"),
    (" DO",           "Physician (DO)"),
    (", DO",          "Physician (DO)"),
    (" PA",           "Advanced Practice Provider (PA)"),
    (", PA",          "Advanced Practice Provider (PA)"),
    (" NP",           "Advanced Practice Provider (NP)"),
    (", NP",          "Advanced Practice Provider (NP)"),
    ("CARDIOLOGY",    "Cardiologist"),
    ("ORTHOPEDIC",    "Orthopaedic Surgeon"),
    ("ORTHOPAEDIC",   "Orthopaedic Surgeon"),
    ("PEDIATRIC",     "Pediatrician"),
    ("RADIOLOGY",     "Radiologist"),
    ("ONCOLOGY",      "Oncologist"),
    ("HOSPITAL",      "Hospital"),
    ("MEDICAL CENTER","Hospital"),
    ("HEALTH CENTER", "Community Health Center"),
]


def _derive_specialty(provider_name: str, transaction_set: str) -> str:
    if "X223A2" in transaction_set:
        return "Hospital/Institutional"
    name_upper = provider_name.upper()
    for hint, specialty in _SPECIALTY_HINTS:
        if hint in name_upper:
            return specialty
    return "Physician"


def parse_edi_837(raw: str, source_file: str = "") -> dict:
    """
    Parse an EDI 837P or 837I transaction set and return a NormalizedClaimInput dict.

    Raises ValueError if hard-required fields (claim_id, procedure_codes,
    diagnosis_codes) cannot be extracted.
    """
    segments = _parse_segments(raw)

    transaction_set = ""
    claim_id = None
    member_id = None
    provider_npi = None
    provider_name = ""
    payer_id = None
    billed_amount = None
    date_of_service = None
    diagnosis_codes: list = []
    procedure_codes: list = []
    procedure_quantities: list = []

    for elems in segments:
        if not elems:
            continue
        seg_id = elems[0]

        if seg_id == "GS" and len(elems) > 8:
            transaction_set = elems[8]

        elif seg_id == "CLM" and len(elems) > 2:
            claim_id = elems[1]
            try:
                billed_amount = float(elems[2])
            except (ValueError, IndexError):
                pass

        elif seg_id == "NM1" and len(elems) > 1:
            qualifier = elems[1]
            # element[9] = identification code (NPI or member ID)
            id_value = elems[9] if len(elems) > 9 else ""
            if qualifier == "85":       # Billing / rendering provider
                provider_npi = id_value
                provider_name = elems[3] if len(elems) > 3 else ""
            elif qualifier == "IL":     # Insured / subscriber
                member_id = id_value
            elif qualifier == "40":     # Payer (receiver)
                payer_id = id_value

        elif seg_id == "HI":
            # HI*ABK:R519*ABF:J449~ — AB-prefixed qualifiers are ICD-10 codes
            for elem in elems[1:]:
                if ":" in elem:
                    parts = elem.split(":")
                    qualifier = parts[0]
                    code = parts[1] if len(parts) > 1 else ""
                    if qualifier.startswith("AB") and code:
                        diagnosis_codes.append(code)

        elif seg_id == "SV1" and len(elems) > 4:
            # SV1*HC:99214*161.03*UN*1*11**1~
            svc = elems[1]
            cpt = svc.split(":")[1] if ":" in svc else svc
            procedure_codes.append(cpt)
            try:
                units = int(elems[4]) if elems[4] else 1
            except ValueError:
                units = 1
            procedure_quantities.append(units)

        elif seg_id == "DTP" and len(elems) > 3:
            if elems[1] == "472" and date_of_service is None:
                date_of_service = _yyyymmdd(elems[3])

    # claim_id, procedure_codes, and diagnosis_codes are hard-required — the pipeline
    # cannot run without them. Other fields default to sentinels with warnings so
    # the pipeline can report data-quality issues rather than crashing.
    missing = []
    if not claim_id:
        missing.append("claim_id")
    if not procedure_codes:
        missing.append("procedure_codes")
    if not diagnosis_codes:
        missing.append("diagnosis_codes")
    if missing:
        raise ValueError(f"EDI parse missing required fields: {missing}")

    warnings: list = []
    if not member_id:
        member_id = "UNKNOWN_MEMBER"
        warnings.append("member_id_missing")
    if not provider_npi:
        provider_npi = "UNKNOWN_NPI"
        warnings.append("provider_npi_empty_segment")
    if not date_of_service:
        warnings.append("date_of_service_missing")
    if not billed_amount:
        warnings.append("billed_amount_zero")

    fmt = "EDI_837I" if "X223A2" in transaction_set else "EDI_837P"

    return {
        "claim_id":             claim_id,
        "member_id":            member_id,
        "provider_npi":         provider_npi,
        "provider_specialty":   _derive_specialty(provider_name, transaction_set),
        "date_of_service":      date_of_service or "unknown",
        "diagnosis_codes":      diagnosis_codes,
        "procedure_codes":      procedure_codes,
        "procedure_quantities": procedure_quantities,
        "billed_amount":        billed_amount or 0.0,
        "payer_id":             payer_id or None,
        "source_format":        fmt,
        "source_file":          source_file,
        "intake_warnings":      warnings,
    }
