"""
Demo script for Path 3 — FM-A-5 governance hard stop.

Simulates state corruption (ADMIN_CLEARED → ROUTING) immediately after the
routing step, then shows the ET-07 GOVERNANCE_VIOLATION output.

Usage:
  python run_governance_demo.py
"""

import json
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))

from agents.ws1_agent import ClaimContext, process_claim

_ADMIN_MOCK = {
    "classification": "admin",
    "confidence": 0.91,
    "reasoning": (
        "Routine office visit (99213) for annual wellness exam (Z00.00) billed "
        "by a Primary Care Physician — all three signals unambiguously administrative."
    ),
}

claim_path = os.path.join(os.path.dirname(__file__), "fixtures", "CLAIM-ADMIN-01.json")
with open(claim_path, encoding="utf-8") as f:
    claim = json.load(f)

original_transition = ClaimContext.transition


def patched_transition(self, to_state, *, from_state):
    original_transition(self, to_state, from_state=from_state)
    if to_state == "ADMIN_CLEARED":
        self.state = "ROUTING"  # simulate state corruption


print("Claim:        CLAIM-ADMIN-01 (would normally be approved)")
print("Scenario:     State corrupted to ROUTING immediately after ADMIN_CLEARED")
print("Expected:     ET-07 fires, payment_amount absent, trigger_type=GOVERNANCE_VIOLATION")
print("-" * 70)

with patch("agents.ws1_agent.classify_clinical_content", return_value=_ADMIN_MOCK):
    with patch.object(ClaimContext, "transition", patched_transition):
        result = process_claim(claim)

print(json.dumps(result, indent=2))
