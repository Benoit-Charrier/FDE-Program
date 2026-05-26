# Gate 4 Deliverable 1 — Token Economics Model
## Greenfield Health Systems: WS1 Administrative Claims Adjudication Agent

*Source: `Scenario/scenario_context.md`, `Deliverables/D2A_cognitive_load_map.md`, `Deliverables/D2B_delegation_suitability_matrix.md`, `Deliverables/D2C_volume_value_analysis.md`, `References/atx-economics.md`. All non-scenario figures are labelled as assumptions with confidence levels.*

---

## 0. Executive Summary

- **Primary agentic target:** WS1 — Administrative Adjudication, 338,000 claims/year (1,300/day × 260 working days); the business case is a 63-point gap between Greenfield's 22% auto-adjudication rate and the 85% industry benchmark (scenario.md): each admin claim processed manually costs $18.23 (35 min × $31.25/hr) vs. $0.315 with the agent — a 98.3% per-claim cost reduction; at 338,000 claims/year the agent delivers $568K total operational cost (agent + 7 retained FTEs) against $6.16M for equivalent manual staffing; net cash saving vs. current $1.3M workforce budget is $732K/year — payback period 6.9 months.
- **Model tier finding:** Sonnet for the five judgment micro-tasks (eligibility discrepancy resolution, clinical plausibility assessment, prior auth partial-match resolution, clinical content routing classification, contract exception handling) — no LLM for the five deterministic micro-tasks (format parsing, eligibility lookup, code validity, prior auth lookup, fee schedule calculation), which execute as code or API calls; the cheapest model is not the right answer because HITL cost ($0.26/claim at 25% HITL rate) is 52× larger than token cost ($0.005/claim), and using Haiku for the judgment tasks raises the HITL rate to an estimated 35%, adding $35K/year to annual cost against a token saving of ~$1,560/year.
- **Business case under conservative assumptions:** At 35% HITL rate and 2× build cost ($840K), payback extends to ~17 months — the business case holds under all tested adverse scenarios; the 2-minute admin HITL time (calibrated against Dr. Webb's 3 min/claim clinical review benchmark, which sets the upper bound for targeted exception resolution) has sharply reduced HITL rate sensitivity, shifting the primary financial risk from HITL rate to build cost; scope control within $400K is now the condition that determines whether payback falls inside or outside 12 months, though HITL rate remains the primary quality criterion for production readiness.

---

## 0b. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [1. Scenario context and primary agentic target](#1-scenario-context-and-primary-agentic-target)
- [2. Baseline human cost model](#2-baseline-human-cost-model)
- [3. Agent architecture — per-step model selection](#3-agent-architecture--per-step-model-selection)
- [4. Token economics per case](#4-token-economics-per-case)
- [5. Multi-model comparison](#5-multi-model-comparison)
- [6. Total agent cost per case — recommended option](#6-total-agent-cost-per-case--recommended-option)
- [7. Business case — current volume](#7-business-case--current-volume)
- [8. Scale volume](#8-scale-volume)
- [9. Self-financing roadmap](#9-self-financing-roadmap)
- [10. Sensitivity analysis](#10-sensitivity-analysis)
- [11. Calibration targets](#11-calibration-targets)
- [12. Assumption log](#12-assumption-log)

---

## 1. Scenario Context and Primary Agentic Target

**Engagement:** Greenfield Health Systems — medical claims adjudication payer operation. **Primary agentic target:** WS1 — Administrative Adjudication, selected from the D2C Volume × Value analysis (Agentic Value Score 20/25; Wave 1 assignment). Current annual volume: 338,000 WS1 claims/year (1,300/day × 260 working days — Assumption A-G4D1-1), derived from the 65%/35% administrative/clinical routing split applied to the scenario's 2,000 claims/day figure (scenario_context.md §4). No growth target is stated in the scenario for Greenfield Health Systems; §8 is omitted accordingly. The single constraint that makes manual scaling impossible is the 7.3× daily processing deficit: Greenfield's 20 claims review staff can sustain approximately 274 claims/day of throughput against 2,000 arriving daily (derived from 20 review staff × 480 min/day ÷ 35 min = 274/day — Assumption A-G4D1-2), producing the backlog that puts cycle time at 9+ days and triggers the active SLA penalties James Liu is absorbing (Exchange 3). The ROI is calculable because the scenario provides: a concrete daily volume (2,000/day), a measurable auto-adjudication baseline (22%), a named industry benchmark (85%), a specific FTE headcount (20 review staff), and a committed build budget ($400K, Sarah Chen, Exchange 1). The substitution opportunity is defined enough to close the arithmetic.

---

## 2. Baseline Human Cost Model

```
BASELINE UNIT COST

Time per case:
  Overall average: 35 min/claim (scenario.md — blended across all claim types)
  WS1-specific time: not decomposed in scenario; 35 min/claim applied as baseline
  [Reconciliation note: at 35 min/claim, all 20 staff produce 20 × 2,080 hr × 60 min ÷ 35 min =
   71,314 claims/year of total throughput against 520,000 arriving (2,000/day × 260) — a 7.3×
   shortfall. For WS1 admin claims alone: 338,000/year requires 95 FTEs at 35 min/claim. This
   confirms the capacity crisis is structural and not solvable by headcount alone — the agent
   eliminates per-claim processing time on the standard path, not just headcount.]

Fully loaded hourly cost:
  Base salary estimate: $47,000/year  [Assumption A-G4D1-3 — US claims processor, mid-market]
  Benefits + management overhead multiplier: 1.38× [Assumption A-G4D1-3]
  Fully loaded annual cost: $47,000 × 1.38 = $64,860 ≈ $65,000/year
  Working hours/year: 2,080 (52 weeks × 40 hours)
  Fully loaded hourly rate: $65,000 ÷ 2,080 = $31.25/hour

Workforce cost model:
  Total claims review staff (current): 20 (CFO email Exchange 1; James Liu Exchange 3)
  Annual workforce cost (current): 20 × $65,000 = $1,300,000/year

  Post-automation retained staff: 7 (James Liu Exchange 3; §4f HITL model requires
    ~1.4 FTEs for WS1 HITL work alone at 25% HITL rate, 2-min average)
  Annual retained staff cost: 7 × $65,000 = $455,000/year

  [All 20 staff currently handle both admin and clinical claims — no sub-allocation by
   work stream is possible without per-path processing time data (unstated in scenario).
   The business case is built on per-claim economics (§7), not FTE displacement.]

Baseline cost per case (time-based):
  35 min/claim × ($31.25/hr ÷ 60 min/hr) = $18.23/claim
  [The FTE-allocated rate ($845,000 ÷ 338,000 = $2.50/claim) is not a meaningful unit cost:
   it spreads 13 FTEs' budget over 338,000 arriving claims, but those 13 FTEs can only
   sustain 46,423 claims/year at 35 min/claim — 86% of arriving claims accumulate as backlog.
   The time-based figure ($18.23/claim) is the correct per-claim cost comparator: it
   represents what a human processor actually spends on each claim that gets processed.]
```

**Indirect costs not captured in the primary model:**

- **SLA penalty cost (queue cost):** VP Operations is actively absorbing contractual penalties on claims exceeding 7 days (Exchange 3). The penalty rate is not stated in the scenario; this is an unquantified but confirmed cost that adds to the case for WS1 automation. Conservative estimate: material, directionally increases the business case beyond the FTE model.
- **Rework cost from first-pass errors:** The 41% denial appeal overturn rate (scenario.md) implies a significant proportion of WS1 decisions are wrong at first pass. Each overturned denial requires a full re-adjudication cycle. At 43 appeals/day (Assumption A-D2C-2, D2C), ~18 overturned determinations/day generate rework at full processing cost. Not modelled; directionally adds to the baseline.
- **Opportunity cost of skilled workers on pattern-matching:** Clinical plausibility assessment (MT-WS1-5, D2A) and clinical content routing (MT-WS1-8, D2A) are judgment-requiring tasks performed by all 13 WS1 processors, consuming capacity that cannot be recovered by adding headcount alone.

---

## 3. Agent Architecture — Per-Step Model Selection

*WS1 micro-tasks from D2A §2d. Five deterministic tasks execute as code or API calls — no LLM tokens consumed. Five judgment tasks invoke Sonnet (pattern classification, tolerance reasoning, multi-factor routing). Not all judgment calls run on every claim; Steps 5 and 8 run on every claim; Steps 3, 7, and 10 are conditional, triggered only when the upstream deterministic step surfaces an exception.*

| Step | Micro-task | Execution | Rationale |
|------|-----------|:----------:|-----------|
| 1 | MT-WS1-1: Format parsing and intake normalisation | **Code** | Parse-or-fail logic on structured inputs (EDI 837) and defined field extraction rules; DD=H in D2A; correct answer follows a format specification — an EDI parser or PDF extraction library resolves this, not an LLM |
| 2 | MT-WS1-2: Eligibility lookup — standard path | **API call** | Binary structured lookup (eligible/not eligible on service date); DD=H, CL=L in D2A; the eligibility system returns a boolean result — no reasoning required, no tokens consumed |
| 3 | MT-WS1-3: Eligibility discrepancy resolution | **Sonnet** (conditional, ~5% of claims) | CL=H, DD=L in D2A; triggered only when Step 2 returns a discrepancy; requires contextual pattern recognition ("data lag vs. genuine gap") that no deterministic rule can resolve — escalation errors here contribute directly to the 41% overturn rate |
| 4 | MT-WS1-4: Code validity and pairing check | **Code / lookup table** | ICD-10/CPT crosswalk rules are a structured lookup against a reference table; DD=M in D2A; standard path is a code lookup, not LLM inference; plausibility edge cases surface as exceptions handled by Step 5 |
| 5 | MT-WS1-5: Clinical plausibility assessment | **Sonnet** (every claim) | CL=H, DD=L, EF=H in D2A — tacit clinical coding pattern recognition across diagnosis-procedure-provider combinations; no formal rule exists; runs on every claim entering the WS1 routing pipeline (2,000/day — both administrative and clinical paths, as the routing decision at Step 8 has not yet been made) because no prior step can pre-screen for plausibility violations without LLM reasoning; the primary driver of elevated HITL rate in any Haiku-on-judgment architecture |
| 6 | MT-WS1-6: Prior auth requirement check and lookup | **API call** | Structured lookup: required-or-not, present-or-not; DD=H, CL=L in D2A; the prior auth system returns a record or absence — deterministic check, no tokens consumed |
| 7 | MT-WS1-7: Prior auth partial match resolution | **Sonnet** (conditional, ~8% of claims) | CL=H, DD=L, EF=M in D2A; triggered only when Step 6 returns a partial match; tolerance judgment (unit variance, date mismatch, code variant) with no documented threshold; the decision cannot be resolved by code because no rule defines when a 10-unit authorisation covers a 12-unit claim |
| 8 | MT-WS1-8: Clinical content routing classification | **Sonnet** (every claim) | CL=H, DD=L, EF=H in D2A — multi-factor classification across diagnosis codes, procedure codes, and provider specialty; runs on every claim entering WS1 (2,000/day — this step produces the routing decision that splits claims to administrative or clinical path; it cannot be pre-empted by code); highest-stakes step (false negative = URAC/NCQA compliance violation); confidence threshold gates HITL escalation |
| 9 | MT-WS1-9: Fee schedule application and payment calculation | **Code / rate table** | Fee schedule is a structured rate table; cost-sharing calculation is arithmetic; DD=H, CL=L in D2A; correct answer is computed by a formula against a lookup — an LLM call here adds latency and cost with zero quality benefit |
| 10 | MT-WS1-10: Fee schedule contract exception handling | **Sonnet** (conditional, ~2% of claims) | CL=H, DD=L, Tool Coverage=L in D2A; triggered only when Step 9 flags a contract exception; contract carve-out rules may reside in unstructured documents; Sonnet produces a defensible rate recommendation for HITL confirmation |

**Architecture summary:** The WS1 agent is an orchestrator, not a single-call LLM pipeline. Steps 1, 4, 9 run as in-process code (EDI parsers, code validation libraries, fee arithmetic). Steps 2, 6 run as external API calls (eligibility system, prior auth system). No LLM tokens are consumed on these five paths. Sonnet is invoked only when no deterministic rule resolves the decision. Average Sonnet calls per WS1 claim: **~2.15** (Steps 5 and 8 on every claim; Steps 3, 7, 10 on ~15% of claims combined).

---

## 4. Token Economics Per Case

### 4a. Shared / Cacheable Context (System Prompt)

| Component | Tokens | Cache strategy |
|-----------|-------:|---------------|
| Agent role, output schema, and task instructions | 200 | Cache read (written once per session, read every claim) |
| WS1 decision rules and validation logic | 150 | Cache read |
| HITL escalation criteria and confidence thresholds | 100 | Cache read |
| Compliance boundary instructions (clinical content routing rules) | 50 | Cache read |
| **Total cacheable** | **500** | Amortised across all claims in session |

Cache hit rate: With 2,000 claims/day processed in continuous sessions (steps 1–8 route all incoming claims; steps 9–10 process the 1,300 administrative-path claims), every claim after the first in a session is a cache read. At 10× cheaper than standard input pricing, caching reduces the effective system prompt cost from $1.50/1,000 tokens to $0.15/1,000 tokens (Sonnet pricing). Across 520,000 total claims/year, cache savings on the system prompt: $1.50 × 500 ÷ 1,000,000 × 520,000 = $390/year in uncached cost → $39/year in cached cost; $351/year saving [immaterial relative to HITL cost, but correctly accounted].

### 4b. Per-Judgment-Call Variable Input Tokens

LLM calls occur only for the five judgment micro-tasks. Each call receives only the context relevant to that specific task — not the full claim record — keeping per-call token counts low and focused.

| Judgment task | Input tokens | Output tokens | Frequency per claim |
|---------------|-------------:|:-------------:|:-------------------:|
| MT-WS1-5: Clinical plausibility (diagnosis codes, procedure codes, provider specialty) | 250 | 100 | Every claim entering routing (2,000/day; 1.0×) |
| MT-WS1-8: Clinical content routing (codes, specialty, clinical indicators) | 300 | 100 | Every claim entering routing (2,000/day; 1.0×) |
| MT-WS1-3: Eligibility discrepancy (eligibility record + claim service date context) | 200 | 100 | Conditional (~5%) |
| MT-WS1-7: Prior auth partial match (auth record, procedure details, unit comparison) | 200 | 100 | Conditional (~8%) |
| MT-WS1-10: Contract exception (fee schedule excerpt, contract flag context) | 250 | 100 | Conditional (~2%) |

**Weighted per-claim token calculation:**
```
Always-run calls (Steps 5 and 8):
  Input:  (1.0 × 250) + (1.0 × 300) = 550 tokens
  Output: (1.0 × 100) + (1.0 × 100) = 200 tokens

Conditional calls (average 0.15 calls/claim at ~220 input + 100 output):
  Input:  0.15 × 220 = 33 tokens
  Output: 0.15 × 100 = 15 tokens

System prompt cache reads (500 tokens × 10% × 2.15 calls): ~108 effective-cost tokens

Total effective tokens per claim: 550 + 200 + 33 + 15 + 108 ≈ 906 ≈ ~900 tokens
[Assumption A-G4D1-4 — revised from 1,000 tokens; directionally unchanged]
```

### 4c. Output Tokens Per Claim (aggregate)

| Output type | Tokens | Notes |
|-------------|-------:|-------|
| MT-WS1-5 plausibility assessment result | 100 | Every claim |
| MT-WS1-8 routing classification + confidence score | 100 | Every claim |
| Conditional call outputs (Steps 3, 7, 10 — weighted average) | 15 | ~15% of claims × 100 tokens |
| **Total per-claim output (weighted)** | **~215** | [Assumption A-G4D1-4] |

**Total tokens per claim:**
- Without caching: 500 (system, per call) × 2.15 + 583 (variable input) + 215 (output) = 1,873 tokens
- With caching: 583 (variable input) + 215 (output) + 108 (system prompt cache reads) = ~906 effective tokens

### 4d. Tool Call Costs

| Tool call | Purpose | Cost | Frequency |
|-----------|---------|:----:|-----------|
| Eligibility system API | Member eligibility lookup on service date | $0.010 | Every claim |
| Code validation API / reference data | ICD-10/CPT crosswalk and validity check | $0.010 | Every claim |
| Prior auth system API | Prior auth presence and detail lookup | $0.010 | Every claim |
| Fee schedule system API | Rate lookup for procedure-provider combination | $0.010 | Admin-path claims only (1,300/day) |
| **Total tool call cost** | | **$0.040/admin claim; $0.030/clinical routing claim** | First 3 APIs on all 2,000/day; fee schedule on admin path (1,300/day) only |

[Assumption A-G4D1-5: $0.01/call; all four systems unnamed in scenario; costs are industry-typical estimates for REST API calls within a cloud environment. No third-party premium APIs are assumed.] Tool call costs are immaterial relative to HITL costs but are not zero and are correctly included. Annual tool call cost: (520,000 × $0.030) + (338,000 × $0.010) = $15,600 + $3,380 = $18,980/year.

### 4e. Infrastructure Cost

```
Monthly infrastructure cost (WS1 agent, current volume):
  Compute (agent runtime, async worker): $100/month  [Assumption A-G4D1-6]
  Monitoring, logging, alerting: $80/month
  Storage (claim records, audit trail): $50/month
  Maintenance and patching overhead: $50/month
  Total monthly: $280/month

  Annual infrastructure: $280 × 12 = $3,360/year
  Cases per year: 338,000
  Infrastructure cost per case: $3,360 ÷ 338,000 = $0.010/claim

Note: Infrastructure scales sub-linearly with volume. At 2× volume (676,000 claims/year),
infrastructure would increase to approximately $480/month ($5,760/year) — roughly 1.7× for
2× volume — reflecting compute scaling but not proportional growth in storage or monitoring.
```

### 4f. HITL Cost Per Case

```
HITL rate derivation from D2A breakpoints:
  BP-WS1-1 Eligibility discrepancy (MT-WS1-3, EF=L):    ~5% of WS1 claims
  BP-WS1-2 Coding plausibility flag (MT-WS1-5, EF=H):   ~15% of WS1 claims [Assumption A-G4D1-7]
  BP-WS1-3 Prior auth partial match (MT-WS1-7, EF=M):   ~8% of WS1 claims [Assumption A-D2A-7]
  BP-WS1-4 Clinical content confidence below threshold:   ~10% of WS1 claims [Assumption A-G4D1-8]
  BP-WS1-5 Fee schedule contract exception (MT-WS1-10, EF=L): ~2% of WS1 claims

  Raw additive rate: 5+15+8+10+2 = 40%
  Overlap adjustment: a single claim may trigger multiple breakpoints; ~60% overlap factor applied
  Net HITL rate: 40% × (1 - 0.38) = ~25% of WS1 claims require at least one human review event
  [Assumption A-G4D1-7: overlap factor; actual overlap measured in calibration phase]

HITL time per event:
  Clean exception (agent presents specific flag; human confirms or overrides in 1 step): 1 min
  Complex exception (agent flags ambiguous signals; human reviews context briefly): 3.5 min
  Mix: 70% clean, 30% complex  [Assumption A-G4D1-9]
  Weighted average: (0.70 × 1) + (0.30 × 3.5) = 0.70 + 1.05 = 1.75 min ≈ 2 min
  [Calibrated against Dr. Webb's clinical review benchmark: 20 claims/hour = 3 min/claim
   for a full pre-filled clinical packet review. Admin HITL is a targeted exception
   resolution — simpler than clinical review — and should be faster, not slower.]

Reviewer hourly cost: $31.25/hr (same fully loaded rate as processor team)

Weighted HITL cost per case:
  = 0.25 × (2/60) × $31.25
  = 0.25 × $1.042
  = $0.260/claim
```

---

## 5. Multi-Model Comparison

*Three architectures evaluated. HITL rate is the dominant variable — stated explicitly in each option.*

|  | **Option A: Haiku-only** | **Option B: Blended (recommended)** | **Option C: Sonnet-only** |
|---|:---:|:---:|:---:|
| Token cost per case | $0.002 | $0.005 | $0.007 |
| Tool call cost | $0.040 | $0.040 | $0.040 |
| Expected HITL rate | **35%** | **25%** | **25%** |
| HITL cost per case | $0.365 | $0.260 | $0.260 |
| Infrastructure cost per case | $0.010 | $0.010 | $0.010 |
| **Total agent cost per case** | **$0.417** | **$0.315** | **$0.317** |
| vs. baseline ($18.23/claim) | -97.7% | **-98.3%** | **-98.3%** |

**HITL rate assumptions by option:**
- **Option A (Haiku for judgment tasks, 35% HITL):** Haiku applied to the five judgment micro-tasks (MT-WS1-3, 5, 7, 8, 10) produces less reliable pattern classification and tolerance reasoning than Sonnet. The coding plausibility task (MT-WS1-5, EF=H, DD=L) and clinical content routing task (MT-WS1-8, EF=H, DD=L) are the primary drivers of the elevated rate. Both tasks involve no formal rule — the agent must reason across multi-factor patterns without a deterministic decision function. Haiku's reduced reasoning capability on unstructured pattern recognition produces more borderline outputs that cannot meet the confidence threshold, escalating to HITL at a higher rate. Note: the five deterministic tasks (Steps 1, 2, 4, 6, 9) execute as code or API calls regardless of model tier — they do not appear in this comparison. [Assumption A-G4D1-2]
- **Option B (Sonnet for judgment tasks, 25% HITL — recommended):** Sonnet applied to the five judgment tasks brings reasoning quality to parity with the scenario's expectations for the clinical content classifier and plausibility assessor. HITL triggers are cases that are genuinely ambiguous at the BP-WS1-4 confidence threshold — not cases the model fails to process.
- **Option C (Sonnet for all tasks including deterministic, 25% HITL):** Routing Sonnet to the five deterministic tasks (Steps 1, 2, 4, 6, 9) produces no HITL rate improvement because those steps do not drive HITL escalations. The binary eligibility lookup returns a boolean from an external system; the fee schedule calculation is arithmetic against a rate table. Upgrading these to Sonnet adds token cost with zero quality or HITL benefit. HITL rate is identical to Option B.

**Recommendation: Option B.** Options B and C are essentially equivalent in total per-claim cost ($1.357 vs. $1.359 — a $0.002/claim or $676/year difference at current volume). Option B is correct on architectural grounds: deterministic tasks should execute as code and API calls, not LLM inference. Applying Sonnet to a binary eligibility lookup adds token cost and latency for zero benefit. The correct architecture assigns LLM reasoning capacity only to the steps that require it.

**Required finding:** Token cost is not the dominant variable — HITL cost is. At the base case (Option B, 25% HITL, 2-min average):
- Token cost: $0.005/claim (1.6% of total agent cost)
- HITL cost: $0.260/claim (82.5% of total agent cost)
- HITL cost is **52× larger** than token cost

**Threshold condition:** Haiku-only (Option A) would become optimal only if Haiku achieved the same 25% HITL rate as Sonnet on the judgment tasks. At 25% HITL, Option A total cost would be $0.260 + $0.002 + $0.040 + $0.010 = $0.312/claim — marginally cheaper than Option B ($0.315/claim). Given that the 10-point HITL rate difference between options is driven by the judgment tasks assigned to Haiku (not the deterministic tasks), a scenario where Haiku matches Sonnet on those tasks is implausible. The threshold condition will not be met.

---

## 6. Total Agent Cost Per Case (Recommended Option)

```
Token cost per case:        $0.005   (Sonnet for 5 judgment tasks, ~2.15 calls/claim; code/API for 5 deterministic tasks)
Tool call cost per case:    $0.040   (4 API calls × $0.010)
Infrastructure per case:    $0.010
HITL cost per case:         $0.260   (25% HITL rate × 2 min × $31.25/hr)
Total agent cost per case:  $0.315

vs. Baseline: $18.23/claim → 98.3% reduction in per-claim cost
```

---

## 7. Business Case — Current Volume

```
Per-claim economics (primary business case metric):
  Manual cost per claim:   $18.23  (35 min × $31.25/hr — §2)
  Agent cost per claim:    $0.315  (Option B — §6)
  Saving per claim:        $17.92  (98.3% reduction)
  Annual admin claims:     338,000/year

Annual baseline — total workforce (current state):
  20 FTEs × $65,000 = $1,300,000/year  [Assumption A-G4D1-3]
  [All 20 staff handle both admin and clinical claims today at 14% of arriving volume]

Annual agent running cost (Option B):
  [Steps 1–8 process all 2,000 claims/day (520,000/year); steps 9–10 admin-path only (338,000/year)]
  Token cost:    Admin path (338,000 × $0.005):                   $1,690/year
                 Clinical routing — steps 1–8 (182,000 × $0.005):   $910/year
                 Total:                                           $2,600/year
  Tool calls:    Eligibility, coding, prior auth (520,000 × $0.030): $15,600/year
                 Fee schedule API (admin path, 338,000 × $0.010):     $3,380/year
                 Total:                                           $18,980/year
  Infrastructure: $3,360/year  [fixed: $280/month × 12]
  HITL labour:    338,000 × 0.25 × (2/60) × $31.25 = $88,021/year
    [FTE equivalent: 2,813 hrs ÷ 2,080 hrs/FTE = 1.4 FTEs retained for WS1 HITL]
  Total agent running cost: $112,961/year ≈ $113,000/year

Annual post-automation total cost:
  Agent running cost:      $113,000/year
  Retained staff (7 FTEs): $455,000/year  [James Liu Exchange 3]
  Total:                   $568,000/year

Annual cash saving:
  $1,300,000 − $568,000 = $732,000/year
  [Conservative floor: cash released by transitioning from 20 to 7 FTEs.
   The per-claim model shows why this is conservative: at $18.23/claim, processing
   338,000 admin claims manually would cost $6.16M/year (95 FTEs at $65K). The agent
   achieves this throughput at $568K total — a $5.59M advantage vs. full manual staffing,
   or a 7.3× throughput improvement at 44% of current spend. The $732K saving is realised
   against the current $1.3M budget, not against the hypothetical full-staffing cost.]

Annual saving (CFO gross FTE model — board presentation):
  8 FTE reduction × $65,000 = $520,000/year (Exchange 1)
  [Gross headcount saving before netting agent running costs; used for board presentation]
```

### Build Cost

| Line item | Basis | Cost |
|-----------|-------|-----:|
| Discovery and design (2 weeks: FDE × 1, architect × 1, $200/hr avg) | 2 × 80 hrs × $200 | $32,000 |
| Intake processing pipeline (2 weeks: 2 developers × $200/hr) | 2 × 80 hrs × $200 | $32,000 |
| WS1 agent core development (8 weeks: 2 developers × $200/hr) | 8 × 80 hrs × $200 | $128,000 |
| API integrations (4 systems × 2 weeks × 1 developer × $200/hr) | 4 × 2 × 40 hrs × $200 | $64,000 |
| Clinical content classifier (4 weeks: 2 developers × $200/hr) | 4 × 80 hrs × $200 | $64,000 |
| Testing and calibration (4 weeks: 2 QA + 1 developer × $175/hr blended) | 4 × 120 hrs × $175 | $84,000 |
| Infrastructure setup (one-time compute, networking, monitoring config) | Fixed estimate | $10,000 |
| Change management and staff enablement | 1 week × 2 people | $6,000 |
| **Total build cost** | | **$420,000** |

*[Assumption A-G4D1-10: build cost is estimated at market rates for enterprise healthcare IT; $150–$200/hr for architects and developers, $150/hr for QA, $120/hr for change management. Sarah Chen's committed budget is $400K (Exchange 1). The $420K estimate is 5% over budget — within typical estimation uncertainty; scope management recommendation: defer non-core features (e.g., advanced analytics dashboard, provider rejection notice templating) to Wave 2, targeting a $400K Wave 1 scope.]*

**Build cost cross-checks:**

1. **Industry range:** Healthcare payer process automation: $500K–$2M for full enterprise deployment. $400K–$420K is below the low end of the enterprise range, appropriate for a focused single-work-stream Wave 1 scope. Full programme cost across Waves 1–3 would likely fall at $700K–$1M, consistent with the industry range for a multi-work-stream clinical operations transformation.

2. **Sensitivity validation:** At 2× build cost ($840K), payback extends to $840K ÷ $732K = 13.8 months — within a 2-year investment horizon. Build cost is the primary financial risk: a 2× overrun extends payback from 6.9 months to ~14 months but does not break the business case. Scope control within $400K keeps payback at 6.6 months; scope discipline is a prerequisite to signing off on this payback commitment.

3. **Wave attribution:** The clinical content classifier ($64K) is a Wave 1 asset built for WS1-JtD-2 that is directly reused by WS2-JtD-1 (routing verification) in Wave 2 at zero additional build cost. The intake processing pipeline ($32K) is reused for clinical document extraction in WS2-JtD-2. Total Wave 1 assets inherited by Wave 2 at zero marginal cost: $96K. Wave 2 standalone build cost (without reuse): ~$220K. Wave 2 build cost with reuse: ~$124K. Wave 1 directly reduces Wave 2 marginal cost by $96K — more than the entire cost of building Wave 2's clinical document extraction component from scratch.

```
Payback period (full TCO model):
  $420,000 ÷ $732,000/year = 6.9 months
  [At $400K budget (scope-managed): $400,000 ÷ $732,000 = 6.6 months]

Payback period (CFO gross FTE model):
  $420,000 ÷ $520,000/year = 9.7 months ✓
  [At $400K budget: $400,000 ÷ $520,000 = 9.2 months ✓]

Year-by-year cumulative net (full TCO model, $420K build, $732K/year saving):
  [Assumption A-G4D1-11: build completes at month 6; Year 1 includes 6 months of running savings]
  Year 1: ($732,000 × 6/12) - $420,000 = $366,000 - $420,000 = -$54,000 (investment phase)
  Year 2: -$54,000 + $732,000 = +$678,000 cumulative (break-even at ~month 7)
  Year 3: +$678,000 + $732,000 = +$1,410,000 cumulative

3-year ROI:
  Total saving (3 years, phased): $732,000 × 2.5 = $1,830,000
  Total investment: $420,000
  Net 3-year value: $1,830,000 - $420,000 = $1,410,000
  3-year ROI: $1,410,000 ÷ $420,000 × 100 = 336%
```

**Verdict:** The current-volume economics are strong on the full TCO model (payback ~7 months, 3-year ROI 336%) and consistent with the CFO's gross FTE model (payback 9–10 months). The 2-minute HITL time (calibrated against Dr. Webb's clinical review benchmark) has substantially reduced sensitivity to HITL rate fluctuation: the range from 15% to 35% HITL now shifts annual saving only from $767K to $697K — a $70K difference that does not change the investment verdict. The load-bearing risk has shifted to build cost: at 2× build ($840K), payback extends to ~14 months, which remains viable but exceeds the 12-month threshold. The primary success criterion for the build phase remains HITL rate accuracy — not because it determines whether the case holds, but because a high HITL rate signals that the classifier is not ready for production and will generate rework that is invisible in the cost model.

---

## 8. Scale Volume

*The scenario does not state a revenue growth target or claims volume growth target for Greenfield Health Systems. This section is omitted. If a volume growth assumption is produced during engagement planning, this section should be populated using the per-claim cost of $1.357 (Option B) and the FTE capacity model from §2.*

---

## 9. Self-Financing Roadmap

### Wave 1 — Months 1–6 (Build); Months 7–12 (Running)

```
Use cases in this wave:
  INT — Intake processing pipeline:
    Build cost: $32,000 (absorbed into Wave 1 budget)
    Annual saving: Infrastructure-only (no direct FTE reduction; enables WS1 quality)
    Payback: N/A standalone — Wave 1 prerequisite; ROI realised through WS1
  WS1 — Administrative adjudication agent:
    Build cost: $388,000 (Wave 1 total minus INT: $420K - $32K)
    Annual saving: $732,000/year (full TCO model)
    Payback: $388,000 ÷ $732,000 = 6.4 months ✓

Wave 1 cumulative saving by month 12 (6 months running):
  $732,000 × 6/12 = $366,000

Platform assets built in Wave 1 (reused in Wave 2):
  - Member eligibility API integration: saves ~$16,000 in Wave 2 build cost
    (WS2-JtD-1 verifies claim routing using same eligibility data)
  - Prior authorisation API integration: saves ~$16,000 in Wave 2 build cost
    (WS2-JtD-2 assembles prior auth history from the same prior auth system)
  - Document extraction pipeline (built for INT, PDF/portal normalisation):
    saves ~$20,000 in Wave 2 clinical document extraction build cost
  - Clinical content classifier (built + CMO-certified for WS1-JtD-2):
    saves ~$60,000 in Wave 2 build cost — the classifier is reused directly by
    WS2-JtD-1 for routing verification; CMO certification process is complete
  Estimated Wave 2 build cost reduction from reuse: ~$112,000

Funded by: Sarah Chen's committed $400K implementation budget (Exchange 1)
```

**Wave 1 payback note:** At $420K total build cost and $732K/year saving, payback is 6.9 months — well within the 12-month threshold. On the scope-managed $400K budget, payback is 6.6 months. On the CFO's gross FTE model ($520K/year), payback is 9.2–9.7 months. **Client risk exposure:** the build phase itself is the principal net-negative period; the investment is recovered approximately 7 months post go-live. The remaining financial risk is build cost overrun: at $840K (2× estimate), payback extends to ~14 months. Scope control within $400K, not HITL rate management, is now the primary financial lever the engagement team controls before production release.

---

### Wave 2 — Months 7–12 (Build); Months 13–24 (Running)

```
Use cases in this wave:
  WS2 — Clinical context assembly agent (WS2-JtD-1 + WS2-JtD-2 scope only):
    Build cost standalone: $220,000
    Build cost with Wave 1 reuse: $220,000 - $112,000 = $108,000 incremental
    Annual saving: physician throughput improvement enabling 3 FTE reduction
      = 3 FTEs × $65,000 = $195,000/year
    WS2 agent running cost: 182,000 clinical claims/year × $0.50/claim = $91,000/year
      [Assumption A-G4D1-12: $0.50/claim for context assembly — more token-intensive
       than WS1 due to multi-source document retrieval and synthesis]
    Net WS2 annual saving: $195,000 - $91,000 = $104,000/year
    Payback: $108,000 ÷ $104,000 = 12.5 months ✓ (within tolerance)

Wave 2 cumulative saving by month 24 (12 months running):
  WS1: $732,000/year × 12 months = $732,000 (full second year)
  WS2: $104,000/year × 12 months = $104,000 (first full year)
  Wave 2 cumulative: $490,000 in Year 2 alone

Platform assets built in Wave 2 (reused in Wave 3):
  - Clinical document extraction pipeline extension: saves ~$15,000 in Wave 3
    (appeals documents are a similar unstructured-PDF retrieval problem)
  - Pre-filled review packet schema: reusable as a structured evidence-assembly
    template for appeal root cause classification (APP-JtD-1)
  Estimated Wave 3 build cost reduction from reuse: ~$30,000

Funded by: Wave 1 running savings ($366,000 accumulated by month 12) plus
  Wave 1 platform asset reuse ($112,000 build cost reduction)
```

---

### Wave 3 — Months 13+ (Planning); Months 19+ (Build/Run, conditioned on WS1 steady state)

```
Use cases in this wave:
  APP — Denial appeals management (APP-JtD-1 root cause classification, APP-JtD-2
    administrative path determination):
    Conditioned on: WS1 steady-state appeal pattern confirmed 90 days post-go-live
    Estimated build cost: $150,000 (with Wave 1+2 reuse of claim records, denial
      reason code access, document extraction pipeline)
    Annual saving: dependent on residual appeal volume after WS1 quality improvement;
      cannot be calculated without WS1 steady-state data

Funded by: Wave 1 + Wave 2 accumulated savings

Recommended next step: Do not proceed to build scope until WS1 has been in production
  for 90 days and the residual appeal volume and root cause distribution are measured.
```

---

### Cumulative 3-Year Picture

```
Total investment (Wave 1 + Wave 2 only; Wave 3 deferred):
  Wave 1 build: $420,000
  Wave 2 build (incremental): $108,000
  Total: $528,000

Total saving (3 years, phased):
  WS1: $732,000/year × 2.5 years (running from month 7) = $1,830,000
  WS2: $104,000/year × 1.5 years (running from month 13) = $156,000
  Total saving: $1,986,000

Net 3-year value: $1,986,000 - $528,000 = $1,458,000
Portfolio ROI: $1,458,000 ÷ $528,000 × 100 = 276%
```

**Compounding logic:** The clinical content classifier — built and CMO-certified for WS1-JtD-2 at a cost of $64,000 — is the single platform asset that most reduces Wave 2 marginal cost. It eliminates the $60,000 rebuild cost and, more importantly, it eliminates the CMO certification process from Wave 2 entirely. Dr. Marcus Webb's team certification of the classifier is the highest-effort governance activity in the engagement (it requires establishing and validating the clinical content definition that Sarah Chen explicitly requested in Exchange 3). That process happens once in Wave 1; Wave 2 inherits a certified classifier that it extends rather than re-certifies. Without this reuse, Wave 2 would require not just $60,000 in build cost but 4–6 weeks of CMO team engagement before any clinical-path work could begin — the reuse saves time that does not show up in the cost model but is the primary reason Wave 2 can be delivered in 6 months rather than 9+. The prior auth and eligibility integrations, each saving $16,000, are the next most valuable — not for their cost but because they are validated data pipelines that both WS1 and WS2 agents call against the same upstream sources, meaning data schema issues discovered in Wave 1 are resolved before Wave 2 production routing begins.

---

## 10. Sensitivity Analysis

| Variable | Conservative | Base case | Optimistic |
|----------|:---:|:---:|:---:|
| HITL rate | 35% (+10pp) | 25% | 15% (-10pp) |
| Build cost | $840K (2×) | $420K | $281K (0.67×) |
| FTE fully loaded rate | $55K/year | $65K/year | $75K/year |

**Annual saving and payback (WS1 current volume):**

| Scenario | Annual saving | Payback period |
|----------|:---:|:---:|
| Conservative (all three variables adverse simultaneously) | ~$586,000 | ~17 months |
| Conservative (HITL 35% only, base build and FTE) | ~$697,000 | ~7.2 months |
| Conservative (build cost 2× only, base HITL and FTE) | ~$732,000 | ~13.8 months |
| **Base case** | **$732,000** | **6.9 months** |
| Optimistic (HITL 15% only, base build and FTE) | ~$767,000 | ~6.6 months |
| Optimistic (all three variables favourable simultaneously) | ~$892,000 | ~3.8 months |

*Annual saving calculations (all use $1.3M current workforce baseline, $455K retained staff; agent running cost varies by HITL rate):*
- *35% HITL: 338,000 × 0.35 × (2/60) × $31.25 = $123,229 HITL labour; tech total: $2,600 + $18,980 + $3,360 = $24,940; total agent: $148,169; post-auto total: $148,169 + $455,000 = $603,169; saving: $1,300,000 − $603,169 ≈ $697,000*
- *25% HITL (base): total agent $113,000; post-auto $568,000; saving $732,000*
- *15% HITL: 338,000 × 0.15 × (2/60) × $31.25 = $52,812 HITL labour; total agent: $77,752; post-auto: $532,752; saving: $1,300,000 − $532,752 ≈ $767,000*
- *All-adverse ($55K FTE, $840K build, 35% HITL): baseline $1,100,000; HITL labour $104,220; total agent $129,160; post-auto $129,160 + $385,000 = $514,160; saving $585,840; payback $840,000 ÷ $585,840 ≈ 17 months*
- *All-optimistic ($75K FTE, $281K build, 15% HITL): baseline $1,500,000; HITL labour $57,622; total agent $82,562; post-auto $82,562 + $525,000 = $607,562; saving $892,438; payback $281,000 ÷ $892,438 ≈ 3.8 months*

**Does the business case hold in the conservative scenario?** Yes — the business case holds under all tested adverse scenarios. The maximum payback is ~17 months (all three variables adverse simultaneously), which remains well within a 2-year investment horizon. **The load-bearing risk has shifted from HITL rate to build cost.** The 2-minute HITL time has compressed the HITL rate sensitivity range: a 20-point swing (15% to 35%) changes annual saving by only $70K (from $767K to $697K) — a 9% variation that does not affect the investment verdict. Build cost is now the dominant variable: at 2× ($840K), payback extends to ~14 months. The go/no-go decision for production release should be: *does the agent achieve ≤25% HITL rate in mock calibration testing before a single live claim is processed?* Not because the business case fails above 25%, but because a high HITL rate signals that classifier quality is insufficient for URAC/NCQA compliance obligations — the compliance constraint, not the economics, is the hard stop.

**Token price sensitivity:** A ±50% change in token prices changes annual token cost by ±$1,300/year (50% × $2,600). This is immaterial — it represents 0.34% of the annual saving and would not affect any business decision. Token price sensitivity is not a material variable in this model.

---

## 11. Calibration Targets

| Metric | Target | Business case impact if missed |
|--------|--------|-------------------------------|
| Clinical content classifier recall (true positive rate for clinical claims) | ≥99.5% | At 99.0% recall: ~1,690 clinical claims/year bypass physician review = URAC/NCQA compliance event; agent is suspended; full manual review resumes; 100% of anticipated saving is lost until classifier is retrained and re-certified |
| Clinical content classifier precision (true positive rate for admin claims) | ≥92% | At 85% precision: ~8% of admin claims over-routed to WS2 physician queue = ~27,040 claims/year added to physician queue; Dr. Webb's 20 claims/hour target is unachievable; WS2 cycle time target (6–7 days) is missed |
| WS1 HITL rate | ≤25% — calibration gate; do not release to production above this threshold | At 35% HITL: annual saving changes from $732K to ~$697K — a $35K difference that does not affect the investment verdict; the hard stop is URAC/NCQA compliance, not economics: a high HITL rate signals classifier quality is insufficient for the clinical routing obligation |
| Tokens per case | ≤1,000 effective tokens | At 3× estimate (3,000 tokens): token cost rises from $0.005 to $0.015/claim = $3,380/year additional — immaterial; token budget is not a binding constraint |
| Processing latency per claim (standard path) | ≤60 seconds end-to-end | WS1 claims are batch-processed within a 7-day SLA; 60-second latency is orders of magnitude below the SLA threshold. Latency concern is operational (queue backlog, UI responsiveness for HITL reviewers) not SLA-driven |
| Compliance gate | 0 clinical claims reaching payment path without physician sign-off | Zero tolerance; one violation triggers URAC audit; agent is suspended pending investigation regardless of claim volume or economic impact |

---

## 12. Assumption Log

> **[A-G4D1-1] WS1 annual volume:** 338,000 claims/year derived from 1,300/day × 260 working days (5-day week, 52 weeks). Both the 5-day working week and the 1,300/day WS1 volume are derived assumptions — neither is stated directly in the scenario.
> **Why it matters:** Drives all annual cost calculations. A 7-day operating week would increase volume to 474,500/year, improving per-claim infrastructure economics and increasing total annual saving proportionally.
> **If wrong:** At 1,667 claims/day total (Sarah Chen, Exchange 3), WS1 volume is 1,083/day × 260 = 281,580/year — 17% lower, reducing annual saving from $386K to ~$321K and extending payback to ~15 months.
> **Confidence:** Low — working week not stated; volume figure disputed between two scenario sources.

---

> **[A-G4D1-2] WS1 processing throughput deficit:** 274 claims/day current throughput (20 review staff × 8 hrs × 60 min ÷ 35 min/claim) vs. 2,000/day arriving — a 7.3× overload against the review staff. Used to illustrate the capacity problem; not directly used in economic calculations.
> **Why it matters:** Confirms that the cycle time crisis is structural, not headcount-solvable, which strengthens the case for agentic intervention.
> **If wrong:** If processors handle multiple tasks simultaneously and 35 min/claim overstates single-claim time, throughput may be higher; does not change the primary economic model.
> **Confidence:** Medium — arithmetic is consistent with the observed 9-day cycle time.

---

> **[A-G4D1-3] Fully loaded cost per WS1 reviewer:** $65,000/year (salary ~$47K + 38% benefits/overhead). Not stated in scenario.
> **Why it matters:** The entire workforce baseline ($1.3M current, $455K retained) and annual cash saving ($732K) rest on this figure. A 20% change in FTE rate moves the annual saving by ~$260K (scales both baseline and retained staff cost simultaneously).
> **If wrong:** At $50K/year: baseline = $650K, saving ≈ $191K, payback ~26 months — weak case. At $80K/year: baseline = $1,040K, saving ≈ $581K, payback ~8.7 months — strong case. Must be confirmed in discovery.
> **Confidence:** Medium — $65K is consistent with published US healthcare claims processor compensation data; order-of-magnitude is reliable, exact figure requires confirmation.

---

> **[A-G4D1-4] Token consumption per WS1 claim:** ~906 effective tokens (weighted across ~2.15 Sonnet calls/claim — Steps 5 and 8 on every claim, Steps 3, 7, 10 on ~15% of claims combined). Each call receives only the context relevant to that task; deterministic steps (1, 2, 4, 6, 9) consume no LLM tokens.
> **Why it matters:** Token cost ($0.005/claim) is 0.4% of total agent cost; a 3× error in this assumption changes annual cost by $3,380 — immaterial. Token count is not the binding constraint.
> **If wrong:** Token consumption is not the governing economic variable; calibration should focus on HITL rate, not token count.
> **Confidence:** Low — no actual prompt has been designed; actual per-call consumption determined during capability spec and mock testing.

---

> **[A-G4D1-5] Tool call cost:** $0.010/call × 4 calls = $0.040/claim. API call costs depend on vendor contracts and system architecture not described in the scenario.
> **Why it matters:** Tool call cost ($18,980/year) is 4% of annual agent running cost; not the dominant variable.
> **If wrong:** At $0.05/call (5× higher): tool call cost rises to ~$0.23/claim blended = $75,920/year additional — adds 16% to agent running cost and reduces annual saving from $732K to ~$656K. Would require confirming external API pricing in discovery.
> **Confidence:** Low — no systems named in scenario; $0.01/call is an internal API cost estimate.

---

> **[A-G4D1-6] Infrastructure cost:** $280/month ($3,360/year) for compute, monitoring, storage, and maintenance.
> **Why it matters:** Infrastructure cost ($0.010/claim) is 0.7% of total agent cost; immaterial.
> **If wrong:** Even at 3× ($10,080/year), infrastructure adds only $0.030/claim — changes annual saving by $6,720. Not a binding variable.
> **Confidence:** Low — cloud infrastructure not described in scenario; estimate is consistent with a moderate-scale single-agent deployment.

---

> **[A-G4D1-7] WS1 HITL rate — base case 25%:** Derived from D2A breakpoints with overlap adjustment. Individual breakpoint rates: BP-WS1-1 (5%), BP-WS1-2 (15%), BP-WS1-3 (8%), BP-WS1-4 (10%), BP-WS1-5 (2%) = 40% additive; 38% overlap adjustment yields 25% net. BP-WS1-2 coding plausibility (15%) is the largest driver and is unknown in the scenario (D0C Unknown U-4).
> **Why it matters:** HITL rate is the dominant cost variable — it determines 95.9% of per-claim agent cost. This is the single most consequential assumption in the model.
> **If wrong:** At 35% HITL: annual saving halved to $208K, payback 2.0 years (fails gate). At 15% HITL: annual saving rises to $559K, payback 9 months. HITL rate must be measured in mock calibration before production release.
> **Confidence:** Low — all individual breakpoint rates are estimates; overlap factor is modelled, not measured. This assumption has the highest materiality in the model.

---

> **[A-G4D1-8] Clinical content routing confidence threshold HITL rate — 10%:** Design target for BP-WS1-4; the HITL queue size at the clinical content classifier confidence threshold. This is a configurable parameter, not a measured outcome.
> **Why it matters:** Part of the 25% aggregate HITL rate. A higher confidence threshold (more conservative routing) increases this rate toward WS2; a lower threshold increases false negative risk. The threshold must be certified by Dr. Webb's team.
> **If wrong:** If threshold must be set conservatively (Dr. Webb requires near-zero false negative tolerance), the HITL rate from BP-WS1-4 alone could reach 20–25%, materially raising total HITL above 25%.
> **Confidence:** Low — the threshold is a design decision not yet made; it depends on classifier accuracy and CMO tolerance for false positives.

---

> **[A-G4D1-9] HITL time split:** 70% clean exceptions (1 min), 30% complex exceptions (3.5 min), weighted average 2 min. Calibrated against Dr. Webb's clinical review benchmark (20 claims/hour = 3 min/claim for a full pre-filled clinical packet). Admin HITL is a targeted exception resolution — simpler than clinical review — and should be faster.
> **Why it matters:** Directly affects HITL cost per claim ($0.260). At 100% complex (3.5 min): HITL cost rises to $0.365/claim — a 40% increase that adds ~$36K/year to agent running cost; saving falls from $732K to ~$696K. The sensitivity range is narrow.
> **If wrong (upward):** If admin HITL exceptions prove more complex than the clinical benchmark implies — e.g., if reviewers must navigate multiple systems to confirm a flag — actual time could be 5 min average. At 5 min: HITL cost = $0.651/claim; annual saving drops to ~$626K; payback rises to ~8 months. Still a strong case.
> **Confidence:** Medium — benchmark is externally grounded (Dr. Webb's clinical review rate); admin HITL is structurally simpler; the 2-minute estimate is directionally reliable but requires calibration against actual reviewer behaviour in UAT.

---

> **[A-G4D1-10] Build cost estimate:** $420K total; itemised from FTE-week basis at $200/hr developer, $175/hr QA, blended $150/hr for architects and change management. Sarah Chen's committed budget is $400K (Exchange 1).
> **Why it matters:** Build cost is the denominator for payback. At 2× ($840K), payback extends to ~14 months — still viable but above the 12-month threshold; scope control within $400K holds payback at 6.6 months.
> **If wrong:** The estimate is 5% over the committed $400K budget. If scope is not managed, the programme runs over budget on the first wave. Scope management recommendation: defer provider rejection notice templating and analytics dashboard to Wave 2, cutting ~$20K from the Wave 1 build.
> **Confidence:** Medium — itemised estimate with explicit basis; consistent with comparable healthcare automation projects.

---

> **[A-G4D1-11] Build timeline:** 6 months from engagement start to go-live (4 months development + 2 months testing/calibration). Year 1 savings are therefore 6 months of running savings.
> **Why it matters:** Year 1 net is negative ($193K savings vs. $420K investment). Break-even occurs at month 13.
> **If wrong:** If build extends to 9 months, Year 1 net worsens and break-even shifts to month 16. If build compresses to 4 months, Year 1 net improves slightly.
> **Confidence:** Low — timeline not stated in scenario; 6 months is typical for a focused single-work-stream agentic build with 4 API integrations.

---

> **[A-G4D1-12] WS2 agent running cost:** $0.50/claim for context assembly (182,000 claims/year = $91K/year). WS2 agent is more token-intensive than WS1 due to multi-source retrieval and unstructured clinical note processing.
> **Why it matters:** Affects Wave 2 net saving ($195K FTE saving - $91K running cost = $104K/year). At $1.00/claim: running cost rises to $182K and net saving drops to $13K/year — nearly break-even.
> **If wrong:** WS2 agent economics are highly sensitive to clinical note retrieval cost. If clinical notes require large context windows for synthesis, per-claim token cost could be 3–5× the WS1 estimate. WS2-specific TCO model is a required Wave 2 planning deliverable before commitment.
> **Confidence:** Low — WS2 agent design is not yet specified; the $0.50/claim estimate is directional only.
