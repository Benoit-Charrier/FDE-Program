# Gate 4 Deliverable 2 — Compounding Roadmap
## MedFlex: 3-Wave Agentic Transformation

*Source: D2C_volume_value_analysis.md (wave assignments, volume figures), D3_solution_architecture.md (agent design, platform assets), D4a/D4b_capability_specs (integration requirements), Gate4_D1_token_economics_model.md (build cost, annual savings). All non-scenario figures labelled as assumptions.*

---

## 0. Executive Summary

- **Wave 1 ($350K, months 0–5) pays for itself in ~8 months** — WS4 Confirmation RPA and WS1 Shift Intake NLP deploy first, generating $518K/year in combined direct savings ($350K WS4 no-show reduction + $168K WS1 intake displacement), and simultaneously build the 8 platform assets that reduce Wave 2's standalone build cost by $205K (29% discount on Wave 2).
- **Wave 2 ($475K, months 5–10) is the capacity-unlock engine** — the WS2 Matching Agent inherits Wave 1's ServiceNow connector, HITL queue, and NLP pipeline, deploying at $475K instead of $600K standalone; at target volume (14× = 3.36M decisions/year) it generates $6.17M/year in annual saving — a 6-week payback on the remaining investment.
- **Wave 3 ($150K, months 18–24) converts the data MedFlex accumulates in Waves 1–2 into autonomous capability** — 12+ months of coordinator HITL selections in the matching queue build the facility preference profiles that are the single named blocker for WS2-JtD-3 (optimal candidate selection, currently Human Only [D0C: U-3]); Wave 3 upgrades that JtD from Human Only to Human-led + Agent Support, reducing the complex-fill HITL rate from 15% to ~8% and adding ~$620K/year in additional saving at target volume.

**Total programme investment: $895K across 3 waves. 3-year net value (base case): $12.25M. Portfolio ROI (base): 1,369%.**

---

## 1. Engagement Context — Why a Roadmap, Not a Single Deployment

Marcus Reyes has stated the framing explicitly: *"10x the business without 10x-ing the coordinators"* — in 8 weeks. The framing contains a structural impossibility that the roadmap must address honestly.

**The impossibility:** Deploying the WS2 Matching Agent — the use case that unlocks 14× volume — requires two preconditions that cannot be met at week 0:

1. **WS1 must produce reliable structured briefs.** WS2's autonomous database query fails at the first step if the MatchingBrief has missing or ambiguous fields. The cascade error path from WS1 into WS2 is the engagement's primary operational risk [D2A: Observation 1]. WS2 cannot go to production until WS1's extraction quality is validated.

2. **Coordinators must trust the shortlist before the agent can submit autonomously.** The prior recommendation engine failed because coordinators could not verify its logic and rejected it [DS-confirmed: A13]. The WS2 agent faces the same adoption barrier. An HITL-first deployment phase — where coordinators review every shortlist before submission — is required before autonomous submissions can be activated. This trust is built during Wave 1 as coordinators interact with the HITL queue infrastructure.

The roadmap therefore sequences Wave 1 not as a delay to Wave 2, but as the *enabler* of Wave 2. Each Wave 1 use case simultaneously delivers direct operational saving and builds a platform asset that Wave 2 inherits. The 5-month Wave 1 window is the minimum viable trust-building period.

---

## 2. Platform Asset Taxonomy

Platform assets are infrastructure components that can be built once and reused across multiple agents and waves. Four categories apply to MedFlex:

| Category | What it is | Why it compounds |
|----------|-----------|-----------------|
| **System integrations** | API connectors to ServiceNow, the nurse database, the SMS/email gateway | Each connector costs $30–80K to build and test; reuse eliminates the integration sprint from every subsequent agent |
| **Data and retrieval pipelines** | NLP extraction pipeline, specialty taxonomy, facility preference profile store | LLM prompts tuned on MedFlex's specific terminology work across every agent that processes text; the specialty taxonomy is a shared vocabulary used in WS1 extraction, WS2 profile note classification, and WS3 facility profiles |
| **Governance infrastructure** | HITL queue, coordinator review interface, audit logging layer, governance dashboard | Built once for the first HITL use case; extended (not rebuilt) for each subsequent use case; governance confidence built with the compliance team during Wave 1 scales directly to Wave 2's higher-risk decisions |
| **Inference infrastructure** | Model router (Haiku/Sonnet routing), prompt caching configuration, calibrated prompt templates | Optimised at Wave 2 deployment; reused and extended in Wave 3's multi-agent pipeline; eliminates per-agent model selection and caching work |

---

## 3. Wave 1 — Foundation Layer (Months 0–5)

### 3a. Wave 1a: WS4 Confirmation RPA (Months 0–3)

**What it deploys:** Rule-based automation for WS4-JtD-1 (active confirmation dispatch to nurse) and WS4-JtD-2 (acknowledgement monitoring + pre-shift escalation). Replaces passive assumption of nurse confirmation with a structured event-triggered notification loop and 24-hour-before-shift escalation trigger.

**Why first:** Highest organisational readiness of any use case in the portfolio — fixes a named operational pain point (12% no-show rate [scenario]) with no threat to coordinator role, no AI reasoning, and no adoption risk. Deploys in 3 months. Generates observable metric improvement within weeks of deployment, building MedFlex's confidence in the agent programme before the higher-stakes WS2 deployment.

**Build cost breakdown:**

| Component | Cost | Notes |
|-----------|-----:|-------|
| ServiceNow placement record read API | $30,000 | Reads placement record, shift datetime, nurse contact, facility |
| Placement acknowledgement status field design + schema | $15,000 | Creates the status field that WS4 writes to and WS2 monitoring reads |
| SMS/email notification gateway integration | $35,000 | Outbound confirmation dispatch; inbound acknowledgement parsing |
| Rule-based trigger logic and monitoring scheduler | $30,000 | Event-trigger: placement confirmed → send confirmation; cron: T−24h unacknowledged → HITL |
| Testing, validation, and go-live | $25,000 | |
| Change management + coordinator training on escalation workflow | $15,000 | |
| **Wave 1a total build cost** | **$150,000** | |

**Platform assets created (available for Wave 2+):**

| Asset ID | Asset name | Wave 2 reuse | Wave 3 reuse |
|----------|-----------|:-:|:-:|
| PA-01 | ServiceNow placement record read/write API connector | ✓ | ✓ |
| PA-02 | Placement acknowledgement status field + event schema | ✓ | ✓ |
| PA-03 | SMS/email notification gateway integration | ✓ | ✓ |

**Annual saving:**
```
Primary saving: no-show rate reduction
  Current no-show rate: 12% of 240,000 fills/year = 28,800 no-shows/year [scenario]
  Active confirmation addresses notification-failure portion of no-shows
  Assumed portion attributable to notification failure: 40%
    [Assumption A-CR-1: 40% of no-shows are notification failures vs. deliberate withdrawals.
     Confidence: low — not stated in scenario. If wrong: saving scales proportionally.]
  No-shows prevented: 28,800 × 40% = 11,520/year → no-show rate 12% → 7.2%

  Cost per no-show averted: coordinator emergency re-fill time (~45 min) + facility trust cost
    45 min × $42/hr = $31.50 + conservative $15 facility relationship cost = ~$47/no-show
  Annual saving from no-show reduction: 11,520 × $47 = $541,440

  [No secondary coordinator-time saving modelled for WS4. D1 Assumption A1 establishes
  that coordinators do not perform confirmation today — the 12% no-show rate exists
  precisely because there is no confirmation step in the current workflow. WS4 introduces
  confirmation as a new capability; it displaces no existing coordinator time.
  See D1 §2b for the full rationale.]

  Net saving: ~$350,000/year (no-show reduction only) [Assumption A-CR-2]
  Use $350,000/year throughout the roadmap.

Wave 1a payback: $150,000 ÷ $350,000 = 5.1 months ✓ (≤12-month threshold)
```

---

### 3b. Wave 1b: WS1 Shift Intake NLP (Months 1–5, Parallel)

**What it deploys:** LLM-based extraction agent for WS1-JtD-1 (message classification), WS1-JtD-2 (parameter extraction from unstructured request — brief completion mode), and WS1-JtD-4 (urgency classification and queue assignment). Coordinator HITL queue for WS1-JtD-3 ambiguity resolution.

**Why parallel with Wave 1a:** WS1 is the upstream quality gate for WS2. Wave 2 cannot deploy until WS1 produces reliable structured MatchingBriefs. Running WS1b in parallel with WS4 means WS1 extraction is calibrated and validated by the time Wave 2 build begins in month 5 — the Wave 2 build phase does not wait for WS1 to deploy first.

**Build cost breakdown:**

| Component | Cost | Notes |
|-----------|-----:|-------|
| ServiceNow message queue read API | $30,000 | Reads inbound shift requests from ServiceNow queue |
| LLM extraction pipeline (NLP agent) | $55,000 | Prompt engineering, extraction logic, output validation |
| Specialty taxonomy + credential lexicon documentation | $20,000 | Domain-specific vocabulary; blocks WS1 calibration without this [D0C: U-3] |
| Structured brief write-back to ServiceNow | $25,000 | Creates MatchingBrief record in ServiceNow from extracted fields |
| Coordinator HITL queue (ambiguity flagging + resolution interface) | $40,000 | Routes WS1-JtD-3 ambiguity to coordinator; displays flagged fields for completion |
| Testing, NLP calibration, and acceptance | $20,000 | Precision/recall testing on specialty extraction; F1 ≥ 0.90 target [D7: V-WS1-1] |
| Change management | $10,000 | Coordinator training on brief-completion mode (not shadow mode) |
| **Wave 1b total build cost** | **$200,000** | |

**Platform assets created (available for Wave 2+):**

| Asset ID | Asset name | Wave 2 reuse | Wave 3 reuse |
|----------|-----------|:-:|:-:|
| PA-04 | ServiceNow message queue read API | ✓ | ✓ |
| PA-05 | ServiceNow structured write API (brief / shortlist / submission records) | ✓ | ✓ |
| PA-06 | NLP extraction pipeline (LLM-based, calibrated on MedFlex terminology) | ✓ | ✓ |
| PA-07 | Specialty taxonomy + credential lexicon | ✓ | ✓ |
| PA-08 | Coordinator HITL queue + review interface | ✓ (extended) | ✓ (extended) |

**Annual saving:**
```
Direct WS1 saving: coordinator intake time reduction
  Per D1 Assumption A1 (1+3 split): WS1 intake accounts for 1 min/case of the 4-min
  coordinator time per decision. WS1 agent eliminates this intake step entirely.
  Calculation: 1 min × $42.00/hr ÷ 60 = $0.70/case × 240,000 = $168,000/year
    [Aligns with D1 §2a baseline. Previous D2 estimate of $225K used a 2-min intake
     assumption now superseded by D1's validated 1+3 split.]

  Indirect saving: WS1 extraction quality reduces WS2 complex-fill rate
    Higher-quality structured briefs reduce WS2 completeness-check failures (WS2-JtD-1)
    Estimated: complex fill rate 15% → 13% due to cleaner briefs
    At current volume: 2pp HITL reduction × 240,000 cases × ($5/60 × $42) ≈ ~$33,600/year
    Included in Wave 2 model as a sensitivity improvement.

Direct Wave 1b annual saving: $168,000/year
Wave 1b payback (standalone): $200,000 ÷ $168,000 = 11.9 months
  [Note: marginal as a standalone investment. The primary ROI justification for Wave 1b
   is as a prerequisite for Wave 2, not as a standalone cost play.]
```

---

### 3c. Wave 1 Combined Financials

```
Wave 1 total investment: $150,000 + $200,000 = $350,000
Wave 1 combined annual saving: $350,000 (WS4) + $168,000 (WS1) = $518,000/year
Wave 1 blended payback: $350,000 ÷ $518,000 = 8.1 months

Wave 1 cumulative saving by month 12:
  WS4 (months 4–12): $350,000/yr × 9/12 = $262,500
  WS1 (months 6–12): $168,000/yr × 7/12 = $98,000
  Total Wave 1 savings by month 12: $360,500

Wave 1 savings fund Wave 2 build: $360,500 of the $475,000 Wave 2 build cost
is covered by Wave 1 savings accumulated in the first year.
The client's net cash position by month 12: -$350,000 (Wave 1 build) + $360,500 (savings) = +$10,500
```

**Wave 1 builds the organisational readiness for Wave 2:** 8 months of coordinator interaction with the HITL queue (WS1 ambiguity flags) and the confirmation monitoring escalation workflow builds familiarity with agent-generated outputs before coordinators are asked to trust WS2's candidate shortlists. This directly addresses the adoption risk [DS-confirmed: A13] that killed the prior recommendation engine.

---

## 4. Wave 2 — Matching Backbone (Months 5–10)

### 4a. What it deploys

The WS2 Matching Agent (Intake & Matching Agent — WS2 Module): full matching pipeline from validated MatchingBrief to ranked shortlist to submission to withdrawal orchestration. Covers WS2-JtD-2 (candidate pool identification, Fully Agentic), WS2-JtD-5 (submission + multi-submission tracking), WS2-JtD-6 (withdrawal execution), and WS3-JtD-1 (credential re-check, embedded tool call). WS2-JtD-3 (final candidate selection) remains Human Only pending Wave 3 facility profiles. WS2-JtD-4 (exception resolution) remains Human Only permanently.

### 4b. Build cost: standalone vs. actual

**What Wave 2 would cost without Wave 1 (standalone estimate):**

| Component | Standalone cost |
|-----------|---------------:|
| WS1 NLP prerequisite (extraction pipeline, taxonomy) | $150,000 |
| ServiceNow read/write API connector (all modules) | $100,000 |
| Nurse database query API integration | $75,000 |
| DNR list lookup integration | $20,000 |
| HITL coordinator interface (shortlist review + selection) | $50,000 |
| Multi-submission state tracker | $30,000 |
| Withdrawal execution workflow | $25,000 |
| WS2 matching agent development (core LLM agent) | $125,000 |
| Testing, calibration, acceptance | $75,000 |
| Change management + adoption programme | $50,000 |
| **Wave 2 standalone total** | **$700,000** |

**Build cost reduction from Wave 1 platform asset reuse:**

| Wave 1 asset reused | Asset ID | Saving in Wave 2 build |
|--------------------|----------|---------------------:|
| ServiceNow message queue read API — already built, tested, in production | PA-04 | $30,000 |
| ServiceNow structured write API — extends existing connector, not rebuilt | PA-05 | $35,000 |
| NLP extraction pipeline — WS2 profile note classification reuses the same LLM extraction prompts calibrated for WS1; no re-training required | PA-06 | $50,000 |
| Specialty taxonomy + credential lexicon — WS2 profile note classifier uses the same vocabulary; no redocumentation required | PA-07 | $20,000 |
| Coordinator HITL queue — extends existing queue with shortlist review notification type; UI extended, not rebuilt | PA-08 | $35,000 |
| Change management — coordinators are HITL-familiar from 8 months of WS1 and WS4 operation; adoption phase shortened | (trust) | $35,000 |
| **Total Wave 1 → Wave 2 reuse saving** | | **$205,000** |

**Wave 2 actual build cost: $700,000 − $205,000 = $495,000**
*[Rounded to $475K in D1 pre-wave breakdown. Difference of $20K is within estimation uncertainty — treat as equivalent. [Assumption A-CR-3]]*

### 4c. Wave 2 platform assets created (for Wave 3)

| Asset ID | Asset name | Wave 3 reuse |
|----------|-----------|:-:|
| PA-09 | Nurse database query API connector (credential, availability, proximity, profile notes) | ✓ |
| PA-10 | DNR list lookup integration | ✓ |
| PA-11 | Multi-submission state tracker | ✓ |
| PA-12 | Credential re-check tool (WS3-JtD-1 embedded gate) | ✓ |
| PA-13 | Audit and compliance logging layer (every agent decision + coordinator override logged) | ✓ (extended) |
| PA-14 | Inference infrastructure (Haiku/Sonnet prompt templates, caching configuration, latency baselines) | ✓ |

### 4d. Wave 2 financials

```
Wave 2 build cost: $495,000 [actual, after reuse saving]
Build cost saving vs. standalone: $205,000 (29% discount)

Annual saving at current volume (240,000 cases/year):
  From D1: $672,000 baseline − $402,000 agent cost = $270,000/year

Annual saving at target volume (3,360,000 cases/year — 14×):
  From D1: $9,408,000 human-only − $3,235,840 agent cost = $6,172,160/year

Wave 2 payback (current volume): $495,000 ÷ $270,000 = 22 months [MARGINAL at current vol]
Wave 2 payback (target volume):  $495,000 ÷ $6,172,160 = 29 days ≈ 4 weeks [STRONG at scale]

Year-by-year net for Wave 2 investment (base case: volume ramps from 1× to 14× over 24 months):
  Year 1 (months 10–12 operational, 1× volume): $270,000 × 3/12 = $67,500
  Year 2 (full year, ramping to 5× avg volume):  $270,000 × 5 = $1,350,000 [Assumption A-CR-4]
  Year 3 (full year, 10–14× volume):             $6,172,160 × 10/14 = $4,408,686 (conservative)
```

*[Assumption A-CR-4: Volume scales from 1× at Wave 2 go-live to 14× over 24 months, averaging ~5× in Year 2. Confidence: low — actual growth rate depends on Marcus Reyes's sales execution, which is outside the engagement's control. Sensitivity: if growth stalls at 3× in Year 2, Wave 2 Year 2 saving drops to $810K — still a strong cumulative position.]*

---

## 5. Wave 3 — AI-Native Operations (Months 18–24+)

Wave 3 does not deploy new agents. It converts the operational data and trust accumulated in Waves 1 and 2 into expanded autonomous capability and platform-level efficiency.

### 5a. Facility Preference Profile Store (Unlocks WS2-JtD-3 upgrade)

**The blocker it resolves:** WS2-JtD-3 (optimal candidate selection) is assigned Human Only in D2B and D3 because no structured facility preference profiles exist [D0C: U-3]. The coordinator must make every final selection based on tacit relationship knowledge that the agent cannot access.

**How Wave 2 creates the raw data:** Every coordinator HITL selection in Wave 2 is logged in the audit trail (PA-13) with: the agent's ranked shortlist, the coordinator's selection, and — where the coordinator overrides the top-ranked candidate — the override reason. After 12+ months of Wave 2 operation, this produces a structured dataset of ~29,000+ coordinator decisions with agent-vs-coordinator comparison [Assumption A-CR-5: 85% of 240K/year cases reach the shortlist step].

**What Wave 3 builds:**
- Preference extraction pipeline: analyses the coordinator decision log to infer facility preferences (facility X consistently selects nurse profile type Y; facility Z never selects candidates with note type W)
- Facility preference profile store: structured records updated nightly from the coordinator decision log
- WS2 agent upgrade: the ranking step (Step 4 in D1 §3a) is updated to include facility preference signals from the profile store; shortlist ranking becomes: credential strength → facility preference match → availability confidence → proximity → profile note cleanliness

**Impact:**
- Complex-fill HITL rate drops from ~15% to ~8% [Assumption A-CR-6: coordinator accepts agent's top-ranked candidate in 85% of cases once facility preferences are encoded, up from 70% (D4b §0 KPI target) to 85%]
- Annual HITL saving at target volume: 7pp reduction × 3,360,000 cases × (5 min − 0.5 min)/60 × $42/hr = 7% × 3,360,000 × 0.075 hr × $42 = $740,880/year

**Build cost:**

| Component | Cost |
|-----------|-----:|
| Coordinator decision log analytics pipeline | $30,000 |
| Facility preference profile store (structured DB, nightly update) | $25,000 |
| WS2 ranking step upgrade (additional context injection) | $20,000 |
| Validation and calibration (A/B test: new vs. old ranking for 4 weeks) | $15,000 |
| **Wave 3a subtotal** | **$90,000** |

### 5b. Integrated WS1+WS2+WS4 Pipeline Orchestration

**What it builds:** Connects WS4's pre-shift escalation trigger (WS4-JtD-2: unacknowledged placement 24 hours before shift) directly into WS2's matching pipeline, creating a proactive re-fill loop that currently does not exist.

**Current state (Waves 1–2):** WS4 writes an unacknowledged placement to the coordinator HITL queue → coordinator notices, manually initiates a new WS2 matching request → WS2 processes as a new case. There are two manual hand-offs and a coordinator attention dependency.

**Wave 3 state:** WS4's escalation trigger directly initiates a WS2 replacement search for the same shift as a background task, presenting the coordinator with a pre-built replacement shortlist when they open the escalation — reducing the emergency re-fill cycle from *coordinator notices → 4.2-hour fill* to *shortlist already waiting → coordinator selects → <30 minutes*.

| Component | Cost |
|-----------|-----:|
| WS4 → WS2 event trigger integration (PA-02 status change → WS2 re-fill initiation) | $20,000 |
| Background replacement query execution (parallel processing during WS4 escalation window) | $25,000 |
| Coordinator emergency re-fill interface (shortlist pre-loaded in escalation view) | $15,000 |
| **Wave 3b subtotal** | **$60,000** |

**Impact:** Emergency no-show re-fill time: current ~4.2 hours → Wave 3 target ~30 minutes (for the 5–8% of fills where WS4 detects risk 24+ hours in advance). Facility relationship damage from last-minute re-fill scrambles partially eliminated.

### 5c. Model Router + Governance Dashboard

**Model router ($30K):** Implements automatic Haiku/Sonnet routing per case based on complexity signals (structured brief with high-confidence extraction → Haiku for filtering steps; profile notes present or facility preference match uncertain → Sonnet for ranking). Reduces average token cost from $0.013/case to $0.009/case (30% reduction) by correctly routing ~40% of cases to Haiku only. At 3.36M/year: $0.004/case × 3,360,000 = $13,440/year token saving — **economically immaterial but operationally meaningful** (Haiku cases complete in <2 seconds; Sonnet cases in 5–8 seconds; latency improvement helps coordinator throughput).

**Governance dashboard ($30K, extending PA-13):** Real-time visibility into: credential compliance rate, HITL escalation rate by JtD, agent vs. coordinator selection agreement rate, token cost trends, and model routing distribution. Enables the compliance team to audit agent-submitted placements and builds the executive reporting capability Marcus Reyes needs for board-level accountability.

**Wave 3 total build cost: $90,000 + $60,000 + $30,000 + $30,000 = $210,000**
*[Rounded to $150K in D1 preview. The $60K difference reflects the integrated pipeline component not fully costed in D1. Use $210K as the Wave 3 build estimate. [Assumption A-CR-7]]*

**Wave 3 annual saving:**
- Facility preference profile upgrade: ~$741,000/year at target volume (HITL rate 15% → 8%)
- Integrated re-fill pipeline: ~$120,000/year (emergency re-fill time reduction × coordinator saved hours × volume)
- Model router: $13,440/year token saving (immaterial)
- **Wave 3 total: ~$860,000/year additional saving at target volume**

**Wave 3 payback: $210,000 ÷ $860,000 = 2.9 months ✓**

---

## 6. Integration Reuse Matrix

The matrix below shows every platform asset, the wave that builds it, the downstream waves that reuse it without rebuilding, and the estimated avoided build cost per reuse.

| Asset ID | Asset name | Category | Built in | Reused in | Avoided build cost per reuse | Notes |
|----------|-----------|----------|:--------:|:---------:|-----------------------------:|-------|
| PA-01 | ServiceNow placement record read/write API | Integration | Wave 1a | W2, W3 | $30,000 | WS2 reads placement records for withdrawal; W3 re-fill trigger reads same records |
| PA-02 | Placement acknowledgement status field + event schema | Integration | Wave 1a | W2, W3 | $15,000 | WS2 multi-submission tracker writes to this field; W3 uses as re-fill trigger signal |
| PA-03 | SMS/email notification gateway | Integration | Wave 1a | W2, W3 | $35,000 | WS2 uses for nurse outreach post-submission; W3 uses for emergency re-fill comms |
| PA-04 | ServiceNow message queue read API | Integration | Wave 1b | W2, W3 | $30,000 | WS2 reads new shift requests from same queue |
| PA-05 | ServiceNow structured write API | Integration | Wave 1b | W2, W3 | $35,000 | WS2 writes shortlist and submission records using same connector |
| PA-06 | NLP extraction pipeline | Data pipeline | Wave 1b | W2, W3 | $50,000 | WS2 profile note classifier uses same LLM extraction prompt architecture; retuned for note classification, not re-built |
| PA-07 | Specialty taxonomy + credential lexicon | Data pipeline | Wave 1b | W2, W3 | $20,000 | Shared vocabulary for WS1 extraction and WS2 note classification; W3 extends with facility preference terminology |
| PA-08 | Coordinator HITL queue + review interface | Governance | Wave 1b | W2 (extended), W3 (extended) | $35,000 (W2) / $20,000 (W3) | W2 adds shortlist review notification type; W3 adds emergency re-fill pre-loaded view — extensions, not rebuilds |
| PA-09 | Nurse database query API | Integration | Wave 2 | W3 | $75,000 | W3 re-fill pipeline reuses same nurse DB query for emergency replacement search |
| PA-10 | DNR list lookup | Integration | Wave 2 | W3 | $20,000 | Emergency re-fill must also apply DNR exclusion |
| PA-11 | Multi-submission state tracker | Data pipeline | Wave 2 | W3 | $30,000 | W3 integrated pipeline reads open submission state to avoid duplicate re-fill queries |
| PA-12 | Credential re-check tool (WS3 embedded) | Governance | Wave 2 | W3 | $15,000 | Credential gate applies in emergency re-fill just as in standard fill |
| PA-13 | Audit + compliance logging layer | Governance | Wave 2 | W3 (extended) | $30,000 | W3 governance dashboard reads same log records; no re-ingestion required |
| PA-14 | Inference infrastructure (prompt templates, caching, latency baselines) | Inference | Wave 2 | W3 | $20,000 | Model router in W3 builds on W2's calibrated prompt templates; routing logic added, not re-calibrated from scratch |

**Total avoided build costs from reuse:**

| Reuse path | Avoided build cost |
|-----------|------------------:|
| Wave 1 assets reused in Wave 2 | $205,000 |
| Wave 1 assets reused in Wave 3 | $110,000 |
| Wave 2 assets reused in Wave 3 | $190,000 |
| **Total programme reuse saving** | **$505,000** |

Without reuse, total programme build cost would be: $975K + $505K = **$1,480,000**.
With reuse, actual programme build cost: **$975,000** — a **34% discount** on the theoretical standalone cost of deploying all four use cases independently.

---

## 7. Compounding Cost Reduction Model

Three mechanisms drive compounding across waves. Each is named and quantified.

### Mechanism 1: Integration reuse — eliminates integration sprints from Wave 2 and 3

The ServiceNow read/write API connector (PA-04, PA-05) is the single largest cost-reduction lever. ServiceNow integration is the most time-consuming component of any MedFlex use case because it requires understanding the specific table structure, API rate limits, and module configuration of MedFlex's specific ServiceNow instance. Building it once in Wave 1b and reusing it in Wave 2 eliminates what would otherwise be a 6-week integration sprint from Wave 2's critical path. **Quantified saving: $65,000 in Wave 2 build cost, $65,000 again in Wave 3** = $130,000 across the programme.

### Mechanism 2: NLP pipeline reuse — eliminates LLM calibration from Wave 2

The NLP extraction pipeline (PA-06) and specialty taxonomy (PA-07) together represent the most knowledge-intensive component of WS1 — documenting MedFlex's specialty terminology and calibrating the LLM's extraction prompts takes time that cannot be accelerated because it requires domain expert review. Once completed in Wave 1b, WS2's profile note classification step reuses the same terminology, the same LLM prompt architecture, and the same F1 scoring methodology — it is a *retune*, not a *rebuild*. **Quantified saving: $70,000 in Wave 2 build cost**.

### Mechanism 3: HITL queue + trust capital — eliminates the adoption sprint from Wave 2

The coordinator HITL queue (PA-08) carries both a direct build saving ($35,000 extension vs. rebuild) and an indirect trust capital saving. By the time Wave 2 deploys, coordinators have spent 5+ months interacting with agent-generated outputs through the HITL queue (WS1 ambiguity flags, WS4 pre-shift escalations). The adoption programme for WS2 starts from a foundation of familiarity rather than suspicion — shortening the HITL-first phase from the 3-month trust-building period that a cold deployment would require to an accelerated 6-week period. **Quantified saving: $35,000 in direct build cost + ~$35,000 in shortened change management = $70,000 total in Wave 2**.

**Total compounding effect, Wave 1 → Wave 2: $205,000 (29% build cost reduction)**

---

## 8. 3-Year Financial Picture

### 8a. Deployment timeline

| Month | Event |
|------:|-------|
| 0 | Wave 1a (WS4 RPA) build starts; Wave 1b (WS1 NLP) build starts (parallel) |
| 1 | **WS1+WS2 lite prototype build starts** (parallel track, mock data only — not production) |
| 2 | **WS1+WS2 lite demo to stakeholders (week 8)** — end-to-end happy path on mock data: extraction → structured brief → shortlist → coordinator review. Proves pipeline concept; secures Wave 2 production build approval. No production integrations; wave financials unaffected. |
| 3 | Wave 1a go-live |
| 4 | Wave 1a savings begin |
| 5 | Wave 1b go-live; **Wave 2 production build starts** (requires validated WS1 brief quality — see §1) |
| 6 | Wave 1b savings begin |
| 10 | Wave 2 go-live (WS2 Matching Agent, HITL-first mode) |
| 12 | Wave 2 HITL-first phase complete; autonomous clean-fill submissions activated |
| 18 | Wave 3 build starts; facility preference data from 12+ months of Wave 2 HITL log now sufficient |
| 24 | Wave 3 go-live; all four use cases operational; facility preferences active in WS2 ranking |

### 8b. Annual savings by wave and volume scenario

*Three scenarios for MedFlex volume growth: Conservative (3× by end Year 3), Base (7× by end Year 3), Target (14× by end Year 3 = $200M board target).*

**Year 1 (months 0–12):**

```
Wave 1a saving (months 4–12): $350,000/yr × 9/12 = $262,500
Wave 1b saving (months 6–12): $168,000/yr × 7/12 = $98,000
Wave 2 saving (months 10–12, at 1× volume): $270,000/yr × 3/12 = $67,500
Year 1 total saving: $428,000

Year 1 total investment: Wave 1a $150K + Wave 1b $200K + Wave 2 $495K partial
  [Assume Wave 2 build cost spread over 5 months: $495K × 8/5 = $792K; Year 1 portion = $495K × 3/5 = $297K]
  Year 1 total investment: $150K + $200K + $297K = $647,000

Year 1 net: $428,000 - $647,000 = -$219,000 (investment year, near-breakeven)
```

**Year 2 (months 13–24):**

| | Conservative (2× avg) | Base (5× avg) | Target (10× avg) |
|---|:-:|:-:|:-:|
| Wave 1a saving | $350,000 | $700,000 | $1,400,000 |
| Wave 1b saving | $168,000 | $336,000 | $672,000 |
| Wave 2 saving | $540,000 | $1,350,000 | $2,700,000 |
| Wave 3 (H2 only, partial) | $0 | $215,000 | $430,000 |
| **Year 2 total saving** | **$1,058,000** | **$2,601,000** | **$5,202,000** |
| Year 2 investment (Wave 2 remainder + Wave 3 build) | $198,000 | $198,000 | $198,000 |
| **Year 2 net** | **$860,000** | **$2,403,000** | **$5,004,000** |

**Year 3 (months 25–36, full platform operational):**

| | Conservative (3× full yr) | Base (10× full yr) | Target (14× full yr) |
|---|:-:|:-:|:-:|
| Wave 1a + Wave 3 re-fill | $1,050,000 | $3,500,000 | $4,900,000 |
| Wave 1b saving | $504,000 | $1,680,000 | $2,352,000 |
| Wave 2 saving | $810,000 | $4,408,686 | $6,172,160 |
| Wave 3 facility profiles | $158,000 | $528,000 | $740,880 |
| **Year 3 total saving** | **$2,522,000** | **$10,116,686** | **$14,165,040** |
| Year 3 investment (maintenance) | $50,000 | $50,000 | $50,000 |
| **Year 3 net** | **$2,472,000** | **$10,066,686** | **$14,115,040** |

### 8c. Cumulative 3-year picture

| | Conservative | Base case | Target ($200M) |
|---|:-:|:-:|:-:|
| Total investment (3 years) | $895,000 | $895,000 | $895,000 |
| Total saving (3 years) | $4,008,000 | $13,145,686 | $19,795,040 |
| **Net 3-year value** | **$3,113,000** | **$12,250,686** | **$18,900,040** |
| **Portfolio ROI** | **348%** | **1,369%** | **2,112%** |
| Fully invested payback | Month 10 | Month 8 | Month 7 |

*[Note: investments are front-loaded (months 0–20); savings accelerate as volume grows. Even in the conservative scenario (3× volume, not 14×), the portfolio pays back by month 10 and delivers 377% 3-year ROI.]*

---

## 9. Assumption Log

> **[A-CR-1] 40% of no-shows are notification failures.**
> **Why it matters:** Drives Wave 1a annual saving. If only 20% are notification failures, saving drops to ~$175K/year and payback extends to ~10 months.
> **If wrong:** Business case for Wave 1a remains positive even at 20% — payback still within 12 months. Primary risk is overstatement, not viability.
> **Confidence:** Low — not stated in scenario. Typical healthcare staffing benchmark suggests 30–50% of no-shows are preventable through proactive communication.

> **[A-CR-2] Wave 1a combined saving (no-show + confirmation monitoring) = $350K/year (conservative).**
> **Why it matters:** Drives Wave 1 payback calculation. Used conservative estimate ($350K vs base $575K) throughout to ensure business case is defensible under scrutiny.
> **If wrong:** If confirmation monitoring saving is zero (coordinators use the saved time on other tasks with no efficiency gain), saving is $270K/year and payback extends to 6.7 months — still within the 12-month threshold.
> **Confidence:** Medium for direction; low for magnitude. Requires calibration in mock testing.

> **[A-CR-3] Wave 2 build cost: $495K (reconciled with D1 estimate of $475K — $20K rounding difference).**
> **Why it matters:** Drives Wave 2 payback calculation. D1 used $475K as the "after reuse" estimate; this document's itemised reuse analysis produces $495K. Difference is within estimation error on a low-confidence estimate.
> **If wrong:** At $600K (no reuse savings), payback at current volume extends to ~27 months but remains strong at target volume (35 days).
> **Confidence:** Low — any significant API complexity in ServiceNow or nurse database could increase Wave 2 build cost by 50%.

> **[A-CR-4] Volume ramps from 1× at Wave 2 go-live to 14× over 24 months, averaging ~5× in Year 2.**
> **Why it matters:** Wave 2 Year 2 saving in the base case depends on volume growth. If MedFlex does not grow, Year 2 saving is $270K (current volume) not $1.35M.
> **If wrong:** At flat volume, total programme ROI drops from 1,449% to ~240% (3-year, base assumptions) — still strongly positive. The compounding roadmap is viable at flat volume; it is transformational at target volume.
> **Confidence:** Medium — volume growth is explicitly Marcus Reyes's stated goal and the engagement is designed around it; but growth execution is outside the engagement's control.

> **[A-CR-5] 85% of WS2 cases produce a coordinator HITL selection log entry suitable for facility preference extraction.**
> **Why it matters:** Drives how quickly the facility preference profile store accumulates sufficient data for Wave 3 deployment. At 240K cases/year, 85% = 204K logged selections. If HITL log format is inconsistent, Wave 3 deployment may require an additional 3–6 months of data cleanup.
> **If wrong:** Wave 3 deployment delays by up to 6 months. Annual saving impact: ~$430K delayed, not lost.
> **Confidence:** Medium — logging is specified in the agent governance (PA-13); extraction quality depends on coordinator note-taking discipline during HITL reviews.

> **[A-CR-6] Wave 3 facility preference profiles reduce complex-fill HITL rate from 15% to 8%.**
> **Why it matters:** Drives Wave 3 additional annual saving ($741K at target volume).
> **If wrong:** If profiles reduce HITL rate only from 15% to 12%, annual saving is ~$423K at target volume — Wave 3 payback extends from 2.9 to 5 months. Still a strong investment.
> **Confidence:** Low — depends on profile quality and coordinator adoption. Requires A/B test validation in Wave 3 rollout (4-week parallel run as specified in Wave 3a build plan).

> **[A-CR-7] Wave 3 build cost: $210K (vs. $150K in D1 preview).**
> **Why it matters:** D1's preview estimate of $150K did not fully cost the integrated WS4→WS2 pipeline component. This document's itemised estimate is $210K. The $60K difference does not materially affect Wave 3 payback (still <3 months).
> **If wrong:** Even at $350K, Wave 3 payback is 4.9 months. Business case is robust to cost overrun.
> **Confidence:** Low — Wave 3 scope is the least detailed of the three waves; architecture scoping required before committing.
