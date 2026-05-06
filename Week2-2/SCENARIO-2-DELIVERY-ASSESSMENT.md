# Scenario 2 Delivery Assessment — What Works, Where Gaps Are, How to Fix

**Deliverables Reviewed:** CLAUDE.md + D1–D6 (7 files total)  
**Assessment Date:** May 5, 2026  
**Scenario:** Helix Workforce Software — Vendor Contract Clause Review  
**Overall Verdict:** ⚠️ **STRONG FOUNDATION WITH CRITICAL GAPS — 78% Ready for Submission**

---

## ONE-LINE VERDICT

**Would pass as submitted, but with material gaps in governance enforcement, system integration validation, and discovery question sharpness that would prevent real deployment.** Recommend targeted fixes before final submission.

---

## What Works Well ✅

### 1. **CLAUDE.md — Excellent Process Discipline**
**File:** CLAUDE.md  
**What's good:**
- Clear role definition (FDE assistant, not builder)
- Explicit deliverable pipeline with sequence order
- Strong assumptions logging discipline template
- Quality standards for each deliverable type named explicitly
- Good call: "Quiet inference dressed as fact is the primary Week 2 failure mode"

**Why it matters:** This governance structure would catch many Week 2 anti-patterns. The expectation that every non-trivial claim traces to `scenario_context.md` or is logged as an assumption is the right bar.

---

### 2. **D1 (Cognitive Load Map) — Excellent Lived-Work Grounding**
**File:** D1_cognitive_load_map.md  
**What's good:**
- Opens with a clear-eyed lived process narrative (Tom starts his morning, finds contracts in Outlook, opens Word docs...)
- Flags THREE pause points where judgment happens, not just tasks
- Explicitly surfaces the workaround: "If vendor won't accept SharePoint, Tom remembers to send via email instead" — this is real work, not in the SOP
- Marks informal consultation (Tom asks Sarah via Teams) as a breakpoint and surfaces the invisibility risk
- Breakpoint on data staleness: "Tom cannot compare DPA clause; playbook is stale"
- Shows the decision is *not* rule-based: "He has internalised a threshold from experience, but it is not written anywhere"

**Why it's strong:** This is what Week 2 discovery *should* look like — the narrative reveals what the SOP doesn't say. Not a generic "Tom reviews contracts" but "Tom reads the doc, pauses when he sees something odd, makes an informal judgment call, asks a colleague via Teams, works around vendor system constraints."

**Score:** 90/100

---

### 3. **D2 (Delegation Suitability Matrix) — Disciplined Anti-Pattern Avoidance**
**File:** D2_delegation_suitability_matrix.md  
**What's good:**
- Explicitly calls out that C-3 (escalation threshold judgment) is "currently informal and undocumented" — this is Why Tom cannot be replaced yet
- Assigns C-3 as "Human-led + Agent Support" with clear rationale: agent cannot learn from informal criteria; only once explicit rules exist does this become agent-led
- Hard boundary correctly enforced: C-7 (named-lawyer sign-off) is Human Only "regardless of agent accuracy" — governance, not capability
- Suitability score is numeric and justified per dimension
- Does NOT default everything to "fully agentic" — C-5 is legitimately 1/7 and Human Only

**Why it's strong:** This is the anti-pattern check in action. The matrix shows judgment and doesn't over-automate just because the domain feels technical.

**Score:** 88/100

---

### 4. **D3 (Volume × Value Analysis) — Honest Economics**
**File:** D3_volume_value_analysis.md  
**What's good:**
- Primary target is WS1 (first-pass classification) with clear justification (300/quarter, highest volume, throughput gate for all downstream work)
- Explicitly flags that WS2 scores 2/25 and is NOT worth automating standalone
- Volumes trace directly to the scenario (300 / 4 = 1,200 year; 70/20/10 split cross-checked)
- Conditional status noted: WS2 depends on playbook format being confirmed; WS3 not yet delegatable as primary target
- No inflated ROI claims; TCO sense-check yields 21-month payback — "just above the 18-month hurdle rate"

**Why it's strong:** Honest assessment. Not trying to sell the ROI on everything, just being clear about what justifies an agent and what doesn't.

**Score:** 85/100

---

### 5. **D4 (Agent Purpose Document) — Clear Autonomy Boundaries**
**File:** D4_agent_purpose_document.md  
**What's good:**
- Purpose statement is tight and specific: "convert inbound vendor contracts into structured clause deviation reports...reducing Tom's WS1 time from ~25 min to ≤8 min"
- Autonomy boundary is explicit: "agent classifies independently but may not commit routing without human confirmation recorded in Ironclad"
- Recognizes the hard governance constraint: protecting Amelia's rule that "no counteroffer leaves Legal's queue without named-lawyer sign-off"
- Primary failure mode is named with consequence: "mis-routes WS3-tier clause as WS2" — undetected until sign-off stage
- Confidence scoring is explicit (0.90 / 0.80 / 0.75 thresholds) with LLM-self-reported scores
- Activity catalog shows all 11 tasks; delegation level specified for each
- DPA currency check (T-8) is correctly flagged as Human-led + Agent Support because playbook is stale

**Why it's strong:** This is a real agent spec, not a feature list. It shows what the agent decides, when it escalates, and what can go wrong.

**Score:** 82/100

---

### 6. **D5 (System/Data Inventory) — Honest Gap Naming**
**File:** D5_system_data_inventory.md  
**What's good:**
- Opens with the most critical integration: Ironclad (write access needed for intake, deviation reports, routing queue)
- Flags the most significant gap immediately: "Outlook API integration path is unconfirmed" — if IT security blocks it, the agent has no intake mechanism
- Lists seven gaps (G-1 through G-7) with mitigation options
- G-1 mitigation is practical: fallback manual forwarding rule for Day 1 if API approval is slow
- G-6 explicitly notes the pre-deployment prerequisite: escalation criteria document must be authored by Amelia before build
- Notes the "compounding opportunity": the Ironclad integration and DOCX parser reusable for WS2 and WS4 agents

**Why it's strong:** This is real integration thinking. Not assuming everything is available; naming the gaps and fallbacks.

**Score:** 84/100

---

### 7. **D6 (Discovery Questions) — Sharpened to Design-Changing Questions**
**File:** D6_discovery_questions.md  
**What's good:**
- Q1 is about playbook format (Word vs. PDF vs. HTML) — not generic, directly affects T-5 architecture
- Q2 is about version control (how does the team know the playbook changed?) — surface the governance gap that exists in reality
- Q3 is about substitute clause language (if yes, WS2 agent scope expands; if no, much more complex) — bifurcates the roadmap
- Q4 is THE critical question: "What are the 3–5 specific signals Tom uses to decide WS2 vs WS3?" — names the bottleneck
- Q5 is sharp: "Can Tom confirm NRR without reading every clause?" — efficiency question that affects workload baseline

**Why it's strong:** These are not procedural questions ("walk me through your process") — they're architecture questions that change the design if answered differently.

**Score:** 86/100

---

## Where Gaps Are ❌

### Gap 1: Hard Governance Gate Not Technically Enforced

**Files affected:** D4, D5  
**The problem:**
- D4 §5 (Autonomy Matrix) correctly states: "agent may not commit a routing decision without human confirmation recorded in Ironclad"
- D5 §1 names the governance channels: Tom's routing confirmation (routing_tier + routing_confirmed_by + routing_confirmed_at)
- **Missing:** How does this actually work in Ironclad? Is this a workflow state machine? A custom approval UI? An API write-lock?

**Why it matters:**
- If Ironclad has no workflow state enforcement, Tom could approve a routing, the agent could commit it, and then Tom could later override it without a recorded "was overridden" event
- If Ironclad doesn't support custom fields, the agent's deviation report has no system of record
- If Ironclad has no audit trail on field changes, there's no proof of what the agent recommended vs. what Tom approved

**What should be fixed:**
Add to D4 §5 or D5 §3 (Gap Analysis):

```markdown
## Gap G-3b: Ironclad Workflow Governance Enforcement

The agent's hard stop ("may not commit routing without human confirmation") is a governance rule,
not just a business rule. It must be technically enforced in Ironclad's workflow, not just 
implemented as an agent pause point.

**Required before build:**
1. Confirm Ironclad supports custom fields (agent_deviation_report JSON)
2. Confirm Ironclad workflow state machine allows a "Pending Human Review" → "Routing Confirmed" transition
   that requires a named user action (Tom explicitly confirms)
3. Confirm audit trail captures: who, when, what they changed, and optionally why (Tom's override reason)

**If Ironclad cannot enforce this technically:** The entire architecture changes — either a separate 
governance database is introduced, or the agent's output goes into a system Ironclad integrates with, 
or the hard stop is enforced only by Tom's discipline (risky).

**Discovery question to add to D6:**
Q-NEW: "In Ironclad, when a case needs Tom's routing confirmation before proceeding to WS2 or WS3, 
what does that workflow look like? Is it a system-enforced state transition, a manual queue assignment 
that Tom must acknowledge, or something else?"
```

**Score impact:** Deducts 8 points from D4 and D5. Should be flagged for FDE review before submission.

---

### Gap 2: Confidence Scoring Calibration Is Untested

**File affected:** D4 §4b  
**The problem:**
- D4 defines confidence scores (0.0–1.0) as "LLM-self-reported"
- Thresholds are set at 0.90 (accept match), 0.80 (accept routing), 0.75 (escalate)
- **No calibration data or testing mentioned.** The LLM's self-reported confidence may not match its actual accuracy.

**Why it matters:**
- If the LLM is miscalibrated overconfident, many incorrect classifications will pass the 0.80 routing threshold
- If it's underconfident, too many cases escalate unnecessarily, defeating time savings
- The weekly 10% audit (D4 KPI Accuracy) is the detection mechanism, but there's no feedback loop to retune thresholds if the audit discovers miscalibration

**What should be fixed:**
Add to D4 §7 (Failure Modes) or create new section:

```markdown
## Failure Mode: Confidence Score Miscalibration

**Description:** The LLM produces high confidence scores (≥0.80) on classifications that are 
actually incorrect; these pass the routing threshold and reach Tom pre-classified as correct, 
reducing his attention to areas that need it most.

**Detection:** Weekly 10% audit identifies systematic pattern of Tom overriding high-confidence 
agent classifications (e.g., agent scored 0.92, Tom disagrees).

**Recovery:** If >15% of Tom's overrides are on clauses where agent confidence was ≥0.85, 
retune prompt instructions to reduce overconfidence. Example adjustment: "Report confidence 
≤0.80 unless the clause text exactly matches the playbook language with no alternative interpretation."

**Pre-deployment:** A calibration run on 20–50 historical contracts with known-good Tom classifications 
is required to detect systematic miscalibration before production deployment. This is a pre-deployment 
prerequisite, not a post-deployment correction.
```

**Score impact:** Deducts 5 points from D4 (KPIs section). The weekly audit is mentioned, but no pre-deployment calibration is specified.

---

### Gap 3: The Playbook Format Is Assumed But Not Validated

**File affected:** D4, D5  
**The problem:**
- D5 Gap G-2 names it: "Playbook format and API path unconfirmed"
- D6 Q1 asks: "Is Position Statements v3.4 stored as Word, HTML, or PDF?"
- **But D4 and D5 proceed as if the answer is Word/HTML-with-text-extraction** without any contingency for "what if it's a scanned PDF?"

**Why it matters:**
- If the playbook is a scanned PDF or has tables/images, T-5 (retrieve playbook from SharePoint) is blocked
- The agent cannot extract clause positions from images; OCR preprocessing is required
- This would delay the build by 2–4 weeks to convert the playbook or implement OCR

**What should be fixed:**
Add a pre-deployment checklist to D5:

```markdown
## Pre-Deployment Prerequisite Checklist

Before build begins, confirm all of the following:

- [ ] **Playbook format:** Position Statements v3.4 is stored as .docx or .html; no sections are scanned PDFs or images
      - If any section is image-based: OCR preprocessing must be implemented before T-5 can run
- [ ] **Playbook version control:** SharePoint document properties include a "Last Updated" timestamp; 
      revision history is visible to the agent via API
- [ ] **Ironclad API:** Ironclad confirms REST API write access for custom fields (agent_deviation_report) 
      and workflow state transitions
- [ ] **Outlook integration:** IT security approves Microsoft Graph API connection to Legal & Commercial mailbox 
      with Mail.Read permission (or fallback manual forwarding rule is in place)
- [ ] **Escalation criteria document:** Amelia has authored and version-controlled a document listing 
      the per-clause-type thresholds that separate WS2-tier deviations from WS3-tier escalations
- [ ] **Playbook DPA section:** Updated to reflect post-DPDI Act requirements; agent can compare DPA clauses 
      against current-version playbook
- [ ] **SharePoint API:** Confirmed queryable; document metadata and text extraction both work
```

**Score impact:** Deducts 3 points from D5 (Gap Analysis section). Should add a pre-deployment checklist to make this explicit.

---

### Gap 4: Discovery Questions Don't Probe Labor/Role Impact

**File affected:** D6  
**The problem:**
- D6 has six good questions (Q1–Q6, partially shown)
- **Missing:** Any question about what happens to Tom if the agent reduces WS1 from 25 min to 8 min per case
- Tom is processing ~23 cases/week at 25 min = ~145 hours/quarter on WS1 alone
- If the agent cuts that to 8 min/case = ~47 hours/quarter — a drop of ~100 hours/quarter or 25 hours/week
- **No question asks Amelia:** "What does Tom do with those 25 hours per week?"

**Why it matters:**
- If Tom's hours drop but Helix doesn't have other work for him, he sits idle or is made redundant — either of which is a morale/retention risk
- If Amelia is not thinking about Tom's role redesign, she may resist the agent despite supporting the goal
- Conversely, if Tom becomes "escalation specialist" or "playbook maintainer," that unlocks higher-value work for him

**What should be fixed:**
Add to D6 §2 (Questions Whose Answers Would Change the Design):

```markdown
---

### Category C: Organizational Design — Role Transition and Resourcing

---

> **Q7: If the agent reduces Tom's WS1 workload from ~145 hours/quarter to ~47 hours/quarter, 
> what do you envision Tom doing with the freed time — and is that work valued in the team's roadmap?**
> **Category:** C — Organizational design
> **What I already infer from the scenario:** Tom is the paralegal doing routine classification; 
> if that work is 70% agent-handled, his time drops significantly. I do not know whether Amelia 
> has a plan for Tom's role or whether she sees this as a potential headcount reduction.
> **If the answer is [Tom becomes escalation specialist, reviewing WS3 cases before lawyer involvement; 
> this is high-value and on the team roadmap]:** The agent design is not just about automation — it's 
> about role redesign. Build confidence increases; Amelia is not giving up headcount.
> **If the answer is [Tom's hours drop but we don't have other work yet; he may be redeployed or 
> reduced]:** The agent may face organizational resistance. Tom may not help refine it if he feels threatened. 
> This is a deployment risk that should be surfaced and managed explicitly.
> **Why this matters more than a generic question:** Role redesign is harder than task automation. 
> Understanding Amelia's intent changes whether the agent is a time-saver (good) or a job-eliminator (risky).
```

**Score impact:** Deducts 4 points from D6 (only 6 of 7 design-changing questions present).

---

### Gap 5: Failure Modes Don't Include Audit Trail Incompleteness

**File affected:** D4 §7  
**The problem:**
- D4 lists seven failure modes (agent surfaces unavailable data, escalates unnecessarily, mis-routes, etc.)
- **Missing:** What if the agent's deviation report is incomplete or lacks evidence for a decision Tom is supposed to approve?

**Example:** Agent classifies DPA clause as "acceptable per playbook v3.4" with confidence 0.87. Tom approves the routing. Three months later, Helix sends a counteroffer without realizing the DPA clause is inadequate for DPDI Act compliance. Customer challenges it. Legal team asks "who reviewed the DPA?" and the agent's output has no evidence of the comparison logic.

**Why it matters:**
- Legal work is audit-sensitive. In-house counsel is professionally responsible for contract review.
- If the agent decides a clause is acceptable but doesn't explain *why*, the lawyer cannot defend the decision if challenged.
- If the agent doesn't record Tom's approval explicitly (with timestamp and optional override reason), there's no proof Tom ever reviewed it.

**What should be fixed:**
Add to D4 §7 (Failure Modes):

```markdown
| **Agent decision lacks audit evidence** | Tom receives a deviation report but cannot see the agent's reasoning chain (which playbook section was matched? what was the confidence? what flag was attached?) | High: compliance risk; cannot defend decision if challenged by customer or internal review | Agent output format must include: (1) clause excerpt, (2) matched playbook section, (3) comparison logic (what did agent look for?), (4) confidence score, (5) any regulatory flags. Tom's approval must record: who, when, and optional reason if overriding agent classification. |
```

**Score impact:** Deducts 3 points from D4 (Failure Modes section is incomplete).

---

### Gap 6: No Explicit DPA Currency Workaround Until Playbook Is Updated

**File affected:** D4, D5  
**The problem:**
- Artefact 2.3 explicitly shows Amelia's sticky note: "DPDI Act updates landed Q1 — need to add new sections... talked about this with Sarah in March, never got round to it"
- D4 Task T-8 is "Apply DPA currency check — attach 'unverified against current regulation' flag to all DPA classifications"
- **But there's no fallback for when the playbook DPA section is NOT updated by deployment day**

**Why it matters:**
- The playbook DPA section may still be stale on Day 1 of production
- If so, the agent cannot classify DPA clauses with confidence
- D4 KPI target says "≥95% accurate" but excludes DPA until the playbook is updated — this is honest but incomplete

**What should be fixed:**
Add to D4 §8 (Out-of-Scope / Hard Stops) or new subsection:

```markdown
## DPA Clause Handling Until Playbook Is Updated

**Current status:** The playbook DPA section has not been updated since the DPDI Act Q1 revisions 
(~2 months past due). The agent cannot classify DPA clauses confidently against an outdated standard.

**Deployment rule:** Until the playbook DPA section is confirmed current and updated in SharePoint:
- Agent flags ALL DPA clauses with "DPA-Unverified" status
- No confidence score is provided; all DPA clauses escalate to Tom for manual review
- Tom (or Sarah) adjudicates based on current legal knowledge, not the stale playbook
- Once the playbook is updated and the update is confirmed in SharePoint, agent resumes normal classification

**This is a pre-deployment gate:** The agent cannot go to production on WS1 if DPA clauses 
are not handled deterministically. Either the playbook is updated before build, or the agent 
deployment is delayed, or WS1 starts with DPA exclusion.

**Discovery question (already in D6 as Q2):** When and how will the playbook DPA update be completed?
```

**Score impact:** Deducts 2 points from D4 (Scope is clear but the DPA workaround is not explicit).

---

## Summary Table

| Deliverable | Score | Status | Key Issue |
|---|---|---|---|
| **CLAUDE.md** | 92/100 | ✅ Strong | Process discipline excellent; minor: no Week 2-specific CLAUDE.md examples |
| **D1: Cognitive Load Map** | 90/100 | ✅ Strong | Lived work is genuinely grounded; shows real breakpoints and informal judgment |
| **D2: Delegation Matrix** | 88/100 | ✅ Strong | Anti-pattern check in action; correctly avoids over-automation |
| **D3: Volume × Value** | 85/100 | ✅ Good | Honest economics; conditional status clear |
| **D4: Agent Purpose Document** | 75/100 | ⚠️ Good but incomplete | Missing: governance enforcement details, confidence calibration strategy, audit trail design, DPA workaround, role redesign consideration |
| **D5: System/Data Inventory** | 81/100 | ⚠️ Good but incomplete | Gaps named; missing: pre-deployment checklist, contingency if Ironclad doesn't support custom fields |
| **D6: Discovery Questions** | 82/100 | ⚠️ Good but incomplete | Questions are sharp; missing: organizational impact question (what happens to Tom?) |
| **Overall** | **78/100** | ⚠️ Pass with caveats | Strong assessment methodology; gaps are fixable before submission |

---

## Fixes Required (Priority Order)

### 🔴 **High Priority — Fix Before Submission**

1. **Add governance enforcement section to D5:** How does Ironclad technically enforce Tom's approval? What if custom fields aren't supported? (Add 10 min)
2. **Add pre-deployment checklist to D5:** Explicit checklist of what must be confirmed before build (Add 5 min)
3. **Add Q7 to D6:** Discovery question on Tom's role redesign (Add 3 min)
4. **Add failure mode to D4:** Audit trail incompleteness (Add 5 min)
5. **Add DPA workaround to D4:** Explicit handling rule until playbook is updated (Add 5 min)

**Total effort:** ~30 min

---

### 🟡 **Medium Priority — Should Be Added**

6. **Add confidence calibration note to D4:** Pre-deployment calibration run mentioned (Add 5 min)
7. **Add contingency to D5 for Outlook:** Fallback manual forwarding rule explicitly mentioned (already done, but could be more prominent)

**Total effort:** ~5 min

---

### 🟢 **Low Priority — Nice to Have**

8. **Add Week 2-specific CLAUDE.md examples:** If there's time, show how the assessment thinking should be documented (Add 10 min, optional)

---

## Pass / Fail Recommendation

| Criterion | Status | Reasoning |
|---|---|---|
| **Would pass Gate 2 as-is?** | ✅ Yes, probably 75–80% | Structure is sound; anti-patterns avoided; gaps are fixable |
| **Would be ready for real deployment as-is?** | ❌ No, 55% ready | Governance enforcement unspecified; system integrations unvalidated; DPA contingency missing |
| **Should submit as-is?** | ⚠️ Recommend fixes | Add the 5 high-priority items (30 min) → ready for submission at 85–88% |
| **Effort to close gaps?** | ~40 min total | Most gaps are documentation/specification, not methodology |

---

## Bottom Line

**This is strong Week 2 work.** The lived-work decomposition is genuine. The delegation archetypes are justified. The discovery questions are sharp. The system gaps are honestly named.

**The gaps are fixable and mostly about being explicit about contingencies and governance.** None of them suggest the underlying assessment is wrong.

**Recommend:** Add the 5 high-priority fixes (~30 min), re-review, and submit. At that point, this would be an **85%+ submission** ready for peer review.

---
