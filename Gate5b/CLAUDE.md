# CLAUDE.md — Gate 5b Final Exam: AML/KYC Case Review Agent (Lattice Pay)

## What this project is

Agentic AML/KYC case review system for Lattice Pay. The agent does the 40-minute synthesis work
(ingest → narrative → pattern detection → watchlist reconciliation → disposition recommendation)
so analysts do the 18-minute judgement work. SAR filing, customer freeze, OFAC confirmation, and
customer communication are NOT delegated to the agent.

**Exam clock:** 09:00–17:00 CET. Design deliverables by 13:30. Curveball adaptation by 14:00.
Working prototype + self-assessment by 17:00.

---

## Exam anchor documents

| File | Purpose |
|---|---|
| `README.md` | Packet cover — deliverable list pointers |
| `scenario-brief.md` | Full engagement context, scope guardrails, stakeholders, success metrics |
| `final-exam-rules.md` | 12-deliverable list, schedule, automatic-fail indicators, self-assessment prompt |

---

## Reference materials (design aid)

| File | Purpose |
|---|---|
| `References/the-fde.md` | FDE role and approach principles |
| `References/atx-concepts.md` | Core agentic concepts for design |
| `References/atx-agent-mapping.md` | How to map cognitive work to agent boundaries |
| `References/atx-assessment.md` → `References/1-atx-assessment.md` | Assessment framework |
| `References/atx-economics.md` | Economics sketch framework (baseline vs agent cost) |
| `References/atx-scoring.md` | Scoring approach reference |
| `References/production-spec-checklist.md` | Checklist for production-grade capability spec |
| `References/spec-ambiguity-vs-builder-mistakes.md` | How to write unambiguous specs |
| `References/claude-md-examples-guide.md` | CLAUDE.md patterns and examples |

---

## Mock data — case queue

| File | Purpose |
|---|---|
| `mock-data/case-queue/queue.md` | The alert queue the analyst sees — **start here** |
| `mock-data/case-queue/alert-detail-summaries.md` | Per-alert detail summaries for all 8 cases |

---

## Mock data — 8 active cases

### KYC profiles (`mock-data/kyc-profiles/`)

| File | Account type | Alert type |
|---|---|---|
| `C-CON-2207715_kyc.json` | Consumer | Watchlist false-positive (common name) |
| `C-CON-3318822_kyc.json` | Consumer | Routine structuring / no-SAR baseline |
| `C-CON-5530118_kyc.json` | Consumer | OOS remittance routing (channel = cross-border-remittance) |
| `C-CON-7714290_kyc.json` | Consumer | Structuring — 7 cash deposits in [$4,810–$4,940] range over 6-day window |
| `C-CON-7720338_kyc.json` | Consumer | High-aggregate cash-equivalent inbound, thin KYC (tier-1, no address/SSN) |
| `C-CON-9923441_kyc.json` | Consumer | Watchlist genuine hit — escalation needed |
| `C-BIZ-4408821_kyc.json` | Business | High-velocity merchant payments |

*(High-aggregate cash-equivalent / thin-KYC case: check queue.md for the 8th account ID)*

### Transaction history — 90-day extracts (`mock-data/transaction-history/`)

| File |
|---|
| `C-CON-2207715_90day.csv` |
| `C-CON-3318822_90day.csv` |
| `C-CON-5530118_90day.csv` |
| `C-CON-7714290_90day.csv` |
| `C-CON-7720338_90day.csv` |
| `C-CON-9923441_90day.csv` |
| `C-BIZ-4408821_90day.csv` |

### Watchlist screenings (`mock-data/watchlist-screenings/`)

| File | Notes |
|---|---|
| `C-CON-2207715_ofac_screening.txt` | Common-name false-positive — Gonzalez / Alava |
| `C-CON-9923441_ofac_screening.txt` | Common-name false-positive (Mohammed Khan / KHAN Muhammad) — DOB delta 21 years → DISCONFIRMED |
| `C-BIZ-4408821_screening.txt` | Business account screening |

### Sanctions list reference extracts (`mock-data/sanctions-list-extracts/`)

| File |
|---|
| `OFAC_SDN_Gonzalez_Alava.txt` |
| `OFAC_SDN_KHAN_Muhammad.txt` |

### Counterparty network (`mock-data/counterparty-network/`)

| File | Notes |
|---|---|
| `C-CON-6611442_linked_network.json` | JSON adjacency list — network analysis case |

### Customer RFI email threads (`mock-data/customer-rfi-emails/`)

| File | Notes |
|---|---|
| `C-CON-7720338_prior_RFI_thread_2026-05.eml` | Prior RFI — thin-KYC case (soft-freeze dispute) |
| `C-CON-3318822_prior_RFI_tobacco.eml` | Prior RFI — structuring / no-SAR baseline |

---

## Design deliverables (`design/`)

| File | Deliverable |
|---|---|
| `design/01-discovery-notes.md` | #1 — Discovery notes: problem framing, stakeholder alignment, scope boundaries, open assumptions |
| `design/02-cognitive-work-assessment.md` | #2 — Cognitive work assessment: 58-min case decomposed into 5 JtDs (brief terminology) with zones within each JtD, delegation analysis, suitability gate (25/25 score) |
| `design/03-agent-purpose-document.md` | #3 — Agent Purpose Document: LACRA KPIs, failure modes, autonomy matrix, escalation triggers, activity catalog |
| `design/04-architecture-decision-record.md` | #4 — ADRs: single-agent vs multi-agent (ADR-001), model selection Sonnet (ADR-002), dual JSON+prose output (ADR-003), PII handling (ADR-004) |
| `design/05-capability-specification.md` | #5 — Production-grade capability spec: 5-JtD pipeline, input/output schemas, pattern detection rules (3a–3f), watchlist reconciliation logic, 10-point disposition decision tree, governance, error handling, tool interfaces, assumptions register |
| `design/06-validation-plan.md` | #6 — Validation plan: 5 test scenarios (happy path, SAR escalation, OOS routing, missing data, reproducibility) with explicit pass/fail criteria |
| `design/07-economics-sketch.md` | #7 — Economics sketch: $55.77 baseline → $17.37 agent-augmented per case; $420K build, ~8-month payback, $2.7M 3-year net; sensitivity analysis |

---

## 12 Deliverables checklist

**Design phase — submit by 13:30**

- [x] 1. Discovery notes — problem framing + success metrics
- [x] 2. Cognitive work assessment — delegation analysis
- [x] 3. Agent Purpose Document — autonomy matrix + escalation triggers
- [x] 4. Architecture Decision Record (≥1)
- [x] 5. Production-grade capability specification (the spec the prototype is built from)
- [x] 6. Validation plan
- [x] 7. Economics sketch — baseline vs agent cost, order-of-magnitude ROI
- [x] 8. `CLAUDE.md` for the agent project *(this file)*

**Curveball response — submit by 14:00**

- [x] 9. Revised delegation design + spec amendments — targeted adaptation with explicit reasoning

**Build phase — submit by 17:00**

- [x] 10. Working prototype — primary flow + failure escalation + ≥1 edge case, tests, demo script
- [x] 11. Supplementary spec amendment note — AM-06 correction + AM-07 through AM-11 in design/11-spec-amendments.md
- [x] 12. Self-assessment output — full package run through the Standardised Self-Assessment Prompt

> **Both design and build must pass independently.** A dead prototype fails regardless of design quality.
> If the build diverges from the spec, file an amendment note — silent divergence is an automatic fail.

---

## Agent scope guardrails (baked in — never override)

**Delegated to agent:** ingest, narrative synthesis, pattern detection, watchlist reconciliation, disposition recommendation with reasoning + confidence.

**NOT delegated — analyst/supervisor only:**
- SAR filing decision
- Customer freeze decision
- OFAC positive confirmation
- Any communication with customer or third party
- Broker-dealer / securities alerts (out of scope entirely)
- Cross-border remittance product-specific alerts (separate team)

---

## Success metrics (from Dr. Priya Rao)

| Metric | Target |
|---|---|
| Per-case analyst handling time | ≤ 18 min (from 58 min baseline) |
| Alert-to-disposition median cycle | ≤ 2.5 days (from 6.2 days) |
| SAR-eligible detection precision | ≥ 75% |
| SAR-eligible recall | ≥ 95% |
| Disposition reproducibility | 100% across audit sample |

---

## Key stakeholder constraints

- **Dr. Priya Rao (CCO):** Explainability on demand to FinCEN / state regulator. No black box.
- **William Akoto (Engineering):** PII stays inside Lattice infrastructure. No raw customer data to third-party APIs unless contractually safe-harboured.
- **Tomáš Brejcha (FinCEN examiner):** Reproducibility of dispositions. Explainable model contributions.
- **Diane Reston (Senior analyst):** Augmentation not replacement. "Do the boring synthesis, let me argue with it."

---

## Build targets (prototype scope)

1. **Primary agentic flow** — one case end-to-end: ingest → synthesise → pattern → watchlist → disposition
2. **Failure-mode escalation** — genuine watchlist hit or layering pattern triggering escalate-to-SAR path
3. **Edge case** — common-name watchlist false-positive handled correctly (not escalated)
4. **Tests** — 13 tests (T1–T13) covering all 8 real mock-data cases + 5 synthetic paths
5. Demo script

---

## Build decisions (locked before build phase)

| Decision | Choice | Rationale |
|---|---|---|
| Architecture | Pipeline mode — Python pre-loads all data via tool functions → one Claude API call at temperature=0 → parse JSON output | ADR-001: "one LLM call chain per case"; simpler, reproducible, fits 3-hour window |
| OOS channel detection | `"remittance" in channel.lower()` (substring, not exact match) | Actual CSV value is `cross-border-remittance`; spec intent is remittance product, not a literal string |
| T2 layering / decision point 9 | Network file counts as a data source; decision point 3 (LAYERING HIGH → ESCALATE_SAR) fires before point 9 | C-CON-6611442 has no KYC/transaction CSVs but network file contains all hop chain data |
| T4 missing-data test fixture | Synthetic customer ID `C-CON-0000001` (no files exist) | No file deletion; self-contained; both read_kyc and read_transactions return None → FURTHER_INFO_NEEDED |
| Language | Python | Spec tool interfaces use Python type hints; Anthropic SDK is Python-native |

### Spec amendment notes

- **AM-01:** JtD-1a scope detection: spec says `channel = "remittance"`; actual mock data uses `channel = "cross-border-remittance"`. Rule implemented as substring match. Intent unambiguous.
- **AM-02:** Decision point 9 ("both KYC and transaction history missing → FURTHER_INFO_NEEDED") applies when no data is available from *any* source. Network file data satisfies the data requirement for the layering case (C-CON-6611442).
- **AM-03:** Enhanced audit log schema (FinCEN FIN-2026-A-008 Req 1): add `patterns_detected_summary`, `watchlist_resolution`, `supporting_transactions`, `sdn_list_version`, `analyst_action` (null at agent time, updated by case mgmt system).
- **AM-04:** Add `sdn_list_version` field to case package output. Prototype: hardcoded to mock SDN date "2026-05-01".
- **AM-05:** Designate full case package JSON as the FIN-2026-A-008 Req 4 explainability record (span-level attribution via `patterns_detected[].evidence[]` and `disposition.supporting_transactions[]`).
- **AM-06:** Add `sar_clock_start_utc` field to output (= `triggered_at_utc` for ESCALATE_SAR, null otherwise). Designates 30-day FinCEN SAR-filing clock T0 per Req 5 — clock starts at alert trigger, not agent processing time. Add `alert_status` field (hardcoded to "OPEN" in prototype).
- **AM-07:** Linked account KYC retrieval loop not implemented in prototype (relies on network file being self-contained per AM-02). Production Wave 1 must add the loop.
- **AM-08:** Transaction row truncation (500 rows) and network account cap (10) not enforced in prototype. No mock file exceeds limits. Production must add pre-processing guards.
- **AM-09:** `monetary_scope_usd` and `analyst_queue_tag` are accepted but unused. Production should route `analyst_queue_tag = "High"` to a priority queue.
- **AM-10:** Velocity anomaly (JtD-3c) uses 90-day extract as proxy for 12-month prior average. Substitution: `prior_60d / 2` as monthly proxy; if `prior_60d = 0`, flag "no prior baseline" at MEDIUM severity. Production must extend to 12-month data source.
- **AM-11:** Mixed remittance scope detection uses direction-based rule: any OUTBOUND remittance-channel transaction → OOS; only INBOUND remittance-channel transactions → IN_SCOPE with data_gap note. Fixes the any-transaction check that incorrectly routed mixed-profile customers OOS.

---

## Disposition vocabulary (five values only)

`CLEAR` | `ESCALATE_SAR` | `CUSTOMER_RFI` | `ACCOUNT_FREEZE` | `FURTHER_INFO_NEEDED`

Every recommendation must include: disposition value, reasoning, span-citations to underlying transactions, confidence level (0–1).

---

## Exam self-assessment prompt (run in final 15–30 min)

```
Review this [specification / agent design / prototype] as a senior FDE would.
Evaluate against these criteria:

1. DELEGATION: Are the human/agent boundaries justified?
2. AMBIGUITY: Identify every statement that could be interpreted two ways.
3. BUILDABILITY: Could an AI coding agent build this without clarifying questions?
4. FAITHFULNESS: Does the prototype implement what the spec describes?
5. ECONOMICS: Does the implicit cost model make sense?
6. VALIDATION: Are the failure modes covered?
7. SCORE: Rate this deliverable 1–100 with specific rationale.
```
