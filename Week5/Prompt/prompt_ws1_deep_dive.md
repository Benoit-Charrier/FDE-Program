# Prompt: WS1 Deep Dive — How the Administrative Agent Works

**Output files (produce both):**
- `Deliverables/ws1_deep_dive.md` — the deep dive in Markdown
- `Deliverables/ws1_deep_dive.html` — the same content as a self-contained HTML document (see §HTML spec below)

**Context:** This document is a companion to `Deliverables/client_proposal.md`. It provides the operational detail behind the Wave 1 administrative adjudication agent — intended for stakeholders who want to understand the mechanics before approving the build scope, or for the team leading the discovery and capability spec phases. It is not a system specification; that is the job of the capability specs (C6a, C6b). It is a structured explanation of what the agent does, step by step, in language that a claims operations lead can evaluate.

---

## Read all inputs before writing

| File | What to pull from it |
|------|---------------------|
| `Scenario/scenario_context.md` | Source of truth — volumes, stakeholders, systems, constraints |
| `Deliverables/C1_problem_framing.md` | §3 — why agent over RPA (the argument this document must be consistent with) |
| `Deliverables/D2A_cognitive_load_map.md` | §2a (lived process narrative for WS1), §2c (cognitive zones and breakpoints), §2d (micro-task inventory with dimension scores), §2e (process topology Mermaid diagrams — reproduce verbatim) |
| `Deliverables/D2B_delegation_suitability_matrix.md` | Delegation archetypes and dimension scores for WS1-JtD-1, WS1-JtD-2, WS1-JtD-3 |
| `Deliverables/C1_token_economics_model.md` | §3 (per-step model selection table — the RPA / LLM / HITL classification for each step), §4f (HITL time and rate derivation), §11 (calibration targets) |
| `Deliverables/C3_agentic_solution_architecture.md` | §2 Agent 2 purpose block (escalation triggers, governance constraint), §3 autonomy matrix rows for WS1 actions |

**Prohibition:** Do not invent numbers, step names, or system references not present in these sources. If a detail is not in the inputs, say so explicitly and label it as an assumption.

---

## Audience and tone

**Audience:** Claims operations leads, the project sponsor team (Sarah Chen / Dr. Marcus Webb / James Liu), and any technical reviewers involved in scoping the Wave 1 build. Readers have deep domain knowledge of claims adjudication but may not have read the full ATX deliverables.

**Tone rules:**
- Plain operational language. No methodology jargon: "delegation archetype," "cognitive zone," "non-deterministic," "ATX," "JtD," "micro-task ID" (MT-WS1-X) must not appear.
- Name every step in claims-domain terms: "eligibility check," "coding plausibility review," "prior auth match," "clinical routing," "payment calculation."
- Every number has a source. Every escalation trigger has a rate.
- The physician sign-off requirement is stated as a regulatory fact (URAC/NCQA), not as a capability limitation.

---

## Required structure and content

### Section 1: What this document covers

One short paragraph. State that this document explains, step by step, how the Wave 1 administrative adjudication agent processes a claim from arrival to disposition — what the agent decides alone, where it pauses for a reviewer, and where a physician must be in the loop by regulatory requirement. State that this is not a technical specification; it is an operational description for decision-makers evaluating the build scope.

---

### Section 2: The agent's job in one paragraph

Reproduce the Agent 2 (WS1 Administrative Adjudication Agent) purpose block from C3 §2, rewritten in plain language. One tight paragraph — not a bullet list. Cover:
- What it receives as input (a normalised claim record from the intake agent)
- The four categories of work it performs (eligibility validation, coding review, prior auth check, clinical routing classification, payment determination)
- What it produces as output: one of four dispositions (auto-approved with payment amount / rejected with specific failure code / routed to physician review queue / escalated to human reviewer for exception resolution)
- The one thing it cannot produce without a physician: a medical necessity determination on any claim with clinical content

Source: C3 §2 Agent 2, Gate4_D6 §3.

---

### Section 3: Step-by-step — what happens to a claim

A table with three columns: **Step | How it is handled | Why this approach**

Use plain claims-domain step names (not MT-WS1-X identifiers). For the "How it is handled" column, use exactly one of these four labels:
- **Automated (rule / code)** — no LLM, no human
- **Automated (API call)** — calls an external system, binary result
- **Agent judgment** — LLM reasoning; may escalate
- **Agent judgment → mandatory physician review** — LLM routes; physician always decides

For the "Why this approach" column, explain in one sentence why this specific step uses this approach — ground each explanation in the nature of the decision (is it deterministic? does it require pattern recognition? is it compliance-governed?). Do not repeat the label.

| Step | How it is handled | Why this approach |
|------|:---:|-------------------|
| Format parsing and field extraction (EDI 837, PDF, portal) | Automated (rule / code) | EDI 837 is a structured specification; the correct fields are enumerated — an LLM call adds latency and cost with zero quality benefit |
| Member eligibility lookup | Automated (API call) | The eligibility system returns a binary result (eligible / not eligible on service date); no reasoning required |
| Eligibility discrepancy resolution | Agent judgment | When the eligibility check returns an ambiguous result (e.g., termination date near service date), the agent distinguishes data-entry lag from a genuine coverage gap using contextual pattern recognition — a task no formal rule covers (~5% of claims) |
| Code validity and pairing check | Automated (rule / code) | ICD-10/CPT crosswalk rules are a structured lookup against a reference table; the standard path is a code-validity query, not LLM inference |
| Coding plausibility assessment | Agent judgment | The agent evaluates whether the code combination is clinically plausible given provider type and diagnosis — a judgment that varies by context and is not codifiable as a rule (~15% of claims trigger a flag) |
| Prior authorisation lookup | Automated (API call) | The prior auth system returns a record or its absence; deterministic binary check |
| Prior authorisation partial-match resolution | Agent judgment | When the auth on file differs from the claim (unit variance, code variant, date mismatch), the agent assesses whether the difference falls within a defensible tolerance — no documented threshold exists (~8% of claims) |
| Clinical content routing classification | Agent judgment → mandatory physician review | The agent classifies each claim as administrative or clinical using multi-factor pattern recognition across diagnosis codes, procedure codes, and provider specialty; any claim classified as clinical is sent to the physician queue without exception — this is a URAC/NCQA compliance requirement, not a design choice (~10% of claims escalated for confidence review before routing) |
| Payment calculation | Automated (rule / code) | Fee schedule application is arithmetic against a rate table; the correct answer is computed by formula — an LLM call produces no quality improvement |
| Contract exception handling | Agent judgment | When a fee schedule exception flag is raised, the agent reviews the contract carve-out context and produces a rate recommendation for human confirmation (~2% of claims) |

Source: C1_token_economics §3.

Below the table, add this paragraph:

> **The five automated steps (format parsing, eligibility lookup, code validity check, prior auth lookup, payment calculation) consume no LLM tokens.** They run as in-process code or external API calls. This is the correct architecture: an LLM call on a binary eligibility lookup adds cost and latency for zero quality benefit. The five judgment steps (eligibility discrepancy resolution, coding plausibility, prior auth partial-match, clinical routing, contract exception) invoke the LLM only when no deterministic rule resolves the decision. Average LLM calls per claim: ~2.15 (routing classification and coding plausibility run on every claim; the other three run conditionally on ~15% of claims combined).

---

### Section 4: Process flow diagrams

Add this caption above the first diagram:
> **Phase 1 — Intake through coding and eligibility.** Every claim enters here regardless of path. Steps shown in colour involve agent judgment; steps shown without fill are deterministic rule execution or API calls.

Embed the Phase 1 Mermaid flowchart from D2A §2e verbatim. Do not modify it.

Add this caption above the second diagram:
> **Phase 2 — Prior authorisation, clinical routing, and payment.** The routing decision at step 8 (clinical content classification) is the compliance gate: a claim classified as clinical is sent to the physician queue; a claim classified as administrative proceeds to payment determination. The routing decision cannot be reversed by the payment agent — physician review is enforced by the queue architecture, not by policy.

Embed the Phase 2 Mermaid flowchart from D2A §2e verbatim. Do not modify it.

---

### Section 5: When a claim goes to a human reviewer

**Format:** A two-part section. First, a table of the five escalation triggers. Second, a short narrative about what the reviewer experience looks like.

**Escalation trigger table:**

| Trigger | Condition | Approximate frequency | What the reviewer decides |
|---------|-----------|:---:|--------------------------|
| Eligibility discrepancy | Agent cannot resolve whether a near-term eligibility boundary is a data lag or a genuine coverage gap | ~5% of claims | Confirm eligibility or deny with specific reason |
| Coding plausibility flag | Agent scores a code combination as clinically implausible for the provider type or diagnosis | ~15% of claims | Confirm the code pairing is valid or reject the code |
| Prior auth partial match | Auth on file differs from the claim in units, dates, or code variant beyond the agent's defensible range | ~8% of claims | Approve the variance or require the provider to re-submit with a matching auth |
| Clinical routing confidence below threshold | The clinical content classifier's confidence score falls below the configured threshold — the agent is uncertain whether the claim contains clinical content | ~10% of claims | Confirm routing: administrative path or clinical physician queue |
| Contract exception | The fee schedule lookup surfaces a contract carve-out that requires rate determination beyond the standard rate table | ~2% of claims | Approve the agent's recommended rate or apply an alternate rate |

Source: C3 §2 Agent 2 escalation triggers; rates from C1_token_economics §4f.

**Reviewer experience narrative:**

Three short paragraphs:

1. **What the reviewer sees:** The reviewer receives a focused exception packet — not the raw claim file. The packet contains: the specific flag the agent raised, the relevant claim fields (member ID, service date, codes, provider), the agent's reasoning (what it found and why it cannot resolve it), and a single yes/no or choose-one decision prompt. The reviewer does not need to re-read the whole claim.

2. **How long it takes:** At the base case, a reviewer handles approximately 25% of claims as HITL events. The average review time is 2 minutes (1 minute for clear exceptions — confirming an eligibility check, approving a code pairing that the agent flagged conservatively; 3.5 minutes for complex exceptions — evaluating a prior auth tolerance call or confirming a clinical routing decision). Source: C1_token_economics §4f, calibrated against Dr. Marcus Webb's clinical review benchmark of 3 minutes per claim for a full pre-filled clinical packet — admin HITL is a narrower, targeted task and should be faster. At 1.4 FTE-equivalent for HITL volume, this is well within the 7-staff retention target.

3. **What the reviewer's decision produces:** The reviewer confirms, overrides, or escalates. A confirmation writes an audit record and releases the claim to the next step. An override writes the reviewer's decision with a reason code and releases. A further escalation flags the claim for supervisor review. Every reviewer action — including a confirmation — is logged with a timestamp, reviewer ID, and decision code. This audit trail is the primary evidence for URAC/NCQA compliance review.

---

### Section 6: The compliance boundary

One short section — three bullet points, no prose padding.

- **What the boundary is:** Any claim classified as containing clinical content must be reviewed by a licensed physician or advanced practice provider before a coverage determination is made. This is not a design choice — it is required by URAC/NCQA accreditation standards (Dr. Marcus Webb, Exchange 2).
- **How it is enforced:** The clinical content classifier (step 8) routes clinical claims to the physician queue. The payment agent (step 9) cannot receive a claim that has not cleared the physician queue. The routing is enforced by the queue architecture — there is no manual override path that bypasses physician review.
- **What the calibration gate means:** Before go-live, the classifier must achieve ≥99.5% recall on clinical claims — meaning it must correctly identify at least 995 out of every 1,000 clinical claims. Below this threshold, clinical claims can reach the payment path without physician review, constituting a URAC/NCQA compliance event. This threshold is the single go-live gate that cannot be relaxed regardless of economic pressure. Source: C1_token_economics §11.

---

### Section 7: Key numbers at a glance

A compact reference table for readers who want the economics without reading the full business case. Source: C1_token_economics §6, §7.

| Metric | Figure | Source |
|--------|--------|--------|
| Claims processed through WS1 pipeline daily (steps 1–8) | 2,000 | scenario_context.md |
| Claims on administrative path daily (steps 9–10) | 1,300 (65% of 2,000 — stakeholder estimate) | scenario_context.md, Exchange 3 |
| Current manual cost per admin claim | $18.23 (35 min × $31.25/hr) | C1_token_economics §2 |
| Agent cost per admin claim | $0.315 | C1_token_economics §6 |
| Per-claim cost reduction | 98.3% | C1_token_economics §6 |
| HITL rate (base case) | 25% of claims | C1_token_economics §4f |
| Average HITL review time | 2 minutes | C1_token_economics §4f |
| HITL FTE equivalent | 1.4 FTEs | C1_token_economics §7 |
| Annual agent running cost (Wave 1) | $113K/year | C1_token_economics §7 |
| Annual net saving (Wave 1) | $732K/year | C1_token_economics §7 |
| Payback period | 6.9 months from go-live | C1_token_economics §7 |
| Clinical classifier recall required for go-live | ≥99.5% | C1_token_economics §11 |

---

## HTML specification

Produce `Deliverables/ws1_deep_dive.html` as a self-contained HTML file. Apply the same visual design as `client_proposal.html`:

**Shared styles (copy from the proposal HTML spec):**
- System font stack, 16px base, 1.6 line-height, 900px max-width centered
- Primary accent `#1a4a7a`, secondary `#2d7d46`, background `#ffffff`, alternating table rows `#f7f9fb`, border `#dde3ea`
- Sticky top nav with anchor links to each section
- Full-width tables, `border-collapse: collapse`, `#1a4a7a` header rows, white header text, 10px 14px cell padding

**Section-specific styling:**
- Step table (Section 3): colour-code the "How it is handled" column cells by label:
  - "Automated (rule / code)" → light grey background (`#f0f0f0`)
  - "Automated (API call)" → light grey background (`#f0f0f0`)
  - "Agent judgment" → light amber (`#fff3e0`)
  - "Agent judgment → mandatory physician review" → light red (`#fff0f0`), bold text
- Compliance boundary section (Section 6): red left border callout box (`4px solid #c0392b`, `#fff5f5` background), bold label "COMPLIANCE BOUNDARY:"
- Key numbers table (Section 7): the clinical classifier recall row should be highlighted with a light red background to reinforce its status as a go-live gate

**Mermaid diagrams:**
- Include Mermaid.js CDN: `https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js`
- `mermaid.initialize({ startOnLoad: true, theme: 'neutral' });`
- Each diagram: `<div class="mermaid">...</div>` with `<p class="diagram-caption">` caption in italic grey below

**Print styles:** `@media print` — hide nav, black text on white, preserve table borders.

**Page title / meta:**
```html
<title>WS1 Administrative Agent — How It Works | Greenfield Health Systems</title>
<meta name="author" content="Benoit Charrier">
<meta name="description" content="Step-by-step explanation of the Wave 1 administrative adjudication agent for Greenfield Health Systems">
```

---

## Acceptance criteria (all must pass)

- [ ] Every step in the Section 3 table uses one of the four exact "How it is handled" labels — no invented labels
- [ ] No micro-task IDs (MT-WS1-X) appear anywhere in either output file
- [ ] Process topology diagrams (Section 4) are the exact Mermaid flowcharts from D2A §2e — reproduced verbatim, not simplified or redrawn
- [ ] Compliance boundary section names URAC/NCQA and Dr. Marcus Webb (Exchange 2) as the source — not "best practice" or "risk management"
- [ ] Clinical classifier recall ≥99.5% appears in both Section 6 and Section 7
- [ ] HITL numbers use the corrected figures: 25% rate, 2-minute average (1 min clean / 3.5 min complex), 1.4 FTE equivalent
- [ ] Agent cost uses $0.315/claim; annual saving uses $732K/year
- [ ] The "65%/35% split is a stakeholder estimate" is flagged where the 1,300/day figure appears
- [ ] Section 7 key numbers table includes source column — every figure is traceable
- [ ] HTML step table colour-codes "mandatory physician review" rows in light red with bold text
- [ ] HTML compliance boundary is a red callout box with the "COMPLIANCE BOUNDARY:" label
- [ ] Mermaid diagrams are wrapped in `<div class="mermaid">` and `mermaid.initialize()` is called
- [ ] HTML is self-contained — Mermaid CDN is the only external reference

## Fail signals — do not produce output that contains these

- Step table rows that paraphrase or simplify the D2A §2e Mermaid diagrams — the diagrams are the authoritative topology; do not redraw them
- Physician sign-off described as a capability limitation ("the agent cannot make this decision") — it is a regulatory requirement
- HITL time of 10 minutes — the corrected figure is 2 minutes average; the old figure is wrong and must not appear
- The statement that the business case depends on keeping HITL rate below 25% — with 2-minute HITL time, the business case holds even at 35% HITL; the 25% threshold is a quality/compliance gate, not an economic survival condition
- Generic risk language about AI errors — only the named failure modes from C3 §2 and C1_token_economics §11
- ATX methodology jargon in any client-facing section of either output file
