"""
Code validity check stub (S-03).
Returns valid for all codes in the fixture set.
"""


def check_code_validity(claim: dict) -> dict:
    return {
        "status": "valid",
        "invalid_codes": [],
    }
