# Prompt: Gate 4 Deliverable 2 — Compounding Roadmap

## Inputs (read all of these before producing any output)

1. **Token economics model** — `Deliverables/C1_token_economics_model.md`. Source of truth for build costs, annual savings per use case, and ROI figures. Do not recompute; reference D1 figures directly.
2. **Volume × value analysis** — `Deliverables/D2C_volume_value_analysis.md` (or equivalent). Source of wave assignments and volume figures for each use case.
3. **Solution architecture** — `Deliverables/D3_solution_architecture.md` (or equivalent). Source of agent design, platform assets, and integration dependencies.
4. **Capability specs** — `Deliverables/D4a_capability_spec.md` and `Deliverables/D4b_capability_spec.md` (or equivalent). Source of integration requirements that drive platform asset definitions.
5. **Scenario** — `Scenario/scenario.md`. Source of all factual client figures (volume, staff counts, current costs, stated problems). Any figure not in the scenario must be labelled as an assumption.

---

## Core concept: what a compounding roadmap is

A compounding roadmap is not a deployment schedule. It is an argument that:

1. **Wave sequencing is causal, not arbitrary.** Each wave must deploy in the order shown because later waves have hard prerequisites that earlier waves create. The roadmap must name those prerequisites explicitly — not assert ordering by convenience.

2. **Platform assets reduce the marginal cost of each subsequent wave.** Every integration, pipeline, and governance component built in an earlier wave can be reused rather than rebuilt in later waves. The roadmap quantifies this reuse as avoided build cost (standalone cost − actual cost with reuse).

3. **Trust capital is a non-financial platform asset.** Human adoption of agent outputs is a prerequisite for autonomous operation. If coordinators have never interacted with agent-generated outputs before Wave 2 deploys, the adoption sprint for Wave 2 starts from zero trust. Each wave of HITL operation shortens subsequent adoption cycles and must be counted as a compounding asset even though it has no direct financial expression.

The anti-pattern to avoid: treating waves as independent projects with independent business cases. A wave whose standalone ROI is marginal may be essential as a prerequisite for the next wave. The roadmap must show both the standalone and the programme-level view.

---

## Platform asset taxonomy

Use this four-category taxonomy to classify every asset. Do not invent new categories.

| Category | Definition |
|----------|-----------|
| **System integrations** | API connectors to external systems (CRM, databases, notification gateways). Costs $30–80K to build and test; reuse eliminates the integration sprint from every subsequent agent. |
| **Data and retrieval pipelines** | NLP pipelines, domain vocabularies, feature stores, preference profile stores. LLM prompts calibrated on client-specific terminology work across all agents that process similar text — reuse is a retune, not a rebuild. |
| **Governance infrastructure** | HITL queue, coordinator review interface, audit logging, compliance dashboard. Built once for the first HITL use case; extended (not rebuilt) for each subsequent use case. |
| **Inference infrastructure** | Model router, prompt caching configuration, calibrated prompt templates, latency baselines. Optimised once; reused across all agents in the programme. |

---

## Your task

Produce a compounding roadmap for the client engagement. The roadmap must:

- Justify wave sequencing with explicit prerequisite logic — not just a timeline
- Show standalone build cost and actual build cost (after reuse) for each wave after Wave 1
- Quantify the compounding mechanisms in money: what would each wave cost if deployed standalone, and what does platform asset reuse actually save
- Present three volume scenarios (conservative / base / target) for the Year 2 and Year 3 financial picture
- Tag every claim not directly sourced from the scenario as an assumption with confidence level and failure consequence

---

## Required output structure

### 0. Executive Summary

Three bullets:
- Wave 1: cost, payback months, combined annual saving, and what platform assets it creates that fund Wave 2
- Wave 2: cost, payback at current volume vs. target volume, and the reuse discount vs. standalone
- Wave 3: cost, what Wave 2 data it consumes to unlock, and additional annual saving

Close with: total investment, 3-year net value (base case), and portfolio ROI.

---

### 1. Engagement context — why a roadmap, not a single deployment

State the structural reason the highest-value use case cannot deploy at week 0. Name the specific prerequisites that Wave 1 must create before Wave 2 can produce reliable outputs. This section must be specific to the engagement — not generic platform rationale.

---

### 2. Platform asset taxonomy

Brief table explaining the four asset categories and why assets in each category compound across waves.

---

### 3. Wave 1 — Foundation layer

#### 3a. Use case 1 (first to deploy)

- What it deploys (specific JtDs or task clusters)
- Why first (organisational readiness, adoption risk, prerequisite role)
- Build cost breakdown: itemised table with component, cost, and notes
- Platform assets created: table with Asset ID, name, and reuse flags per subsequent wave
- Annual saving: calculation with explicit assumption labels for any figure not from the scenario

#### 3b. Use case 2 (parallel deployment if applicable)

Same structure as 3a. If parallel: state why parallel deployment is valid (no dependency between 3a and 3b) and what the prerequisite role of 3b is for Wave 2.

#### 3c. Wave 1 combined financials

```
Wave 1 total investment: [sum]
Wave 1 combined annual saving: [sum]
Wave 1 blended payback: [months]

Wave 1 cumulative saving by month 12:
  [Use case 1] (months go-live to month 12): ...
  [Use case 2] (months go-live to month 12): ...
  Total: ...

Wave 1 savings cover Wave 2 build: [how much of Wave 2 build cost is funded by Wave 1 savings]
Client net cash position at month 12: [Wave 1 investment] + [Wave 1 savings by month 12]
```

---

### 4. Wave 2 — Capacity unlock

#### 4a. What it deploys
Specific use cases, JtDs, and autonomy level at launch (HITL-first vs. autonomous). Name any JtDs that remain human-only and why.

#### 4b. Build cost: standalone vs. actual

Two tables:
1. Standalone cost: what this wave would cost with no prior platform assets
2. Reuse saving: each Wave 1 asset reused, avoided cost per asset, total saving

State the actual build cost: `standalone − reuse saving`.

#### 4c. Platform assets created
Table: Asset ID, name, category, which subsequent waves reuse it.

#### 4d. Wave 2 financials

```
Build cost: [actual, after reuse saving] vs. [standalone]
Annual saving at current volume: [from D1]
Annual saving at target volume: [from D1]
Payback at current volume: [months]
Payback at target volume: [days/weeks]
Year-by-year net (base case): [Year 1 partial, Year 2, Year 3]
```

---

### 5. Wave 3 — Compounding operations

Wave 3 does not deploy new agents. It converts the operational data and trust accumulated in earlier waves into expanded autonomous capability and infrastructure efficiency. Structure as named mechanisms:

For each mechanism:
- What blocker it resolves (name the specific unresolved item from the architecture or delegation matrix)
- How earlier waves create the data or trust it requires
- What it builds (specific components with itemised costs)
- Annual saving impact

Close with: Wave 3 total build cost, total additional annual saving, payback.

---

### 6. Integration reuse matrix

Full matrix: every platform asset across all waves, with:
- Asset ID and name
- Category (from taxonomy)
- Wave built
- Waves that reuse it
- Avoided build cost per reuse instance

Total row: programme reuse saving vs. theoretical standalone total.

---

### 7. Compounding cost reduction mechanisms

Name and quantify the three to four primary mechanisms. For each:
- Mechanism name (e.g., integration reuse, NLP pipeline reuse, trust capital)
- How it works
- Quantified saving across the programme

---

### 8. 3-year financial picture

#### 8a. Deployment timeline

Table: Month → Event. Include:
- Build start dates for each wave and use case
- Any early demo or prototype milestone (with explicit note if mock data only and production financials unaffected)
- Go-live dates
- Savings start dates
- Wave 3 build and go-live

#### 8b. Annual savings by wave and volume scenario

Three scenarios × three years. For Year 2 and Year 3, show rows per wave/use case and year totals. Include:
- Conservative (low volume growth multiplier)
- Base case (medium multiplier)
- Target (maximum stated multiplier)

State the volume multipliers being used and label them as assumptions if not confirmed.

#### 8c. Cumulative 3-year picture

| | Conservative | Base case | Target |
|---|:-:|:-:|:-:|
| Total investment | | | |
| Total saving | | | |
| Net 3-year value | | | |
| Portfolio ROI | | | |
| Fully invested payback | | | |

---

### 9. Assumption log

Every assumption used in financial calculations, in this format:

> **[A-code]** [What is being assumed]
> **Why it matters:** [Which calculation it drives; magnitude of impact if wrong]
> **If wrong:** [What changes; whether the business case remains viable]
> **Confidence:** Low / Medium / High

Flag: any assumption with low confidence that would break the business case if wrong must be called out in the Executive Summary.

---

## Calculation standards

- **Payback threshold**: ≤12 months for any individual wave to be recommended without qualification; waves with >12-month standalone payback must justify via programme-level dependency
- **Volume scenarios**: conservative = 2–3× peak volume; base = 5–7× peak volume; target = stated client goal (e.g., 10–14×)
- **Annual saving formula**: (labour time displaced per case) × (labour cost per hour ÷ 60) × (cases per year at scenario volume) − (agent operating cost)
- **Standalone vs. actual**: standalone = cost if wave deployed with no prior platform assets; actual = standalone − confirmed reuse savings from earlier waves
- All figures in USD; round to nearest $1,000 for components, nearest $1 for per-case unit economics
