# D5 — Build-Loop Response Memo: Apex Billing Dispute Resolution Agent

**Produced:** 2026-05-08
**Status:** Draft — awaiting FDE review
**Source spec:** `Deliverables/D4_agent_purpose_document.md` (revision 1)
**Build loop output:** `Deliverables/Build_loop_analysis.md`
**Taxonomy reference:** `references/spec-ambiguity-vs-builder-mistakes.md`

---

## 0. Build context

This memo applies the 5-category build-loop taxonomy to every signal from the D4A build loop run against the Apex Billing Dispute Resolution Agent spec. D4 revision 1 already incorporated fixes for S-2 (T-007 rule framework) and S-4 (T-001 disambiguation rule) — those revisions are recorded in §3 as originally required. Remaining gaps drive D6 discovery questions.

---

## 1. Signal inventory

| Signal ID | What the build produced | What the spec required or intended | First-pass classification |
|---|---|---|---|
| S-1 | `classify_from_contact_text()` raises `NotImplementedError`; NLP classification path not built | T-005 requires classification from "Parsed contact text" — no NLP rules defined in spec | Legitimate unknown surfaced correctly |
| S-2 | T-007 `charge_validity_assessment` not built; Q-5 raised | T-007 says "rule-based verdict for clear cases" — zero rules defined for any dispute type | Legitimate unknown surfaced correctly |
| S-3 | T-001 NLP intake parser not built; Q-3 raised | D4 §1: "receives disputes from CRM case queue" — trigger mechanism (webhook / polling / email parser) not specified | Legitimate unknown surfaced correctly |
| S-4 | T-001 multi-invoice disambiguation not built; Q-4 raised | T-001: "extract structured fields" — no disambiguation logic for contacts referencing multiple invoices | Legitimate unknown surfaced correctly |
| S-5 | T-011 APEX_CREDITS write not built; Q-1 raised | D4 A-5 assumes write path exists (Low confidence) but defines no mechanism | Legitimate unknown surfaced correctly |
| S-6 | T-010 CRM approval routing not built; Q-2 raised | D4 §5: "system-enforced via CRM workflow state" — Salesforce Approval Process configuration unconfirmed | Legitimate unknown surfaced correctly |
| S-7 | ET-006 routing partially blocked; Q-6 raised | D4 §5 / ET-006: "approval threshold [ASSUMPTION A-6: threshold TBD]" | Legitimate unknown surfaced correctly |
| S-8 | `audit_scanner.py` uses `KNOWN_REASON_CODES = {FUEL_RECALC, GOODWILL, INV_CORR}` as the complete set | D4 FM-3: "FUEL_RECALC, GOODWILL, INV_CORR, **or other formally defined code**" — "or other" implies the set may not be closed | Spec gap |
| S-9 | Account status check not built; Q-8 raised | D4 §5: check APEX_CUSTOMER_MASTER for inactive / collections / payment-plan — no field names or status values defined | Legitimate unknown surfaced correctly |
| S-10 | T-012 customer notification not built | D4 T-012: "Notify customer of resolution and expected credit timeline" — API pattern and notification templates undefined | Legitimate unknown surfaced correctly |
| S-11 | `confidence_router.py` threshold is a function parameter (`current_threshold=0.85`) | D4 §3 states the 0.85 threshold and a recalibration procedure — no specification of how the threshold value should be stored or changed at runtime | Unjustified implementation choice |
| S-12 | `pattern_detector.py` defines "open" as `PENDING_CLAIM or AWAITING_CUST` (inferred from artefact, not surfaced as a question) | D4 T-008: "flag if customer has ≥2 **open** disputes of same type" — "open" not technically defined | Spec gap |
| S-13 | `staleness_checker.py` implements only the freshness check (invoice too recent for batch); test "two-days-old → not stale" passes | D4 §8 Hard Stop 5: "If invoice date is **> 1 business day older** than the dispute contact date, flag the mismatch and escalate per ET-004" — mismatch check (invoice too old) absent | Builder misread |

---

## 2. Classified signal responses

---

```
Signal S-1: T-005 NLP contact text classification path not implemented

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: D4 §4 T-005: "Classify dispute type (fuel surcharge / redelivery fee / dimensional
  weight / other)" with data required "Parsed contact text, invoice line items" and tool
  "Internal classification; Aurum CSV." The spec identifies the input (contact text) but
  defines no classification rules, confidence logic, or fallback for unmatched text.
- Build: classify_from_contact_text() raises NotImplementedError. Builder note: "spec gap
  (see Q-5)." The structured path (classify_from_structured_field()) is fully built for
  cases already in APEX_DISPUTES_OPEN.
- Why legitimate unknown and not spec gap: a spec gap requires two defensible interpretations
  to exist. The spec was simply silent — it named "parsed contact text" as an input without
  providing any rules for what to do with it. There was nothing to misinterpret.

Response:
"You're right that the spec didn't define NLP classification rules for T-005. The correct
behaviour is: when a dispute arrives as an inbound customer contact without a pre-existing
DISPUTE_TYPE field, extract dispute type markers from contact text (keywords: 'fuel surcharge',
'fuel charge', 'redelivery', 're-delivery', 'dimensional weight', 'weight charge'); assign
confidence ≥ 0.85 only if exactly one dispute type matches with no overlap; if no match or
multiple matches, confidence = 0.0 → trigger ET-002; if single match below 0.85 → trigger
ET-001. I'm adding this to the spec now — see Revision R-1 in §3."

Ownership: Shared — FDE acknowledges the gap; spec revision required before builder can implement.
```

---

```
Signal S-2: T-007 charge validity assessment has zero rules defined

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: D4 §4 T-007: "Assess charge validity: rule-based verdict for clear cases;
  confidence-scored for ambiguous." No rules for any of the three dispute types.
- Build: T-007 not built. Q-5 raised: "D4 §4 T-007 states 'rule-based verdict for clear
  cases' but provides zero rules. Without rules the 'rule-based' path cannot be built."
  Builder classified this as the highest-priority spec gap.
- Why legitimate unknown and not spec gap: the spec said "rule-based" implying rules
  should exist, but provided none. Any implementation would have been a guess. The builder
  correctly surfaced the gap rather than inventing rules.

Response:
"You're right that the spec didn't supply the validity rules. The correct behaviour is the
T-007 rule framework in D4 §4b (added revision 1): implement the two-step logic for each
of FUEL_SURCH_DAMAGE, DIM_WEIGHT, and REDELIVERY_FEE including the step-by-step verification,
confidence score assignments per outcome band, and escalation triggers. Note that Q-V1
through Q-V6 in D6 may upgrade certain HITL-required paths to autonomous once Apex answers
policy questions — build with hooks for those upgrades. Addressed in D4 revision 1."

Ownership: Shared — addressed in D4 revision 1 (§4b T-007 rule framework).
```

---

```
Signal S-3: T-001 intake trigger mechanism not specified

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: D4 §1: "Receives disputes from the CRM case queue." Source named; delivery
  mechanism not defined.
- Build: Q-3 raised. Three architectures identified: (a) Salesforce Outbound Message /
  webhook; (b) scheduled CRM REST API polling; (c) email parser creates CRM cases. Each
  requires a different module structure.
- Why legitimate unknown and not spec gap: the spec was silent on the trigger — it named
  the source without describing how delivery works. No competing interpretations of the
  spec text existed.

Response:
"You're right that the spec didn't address how the agent is triggered. The correct intake
mechanism is to be confirmed with Apex IT (D6 Q-BUILD-3). Pending confirmation, design T-001
to support a Salesforce Outbound Message / webhook as the primary path, with 15-minute CRM
REST API polling as the fallback (filtered to status=NEW, case_type=BILLING_DISPUTE). In
polling mode, the agent must check for an existing agent summary field before processing to
prevent duplicate handling. I'm adding this to the spec — see Revision R-3 in §3."

Ownership: Shared — intake channel must be confirmed with Apex IT (D6 Q-BUILD-3).
```

---

```
Signal S-4: T-001 multi-invoice disambiguation not specified

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: D4 §4 T-001 (original): "Parse inbound dispute contact and extract structured
  fields." No disambiguation rule for contacts referencing more than one invoice.
- Build: Q-4 raised. Artefact evidence cited: customer C-04451 has two invoices on the same
  date (INV-2026-04318 and INV-2026-04320). A customer email disputing "my April invoice"
  is genuinely ambiguous.
- Why legitimate unknown and not spec gap: the spec was silent on the multi-invoice case —
  there were no competing interpretations to choose between.

Response:
"You're right that the spec didn't address multi-invoice disambiguation. The correct
behaviour is the 4-step disambiguation rule added in D4 revision 1 (T-001): single
INV-YYYY-NNNNN reference → use it; no reference but one open dispute exists → use that
dispute's INVOICE_NO; multiple references → create one case per invoice; no reference found
→ send acknowledgement requesting invoice number, log as PENDING_INTAKE. Addressed in D4
revision 1."

Ownership: Shared — addressed in D4 revision 1.
```

---

```
Signal S-5: T-011 APEX_CREDITS write path mechanism undefined

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: D4 §9 A-5: "A programmatic write path to APEX_CREDITS exists (or can be
  established)... Confidence: Low." Target named; mechanism absent.
- Build: T-011 not built. Q-1 raised with three fallback architectures depending on what
  Apex IT confirms.
- Why legitimate unknown and not spec gap: A-5 was explicitly marked Low confidence — the
  spec was transparent about not knowing the write path, not ambiguous between two
  interpretations. The builder surfaced the branching question correctly.

Response:
"You're right that the spec didn't resolve the write path mechanism. The correct behaviour
depends on which path Apex IT confirms (D6 Q-BUILD-1): (a) direct DB write or controlled API
→ T-011 is a programmatic write after APPROVER_ID is present; (b) pre-populated auto-ticket
→ T-011 generates the ticket for human submission, 48-hour turnaround remains, and D4 §1's
'Fully Agentic below threshold for C-8' claim must be revised to 'Agent-led + Human
Oversight'; (c) no write path → T-011 prepares the record only. A-5 updated to BLOCKING GAP
in D4 revision 1."

Ownership: Shared — write path confirmation required with Apex IT (D6 Q-BUILD-1) before T-011 can be built.
```

---

```
Signal S-6: T-010 CRM approval gate mechanism (Salesforce configuration) undefined

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: D4 §5 Enforcement mechanism: "The CRM workflow engine holds the case in
  PENDING_APPROVAL state until a human agent performs an authenticated approval action
  (API call with user token + CREDIT_AMT input). The APPROVER_ID field is populated only
  by the authenticated token — the agent has no write permission to this field."
- Build: Q-2 raised: "This requires Salesforce Approval Process or Flow to be configured.
  REST APIs are confirmed but workflow state capability is not."
- Why legitimate unknown and not spec gap: the spec required a specific governance outcome
  (system-enforced gate) but was silent on the Salesforce feature that would deliver it.
  The builder correctly identified the gap between the governance requirement and the
  unconfirmed Salesforce capability.

Response:
"You're right that the spec required system enforcement without specifying the Salesforce
configuration. The correct implementation: if Salesforce Approval Process is available,
T-010 submits via the Salesforce Approval Process API and APPROVER_ID is populated by the
authenticated approver's user token. If not configured, flag this as a pre-deployment
requirement — the governance gate degrades to procedure-only until it is configured. I'm
adding a Salesforce configuration prerequisite note to D4 §5 — see Revision R-6 in §3."

Ownership: Shared — Salesforce Approval Process availability must be confirmed with Apex IT (D6 Q-BUILD-2).
```

---

```
Signal S-7: ET-006 approval threshold explicitly TBD

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: D4 §5 / ET-006: "credit recommendation amount exceeds approval threshold
  [ASSUMPTION A-6: threshold TBD by COO/finance prior to deployment; flagged as
  prerequisite item]."
- Build: Q-6 raised. Routing logic in T-009/T-010 blocked — without the threshold value,
  the agent cannot determine whether to route to the standard approver or the COO-designated
  senior approver.
- Why legitimate unknown and not builder misread: the spec explicitly named this as TBD
  and a governance prerequisite — the builder correctly surfaced it rather than guessing
  a threshold.

Response:
"You're right that the spec didn't supply the threshold — it is a governance prerequisite.
The correct behaviour once defined: if CREDIT_AMT < threshold → route to standard approver;
if CREDIT_AMT ≥ threshold → route to COO-designated senior approver per ET-006. Implement
T-009's routing logic to read the threshold from the policy registry at runtime (not
hardcoded), so the COO can configure it without a code deployment. I'm adding a policy
registry read instruction and an interim default (all cases → standard approver with a
'threshold not configured' warning) to D4 ET-006 — see Revision R-7 in §3."

Ownership: Shared — threshold must be defined by COO/finance (D6 Q-BUILD-6).
```

---

```
Signal S-8: REASON_CODE taxonomy ambiguous — "or other formally defined code" creates an open set

Classification: Spec gap

Evidence:
- Spec: D4 §7 FM-3: "REASON_CODE is not a defined taxonomy value {FUEL_RECALC, GOODWILL,
  INV_CORR, or other formally defined code}." The phrase "or other formally defined code"
  is ambiguous: it could mean "these three plus any future approved additions" or "these
  three are examples from a larger set defined elsewhere."
- Build: audit_scanner.py uses KNOWN_REASON_CODES = {FUEL_RECALC, GOODWILL, INV_CORR}
  derived from the artefact. Builder flagged this in the module note: "REASON_CODE taxonomy
  is inferred from the artefact sample, not formally defined in D4."
- Why spec gap and not legitimate unknown: two defensible interpretations existed — "these
  three are the complete approved set at deployment" vs. "more codes may exist and the set
  is open." The builder chose "closed set of three" (the artefact-grounded interpretation).
  If the credit policy introduces additional codes, the scanner will generate false-positive
  compliance violations. The FDE must clarify which interpretation is correct.

Response:
"I need to revise the spec because the original statement was ambiguous between interpretation
A ('FUEL_RECALC, GOODWILL, INV_CORR' is the complete approved set) and interpretation B
(the set is open and other formally defined codes may exist). The correct behaviour is
interpretation A: the approved REASON_CODE taxonomy at initial deployment is exactly
{FUEL_RECALC, GOODWILL, INV_CORR}. Any addition requires a formal policy registry update
with a version number and COO approval date. The audit scanner's KNOWN_REASON_CODES constant
must be read from the policy registry at runtime — not hardcoded — so new codes can be added
without a code deployment. See Revision R-8 in §3."

Ownership: FDE
```

---

```
Signal S-9: APEX_CUSTOMER_MASTER schema and account status field values not defined

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: D4 §5 Autonomy Matrix (Human Takes Over): "The customer's account has been flagged
  as inactive, in collections, or under a formal payment plan in the APEX_CUSTOMER_MASTER
  export." Business conditions named; technical field names and status values absent.
- Build: Q-8 raised; account status check not built. Builder: "field names and status values
  unknown; a check cannot be built without knowing the field name and the set of values that
  trigger escalation."
- Why legitimate unknown and not spec gap: the spec described the business condition
  unambiguously (inactive, collections, payment plan) but was silent on the technical
  implementation. There were no competing interpretations of what "inactive" means — the
  spec just didn't say how to check for it.

Response:
"You're right that the spec didn't specify the APEX_CUSTOMER_MASTER field structure. Once
the schema is obtained from Apex IT (D6 Q-BUILD-8), implement the account status check as:
retrieve the customer's record from APEX_CUSTOMER_MASTER by customer ID; check the account
status field for values mapped to inactive, collections, and payment-plan; if any match,
trigger the Human Takes Over path. Until the schema is confirmed, implement the check as a
stub that logs 'CUSTOMER_MASTER_SCHEMA_UNCONFIRMED' and passes through — flag as a
post-deployment validation task. See Revision R-9 in §3."

Ownership: Shared — schema must be confirmed with Apex IT before implementation.
```

---

```
Signal S-10: T-012 customer notification templates and CRM outbound API not defined

Classification: Legitimate unknown surfaced correctly

Evidence:
- Spec: D4 §4 T-012: "Notify customer of resolution and expected credit timeline" with
  data required "Resolved case details, credit amount, expected statement date" and tool
  "CRM outbound messaging API." Purpose and data named; template content and API call
  pattern absent.
- Build: T-012 listed in section 3 as blocked: "CRM outbound messaging API spec unknown;
  notification templates not defined."
- Why legitimate unknown and not spec gap: the spec was simply silent on template content
  and API specification — no two competing interpretations existed.

Response:
"You're right that the spec didn't define the notification templates or API pattern. The
correct implementation: (a) Credit confirmed template — 'Your billing dispute for invoice
[INVOICE_NO] has been reviewed. A credit of £[CREDIT_AMT] will appear on your next
statement, expected within [CREDIT_TIMELINE] business days. Reference: [CRM_CASE_ID].';
(b) Escalated/pending template — 'Your billing dispute (reference [CRM_CASE_ID]) is under
review. We will respond within 2 business days.'; (c) CRM API call: POST to the CRM case
outbound email endpoint with template populated from case fields; agent must receive a
confirmed send receipt before logging CUSTOMER_NOTIFIED — if send fails, log
NOTIFICATION_FAILED and alert the assigned billing agent. Exact endpoint to confirm with
Salesforce administrator. See Revision R-10 in §3."

Ownership: Shared — CRM messaging capability and templates require confirmation before implementation.
```

---

```
Signal S-11: confidence_router.py implements threshold as a function parameter — recalibration
mechanism unspecified in spec

Classification: Unjustified implementation choice

Evidence:
- Spec: D4 §3 states the threshold as "0.85." The recalibration procedure describes raising
  it "by 0.05 increments" and logging "in a policy version control register maintained by
  the COO's designated operations lead" — but does not specify whether the threshold should
  be a function parameter, a config file entry, a database value, or another mechanism.
- Build: route_by_confidence(confidence_score, current_threshold=0.85) — threshold is a
  function parameter with a default value. Builder note: "Threshold is a parameter, not a
  constant, to support post-deployment recalibration without code deployment."
- Why unjustified implementation choice and not acceptable variation: the spec describes a
  recalibration procedure that implies the threshold should be changeable without a code
  deployment. A function parameter satisfies "not hardcoded" syntactically but still requires
  the calling code to read the value from somewhere — which means a config source is needed
  anyway. The builder made a design decision the spec was silent on, and the chosen
  mechanism only partially addresses the spec's recalibration intent.

Response:
"This wasn't specified in the spec. Before deciding whether to keep it, we need to align:
the spec's recalibration procedure requires threshold changes to be logged in a policy
version control register — this implies the threshold should be read from an external
config source (policy registry, config file, or database field) at runtime, not passed as
a parameter. A function parameter approach requires the caller to supply the value, which
means the config read must happen somewhere upstream anyway. We should align on: (a) the
calling code reads the threshold from the policy registry at runtime and passes it to
route_by_confidence() — which keeps your parameter approach and adds a registry read; or
(b) the threshold is read inside the function from a config singleton. Either approach
satisfies the spec's recalibration intent. Please don't commit either until we've confirmed
the config strategy with the build guidelines."

Ownership: Collaborative
```

---

```
Signal S-12: pattern_detector.py defines "open" dispute status as PENDING_CLAIM or
AWAITING_CUST — inferred from artefact without surfacing the interpretation

Classification: Spec gap

Evidence:
- Spec: D4 §4 T-008: "Detect repeat dispute pattern: flag if customer has ≥2 open disputes
  of same type." D4 §6 ET-005: "customer has ≥2 open disputes of the same dispute type in
  APEX_DISPUTES_OPEN at time of intake." "Open" is not technically defined in either location.
- Build: detect_repeat_pattern() counts disputes with STATUS in {PENDING_CLAIM,
  AWAITING_CUST}, explicitly excluding RESOLVED. This was derived from the artefact data
  without raising a question.
- Why spec gap and not legitimate unknown surfaced correctly: a legitimate unknown requires
  the builder to surface the gap. The builder chose an interpretation (PENDING_CLAIM /
  AWAITING_CUST = open) and proceeded without raising a question. Both interpretations are
  defensible ("any status except RESOLVED" vs. "specifically PENDING_CLAIM and AWAITING_CUST")
  — the spec was ambiguous on the technical definition of "open." If APEX_DISPUTES_OPEN uses
  additional statuses in production (e.g., IN_REVIEW, ESCALATED), the pattern detector will
  silently miss those cases, and high-risk repeat-dispute accounts will bypass ET-005
  escalation.

Response:
"I need to revise the spec because the original statement was ambiguous between 'open means
any non-RESOLVED status' and 'open means specifically PENDING_CLAIM and AWAITING_CUST.'
The correct behaviour is: 'open dispute' is defined as any APEX_DISPUTES_OPEN record with
STATUS in {PENDING_CLAIM, AWAITING_CUST} — derived from the 2026-04-14 artefact sample.
RESOLVED disputes are excluded. The OPEN_STATUSES set must be read from config, not
hardcoded, so that if the confirmed production schema uses different values, the set can be
updated without a code deployment. Confirm the complete STATUS taxonomy with Apex IT
(D6 Q-BUILD-8 or a separate schema question). See Revision R-12 in §3."

Ownership: FDE
```

---

```
Signal S-13: staleness_checker.py misses Hard Stop 5's invoice-to-dispute mismatch check

Classification: Builder misread

Evidence:
- Spec: D4 §8 Hard Stop 5: "Never use Aurum invoice data to make a validity assessment
  without first checking the invoice date against the dispute contact date. If the invoice
  date is > 1 business day older than the dispute contact date, the agent must flag the
  mismatch and escalate per ET-004 before generating any validity verdict. The data-stale
  check is not optional."
- Build: staleness_checker.py implements is_invoice_stale(invoice_dt, batch_export_dt) —
  returns True if the invoice is too recent to appear in the T-1 batch (same-day or
  future-dated). Test case "two-days-old → not stale" confirms an invoice from 2 business
  days before the dispute passes through without flagging. The module cites "D4 §8 Hard
  Stop 5" as its spec source.
- Why builder misread and not spec gap: Hard Stop 5 states both the trigger condition
  (invoice date > 1 business day older than dispute contact date) and the required action
  (flag mismatch, escalate per ET-004) unambiguously. The builder's implementation satisfies
  T-014 (freshness: invoice not yet in batch) but not Hard Stop 5 (mismatch: invoice may
  be from the wrong day). These are two distinct checks — the builder conflated them while
  claiming to implement both. The test case "two-days-old → not stale" directly contradicts
  the spec: an invoice dated 2 business days before the dispute IS > 1 business day older
  and MUST be flagged per Hard Stop 5.

Response: [See §4 — Re-prompt for S-13]

Ownership: Builder
```

---

## 3. Spec revision log

```
Revision R-1 (for Signal S-1):

Section revised: D4 §4 T-005 — tool description and classification logic
Original text: "Classify dispute type (fuel surcharge / redelivery fee / dimensional weight
  / other)" with tool "Internal classification; Aurum CSV"
Revised text: "Classify dispute type (fuel surcharge / redelivery fee / dimensional weight /
  other). Two paths: (1) Structured path — if dispute already has a DISPUTE_TYPE field in
  APEX_DISPUTES_OPEN, classify directly from that field; confidence 1.0 for known types
  {FUEL_SURCH_DAMAGE, DIM_WEIGHT, REDELIVERY_FEE}, confidence 0.0 + UNKNOWN for anything
  outside taxonomy (trigger ET-002). (2) NLP path — for inbound contacts without a
  pre-existing DISPUTE_TYPE field, extract dispute type markers from contact text (keywords:
  'fuel surcharge', 'fuel charge', 'redelivery', 're-delivery', 'dimensional weight',
  'weight charge'); assign confidence ≥ 0.85 only if exactly one dispute type marker matches
  with no overlap between categories; if no match or multiple matches → confidence 0.0,
  trigger ET-002; if single match with confidence < 0.85 → trigger ET-001."
What the revision prevents: a builder implementing T-005 without NLP rules would either
  invent keyword heuristics inconsistently or leave the NLP path unimplemented, blocking
  all intake that arrives as a new customer contact rather than via APEX_DISPUTES_OPEN.
Category: Legitimate unknown — gap filled
```

---

```
Revision R-2 (for Signal S-2):

Section revised: D4 §4b (T-007 validity assessment rule framework) — added in revision 1
Original text: [§4b did not exist in D4 original]
Revised text: [The full T-007 rule framework in D4 §4b: FUEL_SURCH_DAMAGE two-step rule,
  DIM_WEIGHT two-step rule, REDELIVERY_FEE two-step rule, confidence score band table
  (0.90–1.00 autonomous / 0.80–0.89 HITL strong evidence / 0.50–0.79 HITL conflicting /
  <0.50 HITL from scratch), and D6 discovery questions Q-V1 through Q-V6]
What the revision prevents: a builder producing T-007 rules from inference rather than
  policy — generating validity verdicts based on the builder's domain assumptions, not
  Apex's actual credit policy, at 60 cases/day.
Category: Legitimate unknown — gap filled (addressed in D4 revision 1)
```

---

```
Revision R-3 (for Signal S-3):

Section revised: D4 §4 T-001 — intake trigger mechanism
Original text: [D4 §1] "Receives disputes from the CRM case queue."
Revised text: "Intake trigger: (Primary path, to confirm with Apex IT — D6 Q-BUILD-3)
  Salesforce Outbound Message or webhook push when a new case with case_type=BILLING_DISPUTE
  enters the CRM queue. (Fallback path) Scheduled CRM REST API polling every 15 minutes for
  cases with status=NEW and case_type=BILLING_DISPUTE. In polling mode, the agent must check
  for an existing agent-generated summary field in the case record before initiating T-001;
  if the field is populated, skip this case to prevent duplicate processing."
What the revision prevents: T-001 module lacking an entry point — the agent cannot process
  disputes it has no mechanism to receive.
Category: Legitimate unknown — gap filled
```

---

```
Revision R-4 (for Signal S-4):

Section revised: D4 §4 T-001 — multi-invoice disambiguation rule
Original text: [No disambiguation rule in D4 original]
Revised text: [The 4-step disambiguation rule added in D4 revision 1: (1) single
  INV-YYYY-NNNNN reference in contact → use that invoice; (2) no reference extractable
  AND exactly one open dispute for this customer in APEX_DISPUTES_OPEN → use that
  dispute's INVOICE_NO; (3) multiple invoice numbers with no single-match → one case per
  invoice; (4) no invoice reference and no existing open dispute → acknowledge with
  "please provide your invoice number," log as PENDING_INTAKE]
What the revision prevents: the agent processing only the first extracted invoice number
  (missing others) or refusing to proceed on ambiguous contacts, causing incorrect case
  handling for a scenario confirmed by artefact data (C-04451, two invoices same date).
Category: Legitimate unknown — gap filled (addressed in D4 revision 1)
```

---

```
Revision R-5 (for Signal S-5):

Section revised: D4 §9 A-5 status
Original text: "Confidence: Low"
Revised text: "Confidence: Low — STATUS: BLOCKING GAP (confirmed D4A build loop, revision 1).
  Three fallback architectures pending Apex IT confirmation (D6 Q-BUILD-1): (a) direct DB
  write or controlled API → T-011 is a programmatic write after APPROVER_ID is confirmed;
  (b) pre-populated auto-ticket to Aurum support → T-011 generates the ticket for human
  submission; 48-hour turnaround remains; D4 §1 'Fully Agentic below threshold for C-8'
  must be revised to 'Agent-led + Human Oversight'; (c) no write path → T-011 prepares
  the compliant record only; human submits the Aurum ticket. T-011 cannot be built until
  Apex IT confirms which path is available."
What the revision prevents: building T-011 against an assumed write capability that may
  not exist — producing either unrunnable code or a module that errors at runtime.
Category: Legitimate unknown — gap filled with status update
```

---

```
Revision R-6 (for Signal S-6):

Section revised: D4 §5 Enforcement mechanism — prerequisite note
Original text: "The credit record write gate is system-enforced via workflow state..."
Revised text: "[Existing enforcement text] — Pre-deployment prerequisite (added revision 1):
  This enforcement requires Salesforce Approval Process or equivalent Flow configuration.
  If Salesforce is in basic CRM mode without Approval Processes configured, the
  PENDING_APPROVAL → APPROVED transition cannot be system-enforced; the governance gate
  degrades to a procedural control (dispatcher manually enters APPROVER_ID), which
  represents the governance risk described in FM-5. This must be resolved before deployment.
  Confirm Salesforce edition and Approval Process availability with Apex IT (D6 Q-BUILD-2)
  before building T-010."
What the revision prevents: deploying T-010 against a governance mechanism that is
  unavailable in the actual Salesforce instance, leaving the primary governance gate as
  procedure-dependent rather than system-enforced.
Category: Legitimate unknown — gap filled
```

---

```
Revision R-7 (for Signal S-7):

Section revised: D4 §6 ET-006 trigger condition
Original text: "Credit recommendation amount exceeds approval threshold [ASSUMPTION A-6:
  threshold TBD]"
Revised text: "Credit recommendation amount exceeds approval threshold. Threshold value:
  defined by COO/finance before deployment (D6 Q-BUILD-6). The threshold must be stored in
  the policy registry (version-controlled, with COO approval date and effective date) —
  not hardcoded. T-010 routing reads the threshold from the policy registry at runtime.
  Until the threshold is defined in the policy registry, T-010 defaults to routing all
  credit recommendations to the standard approver, and a 'APPROVAL_THRESHOLD_NOT_CONFIGURED
  — defaulting to standard approver' warning is logged to the operations lead's daily report."
What the revision prevents: T-010 routing being hardcoded to a placeholder threshold, or
  remaining unimplemented while waiting for a governance decision.
Category: Legitimate unknown — gap filled with interim default behaviour
```

---

```
Revision R-8 (for Signal S-8):

Section revised: D4 §7 FM-3 — REASON_CODE taxonomy definition
Original text: "REASON_CODE is not a defined taxonomy value {FUEL_RECALC, GOODWILL,
  INV_CORR, or other formally defined code}"
Revised text: "REASON_CODE is not in the approved REASON_CODE taxonomy. The approved
  taxonomy at initial deployment is exactly: {FUEL_RECALC, GOODWILL, INV_CORR}. No other
  values are valid at deployment. Any addition requires a formal policy registry update
  with a version number and COO approval date. The audit scanner's KNOWN_REASON_CODES
  constant must be read from the policy registry at runtime — not hardcoded — so that new
  policy-approved codes can be added without a code deployment. Note: the artefact sample
  (APEX_CREDITS_20260414) shows exactly these three codes; no others have been observed."
What the revision prevents: two failure modes — (a) the scanner flagging future
  policy-approved codes as compliance violations because the set was hardcoded as closed;
  (b) the scanner accepting informal codes never approved because "or other formally defined
  code" was read as an open set requiring no formal process.
Category: Spec gap — ambiguity resolved
```

---

```
Revision R-9 (for Signal S-9):

Section revised: D4 §5 Autonomy Matrix — Human Takes Over condition
Original text: "The customer's account has been flagged as inactive, in collections, or
  under a formal payment plan in the APEX_CUSTOMER_MASTER export"
Revised text: "[Existing condition] — Technical implementation prerequisite: the
  APEX_CUSTOMER_MASTER CSV schema is not available in the Gate2 artefacts. Before building
  this check, obtain the schema from Apex IT (D6 Q-BUILD-8) and identify: (a) the account
  status field name; (b) the set of values that map to inactive, in collections, and under
  a formal payment plan. Add these to the canonical schemas in aurum_ingestion.py. Until
  the schema is confirmed, implement the account status check as a stub that logs
  'CUSTOMER_MASTER_SCHEMA_UNCONFIRMED' and passes through without blocking — flag as a
  post-deployment validation task."
What the revision prevents: building an account status check against field names that
  don't exist in the actual export, producing a module that either always errors or always
  passes through, silently failing to catch high-risk accounts.
Category: Legitimate unknown — gap filled
```

---

```
Revision R-10 (for Signal S-10):

Section revised: D4 §4 T-012 — notification templates and API specification
Original text: "Notify customer of resolution and expected credit timeline" with tool
  "CRM outbound messaging API"
Revised text: "Notify customer using one of two templates: (a) Credit confirmed —
  'Your billing dispute for invoice [INVOICE_NO] has been reviewed. A credit of
  £[CREDIT_AMT] will appear on your next statement, expected within [CREDIT_TIMELINE]
  business days. Your reference number is [CRM_CASE_ID].'; (b) Escalated/pending —
  'Your billing dispute (reference [CRM_CASE_ID]) is under review by our billing team.
  We will respond within 2 business days.' CRM API: POST to the CRM case outbound email
  endpoint with template populated from case fields. The agent must receive a confirmed
  send receipt before logging case status as CUSTOMER_NOTIFIED. If send fails, log as
  NOTIFICATION_FAILED and alert the assigned billing agent. Exact endpoint and API version
  to confirm with Salesforce administrator (D6 Q-BUILD-3)."
What the revision prevents: T-012 remaining unimplemented because the builder has no
  template content to work from, or being implemented with hardcoded message text that
  cannot be updated without a code deployment.
Category: Legitimate unknown — gap filled
```

---

```
Revision R-12 (for Signal S-12):

Section revised: D4 §4 T-008 and D4 §6 ET-005 — definition of "open" dispute
Original text (T-008): "flag if customer has ≥2 open disputes of same type"
Revised text (T-008): "Flag if customer has ≥2 open disputes of same type, where 'open'
  is defined as any APEX_DISPUTES_OPEN record with STATUS in {PENDING_CLAIM, AWAITING_CUST}.
  RESOLVED disputes are excluded. The OPEN_STATUSES set must be read from config, not
  hardcoded, to accommodate confirmed production schema values once obtained from Apex IT.
  Source: APEX_DISPUTES_OPEN artefact (2026-04-14 sample)."
Original text (ET-005): "customer has ≥2 open disputes of the same dispute type in
  APEX_DISPUTES_OPEN at time of intake"
Revised text (ET-005): "[Same addition: 'where open is defined as STATUS in
  {PENDING_CLAIM, AWAITING_CUST}']"
What the revision prevents: the pattern detector silently missing cases where open disputes
  carry a different status value (e.g., IN_REVIEW, ESCALATED), allowing high-risk
  repeat-dispute accounts to bypass ET-005 and be processed as standard individual cases.
Category: Spec gap — ambiguity resolved
```

---

## 4. Builder correction memos

```
Re-prompt for Signal S-13:

The spec states (D4 §8 Hard Stop 5):
"Never use Aurum invoice data to make a validity assessment without first checking the
invoice date against the dispute contact date. If the invoice date is > 1 business day
older than the dispute contact date, the agent must flag the mismatch and escalate per
ET-004 before generating any validity verdict. The data-stale check is not optional."

Your implementation of staleness_checker.py checks whether an invoice is too recent to
appear in the T-1 batch (same-day or future-dated invoice). This correctly implements T-014.
However, the test case "two-days-old → not stale" confirms that an invoice dated 2 business
days before the dispute contact date returns not stale and proceeds without flagging. This
directly contradicts Hard Stop 5, which requires flagging when the invoice date is > 1
business day OLDER than the dispute date — the mismatch direction, not only the freshness
direction. Hard Stop 5 exists specifically to prevent FM-4: retrieving an older invoice for
the same customer and assessing the wrong charge.

Please revise staleness_checker.py to implement two distinct checks:

1. is_invoice_too_recent(invoice_dt, batch_export_dt) — existing T-014 check; returns True
   if invoice was generated after the T-1 batch cutoff (data not yet in batch).

2. is_invoice_date_mismatch(invoice_dt, dispute_contact_dt) — new Hard Stop 5 check;
   returns True if invoice_dt is more than 1 business day before dispute_contact_dt
   (i.e., invoice_dt < dispute_contact_dt - 1 business day).

Add the following tests to cover the mismatch direction:
- invoice dated 2 business days before dispute → is_invoice_date_mismatch = True
- invoice dated 1 business day before dispute → is_invoice_date_mismatch = False
  (threshold is strictly greater than 1 business day — same-day and 1-day-old are fine)
- invoice dated same day as dispute → is_invoice_date_mismatch = False

The calling workflow must run BOTH checks before proceeding to T-007. If either returns
True, escalate per ET-004 before generating any validity verdict.
```

---

## 5. Diagnostic accuracy self-assessment

**Hardest classification call:**
"The hardest call in this fixture was Signal S-13. I initially read it as a spec gap because the builder cited Hard Stop 5 as a spec source for staleness_checker.py — which suggested the builder had read it and made an interpretation. On closer reading I classified it as a builder misread because Hard Stop 5's trigger condition is unambiguous ('invoice date > 1 business day older than dispute contact date') and the test case 'two-days-old → not stale' is a direct contradiction — that case should flag per Hard Stop 5, but the implementation passes it through. The distinguishing factor was the test data: it proved the mismatch direction was absent from the implementation, not just underdescribed. A citation in the spec source note is not evidence of correct implementation — the builder read Hard Stop 5 but conflated it with T-014."

**Closest miss:**
"The signal I came closest to misclassifying was S-12 (pattern_detector.py defining 'open' as PENDING_CLAIM or AWAITING_CUST). The risk of error was that the builder made a well-reasoned inference from artefact data and produced a working implementation — this looks like acceptable variation, not a spec deficiency. I avoided classifying it as legitimate unknown surfaced correctly because the builder did NOT surface the interpretation as a question; they chose it and proceeded. That is the defining feature of a spec gap: ambiguity existed, the builder chose one interpretation without flagging it, and the FDE owns the clarification. A legitimate unknown requires the builder to have surfaced the gap — which the builder did not do here."

**Pre-session prediction:**
"Before the build loop, I predicted the hardest part of build-loop diagnosis would be distinguishing spec gaps from legitimate unknowns — specifically, cases where the spec made a statement that implied coverage (like 'rule-based verdict for clear cases') without providing the underlying rules. Looking at this fixture, that prediction was partially accurate: S-2 (T-007) fits exactly — 'rule-based' without rules is the canonical version of this trap. The harder calls turned out to be S-13 (a builder misread disguised by a spec-source citation) and S-12 (a spec gap disguised as a reasonable inferred implementation), neither of which I had specifically anticipated."
