# Prompt: Capstone C12 — Begin Building (WS1 Administrative Adjudication Agent)

This prompt is run **once** to start the build loop. The agents under build are WS1 (Administrative Adjudication Agent) and WS2 (Clinical Review Support Agent) for Greenfield Health Systems. The output feeds directly into `prompt_D5_build_loop_response.md`, which produces the C12 build-loop reflection.

**Build WS1 first.** WS2 has a BLOCKING gap (S-08: physician review queue — no API contract available; see IC-S-08 SCOPE-OUT in D4_integration_specs.md). WS1's administrative path is fully specified with no blocking integration gaps.

---

## Inputs (read all before writing a single line of code)

- `Deliverables/D4_preamble_capability_spec.md` — shared entities, shared data models, shared enums. Read this first. All entity definitions referenced in D4a and D4b originate here (ClaimRecord, AuditLogEntry, CalibrationRecord, EscalationPacket, ResolutionRecord).
- `Deliverables/D4a_capability_spec.md` — WS1 Administrative Adjudication Agent — full capability spec (§0–§14). This is the primary build spec for this pass.
- `Deliverables/D4b_capability_spec.md` — WS2 Clinical Review Support Agent — full capability spec (§0–§14). Read for lifecycle context; do not build WS2 until S-08 is resolved.
- `Deliverables/D4_integration_preamble.md` — system inventory, gap register (G-1 through G-6), risk register. Use this to identify which systems are SCOPE-OUT (stub behaviour defined), which are BLOCKING, and which have known discovery gaps.
- `Deliverables/D4_integration_specs.md` — integration contracts for all 16 systems (IC-S-01 through IC-S-16). Every system interaction must conform to the contract here, including stub behaviour for SCOPE-OUT entries (IC-S-06, IC-S-08, IC-S-13, IC-S-15).
- `References/production-spec-checklist.md` — use to confirm spec completeness before writing implementation code for each task.

---

## The build task

Build the WS1 Administrative Adjudication Agent as described in `Deliverables/D4a_capability_spec.md`.

Read all input files in full before writing a single line of code. Shared entities are defined in D4_preamble — do not redefine them.

Then produce three outputs in sequence:

**1. What I can build confidently without asking any questions**

List the parts of D4a that are complete enough to implement immediately — specific task flows (T-01 through T-10, T-12), integration contracts, or entity definitions where every decision is made and every edge case is covered. Be precise: name the task IDs, not just "most of the spec." For SCOPE-OUT systems, confirm the stub behaviour from D4_integration_specs.md before listing them as buildable.

**2. What I need to clarify before building the rest**

List each open question precisely. For each:
- Name the spec section or task ID it relates to
- State exactly what is ambiguous or missing
- State what assumption you would make if forced to proceed, and whether that assumption is safe or risky
- Check whether the gap is already documented in `D4_integration_preamble.md` before flagging — if it is, reference the gap ID (G-N) rather than treating it as new

Format:
> *[Task ID / Section]*: [Exact question]. If unanswered, I would assume [X] — this is [safe / risky] because [reason]. *(Pre-documented gap: [G-N] if applicable)*

**3. Build the part you are most confident about**

Build the single WS1 task flow or integration contract you rated most complete. Enough code to demonstrate a real implementation choice — not scaffolding. Name what you chose and why (most complete, fewest open questions, no SCOPE-OUT dependencies).

Priority candidates in order of spec completeness:
- T-01: Inbound claim receipt and schema validation (IC-S-01, IC-S-10, IC-S-16)
- T-03: Member eligibility check (IC-S-02, IC-S-09, IC-S-10)
- T-09: Payment authorisation gateway with FM-A-5 hard stop (IC-S-11, IC-S-07, IC-S-10)

If you choose T-09, implement the pre-condition re-validation in full — not a simplified version. FM-A-5 is the highest-risk integration point in WS1.

---

## Non-negotiable constraints

- All system names and base URLs are `DISCOVERY_REQUIRED` (see D4_integration_specs.md header). Use the placeholder convention in integration code.
- Do not write any code that transitions a claim from `PENDING_PHYSICIAN_REVIEW` to `PAYMENT_CALCULATING` or `APPROVED`. This is FM-A-5. The governance hard stop (`GOVERNANCE_HARD_STOP_TRIGGERED` written to S-10) must fire first.
- CalibrationRecord startup validation (6-field check: state, cmo_signoff_date, recall_achieved ≥ 0.995, holdout_set_size ≥ 500, call_site = ROUTING, classifier_version) must pass before any claim processing begins. Fail-fast on any validation failure.
- Audit-first ordering: every S-10 AuditLogEntry must reach `COMMITTED` before the corresponding S-07 state transition `PATCH` is issued.
- Optimistic locking: every S-07 state transition `PATCH` must include `from_state`. Handle 409 Conflict explicitly.
- SCOPE-OUT stubs must behave exactly as specified in D4_integration_specs.md — do not substitute production logic for stub behaviour in this pass.

---

## Output

Write everything — what was built, questions raised, what could not be built and why — to `Deliverables/C12_build_loop_start.md` under a section headed **Build Loop Output — Pass 1 (WS1)**.

Then run `prompt_D5_build_loop_response.md` on this output.
