# C12: Prototype Scope Decision
**Engagement:** Greenfield Health Systems — Medical Claims Adjudication Transformation
**Phase:** Capstone Build — Scope Boundary
**Prepared:** 2026-05-21
**Source:** `Deliverables/C3_agentic_solution_architecture.md`, `Deliverables/C1_token_economics_model.md`

---

## Recommended prototype scope: WS1 Administrative Adjudication Agent — core claim pipeline

**One agentic flow end-to-end.** A claim arrives as a structured JSON object and passes through:

1. Eligibility lookup (stubbed tool — returns eligible / discrepancy)
2. Code validity check (stubbed tool — returns valid / invalid pair)
3. Prior auth lookup (stubbed tool — returns present / partial match / absent)
4. Clinical content classification (real LLM call — returns `{classification, confidence, reasoning}`)
5. Fee schedule lookup (stubbed tool — returns rate)
6. Output: auto-approved with payment amount, OR HITL escalation object with structured reason

---

## The three required paths

| Path | What fires | What it demonstrates |
|---|---|---|
| **Happy path** | All tool calls pass; LLM routes as `admin` with confidence ≥ threshold | Full state machine runs; claim exits auto-approved |
| **Failure-mode escalation** | LLM returns `confidence < threshold` on a borderline claim | HITL escalation fires with structured reason, confidence score, and claim context |
| **Edge case** | Prior auth returns partial match (10 units authorised, 12 claimed) | Configurable tolerance rule resolves within-tolerance automatically; outside-tolerance escalates |

---

## Step-by-step implementation plan (from ws1_deep_dive.md §3)

Each of the 10 steps in the WS1 pipeline is assigned one of three statuses: **Implement** (built and tested), **Stub** (hardcoded mock return, no real logic), or **Out of scope** (not present in the prototype).

| Step | ws1_deep_dive handling | Prototype status | Implementation note |
|---|---|---|---|
| Format parsing and field extraction (EDI 837, PDF, portal) | Automated (rule / code) | **Out of scope** | Claim arrives as a pre-structured JSON object; no parsing logic needed for the demo |
| Member eligibility lookup | Automated (API call) | **Stub** | Tool returns `eligible` for the happy path; returns `discrepancy` for a designated mock claim ID (fixture `CLAIM-ELIG-01`) — not a required demo path, but proves the tool integration is wired correctly and the discrepancy branch is reachable |
| Eligibility discrepancy resolution | Agent judgment (~5% of claims) | **Out of scope** | Dropped to keep LLM call count focused on the higher-signal clinical routing decision; escalation pattern is demonstrated via clinical routing instead |
| Code validity and pairing check | Automated (rule / code) | **Stub** | Tool returns `valid` for all mock claims; invalid-code path is not a required demo path |
| Coding plausibility assessment | Agent judgment (~15% of claims) | **Out of scope** | Would require a second LLM call with its own confidence threshold; cut to keep the prototype to one real LLM call — the clinical content classifier is the demo's core |
| Prior authorisation lookup | Automated (API call) | **Stub** | Tool returns `present_exact`, `present_partial`, or `absent` based on mock claim fixture |
| Prior authorisation partial-match resolution | Agent judgment (~8% of claims) | **Implement** | Configurable tolerance rule (default: ≤15% unit variance auto-resolves; >15% escalates to HITL); this is the edge case path; tolerance threshold must be a named config parameter, not hardcoded |
| Clinical content routing classification | Agent judgment — LLM call | **Implement** | The single real LLM call in the prototype; returns `{classification: "admin"\|"clinical"\|"uncertain", confidence: 0.0–1.0, reasoning: str}`; confidence below configurable threshold triggers HITL escalation; this is the primary agentic flow and the failure-mode escalation path |
| Payment calculation | Automated (rule / code) | **Stub** | Tool accepts procedure code and member ID, returns a fee schedule rate from a mock rate table; arithmetic applied in code |
| Contract exception handling | Agent judgment (~2% of claims) | **Out of scope** | No contract exception data to mock meaningfully; standard rate stub covers all demo claims |
| Exception reviewer interface | Human-facing queue UI | **Stub** | A CLI command `python review_claim.py --claim-id <ID> --decision <approve\|reject\|escalate>` that reads the escalation JSON, displays the structured reason and claim context, and records the reviewer decision. Demonstrates that the HITL loop is complete — escalation is not a terminal state — and that the agent's output is sufficient for a reviewer to act without re-gathering documents. The physician review interface (WS2) is out of scope. |

**LLM calls in prototype:** 1 (clinical content routing classification). All other judgment steps are either stubbed or out of scope.

**Configurable parameters that must be named (not hardcoded):**
- `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` — default 0.70; below this, clinical routing escalates to HITL
- `PRIOR_AUTH_UNIT_TOLERANCE_PCT` — default 0.15 (15%); above this, partial match escalates to HITL

---

## What is explicitly out of scope

- PDF/portal parsing — claim arrives as structured JSON only
- Coding plausibility LLM call (MT-WS1-5) — stubbed as rule pass-through; one LLM call is enough to demonstrate the classifier pattern
- Fee schedule contract exceptions — stub returns standard rate; no exception path
- Intake anomaly detection — no duplicate detection in scope
- WS2 context assembly — blocked by unknown integration anyway
- Queue management agent — infrastructure, not the demonstrable intelligence
- Physician review interface (WS2 clinical path) — out of scope; the WS2 clinical reviewer interface is a separate build from the WS1 exception queue and depends on Wave 2 being in scope

---

## Why it's hard enough

The central challenge is prompt engineering a clinical content classifier that produces **calibrated, structured output** — a confidence score plus a classification plus a brief reasoning trace — reliably enough that the threshold gate behaves predictably across different claim types. This is not a trivial LLM call: the model must simultaneously assess diagnosis code, procedure code, and provider specialty as a combined signal (the AI-native moment from C3), produce a numeric confidence it actually means, and structure its output consistently for the routing logic to parse. Getting this right across mock claims that deliberately sit near the classification boundary is genuinely hard. If the classifier returns `0.85` for obviously-administrative claims and `0.40` for obviously-clinical claims and `0.60` for borderline ones, the architecture is working. If it returns `0.9` for everything, the prototype fails its own test.

The prior auth edge case adds a second design challenge: a configurable tolerance threshold that is itself a named architectural parameter (from C3's ADR-1 trade-off discussion). The test must prove the tolerance rule is actually configurable — not hardcoded — because the architecture explicitly says this is a design parameter requiring Ops alignment.

**Calibration mitigation — system prompt design.** The classifier system prompt must do more than ask for a confidence score. It must instruct the model to reserve `confidence ≥ 0.85` only for claims where *all three signals* (diagnosis code, procedure code, provider specialty) are unambiguously administrative, and to return `0.55–0.70` when any one signal is ambiguous or contradictory. Without this instruction, the model will tend to return high confidence for nearly everything, making the threshold gate meaningless. Mock claims must include at least two fixtures engineered to sit near the boundary — e.g., a procedure code that is typically administrative paired with a specialist provider type — to pressure-test whether the calibration instruction actually produces differentiated scores in practice.

---

## What we expect to learn

**1. Does the LLM produce calibrated confidence scores on healthcare coding patterns?**
The architecture bets that it does. If mock claims near the clinical/administrative boundary all return confidence ≥ 0.80, the HITL queue will be smaller than modelled. If borderline claims cluster around 0.55–0.65, the threshold is a real control point and the calibration problem is real.

**2. Is the HITL escalation message format actually useful?**
The escalation object should tell a human *what made this uncertain* — which code combination triggered the flag, what the classifier saw, what it couldn't resolve. If the demo shows a readable, actionable escalation message, it validates the architecture's HITL design. A bare confidence score would not.

**3. Does the single-agent state machine hold together across interrupted paths?**
The prior auth edge case tests whether the agent correctly continues to routing after resolving a partial match, rather than exiting early or losing claim state. This validates ADR-3's single-agent-over-pipeline decision.

---

## Test coverage

Three test functions must be written as skeletons *before* the agent code, so the build loop has an explicit definition of done for each path.

| Test | Fixture | Key assertions |
|------|---------|----------------|
| `test_happy_path` | Admin claim, all stubs pass, classifier returns `admin` with confidence ≥ threshold | Output status is `approved`; `payment_amount` is present and non-zero; no escalation object in response |
| `test_hitl_escalation` | Borderline claim, classifier returns confidence < threshold | Output status is `escalated`; `reason` field is non-empty and names the ambiguous signal; `confidence` score is present; full claim context is included in the escalation object |
| `test_prior_auth_edge_case` | Partial match fixture — 12 units claimed, 10 authorised (20% over, above the 15% default tolerance) | Output status is `escalated`; escalation object includes `partial_auth_flag: true` and the unit variance; pipeline does not exit early before reaching the routing step |

A fourth fixture (`CLAIM-ELIG-01`, eligibility discrepancy) is included in the mock data set to confirm the eligibility stub is wired correctly. This fixture is not a required demo path and does not need a dedicated test function — a simple assertion that the stub returns `discrepancy` for that claim ID is sufficient.

Full test specification — acceptance criteria, pass/fail thresholds, and regression scope — will be detailed in the Validation Plan (C9).

---

## Mock data

The prototype has no client data. All claim inputs are structured JSON fixtures created for the build. The minimum fixture set is:

| Fixture ID | Purpose | Key field values |
|------------|---------|-----------------|
| `CLAIM-ADMIN-01` | Happy path | Procedure: 99213 (office visit), Diagnosis: Z00.00 (routine exam), Provider type: PCP — all signals unambiguously administrative |
| `CLAIM-CLINICAL-01` | HITL escalation — boundary claim | Procedure: 27447 (knee replacement), Diagnosis: M17.11 (osteoarthritis), Provider type: Orthopaedic surgeon — near the clinical/administrative boundary; classifier confidence expected in the 0.55–0.70 range |
| `CLAIM-PRIORAUTH-01` | Prior auth edge case | Same procedure/diagnosis as `CLAIM-ADMIN-01`; prior auth record authorises 10 units, claim requests 12 (20% variance — above the 15% tolerance threshold) |
| `CLAIM-ELIG-01` | Eligibility stub wiring check | Any claim; eligibility stub returns `discrepancy` for this ID |

Fixtures are static JSON files committed to the repository. No dynamic data generation is required. The mock fee schedule rate table (used by the payment calculation stub) covers the procedure codes present in the fixture set only — no general-purpose rate table needed.

---

## Demo script

**Total target time: under 5 minutes.** Run the three paths in sequence. The exact CLI command will be confirmed during the build, but the structure is `python run_claim.py --fixture <FIXTURE_ID>`.

---

**Setup — 30 seconds**

Open two panes: the project root in one, `config.py` in the other.

Point to the two configurable parameters:
```
CLINICAL_CONTENT_CONFIDENCE_THRESHOLD = 0.70
PRIOR_AUTH_UNIT_TOLERANCE_PCT = 0.15
```

Say: *"These two numbers are the design parameters from the architecture. Everything the agent decides routes through them. We'll see both fire."*

---

**Path 1 — Happy path — 90 seconds**

```bash
python run_claim.py --fixture CLAIM-ADMIN-01
```

Expected output:
```json
{
  "claim_id": "CLAIM-ADMIN-01",
  "status": "approved",
  "payment_amount": 85.00,
  "classification": "admin",
  "confidence": 0.91,
  "audit_trail": ["eligibility: eligible", "codes: valid", "prior_auth: present_exact", "routing: admin @ 0.91"]
}
```

Point to: `status: approved`, `confidence: 0.91` (above threshold), `audit_trail` showing every step completed. Say: *"Full pipeline, one real LLM call, zero physician involvement. This is the 65% path."*

---

**Path 2 — Failure-mode escalation — 90 seconds**

```bash
python run_claim.py --fixture CLAIM-CLINICAL-01
```

Expected output:
```json
{
  "claim_id": "CLAIM-CLINICAL-01",
  "status": "escalated",
  "escalation_reason": "Clinical content classifier returned confidence 0.62 — below threshold 0.70. Ambiguous signal: procedure 27447 (total knee replacement) with orthopaedic surgeon provider type. Cannot confirm administrative path without physician review.",
  "confidence": 0.62,
  "claim_context": {
    "procedure_code": "27447",
    "diagnosis_code": "M17.11",
    "provider_type": "orthopaedic_surgeon"
  }
}
```

Point to: `confidence: 0.62` (below 0.70 threshold), `escalation_reason` naming the specific ambiguous signal, `claim_context` giving the reviewer everything they need. Say: *"The agent doesn't guess. It names what it couldn't resolve and hands off a structured packet."*

Now close the HITL loop:

```bash
python review_claim.py --claim-id CLAIM-CLINICAL-01 --decision escalate-to-physician
```

Expected output:
```
Claim CLAIM-CLINICAL-01 — reviewer decision recorded: escalate-to-physician
Escalation reason: Clinical content classifier returned confidence 0.62 — below threshold 0.70.
Audit record written. Claim status: pending-physician-review.
```

Point to: the escalation is not a terminal state — a reviewer received it, read the agent's reason, and recorded a decision. Say: *"This is the handoff boundary. The exception reviewer doesn't re-gather documents — the agent already did that. The reviewer acts on what the agent produced."*

---

**Path 3 — Edge case — 60 seconds**

```bash
python run_claim.py --fixture CLAIM-PRIORAUTH-01
```

Expected output:
```json
{
  "claim_id": "CLAIM-PRIORAUTH-01",
  "status": "escalated",
  "escalation_reason": "Prior authorisation partial match: 12 units claimed, 10 units authorised (20.0% variance). Exceeds configured tolerance of 15.0%. Requires manual review before payment determination.",
  "partial_auth_flag": true,
  "authorised_units": 10,
  "claimed_units": 12,
  "variance_pct": 0.20
}
```

Point to: `partial_auth_flag: true`, the variance calculation, and the fact that the tolerance threshold from `config.py` appears in the reason string. Say: *"This escalation fired before the LLM call — the tolerance rule is deterministic. The configurable threshold means Ops can tune this without touching code."*

---

**Wrap-up — 30 seconds**

Show the test run:
```bash
pytest tests/ -v
```

All three tests pass. Say: *"Three paths, one real LLM call, two configurable parameters. The clinical path, WS2 context assembly, and queue management are in the architecture but not in this prototype — the spec is buildable, and this is the proof."*

---

## Why this is not bloated

Five work days of build time would be required to add the intake agent (PDF parsing, duplicate detection) and even a stub of WS2 context assembly. Neither adds to what the capstone needs to demonstrate. The graders are evaluating whether the WS1 spec is buildable and whether the three required paths behave as designed — not whether all five agents run. Cutting to the core WS1 flow with three clean paths and a 5-minute demo script is the honest scope call.
