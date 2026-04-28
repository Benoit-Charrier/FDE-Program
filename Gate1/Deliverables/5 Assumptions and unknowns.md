# Assumptions and Unknowns
## FNOL Processing Agent — Insurance Claims Automation

---

## 1. How to read this document

This log is the accountability record for every claim made across Deliverables 1–4 that is not directly supported by the scenario. Assumptions that turn out to be wrong are not failures — they are the spec's load-bearing joints, and knowing which ones are wrong early is the point. An assumption that breaks after build starts becomes a scope change, a spec rewrite, or a failed integration. An unknown left unresolved before build starts is a risk that will surface as a gap during development. Every [TODO], [ASSUMED], and [SCOPE-OUT] marker in Deliverables 2, 3, and 4 is tracked here. Review this log with the client before the build begins; every item marked FLAGGED_FOR_VALIDATION or BLOCKER requires a client answer before the corresponding spec section can be treated as firm.

---

## 2. Assumptions register

---

### Domain: Data

```
[A-1] FNOL inputs always contain an extractable policy identifier
Statement: Every claim received across all three channels (email, phone transcript,
  web form) contains a policy identifier matching the pattern [A-Z]{2}-[0-9]{8},
  either stated explicitly by the claimant or present in the system metadata.
Domain: Data
Why it matters: The policy identifier is the key used to retrieve the policy record
  from the legacy system (REQ-5). If it is absent, coverage validation cannot begin
  and the claim enters COVERAGE_UNCERTAIN immediately, requiring specialist intervention
  on 100% of claims without an identifier. This would collapse the automation ROI.
If wrong: Every claim without a policy identifier enters INTEGRATION_ERROR / escalation
  at step 2.1. If 20% of email claims omit the policy number (plausible for distressed
  claimants), 60 claims/day require manual policy lookup before processing can continue,
  adding specialist load the capacity model did not account for.
Status: FLAGGED_FOR_VALIDATION
Validation question: In your current FNOL intake, what percentage of inbound emails
  and phone calls fail to include a policy number? How do your specialists currently
  recover a policy number when the claimant does not provide one?
Confidence: Medium — web forms enforce the field; email and phone are uncontrolled.
```

```
[A-2] Claimant contact email is always present and extractable from claim inputs
Statement: Every FNOL submission contains an email address for the claimant, either
  as a structured field (web form), in the email header (email channel), or spoken
  during the call and captured in the transcript. The agent uses this as the
  acknowledgement destination for REQ-7 and REQ-8.
Domain: Data
Why it matters: REQ-7 (receipt acknowledgement) must fire within 300 seconds
  unconditionally. If no email address is available, the acknowledgement cannot be
  sent and the primary claimant SLA metric immediately fails.
If wrong: For phone transcript claims where the claimant does not provide an email
  address, the RECEIPT acknowledgement cannot be sent. The 300-second SLA is
  structurally unachievable for that subset. An alternative contact channel (SMS,
  postal) would need to be specced — which is currently out of scope.
Status: FLAGGED_FOR_VALIDATION
Validation question: For phone-channel claims today, do your specialists always
  capture an email address? What is your fallback contact method when a claimant
  does not have or provide an email address?
Confidence: Low — phone transcripts have no structural guarantee of email presence.
```

```
[A-3] Loss date and estimated loss value are always explicitly present or inferrable
  from claim inputs across all three channels
Statement: The NLP extraction step (REQ-1) can reliably extract loss_date and
  estimated_loss_value from every claim input. Loss date is stated or implied
  (e.g., "last Tuesday"), and estimated loss value is either stated as a number,
  a range, or a description from which an estimate can be derived.
Domain: Data
Why it matters: loss_date is used to validate policy in-force status (REQ-5).
  estimated_loss_value drives severity scoring (REQ-3). If either field is
  unextractable, parse_confidence drops below 0.70 and the claim enters
  PARSE_UNCERTAIN, requiring specialist correction before processing continues.
  The proportion of claims entering PARSE_UNCERTAIN directly determines specialist
  workload and SLA achievability for those claims.
If wrong: If 15% of claims lack an explicit loss date or estimable value — which is
  realistic for distressed or unsophisticated claimants — 45 claims/day enter
  PARSE_UNCERTAIN before any triage begins. The specialist load increase is not
  accounted for in the current capacity model, and the 30-minute recovery window
  per claim risks SLA breach for every affected claim.
Status: FLAGGED_FOR_VALIDATION
Validation question: In your current FNOL intake, how often do claimants fail to
  state a date of loss or provide any cost estimate? What does your team do when
  a claim arrives with no date and no estimated value?
Confidence: Low — the scenario provides no sample claims; this cannot be assessed
  without real data.
```

---

### Domain: Systems

```
[A-4] CRM exposes real-time adjuster availability and contact details via structured API fields
Statement: The CRM API returns per-adjuster is_available (boolean), adjuster_specialty
  (enum), current_queue_depth (integer), adjuster_name (string), and adjuster_contact
  (email or phone) as structured fields on the adjuster resource endpoint. These fields
  are updated in real time by the CRM when adjusters change availability status.
Domain: Systems
Why it matters: REQ-6 (adjuster routing) depends on real-time availability to select
  the correct adjuster. REQ-8 (routing confirmation) depends on adjuster name and
  contact details to populate the claimant message. Stale or absent availability data
  produces incorrect routing; absent contact details produces a generic (lower-value)
  routing confirmation.
If wrong (availability not real-time): The agent assigns claims to adjusters who are
  unavailable, producing a high reassignment rate (D4 metric: > 10% reassignments/week)
  and an inflated QUEUE_OVERFLOW rate. The routing accuracy metric fails immediately
  post go-live.
If wrong (contact details absent): REQ-8 falls back to a generic message ("you will
  be contacted") — the routing confirmation loses its primary value to the claimant
  and the metric for claimant acknowledgement quality cannot be measured.
Status: FLAGGED_FOR_VALIDATION
Validation question: Does your CRM today expose adjuster availability as a structured
  boolean field per adjuster, and is that field updated in real time when an adjuster
  goes out of office or reaches capacity? Does it also hold each adjuster's direct
  contact email or phone number as a structured field?
Confidence: Medium — described as "modern CRM with APIs"; real-time availability is
  common but not universal.
```

```
[A-5] Phone call transcripts are converted to plain text before reaching the agent
Statement: The call centre system produces a text transcript of each FNOL phone call
  and delivers that transcript to the CRM (or a shared folder the agent polls) before
  the agent processes the claim. The agent never processes audio directly.
Domain: Systems
Why it matters: The ingestion spec (REQ-1) defines the input format for PHONE_TRANSCRIPT
  as "plain text, max 50,000 chars." If the agent must handle audio files, the NLP
  extraction pipeline requires a speech-to-text component that is currently out of scope
  and unspecified.
If wrong: Audio FNOL files cannot be processed by the current spec. The phone channel
  would be excluded from automation entirely, reducing the agent's coverage from 3
  channels to 2 and leaving the phone channel (potentially the majority of inbound
  claims) in the manual process. The capacity deficit calculation does not change
  because phone claims remain manual — but the business case weakens significantly.
Status: FLAGGED_FOR_VALIDATION
Validation question: When a claimant calls to report a claim, does your call centre
  system produce a text transcript automatically? If so, where is that transcript
  stored and how quickly is it available after the call ends?
Confidence: Medium — call centre transcription is common; automatic delivery to the
  claims system is not universal.
```

```
[A-6] Policy identifiers are unique within the policy administration system
Statement: Each policy_id value ([A-Z]{2}-[0-9]{8}) maps to exactly one policy record
  in the policy administration system. The agent uses policy_id as the sole lookup key.
Domain: Systems
Why it matters: If two policy records share the same policy_id (e.g., after a system
  migration, reissue, or data error), the retrieval step (2.1) returns ambiguous results.
  The spec handles this by escalating to HUMAN_ONLY — but if it is a systematic data
  quality issue, it will fire on every affected claim.
If wrong: Every claim whose policy_id has a duplicate record in the policy admin system
  enters COVERAGE_DISPUTED immediately, bypassing all automation for coverage validation.
  If 5% of policies are affected, 15 claims/day go straight to human-only coverage
  resolution. The specialist capacity model does not account for this volume.
Status: FLAGGED_FOR_VALIDATION
Validation question: Has your policy administration system ever had duplicate policy
  identifiers — for example, after a system migration or policy reissue? Are there
  any known data quality issues with policy ID uniqueness in the current system?
Confidence: Medium — modern policy admin systems enforce uniqueness; legacy systems
  after migrations may not.
```

---

### Domain: Organisation

```
[A-7] The 12 specialist FTEs can service AGENT_REVIEW escalations within the 30 / 15-minute
  review windows during business hours
Statement: The 12 specialists who currently handle all FNOL processing will transition
  to a review function post go-live. Their available capacity is sufficient to action
  EscalationBriefings within the defined windows (30 minutes for standard reviews,
  15 minutes for special handling flags), assuming the escalation rate stays within
  the projected 15–35% band (45–105 escalations per day on 300 claims).
Domain: Organisation
Why it matters: The review window determines SLA achievability for escalated claims.
  If specialists cannot clear the review queue within the window, claims auto-escalate
  to ESCALATED status, which may trigger SLA breach. The entire delegation model in
  D2 rests on specialists being available to review within these windows.
If wrong (capacity insufficient): Escalation briefings pile up; review windows expire;
  claims auto-escalate; SLA breach rate for escalated claims is high. The 30-minute
  window may need to be extended, which reduces SLA achievability for all escalated
  claims (a 30-minute window leaves 90 minutes for the rest of the process; a 60-minute
  window leaves only 60 minutes).
If wrong (specialists unavailable outside business hours): Every claim received outside
  business hours that requires AGENT_REVIEW will breach SLA unless the review window
  spans to next business day — which the 2-hour SLA does not permit.
Status: FLAGGED_FOR_VALIDATION
Validation question: What are your specialists' working hours, and do you have any
  FNOL coverage outside standard business hours today? If claims arrive at 10pm,
  how are they currently handled? Is there an on-call rota for critical escalations?
Confidence: Low — the scenario does not state working hours or shift patterns.
```

```
[A-8] The client has a defined on-call escalation path for out-of-hours critical claims
Statement: For claims with FATALITY, LEGAL_REPRESENTATION, or FRAUD_INDICATOR flags
  that arrive outside business hours, a named contact or rota exists that the agent
  can notify. The 15-minute special handling review window applies regardless of time
  of day.
Domain: Organisation
Why it matters: Special handling flags (tier 1.5) have a 15-minute review window.
  If no one is available to action them outside business hours, every out-of-hours
  flagged claim will auto-escalate to ESCALATED, the 15-minute window will expire,
  and the SLA will breach for the most sensitive claim types.
If wrong: FATALITY and LEGAL_REPRESENTATION claims arriving overnight are processed
  without specialist review within the SLA window. Regulatory breach risk for fatality
  claims is high; legal exposure for claims where legal representation was active
  but not handled correctly is significant.
Status: FLAGGED_FOR_VALIDATION
Validation question: Do you have an on-call rota today for urgent or sensitive claims
  received outside business hours? Who is the escalation contact for a fatality claim
  received at midnight on a Sunday?
Confidence: Low — no staffing structure stated in scenario.
```

---

### Domain: Process

```
[A-9] The current claimant acknowledgement is a manual step performed at the end of
  the 22-minute handling cycle — not an automated first-contact response
Statement: Today, the claimant's first communication from the insurer after submitting
  an FNOL is sent by a specialist at or near the end of the 22-minute process, not
  by an automated system on receipt.
Domain: Process
Why it matters: The primary claimant SLA improvement in D1 is driven by the agent
  sending a receipt acknowledgement within 5 minutes of claim arrival (REQ-7) — well
  before triage is complete. If the acknowledgement is already automated today (e.g.,
  an auto-reply email on receipt), the 31% SLA breach figure does not represent
  acknowledgement delay — it represents something downstream — and the target metric
  (< 30 minutes for 90% of claims) may already be met for the first-contact step.
If wrong: The receipt ACK metric (D1 success metric row 5) is measuring something
  already solved. The real SLA bottleneck is downstream (adjuster contact, not
  acknowledgement), and the spec's primary SLA intervention is solving the wrong
  problem. The capability specification would need to be reframed around routing
  speed and adjuster contact SLA rather than acknowledgement speed.
Status: FLAGGED_FOR_VALIDATION
Validation question: When a claimant submits an FNOL today — by email, phone, or
  web form — do they receive any automated acknowledgement immediately on receipt,
  or does all communication come from a specialist? If automated, what does the
  message contain, and how quickly is it sent?
Confidence: Low — scenario does not state whether any automated response exists today.
```

```
[A-10] The 18% routing error rate is primarily caused by misclassification of claim type
  or adjuster specialty — not by adjuster capacity or availability constraints
Statement: When a claim is routed to the wrong adjuster today, the primary cause is
  that the specialist misjudged the claim type (e.g., classified a liability claim as
  a property claim) or selected the wrong adjuster specialty. The error is in the
  decision, not in the information available to make it.
Domain: Process
Why it matters: The agent improves routing accuracy by making classification more
  reliable (REQ-2). If routing errors are actually caused by adjuster unavailability
  (the right adjuster is not available so the specialist routes to whoever is free),
  then classification accuracy improvements will not reduce the 18% error rate —
  adjuster capacity management would need to be in scope.
If wrong: The 96% routing accuracy target (D1 success metrics) is not achievable
  through classification improvement alone. Adjuster workload balancing (REQ-6 uses
  lowest queue depth selection) addresses availability-driven errors partially, but
  if the root cause is structural adjuster understaffing in certain specialties,
  no routing algorithm resolves it.
Status: FLAGGED_FOR_VALIDATION
Validation question: When a claim is re-routed today — when an adjuster passes it
  to a colleague — what is the most common reason given? Is it typically "wrong
  type of claim for me" (classification error) or "too busy / wrong specialty
  available" (capacity error)?
Confidence: Medium — classification error is the more common cause in documented
  FNOL literature, but this client's specific error pattern is unknown.
```

---

### Domain: Regulatory

```
[A-11] GDPR applies to claimant personal data; FCA claims handling rules apply to
  the process; financial records must be retained for 7 years
Statement: The client is subject to GDPR (or equivalent data protection regulation)
  for personal data in claim inputs. The claims handling process is governed by FCA
  rules (or equivalent national insurance regulator) requiring audit trails and HITL
  checkpoints for coverage decisions. Financial transaction records (claim audit logs)
  must be retained for a minimum of 7 years.
Domain: Regulatory
Why it matters: These assumptions drive the audit log schema (§10 of D3), the
  anonymisation requirement for PII, the immutability constraint on audit records,
  and the retention periods. If the regulatory regime is different (e.g., the client
  operates in a jurisdiction where data protection rules are different, or where
  insurance regulation does not require 7-year retention), multiple requirements
  in the capability spec must change.
If wrong (not UK / EU jurisdiction): GDPR anonymisation rules may not apply;
  7-year retention may be incorrect (too long or too short); FCA HITL requirements
  may differ. The audit log schema and compliance section (D3 §10) must be rebuilt
  against the actual regulatory requirements.
If wrong (PCI-DSS does not apply): The card number redaction requirement in D3 §10
  is unnecessary overhead; it can be removed from REQ-1 processing.
Status: FLAGGED_FOR_VALIDATION
Validation question: In which country or countries does this insurer operate and
  handle claims? Are you subject to FCA regulation (or equivalent)? Does your
  current claims process handle payment card details in FNOL submissions, and if
  so, are you PCI-DSS certified?
Confidence: Low — jurisdiction, regulator, and PCI-DSS status are all unconfirmed.
```

---

## 3. Open unknowns

---

```
[U-1] Policy administration system SOAP contract
What we don't know: The WSDL, operation names, request/response XML schemas, fault
  codes, authentication mechanism, base endpoint URL, and performance characteristics
  (average response time, rate limits, concurrency limits) of the legacy policy
  administration system SOAP service.
Why it blocks build: The entire coverage validation step (REQ-5, D3 §7.2) depends on
  this integration. Without the WSDL, the agent cannot construct a valid SOAP request,
  cannot map the response to the Claim entity's policy fields, and cannot define retry
  logic against actual fault codes. The mock stub in the console application (D3 §11)
  can be built without this, but the real integration cannot be completed. This is the
  single highest-risk integration in the system — it is legacy, it is external, and it
  has SOAP (not REST), which means no auto-generated client from an OpenAPI spec.
Who can answer: Head of IT / Systems Architect at the client (the team responsible
  for the legacy policy admin system).
How to resolve: Client provides WSDL file. FDE team reviews WSDL, maps required
  operations to D3 §7.2 spec, and confirms authentication method via 30-minute
  technical call. Estimated resolution time: 3–5 business days after WSDL receipt.
Priority: BLOCKER — build of the real policy admin integration cannot begin without this.
```

```
[U-2] Sample claim data for NLP model development, test set definition, and acceptance
  criterion validation
What we don't know: Representative examples of real FNOL claims across all three
  channels (email, phone transcript, web form) and all five claim types (motor,
  property, liability, health, other). The scenario explicitly states there is no
  sample claim data, no appendix, and no SOW.
Why it blocks build: The acceptance criteria for REQ-1, REQ-2, REQ-3, and REQ-4
  are stated as percentages against a test set (e.g., "parse_confidence ≥ 0.70 on
  ≥ 85% of inputs"). Without a test set, these criteria cannot be measured and the
  acceptance test cannot be run. More fundamentally, the NLP extraction and
  classification models must be configured or fine-tuned on claim data that matches
  the client's policy types, claim language, and input formats. A model trained on
  generic insurance data may perform significantly worse on this client's specific
  vocabulary and document structures — and there is no way to know without samples.
Who can answer: Claims Operations Manager (has access to historical FNOL records);
  Data Protection Officer (must approve sharing of anonymised samples for development
  purposes).
How to resolve: Client provides a minimum of 200 anonymised historical FNOL claims
  (50 per channel minimum, spanning all five claim types) with ground-truth labels
  (claim type, severity, flags, coverage outcome). DPO sign-off required. Estimated
  resolution time: 2–4 weeks (data extraction, anonymisation, DPO approval).
Priority: BLOCKER — acceptance criteria for REQ-1 through REQ-4 cannot be validated
  without labelled test data. Model calibration cannot proceed.
```

```
[U-3] Severity scoring model thresholds and claim value boundary definitions
  (referenced as [TODO: D5-U1] in D2 and D3)
What we don't know: The specific claim value (in the client's currency) that should
  separate LOW/MEDIUM from HIGH/CRITICAL severity, and the scoring model formula
  that maps claim_type + estimated_loss_value + policy_tier to a severity_score (0–100).
  The working hypothesis in D2 and D3 uses [CURRENCY]10,000 and score boundary 60,
  but these are placeholders.
Why it blocks build: The severity threshold determines the escalation rate. If set at
  the wrong level, the agent either over-escalates (defeating the automation ROI) or
  under-escalates (high-value claims processed without specialist review). The
  acceptance criteria for REQ-3 cannot be tested until the threshold is defined and
  used to generate a labelled test set.
Who can answer: Head of Claims / Senior Claims Manager (who sets reserve guidelines
  and defines what constitutes a high-value claim for this insurer).
How to resolve: Workshop with Head of Claims to define: (1) the claim value bands by
  claim type that constitute LOW/MEDIUM/HIGH/CRITICAL; (2) any non-value factors that
  affect severity (e.g., claim type alone elevating severity regardless of value);
  (3) policy tier influence on severity. Estimated resolution time: 1 half-day workshop.
Priority: HIGH — spec can proceed with placeholder values but acceptance criteria
  cannot be validated until thresholds are confirmed.
```

```
[U-4] Fraud detection capability: model availability, historical fraud data, and
  threshold definition (referenced as [TODO: D5-U2] in D2 and D3)
What we don't know: Whether the client has any existing fraud detection model or
  tooling. If not, whether fraud signal detection must be built from scratch using
  claim text signals alone. What the client's historical fraud rate is and what
  types of fraud are most common in their portfolio. What fraud_score threshold (0.60
  used as working hypothesis) is appropriate.
Why it blocks build: REQ-4 (special handling flag detection) includes FRAUD_INDICATOR
  as a required flag. The build approach depends entirely on the answer: if the client
  has a fraud model, the agent integrates with it; if not, the agent must implement
  text-based fraud signal detection, which requires labelled fraud examples to calibrate.
  Without knowing the approach, the integration contract for fraud detection (or the
  NLP model design) cannot be written.
Who can answer: Head of Claims Operations and/or Head of Fraud (if the function exists
  separately); IT team (to confirm whether a fraud detection system is in production).
How to resolve: Discovery call to determine: (1) does a fraud detection system exist?
  (2) if yes, what is its API contract? (3) if no, can the client provide labelled
  historical fraud examples for model development? Estimated resolution time: 1–2 weeks.
Priority: HIGH — fraud flag detection is a required safety feature; a non-functional
  fraud detector is a known gap that must be scoped correctly before build.
```

```
[U-5] CRM API documentation, rate limits, and capability confirmation
  (referenced as [UNKNOWN] across D3 §7.1 and [ASSUMED] for multiple capabilities)
What we don't know: The full API documentation for the CRM's claims endpoint, adjuster
  endpoint, email send endpoint, and review queue endpoint. Specifically: (a) rate
  limits per endpoint, (b) whether a review queue / task queue endpoint exists with
  the required fields, (c) whether the email send endpoint is native to the CRM or
  requires a third-party email provider integration, (d) OAuth token endpoint URL
  and client credentials provisioning process.
Why it blocks build: All six CRM operations in D3 §7.1 have [UNKNOWN] rate limits.
  If the CRM enforces a rate limit lower than the agent's expected throughput (e.g.,
  50 req/min on the claims endpoint while the agent needs 300 creates/day + status
  updates), the agent must implement request queuing and backoff logic not currently
  in the spec. If the review queue endpoint does not exist or has different field
  names, the EscalationBriefing design (REQ-9) must change.
Who can answer: CRM vendor (if SaaS) or IT team (if self-hosted); CRM Administrator.
How to resolve: Request CRM API documentation from vendor/IT team. Schedule 1-hour
  API walkthrough with CRM administrator to confirm all required operations exist
  and to obtain rate limit figures. Estimated resolution time: 1–3 business days.
Priority: HIGH — without rate limits, the agent may be throttled in production;
  without review queue confirmation, REQ-9 cannot be built to spec.
```

```
[U-6] Specialist review capacity model and out-of-hours escalation process
  (referenced as assumption [A-7] and [A-8] above)
What we don't know: The actual working hours of the 12 specialist FTEs, the volume
  of claims received outside business hours (what percentage of 300 daily claims
  arrive evenings and weekends), and whether any on-call rota exists for critical
  escalations outside business hours.
Why it blocks build: The review window SLAs (30 minutes / 15 minutes for special flags)
  are achievable only if a specialist is available to act within the window. If 30%
  of claims arrive outside business hours and no on-call rota exists, the 15-minute
  special handling window structurally cannot be met for out-of-hours flagged claims.
  The spec must either define extended staffing as a go-live pre-condition, or define
  a different handling path for out-of-hours special handling flags.
Who can answer: Claims Operations Manager; HR / Workforce Planning.
How to resolve: Request claim arrival time-of-day distribution from Claims Operations.
  Review staffing rota to determine actual coverage hours. Define out-of-hours
  escalation path (on-call mobile, escalation email) before spec is finalised.
  Estimated resolution time: 1–2 business days.
Priority: HIGH — without this, the SLA model for escalated claims is based on an
  unvalidated staffing assumption.
```

```
[U-7] Data retention policy and PCI-DSS applicability
  (referenced as [TODO: D5-U10] in D3 §10)
What we don't know: The client's specific data retention policy for claims records,
  whether PCI-DSS certification is in scope (i.e., whether payment card details ever
  appear in FNOL inputs), and the jurisdiction(s) in which the client operates (which
  determines which data protection regulation applies).
Why it blocks build: The retention periods in D3 §10 (7 years for audit logs, 2 years
  for integration error logs) are assumed. If the client's actual regulatory requirement
  is different, the audit schema and storage infrastructure must change. The PCI-DSS
  card number redaction requirement in REQ-1 is conditional on PCI-DSS applying — if
  it does not, the redaction feature adds cost and latency with no benefit.
Who can answer: Data Protection Officer / Compliance Lead; Legal team.
How to resolve: Request data retention schedule from DPO. Confirm jurisdiction.
  Confirm whether PCI-DSS is in scope via brief compliance call. Estimated resolution
  time: 3–5 business days.
Priority: HIGH — compliance requirements must be confirmed before the audit and
  governance section of the spec (D3 §10) is treated as final.
```

```
[U-8] Claimant communication content: templates, legal sign-off, expected contact
  SLA, and special handling keyword sets (referenced as [TODO: D5-U9] in D3)
What we don't know: (a) The approved text of the receipt acknowledgement email and
  routing confirmation email — specifically what can and cannot be said to a claimant
  at each stage. (b) The expected adjuster contact timeframe to include in the routing
  confirmation. (c) The legally approved keyword sets for FATALITY and LEGAL_REPRESENTATION
  flag detection. (d) The duplicate claim deduplication window (24 hours used as
  working hypothesis). (e) The on-call contact list for out-of-hours SLA breach alerts.
Why it blocks build: REQ-7 and REQ-8 depend on approved message templates.
  REQ-4 depends on validated keyword sets. Using unapproved language in an automated
  claimant message creates legal exposure (potential admission of liability or
  commitment to an outcome). The keyword sets for FATALITY and LEGAL_REPRESENTATION
  must be validated by the client's legal/compliance team — the working set in D3
  is illustrative only.
Who can answer: Head of Claims Communications / Legal team (for message templates
  and keyword sets); Claims Operations Manager (for contact SLA and dedup window).
How to resolve: Workshop with Claims Communications and Legal to review and approve
  all automated message templates. Separate session with Claims Operations to agree
  contact SLA and deduplication policy. Estimated resolution time: 1–2 weeks
  (legal sign-off typically takes longer than technical review).
Priority: HIGH — automated messages that have not been legally reviewed must not
  go to production.
```

```
[U-9] Adjuster reserve field availability in CRM for retrospective quality detection
What we don't know: Whether the CRM exposes the adjuster's first recorded reserve
  value for a claim as a structured API field. This field is required by the D4
  retrospective quality detection mechanism (nightly batch comparing
  Claim.estimated_loss_value against adjuster reserve to detect extraction underestimation).
Why it blocks build: The primary detection mechanism for quiet failure mode 2
  (systematic NLP underestimation of claim value — D4 §4) depends on this field.
  Without it, the most dangerous quiet failure mode (high-value claim silently
  classified as low-severity) has no automated detection. An alternative detection
  mechanism would need to be designed.
Who can answer: CRM Administrator; Head of Claims Operations (who knows what the
  adjuster workflow captures in CRM).
How to resolve: Request CRM data model documentation and confirm whether reserve
  value is a structured field on the claim record or buried in free-text adjuster
  notes. If structured: confirm API accessibility. If unstructured: design an
  alternative detection mechanism (e.g., adjuster severity disagreement rate from
  claim re-routing). Estimated resolution time: 2–3 business days.
Priority: HIGH — without this, the retrospective quality detection for the most
  dangerous quiet failure mode is not implementable as designed in D4.
```

---

## 4. Scope-outs

```
[S-1] Policy Administration System — SOAP Integration Contract
What was deferred: The full SOAP integration contract for the legacy policy
  administration system: WSDL, operation names, request/response XML schemas,
  fault codes, authentication details, base endpoint URL, rate limits, and
  concurrency limits.
From: D3 §7.2 — Integration contracts — Policy Administration System (Legacy — SOAP)
  "[SCOPE-OUT: Full SOAP contract... not specifiable from the scenario]"
Resolution plan: Client provides WSDL file before integration build begins. FDE team
  maps WSDL operations to the required fields listed in D3 §7.2 (GetPolicyByID,
  PolicyRecord field list). Authentication method confirmed via technical call.
  Build uses a configurable mock stub (USE_POLICY_ADMIN_MOCK = true/false in .env)
  until the real contract is confirmed. The mock is included in the console application
  (D3 §11) and all test scenarios in D4 use the mock. The real integration replaces
  the mock at the point the WSDL is received and the contract is confirmed.
Owner: Joint — client provides WSDL; FDE writes integration client
Deadline: Before integration build sprint begins (after spec is finalised and
  accepted). This is a BLOCKER for the real integration — see U-1.
```

```
[S-2] DMS Integration Contract — Protocol, Authentication, and Endpoint Details
What was deferred: The DMS protocol (assumed REST over HTTPS), authentication method
  (assumed API key), base URL, exact endpoint paths, request format (multipart or JSON),
  and response schemas are all [ASSUMED] in D3 §7.3.
From: D3 §7.3 — Integration contracts — Document Management System
  "[ASSUMED: REST over HTTPS — protocol not stated in scenario]"
  "[ASSUMED: https://dms.client.internal/api/v1]"
  "[ASSUMED: API key in Authorization header]"
Resolution plan: Request DMS API documentation from IT team. If DMS is a third-party
  SaaS product (SharePoint, OpenText, M-Files, etc.), vendor documentation is likely
  available. Confirm: protocol, authentication, document create endpoint, request
  format, and whether FNOL_CLAIM is a supported document type. The DMS integration
  is non-blocking for claim processing (D3 §9: DMS failure does not halt processing),
  so this scope-out has lower urgency than S-1.
Owner: Client IT team provides documentation; FDE confirms contract and updates D3 §7.3
Deadline: Before integration build sprint for DMS. Non-blocking for core triage and
  routing build — DMS can be completed in a later sprint.
```

```
[S-3] CRM Rate Limits and Review Queue Endpoint Confirmation
What was deferred: All six CRM operations in D3 §7.1 have [UNKNOWN] rate limits.
  The review queue endpoint (CREATE_ESCALATION_BRIEFING) is specced against an
  assumed path (/review-queue) with assumed field names that must be confirmed
  against the actual CRM API.
From: D3 §7.1 — Integration contracts — CRM (Modern — REST API)
  "Rate limit: [UNKNOWN — flag for client confirmation; assume 100 req/min]"
  (repeated for all 6 operations)
Resolution plan: Request CRM API documentation (see U-5). Once rate limits are
  confirmed, update D3 §7.1 with actual values and add request throttling logic
  if any limit is below the agent's throughput requirement (estimated peak: ~5
  req/min for CREATE_CLAIM at 300 claims/day, but higher for UPDATE_CLAIM_STATUS
  during burst processing). If the review queue endpoint does not exist with the
  required fields, design an alternative EscalationBriefing delivery mechanism.
Owner: Client CRM Administrator provides API docs; FDE updates spec
Deadline: Before CRM integration build begins. Non-blocking for mock-based
  console application development.
```

---

## 5. Risk summary table

| ID | Summary | If unresolved | Priority | Owner |
|---|---|---|---|---|
| U-1 | Policy admin SOAP WSDL not available | Coverage validation integration cannot be built; agent runs with mock stub only; production deployment blocked | BLOCKER | Client IT / Systems Architect |
| U-2 | No sample claim data for NLP model development and test set | Acceptance criteria for REQ-1 through REQ-4 cannot be validated; model may perform significantly worse on real data than on synthetic test cases | BLOCKER | Client Claims Operations Manager + DPO |
| S-1 | SOAP integration contract scoped out | Same consequence as U-1; mock stub ships to production, which is not acceptable | BLOCKER | Joint (client provides WSDL; FDE writes client) |
| U-3 | Severity scoring thresholds undefined | Severity tier boundaries remain placeholders; agent may over- or under-escalate systematically; D4 acceptance criteria for REQ-3 untestable | HIGH | Head of Claims |
| U-8 | Claimant message templates not legally reviewed | Automated messages to claimants carry legal exposure; cannot deploy REQ-7 or REQ-8 to production without legal sign-off | HIGH | Claims Legal / Communications team |
| U-5 | CRM API rate limits and review queue endpoint unconfirmed | Agent may be throttled in production; REQ-9 (escalation briefing) may require redesign if review queue endpoint does not match spec | HIGH | CRM Administrator |
| U-4 | Fraud detection capability undefined | FRAUD_INDICATOR flag in REQ-4 has no model to power it; silent gap in special handling coverage | HIGH | Head of Claims Operations / Head of Fraud |
| U-6 | Out-of-hours specialist coverage unknown | AGENT_REVIEW and special handling review windows structurally unachievable for out-of-hours claims if no on-call rota exists; SLA model is invalid without this | HIGH | Claims Operations Manager |
| U-7 | Data retention policy and PCI-DSS applicability unconfirmed | D3 §10 compliance section built on unvalidated assumptions; wrong retention period or missing PCI-DSS redaction creates regulatory exposure | HIGH | DPO / Compliance Lead |
| A-1 | Policy identifier not always present in email/phone inputs | Up to 60 claims/day may enter PARSE_UNCERTAIN before triage; specialist capacity model breaks down | MEDIUM | Claims Operations Manager |
| A-2 | Claimant email not always present in phone transcripts | Receipt ACK (REQ-7) cannot be sent for affected claims; SLA metric fails for phone channel subset | MEDIUM | Claims Operations Manager |
| U-9 | Adjuster reserve field not confirmed in CRM | Primary retrospective quality detection mechanism (D4 §4, quiet failure mode 2) is not implementable; silent under-escalation of high-value claims has no automated detection | HIGH | CRM Administrator / Head of Claims Operations |
| S-2 | DMS protocol and contract deferred | DMS integration built on assumed REST/API-key contract; may require rework if protocol differs | MEDIUM | Client IT team |
| A-11 | Regulatory jurisdiction and retention period unconfirmed | Audit schema and retention periods may be wrong; potential regulatory non-compliance on go-live | HIGH | DPO / Legal |
