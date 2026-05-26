# Prompt: Client Proposal — Agentic Claims Transformation

**Output files (produce both):**
- `Deliverables/client_proposal.md` — the proposal in Markdown
- `Deliverables/client_proposal.html` — the same content as a self-contained HTML document (see §HTML spec below)

---

## Read all inputs before writing

Read every file listed below in full before producing a single word of output. Do not produce output that is inconsistent with any of these inputs. Every factual claim in the proposal must be traceable to one of these sources — if it is not, label it as an assumption with a confidence level.

| File | What to pull from it |
|------|---------------------|
| `Scenario/scenario_context.md` | Source of truth — volumes, stakeholders, systems, constraints, all named numbers |
| `Deliverables/C1_problem_framing.md` | Problem statement narrative (§2a, §2b), why-agent-not-RPA argument (§3), per-stakeholder success definition (§4) |
| `Deliverables/D2A_cognitive_load_map.md` | WS1 and WS2 process topology Mermaid diagrams (§2e, §3e), micro-task inventory, zone and breakpoint names |
| `Deliverables/D2B_delegation_suitability_matrix.md` | Delegation archetypes per JtD, dimension scores, governance constraints |
| `Deliverables/D2C_volume_value_analysis.md` | Volume × Value quadrant Mermaid chart (§4), wave sequencing (§10), work stream descriptions and volumes |
| `Deliverables/C1_token_economics_model.md` | All financial figures — per-claim cost, annual saving, payback, HITL rate, agent running cost, wave economics; §3 model selection table (RPA vs LLM vs HITL classification per step) |
| `Deliverables/C3_agentic_solution_architecture.md` | Agent purpose blocks (§2), workflow-to-agent mapping table (§1), autonomy matrix (§3), AI-native moment |
| `Deliverables/Gate4_D6_capstone_proposal.md` | Success metrics table (§2), routing logic, HITL queue design |

**Prohibition:** Do not invent numbers, system names, stakeholder names, timelines, or constraint details not present in these sources. If the scenario is silent on a point, say so explicitly in the proposal and label it as an assumption.

---

## Audience and tone

**Audience:** Sarah Chen (CFO), Dr. Marcus Webb (CMO), James Liu (VP Operations). These are the three stakeholders named in the scenario. The proposal is addressed to them collectively.

**Tone rules:**
- Executive-level: each paragraph earns its place. No filler, no caveats that do not change a decision, no section that merely restates the work.
- Evidence-based: every claim has a number or a source. Generic statements ("AI will improve efficiency") are not permitted.
- Plainspoken: no ATX methodology jargon in any client-facing section. "Delegation archetype," "non-deterministic," "cognitive load," "ATX," "JtD" must not appear. Use plain equivalents: "decision the agent makes alone," "judgment call," "tasks the agent handles vs. tasks physicians must own."
- Stakeholder-specific: where a section is directly relevant to one stakeholder's concern, name that concern. Sarah Chen cares about cost and payback. Dr. Webb cares about physician sign-off and compliance. James Liu cares about cycle time and queue management.
- No apology: non-agentic residual is not a failure. Where humans remain in the loop, the proposal must explain why that boundary is the right design, not an apology for a limitation.

---

## Required structure and content

### Section 0: Cover

One paragraph, no bullet points.

State: the client name, the engagement scope (medical claims adjudication), the date (2026-05-21), and a one-sentence framing of what this document proposes. Do not summarise the proposal on the cover — the executive summary does that.

---

### Section 1: Executive Summary

**Format:** Three paragraphs, no headers, no bullets. Each paragraph is one tight argument.

**Paragraph 1 — The problem:**
State the business problem in terms of the three metrics that make it undeniable: auto-adjudication rate (22% vs. 85% industry benchmark), cycle time (8–9 days vs. 7-day SLA threshold with active penalties), and denial appeal overturn rate (41%). Do not list symptoms — explain the single structural cause: the absence of a clinical content classifier means every claim receives full manual adjudication regardless of complexity. Source: C1_problem_framing §2b and scenario_context.md.

**Paragraph 2 — The solution:**
Describe the proposed system at the executive level: a four-component agentic pipeline (intake normalisation, administrative adjudication, clinical pre-screening, appeals support) deployed in three waves. State the delegation boundary clearly: 65% of claims on a fully automated administrative path, 35% to a physician HITL queue but with agent pre-filling reducing physician time from 35 min to 3 min per claim. Source: D2C §10, C3 §1, Gate4_D6 §3.

**Paragraph 3 — The case:**
State the business case in one paragraph: per-claim cost reduction ($18.23 → $0.315, 98.3%), annual cash saving ($732K/year against current $1.3M workforce), payback period (6.9 months), and the compliance non-negotiable (physician sign-off on all clinical claims preserved by design, not by policy). Source: C1_token_economics §6, §7.

---

### Section 2: Table of Contents

Auto-generate after the full document is written. Markdown anchor links. Exact section title matches.

---

### Section 3: Problem Statement

**3.1 — What we heard**

Three short named blocks — one per stakeholder. Each block: the stakeholder's name and role, the specific concern they raised (with source — Exchange 1, 2, or 3), and the metric that makes the concern concrete. Do not invent concerns not stated in the scenario.

**3.2 — What is broken**

Reproduce the two root cause diagnoses from C1_problem_framing §2b as a numbered list. Each item: the broken element, the symptom it produces (with numbers), why it persists, and what fixing it unlocks. Use the exact framing from C1_problem_framing — these were written for this engagement.

**3.3 — Why automation, not process change or hiring**

A three-item table:

| Alternative considered | What it addresses | Why it doesn't close the gap |
|------------------------|-------------------|------------------------------|

Use the three alternatives from C1_problem_framing §3: RPA/rules engine, workflow tool, hiring. Do not dismiss them as "not AI" — explain specifically what each can and cannot do in the context of Greenfield's two root causes. The agent case is strongest when the alternatives are taken seriously.

---

### Section 4: Stakeholder Map

A table with four columns: **Stakeholder | Role | Primary concern | What success looks like for them**

Row for each of: Sarah Chen (CFO), Dr. Marcus Webb (CMO), James Liu (VP Operations), and one row for "Claims processors and clinical reviewers" as the operational population affected. Source: scenario_context.md, C1_problem_framing §4, scenario_enriched.md exchanges.

Below the table: one paragraph identifying the key tension that the solution must resolve — the CFO's cost reduction requirement in direct tension with the CMO's physician sign-off requirement — and how the negotiated 65%/35% routing split (Exchange 3) resolved it. Frame this as a design decision that was already made by the stakeholders, not one that the proposal is making.

---

### Section 5: Proposed Solution

#### 5.1 — Scope, out-of-scope, constraints, and risks

**In scope (this engagement):**
- A bulleted list of what is included across all waves and components. Be specific — name the work streams and the agent functions. Source: D2C §10, C3 §1.

**Out of scope:**
- A bulleted list. Each item must name the reason it is out of scope — cost, compliance boundary, prerequisite gap, or phasing decision. Do not list things as out of scope without a reason.

**Constraints:**
A numbered list. Each constraint: what it is, where it comes from (stakeholder, regulation, or system), and what it means for the design. Include:
1. Budget: $400K Wave 1 commitment (Sarah Chen, Exchange 1)
2. Compliance: Physician sign-off on all clinical claims required by URAC/NCQA accreditation (Dr. Marcus Webb, Exchange 2)
3. Clinical content definition: undefined in current process — must be produced as a design output before classifier build (scenario_context.md, Exchange 3)
4. Any system integration constraints named in scenario_context.md or flagged in C3 §6

**Risks:**
A table with three columns: **Risk | Likelihood | Mitigation already designed**

Include exactly four risks:
1. Clinical content classifier confidence threshold — the single dial that controls both compliance exposure and HITL queue size (source: C3 §0 bullet 3, C1_token_economics §11)
2. Build cost overrun — at 2× build, payback extends from 6.9 to ~14 months (source: C1_token_economics §10)
3. Clinical notes integration feasibility — unconfirmed source system is a Wave 2 hard blocker (source: C3 §5 WS2-JtD-2, D2C pre-screen)
4. HITL rate exceeding calibration target — HITL rate is the primary quality signal for production readiness (source: C1_token_economics §11)

---

#### 5.2 — The four work streams

**Format for each work stream:** A short heading block followed by a three-bullet description. Do not use technical architecture language — describe what each work stream does, not how the agent works internally.

Work stream order: INT (Intake), WS1 (Administrative Adjudication), WS2 (Clinical Review), APP (Denial Appeals). After the four descriptions, embed the Volume × Value quadrant.

**Volume × Value quadrant:**
Copy the Mermaid `quadrantChart` exactly from D2C §4. Label the quadrants with business-plain labels:
- Quadrant 1 (high volume, high judgment): "Primary targets — automate now"
- Quadrant 2 (high volume, low judgment): "Rules and automation"
- Quadrant 3 (low volume, low judgment): "Not worth automating"
- Quadrant 4 (low volume, high judgment): "Selected use cases"

Add one sentence below the chart identifying WS1 as the Wave 1 primary target and explaining why WS2, despite scoring highest on judgment, cannot be the primary target (URAC/NCQA compliance constraint limits agent scope to context assembly only).

---

#### 5.3 — Delivery waves

A three-wave table. For each wave:

| Wave | Scope | Timeline | Agent components activated | Annual saving (incremental) | What this wave funds |

Pull exact numbers from C1_token_economics §9. Use the Wave 1/2/3 structure as defined there.

Below the table: one paragraph on the compounding logic — explain how Wave 1 assets (clinical content classifier, eligibility API integration, prior auth integration) reduce Wave 2 build cost and eliminate the CMO re-certification process. Source: C1_token_economics §9 compounding logic paragraph.

---

#### 5.4 — Key assumptions

A table with four columns: **Assumption | Source | Why it matters | If wrong**

Include these five assumptions (pull exact text from C1_token_economics §12 and C3 §6):
1. 65%/35% administrative/clinical routing split is a stakeholder estimate, not a measured baseline
2. Clinical content definition does not yet exist — must be produced as a design output
3. All system integrations (eligibility, prior auth, fee schedule) are available as APIs — unconfirmed
4. 25% HITL rate at 2-minute average review time — the economic model's primary calibration commitment
5. $65K fully loaded cost per reviewer — the FTE baseline the business case rests on

---

### Section 6: Business Case

#### 6.1 — Per-claim economics

A two-row comparison table: **Current state vs. With agent**

| Metric | Current state | With agent | Change |
|--------|:---:|:---:|:---:|
| Cost per admin claim | $18.23 | $0.315 | −98.3% |
| Claims/day (admin path) | ~274 processable | 1,300 | 5.7× throughput |
| FTE equivalent for WS1 HITL | 20 staff (all tasks) | 7 retained + 1.4 HITL | 12 displaced |
| Cycle time — admin path | 8–9 days | 4–5 days | target |
| Cycle time — clinical path | 8–9 days | 6–7 days | target |

Source: C1_token_economics §2, §6, §7.

#### 6.2 — Annual economics (all waves)

A three-section block:

**Wave 1 (WS1 + INT):**
- Agent running cost: $113K/year (token, tool call, infrastructure, HITL labour — 2 min average)
- Retained staff: 7 FTEs × $65K = $455K/year
- Total post-automation: $568K/year
- vs. Current workforce: $1.3M/year
- Annual cash saving: $732K/year
- Build cost: $420K (Wave 1)
- Payback: 6.9 months

**Wave 2 (WS2 Clinical Pre-screening, incremental):**
- Incremental build cost: $108K (with Wave 1 reuse)
- Annual saving: $104K/year (net of agent running cost)
- Payback: 12.5 months

**Wave 3 (APP Denial Appeals, conditional):**
- Conditioned on WS1 steady-state quality data (90 days post-go-live)
- Estimated build cost: $150K
- Annual saving: dependent on residual appeal volume after WS1 quality improvement

**3-year portfolio summary:**
| | |
|---|---|
| Total investment (Waves 1+2) | $528K |
| Total 3-year saving (Waves 1+2) | $1,986K |
| Net 3-year value | $1,458K |
| Portfolio ROI | 276% |

Source: C1_token_economics §9.

#### 6.3 — Sensitivity

A compact version of the sensitivity table from C1_token_economics §10. Include only four rows:
- All adverse (35% HITL, 2× build, $55K FTE): ~$586K saving, ~17-month payback
- Conservative HITL only (35%): ~$697K saving, ~7.2-month payback
- **Base case: $732K saving, 6.9-month payback**
- All optimistic (15% HITL, 0.67× build, $75K FTE): ~$892K saving, ~3.8-month payback

One sentence below: "The business case holds under all tested adverse scenarios; the primary financial risk is build cost overrun, not HITL rate fluctuation."

---

#### 6.4 — Break-even timeline

Produce a chart with:
- **X axis:** Time in months from project start (0 → 24)
- **Y axis:** Cumulative amount in $K (0 → 1,100)
- **Line 1 — Cumulative Investment** (what has been spent): rises linearly during the 6-month build phase, then flattens
- **Line 2 — Cumulative Net Saving** (cash returned after all post-automation costs): zero during build, then rises at $61K/month from month 7 onward
- **Annotation:** Mark the break-even crossing clearly (month ~13)

**Pre-calculated data (use these exact figures — do not recalculate):**

Build phase assumption: $420K build cost spread evenly over 6 months = $70K/month. Net monthly saving after go-live: $732K ÷ 12 = $61K/month. This figure is taken directly from C1_token_economics §7 — it already nets out agent running cost ($113K/year) and retained staff ($455K/year) against the current $1.3M workforce, so no further adjustments are needed.

| Month | Cumulative Investment ($K) | Cumulative Net Saving ($K) |
|-------|:---:|:---:|
| 0 | 0 | 0 |
| 2 | 140 | 0 |
| 4 | 280 | 0 |
| 6 | 420 | 0 ← Go-live |
| 8 | 420 | 122 |
| 10 | 420 | 244 |
| 12 | 420 | 366 |
| **13** | **420** | **427** ← **Break-even (lines cross)** |
| 14 | 420 | 488 |
| 16 | 420 | 610 |
| 18 | 420 | 732 (1 year of saving) |
| 20 | 420 | 854 |
| 22 | 420 | 976 |
| 24 | 420 | 1,098 |

**In the Markdown file (`client_proposal.md`):**

Produce this Mermaid `xychart-beta` chart using the data above:

```
xychart-beta
    title "Cumulative Investment vs. Net Saving — Wave 1 (Base Case)"
    x-axis "Month from project start" [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
    y-axis "Cumulative Amount ($K)" 0 --> 1100
    line "Cumulative Investment ($K)" [0, 140, 280, 420, 420, 420, 420, 420, 420, 420, 420, 420, 420]
    line "Cumulative Net Saving ($K)"  [0, 0, 0, 0, 122, 244, 366, 488, 610, 732, 854, 976, 1098]
```

Below the Mermaid chart in the Markdown file, add this note as a blockquote:

> **Reading this chart:** The blue line (investment) rises during the 6-month build phase and flattens at $420K at go-live. The green line (net saving) begins at go-live and rises at $61K/month. The lines cross at approximately month 13 — the break-even point. Every month beyond month 13, the programme is in net positive territory. At month 24, cumulative net saving is $1,098K against a total investment of $420K.

**In the HTML file (`client_proposal.html`):**

Replace the Mermaid chart with a `<canvas>` element rendered by inline JavaScript (no external charting library — the Mermaid CDN is already the only permitted external reference, and this chart benefits from precise annotation that Mermaid cannot provide). Implement it as follows:

```html
<canvas id="breakEvenChart" width="860" height="400"
        style="max-width:100%; display:block; margin:0 auto;"></canvas>

<script>
(function() {
  const canvas = document.getElementById('breakEvenChart');
  const ctx = canvas.getContext('2d');

  // Data: [month, investment_$K, saving_$K]
  const data = [
    [0,0,0],[2,140,0],[4,280,0],[6,420,0],
    [8,420,122],[10,420,244],[12,420,366],
    [13,420,427],[14,420,488],[16,420,610],
    [18,420,732],[20,420,854],[22,420,976],[24,420,1098]
  ];

  // Layout constants
  const PAD = { top: 40, right: 60, bottom: 60, left: 80 };
  const W = canvas.width - PAD.left - PAD.right;
  const H = canvas.height - PAD.top - PAD.bottom;
  const X_MAX = 24, Y_MAX = 1100;

  function px(month) { return PAD.left + (month / X_MAX) * W; }
  function py(val)   { return PAD.top  + H - (val   / Y_MAX) * H; }

  // --- Shaded build phase (months 0–6) ---
  ctx.fillStyle = 'rgba(160,92,0,0.07)';
  ctx.fillRect(px(0), PAD.top, px(6) - px(0), H);

  // --- Axes ---
  ctx.strokeStyle = '#dde3ea';
  ctx.lineWidth = 1;
  // Y gridlines
  [0, 200, 400, 600, 800, 1000].forEach(v => {
    ctx.beginPath();
    ctx.moveTo(PAD.left, py(v));
    ctx.lineTo(PAD.left + W, py(v));
    ctx.stroke();
  });

  ctx.strokeStyle = '#aab';
  ctx.lineWidth = 1;
  // X axis
  ctx.beginPath(); ctx.moveTo(PAD.left, PAD.top + H); ctx.lineTo(PAD.left + W, PAD.top + H); ctx.stroke();
  // Y axis
  ctx.beginPath(); ctx.moveTo(PAD.left, PAD.top); ctx.lineTo(PAD.left, PAD.top + H); ctx.stroke();

  // Axis labels
  ctx.fillStyle = '#555';
  ctx.font = '12px -apple-system, sans-serif';
  ctx.textAlign = 'center';
  [0,4,8,12,16,20,24].forEach(m => {
    ctx.fillText(m, px(m), PAD.top + H + 20);
  });
  ctx.textAlign = 'right';
  [0,200,400,600,800,1000].forEach(v => {
    ctx.fillText('$' + v + 'K', PAD.left - 8, py(v) + 4);
  });

  // Axis titles
  ctx.fillStyle = '#333';
  ctx.font = 'bold 13px -apple-system, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('Month from project start', PAD.left + W / 2, canvas.height - 6);
  ctx.save();
  ctx.translate(16, PAD.top + H / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText('Cumulative Amount ($K)', 0, 0);
  ctx.restore();

  // --- Investment line (amber) ---
  ctx.strokeStyle = '#c07800';
  ctx.lineWidth = 2.5;
  ctx.setLineDash([]);
  ctx.beginPath();
  data.forEach(([m, inv], i) => {
    i === 0 ? ctx.moveTo(px(m), py(inv)) : ctx.lineTo(px(m), py(inv));
  });
  ctx.stroke();

  // --- Saving line (green) ---
  ctx.strokeStyle = '#2d7d46';
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  data.forEach(([m,, sav], i) => {
    i === 0 ? ctx.moveTo(px(m), py(sav)) : ctx.lineTo(px(m), py(sav));
  });
  ctx.stroke();

  // --- Go-Live vertical line ---
  ctx.strokeStyle = '#1a4a7a';
  ctx.lineWidth = 1.5;
  ctx.setLineDash([5, 4]);
  ctx.beginPath();
  ctx.moveTo(px(6), PAD.top);
  ctx.lineTo(px(6), PAD.top + H);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = '#1a4a7a';
  ctx.font = '11px -apple-system, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('Go-Live', px(6), PAD.top - 6);

  // --- Break-even dot + label ---
  const beX = px(13), beY = py(427);
  ctx.fillStyle = '#c0392b';
  ctx.beginPath();
  ctx.arc(beX, beY, 7, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#c0392b';
  ctx.font = 'bold 12px -apple-system, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('Break-even (month 13)', beX + 10, beY + 4);

  // --- Legend ---
  const LX = PAD.left + W - 240, LY = PAD.top + 12;
  [[  '#c07800', 'Cumulative Investment'],
   ['#2d7d46', 'Cumulative Net Saving']].forEach(([color, label], i) => {
    ctx.strokeStyle = color; ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.moveTo(LX, LY + i*22 + 6); ctx.lineTo(LX + 30, LY + i*22 + 6); ctx.stroke();
    ctx.fillStyle = '#333'; ctx.font = '12px -apple-system, sans-serif'; ctx.textAlign = 'left';
    ctx.fillText(label, LX + 36, LY + i*22 + 10);
  });

  // --- Build phase label ---
  ctx.fillStyle = 'rgba(160,92,0,0.6)';
  ctx.font = '11px -apple-system, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('Build phase', px(3), PAD.top + 16);

})();
</script>
```

Below the canvas chart, add the same blockquote reading guide as in the Markdown version.

---

### Section 7: Success Metrics

A table with five columns: **Metric | Baseline | Target | Measured by | Stakeholder**

Include these metrics (source: Gate4_D6 §2, C1_problem_framing §4):
1. Auto-adjudication rate | 22% | ≥80% of admin-path claims | Monthly claims system report | Sarah Chen
2. Cycle time — administrative path | 8–9 days | ≤5 days | Queue management system | James Liu
3. Cycle time — clinical path | 8–9 days | ≤7 days | Queue management system | James Liu
4. Physician review time per claim | 35 min | ≤3 min with pre-filled packet | Agent audit log | Dr. Marcus Webb
5. Denial appeal overturn rate | 41% | ≤15% | Appeals system (90 days lag) | All three stakeholders
6. Clinical classifier recall (true positive for clinical claims) | Unmeasured | ≥99.5% | Mock calibration before go-live | Dr. Marcus Webb
7. SLA penalty incurrence | Active (Exchange 3) | Zero | Legal/operations reporting | James Liu / Sarah Chen

Below the table: one paragraph explaining the compliance gate — the clinical classifier recall target (≥99.5%) is not a performance aspiration, it is a go-live gate. Below this threshold, a clinical claim can reach the payment path without physician review, constituting a URAC/NCQA compliance event. Source: C1_token_economics §11, C3 §2 Agent 2 governance constraint.

---

---

## HTML specification

After producing the Markdown file, produce a second file `Deliverables/client_proposal.html` with the following requirements:

**Self-contained:** No external CSS, fonts, or JS. The file must render correctly when opened directly in a browser without internet access.

**Typography:**
- Body font: system font stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`)
- Monospace for code/diagram placeholder text: `'Courier New', monospace`
- Base font size: 16px, line-height 1.6
- Max content width: 900px, centered

**Layout:**
- Top navigation bar with anchor links to each section (sticky, white background)
- Main content area with comfortable padding (32px horizontal on desktop)
- Section numbers displayed in a muted colour (e.g. `#888`) beside section titles

**Colour palette (professional, not garish):**
- Primary accent: `#1a4a7a` (dark blue — headings, nav links, table headers)
- Secondary: `#2d7d46` (dark green — success metrics callouts)
- Warning/risk: `#a05c00` (amber — risk table)
- Background: `#ffffff` with alternating table rows at `#f7f9fb`
- Border/divider: `#dde3ea`

**Mermaid diagrams:**
- Include Mermaid.js via CDN in the `<script>` tag: `https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js`
- Initialize with: `mermaid.initialize({ startOnLoad: true, theme: 'neutral' });`
- Wrap each Mermaid block in `<div class="mermaid">...</div>`
- Add a visible caption below each diagram using `<p class="diagram-caption">` in italic grey

**Tables:**
- Full-width, `border-collapse: collapse`
- Header row: `#1a4a7a` background, white text
- Alternating row stripes
- Cell padding: 10px 14px

**Executive summary:**
- Display as a distinct styled box: light blue background (`#eaf2fb`), left border accent (`4px solid #1a4a7a`), padding 20px, slightly larger font (17px)

**Callout boxes:**
- Risk table: amber left border (`4px solid #a05c00`), `#fff8f0` background
- Compliance gate note in §7: red left border (`4px solid #c0392b`), `#fff5f5` background, bold label "COMPLIANCE GATE:"

**Print styles:**
- `@media print`: hide navigation bar, ensure tables don't break across pages where possible, black text on white background, preserve table borders

**Page title / meta:**
```html
<title>Agentic Claims Transformation — Greenfield Health Systems</title>
<meta name="author" content="Benoit Charrier">
<meta name="description" content="Executive proposal for agentic transformation of medical claims adjudication">
```

---

## Acceptance criteria (all must pass)

- [ ] Every number in the proposal traces to a named source file — no invented figures
- [ ] Executive summary is exactly three paragraphs, no bullets, no headers
- [ ] Problem statement names the structural cause (absent clinical content classifier), not just the symptoms
- [ ] Why-not-alternatives table takes each alternative seriously — explains what it can do, not just what it can't
- [ ] Volume × Value quadrant is the exact Mermaid chart from D2C §4 — not redrawn or paraphrased
- [ ] WS1 process topology diagrams are the exact Mermaid flowcharts from D2A §2e — not redrawn
- [ ] Business case uses the corrected figures: $0.315/claim, $732K/year saving, 6.9-month payback, 2-minute HITL average
- [ ] Break-even chart (§6.4) uses the pre-calculated data table exactly — investment line flattens at $420K at month 6, saving line crosses it at month 13
- [ ] Markdown version uses Mermaid `xychart-beta`; HTML version uses the inline Canvas implementation with go-live marker, break-even annotation, and build-phase shading
- [ ] Break-even chart includes the reading-guide blockquote below it
- [ ] Compliance gate (clinical classifier recall ≥99.5%) appears in both the risks table and the success metrics section
- [ ] Sensitivity table shows the business case holds under all adverse scenarios — do not cherry-pick
- [ ] Physician sign-off requirement is named as a design constraint, not a risk or a limitation
- [ ] HTML file is self-contained — verify no external CSS or font imports (Mermaid CDN is the only permitted external reference)
- [ ] Mermaid diagrams are wrapped in `<div class="mermaid">` and `mermaid.initialize()` is called
- [ ] ATX methodology language does not appear anywhere in the client-facing sections of either file

## Fail signals — do not produce output that contains these

- Numbers that differ from C1_token_economics_model.md (the corrected version with $0.315/claim and $732K/year)
- "65%/35% split is a fact" — it is a stakeholder estimate (Dr. Marcus Webb, Exchange 3); always flag as such
- Wave 2 economics presented without flagging clinical notes integration as a hard prerequisite blocker
- A sensitivity table that only shows the base case and optimistic scenarios — the conservative scenarios must be visible
- Generic AI risk language ("the model may produce errors") — only named, specific failure modes from the deliverables
- Physician sign-off described as "where the agent can't be trusted" — it is a regulatory requirement, not a capability limitation
- Break-even chart that recalculates its own data instead of using the pre-calculated table — all numbers in §6.4 are locked; do not recompute them
- A break-even chart with no go-live marker, no break-even annotation, and no build-phase shading — these three elements are required
- HTML with broken Mermaid rendering (missing initialization or missing div wrapper)
- HTML that requires internet access beyond the Mermaid CDN
