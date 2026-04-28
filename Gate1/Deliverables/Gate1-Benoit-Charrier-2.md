#this version 2 contains the concatenation of all 5 files in the folder with my name. the previous version has a wrong concatenation. all 5 files were ready before the deadline.

# Problem Statement and Success Metrics
## FNOL Processing Agent — Insurance Claims Automation

---

## 1. Problem statement — claimant perspective

When a claimant submits a first notice of loss — after a car accident, a flood, a theft — they are in a moment of disruption and need prompt confirmation that their insurer has received and is acting on their report. The current process guarantees acknowledgement within 2 hours, but breaches that guarantee for 1 in 3 claimants (31% SLA breach rate). On a 300-claim day, 93 people wait longer than 2 hours with no word — some considerably longer, since the breach rate tells us nothing about how far over the 2-hour mark those claims fall. For claimants, this is not an administrative inconvenience: it is uncertainty about whether a major financial event is being handled. The 18% routing error compounds this — a claim routed to the wrong adjuster must be re-routed before meaningful progress begins, adding further unacknowledged delay to claimants who have already been waiting.

---

## 2. Problem statement — business perspective

The claims team runs a structural capacity deficit. Processing 300 claims per day at 22 minutes per claim requires 6,600 minutes (110 hours) of specialist time per day. Twelve specialists, assuming 8-hour days, provide 5,760 minutes (96 hours) of capacity — a shortfall of 840 minutes (14 hours) per day. [A3] This arithmetic directly explains the 31% SLA breach: the team cannot physically handle peak volume within the 2-hour window. Beyond capacity, the 18% routing error rate — 54 mis-routed claims per day — creates rework that consumes specialist time that is already scarce, and degrades adjuster productivity by sending them claims outside their specialty. The combined effect is an operation that is expensive (12 FTEs on manual triage), slow (22 min/claim average), inaccurate (18% error on a step that could be automated), and unreliable (31% SLA breach). Without an automated first-line capability, the only paths to SLA compliance are headcount growth or volume reduction — neither of which the client has indicated is available. The client's stated design constraint is that any solution must retain human oversight for high-value or ambiguous claims — full automation is not the goal, but neither is the status quo. The target state is an operation where routine claims are handled end-to-end by the agent and specialists are reserved for the cases that genuinely require their judgment.

---

## 3. Why an AI agent — not traditional software, not RPA, not a process change

**Traditional rule-based software** cannot address this problem because FNOL inputs arrive as unstructured text from three channels: email, phone transcripts, and web forms. Rule-based systems require structured, predictable inputs. They can handle a structured web form with fixed fields, but cannot parse "my car was hit from behind at the junction near the office" and derive claim severity, coverage type, and adjuster routing from that narrative. Traditional software would cover at most one input channel and would still require specialists to handle email and phone transcript inputs — leaving the majority of the capacity problem unsolved.

**RPA** automates interactions with existing UIs by scripting clicks and keystrokes. It requires predictable screen layouts and structured data. Phone transcripts and emails are free-form; RPA cannot interpret semantic content or extract structured claim attributes from them. Even for structured web form inputs, RPA cannot perform the policy coverage validation step, which requires reading the policy record and applying judgment about whether the claimed event falls within coverage terms. RPA addresses data entry, not reasoning.

**Human process change** — optimising the existing manual workflow — fails on the capacity arithmetic alone. Even if a redesigned process reduced handling time by 25% (from 22 min to 16.5 min per claim), the team would need 4,950 minutes per day against 5,760 available, which clears the deficit with no buffer for volume spikes or absences. [A3] More fundamentally, process change does not address the structural mismatch: the problem is not that specialists are working inefficiently; it is that unstructured inputs require human interpretation for every claim, whether that takes 15 minutes or 25. Only removing human interpretation from the routine cases breaks the scaling constraint.

**An AI agent is the right answer** because: (1) the inputs are unstructured and require natural language understanding to classify and extract claim attributes — a capability only AI provides at the required speed and scale; (2) the decisions span multiple systems (claim text, policy record, adjuster availability) and must be synthesised in a single workflow — an agent can orchestrate this where a human must context-switch manually; (3) the client's stated requirement — full automation where appropriate, human oversight for ambiguous or high-value claims — is precisely the agent-with-delegation pattern; and (4) the volume (300/day) is high enough that even partial automation of routine cases closes the capacity deficit without headcount growth.

---

## 4. Success metrics

| Metric | Baseline (from scenario) | Target | How measured | Timeframe |
|--------|--------------------------|--------|--------------|-----------|
| SLA compliance rate | 69% (31% breach) | 95% | % of claims with claimant acknowledgement logged within 120 minutes of receipt; measured daily from CRM timestamp data | 90 days post go-live |
| Routing accuracy | 82% (18% error) | 96% | % of agent-routed claims accepted by the receiving adjuster without re-routing; measured weekly from CRM reassignment logs | 90 days post go-live |
| Average handling time — agentic claims | 22 min (manual baseline) | < 3 min | Elapsed time from claim receipt to routing decision logged in CRM, for claims processed without human escalation; measured per claim, reported as p50 and p95 | 90 days post go-live |
| Daily claim throughput without headcount increase | 300 claims/day with 12 FTEs | 300 claims/day with ≤ 12 FTEs | Total claims processed per day from CRM; FTE count from HR records; measured monthly | 90 days post go-live |
| Time to claimant acknowledgement | Not directly stated; implied ≤ 120 min with 31% breach [A5] | < 30 min for 90% of agent-handled claims | Time from claim receipt timestamp to acknowledgement sent timestamp in CRM; measured per claim, reported as p90 | 90 days post go-live |
| Escalation rate (agent to human) | Not applicable today (all human) | 15%–35% [A6] | % of claims where agent triggers AGENT_REVIEW or HUMAN_ONLY tier; measured weekly; alert if outside 15%–35% band | 90 days post go-live |

**Note on targets:** All targets above are proposed based on the stated business goals and industry reference points. [A1] None have been confirmed by the client. They must be validated before the success metrics are treated as contractual commitments.

---

## 5. Assumption log

> **Assumption [A1]:** All success metric targets (95% SLA compliance, 96% routing accuracy, < 3 min handling time, < 30 min acknowledgement) are proposed by the delivery team, not stated by the client.
> **Why it matters:** These targets drive the acceptance criteria in the capability specification and the pass/fail thresholds in the validation design. If the client has different targets, the spec thresholds change.
> **If wrong:** The system is built to the wrong bar — it may be over-engineered (if targets are lower) or under-scoped (if targets are higher, e.g. 99% SLA compliance requires different escalation logic).
> **Confidence:** Low — no client target confirmation in scenario.

> **Assumption [A2]:** The 18% routing error is caused primarily by misclassification of claim type or adjuster specialty, not by downstream constraints such as adjuster availability, geography, or workload balancing.
> **Why it matters:** If errors are classification-driven, an AI agent that correctly classifies claims will reduce them. If errors are capacity-driven (routed correctly but to an overloaded adjuster who passes it on), AI classification does not fix the problem — capacity management does.
> **If wrong:** The routing accuracy target is not achievable through classification improvement alone; the spec must include adjuster workload balancing logic, which is a significantly larger integration requirement.
> **Confidence:** Medium — misclassification is the most common driver of routing error in FNOL contexts, but this is not confirmed in the scenario.

> **Assumption [A3]:** Specialists work 8-hour days with no dedicated non-claim time (no meetings, training, or admin time factored in). The capacity calculation (12 × 8 × 60 = 5,760 min/day) assumes 100% productive utilisation.
> **Why it matters:** The capacity deficit (6,600 min needed vs 5,760 available) is the primary justification for why process change alone cannot close the SLA breach. If actual productive time per specialist is less than 8 hours, the deficit is larger, strengthening the case. If specialists have surge capacity or flexible hours, the deficit may be partially offset.
> **If wrong (productive time < 8h):** The capacity deficit is larger than calculated; the business case for automation is stronger.
> **If wrong (flexible capacity available):** The breach rate may be partially explainable by staffing patterns, not just volume — the agent may only need to cover peak periods, which changes the build scope.
> **Confidence:** Medium — 8-hour day is a standard assumption; actual productive utilisation is typically lower.

> **Assumption [A4]:** The 2-hour SLA clock starts at claim receipt (when the email, transcript, or web form arrives in the system) and covers the full cycle: triage, coverage validation, routing, and claimant acknowledgement.
> **Why it matters:** If the SLA clock starts later (e.g., when a specialist picks up the claim), the gap between receipt and pick-up is not measured, and the breach rate understates the true claimant wait time. This affects how we instrument the SLA metric and where the agent must insert itself in the workflow.
> **If wrong:** The measurement baseline is incorrect, and the 69% SLA compliance figure is not comparable to what the agent will produce under a different clock definition.
> **Confidence:** Medium — the scenario states the 2-hour requirement alongside the four steps, implying end-to-end coverage, but this is not explicit.

> **Assumption [A5]:** The current acknowledgement to the claimant is a manual step performed by a specialist, and it happens at or near the end of the 22-minute handling cycle — not as an automated first-contact response on receipt.
> **Why it matters:** If acknowledgement is already automated on receipt (e.g., an auto-reply email), the claimant-facing SLA is partially met regardless of the agent, and the 31% breach applies to something downstream (e.g., adjuster assignment confirmation). This changes which part of the process the agent must own to move the SLA metric.
> **If wrong:** The acknowledgement metric target (< 30 min for 90% of claims) is already being met today for the first-contact step, and the meaningful claimant metric is time to adjuster assignment — which requires a different measurement approach.
> **Confidence:** Low — the scenario does not state whether an automated acknowledgement exists.

> **Assumption [A6]:** Between 15% and 35% of claims will require human review or decision (AGENT_REVIEW or HUMAN_ONLY delegation tier). This band reflects the client's stated intent to automate "most" claims while retaining oversight for high-value or ambiguous cases.
> **Why it matters:** The escalation rate is a two-sided control: too low means the agent is under-escalating (potential quality risk); too high means the automation ROI is insufficient and FTE time is not freed as projected.
> **If wrong (escalation rate < 15%):** The agent may be under-escalating ambiguous claims, accepting low-confidence decisions that should go to a human. Silent quality risk.
> **If wrong (escalation rate > 35%):** The automation does not free enough specialist capacity to close the structural deficit; the business case weakens or additional automation scope is required.
> **Confidence:** Low — "most" is not quantified in the scenario; the 15%–35% band is a working hypothesis to be validated with the client.
# Delegation Analysis
## FNOL Processing Agent — Insurance Claims Automation

---

## 1. FNOL process decomposition

The scenario names four steps. Each is broken into sub-tasks below. Sub-tasks marked with [AGENT-CANDIDATE] are where automation directly addresses the capacity and accuracy problems identified in Deliverable 1.

**Step 1 — Triage by severity**
- 1.1 Parse and extract structured claim attributes from unstructured input (email / phone transcript / web form)
- 1.2 Classify claim type (motor, property, liability, health, other) [AGENT-CANDIDATE]
- 1.3 Assess severity level for LOW and MEDIUM claims [AGENT-CANDIDATE]
- 1.4 Assess severity level for HIGH and CRITICAL claims
- 1.5 Detect special handling flags: fatality, legal representation, vulnerable claimant, fraud indicator

**Step 2 — Validate against policy coverage**
- 2.1 Retrieve policy record from legacy policy administration system [AGENT-CANDIDATE]
- 2.2 Validate policy is active and in-force at date of loss [AGENT-CANDIDATE]
- 2.3 Match claim type to policy coverage — high confidence (coverage_match_confidence ≥ 0.85) [AGENT-CANDIDATE]
- 2.4 Match claim type to policy coverage — ambiguous (coverage_match_confidence 0.70–0.84)
- 2.5 Apply coverage exclusions check
- 2.6 Resolve coverage disputes and ambiguous coverage interpretations

**Step 3 — Route to the appropriate adjuster**
- 3.1 Identify required adjuster specialty from claim type and severity [AGENT-CANDIDATE]
- 3.2 Select adjuster from available queue by specialty and workload [AGENT-CANDIDATE]
- 3.3 Assign claim to adjuster in CRM [AGENT-CANDIDATE]
- 3.4 Notify adjuster of new assignment [AGENT-CANDIDATE]

**Step 4 — Acknowledge to the claimant**
- 4.1 Send initial receipt acknowledgement on claim arrival [AGENT-CANDIDATE]
- 4.2 Send routing confirmation once adjuster assigned (standard claims)
- 4.3 Communicate escalation, delay, or special-handling status to claimant

---

## 2. Delegation table

| Sub-task | Delegation tier | Rationale | Threshold / condition | Escalation path |
|---|---|---|---|---|
| **1.1** Parse and extract structured attributes from input | `AGENT_ONLY` | Pure data transformation — no decision made, no consequence attached to the extraction itself. Errors surface and are corrected at 1.2 and 2.3. Fully reversible. | Always applies | Extraction confidence < 0.70: flag claim as PARSE_UNCERTAIN; hold for 1.2 classification with reduced confidence weight |
| **1.2** Classify claim type | `AGENT_LOG` | High-volume pattern-matching against well-defined categories. Confidence score is calculable and auditable. Error consequence is low — a wrong classification is caught at adjuster routing before reaching the claimant. | classification_confidence ≥ 0.85: AGENT_LOG. classification_confidence < 0.85: escalate to AGENT_REVIEW | Escalate to AGENT_REVIEW; specialist confirms or corrects classification within 30 min review window [D5] |
| **1.3** Assess severity — LOW / MEDIUM | `AGENT_LOG` | Severity scoring for LOW and MEDIUM claims uses deterministic rules (claim type + estimated loss value + policy tier). Consequence of misrating LOW→MEDIUM is low: the claim gets slightly more attention than needed. Misrating MEDIUM→LOW is caught by the escalation trigger on claim value. | claim_value < [CURRENCY]10,000 AND claim_type ∉ {FATALITY, LEGAL, FRAUD_FLAG} AND severity_score < 60 [TODO: validate claim value threshold and scoring model with client — see D5-U1] | If any special flag is detected post-scoring, re-run at tier 1.5 |
| **1.4** Assess severity — HIGH / CRITICAL | `AGENT_REVIEW` | Severity determinations of HIGH or CRITICAL affect adjuster assignment, reserve setting, and regulatory reporting obligations. A downward misclassification (CRITICAL scored as HIGH) delays mandatory notifications and may breach regulatory SLAs. Consequence is not fully reversible within the 2-hour window. Human confirmation closes the error risk at low cost (one review, not full re-processing). | claim_value ≥ [CURRENCY]10,000 OR severity_score ≥ 60 OR claim_type = CRITICAL_EVENT [TODO: validate thresholds — see D5-U1] | Specialist confirms or reclassifies within 30-min review window; if window expires without action, claim auto-escalates to AGENT_SUPPORT with SLA warning logged |
| **1.5** Detect special handling flags (fatality, legal representation, vulnerable claimant, fraud indicator) | `AGENT_REVIEW` | A missed flag has asymmetric consequences: missed fatality = regulatory breach; missed legal representation = wrong communication channel activated; missed fraud indicator = loss. The agent flags; a human confirms. The cost of a false positive (flagging something that isn't a flag) is low — one extra review. The cost of a false negative is high and in some cases irreversible. | flag_keyword_match = TRUE OR sentiment_classifier = DISTRESSED AND claim_type = FATALITY_CANDIDATE OR fraud_score ≥ 0.60 [TODO: validate fraud_score threshold — see D5-U2] | Specialist reviews flag within 15-min window; if confirmed, claim enters HUMAN_ONLY track for affected sub-tasks |
| **2.1** Retrieve policy record from policy admin system | `AGENT_ONLY` | Read-only system call. No decision made. If retrieval fails, that is an integration error handled by the error-handling spec, not a delegation decision. Logging every retrieval adds overhead with no safety benefit. | Always applies | Integration failure: claim enters INTEGRATION_ERROR state; specialist notified within 5 min; manual retrieval fallback [TODO: confirm manual fallback process with client — see D5-U3] |
| **2.2** Validate policy in-force status | `AGENT_LOG` | Binary determination: policy is either active at date of loss or it is not. Low ambiguity. Decision is auditable, traceable to policy system data. Consequence of error (declaring an active policy lapsed) is significant but detectable — the adjuster will catch it. Logging creates the audit trail that allows error recovery. | policy_status = ACTIVE AND policy_end_date > loss_date AND policy_start_date ≤ loss_date | Policy not in force: claim flagged as COVERAGE_UNCERTAIN; AGENT_SUPPORT tier activated for specialist confirmation |
| **2.3** Match claim type to coverage — high confidence | `AGENT_LOG` | With confidence ≥ 0.85, the match between the classified claim type and the policy coverage terms is unambiguous. The agent's determination is auditable and traceable to specific policy clauses. The adjuster reviews the full claim and will catch mismatches. Logging every decision creates the evidence trail for dispute resolution. | coverage_match_confidence ≥ 0.85 AND no exclusion flags raised | Confidence drops below 0.85: escalate to 2.4 |
| **2.4** Match claim type to coverage — ambiguous | `AGENT_REVIEW` | Coverage confidence in the 0.70–0.84 band indicates the agent has identified a plausible match but cannot rule out alternative interpretations. Acting without review risks either wrongly accepting a non-covered claim (financial exposure) or wrongly rejecting a valid claim (regulatory and legal risk). Human confirmation at this stage is inexpensive relative to the cost of a coverage error. | coverage_match_confidence ≥ 0.70 AND coverage_match_confidence < 0.85 | Specialist reviews agent's coverage determination and supporting policy text within 30-min window; outcome logged with reviewer_id |
| **2.5** Apply coverage exclusions check | `AGENT_REVIEW` | Exclusions in insurance policies are often worded broadly and interpreted narrowly (or vice versa) in ways that require professional judgment. Applying an exclusion incorrectly is not reversible within the claims process — it triggers a formal dispute. The agent identifies candidate exclusions; a specialist confirms applicability. | exclusion_candidate_count ≥ 1 OR exclusion_confidence < 0.90 | Specialist reviews candidate exclusions against full policy text within 30-min window; decision logged with supporting clause references |
| **2.6** Resolve coverage disputes and ambiguous coverage interpretations | `HUMAN_ONLY` | Coverage interpretation with no clear answer requires professional accountability. See boundary justification (Section 3). | coverage_match_confidence < 0.70 OR coverage_type = DISPUTED OR exclusion_confirmed = CONTESTED | Specialist assigned via AGENT_SUPPORT; agent provides structured summary of claim, policy text, and point of ambiguity. No agent action until human decision logged. |
| **3.1** Identify required adjuster specialty | `AGENT_LOG` | Specialty mapping is deterministic: claim_type → specialty is a lookup table. Once claim type is confirmed (1.2), specialty derivation requires no judgment. Errors are caught at adjuster assignment when no adjuster of the derived specialty exists. | Always applies post 1.2 confirmation | Specialty not found in active adjuster pool: escalate to AGENT_SUPPORT for manual specialty assignment |
| **3.2** Select adjuster from available queue | `AGENT_ONLY` | Adjuster selection within a confirmed specialty is workload balancing — a deterministic optimisation (lowest current queue depth OR round-robin [TODO: confirm selection algorithm with client — see D5-U4]). No judgment required. No claimant-facing consequence of imperfect balancing. | adjuster_available_count ≥ 1 AND adjuster_specialty = required_specialty | No adjuster available: claim enters QUEUE_OVERFLOW state; AGENT_SUPPORT tier activated; specialist assigns manually |
| **3.3** Assign claim to adjuster in CRM | `AGENT_LOG` | CRM write action executing a confirmed routing decision. Logged automatically by CRM on write [D3]. No judgment required — the decision was made at 3.1/3.2. Logging here provides the timestamp used to measure adjuster SLA. | Always applies post 3.2 | CRM write failure: retry 3× with exponential backoff; if all fail, enter INTEGRATION_ERROR state and notify specialist |
| **3.4** Notify adjuster of new assignment | `AGENT_ONLY` | Standardised notification (claim reference, severity, receipt timestamp, claim summary). No decision content. Fully reversible if routing is corrected — a correction notification supersedes the original. | Always applies post 3.3 | Notification delivery failure: log failure; retry once; if failed, log as NOTIFY_FAILED for specialist follow-up |
| **4.1** Send initial receipt acknowledgement to claimant | `AGENT_ONLY` | See boundary justification (Section 3). This step must fire in < 5 minutes of claim receipt, unconditionally. | Always applies on claim receipt, before any triage begins | Delivery failure: retry once; log as ACK_FAILED; flag for manual send within 15 min |
| **4.2** Send routing confirmation to claimant — standard claims | `AGENT_LOG` | Standardised message confirming adjuster assignment and expected contact timeline [D4]. No judgment required. Content is templated; the agent fills adjuster name [ASSUMED], contact channel, and expected contact time. [D2] | claim_status = ROUTED AND special_handling_flag = FALSE | Escalated or flagged claims: step deferred to 4.3 (specialist communication) |
| **4.3** Communicate escalation, delay, or special-handling status to claimant | `HUMAN_ONLY` | See boundary justification (Section 3). | claim_status = ESCALATED OR special_handling_flag = TRUE OR routing_delay > 60 min | Specialist drafts and sends communication; agent provides structured briefing note (claim summary, reason for delay, claimant contact history) via AGENT_SUPPORT |

---

## 3. Delegation boundary justification

### AGENT_ONLY: 4.1 — Initial receipt acknowledgement

The boundary is drawn here — not at AGENT_LOG, not at AGENT_REVIEW — because the receipt acknowledgement is legally benign and SLA-critical simultaneously. The message contains only three elements: confirmation of receipt, a claim reference number, and a statement that processing has begun. It makes no representation about coverage, no commitment to an outcome, and no statement that could constitute an admission of liability. Nothing about this message requires judgment, and nothing about it requires an audit trail beyond the CRM timestamp that records it was sent. More importantly, this step must fire within minutes of claim receipt — well before any triage is complete. Routing it through human review or even human logging would introduce the exact delay it is designed to eliminate. The alternative — waiting for triage to complete before acknowledging — is the current process and produces the 31% SLA breach. The boundary is AGENT_ONLY because delaying it by one degree of oversight would defeat the purpose of building the agent at all.

### AGENT_ONLY: 2.1 — Policy record retrieval

The boundary is drawn at AGENT_ONLY because this sub-task contains no decision and no judgment — it is a read from a named system (the legacy policy administration SOAP endpoint) keyed on a policy identifier extracted from the claim. The agent cannot "get it wrong" at this step in any way that has consequence; it either retrieves the record or encounters an integration error. Integration errors are handled by the error-handling spec (retry, then escalate), not by this delegation tier. Making this AGENT_LOG would mean generating an audit entry for every successful read from a system that presumably already logs reads itself — overhead with no safety benefit.

### HUMAN_ONLY: 2.6 — Coverage dispute resolution

The boundary is drawn here for two reasons that are independent of each other, and both must hold before the boundary can move. First, **reversibility**: once a coverage decision is communicated to the claimant, retracting it triggers a formal dispute process with regulatory oversight in most insurance jurisdictions. An agent that wrongly denies or wrongly accepts coverage creates a liability that cannot be unwound in the 2-hour processing window. Second, **professional accountability**: coverage interpretation is a regulated professional act in many jurisdictions. The claims specialist who signs off on a coverage determination is personally and institutionally accountable for that decision in a way that an AI system cannot be — and the client has explicitly stated they want human oversight for "high-value or ambiguous claims." Ambiguous coverage is the definition of the case the client had in mind. The boundary could only move to AGENT_REVIEW if the client provides evidence that their coverage language is unambiguous enough that confidence ≥ 0.85 means "effectively certain" — which requires testing against historical coverage dispute data we do not have.

### HUMAN_ONLY: 4.3 — Escalation and special-handling communications

The boundary is drawn here because claimant communications about delays, escalations, or special circumstances carry obligations that vary by jurisdiction, claim type, and claimant vulnerability in ways that cannot be reliably encoded in a template. Specific risks: a message that says "your claim is being reviewed" may constitute acknowledgement of coverage in some jurisdictions. A message to a claimant who has flagged legal representation must go through their solicitor, not directly to them. A message to a bereaved claimant (fatality claim) has tone and content requirements governed by the client's vulnerable customer policy, which we have not seen. These are not edge cases to be handled with confidence thresholds — they are the cases where the agent has already escalated because it detected something that requires human judgment. The communication following an escalation must be owned by the human who owns the escalation.

---

## 4. Override and audit requirements

| Sub-task | Can human override? | Override mechanism | Audit trail fields |
|---|---|---|---|
| **1.1** Parse and extract | Yes | Specialist edits extracted fields in CRM; edit triggers re-run of 1.2 onward | claim_id, agent_id, extraction_timestamp, extracted_fields (JSON), parse_confidence, override_by (if applicable), override_timestamp, corrected_fields |
| **1.2** Classify claim type | Yes | Specialist selects correct classification in CRM review interface; triggers re-run of 1.3/1.4 | claim_id, agent_id, classification_timestamp, predicted_type, classification_confidence, review_outcome (CONFIRMED / CORRECTED), reviewer_id, corrected_type (if corrected), review_timestamp |
| **1.3** Assess severity LOW/MEDIUM | Yes | Specialist can upgrade severity in CRM; triggers re-routing | claim_id, agent_id, severity_score, assigned_severity, severity_timestamp, override_by (if applicable), override_severity, override_reason |
| **1.4** Assess severity HIGH/CRITICAL | Yes — review is the primary mechanism | Specialist confirms or reclassifies in review interface within 30-min window | claim_id, agent_id, severity_score, proposed_severity, review_window_opened, reviewer_id, review_decision (CONFIRMED / RECLASSIFIED), reclassified_to (if applicable), review_timestamp |
| **1.5** Detect special handling flags | Yes | Specialist dismisses false-positive flag or confirms flag and activates special-handling track | claim_id, agent_id, flags_detected (array), detection_confidence (per flag), review_outcome (CONFIRMED / DISMISSED per flag), reviewer_id, review_timestamp |
| **2.1** Retrieve policy record | Yes — specialist can trigger manual retrieval | CRM "manual policy lookup" action | claim_id, retrieval_timestamp, policy_id, retrieval_method (AUTOMATED / MANUAL), retrieval_status (SUCCESS / FAILED), failure_reason (if failed) |
| **2.2** Validate policy in-force | Yes | Specialist can override LAPSED determination if evidence supports | claim_id, agent_id, policy_status_at_loss_date, validation_decision (IN_FORCE / LAPSED / UNCERTAIN), validation_timestamp, override_by (if applicable), override_reason |
| **2.3** Match coverage — high confidence | Yes | Specialist can flag a high-confidence match for review; triggers 2.4 path | claim_id, agent_id, coverage_match_confidence, matched_coverage_clauses (array), match_decision, match_timestamp, override_flag (if specialist triggers review) |
| **2.4** Match coverage — ambiguous | Yes — review is the primary mechanism | Specialist reviews in structured interface showing claim text, policy clause, and agent reasoning | claim_id, agent_id, coverage_match_confidence, coverage_options_presented (array), reviewer_id, coverage_decision (ACCEPTED / REJECTED / REFERRED), decision_reason, review_timestamp |
| **2.5** Apply exclusions check | Yes — review is the primary mechanism | Specialist confirms or rejects candidate exclusion | claim_id, agent_id, exclusion_candidates (array with confidence scores), reviewer_id, exclusion_decision (per candidate: APPLIED / REJECTED), decision_reason, review_timestamp |
| **3.1** Identify adjuster specialty | Yes | Specialist can override derived specialty in CRM | claim_id, derived_specialty, derivation_rule, derivation_timestamp, override_by (if applicable), overridden_specialty, override_reason |
| **3.2** Select adjuster | Yes | Specialist can reassign to a specific adjuster | claim_id, adjuster_selected_id, selection_method (ALGORITHM / MANUAL), queue_depth_at_selection, selection_timestamp, reassigned_by (if applicable), reassigned_to, reassignment_reason |
| **3.3** Assign in CRM | Yes | Specialist can trigger reassignment; creates new assignment record | claim_id, adjuster_id, assignment_timestamp, assignment_method (AGENT / MANUAL), assigned_by (agent_id or specialist_id) |
| **3.4** Notify adjuster | Yes | Specialist can trigger re-notification after reassignment | claim_id, adjuster_id, notification_timestamp, notification_channel, delivery_status, retry_count |
| **4.1** Send receipt acknowledgement | Yes — post-send correction only | Specialist can send a corrected acknowledgement; both versions logged | claim_id, claimant_contact, acknowledgement_timestamp, delivery_status, correction_sent (boolean), correction_timestamp (if applicable) |
| **4.2** Send routing confirmation | Yes | Specialist can suppress or edit before send (within 10-min hold window [D5]) | claim_id, claimant_contact, routing_confirmation_timestamp, adjuster_id, delivery_status, suppressed_by (if applicable), suppression_reason |

---

## 5. Assumption log (delegation-specific)

> **Assumption [D1]:** Severity thresholds (LOW/MEDIUM vs HIGH/CRITICAL) are defined by claim value ([CURRENCY]10,000 boundary) and a severity score (threshold 60). Both numbers are working hypotheses — the scenario provides no claim value distribution data and no definition of severity scoring criteria.
> **Why it matters:** These thresholds determine what fraction of claims go to AGENT_LOG vs AGENT_REVIEW. If set too low, the agent over-escalates and the capacity benefit is lost. If set too high, genuinely complex claims are auto-processed and quality risk increases.
> **If wrong:** Escalation rate falls outside the 15–35% band established in Deliverable 1. Threshold must be recalibrated against live claim data. Tagged as [TODO: D5-U1].
> **Confidence:** Low — no historical claim value or severity distribution data available from scenario.

> **Assumption [D2]:** The coverage match confidence threshold (0.85 for AGENT_LOG, 0.70–0.84 for AGENT_REVIEW, < 0.70 for HUMAN_ONLY) is assumed to be calibrated correctly for this client's policy language. Confidence scores from an NLP model are not absolute — a model that achieves 0.85 confidence on one policy portfolio may achieve systematically lower confidence on a different one.
> **Why it matters:** If the client's policy language is more complex or archaic than the model was trained on, confidence scores will be systematically depressed. This would push more claims into AGENT_REVIEW than projected, increasing specialist load and reducing automation ROI.
> **If wrong:** Coverage validation escalation rate is higher than expected; the delegation boundaries for 2.3/2.4/2.6 must be re-drawn based on empirical model performance against the client's actual policy data.
> **Confidence:** Low — no model benchmarking against client policy data possible at spec stage.

> **Assumption [D3]:** Fraud detection (sub-task 1.5) can be operationalised at the FNOL stage using text-based signals (claim narrative keywords, claim history patterns, anomalous values) with a fraud_score threshold of 0.60. The scenario mentions no existing fraud detection system. If the client has a dedicated fraud detection model or tooling, its output would be used; if not, the agent must derive fraud signals from claim content alone.
> **Why it matters:** Fraud flag detection uses a single threshold (0.60) that has not been validated against the client's historical fraud rate or fraud patterns. A threshold that is too low generates false positives that burden specialists; too high misses genuine fraud.
> **If wrong:** The fraud flag mechanism either under-detects (fraud reaches adjusters undetected) or over-detects (specialists spend disproportionate time on false positives). Tagged as [TODO: D5-U2].
> **Confidence:** Low — no fraud data, no fraud model, and no client fraud detection infrastructure confirmed.

> **Assumption [D4]:** The routing confirmation message sent at sub-task 4.2 can include the assigned adjuster's name and contact channel. This assumes the CRM holds adjuster contact details in a structured, retrievable format and that sharing this information with the claimant is consistent with the client's communication policy.
> **Why it matters:** If adjuster contact details are not in the CRM or are not shareable with claimants, the routing confirmation template must be redesigned — it cannot commit to a named contact. This changes the information value of the acknowledgement to the claimant.
> **If wrong:** The routing confirmation becomes generic ("your claim has been assigned and you will be contacted within [X] hours"), reducing its usefulness as a claimant SLA signal.
> **Confidence:** Medium — modern CRMs typically hold this data; shareability policy is assumed but unconfirmed.

> **Assumption [D5]:** The AGENT_REVIEW window — the time a specialist has to review and veto an agent decision before it is treated as confirmed — is set at 30 minutes for standard reviews and 15 minutes for special handling flags. These windows are assumptions, not client requirements. The windows must be short enough that downstream steps (routing, acknowledgement) are not held up past the 2-hour SLA, but long enough that specialists can actually perform a review.
> **Why it matters:** Review windows directly affect SLA achievability for escalated claims. A 30-minute review window means an AGENT_REVIEW claim that uses the full window has at most 90 minutes remaining for the rest of the process (coverage check, routing, acknowledgement) to complete within the 2-hour SLA. If the window is too short, reviews are rubber-stamped. If too long, the SLA is breached for every escalated claim.
> **If wrong:** Either the escalated-claim SLA compliance rate is structurally unachievable, or review quality is so low that AGENT_REVIEW provides no real safety benefit.
> **Confidence:** Low — no data on specialist review capacity or average review duration.
# Capability Specification
## FNOL Processing Agent — Insurance Claims Automation

---

## 1. Purpose and scope

### Purpose
The FNOL Processing Agent automates the first-notice-of-loss intake workflow for a mid-size insurance company receiving 300 claims per day as unstructured text across three input channels (email, phone transcript, web form). The agent parses incoming claims, classifies claim type and severity, validates policy coverage against the legacy policy administration system, routes the claim to the appropriate adjuster via the CRM, and sends a claimant acknowledgement — all within the 2-hour SLA window. Routine claims are handled end-to-end without specialist involvement. Claims that exceed confidence thresholds, are high-value, are ambiguous, or carry special handling flags are escalated to human specialists with a structured briefing note. The agent does not make final decisions on coverage disputes or escalation communications; those remain human-owned per the delegation boundaries in Deliverable 2.

### In scope
- Ingestion of unstructured claim text from email, phone transcript, and web form
- Extraction of structured claim attributes using NLP (loss date, loss description, claim type, policy identifier, estimated loss value)
- Claim type classification (motor, property, liability, health, other)
- Severity assessment (LOW, MEDIUM, HIGH, CRITICAL) with delegation-tier routing
- Special handling flag detection (fatality, legal representation, vulnerable claimant, fraud indicator)
- Policy record retrieval from the legacy policy administration system via SOAP
- Policy in-force validation (active status at date of loss)
- Coverage match confidence scoring and delegation-tier routing
- Coverage exclusion candidate identification
- Adjuster specialty derivation and workload-balanced assignment via CRM
- Claimant receipt acknowledgement (sent within 5 minutes of claim receipt, unconditionally)
- Claimant routing confirmation (sent on successful adjuster assignment, standard claims only)
- Structured escalation briefing note generation for specialist-handled claims
- Claim document storage in the document management system
- SLA monitoring and breach-prevention alerting
- Duplicate claim detection
- Full audit logging of all agent decisions and actions

### Out of scope
- Claims adjustment (determining settlement amounts or reserve values)
- Fraud investigation (the agent flags; investigation is out of scope)
- Coverage dispute resolution (human-only per D2 tier 2.6)
- Escalation and special-handling claimant communications (human-only per D2 tier 4.3)
- Policy issuance, renewal, or endorsement
- Adjuster workforce scheduling or capacity management
- Legal proceedings management
- Any action on claims with status COVERAGE_DENIED (handed off to specialist)
- Integration with any system not named in the scenario (CRM, policy admin system, DMS)

---

## 2. Inputs and outputs

### Inputs

| Input | Source system | Format | Required / Optional | Validation rule |
|---|---|---|---|---|
| Email claim text | Email inbox (CRM-integrated) [ASSUMED: CRM polls or webhooks the inbox] | Plain text or HTML, max 50,000 chars | Required | Must contain at least one of: policy number pattern `[A-Z]{2}-[0-9]{8}` OR claimant name; reject and log if neither present |
| Phone transcript text | Call centre transcription system [ASSUMED: transcripts delivered to CRM or shared folder] | Plain text, max 50,000 chars | Required | Must be non-empty string of length ≥ 50 chars; reject and log if below minimum |
| Web form submission | CRM web form endpoint | JSON object (see REQ-1 for field list) | Required | All required fields present per web form schema; validated at ingestion before processing begins |
| Policy record | Legacy policy administration system (SOAP) | XML SOAP response (see §7 integration contract) | Required for coverage validation | Policy ID extracted from claim input must match exactly one policy record; if zero or multiple, enter COVERAGE_UNCERTAIN state |
| Adjuster pool | CRM (REST) | JSON array of adjuster objects | Required for routing | Must contain ≥ 1 adjuster with matching specialty; if empty, enter QUEUE_OVERFLOW state |

### Outputs

| Output | Target system / recipient | Format | Trigger condition |
|---|---|---|---|
| ClaimRecord | CRM (REST POST) | JSON (see Entity: Claim) | On every claim ingestion; created before processing begins |
| ClaimAuditLog entry | Audit log store [ASSUMED: CRM audit module or separate logging service — see D5-U6] | JSON (see §10 audit schema) | On every agent action |
| Claimant receipt acknowledgement | Claimant (email via CRM) | Plain text email, templated (see REQ-7) | Within 5 minutes of ClaimRecord creation, unconditionally |
| Claimant routing confirmation | Claimant (email via CRM) | Plain text email, templated (see REQ-8) | When claim transitions to ROUTED state AND special_handling_flags = [] |
| Adjuster assignment notification | Adjuster (CRM notification) | CRM notification (see REQ-6) | When ClaimAssignment record is created |
| Specialist escalation briefing | Human specialist (CRM review queue) | Structured JSON briefing note (see REQ-9) | When claim enters any PENDING_REVIEW or ESCALATED state |
| Claim document | Document management system | Original input text + extracted attributes as PDF [ASSUMED: PDF generation is within agent scope — see D5-U7] | On claim ingestion, before triage begins |
| SLA breach warning | Operations team [ASSUMED: via CRM alert or email — see D5-U6] | CRM alert | When remaining time to SLA deadline ≤ 30 minutes AND claim status ≠ COMPLETED |

---

## 3. Entity definitions

```
Entity: Claim
Attributes:
- id: UUID v4, primary key, required, generated on creation, immutable
- external_reference: string, format [A-Z]{2}-[0-9]{8}, required, generated on creation, immutable, unique
- source_channel: enum [EMAIL, PHONE_TRANSCRIPT, WEB_FORM], required, immutable
- raw_input: string, max 50,000 chars, required, immutable
- policy_id: string, format [A-Z]{2}-[0-9]{8}, required (extracted from raw_input), immutable
- loss_date: ISO 8601 date (YYYY-MM-DD), required [ASSUMED: always extractable from input — see D5-U5]
- loss_description: string, max 5,000 chars, required (extracted), immutable
- claim_type: enum [MOTOR, PROPERTY, LIABILITY, HEALTH, OTHER], required after TRIAGING
- classification_confidence: decimal(4,3), range 0.000–1.000, required after TRIAGING
- severity: enum [LOW, MEDIUM, HIGH, CRITICAL], required after TRIAGING
- severity_score: integer, range 0–100, required after TRIAGING [TODO: scoring model to be validated with client — see D5-U1]
- special_handling_flags: array of enum [FATALITY, LEGAL_REPRESENTATION, VULNERABLE_CLAIMANT, FRAUD_INDICATOR], default [], updated after TRIAGING
- fraud_score: decimal(4,3), range 0.000–1.000, optional [TODO: fraud scoring model — see D5-U2]
- parse_confidence: decimal(4,3), range 0.000–1.000, required after PARSING
- policy_status: enum [IN_FORCE, LAPSED, UNCERTAIN], required after VALIDATING
- coverage_match_confidence: decimal(4,3), range 0.000–1.000, required after VALIDATING
- coverage_status: enum [COVERED, NOT_COVERED, UNCERTAIN, DISPUTED], required after VALIDATING
- exclusion_candidates: array of strings (policy clause references), default []
- status: enum [see state machine below], required, default RECEIVED
- sla_deadline: ISO 8601 timestamp UTC, = created_at + 7200 seconds, required, immutable
- sla_breached: boolean, default false, set to true when current_time > sla_deadline AND status ≠ COMPLETED
- agent_id: string (agent version identifier), required, immutable
- created_at: ISO 8601 timestamp UTC, required, immutable
- updated_at: ISO 8601 timestamp UTC, required, updated on every state transition

State machine:
- RECEIVED → PARSING: on ClaimRecord creation
- PARSING → PARSED: parse_confidence ≥ 0.70
- PARSING → PARSE_UNCERTAIN: parse_confidence < 0.70
- PARSE_UNCERTAIN → PARSING: specialist corrects extracted fields and triggers re-parse
- PARSED → TRIAGING: automatic, no condition
- TRIAGING → TRIAGED: severity ∈ {LOW, MEDIUM} AND special_handling_flags = [] AND classification_confidence ≥ 0.85
- TRIAGING → TRIAGE_PENDING_REVIEW: severity ∈ {HIGH, CRITICAL} OR special_handling_flags ≠ [] OR classification_confidence < 0.85
- TRIAGE_PENDING_REVIEW → TRIAGED: specialist confirms within review window
- TRIAGE_PENDING_REVIEW → ESCALATED: review window expires (30 min for severity; 15 min for flags) with no specialist action
- TRIAGED → VALIDATING: automatic, no condition
- VALIDATING → COVERAGE_CONFIRMED: coverage_match_confidence ≥ 0.85 AND exclusion_candidates = [] AND policy_status = IN_FORCE
- VALIDATING → COVERAGE_PENDING_REVIEW: (coverage_match_confidence ≥ 0.70 AND coverage_match_confidence < 0.85) OR exclusion_candidates ≠ []
- VALIDATING → COVERAGE_DISPUTED: coverage_match_confidence < 0.70 OR policy_status = UNCERTAIN
- VALIDATING → COVERAGE_LAPSED: policy_status = LAPSED
- COVERAGE_PENDING_REVIEW → COVERAGE_CONFIRMED: specialist approves within review window
- COVERAGE_PENDING_REVIEW → COVERAGE_DISPUTED: specialist refers to dispute resolution
- COVERAGE_PENDING_REVIEW → ESCALATED: review window expires (30 min) with no specialist action
- COVERAGE_DISPUTED → COVERAGE_CONFIRMED: specialist resolves — coverage accepted
- COVERAGE_DISPUTED → COVERAGE_DENIED: specialist resolves — coverage denied
- COVERAGE_CONFIRMED → ROUTING: automatic, no condition
- ROUTING → ROUTED: adjuster_available_count ≥ 1 AND adjuster assigned in CRM
- ROUTING → QUEUE_OVERFLOW: adjuster_available_count = 0 for required specialty
- QUEUE_OVERFLOW → ROUTED: specialist manually assigns adjuster
- ROUTED → ACKNOWLEDGED: receipt acknowledgement delivered (always fires ≤ 5 min post-RECEIVED regardless of routing state)
- ACKNOWLEDGED → COMPLETED: routing confirmation sent (standard claims)
- Any non-terminal state → INTEGRATION_ERROR: required external system unavailable after retry exhaustion
- INTEGRATION_ERROR → [state at time of error]: specialist resolves integration issue; agent retries
- RECEIVED → DUPLICATE: duplicate detection check fires within 60 seconds of RECEIVED

Terminal states: COMPLETED, COVERAGE_DENIED, DUPLICATE

Invalid transitions:
- COMPLETED → any state (terminal — cannot be re-opened by agent)
- COVERAGE_DENIED → ROUTING (denied claims must not be routed to an adjuster)
- DUPLICATE → any state other than COMPLETED (duplicate claims must not be processed)
- ROUTING → VALIDATING (routing cannot loop back to coverage validation)
- TRIAGED → PARSING (triage result cannot revert to parse state without specialist reset)

Constraints:
- sla_deadline must equal created_at + 7200 seconds; cannot be modified after creation
- coverage_status = COVERED must not be set when policy_status = LAPSED
- status = ROUTED requires ClaimAssignment.claim_id = this.id to exist
- special_handling_flags = [LEGAL_REPRESENTATION] requires claim_status ≠ ACKNOWLEDGED until specialist confirms communication channel
```

```
Entity: ClaimAssignment
Attributes:
- id: UUID v4, primary key, required, generated on creation, immutable
- claim_id: UUID, foreign key → Claim.id, required, immutable, on delete: restrict
- adjuster_id: string (CRM adjuster identifier), required
- adjuster_specialty: enum [MOTOR, PROPERTY, LIABILITY, HEALTH, GENERAL], required
- assignment_method: enum [AGENT_ALGORITHM, MANUAL_SPECIALIST], required, immutable
- queue_depth_at_assignment: integer, ≥ 0, required
- assigned_by: string (agent_id or specialist_id), required, immutable
- created_at: ISO 8601 timestamp UTC, required, immutable
- superseded_at: ISO 8601 timestamp UTC, null by default; set if reassignment occurs
- superseded_by: UUID → ClaimAssignment.id, null by default

State machine:
- ACTIVE: current assignment
- ACTIVE → SUPERSEDED: a new ClaimAssignment is created for the same claim_id
- SUPERSEDED: previous assignment; retained for audit

Terminal states: SUPERSEDED (once superseded, never re-activated)

Constraints:
- At most one ClaimAssignment per claim_id with status = ACTIVE at any time
- adjuster_specialty must match Claim.claim_type mapping (see Decision 3)
- Cannot create a new ACTIVE assignment if Claim.status = COMPLETED or COVERAGE_DENIED
```

```
Entity: AdjusterQueueEntry
Attributes:
- adjuster_id: string, required (CRM identifier)
- adjuster_specialty: enum [MOTOR, PROPERTY, LIABILITY, HEALTH, GENERAL], required
- current_queue_depth: integer, ≥ 0, required
- is_available: boolean, required
- last_updated: ISO 8601 timestamp UTC, required

State machine:
- AVAILABLE: is_available = true
- AVAILABLE → UNAVAILABLE: is_available set to false (out of office, at capacity [ASSUMED: CRM exposes availability flag])
- UNAVAILABLE → AVAILABLE: is_available set to true

Constraints:
- Agent reads AdjusterQueueEntry as read-only; CRM is authoritative source
- Agent must re-query AdjusterQueueEntry within 30 seconds before creating ClaimAssignment to prevent stale assignment [ASSUMED: CRM supports real-time availability — see D5-U4]
```

```
Entity: AcknowledgementRecord
Attributes:
- id: UUID v4, primary key, required, generated on creation, immutable
- claim_id: UUID, foreign key → Claim.id, required, immutable, on delete: restrict
- acknowledgement_type: enum [RECEIPT, ROUTING_CONFIRMATION, ESCALATION_NOTICE], required, immutable
- recipient_contact: string (email address), required, immutable [ASSUMED: claimant email always available — see D5-U5]
- template_id: string (template version identifier), required, immutable
- rendered_content: string (final message text), required, immutable
- sent_at: ISO 8601 timestamp UTC, required, immutable
- delivery_status: enum [SENT, DELIVERED, FAILED], required, default SENT
- delivery_confirmed_at: ISO 8601 timestamp UTC, null until delivery confirmed
- retry_count: integer, ≥ 0, default 0, max 1 (one retry only)

State machine:
- SENT → DELIVERED: delivery confirmation received from email provider
- SENT → FAILED: delivery failure received OR no confirmation within 60 seconds
- FAILED → SENT: retry triggered (max 1 retry; if second attempt fails, status = FAILED and specialist notified)

Constraints:
- acknowledgement_type = RECEIPT must have sent_at ≤ Claim.created_at + 300 seconds
- One RECEIPT AcknowledgementRecord per claim_id (cannot send two initial receipts)
- acknowledgement_type = ROUTING_CONFIRMATION requires Claim.status = ROUTED before creation
- acknowledgement_type = ROUTING_CONFIRMATION must not be created if Claim.special_handling_flags ≠ []
```

```
Entity: EscalationBriefing
Attributes:
- id: UUID v4, primary key, required, generated on creation, immutable
- claim_id: UUID, foreign key → Claim.id, required, immutable, on delete: restrict
- escalation_reason: enum [LOW_PARSE_CONFIDENCE, LOW_CLASSIFICATION_CONFIDENCE, HIGH_SEVERITY, SPECIAL_FLAG_DETECTED, AMBIGUOUS_COVERAGE, COVERAGE_DISPUTE, QUEUE_OVERFLOW, SLA_RISK, INTEGRATION_ERROR], required, immutable
- escalation_detail: string (structured summary), max 2,000 chars, required, immutable
- claim_snapshot: JSON (Claim attributes at time of escalation), required, immutable
- policy_snapshot: JSON (policy record at time of escalation), optional
- review_window_deadline: ISO 8601 timestamp UTC, required (= escalation created_at + review window in seconds)
- assigned_to_specialist_id: string, optional (null until specialist picks up)
- created_at: ISO 8601 timestamp UTC, required, immutable
- resolved_at: ISO 8601 timestamp UTC, null until specialist acts
- resolution: enum [CONFIRMED, CORRECTED, REFERRED, OVERRIDDEN], optional (null until resolved)

State machine:
- OPEN: awaiting specialist review
- OPEN → RESOLVED: specialist acts within review_window_deadline
- OPEN → EXPIRED: review_window_deadline passes with no action; claim transitions to ESCALATED

Constraints:
- One OPEN EscalationBriefing per claim_id at any time (cannot open two simultaneous escalations for the same claim)
- resolved_at must be ≤ review_window_deadline to count as within-SLA
```

---

## 4. Requirements

```
REQ-1: Claim Ingestion and Attribute Extraction
Description: The agent must ingest claim inputs from all three source channels (EMAIL, PHONE_TRANSCRIPT, WEB_FORM) and extract the following structured attributes using NLP: policy_id, loss_date, loss_description, estimated_loss_value [ASSUMED: always estimable from input — see D5-U5], claimant_contact_email [ASSUMED: always present — see D5-U5], claim_narrative (cleaned text for downstream classification). Extraction must assign a parse_confidence score in range 0.000–1.000.
Acceptance criterion: For a test set of 50 representative claim inputs (to be defined by client before build [TODO: D5-U8 — no sample data available]), extraction must achieve parse_confidence ≥ 0.70 on ≥ 85% of inputs within 10 seconds of receipt per claim.
Delegation tier: AGENT_ONLY (1.1)
Error handling: If parse_confidence < 0.70, claim transitions to PARSE_UNCERTAIN. EscalationBriefing created with escalation_reason = LOW_PARSE_CONFIDENCE. Specialist notified within 5 minutes via CRM review queue. Claim processing halts until specialist corrects extracted fields and triggers re-parse.
```

```
REQ-2: Claim Type Classification
Description: The agent must classify every parsed claim into exactly one claim_type: MOTOR, PROPERTY, LIABILITY, HEALTH, or OTHER. Classification must produce a classification_confidence score in range 0.000–1.000. If classification_confidence ≥ 0.85, classification is accepted as AGENT_LOG. If classification_confidence < 0.85, claim transitions to TRIAGE_PENDING_REVIEW.
Acceptance criterion: On a held-out test set validated against client ground-truth labels [TODO: D5-U8], classification must achieve ≥ 90% accuracy at confidence ≥ 0.85, measured as (correct classifications / total classifications at threshold). Classification latency must be ≤ 5 seconds per claim.
Delegation tier: AGENT_LOG (1.2) / AGENT_REVIEW (1.2, when confidence < 0.85)
Error handling: If classification_confidence < 0.85, EscalationBriefing created with escalation_reason = LOW_CLASSIFICATION_CONFIDENCE. Specialist confirms or corrects within 30-minute review window. If window expires, claim transitions to ESCALATED; specialist notified with SLA remaining time displayed.
```

```
REQ-3: Severity Assessment
Description: The agent must assess claim severity as LOW, MEDIUM, HIGH, or CRITICAL using a severity scoring model that takes as inputs: claim_type, estimated_loss_value, claim_narrative, and special_handling_flags. The severity_score (0–100) maps to severity tiers as follows: 0–39 = LOW, 40–59 = MEDIUM, 60–79 = HIGH, 80–100 = CRITICAL [TODO: scoring model and value thresholds to be validated with client — see D5-U1]. Claims with severity ∈ {LOW, MEDIUM} are processed via AGENT_LOG. Claims with severity ∈ {HIGH, CRITICAL} are escalated to AGENT_REVIEW.
Acceptance criterion: Severity assessment must complete within 3 seconds of classification_confidence being set. For LOW/MEDIUM claims, claim must transition to TRIAGED within 3 seconds of severity assignment with no human action required. For HIGH/CRITICAL claims, EscalationBriefing must be created within 5 seconds of severity assignment.
Delegation tier: AGENT_LOG for LOW/MEDIUM (1.3); AGENT_REVIEW for HIGH/CRITICAL (1.4)
Error handling: If severity scoring model fails to produce a score (e.g., model service unavailable), default severity = HIGH and escalate. Log failure with claim_id and error detail. Never default to LOW or MEDIUM on scoring failure.
```

```
REQ-4: Special Handling Flag Detection
Description: The agent must scan every parsed claim for four special handling flags. Detection rules:
  - FATALITY: claim_narrative contains any of keyword set F [TODO: keyword set to be defined with client legal/compliance team — see D5-U9]; OR claim_type = MOTOR AND loss_description contains "fatal" OR "death" OR "deceased"
  - LEGAL_REPRESENTATION: claim_narrative contains "solicitor" OR "lawyer" OR "legal representative" OR "my attorney" [TODO: expand keyword set — see D5-U9]
  - VULNERABLE_CLAIMANT: claim_narrative sentiment_score < 0.20 [ASSUMED: sentiment model available; threshold assumed — see D5-U2] OR claimant_age > 75 [ASSUMED: age extractable from input — see D5-U5]
  - FRAUD_INDICATOR: fraud_score ≥ 0.60 [TODO: fraud model and threshold — see D5-U2]
Any detected flag triggers AGENT_REVIEW with a 15-minute review window. Multiple flags are reported in a single EscalationBriefing.
Acceptance criterion: False negative rate (flag present but not detected) must be < 2% on a labelled test set [TODO: D5-U8]. False positive rate must be < 20% (acceptable cost for safety-critical flags). Detection must complete within 5 seconds of parse_confidence being set.
Delegation tier: AGENT_REVIEW (1.5)
Error handling: If any flag detection model fails, default to SPECIAL_FLAG_DETECTED = true for FATALITY and LEGAL_REPRESENTATION categories, and escalate. Log model failure. Never suppress flag detection on model failure.
```

```
REQ-5: Policy Coverage Validation
Description: The agent must retrieve the policy record from the policy administration system using policy_id, validate policy in-force status at loss_date, and compute coverage_match_confidence for the classified claim_type against the policy's covered perils. Coverage routing follows:
  - policy_status ≠ IN_FORCE: transition to COVERAGE_LAPSED; EscalationBriefing created
  - coverage_match_confidence ≥ 0.85 AND exclusion_candidates = []: AGENT_LOG; transition to COVERAGE_CONFIRMED
  - coverage_match_confidence ≥ 0.70 AND coverage_match_confidence < 0.85, OR exclusion_candidates ≠ []: AGENT_REVIEW; 30-minute review window
  - coverage_match_confidence < 0.70: HUMAN_ONLY; transition to COVERAGE_DISPUTED; specialist assigned
Acceptance criterion: Policy retrieval must complete within 8 seconds of TRIAGED state. Coverage confidence scoring must complete within 5 seconds of successful policy retrieval. Total validation step (retrieve + validate) must complete within 15 seconds of TRIAGED state for 95% of claims.
Delegation tier: AGENT_ONLY for retrieval (2.1); AGENT_LOG for in-force check (2.2); AGENT_LOG for high-confidence match (2.3); AGENT_REVIEW for ambiguous match (2.4, 2.5); HUMAN_ONLY for disputes (2.6)
Error handling: If policy retrieval fails after 3 retries (see §7 integration contract), claim transitions to INTEGRATION_ERROR. Specialist notified within 5 minutes. Manual policy lookup triggered. If policy_id matches zero records, coverage_status = UNCERTAIN and claim escalated. If policy_id matches multiple records [ASSUMED: policy IDs are unique — see D5-U3], claim escalated with escalation_reason = COVERAGE_DISPUTE.
```

```
REQ-6: Adjuster Routing
Description: The agent must assign every claim with status COVERAGE_CONFIRMED to an available adjuster with matching specialty. Specialty mapping: MOTOR → MOTOR, PROPERTY → PROPERTY, LIABILITY → LIABILITY, HEALTH → HEALTH, OTHER → GENERAL. Selection algorithm: lowest current_queue_depth among available adjusters with matching specialty [TODO: confirm selection algorithm with client — see D5-U4]. Assignment is written to CRM as a ClaimAssignment record. Adjuster is notified via CRM notification within 60 seconds of assignment.
Acceptance criterion: Routing must complete within 10 seconds of COVERAGE_CONFIRMED state for 95% of claims. CRM assignment write must be confirmed (HTTP 200 or 201) before claim transitions to ROUTED. Adjuster notification must be sent within 60 seconds of ClaimAssignment creation.
Delegation tier: AGENT_LOG for specialty derivation (3.1); AGENT_ONLY for adjuster selection (3.2); AGENT_LOG for CRM assignment (3.3); AGENT_ONLY for adjuster notification (3.4)
Error handling: If no adjuster available for required specialty, claim transitions to QUEUE_OVERFLOW. EscalationBriefing created with escalation_reason = QUEUE_OVERFLOW. Specialist notified immediately. Agent retries routing every 5 minutes for up to 60 minutes; if no adjuster available after 60 minutes, claim remains in QUEUE_OVERFLOW and SLA breach warning fires.
```

```
REQ-7: Claimant Receipt Acknowledgement
Description: The agent must send a receipt acknowledgement to the claimant within 300 seconds (5 minutes) of ClaimRecord.created_at. This step fires unconditionally — it does not wait for triage, coverage validation, or routing to complete. The acknowledgement must contain: (a) claim external_reference, (b) statement that the claim has been received and is being processed, (c) the 2-hour SLA commitment (i.e. "you will be contacted within 2 hours"), (d) a contact number or email for queries [TODO: client to provide contact details — see D5-U9]. The message must not contain any statement about coverage status, adjuster identity, or claim outcome.
Acceptance criterion: AcknowledgementRecord with acknowledgement_type = RECEIPT must be created with sent_at ≤ Claim.created_at + 300 seconds for 100% of claims (no exceptions). Delivery confirmation must be received within 60 seconds of sending. If delivery fails, one retry fires immediately; if retry fails, specialist is notified within 5 minutes for manual send.
Delegation tier: AGENT_ONLY (4.1)
Error handling: If email delivery fails on first attempt, retry once immediately. If retry fails, create AcknowledgementRecord with delivery_status = FAILED and add to specialist manual-send queue within 5 minutes. Log failure with claim_id, recipient_contact, failure_reason, and retry_count.
```

```
REQ-8: Claimant Routing Confirmation
Description: The agent must send a routing confirmation to the claimant after claim transitions to ROUTED, provided special_handling_flags = []. The confirmation must contain: (a) claim external_reference, (b) assigned adjuster name [ASSUMED: available in CRM — see D4 from D2], (c) adjuster contact channel [ASSUMED: email or phone available in CRM — see D4 from D2], (d) expected next-contact timeframe [TODO: client to confirm standard expected contact SLA — see D5-U9], (e) claim external_reference for further queries. If special_handling_flags ≠ [], routing confirmation is suppressed; specialist handles claimant communication per HUMAN_ONLY tier 4.3.
Acceptance criterion: AcknowledgementRecord with acknowledgement_type = ROUTING_CONFIRMATION must be created within 120 seconds of Claim transitioning to ROUTED state, for all claims where special_handling_flags = []. Routing confirmation must never be sent for claims with special_handling_flags ≠ [].
Delegation tier: AGENT_LOG (4.2)
Error handling: Same retry logic as REQ-7. If adjuster name or contact channel is not available in CRM, send generic confirmation ("your claim has been assigned; you will be contacted within [X] hours") and log missing data fields for specialist follow-up.
```

```
REQ-9: Human Escalation and Review Queue
Description: For every claim that enters a PENDING_REVIEW, ESCALATED, COVERAGE_DISPUTED, or QUEUE_OVERFLOW state, the agent must create an EscalationBriefing and add it to the CRM specialist review queue. The briefing must contain: claim_id, external_reference, escalation_reason, escalation_detail (plain-text summary of what triggered escalation and what the agent determined), claim_snapshot (all Claim attributes at escalation time), policy_snapshot (if available), review_window_deadline, and time remaining before SLA breach. The review queue must be orderable by review_window_deadline ascending (most urgent first).
Acceptance criterion: EscalationBriefing must be created and visible in CRM review queue within 30 seconds of claim entering a review state. Review queue must support sort by review_window_deadline. Specialist must be able to action (confirm/correct/refer) a briefing from within the CRM interface without switching systems.
Delegation tier: AGENT_REVIEW / AGENT_SUPPORT / HUMAN_ONLY (varies per sub-task)
Error handling: If CRM write fails for EscalationBriefing, retry 3× with exponential backoff. If all retries fail, send email alert directly to on-call specialist with briefing content in email body. Log CRM write failure with claim_id and error detail.
```

```
REQ-10: SLA Monitoring and Breach Prevention
Description: The agent must monitor every active claim's time-to-SLA-deadline. At T-30 minutes (30 minutes before sla_deadline), if claim status ≠ COMPLETED, the agent must fire a breach-prevention alert. The alert must include: claim_id, external_reference, current status, time remaining, and the next step required to progress the claim. Alert destination: operations team [ASSUMED: CRM alert or email — see D5-U6]. The agent must also set Claim.sla_breached = true when current_time > sla_deadline AND claim status ≠ COMPLETED. SLA status must be visible on each EscalationBriefing.
Acceptance criterion: Breach-prevention alert must fire within 60 seconds of T-30 minutes for 100% of at-risk claims. Claim.sla_breached must be set to true within 60 seconds of sla_deadline passing for any non-COMPLETED claim. Alert must include all five required fields.
Delegation tier: AGENT_LOG (monitoring); AGENT_ONLY (alert send)
Error handling: If alert delivery fails, retry once immediately. If retry fails, log failure with claim_id. SLA breach status is still recorded in ClaimRecord regardless of alert delivery failure.
```

---

## 5. Decision logic

```
Decision: Severity Triage
Input: claim_type (enum), estimated_loss_value (decimal), severity_score (integer 0–100), special_handling_flags (array)
Logic:
  IF special_handling_flags ≠ [] THEN
    → escalate to AGENT_REVIEW (tier 1.5); create EscalationBriefing (escalation_reason = SPECIAL_FLAG_DETECTED)
  ELSE IF severity_score ≥ 80 THEN
    → severity = CRITICAL; escalate to AGENT_REVIEW (tier 1.4); create EscalationBriefing (escalation_reason = HIGH_SEVERITY)
  ELSE IF severity_score ≥ 60 THEN
    → severity = HIGH; escalate to AGENT_REVIEW (tier 1.4); create EscalationBriefing (escalation_reason = HIGH_SEVERITY)
  ELSE IF severity_score ≥ 40 THEN
    → severity = MEDIUM; log decision (tier 1.3); transition to TRIAGED
  ELSE
    → severity = LOW; log decision (tier 1.3); transition to TRIAGED
  [TODO: severity_score thresholds require validation with client against historical claim data — see D5-U1]
Output: Claim.severity set; Claim.status updated; EscalationBriefing created if AGENT_REVIEW triggered
Delegation tier: AGENT_LOG for LOW/MEDIUM; AGENT_REVIEW for HIGH/CRITICAL
```

```
Decision: Coverage Validation
Input: policy_status (enum), coverage_match_confidence (decimal), exclusion_candidates (array), loss_date (date), policy_start_date (date), policy_end_date (date)
Logic:
  IF policy_status ≠ IN_FORCE OR loss_date < policy_start_date OR loss_date > policy_end_date THEN
    → coverage_status = NOT_COVERED; Claim.status = COVERAGE_LAPSED; create EscalationBriefing
  ELSE IF coverage_match_confidence < 0.70 THEN
    → coverage_status = DISPUTED; Claim.status = COVERAGE_DISPUTED; create EscalationBriefing (HUMAN_ONLY)
  ELSE IF coverage_match_confidence ≥ 0.70 AND coverage_match_confidence < 0.85 THEN
    → coverage_status = UNCERTAIN; Claim.status = COVERAGE_PENDING_REVIEW; create EscalationBriefing (AGENT_REVIEW); 30-min window
  ELSE IF exclusion_candidates ≠ [] THEN
    → coverage_status = UNCERTAIN; Claim.status = COVERAGE_PENDING_REVIEW; create EscalationBriefing (AGENT_REVIEW); 30-min window
  ELSE
    → coverage_status = COVERED; Claim.status = COVERAGE_CONFIRMED; log decision
Output: Claim.coverage_status set; Claim.coverage_match_confidence set; Claim.status updated
Delegation tier: AGENT_LOG for confirmed coverage; AGENT_REVIEW for ambiguous; HUMAN_ONLY for disputes
```

```
Decision: Adjuster Routing
Input: claim_type (enum), severity (enum), AdjusterQueueEntry[] (array of available adjusters)
Logic:
  specialty_required = specialty_map[claim_type]
    where specialty_map = {MOTOR: MOTOR, PROPERTY: PROPERTY, LIABILITY: LIABILITY, HEALTH: HEALTH, OTHER: GENERAL}
  candidates = [a for a in AdjusterQueueEntry where a.adjuster_specialty = specialty_required AND a.is_available = true]
  IF candidates = [] THEN
    → Claim.status = QUEUE_OVERFLOW; create EscalationBriefing (escalation_reason = QUEUE_OVERFLOW)
  ELSE
    → selected = candidates.sort_by(current_queue_depth ASC)[0]  [TODO: confirm selection algorithm — see D5-U4]
    → create ClaimAssignment(adjuster_id = selected.adjuster_id, assignment_method = AGENT_ALGORITHM)
    → Claim.status = ROUTED
Output: ClaimAssignment created; Claim.status = ROUTED or QUEUE_OVERFLOW
Delegation tier: AGENT_ONLY
```

```
Decision: Escalation Trigger
Input: Claim.status, EscalationBriefing.review_window_deadline, current_time
Logic:
  IF Claim.status ∈ {TRIAGE_PENDING_REVIEW, COVERAGE_PENDING_REVIEW} AND
     current_time > EscalationBriefing.review_window_deadline AND
     EscalationBriefing.resolved_at IS NULL THEN
    → Claim.status = ESCALATED; EscalationBriefing.status = EXPIRED
    → send urgent CRM alert to operations team with claim_id and time_overdue
  ELSE IF current_time > Claim.sla_deadline - 1800 AND Claim.status ≠ COMPLETED THEN
    → fire SLA breach-prevention alert (REQ-10)
  ELSE IF current_time > Claim.sla_deadline AND Claim.status ≠ COMPLETED THEN
    → Claim.sla_breached = true; log breach with claim_id, final_status, breach_duration_seconds
Output: Claim.status updated if escalated; alert sent if SLA at risk; Claim.sla_breached set if deadline passed
Delegation tier: AGENT_LOG
```

---

## 6. Escalation triggers

| Trigger condition | Threshold | Action | Notified party | SLA | If SLA breached |
|---|---|---|---|---|---|
| Parse confidence low | parse_confidence < 0.70 | Create EscalationBriefing; halt processing | On-call specialist (CRM queue) | Specialist must act within 60 minutes | Claim.status = ESCALATED; operations notified |
| Classification confidence low | classification_confidence < 0.85 | Create EscalationBriefing; await specialist confirmation | On-call specialist (CRM queue) | 30 minutes | Claim.status = ESCALATED; SLA warning sent |
| High / Critical severity | severity_score ≥ 60 | Create EscalationBriefing; await specialist confirmation | On-call specialist (CRM queue) | 30 minutes | Claim.status = ESCALATED; SLA warning sent |
| Special handling flag detected | special_handling_flags ≠ [] | Create EscalationBriefing; 15-min window | On-call specialist (CRM queue) | 15 minutes | Claim.status = ESCALATED; escalate to senior specialist |
| Ambiguous coverage | coverage_match_confidence ≥ 0.70 AND < 0.85 | Create EscalationBriefing; await specialist confirmation | On-call specialist (CRM queue) | 30 minutes | Claim.status = ESCALATED; SLA warning sent |
| Exclusion candidate identified | exclusion_candidates.count ≥ 1 | Create EscalationBriefing; await specialist confirmation | On-call specialist (CRM queue) | 30 minutes | Claim.status = ESCALATED; SLA warning sent |
| Coverage disputed | coverage_match_confidence < 0.70 OR coverage_type = DISPUTED | Create EscalationBriefing; HUMAN_ONLY; no agent action until specialist decides | Senior specialist (CRM queue) | No automated window; claim stays in COVERAGE_DISPUTED | Claim.sla_breached flagged; operations notified |
| Policy lapsed | policy_status ≠ IN_FORCE | Create EscalationBriefing; HUMAN_ONLY | Senior specialist (CRM queue) | No automated window | Claim.sla_breached flagged; operations notified |
| No adjuster available | adjuster_available_count = 0 for required specialty | Create EscalationBriefing; retry every 5 min for 60 min | On-call specialist (CRM queue) | 60 minutes to manual assignment | Claim.status = ESCALATED; SLA breach imminent |
| SLA breach risk | current_time > sla_deadline - 1800 seconds AND status ≠ COMPLETED | Send SLA breach-prevention alert | Operations team | Alert must fire ≥ 30 min before breach | N/A (alert IS the action) |
| Receipt ACK delivery failed | AcknowledgementRecord.delivery_status = FAILED after retry | Add to manual-send queue | On-call specialist | 15 minutes to manual send | Log; escalate to operations |
| Integration unavailable | External system returns HTTP 5xx × 3 OR timeout × 3 | Transition to INTEGRATION_ERROR; notify specialist | On-call specialist | 30 minutes to manual resolution | Claim.sla_breached flagged if no resolution within SLA |

---

## 7. Integration contracts

### 7.1 CRM (Modern — REST API)

```
Integration: CRM
Purpose: Create and update Claim records; read and write ClaimAssignment records;
         read AdjusterQueueEntry data; send adjuster notifications; post to specialist
         review queue; send claimant acknowledgement emails via CRM email service
Protocol: REST / HTTPS
Base URL: [ASSUMED: https://crm.client.internal/api/v1 — to be confirmed with client]
Authentication: OAuth 2.0 Bearer token; client_credentials grant;
                token stored in environment variable CRM_ACCESS_TOKEN;
                token endpoint: [ASSUMED: https://crm.client.internal/oauth/token];
                token TTL: 3600 seconds; refresh 60 seconds before expiry

Operations:

  CREATE_CLAIM:
    Method: POST
    Path: /claims
    Request (JSON):
      {
        "external_reference": string (required, format [A-Z]{2}-[0-9]{8}),
        "source_channel": enum [EMAIL, PHONE_TRANSCRIPT, WEB_FORM] (required),
        "raw_input": string (required, max 50000 chars),
        "policy_id": string (required),
        "loss_date": string ISO 8601 date (required),
        "loss_description": string (required, max 5000 chars),
        "status": string = "RECEIVED" (required),
        "sla_deadline": string ISO 8601 datetime UTC (required),
        "agent_id": string (required),
        "created_at": string ISO 8601 datetime UTC (required)
      }
    Response (HTTP 201):
      { "id": UUID, "external_reference": string, "created_at": string }
    Response (HTTP 400): { "error": string, "field": string }
    Response (HTTP 409): { "error": "duplicate_external_reference" }
    Response (HTTP 5xx): { "error": string, "trace_id": string }
    Timeout: 5000ms
    Retry: HTTP 5xx or timeout: 3 retries, exponential backoff 1s/2s/4s
           HTTP 4xx: no retry; log and escalate
    Rate limit: [UNKNOWN — flag for client confirmation; assume 100 req/min]
    Fallback: If CREATE_CLAIM fails after retries, write claim to local buffer file
              (claim_id + raw_input + timestamp); alert specialist within 5 minutes;
              retry from buffer when CRM recovers

  UPDATE_CLAIM_STATUS:
    Method: PATCH
    Path: /claims/{claim_id}
    Request (JSON):
      {
        "status": enum (required),
        "updated_at": string ISO 8601 datetime UTC (required),
        "[any other fields being updated]": value
      }
    Response (HTTP 200): { "id": UUID, "status": string, "updated_at": string }
    Response (HTTP 404): { "error": "claim_not_found" }
    Response (HTTP 409): { "error": "invalid_status_transition", "from": string, "to": string }
    Timeout: 3000ms
    Retry: HTTP 5xx or timeout: 3 retries, exponential backoff 1s/2s/4s
    Rate limit: [UNKNOWN]
    Fallback: If status update fails after retries, log failure with claim_id and target_status;
              add to retry queue; alert specialist if claim is in a time-critical state

  GET_ADJUSTER_QUEUE:
    Method: GET
    Path: /adjusters?specialty={specialty}&is_available=true
    Request: Query params only
    Response (HTTP 200):
      {
        "adjusters": [
          {
            "adjuster_id": string,
            "adjuster_specialty": enum,
            "current_queue_depth": integer,
            "is_available": boolean,
            "last_updated": string ISO 8601 datetime UTC
          }
        ]
      }
    Response (HTTP 200, empty): { "adjusters": [] }
    Timeout: 3000ms
    Retry: HTTP 5xx or timeout: 2 retries, exponential backoff 1s/2s
    Rate limit: [UNKNOWN]
    Fallback: If GET_ADJUSTER_QUEUE fails after retries, transition claim to QUEUE_OVERFLOW;
              notify specialist immediately

  CREATE_CLAIM_ASSIGNMENT:
    Method: POST
    Path: /claim-assignments
    Request (JSON):
      {
        "claim_id": UUID (required),
        "adjuster_id": string (required),
        "adjuster_specialty": enum (required),
        "assignment_method": enum [AGENT_ALGORITHM, MANUAL_SPECIALIST] (required),
        "queue_depth_at_assignment": integer (required),
        "assigned_by": string (required),
        "created_at": string ISO 8601 datetime UTC (required)
      }
    Response (HTTP 201): { "id": UUID, "claim_id": UUID, "adjuster_id": string }
    Response (HTTP 409): { "error": "active_assignment_exists" }
    Timeout: 5000ms
    Retry: HTTP 5xx or timeout: 3 retries, exponential backoff 1s/2s/4s
    Rate limit: [UNKNOWN]
    Fallback: If assignment fails after retries, transition claim to QUEUE_OVERFLOW; notify specialist

  SEND_EMAIL:
    Method: POST
    Path: /emails
    Request (JSON):
      {
        "to": string (email address, required),
        "subject": string (required, max 200 chars),
        "body": string (required, max 10000 chars, plain text),
        "claim_id": UUID (required, for audit linkage),
        "template_id": string (required),
        "send_at": string ISO 8601 datetime UTC (optional; omit for immediate send)
      }
    Response (HTTP 202): { "message_id": string, "queued_at": string }
    Response (HTTP 400): { "error": string, "field": string }
    Timeout: 5000ms
    Retry: HTTP 5xx or timeout: 1 retry after 2s (receipt ACK only; one retry maximum per REQ-7)
    Rate limit: [UNKNOWN]
    Fallback: Log FAILED AcknowledgementRecord; add to manual-send queue; alert specialist

  CREATE_ESCALATION_BRIEFING:
    Method: POST
    Path: /review-queue
    Request (JSON):
      {
        "claim_id": UUID (required),
        "escalation_reason": enum (required),
        "escalation_detail": string (required, max 2000 chars),
        "claim_snapshot": object (required),
        "policy_snapshot": object (optional),
        "review_window_deadline": string ISO 8601 datetime UTC (required),
        "created_at": string ISO 8601 datetime UTC (required)
      }
    Response (HTTP 201): { "briefing_id": UUID }
    Timeout: 5000ms
    Retry: HTTP 5xx or timeout: 3 retries, exponential backoff 1s/2s/4s
    Rate limit: [UNKNOWN]
    Fallback: If CRM write fails after retries, send email to on-call specialist with full briefing content in body; log failure

Data mapping (internal → CRM):
  Claim.id → /claims/{id} path parameter
  Claim.external_reference → claims.external_reference
  Claim.source_channel → claims.source_channel
  Claim.status → claims.status
  Claim.sla_deadline → claims.sla_deadline
  ClaimAssignment.adjuster_id → claim-assignments.adjuster_id
  AdjusterQueueEntry.adjuster_id ← adjusters[].adjuster_id
  AdjusterQueueEntry.current_queue_depth ← adjusters[].current_queue_depth
```

---

### 7.2 Policy Administration System (Legacy — SOAP)

```
Integration: Policy Administration System
Purpose: Retrieve policy record by policy_id to validate in-force status and
         coverage terms against claim type
Protocol: SOAP over HTTPS
Base URL / endpoint: [ASSUMED: https://policy-admin.client.internal/ws — to be confirmed with client]
Authentication: [ASSUMED: WS-Security UsernameToken; credentials stored in environment
                variables POLICY_ADMIN_USER and POLICY_ADMIN_PASS — to be confirmed with client]

[SCOPE-OUT: Full SOAP contract (WSDL, operation names, request/response XML schemas,
fault codes) is not specifiable from the scenario. The scenario confirms the system
exists and uses SOAP endpoints but provides no WSDL or API documentation.

Resolution: Client to provide WSDL file before build begins.
Build approach: Stub this integration with a configurable mock that accepts a
policy_id and returns a configurable policy record (in-force / lapsed / not-found).
Mock must be replaceable with the real SOAP client by changing one configuration flag
(USE_POLICY_ADMIN_MOCK = true/false in .env).

Known operations required (to be confirmed against WSDL):
  - GetPolicyByID(policy_id: string) → PolicyRecord
  - PolicyRecord fields required by agent:
      policy_id: string
      policy_status: enum [ACTIVE, LAPSED, CANCELLED, SUSPENDED]
      policy_start_date: date
      policy_end_date: date
      covered_perils: array of strings (peril types covered)
      exclusions: array of strings (exclusion clause references)
      policy_holder_name: string
      policy_tier: string [ASSUMED: used in severity scoring — see D5-U1]

Timeout: 8000ms (legacy systems may be slow; confirmed assumption — see D5-U3)
Retry: SOAP fault (server-side): 3 retries, exponential backoff 2s/4s/8s
       SOAP fault (client-side, e.g. invalid policy_id): no retry; log and escalate
       Timeout: 2 retries, same backoff
Rate limit: [UNKNOWN — legacy systems may have undocumented concurrency limits;
             assume max 10 concurrent connections until client confirms — see D5-U3]
Fallback: If policy retrieval fails after retries, transition claim to INTEGRATION_ERROR;
          notify specialist within 5 minutes for manual policy lookup;
          agent cannot proceed with coverage validation until policy record is available]
```

---

### 7.3 Document Management System (DMS)

```
Integration: Document Management System
Purpose: Store original claim input (raw text) and extracted attributes as a
         document associated with the claim record, for adjuster reference and
         regulatory retention
Protocol: [ASSUMED: REST over HTTPS — protocol not stated in scenario; see D5-U6]
Base URL: [ASSUMED: https://dms.client.internal/api/v1 — to be confirmed with client]
Authentication: [ASSUMED: API key in Authorization header; stored in environment
                variable DMS_API_KEY — to be confirmed with client]

Operations:

  STORE_CLAIM_DOCUMENT:
    Method: POST
    Path: [ASSUMED: /documents]
    Request (multipart/form-data or JSON [ASSUMED]):
      {
        "document_type": string = "FNOL_CLAIM" (required),
        "claim_id": UUID (required),
        "external_reference": string (required),
        "content_text": string (raw_input, required),
        "extracted_attributes": object (JSON of extracted claim fields, required),
        "source_channel": enum (required),
        "created_at": string ISO 8601 datetime UTC (required)
      }
    Response (HTTP 201 [ASSUMED]):
      { "document_id": string, "stored_at": string }
    Response (HTTP 400 [ASSUMED]): { "error": string }
    Timeout: 10000ms
    Retry: HTTP 5xx or timeout: 3 retries, exponential backoff 2s/4s/8s
           HTTP 4xx: no retry; log and alert specialist
    Rate limit: [UNKNOWN]
    Fallback: If DMS storage fails after retries, store document to local fallback
              directory (./fallback_docs/{claim_id}.json); log failure;
              alert specialist; retry DMS storage when system recovers.
              Claim processing continues — DMS failure must not block triage or routing.

Data mapping (internal → DMS):
  Claim.id → document.claim_id
  Claim.external_reference → document.external_reference
  Claim.raw_input → document.content_text
  Claim.{all extracted fields} → document.extracted_attributes
  Claim.source_channel → document.source_channel
  Claim.created_at → document.created_at
```

---

## 8. State model

```
States (SCREAMING_SNAKE_CASE):
  RECEIVED, PARSING, PARSED, PARSE_UNCERTAIN,
  TRIAGING, TRIAGE_PENDING_REVIEW, TRIAGED,
  VALIDATING, COVERAGE_PENDING_REVIEW, COVERAGE_DISPUTED, COVERAGE_CONFIRMED,
  COVERAGE_LAPSED, COVERAGE_DENIED,
  ROUTING, QUEUE_OVERFLOW, ROUTED,
  ACKNOWLEDGED, COMPLETED,
  ESCALATED, INTEGRATION_ERROR, DUPLICATE

Transitions:
  RECEIVED → PARSING: ClaimRecord created; DMS store initiated in parallel
  RECEIVED → DUPLICATE: duplicate check returns match within 60 seconds of RECEIVED
  PARSING → PARSED: parse_confidence ≥ 0.70
  PARSING → PARSE_UNCERTAIN: parse_confidence < 0.70
  PARSE_UNCERTAIN → PARSING: specialist submits corrected extracted fields
  PARSED → TRIAGING: automatic
  TRIAGING → TRIAGED: severity ∈ {LOW, MEDIUM} AND special_handling_flags = [] AND classification_confidence ≥ 0.85
  TRIAGING → TRIAGE_PENDING_REVIEW: severity ∈ {HIGH, CRITICAL} OR special_handling_flags ≠ [] OR classification_confidence < 0.85
  TRIAGE_PENDING_REVIEW → TRIAGED: specialist confirms within review window
  TRIAGE_PENDING_REVIEW → ESCALATED: review window expires with no specialist action
  TRIAGED → VALIDATING: automatic
  VALIDATING → COVERAGE_CONFIRMED: policy_status = IN_FORCE AND coverage_match_confidence ≥ 0.85 AND exclusion_candidates = []
  VALIDATING → COVERAGE_PENDING_REVIEW: policy_status = IN_FORCE AND (coverage_match_confidence ≥ 0.70 AND < 0.85 OR exclusion_candidates ≠ [])
  VALIDATING → COVERAGE_DISPUTED: policy_status = IN_FORCE AND coverage_match_confidence < 0.70
  VALIDATING → COVERAGE_LAPSED: policy_status ≠ IN_FORCE
  COVERAGE_PENDING_REVIEW → COVERAGE_CONFIRMED: specialist approves within review window
  COVERAGE_PENDING_REVIEW → COVERAGE_DISPUTED: specialist refers to dispute resolution
  COVERAGE_PENDING_REVIEW → ESCALATED: review window expires with no specialist action
  COVERAGE_DISPUTED → COVERAGE_CONFIRMED: specialist resolves — coverage accepted
  COVERAGE_DISPUTED → COVERAGE_DENIED: specialist resolves — coverage denied
  COVERAGE_CONFIRMED → ROUTING: automatic
  ROUTING → ROUTED: adjuster selected and ClaimAssignment created in CRM
  ROUTING → QUEUE_OVERFLOW: no available adjuster of required specialty
  QUEUE_OVERFLOW → ROUTED: specialist manually creates ClaimAssignment
  ROUTED → ACKNOWLEDGED: AcknowledgementRecord (ROUTING_CONFIRMATION) created
    NOTE: AcknowledgementRecord (RECEIPT) is created at RECEIVED → PARSING transition,
    independently of routing state. ACKNOWLEDGED state reflects routing confirmation sent.
  ACKNOWLEDGED → COMPLETED: all required steps complete
  Any non-terminal state → INTEGRATION_ERROR: required external system unavailable after retry exhaustion
  INTEGRATION_ERROR → [state at time of error]: specialist resolves; agent retries from last stable state

Terminal states: COMPLETED, COVERAGE_DENIED, DUPLICATE

Invalid transitions:
  COMPLETED → any state (COMPLETED is terminal; re-opening requires manual specialist action outside agent scope)
  COVERAGE_DENIED → ROUTING (a denied claim must never be assigned to an adjuster)
  DUPLICATE → any state other than remaining DUPLICATE (duplicate claims are frozen)
  ROUTED → VALIDATING (routing cannot reverse to coverage validation without specialist reset)
  COVERAGE_CONFIRMED → TRIAGE_PENDING_REVIEW (coverage confirmation cannot revert to triage review)
  ACKNOWLEDGED → TRIAGING (acknowledged claims cannot revert to triage)
```

---

## 9. Error handling

| Failure | Detection | Agent action | Human notification | Recovery |
|---|---|---|---|---|
| CRM unavailable | HTTP 5xx × 3 or connection timeout × 3 within 12s total retry window | Transition claim to INTEGRATION_ERROR; write claim to local buffer file with claim_id + status + timestamp | On-call specialist via email within 5 minutes (fallback to email if CRM is down) | Retry from buffer every 5 minutes; resume from last confirmed CRM state when CRM recovers; specialist confirms recovery |
| Policy admin system unavailable | SOAP fault (server) × 3 or timeout × 3 within 28s total retry window | Transition claim to INTEGRATION_ERROR; halt at VALIDATING; log policy_id and failure reason | On-call specialist via CRM (if CRM available) or email within 5 minutes | Specialist performs manual policy lookup; enters policy record via CRM interface; agent resumes VALIDATING on specialist action |
| DMS unavailable | HTTP 5xx × 3 or timeout × 3 | Write to local fallback directory ./fallback_docs/{claim_id}.json; log failure; continue processing (DMS failure is non-blocking) | Specialist notified via CRM alert within 30 minutes (non-urgent) | Retry DMS storage every 15 minutes; specialist confirms when resolved |
| Coverage data missing | policy record retrieved but covered_perils field is empty or null | Set coverage_match_confidence = 0.0; transition to COVERAGE_DISPUTED; create EscalationBriefing | Senior specialist via CRM review queue immediately | Specialist obtains policy details from insurer system directly; enters coverage determination manually |
| Classification confidence below threshold | classification_confidence < 0.85 | Create EscalationBriefing (LOW_CLASSIFICATION_CONFIDENCE); 30-min review window | On-call specialist via CRM review queue | Specialist confirms or corrects claim_type; agent resumes from TRIAGING with corrected classification |
| SLA breach imminent | current_time > sla_deadline - 1800s AND status ≠ COMPLETED | Fire SLA breach-prevention alert (REQ-10) | Operations team via CRM alert | Operations team escalates to senior specialist; manual intervention to accelerate processing |
| Duplicate claim detected | claim with same policy_id AND loss_date AND claim_type exists AND was created within 24 hours [ASSUMED: 24-hour dedup window — see D5-U9] | Transition to DUPLICATE; do not process further; log duplicate_of = original_claim_id | On-call specialist via CRM alert within 5 minutes | Specialist confirms or overrides duplicate status; if override, agent resumes from RECEIVED |
| Receipt ACK delivery failed | AcknowledgementRecord.delivery_status = FAILED after 1 retry | Log ACK_FAILED; add to manual-send queue | On-call specialist via CRM alert within 5 minutes | Specialist sends manual acknowledgement; updates AcknowledgementRecord manually |
| No adjuster available | adjuster_available_count = 0 for required specialty | Transition to QUEUE_OVERFLOW; create EscalationBriefing; retry every 5 minutes for 60 minutes | On-call specialist via CRM review queue immediately | Specialist manually assigns adjuster; agent transitions claim to ROUTED on manual assignment confirmation |

---

## 10. Audit and governance

### Audit log schema
Every agent action writes one audit log entry. All entries include the following base fields:

```
Base audit fields (all entries):
- log_id: UUID v4, generated on write, immutable
- claim_id: UUID, foreign key → Claim.id
- action_type: enum [CLAIM_CREATED, STATUS_TRANSITION, EXTRACTION_COMPLETE,
                     CLASSIFICATION_COMPLETE, SEVERITY_ASSESSED, FLAG_DETECTED,
                     POLICY_RETRIEVED, COVERAGE_VALIDATED, ADJUSTER_SELECTED,
                     ASSIGNMENT_CREATED, ACK_SENT, ESCALATION_CREATED,
                     SPECIALIST_REVIEW_COMPLETE, SLA_WARNING_FIRED, ERROR_LOGGED]
- agent_id: string (agent version identifier)
- timestamp: ISO 8601 datetime UTC, immutable
- duration_ms: integer (processing time for this action)

Additional fields by action_type:
  EXTRACTION_COMPLETE: parse_confidence, extracted_fields (JSON)
  CLASSIFICATION_COMPLETE: claim_type, classification_confidence
  SEVERITY_ASSESSED: severity, severity_score, delegation_tier
  FLAG_DETECTED: flags_detected (array), confidence_per_flag (object)
  POLICY_RETRIEVED: policy_id, retrieval_method, policy_status_returned
  COVERAGE_VALIDATED: coverage_match_confidence, coverage_status, exclusion_candidates (array)
  ADJUSTER_SELECTED: adjuster_id, adjuster_specialty, queue_depth_at_selection, selection_method
  ASSIGNMENT_CREATED: assignment_id, adjuster_id
  ACK_SENT: acknowledgement_type, recipient_contact (masked to first 3 chars + @domain), delivery_status
  ESCALATION_CREATED: escalation_reason, review_window_deadline
  SPECIALIST_REVIEW_COMPLETE: reviewer_id, review_decision, original_value, corrected_value (if applicable)
  SLA_WARNING_FIRED: time_remaining_seconds, current_status
  ERROR_LOGGED: error_type, error_detail, retry_count, recovery_action
  STATUS_TRANSITION: from_status, to_status, transition_trigger
```

### Retention periods

| Log type | Retention period | Basis |
|---|---|---|
| Claim audit log (all entries) | 7 years | [ASSUMED: financial services regulatory requirement — see D5-A-Regulatory] |
| Claimant personal data (name, contact, raw claim text) | As per client data retention policy [UNKNOWN — see D5-U10] | GDPR / data protection |
| Integration error logs | 2 years | [ASSUMED: operational audit requirement] |
| SLA breach logs | 7 years | [ASSUMED: regulatory reporting] |
| Specialist review decisions | 7 years | Professional accountability audit |

### Compliance constraints
- **Data protection [ASSUMED: GDPR applies — see D5-A-Regulatory]:** Raw claim text (raw_input) may contain personal data (name, address, bank details). raw_input must be encrypted at rest. PII fields must be anonymisable on subject access request without deleting the audit record.
- **FCA / insurance regulatory requirements [ASSUMED: UK FCA rules apply — see D5-A-Regulatory]:** Claims handling SLAs and escalation decisions are subject to regulatory audit. Audit trail must be immutable and available for regulator inspection. Coverage dispute decisions must be logged with the name and authorisation level of the deciding specialist.
- **PCI-DSS [ASSUMED: may apply if payment card details appear in claim text]:** Agent must detect and redact payment card numbers (pattern: 16-digit sequences) from raw_input before storage. [TODO: confirm with client whether PCI-DSS applies — see D5-U10]

### HITL checkpoints with SLAs

| Checkpoint | Trigger | Review window | Escalation if breached |
|---|---|---|---|
| Parse uncertainty review | parse_confidence < 0.70 | 60 minutes | Claim.status = ESCALATED; senior specialist assigned |
| Low-confidence classification review | classification_confidence < 0.85 | 30 minutes | Claim.status = ESCALATED; SLA warning fired |
| HIGH/CRITICAL severity confirmation | severity ∈ {HIGH, CRITICAL} | 30 minutes | Claim.status = ESCALATED; senior specialist assigned |
| Special handling flag confirmation | special_handling_flags ≠ [] | 15 minutes | Claim.status = ESCALATED; senior specialist assigned immediately |
| Ambiguous coverage review | 0.70 ≤ coverage_match_confidence < 0.85 | 30 minutes | Claim.status = ESCALATED; SLA warning fired |
| Exclusion check confirmation | exclusion_candidates ≠ [] | 30 minutes | Claim.status = ESCALATED |
| Coverage dispute resolution | coverage_match_confidence < 0.70 | No automated window; specialist owns SLA | Senior specialist; operations notified if sla_deadline within 60 minutes |
| Queue overflow manual routing | adjuster_available_count = 0 | 60 minutes | SLA breach imminent; operations escalated |

---

## 11. Build artefacts

The following artefacts must be produced in `agent_build/` alongside the specification.

### Console application (`agent_build/src/main.py` or equivalent)

The console application must demonstrate the agent's core workflow end-to-end using a single configurable input file. It is not a production runtime; it is a closed build loop demonstration.

**Inputs:**
- `--input` (required): path to a JSON file containing a claim object with fields: source_channel, raw_input, policy_id, loss_date
- `--mock-policy` (required): path to a JSON file containing a mock policy record (used in place of the real SOAP endpoint)
- `--mock-adjusters` (required): path to a JSON file containing a mock adjuster pool array
- `--output-dir` (optional, default: `./output`): directory for HTML report and log output

**Behaviour:**
The application must execute and log each processing step in sequence:
1. Load input claim
2. Parse and extract attributes (log parse_confidence)
3. Classify claim type (log classification_confidence)
4. Assess severity (log severity_score and tier)
5. Detect special handling flags (log any flags found)
6. Validate policy coverage against mock policy record (log coverage_match_confidence)
7. Route to adjuster from mock adjuster pool (log selected adjuster_id and queue_depth)
8. Output final Claim state as JSON
9. Generate HTML report

Each step must print to console: step number, action taken, key output values, delegation tier applied, and whether the step triggered an escalation.

**On escalation:** The console app must print `[ESCALATION] reason: {reason}, review_window: {minutes} min` and continue processing as if a specialist confirmed the agent's recommendation (simulating the happy path through review).

### HTML report (`agent_build/output/report.html`)

The HTML report must be generated after the console application run and must contain:
- Header: claim external_reference, source_channel, processing date/time, total processing time (ms)
- Processing summary table: each step, duration (ms), outcome, delegation tier, escalation triggered (Y/N)
- Claim outcome section: final claim_type, severity, coverage_status, assigned adjuster_id, SLA status (MET / BREACHED)
- Assumptions flagged during run: list of [ASSUMED] markers encountered during processing with their field values

The HTML report must use inline CSS only (no external dependencies) and must render correctly when opened as a local file.

### Workflow diagram (`agent_build/docs/workflow.md` — Mermaid format)

```
flowchart TD
  A([EMAIL / PHONE_TRANSCRIPT / WEB_FORM]) --> B[PARSE & EXTRACT\nREQ-1 · AGENT_ONLY]
  B -->|parse_confidence ≥ 0.70| C[CLASSIFY CLAIM TYPE\nREQ-2 · AGENT_LOG]
  B -->|parse_confidence < 0.70| R1[SPECIALIST REVIEW\nPARSE_UNCERTAIN]
  R1 --> B
  C -->|confidence ≥ 0.85| D[ASSESS SEVERITY\nREQ-3]
  C -->|confidence < 0.85| R2[SPECIALIST REVIEW\nTRIAGE_PENDING_REVIEW]
  R2 --> D
  D -->|LOW / MEDIUM| E[DETECT FLAGS\nREQ-4 · AGENT_REVIEW]
  D -->|HIGH / CRITICAL| R3[SPECIALIST REVIEW\nTRIAGE_PENDING_REVIEW]
  R3 --> E
  E -->|no flags| F[VALIDATE COVERAGE\nREQ-5]
  E -->|flag detected| R4[SPECIALIST REVIEW\n15-min window]
  R4 --> F
  F -->|confidence ≥ 0.85, in force| G[ROUTE TO ADJUSTER\nREQ-6 · AGENT_ONLY]
  F -->|confidence 0.70–0.84 or exclusion| R5[SPECIALIST REVIEW\n30-min window]
  F -->|confidence < 0.70 or disputed| R6[HUMAN ONLY\nCOVERAGE_DISPUTED]
  F -->|policy lapsed| R7[HUMAN ONLY\nCOVERAGE_LAPSED]
  R5 --> G
  G -->|adjuster available| H[ASSIGN IN CRM\nREQ-6 · AGENT_LOG]
  G -->|no adjuster| R8[SPECIALIST MANUAL\nQUEUE_OVERFLOW]
  R8 --> H
  H --> I[NOTIFY ADJUSTER\nREQ-6 · AGENT_ONLY]
  I --> J[SEND ROUTING CONFIRMATION\nREQ-8 · AGENT_LOG]
  J --> K([COMPLETED])

  A -.->|within 5 min, unconditional| ACK[SEND RECEIPT ACK\nREQ-7 · AGENT_ONLY]
  style ACK fill:#d4edda
  style R6 fill:#f8d7da
  style R7 fill:#f8d7da
```

The diagram must be saved as `agent_build/docs/workflow.md` containing the Mermaid block above, and also rendered as a PNG using a Mermaid CLI command documented in `agent_build/docs/README.md`.
# Validation Design
## FNOL Processing Agent — Insurance Claims Automation

---

## 1. Validation strategy overview

Confirming the agent is right requires running structured test scenarios against known ground-truth outcomes — correct claim type, correct severity tier, correct adjuster specialty, correct delegation tier fired — and asserting that every output matches the expected value exactly. That confirms the happy path and known failure modes. Detecting that the agent is wrong when no one notices requires a different mechanism entirely: production monitoring that compares agent decisions against independent ground-truth signals that arrive after the fact. The primary quiet failure detection mechanism is **retrospective outcome comparison**: after a claim is processed, the adjuster's first recorded action (reserve value set, claim type confirmed, legal flag noted) is compared against the agent's original classification and routing decision. Systematic discrepancies between what the agent decided at FNOL intake and what the adjuster found on contact — claim value underestimated, specialty wrong, legal flag missed — are the signal that the agent is consistently wrong in a way that looks correct at processing time. This comparison runs as a nightly batch job against the prior 24 hours of routed claims, with alerts firing when discrepancy rates exceed defined thresholds. Without this retrospective signal, the agent can be completely wrong and every metric will look green.

---

## 2. Test scenarios

---

### Scenario 1: Standard Property Claim — Full Automation Path

```
Scenario 1: Standard property claim, end-to-end automation
Type: Happy Path

Description:
Tests the core automation path for a routine, low-complexity claim. Validates that
a standard property claim arrives, is processed entirely without human intervention,
and reaches COMPLETED within the 2-hour SLA. This is the baseline: if this fails,
nothing else is worth testing.

Preconditions:
- CRM is available and responding (HTTP 200 on health check)
- Policy admin system (mock) is available and returns a valid in-force policy record
- DMS is available
- Adjuster pool contains 3 PROPERTY adjusters with queue depths 1, 3, 6
- No active INTEGRATION_ERROR states in the system
- Email inbox polling is active

Input:
- source_channel: EMAIL
- raw_input: "I need to report a claim. My name is Sarah Chen. Policy number PR-87654321.
  On 12 January 2025 a burst pipe flooded my kitchen. Estimated repair cost from
  the plumber is around £4,500. Please can you process this urgently."
- Mock policy record:
    policy_id: PR-87654321
    policy_status: ACTIVE
    policy_start_date: 2023-06-01
    policy_end_date: 2026-06-01
    covered_perils: [PROPERTY_WATER_DAMAGE, PROPERTY_FIRE, PROPERTY_THEFT]
    exclusions: []
- Mock adjuster pool: [
    {adjuster_id: ADJ-101, specialty: PROPERTY, queue_depth: 1, is_available: true},
    {adjuster_id: ADJ-102, specialty: PROPERTY, queue_depth: 3, is_available: true},
    {adjuster_id: ADJ-103, specialty: PROPERTY, queue_depth: 6, is_available: true}
  ]

Expected agent behaviour (step by step):
1. ClaimRecord created (status = RECEIVED, external_reference = PR-XXXXXXXX,
   sla_deadline = created_at + 7200s)
2. DMS store initiated in parallel (document stored within 10s)
3. AcknowledgementRecord (RECEIPT) created and email sent to claimant within 300s of created_at;
   content includes external_reference and 2-hour SLA statement; no coverage language
4. Claim transitions RECEIVED → PARSING
5. NLP extraction: policy_id = PR-87654321, loss_date = 2025-01-12, claim_type_candidate = PROPERTY,
   estimated_loss_value = 4500, parse_confidence = 0.91 (above 0.70 threshold)
6. Claim transitions PARSING → PARSED
7. Claim transitions PARSED → TRIAGING
8. Classification: claim_type = PROPERTY, classification_confidence = 0.93 (above 0.85)
9. Severity scoring: severity_score = 38 (loss_value £4,500 < £10,000 AND no CRITICAL_EVENT
   flags); severity = LOW
10. Special handling flag scan: no fatality, legal, fraud, or vulnerable signals detected;
    special_handling_flags = []
11. Claim transitions TRIAGING → TRIAGED (no EscalationBriefing created)
12. Claim transitions TRIAGED → VALIDATING
13. Policy retrieval from mock: IN_FORCE, policy_start_date ≤ loss_date ≤ policy_end_date
14. Coverage match: PROPERTY_WATER_DAMAGE matches classified claim_type PROPERTY;
    coverage_match_confidence = 0.93 (above 0.85); exclusion_candidates = []
15. Claim transitions VALIDATING → COVERAGE_CONFIRMED (AGENT_LOG; no EscalationBriefing)
16. Claim transitions COVERAGE_CONFIRMED → ROUTING
17. Adjuster selection: specialty_required = PROPERTY; candidates = [ADJ-101(depth 1),
    ADJ-102(depth 3), ADJ-103(depth 6)]; selected = ADJ-101 (lowest queue_depth)
18. ClaimAssignment created: adjuster_id = ADJ-101, assignment_method = AGENT_ALGORITHM
19. CRM PATCH: Claim.status = ROUTED
20. Adjuster notification sent to ADJ-101 via CRM within 60s of assignment
21. AcknowledgementRecord (ROUTING_CONFIRMATION) created; email sent to claimant with
    adjuster name, contact details, and expected contact timeframe
22. Claim transitions ROUTED → ACKNOWLEDGED → COMPLETED
23. Total elapsed time from created_at to COMPLETED: < 180s (3 minutes)

Expected output:
- Claim.status = COMPLETED
- Claim.claim_type = PROPERTY
- Claim.severity = LOW
- Claim.coverage_status = COVERED
- Claim.sla_breached = false
- ClaimAssignment.adjuster_id = ADJ-101
- ClaimAssignment.assignment_method = AGENT_ALGORITHM
- AcknowledgementRecord count for this claim = 2 (RECEIPT + ROUTING_CONFIRMATION)
- AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s
- EscalationBriefing count for this claim = 0
- Audit log entry count ≥ 10 (one per named action in steps above)
- DMS document stored = 1

Pass criterion:
  Claim.status = COMPLETED
  AND ClaimAssignment.adjuster_specialty = PROPERTY
  AND AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s
  AND EscalationBriefing.count = 0
  AND total_elapsed_seconds < 180
  AND Claim.sla_breached = false

Fail criterion:
  Claim.status ≠ COMPLETED after 300s
  OR ClaimAssignment.adjuster_specialty ≠ PROPERTY
  OR AcknowledgementRecord[RECEIPT].sent_at > Claim.created_at + 300s
  OR EscalationBriefing.count > 0
  OR Claim.sla_breached = true

Quiet failure risk:
The agent selects adjuster ADJ-101 (PROPERTY specialty, queue depth 1) correctly.
But if the specialty mapping table has a data error and PROPERTY maps to GENERAL,
the agent assigns a GENERAL adjuster, the claim reaches COMPLETED, and all metrics
look correct. The claimant is acknowledged, the adjuster is notified — the error
only surfaces when the GENERAL adjuster contacts the claimant and lacks the
specialist knowledge to handle a water damage claim.

Detection mechanism: Nightly batch job compares ClaimAssignment.adjuster_specialty
against specialty_map[Claim.claim_type] for all claims assigned in the prior 24h.
Alert fires if specialty mismatch count > 5% of routed claims (15 claims on a 300/day
volume). This is independent of whether the claim reached COMPLETED.
```

---

### Scenario 2: Severity Threshold Boundary — Low/Medium vs High/Critical

```
Scenario 2: Severity threshold boundary — sub-case A (below) and sub-case B (above)
Type: Delegation Boundary

Description:
Tests that the severity threshold (severity_score = 60, corresponding to claim_value
≈ £10,000) fires the correct delegation tier on both sides of the boundary. Sub-case A
(score = 59) must produce AGENT_LOG with no escalation. Sub-case B (score = 61) must
produce AGENT_REVIEW with an EscalationBriefing. Both claims are otherwise identical.
This tests the boundary established in D2 tier 1.3/1.4 and the threshold flagged as
[TODO: D5-U1]. If the boundary is off by even one point, one class of high-value
claims will be silently under-escalated.

Preconditions:
- CRM available; policy admin mock available; same mock policy record for both sub-cases
- Mock policy: policy_id = MO-11223344, status = ACTIVE, covered_perils = [MOTOR_COLLISION]
- Adjuster pool: 2 MOTOR adjusters available, queue depths 2 and 4
- Severity scoring model configured with £10,000 threshold and score boundary at 60

--- Sub-case A: score below threshold ---

Input:
- source_channel: WEB_FORM
- policy_id: MO-11223344
- loss_date: 2025-02-03
- claim_type_candidate: MOTOR
- estimated_loss_value: £9,800
- loss_description: "Rear-end collision, significant boot and bumper damage"
- special_handling_flags candidate: none
- Severity model output for this input: severity_score = 59

Expected agent behaviour:
1. Parse and extract: parse_confidence = 0.94
2. Classify: claim_type = MOTOR, classification_confidence = 0.91
3. Severity: severity_score = 59; severity = MEDIUM (59 < 60 threshold)
4. Delegation tier 1.3 fires: AGENT_LOG
5. Claim transitions TRIAGING → TRIAGED
6. No EscalationBriefing created at triage stage

Expected output (Sub-case A):
- Claim.severity = MEDIUM
- Claim.status transitions through to TRIAGED without TRIAGE_PENDING_REVIEW
- EscalationBriefing.count at triage stage = 0
- Audit log contains entry: action_type = SEVERITY_ASSESSED, severity = MEDIUM,
  severity_score = 59, delegation_tier = AGENT_LOG

Pass criterion (Sub-case A):
  Claim.status = TRIAGED (not TRIAGE_PENDING_REVIEW)
  AND Claim.severity = MEDIUM
  AND EscalationBriefing.count = 0 at triage stage
  AND audit log entry severity_score = 59 AND delegation_tier = AGENT_LOG

Fail criterion (Sub-case A):
  Claim.status = TRIAGE_PENDING_REVIEW
  OR EscalationBriefing created at triage stage
  OR Claim.severity ∈ {HIGH, CRITICAL}

--- Sub-case B: score above threshold ---

Input:
- All fields identical to Sub-case A except:
- estimated_loss_value: £10,200
- Severity model output for this input: severity_score = 61

Expected agent behaviour:
1. Parse and extract: parse_confidence = 0.94
2. Classify: claim_type = MOTOR, classification_confidence = 0.91
3. Severity: severity_score = 61; severity = HIGH (61 ≥ 60 threshold)
4. Delegation tier 1.4 fires: AGENT_REVIEW
5. Claim transitions TRIAGING → TRIAGE_PENDING_REVIEW
6. EscalationBriefing created: escalation_reason = HIGH_SEVERITY,
   review_window_deadline = created_at + 1800s (30 min)
7. Specialist notified via CRM review queue within 30s

Expected output (Sub-case B):
- Claim.severity = HIGH
- Claim.status = TRIAGE_PENDING_REVIEW
- EscalationBriefing.count = 1 at triage stage
- EscalationBriefing.escalation_reason = HIGH_SEVERITY
- EscalationBriefing.review_window_deadline = claim.created_at + 1800s
- CRM review queue entry visible within 30s

Pass criterion (Sub-case B):
  Claim.status = TRIAGE_PENDING_REVIEW
  AND Claim.severity = HIGH
  AND EscalationBriefing.count = 1
  AND EscalationBriefing.review_window_deadline = claim.created_at + 1800s
  AND CRM review queue entry created within 30s

Fail criterion (Sub-case B):
  Claim.status = TRIAGED (bypassed TRIAGE_PENDING_REVIEW)
  OR EscalationBriefing.count = 0
  OR Claim.severity ∈ {LOW, MEDIUM}

Quiet failure risk:
The boundary test confirms the threshold fires correctly when the estimated_loss_value
is extracted accurately. The quiet failure is when the NLP extraction reads £10,200 as
£1,020 (misplaced decimal or comma parsing error). The agent scores severity_score = 32
(LOW), bypasses AGENT_REVIEW, and routes the £10,200 claim as a LOW-priority case.
The claim reaches COMPLETED. No specialist ever sees it at triage.

Detection mechanism: Nightly batch comparison of Claim.estimated_loss_value (extracted
at FNOL) against ClaimAssignment adjuster's first recorded reserve value in CRM.
Alert fires if extracted_value < 0.5 × adjuster_reserve_value for more than 3 claims
per day (indicating systematic extraction underestimation). This catches the pattern
before it compounds.
```

---

### Scenario 3: Ambiguous Coverage with Exclusion Candidate

```
Scenario 3: Coverage confidence in AGENT_REVIEW band with exclusion candidate present
Type: Edge Case

Description:
Tests the coverage validation path when the agent identifies a coverage match but
with low-to-medium confidence AND an exclusion candidate. Both conditions independently
trigger AGENT_REVIEW (D2 tier 2.4 and 2.5). This scenario verifies that either condition
alone is sufficient to trigger the review, and that the EscalationBriefing correctly
surfaces both the confidence score and the exclusion clause reference for the specialist.
A common failure mode is that exclusion detection fires correctly but the briefing note
omits the policy clause text — the specialist then confirms without actually reading
the clause.

Preconditions:
- Policy admin mock configured to return a policy with one candidate exclusion
- Mock policy:
    policy_id: PR-99887766
    policy_status: ACTIVE
    covered_perils: [PROPERTY_WATER_DAMAGE, PROPERTY_ACCIDENTAL_DAMAGE]
    exclusions: ["Clause 14.3: Damage arising from gradual deterioration or wear and tear"]
- Adjuster pool: 2 PROPERTY adjusters available
- Coverage model configured to return coverage_match_confidence = 0.72 for this
  claim/policy combination (in the 0.70–0.84 AGENT_REVIEW band)
- Exclusion detection model configured to flag Clause 14.3 with exclusion_confidence = 0.78

Input:
- source_channel: PHONE_TRANSCRIPT
- raw_input: "Transcript ref 20250220-4421. Claimant: David Okafor. Policy PR-99887766.
  Reporting damp and water staining on the living room ceiling. Has been there a while,
  noticed it getting worse over the past few months. Thinks it might be a slow leak from
  the bathroom above. Estimated repair cost approximately £3,800."
- loss_date: 2025-02-20
- estimated_loss_value: £3,800

Expected agent behaviour:
1. Parse: parse_confidence = 0.88; extracted claim_type_candidate = PROPERTY,
   loss_description = "gradual water ingress / ceiling damp from suspected slow leak"
2. Classify: claim_type = PROPERTY, classification_confidence = 0.89
3. Severity: severity_score = 36 (£3,800 < £10,000, no CRITICAL_EVENT); severity = LOW
4. Flag scan: no fatality, legal, fraud, or vulnerable signals; special_handling_flags = []
5. Transition TRIAGING → TRIAGED
6. Policy retrieval: IN_FORCE, policy_start_date ≤ loss_date ≤ policy_end_date
7. Coverage matching: coverage_match_confidence = 0.72 (in 0.70–0.84 band → AGENT_REVIEW)
8. Exclusion scan: Clause 14.3 identified as candidate exclusion;
   exclusion_confidence = 0.78; exclusion_candidates = ["Clause 14.3"]
9. Either condition alone triggers AGENT_REVIEW; both conditions present — single
   EscalationBriefing created with both signals surfaced
10. Claim transitions VALIDATING → COVERAGE_PENDING_REVIEW
11. EscalationBriefing created: escalation_reason = AMBIGUOUS_COVERAGE,
    escalation_detail includes: coverage_match_confidence = 0.72,
    exclusion_candidates = ["Clause 14.3: Damage arising from gradual deterioration
    or wear and tear"], full policy_snapshot, full claim_snapshot
12. Review window: review_window_deadline = created_at + 1800s
13. Specialist presented with: agent's coverage determination, policy clause text
    (Clause 14.3 verbatim), and claim narrative

Expected output:
- Claim.status = COVERAGE_PENDING_REVIEW
- Claim.coverage_match_confidence = 0.72
- Claim.exclusion_candidates = ["Clause 14.3"]
- EscalationBriefing.count = 1
- EscalationBriefing.escalation_detail contains policy_snapshot with Clause 14.3 text
- EscalationBriefing.escalation_detail contains coverage_match_confidence = 0.72
- EscalationBriefing.review_window_deadline = created_at + 1800s
- AcknowledgementRecord[RECEIPT] sent within 300s (fires independently of coverage state)
- No AcknowledgementRecord[ROUTING_CONFIRMATION] yet (routing not yet determined)

Pass criterion:
  Claim.status = COVERAGE_PENDING_REVIEW
  AND EscalationBriefing.count = 1
  AND EscalationBriefing.escalation_detail CONTAINS coverage_match_confidence = 0.72
  AND EscalationBriefing.escalation_detail CONTAINS "Clause 14.3"
  AND AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s
  AND AcknowledgementRecord[ROUTING_CONFIRMATION].count = 0

Fail criterion:
  Claim.status = COVERAGE_CONFIRMED (bypassed AGENT_REVIEW — agent over-confident)
  OR EscalationBriefing.escalation_detail DOES NOT CONTAIN exclusion clause text
    (specialist briefed without the evidence needed to make a decision)
  OR AcknowledgementRecord[RECEIPT] NOT sent within 300s
    (SLA-critical ACK blocked by coverage review state — must not happen)

Quiet failure risk:
The agent correctly triggers AGENT_REVIEW but the EscalationBriefing omits the
policy_snapshot or renders it as a raw policy_id reference rather than the actual
clause text. The specialist sees "exclusion candidate: Clause 14.3" but not the
clause wording. They confirm coverage without reading the clause. A "gradual
deterioration" exclusion that should have denied coverage is rubber-stamped.

Detection mechanism: Structured audit of EscalationBriefing records where
resolution = CONFIRMED and exclusion_candidates ≠ []. Sample 100% of these cases
for the first 30 days post-go-live; specialist confirms they reviewed clause text,
not just the reference. Long-term: if adjuster-recorded coverage dispute rate for
claims with exclusion candidates > 15%, trigger briefing content audit.
```

---

### Scenario 4: Policy Administration System Unavailable Mid-Processing

```
Scenario 4: SOAP policy admin system unavailable — all retries exhausted
Type: Failure Mode

Description:
Tests the INTEGRATION_ERROR path when the legacy policy administration system is
unavailable during coverage validation. This is the most likely production failure
given the system is described as "legacy." The critical assertions are: (1) the
receipt ACK was already sent before policy retrieval — it must not be withheld, (2)
the claim halts correctly at VALIDATING without proceeding to routing, (3) the
specialist is notified within 5 minutes, and (4) processing resumes correctly after
the system recovers. This scenario also tests that DMS storage is non-blocking —
a DMS failure at the same time must not compound the error.

Preconditions:
- CRM available
- Policy admin system mock configured to return HTTP 503 on all requests for this test run
- DMS available
- Adjuster pool available (not needed — routing should not be reached)
- Receipt ACK was queued successfully at claim receipt (pre-condition: email service available)

Input:
- source_channel: EMAIL
- raw_input: "Claim notification. Policy LI-55443322. Date of incident 15 March 2025.
  Liability claim — I was involved in a dispute with a neighbour causing property damage.
  Estimated damage £6,200."
- loss_date: 2025-03-15
- estimated_loss_value: £6,200
- Mock policy admin: configured to return HTTP 503 (Service Unavailable) on all requests
  for policy_id LI-55443322; all 3 retries (2s/4s/8s backoff) return 503

Expected agent behaviour:
1. ClaimRecord created (status = RECEIVED)
2. DMS store initiated
3. AcknowledgementRecord (RECEIPT) created and sent within 300s — fires before policy
   retrieval; must not be affected by SOAP failure
4. Parse: parse_confidence = 0.87; claim_type_candidate = LIABILITY
5. Classify: LIABILITY, confidence = 0.88
6. Severity: severity_score = 42; severity = MEDIUM; no flags
7. Transition TRIAGING → TRIAGED
8. Transition TRIAGED → VALIDATING
9. Policy retrieval attempt 1: HTTP 503 → wait 2s
10. Policy retrieval attempt 2: HTTP 503 → wait 4s
11. Policy retrieval attempt 3: HTTP 503 → wait 8s
12. All retries exhausted (total elapsed for retry cycle: 14s)
13. Claim transitions VALIDATING → INTEGRATION_ERROR
14. EscalationBriefing created: escalation_reason = INTEGRATION_ERROR,
    escalation_detail = "Policy admin system unavailable; 3 retries exhausted;
    policy_id = LI-55443322"
15. Specialist notified via CRM review queue within 5 minutes of INTEGRATION_ERROR
16. Processing halted — claim does NOT transition to COVERAGE_CONFIRMED or ROUTING
17. [Recovery] Specialist resolves issue; triggers manual policy lookup in CRM
18. Agent receives manual policy record; transitions INTEGRATION_ERROR → VALIDATING
19. Coverage validation proceeds with manually provided policy record
20. Claim continues to COMPLETED (assuming policy is in-force and coverage confirmed)

Expected output:
- Claim.status = INTEGRATION_ERROR (before recovery)
- AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s (unaffected by failure)
- EscalationBriefing.escalation_reason = INTEGRATION_ERROR
- EscalationBriefing created within 30s of INTEGRATION_ERROR transition
- Specialist notification visible in CRM review queue within 300s of INTEGRATION_ERROR
- No ClaimAssignment record exists (routing not attempted)
- No AcknowledgementRecord[ROUTING_CONFIRMATION] (not sent)
- Audit log entry: action_type = ERROR_LOGGED, error_type = INTEGRATION_ERROR,
  retry_count = 3, error_detail contains "HTTP 503"

Pass criterion:
  Claim.status = INTEGRATION_ERROR after retry exhaustion
  AND AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s
  AND ClaimAssignment.count = 0
  AND EscalationBriefing.escalation_reason = INTEGRATION_ERROR
  AND specialist CRM notification created within 300s of INTEGRATION_ERROR
  AND audit log retry_count = 3

Fail criterion:
  Claim.status = COVERAGE_CONFIRMED or ROUTED (processing continued past INTEGRATION_ERROR)
  OR AcknowledgementRecord[RECEIPT] NOT sent within 300s
  OR EscalationBriefing.count = 0
  OR specialist notification NOT created within 300s

Quiet failure risk:
After INTEGRATION_ERROR, the specialist manually enters the policy record via CRM.
If the specialist enters policy_status = IN_FORCE when the policy is actually LAPSED
(misread policy number, wrong policy retrieved), the agent validates coverage against
the wrong record. The claim proceeds to ROUTING and COMPLETED. The error is only
discovered when the adjuster contacts the claimant and the claimant has no valid
policy. At that point, a coverage decision has been implicitly communicated.

Detection mechanism: For all claims where ClaimAuditLog contains retrieval_method =
MANUAL, flag for mandatory specialist supervisor sign-off before the claim can
transition from INTEGRATION_ERROR back to VALIDATING. Alternatively: once the policy
admin system recovers, automated reconciliation of all manually-entered policy records
against the live system; alert if any discrepancy found. Either mechanism must run
before the 2-hour SLA window closes.
```

---

### Scenario 5: Under-Escalation at the Delegation Boundary — Extraction Value Error Causing Silent Severity Downgrade

```
Scenario 5: NLP extraction misreads claim value; HIGH claim processed as LOW
Type: Failure Mode / Delegation Boundary

Description:
Tests the most dangerous quiet failure mode for this agent: the NLP extraction
produces an estimated_loss_value that is significantly lower than the true value,
causing the severity scoring model to produce LOW instead of HIGH. The claim bypasses
AGENT_REVIEW entirely. It reaches COMPLETED. No specialist ever reviews it at triage.
The adjuster only discovers the true value when contacting the claimant. This is a
failure at the delegation boundary (the HIGH/CRITICAL threshold) that is undetectable
by the standard happy-path test suite, because from the pipeline's perspective
everything worked correctly — the agent processed the claim end-to-end as designed
for a LOW claim.

Preconditions:
- CRM, policy admin mock, DMS all available
- Mock policy: policy_id = MO-66554433, ACTIVE, covered_perils = [MOTOR_COLLISION]
- NLP extraction model in this test is configured to misparse "£14,000" as "£1,400"
  (simulating a comma/period locale parsing error: "14,000" read as "1.400" → £1,400)
- Adjuster pool: 2 MOTOR adjusters available

Input:
- source_channel: EMAIL
- raw_input: "Dear claims team, I'm writing about a serious collision on 4 April 2025.
  Policy ref MO-66554433. My car was written off — the repair estimate from the garage
  is £14,000 which is more than the car is worth. I also had to hire a replacement
  vehicle at £350. Please advise urgently."
- loss_date: 2025-04-04
- True estimated_loss_value in input: £14,000
- Extraction model output (defective): estimated_loss_value = £1,400

Expected agent behaviour (with extraction defect active):
1. Parse: parse_confidence = 0.89; extracted estimated_loss_value = £1,400 (WRONG)
2. Classify: claim_type = MOTOR, classification_confidence = 0.92
3. Severity scoring: severity_score = 14 (based on £1,400, well below £10,000 threshold)
4. Severity = LOW
5. Tier 1.3 fires: AGENT_LOG (no AGENT_REVIEW triggered — this is the failure)
6. Claim transitions TRIAGING → TRIAGED (no EscalationBriefing)
7. Coverage match: MOTOR_COLLISION covered; confidence = 0.91; no exclusions
8. Transition → COVERAGE_CONFIRMED
9. Routing: MOTOR adjuster selected (ADJ-201, queue depth 1)
10. Claim reaches COMPLETED
11. AcknowledgementRecord[RECEIPT] and [ROUTING_CONFIRMATION] both sent
12. Claim appears successful in all dashboard metrics

Expected output (with defect — this is what the agent DOES, not what it should do):
- Claim.status = COMPLETED
- Claim.severity = LOW
- Claim.estimated_loss_value = £1,400 (wrong)
- EscalationBriefing.count = 0
- All SLA metrics green
- No human specialist ever reviewed the triage decision

Pass criterion for this scenario (tests that the DETECTION mechanism fires):
  Nightly batch job runs comparing Claim.estimated_loss_value against
  ClaimAssignment adjuster's first recorded reserve value for this claim
  AND adjuster records reserve = £14,000 (or similar) within 48h of assignment
  AND discrepancy alert fires: extracted_value (£1,400) < 0.5 × adjuster_reserve (£14,000)
  AND alert is delivered to operations team

Fail criterion:
  Nightly batch comparison does NOT run for this claim
  OR adjuster reserve is recorded but discrepancy threshold check does not fire
  OR alert fires but is delivered to an unmonitored queue (alert acknowledged = false
     within 24h of firing)

Quiet failure risk:
This scenario IS the quiet failure. The detection mechanism (retrospective comparison
of extracted value against adjuster reserve) is the only signal. If the adjuster does
not set a reserve value within 48h of assignment (e.g., claim is sitting in their
queue unactioned), the discrepancy is never detected.

Detection mechanism (two layers):
Primary: Nightly batch — compare Claim.estimated_loss_value against adjuster reserve
  for all claims closed or updated in prior 24h; alert if extracted < 0.5 × reserve
  for > 3 claims/day.
Secondary: For any MOTOR or PROPERTY claim where Claim.estimated_loss_value < £2,000
  but adjuster does not set a reserve within 72h of assignment, flag for
  supervisor review — unactioned low-value claims assigned to motor specialists are
  a red flag for misclassified high-value claims.
```

---

## 3. Delegation boundary test

Scenario 2 above is the explicit delegation boundary test (`Type: Delegation Boundary`). It covers:

- **The boundary tested:** severity_score threshold between AGENT_LOG (score ≤ 59) and AGENT_REVIEW (score ≥ 60), which maps to the D2 tier 1.3 / 1.4 split
- **Sub-case A** (score = 59): must produce TRIAGED with no EscalationBriefing — confirms AGENT_LOG fires correctly below the threshold
- **Sub-case B** (score = 61): must produce TRIAGE_PENDING_REVIEW with EscalationBriefing — confirms AGENT_REVIEW fires correctly above the threshold
- **Why this boundary matters:** if the threshold is off by one point in the wrong direction, every claim in the £9,000–£11,000 range is either over-escalated (defeating the automation ROI) or under-escalated (high-value claims processed without specialist review)

Scenario 5 also tests a delegation boundary failure — specifically the case where the boundary threshold fires on corrupted input data, not on the correct input value. This is distinct from Scenario 2: Scenario 2 tests whether the threshold fires at the right value; Scenario 5 tests whether the threshold can be silently defeated by an upstream extraction error.

---

## 4. Quiet failure detection design

| Quiet failure mode | Why it would not be caught by standard tests | Detection mechanism |
|---|---|---|
| Agent routes claim to wrong adjuster specialty (e.g. PROPERTY claim assigned to GENERAL adjuster) | Standard tests confirm the claim reaches COMPLETED and the claimant is acknowledged. Routing accuracy is not verified post-assignment in the happy-path test. The COMPLETED state looks identical whether the specialty is correct or wrong. | Nightly batch: compare ClaimAssignment.adjuster_specialty against specialty_map[Claim.claim_type] for all claims assigned in the prior 24h. Alert fires if mismatch count > 5% of routed claims (threshold: 15 mismatches on a 300-claim day). Alert delivered to operations team via CRM. |
| NLP extraction systematically underestimates claim value for a specific input format (e.g. comma-formatted numbers: "14,000" parsed as "1,400") | Standard tests use manually crafted inputs with unambiguous value formats. Production inputs arrive from real claimants whose formatting varies by locale, channel, and literacy. A parsing defect on comma-formatted numbers would affect all such claims silently — each reaches COMPLETED with green metrics. | Nightly batch: compare Claim.estimated_loss_value (extracted at FNOL) against adjuster's first recorded reserve value for the same claim. Alert fires if extracted_value < 0.5 × adjuster_reserve for > 3 claims in any 24h window. This requires the CRM to expose the adjuster reserve field; flagged as dependency in D5. |
| Coverage confidence inflation — agent assigns coverage_match_confidence = 0.88 to a genuinely ambiguous claim, bypassing AGENT_REVIEW | Standard tests set coverage_match_confidence in the test fixture. In production, the confidence model runs on real policy language it may not have been trained on. A model that is systematically overconfident on certain policy clause types will never trigger AGENT_REVIEW, and all claims in that clause category will be auto-confirmed. The metric "coverage validation confidence distribution" looks healthy because high scores are recorded. | Track post-routing coverage dispute rate: % of COVERAGE_CONFIRMED (AGENT_LOG) claims where the adjuster subsequently records a coverage dispute or refers back to claims manager within 30 days of assignment. Alert fires if this rate exceeds 8% of AGENT_LOG coverage decisions over a rolling 30-day window. This retrospective signal catches systematic overconfidence that confidence score monitoring alone cannot detect. |
| Special handling flag missed for indirect or non-standard phrasing (e.g. "my wife's solicitor suggested I call" — LEGAL_REPRESENTATION not triggered by keyword match) | Standard tests inject claims with exact keyword matches from the defined keyword set. Production claimants paraphrase, hedge, and reference legal representation indirectly. A keyword-based detector has a hard boundary: if the phrase does not match the list, no flag. Tests only cover the listed keywords. | Monthly reconciliation: compare FNOL LEGAL_REPRESENTATION flag rate against rate at which adjusters subsequently record "claimant represented by solicitor" in CRM notes. Alert fires if adjuster-reported legal representation rate exceeds FNOL-detected rate by more than 3 percentage points over a rolling 30-day window. This gap is the false negative rate for the flag detector. |
| SLA breach prevention alert fires correctly but is delivered to an unmonitored queue or inbox | Standard tests confirm the SLA warning alert is sent (REQ-10 pass criterion). They do not test whether anyone receives or acts on it. If the alert destination (operations team CRM queue or email) is unmonitored outside business hours, 100% of out-of-hours at-risk claims breach SLA silently with green alert-sent metrics. | Monitor alert acknowledgement: for every SLA breach-prevention alert sent, check for acknowledgement (CRM queue "viewed" event or email open) within 15 minutes. If no acknowledgement within 15 minutes, escalate to secondary contact (on-call mobile number [TODO: D5-U9 — contact list not defined]). Track unacknowledged alert rate; alert fires if > 2 unacknowledged SLA warnings in any 24h window. |

---

## 5. Metrics to watch in production

| Metric | Measurement method | Alert threshold | Action if breached |
|---|---|---|---|
| Agent routing accuracy | Nightly batch: ClaimAssignment.adjuster_specialty vs specialty_map[Claim.claim_type] for all claims routed in prior 24h. Accuracy = matched / total routed. | < 95% accuracy (> 15 mismatches on 300-claim day) | Pause agent routing immediately; all routing switches to AGENT_SUPPORT (manual); investigate specialty mapping table and claim_type classification accuracy; resume only after root cause confirmed |
| SLA compliance rate | Daily: % of claims where AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.sla_deadline for all claims closed on that calendar day. | < 90% on any calendar day (> 30 SLA breaches on 300-claim day) | Operations review same day; examine INTEGRATION_ERROR count, COVERAGE_DISPUTED backlog, and QUEUE_OVERFLOW duration for that day; report to client within 24h |
| Escalation rate (two-sided) | Daily: % of claims where EscalationBriefing.count ≥ 1, measured across all claims ingested that day. | < 10%: under-escalating (fewer than 30 escalations on 300-claim day). > 40%: over-escalating (more than 120 escalations) | < 10%: review confidence thresholds; sample 20 AGENT_LOG decisions for spot-check; risk of silent under-escalation. > 40%: review threshold calibration; check for model drift or input format changes; automation ROI at risk |
| Coverage validation confidence distribution | Daily: median and p10 of coverage_match_confidence across all claims that reached VALIDATING that day. | Median drops below 0.78 (from expected ~0.90) OR p10 drops below 0.60 | Investigate policy data quality; check if new policy types or clause formats were introduced; consider temporary lowering of AGENT_LOG threshold to 0.88 until cause identified |
| False negative escalation rate | Weekly: % of AGENT_LOG decisions (severity LOW/MEDIUM, no escalation) that were subsequently corrected by a specialist (claim_type changed OR severity upgraded OR coverage_status changed from COVERED). Measured from CRM audit trail. | > 5% of AGENT_LOG decisions corrected per week (> 105 corrections on 2,100 weekly AGENT_LOG decisions at 300/day) | Review scoring model accuracy; inspect corrected claims for patterns (specific claim types, channels, or value ranges over-represented); recalibrate confidence thresholds or severity model; do not accept > 5% correction rate as steady-state |
| Receipt ACK timeliness | Continuous: for every ClaimRecord, check AcknowledgementRecord[RECEIPT].sent_at ≤ Claim.created_at + 300s. Report as daily % in-time. | < 98% (> 6 ACKs late on 300-claim day) | Investigate email delivery pipeline; check CRM SEND_EMAIL operation latency; if systemic, switch to direct SMTP fallback for ACK send |
| Adjuster reassignment rate | Weekly: % of ClaimAssignments where superseded_at is set within 24h of created_at. | > 10% (> 210 reassignments/week on 2,100 weekly assignments) | Review specialty mapping accuracy; check adjuster availability data freshness in CRM; high reassignment rate indicates routing decisions based on stale adjuster pool data |
| Post-routing coverage dispute rate | Monthly rolling 30-day: % of COVERAGE_CONFIRMED (AGENT_LOG) claims where adjuster subsequently records coverage dispute in CRM within 30 days. | > 8% of AGENT_LOG coverage confirmations disputed | Investigate coverage confidence model; audit EscalationBriefing records for the disputed claims to identify what confidence score was assigned; likely indicates systematic model overconfidence on a specific coverage type |
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
