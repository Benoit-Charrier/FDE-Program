"""
Fee schedule lookup stub (S-05).
Returns contracted_rate and cost_sharing_proportion from a static mock table.
payment_amount = contracted_rate * (1 - cost_sharing_proportion), rounded half-up to 2dp.
"""

import decimal

_RATE_TABLE = {
    "99213": {"contracted_rate": "106.25", "cost_sharing_proportion": "0.20"},
    "99214": {"contracted_rate": "106.25", "cost_sharing_proportion": "0.20"},
    "27447": {"contracted_rate": "390.63", "cost_sharing_proportion": "0.20"},
    "97110": {"contracted_rate": "56.25",  "cost_sharing_proportion": "0.20"},
}
_DEFAULT = {"contracted_rate": "125.00", "cost_sharing_proportion": "0.20"}


def get_payment_amount(claim: dict) -> float:
    procedure_code = claim["procedure_codes"][0]
    row = _RATE_TABLE.get(procedure_code, _DEFAULT)
    rate = decimal.Decimal(row["contracted_rate"])
    share = decimal.Decimal(row["cost_sharing_proportion"])
    amount = rate * (1 - share)
    return float(amount.quantize(decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP))
