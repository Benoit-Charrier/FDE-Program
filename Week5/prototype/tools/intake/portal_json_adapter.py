"""
Adapter: Claims Pack portal-JSON → WS1 normalised claim record.

The Claims Pack portal-JSON shape uses nested objects (submitter, patient,
insurance, service_lines). WS1 expects a flat dict with procedure_codes,
diagnosis_codes, member_id, etc.
"""


def adapt_portal_json(raw: dict, source_file: str = "") -> dict:
    """
    Convert a Claims Pack portal-JSON claim to NormalizedClaimInput canonical format.

    Raises ValueError if hard-required fields (submission_id, service_lines,
    diagnoses) are missing.
    """
    submission_id = raw.get("submission_id")
    if not submission_id:
        raise ValueError("portal-JSON missing required field: submission_id")

    service_lines = raw.get("service_lines", [])
    diagnoses = raw.get("diagnoses", [])

    if not service_lines:
        raise ValueError(f"{submission_id}: no service_lines")
    if not diagnoses:
        raise ValueError(f"{submission_id}: no diagnoses")

    submitter = raw.get("submitter", {})
    insurance = raw.get("insurance", {})

    warnings: list = []

    member_id = insurance.get("member_id") or ""
    if not member_id:
        member_id = "UNKNOWN_MEMBER"
        warnings.append("member_id_missing")

    provider_npi = submitter.get("npi") or ""
    if not provider_npi:
        provider_npi = "UNKNOWN_NPI"
        warnings.append("provider_npi_missing")

    billed_amount = raw.get("total_charge_amount", 0.0) or 0.0
    if billed_amount == 0.0:
        warnings.append("billed_amount_zero")

    # Date of service: earliest service-line date
    dates = [sl.get("date_of_service") for sl in service_lines if sl.get("date_of_service")]
    date_of_service = min(dates) if dates else "unknown"
    if date_of_service == "unknown":
        warnings.append("date_of_service_missing")

    payer_id = insurance.get("payer_id") or None
    group_id = insurance.get("group_id") or None

    return {
        "claim_id":             submission_id,
        "member_id":            member_id,
        "provider_npi":         provider_npi,
        "provider_specialty":   submitter.get("specialty") or "Unknown",
        "date_of_service":      date_of_service,
        "diagnosis_codes":      [d["code"] for d in diagnoses],
        "procedure_codes":      [sl["cpt_code"] for sl in service_lines],
        "procedure_quantities": [sl.get("units", 1) for sl in service_lines],
        "billed_amount":        billed_amount,
        "payer_id":             payer_id,
        "group_id":             group_id,
        "source_format":        "PORTAL_FORM",
        "source_file":          source_file,
        "intake_warnings":      warnings,
    }
