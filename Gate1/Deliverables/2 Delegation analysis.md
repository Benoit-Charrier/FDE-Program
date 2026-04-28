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
