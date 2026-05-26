# D0C: Discovery Synthesis
**Engagement:** Greenfield Health Systems — Medical Claims Adjudication Transformation
**Phase:** ATX Assessment Phase 1 — Discovery
**Prepared:** 2026-05-20
**Source of truth:** `Scenario/scenario_context.md`

---

## 0. Executive Summary

- **Primary cognitive workload finding:** WS1 (administrative adjudication) consumes the greatest total skilled human time — the current 78% manual processing rate against ~2,000 claims/day (scenario.md) generates roughly 1,560 claims/day requiring full processor handling, which at 35 min/claim average (scenario.md) represents a processing load that materially exceeds the 20-person claims review staff's daily capacity and directly explains the 8–9 day cycle time currently triggering active SLA penalties (Exchange 3).
- **Most critical lived-vs-documented gap:** No formal clinical content classifier exists in the current process — processors are routing claims to physician review through undocumented pattern recognition rather than a codified criterion, which is the structural cause of the 41% denial appeal overturn rate (scenario.md) and the highest-consequence design risk in the engagement.
- **Highest-signal delegation opportunity:** WS1 administrative adjudication presents the clearest agent intervention case — the four required administrative steps (eligibility verification, coding validation, prior auth completeness, payment determination) are codifiable, low-clinical-risk, and reversible, and the industry benchmark of 85% auto-adjudication vs. the current 22% (scenario.md) confirms this delegation path is proven and that the gap is a process problem, not a fundamental complexity problem.

---

## 0b. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Lived process narrative](#1-lived-process-narrative)
- [2. Points of Pain inventory](#2-points-of-pain-inventory)
- [3. ATX discovery dimensions — assessment per work stream](#3-atx-discovery-dimensions--assessment-per-work-stream)
- [4. Cognitive workload hotspots](#4-cognitive-workload-hotspots)
- [5. Known unknowns](#5-known-unknowns)
- [6. Assumption log](#6-assumption-log)

---

## 1. Lived Process Narrative

*Source note: this narrative is reconstructed from scenario_context.md, scenario.md, and scenario_enriched.md. Sections explicitly drawing on inference are flagged as assumptions in Section 6. WS1/WS2 labels refer to target-state designations from the negotiated routing split; current-state routing is undifferentiated (see Step 4 below).*

### Trigger and intake

A claim enters the Greenfield system via one of three formats: EDI 837 (structured electronic), PDF (semi-structured document), or portal submission (web form) (scenario.md). Each claim arrives with at minimum: member ID, provider information, date(s) of service, diagnosis codes (ICD-10), and procedure codes (CPT/HCPCS).

**Coordination work:** Three intake formats with fundamentally different structure levels means that intake normalisation is not uniform. EDI 837 claims arrive pre-structured and machine-readable; PDF claims require data extraction before processing logic can apply. How Greenfield handles this format disparity is not described in the scenario — assumption [A-D0C-1] is that processors handle all three formats but that PDF and portal submissions require more initial extraction work, adding per-claim handling time before adjudication steps begin.

### Step 1 — Eligibility verification

A processor opens the claim and verifies that the member was actively enrolled in the plan on the date of service, cross-referencing member eligibility records against the claim's service date.

**Pause point:** If a discrepancy appears — plan terminated, dependent eligibility gap, coverage lapse on a specific date — the processor must determine whether this is a data synchronisation error or a legitimate coverage gap. These two outcomes look identical in the claim record but require different actions (override vs. deny).

**Judgment call:** A coverage lapse on a service date may reflect a grace period, a billing system lag, or a genuine gap. Resolving it requires policy knowledge and, in many cases, a judgment about the most probable explanation. This is the kind of decision that produces inconsistency across a team of processors when no documented escalation path exists (assumption [A-D0C-2]).

**Delegation note:** For the majority of claims, eligibility is either confirmed or denied with no ambiguity — binary outcome, deterministic lookup. This is the closest step to a pure rule-based check in the entire process. For the standard path, a scripted rule or RPA is sufficient; an agent is not warranted (see Hotspot WS1-1).

### Step 2 — Coding validation

The processor reviews the submitted ICD-10 and CPT/HCPCS codes for accuracy and appropriateness. This includes:
- Technical validity of individual codes
- Code-diagnosis pairing logic (does the procedure match the diagnosis?)
- Bundling and unbundling checks (prevention of duplicate billing for component procedures)
- Place-of-service code consistency

**Judgment call:** Code-diagnosis pairing is semi-structured. Formal crosswalk rules exist, but a code can be technically valid against a diagnosis while being clinically implausible given the provider specialty, patient history, or place of service. Detecting implausible combinations requires pattern recognition built from processing experience, not just rules lookup (assumption [A-D0C-3]).

**Pause point:** Processors stop to consult coding reference tools when encountering unfamiliar combinations or specialty-specific codes. The tools used are not named in the scenario (assumption [A-D0C-4]).

**Workaround:** When a code combination is unusual but not clearly wrong, processors may pass it through with a mental flag rather than escalating, accepting first-pass risk in exchange for throughput. This behaviour is inferred from the 41% denial appeal overturn rate (scenario.md), which suggests upstream decisions are frequently incorrect.

### Step 3 — Prior authorisation completeness check

Certain procedures require advance approval (prior authorisation) before the provider performs them. The processor verifies:
- Whether a prior auth was required for the procedure(s) on the claim
- Whether a valid prior auth is on file
- Whether the auth is approved for the correct procedure codes, date(s) of service, and number of units/visits

**Coordination work:** Prior auth records likely reside in a system separate from the claim record (assumption [A-D0C-4]). If so, the processor manually cross-references two systems to verify completeness — looking up the auth by member ID and procedure code and confirming it matches the claim.

**Pause point:** Partial matches require a judgment call. If an auth was approved for 10 units and the claim is for 12, the processor must decide: provider error, legitimate overrun, or deny? If the auth has a date range discrepancy, the same logic applies. Each of these decisions takes time and introduces inconsistency.

**Async wait:** When prior auth is missing and must be requested, the claim enters a pending state while the processor waits for the provider to respond. This is one of the primary contributors to the 8–9 day average cycle time (Exchange 3) — each async wait extends the cycle without the claim moving through adjudication.

### Step 4 — Routing decision (the undocumented critical step)

After the three administrative checks, the processor must decide: **Does this claim contain clinical content that requires physician review?**

*This step does not appear as a named step in scenario.md, which lists four required steps: eligibility verification, coding validation, medical necessity review, and payment determination. However, the stakeholder exchanges make clear that a routing decision between medical necessity review and payment determination must occur, and that this decision is the central design problem of the engagement. The lived process includes a routing step that the documented four-step flow does not explicitly name.*

**This is the most critical lived-vs-documented gap in the process.**

In the absence of a formal clinical content classifier, this routing decision is made by processors using undocumented pattern recognition: certain diagnosis codes, procedure types, and provider specialties may trigger a clinical flag based on the processor's training and experience. Two processors working the same claim may make different routing decisions. Sarah Chen's Exchange 3 message — requesting that "clinical flagging" criteria be formally defined — confirms that no written criteria currently exist.

**Judgment call:** The processor is making a quasi-clinical routing decision without clinical training. The asymmetry of errors matters: routing a clinical claim as administrative (false negative) creates a compliance violation under Dr. Marcus Webb's non-negotiable governance constraint (Exchange 2). Routing an administrative claim as clinical (false positive) creates unnecessary physician queue load and cycle time extension. Neither error type is acceptable at scale.

**The 41% denial appeal overturn rate** (scenario.md) is the primary evidence that this routing decision is currently inconsistent — claims are either being mis-routed or mis-decided at the first-pass stage, and those errors are being caught at appeal.

### Step 5a — Administrative payment determination (WS1 path)

For claims routed as administrative-only, the processor applies the fee schedule to determine the payment amount, checks for duplicate claim submissions, applies applicable member cost-sharing (co-pay, deductible, co-insurance), and issues a payment decision.

**Judgment call (edge cases):** Standard fee schedule application is rule-bound. Exceptions exist for carved-out procedures, bundled payment arrangements, and out-of-network providers with individually negotiated rates. These are low-frequency but require knowledge of specific contractual arrangements that may not be fully encoded in the payment system (assumption [A-D0C-6]).

### Step 5b — Clinical review (WS2 path)

For claims routed as containing clinical content, the claim enters a physician reviewer queue. A physician or advanced practice provider opens the claim and must assemble clinical context before any medical judgment can be applied:
- Diagnosis codes and procedure codes (validated in Step 2)
- Clinical documentation from the provider (location and access method unknown — assumption [A-D0C-7])
- Prior authorisation history if applicable
- Medical necessity criteria (the specific criteria tool — e.g., InterQual, Milliman — is not named in the scenario, assumption [A-D0C-4])

**Coordination work:** The physician is assembling multi-source clinical context before they can apply medical judgment. This context-assembly phase is information-gathering work, not clinical judgment — it consumes physician time without requiring physician expertise. Without a pre-filled review packet, this represents the primary recoverable time cost in WS2. Dr. Marcus Webb's estimate of 20 claims/hour throughput with pre-screening (Exchange 3) implies that context assembly currently consumes a significant portion of per-claim physician time.

**Pause point:** The physician must determine whether the clinical documentation supports medical necessity for the procedure. If documentation is sparse, contradictory, or missing, the reviewer must request additional information from the provider — creating another async wait cycle.

**Non-negotiable governance constraint:** Every denial of a claim with clinical content requires physician or advanced practice provider sign-off (Dr. Marcus Webb, Exchange 2). CMO team will not certify any system that bypasses this requirement. This is the hardest delegation stop in the engagement — it is compliance-linked and applies regardless of agent confidence level.

### Current state performance indicators

| Metric | Value | Source |
|---|---|---|
| Auto-adjudication rate | 22% (industry benchmark: 85%) | scenario.md |
| Average processing time | 35 min/claim | scenario.md |
| Average cycle time | 8 days (currently 9+ days) | scenario.md, Exchange 3 |
| Denial appeal overturn rate | 41% | scenario.md |
| Error rate | ~1.2% | scenario_enriched.md |
| SLA penalty threshold | 7 days | scenario.md |
| Claims volume | ~2,000/day (reconciliation note: 1,667/day also stated — see Assumption A-1) | scenario.md, Exchange 3 |

The 63-point gap between current auto-adjudication (22%) and industry benchmark (85%) represents the primary operational and economic opportunity. The 41% overturn rate and 9+ day cycle time confirm that the current manual process is both slow and systematically inaccurate — the accuracy problem and the speed problem share a common structural cause: the absence of a formal clinical content routing criterion.

---

## 2. Points of Pain Inventory

*Volume derivations: steps 1–4 (eligibility, coding, prior auth, routing classification) apply to all 2,000 claims/day (14,000/week) before the routing split occurs. The 65%/35% split applies only to step 5a (payment determination — 1,300/day admin path) and step 5b (clinical review — 700/day clinical path). The split is a stakeholder-negotiated target state estimate (Assumption A-2), not a measured current-state figure. Current-state routing volumes are unknown.*

| Work Stream | Pain Description | Volume (per week/month) | Pain Level | Lived-vs-Documented Gap | Key Data/Systems Involved | Delegation Signal | Candidate for Automation? |
|---|---|---|---|---|---|---|---|
| WS1 — Administrative adjudication | Eligibility verification requires cross-system lookup; mismatches require judgment to distinguish data errors from genuine coverage gaps | ~14,000/week derived (2,000/day × 7 — applies to all claims before routing split) | M | Standard path is algorithmic; manual handling for straightforward eligibility checks adds no value | Member eligibility system (unnamed — A-D0C-4), claim record | High: binary outcome for most cases; standard path is fully codifiable | **Yes — RPA or scripted rule sufficient for standard path; agent not warranted** |
| WS1 — Administrative adjudication | Coding validation requires code-diagnosis plausibility judgment beyond what formal crosswalk rules capture; implausible combinations require pattern recognition | ~14,000/week derived (2,000/day × 7 — applies to all claims before routing split) | H | Rules engines validate code existence; clinical plausibility judgment is a separate, more cognitively demanding task that formal rules do not fully address | Code lookup tools (unnamed — A-D0C-4), claim record | Medium: standard rule path is codifiable; edge-case plausibility patterns require classifier or ML-augmented approach | Yes — agent or rules-plus-classifier for plausibility flagging; HITL escalation for ambiguous cases |
| WS1 — Administrative adjudication | Prior auth completeness check requires multi-system cross-reference; partial matches (unit variances, date mismatches) require judgment | ~14,000/week derived (2,000/day × 7 — applies to all claims before routing split) | H | Documented process: verify auth exists. Lived process: verify auth precisely matches claim, resolve partial matches, decide on unit/date tolerance — each requiring judgment | Prior auth system (unnamed — A-D0C-4), claim record | Medium: matching logic is codifiable; tolerance thresholds are configurable rules; edge cases require HITL | Yes — agent with configurable matching rules; HITL escalation for partial matches outside tolerance |
| WS1 — Administrative adjudication | Payment determination has edge-case complexity for carved-out procedures and individually negotiated contract rates that may not be encoded in the fee schedule system | ~9,100/week derived (1,300/day × 7 — admin-path only, post-routing-split) | M | Standard fee schedule application is rule-bound; contract exceptions are handled via informal processor knowledge rather than encoded rules | Fee schedule system (unnamed — A-D0C-4), contract database (unnamed — A-D0C-4) | High for standard path; Medium for exceptions — standard path is fully automatable; exceptions require contract rule encoding first | Yes — agent for standard fee schedule path; HITL escalation for contract exceptions until rules are encoded |
| WS2 — Clinical review | No formal clinical content classifier — routing to physician review is currently done by processors using undocumented pattern recognition, producing inconsistent routing decisions | ~14,000/week derived (2,000/day × 7 — routing classification applies to all incoming claims; 4,900/week proceed to WS2 path) | H | **Primary lived-vs-documented gap:** the documented process names medical necessity review as a step; the lived process contains an undocumented prior routing decision that determines whether medical necessity review occurs at all | Claim record, processor judgment | Low for full automation; High for classifier-assisted routing with configurable confidence threshold | Yes — agent classifier with HITL escalation for low-confidence cases; definition of clinical content must be produced as a design output first (Assumption A-4) |
| WS2 — Clinical review | Physician reviewers manually assemble multi-source clinical context before applying medical necessity judgment; no pre-filled review packet exists | ~4,900/week derived | H | Documented output: physician makes a determination. Lived process: physician first spends undocumented time gathering clinical notes, prior auth records, and code history from multiple sources before any judgment is possible | Clinical notes system (unknown — A-D0C-7), prior auth system, claim codes | High: context assembly is codifiable structured data retrieval; medical necessity judgment requires physician sign-off | Yes — agent generates pre-filled review packet; physician makes final determination (URAC/NCQA hard stop) |
| Cross-cutting | Three claim formats (EDI 837, PDF, portal) require different handling; PDF and portal submissions require data extraction before processing logic can apply | All ~14,000 claims/week | M | Format normalisation work is not described in the documented four-step process; it is a prerequisite step that consumes processor time before adjudication begins | Intake channel, claim record | High: structured data extraction is a well-established automation problem; EDI 837 is already machine-readable | Yes — document processing pipeline (OCR + structured extraction) for PDF and portal; EDI 837 already structured |
| Cross-cutting | 41% denial appeal overturn rate (scenario.md) indicates systemic first-pass errors that generate rework, re-review cycles, and processor time on appeal processing | Unknown volume — appeal rate and average resolution time not stated in scenario | H | Denial appeals are documented as a metric; root cause decomposition (routing error vs. coding error vs. medical necessity error) is not documented and is unknown | Claim record, appeal record, denial reason codes | Medium: root cause classification is codifiable; resolution requires judgment and may require HITL | Partial — agent triage of appeal reason codes; root cause attribution helps prioritise upstream fixes (see Unknown U-6) |
| Cross-cutting | Cycle time running 9+ days against 7-day SLA penalty threshold (Exchange 3); penalties are currently live | All claims | H | The 7-day SLA and its penalty consequence are documented; the specific bottleneck steps driving the 9+ day average (clinical queue depth, async provider wait times, processing backlog) are not documented and are unknown | All systems; claims queue management | High: queue prioritisation and SLA-proximity alerting are codifiable agent behaviours | Yes — agent-driven queue management and SLA-proximity escalation |

**Pain level justification:**

| Level | Criteria applied |
|---|---|
| H (High) | Directly contributing to the current SLA penalty breach or the 41% denial overturn rate; or involves physician-judgment work with the highest per-error compliance consequence; or represents the primary undocumented gap in the process |
| M (Medium) | Contributes to cycle time or processing overhead but is more codifiable and has lower exception rates; the standard path can be addressed with rules-level automation |
| L (Low) | No pain points scored Low — every identified point either contributes to the SLA breach, the overturn rate, or is a prerequisite blocker for agent implementation |

*Note: WS1 eligibility verification and WS1 payment determination are scored M because the standard path for each is near-algorithmic and the judgment portion is confined to low-frequency edge cases. WS2 pain points are scored H because both involve the primary compliance constraint (physician sign-off) and the primary design gap (undefined clinical content criterion). Not all work streams are scored identically.*

---

## 3. ATX Discovery Dimensions — Assessment Per Work Stream

*Evidence for each cell is drawn from scenario_context.md. Where the scenario is silent, the cell reads "Unknown — requires discovery." All system references are assumptions per Section 6.*

| Work Stream | Volume & Time | Cognitive Nature | Data & Systems | Risk & Compliance | Organisational |
|---|---|---|---|---|---|
| **WS1 — Administrative adjudication** | ~2,000 claims/day for steps 1–4 (eligibility, coding, prior auth, routing — apply to all incoming claims); 1,300/day for step 5a (payment determination, admin-path only); no per-step time breakdown available; all time is included in the 35 min/claim overall average (scenario.md); claims review staff capacity of 20 is materially exceeded by the manual processing load at this volume | Primarily rule-bound (eligibility, fee schedule); judgment-intensive for coding plausibility and prior auth edge cases (assumption A-D0C-3); experience-dependent pattern recognition for coding validation | Three input formats (EDI 837, PDF, portal — scenario.md); multiple systems inferred but none named (A-D0C-4); manual cross-referencing between claim record and prior auth system assumed; data quality is unknown | Lower clinical risk than WS2; errors are recoverable via appeal process; the 41% overturn rate (scenario.md) confirms that upstream WS1 errors do reach the denial stage | Processor-owned end-to-end; no named escalation path in the scenario; James Liu (VP Operations) owns throughput and SLA performance; async waits (prior auth requests) create inter-organisational dependency on provider response |
| **WS2 — Clinical review** | ~700 claims/day derived (35% × 2,000 — assumption A-2); current per-claim physician time without pre-screening: Unknown — requires discovery; target with pre-screening: ~3 min/claim derived from Dr. Webb's 20 claims/hour (Exchange 3); this is a target state figure, not a current state measurement | Highest cognitive load in the process — requires clinical judgment for medical necessity determination; context assembly phase (gathering notes, prior auth, codes) is information retrieval, not clinical judgment, and is the primary recoverable time cost | Clinical notes source system: Unknown — requires discovery (A-D0C-7); prior auth, diagnosis codes, procedure codes required; multi-source context assembly before any determination; no system is named in the scenario | URAC/NCQA accreditation requires physician or advanced practice provider sign-off on every clinical determination (Dr. Marcus Webb, Exchange 2) — hardest compliance constraint in the engagement; wrong decisions carry legal and patient-care consequences | Physician-owned decision; processor routes to physician queue (WS2 depends on correct WS1-to-WS2 routing); Dr. Marcus Webb holds non-negotiable sign-off authority; clinical determination crosses into Dr. Webb's domain from James Liu's operational domain, creating a cross-functional handoff |

---

## 4. Cognitive Workload Hotspots

> **Hotspot [WS1-1]:** WS1 — Administrative adjudication — eligibility verification edge-case resolution
> **What the human does:** Determines whether a coverage discrepancy (date mismatch, plan termination, dependent status gap) is a data synchronisation error or a legitimate coverage gap. Applies knowledge of grace periods, plan structure, and member history to make a call on which action to take.
> **Why a machine can't trivially replace this today:** The resolution requires contextual reasoning about whether a data anomaly reflects a system lag versus a real eligibility gap — two outcomes that present identically in the claim record but require opposite responses. Without a pattern library of historical exception resolutions, a rule engine flags every discrepancy for manual review.
> **Delegation signal:** High codifiability for the standard path — binary outcome (eligible / not eligible) applies to the majority of claims. Edge cases are low-frequency (assumption A-D0C-2). For the standard path, a scripted rule or RPA is sufficient — an agent is **not warranted** for this step. For edge-case resolution, an agent with pattern-matching on historical exception resolutions could reduce escalation volume. Delegation archetype recommendation: **fully agentic** for standard path (RPA-level); **human-led + agent support** for exception resolution.

---

> **Hotspot [WS1-2]:** WS1 — Administrative adjudication — coding validation plausibility judgment
> **What the human does:** Reviews submitted ICD-10/CPT code combinations for clinical plausibility — not merely technical rule conformance, but whether the procedure and diagnosis make sense together given the provider specialty, place of service, and claim context. Detects patterns associated with upcoding, unbundling, or misapplication.
> **Why a machine can't trivially replace this today:** Clinical plausibility judgment is not fully captured in formal crosswalk rules. Processors are applying pattern recognition developed through experience — recognising unusual combinations that technical rules permit but that signal billing anomalies. The tacit component of this knowledge is not currently encoded anywhere in the system (assumption A-D0C-3).
> **Delegation signal:** Partially codifiable via a classifier trained on historical claim-coding patterns and known-anomalous combinations. Exception rate is unknown (Unknown U-4) — if > 20% of claims have non-obvious combinations, the agent requires robust HITL escalation as a primary function. Delegation archetype: **agent-led + human oversight** for pattern flagging; HITL review for flagged combinations.

---

> **Hotspot [WS2-1]:** WS2 — Clinical review — clinical content routing decision
> **What the human does:** Determines whether a claim contains clinical content requiring physician review, using informal pattern recognition on diagnosis codes, procedure codes, and provider specialty. No formal criterion guides this decision in the current process.
> **Why a machine can't trivially replace this today:** The routing criterion is undefined — "clinical content" has no operational definition in the current process (scenario_context.md Assumption A-4; Sarah Chen Exchange 3). An agent cannot be specified for this decision until the criterion is formally defined by Dr. Webb's CMO team. Additionally, error asymmetry makes threshold calibration critical: a false negative (routing clinical claim as administrative) is a compliance violation; a false positive (routing administrative claim as clinical) overloads the physician queue.
> **Delegation signal:** High delegation potential once the criterion is defined and the classifier is built and certified. The definition is the prerequisite design output — it must come from Dr. Webb's team before agent specification is possible. Delegation archetype: **agent-led + human oversight** with configurable confidence threshold; below threshold escalates to HITL classification queue.

---

> **Hotspot [WS2-2]:** WS2 — Clinical review — medical necessity determination
> **What the human does:** Physician applies medical necessity criteria to the clinical evidence — diagnosis codes, procedure codes, clinical notes, and prior auth history — synthesising multi-source information into a determination: approve, deny, or request additional information.
> **Why a machine can't trivially replace this today:** Medical necessity determination requires clinical judgment against evidence that may be ambiguous, incomplete, or contradictory. The decision carries direct patient impact and legal liability. URAC/NCQA accreditation explicitly requires licensed reviewer sign-off (Exchange 2, Dr. Marcus Webb). This is a hard delegation stop regardless of agent confidence level — it is a regulatory constraint, not a design preference.
> **Delegation signal:** **Not fully delegatable** under the current regulatory framework. This is a HITL hard stop. The agent opportunity is in pre-filling the physician's review context (context assembly, prior auth retrieval, code summary), reducing physician time-per-claim from an unknown current baseline to the ~3 min/claim target (derived from Dr. Webb's 20 claims/hour with pre-screening, Exchange 3). Delegation archetype: **human-led + agent support** — agent assembles context, physician decides.

---

## 5. Known Unknowns

> **Unknown [U-1]:** What is the operational definition of "clinical content" in Greenfield's current routing process — specifically, which diagnosis codes, procedure codes, or claim characteristics trigger clinical review today?
> **Why it matters for agent design:** The WS2 clinical content classifier cannot be specified or built without a formal definition. The definition determines training criteria, confidence threshold design, and the precise boundary between WS1 and WS2. Sarah Chen's Exchange 3 request ("Draft the requirements for what 'clinical flagging' means") confirms this definition does not currently exist in written form. This is the single most consequential open design question in the engagement.
> **How to discover it:** Interview Dr. Marcus Webb and members of the clinical review team; examine a sample of 50–100 recent clinical review decisions and ask reviewers to articulate what triggered clinical routing; review any denial reason code patterns for clinical vs. administrative split.

---

> **Unknown [U-2]:** What systems does Greenfield currently use for claims processing, prior authorisation management, eligibility verification, and clinical documentation — and which have accessible APIs?
> **Why it matters for agent design:** No systems are named anywhere in the scenario (scenario_context.md Section 6). System integration feasibility — API availability, data schemas, access controls, vendor constraints — is a prerequisite for all WS1 and WS2 agent architecture decisions. If key systems are black-box legacy platforms with no API, the build architecture must account for file-based integration, screen scraping, or custom connectors, which significantly changes cost, risk, and timeline.
> **How to discover it:** Request a systems inventory and data flow diagram from James Liu's operations team; ask for API documentation or vendor contacts for each named system; identify the clearinghouse or trading partner handling EDI 837 intake.

---

> **Unknown [U-3]:** What is the step-level time breakdown within the 35 min/claim average — specifically, how much time is spent on each of the four documented steps versus the undocumented routing decision and context assembly work?
> **Why it matters for agent design:** The 35 min/claim average (scenario.md) is not decomposed by step or claim type (administrative vs. clinical). The token economics model and headcount reduction case require per-step time baselines to calculate actual time savings per agent intervention. Without this, the economic model rests on an aggregate average that may misrepresent the per-step opportunity by an unknown margin.
> **How to discover it:** Request any existing time-tracking or productivity data from James Liu's operations team; conduct a time-motion study by shadowing processors through 10–15 complete claim cycles; ask processors to estimate time distribution across steps.

---

> **Unknown [U-4]:** What is the exception rate within WS1 administrative adjudication — what percentage of coding validation checks and prior auth verifications require escalation, supervisor consultation, or deviation from the standard rule path?
> **Why it matters for agent design:** If the exception rate exceeds 20%, the WS1 agent must handle exceptions as a primary function, not as edge cases. This shifts the delegation archetype, changes the HITL queue sizing requirement, and affects the economic model. An agent designed for a 5% exception rate will perform poorly if the true rate is 25%.
> **How to discover it:** Sample 100 recent WS1 claims and count how many required escalation or exception handling; ask processors to estimate what percentage of their day is spent on non-standard cases; review any existing quality assurance or audit logs for exception frequency.

---

> **Unknown [U-5]:** Where does clinical documentation (physician notes, procedure reports, clinical narratives) currently reside, and how do physician reviewers access it during WS2 review?
> **Why it matters for agent design:** The WS2 agent's primary value is assembling the pre-filled review packet. If clinical notes are stored in a separate EHR or document repository, the agent requires either API access to that system or a document extraction capability. If notes are faxed or transmitted as unstructured PDFs attached to the claim, the extraction problem is significantly harder and introduces data quality risk. The entire WS2 agent architecture depends on the answer.
> **How to discover it:** Shadow a physician reviewer through a complete WS2 claim cycle; observe which systems they open, in what order, and what information they are looking for before making a determination; ask explicitly: "Where do you find the clinical notes for this claim?"

---

> **Unknown [U-6]:** What is the root cause breakdown of the 41% denial appeal overturn rate — specifically, what proportion is attributable to WS1-to-WS2 misrouting, coding errors, incorrect medical necessity determinations, and other causes?
> **Why it matters for agent design:** The 41% overturn rate is the highest-signal quality metric in the scenario (scenario.md) and the clearest evidence that the current process has systemic accuracy problems. Without root cause decomposition, it is impossible to determine which agent intervention has the greatest impact. If the majority of overturns originate from misrouting (WS2-1), the classifier is the highest-leverage intervention. If the majority originate from coding errors (WS1-2), the coding validation agent takes precedence. The prioritisation of WS1 vs. WS2 agent development depends partly on this decomposition.
> **How to discover it:** Pull the last 3–6 months of denial appeals and their outcomes; classify by initial denial reason code and overturn reason; map each overturn category to the step in the adjudication process where the error was introduced.

---

> **Unknown [U-7]:** How many physicians or advanced practice providers are currently dedicated to WS2 clinical review, and what is the current clinical review queue depth and average physician throughput per day without agent pre-screening?
> **Why it matters for agent design:** Dr. Webb's 20 claims/hour estimate (Exchange 3) assumes pre-screening is in place. The current throughput without pre-screening is unknown. The number of clinical reviewers determines whether the HITL queue is currently a bottleneck and whether the proposed agent system can clear the projected ~700 clinical claims/day within the 6–7 day target cycle time with existing physician capacity. If physician headcount is insufficient at 20 claims/hour, the staffing model must account for it regardless of agent performance.
> **How to discover it:** Request current clinical review staffing data from Dr. Marcus Webb; review physician review queue depth and age-of-queue metrics for the past 90 days; calculate required physician capacity at 20 claims/hour for 700 claims/day and compare to available headcount.

---

## 6. Assumption Log

> **Assumption [A-D0C-1]:** PDF and portal claim submissions require additional data extraction work before processing can begin, compared to EDI 837 which arrives pre-structured.
> **Why it matters:** If PDF extraction is a significant per-claim time cost, a document processing pipeline (OCR + structured extraction) may be a prerequisite for WS1 agent input data quality. It also affects what percentage of claims arrive in a machine-readable state today.
> **If wrong:** If Greenfield already has a normalisation layer that converts all formats to structured data before processors see them, this overhead is already absorbed and the agent's input quality is higher than assumed.
> **Confidence:** Medium — three formats are listed in scenario.md; the handling difference is inferred from the structural difference between EDI 837 and PDF.

---

> **Assumption [A-D0C-2]:** Processors apply informal personal heuristics for ambiguous eligibility edge cases rather than following a formal documented escalation protocol, producing handling inconsistency across the processor team.
> **Why it matters:** If processors are individually resolving edge cases without documentation, the exception patterns that would drive agent exception handling are not captured or structured anywhere. This makes eligibility edge-case training data harder to assemble and means the agent's edge-case behaviour cannot be validated against a ground-truth protocol.
> **If wrong:** If a formal escalation path for eligibility edge cases exists and is consistently followed, the exception patterns are more structured, training data is more available, and the agent edge-case design is simpler.
> **Confidence:** Low — inferred from the general pattern of informal workarounds in high-volume claims environments and the absence of any described escalation path in the scenario; not directly stated.

---

> **Assumption [A-D0C-3]:** Coding validation involves significant judgment for non-obvious code-diagnosis combinations, beyond technical rules lookup — processors are applying clinical plausibility pattern recognition developed through processing experience.
> **Why it matters:** If coding validation is primarily a rules lookup with low judgment content, it is a simpler automation target (rules engine sufficient). If judgment content is high, the agent requires a classifier, and the exception rate becomes a critical design parameter. The wrong assumption here would cause either over-engineering (building an agent when a rules engine suffices) or under-engineering (building a rules engine that fails on the plausibility judgments that constitute most of the actual work).
> **If wrong:** If coding validation is fully rule-bound with no plausibility judgment component, WS1 simplifies significantly and the fully agentic archetype is more defensible.
> **Confidence:** Medium — supported by domain knowledge from D0A (domain research); the scenario lists coding validation as a required step but provides no detail on the cognitive complexity involved.

---

> **Assumption [A-D0C-4]:** The scenario names no systems. All system references in this document — eligibility system, prior auth system, code lookup tools, fee schedule, clinical notes repository, medical necessity criteria tools — are assumptions based on standard healthcare claims processing environments.
> **Why it matters:** System integration feasibility is a prerequisite for the entire agent architecture design. Every agent that touches an external system depends on API availability, data schema quality, and access controls that are entirely unknown at this stage.
> **If wrong:** Any specific system reference in this document could be wrong — Greenfield may use different platforms, may have already consolidated onto fewer systems, or may use a single integrated claims management platform that makes multi-system cross-referencing unnecessary.
> **Confidence:** Low — no systems are named anywhere in the scenario (scenario_context.md Section 6). This assumption applies universally to all system references.

---

> **Assumption [A-D0C-5]:** The current routing decision (clinical vs. administrative) is made by processors using undocumented pattern recognition. No formal clinical content criterion exists in written form.
> **Why it matters:** If this assumption is wrong and formal routing criteria do exist in a policy document, the WS2 classifier design starts from a higher baseline (encode existing criteria rather than build from scratch). The definition phase is shorter and the CMO certification process is simpler.
> **If wrong:** If formal routing criteria exist, the clinical content classifier specification phase is significantly shorter and the design risk is lower.
> **Confidence:** Medium — Sarah Chen's Exchange 3 message requesting that "clinical flagging" criteria be defined strongly implies they do not currently exist in written form; treating this as medium rather than high confidence because the absence of a written document does not preclude the existence of an informal protocol.

---

> **Assumption [A-D0C-6]:** Contract-specific fee schedule exceptions (carved-out procedures, individually negotiated out-of-network rates) are handled by processors using informal knowledge rather than encoded rules in the payment system.
> **Why it matters:** If WS1 payment determination exceptions are not encoded in any system, the agent cannot access them and will either escalate all exceptions or make incorrect payment decisions on contract edge cases. Encoding these rules is a prerequisite for a fully agentic payment determination path.
> **If wrong:** If all contract exceptions are encoded in the existing payment system, the payment determination step is more automatable and the agent has fewer HITL escalation cases.
> **Confidence:** Low — inferred from operational patterns typical in payer environments; not stated in the scenario.

---

> **Assumption [A-D0C-7]:** Clinical documentation (physician notes, operative reports, clinical narratives) submitted by providers is stored in a system separate from the claims record and requires manual retrieval by physician reviewers during WS2 review.
> **Why it matters:** If clinical notes are not co-located with the claim record, the WS2 pre-filling agent requires API access to a separate clinical documentation system (unknown) or document ingestion capabilities. The integration complexity and data quality risk for the WS2 agent depends entirely on where notes live and in what format.
> **If wrong:** If clinical notes are attached directly to the claim record (e.g., as documents in a unified claims management platform), the context assembly function is significantly simpler and the integration surface is smaller.
> **Confidence:** Low — common pattern in payer operations (claims and clinical documentation typically live in separate systems); not stated in the scenario.
