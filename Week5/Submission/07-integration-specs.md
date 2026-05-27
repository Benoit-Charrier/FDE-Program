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


---

# D4 — Integration Specifications
## Greenfield Health Systems: Medical Claims Adjudication Transformation

> **Reading order:** Read alongside `D4_integration_preamble.md` (system inventory, gap analysis,
> risk register) and `D4_preamble_capability_spec.md` (shared entity definitions). All system
> names, base URLs, and API field names are DISCOVERY_REQUIRED unless confirmed in the scenario.
> No system is named in `Scenario/scenario_context.md` — every system name below is an
> assumption until confirmed in discovery.

**Systems covered:** 12 full contracts + 4 SCOPE-OUT entries (S-01 through S-16).
**Pass sequence:** 7a (scaffold + SCOPE-OUT + IC-S-10 + IC-S-16) → 7b → 7c → 7d → 7e → 7f.
**Scenario:** Option A — Healthcare Claims Processing Transformation
**Client:** Greenfield Health Systems
**Agents in scope:** WS1 (Administrative Adjudication Agent), WS2 (Clinical Review Support Agent)

---

## Table of Contents

| Contract ID | System | Type | Pass |
|-------------|--------|------|------|
| IC-S-06 | Contract Document Store | SCOPE-OUT | 7a |
| IC-S-08 | Physician Review Queue Interface | SCOPE-OUT (BLOCKING) | 7a |
| IC-S-10 | Audit Log System | Full contract | 7a |
| IC-S-13 | Clinical Notes Source System | SCOPE-OUT (Wave 2) | 7a |
| IC-S-15 | Medical Necessity Criteria System | SCOPE-OUT (degrading) | 7a |
| IC-S-16 | Configuration Management System | Full contract | 7a |
| IC-S-01 | Clearinghouse / Provider Portal (inbound) | Full contract | 7b |
| IC-S-12 | Provider Portal / Clearinghouse (outbound) | Full contract | 7b |
| IC-S-02 | Member Eligibility System | Full contract | 7c |
| IC-S-03 | Code Validation Reference | Full contract | 7c |
| IC-S-05 | Fee Schedule System | Full contract | 7c |
| IC-S-04 | Prior Authorisation System | Full contract | 7d |
| IC-S-14 | Claims History Database | Full contract | 7d |
| IC-S-09 | HITL Exception Management System | Full contract | 7e |
| IC-S-11 | Payment Processing System | Full contract | 7e |
| IC-S-07 | Claims Management System | Full contract | 7f |

---

## SCOPE-OUT Entries

Four systems are SCOPE-OUT per `D4_integration_preamble.md` §1 Pass 7 decision column. Full contracts are deferred pending gap resolution.

---

## IC-S-06 — Contract Document Store — SCOPE-OUT

**Gap reference:** G-2
**Why out of scope:** API availability unknown. Contract exception rules may exist only as unstructured documents (Word, PDF, email threads) with no machine-readable structure. WS1 T-10 (contract exception handling) cannot be automated until this gap is resolved. Per ADR-1, WS1 launches in degraded mode: standard-path payment proceeds; claims with contract exception flags route to HITL exception processor (ET-06) indefinitely until gap is resolved. WS1-JtD-3 is held at Agent-led + Human Oversight until full contract is written.

**What is needed before build can start:**
1. VP Operations confirms whether contract exception rules are stored in a structured, queryable system — system name and API documentation required.
2. If rules are unstructured documents: estimate of active exception agreements in scope for Wave 1 and owner for the data encoding project.
3. Once system is confirmed: full integration contract (10 sections) written before WS1-JtD-3 is promoted to Fully Agentic.

**Owner:** VP Operations (James Liu) to confirm storage mechanism; IT team to confirm API availability once system is identified.

**Stub behaviour during development:** WS1 T-10 unconditionally routes to ET-06 (HITL exception escalation) when a contract exception flag is present. No contract lookup attempted. `EscalationPacket.escalation_reason = CONTRACT_EXCEPTION_LOOKUP_UNAVAILABLE`. All contract exception claims processed manually in Wave 1.

**Wave:** Wave 1.5 — WS1 launches in degraded mode at Wave 1; WS1-JtD-3 promoted to Fully Agentic in Wave 1.5 after contract rules are encoded and full integration contract is written.

---

## IC-S-08 — Physician Review Queue Interface — SCOPE-OUT (BLOCKING)

**Gap reference:** G-4
**Why out of scope:** System identity unknown. No physician review system is named or implied in the scenario. This is the primary URAC/NCQA compliance evidence point — the approval token satisfying individual physician sign-off. Without this system, the entire clinical path (35% of ~2,000 claims/day) cannot be processed. WS2 cannot go live until G-4 is resolved.

**What is needed before build can start:**
1. System identity: what tool (or tools) physicians currently use to receive and review clinical claims. If none exists, a Wave 1 build scope item (minimal HITL queue UI) must be added.
2. Authentication model: does the system require individual authenticated physician login before a determination can be recorded? Shared-account login is not acceptable under URAC/NCQA.
3. Approval token schema: minimum required fields for URAC/NCQA compliance — `physician_id` (non-null, individually attributable), `determination_type` (enum), `claim_id`, `timestamp` (immutable).
4. API documentation for write (EscalationPacket and PhysicianReviewPacket delivery) and read (determination token retrieval).

**Owner:** Dr. Marcus Webb (CMO) to identify existing physician review workflow; IT team to assess API readiness; Legal/Compliance to confirm URAC/NCQA token requirements.

**Stub behaviour during development:** WS2 T-B-07 (packet delivery) writes to S-09 HITL exception queue as fallback. Physician determination simulated via manual test fixture injected into ClaimRecord. FM-B-5 governance hard stop (physician determination without `human_id`) remains active in test harness.

**Wave:** Wave 1 (BLOCKING) — WS2 cannot go live until resolved. Email + web form bridge acceptable as degraded Wave 1 interim per G-4 mitigation option 3 (individual login + immutable timestamp required even in bridge mode), but not steady-state.

---

## IC-S-13 — Clinical Notes Source System — SCOPE-OUT (Wave 2 blocker)

**Gap reference:** G-5
**Why out of scope:** System identity and access mechanism unknown. May be a FHIR-compliant provider API, EDI 275 attachment, portal upload, fax-to-PDF, or direct EHR vendor API. HIPAA BAA between Greenfield and treating provider / EHR vendor is a hard prerequisite before any programmatic access can be scoped. Without clinical notes, WS2 packet assembly (JtD-2) cannot include treating provider documentation; the 30–45 min physician document-hunting time (Dr. Webb's Exchange 3 estimate) is not reduced.

**What is needed before build can start:**
1. Access mechanism: how do treating providers currently submit clinical documentation (EDI 275, portal upload, fax, EHR API)?
2. Storage: is documentation stored in S-07 (claims management system) or a separate document management system?
3. HIPAA BAA: confirmed between Greenfield and any EHR vendor or clearinghouse clinical document exchange partner before IT begins integration scoping.
4. If FHIR API: base URL, supported FHIR resources (DocumentReference, DiagnosticReport, etc.), and authentication method.

**Owner:** IT team (integration assessment); Legal/Compliance (BAA confirmation); Clinical Operations (document submission workflow confirmation).

**Stub behaviour during development:** WS2 T-B-05 (clinical notes retrieval) returns empty list. `PhysicianReviewPacket.completeness_indicator` marks `clinical_notes` section as SCOPE-OUT (excluded from numerator and denominator of completeness calculation). Physician receives packet with note: "Clinical notes: pending Wave 2 integration — retrieve manually."

**Wave:** Wave 2 — WS2 launches without clinical notes in Wave 1 per D3 §5 fallback path; promoted to Wave 2 after G-5 resolution and HIPAA BAA confirmation.

---

## IC-S-15 — Medical Necessity Criteria System — SCOPE-OUT (degrading)

**Gap reference:** G-6
**Why out of scope:** Format and hosting unconfirmed. Criteria may be licensed from a vendor (InterQual, MCG Health, Milliman) or maintained in-house by the CMO team in PDF, Word, or scan format. If not machine-readable, a pre-deployment OCR and chunking exercise is required before a retrieval index can be built. Without criteria augmentation: WS1 T-08 classifier accuracy degrades on borderline cases; WS2 physician packets exclude applicable criteria section. Both are Degrading — agents launch, quality suffers.

**What is needed before build can start:**
1. Criteria source: licensed vendor (which vendor? API or structured export available?) or CMO-maintained documents (format, version control mechanism)?
2. If vendor: license scope confirmation (does license permit agent-mediated retrieval?) and API documentation.
3. If documents: OCR quality assessment; pre-deployment chunking project scoping; minimum viable coverage for Wave 1 (top 10–15 procedure types by WS1 volume).
4. Retrieval quality evaluation: precision@1 ≥ 85%, recall@3 ≥ 95% required before classifier deployment with criteria augmentation.

**Owner:** CMO team (criteria source identification); Legal/Compliance (vendor license review); IT (retrieval index build).

**Stub behaviour during development:** WS1 T-08 runs without criteria augmentation (classifier receives structured claim signals only). WS2 T-B-06 (criteria section retrieval) returns empty. `PhysicianReviewPacket.completeness_indicator` marks `criteria_section` as SCOPE-OUT. CalibrationRecord used for go-live must document that holdout set labelling was performed without criteria augmentation; `recall_achieved ≥ 0.995` must be satisfied on this basis before Wave 1 go-live.

**Wave:** Post-MVP — WS1 and WS2 launch without criteria augmentation; integrated in Wave 2 after G-6 resolution and retrieval index validation.

---

## IC-S-10 — Audit Log System

**Used by:** Both WS1 (24-value action enum) and WS2 (26-value action enum)
**Access type:** Write only (append-only); no read access granted to either agent

### §1. Integration Purpose

WS1 and WS2 write one `AuditLogEntry` record to this system for every action that transitions ClaimRecord state, produces a ClinicalClassificationResult, triggers an escalation, issues a payment instruction, or records a governance hard stop. The audit log is the primary HIPAA compliance artefact and the evidence base for URAC/NCQA certification.

**Not in scope for this contract:** ClaimRecord state storage (S-07), CalibrationRecord storage (S-16), payment execution (S-11). Agents write only — no read-back from this system.

### §2. System Description

- **Assumed system name:** Greenfield Audit Log Service (DISCOVERY_REQUIRED — may be a module of the claims management platform, a dedicated compliance service, or an immutable object store)
- **Base URL:** DISCOVERY_REQUIRED (`https://audit.greenfield-internal.example/v1` as placeholder)
- **Operations:** POST (append new entry); no GET, PUT, PATCH, or DELETE in scope for agent credentials
- **Immutability requirement:** No UPDATE or DELETE permitted at any layer (API, application, storage). Must be technically enforced at the storage layer — not a procedural control. Acceptable implementations: write-once object store with object lock enabled, append-only Kafka topic with consumer-group-only read access, or compliance-grade WORM storage.
- **Retention:** 7 years minimum for all entries where the associated ClaimRecord involves clinical routing, physician determination, or payment approval (HIPAA clinical record retention). 3 years minimum for all other entries.

### §3. Authentication and Authorisation

- **Method:** DISCOVERY_REQUIRED. Recommended: per-agent-instance service-account API key; mTLS acceptable if internal PKI is available.
- **Credential storage:** Agent secrets manager (not hardcoded); key name `AUDIT_LOG_API_KEY`
- **Scope:** Write-only. No read endpoint accessible with agent credential. Confirm with a 405 test on DELETE before go-live.
- **Token rotation:** DISCOVERY_REQUIRED. Recommended: rotate every 90 days. Agent must handle 401 gracefully — suspend all processing and alert ops.
- **Fallback if credential unavailable at startup:** Agent refuses to start. Log locally to `AUDIT_QUEUED_LOCAL` with ops alert. Do not process claims without an active, write-capable audit log credential.

### §4. Endpoint Contracts

**Operation: Append audit entry**

```
POST /audit-entries
Content-Type: application/json
Authorization: Bearer {AUDIT_LOG_API_KEY}
```

Required request fields:

| Field | Type | Constraint |
|-------|------|-----------|
| `id` | UUID | Generated by agent before call; used for idempotency |
| `timestamp` | ISO 8601 UTC | Millisecond precision; set at moment of action |
| `agent_id` | string ≤ 64 chars | Format: `{agent_name}:{version}:{instance_id}` |
| `action` | enum | Agent-specific exhaustive enum (see below) |
| `entity_type` | string ≤ 64 chars | e.g. `"ClaimRecord"`, `"ClinicalClassificationResult"` |
| `entity_id` | UUID | Foreign key to entity |
| `input_summary` | JSON object | Min fields: `entity_id`, `state_before`, `trigger_condition` |
| `output_summary` | JSON object | Min fields: `state_after`, `primary_output_value` |
| `delegation_tier` | enum | `AGENT_ALONE` \| `AGENT_LOGS` \| `AGENT_PROPOSES` \| `HUMAN_DECIDES` |
| `escalation_triggered` | boolean | |
| `compliance_flags` | array of strings | Default `[]` |

Optional fields (conditionally required):

| Field | Type | Required when |
|-------|------|---------------|
| `human_id` | UUID | `delegation_tier ∈ {HUMAN_DECIDES, AGENT_PROPOSES}` — null when `AGENT_ALONE` |
| `confidence_score` | float 0.000–1.000 | `action = CLINICAL_CLASSIFICATION_COMPLETED` |
| `escalation_trigger_id` | string ≤ 16 chars | `escalation_triggered = true`; must match a defined ET-ID |

**Action enum — WS1 (24 values, exhaustive):**
`CLAIM_INTAKE_VALIDATED`, `CLAIM_STATE_TRANSITION`, `ELIGIBILITY_CONFIRMED`, `ELIGIBILITY_CORRECTED`, `ELIGIBILITY_ESCALATED`, `CODE_VALIDITY_CHECKED`, `CODE_PLAUSIBILITY_ASSESSED`, `PRIOR_AUTH_CONFIRMED`, `PRIOR_AUTH_TOLERANCE_APPLIED`, `PRIOR_AUTH_ESCALATED`, `CLINICAL_CLASSIFICATION_COMPLETED`, `CLINICAL_ESCALATED_ET01`, `CLINICAL_ESCALATED_ET02`, `PAYMENT_APPROVED`, `CLAIM_REJECTED`, `ESCALATION_TRIGGERED`, `ESCALATION_DELIVERED`, `ESCALATION_DELIVERY_FAILED`, `SCHEMA_VALIDATION_FAILED`, `GOVERNANCE_HARD_STOP_TRIGGERED`, `AUDIT_LOG_QUEUED_LOCAL`, `REFERENCE_DATA_EXPIRED`, `STARTUP_CALIBRATION_CHECK_PASSED`, `STARTUP_CALIBRATION_CHECK_FAILED`

**Action enum — WS2 (26 values, exhaustive):**
`CLAIM_RECEIVED_BY_WS2`, `ROUTING_VERIFICATION_CONFIRMED`, `ROUTING_VERIFICATION_ESCALATED`, `PRIOR_AUTH_HISTORY_RETRIEVED`, `CLAIMS_HISTORY_RETRIEVED`, `CLINICAL_NOTES_RETRIEVED`, `CRITERIA_SECTION_RETRIEVED`, `INTEGRATION_DEGRADED`, `PACKET_COMPLETENESS_ASSESSED`, `PACKET_ASSEMBLED`, `PACKET_DELIVERED`, `PACKET_DELIVERY_FAILED`, `PHYSICIAN_DETERMINATION_RECEIVED`, `ADDITIONAL_INFO_REQUEST_DRAFTED`, `ADDITIONAL_INFO_REQUEST_DISPATCHED`, `ADDITIONAL_INFO_RECEIVED`, `NEW_PACKET_ASSEMBLED_FOR_REVIEW`, `CLAIM_STATE_TRANSITION`, `ESCALATION_TRIGGERED`, `ESCALATION_DELIVERED`, `ESCALATION_DELIVERY_FAILED`, `SCHEMA_VALIDATION_FAILED`, `GOVERNANCE_HARD_STOP_TRIGGERED`, `AUDIT_LOG_QUEUED_LOCAL`, `STARTUP_CALIBRATION_CHECK_PASSED`, `STARTUP_CALIBRATION_CHECK_FAILED`

**Status code → agent action:**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 202 | Committed | Continue to next operation |
| 400 | Missing required field or invalid enum value | Do NOT retry — ET-07: suspend claim with `incomplete_audit = true` flag; alert ops |
| 401 | Credential expired or invalid | Attempt token refresh once; if still 401 → suspend all claim processing; ops alert |
| 409 | Duplicate `entry_id` | Treat as COMMITTED (idempotent); log warning; continue |
| 429 | Rate limit exceeded | Queue locally; retry with exponential backoff (§5); do not suspend claim |
| 503 | System unavailable | Queue entry to `AUDIT_QUEUED_LOCAL`; suspend claim from terminal-state transitions; retry every 30s; ops alert after 5 min sustained unavailability |

**Worked example — WS1 administrative claim payment approval:**

Request:
```json
POST /audit-entries
{
  "id": "a3f7c2d1-8b4e-4f9a-bc12-5e6d7f8a9b0c",
  "timestamp": "2025-03-15T14:23:07.412Z",
  "agent_id": "ws1-admin-adjudicator:v1.0.0:instance-003",
  "action": "PAYMENT_APPROVED",
  "entity_type": "ClaimRecord",
  "entity_id": "b9e2a1f4-3c7d-4e8b-a021-6f5c4d3e2f1a",
  "input_summary": {
    "entity_id": "b9e2a1f4-3c7d-4e8b-a021-6f5c4d3e2f1a",
    "state_before": "PAYMENT_CALCULATING",
    "trigger_condition": "T-09_FEE_SCHEDULE_LOOKUP_COMPLETE",
    "upstream_gates_passed": [
      "ELIGIBILITY_CONFIRMED", "CPT_99213_VALID", "ICD10_M17_11_VALID",
      "PRIOR_AUTH_CONFIRMED", "ADMIN_ROUTING_CONFIRMED"
    ],
    "fee_schedule_version": "GHS-FS-2025-01",
    "procedure_code": "99213",
    "diagnosis_code": "M17.11"
  },
  "output_summary": {
    "state_after": "APPROVED",
    "primary_output_value": "185.00",
    "currency": "USD",
    "payment_instruction_id": "pi-c3d4e5f6-7a8b-9c0d"
  },
  "delegation_tier": "AGENT_ALONE",
  "escalation_triggered": false,
  "compliance_flags": ["ADMIN_PATH_COMPLETE", "AUDIT_TRAIL_COMPLETE"]
}
```

Response:
```json
HTTP 202
{
  "entry_id": "a3f7c2d1-8b4e-4f9a-bc12-5e6d7f8a9b0c",
  "state": "COMMITTED",
  "timestamp_received": "2025-03-15T14:23:07.489Z"
}
```

**Worked example — WS2 physician determination received:**

Request:
```json
POST /audit-entries
{
  "id": "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a",
  "timestamp": "2025-03-15T16:45:22.103Z",
  "agent_id": "ws2-clinical-review:v1.0.0:instance-001",
  "action": "PHYSICIAN_DETERMINATION_RECEIVED",
  "entity_type": "ClaimRecord",
  "entity_id": "e7f8a9b0-c1d2-3e4f-5a6b-7c8d9e0f1a2b",
  "input_summary": {
    "entity_id": "e7f8a9b0-c1d2-3e4f-5a6b-7c8d9e0f1a2b",
    "state_before": "PHYSICIAN_REVIEWING",
    "trigger_condition": "DETERMINATION_TOKEN_RECEIVED_FROM_S08",
    "physician_id": "dr-webb-id-001",
    "packet_id": "pkt-3c4d5e6f-7a8b",
    "packet_delivered_at": "2025-03-15T12:44:00.000Z"
  },
  "output_summary": {
    "state_after": "APPROVED",
    "primary_output_value": "APPROVED",
    "determination_type": "CLINICAL_APPROVED"
  },
  "delegation_tier": "HUMAN_DECIDES",
  "human_id": "dr-webb-id-001",
  "escalation_triggered": false,
  "compliance_flags": ["URAC_NCQA_CLINICAL_GATE", "PHYSICIAN_ATTRIBUTION_CONFIRMED", "AUDIT_TRAIL_COMPLETE"]
}
```

Response:
```json
HTTP 202
{
  "entry_id": "d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a",
  "state": "COMMITTED",
  "timestamp_received": "2025-03-15T16:45:22.189Z"
}
```

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 429 Rate limit | Yes | 3 | Exponential: 2s, 4s, 8s | Queue locally; alert ops if local queue > 50 entries |
| 503 Unavailable | Yes (with local queue) | Indefinite | Fixed 30s | Alert ops after 5 min; suspend claim from terminal-state writes |
| Timeout > 5s | Yes | 2 | Linear 5s | Treat as 503 |
| 401 Credential invalid | Yes | 1 (after token refresh) | None | Suspend all claim processing; ops alert immediately |
| 400 Validation failure | No | 0 | N/A | ET-07: `incomplete_audit = true` on ClaimRecord; suspend claim progression |

**ET-07 hard stop:** When an audit entry cannot be committed due to a 400 validation error, the claim is suspended with `incomplete_audit = true`. No further state transitions are permitted for that claim until the audit entry is confirmed committed (requires a code fix, not a retry). Claim is not lost — it remains in its current state awaiting resolution.

### §6. Rate Limits and Throttling

All values DISCOVERY_REQUIRED. Expected profile for capacity planning:

- **Peak write rate:** ~40 entries/min per agent instance (2,000 claims/day × ~10 entries/claim ÷ 8 hours ÷ 60 min; peak burst ~400 entries/min across all instances)
- **Minimum required capacity:** 200 writes/min per agent instance to handle burst safely
- **Daily volume:** ~20,000 entries/day combined (WS1 + WS2)
- **Local queue buffer:** Up to 50 entries held locally before ops alert; queue drained on reconnection

### §7. Data Mapping

| Internal field (AuditLogEntry entity) | External API field | Direction |
|---------------------------------------|-------------------|-----------|
| `id` | `id` | Agent → System |
| `timestamp` | `timestamp` | Agent → System |
| `agent_id` | `agent_id` | Agent → System |
| `action` | `action` | Agent → System |
| `entity_type` | `entity_type` | Agent → System |
| `entity_id` | `entity_id` | Agent → System |
| `input_summary` | `input_summary` | Agent → System |
| `output_summary` | `output_summary` | Agent → System |
| `delegation_tier` | `delegation_tier` | Agent → System |
| `human_id` | `human_id` | Agent → System |
| `confidence_score` | `confidence_score` | Agent → System |
| `escalation_triggered` | `escalation_triggered` | Agent → System |
| `escalation_trigger_id` | `escalation_trigger_id` | Agent → System |
| `compliance_flags` | `compliance_flags` | Agent → System |
| *(response)* | `entry_id` | System → Agent | Confirmation; equals `id` sent |
| *(response)* | `state` | System → Agent | Must equal `COMMITTED`; any other value treated as failure |

No inbound data mapping — agents do not read from S-10.

### §8. State Synchronisation

- **Pattern:** Write-only on event; no polling, no caching
- **Ordering guarantee required:** S-10 write must complete with `state = COMMITTED` BEFORE the corresponding S-07 ClaimRecord state transition PATCH is issued. If S-10 write fails, the S-07 write must not proceed (ET-07 applies). This sequencing is architecturally enforced in agent task execution order.
- **No read-back:** Compliance team queries S-10 via a separate read interface not in scope for this contract.

### §9. Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| S-10 system down (503) | Queue audit entry locally in `AUDIT_QUEUED_LOCAL`; suspend the affected claim from terminal-state transitions; retry every 30s; ops alert after 5 min |
| Unexpected response schema | Log entry locally as unconfirmed; apply ET-07 to affected claim |
| Rate limit exceeded (429) | Queue locally; retry with exponential backoff; do not suspend claim until local queue > 50 |
| Credential invalid (401) | Suspend all claim processing after one failed refresh attempt; ops alert |

No claim may reach APPROVED, REJECTED, or CLOSED state without a confirmed committed audit trail entry for that transition. This is an architectural hard stop, not a configurable option.

### §10. Pre-deployment Checklist

- [ ] System name and base URL confirmed; all DISCOVERY_REQUIRED values replaced
- [ ] Write-only API credential provisioned in secrets manager as `AUDIT_LOG_API_KEY`
- [ ] Immutability confirmed at storage layer (not just API layer) — IT documentation required; test: attempt DELETE on a committed entry → confirm 405 or 403
- [ ] No DELETE or UPDATE accessible with agent credential — confirm via integration test
- [ ] 7-year retention policy confirmed for clinical entries; compliance team sign-off required
- [ ] Rate limit confirmed ≥ 200 writes/min per agent instance; load test at 400 entries/min before go-live
- [ ] ET-07 end-to-end test: simulate S-10 503 → confirm claim enters `incomplete_audit` state → confirm claim does not advance to APPROVED → confirm local queue drains on S-10 recovery
- [ ] Duplicate `entry_id` test: confirm 409 response and agent treats as COMMITTED (idempotency check)
- [ ] Ordering test: confirm S-10 write completes before S-07 PATCH in integration test harness (log timestamps)
- [ ] WS1 and WS2 action enums validated: confirm system accepts all 24 WS1 values and all 26 WS2 values; reject an unlisted value with 400

---

## IC-S-16 — Configuration Management System

**Used by:** Both WS1 (reads `call_site = ROUTING` CalibrationRecord) and WS2 (reads `call_site = VERIFICATION` CalibrationRecord)
**Access type:** Read only (agent startup only; no writes by either agent)

### §1. Integration Purpose

WS1 and WS2 each read one `CalibrationRecord` from this system at agent startup. The CalibrationRecord contains the CMO-signed clinical content confidence threshold and calibration metadata. Agents fail fast and refuse to start if a valid, CMO-signed record cannot be retrieved and validated.

**Not in scope for this contract:** Writing or updating CalibrationRecords (done by the CMO calibration team through a separate governance workflow); claim processing; audit logging (S-10); any runtime configuration outside the CalibrationRecord.

### §2. System Description

- **Assumed system name:** Greenfield Configuration Service (DISCOVERY_REQUIRED — may be a secrets manager such as AWS Secrets Manager or HashiCorp Vault, a configuration database, or a purpose-built artefact store)
- **Base URL:** DISCOVERY_REQUIRED (`https://config.greenfield-internal.example/v1` as placeholder)
- **Operations:** GET (read CalibrationRecord by `call_site`); no write access granted to agents
- **Two separate records required:** one for `call_site = ROUTING` (WS1 threshold, default 0.700), one for `call_site = VERIFICATION` (WS2 threshold, default 0.850). Agents must read only the record matching their call_site. Cross-contamination (WS1 loading the VERIFICATION record or vice versa) is a startup validation hard stop.

### §3. Authentication and Authorisation

- **Method:** DISCOVERY_REQUIRED. Recommended: per-agent service-account API key with read-only scope.
- **Credential storage:** Agent secrets manager; key name `CONFIG_API_KEY`
- **Scope:** Read-only; CalibrationRecord for the agent's own `call_site` only. WS1 credential must not return the VERIFICATION record; WS2 credential must not return the ROUTING record — confirm via cross-contamination test in §10.
- **Token rotation:** DISCOVERY_REQUIRED. Recommended: rotate every 90 days.
- **Fallback if credential unavailable at startup:** Fail fast. Do not process claims. Ops alert. Do not use a cached record from a prior session.

### §4. Endpoint Contracts

**Operation: Read CalibrationRecord**

```
GET /calibration-records?call_site={ROUTING|VERIFICATION}&state=SIGNED
Authorization: Bearer {CONFIG_API_KEY}
```

Query parameters:

| Parameter | Required | Value |
|-----------|----------|-------|
| `call_site` | Yes | `ROUTING` (WS1) or `VERIFICATION` (WS2) |
| `state` | Yes | Must be `SIGNED`; agent must reject DRAFT or SUPERSEDED records |
| `classifier_version` | Optional | If provided, system returns record matching this version; 404 if no match |

**Status code → agent action:**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 200 | Valid record returned | Proceed to 6-field startup validation |
| 404 | No SIGNED record for this `call_site` | Fail fast — ops and CMO team alert immediately |
| 401 | Credential invalid | Fail fast — ops alert |
| 503 | System unavailable | Retry once after 10s; if still unavailable, fail fast; do not use cached value |

**6-field startup validation — all six must pass before agent starts processing claims:**

| # | Field | Rule | Failure action |
|---|-------|------|----------------|
| 1 | `state` | Must equal `SIGNED` | Fail fast — DRAFT and SUPERSEDED records are rejected |
| 2 | `cmo_signoff_date` | Must be non-null | Fail fast |
| 3 | `recall_achieved` | Must be ≥ 0.995 | Fail fast |
| 4 | `holdout_set_size` | Must be ≥ 500 | Fail fast |
| 5 | `call_site` | Must match calling agent: `ROUTING` for WS1, `VERIFICATION` for WS2 | Fail fast — wrong call_site is a configuration defect, not a data issue |
| 6 | `classifier_version` | Must match the `classifier_version` of the deployed classifier binary | Fail fast — version mismatch means calibration was performed on a different model |

Any validation failure → agent does not start; `STARTUP_CALIBRATION_CHECK_FAILED` written to local log and to S-10 (if S-10 is reachable); ops and CMO team alerted with which field failed.

**Worked example — WS1 startup (ROUTING record):**

Request:
```
GET /calibration-records?call_site=ROUTING&state=SIGNED
Authorization: Bearer {CONFIG_API_KEY}
```

Response:
```json
HTTP 200
{
  "id": "cr-7d8e9f0a-1b2c-3d4e-5f6a-7b8c9d0e1f2a",
  "call_site": "ROUTING",
  "threshold_value": 0.700,
  "recall_achieved": 0.997,
  "precision_achieved": 0.812,
  "holdout_set_size": 620,
  "holdout_set_labelling_date": "2025-02-10",
  "threshold_sweep_range_low": 0.40,
  "threshold_sweep_range_high": 0.95,
  "threshold_sweep_step": 0.05,
  "classifier_version": "clinical-classifier:v2.1.0",
  "cmo_reviewer_name": "Dr. Marcus Webb",
  "cmo_reviewer_id": "usr-cmo-webb-001",
  "cmo_signoff_date": "2025-02-14",
  "state": "SIGNED",
  "created_at": "2025-02-14T16:00:00.000Z",
  "updated_at": "2025-02-14T16:00:00.000Z"
}
```

Startup validation result: all 6 fields pass. `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` set to `0.700` for this session. `STARTUP_CALIBRATION_CHECK_PASSED` written to S-10 with `calibration_record_id = "cr-7d8e9f0a-..."`.

**Worked example — WS2 startup (VERIFICATION record):**

Request:
```
GET /calibration-records?call_site=VERIFICATION&state=SIGNED
Authorization: Bearer {CONFIG_API_KEY}
```

Response:
```json
HTTP 200
{
  "id": "cr-2n3o4p5q-6r7s-8t9u-0v1w-2x3y4z5a6b7c",
  "call_site": "VERIFICATION",
  "threshold_value": 0.850,
  "recall_achieved": 0.996,
  "precision_achieved": 0.789,
  "holdout_set_size": 580,
  "holdout_set_labelling_date": "2025-02-10",
  "threshold_sweep_range_low": 0.40,
  "threshold_sweep_range_high": 0.95,
  "threshold_sweep_step": 0.05,
  "classifier_version": "clinical-classifier:v2.1.0",
  "cmo_reviewer_name": "Dr. Marcus Webb",
  "cmo_reviewer_id": "usr-cmo-webb-001",
  "cmo_signoff_date": "2025-02-14",
  "state": "SIGNED",
  "created_at": "2025-02-14T16:05:00.000Z",
  "updated_at": "2025-02-14T16:05:00.000Z"
}
```

Note: VERIFICATION threshold (0.850) is intentionally higher than ROUTING threshold (0.700). The two thresholds are separately configurable and separately calibrated per D3 ADR-2. The difference is a design decision, not an error.

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 503 Unavailable | Yes | 1 | 10s fixed | Fail fast; do not start; ops alert |
| 401 Credential invalid | No | 0 | N/A | Fail fast; ops alert |
| 404 Record not found | No | 0 | N/A | Fail fast; CMO calibration workflow is blocked; ops and CMO alert |
| Validation failure (§4 6-field) | No | 0 | N/A | Fail fast; log which field failed; ops and CMO alert |

No retry loop on validation failure — a misconfigured or unsigned record is a governance defect, not a transient error. Retrying would not change the result and could mask a real configuration problem.

### §6. Rate Limits and Throttling

- **Call frequency:** Once at agent startup; once per recovery after `STARTUP_CALIBRATION_CHECK_FAILED`
- **Requests/day:** ≤ 10 per agent instance under normal operations (covers restarts and deployments)
- **Rate limit:** DISCOVERY_REQUIRED. Any reasonable limit is sufficient given the extremely low call frequency.

### §7. Data Mapping

| External API field | Internal usage | Direction |
|--------------------|----------------|-----------|
| `id` | `CalibrationRecord.id` → stored as `ClinicalClassificationResult.calibration_record_id` on every classifier call | System → Agent |
| `threshold_value` | `CLINICAL_CONTENT_CONFIDENCE_THRESHOLD` runtime parameter; set at startup; immutable during session | System → Agent |
| `recall_achieved` | Startup validation field 3 | System → Agent |
| `holdout_set_size` | Startup validation field 4 | System → Agent |
| `cmo_signoff_date` | Startup validation field 2 | System → Agent |
| `call_site` | Startup validation field 5 | System → Agent |
| `classifier_version` | Startup validation field 6 | System → Agent |
| `state` | Startup validation field 1 | System → Agent |
| `cmo_reviewer_name` | Logged in `STARTUP_CALIBRATION_CHECK_PASSED` audit entry (informational) | System → Agent |
| All remaining fields | Logged in startup audit entry (informational) | System → Agent |

No writes from agent to this system.

### §8. State Synchronisation

- **Pattern:** Read once at startup; no caching with TTL; no polling during session
- **Rationale:** CalibrationRecord is immutable once SIGNED. A threshold change during a live session is not supported — it requires a controlled agent restart. This is a governance requirement: every threshold change must be accompanied by a logged `STARTUP_CALIBRATION_CHECK_PASSED` event, creating an auditable record of when the new threshold took effect.
- **Hot reload not supported:** Deliberate. An in-session threshold update would not produce an audit event and would bypass the 6-field startup validation. Restarts are the enforcement mechanism.

### §9. Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| System unavailable at startup | Fail fast — do not start; do not use a cached value from a prior session |
| Record not found (404) | Fail fast — CMO calibration workflow is blocked; alert ops and CMO team |
| Validation failure | Fail fast — log which field failed; do not start with an invalid record |
| System unavailable mid-session | No action needed — record is already loaded in memory; S-16 is not called during claims processing |

Graceful degrade is not acceptable at startup. Operating without a valid, CMO-signed calibration record is a governance defect regardless of operational urgency.

### §10. Pre-deployment Checklist

- [ ] System name and base URL confirmed; all DISCOVERY_REQUIRED values replaced
- [ ] Read-only API credential provisioned in secrets manager as `CONFIG_API_KEY`
- [ ] Two CalibrationRecords created and in SIGNED state: one `call_site = ROUTING`, one `call_site = VERIFICATION`
- [ ] Both records: `recall_achieved ≥ 0.995`, `holdout_set_size ≥ 500`, `cmo_signoff_date` non-null
- [ ] `classifier_version` in both records matches deployed classifier binary — confirmed by IT
- [ ] CMO sign-off mechanism confirmed: SSO-authenticated approval workflow (not manual name-field entry) strongly recommended; current mechanism documented in governance record
- [ ] Startup validation test WS1: load ROUTING record → all 6 fields pass → `STARTUP_CALIBRATION_CHECK_PASSED` written to S-10 with correct `calibration_record_id`
- [ ] Startup validation test WS2: load VERIFICATION record → all 6 fields pass → `STARTUP_CALIBRATION_CHECK_PASSED` written to S-10
- [ ] Fail-fast test: provide DRAFT record → confirm agent refuses to start → `STARTUP_CALIBRATION_CHECK_FAILED` written to local log with field name `state`
- [ ] Cross-contamination test: WS1 credential cannot retrieve `call_site = VERIFICATION` record (expect 403 or 404); WS2 credential cannot retrieve `call_site = ROUTING` record

---

*Pass 7a complete. Pass 7b appends IC-S-01 and IC-S-12.*

---

## IC-S-01 — Clearinghouse / Provider Portal (Inbound Intake)

**Used by:** WS1 only (upstream feed into S-07; WS1 T-01 polls S-07 for NORMALISED-state ClaimRecords)
**Access type:** Event trigger (push) or polling (fallback per G-1); WS1 does not call S-01 directly — S-01 feeds the intake normalisation pipeline which writes NORMALISED ClaimRecords to S-07

### §1. Integration Purpose

S-01 is the submission gateway through which treating providers and submitting entities deliver claim packets to Greenfield. The intake normalisation pipeline (Intake & Anomaly Agent, D3 §2 Agent 1) receives from S-01, normalises to canonical `NormalizedClaimInput` format (authoritative field schema in `D4_canonical_claim_record.md`), and writes NORMALISED-state records to S-07. WS1 T-01 picks up from S-07 — it does not call S-01 directly.

This contract specifies: the intake mechanism S-01 must expose, the event/poll interface the intake pipeline consumes, and the ClaimRecord fields that must be populated when a NORMALISED record lands in S-07.

**Not in scope for this contract:** EDI 837 parsing or PDF extraction logic (Intake Agent responsibility); outbound rejection notice delivery to providers (S-12 contract); payment remittance (S-11 contract).

### §2. System Description

- **Assumed system name:** Greenfield Clearinghouse Partner (DISCOVERY_REQUIRED — likely an existing EDI clearinghouse partner such as a standard payer clearinghouse; the function is commodity infrastructure)
- **Base URL:** DISCOVERY_REQUIRED (`https://clearinghouse.greenfield-partner.example/api/v1` as placeholder)
- **Supported submission formats:** Eight formats confirmed in Claims Pack mock data — EDI 837P (professional, 50%), EDI 837I (institutional, 10%), provider portal JSON (20%), FHIR R4 Claim resource (5%), CMS-1500 paper PDF (10%), email .eml (1.5%), fax cover sheet PDF (1.5%), exception notes PDF (2%). **Note:** 85% of volume is machine-readable electronic format; 15% requires OCR or LLM extraction and carries higher per-claim intake cost.
- **Operations consumed by intake pipeline:** Claim submission event notification (push) OR claim staging table query (poll) — G-1 determines which path; both must be specified here

### §3. Authentication and Authorisation

- **Inbound submissions (provider → clearinghouse):** Provider authenticates to clearinghouse per clearinghouse partner's submission protocol (outside agent scope — providers use existing EDI trading partner agreements)
- **Intake pipeline → clearinghouse:** DISCOVERY_REQUIRED. Recommended: OAuth 2.0 client credentials with clearinghouse partner; alternatively, mTLS for EDI transport. Credentials stored in intake pipeline secrets manager.
- **Agent credential:** WS1 does not authenticate to S-01 directly. WS1 authenticates to S-07 only. The S-01 ↔ intake pipeline credential is in scope for the Intake Agent contract (separate deployment), not this contract.
- **HIPAA:** Clearinghouse partner must have a signed Business Associate Agreement with Greenfield Health Systems covering EDI 837 claim data. BAA confirmation is a pre-deployment checklist item.

### §4. Endpoint Contracts

**Path A — Event push (preferred, G-1 option 1):**

The clearinghouse partner pushes a notification to an internal Greenfield endpoint when a new claim submission arrives.

```
POST /intake/claim-received
Content-Type: application/json
{
  "submission_id":      "string — clearinghouse internal ID for this submission batch",
  "submission_format":  "enum [EDI_837P, EDI_837I, PORTAL_FORM, FHIR_R4, CMS1500_PDF, EMAIL_EML, FAX_PDF, EXCEPTION_NOTES_PDF]",
  "provider_npi":       "string — 10-digit NPI of submitting provider",
  "submitted_at":       "ISO 8601 UTC timestamp",
  "claim_count":        "integer — number of claims in this submission batch",
  "endpoint_url":       "string — where the intake pipeline can retrieve the full payload"
}
```

Intake pipeline fetches full payload from `endpoint_url`, parses, normalises, writes NORMALISED ClaimRecords to S-07.

**Path B — Internal staging table poll (fallback, G-1 option 2):**

The clearinghouse writes to an internal claims staging table that the intake pipeline polls at a configurable interval.

```
GET /claims/staging?state=PENDING_INTAKE&limit=50&cursor={cursor_token}
Authorization: Bearer {CLEARINGHOUSE_API_KEY}

Response (200 OK):
{
  "claims": [
    {
      "submission_id": "CLH-2025-0315-00421",
      "submission_format": "EDI_837P",
      "provider_npi": "1234567890",
      "submitted_at": "2025-03-15T08:12:33.000Z",
      "member_id": "GHS-MBR-4491023",
      "date_of_service": "2025-03-10",
      "procedure_codes": ["99213"],
      "diagnosis_codes": ["M17.11"],
      "payload_url": "/claims/staging/CLH-2025-0315-00421/payload"
    }
  ],
  "next_cursor": "eyJsYXN0X2lkIjoiQ0xILTIwMjUtMDMxNS0wMDQyMSJ9",
  "has_more": true
}
```

**ClaimRecord fields required in S-07 after normalisation (WS1 T-01 validation at intake):**

| Field | Source | Required |
|-------|--------|---------|
| `id` | Generated by intake pipeline | Yes |
| `state` | Set to `NORMALISED` by intake pipeline | Yes |
| `external_claim_id` | `submission_id` from clearinghouse | Yes |
| `member_id` | Extracted from EDI 837 / portal form | Yes |
| `provider_npi` | 10-digit NPI format | Yes |
| `date_of_service` | Extracted from claim | Yes (ISO 8601 date) |
| `procedure_codes` | CPT codes from claim | Yes (≥ 1, 5-digit CPT format) |
| `diagnosis_codes` | ICD-10 codes from claim | Yes (≥ 1, ICD-10 format) |
| `submission_format` | `EDI_837P` / `EDI_837I` / `PORTAL_FORM` / `FHIR_R4` / `CMS1500_PDF` / `EMAIL_EML` / `FAX_PDF` / `EXCEPTION_NOTES_PDF` | Yes |
| `created_at` | Set by intake pipeline at normalisation | Yes |
| `payer_id` | Derived from member eligibility lookup during normalisation | Yes |

**Status codes (polling path):**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 200 | Claims available | Process batch; advance cursor |
| 200 with empty `claims` array | No pending submissions | Wait `INTAKE_POLL_INTERVAL_SECONDS` (configurable; default 60); poll again |
| 401 | Credential expired | Refresh token; retry once; if fails → ops alert |
| 429 | Rate limit exceeded | Back off per §6; do not drop claims |
| 503 | Clearinghouse unavailable | Pause polling; retry every 60s; ops alert after 10 min; no WS1 processing impact (existing NORMALISED records in S-07 continue processing) |

**Worked example — polling path, single claim ingestion:**

Request:
```
GET /claims/staging?state=PENDING_INTAKE&limit=50&cursor=
Authorization: Bearer {CLEARINGHOUSE_API_KEY}
```

Response:
```json
HTTP 200
{
  "claims": [
    {
      "submission_id": "CLH-2025-0315-00421",
      "submission_format": "EDI_837P",
      "provider_npi": "1234567890",
      "submitted_at": "2025-03-15T08:12:33.000Z",
      "member_id": "GHS-MBR-4491023",
      "date_of_service": "2025-03-10",
      "procedure_codes": ["99213"],
      "diagnosis_codes": ["M17.11"],
      "payload_url": "/claims/staging/CLH-2025-0315-00421/payload"
    }
  ],
  "next_cursor": "eyJsYXN0X2lkIjoiQ0xILTIwMjUtMDMxNS0wMDQyMSJ9",
  "has_more": false
}
```

After normalisation, S-07 ClaimRecord written with `state = NORMALISED`, `external_claim_id = "CLH-2025-0315-00421"`, `provider_npi = "1234567890"`. WS1 T-01 picks up on next S-07 poll.

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 503 Clearinghouse unavailable | Yes | Indefinite (with pause) | Fixed 60s | Ops alert after 10 min; WS1 continues processing existing NORMALISED records; no new intake until clearinghouse recovers |
| 429 Rate limit | Yes | 3 | Exponential: 5s, 10s, 20s | Pause polling until rate limit window resets; ops alert |
| 401 Credential | Yes | 1 | None | Ops alert; pause intake |
| Malformed submission payload | No | 0 | N/A | Intake Agent logs `SCHEMA_VALIDATION_FAILED`; claim enters `PARSE_FAILED` state in S-07; exception escalated via S-09; WS1 never sees PARSE_FAILED claims |

### §6. Rate Limits and Throttling

- **Incoming submission rate:** DISCOVERY_REQUIRED. Expected: ~2,000 claims/day = ~85 claims/hour = 1–2 claims/min average; peak burst estimated 3× average = 5 claims/min
- **Polling frequency (Path B):** `INTAKE_POLL_INTERVAL_SECONDS` (configurable; default 60s; minimum 30s to avoid hammering clearinghouse)
- **Clearinghouse rate limit:** DISCOVERY_REQUIRED. Standard clearinghouse partners support ≥ 100 API calls/min for batch polling; confirm before go-live.

### §7. Data Mapping

| Clearinghouse field | Internal ClaimRecord field | Direction | Notes |
|--------------------|--------------------------|-----------|-------|
| `submission_id` | `external_claim_id` | S-01 → Agent | Clearinghouse's reference ID for this submission |
| `provider_npi` | `provider_npi` | S-01 → Agent | 10-digit NPI format |
| `submitted_at` | `created_at` | S-01 → Agent | Submission timestamp; used for SLA clock start |
| `submission_format` | `submission_format` | S-01 → Agent | Enum: `EDI_837P` / `EDI_837I` / `PORTAL_FORM` / `FHIR_R4` / `CMS1500_PDF` / `EMAIL_EML` / `FAX_PDF` / `EXCEPTION_NOTES_PDF` |
| `X-Submitter-NPI` (email only) | `provider_npi` | S-01 → Agent | Custom RFC 5322 header on `.eml` submissions — 10-digit NPI; extracted by Intake Agent before normalisation |
| `X-Submitter-TaxID` (email only) | *(provider tax ID — supplementary)* | S-01 → Agent | Custom RFC 5322 header on `.eml` submissions; DISCOVERY_REQUIRED whether this maps to a ClaimRecord field |
| `member_id` (from 837 loop) | `member_id` | S-01 → Agent | Extracted by Intake Agent from EDI 837 Loop 2010BA |
| `date_of_service` (from 837) | `date_of_service` | S-01 → Agent | EDI 837 DTP*472 segment; ISO 8601 date after normalisation |
| `procedure_codes` (SV1/SV2) | `procedure_codes` | S-01 → Agent | CPT 5-digit format; array |
| `diagnosis_codes` (HI segment) | `diagnosis_codes` | S-01 → Agent | ICD-10 format; array |

No writes from agent or intake pipeline back to S-01 after intake acknowledgement.

### §8. State Synchronisation

- **Pattern:** Event push (Path A) or polling at configurable interval (Path B)
- **WS1 perspective:** WS1 polls S-07 for `state = NORMALISED` records; it has no direct state sync with S-01
- **Deduplication:** Intake pipeline checks S-07 for existing records with matching `(external_claim_id, member_id, date_of_service, provider_npi)` before writing; duplicates trigger `PENDING_HITL_EXCEPTION` per T-01 duplicate detection logic

### §9. Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| Clearinghouse down | Graceful degrade — WS1 continues processing existing NORMALISED records in S-07; no new claims enter the pipeline until clearinghouse recovers; no data loss (clearinghouse holds undelivered submissions) |
| Push notification missed (Path A) | Fallback to polling (Path B) as secondary intake mechanism; both paths must be implemented regardless of which is primary |
| Malformed EDI payload | Intake Agent routes to `PARSE_FAILED`; exception processor handles; WS1 not involved |
| Email/fax/exception-notes extraction failure | LLM extraction returns incomplete required fields — Intake Agent routes to `PARSE_FAILED` with `extraction_confidence` score attached; exception processor reviews; WS1 never sees `PARSE_FAILED` records. Higher expected rate than EDI failures: email (~5%), fax (~10%), exception notes (~15%) extraction failure rate assumed. |
| CMS-1500 OCR failure | If live OCR is run (rather than using pre-extracted `cms1500-ocr/` text from clearinghouse): incomplete field extraction routes claim to `PARSE_FAILED`. Pre-extracted text path: only `PARSE_FAILED` if extracted text is too truncated for required field recovery. |
| Rate limit exceeded | Reduce poll frequency; queue notifications locally; ops alert |

### §10. Pre-deployment Checklist

- [ ] Clearinghouse partner confirmed with IT; system name and API documentation obtained; DISCOVERY_REQUIRED values replaced
- [ ] G-1 discovery action resolved: confirm whether event push (Path A) or polling (Path B) is the primary intake mechanism
- [ ] Both Path A and Path B implemented in intake pipeline regardless of which is primary (resilience requirement)
- [ ] Signed Business Associate Agreement (BAA) with clearinghouse partner covering EDI 837 claim data — Legal confirmation required before any PHI transmitted
- [ ] HIPAA EDI trading partner agreement (ISA/GS envelope credentials) established with clearinghouse partner
- [ ] Poll interval configured: `INTAKE_POLL_INTERVAL_SECONDS` default 60s; confirm with IT that this interval does not exceed clearinghouse's rate limit
- [ ] ClaimRecord schema validation test: submit a known-good EDI 837P → confirm NORMALISED record appears in S-07 with all required fields populated
- [ ] Malformed submission test: submit an intentionally malformed EDI payload → confirm claim enters PARSE_FAILED state in S-07 → confirm exception escalated via S-09; confirm WS1 never picks up PARSE_FAILED records

---

## IC-S-12 — Provider Portal / Clearinghouse (Outbound Rejection Notices)

**Used by:** WS1 only (T-10/T-12 — rejection notice dispatch after REJECTED state transition)
**Access type:** Write (push); WS1 writes outbound rejection notices to provider portal or clearinghouse for delivery to the submitting provider

### §1. Integration Purpose

When WS1 determines a claim must be rejected (ineligible member, invalid or implausible codes, missing required prior auth), it writes a structured rejection notice to S-12 for delivery to the submitting provider. The notice must include machine-readable rejection codes to enable provider resubmission workflows.

**Not in scope for this contract:** Inbound claim intake (S-01); payment remittance for approved claims (S-11); clinical path escalation (S-08/S-09). S-12 handles only outbound denials — it does not handle remittance advice for approved claims.

**Note on shared clearinghouse:** S-01 and S-12 may be the same clearinghouse partner. Confirm in discovery. If they are the same partner, a single set of credentials and base URL applies; the endpoint contracts are distinct operations on the same system. If they are different systems, separate credentials and contracts apply.

### §2. System Description

- **Assumed system name:** Greenfield Clearinghouse Partner — Outbound Channel (DISCOVERY_REQUIRED — may be the same partner as S-01, or a separate outbound-only clearinghouse)
- **Base URL:** DISCOVERY_REQUIRED; same as S-01 if confirmed to be the same clearinghouse (`https://clearinghouse.greenfield-partner.example/api/v1`)
- **Outbound format:** EDI 835 remittance advice (standard) or structured rejection notice via provider portal API; machine-readable rejection codes mandatory

### §3. Authentication and Authorisation

- **Method:** DISCOVERY_REQUIRED. Recommended: same service-account credential as S-01 if same clearinghouse partner; separate read-only scoped key for outbound-only.
- **Credential storage:** Agent secrets manager; key name `REJECTION_NOTICE_API_KEY`
- **Scope:** Write-only; no read access to provider portal records
- **HIPAA:** Same BAA as S-01 if same clearinghouse partner. If separate partner, a separate BAA covering outbound remittance and denial notice data is required.
- **Regulatory format requirement:** Outbound rejection notices must comply with HIPAA EOB (Explanation of Benefits) format requirements and applicable state-specific timely notice regulations. Legal review of rejection notice template required before deployment.

### §4. Endpoint Contracts

**Operation: Write rejection notice**

```
POST /notices/rejections
Content-Type: application/json
Authorization: Bearer {REJECTION_NOTICE_API_KEY}
```

Required request fields:

| Field | Type | Constraint |
|-------|------|-----------|
| `claim_id` | UUID | WS1 internal ClaimRecord ID |
| `external_claim_id` | string | Original clearinghouse submission ID (from `ClaimRecord.external_claim_id`); provider's reference |
| `provider_npi` | string | 10-digit NPI; identifies the recipient |
| `member_id` | string | Greenfield member ID |
| `date_of_service` | ISO 8601 date | From ClaimRecord |
| `rejection_codes` | array of strings | Machine-readable X12 Claim Adjustment Reason Codes (CARCs); minimum 1 code; must come from the validated rejection code reference set — free-text not accepted |
| `reason_descriptions` | array of strings | Human-readable description corresponding to each rejection code |
| `resubmission_guidance` | string ≤ 1024 chars | Specific actionable guidance for provider resubmission (e.g., "Prior authorisation required for CPT 27447 — obtain PA from Greenfield before resubmission") |
| `denial_date` | ISO 8601 date | Date of denial determination |
| `audit_log_entry_id` | UUID | The S-10 AuditLogEntry ID for the `CLAIM_REJECTED` action; required for reconciliation |

Optional fields:

| Field | Type | Use |
|-------|------|-----|
| `appeal_rights_statement` | string | Required by some state regulations; include when applicable |
| `internal_claim_reference` | string | For provider reconciliation |

**Status code → agent action:**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 202 | Notice queued for delivery | Write `CLAIM_REJECTED` + delivery confirmation to S-10; ClaimRecord.state = REJECTED |
| 400 | Missing required field or invalid rejection code | Do NOT retry — log defect; manual review; claim remains in REJECTED state but notice not delivered; ops alert |
| 401 | Credential expired | Refresh once; retry; if fails → ops alert |
| 409 | Duplicate notice (same `claim_id` + `denial_date`) | Treat as delivered (idempotent); log warning; do not re-send |
| 429 | Rate limit | Queue locally; retry with backoff |
| 503 | System unavailable | Queue notice locally; retry every 60s; ops alert after 10 min; notice must be delivered before SLA expiry |

**Worked example — rejection for missing prior authorisation:**

Request:
```json
POST /notices/rejections
{
  "claim_id": "e1f2a3b4-c5d6-7e8f-9a0b-1c2d3e4f5a6b",
  "external_claim_id": "CLH-2025-0315-00892",
  "provider_npi": "1234567890",
  "member_id": "GHS-MBR-4491023",
  "date_of_service": "2025-03-10",
  "rejection_codes": ["CO-197"],
  "reason_descriptions": [
    "CO-197: Precertification/authorization/notification absent"
  ],
  "resubmission_guidance": "Prior authorisation is required for CPT 27447 (total knee arthroplasty) under plan GHS-PLAN-GOLD-2025. Submit PA request via Greenfield provider portal before resubmitting this claim.",
  "denial_date": "2025-03-15",
  "audit_log_entry_id": "f7g8h9i0-j1k2-3l4m-5n6o-7p8q9r0s1t2u"
}
```

Response:
```json
HTTP 202
{
  "notice_id": "ntc-a1b2c3d4-e5f6-7g8h",
  "delivery_status": "QUEUED",
  "estimated_delivery": "2025-03-15T15:00:00.000Z"
}
```

**Worked example — rejection for ineligible member:**

Request:
```json
POST /notices/rejections
{
  "claim_id": "b3c4d5e6-f7a8-9b0c-1d2e-3f4a5b6c7d8e",
  "external_claim_id": "CLH-2025-0315-00905",
  "provider_npi": "9876543210",
  "member_id": "GHS-MBR-3318847",
  "date_of_service": "2025-03-08",
  "rejection_codes": ["CO-27", "CO-96"],
  "reason_descriptions": [
    "CO-27: Expenses incurred after coverage terminated",
    "CO-96: Non-covered charge(s)"
  ],
  "resubmission_guidance": "Member GHS-MBR-3318847 coverage ended 2025-02-28. Service date 2025-03-08 falls outside coverage period. Verify member eligibility before resubmission.",
  "denial_date": "2025-03-15",
  "audit_log_entry_id": "g8h9i0j1-k2l3-4m5n-6o7p-8q9r0s1t2u3v"
}
```

Response:
```json
HTTP 202
{
  "notice_id": "ntc-b2c3d4e5-f6a7-8b9c",
  "delivery_status": "QUEUED",
  "estimated_delivery": "2025-03-15T15:00:00.000Z"
}
```

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 429 Rate limit | Yes | 3 | Exponential: 5s, 10s, 20s | Queue locally; retry; ops alert if local queue > 20 notices |
| 503 Unavailable | Yes | Indefinite (with local queue) | Fixed 60s | Ops alert after 10 min; notice must be delivered before regulatory timely notice deadline |
| Timeout > 5s | Yes | 2 | Linear 5s | Treat as 503 |
| 400 Validation failure | No | 0 | N/A | Log defect; ops alert; manual delivery if timely notice deadline is imminent |

**Timely notice obligation:** State regulations typically require denial notices within 30 days of claim receipt (varies by state). The local queue must drain before this deadline. If S-12 is unavailable for > 24 hours, ops team must escalate to manual delivery.

### §6. Rate Limits and Throttling

- **Outbound rejection volume:** DISCOVERY_REQUIRED. Expected: ~15–20% of 2,000 claims/day = 300–400 rejection notices/day = ~1–2 per minute average
- **Rate limit:** DISCOVERY_REQUIRED. Standard clearinghouse partners support ≥ 100 writes/min; confirm before go-live.
- **Concurrent connections:** DISCOVERY_REQUIRED. Single connection per agent instance is sufficient given the low volume.

### §7. Data Mapping

| Internal field (ClaimRecord) | External API field | Direction | Notes |
|------------------------------|-------------------|-----------|-------|
| `id` | `claim_id` | Agent → System | WS1 internal ID |
| `external_claim_id` | `external_claim_id` | Agent → System | Provider's reference for reconciliation |
| `provider_npi` | `provider_npi` | Agent → System | 10-digit NPI |
| `member_id` | `member_id` | Agent → System | |
| `date_of_service` | `date_of_service` | Agent → System | |
| `rejection_codes` (from T-10/T-12) | `rejection_codes` | Agent → System | X12 CARC codes; array; min 1 |
| *(derived from rejection_codes)* | `reason_descriptions` | Agent → System | Human-readable; one per rejection code |
| *(generated by T-12)* | `resubmission_guidance` | Agent → System | Actionable, claim-specific guidance |
| *(AuditLogEntry.id for CLAIM_REJECTED action)* | `audit_log_entry_id` | Agent → System | S-10 reference |
| *(response)* | `notice_id` | System → Agent | Stored in AuditLogEntry.output_summary |
| *(response)* | `delivery_status` | System → Agent | `QUEUED` confirms acceptance |

No inbound data mapping — WS1 does not read from S-12.

### §8. State Synchronisation

- **Pattern:** Write-on-event; no polling; no caching
- **Trigger:** ClaimRecord transitions to REJECTED state → WS1 immediately writes rejection notice to S-12 → notice_id stored in AuditLogEntry.output_summary
- **Delivery confirmation:** S-12 acceptance (202) confirms the notice is queued; actual delivery to provider is S-12's responsibility. WS1 logs CLAIM_REJECTED with `delivery_status = QUEUED` — WS1 does not track final delivery status.

### §9. Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| S-12 down (503) | Queue notice locally; retry every 60s; ops alert after 10 min; do not block ClaimRecord from REJECTED state — the claim is rejected regardless of notice delivery status |
| Invalid rejection code (400) | Log defect; manual review; ops alert; if timely notice deadline imminent, ops team delivers notice manually |
| Rate limit (429) | Queue locally; retry with backoff; volume is low enough that local queue will drain within minutes |

ClaimRecord.state = REJECTED is set regardless of S-12 delivery status. A notice delivery failure does not reverse the rejection determination — it creates a separate delivery tracking obligation.

### §10. Pre-deployment Checklist

- [ ] Confirm whether S-12 is the same clearinghouse partner as S-01 — if yes, a single credential and BAA applies; if not, separate BAA required
- [ ] System name, base URL, and API documentation confirmed; DISCOVERY_REQUIRED values replaced
- [ ] Write-only API credential provisioned in secrets manager as `REJECTION_NOTICE_API_KEY`
- [ ] Rejection code reference set confirmed: X12 CARC codes validated as the correct standard; rejection code vocabulary loaded into WS1 at startup
- [ ] Legal review of rejection notice template completed: HIPAA EOB format compliance and applicable state timely notice requirements confirmed
- [ ] End-to-end test: submit a claim that will be rejected for missing PA → confirm rejection notice delivered with `CO-197` code → confirm `CLAIM_REJECTED` AuditLogEntry written to S-10 with `notice_id` in `output_summary`
- [ ] Duplicate notice test: send same `claim_id` + `denial_date` twice → confirm 409 response and second notice not delivered
- [ ] Timely notice SLA test: simulate S-12 down for 2 hours → confirm local queue holds notices → confirm notices delivered on recovery → confirm no timely notice deadline breach

---

*Pass 7b complete. Pass 7c appends IC-S-02, IC-S-03, IC-S-05.*

---

## IC-S-02 — Member Eligibility System

**Used by:** WS1 only (T-02 eligibility lookup; T-03 eligibility discrepancy resolution)
**Access type:** Read only (real-time lookup per claim); contains PHI — HIPAA minimum necessary standard applies

### §1. Integration Purpose

WS1 T-02 queries member eligibility for every claim at the start of the pipeline. The lookup confirms: is the member covered under the stated plan on the date of service? If the lookup returns a discrepancy (INACTIVE, PLAN_ID_MISMATCH, COVERAGE_GAP), T-03 applies deterministic correction rules before escalating to HITL.

**Not in scope for this contract:** Updating or writing eligibility records; querying eligibility for non-claim purposes; bulk eligibility verification. Write access to the eligibility system is explicitly excluded.

### §2. System Description

- **Assumed system name:** Greenfield Member Eligibility Service (DISCOVERY_REQUIRED — likely a module of the core payer administration platform; HIPAA 270/271 eligibility transaction is standard payer infrastructure)
- **Base URL:** DISCOVERY_REQUIRED (`https://eligibility.greenfield-internal.example/v1`)
- **Operations:** GET (real-time eligibility lookup); supports HIPAA 270/271 transaction semantics in JSON wrapper

### §3. Authentication and Authorisation

- **Method:** DISCOVERY_REQUIRED. Recommended: service-account API key (read-only scope).
- **Credential storage:** Agent secrets manager; key name `ELIGIBILITY_API_KEY`
- **Scope:** Read-only; minimum necessary fields only (`member_id`, `plan_id`, `date_of_service`); no write access; no bulk query access
- **PHI handling:** Response contains PHI (coverage status, dates); agent stores only the fields required for T-02/T-03 processing; no PHI written to external logs

### §4. Endpoint Contracts

**Operation: Eligibility lookup**

```
GET /members/{member_id}/eligibility?plan_id={plan_id}&date_of_service={YYYY-MM-DD}
Authorization: Bearer {ELIGIBILITY_API_KEY}
```

**Success response (200 OK):**

```json
{
  "member_id": "GHS-MBR-4491023",
  "plan_id": "GHS-PLAN-GOLD-2025",
  "date_of_service": "2025-03-10",
  "eligibility_status": "ACTIVE",
  "coverage_start_date": "2025-01-01",
  "coverage_end_date": "2025-12-31",
  "last_verified_at": "2025-03-14T22:00:00.000Z"
}
```

**`eligibility_status` enum:**

| Value | Meaning | T-02/T-03 action |
|-------|---------|-----------------|
| `ACTIVE` | Member covered on date_of_service | Proceed to T-04 |
| `INACTIVE` | Coverage not active | T-03: check `last_verified_at` lag; if lag > 24h, treat as possible data lag (not auto-deny); escalate ET-03 |
| `NOT_FOUND` | Member ID not in system | T-03: escalate ET-03 immediately |
| `PLAN_ID_MISMATCH` | Member found but under different plan | T-03: apply plan correction rule if deterministic; else ET-03 |
| `COVERAGE_GAP` | Member active but gap includes date_of_service | T-03: check if gap < 3 days (data lag candidate); else ET-03 |

**Eligibility data lag handling (T-03 rule — do not auto-deny):** Eligibility systems batch-update overnight. `INACTIVE` or `COVERAGE_GAP` where `last_verified_at` is > 24 hours old may reflect stale data, not true ineligibility. T-03 must not auto-deny on these statuses — escalate ET-03 for human confirmation.

**Status code → agent action:**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 200 | Valid response | Process `eligibility_status` per T-02/T-03 logic |
| 404 | Member not found | `eligibility_status = NOT_FOUND`; escalate ET-03 |
| 401 | Credential invalid | Refresh once; retry; if fails → ops alert, suspend processing |
| 429 | Rate limit | Queue; backoff per §5 |
| 503 | System unavailable | Retry once after 5s; if still unavailable → escalate ET-03 (cannot adjudicate without eligibility confirmation); claim enters PENDING_HITL_EXCEPTION |

**Worked example — active member:**

Request:
```
GET /members/GHS-MBR-4491023/eligibility?plan_id=GHS-PLAN-GOLD-2025&date_of_service=2025-03-10
Authorization: Bearer {ELIGIBILITY_API_KEY}
```

Response:
```json
HTTP 200
{
  "member_id": "GHS-MBR-4491023",
  "plan_id": "GHS-PLAN-GOLD-2025",
  "date_of_service": "2025-03-10",
  "eligibility_status": "ACTIVE",
  "coverage_start_date": "2025-01-01",
  "coverage_end_date": "2025-12-31",
  "last_verified_at": "2025-03-14T22:00:00.000Z"
}
```

Result: T-02 confirms eligibility; proceeds to T-04. AuditLogEntry written: `action = ELIGIBILITY_CONFIRMED`.

**Worked example — stale INACTIVE (data lag candidate):**

Request:
```
GET /members/GHS-MBR-7712345/eligibility?plan_id=GHS-PLAN-SILVER-2025&date_of_service=2025-03-12
```

Response:
```json
HTTP 200
{
  "member_id": "GHS-MBR-7712345",
  "plan_id": "GHS-PLAN-SILVER-2025",
  "date_of_service": "2025-03-12",
  "eligibility_status": "INACTIVE",
  "coverage_start_date": "2025-01-01",
  "coverage_end_date": null,
  "last_verified_at": "2025-03-09T22:00:00.000Z"
}
```

Result: T-03 checks `last_verified_at` — 3 days ago (> 24h lag threshold). Data lag candidate; do not auto-deny. Escalate ET-03 with `trigger_signal_values = {eligibility_status: "INACTIVE", last_verified_at: "2025-03-09T22:00:00.000Z", lag_hours: 72}`. AuditLogEntry: `action = ELIGIBILITY_ESCALATED`.

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 503 Unavailable | Yes | 1 | 5s fixed | Escalate ET-03; claim to PENDING_HITL_EXCEPTION; exception processor confirms eligibility manually |
| Timeout > 5s | Yes | 1 | None | Treat as 503 |
| 429 Rate limit | Yes | 3 | Exponential: 1s, 2s, 4s | Ops alert; queue claim; retry |
| 401 Credential | Yes | 1 | None | Suspend processing; ops alert |
| 404 Not found | No | 0 | N/A | Escalate ET-03 immediately |

### §6. Rate Limits and Throttling

- **Call frequency:** 1 call per claim at T-02; ~2,000 calls/day = ~1.4 calls/min average; peak burst ~10 calls/min
- **Minimum required capacity:** ≥ 20 calls/min per agent instance (sufficient headroom for burst)
- **Rate limit:** DISCOVERY_REQUIRED. Standard payer eligibility APIs support ≥ 100 real-time lookups/min; confirm before go-live.

### §7. Data Mapping

| Internal ClaimRecord field | External API parameter/response field | Direction | Notes |
|---------------------------|--------------------------------------|-----------|-------|
| `member_id` | `{member_id}` (path) | Agent → System | |
| `payer_id` | `plan_id` (query param) | Agent → System | |
| `date_of_service` | `date_of_service` (query param) | Agent → System | ISO 8601 date |
| *(T-02 result)* | `eligibility_status` | System → Agent | Stored in AuditLogEntry.input_summary; not persisted to ClaimRecord |
| *(T-02 result)* | `coverage_start_date`, `coverage_end_date` | System → Agent | Used in T-03 lag analysis; not persisted to ClaimRecord |
| *(T-02 result)* | `last_verified_at` | System → Agent | Used in T-03 lag threshold check (> 24h) |

No writes to eligibility system.

### §8. State Synchronisation

- **Pattern:** On-demand per claim at T-02 execution; no caching
- **Rationale for no caching:** Eligibility data is member-specific and changes with coverage events; caching introduces the data lag risk that T-03 is designed to catch. Re-querying on every claim ensures the freshest available status.

### §9. Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| S-02 unavailable | Escalate ET-03 — cannot auto-adjudicate without eligibility confirmation; claim to PENDING_HITL_EXCEPTION; exception processor confirms manually |
| INACTIVE / COVERAGE_GAP with stale `last_verified_at` | Escalate ET-03 (do not auto-deny); T-03 explicit rule |
| Unexpected response schema | Treat as 503; escalate ET-03 |

Auto-denial without eligibility confirmation is not a valid fallback.

### §10. Pre-deployment Checklist

- [ ] System name and base URL confirmed; DISCOVERY_REQUIRED values replaced
- [ ] Read-only API credential provisioned as `ELIGIBILITY_API_KEY`; no write scope granted — confirmed via integration test (attempt write → confirm 403 or 405)
- [ ] PHI handling confirmed: eligibility response fields not written to unencrypted external logs; only `eligibility_status` and `last_verified_at` retained in AuditLogEntry
- [ ] Data lag threshold (24 hours) confirmed with compliance team as the correct threshold for ET-03 escalation vs. data lag candidate treatment
- [ ] P95 latency test: confirm ≤ 5s P95 response time under expected load (20 concurrent lookups)
- [ ] ET-03 escalation end-to-end test: simulate 503 from S-02 → confirm claim enters PENDING_HITL_EXCEPTION → confirm EscalationPacket delivered to S-09
- [ ] Data lag test: query for member with INACTIVE status where `last_verified_at` > 24h → confirm T-03 routes to ET-03 (not auto-deny) → confirm AuditLogEntry action = ELIGIBILITY_ESCALATED

---

## IC-S-03 — Code Validation Reference (ICD-10 / CPT)

**Used by:** WS1 only (T-04 ICD-10 validation; T-05 CPT validation and procedure-diagnosis plausibility)
**Access type:** Read (batch-loaded at startup; no real-time API calls during claim processing)

### §1. Integration Purpose

WS1 loads the ICD-10 diagnosis code and CPT procedure code validity reference sets at agent startup. T-04 validates each diagnosis code against the current ICD-10 reference; T-05 validates each procedure code against the current CPT reference and checks procedure-diagnosis pairing plausibility.

**Not in scope for this contract:** Medical necessity criteria retrieval (S-15, SCOPE-OUT); clinical notes (S-13, SCOPE-OUT); fee schedule rates (S-05 contract). S-03 covers code validity and plausibility — not rates or necessity judgements.

### §2. System Description

- **Assumed system name:** Greenfield Code Validation Reference Service (DISCOVERY_REQUIRED — may be a licensed CMS/AMA code set API, a flat-file batch download, or a module of the claims management platform)
- **Base URL:** DISCOVERY_REQUIRED (`https://coderef.greenfield-internal.example/v1`)
- **Operations:** GET (batch download of current code reference at startup); optionally GET for single-code real-time lookup (fallback for novel codes not in batch)
- **Code set licenses:** CMS ICD-10 (public, no license fee); AMA CPT (licensed — requires paid AMA subscription confirming agent use is permitted)
- **Update cycle:** ICD-10 annually each October 1; CPT annually each January 1

### §3. Authentication and Authorisation

- **Method:** DISCOVERY_REQUIRED. Recommended: service-account API key (read-only).
- **Credential storage:** Agent secrets manager; key name `CODE_REF_API_KEY`
- **Scope:** Read-only; no write access; no bulk export beyond what is required for the startup batch load
- **License compliance:** AMA CPT license must explicitly permit agent-mediated lookup and batch download. Legal confirmation required before go-live.

### §4. Endpoint Contracts

**Operation A: Batch load at startup**

```
GET /code-references/batch?code_type={ICD10|CPT}&effective_date={YYYY-MM-DD}
Authorization: Bearer {CODE_REF_API_KEY}

Response (200 OK):
{
  "code_type": "CPT",
  "effective_date": "2025-01-01",
  "version_id": "CPT-2025-01",
  "valid_through": "2025-12-31",
  "codes": [
    {
      "code": "99213",
      "description": "Office or other outpatient visit, established patient, moderate complexity",
      "valid_from": "2025-01-01",
      "valid_through": "2025-12-31",
      "requires_modifier": false
    },
    {
      "code": "27447",
      "description": "Arthroplasty, knee, condyle and plateau; medial AND lateral compartments",
      "valid_from": "2025-01-01",
      "valid_through": "2025-12-31",
      "requires_modifier": false
    }
  ],
  "total_codes": 10847,
  "next_cursor": null
}
```

Startup validation on batch load:
1. `version_id` is non-null
2. `valid_through ≥ today` — stale reference triggers `REFERENCE_DATA_EXPIRED` and fires ET-06; agent does not start claim processing with a stale reference
3. `total_codes > 0`

**Operation B: Single-code lookup (optional, for novel codes not in batch):**

```
GET /code-references/{code_type}/{code}?effective_date={YYYY-MM-DD}
Authorization: Bearer {CODE_REF_API_KEY}

Response:
{
  "code": "99214",
  "code_type": "CPT",
  "valid_from": "2025-01-01",
  "valid_through": "2025-12-31",
  "description": "Office or other outpatient visit, established patient, moderate-high complexity",
  "requires_modifier": false
}
```

**Plausibility pairing table (loaded alongside code reference at startup):**

```
GET /code-references/plausibility-pairs?version_id={CPT-2025-01}

Response:
{
  "version_id": "CPT-2025-01",
  "valid_through": "2025-12-31",
  "pairs": [
    {
      "procedure_code": "27447",
      "icd_chapter_prefix": "M",
      "required_icd_ranges": ["M16", "M17"],
      "plausibility_verdict": "EXPECTED"
    }
  ],
  "total_pairs": 4231
}
```

**Status codes (batch load):**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 200 | Batch loaded | Proceed to startup validation (version_id, valid_through, total_codes) |
| 404 | No reference for requested effective_date | Fail fast; ops alert |
| 401 | Credential invalid | Fail fast; ops alert |
| 503 | Unavailable | Retry once after 30s; if still unavailable, fail fast |

**Worked example — T-05 CPT validation for CPT 27447 with ICD-10 M17.11:**

WS1 T-05 checks plausibility pairing table (loaded at startup):
- `procedure_code = "27447"`, `diagnosis_code = "M17.11"` (primary osteoarthritis, right knee)
- Table lookup: pair `(27447, M17)` → `plausibility_verdict = EXPECTED`
- Result: Plausibility confirmed; proceed to T-06 (prior auth check)
- AuditLogEntry: `action = CODE_PLAUSIBILITY_ASSESSED`, `output_summary.verdict = EXPECTED`

**Worked example — novel combination not in plausibility table:**

- `procedure_code = "93306"` (echocardiography), `diagnosis_code = "M17.11"` (knee osteoarthritis)
- Table lookup: pair `(93306, M17)` → not found
- T-05 logs `RETRIEVAL_THRESHOLD_NOT_MET` in compliance_flags; if vector store augmentation (S-15) is available, queries vector store with cosine similarity ≥ 0.70; if S-15 SCOPE-OUT, logs `S15_SCOPE_OUT` and escalates ET-05 (coding implausibility)

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 503 at startup | Yes | 1 | 30s fixed | Fail fast; do not start claim processing with no reference |
| Stale reference (`valid_through < today`) | No | 0 | N/A | Fire `REFERENCE_DATA_EXPIRED`; ET-06 escalation; agent does not start |
| 401 | No | 0 | N/A | Fail fast; ops alert |

No retries during claim processing — the reference is batch-loaded at startup. Runtime code checks are in-memory lookups; S-03 is not called per claim.

### §6. Rate Limits and Throttling

- **Call frequency:** Batch load once at startup (~2 calls — one for ICD-10, one for CPT); single-code fallback lookups are rare
- **Batch download size:** ~10,000–12,000 CPT codes; ~70,000+ ICD-10 codes (with pagination); total startup load < 5 minutes expected
- **Rate limit:** DISCOVERY_REQUIRED. Batch download may require special arrangement with the code reference provider; confirm before go-live.

### §7. Data Mapping

| Internal usage | External API field | Direction | Notes |
|----------------|-------------------|-----------|-------|
| T-04/T-05 in-memory code table | `codes[].code`, `codes[].valid_from`, `codes[].valid_through` | System → Agent | Loaded at startup; in-memory for claim processing |
| T-05 plausibility table | `pairs[].procedure_code`, `pairs[].icd_chapter_prefix`, `pairs[].plausibility_verdict` | System → Agent | |
| Pipeline startup version check | `version_id`, `valid_through` | System → Agent | Must be ≥ today |
| AuditLogEntry.input_summary | `version_id` | System → Agent | Logged for every T-04/T-05 audit entry |

### §8. State Synchronisation

- **Pattern:** Batch load at agent startup; in-memory for the session duration
- **Version control:** `version_id` logged in every AuditLogEntry for T-04/T-05 actions; provides full traceability of which code set version validated each claim
- **Update mechanism:** New reference loaded on next agent restart (controlled deployment); no hot reload. Annual update cycle (ICD-10 October, CPT January) triggers a planned restart.

### §9. Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| Stale reference at startup | Fail fast — `REFERENCE_DATA_EXPIRED`; fire ET-06; do not start claim processing |
| S-03 unavailable at startup | Fail fast — retry once after 30s; if still unavailable, do not start |
| Code not found in batch (novel code) | Single-code real-time lookup (Operation B) if configured; if unavailable, escalate ET-05 |

### §10. Pre-deployment Checklist

- [ ] System name and base URL confirmed; DISCOVERY_REQUIRED values replaced
- [ ] Read-only API credential provisioned as `CODE_REF_API_KEY`
- [ ] AMA CPT license confirmed to permit agent-mediated batch download and in-memory use — Legal sign-off required
- [ ] CMS ICD-10 reference confirmed as current year version (October release); `valid_through = 2025-09-30` for the 2025 release
- [ ] Annual update procedure documented: who triggers the agent restart when ICD-10 or CPT annual updates are released? Operations runbook required.
- [ ] Stale reference test: set `valid_through` to yesterday → confirm agent fires `REFERENCE_DATA_EXPIRED` → confirm agent does not start → confirm ET-06 logged
- [ ] Novel code test: query a code not in the plausibility table → confirm T-05 logs `RETRIEVAL_THRESHOLD_NOT_MET` and escalates ET-05

---

## IC-S-05 — Fee Schedule System

**Used by:** WS1 only (T-09 payment calculation; determines `payment_amount` for ADMIN_CLEARED claims)
**Access type:** Read only (on-demand per claim at T-09); commercially sensitive — contracted rates must not be logged externally

### §1. Integration Purpose

WS1 T-09 queries the fee schedule to determine the contracted rate for an approved administrative claim immediately before writing the payment instruction to S-11. The query is claim-specific: provider + procedure code + plan + any modifier codes.

**Not in scope for this contract:** Contract exception handling (S-06, SCOPE-OUT — covers non-standard rates only); clinical path payment (clinical claims reach APPROVED only after physician sign-off, which writes to S-07; the fee schedule lookup for clinical claims uses the same endpoint). Fee schedule management, rate negotiation, or updates are not agent responsibilities.

### §2. System Description

- **Assumed system name:** Greenfield Fee Schedule Service (DISCOVERY_REQUIRED — may be a module of the claims management platform or a separate rate management system)
- **Base URL:** DISCOVERY_REQUIRED (`https://feeschedule.greenfield-internal.example/v1`)
- **Operations:** GET (on-demand rate lookup per claim); no write access

### §3. Authentication and Authorisation

- **Method:** DISCOVERY_REQUIRED. Recommended: service-account API key (read-only).
- **Credential storage:** Agent secrets manager; key name `FEE_SCHEDULE_API_KEY`
- **Scope:** Read-only; contracted rate data only; no access to rate negotiation records, amendment history, or contract exception clauses (S-06)
- **Confidentiality:** Contracted rates are commercially sensitive. Rate values must not appear in external logs, exception packets, or rejection notices. They may appear in AuditLogEntry.output_summary (internal compliance record) but not in S-12 outbound notices.

### §4. Endpoint Contracts

**Operation: Rate lookup**

```
GET /rates?provider_id={provider_id}&procedure_code={cpt_code}&plan_id={plan_id}&date_of_service={YYYY-MM-DD}&modifier_codes={comma_separated}
Authorization: Bearer {FEE_SCHEDULE_API_KEY}
```

**Success response (200 OK):**

```json
{
  "provider_id": "1234567890",
  "procedure_code": "99213",
  "plan_id": "GHS-PLAN-GOLD-2025",
  "date_of_service": "2025-03-10",
  "modifier_codes": [],
  "contracted_rate": 185.00,
  "cost_sharing_proportion": 0.20,
  "member_responsibility": 37.00,
  "payer_responsibility": 148.00,
  "rate_version": "GHS-FS-2025-01",
  "rate_valid_through": "2025-12-31"
}
```

**`payment_amount` derivation:** `payer_responsibility` = `contracted_rate × (1 - cost_sharing_proportion)`. Agent uses `payer_responsibility` as `payment_amount` in the S-11 payment instruction. Member responsibility is informational only — member billing is outside agent scope.

**Modifier code handling:** When `modifier_codes` is non-empty, the fee schedule must return the rate adjusted for the modifier. If modifier combination is unrecognised, the system returns 422 with `error_code = MODIFIER_NOT_APPLICABLE`; agent escalates ET-06.

**Status code → agent action:**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 200 | Rate found | Validate `rate_valid_through ≥ today`; compute `payment_amount`; proceed to T-09 payment write |
| 404 | No rate for this provider/procedure/plan | Escalate ET-06 (no contracted rate found) |
| 422 | Modifier code unrecognised | Escalate ET-06 with `trigger_signal_values = {modifier_codes, procedure_code, error_code}` |
| 401 | Credential invalid | Suspend; ops alert |
| 429 | Rate limit | Queue; backoff |
| 503 | Unavailable | Retry once after 5s; if still unavailable → escalate ET-06; claim to PENDING_HITL_EXCEPTION |

**Worked example — standard office visit:**

Request:
```
GET /rates?provider_id=1234567890&procedure_code=99213&plan_id=GHS-PLAN-GOLD-2025&date_of_service=2025-03-10&modifier_codes=
Authorization: Bearer {FEE_SCHEDULE_API_KEY}
```

Response:
```json
HTTP 200
{
  "provider_id": "1234567890",
  "procedure_code": "99213",
  "plan_id": "GHS-PLAN-GOLD-2025",
  "date_of_service": "2025-03-10",
  "modifier_codes": [],
  "contracted_rate": 185.00,
  "cost_sharing_proportion": 0.20,
  "member_responsibility": 37.00,
  "payer_responsibility": 148.00,
  "rate_version": "GHS-FS-2025-01",
  "rate_valid_through": "2025-12-31"
}
```

`payment_amount = 148.00` USD. S-11 payment instruction written with this value.

**Worked example — rate not found (no contracted rate for this provider):**

```json
HTTP 404
{
  "error_code": "RATE_NOT_FOUND",
  "provider_id": "9988776655",
  "procedure_code": "93306",
  "plan_id": "GHS-PLAN-SILVER-2025",
  "message": "No contracted rate exists for this provider-procedure-plan combination"
}
```

T-09 escalates ET-06: `escalation_reason = CONTRACT_EXCEPTION`, `trigger_signal_values = {error_code: "RATE_NOT_FOUND", provider_npi: "9988776655", procedure_code: "93306", payer_id: "GHS-PLAN-SILVER-2025"}`.

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 503 Unavailable | Yes | 1 | 5s fixed | Escalate ET-06; claim to PENDING_HITL_EXCEPTION |
| Timeout > 5s | Yes | 1 | None | Treat as 503 |
| 429 Rate limit | Yes | 3 | Exponential: 1s, 2s, 4s | Queue; ops alert |
| 404 Rate not found | No | 0 | N/A | Escalate ET-06 |
| 422 Modifier unrecognised | No | 0 | N/A | Escalate ET-06 |
| 401 Credential | No | 0 | N/A | Suspend; ops alert |

### §6. Rate Limits and Throttling

- **Call frequency:** 1 call per ADMIN_CLEARED claim at T-09; ~65% of 2,000 claims/day = ~1,300 calls/day = ~1.4 calls/min average; peak burst ~15 calls/min
- **Minimum required capacity:** ≥ 20 calls/min per agent instance
- **Rate limit:** DISCOVERY_REQUIRED. Internal fee schedule systems typically support ≥ 100 lookups/min; confirm before go-live.

### §7. Data Mapping

| Internal field | External API field | Direction | Notes |
|----------------|-------------------|-----------|-------|
| `ClaimRecord.provider_npi` | `provider_id` (query param) | Agent → System | 10-digit NPI |
| `ClaimRecord.procedure_codes[0]` | `procedure_code` (query param) | Agent → System | Primary procedure code; multi-procedure support DISCOVERY_REQUIRED |
| `ClaimRecord.payer_id` | `plan_id` (query param) | Agent → System | |
| `ClaimRecord.date_of_service` | `date_of_service` (query param) | Agent → System | |
| `ClaimRecord.modifier_codes` | `modifier_codes` (query param) | Agent → System | Comma-separated; empty string if none |
| `payment_amount` | `payer_responsibility` | System → Agent | Written to ClaimRecord and S-11 payment instruction |
| `rate_version` | `rate_version` | System → Agent | Logged in AuditLogEntry.input_summary for audit traceability |
| `rate_valid_through` | `rate_valid_through` | System → Agent | Validated: must be ≥ today; otherwise fire ET-06 |

Contracted rates (`contracted_rate`, `cost_sharing_proportion`) not written to S-10 external logs or S-12 rejection notices. Internal AuditLogEntry only.

### §8. State Synchronisation

- **Pattern:** On-demand per claim at T-09 execution; no caching
- **Rationale for no caching:** Rate schedules can change with provider contract amendments; caching a rate that was subsequently amended creates an overpayment risk. Re-querying on every claim is the safe default.
- **Version check at startup:** Agent verifies that at least one fee schedule version is accessible and `rate_valid_through ≥ today` before starting claim processing. Stale fee schedule fires ET-06 and blocks startup.

### §9. Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| S-05 unavailable | Escalate ET-06 — cannot auto-pay without confirmed rate; claim to PENDING_HITL_EXCEPTION; exception processor confirms rate manually |
| Rate not found (404) | Escalate ET-06 — possible contract exception (S-06) or out-of-network provider |
| Stale `rate_valid_through` | Fire `REFERENCE_DATA_EXPIRED`; escalate ET-06 |

Auto-payment without a confirmed contracted rate is not a valid fallback.

### §10. Pre-deployment Checklist

- [ ] System name and base URL confirmed; DISCOVERY_REQUIRED values replaced
- [ ] Read-only API credential provisioned as `FEE_SCHEDULE_API_KEY`; confirmed no write scope
- [ ] Contracted rate confidentiality confirmed: rate values do not appear in S-10 external audit logs or S-12 rejection notices — only in internal AuditLogEntry.output_summary
- [ ] Fee schedule version current and `rate_valid_through ≥ 2025-12-31` for plan year 2025; annual update procedure documented
- [ ] Multi-procedure claim handling confirmed: if a claim has multiple procedure codes, confirm whether S-05 supports multiple lookups per claim or if each code requires a separate call (affects rate limit planning)
- [ ] Rate-not-found end-to-end test: query a known non-contracted provider → confirm 404 → confirm ET-06 escalation → confirm claim enters PENDING_HITL_EXCEPTION
- [ ] Modifier code test: query with an unrecognised modifier → confirm 422 → confirm ET-06 escalation

---

*Pass 7c complete. Pass 7d appends IC-S-04 and IC-S-14.*

---

## IC-S-04 — Prior Authorisation System

**Used by:** WS1 only (T-06 prior auth presence check; T-07 partial-match resolution)
**Access type:** Read only; write access to the prior auth system is explicitly excluded from agent authority

### §1. Integration Purpose

WS1 T-06 determines whether a prior authorisation exists for the claimed procedure + member + service date. T-07 handles partial matches (authorised units ≠ claimed units) using the configurable `PRIOR_AUTH_UNIT_TOLERANCE_PCT` parameter. If no prior auth is found for a procedure that requires one, or if the partial match exceeds tolerance, ET-04 escalates to HITL.

**Not in scope for this contract:** Creating, approving, or amending prior auth records; querying prior auth for non-adjudication purposes. Write access is technically prohibited — the agent may not modify prior auth records under any circumstance.

### §2. System Description

- **Assumed system name:** Greenfield Prior Authorisation Service (DISCOVERY_REQUIRED — likely a module of the core payer administration platform; prior auth management is a standard payer function)
- **Base URL:** DISCOVERY_REQUIRED (`https://priorauth.greenfield-internal.example/v1`)
- **Operations:** GET (prior auth lookup by member + procedure + service date); read-only

### §3. Authentication and Authorisation

- **Method:** DISCOVERY_REQUIRED. Recommended: service-account API key with read-only scope enforced at the API level — not just a procedural control.
- **Credential storage:** Agent secrets manager; key name `PRIOR_AUTH_API_KEY`
- **Scope:** Read-only; no write, update, or delete access. **Write exclusion is a hard requirement — not configurable.** The agent credential must not have write scope on the prior auth system. This is a compliance boundary: agents may not self-authorise procedures.
- **Enforcement:** IT must confirm the API key scope restriction is technically enforced (not just documented). Pre-deployment integration test: attempt a write (POST/PATCH) with `PRIOR_AUTH_API_KEY` → confirm 403. This test is mandatory.

### §4. Endpoint Contracts

**Operation: Prior auth lookup**

```
GET /authorizations?member_id={member_id}&procedure_code={cpt_code}&service_date={YYYY-MM-DD}
Authorization: Bearer {PRIOR_AUTH_API_KEY}
```

**`prior_auth_status` enum and T-06/T-07 action:**

| Status | Meaning | T-06/T-07 action |
|--------|---------|-----------------|
| `NOT_REQUIRED` | Procedure does not require prior auth under this plan | Proceed to T-08 (clinical routing) |
| `PRESENT_EXACT_MATCH` | Auth found; `authorized_units = claimed_units` | Proceed to T-08 |
| `PRESENT_PARTIAL_MATCH` | Auth found; `authorized_units ≠ claimed_units` | T-07: evaluate `PRIOR_AUTH_UNIT_TOLERANCE_PCT`; proceed or escalate ET-04 |
| `NOT_FOUND` | No auth record for this member/procedure/date | T-06: check if procedure requires auth; if yes → escalate ET-04 |
| `EXPIRED` | Auth exists but `expiry_date < service_date` | T-06: escalate ET-04 with `trigger_signal_values = {expiry_date, service_date}` |

**`PRIOR_AUTH_UNIT_TOLERANCE_PCT` logic (T-07):**
```
units_variance_pct = abs(authorized_units - claimed_units) / authorized_units × 100
IF units_variance_pct ≤ PRIOR_AUTH_UNIT_TOLERANCE_PCT (configurable; default 10%):
  THEN proceed — tolerance applied; log PRIOR_AUTH_TOLERANCE_APPLIED
ELSE:
  THEN escalate ET-04 — partial match exceeds tolerance
```

**Success response (200 OK) — exact match:**

```json
{
  "authorization_id": "PA-2025-04-00892",
  "member_id": "GHS-MBR-4491023",
  "procedure_code": "27447",
  "plan_id": "GHS-PLAN-GOLD-2025",
  "service_date": "2025-03-10",
  "prior_auth_status": "PRESENT_EXACT_MATCH",
  "authorized_units": 1,
  "claimed_units": 1,
  "authorized_provider_id": "1234567890",
  "issued_date": "2025-02-20",
  "expiry_date": "2025-04-20"
}
```

**Success response (200 OK) — partial match:**

```json
{
  "authorization_id": "PA-2025-03-00442",
  "member_id": "GHS-MBR-5502134",
  "procedure_code": "97110",
  "plan_id": "GHS-PLAN-SILVER-2025",
  "service_date": "2025-03-14",
  "prior_auth_status": "PRESENT_PARTIAL_MATCH",
  "authorized_units": 10,
  "claimed_units": 12,
  "authorized_provider_id": "9876543210",
  "issued_date": "2025-02-15",
  "expiry_date": "2025-05-15"
}
```

T-07: `units_variance_pct = abs(10-12)/10 × 100 = 20%`. If `PRIOR_AUTH_UNIT_TOLERANCE_PCT = 10%`, 20% > 10% → escalate ET-04.

**Success response (200 OK) — not required:**

```json
{
  "member_id": "GHS-MBR-6614222",
  "procedure_code": "99213",
  "plan_id": "GHS-PLAN-GOLD-2025",
  "service_date": "2025-03-12",
  "prior_auth_status": "NOT_REQUIRED"
}
```

T-06: proceed to T-08.

**Status codes:**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 200 | Response received | Process `prior_auth_status` per T-06/T-07 logic above |
| 404 | No record exists for this query | `prior_auth_status = NOT_FOUND`; T-06 escalates ET-04 if procedure requires auth |
| 401 | Credential invalid | Suspend; ops alert |
| 429 | Rate limit | Queue; backoff |
| 503 | Unavailable | Retry once after 5s; if still unavailable → escalate ET-04; no payment determination without PA confirmation for procedures requiring it |

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 503 Unavailable | Yes | 1 | 5s fixed | Escalate ET-04; claim to PENDING_HITL_EXCEPTION |
| Timeout > 5s | Yes | 1 | None | Treat as 503 |
| 429 Rate limit | Yes | 3 | Exponential: 1s, 2s, 4s | Queue; ops alert |
| 404 Not found | No | 0 | N/A | Apply NOT_FOUND logic per T-06 |

Cannot auto-adjudicate a PA-required procedure without PA confirmation.

### §6. Rate Limits and Throttling

- **Call frequency:** 1 call per claim that requires prior auth check; subset of 2,000/day; exact proportion DISCOVERY_REQUIRED (depends on what % of Greenfield's procedure mix requires PA)
- **Expected volume:** ~500–800 PA lookups/day (rough estimate); < 2 calls/min average
- **Minimum required capacity:** ≥ 20 calls/min per agent instance

### §7. Data Mapping

| Internal field | External API field | Direction | Notes |
|----------------|-------------------|-----------|-------|
| `ClaimRecord.member_id` | `member_id` (query param) | Agent → System | |
| `ClaimRecord.procedure_codes[0]` | `procedure_code` (query param) | Agent → System | Primary procedure |
| `ClaimRecord.date_of_service` | `service_date` (query param) | Agent → System | |
| *(result)* | `prior_auth_status` | System → Agent | Drives T-06/T-07 branching |
| *(result)* | `authorized_units` | System → Agent | Required for T-07 partial-match calculation |
| *(result)* | `expiry_date` | System → Agent | Validated: must be ≥ service_date |
| *(result)* | `authorization_id` | System → Agent | Logged in AuditLogEntry.input_summary |
| `PRIOR_AUTH_UNIT_TOLERANCE_PCT` (config) | N/A | Internal | Configurable parameter; default 10%; drives T-07 threshold |

No writes to prior auth system.

### §8. State Synchronisation

- **Pattern:** On-demand per claim at T-06; no caching
- **No caching rationale:** Prior auth records change (amendments, expirations); caching creates stale-auth risk. Query per claim.

### §9. Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| S-04 unavailable | Escalate ET-04 — cannot auto-adjudicate PA-required procedures without PA confirmation; HITL confirms manually |
| NOT_FOUND for PA-required procedure | Escalate ET-04 — possible resubmission without PA, or PA obtained outside system |
| EXPIRED auth | Escalate ET-04 — possible PA amendment pending |

No auto-payment for PA-required procedures without PA confirmation.

### §10. Pre-deployment Checklist

- [ ] System name and base URL confirmed; DISCOVERY_REQUIRED values replaced
- [ ] Read-only API credential provisioned as `PRIOR_AUTH_API_KEY`
- [ ] **Write exclusion test (mandatory):** Attempt POST/PATCH to prior auth system using `PRIOR_AUTH_API_KEY` → confirm 403 response; document test result
- [ ] `PRIOR_AUTH_UNIT_TOLERANCE_PCT` default value (10%) confirmed with VP Operations and CMO as acceptable tolerance; configurable parameter documented
- [ ] Prior auth requirement table confirmed: which procedure codes require prior auth under which plans? This table is used by T-06 to determine whether NOT_FOUND is an ET-04 trigger
- [ ] P95 latency test: ≤ 5s under expected load
- [ ] ET-04 escalation test: query for a PA-required procedure with `NOT_FOUND` response → confirm ET-04 fires → confirm EscalationPacket delivered to S-09
- [ ] Partial-match test: query returning `PRESENT_PARTIAL_MATCH` with units_variance > `PRIOR_AUTH_UNIT_TOLERANCE_PCT` → confirm ET-04 escalation

---

## IC-S-14 — Claims History Database

**Used by:** WS2 only (T-B-05 claims history retrieval for PhysicianReviewPacket assembly)
**Access type:** Read only (on-demand per clinical claim during WS2 packet assembly)

### §1. Integration Purpose

WS2 T-B-05 retrieves the member's prior claims history for the relevant diagnosis range and a configurable lookback period. This history is included in the PhysicianReviewPacket to give the reviewing physician context on the member's prior treatment and claim patterns.

**Not in scope for this contract:** Current-cycle claim data (that is in S-07 ClaimRecord); clinical notes from treating providers (S-13, SCOPE-OUT); prior auth history (S-04 contract, read by WS1).

**Relationship to S-07:** S-14 may be a read view or query interface on the same database as S-07 (claims management system). Confirm in discovery. If confirmed to be the same system, this contract is an addendum to IC-S-07 specifying the history query endpoint and data mapping — not a separate integration.

### §2. System Description

- **Assumed system name:** Greenfield Claims History Service (DISCOVERY_REQUIRED — likely a read-optimised view or reporting database derived from S-07; confirm whether it is the same system or a separate data store)
- **Base URL:** DISCOVERY_REQUIRED (`https://claimshistory.greenfield-internal.example/v1`; or a separate endpoint on S-07's base URL if the same system)
- **Operations:** GET (member claims history by diagnosis range and lookback period); read-only

### §3. Authentication and Authorisation

- **Method:** DISCOVERY_REQUIRED. Recommended: same service-account credential as S-07 with an additional read-scope on the history query endpoint, or a separate read-only key for the history endpoint.
- **Credential storage:** Agent secrets manager; key name `CLAIMS_HISTORY_API_KEY`
- **Scope:** Read-only; query scope limited to minimum necessary: `member_id` + relevant diagnosis code range + lookback period. No bulk export; no access to claims for other members.
- **PHI:** Historical claims contain PHI. Access is read-only, minimum necessary, and scoped to the clinical claim being assembled.

### §4. Endpoint Contracts

**Operation: Member claims history query**

```
GET /claims/history?member_id={member_id}&icd_chapter_prefix={prefix}&lookback_days={days}&limit=50
Authorization: Bearer {CLAIMS_HISTORY_API_KEY}
```

Query parameters:

| Parameter | Type | Required | Default | Notes |
|-----------|------|----------|---------|-------|
| `member_id` | string | Yes | — | Greenfield member ID |
| `icd_chapter_prefix` | string | Yes | — | ICD-10 chapter or range prefix (e.g., `M` for musculoskeletal, `I` for cardiovascular); limits query to relevant diagnosis range |
| `lookback_days` | integer | No | 365 | Configurable (`CLAIMS_HISTORY_LOOKBACK_DAYS`); default 365 |
| `limit` | integer | No | 50 | Pagination; max 100 per page |
| `cursor` | string | No | — | Pagination cursor for > 50 results |

**Success response (200 OK):**

```json
{
  "member_id": "GHS-MBR-4491023",
  "icd_chapter_prefix": "M",
  "lookback_days": 365,
  "query_date": "2025-03-15",
  "claims": [
    {
      "claim_id": "CLM-2024-08-00112",
      "date_of_service": "2024-08-14",
      "procedure_codes": ["99213"],
      "diagnosis_codes": ["M17.11", "M25.561"],
      "adjudication_status": "APPROVED",
      "payment_amount": 185.00,
      "provider_id": "1234567890"
    },
    {
      "claim_id": "CLM-2025-01-00034",
      "date_of_service": "2025-01-22",
      "procedure_codes": ["20610"],
      "diagnosis_codes": ["M17.11"],
      "adjudication_status": "APPROVED",
      "payment_amount": 210.00,
      "provider_id": "1234567890"
    }
  ],
  "total_results": 2,
  "next_cursor": null
}
```

**PhysicianReviewPacket.completeness_indicator and empty history:**
If S-14 returns an empty `claims` array (no history in the lookback period for this diagnosis range), this is a valid response — not a failure. The PhysicianReviewPacket.completeness_indicator marks the `claims_history` section as present but empty, and includes the lookback period in the packet so the physician knows the query was performed.

**Status codes:**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 200 | History returned (may be empty) | Populate PhysicianReviewPacket.claims_history section |
| 404 | Member not found | Log `CLAIMS_HISTORY_RETRIEVED` with `records_found = 0`; mark packet section as empty |
| 401 | Credential invalid | Suspend; ops alert |
| 429 | Rate limit | Queue; backoff |
| 503 | Unavailable | Retry once after 5s; if still unavailable → mark `claims_history` section as INTEGRATION_DEGRADED in packet; physician notified in packet; continue packet assembly without history |

**Worked example — WS2 packet assembly for knee arthroplasty clinical claim:**

Request:
```
GET /claims/history?member_id=GHS-MBR-4491023&icd_chapter_prefix=M&lookback_days=365&limit=50
Authorization: Bearer {CLAIMS_HISTORY_API_KEY}
```

Response: (as shown above — 2 prior musculoskeletal claims for this member)

WS2 populates `PhysicianReviewPacket.claims_history` with both records. `completeness_indicator` marks `claims_history = PRESENT`. AuditLogEntry: `action = CLAIMS_HISTORY_RETRIEVED`, `output_summary.records_found = 2`.

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 503 Unavailable | Yes | 1 | 5s fixed | Graceful degrade — mark `claims_history` as INTEGRATION_DEGRADED; include note in packet; physician retrieves manually |
| Timeout > 5s | Yes | 1 | None | Treat as 503 |
| 429 Rate limit | Yes | 3 | Exponential: 1s, 2s, 4s | Queue; ops alert |

Unlike S-02 (eligibility) and S-04 (prior auth), S-14 unavailability does not block packet delivery — it degrades packet completeness. The claim continues to PHYSICIAN_REVIEWING with a note that history is unavailable.

### §6. Rate Limits and Throttling

- **Call frequency:** 1 call per clinical claim during WS2 packet assembly; ~35% of 2,000 claims/day = ~700 clinical claims/day = ~1 call/min average; peak burst ~10 calls/min
- **Minimum required capacity:** ≥ 20 calls/min per agent instance
- **Rate limit:** DISCOVERY_REQUIRED. Internal database queries; typically ≥ 100 calls/min supportable.

### §7. Data Mapping

| Internal field | External API field | Direction | Notes |
|----------------|-------------------|-----------|-------|
| `ClaimRecord.member_id` | `member_id` (query param) | Agent → System | |
| *(derived from claim's diagnosis codes)* | `icd_chapter_prefix` (query param) | Agent → System | Chapter prefix extracted from primary diagnosis code (e.g., `M17.11` → `M`) |
| `CLAIMS_HISTORY_LOOKBACK_DAYS` (config) | `lookback_days` (query param) | Agent → System | Configurable; default 365 |
| *(response)* | `claims[].claim_id` | System → Agent | Included in packet as reference |
| *(response)* | `claims[].date_of_service` | System → Agent | |
| *(response)* | `claims[].procedure_codes` | System → Agent | |
| *(response)* | `claims[].diagnosis_codes` | System → Agent | |
| *(response)* | `claims[].adjudication_status` | System → Agent | APPROVED / REJECTED / PENDING — physician context |
| *(response)* | `claims[].payment_amount` | System → Agent | Informational for physician; not used in payment calculation |
| *(response)* | `total_results` | System → Agent | Logged in AuditLogEntry.output_summary |

No writes to S-14.

### §8. State Synchronisation

- **Pattern:** On-demand at T-B-05 execution during WS2 packet assembly; no caching
- **Relationship to S-07:** If S-14 is a read view on S-07, the same credential rotation and BAA applies. Confirm in discovery.

### §9. Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| S-14 unavailable (503) | Graceful degrade — `claims_history` marked INTEGRATION_DEGRADED in packet; physician notified; packet delivered without history section |
| Empty history (200 with no records) | Not a failure — valid response; packet section marked present but empty with lookback period noted |
| Query too broad (> 100 results) | Paginate; max 100 per page; include summary counts in packet if pagination limit is reached |

### §10. Pre-deployment Checklist

- [ ] Confirm whether S-14 is the same system as S-07 or a separate data store; if same, integrate as an endpoint on the IC-S-07 contract
- [ ] System name and base URL confirmed; DISCOVERY_REQUIRED values replaced
- [ ] Read-only API credential provisioned as `CLAIMS_HISTORY_API_KEY`
- [ ] `CLAIMS_HISTORY_LOOKBACK_DAYS` confirmed with ops team (default 365 appropriate for clinical review context?)
- [ ] `icd_chapter_prefix` query scope confirmed: does the system support ICD-10 chapter prefix filtering, or does it return all history for the member? If all history, WS2 filters client-side (acceptable for < 10 years of records; confirm data volume)
- [ ] Graceful degrade test: simulate S-14 503 → confirm packet assembled without claims_history section → confirm `INTEGRATION_DEGRADED` flag in packet → confirm `CLAIMS_HISTORY_RETRIEVED` AuditLogEntry with `records_found = 0` and `degradation_reason = S14_UNAVAILABLE`
- [ ] PHI access scope test: confirm credential cannot query history for a member_id not associated with a ClaimRecord currently in WS2 processing

---

*Pass 7d complete. Pass 7e appends IC-S-09 and IC-S-11.*

---

## IC-S-09 — HITL Exception Management System

**Used by:** Both WS1 (T-12 exception escalation for ET-03 through ET-07) and WS2 (T-B-09 exception escalation)
**Access type:** Read-Write (WS1/WS2 write EscalationPackets; poll for resolution tokens)

### §1. Integration Purpose

When either agent triggers an exception escalation (ET-series events), it writes an EscalationPacket to S-09 for delivery to the HITL exception processor queue. The agent then polls S-09 for a resolution token. When the exception processor resolves the escalation, the agent reads the resolution decision and uses it to determine the next ClaimRecord state transition.

**WS1 writes escalations for:** eligibility discrepancy (ET-03), prior auth mismatch (ET-04), coding plausibility (ET-05), contract exception (ET-06), audit failure (ET-07).
**WS2 writes escalations for:** routing verification conflict (ET-B-01), packet delivery failure (ET-B-03), and SLA breach re-escalation (ET-B-04).

**Note on S-07 relationship:** S-09 may be a workflow module within S-07 (claims management platform). Confirm in discovery. If it is the same system, this contract describes the exception queue endpoints specifically — distinct from the ClaimRecord state write endpoints in IC-S-07.

**Not in scope:** Physician clinical review queue (S-08, SCOPE-OUT — clinical path; different from exception processor queue); payment processing (S-11); outbound rejection notices (S-12).

### §2. System Description

- **Assumed system name:** Greenfield HITL Exception Management System (DISCOVERY_REQUIRED — may be a module of S-07 or a standalone workflow tool)
- **Base URL:** DISCOVERY_REQUIRED (`https://exceptions.greenfield-internal.example/v1`; or a queue endpoint on S-07's base URL if same system)
- **Operations:** POST (write EscalationPacket); GET (poll for resolution); no DELETE

### §3. Authentication and Authorisation

- **Method:** DISCOVERY_REQUIRED. Recommended: service-account API key per agent (WS1 key, WS2 key); read-write scope on exception queue only.
- **Credential storage:** Agent secrets manager; WS1 key name `EXCEPTION_MGMT_API_KEY_WS1`, WS2 key name `EXCEPTION_MGMT_API_KEY_WS2`
- **Scope:** Write (EscalationPacket creation); Read (resolution token poll for the agent's own escalations only). Agents must not read another agent's escalations.
- **PHI:** EscalationPackets contain claim PHI; access limited to claims assigned to this agent instance.

### §4. Endpoint Contracts

**Operation A: Write EscalationPacket**

```
POST /escalations
Content-Type: application/json
Authorization: Bearer {EXCEPTION_MGMT_API_KEY_WS1|WS2}
```

Required fields:

| Field | Type | Constraint |
|-------|------|-----------|
| `escalation_id` | UUID | Generated by agent; used for idempotency and resolution polling |
| `claim_id` | UUID | ClaimRecord.id |
| `escalation_trigger_id` | string | Must match a defined ET-ID from D4a or D4b spec (e.g., `ET-03`, `ET-B-01`) |
| `escalation_reason` | enum | See reason enum below |
| `trigger_signal_values` | JSON object | Specific numeric/enum values that caused the trigger (not prose) |
| `required_resolution` | enum | See resolution options enum below |
| `routing_queue` | enum | `EXCEPTION_PROCESSOR` (WS1 ET-03 through ET-07) or `CODING_SPECIALIST` (ET-05) or `CONTRACT_OWNER` (ET-06 with amendment_flag) |
| `sla_hours` | integer | Hours until SLA breach; from escalation trigger table in D4a/D4b |
| `assembled_by_agent` | string | `agent_id` of the assembling agent |
| `timestamp` | ISO 8601 UTC | Moment of escalation |
| `audit_log_entry_id` | UUID | S-10 AuditLogEntry ID for `ESCALATION_TRIGGERED` action; written before this call |

Optional:
- `claim_record_snapshot`: JSON snapshot of ClaimRecord at time of escalation (recommended for exception processor context)
- `borderline_confidence_flag`: boolean (ET-02 only)

**`escalation_reason` enum (exhaustive):**
`ELIGIBILITY_DISCREPANCY`, `PRIOR_AUTH_MISMATCH`, `PRIOR_AUTH_NOT_FOUND`, `CODING_IMPLAUSIBILITY`, `CONTRACT_EXCEPTION`, `CONTRACT_EXCEPTION_LOOKUP_UNAVAILABLE`, `AUDIT_LOG_FAILURE`, `GOVERNANCE_VIOLATION`, `ROUTING_VERIFICATION_CONFLICT`, `PACKET_DELIVERY_FAILURE`, `SLA_BREACH_REESCALATION`

**`required_resolution` enum (per escalation trigger — constrained, not free-text):**

| Escalation | Permitted resolution values |
|------------|---------------------------|
| ET-03 (eligibility) | `ELIGIBILITY_CONFIRMED` \| `ELIGIBILITY_REJECTED` \| `RETURN_TO_SUBMITTER` |
| ET-04 (prior auth) | `PRIOR_AUTH_CONFIRMED` \| `PRIOR_AUTH_DENIED` \| `RETURN_TO_SUBMITTER` |
| ET-05 (coding) | `CODING_CONFIRMED_PLAUSIBLE` \| `CODING_CONFIRMED_IMPLAUSIBLE` \| `RETURN_TO_SUBMITTER` |
| ET-06 (contract) | `EXCEPTION_RESOLVED` \| `CLAIM_REJECTED` \| `RETURN_TO_SUBMITTER` |
| ET-07 (audit write failure — `trigger_type = AUDIT_FAILURE`) | `RECONSTRUCT_AND_CONTINUE` \| `REJECT_CLAIM` \| `ESCALATE_TO_COMPLIANCE` |
| ET-07 (governance hard-stop — `trigger_type = GOVERNANCE_VIOLATION`) | `INVESTIGATE_STATE_MACHINE` \| `REJECT_CLAIM` \| `ESCALATE_TO_COMPLIANCE` |
| ET-B-01 (routing conflict) | `ROUTING_CONFIRMED_ADMIN` \| `ROUTING_CONFIRMED_CLINICAL` |

Free-text resolutions are not accepted. If the system returns a resolution_decision not in the permitted enum for the escalation trigger, the agent logs a defect and escalates to ops.

**Success response (201 Created):**
```json
{
  "escalation_id": "esc-a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "status": "QUEUED",
  "sla_deadline": "2025-03-15T18:23:07.000Z",
  "queue": "EXCEPTION_PROCESSOR"
}
```

**Operation B: Poll for resolution**

```
GET /escalations/{escalation_id}/resolution
Authorization: Bearer {EXCEPTION_MGMT_API_KEY_WS1|WS2}
```

**Response — resolved:**
```json
{
  "escalation_id": "esc-a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "status": "RESOLVED",
  "resolution_decision": "ELIGIBILITY_CONFIRMED",
  "resolved_by": "ep-user-liu-ops-001",
  "resolution_timestamp": "2025-03-15T16:44:22.000Z",
  "resolution_note": "Member verified active via phone confirmation with member services"
}
```

**Response — pending (SLA not breached):**
```json
{
  "escalation_id": "esc-a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "status": "PENDING",
  "sla_deadline": "2025-03-15T18:23:07.000Z",
  "minutes_remaining": 99
}
```

**Response — SLA breached:**
```json
{
  "escalation_id": "esc-a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "status": "SLA_BREACHED",
  "sla_deadline": "2025-03-15T18:23:07.000Z",
  "breach_logged_at": "2025-03-15T18:23:08.000Z"
}
```

On `SLA_BREACHED`: agent re-sends EscalationPacket with `escalation_reason = SLA_BREACH_REESCALATION` and `URGENT` flag; supervisor notified per D4a/D4b escalation table.

**Poll interval:** `ESCALATION_POLL_INTERVAL_SECONDS` (configurable; default 300s / 5 min). Do not poll more frequently than every 60s.

**Status codes:**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 201 | Escalation queued | Record `escalation_id`; begin polling at configured interval |
| 200 | Resolution retrieved | Process `resolution_decision` per escalation logic |
| 404 | Escalation not found | Log defect; ops alert; re-submit EscalationPacket |
| 401 | Credential invalid | Suspend; ops alert |
| 503 | System unavailable | Retry POST/GET with exponential backoff; claim remains in PENDING_HITL_EXCEPTION state (not lost) |

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 503 (write) | Yes | 3 | Exponential: 5s, 10s, 20s | Queue EscalationPacket locally; retry every 60s; claim stays in PENDING_HITL_EXCEPTION |
| 503 (poll) | Yes | 3 | Exponential: 5s, 10s, 20s | Resume polling on recovery; claim state unchanged |
| 400 Invalid resolution enum | No | 0 | N/A | Log defect; ops alert; require manual resolution |
| Unexpected resolution_decision value | No | 0 | N/A | Log defect; ops alert; do not advance claim |

### §6. Rate Limits and Throttling

- **Write volume:** ~10–15% of 2,000 claims/day escalated = ~200–300 EscalationPackets/day
- **Poll volume:** ~200–300 active escalations × poll every 5 min = ~40–60 poll calls/min at peak open queue depth
- **Minimum required capacity:** ≥ 100 calls/min (write + poll combined)
- **Rate limit:** DISCOVERY_REQUIRED.

### §7. Data Mapping

**Write (EscalationPacket → S-09):**

| Internal field | External API field | Direction |
|----------------|-------------------|-----------|
| `EscalationPacket.id` | `escalation_id` | Agent → System |
| `EscalationPacket.claim_id` | `claim_id` | Agent → System |
| `EscalationPacket.escalation_trigger_id` | `escalation_trigger_id` | Agent → System |
| `EscalationPacket.escalation_reason` | `escalation_reason` | Agent → System |
| `EscalationPacket.trigger_signal_values` | `trigger_signal_values` | Agent → System |
| `EscalationPacket.required_resolution` | `required_resolution` | Agent → System |
| `EscalationPacket.routing_queue` | `routing_queue` | Agent → System |
| `EscalationPacket.response_sla_hours` | `sla_hours` | Agent → System |
| `agent_id` | `assembled_by_agent` | Agent → System |
| `AuditLogEntry.id` (ESCALATION_TRIGGERED) | `audit_log_entry_id` | Agent → System |

**Read (resolution token → agent):**

| External API field | Internal usage | Direction |
|--------------------|----------------|-----------|
| `resolution_decision` | Drives next ClaimRecord state transition | System → Agent |
| `resolved_by` | Written to AuditLogEntry.human_id | System → Agent |
| `resolution_timestamp` | Written to AuditLogEntry.timestamp | System → Agent |
| `status` | `RESOLVED` / `PENDING` / `SLA_BREACHED` triggers agent logic | System → Agent |

### §8. State Synchronisation

- **Pattern:** Write EscalationPacket once; poll for resolution at configurable interval until `status = RESOLVED` or `SLA_BREACHED`
- **Claim state during polling:** ClaimRecord remains in `PENDING_HITL_EXCEPTION`; WS1 does not process it further until resolution received
- **Resolution → state transition:** Agent reads `resolution_decision`, determines next ClaimRecord state (e.g., `ELIGIBILITY_CONFIRMED` → resume from ADMIN_VALIDATING; `ELIGIBILITY_REJECTED` → REJECTED), writes S-10 audit entry, then writes S-07 state transition

### §9. Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| S-09 down on write | Queue EscalationPacket locally; claim stays in PENDING_HITL_EXCEPTION; retry every 60s; ops alert after 10 min |
| S-09 down on poll | Resume polling on recovery; no claim state change; SLA clock continues running |
| Unexpected resolution enum value | Log defect; ops alert; manual resolution required |

### §10. Pre-deployment Checklist

- [ ] Confirm whether S-09 is a module of S-07 or an independent system; if same, integrate as exception queue endpoints on IC-S-07 contract
- [ ] System name and base URL confirmed; DISCOVERY_REQUIRED values replaced
- [ ] WS1 and WS2 credentials provisioned separately (`EXCEPTION_MGMT_API_KEY_WS1`, `EXCEPTION_MGMT_API_KEY_WS2`); cross-access test: WS1 credential cannot read WS2 escalations
- [ ] Resolution enum values confirmed with exception processor team — they must match the permitted enum in §4; any value not in the enum is a defect
- [ ] Poll interval `ESCALATION_POLL_INTERVAL_SECONDS` configured (default 300s); confirm minimum 60s floor
- [ ] SLA breach test: create escalation with `sla_hours = 0` → confirm `SLA_BREACHED` status on next poll → confirm re-escalation with `URGENT` flag → confirm supervisor notification
- [ ] S-09 unavailability test: simulate 503 on write → confirm EscalationPacket queued locally → confirm claim stays in PENDING_HITL_EXCEPTION → confirm write succeeds on recovery

---

## IC-S-11 — Payment Processing System

**Used by:** WS1 only (T-09 payment instruction write for ADMIN_CLEARED claims after fee schedule lookup)
**Access type:** Write only (push to payment queue); no read access granted

### §1. Integration Purpose

WS1 T-09 writes a payment instruction to S-11 after all upstream pipeline gates have passed and `payment_amount` has been calculated from S-05. Payment execution (disbursement to provider) is S-11's responsibility — WS1 writes the instruction and does not confirm disbursement completion.

**Agent autonomy level for this action:** `AGENT_ACTS, HUMAN_NOTIFIED_AFTER` per D3 autonomy matrix. This is the highest-autonomy action in the WS1 pipeline. It is valid only when all upstream gates have been confirmed in the current pipeline run — not just when `ClaimRecord.state = ADMIN_CLEARED`.

**Not in scope:** Payment confirmation or reconciliation; clinical claim payments (clinical claims reach APPROVED only after physician sign-off, which triggers a separate downstream payment process not in agent scope); member billing or cost-sharing collection.

### §2. System Description

- **Assumed system name:** Greenfield Payment Processing System (DISCOVERY_REQUIRED — may be an internal payment disbursement platform or a connection to an external payment network)
- **Base URL:** DISCOVERY_REQUIRED (`https://payments.greenfield-internal.example/v1`)
- **Operations:** POST (write payment instruction to queue); no read access
- **Processing model:** WS1 writes to a payment instruction queue; S-11 picks up and executes disbursement on its own schedule (batch window or real-time depending on S-11 architecture). Agent does not receive a disbursement confirmation.

### §3. Authentication and Authorisation

- **Method:** DISCOVERY_REQUIRED. Recommended: service-account API key (write-only scope). No read access to payment records.
- **Credential storage:** Agent secrets manager; key name `PAYMENT_API_KEY`
- **Scope:** Write-only to the payment instruction queue. No read access. No access to payment records, bank routing details, or disbursement confirmations.
- **Financial risk note:** Write-only scope must be technically enforced at the API level. The agent must not be able to query payment records — this prevents overpayment auditing being done by the agent itself rather than by a dedicated financial controls process.

### §4. Endpoint Contracts

**Pre-condition check (T-09 — run before every payment instruction write):**

T-09 re-reads the full ClaimRecord from S-07 at the moment of the payment write and validates all upstream gates. The gate states from earlier in the pipeline run are not trusted — they are re-verified at T-09 execution time:

| Gate | Re-verified field | Required value |
|------|-----------------|----------------|
| Eligibility | ClaimRecord.eligibility_status (or last T-02 result in session) | `ACTIVE` |
| Code validity | T-04 result in session | `ALL_CODES_VALID` |
| Code plausibility | T-05 result in session | `PLAUSIBLE` or `TOLERANCE_APPLIED` |
| Prior auth | T-06/T-07 result in session | `CONFIRMED` or `NOT_REQUIRED` |
| Clinical routing | ClaimRecord.state | Must be `ADMIN_CLEARED`; NOT `PENDING_PHYSICIAN_REVIEW` — **FM-A-5 hard stop** |

If any gate re-verification fails at T-09 time: log `GOVERNANCE_HARD_STOP_TRIGGERED`; halt payment write; escalate ET-07 equivalent; claim re-enters PENDING_HITL_EXCEPTION.

**Operation: Write payment instruction**

```
POST /payment-instructions
Content-Type: application/json
Authorization: Bearer {PAYMENT_API_KEY}
```

Required fields:

| Field | Type | Constraint |
|-------|------|-----------|
| `instruction_id` | UUID | Generated by agent; idempotency key |
| `claim_id` | UUID | ClaimRecord.id |
| `external_claim_id` | string | Clearinghouse reference for reconciliation |
| `provider_npi` | string | 10-digit NPI of payee |
| `payment_amount` | decimal | USD; 2 decimal places; > 0.00; sourced from S-05 `payer_responsibility` |
| `procedure_codes` | array of strings | CPT codes from claim; for remittance advice |
| `date_of_service` | ISO 8601 date | |
| `payer_id` | string | For S-11 routing to correct payment account |
| `remittance_codes` | array of strings | X12 Claim Adjustment Reason Codes for remittance advice |
| `approval_token_id` | UUID | The AuditLogEntry.id for the `PAYMENT_APPROVED` action in S-10 — S-11 can verify the audit trail independently |
| `audit_log_entry_id` | UUID | Same as `approval_token_id`; redundant for explicitness; the S-10 entry must exist before this write |

**Success response (202 Accepted):**

```json
{
  "instruction_id": "pi-c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
  "status": "QUEUED",
  "queued_at": "2025-03-15T14:23:08.000Z"
}
```

WS1 does not poll for disbursement confirmation. `QUEUED` is the terminal status from WS1's perspective.

**Status codes:**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 202 | Instruction queued | Write `PAYMENT_APPROVED` to S-10; transition ClaimRecord.state to APPROVED |
| 400 | Missing field or invalid format | Do NOT retry — log defect; halt payment; ops alert; claim to PENDING_HITL_EXCEPTION |
| 401 | Credential invalid | Suspend; ops alert |
| 409 | Duplicate `instruction_id` | Treat as accepted (idempotent); log warning; transition ClaimRecord to APPROVED |
| 503 | System unavailable | Queue payment instruction locally; retry every 60s; ops alert after 10 min; ClaimRecord state holds at PAYMENT_CALCULATING until instruction confirmed queued |

**Worked example — standard administrative claim payment:**

Request:
```json
POST /payment-instructions
{
  "instruction_id": "pi-c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
  "claim_id": "b9e2a1f4-3c7d-4e8b-a021-6f5c4d3e2f1a",
  "external_claim_id": "CLH-2025-0315-00421",
  "provider_npi": "1234567890",
  "payment_amount": 148.00,
  "procedure_codes": ["99213"],
  "date_of_service": "2025-03-10",
  "payer_id": "GHS-PLAN-GOLD-2025",
  "remittance_codes": ["PR-2"],
  "approval_token_id": "a3f7c2d1-8b4e-4f9a-bc12-5e6d7f8a9b0c",
  "audit_log_entry_id": "a3f7c2d1-8b4e-4f9a-bc12-5e6d7f8a9b0c"
}
```

Response:
```json
HTTP 202
{
  "instruction_id": "pi-c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f",
  "status": "QUEUED",
  "queued_at": "2025-03-15T14:23:08.000Z"
}
```

Post-write: AuditLogEntry written with `action = PAYMENT_APPROVED`, `output_summary.payment_amount = 148.00`. ClaimRecord.state transitions to APPROVED.

**Worked example — FM-A-5 hard stop (payment bypassing physician review):**

Pre-condition check at T-09 detects: `ClaimRecord.state = PENDING_PHYSICIAN_REVIEW` (not `ADMIN_CLEARED`).
Action: **Payment write aborted.** AuditLogEntry written: `action = GOVERNANCE_HARD_STOP_TRIGGERED`, `output_summary.reason = FM_A5_PAYMENT_BYPASS_ATTEMPTED`, `compliance_flags = ["URAC_NCQA_VIOLATION_PREVENTED"]`. Claim to PENDING_HITL_EXCEPTION. Ops and CMO alert.

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 503 Unavailable | Yes (with local queue) | Indefinite | Fixed 60s | Ops alert after 10 min; ClaimRecord holds at PAYMENT_CALCULATING |
| Timeout > 5s | Yes | 1 | None | Treat as 503 |
| 429 Rate limit | Yes | 3 | Exponential: 2s, 4s, 8s | Queue locally; ops alert |
| 400 Validation failure | No | 0 | N/A | Log defect; halt; ops alert |
| T-09 pre-condition failure | No | 0 | N/A | FM-A-5 hard stop; `GOVERNANCE_HARD_STOP_TRIGGERED`; PENDING_HITL_EXCEPTION |

### §6. Rate Limits and Throttling

- **Write volume:** ~65% of 2,000 claims/day passing admin path = ~1,300 payment instructions/day = ~1.8 writes/min average; peak burst ~15 writes/min
- **Minimum required capacity:** ≥ 30 writes/min per agent instance
- **Rate limit:** DISCOVERY_REQUIRED. Payment systems with batch windows may have restricted real-time write capacity; confirm whether S-11 is real-time queue or batch file.

### §7. Data Mapping

| Internal field | External API field | Direction | Notes |
|----------------|-------------------|-----------|-------|
| `ClaimRecord.id` | `claim_id` | Agent → System | |
| `ClaimRecord.external_claim_id` | `external_claim_id` | Agent → System | Clearinghouse reference |
| `ClaimRecord.provider_npi` | `provider_npi` | Agent → System | 10-digit NPI |
| `payment_amount` (from S-05 `payer_responsibility`) | `payment_amount` | Agent → System | USD, 2 decimal places |
| `ClaimRecord.procedure_codes` | `procedure_codes` | Agent → System | For remittance advice |
| `ClaimRecord.date_of_service` | `date_of_service` | Agent → System | |
| `ClaimRecord.payer_id` | `payer_id` | Agent → System | |
| *(derived from rejection code reference)* | `remittance_codes` | Agent → System | X12 CARC for remittance |
| `AuditLogEntry.id` (PAYMENT_APPROVED) | `approval_token_id`, `audit_log_entry_id` | Agent → System | S-11 can verify against S-10 |
| *(response)* | `instruction_id` | System → Agent | Stored in AuditLogEntry.output_summary |
| *(response)* | `status` | System → Agent | Must equal `QUEUED` |

No reads from S-11.

### §8. State Synchronisation

- **Pattern:** Write-on-event at T-09 completion; no polling; no caching
- **ClaimRecord.state timing:** State transitions to APPROVED only after 202 received from S-11. If S-11 returns 503, ClaimRecord stays at PAYMENT_CALCULATING until 202 confirmed.
- **Disbursement:** S-11 picks up queued instruction and executes on its own schedule; WS1 has no visibility into disbursement completion.

### §9. Failure Modes and Fallbacks

| Failure | Fallback |
|---------|---------|
| S-11 unavailable | Queue payment instruction locally; retry every 60s; ClaimRecord holds at PAYMENT_CALCULATING; ops alert after 10 min |
| T-09 pre-condition gate failure | FM-A-5 hard stop — abort payment; `GOVERNANCE_HARD_STOP_TRIGGERED`; PENDING_HITL_EXCEPTION |
| Validation failure (400) | Log defect; ops alert; manual payment required |

### §10. Pre-deployment Checklist

- [ ] System name and base URL confirmed; DISCOVERY_REQUIRED values replaced
- [ ] Write-only API credential provisioned as `PAYMENT_API_KEY`; confirmed no read access — integration test: attempt GET on payment records → confirm 403 or 405
- [ ] S-11 processing model confirmed: real-time queue or batch window? If batch, confirm maximum latency between WS1 write and S-11 pickup (affects SLA planning)
- [ ] `payment_amount` format confirmed: USD with exactly 2 decimal places; confirm S-11 rejects > 2 decimal places (prevents rounding errors)
- [ ] FM-A-5 hard stop test (mandatory): provide a ClaimRecord in `PENDING_PHYSICIAN_REVIEW` state to T-09 → confirm payment write aborted → confirm `GOVERNANCE_HARD_STOP_TRIGGERED` AuditLogEntry written → confirm ClaimRecord transitions to PENDING_HITL_EXCEPTION → confirm ops alert
- [ ] T-09 pre-condition re-verification test: simulate a claim where one upstream gate result has changed between pipeline entry and T-09 execution → confirm T-09 detects the discrepancy and halts
- [ ] Duplicate instruction_id test: send same `instruction_id` twice → confirm 409 and second write treated as idempotent (no double-payment)
- [ ] S-11 unavailability test: simulate 503 → confirm local queue holds instruction → confirm ClaimRecord stays at PAYMENT_CALCULATING → confirm instruction delivered and ClaimRecord transitions to APPROVED on recovery

---

*Pass 7e complete. Pass 7f appends IC-S-07.*

---

## IC-S-07 — Claims Management System

**Used by:** Both WS1 (all state transitions for administrative path) and WS2 (all state transitions for clinical path)
**Access type:** Read-Write; the primary workflow state store for the entire adjudication pipeline

> **Read before finalising D4a §8 and D4b §8 enforcement mechanism statements.** The G-3 gap (§9 below) determines whether the URAC/NCQA compliance gate is system-enforced or procedure-dependent. Until G-3 is confirmed, enforcement is classified as procedure-dependent with a middleware guard recommendation. See §3 Sign-off Integrity Summary in `D4_integration_preamble.md`.

### §1. Integration Purpose

S-07 is the authoritative state store for every ClaimRecord in the adjudication pipeline. Both WS1 and WS2 read ClaimRecords, write state transitions, and write non-state field updates to this system on every pipeline step.

**WS1 uses S-07 for:** Polling for NORMALISED-state claims at T-01 (batch intake); reading ClaimRecord at each pipeline task; writing state transitions at every T-step; writing clinical_classification_id (T-08); writing payment_amount and rejection_codes (T-09/T-11); writing HITL queue assignments.

**WS2 uses S-07 for:** Reading ClaimRecord at T-B-01 (startup verification that claim is in PENDING_PHYSICIAN_REVIEW); writing state transitions through CLINICAL_PACKET_ASSEMBLY → PHYSICIAN_REVIEWING → APPROVED; writing physician_packet_id and hitl_disposition.

**Not in scope:** Physician review queue (S-08, SCOPE-OUT — not part of S-07 even if it may share the same platform); exception management queue (S-09 — separate contract; may be a module of the same platform); audit log writes (S-10 — separate contract); fee schedule or eligibility data (separate systems).

### §2. System Description

- **Assumed system name:** Greenfield Claims Management Platform (DISCOVERY_REQUIRED — the function is named in the scenario as "claims processing team"; platform name is an assumption)
- **Base URL:** DISCOVERY_REQUIRED (`https://claims.greenfield-internal.example/v1`)
- **Operations:** Five operations in scope; see §4
- **State machine:** 16-state ClaimRecord lifecycle (see §4 state transition contract); enforceability at API layer is G-3 gap — see §9

### §3. Authentication and Authorisation

- **Method:** DISCOVERY_REQUIRED. Recommended: per-agent service-account API key; separate keys for WS1 and WS2 to enable field-level write scope control.
- **WS1 credential storage:** Secrets manager; key name `CLAIMS_MGMT_API_KEY_WS1`
- **WS2 credential storage:** Secrets manager; key name `CLAIMS_MGMT_API_KEY_WS2`
- **Agent-writable fields — WS1:** `state`, `clinical_classification_id`, `rejection_codes`, `payment_amount`, `hitl_disposition`, `hitl_queue_type`, `hitl_assigned_to`, `updated_by`, `updated_at`
- **Agent-writable fields — WS2:** `state` (WS2-owned transitions only — see §4), `clinical_classification_id_ws2`, `physician_packet_id`, `hitl_disposition`, `updated_by`, `updated_at`
- **Fields neither agent may write:** `member_id`, `provider_npi`, `procedure_codes`, `diagnosis_codes`, `date_of_service`, `payer_id`, `external_claim_id`, `created_at` (immutable claim identity fields)
- **PHI:** ClaimRecord contains PHI; minimum necessary field access; write scope limited to adjudication-relevant fields only; no bulk delete, no schema modification access

### §4. Endpoint Contracts

**Operation A — ClaimRecord read (single record)**

```
GET /claims/{claim_id}
Authorization: Bearer {CLAIMS_MGMT_API_KEY_WS1|WS2}
```

Response: full ClaimRecord JSON including all fields (read scope covers all fields for assigned claims).

Used by: WS1 at every pipeline task to read current state; WS2 T-B-01 at startup to verify claim is in PENDING_PHYSICIAN_REVIEW.

**Status codes:**

| HTTP Status | Meaning | Agent action |
|-------------|---------|--------------|
| 200 | Record found | Process ClaimRecord |
| 404 | Claim not found | Log defect; ops alert — a claim should never be missing once in pipeline |
| 401 | Credential invalid | Suspend; ops alert |
| 503 | Unavailable | Retry 2× with 5s backoff; if still unavailable → circuit breaker; claim-level queuing; ops alert |

---

**Operation B — ClaimRecord state transition write (critical operation)**

```
PATCH /claims/{claim_id}/state
Content-Type: application/json
Authorization: Bearer {CLAIMS_MGMT_API_KEY_WS1|WS2}
{
  "from_state": "string — REQUIRED — current state for optimistic locking",
  "to_state":   "string — REQUIRED — target state from defined state machine",
  "updated_by": "string — REQUIRED — agent_id (agent-initiated) or human_id (HITL-initiated)",
  "audit_log_entry_id": "UUID — REQUIRED — S-10 entry for this transition; must exist before this call"
}
```

**`audit_log_entry_id` ordering requirement:** The S-10 AuditLogEntry for the action that produced this state transition must be written and confirmed `COMMITTED` BEFORE this PATCH is issued. If S-10 write fails (ET-07), this PATCH must not be issued.

**`from_state` optimistic locking:** The system must reject the PATCH with 409 Conflict if `ClaimRecord.state ≠ from_state` at the time of the write. This prevents concurrent writes from producing inconsistent state. If 409 received: agent re-reads ClaimRecord state (Operation A), determines whether a retry is valid, and proceeds or escalates.

**Expected 409 response body (desired system behaviour — G-3):**

```json
{
  "error_code": "INVALID_STATE_TRANSITION",
  "current_state": "PENDING_PHYSICIAN_REVIEW",
  "requested_state": "PAYMENT_CALCULATING",
  "message": "Transition from PENDING_PHYSICIAN_REVIEW to PAYMENT_CALCULATING is not permitted"
}
```

**WS1-owned state transitions (agent may only write these — any other from/to combination is a defect):**

| From state | To state | Trigger |
|-----------|---------|---------|
| `NORMALISED` | `ADMIN_VALIDATING` | T-01 intake |
| `ADMIN_VALIDATING` | `ROUTING` | T-02 through T-07 all pass |
| `ADMIN_VALIDATING` | `PENDING_HITL_EXCEPTION` | ET-03, ET-04, ET-05, ET-07 |
| `ROUTING` | `ADMIN_CLEARED` | T-08 ADMIN classification above threshold |
| `ROUTING` | `PENDING_PHYSICIAN_REVIEW` | T-08 CLINICAL/UNCERTAIN or below-threshold ADMIN |
| `ADMIN_CLEARED` | `PAYMENT_CALCULATING` | T-09 starts fee schedule lookup |
| `ADMIN_CLEARED` | `PENDING_HITL_EXCEPTION` | ET-07 audit write failure before ADMIN_CLEARED → PAYMENT_CALCULATING transition |
| `PAYMENT_CALCULATING` | `APPROVED` | T-09 fee schedule confirmed, payment instruction queued |
| `PAYMENT_CALCULATING` | `PENDING_HITL_EXCEPTION` | T-09 fee schedule failure (ET-06) |
| `PENDING_HITL_EXCEPTION` | `ROUTING` | Exception processor resolves; claim returns to routing stage |
| `PENDING_HITL_EXCEPTION` | `PAYMENT_CALCULATING` | Exception processor resolves ET-06 contract exception; claim resumes payment calculation |
| `ADMIN_VALIDATING` | `REJECTED` | T-02/T-04/T-05 deterministic rejection |
| `PENDING_HITL_EXCEPTION` | `ADMIN_VALIDATING` | Exception processor resolves ELIGIBILITY_CONFIRMED (re-enters pipeline) |
| `PENDING_HITL_EXCEPTION` | `REJECTED` | Exception processor resolves ELIGIBILITY_REJECTED / CLAIM_REJECTED |
| `APPROVED` | `CLOSED` | Downstream process closes after payment processed |
| `REJECTED` | `CLOSED` | Downstream process closes after rejection notice delivered |

**WS2-owned state transitions:**

| From state | To state | Trigger |
|-----------|---------|---------|
| `PENDING_PHYSICIAN_REVIEW` | `CLINICAL_PACKET_ASSEMBLY` | T-B-02 routing verification confirms CLINICAL; CalibrationRecord validated |
| `CLINICAL_PACKET_ASSEMBLY` | `PHYSICIAN_REVIEWING` | T-B-07 packet delivered to S-08 |
| `PHYSICIAN_REVIEWING` | `APPROVED` | Physician determination APPROVED (human_id non-null — hard stop) |
| `PHYSICIAN_REVIEWING` | `REJECTED` | Physician determination REJECTED (human_id non-null) |
| `PHYSICIAN_REVIEWING` | `PENDING_ADDITIONAL_INFO` | Physician requests more information |
| `PENDING_ADDITIONAL_INFO` | `CLINICAL_PACKET_ASSEMBLY` | Additional info received; new packet assembled |
| `PHYSICIAN_REVIEWING` | `PENDING_HITL_EXCEPTION` | WS2 ET-B series escalation |

**Forbidden transitions (FM-A-5 and FM-B-5 governance hard stops):**

| Forbidden from | Forbidden to | Reason |
|---------------|-------------|--------|
| `PENDING_PHYSICIAN_REVIEW` | `PAYMENT_CALCULATING` | FM-A-5: payment bypass without physician sign-off (URAC/NCQA violation) |
| `PENDING_PHYSICIAN_REVIEW` | `APPROVED` | FM-A-5: same |
| `PHYSICIAN_REVIEWING` | `APPROVED` with `human_id = null` | FM-B-5: physician determination without attributed human_id (URAC/NCQA violation) |
| `PENDING_PHYSICIAN_REVIEW` | `PHYSICIAN_REVIEWING` | WS2 only: must pass through CLINICAL_PACKET_ASSEMBLY |

If a forbidden transition is attempted: agent fires `GOVERNANCE_HARD_STOP_TRIGGERED`, writes AuditLogEntry, and does NOT issue the PATCH.

**State transition 409 → agent action:**

- Re-read ClaimRecord (Operation A)
- If current state is a valid predecessor to intended state, retry PATCH with updated `from_state`
- If current state is a forbidden predecessor (e.g., PENDING_PHYSICIAN_REVIEW when attempting payment write), fire `GOVERNANCE_HARD_STOP_TRIGGERED` and halt

---

**Operation C — ClaimRecord field write (non-state fields)**

```
PATCH /claims/{claim_id}/fields
Content-Type: application/json
Authorization: Bearer {CLAIMS_MGMT_API_KEY_WS1|WS2}
{
  "clinical_classification_id":     "UUID — WS1 T-08 only",
  "clinical_classification_id_ws2": "UUID — WS2 T-B-05 only",
  "rejection_codes":                ["array of strings — WS1 T-11 only"],
  "payment_amount":                 "decimal USD — WS1 T-09 only",
  "hitl_disposition":               "string — WS1 or WS2 after HITL resolution",
  "physician_packet_id":            "UUID — WS2 T-B-07 only",
  "hitl_queue_type":                "string — WS1 T-12 only",
  "hitl_assigned_to":               "string — WS1 T-12 only",
  "updated_by":                     "string — agent_id",
  "updated_at":                     "ISO 8601 UTC"
}
```

Only the fields listed above are writable via this endpoint. The system must reject writes to claim identity fields (`member_id`, `provider_npi`, etc.) with 400. Each agent's credential is scoped to its writable fields (see §3).

**WS1 writes to:** `clinical_classification_id`, `rejection_codes`, `payment_amount`, `hitl_disposition`, `hitl_queue_type`, `hitl_assigned_to`, `updated_by`, `updated_at`
**WS2 writes to:** `clinical_classification_id_ws2`, `physician_packet_id`, `hitl_disposition`, `updated_by`, `updated_at`

---

**Operation D — ClaimRecord batch query (WS1 T-01 intake polling)**

```
GET /claims?state=NORMALISED&limit=50&cursor={cursor_token}
Authorization: Bearer {CLAIMS_MGMT_API_KEY_WS1}
```

Used by WS1 when S-01 intake uses polling fallback (G-1 option 2). Returns paginated list of NORMALISED-state ClaimRecords for WS1 to pick up.

**Response (200 OK):**
```json
{
  "claims": [
    {
      "claim_id": "b9e2a1f4-3c7d-4e8b-a021-6f5c4d3e2f1a",
      "state": "NORMALISED",
      "created_at": "2025-03-15T08:12:33.000Z",
      "provider_npi": "1234567890",
      "member_id": "GHS-MBR-4491023"
    }
  ],
  "next_cursor": "eyJsYXN0X2lkIjoiYjllMmExZjQifQ==",
  "has_more": false
}
```

**Poll interval:** `NORMALISED_CLAIM_POLL_INTERVAL_SECONDS` (configurable; default 60s). WS1 picks up NORMALISED records and transitions them to ADMIN_VALIDATING (Operation B) before processing.

---

**Operation E — PhysicianReviewPacket write (WS2 T-B-07)**

```
POST /claims/{claim_id}/physician-packets
Content-Type: application/json
Authorization: Bearer {CLAIMS_MGMT_API_KEY_WS2}
{
  "packet_id":              "UUID — generated by WS2",
  "claim_id":               "UUID",
  "assembled_at":           "ISO 8601 UTC",
  "completeness_indicator": "float 0.00–1.00",
  "sections_present":       ["array of section names"],
  "sections_scope_out":     ["array of SCOPE-OUT section names — excluded from numerator and denominator"],
  "audit_log_entry_id":     "UUID — S-10 entry for PACKET_ASSEMBLED action"
}
```

**Response (201 Created):**
```json
{
  "packet_id": "pkt-3c4d5e6f-7a8b-9c0d-1e2f",
  "state": "ASSEMBLING",
  "stored_at": "2025-03-15T13:44:00.000Z"
}
```

---

**Worked example — state transition write: ROUTING → PENDING_PHYSICIAN_REVIEW (WS1 T-08, clinical routing):**

```json
PATCH /claims/b9e2a1f4-3c7d-4e8b-a021-6f5c4d3e2f1a/state
{
  "from_state": "ROUTING",
  "to_state": "PENDING_PHYSICIAN_REVIEW",
  "updated_by": "ws1-admin-adjudicator:v1.0.0:instance-003",
  "audit_log_entry_id": "e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b"
}
```

Response:
```json
HTTP 200
{
  "claim_id": "b9e2a1f4-3c7d-4e8b-a021-6f5c4d3e2f1a",
  "previous_state": "ROUTING",
  "current_state": "PENDING_PHYSICIAN_REVIEW",
  "updated_at": "2025-03-15T14:05:22.000Z"
}
```

**Worked example — 409 Conflict: optimistic lock mismatch (concurrent write detected):**

```json
PATCH /claims/b9e2a1f4-3c7d-4e8b-a021-6f5c4d3e2f1a/state
{
  "from_state": "ROUTING",
  "to_state": "ADMIN_CLEARED",
  "updated_by": "ws1-admin-adjudicator:v1.0.0:instance-003",
  "audit_log_entry_id": "f6a7b8c9-d0e1-2f3a-4b5c-6d7e8f9a0b1c"
}
```

Response:
```json
HTTP 409
{
  "error_code": "INVALID_STATE_TRANSITION",
  "current_state": "PENDING_HITL_EXCEPTION",
  "requested_from_state": "ROUTING",
  "requested_to_state": "ADMIN_CLEARED",
  "message": "Claim state has changed since read. Requested from_state 'ROUTING' does not match current state 'PENDING_HITL_EXCEPTION'."
}
```

Agent action: re-read ClaimRecord (Operation A); `PENDING_HITL_EXCEPTION` is valid — another process escalated while this agent was processing. Do not retry. Log concurrency event. Halt WS1 processing of this claim.

**Worked example — FM-A-5 hard stop (forbidden transition attempted):**

Agent pre-condition check at T-09 detects `ClaimRecord.state = PENDING_PHYSICIAN_REVIEW`. Agent does NOT issue the PATCH. Instead:
- AuditLogEntry written: `action = GOVERNANCE_HARD_STOP_TRIGGERED`, `compliance_flags = ["URAC_NCQA_VIOLATION_PREVENTED", "FM_A5"]`
- ClaimRecord state written to `PENDING_HITL_EXCEPTION` via legitimate transition
- Ops and CMO alert fired

### §5. Error Handling and Retry Logic

| Condition | Retry | Max attempts | Backoff | If all fail |
|-----------|-------|--------------|---------|-------------|
| 503 Unavailable | Yes | 2 | 5s linear | Circuit breaker; claim-level queuing; ops alert after sustained unavailability |
| Timeout > 5s | Yes | 2 | 5s linear | Treat as 503 |
| 409 Conflict (stale `from_state`) | Yes | 1 (after re-read) | None | Re-read; if new state is valid predecessor, retry; else halt |
| 409 Conflict (forbidden transition) | No | 0 | N/A | FM hard stop; `GOVERNANCE_HARD_STOP_TRIGGERED` |
| 400 Validation failure | No | 0 | N/A | Log defect; ops alert |
| 401 Credential | No | 0 | N/A | Suspend; ops alert |

### §6. Rate Limits and Throttling

- **Read volume:** ~5–8 reads per claim across WS1 pipeline = ~10,000–16,000 reads/day
- **Write volume:** ~4–6 state transitions per claim = ~8,000–12,000 writes/day
- **Combined volume:** ~18,000–28,000 calls/day; peak burst ~200 calls/min across all instances
- **Minimum required capacity:** ≥ 200 calls/min per agent instance
- **Rate limit:** DISCOVERY_REQUIRED. Internal system; expected capacity ≥ 500 calls/min; confirm before go-live.

### §7. Data Mapping

**Read mapping (System → Agent, all operations):**

| External field | Internal ClaimRecord field | Notes |
|----------------|--------------------------|-------|
| `claim_id` | `ClaimRecord.id` | UUID |
| `state` | `ClaimRecord.state` | 16-value enum |
| `member_id` | `ClaimRecord.member_id` | Immutable |
| `provider_npi` | `ClaimRecord.provider_npi` | 10-digit NPI |
| `procedure_codes` | `ClaimRecord.procedure_codes` | CPT array |
| `diagnosis_codes` | `ClaimRecord.diagnosis_codes` | ICD-10 array |
| `date_of_service` | `ClaimRecord.date_of_service` | ISO 8601 date |
| `payer_id` | `ClaimRecord.payer_id` | |
| `external_claim_id` | `ClaimRecord.external_claim_id` | Clearinghouse reference |
| `clinical_classification_id` | `ClaimRecord.clinical_classification_id` | FK to ClinicalClassificationResult |
| `payment_amount` | `ClaimRecord.payment_amount` | Decimal USD |
| `rejection_codes` | `ClaimRecord.rejection_codes` | String array |
| `hitl_disposition` | `ClaimRecord.hitl_disposition` | |
| `physician_packet_id` | `ClaimRecord.physician_packet_id` | FK to PhysicianReviewPacket (WS2) |
| `updated_by` | `ClaimRecord.updated_by` | agent_id or human_id |
| `updated_at` | `ClaimRecord.updated_at` | ISO 8601 UTC |

**Write mapping (Agent → System, Operation B state transition):**

| Internal field | External API field | Notes |
|----------------|-------------------|-------|
| Current state (from read) | `from_state` | Optimistic lock |
| Target state | `to_state` | Must be in WS1 or WS2 permitted transition table |
| `agent_id` or `human_id` | `updated_by` | |
| `AuditLogEntry.id` | `audit_log_entry_id` | Must be COMMITTED in S-10 before this write |

**Write mapping (Agent → System, Operation C field write):**

| Internal field | External API field | WS1 / WS2 |
|----------------|--------------------|-----------|
| `ClinicalClassificationResult.id` | `clinical_classification_id` | WS1 |
| `payment_amount` | `payment_amount` | WS1 |
| `rejection_codes` | `rejection_codes` | WS1 |
| `hitl_queue_type` | `hitl_queue_type` | WS1 |
| `hitl_assigned_to` | `hitl_assigned_to` | WS1 |
| `ClinicalClassificationResult_WS2.id` | `clinical_classification_id_ws2` | WS2 |
| `PhysicianReviewPacket.id` | `physician_packet_id` | WS2 |
| `hitl_disposition` | `hitl_disposition` | WS1 and WS2 |

### §8. State Synchronisation

- **Pattern:** On-demand read per pipeline task; write-on-state-change
- **Optimistic locking:** `from_state` field enforces concurrency safety; every PATCH must include the state read immediately before the write
- **WS1 intake polling:** Operation D polls S-07 at `NORMALISED_CLAIM_POLL_INTERVAL_SECONDS` (default 60s) when S-01 intake uses polling fallback
- **No local caching of ClaimRecord state:** Each pipeline task re-reads the ClaimRecord before writing; stale in-memory state is not used to determine write eligibility

### §9. Failure Modes and Fallbacks — G-3 Gap and Sign-off Integrity

**G-3 gap: state machine enforcement classification**

The URAC/NCQA compliance gate (clinical claims must not reach payment without physician sign-off) relies on the claims management platform rejecting forbidden state transitions at the API layer.

**Current classification: PROCEDURE-DEPENDENT** (pending G-3 discovery)

> If the claims management platform accepts any state transition PATCH regardless of the `from_state` / `to_state` combination (i.e., does not enforce state machine guards at the API layer), then the forbidden transition `PENDING_PHYSICIAN_REVIEW → PAYMENT_CALCULATING` can be written if a bug in WS1 issues the PATCH. The FM-A-5 governance hard stop would then be procedure-dependent on agent code correctness only — not system-enforced.

**If G-3 confirmed system-enforced** (platform rejects forbidden transitions with 409):
- Update D4a §8 enforcement mechanism statement to: "System-enforced — claims management platform rejects invalid state transitions at API layer with 409 Conflict"
- Update D4b §8 to the same
- This is the preferred classification; it reduces governance risk to near-zero for the payment bypass path

**If G-3 confirmed procedure-dependent** (platform accepts any state transition write):
- D4a §8 and D4b §8 remain: "Procedure-dependent — enforced by middleware guard (G-3 mitigation option 2) and agent pre-condition check"
- Implement middleware guard: an API wrapper that validates the requested state transition against the permitted transition table before forwarding to the platform
- Monthly audit: zero APPROVED records where the ClaimRecord was simultaneously in PENDING_PHYSICIAN_REVIEW state at the time of the APPROVED write (detect any FM-A-5 or FM-B-5 bypass)
- Document as governance risk in D4a §12 FM-A-5 and D4b §12 FM-B-5

**FM-B-5 hard stop (WS2 specific — physician determination without human_id):**

When WS2 receives a physician determination token from S-08 with `physician_id = null`, WS2 must:
1. Fire `GOVERNANCE_HARD_STOP_TRIGGERED` synchronously before any S-07 write
2. Write AuditLogEntry with `compliance_flags = ["URAC_NCQA_VIOLATION_PREVENTED", "FM_B5", "PHYSICIAN_ATTRIBUTION_MISSING"]`
3. NOT write APPROVED to ClaimRecord
4. Escalate to PENDING_HITL_EXCEPTION with `escalation_reason = PHYSICIAN_ATTRIBUTION_MISSING`

This is an architectural hard stop independent of G-3.

**General failure modes:**

| Failure | Fallback |
|---------|---------|
| S-07 unavailable | Circuit breaker; claim-level queuing; ops alert; SLA clock continues running |
| 409 from valid state race | Re-read; retry once with updated `from_state`; if new state is not a valid predecessor, halt and log |
| 409 from forbidden transition | FM hard stop; do not retry; `GOVERNANCE_HARD_STOP_TRIGGERED` |
| Unexpected ClaimRecord schema | Log defect; suspend claim; ops alert |
| S-10 write failure (ET-07) | Do NOT issue S-07 state transition PATCH until S-10 confirms COMMITTED |

### §10. Pre-deployment Checklist

- [ ] System name and base URL confirmed; DISCOVERY_REQUIRED values replaced
- [ ] WS1 and WS2 credentials provisioned separately: `CLAIMS_MGMT_API_KEY_WS1` and `CLAIMS_MGMT_API_KEY_WS2`
- [ ] **G-3 discovery action (mandatory before go-live):** Ask IT: "Does the claims management platform support write-level state guards that reject state transitions not allowed by the defined state machine? Specifically: if we issue a PATCH from PENDING_PHYSICIAN_REVIEW to PAYMENT_CALCULATING, does the system return 409 or does it accept the write?" Document the answer and update D4a §8 and D4b §8 enforcement mechanism accordingly.
- [ ] **If G-3 procedure-dependent:** Implement middleware state transition guard before go-live; document as governance risk in D4a §12 and D4b §12
- [ ] Field-level write scope test for WS1: attempt write to `member_id` using `CLAIMS_MGMT_API_KEY_WS1` → confirm 400 or 403
- [ ] Field-level write scope test for WS2: attempt write to `payment_amount` using `CLAIMS_MGMT_API_KEY_WS2` → confirm 400 or 403
- [ ] FM-A-5 hard stop test (mandatory): WS1 T-09 pre-condition check with `ClaimRecord.state = PENDING_PHYSICIAN_REVIEW` → confirm PATCH not issued → confirm `GOVERNANCE_HARD_STOP_TRIGGERED` AuditLogEntry → confirm ops and CMO alert
- [ ] FM-B-5 hard stop test (mandatory): WS2 receives determination token with `physician_id = null` → confirm APPROVED PATCH not issued → confirm `GOVERNANCE_HARD_STOP_TRIGGERED` AuditLogEntry with `FM_B5` flag → confirm escalation to PENDING_HITL_EXCEPTION
- [ ] Optimistic locking test: issue two concurrent PATCHes for the same claim with the same `from_state` → confirm only one succeeds (200) and the second returns 409 Conflict
- [ ] `audit_log_entry_id` ordering test: issue state transition PATCH with an `audit_log_entry_id` that does not exist in S-10 → confirm system rejects (400 or 422) OR confirm agent's own pre-condition check blocks the PATCH before it is issued
- [ ] Monthly governance audit procedure documented: query for any APPROVED ClaimRecord with no PhysicianReviewPacket in COMPLETE state (FM-A-5 detection); query for any APPROVED ClaimRecord with `human_id = null` in the physician determination AuditLogEntry (FM-B-5 detection)
- [ ] Load test: 200 concurrent state transition writes → confirm P95 ≤ 2s; confirm no state corruption under load

---

*Pass 7 complete. All integration contracts delivered.*
