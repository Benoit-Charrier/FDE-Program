# Prompt: Gate 4 Deliverable 1 — Token Economics Model

## Inputs (read all of these before producing any output)

1. **Scenario file** — `Scenario/scenario_context.md` (or your chosen Weeks 1–3 scenario file). Do not invent numbers, systems, or constraints not present there. Every figure must trace back to the scenario or be explicitly labelled as an assumption.
2. **Volume × Value analysis** — your D2C deliverable. Read it for: the primary agentic target, annual case volume, the preliminary TCO sense-check, and the HITL rate derived from D2A breakpoints.
3. **Delegation Suitability Matrix** — your D2B deliverable. Read it for: HITL rates per work stream, archetype assignments, and the breakpoints that mark where human judgment is non-negotiable.
4. **Cognitive Load Map** — your D2A deliverable. Read it for: the per-step time estimates, micro-task structure, and the specific breakpoints that determine what fraction of each case a human must own.
5. **ATX Economics Reference** — `References/atx-economics.md`. Follow its five-step model: baseline → token economics → ROI → self-financing roadmap → calibration.
6. **ATX Scoring Reference** — `References/atx-scoring.md`. Use its TCO formula and sequencing logic.

If a prior deliverable is unavailable, derive the missing inputs from the scenario directly and label every derived figure as an assumption.

---

## Your task

Produce a token economics model for the primary agentic target from your Volume × Value analysis. This is a CFO-grade business case, not a back-of-envelope estimate. Output file: `Deliverables/Gate4_D1_token_economics_model.md`.

The model must cover: baseline human cost, agent cost per case broken down by component (tokens + tools + infrastructure + HITL), multi-model analysis showing *when to use which model tier*, annual saving, build cost, payback period, and a sensitivity analysis that shows whether the business case holds under conservative assumptions.

---

## Required structure

### 0. Executive summary

Three bullet points, written first. Each is one sentence.

1. The primary agentic target, its annual case volume, and the one-line business case (baseline cost vs. agent cost — tie to a number from the scenario)
2. The model tier finding: which tier is recommended, which is not, and the one reason the cheapest model is not automatically the right answer
3. Whether the business case holds under conservative assumptions — state the payback period in the conservative scenario

This section must be self-contained. A reader who reads only this should know the agent target, the cost structure, and the stress-tested ROI.

---

### 1. Scenario context and primary agentic target

State in one paragraph:
- The scenario name and primary agentic target (from your D2C analysis)
- The annual case volume at current state and at any stated growth target
- The single constraint that makes manual scaling impossible (tie to a scenario number)
- Why this is the right use case for an economics model (why the ROI is calculable, not speculative)

---

### 2. Baseline human cost model

Show all arithmetic. Every non-scenario figure must be labelled as an assumption.

```
Baseline unit cost:
  Time per case (hours): [from D2A micro-task inventory, or scenario if stated directly]
  Derivation: [show how you calculated the per-case time — e.g., total capacity ÷ case volume]
  Fully loaded hourly cost: [£/$/€ — label as assumption if not in scenario]
    = base salary × benefits multiplier ÷ working hours/year
  Baseline cost per case = time × hourly cost = [calculated]

Annual baseline:
  Cases per year = [volume × working days — show derivation]
  Annual baseline cost = cases per year × cost per case = [calculated]
```

Include, below the calculation, a note on **indirect costs** not captured in the primary model (queue cost from delays, error cost from mismatch rate, opportunity cost of skilled workers on low-value tasks). Cite scenario numbers where available. Label as qualitative where not calculable.

---

### 3. Agent architecture — per-step model selection

List every processing step the agent performs for a single case. For each step, assign a model tier and justify the assignment in one sentence. This section makes the multi-model rationale explicit before the cost calculation.

| Step | Task description | Model tier | Rationale |
|------|-----------------|:---------:|-----------|
| 1 | [e.g., input validation / completeness check] | Haiku / Sonnet / Opus | [deterministic check → cheap; complex synthesis → mid/frontier] |
| … | | | |

**Model tier assignment rules (apply these explicitly):**
- **Haiku / cheap tier:** Deterministic checks, structured data lookups, rule application on structured inputs, template-based output formatting. No reasoning required — the right answer follows a formula.
- **Sonnet / mid tier:** Pattern-following with contextual adaptation, classification of unstructured inputs where the rules are known but the application requires judgment, ranking with explainable rationale.
- **Opus / frontier tier:** Only when no cheaper tier can produce a reliable output — multi-source synthesis under genuine ambiguity, high-stakes irreversible decisions with no HITL backstop. If you assign Opus to a step, explicitly state why Sonnet was insufficient.

**Anti-pattern to avoid:** Assigning mid- or frontier-tier to every step by default. A step that follows a deterministic rule on structured input does not need Sonnet. Identify at least one step that Haiku handles correctly, and at least one step where the cheaper model would produce worse output and why.

---

### 4. Token economics per case

#### 4a. Shared / cacheable context (system prompt)

List the components of the system prompt and estimate their token size. Mark each as cacheable or per-call.

| Component | Tokens | Cache strategy |
|-----------|-------:|---------------|
| [e.g., agent rules, output schema, domain logic] | [est.] | Cache read (written once, read N×/day) |
| … | | |
| **Total cacheable** | | |

State the cache hit rate (cases per day ÷ total calls — any session with ≥ 2 calls achieves a cache hit). State the cache read pricing used (typically 10× cheaper than standard input; verify against current provider pricing).

#### 4b. Per-case variable input tokens

| Component | Tokens | Notes |
|-----------|-------:|-------|
| [e.g., structured case data, retrieved context, prior conversation] | [est.] | |
| **Total per-case input** | | |

#### 4c. Output tokens per case

| Component | Tokens | Notes |
|-----------|-------:|-------|
| [e.g., reasoning output, structured action payload, user-facing text] | [est.] | |
| **Total per-case output** | | |

**Total tokens per case:**
- Without caching: system prompt + per-case input + output = [N] tokens
- With caching: per-case input + output + cache read = [N] tokens (effective)

#### 4d. Tool call costs

| Tool call | Purpose | Cost | Frequency |
|-----------|---------|:----:|-----------|
| [system read / DB query / write-back] | [what it does] | $[X] | Every case / N% of cases |
| **Total tool call cost** | | **$[X]/case** | |

Label all unit costs as assumptions if not contractually confirmed. Note whether tool call costs are material relative to token costs and HITL costs — if immaterial, say so explicitly.

#### 4e. Infrastructure cost

Allocate platform costs per case. Include compute, monitoring, storage, and maintenance. Show current-volume and target-volume figures separately if a growth target exists.

```
Monthly infrastructure cost (current volume): [$ — label as assumption]
Cases per month: [volume ÷ 12]
Infrastructure cost per case: [monthly ÷ cases]

Annual infrastructure (current volume): [calculated]
Annual infrastructure (target volume): [calculated — note whether this scales linearly or sub-linearly and why]
```

#### 4f. HITL cost per case

```
HITL rate: [% of cases requiring human review — derive from D2A breakpoints or D2B archetype assignments]
  Derivation: [state which specific breakpoints or archetype assignments drive this rate]

Time per HITL event:
  Clean case (coordinator reviews pre-built output and confirms): [X min]
  Complex case (coordinator reviews and applies judgment): [Y min]
  [If two distinct HITL paths exist in D2A, model both separately]

Reviewer hourly cost: [$X/hr]

Weighted HITL cost per case:
  = (% complex × complex_time/60 × hourly_rate) + (% clean × clean_time/60 × hourly_rate)
  = [calculated]
```

---

### 5. Multi-model comparison

Evaluate at minimum three architecture options. For each, compute the per-case cost in full.

| | Option A: [cheap-only] | Option B: [blended — recommended] | Option C: [mid-tier-only] |
|---|:-:|:-:|:-:|
| Token cost per case | $[X] | $[X] | $[X] |
| Tool call cost | $[X] | $[X] | $[X] |
| Expected HITL rate | [%] | [%] | [%] |
| HITL cost per case | $[X] | $[X] | $[X] |
| Infrastructure cost per case | $[X] | $[X] | $[X] |
| **Total agent cost per case** | **$[X]** | **$[X]** | **$[X]** |
| vs. baseline ($[Z]) | -[N]% | -[N]% | -[N]% |

Below the table, write one paragraph stating:
1. Which option is recommended and why
2. Whether the model tier decision is driven by token cost or HITL rate — state which is the larger variable and by what multiple
3. The threshold condition: at what HITL rate would the cheapest model become the optimal choice?

**Required finding:** Token cost is typically not the dominant variable — HITL cost is. If your numbers show otherwise, state why this case is an exception.

---

### 6. Total agent cost per case (recommended option)

```
Token cost per case:        $[X]
Tool call cost per case:    $[X]
Infrastructure per case:    $[X]
HITL cost per case:         $[X]
Total agent cost per case:  $[X]

vs. Baseline: $[Z] per case → [N]% reduction
```

---

### 7. Business case — current volume

```
Annual volume (current): [cases/year — derive from scenario]
Annual baseline cost:    cases × baseline_cost_per_case = $[X]
Annual agent cost:       cases × agent_cost_per_case = $[X]
Annual infrastructure:   $[X]
Total annual cost (agent + infra): $[X]
Annual saving:           annual_baseline - total_annual_agent_cost = $[X]

Build cost:
  [Itemise: discovery + design, development, integration, testing, change management]
  Total build cost: $[X] [label as assumption]
```

**Build cost estimation methodology (required):** The scenario contains no build cost data. Every line item must be sized by an explicit estimation basis — typically FTE-week estimate × blended services rate ($150–250/hr for enterprise IT: architects at the higher end, developers mid-range, trainers lower). For each line, include a one-line note showing the implicit derivation (e.g., *"ServiceNow integration: ~4 developer weeks × $200/hr + platform licensing overhead"*). Do not state a single-line total without this decomposition.

After the itemisation, include the following three cross-checks:

1. **Industry range:** State whether the total falls within the typical range for comparable projects in this domain (e.g., healthcare data integration: $500K–$2M). If the estimate sits outside the range, explain why.
2. **Sensitivity validation:** Verify that the business case survives at 2× build cost (see §10 sensitivity). If it does not, flag that build cost is load-bearing and requires early scope control before commitment.
3. **Wave attribution:** If any component properly belongs to a different wave's budget (e.g., a prerequisite use case that is Wave 1 but costed here as a WS dependency), name the component, its attributed wave, and state both the standalone cost (without the prerequisite) and the full dependency-stack cost. This prevents double-counting in the compounding roadmap.

```
Payback period:          build_cost ÷ annual_saving = [X months/years]

Year-by-year net (cumulative):
  Year 1: annual_saving - build_cost = $[X]
  Year 2: [cumulative]
  Year 3: [cumulative]

3-year ROI:  ((annual_saving × 3) - build_cost) ÷ build_cost × 100 = [X]%
```

**Verdict:** state in one sentence whether the current-volume economics are compelling, marginal, or weak — and what condition changes the verdict.

---

### 8. Business case — target / scale volume (include if the scenario names a growth target)

If the scenario states a revenue or volume growth target, model the economics at that target volume. Show:

```
Target case volume:           [derived from growth target × current volume]
Human-only cost at target:    coordinators required × loaded annual cost = $[X]
  Coordinator headcount:      [target_cases/year × time_per_case ÷ working_hours/year]

Agent cost at target volume:  agent_cost_per_case × target_cases = $[X]
Infrastructure at scale:      $[X/year]
Total annual agent cost:      $[X]

Annual saving (target):       human_only - agent_cost = $[X]
Payback period (target):      build_cost ÷ annual_saving = [X weeks/months]
3-year ROI (target):          [X]%
```

State the single assumption the scale-economics case rests on, and what happens to the business case if that assumption is wrong.

If the scenario does not name a growth target, omit §8 and note the omission.

---

### 9. Self-financing roadmap

Structure the use case sequence so early ROI funds subsequent waves. This section makes the compounding thesis concrete — it is not a list of waves, it is an argument that each wave is economically self-sustaining and reduces the cost of the next.

**Wave structure:**

For each wave, produce a block in this format:

```
Wave [N] — [months X–Y from engagement start]

Use cases in this wave:
  [Use case name]: build cost $[X], annual saving $[Y], payback [Z months]
  [Use case name]: build cost $[X], annual saving $[Y], payback [Z months]

Wave [N] cumulative saving by month [end of first year]: $[sum]

Platform assets built in this wave (reused in Wave N+1):
  - [Integration or component name]: saves an estimated $[X] in Wave [N+1] build cost
  - [Integration or component name]: [saving or reuse benefit]
  Estimated Wave [N+1] build cost reduction from reuse: $[sum]

Funded by: [Wave N-1 savings / initial investment / client budget — state the source]
```

**Required:**
- Wave 1 must be self-funding: payback ≤ 12 months on Wave 1 use cases. If Wave 1 does not pay back within 12 months, state why and what the client's risk exposure is.
- Each wave after Wave 1 must name at least two platform assets it inherits from the prior wave and estimate the build cost reduction those assets create.
- If your scenario has only one primary agentic target, include at least the prerequisite use cases (e.g., the intake agent that must precede the matching agent) as distinct wave entries.

**Cumulative 3-year picture:**

```
Total investment (all waves): $[sum of build costs]
Total saving (3 years):       $[annual saving × 3, summed across waves with appropriate phasing]
Net 3-year value:             $[total saving - total investment]
Portfolio ROI:                [net value ÷ total investment × 100]%
```

**Compounding logic (required paragraph):** After completing the wave blocks, write 2–3 sentences naming the specific platform assets — by name, not by category — that make the roadmap self-financing. Explain which integration or component built in Wave 1 is the one that most reduces Wave 2 marginal cost, and by how much.

---

### 10. Sensitivity analysis

Model three scenarios across the variables that most affect the business case. Always include HITL rate and build cost as two of the variables — those are the dominant uncertainties in almost every agentic case. Add a third variable specific to your scenario.

| Variable | Conservative | Base case | Optimistic |
|----------|:-:|:-:|:-:|
| HITL rate | [+10pp vs base] | [base] | [-10pp vs base] |
| Build cost | [2× base] | [base] | [0.67× base] |
| [Scenario-specific variable — e.g., volume growth, coordinator rate, token price] | | | |

**Sensitivity table — annual saving and payback period (at the volume scenario that is most decision-relevant):**

| Scenario | Annual saving | Payback period |
|----------|:-:|:-:|
| Conservative | $[X] | [X months] |
| Base case | $[X] | [X months] |
| Optimistic | $[X] | [X months] |

Below the table, state: does the business case hold in the conservative scenario? If payback > 18 months in the conservative scenario, identify which assumption is load-bearing and what condition would need to be true to keep the business case viable.

**Token price sensitivity:** Always model ±50% token price change. State whether this changes the recommendation — in most cases it will not, because HITL cost dominates. If token price sensitivity is not material, say so in one sentence and move on. Do not spend analysis on an immaterial variable.

---

### 11. Calibration targets

These are the operating-point thresholds the agent must hit in mock testing before production release. If any target is missed, state what the business case impact is.

| Metric | Target | Business case impact if missed |
|--------|--------|-------------------------------|
| [e.g., task accuracy / shortlist precision] | [≥ X%] | [HITL rate rises → cost per case increases] |
| [HITL rate] | [≤ X%] | [If exceeded by Y pp, annual saving drops by $Z] |
| [Tokens per case] | [≤ N tokens] | [Cost per case rises by $X; state at what multiple this becomes material] |
| [Latency per case] | [≤ N seconds] | [User experience threshold; adoption risk] |
| [Compliance gate] | [0 violations] | [Regulatory or patient safety event; agent paused] |

---

### 12. Assumption log

Use this format for every non-trivial claim not directly stated in the scenario:

> **[A-N] [short name]:** [what is being taken as given]
> **Why it matters:** [which cost component or ROI figure it drives — quantify if possible]
> **If wrong:** [what the business case impact is — directional or calculated]
> **Confidence:** low / medium / high

Required minimum assumptions:
- Fully loaded hourly cost for the human worker performing this task
- Annual working days or hours (base for volume calculation)
- Build cost estimate
- HITL rate per model tier option
- Clean vs. complex case review time split
- Infrastructure cost scaling factor

---

## Acceptance criteria (all must pass)

- [ ] Executive summary covers: target + volume, model tier finding, stress-tested payback period — in three sentences
- [ ] Baseline cost arithmetic is shown and every non-scenario figure is labelled as an assumption
- [ ] Per-step model selection table is present; at minimum one step is assigned cheap tier with justification and at minimum one step is assigned mid/frontier tier with justification
- [ ] Three model-tier options are evaluated (cheap-only, blended, mid-tier-only minimum); each has a fully calculated per-case cost
- [ ] The comparison table explicitly states whether the token cost or the HITL cost is the dominant variable
- [ ] Business case at current volume is fully calculated (saving, build cost, payback, 3-year ROI)
- [ ] Sensitivity analysis covers HITL rate, build cost, and at least one scenario-specific variable; conservative scenario payback period is stated
- [ ] Sensitivity analysis conclusion states whether the business case holds under conservative assumptions — not just whether numbers changed
- [ ] Token price sensitivity is addressed and its materiality (or immateriality) is stated explicitly
- [ ] Self-financing roadmap is present with at least two waves; each wave names its use cases with build cost + annual saving + payback, and names the platform assets it creates for the next wave with an estimated build cost reduction
- [ ] Wave 1 payback is ≤ 12 months, or a deviation is explicitly stated and the client risk exposure is named
- [ ] Compounding logic paragraph names specific shared assets — not category labels — and states the build cost reduction they produce
- [ ] Cumulative 3-year picture is present with total investment, total saving, net value, and portfolio ROI
- [ ] Calibration targets are present with stated business case impact for each missed target
- [ ] Assumption log is present with confidence levels; all listed assumptions appear in the body of the document where the relevant number is used
- [ ] Every claimed HITL rate traces to D2A breakpoints, D2B archetype assignments, or a scenario-stated figure — not assumed without derivation

## Fail signals — do not produce output that contains these

- Token cost presented as the dominant cost component without checking whether HITL cost is larger
- All processing steps assigned to the same model tier (typically Sonnet or Opus throughout) without evaluating whether cheaper tiers are sufficient for deterministic steps
- Sensitivity analysis that only models optimistic or base-case scenarios — conservative scenario is required
- Build cost stated as a single number with no itemisation, no confidence label, and no estimation methodology — each line must show how it was derived (FTE-week basis or comparable project benchmark) and include the three cross-checks: industry range, 2× sensitivity validation, and wave attribution for any prerequisite components
- HITL rate stated as a percentage with no derivation — it must trace to D2A breakpoints or D2B archetype assignments, not be pulled from air
- Sensitivity analysis conclusion that only says "the numbers change" — it must state whether the business case still holds and what the conservative payback period is
- Multi-model comparison that omits the HITL rate impact of each model option — if a better model reduces the HITL rate, that saving must be quantified and compared to the token cost premium
- Self-financing roadmap that lists waves without naming platform assets — "we will build integrations" is not a compounding argument; name the specific integration, which future agent reuses it, and what it saves
- Wave 1 that takes longer than 12 months to pay back without stating the client's risk exposure or the condition that justifies the longer horizon
- Cumulative 3-year picture omitted or stated only directionally ("the business case is strong") without a calculated portfolio ROI
- Assumptions embedded in prose without appearing in the assumption log
- Volume numbers that do not trace to the scenario and are not labelled as assumptions
- Infrastructure cost set to zero or omitted entirely — even a preliminary estimate must be shown
