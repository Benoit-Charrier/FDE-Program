# D4 — Integration Preamble
## Greenfield Health Systems: Medical Claims Adjudication Transformation

*Source inputs: `Deliverables/D4_preamble_capability_spec.md` §3 (system inventory starting list), `Scenario/scenario_context.md`. Every system in §3 of the capability preamble has a corresponding row in §1 below. Systems not named in `Scenario/scenario_context.md` are labelled as assumptions.*

> **Feeds directly into:** D4a §8 and D4b §8 (autonomy matrix enforcement mechanism). Capability spec authors must read §3 sign-off integrity risk entry before finalising those sections.

---

## §1. System and Data Inventory

*Scenario_context.md names no specific systems. All system names below are assumptions unless noted. "Named in scenario" means the function (not the platform) is stated in the scenario.*

| # | System / Source | Data needed | Access type | Inferred availability | Gap / Risk | Priority | Pass 7 decision |
|---|-----------------|-------------|-------------|-----------------------|------------|----------|-----------------|
| S-01 | **Clearinghouse / provider portal** (inbound intake) — A-P1-1 | Inbound claim submissions in EDI 837, PDF, and portal format; submission metadata (provider NPI, submission timestamp) | Event trigger (push) or Read (poll) | API likely available — standard payer EDI clearinghouse infrastructure; submission gateway is a commodity component in the payer space | Intake mechanism (push vs. pull) and security approval not confirmed — see G-1 | Required | Full contract |
| S-02 | **Member eligibility system** — A-P1-2 | Member ID, plan ID, date-of-service active coverage status; eligibility discrepancy context when binary lookup returns a mismatch | Read (real-time lookup) | API likely available — eligibility verification is a foundational payer operation; HIPAA 270/271 eligibility transaction is an industry standard | System name and API documentation unconfirmed. Not named in scenario — existence and API availability are assumed. | Required | Full contract |
| S-03 | **Code validation reference (ICD-10 / CPT)** — A-P1-3 | ICD-10 diagnosis code validity; CPT procedure code validity; procedure-diagnosis pair plausibility rules | Read (batch-loaded structured lookup) | API likely available — licensed CMS / AMA code sets are available via structured API or flat file; code pairing tables are a standard adjudication component | Plausibility reference (novel combinations) requires vector retrieval augmentation beyond structured table — see §4 retrieval design in D4 preamble. Not named in scenario — existence and API availability are assumed. | Required | Full contract |
| S-04 | **Prior authorisation system** — A-P1-4 | Prior auth record presence (yes/no) for member + procedure + service date; authorised unit counts; partial-match context | Read (real-time lookup) | API likely available — prior auth management is a core payer function; most enterprise payer platforms expose a prior auth query API | System name and read/write scope unconfirmed. Not named in scenario — existence and API availability are assumed. Write access must be explicitly excluded from integration contract. | Required | Full contract |
| S-05 | **Fee schedule system** — A-P1-5 | Contracted rate by provider + procedure code + plan; cost-sharing rules; modifier code adjustments | Read (on-demand retrieval) | API likely available — fee schedule management is a standard payer infrastructure component | Contract exception rules (S-06) are distinct from standard fee schedule rates — this system covers standard path only. Not named in scenario — existence and API availability are assumed. | Required | Full contract |
| S-06 | **Contract document store** — A-P1-6 | Provider/payer contract exception clauses by provider ID + payer ID + procedure code range; amendment status flags | Read (on-demand retrieval) | API unknown — A-D0C-6 in D3: contract exception storage mechanism is unconfirmed; may exist as structured database, document management system, or institutional knowledge | See G-2. Not named in scenario — existence and API availability are assumed. | Required (for WS1-JtD-3 full automation; Degrading if absent per ADR-1: standard path proceeds, contract exception path routes to HITL) | SCOPE-OUT |
| S-07 | **Claims management system** (internal ClaimRecord store + workflow engine) — write API | ClaimRecord state transitions (all 16 defined in D4 preamble §2); physician HITL queue writes; HITL exception queue writes; custom field writes — WS1: `clinical_classification_id`, `rejection_codes`, `payment_amount`, `hitl_disposition`, `hitl_queue_type`, `hitl_assigned_to`; WS2: `clinical_classification_id_ws2`, `physician_packet_id`, `hitl_disposition` | Read-Write (real-time) | API likely available — internal system; the agent requires write access to its own workflow store. Named in scenario by function ("claims processing team" — scenario_context.md §3); API specifics and integration maturity are assumptions beyond what is stated. | Whether state machine enforcement is implemented at the API layer (system-enforced) or only in agent code (procedure-dependent) is the highest-priority integration risk — see G-3 and §3 sign-off integrity risk. | Required | Full contract |
| S-08 | **Physician review queue interface** (HITL delivery) — A-P1-15 | Delivery of EscalationPackets and pre-filled review packets to physician HITL queue; acknowledgement and resolution token capture; physician identity and timestamp logging | Read-Write (real-time push + resolution read) | Unknown — no physician review system is named in the scenario; may be an existing claims review tool, an EHR physician portal, or a purpose-built queue interface. Not named in scenario — existence and API availability are assumed. | See G-4. This system is the primary URAC/NCQA compliance evidence store — its audit trail design is the most consequential integration risk in the engagement. | Required | SCOPE-OUT |
| S-09 | **HITL exception management system** — A-P1-16 | Exception processor queue receives EscalationPackets; resolution decisions are written back; disposition feeds ClaimRecord state transition | Read-Write | API likely available — assumed to be a module of the claims management system (S-07) or a workflow tool; exception queue management is standard in payer operations | May be the same system as S-07 (claims management platform includes a queue/workflow module) — confirm in discovery to avoid duplicate integration contracts. Not named in scenario — existence and API availability are assumed. | Required | Full contract |
| S-10 | **Audit log system** — A-P1-18 | Append-only AuditLogEntry records; all agent actions; compliance-grade retention and immutability guarantees | Write (append-only) | API likely available — an audit log store is a standard compliance infrastructure component; may be a dedicated service or a module of the claims management platform | Append-only immutability guarantee and compliance-grade retention (7 years for clinical records — see §3) must be confirmed at the API level, not assumed from platform marketing. Not named in scenario — existence and API availability are assumed. | Required | Full contract |
| S-11 | **Payment processing system** — A-P1-13 | Approved claim record with payment_amount, approval token, and audit_log_entry ID; write to payment queue for disbursement | Write (event or API push) | API likely available — payment processing is a core payer function; write integration to the payment system is standard in adjudication pipelines | Payment processing is downstream of WS1 — agent writes to a payment queue and the payment system picks up. Write access scope and payment instruction format must be confirmed before deployment. Not named in scenario — existence and API availability are assumed. | Required | Full contract |
| S-12 | **Provider portal / clearinghouse** (outbound rejection notices) — A-P1-14 | Rejection notice delivery to providers; machine-readable rejection_codes array; provider acknowledgement tracking | Write (push) | API likely available — standard payer-to-provider clearinghouse communication; EDI 835 remittance and rejection notice delivery are commodity | May be the same clearinghouse as S-01 (inbound intake and outbound notices through the same partner) — confirm in discovery. Not named in scenario — existence and API availability are assumed. | Required | Full contract |
| S-13 | **Clinical notes source system** — A-P1-7 | Treating provider clinical notes for WS2 packet assembly: treatment notes, operative reports, lab results, prior auth clinical documentation | Read (on-demand retrieval) | Unknown — A-D0C-7 in D3: system identity unknown; may be an EHR API, a FHIR-compliant provider API, a document management system, or fax-only; HIPAA BAA and access controls unknown | See G-5. This is the Wave 2 hard blocker for WS2 JtD-2. Not named in scenario — existence and API availability are assumed. | Required (WS2 Wave 2) | SCOPE-OUT |
| S-14 | **Claims history database** — A-P1-8 | Member's prior claims history for relevant diagnosis range and configurable lookback period; used for WS2 packet assembly context | Read (on-demand retrieval) | API likely available — historical claims records are internal data; assumed queryable from the same claims management platform (S-07) | Lookback period and query granularity (diagnosis cluster vs. all claims for member) must be confirmed with the ops team before WS2 spec is finalised. Not named in scenario — existence and API availability are assumed. | Important (WS2 JtD-2 packet completeness degrades if absent; physician must retrieve history manually) | Full contract |
| S-15 | **Medical necessity criteria system** — A-P1-9/10 | InterQual, Milliman, or proprietary CMO-maintained criteria; sections by procedure type and diagnosis code range; used for WS1 T-08 classifier augmentation and WS2 JtD-1/JtD-2 | RAG (retrieval-augmented) | Unknown — format and hosting unconfirmed; may be a licensed vendor API (InterQual Connect, MCG Health), a structured in-house database, or PDF/scan-based documents. Not named in scenario — existence and API availability are assumed. | See G-6. Format confirmation (machine-readable vs. scan-based) is the blocking prerequisite for the retrieval index build. | Important (classifier accuracy degrades without augmentation; physician packet incomplete without criteria section) | SCOPE-OUT |
| S-16 | **Configuration management system** (calibration artefacts) | Signed classifier calibration artefacts (threshold value, CMO sign-off, holdout set metadata); agent version records; system prompt versions | Read (agent startup) | API likely available — internal configuration store; may be a secrets manager, a configuration database, or a file-based store | CMO sign-off must be captured as a structured record in this system before go-live — the mechanism for recording the signature (digital signature, approval workflow, manual entry) must be confirmed. Not named in scenario — existence and API availability are assumed. | Required | Full contract |

---

## §2. Gap Analysis

*Gap entries produced for every §1 row with "API unknown," "Unknown," or "Manual or document-only" inferred availability.*

---

```
Gap G-1: Clearinghouse / provider portal — intake trigger mechanism
What the agent cannot do without it: WS1 T-01 (claim format parsing and canonical record
  extraction) has no trigger; claim intake does not start. No claims enter the pipeline.
Severity: Blocking (agent cannot launch)
Mitigation options:
  1. Confirm with IT that the existing clearinghouse partner supports an event-push
     mechanism (webhook or EDI batch delivery to an agent-readable endpoint) — most
     clearinghouses support both; this may require only a configuration change, not a
     new integration.
  2. Implement a polling mechanism against an internal claims staging table that the
     clearinghouse already populates via existing EDI pipeline — agent polls for
     RECEIVED-state records at a configurable interval (e.g., every 60 seconds).
  3. Defer EDI intake to a prerequisite Intake & Anomaly Agent deployment (D3 §2,
     Agent 1) and have WS1 pick up from the normalised ClaimRecord queue only —
     reducing WS1's intake dependency to an internal queue read.
Discovery action: "Does the current EDI clearinghouse partner support an event or webhook
  notification to an internal endpoint when a new claim submission arrives? If not, does
  the claims management system maintain a staging table of inbound claims that a new
  process can poll?"
```

---

```
Gap G-2: Contract document store — API availability and structure
What the agent cannot do without it: WS1 T-10 (contract exception handling) cannot
  access exception rules. Claims with contract exception flags (ET-06) route to HITL
  exception processor; the standard payment path for ~2% of WS1 claims is blocked.
  WS1-JtD-3 cannot reach Fully Agentic archetype (D3 ADR-1) until this gap is resolved.
Severity: Degrading (agent launches with reduced capability — standard-path payment
  determination proceeds; contract exception path routes to HITL exception processor
  indefinitely until gap is resolved)
Mitigation options:
  1. Confirm with VP Operations that contract exception rules are stored in a structured,
     queryable system (database, contract management platform) — if so, request API
     documentation and include in Pass 7 integration contracts.
  2. If rules are currently in documents (Word, PDF, email), scope a pre-deployment
     data encoding project to produce a structured contract exception table as a Wave 1
     prerequisite for WS1-JtD-3 automation (D3 ADR-1 revisit condition).
  3. Accept the degraded state at launch: WS1-JtD-3 standard path auto-approves;
     contract exception path routes to HITL at ET-06; Wave 1 go-live proceeds without
     full automation; promote WS1-JtD-3 to Fully Agentic in Wave 1.5 after contract
     rules are encoded.
Discovery action: "Where are Greenfield's negotiated contract exception rates with in-scope
  providers and payers currently stored? Is there a contract management system with a
  queryable API, a shared document folder, or are rate exceptions tracked in processor
  institutional knowledge? How many active exception agreements are in scope for Wave 1?"
```

---

```
Gap G-3: Claims management system — state machine enforcement at API layer
What the agent cannot do without it: If the claims management system does not enforce
  ClaimRecord state machine transitions at the API layer, the PENDING_PHYSICIAN_REVIEW →
  APPROVED bypass (the primary URAC/NCQA compliance gate) is procedure-dependent on agent
  code correctness only. WS1 T-09 could theoretically execute on a PENDING_PHYSICIAN_REVIEW
  claim if a bug or misconfiguration allows it. This is not a task that "cannot launch" —
  it is a governance risk that changes the enforcement mechanism classification in D4a §8
  and D4b §8.
Severity: Blocking if state machine enforcement is required to be system-enforced
  (URAC/NCQA certification may require demonstrated technical enforcement, not reliance
  on agent code alone); Degrading if a procedural control is acceptable
Mitigation options:
  1. Confirm with IT whether the claims management platform supports write-level state
     guards (workflow engine rules that reject state transitions not permitted by the
     state machine) — if yes, the gate is system-enforced; document as such in D4a §8.
  2. If the platform does not enforce state transitions at the API layer, implement a
     middleware guard: a dedicated API wrapper that validates the requested state transition
     against the defined state machine before forwarding to the platform — this makes
     the guard system-enforced at the middleware layer.
  3. If neither option is feasible before go-live, the enforcement mechanism is procedure-
     dependent; document this in D4a §8 §12 as a governance risk; add a post-deployment
     monthly verification that no T-09 execution record exists for any claim that was
     simultaneously in PENDING_PHYSICIAN_REVIEW state.
Discovery action: "Does the claims management platform support configurable workflow state
  guards that reject write requests for state transitions not allowed by the defined state
  machine? For example, can we configure the system to return a 409 Conflict error if a
  payment approval write is attempted on a claim in the pending_physician_review state?"
```

---

```
Gap G-4: Physician review queue interface — system unknown
What the agent cannot do without it: WS1 T-12 (escalation packet assembly for clinical
  routing) cannot deliver EscalationPackets to the physician HITL queue. WS2 JtD-2
  (packet delivery to physician queue) is entirely blocked. The URAC/NCQA compliance
  gate cannot be implemented — clinical claims cannot reach physician review.
  This is a complete block on all clinical-path claims.
Severity: Blocking (clinical path agent cannot launch; URAC/NCQA compliance gate is absent)
Mitigation options:
  1. Confirm with Dr. Webb's team what system physicians currently use to receive and
     review escalated claims — if an existing clinical review workflow tool exists (e.g.,
     a component of the claims management platform, an EHR inbox, or a purpose-built
     review tool), the integration contract is scoped against that system in Pass 7.
  2. If no existing tool exists, scope a physician review queue interface as a Wave 1
     build component — a minimal HITL queue UI that accepts EscalationPacket records,
     presents them to physicians, and captures the approval token with identity and
     timestamp. This adds a build scope item to Wave 1.
  3. As a Wave 1 fallback: deliver escalation packets via email with a structured
     format and capture physician sign-off via a web form that writes to the audit log
     system (S-10) — degraded UX but URAC/NCQA compliant if identity and timestamp
     are captured. This is acceptable only as a bridge, not a steady-state solution.
Discovery action: "What system does a physician or advanced practice provider currently
  use when they need to review a claim before finalisation? Is there an existing queue
  or inbox in the claims management platform or EHR system that handles physician review
  requests today, even manually?"
```

---

```
Gap G-5: Clinical notes source system — system identity and API availability unknown
What the agent cannot do without it: WS2 JtD-2 (clinical context assembly) cannot
  retrieve clinical documentation. The pre-filled review packet contains no clinical
  notes; physicians receive only structured claim data without provider documentation.
  WS2's primary economic value (reducing physician review time from manual to
  ~3 min/claim per Dr. Webb's Exchange 3 estimate) is not realised.
Severity: Blocking for WS2 Wave 2 deployment as specified; D3 §5 explicitly identifies
  this as a conditional assignment — if the API is inaccessible, WS2 JtD-2 reverts to
  Human-led + Agent Support
Mitigation options:
  1. Confirm with IT and clinical ops whether treating provider clinical notes are
     accessible via a FHIR-compliant provider API or a clearinghouse clinical document
     exchange (e.g., CommonWell, Carequality) — HIPAA BAA requirements apply and
     must be addressed before agent access is granted.
  2. If notes are submitted by providers as attachments to the claim (EDI 275 or portal
     upload), confirm whether they are stored in the claims management platform (S-07)
     and accessible from the same API — this would eliminate the need for a separate
     integration.
  3. If programmatic access is blocked by EHR vendor restrictions or fax-only workflows,
     scope WS2 JtD-2 as Human-led + Agent Support at Wave 2 launch: physician retrieves
     documents manually; agent processes whatever is provided and assists with prior auth
     history synthesis and structured note-taking only (D3 §5 fallback path).
Discovery action: "How do treating providers currently submit clinical documentation
  to support claims with clinical content — is it as an EDI 275 attachment, a portal
  upload, a fax, or a direct EHR-to-payer API submission? Is the documentation stored
  in a system that Greenfield's internal processes can query programmatically?"
```

---

```
Gap G-6: Medical necessity criteria system — format and availability unknown
What the agent cannot do without it: WS1 T-08 (clinical content routing classification)
  runs without criteria augmentation, reducing classifier accuracy on borderline claims
  and replicating the inconsistency that drives the 41% overturn rate (D3 §1).
  WS2 JtD-2 (pre-filled review packet) cannot include the applicable criteria section;
  physician reviews without criteria context. Both impacts are Degrading, not Blocking —
  the agent runs; accuracy and packet completeness suffer.
Severity: Degrading (WS1 classifier accuracy and WS2 packet completeness degrade;
  agent launches but at reduced quality)
Mitigation options:
  1. Confirm with CMO team whether criteria are licensed from a vendor (InterQual,
     MCG Health, Milliman) and whether that vendor provides a structured API or
     machine-readable export format — most enterprise clinical criteria vendors offer
     an API or structured XML/JSON export.
  2. If criteria exist as PDFs, engage the CMO team in a pre-deployment OCR and
     chunking exercise: convert criteria PDFs to text-extractable format, build the
     retrieval index before go-live, and establish a version control workflow.
  3. As a minimum viable approach for Wave 1: have the CMO team identify the 10–15
     most common procedure types in the WS1 volume and produce structured criteria
     summaries for those types only — covering the majority of volume with a manageable
     first chunking effort; expand to full criteria coverage in Wave 2.
Discovery action: "Does Greenfield license clinical criteria from a vendor (InterQual,
  MCG Health, Milliman, or similar), and does that vendor provide a machine-readable
  API or structured export? If Greenfield uses proprietary CMO-developed criteria,
  in what format are they stored and maintained?"
```

---

## §3. Integration Risk Register

*All five risk types assessed for each system. A type is omitted only where the reason it does not apply is stated.*

| System | Risk type | Risk description | Likelihood | Impact | Mitigation |
|--------|-----------|------------------|---------:|--------:|------------|
| S-01 Clearinghouse / provider portal | Data quality | EDI 837 submissions may be malformed, PDF submissions may be illegible, portal submissions may have non-standard field mappings — Intake Agent handles these but WS1 receives normalised records only | L | M | Intake & Anomaly Agent normalisation is the guard; WS1 T-01 validates the canonical record schema before processing |
| S-01 | API availability | Clearinghouse EDI infrastructure is commodity and high-availability; batch EDI delivery has known latency patterns | L | M | Polling fallback (option 2 in G-1) provides resilience if event push fails |
| S-01 | Legal / compliance | HIPAA covered entity data transmission; clearinghouse agreements include BAA requirements | M | H | BAA confirmation is a pre-deployment checklist item (S-01 is a covered function); standard payer clearinghouse agreements cover this |
| S-01 | Audit trail | Inbound submission timestamp and format recorded in ClaimRecord.created_at and submission_format at intake | L | L | Intake normalisation step records submission provenance; no additional logging needed at this layer |
| S-01 | Sign-off integrity | Not applicable — S-01 is an inbound data channel, not an approval gate; no sign-off mechanism involved | — | — | N/A |
| S-02 Member eligibility | Data quality | Eligibility data may be subject to batch update lag — coverage confirmed as of last batch sync, not real-time; data-of-service coverage gaps may reflect lag not actual ineligibility | H | H | T-03 eligibility discrepancy resolution explicitly handles data-lag cases; ET-03 escalates unresolvable discrepancies to HITL rather than auto-denying |
| S-02 | API availability | Eligibility APIs in payer infrastructure are typically high-availability; P95 ≤ 5 seconds is achievable in most production environments | L | H | Agent must implement a timeout (5s) with one retry and ET-03 escalation on persistent failure — cannot auto-adjudicate without eligibility confirmation |
| S-02 | Legal / compliance | HIPAA PHI — member eligibility data contains protected health information; read-only access; no write exposure | M | H | Read-only scope must be confirmed in integration contract; no write access granted to eligibility system |
| S-02 | Audit trail | T-02 eligibility lookup result is recorded in AuditLogEntry input_summary for every claim | L | L | Standard audit logging covers this |
| S-02 | Sign-off integrity | Not applicable — S-02 is a data lookup, not an approval gate | — | — | N/A |
| S-03 Code validation reference | Data quality | ICD-10 and CPT code sets are updated annually; a stale reference produces incorrect validity results; code pairing plausibility rules may not cover novel combinations | M | M | Pre-deployment checklist item 2 (version control); T-04 and T-05 check reference version at pipeline startup; ET-06 flags stale reference |
| S-03 | API availability | Licensed code sets are available as flat files or API; structured table lookups are low-latency | L | M | Batch-loaded reference means API unavailability does not block in-flight processing; pipeline restarts on reconnection |
| S-03 | Legal / compliance | CMS and AMA code set licenses require paid subscription; use of unlicensed code sets is a compliance risk | M | M | License confirmation is a pre-deployment prerequisite; IT and legal must confirm licensing scope covers agent use |
| S-03 | Audit trail | Code lookup results recorded in AuditLogEntry for T-04 and T-05 actions | L | L | Standard audit logging covers this |
| S-03 | Sign-off integrity | Not applicable — S-03 is a reference lookup, not an approval gate | — | — | N/A |
| S-04 Prior auth system | Data quality | Prior auth records may be incomplete (partial match: different units authorised vs. claimed) or stale (auth expired, amendment pending); these are the explicit trigger conditions for ET-04 and T-07 | H | H | T-07 partial-match resolution logic; ET-04 HITL escalation; PRIOR_AUTH_UNIT_TOLERANCE_PCT configurable parameter |
| S-04 | API availability | Prior auth APIs vary in maturity; some payer systems expose well-documented APIs; others are internal and poorly documented | M | H | Timeout (5s) with one retry; ET-04 escalation on persistent failure; no payment determination can proceed without prior auth confirmation for procedures requiring it |
| S-04 | Legal / compliance | Prior auth records contain PHI; read-only scope required; write access to prior auth records is explicitly excluded from agent authority (D4 preamble §2 ClaimRecord hard stops) | M | H | Write exclusion must be technically enforced in integration contract (read-only API key or scope restriction); agent write access to prior auth system is a critical defect |
| S-04 | Audit trail | T-06 and T-07 lookup results and match analysis recorded in AuditLogEntry | L | L | Standard audit logging covers this |
| S-04 | Sign-off integrity | Not applicable — S-04 is a data lookup; prior auth confirmation is an input to the adjudication decision, not the approval gate itself | — | — | N/A |
| S-05 Fee schedule | Data quality | Fee schedules are updated periodically (plan year changes, renegotiated rates); a stale fee schedule produces incorrect payment amounts; modifier codes may apply rate adjustments not captured in the base rate | M | H | Pre-deployment checklist item 2 (version control); pipeline startup version check; ET-06 flags expired reference; payment amount overpayment risk if stale |
| S-05 | API availability | Fee schedule systems are internal and typically high-availability; on-demand retrieval with low-latency | L | M | Timeout with retry; ET-06 escalation on persistent failure |
| S-05 | Legal / compliance | Fee schedule data may include negotiated rates that are commercially sensitive; read-only access; no compliance exposure beyond confidentiality | L | M | Read-only access scope in integration contract |
| S-05 | Audit trail | T-09 fee schedule lookup and payment calculation recorded in AuditLogEntry.output_summary | L | L | Standard audit logging covers this |
| S-05 | Sign-off integrity | Not applicable — fee schedule is a reference input; payment approval is the approval gate (see S-07 sign-off integrity) | — | — | N/A |
| S-06 Contract document store | Data quality | Contract exception rules may exist as unstructured documents (Word, PDF, email threads) with no machine-readable structure; amendment status tracking may be manual | H | H | G-2 mitigation option 2 (data encoding project before WS1-JtD-3 promotion); ADR-1 holds WS1-JtD-3 at Agent-led + Human Oversight until this is resolved |
| S-06 | API availability | API unknown — system may not exist as a queryable data store | H | M | ET-06 HITL escalation is the fallback; WS1 launches in degraded mode per ADR-1 |
| S-06 | Legal / compliance | Contract exception data is commercially sensitive; access controls must limit agent to read-only scope | M | M | Read-only scope in integration contract when built |
| S-06 | Audit trail | T-10 contract exception lookup and result recorded in AuditLogEntry | L | L | Standard audit logging covers this when system exists |
| S-06 | Sign-off integrity | Not applicable — S-06 is a reference data source; contract exception sign-off is handled through ET-06 HITL escalation path | — | — | N/A |
| S-07 Claims management system | Data quality | ClaimRecord field values entered or updated by other processes (e.g., prior clearinghouse normalisation) may have different formats than the agent expects; concurrent updates to the same record from multiple processes must be handled | M | H | Canonical record schema validated at T-01; optimistic locking or state-check-before-write pattern in all state transition writes |
| S-07 | API availability | Internal system — highest availability requirement; agent processing pipeline is blocked if this system is down | M | H | Circuit breaker with claim-level queuing; failed claims re-queued with SLA clock awareness; ops alert on sustained unavailability |
| S-07 | Legal / compliance | PHI data store; write access is the highest-risk operation; agent writes only to defined fields — WS1: `state`, `clinical_classification_id`, `rejection_codes`, `payment_amount`, `hitl_disposition`, `hitl_queue_type`, `hitl_assigned_to`, `updated_by`, `updated_at`; WS2: `state`, `clinical_classification_id_ws2`, `physician_packet_id`, `hitl_disposition`, `updated_by`, `updated_at` | M | H | Write scope must be field-level in integration contract; no bulk delete or schema modification access |
| S-07 | Audit trail | Every ClaimRecord write produces an AuditLogEntry via T-11; audit trail is the primary compliance artefact | L | H | AuditLogEntry generation failure triggers ET-07 (claim suspended with incomplete_audit flag); audit integrity is architecturally enforced |
| **S-07** | **Sign-off integrity** | **CRITICAL — PRIMARY ENFORCEMENT MECHANISM ASSESSMENT:** The URAC/NCQA compliance gate (clinical claims must not reach payment without physician sign-off) is intended to be system-enforced: T-09 (payment calculation) reads only from claims in ADMIN_CLEARED state; claims in PENDING_PHYSICIAN_REVIEW state are architecturally excluded from T-09 reads. **The system-enforced classification holds only if the claims management platform enforces state machine transitions at the API layer** — that is, if a write request to move a claim from PENDING_PHYSICIAN_REVIEW to PAYMENT_CALCULATING is rejected at the platform API with a 4xx error unless a valid physician approval token is present in the request. **If the platform does not enforce state machine guards and accepts any state transition write**, the gate is procedure-dependent: it relies on the agent code never issuing a T-09 call for a PENDING_PHYSICIAN_REVIEW claim. Procedure-dependent enforcement creates a compliance risk if the agent code contains a bug, is misconfigured, or is called directly via API by a developer. **Classification decision for D4a §8 and D4b §8:** Until G-3 discovery confirms system-enforced state guards, the enforcement mechanism must be classified as **procedure-dependent with a middleware guard recommendation** (G-3 mitigation option 2). If confirmed as system-enforced, update D4a §8 and D4b §8 enforcement mechanism statements accordingly. | H | H | G-3 mitigation option 2 (middleware state transition guard); monthly audit of T-09 execution records vs. PENDING_PHYSICIAN_REVIEW state history; this risk must appear as a governance risk in D4a §12 and D4b §12 until system-enforced status is confirmed |
| S-08 Physician review queue | Data quality | Physician review decisions must be captured with identity (not just checkbox acknowledgement); partial or unsigned approvals do not satisfy URAC/NCQA requirements | H | H | Approval token must include: reviewer identity (physician ID), timestamp, claim_id, and decision type — minimum required fields confirmed in G-4 discovery |
| S-08 | API availability | System unknown — availability cannot be assessed | H | H | G-4 mitigation option 3 (email + web form bridge) as fallback only; system confirmation is the blocker |
| S-08 | Legal / compliance | PHI in escalation packets and review records; HIPAA access controls required for physician access to claim data; minimum necessary standard applies | H | H | Access scope limited to claims in PENDING_PHYSICIAN_REVIEW state assigned to this physician; no bulk record access |
| S-08 | Audit trail | Physician approval token capture is the primary URAC/NCQA compliance evidence; must be immutable, timestamped, and queryable by claim_id | H | H | Approval token must write to S-10 (audit log) simultaneously with ClaimRecord update; loss of audit record is a URAC/NCQA compliance event |
| **S-08** | **Sign-off integrity** | **Related to S-07 sign-off integrity assessment above.** The physician review queue system is the capture point for the approval token that unlocks the ClaimRecord state transition from PHYSICIAN_REVIEWING to APPROVED. If S-08 allows physicians to record determinations without capturing identity and timestamp (e.g., a shared account login, an unsigned batch approval), the sign-off is present in the ClaimRecord but is not individually attributable — failing the URAC/NCQA individual physician sign-off requirement. **Classification:** Procedure-dependent on S-08 system design — the queue interface must require authenticated individual login before a determination can be recorded. This cannot be assumed; it must be confirmed in the S-08 system specification. | H | H | G-4 discovery action must include: "Does the physician review system require individual authenticated login before recording a determination, and does it capture the logged-in physician's identity with the timestamp in an immutable record?" |
| S-09 HITL exception management | Data quality | Exception processor resolution decisions must be specific (approve, reject, or return-to-pipeline with specific instruction) — free-text resolutions create downstream state ambiguity | M | M | EscalationPacket.required_resolution field constrains resolutions to defined options; resolution_decision field accepts string but is validated against expected response types |
| S-09 | API availability | Assumed part of S-07 (claims management platform) — if so, availability is shared; if separate, independent availability assessment needed | M | M | Confirm in discovery whether S-09 is a module of S-07 or an independent system |
| S-09 | Legal / compliance | PHI in exception processor queue; access limited to assigned exception processors | M | M | Role-based access control; only exception processors assigned to this claim can read or resolve the escalation packet |
| S-09 | Audit trail | EscalationPacket resolution recorded in AuditLogEntry with action = HITL_RESOLVED | L | L | Standard audit logging covers this |
| S-09 | Sign-off integrity | Exception processor dispositions are procedure-dependent: the system records the resolution, but nothing prevents an exception processor from recording a resolution without actually reviewing the claim. This is acceptable for HITL exception queue (non-clinical path) but must be distinguished from the physician clinical review gate (S-07/S-08). | M | M | SLA monitoring (response_sla_hours) and operations audit review of resolution quality; not a URAC/NCQA compliance exposure for the non-clinical path |
| S-10 Audit log system | Data quality | Audit records must be complete (all required fields present) at write time — ET-07 is the guard for incomplete records; records with missing fields are not acceptable | M | H | T-11 validates all required fields before write; ET-07 triggers on any missing field; claim suspended until complete audit record is confirmed |
| S-10 | API availability | Audit log must be available whenever the agent processes a claim; unavailability blocks all processing (no claim can reach terminal state without an audit record) | M | H | Circuit breaker; claim-level queuing until audit log recovers; processing resumes from last committed state |
| S-10 | Legal / compliance | HIPAA-compliant PHI audit trail; minimum 7-year retention for clinical decision records (see §13 in per-agent specs); retention period must be confirmed with compliance team | M | H | Retention period confirmation is a pre-deployment checklist item |
| S-10 | Audit trail | The audit log is its own audit trail — append-only immutability is the primary requirement | L | H | Immutability must be technically enforced at the storage layer (not just at the application layer); confirmed in integration contract |
| S-10 | Sign-off integrity | Not applicable — S-10 is the audit evidence store, not an approval gate | — | — | N/A |
| S-11 Payment processing | Data quality | Payment instruction format must be precise (payment_amount, provider routing information, remittance advice codes); a malformed payment instruction creates a reconciliation problem | M | H | T-09 output validated against payment instruction schema before write; format confirmation in integration contract |
| S-11 | API availability | Payment processing systems have scheduled batch windows in many payer environments; real-time payment disbursement may not be available | M | M | Agent writes to a payment queue (not direct disbursement); queue pickup timing is the payment system's responsibility; agent's obligation is write confirmation only |
| S-11 | Legal / compliance | Payment data is financially sensitive; write access is high-risk; no read access to payment system required | M | H | Write-only scope; no read access granted; payment confirmation is a separate downstream process |
| S-11 | Audit trail | Payment instruction write recorded in AuditLogEntry with action = PAYMENT_APPROVED and output_summary including payment_amount | L | M | Standard audit logging covers this |
| S-11 | Sign-off integrity | The payment approval for standard administrative claims is AGENT ACTS, HUMAN NOTIFIED AFTER (D3 autonomy matrix): agent writes payment instruction directly without pre-approval. This is the highest-autonomy action in the WS1 pipeline — it is acceptable only when all upstream gates (eligibility, coding, prior auth, clinical routing) have passed. The sign-off integrity risk is that an upstream gate failure could produce a false ADMIN_CLEARED state and allow payment to proceed. Mitigation: all upstream gate results must be validated in T-09 pre-conditions before the payment write is executed; T-09 reads the full claim state at execution time, not just the state at the time of the ROUTING → ADMIN_CLEARED transition. | M | H | T-09 pre-condition check validates complete upstream pipeline state before writing payment instruction; AuditLogEntry captures all upstream gate results in input_summary |
| S-12 Provider portal / clearinghouse (outbound) | Data quality | Rejection notices must include machine-readable rejection_codes that providers can process for resubmission; free-text rejection reasons are insufficient | M | M | rejection_codes array validated against the rejection reason code reference set (S-14 analogue) before write |
| S-12 | API availability | Same availability profile as S-01 if using the same clearinghouse partner | L | M | Retry with backoff; queue rejected notices locally if clearinghouse is unavailable; deliver on reconnection |
| S-12 | Legal / compliance | Denial notices have regulatory format requirements (HIPAA EOB, state-specific timely notice requirements) | M | H | Rejection notice format must comply with applicable EOB and timely notice requirements; legal review of notice template before deployment |
| S-12 | Audit trail | Rejection notice delivery recorded in AuditLogEntry with action = CLAIM_REJECTED | L | L | Standard audit logging covers this |
| S-12 | Sign-off integrity | Not applicable — outbound rejection notices are a AGENT ACTS, HUMAN NOTIFIED AFTER action per D3 autonomy matrix for agent-initiated rejections; not an approval gate | — | — | N/A |
| S-13 Clinical notes source | Data quality | Clinical notes may be incomplete, illegible (if fax-to-PDF), or structured in inconsistent provider formats; completeness is the primary WS2 quality signal | H | H | WS2 JtD-2 completeness assessment surfaces missing fields to physician via completeness indicator; BP-WS2-2 escalation if documentation not retrievable |
| S-13 | API availability | Unknown — FHIR API, clearinghouse, fax, or EHR vendor API; availability unknown | H | H | G-5 mitigation; WS2 Wave 2 blocked until confirmed |
| S-13 | Legal / compliance | Clinical notes are highly sensitive PHI; HIPAA minimum necessary standard applies; HIPAA BAA between Greenfield and treating provider/EHR vendor required before programmatic access | H | H | BAA confirmation is a hard prerequisite for G-5 resolution; legal team must confirm before IT begins integration scoping |
| S-13 | Audit trail | Clinical notes retrieval recorded in AuditLogEntry for WS2 JtD-2; note provenance (source system, document ID, retrieval timestamp) captured in input_summary | M | M | Document provenance capture must be included in the WS2 integration contract when built |
| S-13 | Sign-off integrity | Not applicable — S-13 is a documentation retrieval source; physician review gate is at S-07/S-08 | — | — | N/A |
| S-14 Claims history database | Data quality | Historical claims data may have different schema versions for older records; lookback period and diagnosis code granularity must match WS2 packet requirements | M | M | Lookback period and query scope confirmed in discovery before WS2 spec is finalised |
| S-14 | API availability | Internal database — likely part of S-07 (claims management system); high availability | L | L | If separate from S-07, standard timeout/retry applies |
| S-14 | Legal / compliance | PHI historical claims data; read-only; minimum necessary access (member ID + relevant diagnosis range only) | M | M | Read-only scope; query scope limited to relevant diagnosis range and lookback period |
| S-14 | Audit trail | History retrieval recorded in AuditLogEntry for WS2 JtD-2 | L | L | Standard audit logging covers this |
| S-14 | Sign-off integrity | Not applicable — S-14 is a reference data source | — | — | N/A |
| S-15 Medical necessity criteria | Data quality | Criteria may be in PDF or scan format (not machine-readable), out of date, or inconsistently structured across procedure types — all three conditions degrade retrieval quality | H | H | G-6 mitigation; pre-deployment retrieval quality evaluation (precision@1 ≥ 85%, recall@3 ≥ 95%) before classifier deployment |
| S-15 | API availability | Unknown — vendor API vs. internal document store vs. flat files | H | M | G-6 mitigation; SCOPE-OUT until format confirmed |
| S-15 | Legal / compliance | Licensed vendor criteria (InterQual, MCG Health) have contractual restrictions on data access and distribution; using criteria outside the license scope is a contract violation | M | M | License scope confirmation before retrieval index is built; legal review of vendor agreement |
| S-15 | Audit trail | Criteria section retrieved for each classification recorded in AuditLogEntry.input_summary (section ID and version) | M | M | Criteria section provenance in audit record is required for post-determination defence |
| S-15 | Sign-off integrity | Not applicable — S-15 is a reference retrieval source | — | — | N/A |
| S-16 Configuration management | Data quality | Calibration artefact must contain exact fields: threshold value, recall achieved, holdout set size, labelling date, CMO reviewer name, sign-off timestamp — a partial record is not valid | M | H | ClinicalClassificationResult.calibration_record_id foreign key constraint; agent refuses to load a threshold without a complete, CMO-signed calibration artefact |
| S-16 | API availability | Internal configuration store — typically high availability; agent reads once at startup | L | L | Agent startup fails if calibration artefact cannot be loaded; this is the correct fail-fast behaviour |
| S-16 | Legal / compliance | Calibration artefact is a governance document with CMO signature; must be retained with the same compliance period as the audit records it validates | M | M | Retention policy aligned with audit log retention (7 years) |
| S-16 | Audit trail | Calibration artefact ID and version recorded in every ClinicalClassificationResult.calibration_record_id | L | L | Built into entity design |
| S-16 | Sign-off integrity | CMO sign-off on calibration artefacts is procedure-dependent as designed: the CMO records a signed artefact, but the mechanism for that signature capture (digital signature, approval workflow, manual record entry) is unconfirmed. If the signature is captured only as a text field, it is not technically verifiable. | M | H | Pre-deployment checklist item 6 (CMO sign-off mechanism confirmed); recommend a structured approval workflow that captures a non-repudiable signature (e.g., SSO-authenticated approval event with timestamp) rather than a manually entered name |

---

## Sign-off Integrity Summary for D4a §8 and D4b §8

**Required reading before finalising the autonomy matrix enforcement mechanism in both specs.**

| Gate | System | Classification | Evidence | Required action if procedure-dependent |
|------|--------|---------------|----------|----------------------------------------|
| Clinical routing gate (PENDING_PHYSICIAN_REVIEW → payment path blocked) | S-07 Claims management | **Procedure-dependent until confirmed** (G-3 discovery required) | D4 APD §5 states architectural block, but enforcement depends on claims management platform state machine guards at API layer | Classify as procedure-dependent in D4a §8; add to D4a §12 as governance risk (FM-A-5: governance hard stop bypass); implement middleware guard (G-3 mitigation 2) before go-live |
| Physician sign-off capture (identity + timestamp + decision) | S-08 Physician review queue | **Procedure-dependent** (system unknown) | No system confirmed; approval token design unconfirmed | Classify as procedure-dependent in D4a §8 and D4b §8; discovery action G-4 must be resolved before Wave 2 deployment; this gate is the URAC/NCQA compliance evidence |
| CMO threshold calibration sign-off | S-16 Configuration management | **Procedure-dependent** (signature mechanism unconfirmed) | Calibration artefact design requires CMO name field but signature mechanism is not technically verified | Recommend SSO-authenticated approval workflow; classify as procedure-dependent until confirmed; note in D4a §12 |

---

*Pass 2 complete. Pass 3 (Spec A §0–§8) reads this document — specifically §3 sign-off integrity summary — before finalising the WS1 autonomy matrix §8 enforcement mechanism statement.*
