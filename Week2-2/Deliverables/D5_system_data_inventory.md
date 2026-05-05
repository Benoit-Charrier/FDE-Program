# D5 — System/Data Inventory
**Helix Workforce Software — Contract Classifier Agent**
**Produced:** 2026-05-04 | **Status:** Draft — awaiting FDE approval

---

## 0. Executive Summary

- **Most critical integration:** Ironclad (CLM REST API) — it is the agent's only output target for intake records, deviation reports, and routing queue assignments; without write access to Ironclad, the agent produces classifications it cannot persist, and the human confirmation mechanism (Tom's routing sign-off) has no system of record.
- **Most significant gap:** The Outlook API integration path is unconfirmed — if IT security blocks the Microsoft Graph API connection to the Legal & Commercial monitored inbox, T-1 and T-2 are fully blocked and the agent cannot receive contracts autonomously, eliminating the WS1 throughput benefit entirely unless a manual forwarding fallback is implemented on Day 1.
- **Compounding opportunity:** The Ironclad REST API integration and the DOCX-to-clause-section parser built for this agent are directly reusable by the WS2 standard-deviation redlining agent (C-4) and the WS4 sign-off package preparation agent (C-8), meaning the integration cost of the Contract Classifier Agent substantially reduces the marginal cost of the next two agents in this pipeline.

---

## 0b. Table of Contents

- [0. Executive Summary](#0-executive-summary)
- [0b. Table of Contents](#0b-table-of-contents)
- [1. Data and System Requirements](#1-data-and-system-requirements)
- [2. System and Data Inventory Table](#2-system-and-data-inventory-table)
- [3. Gap Analysis](#3-gap-analysis)
- [4. Risk Register](#4-risk-register)
- [5. Context Engineering Design](#5-context-engineering-design)
- [6. Compounding Opportunities](#6-compounding-opportunities)
- [7. Assumption Log](#7-assumption-log)

---

## 1. Data and System Requirements

Requirements are derived directly from the D4 activity catalog (T-1 through T-11). Each requirement is traced to the tasks that depend on it.

### Input Data
*(What the agent reads to do its work)*

| Data | Granularity | Latency | Source | Depends on |
|---|---|---|---|---|
| Inbound vendor contract (Word DOCX) | Full document, one attachment per email | On-event: as each email arrives | Outlook monitored inbox | T-1, T-2, T-4 |
| Email header metadata (sender, subject, received date, delivery channel) | Per email | On-event | Outlook | T-2, T-3 |
| Counterparty name | Per contract — may require extraction from email body or document if not in email subject [Assumption A-D5-1] | On-event | Outlook email body / DOCX first page | T-3 |

### Reference Data
*(Policy documents and standards the agent consults during classification)*

| Data | Granularity | Latency | Source | Depends on |
|---|---|---|---|---|
| Helix negotiation playbook — all seven clause category sections | Section-level (liability cap, DPA, termination, IP, SLA, governing law, indemnity) | On-demand retrieval at start of each case | SharePoint "Position Statements v3.4" | T-5, T-6, T-7 |
| Playbook version timestamp | Document-level metadata property | On-demand at start of each case (same request as playbook retrieval) | SharePoint document properties | T-8, ET-2 |
| DPDI Act effective date | Single configuration constant | Static — loaded at agent startup | Agent configuration store [Assumption A-D5-2] | T-8 |
| Per-clause-type escalation criteria (DEVIATION_STANDARD vs. DEVIATION_ESCALATION thresholds per clause category) | Section-level addendum to playbook | On-demand | SharePoint (version-controlled addendum — pre-deployment prerequisite, does not yet exist) | T-7, T-9 |
| Routing decision thresholds (confidence values: 0.90 / 0.80 / 0.75) | Three scalar constants | Static — loaded at agent startup | Agent configuration store | T-7, T-9, ET-1 |

### Output Targets
*(Systems the agent writes to)*

| Data written | Granularity | Latency | Target | Depends on |
|---|---|---|---|---|
| Intake case record (counterparty, contract type, received date, delivery channel flag) | Per case, on intake | Real-time (within seconds of email receipt) | Ironclad REST API — new case creation endpoint | T-3 |
| Deviation report JSON payload | Per case, on classification completion | Batch (after all clauses classified, ~minutes per case) | Ironclad case record — `agent_deviation_report` custom field [Assumption A-8 from D4] | T-11 |
| Case status update — "Pending Human Review" | Per case | On classification completion | Ironclad workflow stage transition | T-11 |

### Approval / Governance Channels
*(How the designated approver's sign-off is captured and audited)*

| Data | Granularity | Latency | Target | Depends on |
|---|---|---|---|---|
| Tom Reilly's routing confirmation event (WS2 / WS3 / No Redline Required) | Per case — a named user action, not an agent action | Near-real-time (Tom reviews and confirms) | Ironclad case field — `routing_confirmed_by` + `routing_confirmed_at` + `routing_tier` [Assumption A-D5-3] | C-3 autonomy contract, hard governance gate |
| Override record when Tom manually changes a classification | Per clause, on override | Near-real-time | Ironclad case record — `determination_source` field in deviation report | Audit trail, weekly accuracy audit |

---

## 2. System and Data Inventory Table

| System/Source | Data needed | Access type | Inferred availability | Gap/Risk | Priority |
|---|---|---|---|---|---|
| **Outlook** — Legal & Commercial monitored inbox | Inbound vendor contract emails and DOCX attachments; email sender, subject, received date | Event trigger + Read | API unknown — Microsoft Graph API likely available but IT security approval required [Assumption A-D5-4] | **Gap G-1:** Integration path unconfirmed; T-1/T-2 blocked if unavailable | Required |
| **SharePoint** — "Position Statements v3.4" playbook | Seven clause category sections as text; version/last-revised timestamp as document property | Read / RAG | API unknown — Microsoft Graph API for SharePoint likely available; document format (machine-readable vs. scanned) unconfirmed [Assumption A-D5-5] | **Gap G-2:** Playbook format and API path unconfirmed; T-5 blocked | Required |
| **Ironclad CLM** — case management and record store | Write: new case record (intake metadata); Write: deviation report JSON; Write: case status transition; Read: existing case data for ET-6 override count | Read-Write | API likely available — "REST APIs available" confirmed in scenario; specific endpoints and field schema not confirmed [Assumption A-8 from D4] | **Gap G-3:** Field schema and authentication unconfirmed; T-3/T-11 blocked at field level | Required |
| **LLM provider** (e.g., Claude API) | Clause-vs-playbook comparison (T-6); clause classification with confidence score (T-7); routing rationale generation (T-9); deviation report narrative generation (T-10) | Read (API call) | Not named in scenario — existence assumed; legal review of sending contract text to external API required [Assumption A-D5-6] | **Gap G-4:** Legal privilege and data residency review required before deployment | Required |
| **Ironclad CLM** — routing confirmation mechanism | Tom's routing confirmation event (routing_confirmed_by, routing_tier, routing_confirmed_at); human override record | Write (human-triggered) / Read (agent reads confirmation status before allowing case to proceed) | API likely available (same as above); specific workflow event model unconfirmed | **Gap G-3 (shared):** Ironclad workflow state model not documented; hard governance gate depends on this | Required |
| **DPDI Act effective date** — configuration store | Single scalar constant used in DPA currency check (T-8) | Read | Not a system — stored in agent configuration; value not confirmed in scenario [Assumption A-5 from D4] | **Gap G-5:** Value unknown; DPA currency check defaults to always-flag until confirmed | Important |
| **Per-clause-type escalation criteria** — playbook addendum | Threshold definitions for DEVIATION_STANDARD vs. DEVIATION_ESCALATION per clause type (7 categories) | Read / RAG | Does not yet exist — must be authored by Amelia Forsythe as pre-deployment prerequisite | **Gap G-6:** Routing logic conservative default active until document exists; over-escalation risk | Required (pre-deployment) |
| **Ironclad CLM** — prior case records | Historical classification outcomes for the same counterparty (used in ET-6 override count); prior routing decisions for accuracy audit baseline | Read | API likely available (same instance); query capability for historical case data unconfirmed [Assumption A-D5-7] | **Gap G-7:** ET-6 (override count) cannot be computed without queryable case history | Important |
| **Word DOCX parser** (library component) | Clause section extraction from inbound contract documents | Read (in-process) | Not a named system — standard library (python-docx or equivalent); no integration required | None — local library; risk is on parsing accuracy for non-standard document structures | Required |
| **Agent configuration store** | Threshold constants (0.90/0.80/0.75), DPDI Act date, liability cap floor (£250k), routing criteria version identifier | Read | Not a named system — environment variables or a config file; implementation-time decision | None — straightforward; must be version-controlled alongside agent code | Required |

*Named systems (Ironclad, Outlook, SharePoint) — API specifics and integration maturity are assumptions beyond what is stated in scenario_context.md. All other rows labelled as "Not named in scenario."*

---

## 3. Gap Analysis

> **Gap G-1: Outlook API — Legal & Commercial monitored inbox access**
> **What the agent cannot do without it:** T-1 (monitor for inbound contracts) and T-2 (extract email metadata and DOCX attachment) are fully blocked. The agent has no mechanism to receive contracts autonomously.
> **Severity:** Blocking — the agent cannot initiate a case without a contract to classify.
> **Mitigation options:**
> 1. **Fallback Day 1 (manual forwarding rule):** Tom creates an Outlook rule that auto-forwards all vendor contract emails from the Legal & Commercial inbox to a dedicated, agent-monitored SMTP address with a simpler integration path. Reduces T-1/T-2 from Fully Agentic to Agent-led + Tom triggers forwarding, but unblocks the build entirely.
> 2. **Microsoft Graph API (preferred):** Request IT security approval for a registered app with `Mail.Read` permission on the shared Legal & Commercial mailbox. Standard enterprise integration path; approval timeline is the unknown.
> 3. **Shared Mailbox polling:** Create a dedicated shared mailbox (`contracts-intake@helix.com`) for vendor submissions; agent polls via Graph API. Lower security surface than full inbox access; vendors are directed to the new address.
> **Discovery action:** "Has IT approved any Microsoft Graph API connections to Outlook mailboxes for automation tools? What is the approval process for a `Mail.Read` service account on the Legal & Commercial shared inbox?"

---

> **Gap G-2: SharePoint playbook format and access path**
> **What the agent cannot do without it:** T-5 (retrieve current playbook) is blocked, which blocks T-6 and T-7 (all clause comparisons). The agent cannot classify any clause without the playbook.
> **Severity:** Blocking — clause comparison requires the playbook as the reference standard.
> **Mitigation options:**
> 1. **Export to structured JSON (immediate workaround):** Amelia or Tom exports the playbook's seven clause sections to a structured JSON file hosted in a known SharePoint location. The agent reads the JSON file via Graph API rather than parsing the Word/HTML document. This also makes the version timestamp explicit.
> 2. **Microsoft Graph API for SharePoint (preferred):** Confirm that the SharePoint library where "Position Statements v3.4" is stored is accessible via the Graph API's Files endpoint. Standard if the organisation uses Microsoft 365.
> 3. **Static copy in agent repo (last resort):** Embed a snapshot of the playbook as a versioned file in the agent's configuration. Acceptable for a first deployment if SharePoint API is delayed; creates version drift risk if the playbook is updated without also updating the agent's copy.
> **Discovery action:** "Is 'Position Statements v3.4' stored as a Word document, an HTML page, or a PDF in SharePoint? Can a service account with `Files.Read` permission access the Legal & Commercial SharePoint site? What is the direct URL to the playbook document?"

---

> **Gap G-3: Ironclad case data model — field schema, workflow state model, authentication**
> **What the agent cannot do without it:** T-3 (log intake case) and T-11 (write deviation report, trigger queue routing) are blocked at the field level. The routing confirmation gate (C-3) has no system of record.
> **Severity:** Blocking — the agent can classify internally but cannot persist results or enforce the human confirmation gate without confirmed Ironclad write access.
> **Mitigation options:**
> 1. **Ironclad sandbox + admin session:** Request an Ironclad sandbox environment from the Ironclad account rep. Use the admin UI to confirm which workflow template applies to vendor contracts, what custom fields are available, and what the REST API endpoints and auth model are. This is standard practice before building any CLM integration.
> 2. **Mock contract for build phase:** Define a mock JSON schema (D4 §4b provides a starting point) and build against the mock. Integrate with real Ironclad once the field schema is confirmed. Adds a swap-out integration step but unblocks the build.
> 3. **CLM admin interview:** Schedule a 30-minute call with Helix's Ironclad admin (likely Amelia's direct report or an ops team member) to walk through the case data model and available REST endpoints.
> **Discovery action:** "Who administers Ironclad at Helix? Can they share: (1) the vendor contract workflow template; (2) available custom fields on contract cases; (3) the REST API base URL and authentication model (API key vs. OAuth); (4) the workflow stage that corresponds to the paralegal review queue?"

---

> **Gap G-4: LLM provider — legal privilege and data residency review**
> **What the agent cannot do without it:** T-6, T-7, T-9, T-10 all require an LLM. The agent's core classification capability is blocked if LLM access is not approved.
> **Severity:** Blocking — the agent's entire value proposition depends on LLM-based natural language understanding.
> **Mitigation options:**
> 1. **Internal/private LLM deployment:** If Helix has an enterprise LLM agreement (Azure OpenAI, Bedrock, or a self-hosted model), route all contract text through that deployment rather than a public endpoint, eliminating data residency concerns.
> 2. **Data Processing Agreement (DPA) with LLM provider:** Most enterprise LLM providers (Anthropic, OpenAI, Google) offer DPAs that confirm the provider does not use customer data for model training. Confirm that Helix's existing or planned LLM agreement includes a DPA covering commercially sensitive contract text.
> 3. **PII/confidential data scrubbing:** Pre-process contracts to remove counterparty names, pricing details, and personal data before sending to the LLM; pass only clause text and structure. Reduces data sensitivity at the cost of some classification context.
> **Discovery action:** "Does Helix have an existing enterprise agreement with an LLM provider that includes a data processing agreement covering commercially sensitive legal documents? Has Legal reviewed the data residency implications of sending vendor contract text to an external API?"

---

> **Gap G-5: DPDI Act effective date for DPA currency check**
> **What the agent cannot do without it:** T-8 cannot perform a date-based currency check; the DPA currency check defaults to always-flagging all DPA classifications as "Unverified," which is a safe but noisy default that adds unnecessary friction to contracts with compliant DPA clauses.
> **Severity:** Degrading — the agent can launch with the always-flag default; DPA classification accuracy is reduced until the date is provided.
> **Mitigation options:**
> 1. **Ask Amelia directly:** The effective date of the DPDI Act Q1 revisions is a matter of public record; Amelia can confirm which revision is relevant to Helix's DPA standard. Add the date to the agent configuration before deployment.
> 2. **Conservative placeholder:** Use a conservative placeholder date (e.g., 2025-01-01) that ensures all DPA clauses assessed against the current playbook version carry the flag; safe, low-effort, and easy to remove once the actual date is confirmed.
> **Discovery action:** "What specific DPDI Act revisions are you applying to DPA clauses — and from what effective date should we treat the current playbook as stale? This date is needed to automate the DPA currency check."

---

> **Gap G-6: Per-clause-type escalation criteria document**
> **What the agent cannot do without it:** T-9's routing logic uses a conservative default (any deviation with confidence < 0.85 → DEVIATION_ESCALATION) until explicit DEVIATION_STANDARD vs. DEVIATION_ESCALATION criteria are codified per clause type. Without the document, the agent will systematically over-escalate to WS3, defeating the WS1 throughput benefit.
> **Severity:** Blocking for production accuracy — the agent can launch, but the conservative default may route 50%+ of cases to WS3 instead of the expected ~10%, overwhelming the commercial lawyer review capacity.
> **Mitigation options:**
> 1. **Amelia-led criteria workshop:** Schedule a 2-hour session with Amelia and Tom to codify escalation thresholds for each of the seven clause types. The output is a version-controlled addendum to the playbook that becomes part of the reference data for T-7.
> 2. **Phased deployment — high-confidence only:** Deploy the agent in the first phase only for contracts where the LLM produces all-MATCH or all-DEVIATION_STANDARD classifications with confidence ≥ 0.85. This covers the 70% No Redline Required tier and delivers immediate value while criteria are being developed.
> 3. **Tom's historical cases as training data:** Use Tom's prior first-pass decisions (if logged in Ironclad or accessible from email history) to derive empirical escalation thresholds by clause type. Provides a data-grounded starting point for Amelia to ratify rather than creating criteria from scratch.
> **Discovery action:** "Can you walk us through three recent contracts — one standard, one redlined, one escalated — and tell us specifically which clause deviation in each drove the routing decision? We need to convert those decisions into explicit threshold criteria by clause type."

---

> **Gap G-7: Ironclad historical case query — per-counterparty override count**
> **What the agent cannot do without it:** ET-6 (systematic routing misalignment detection) cannot fire automatically; the three-override threshold for counterparty-level recalibration cannot be tracked.
> **Severity:** Low — ET-6 becomes a manual monitoring task. The agent recalibration pathway is still valid; it just loses its automated trigger.
> **Mitigation options:**
> 1. **Ironclad reporting query:** Confirm whether Ironclad's REST API supports filtering cases by counterparty name and returning override event counts. If yes, ET-6 can be automated at no additional infrastructure cost.
> 2. **Manual weekly review:** Tom checks the Ironclad dashboard weekly for counterparties with recurring override patterns; flags for recalibration manually. Acceptable for a v1 deployment given the low volume (23 cases/week).
> **Discovery action:** "Can Ironclad's API return a list of contract cases filtered by counterparty name? Does the case record support a custom field for 'agent override count' that increments on each Tom override?"

---

## 4. Risk Register

| System | Risk type | Risk description | Likelihood | Impact | Mitigation |
|---|---|---|---|---|---|
| **Ironclad CLM** | **Sign-off integrity risk** | The agent writes the routing recommendation to the Ironclad case record. If the Ironclad workflow is misconfigured, a work stream assignment could be triggered by the agent's write rather than by Tom's explicit confirmation event — bypassing the human confirmation gate and violating the hard constraint that routing decisions require a human confirmation before the case proceeds. | M | H | The Ironclad integration must be built so that the `routing_confirmed_by` field can only be written by a named human user (not by the API service account used by the agent); the work stream assignment trigger is bound exclusively to the human confirmation event, not to the agent's deviation report write. The agent's API token must have write access to `agent_deviation_report` only — not to workflow stage transition fields. This separation must be enforced at the Ironclad permission level, not just the application level. |
| **SharePoint** | Data quality risk | The playbook "Position Statements v3.4" may be stored as a Word document, an HTML SharePoint page, or a scanned PDF. If it is a scanned PDF or an image-embedded document, machine-readable text extraction fails and T-5 is blocked. Even if text-extractable, playbook language may be ambiguous (the same clause category position may be stated in prose that supports multiple interpretations — e.g., "reasonable endeavours" vs. "best endeavours" language in SLA commitments). | M | H | Convert playbook to a machine-readable, structured format (JSON or plain text per section) as a pre-deployment prerequisite. Engage Amelia to review and approve the structured version. Implement a playbook version hash check at agent startup: if the playbook changes, the agent flags for re-validation before processing new cases. |
| **Outlook** | API availability / IT security risk | Microsoft Graph API access to the Legal & Commercial inbox may require IT security team approval, a registered Azure AD app, and a conditional access policy exception. Enterprise email security policies sometimes block programmatic inbox access; the approval timeline is typically 2–8 weeks. | H | H | Implement the manual forwarding fallback (Gap G-1 Option 1) as a Day 1 workaround while Graph API approval is in progress. This ensures the agent can be deployed and validated while the integration matures. |
| **LLM provider** | Legal/compliance risk | Sending vendor contract text (which may contain commercially sensitive terms, counterparty pricing, and personal data) to an external LLM API creates potential legal privilege, confidentiality, and GDPR risk. If Helix's clients (NHS trusts, banks) have data residency requirements in their own contracts with Helix, sending their contract text externally may breach those requirements. | M | H | Require a DPA with the LLM provider before deployment. Evaluate whether a private/enterprise LLM deployment (Azure OpenAI, Bedrock, or similar) eliminates the data residency concern. Consult Amelia specifically on whether sending inbound vendor contract text to an external API creates any legal privilege issues. |
| **Ironclad CLM** | Audit trail risk | The agent's classification decisions must be auditable: which playbook version was used, what confidence score was assigned, and whether Tom confirmed or overrode the routing. If the `agent_deviation_report` field is overwritten on each case update (rather than append-only), the audit trail for a case is lost. | M | H | The `agent_deviation_report` field must be treated as append-only or immutable after initial write. Each override by Tom must be recorded as a new event, not a modification of the agent's original classification. This is an Ironclad data model requirement to confirm before build. |
| **SharePoint** | Version drift risk | The playbook will be updated over time (DPA section update is already overdue — Artefact 2.3). If the playbook in SharePoint is updated and the agent does not detect the change, it will classify new contracts against the old standard until the next agent restart or re-indexing cycle. | M | M | Implement a playbook version hash check at the start of each case (T-5). If the hash differs from the last-known version, the agent pauses classification and notifies Tom and Amelia that the playbook has changed and re-validation is required before the new version is used in production. |
| **LLM provider** | Non-determinism / consistency risk | The LLM may produce different classifications for the same clause on different runs (temperature > 0, prompt sensitivity). This creates inconsistency in the audit record: two identical contracts may receive different deviation reports if processed at different times, undermining Tom's ability to trust the system and creating a legal challenge risk. | M | M | Set LLM temperature to 0 for all classification calls. Add a clause-level result hash to the deviation report: if the same clause appears in a later reprocessing, Tom can see whether the classification changed. For borderline cases (confidence 0.75–0.85), the conservative default should be stable across runs at temperature 0. |
| **Agent configuration store** | Configuration integrity risk | The routing thresholds (0.90/0.80/0.75), liability cap floor (£250k), and DPDI date are scalar constants stored in agent configuration. If misconfigured (e.g., thresholds set to 0.0 in a test environment deployed to production), the agent would classify everything as low-confidence and escalate every clause to Tom, or accept all clauses as MATCH with 0% escalation. | L | H | Store configuration values in a version-controlled configuration file (not environment variables alone); require a named sign-off (Tom or Amelia) on any configuration change before deployment. Include a startup validation check: if any threshold is outside a defined valid range, the agent refuses to start and alerts the ops team. |

---

## 5. Context Engineering Design

### Memory Architecture

| Memory type | Content | Storage mechanism | Lifecycle |
|---|---|---|---|
| **In-context (short-term)** | Current contract's extracted clause sections (text), the relevant playbook section for each clause being compared (T-6), the running list of clause classifications produced so far in this case, and the deviation report being assembled | LLM context window — one prompt per clause comparison (per-clause prompting strategy to manage context size; see retrieval strategy below) | Discarded after each clause classification is written to the deviation report; not persisted between clause comparisons |
| **Semantic (long-term, retrieval)** | Playbook sections for each of the seven clause categories, indexed by clause type label; retrieved on-demand for each clause comparison | In-memory cache loaded from SharePoint at case start (7 sections, total ~2–5KB — small enough to cache in full for the duration of one case) | Loaded once per case at T-5; invalidated and reloaded if the playbook version hash changes between cases |
| **Procedural (static instructions)** | Classification system prompt: the seven clause categories and their names; confidence scoring instructions (verbatim from D4 §4b); output schema (JSON clause classification object from D4 §4b); hard-stop instructions (never generate redline language; never classify as confirmed match if DPA_UNVERIFIED flag applies) | System prompt — versioned alongside agent code; not retrieved at runtime | Static; updated only when the classification protocol is revised; version-stamped so the deviation report records which prompt version was active |

---

### Retrieval Strategy

**What triggers a retrieval call:**
- T-5 triggers one retrieval call per case to load the full playbook from SharePoint. The call fetches all seven clause sections and the version timestamp in a single request.
- T-6 triggers one LLM comparison call per identified clause section. The relevant playbook section (pre-loaded in the in-memory cache) is injected directly into the prompt — this is a cache lookup, not a live retrieval call.
- T-8 triggers a configuration read (not a SharePoint call) to compare the playbook version timestamp against the stored DPDI Act effective date.

**Retrieval target:**
Exact match by clause type, not top-K semantic search. The playbook has seven named sections; each identified clause is labelled by the parser with one of the seven clause_type labels. The retrieval is deterministic: `playbook_cache["liability_cap"]` for a liability cap clause. There is no ambiguous semantic retrieval step in the classification path — this design choice eliminates retrieval false positives and makes the retrieval quality fully deterministic.

The only exception: if T-4's clause parser assigns an `unrecognized` clause_type, the agent attempts a semantic match against all seven sections (top-1 only) to determine whether the clause is a paraphrased version of a known category. If top-1 similarity is below a defined threshold, the clause is logged as UNRECOGNIZED and ET-5 conditions are checked.

**How retrieval quality is evaluated:**
Since retrieval is deterministic (exact match by clause_type), the retrieval quality risk is not false-positive section matching — it is the clause_type labelling accuracy of T-4's parser. Retrieval quality is therefore evaluated through the weekly 10% audit: if Tom repeatedly overrides clause_type labels assigned by the parser (e.g., an IP clause being labelled as a termination clause), this is a parser accuracy problem, not a retrieval problem, and is tracked separately from classification accuracy in the audit log.

For the unrecognized-clause semantic retrieval path: the similarity threshold must be set conservatively (≥ 0.85) to avoid false matches that send the wrong playbook section into the classification prompt. Calibration: if the LLM classifies a clause against the wrong playbook section and produces a spurious MATCH or DEVIATION, Tom's override at the routing confirmation step is the detection signal.

**How retrieval costs are managed:**
The full playbook cache is loaded once per case (~7 sections × ~200 tokens per section = ~1,400 tokens) and held in memory for the duration of the case. All seven clause comparisons (T-6) reuse this cached copy — there is no per-clause SharePoint API call. The dominant cost driver is the per-clause LLM comparison call (T-6). For a 40-page contract with approximately 20 identifiable clause sections, the total token cost per case is approximately:
- Playbook load: 1,400 tokens (once per case)
- Per-clause comparison: ~800 tokens per call (clause text + playbook section + classification prompt) × 20 clauses = 16,000 tokens
- Report generation: ~2,000 tokens
- **Total estimated: ~19,400 tokens per case** [Assumption A-D5-8]

At 300 cases/quarter and Claude Sonnet pricing (~$3/M tokens input, ~$15/M tokens output), total estimated token cost per quarter is approximately £250–350 [Assumption — pricing and model subject to change].

---

### Key Context Engineering Risks

1. **Playbook ambiguity produces classification inconsistency.** The playbook position statements are written in legal prose, not in structured rule format. A position like "liability cap should be no less than 12 months of contract value" requires the LLM to (a) identify the stated cap value in the vendor's clause, (b) calculate 12 months of contract value (which may not be in the contract document), and (c) assess the comparison. Steps (b) and (c) depend on information the agent may not have — creating a systematic failure mode for value-dependent comparisons. These cases must be routed conservatively (DEVIATION_ESCALATION) unless the contract states the annual value explicitly.

2. **Clause section parser accuracy degrades on non-standard document structures.** Vendor contracts vary widely in formatting: some use numbered sections with headings, others use lettered schedules, others embed key terms in recitals or annexes. A heading-based parser will miss clauses in unusual locations; a purely semantic parser may over-extract (classifying boilerplate indemnities in signature blocks as IP clauses). The parser's accuracy on edge-case document structures is unknown until tested on Helix's actual contract corpus. The weekly audit must track not just classification accuracy but clause extraction completeness.

3. **Stale playbook deployed after an update creates silent compliance drift.** If the playbook is updated in SharePoint and the version hash check at T-5 fails to detect the change (e.g., the document is re-saved with the same filename but no version-increment), the agent continues classifying against the old standard without any flag. This is a structural risk: the agent's correctness is bounded by its reference data, and the reference data is maintained by a human process that may not follow version-control discipline. Mitigation: enforce SharePoint version numbering discipline and validate the playbook version label (not just the file hash) at startup.

---

## 6. Compounding Opportunities

| Integration built | Future agent that could reuse it | Reuse mechanism |
|---|---|---|
| **Ironclad REST API integration** (case creation, field writes, status transitions, case queries) | WS2 standard-deviation redlining agent (C-4); WS4 sign-off package preparation agent (C-8) | Both agents write outputs to Ironclad case records and read case state. The same API client, authentication configuration, and field schema used by the Contract Classifier Agent are directly applicable; marginal integration cost for the next agent is near-zero for Ironclad. |
| **Word DOCX clause section parser** (T-4) | WS2 redlining agent (C-4) reads the vendor document to insert Track Changes redlines into the correct clause location | The parser produces the clause structure map (section IDs, text locations) that the redlining agent needs to insert markup into the correct part of the document; building this once removes a major technical risk for WS2. |
| **SharePoint playbook retrieval and caching** (T-5) | WS2 redlining agent (C-4) needs the playbook position to generate substitute clause language | Same SharePoint connection, same version-check mechanism, same JSON cache structure. The retrieval layer is reused directly; the downstream use (classification vs. redline drafting) is different but the data source is identical. |
| **LLM classification framework** (prompt architecture, confidence scoring method, output schema) | WS3 counteroffer drafting support agent (C-6); future DPA compliance audit agent | The prompt design (classification instruction + playbook context + structured JSON output schema) is a reusable template. A future DPA compliance agent or a redline quality-checker can inherit the confidence scoring protocol and output schema with minimal modification. |
| **Outlook intake monitoring** (T-1/T-2 + Microsoft Graph API setup) | Any future agent in the Legal & Commercial team that needs to monitor email channels for inbound documents (e.g., a WS4 vendor response tracker watching for counterparty replies) | The Microsoft Graph API registration, authentication, and inbox monitoring pattern are reusable infrastructure components once the IT security approval is obtained — not just for this agent but for any email-triggered automation in the team. |

---

## 7. Assumption Log

> **Assumption [A-D5-1]:** Counterparty name is present in the email subject line or the first page of the vendor contract document and can be extracted by the parser without manual intervention. If the email subject is non-standard (e.g., "RE: Legal review") and the document's first page does not clearly state the counterparty, T-3 will require Tom to manually enter the counterparty name in the Ironclad case record.
> **Why it matters:** Intake automation completeness depends on this. If counterparty extraction fails frequently, T-3 is only partially agentic.
> **Confidence:** Medium

> **Assumption [A-D5-2]:** The DPDI Act effective date and routing threshold constants can be stored in a version-controlled configuration file or environment variable accessible to the agent at runtime. No external secrets manager is assumed.
> **Why it matters:** The DPA currency check (T-8) and escalation logic (ET-1) depend on these constants being present and correct at runtime.
> **Confidence:** High — straightforward configuration pattern

> **Assumption [A-D5-3]:** Ironclad supports custom fields on contract cases sufficient to store: `agent_deviation_report` (JSON, large text), `routing_confirmed_by` (user reference), `routing_confirmed_at` (timestamp), `routing_tier` (enum), and `agent_status` (enum). Custom field creation requires admin access to Ironclad.
> **Why it matters:** The entire governance gate depends on these fields existing and being writable only by the correct parties.
> **Confidence:** Medium — standard CLM platforms support custom fields; Ironclad-specific capability to be confirmed.

> **Assumption [A-D5-4]:** Microsoft Graph API access to the Helix Legal & Commercial Outlook shared mailbox can be obtained via a registered Azure AD application with `Mail.Read` scope. The IT security approval timeline is estimated at 2–8 weeks [not stated in scenario].
> **Why it matters:** The Outlook integration path is the most likely Day 1 deployment blocker.
> **Confidence:** Medium — standard Microsoft 365 integration pattern; approval timeline is organisation-specific.

> **Assumption [A-D5-5]:** SharePoint "Position Statements v3.4" is stored as a Word document or HTML page containing extractable text. It is not a scanned image or a locked PDF. Microsoft Graph API's Files endpoint is accessible to the same service account used for Outlook integration.
> **Why it matters:** Playbook accessibility is the prerequisite for all clause comparison tasks.
> **Confidence:** Medium — SharePoint typically stores documents in text-extractable formats; the specific file format at Helix is unconfirmed.

> **Assumption [A-D5-6]:** Helix will obtain a Data Processing Agreement with the chosen LLM provider covering vendor contract data (commercially sensitive text). Amelia Forsythe will confirm that sending inbound vendor contract text to an external LLM does not create legal privilege issues under UK law.
> **Why it matters:** Without legal clearance, the entire agent is blocked at the LLM layer.
> **Confidence:** Medium — enterprise LLM DPAs are standard; legal privilege analysis is Helix-specific.

> **Assumption [A-D5-7]:** Ironclad's REST API supports querying case records by counterparty name and returning a list of routing override events per case. If not supported natively, a lightweight custom field (`override_count` per counterparty) can be maintained by the agent.
> **Why it matters:** ET-6 (systematic misalignment detection) depends on this query capability.
> **Confidence:** Low — CLM reporting query capabilities vary; not confirmed in scenario.

> **Assumption [A-D5-8]:** Each clause comparison call uses approximately 800 tokens (input: clause text + playbook section + prompt; output: classification JSON). A 40-page contract contains approximately 20 identifiable clause sections. These figures are estimates derived from typical legal clause lengths; actual token consumption will vary by contract complexity and vendor drafting style.
> **Why it matters:** Token cost per case drives the TCO model validated in D3. If actual consumption is 3× the estimate (e.g., complex contracts with verbose clauses), the economics remain favourable but the payback period extends.
> **Confidence:** Low — not validated against actual contract samples.
