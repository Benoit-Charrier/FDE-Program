# Deliverable D0A — Domain Research: Healthcare Claims Processing / Health Insurance Payer Operations

**Domain:** Healthcare claims processing — the adjudication of medical claims submitted by providers against a health plan member's coverage terms by a payer or third-party administrator (TPA).

*Produced as a prior. Sections 1–5 written from training knowledge before reading sealed scenario detail. Gaps are named in section 6.*

---

## 0. Executive Summary

- The domain's cognitive hotspot is the **clinical content classification decision** — the gate that separates administrative adjudication (deterministic, rule-bound) from medical necessity review (judgment-heavy, requiring licensed clinical reviewers); the entire auto-adjudication rate depends on whether this classification is reliable.
- The most important compliance constraint is the **HIPAA / CMS / URAC triad**: all claim data is PHI requiring access-controlled handling; CMS mandates processing timelines with financial penalties for breach; URAC/NCQA accreditation standards require that clinical necessity denials be made (or reviewed) by a licensed clinical reviewer — creating a hard delegation stop that cannot be bypassed regardless of model confidence.
- The highest-leverage agentic opportunity is **auto-adjudication of the administrative claim path** (coding validation, eligibility, completeness, non-clinical payment determination) — the single biggest unknown is whether the clinical/administrative boundary in incoming claims is reliably detectable from structured fields alone (ICD-10 codes, procedure codes), or whether unstructured clinical notes must be read to make the classification accurately.

---

## 0b. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Domain overview](#1-domain-overview)
  - [1a. What this domain does](#1a-what-this-domain-does)
  - [1b. Typical workflow](#1b-typical-workflow)
  - [1c. Common failure modes](#1c-common-failure-modes)
- [2. Regulatory and compliance context](#2-regulatory-and-compliance-context)
- [3. Cognitive work patterns typical to this domain](#3-cognitive-work-patterns-typical-to-this-domain)
  - [3a. Where skilled attention is typically consumed](#3a-where-skilled-attention-is-typically-consumed)
  - [3b. Lived vs. documented gaps typical to this domain](#3b-lived-vs-documented-gaps-typical-to-this-domain)
- [4. ATX dimension pre-assessment](#4-atx-dimension-pre-assessment)
- [5. Hypothesis questions for discovery](#5-hypothesis-questions-for-discovery)
- [6. Assumption log](#6-assumption-log)

---

## 1. Domain Overview

### 1a. What This Domain Does

Health insurance payers — insurers, health plans, and third-party administrators — adjudicate medical claims submitted by healthcare providers (hospitals, physician groups, labs, imaging centers). The core function is to determine whether a submitted claim is covered under the member's benefit plan, coded correctly, medically necessary, and what the payer owes the provider after applying contractual rates, deductibles, copays, and coordination-of-benefits rules. Primary knowledge workers are **claims processors** (who handle administrative adjudication at volume), **clinical reviewers** (MDs, RNs, or licensed clinical auditors who handle medical necessity determinations), and **coding specialists** (who audit ICD-10/CPT/HCPCS coding accuracy and flag billing irregularities). Claims arrive as EDI 837 transactions from clearinghouses, paper claims converted to electronic format, and portal submissions; they exit as Explanation of Benefits (EOB) documents, Electronic Remittance Advice (ERA/835) payments, or denial letters with appeal rights. Volume in mid-size operations runs in the thousands of claims per day; large payers process millions per month. Work is continuous — claims arrive daily from thousands of providers and must be adjudicated within regulatory timelines (14–30 days for clean claims under CMS; state prompt payment laws vary).

### 1b. Typical Workflow

*Domain-typical workflow — client deviations will surface in discovery.*

1. **Claim receipt and intake** — EDI 837 transaction or paper claim received via clearinghouse or portal; parsed, deduplicated, assigned internal claim ID, and queued. `[execution]`
2. **Front-end edits** — automated format validation: required fields present, valid code formats, appropriate modifiers, correct transaction structure per HIPAA 5010 standards. Technically malformed or obviously incomplete claims are rejected here and returned to the provider. `[execution]`
3. **Eligibility verification** — confirm the member was covered on the date of service, identify the correct plan, and pull applicable benefit parameters (deductible, copay, out-of-pocket maximum, network status of rendering provider). `[verification]`
4. **Provider credentialing check** — verify the rendering provider is contracted with the plan for the submitted service type; confirm the provider's NPI is active and that the billed specialty matches the contract. `[verification]`
5. **Coding validation** — verify that ICD-10 diagnosis codes support the procedure codes (CPT/HCPCS); check for unbundling (billing separately for procedures that should be bundled), upcoding (billing a higher-complexity code than performed), and mutually exclusive code combinations. This step is rule-based but requires code-set knowledge. `[verification + judgment]`
6. **Clinical/administrative classification** — determine whether the claim contains clinical content requiring medical necessity review, or whether it can be adjudicated on administrative criteria alone. This is the gate that routes claims to the auto-adjudication path vs. the clinical review path. `[judgment]`
7. **Medical necessity review (clinical path only)** — licensed clinical reviewer applies coverage criteria (InterQual, MCG, or payer-specific clinical guidelines) against the submitted documentation to determine if the service is medically necessary and covered. `[judgment]`
8. **Benefit determination and payment calculation** — apply plan terms: allowed amount per fee schedule, network discount, deductible/copay application, coordination of benefits with other payers if applicable. Calculate payer liability. `[execution]`
9. **Payment or denial issuance** — generate payment via 835/ERA, or issue denial with appropriate CARC/RARC denial codes, denial reason narrative, and appeal rights notice per ACA and state requirements. `[execution]`
10. **Appeal handling (as triggered)** — if provider or member appeals a denial, reopen claim for independent clinical review; apply external review rules where required by state law. `[judgment]`

### 1c. Common Failure Modes

- **Coding error — data and judgment failure.** ICD-10/CPT combinations are clinically invalid or fail to support medical necessity (e.g., a procedure code for a surgical repair paired with a diagnosis code for a condition that does not require surgery). Results in incorrect auto-denial or incorrect auto-payment; high denial overturn rates on appeal trace back to this step.
- **Stale eligibility data — data failure.** Member coverage has changed (termination, plan switch, dependent aging out) but the eligibility system has not updated; claim is processed against the wrong benefit or denied for a member who is actually covered. Requires manual correction and reprocessing.
- **Clinical/administrative misclassification — judgment failure.** A claim coded to look administrative (routine lab, standard office visit) contains attached clinical notes documenting a complex condition that should trigger clinical review. Processor routes to auto-adjudication; clinical content is never reviewed; claim is either over-paid or incorrectly approved. The inverse — flagging routine claims as clinical — floods the reviewer queue without adding value.
- **Prior authorization mismatch — coordination failure.** A service requiring prior authorization was approved in the PA system, but the PA reference number is absent from the claim submission or fails to match on adjudication. Claim is denied for "no PA on file" when a valid authorization exists. Requires manual lookup to resolve.
- **Duplicate claim processing — process failure.** Provider resubmits a claim (common after initial rejection), and the deduplication logic fails to recognize the resubmission as the same claim; payer issues two payments for the same service. Recovery is manual and relationship-damaging.

---

## 2. Regulatory and Compliance Context

| Framework / Constraint | What it governs | Agent design implication |
|------------------------|----------------|--------------------------|
| **HIPAA EDI Transaction Standards (5010)** | Format and content requirements for electronic claims (837), eligibility (270/271), remittance (835), prior auth (278) | Agent must parse and generate HIPAA-compliant transactions; any non-standard field handling (custom segments, payer-specific extensions) requires explicit contract |
| **HIPAA Privacy Rule / Security Rule** | All claim data is PHI (diagnosis codes, treatment data, member identifiers, provider details); requires access controls, audit logs, BAAs with vendors | No claim PHI in uncontrolled contexts; all agent interactions with claim data must be logged; any third-party model processing claim data requires a signed Business Associate Agreement |
| **ACA §2719 — Appeals and External Review** | Mandates internal and external appeal rights; timelines for appeal decisions (72 hours for urgent care, 30–60 days for standard); notices must include reason codes and appeal instructions | Agent-generated denial letters must include correct CARC/RARC codes, accurate appeal rights language, and filing deadlines; missing or incorrect notice language is a regulatory violation |
| **CMS Medicare Advantage / Medicaid Managed Care regulations** | Clean claim payment within 14 days (electronic) or 30 days (paper); denial processing timelines; prior auth rules under 2024 CMS interoperability rule (electronic PA via FHIR) | Agent must track claim age relative to regulatory SLA; escalate claims approaching deadline; prior auth integration must handle FHIR API standards for CMS-covered lines of business |
| **State prompt payment laws** | Vary by state: typically 30–45 days for clean claims; financial penalties (interest on late payment) for breach; some states (CA, NY, TX) have additional requirements | Agent routing must be state-aware; claim SLA timers must use originating-state rules, not a single national rule |
| **ERISA (Employee Retirement Income Security Act)** | Governs self-funded employer health plans; specific notice requirements, appeal timelines, and fiduciary standards distinct from ACA individual/small-group rules | Agent must distinguish ERISA plan type from ACA-regulated plans; denial processing and appeal pathways differ materially |
| **ICD-10-CM / CPT / HCPCS code sets** | Diagnostic coding (ICD-10), procedural coding (CPT), and supplies/drugs/equipment (HCPCS Level II); annual updates; CMS and AMA maintain separate authorities | Coding validation is a deterministic lookup — finite code sets with known valid combinations and edit rules (CCI edits). Highest-confidence automation target in the domain |
| **URAC / NCQA accreditation standards** | Health plan accreditation requires that clinical necessity denials be reviewed or made by a licensed clinical reviewer (MD, RN, or equivalent); denials cannot be issued solely on algorithmic output | **Hard delegation stop:** An agent cannot be the final decision-maker on a clinical necessity denial. AI classification and pre-filling are delegatable; the denial sign-off is not — licensed reviewer must confirm |

**Hardest delegation stop:** Clinical necessity denial without licensed reviewer sign-off. This is both a URAC/NCQA accreditation requirement and a litigation risk (wrongful denial of care). The agent's autonomy ceiling is auto-adjudication of administrative claims and routing + pre-filling for clinical claims — not clinical denial issuance.

---

## 3. Cognitive Work Patterns Typical to This Domain

### 3a. Where Skilled Attention Is Typically Consumed

> **Cognitive Hotspot [CH-1]: Clinical/administrative classification — routing the claim to the correct adjudication path**
> **Cognitive type:** Pattern recognition + exception handling
> **Why it resists simple automation:** The classification must integrate structured fields (ICD-10 codes, CPT codes, place of service) with unstructured content (attached clinical notes, operative reports, physician narratives). A claim can be coded to look routine while the attached notes describe a complex condition. Conversely, a high-complexity procedure code may be for a standard, non-clinical administrative reason. The boundary is not a lookup — it requires reading clinical context.
> **What would make it delegatable:** If the classification can be performed reliably on structured fields alone (ICD-10 category + CPT category + place of service = sufficient signal), then Haiku-tier deterministic logic handles it. If clinical notes must be read, Sonnet-tier NLP is required — with a confidence threshold below which escalation fires automatically, preventing silent misclassification in either direction.

> **Cognitive Hotspot [CH-2]: Medical necessity determination against clinical guidelines**
> **Cognitive type:** Judgment + synthesis
> **Why it resists simple automation:** The reviewer must match the submitted clinical documentation against InterQual or MCG criteria — which are themselves judgment frameworks, not rigid rules. The same diagnosis code can be approved or denied depending on what the clinical notes say about severity, prior treatment attempts, and documented failure of alternative treatments. The criterion is: "is this service necessary for *this patient's* clinical situation?" — a question that requires reading and interpreting the documentation.
> **What would make it delegatable:** Only with a licensed clinical reviewer in the loop. The agent can retrieve the relevant guideline criteria, extract key facts from the clinical notes, and pre-fill a review packet reducing the reviewer's read time from 35 minutes to 3–5 minutes. Full delegation to the agent without human sign-off violates URAC standards.

> **Cognitive Hotspot [CH-3]: Denial reason selection and appeal-defensibility assessment**
> **Cognitive type:** Synthesis + decision-making
> **Why it resists simple automation:** Selecting the correct CARC (Claim Adjustment Reason Code) and RARC (Remittance Advice Remark Code) requires knowing not just why the claim was denied, but which code will accurately represent that reason to the provider, hold up under appeal, and comply with state-specific notice requirements. Experienced reviewers know that certain denial codes trigger automatic appeals and require more thorough documentation; others close cleanly.
> **What would make it delegatable:** For the administrative path, denial codes are deterministic given the failure type (e.g., eligibility failure → specific CARC). For clinical denials, code selection requires the human reviewer's judgment about how to document the clinical reasoning. Administrative denial code assignment is delegatable; clinical denial documentation is not.

> **Cognitive Hotspot [CH-4]: Coordination of benefits triage**
> **Cognitive type:** Verification + exception handling
> **Why it resists simple automation:** When a member has multiple payers (employer plan + Medicare, or two employer plans), determining primary/secondary responsibility requires checking the member's coverage declaration, Medicare Secondary Payer rules (for Medicare involvement), and the birthday rule (for dependent coverage). Errors create a payment loop — primary pays, secondary overpays, primary recoups, provider disputes the recoupment.
> **What would make it delegatable:** COB determination is rule-based when data is clean and current. An agent can execute the logic if the eligibility system contains up-to-date COB data. The failure mode is stale or missing other-coverage data — which is a data infrastructure problem, not an inherent judgment problem.

### 3b. Lived vs. Documented Gaps Typical to This Domain

> **Gap [G-1]: Clinical guidelines are applied inconsistently across reviewers**
> **Why it exists:** InterQual and MCG criteria provide frameworks, but reviewers interpret ambiguous documentation differently. There is no feedback loop connecting denial outcomes to appeal results — a reviewer who denies claims that are consistently overturned on appeal does not receive systematic correction signals. Denial rates for the same diagnosis code can vary by 2–3x across reviewers at the same organisation.
> **Agent design implication:** An agent pre-filling the review packet with the relevant guideline criteria and extracted documentation creates an opportunity to reduce this variance — but only if the criteria extraction is accurate. Inconsistent pre-filling introduces a different kind of variance. Validation design must test inter-reviewer agreement on agent-prepared packets vs. raw claims.

> **Gap [G-2]: "Administrative" claims contain embedded clinical content that processors miss**
> **Why it exists:** Processors trained on the administrative path use a mental shortcut: certain procedure codes (routine labs, standard office visits, preventive care) are treated as administrative without reading attachments. Attached clinical notes — which would trigger clinical review — are present but ignored. This produces a systematic false-negative in the clinical/administrative classification step.
> **Agent design implication:** A classifier trained only on procedure code and diagnosis code patterns will replicate this gap. Any auto-adjudication architecture must decide: does the classifier read attached notes, or does it treat "no notes required" as a safe assumption for certain code categories? This is the primary spec risk for the clinical content classifier.

> **Gap [G-3]: Prior authorization data does not travel reliably with the claim**
> **Why it exists:** PA is often managed in a separate system (or by a separate utilisation management team) from claims adjudication. When a provider submits a claim, the PA reference number must be manually entered or transmitted in a specific EDI field. Providers frequently omit it; the claims system cannot look it up automatically across systems. Result: valid PAs are not matched at adjudication, and claims are denied for missing authorisation that actually exists.
> **Agent design implication:** Auto-adjudication logic that checks for PA must either query the PA system directly (requires API integration) or flag "PA required, not found" as a human-verification item rather than an auto-denial. Treating a missing PA reference as a definitive denial without checking the PA system produces incorrect denials at scale.

---

## 4. ATX Dimension Pre-Assessment

| ATX Dimension | Domain-typical signal | What to probe in discovery |
|---------------|----------------------|---------------------------|
| **Volume & Time** | Very high volume (thousands of claims per day at mid-size operations); continuous flow with regulatory SLA pressure (14–30 days); per-claim time is bimodal: administrative path is minutes, clinical path is 15–45 minutes. Volume makes automation critical; the processing time differential between paths is the core economics argument. | Daily claim volume; current average processing time end-to-end; percentage of claims that breach SLA; staffing headcount vs. incoming volume trend |
| **Cognitive Nature** | Bimodal: administrative adjudication is highly rule-bound and deterministic (coding edits, eligibility, format validation — finite rules against finite code sets); clinical necessity review is judgment-heavy and requires licensed reviewers. The classification gate between them is the critical design problem. | What percentage of claims go to clinical review today? How is the routing decision made? Who makes it? |
| **Data & Systems** | Claims data is highly standardised (EDI 837, ICD-10, CPT, fee schedules) — this is the most structured data environment in healthcare. Clinical documentation (attached notes, operative reports) is unstructured. The structured/unstructured split maps cleanly to a deterministic-Haiku / NLP-Sonnet architecture tier distinction. | Claims management platform (TriZetto/Facets/Optum?); API availability; whether clearinghouse handles front-end edits before claims reach the adjudication system; PA system integration |
| **Risk & Compliance** | High throughout: all data is PHI; CMS timeline penalties; URAC/NCQA accreditation requires licensed reviewer on clinical denials; ACA appeal rights create legal exposure on incorrectly denied claims. The accreditation requirement is the binding delegation stop — it cannot be engineered around, only designed within. | Which lines of business (Medicare Advantage, Medicaid, commercial)? URAC/NCQA accredited? Recent regulatory audits or penalty events? |
| **Organisational** | Claims processors (volume workers), clinical reviewers (the scarce resource — licensed MDs/RNs), coding specialists (audit and quality), appeals team. The scarce resource is clinical reviewer time. Any architecture that increases clinical reviewer throughput — rather than adding volume to the queue — has direct economic value. | How many clinical reviewers? What is their current throughput per day? What fraction of their time is spent on reading documentation vs. making the actual determination? |

**Most constraining dimension: Risk & Compliance.** The URAC/NCQA requirement for licensed reviewer sign-off on clinical necessity denials sets the autonomy ceiling for the entire architecture. Unlike the staffing domain where the compliance gate was a data quality problem (could be solved with better credential infrastructure), this constraint cannot be removed by better data — it is structural and accreditation-linked. Every agent design decision must be oriented around *protecting and accelerating the reviewer*, not replacing the review.

---

## 5. Hypothesis Questions for Discovery

> **HQ-1: How is the clinical/administrative routing decision currently made — by whom, using what criteria, and how consistently?**
> **Hypothesis:** Routing is done by experienced processors using a mental model of which procedure code categories "always" require clinical review, rather than a documented rule set. New processors route incorrectly at a higher rate.
> **If confirmed:** The routing criteria must be extracted and codified as part of the classifier spec; the classifier is replacing tacit knowledge, not a documented rule.
> **If disconfirmed:** If routing criteria are already documented as a rule set, the classifier is automating a known procedure — lower design risk, higher confidence in the training signal.

> **HQ-2: What percentage of claims that go to clinical review are ultimately approved without modification?**
> **Hypothesis:** A significant percentage (30–40%) of claims routed to clinical review are approved without any substantive reviewer intervention — they were misclassified as clinical when they were effectively administrative.
> **If confirmed:** False-positive rate in the current routing is high; an agent classifier that reduces false positives has direct economic value (fewer reviewer-hours on claims that don't need clinical judgment).
> **If disconfirmed:** If most clinical-routed claims genuinely require reviewer judgment, the focus shifts to accelerating reviewer throughput (pre-filling) rather than reducing clinical routing volume.

> **HQ-3: What information does a clinical reviewer actually use to make the necessity determination — the full claim file, or a subset?**
> **Hypothesis:** Reviewers primarily use 3–4 specific data points: the primary diagnosis code, the procedure's clinical indication in the notes, evidence of prior treatment attempts, and the applicable guideline criteria. Most of the claim file is not consulted.
> **If confirmed:** A pre-filled review packet containing only these elements can reduce reviewer read time from 35 minutes to 5 minutes without information loss — this is the HITL acceleration design.
> **If disconfirmed:** If reviewers use the full file unpredictably, pre-filling is harder to design without risk of omitting something material.

> **HQ-4: What claims management system is in use, and does it expose an API for claim data retrieval and status updates?**
> **Hypothesis:** The system is a major platform (TriZetto/Facets, Optum ClaimLogic, or similar) with documented API capabilities, but integration requires custom work and the API may not expose all fields needed for clinical classification.
> **If confirmed:** Integration is feasible but requires scoping; API field mapping must be part of the spec.
> **If disconfirmed (no API):** Agent must operate on exported data or require system modification — significant scope risk.

> **HQ-5: Are clinical notes and supporting documentation attached to the EDI 837 transaction, or do they arrive separately and require manual association?**
> **Hypothesis:** Clinical documentation arrives separately from the claim (fax, portal upload, or separate EDI 275 transaction) and is matched to the claim ID manually or through a document management system with variable accuracy.
> **If confirmed:** Document association is a prerequisite for clinical classification — the agent cannot classify clinical content it cannot read. This is a data infrastructure dependency that must be resolved before clinical classifier scope can be activated.
> **If disconfirmed:** If documentation reliably travels with the claim in a queryable format, clinical classification can begin without a separate document-matching phase.

> **HQ-6: What is the current denial appeal overturn rate, and which denial categories account for the majority of overturns?**
> **Hypothesis:** The overall overturn rate is 35–45%, concentrated in medical necessity denials — indicating that first-pass clinical review is applying criteria too restrictively, or that documentation quality is insufficient at the time of initial adjudication.
> **If confirmed:** Pre-filling the reviewer packet with documentation at the time of initial review (rather than waiting for appeal) would reduce overturns — a quality argument that strengthens the business case beyond throughput.
> **If disconfirmed:** If overturn rate is low, the quality problem is elsewhere and the business case rests primarily on speed and headcount.

> **HQ-7: How is prior authorization managed — same system as claims, separate system, or manual?**
> **Hypothesis:** PA is managed in a separate utilisation management system with no real-time API integration to the claims adjudication platform; PA matching at adjudication is manual or requires processor lookup.
> **If confirmed:** Auto-adjudication logic must include a PA lookup step via API integration or flag "PA status unverified" for human review — it cannot treat missing PA reference as a definitive denial.
> **If disconfirmed:** If PA and claims are integrated in a single system with automatic matching, one integration point is eliminated from the agent's scope.

> **HQ-8: What is the current clean claim rate — the percentage of submitted claims that pass all front-end edits on first submission?**
> **Hypothesis:** Clean claim rate is 70–80%; the remaining 20–30% require provider correction and resubmission, adding processing overhead that is invisible in per-claim time metrics.
> **If confirmed:** Front-end edit automation has already solved the easy part of the problem; the agent's value is in the adjudication step downstream of clean claim acceptance, not in fixing submission quality.
> **If disconfirmed:** If clean claim rate is low (below 60%), provider education and submission quality improvement may be higher-ROI than adjudication automation, and the scope should be revisited.

> **HQ-9: What lines of business does the operation process — commercial fully-insured, self-funded ERISA, Medicare Advantage, Medicaid managed care?**
> **Hypothesis:** Multiple lines of business are processed in the same system with different regulatory requirements applied by processor knowledge rather than system-enforced routing.
> **If confirmed:** The agent must be line-of-business-aware; a single adjudication logic does not apply across all lines. Regulatory SLA timers, denial codes, and appeal rights language differ materially.
> **If disconfirmed:** Single line of business simplifies the regulatory logic significantly.

> **HQ-10: How long has the current auto-adjudication rate (22%) been stable, and what types of claims are currently auto-adjudicated?**
> **Hypothesis:** Auto-adjudication is concentrated in a narrow set of claim types (routine labs, certain preventive codes, standard office visits with clean coding) that were manually whitelisted; the rate has been stable because no one has systematically expanded the whitelist.
> **If confirmed:** The opportunity is to expand the auto-adjudication logic from a static whitelist to a learned classifier — moving from 22% to 80%+ is achievable with better classification, not just more rules.
> **If disconfirmed:** If auto-adjudication has been growing organically and plateaued at 22%, there may be a structural floor — a category of claims that genuinely cannot be auto-adjudicated regardless of classifier quality.

> **HQ-11: What is the consequence — financially and regulatorily — of a false negative in clinical classification (a clinical claim auto-adjudicated without physician review)?**
> **Hypothesis:** A false negative that results in auto-approval of a clinical claim creates payer financial exposure (overpayment for non-covered service) but limited direct liability; a false negative that results in auto-denial of a clinical claim creates wrongful denial liability, appeal burden, and URAC compliance risk.
> **If confirmed:** Auto-approval is higher risk than auto-approval deferral; confidence threshold design must be asymmetric — err toward routing to HITL rather than auto-approving when uncertain.
> **If disconfirmed:** If both error directions carry equivalent weight, confidence threshold calibration is a symmetric optimisation problem.

---

## 6. Assumption Log

> **Assumption [A-1]:** Clinical/administrative split is approximately 30–40% clinical, 60–70% administrative — consistent with standard industry distributions for commercial payers.
> **Why it matters:** This split determines the volume routed to the clinical path and the denominator of the economics model; if clinical volume is higher, headcount savings are lower and reviewer throughput becomes the dominant constraint.
> **If wrong:** A higher clinical percentage (>50%) would shift the economic case from "eliminate administrative headcount" to "accelerate reviewer throughput" — different success metrics and different agent design emphasis.
> **Confidence:** Medium — industry benchmarks support this range; client-specific split depends on member population mix (older or sicker populations generate more clinical claims).
> **How to validate:** Ask: "Of the claims that reach adjudication, what percentage go to clinical review? How is that routing decision made?"

> **Assumption [A-2]:** Clinical reviewers spend the majority of their per-claim time reading documentation to establish context, not on the determination itself.
> **Why it matters:** If true, pre-filling the review packet with extracted context directly reduces reviewer time — the HITL acceleration design has high leverage. If false (the determination itself is the time cost), pre-filling has lower impact.
> **If wrong:** If reviewers spend most time on the decision (consulting guidelines, checking coverage criteria), the agent must surface the relevant guideline text and coverage determination logic — a different kind of pre-filling.
> **Confidence:** Medium — consistent with interviews and operational benchmarks in the domain; time-motion studies of clinical review typically show 60–70% of time on document review.
> **How to validate:** Ask: "Walk me through what you look at when you review a clinical claim. What are you looking for, and where do you spend the most time?"

> **Assumption [A-3]:** ICD-10 diagnosis codes and CPT procedure codes together are sufficient signal to classify most claims as clinical vs. administrative, without reading clinical notes.
> **Why it matters:** If structured codes are sufficient, the classifier is a deterministic lookup (Haiku-tier). If clinical notes must be read, the classifier requires NLP (Sonnet-tier) and the document-association dependency in [G-3] becomes a blocker.
> **If wrong:** Structured-code-only classification will produce the exact Gap [G-2] failure mode — administrative-looking claims with embedded clinical content will be incorrectly auto-adjudicated.
> **Confidence:** Low — this is the central architectural assumption. It needs to be validated against a sample of claims where code-based classification and notes-based classification disagree.
> **How to validate:** Ask to see a sample of claims that were initially routed as administrative but later corrected; examine whether the structured codes alone would have indicated clinical content.

> **Assumption [A-4]:** InterQual or MCG criteria are the operative clinical review guidelines (industry standard for mid-to-large payers).
> **Why it matters:** The pre-filling design must extract the relevant guideline criteria for the claim's diagnosis and procedure; if custom or proprietary guidelines are in use, the extraction logic must be built differently.
> **If wrong:** Payer-specific clinical criteria that are not publicly available require different document sourcing in the pre-filling architecture.
> **Confidence:** Medium — InterQual/MCG are the dominant standards for commercial payers; Medicare uses LCDs (Local Coverage Determinations) which are different in structure and access method.
> **How to validate:** Ask: "What clinical criteria do your reviewers use to make necessity determinations? Are they InterQual, MCG, or something else?"

> **Assumption [A-5]:** The claims management platform has an accessible API that allows programmatic retrieval of claim data and status writes.
> **Why it matters:** All agent integrations in the pipeline depend on this. Without an API, the agent must work with exported data batches, which introduces latency and eliminates real-time adjudication capability.
> **If wrong:** No API requires either a platform integration project (scope risk) or a batch-processing architecture that cannot meet real-time SLA requirements.
> **Confidence:** Low — major platforms (TriZetto, Facets, Optum) have API capabilities, but API access is often licensed separately and documentation quality varies widely; many production deployments do not have API integration enabled.
> **How to validate:** Ask: "Does your claims system have an API? Is it currently used for any integrations? Who manages the integration layer?"

> **Assumption [A-6]:** Denial overturn rate on appeal (~40%) is primarily driven by medical necessity denials, not administrative errors.
> **Why it matters:** If overturns are concentrated in clinical denials, the pre-filling design (better documentation surfaced at initial review) directly reduces the overturn rate — a quality co-benefit that strengthens the business case. If overturns are from administrative errors (eligibility, coding), the agent's administrative path validation is the fix, not the clinical pre-filling.
> **If wrong:** Administrative-error overturns are addressed by improving the administrative path validation logic — a different but still delegatable problem.
> **Confidence:** Medium — industry data consistently shows medical necessity as the primary category of appealed and overturned denials, but the client-specific distribution may differ.
> **How to validate:** Ask: "When you look at your denial overturns, what categories are most common? Medical necessity, coding, eligibility, or something else?"
