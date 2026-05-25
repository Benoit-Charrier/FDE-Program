"""
Eligibility lookup stub (S-02).
Returns INACTIVE for the sentinel member ID used by CLAIM-ELIG-01;
returns ACTIVE for all other member IDs.
"""

_DISCREPANCY_MEMBER_IDS = {"GHS-MBR-INVALID"}


def check_eligibility(claim: dict) -> dict:
    member_id = claim["member_id"]
    if member_id in _DISCREPANCY_MEMBER_IDS:
        return {
            "status": "discrepancy",
            "eligibility_status": "INACTIVE",
            "coverage_start_date": None,
            "coverage_end_date": None,
            "error_code": "MEMBER_NOT_ACTIVE",
        }
    return {
        "status": "eligible",
        "eligibility_status": "ACTIVE",
        "coverage_start_date": "2026-01-01",
        "coverage_end_date": "2026-12-31",
        "error_code": None,
    }
