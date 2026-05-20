# Gate 4 Deliverable 1 — Token Economics Model
## MedFlex: WS2 Nurse-to-Shift Matching Agent

*Source: Scenario/scenario.md, D2C_volume_value_analysis.md, D4b_capability_spec_WS2_lean.md. All non-scenario numbers are labelled as assumptions with confidence levels.*

---

## 0. Executive Summary

| Metric | Current volume (240K/year) | Target volume (3.36M/year — 14×) |
|--------|:-:|:-:|
| WS2 baseline (3 min/case) | $504,000 | $7,056,000 |
| Annual agent cost | $202,560 + $200K infra = **$402,560** | $2,836,000 + $400K infra = **$3,236,000** |
| **WS2 annual saving** | **$101,440 (marginal)** | **$3,820,160** |
| WS1 direct saving (additive) | $168,000 | $2,352,000 |
| **Combined WS1+WS2 saving** | **$269,440** | **$6,172,160** |
| Build cost | $750,000 | $750,000 |
| WS2 payback | 7.4 years (standalone) | ~71 days / 10 weeks |
| Combined WS1+WS2 payback | 2.8 years | ~6 weeks |
| 3-year ROI (WS2 only) | Negative | 1,428% |

*WS4 note: coordinators do not perform shift confirmation today — the 12% no-show rate exists because confirmation does not happen at all. WS4 RPA is a new capability that introduces confirmation for the first time. Its benefit is no-show reduction (revenue preservation), not coordinator time displacement. WS4 economics are modelled separately in Gate 4 D2.*

**Bottom line:** The case for WS2 at current volume is marginal standalone but viable combined with WS1. The compelling case is at scale: WS2 avoids hiring 51 additional matching coordinators at 14× volume (84 → 33 HITL), delivering a 10-week payback. Add WS1's $2.35M intake-automation saving and the combined programme delivers $6.17M/year — consistent with Marcus Reyes's board target economics.

**Model tier finding:** Upgrading from Haiku-only to a Haiku+Sonnet blended architecture costs ~$1,800/year more in tokens but is expected to reduce the HITL rate from 20% to 15%, saving $591,000/year in coordinator time at target volume. **Token cost is not the variable that matters — HITL rate is.**

---

## 1. Scenario Context

**Engagement:** MedFlex, healthcare staffing agency, 5-state US region.
**Primary agentic target:** WS2 — Nurse-to-shift matching (Agentic Value Score: 20/25 — strongest candidate in portfolio).
**Current state:** 8 coordinators, ~120 decisions/coordinator/day, 4.2-hour average time-to-fill, 7% mismatch rate, 12% no-show rate.
**Board target:** 14× revenue growth to $200M in 24 months, with 2-3× headcount (not 14×).
**Agent job:** Given a validated MatchingBrief from WS1, query nurse database, apply hard credential gates (HR-1 to HR-5), classify profile notes, rank a shortlist, present to coordinator for selection, execute submission, manage withdrawal state.

---

## 2. Baseline Cost Model

### 2a. Current human cost per case

```
Total coordinator time per decision (WS1 + WS2 only):
  8 coordinators × 8-hour day = 3,840 coordinator-minutes/day
  3,840 minutes ÷ 960 decisions/day = 4.0 minutes per decision

  WS4 is excluded from this baseline: coordinators do not perform shift confirmation
  today — there is no confirmation step in the current workflow. WS4 RPA introduces
  confirmation as a new capability; its benefit is no-show reduction, not coordinator
  time displacement. Including WS4 in the baseline would invent a current cost that
  does not exist.

Time allocation: WS1 + WS2 only [Assumption A1 — low confidence, see below]:
  WS1 Shift Intake (parsing request, extracting fields, building MatchingBrief): 1 min/case
  WS2 Matching (querying DB, applying rules, reviewing candidates, submitting):  3 min/case
  Total:                                                                         4 min/case ✓

WS2-specific baseline (this model):
  3 min/case × $42.00/hr ÷ 60 = $2.10/case

WS1 baseline (for combined-system reference):
  1 min/case × $42.00/hr ÷ 60 = $0.70/case

Fully loaded hourly cost:
  $60,000 base salary × 1.4× benefits/overhead = $84,000/year
  $84,000 ÷ 2,000 working hours = $42.00/hour fully loaded
  [Assumption A2: US healthcare staffing coordinator market rate. Confidence: low.]

Annual volume (current): 960/day × 250 working days = 240,000 cases/year
  [Assumption A3: 250 working days. Confidence: low — hospitals often operate 365 days.
  If 365 days: 350,400 cases/year, WS2 annual baseline = $735,840.]

WS2 annual baseline cost (current): $2.10 × 240,000 = $504,000/year
WS1 annual baseline cost (current): $0.70 × 240,000 = $168,000/year
Combined WS1+WS2 baseline:          $2.80 × 240,000 = $672,000/year
```

### 2b. Indirect costs (not included in primary model — included for completeness)

| Cost type | Estimated impact | Basis |
|-----------|-----------------|-------|
| Queue cost (4.2-hr time-to-fill) | Lost placements to faster competitors | Scenario states first-to-submit wins [DS-confirmed] |
| Error cost (7% mismatch rate) | Rework, facility relationship damage | Scenario |
| No-show cost (12% no-show rate) | Emergency re-dispatch coordinator time + revenue leakage per unplaced shift | Scenario |
| Opportunity cost | Coordinators doing low-value search vs. relationship work | — |

*No-show cost note: The 12% no-show rate exists because there is no confirmation step in the current workflow — coordinators assign nurses but do not follow up. WS4 RPA introduces automated confirmation for the first time; it is not displacing existing coordinator work but adding a new control. The no-show benefit therefore does not appear in the coordinator time baseline ($2.80/case) and is not captured in this model. See Gate 4 D2 for WS4 standalone economics. Improved shortlist quality from WS2 may reduce no-show frequency if placement mismatch is a contributing factor — not modelled here.*

These are real costs not captured in the $672K baseline. The business case is conservative by excluding them.

---

## 3. Token Economics Model

### 3a. Agent architecture and per-step model selection

The WS2 agent processes a case in 6 logical steps. Model selection is made per step based on whether the task requires AI reasoning or deterministic rule execution.

| Step | Task | Model | Rationale |
|------|------|-------|-----------|
| 1 | Brief completeness validation (status = ADVANCED_TO_WS2, all fields non-null) | **Haiku** | Binary structured check — no reasoning required |
| 2 | Nurse DB query construction (credential, availability, proximity, state-license filters) | **Haiku** | Parameterised template filling from structured MatchingBrief fields |
| 3 | Hard rule gate application (HR-1 to HR-5, DNR exclusion) | **Haiku** | Deterministic rule evaluation on structured data; no inference required |
| 4 | Profile note classification (BLOCKING / RISK_SIGNAL / NEUTRAL) + candidate ranking | **Sonnet** | Free-text note interpretation requires contextual NLP; ranking rationale must be explainable to build coordinator trust [Adoption risk: A13] |
| 5 | Multi-submission state check | **Haiku** | Deterministic comparison of open submission records |
| 6 | Shortlist output formatting + HITL queue notification | **Haiku** | Template-based structured output |

**Design logic:** Sonnet is used only for Step 4 — the one step where AI reasoning replaces genuine coordinator judgment (reading unstructured notes and ranking candidates). All other steps are deterministic and Haiku-sufficient. This minimises token cost while applying the higher-capability model where it prevents coordinator distrust (the primary adoption failure vector from the prior recommendation engine failure [DS-confirmed: A13]).

### 3b. Token consumption per case

**Shared / cacheable context (system prompt):**

| Component | Tokens | Cache strategy |
|-----------|-------:|---------------|
| Matching rules and hard credential logic (HR-1 to HR-5) | 600 | Cache write on session start; cache read on every subsequent call |
| Output format template (CandidateShortlist schema, ShortlistEntry fields) | 350 | Cache read |
| Profile note classification schema (BLOCKING / RISK_SIGNAL / NEUTRAL criteria) | 250 | Cache read |
| Agent identity, scope, governance hard-stop instructions | 300 | Cache read |
| **Total cacheable (system prompt)** | **1,500** | Written once; read ~960× per day at current volume |

**Per-case variable input:**

| Component | Tokens | Notes |
|-----------|-------:|-------|
| Structured MatchingBrief (from WS1) | 400 | Specialty, shift datetime, facility, unit, credential level — structured JSON |
| Nurse DB query results (top 20–30 candidates: credentials, availability, proximity) | 1,500 | Structured records; largest single token contributor |
| Profile notes on shortlisted candidates (free text, 5–8 candidates × avg 100 tokens) | 600 | Variable; zero if notes field is null → NEUTRAL auto-classification |
| **Total per-case variable input** | **2,500** | |

**Per-case output:**

| Component | Tokens | Notes |
|-----------|-------:|-------|
| Ranked shortlist (top 3–5 entries with profile note classification and ranking rationale) | 600 | Sonnet output for Step 4 |
| Orchestration state (submission tracking, withdrawal instructions) | 150 | Haiku output for Steps 5–6 |
| **Total per-case output** | **750** | |

**Total tokens per case:**
- Without caching: 1,500 (system) + 2,500 (input) + 750 (output) = **4,750 tokens**
- With prompt caching (system prompt cached, 99%+ hit rate at 960 calls/day): 2,500 + 750 = **3,250 variable tokens** + 1,500 cache read

### 3c. Tool calls per case

| Tool call | Purpose | Estimated cost | Frequency |
|-----------|---------|---------------|-----------|
| ServiceNow brief read | Retrieve MatchingBrief record | $0.001 | Every case |
| Nurse DB credential query | Filter by specialty + credential level | $0.001 | Every case |
| Nurse DB availability query | Filter by shift datetime + hours | $0.001 | Every case |
| DNR list lookup | HR-4 exclusion gate per facility | $0.001 | Every case |
| Pre-submission credential re-check (WS3 embedded) | Non-bypassable gate before submission | $0.001 | Every case |
| ServiceNow shortlist write | Create CandidateShortlist record + HITL notify | $0.001 | Every case |
| **Total tool call cost** | | **$0.006/case** | |

*[Assumption A4: Tool call unit costs at $0.001 per API call are order-of-magnitude estimates for ServiceNow and structured DB calls. Confidence: low — actual costs depend on MedFlex's ServiceNow tier, API call volume pricing, and database hosting. At 240,000 cases/year, even 10× error = $14,400/year — negligible relative to HITL cost.]*

### 3d. Infrastructure cost

| Component | Current volume | Target volume (14×) | Notes |
|-----------|:-:|:-:|-----|
| Compute (agent runtime, API gateway) | $80,000/year | $160,000/year | Scales sub-linearly with volume [Assumption A5] |
| Monitoring and observability | $40,000/year | $80,000/year | Compliance audit logging required [D4b §0 governance] |
| Storage (ServiceNow records, audit trail) | $30,000/year | $80,000/year | Per-case audit records for credential compliance |
| Maintenance and prompt engineering | $50,000/year | $80,000/year | Ongoing calibration, taxonomy updates |
| **Total infrastructure** | **$200,000/year** | **$400,000/year** | |

*[Assumption A5: Infrastructure scales at ~40% of linear. Confidence: medium — infrastructure costs typically show economies of scale at higher volume.]*

---

## 4. Multi-Model Cost Comparison

Three architecture options are evaluated. The key variable is HITL rate — a better model is expected to produce more accurate, explainable shortlists, reducing coordinator review time and frequency.

### 4a. Per-case token cost by model

**Model tier pricing (May 2026):**

| Model | Input (per 1M) | Output (per 1M) | Cache read (per 1M) |
|-------|:-:|:-:|:-:|
| Claude Haiku 4.5 | $0.80 | $4.00 | $0.08 |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $0.30 |
| Claude Opus 4.7 | $15.00 | $75.00 | $1.50 |

**Option A: Haiku-only (cost-minimised)**

```
System prompt cache read:  1,500 × $0.08/1M  = $0.00012
Per-case input:            2,500 × $0.80/1M  = $0.00200
Per-case output:             750 × $4.00/1M  = $0.00300
Token cost per case:                          $0.00512 ≈ $0.005
```

Risk: Haiku profile note classification produces lower-quality shortlist ranking rationale.
Expected HITL rate impact: 20% of cases require deeper coordinator review (vs. 15% blended).

**Option B: Haiku + Sonnet blended (recommended base case)**

```
Haiku steps (1, 2, 3, 5, 6):
  System prompt cache read:  1,500 × $0.08/1M  = $0.00012
  Variable input (Haiku):    1,700 × $0.80/1M  = $0.00136
  Output (Haiku):              150 × $4.00/1M  = $0.00060
  Haiku subtotal:                               $0.00208

Sonnet step (4 — profile notes + ranking):
  Input to Sonnet:             800 × $3.00/1M  = $0.00240
  Output (Sonnet):             600 × $15.00/1M = $0.00900
  Sonnet subtotal:                              $0.01140

Token cost per case:  $0.00208 + $0.01140 =   $0.01348 ≈ $0.013
```

Expected HITL rate: 15% (Sonnet produces explainable shortlist rationale; coordinator trusts ranking and confirms without re-querying for ~85% of cases).

**Option C: Sonnet-only (quality-maximised)**

```
System prompt cache read:  1,500 × $0.30/1M  = $0.00045
Per-case input:            2,500 × $3.00/1M  = $0.00750
Per-case output:             750 × $15.00/1M = $0.01125
Token cost per case:                          $0.01920 ≈ $0.019
```

Expected HITL rate: 10% (highest-quality shortlist output; most cases have a clear top candidate with full reasoning chain).

### 4b. HITL cost by model option

```
Coordinator hourly rate: $42.00/hr = $0.70/min

HITL time per case:
  Clean fill (coordinator reviews shortlist + confirms top candidate): 30 seconds = 0.5 min
  Complex fill (coordinator reviews + applies judgment): 5.0 minutes

Weighted HITL cost per case:
  Option A (20% complex):  0.20 × (5.0 × $0.70) + 0.80 × (0.5 × $0.70)
                         = 0.20 × $3.50 + 0.80 × $0.35 = $0.70 + $0.28 = $0.98/case

  Option B (15% complex):  0.15 × (5.0 × $0.70) + 0.85 × (0.5 × $0.70)
                         = 0.15 × $3.50 + 0.85 × $0.35 = $0.525 + $0.298 = $0.823/case

  Option C (10% complex):  0.10 × (5.0 × $0.70) + 0.90 × (0.5 × $0.70)
                         = 0.10 × $3.50 + 0.90 × $0.35 = $0.35 + $0.315 = $0.665/case
```

*[Assumption A6: Clean fill review time = 30 seconds (coordinator receives pre-ranked shortlist with credential confirmation and note classification; single click to confirm). Complex fill = 5 minutes (coordinator re-evaluates candidates, may query database independently). Confidence: low — actual review time depends on HITL UX design. If coordinators re-verify agent's credential check manually, clean fill rises to 2+ minutes and all HITL cost estimates increase.]*

### 4c. Total agent cost per case comparison

| | **Option A: Haiku-only** | **Option B: Haiku+Sonnet (recommended)** | **Option C: Sonnet-only** |
|---|:-:|:-:|:-:|
| Token cost | $0.005 | $0.013 | $0.019 |
| Tool call cost | $0.006 | $0.006 | $0.006 |
| HITL cost | $0.980 | $0.823 | $0.665 |
| **Total per case** | **$0.991** | **$0.844** | **$0.690** |
| vs. Baseline ($2.80) | -65% | -70% | -75% |
| HITL rate | 20% | 15% | 10% |

**Key insight:** Token cost is not the dominant variable. HITL cost accounts for 97–99% of total agent cost. A $0.014/case increase in token cost (Haiku → Sonnet-only) saves $0.291/case in HITL cost — a 21:1 return on the incremental token spend. **The model tier decision is a HITL rate decision, not a token cost decision.**

At current volume (240,000 cases/year):
- Haiku-only vs. Sonnet-only: $0.991 - $0.690 = $0.301/case × 240,000 = **$72,240/year additional saving** from upgrading to Sonnet-only

At target volume (3,360,000 cases/year):
- Haiku-only vs. Sonnet-only: $0.301/case × 3,360,000 = **$1,011,360/year additional saving** from upgrading to Sonnet-only

**Recommended architecture: Option B (Haiku+Sonnet blended).** The blended approach captures 70% of the Sonnet-only HITL rate benefit at 40% of the token cost premium. It is more robust to model capability uncertainty than either extreme — if Haiku proves sufficient for ranking, cost decreases; if Sonnet proves insufficient, Opus can be introduced for edge cases without redesigning the pipeline.

---

## 5. Business Case — ROI and Payback Period

### 5a. Build cost breakdown

| Component | Estimated cost | Confidence |
|-----------|:-:|---|
| Assessment, design, and architecture finalisation | $75,000 | Medium |
| WS1 NLP extraction agent (prerequisite) | $150,000 | Low — dependency for WS2 quality |
| WS2 matching agent development | $200,000 | Low |
| ServiceNow integration (brief read, shortlist write, submission) | $100,000 | Low |
| Nurse database API integration and query tooling | $75,000 | Low |
| HITL coordinator interface build | $50,000 | Low |
| Testing, calibration, and acceptance | $75,000 | Medium |
| Change management and coordinator training | $25,000 | Medium |
| **Total build cost** | **$750,000** | Low overall |

#### Estimation methodology

Each line is sized by rough FTE-week estimate × blended healthcare IT services rate ($150–250/hr depending on role — architect, developer, trainer). The scenario contains no build cost data; all figures are order-of-magnitude estimates. The ServiceNow integration line ($100K) carries a premium relative to its technical complexity because ServiceNow platform licensing overhead inflates integration costs beyond pure development time.

**Cross-checks:**
- *Industry range:* Healthcare data integration projects of comparable scope (EHR integrations, NLP extraction pipelines) typically land $500K–$2M. $750K is mid-range.
- *Sensitivity:* Business case holds at $1.5M build cost (4.4-month payback at target volume — see §6). The absolute number matters less than whether the range is plausible.
- *Internal consistency:* Wave 2 actual cost in the compounding roadmap (Gate 4 D2) is $495K after Wave 1 platform asset reuse removes $205K of redundant build work — a 29% discount from this standalone $750K figure, which is consistent with the integration reuse mechanism.

**WS1 prerequisite note:** The $150K WS1 NLP line is included here because WS2 quality depends on receiving well-structured briefs from WS1. However, WS1 is Wave 1b in the compounding roadmap and its cost properly belongs in that wave's budget. If reviewing WS2 in isolation, the standalone WS2 build cost is $600K; the $750K figure represents the full dependency stack.

*[Assumption A7: $750K build cost. Confidence: low — requires architecture scoping to validate, specifically: ServiceNow tier pricing, whether the nurse database has an existing API layer, and whether any MedFlex tooling can be reused for WS1 NLP. Sensitivity: see §6.]*

### 5b. Current volume scenario (240,000 cases/year)

**Using Option B (Haiku+Sonnet, recommended):**

```
WS2 annual baseline (3 min/case):    $2.10 × 240,000   = $504,000
Annual agent variable cost:          $0.844 × 240,000  = $202,560
Annual infrastructure:                                  = $200,000
Total annual agent cost:                                = $402,560

WS2 annual saving:                   $504,000 − $402,560 = $101,440

Build cost:                          $750,000
WS2 standalone payback:              $750,000 ÷ $101,440 = 7.4 years

Year-by-year net (WS2 standalone):
  Year 1: $101,440 − $750,000 = −$648,560
  Year 2: $101,440 − $648,560 = −$547,120
  Year 3: $101,440 − $547,120 = −$445,680
  3-year ROI: −$445,680 ÷ $750,000 = −59%

Combined WS1+WS2 (Wave 1b + Wave 2):
  WS1 direct saving: $168,000   (1 min × 240,000 × $0.70/min — near full automation)
  WS2 saving:        $101,440
  Combined annual:   $269,440 → payback $750K ÷ $269,440 = 2.8 years
  Combined 3-year ROI: ($269,440 × 3 − $750,000) ÷ $750,000 = 7.8%
```

**Verdict at current volume: MARGINAL.** WS2 standalone takes 7.4 years to pay back — the $200K infrastructure cost is too large relative to the $101K annual saving at this volume. Combined with WS1's $168K direct saving, the programme pays back in 2.8 years. Neither figure is the primary business case — the board-level argument requires target volume (§5c).

### 5c. Target volume scenario (3,360,000 cases/year — $200M board target)

The engagement framing is explicit: "10x the business without 10x-ing the coordinators." At 14× volume, the human-only staffing cost is:

```
─── HUMAN-ONLY WS2 AT 14× VOLUME ────────────────────────────────────────────
WS2 coordinator headcount required (3 min matching/case, human-only):
  3,360,000 × 3 min ÷ 60 ÷ 2,000 hr/coordinator = 84 coordinators
Annual WS2 coordinator cost:     84 × $84,000              = $7,056,000

─── AGENT SCENARIO AT 14× VOLUME ────────────────────────────────────────────
HITL coordinator headcount (still required for WS2 review):
  HITL hours/year:  [0.15 × (5/60) + 0.85 × (0.5/60)] × 3,360,000 = 65,800 hrs
  Coordinators:     65,800 ÷ 2,000 hr/coordinator       = 33 coordinators
  Annual HITL coordinator cost:  33 × $84,000            = $2,772,000

Agent token + tool cost:         ($0.844 − $0.823) × 3,360,000 = $63,840
  [Token $0.013 + tool $0.006 = $0.019/case × 3,360,000]
Annual infrastructure:                                    = $400,000

Total annual agent cost:         $2,772,000 + $63,840 + $400,000 = $3,235,840

─── SAVING (WS2 ONLY) ───────────────────────────────────────────────────────
WS2 coordinators avoided:        84 − 33 = 51 coordinators
Avoided headcount cost:          51 × $84,000              = $4,284,000
Less: additional infrastructure:                           −  $400,000
Less: token + tool cost:                                   −   $63,840
WS2 annual net saving:           $4,284,000 − $463,840     = $3,820,160

─── PAYBACK ─────────────────────────────────────────────────────────────────
Build cost:              $750,000
Payback period:          $750,000 ÷ $3,820,160 = 71 days ≈ 10 weeks

Year 1 net (target volume): $3,820,160 − $750,000  = $3,070,160
3-year net value:           ($3,820,160 × 3) − $750,000 = $10,710,480
3-year ROI:                 $10,710,480 ÷ $750,000 = 1,428%

─── COMBINED WS1+WS2 AT 14× VOLUME ─────────────────────────────────────────
WS1 automation eliminates 1 min intake/case (near full automation, minimal HITL):
  1 min × 3,360,000 ÷ 60 ÷ 2,000 = 28 coordinators avoided
  WS1 annual saving: 28 × $84,000 = $2,352,000

Combined WS1+WS2 saving:  $3,820,160 + $2,352,000 = $6,172,160
Combined 3-year ROI:      (($6,172,160 × 3) − $750,000) ÷ $750,000 = 2,369%
Combined payback:         $750,000 ÷ $6,172,160 = 44 days ≈ 6 weeks
```

**Verdict at target volume: COMPELLING.** WS2 standalone delivers 1,428% 3-year ROI and 10-week payback at 14× volume, avoiding 51 matching coordinator hires. Combined with WS1's intake automation (28 additional avoided hires), the programme avoids 79 coordinator hires in total, delivering $6.17M/year and a 6-week payback on the $750K investment — the number Marcus Reyes takes to the board.

**Important caveat [Assumption A8]:** The scale economics assume the $200M revenue target is achieved through volume growth (14× decisions/day), not margin expansion at current volume. If growth is margin-driven, the current-volume combined saving ($269K/year, 2.8-year payback) is the relevant figure. Confidence: medium — "10x without 10x-ing coordinators" explicitly implies throughput, not margin.

---

## 6. Sensitivity Analysis

Three scenarios are modelled across four key variables. The business case is evaluated at target volume (3.36M/year) since that is the decision-relevant scenario.

| Variable | Conservative | Base case | Optimistic |
|----------|:-:|:-:|:-:|
| Token cost (vs. current) | +50% | Current | -30% |
| HITL rate | 25% | 15% | 5% |
| Coordinator loaded cost | $35/hr ($70K loaded) | $42/hr ($84K loaded) | $50/hr ($100K loaded) |
| Build cost | $1,500,000 | $750,000 | $500,000 |

**Annual saving sensitivity at target volume (3.36M cases/year):**

*HITL rate is the dominant variable. Token cost sensitivity is negligible.*

| Scenario | WS2 human-only (14×) | WS2 annual saving | Payback period | 3-year ROI |
|----------|:-:|:-:|:-:|:-:|
| **Conservative** (25% HITL, +50% tokens, $70K coordinator, $1.5M build) | $5,880,000 | $2,207,360 | 8.2 months | 341% |
| **Base case** (15% HITL, current tokens, $84K coordinator, $750K build) | $7,056,000 | $3,820,160 | 71 days | 1,428% |
| **Optimistic** (5% HITL, −30% tokens, $100K coordinator, $500K build) | $8,400,000 | $5,920,160 | 31 days | 3,452% |

**Conservative scenario detail (WS2 only, target volume):**
```
HITL cost per case (25% complex, $35/hr):
  0.25 × (5/60 × $35) + 0.75 × (0.5/60 × $35) = $0.729 + $0.219 = $0.948/case
Token cost (+50%): $0.013 × 1.5 = $0.020/case
Total agent cost per case:  $0.948 + $0.020 + $0.006 = $0.974/case

Annual agent cost (3.36M):  $0.974 × 3,360,000 = $3,272,640
Annual infra:                                    = $400,000
Total annual agent cost:                         = $3,672,640

WS2 human-only (84 coordinators × $70K): $5,880,000
WS2 annual saving: $5,880,000 − $3,672,640 = $2,207,360

Build cost: $1,500,000
Payback: $1,500,000 ÷ $2,207,360 = 8.2 months
3-year net: ($2,207,360 × 3) − $1,500,000 = $5,122,080
3-year ROI: $5,122,080 ÷ $1,500,000 = 341%
```

**Sensitivity conclusion:** The business case holds under all three scenarios. Even stacking four adverse assumptions simultaneously — 25% HITL rate, 50% higher token costs, lower coordinator wages ($70K), and double the build cost — the WS2 standalone payback is 8.2 months and the 3-year ROI is 341%. The 3-min WS2 baseline provides sufficient headroom to absorb adverse conditions. **HITL rate remains the dominant variable**: the difference between conservative (25%) and base (15%) scenarios is $1.6M/year in annual saving at target volume. Token price changes remain economically trivial.

**Token price trend sensitivity:** Model prices have declined approximately 10× every 12–18 months historically. A 50% reduction in token prices from current levels (plausible within the 24-month project horizon) reduces the per-case token cost from $0.013 to $0.007 — a saving of $0.006/case × 3,360,000 = $20,000/year at target volume. **Token price declines are economically trivial relative to HITL cost.** Monitor for model quality improvements that reduce HITL rate, not for token price reductions.

---

## 7. Self-Financing Roadmap (Wave Summary)

Full compounding roadmap is Deliverable #2 (Gate 4). Summary:

| Wave | Use case | Build cost | Annual saving (target vol) | Payback | Platform assets created |
|------|---------|:-:|:-:|:-:|---|
| 1a | WS4 Confirmation RPA (no-show reduction) | $150,000 | $350,000–$500,000 est. | 4–6 months | ServiceNow placement API, SMS/email gateway, notification infrastructure |
| 1b | WS1 Shift Intake NLP | $200,000 | **$168,000/year** (current vol.) / **$2,352,000/year** (target vol.) direct + WS2 quality uplift (indirect) | 11.9 months (current vol. basis) | ServiceNow read/write connector, HITL queue, specialty taxonomy |
| 2 | WS2 Matching Agent (this model) | $400,000 remaining | $3,820,160 at target vol. (WS2 only); $6,172,160 combined WS1+WS2 | 71 days / 10 weeks (WS2 only) | Nurse DB API, shortlist UX, multi-submission tracker |
| 3 | Multi-agent orchestration (WS1+WS2+WS4 pipeline) | $150,000 | Margin improvement | < 6 months | Shared governance layer, model router |

**WS1 saving streams — two distinct mechanisms:**

- **Direct ($168K/year current vol. | $2,352,000/year target vol.):** The 1+3 split (Assumption A1) attributes 1 min/case to WS1 intake — parsing the shift request, extracting specialty/credentials/shift time, and building the structured MatchingBrief. WS1 eliminates this fraction entirely: coordinators receive a validated MatchingBrief in their queue and spend their full available time on matching decisions. Calculation: 1 min × $42.00/hr ÷ 60 = $0.70/case × 240,000 = $168,000 (current); $0.70 × 3,360,000 = $2,352,000 (target). At 14× volume this also reduces HITL coordinator headcount below the 33-coordinator figure in §5c, which was calculated from WS2 HITL hours only.
- **Indirect — WS2 shortlist quality uplift:** Cleaner, consistently structured briefs reduce the rate at which WS2 produces ambiguous or incomplete shortlists. This supports the 15% HITL rate assumption (Option B) — higher intake error rates would push the complex-case fraction up and increase the per-case coordinator cost modelled in §4b.

Wave 1 combined saving ($518K–$668K/year at current volume: $350K–$500K WS4 + $168K WS1) funds Wave 2 deployment. The $400K remaining WS2 build cost (after Wave 1's shared integration assets are already in production) is approximately 60% of the standalone $750K estimate — the compounding effect reduces marginal build cost.

---

## 8. Calibration Targets

These are the operating-point targets the agent must hit before production release. If not met in mock testing, either the business case parameters must be updated or the agent must not go to production.

| Metric | Target | If missed |
|--------|--------|-----------|
| Shortlist accuracy (coordinator selects agent's top-ranked candidate) | ≥ 70% of fills | HITL complex rate increases → HITL cost rises; re-evaluate model tier |
| Clean fill coordinator review time | ≤ 30 seconds (critical assumption A6) | If 2+ minutes: HITL cost per case doubles; coordinator headcount at scale increases from 33 to 55+ |
| Tokens per case | ≤ 4,750 (base; 3,250 variable) | Budget has 5× headroom; non-critical |
| HITL escalation rate | ≤ 15% (Option B) / ≤ 10% (Option C) | Triggers model tier upgrade review |
| Pre-submission credential gate pass rate | 0 HR-1/HR-2/HR-3 violations | Compliance failure; agent paused pending investigation |

---

## 9. Assumption Log

> **[A1] Coordinator time splits 1 min (WS1 intake) + 3 min (WS2 matching) = 4 min total per decision. WS4 has no current coordinator time cost.**
> **Why it matters:** Drives the WS2-specific baseline of $2.10/case and the WS1 baseline of $0.70/case. WS4 is excluded because coordinators do not perform confirmation today — there is no baseline to displace. Including WS4 time in the baseline would manufacture a current cost that does not exist and inflate the combined saving.
> **If wrong:** If WS2 takes only 2 min (WS1 takes 2 min), WS2 baseline drops to $1.40/case and standalone WS2 saving at current volume turns negative (−$67K). At target volume payback extends from 10 weeks to ~6 months. The 3-min allocation is the more conservative and defensible assumption for WS2.
> **Confidence:** Low — no scenario data for the time split. The 1+3 approximation reflects that matching (querying, rule evaluation, profile note review, ranking, shortlist presentation) is substantially more cognitively demanding than intake parsing. Requires validation in discovery.

> **[A2] US healthcare staffing coordinator fully loaded cost = $42/hr ($84K/year).**
> **Why it matters:** HITL cost per case scales linearly with this rate. All cost comparisons depend on it.
> **If wrong:** Sensitivity table shows outcomes at $35/hr (conservative) and $50/hr (optimistic).
> **Confidence:** Low — not stated in scenario; US market estimate.

> **[A3] 250 working days/year.**
> **Why it matters:** Drives annual case volume. If 365 days, annual volume = 350,400/year (+46%).
> **If wrong:** Business case strengthens at current volume (more cases/year); economics at target volume are unchanged (14× is 14× regardless of base).
> **Confidence:** Low — healthcare staffing agencies often operate 365 days/year.

> **[A4] Tool call unit cost = $0.001/call.**
> **Why it matters:** At 6 tool calls/case × 240,000/year = 1,440,000 calls/year × $0.001 = $1,440/year — negligible.
> **If wrong:** Even at 10× estimate, $14,400/year is not material.
> **Confidence:** Low on unit price; immateriality confirmed regardless.

> **[A5] Infrastructure scales at ~40% of linear (economies of scale).**
> **Why it matters:** $200K/year at current volume → $400K/year at 14× volume (not $2.8M).
> **If wrong:** If infrastructure scales linearly: $2.8M/year — increases infrastructure cost by $2.4M. WS2 annual saving drops from $3,820,160 to $1,420,160. Payback extends from 10 weeks to ~6 months. Still strong.
> **Confidence:** Medium — cloud infrastructure typically sub-linear; validate at architecture review.

> **[A6] Clean fill coordinator review = 30 seconds; complex fill = 5 minutes.**
> **Why it matters:** Single most sensitive variable in the model. HITL is 97–99% of per-case agent cost.
> **If wrong:** If clean fill review = 2 minutes (coordinator re-verifies credentials manually): HITL cost per case rises from $0.823 to $1.715 (+108%). WS2 annual saving at target volume drops from $3,820,160 to $823,040. Payback extends from 10 weeks to ~11 months. Still viable, but the 30-second assumption is load-bearing and must be validated against HITL UX design and coordinator behaviour before committing to the economics.
> **Confidence:** Low — depends on interface design and coordinator trust level; prior recommendation engine failure [DS-confirmed: A13] suggests coordinators may be slow to trust agent output initially.

> **[A7] Build cost = $750,000.**
> **Why it matters:** Drives payback calculation. Sensitivity: at $1.5M build cost, payback at target volume = 4.4 months (still strong).
> **If wrong:** Business case holds under build cost up to ~$15M at target volume (payback = 1 year) — a very wide margin.
> **Confidence:** Low — requires architecture scoping.

> **[A8] $200M revenue target scales proportionally with decisions/day.**
> **Why it matters:** The entire scale-economics case (14× volume, 6-week payback) depends on this. If Marcus Reyes's growth target is achievable through margin expansion rather than volume, the agent's capacity-unlock value does not materialise and the current-volume economics ($269K/year saving, 2.8-year payback) are the relevant figures.
> **If wrong:** Reframe the value proposition as quality improvement (lower 7% mismatch rate, lower 12% no-show rate) rather than capacity unlock. Requires remodelling of indirect cost avoidance.
> **Confidence:** Medium — "10x without 10x-ing coordinators" explicitly implies volume growth.

> **[A9] HITL rate impact by model tier: 20% (Haiku-only), 15% (blended), 10% (Sonnet-only).**
> **Why it matters:** HITL rate is the dominant cost driver. The 5-point difference between Haiku-only and Sonnet-only blended represents $591K/year at target volume.
> **If wrong:** If all three model tiers produce the same HITL rate (e.g., the HITL rate is driven by task complexity, not model quality), the cheapest model (Haiku-only) is always optimal. This would reduce the annual saving at target volume by ~$130K. Validate HITL rate in mock testing by holding task mix constant and varying model tier.
> **Confidence:** Low — theoretical; requires empirical validation in mock testing.
