"""
CMS-1500 OCR text parser.

Parses pre-extracted OCR text from CMS-1500 paper claim forms.
The OCR text has character-level noise: dropped letters, spaces inserted
mid-word, substituted characters (0↔O, 1↔I, 5↔S, etc.).

Anchor strategy: search for partial field label strings that survive
OCR noise, then extract the value on the same line.
"""

import re
from datetime import datetime

from tools.intake.edi_parser import _SPECIALTY_HINTS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _first_match(pattern: str, text: str) -> str:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _squish(s: str) -> str:
    """Remove all whitespace (OCR inserts spaces mid-token)."""
    return re.sub(r"\s+", "", s)


# ---------------------------------------------------------------------------
# Section parsers
# ---------------------------------------------------------------------------

def _parse_diagnosis_codes(text: str) -> tuple:
    """
    Extract ICD-10 codes from Field 21 (A–D labeled lines).
    Returns (codes, has_ocr_issue).
    OCR issue = at least one labeled line yielded a code missing its leading letter.
    """
    # Primary: "21." + any garbled spelling of DIAGNOSIS
    section_m = re.search(r"2\d?\.?\s+DI[A-Z\s]{0,4}(?:AG|GN|AG)", text, re.IGNORECASE)
    # Fallback: anchor on "ICD" which survives OCR better
    if not section_m:
        section_m = re.search(r"ICD[-\.\s]?10", text, re.IGNORECASE)
    if not section_m:
        return [], False

    section = text[section_m.end():]
    end_m = re.search(r"\n\s*2[234567]\.", section)
    if end_m:
        section = section[: end_m.start()]

    codes = []
    ocr_issue = False

    for line in section.splitlines():
        line = line.strip()
        # Label A. through D. followed by the code then optional (description)
        m = re.match(r"[A-D]\.?\s+([^(]+)", line, re.IGNORECASE)
        if not m:
            continue
        raw = _squish(m.group(1)).upper()
        if not raw:
            continue
        codes.append(raw)
        # Flag if code doesn't start with a letter (OCR dropped leading char)
        if not raw[0].isalpha():
            ocr_issue = True

    return codes, ocr_issue


def _normalise_service_date(raw: str) -> str | None:
    """Best-effort normalisation of an OCR-garbled date to YYYY-MM-DD."""
    raw = raw.strip()
    # YYYY-MM-DD or YYYY-MM-D
    m = re.match(r"^(\d{4})-(\d{2})-(\d{1,2})$", raw)
    if m:
        y, mo, d = m.group(1), m.group(2), m.group(3).zfill(2)
        try:
            return datetime.strptime(f"{y}-{mo}-{d}", "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            pass
    # YYYYMMDD (hyphens dropped entirely)
    m = re.match(r"^(\d{4})(\d{2})(\d{2})$", raw)
    if m:
        try:
            return datetime.strptime(raw, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            pass
    # YYYY-MMDD (second hyphen dropped)
    m = re.match(r"^(\d{4})-(\d{4})$", raw)
    if m:
        try:
            return datetime.strptime(m.group(1) + m.group(2), "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            pass
    # YY-MM-DD (century prefix dropped)
    m = re.match(r"^(\d{2})-(\d{2})-(\d{1,2})$", raw)
    if m:
        y, mo, d = "20" + m.group(1), m.group(2), m.group(3).zfill(2)
        try:
            return datetime.strptime(f"{y}-{mo}-{d}", "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def _parse_service_lines(text: str) -> tuple:
    """
    Extract procedure_codes, procedure_quantities, date_of_service from Field 24.
    Returns (procedure_codes, procedure_quantities, date_of_service | None).
    """
    # Primary: "24." section header; fallback: "DATE OF SERVICE" column header
    section_m = re.search(
        r"2\d?\.?\s+SERVICE\s+LINE|DATE\s+OF\s+SERVICE\b",
        text, re.IGNORECASE,
    )
    if not section_m:
        return [], [], None

    section = text[section_m.end():]
    end_m = re.search(r"\n\s*2[567]\.", section)
    if end_m:
        section = section[: end_m.start()]

    procedure_codes: list = []
    procedure_quantities: list = []
    dates: list = []

    for line in section.splitlines():
        line = line.strip()
        # Date anchor: flexible — YYYY-MM-DD, YYYY-MM-D, YYYY-MMDD, YYYYMMDD, YY-MM-DD
        m = re.match(r"(\d{4}[-]?\d{2}[-]?\d{1,2}|\d{2}-\d{2}-\d{1,2})\s+(.*)", line)
        if not m:
            continue

        raw_date, rest = m.group(1), m.group(2).strip()
        normalised = _normalise_service_date(raw_date)
        if normalised:
            try:
                dates.append(datetime.strptime(normalised, "%Y-%m-%d"))
            except ValueError:
                pass

        tokens = rest.split()
        if not tokens:
            continue

        # First token after date is POS (1–2 digits) — skip it
        pos_idx = 0
        if tokens[pos_idx].isdigit() and len(tokens[pos_idx]) <= 2:
            pos_idx += 1

        if pos_idx >= len(tokens):
            continue

        # CPT: 5-char numeric token, possibly OCR-split across two tokens
        cpt_tok = tokens[pos_idx] if pos_idx < len(tokens) else ""
        qty_idx = pos_idx + 1

        if (
            len(cpt_tok) <= 2
            and cpt_tok.isdigit()
            and qty_idx < len(tokens)
            and tokens[qty_idx].isdigit()
            and len(tokens[qty_idx]) == 3
        ):
            # Merge: e.g. "9" + "110" → "9110"  (OCR split a 4-5 digit code)
            cpt_tok = cpt_tok + tokens[qty_idx]
            qty_idx += 1

        cpt = _squish(cpt_tok)

        # Skip optional 2-char alphabetic modifier token
        if qty_idx < len(tokens) and tokens[qty_idx].isalpha() and len(tokens[qty_idx]) == 2:
            qty_idx += 1

        # Skip DX-PTR (single digit)
        if qty_idx < len(tokens) and tokens[qty_idx].isdigit() and len(tokens[qty_idx]) == 1:
            qty_idx += 1

        # Units
        qty = 1
        if qty_idx < len(tokens) and tokens[qty_idx].isdigit():
            try:
                qty = int(tokens[qty_idx])
            except ValueError:
                pass

        if cpt:
            procedure_codes.append(cpt)
            procedure_quantities.append(qty)

    date_of_service = min(dates).strftime("%Y-%m-%d") if dates else None
    return procedure_codes, procedure_quantities, date_of_service


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def parse_cms1500_ocr(raw: str, source_file: str = "") -> dict:
    """
    Parse pre-extracted CMS-1500 OCR text and return a NormalizedClaimInput dict.

    Raises ValueError if hard-required fields (claim_id, diagnosis_codes,
    procedure_codes) cannot be extracted.
    """
    text = raw
    warnings: list = []

    # --- claim_id (Field 26) ---
    # "ACCOUNT" OCR variants: ACCONT, ACCONUT, etc. — lazy match between PATIENT and ACC
    raw_id = _first_match(
        r"2\d?\.?\s+PATIENT[^\n]*?ACC[A-Z]*\s+NO\.?:?\s*([A-Za-z0-9 \-]+)",
        text,
    )
    claim_id = _squish(raw_id)
    if not claim_id:
        # Fallback: derive from source filename (reliable for Claims Pack batch files)
        if source_file:
            from pathlib import Path
            claim_id = Path(source_file).stem
            warnings.append("ocr_field_unparseable")
        else:
            raise ValueError("CMS-1500 OCR missing required field: claim_id (Field 26)")
    if not re.match(r"^CLM-\d{4}-\d{7}$", claim_id):
        warnings.append("ocr_field_unparseable")

    # --- member_id (Field 1a) ---
    raw_member = _first_match(
        r"1a?\.?\s+I[A-Z\s'\.]*I\.?D\.?\s+NUMBER:?\s*([A-Za-z0-9 \-]+)",
        text,
    )
    member_id = _squish(raw_member)
    if not member_id:
        member_id = "UNKNOWN_MEMBER"
        warnings.append("member_id_missing")

    # --- diagnosis codes (Field 21) ---
    diagnosis_codes, dx_ocr_issue = _parse_diagnosis_codes(text)
    if not diagnosis_codes:
        raise ValueError(f"{claim_id}: no diagnosis codes (Field 21)")
    if dx_ocr_issue:
        warnings.append("ocr_confidence_low")

    # --- service lines (Field 24) ---
    procedure_codes, procedure_quantities, date_of_service = _parse_service_lines(text)
    if not procedure_codes:
        raise ValueError(f"{claim_id}: no procedure codes (Field 24)")

    # --- date_of_service ---
    if not date_of_service:
        date_of_service = "unknown"
        warnings.append("date_of_service_missing")

    # --- billed amount (Field 28) ---
    raw_amount = _first_match(
        r"28\.?\s+TOTAL\s*CHARG[ES]*:?\s*\$?\s*([\d,\.]+)",
        text,
    )
    try:
        billed_amount = float(raw_amount.replace(",", "")) if raw_amount else 0.0
    except ValueError:
        billed_amount = 0.0
    if billed_amount == 0.0:
        warnings.append("billed_amount_zero")

    # --- provider NPI (Field 33 NPI line) ---
    npi_m = re.search(r"\bNPI:?\s*([\d][\d\s]{6,13})", text, re.IGNORECASE)
    if npi_m:
        provider_npi = _squish(npi_m.group(1).strip())
        if len(provider_npi) < 7:
            provider_npi = "UNKNOWN_NPI"
            warnings.append("provider_npi_missing")
    else:
        provider_npi = "UNKNOWN_NPI"
        warnings.append("provider_npi_missing")

    # --- provider name / specialty (Field 31: physician signature) ---
    provider_name = _first_match(
        r"3[13]\.?\s+S[A-Z\s]*PHYSICIAN[:\s]+(.+)",
        text,
    )
    if not provider_name:
        # Fallback: billing provider info line
        provider_name = _first_match(
            r"33\.?\s+BILLING\s+PROVIDER\s+INFO:?\s*([A-Za-z ,\.]+)",
            text,
        )
    provider_specialty = "Unknown"
    if provider_name:
        name_upper = provider_name.upper()
        for hint, specialty in _SPECIALTY_HINTS:
            if hint in name_upper:
                provider_specialty = specialty
                break

    # --- payer (Field 11c — plan name, not machine ID) ---
    payer_name = _first_match(
        r"11c\.?\s+INSU[RN][AE]NCE\s+PLAN\s+NAME:?\s*(.+)",
        text,
    )
    if payer_name:
        payer_id = payer_name.strip()
        warnings.append("payer_id_is_name")
    else:
        payer_id = None

    # --- group_id (Field 11) ---
    raw_group = _first_match(
        r"11\.?\s+INSUR[A-Z'\s]+POLIC[YI]\s+GROUP\s+NUMBER:?\s*([A-Za-z0-9\- ]+)",
        text,
    )
    group_id = _squish(raw_group) if raw_group else None

    return {
        "claim_id":             claim_id,
        "member_id":            member_id,
        "provider_npi":         provider_npi,
        "provider_specialty":   provider_specialty,
        "date_of_service":      date_of_service,
        "diagnosis_codes":      diagnosis_codes,
        "procedure_codes":      procedure_codes,
        "procedure_quantities": procedure_quantities,
        "billed_amount":        billed_amount,
        "payer_id":             payer_id,
        "group_id":             group_id,
        "source_format":        "CMS1500_OCR",
        "source_file":          source_file,
        "intake_warnings":      warnings,
    }
