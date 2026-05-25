"""
Prior authorisation lookup stub (S-04).
Returns PRESENT_EXACT_MATCH for all fixture claims.
authorized_units matches claimed_units so the tolerance rule never fires.
"""


def check_prior_auth(claim: dict) -> dict:
    claimed_units = claim["procedure_quantities"][0] if claim.get("procedure_quantities") else 1
    return {
        "status": "present_exact",
        "prior_auth_status": "PRESENT_EXACT_MATCH",
        "authorized_units": claimed_units,
        "expiry_date": "2026-12-31",
        "auth_record_id": f"PA-2026-{claim['claim_id']}",
    }
