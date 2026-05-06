# CLAUDE.md — Scenario 4: MiniBase Community Content Moderation

## Scenario Context

MiniBase is a UK-incorporated tabletop-miniature hobbyist platform (~180K users, ~12K posts/day) whose volunteer moderation team (8 volunteers, 2 paid staff) has reached capacity at 47 hours/day of moderation effort. The primary stakeholder is Tomasz "Tom" Włodarczyk, Community Manager, who owns the moderation function and carries personal accountability for sponsor relationships and IP claims. The core risk shaping every design decision is Tom's stated asymmetry: false negatives are existential (one viral wrong removal can destroy community trust and lose sponsors), false positives are survivable — which means no autonomous content action is appropriate at current maturity, and any agent must be designed to support human judgment, not replace it.

---

## Deliverables Index

| File | Contents |
|---|---|
| `cognitive-load-map.md` | Jobs to be Done, micro-tasks, cognitive dimension scores, zones, breakpoints, lived narratives |
| `delegation-suitability-matrix.md` | Delegation dimension scores per work stream, archetype assignments with rationale |
| `volume-value-analysis.md` | V×V scores for all work streams, primary agentic target selection and justification |
| `agent-purpose-document.md` | Full agent specification: purpose, scope, KPIs, autonomy matrix, escalation triggers, failure modes, governance, implementation specification |
| `system-data-inventory.md` | Systems the agent needs, availability status, gaps, risks, environment variables, compounding opportunities |
| `discovery-questions.md` | Design-changing questions for the primary stakeholder with per-answer design consequences |

---

## Key Scenario Facts

Facts that change the design if they change:

- **72% of the queue (WS1, ~1,080/day) is rule-bound** — Boolean checks against enumerable criteria; no LLM agent needed here
- **24% of the queue (WS2, ~360/day) requires multi-source synthesis** — this is the agentic target; 360 cases × 5 min = 30 hours/day moderator effort
- **Tom's stated asymmetry** — "absorb a lot of false positives to avoid one viral false negative" — rules out any fully autonomous content action; every archetype assignment flows from this
- **Shadow governance layer** — Tom's private Google Sheet carries Tier 1 (sponsors) and Tier 2 (special users) routing rules that override the 14-page policy; any agent built from the policy alone will fail
- **Three-tier user model with only one structured tier** — Tier 1/2 in Sheet; Tier 3 (established commercial members) in no structured source; Stripe tier is an imperfect proxy
- **Sub-forum norms are informal and unqueryable** — Painters, Historical, Japanese sub norms live in Tom's tracker; no structured source exists
- **2024 sponsor incident** — @vortex_minis commercial post removed without Tom's review; founder called; near-miss. This event is the load-bearing justification for the Tier 1/2 routing rule and the 100% escalation accuracy KPI
- **Discord #mod-decisions is the de-facto case law** — precedents are built there but unindexed and unsearchable
- **No SLAs exist** for Discord consensus deadlocks, brief assembly timeouts, or moderator inaction — three APD escalation triggers are TBD pending Q1

---

## Key Design Decisions

**D1: WS1 assigned Human-led + Automation Support, not Fully Agentic**
Decision Determinism = High across all 9 micro-tasks; every decision is a Boolean check. A rules engine is cheaper, faster, and eliminates hallucination risk at the exception routing step (steps 4–5, Compliance/Risk = High). An LLM agent adds cost and variance without adding value for deterministic work. The common misclassification — high volume → fully agentic — is the anti-pattern WS1 is designed to avoid.

**D2: WS2 assigned Human-led + Agent Support, not Agent-led + Human Oversight**
The judgment core (steps 10–12) scores High CL + Low DD + High C/R + Low TA simultaneously — the three steps where the moderator weighs asymmetric risk and decides. Agent-led is rejected because autonomous content action at these steps would violate Tom's stated asymmetry. The agent's value is in removing the 3–4 minutes of preparation work per case, not in making the decision.

**D3: WS4 assigned Human-only, not Human-led + Agent Support**
Steps 4–8 are a five-step judgment core where all delegation-blocking dimensions peak simultaneously. Triage criteria live in Tom's head with no structured source (stakeholders_quiz Q3). Volume is 3–5 cases/week — ROI on even partial automation is measured in years. Steps 1–3 and 9–10 are technically automatable but not worth isolating at this volume.

**D4: WS2 selected as primary agentic target over WS1**
WS1 has higher volume (1,080/day vs 360/day) but Non-Determinism = 1 — the wrong kind for an LLM agent. WS2 V×V = 20 (vs WS1 V×V = 5). WS2's context assembly work (six distinct data sources, multi-cultural interpretation, precedent search) is exactly the preparation burden an LLM agent removes without needing to decide.

**D5: Agent scoped to context assembly only — no content decisions under any condition**
Tom's asymmetry makes any autonomous content action a design failure at current maturity. The APD Autonomy Matrix has no row where the agent makes a content decision — this is an explicit design choice, not a gap. The scope boundary derives directly from the CLM judgment core (steps 10–12).

**D6: KPI selection rationale**
- *Context brief completeness ≥95%*: tracks whether the agent delivers its core value — if briefs are incomplete, the agent is not working. Target 95% leaves headroom for cases where data sources are unavailable (Gap-2, Gap-3). Source: derived from agent purpose; target assumed.
- *Tier 1/2 escalation accuracy 100%*: directly measures the 2024 incident risk. Zero misses is the non-negotiable target — one miss is the exact failure mode Tom described. Source: 2024 incident, Tom's stated risk tolerance.
- *Moderator time-per-case ≤3 min (baseline 5 min)*: the primary business metric — a 40% reduction in 30 hours/day of team effort. Target derived from the assumption that context assembly (steps 1–9) accounts for ~3–4 of the 5-minute baseline; judgment (steps 10–12) takes ~1–2 min regardless of agent support. Source: CLM time breakdown; target assumed.
- *Escalation rate ≤15%*: measures the agent's capability ceiling — cases where missing data prevents brief assembly and forces manual handling. 15% ceiling is assumed; actual target should be confirmed once Gap-1 and Gap-2 resolution is known. Source: assumed; test via Q2 and Q3.

**D7: Three TBD SLAs left as TBD, not invented**
APD escalation triggers for Discord consensus deadlock, brief assembly timeout, and moderator inaction have no existing SLA in any scenario source. These were left as TBD with DQ#1 reference rather than invented — an invented SLA would produce a spec that looks complete but would fail operationally. Source: stakeholders_quiz Q4; no SLA data available.

---

## Assumptions Log

Every `[Assumed]` tag from deliverables 1–6, collected.

---

**[A-1] Tier 3 established commercial members are recognisable via Stripe payment tier as a fallback when not in Tom's Sheet**
Confidence: medium — Stripe commercial tier is the only structured proxy available; it does not map cleanly to community standing, and a commercial Stripe account does not guarantee the informal latitude Tom extends
Source: CLM WS1 step 4; CLM WS2 step 2; CLM WS2 Breakpoints
Test via: DQ#6 (does a structured Tier 3 list exist anywhere?)

---

**[A-2] Tier 3 accounts require elevated caution and Senior Moderator sign-off before removal**
Confidence: medium — inferred from stakeholders_quiz Q5 (long-standing commercial members get informal latitude); the specific requirement for Senior Mod sign-off is a design choice not explicitly confirmed by Tom
Source: CLM WS2 Breakpoints
Test via: DQ#6; confirm sign-off requirement directly with Tom in live round

---

**[A-3] A Discourse user ID → Stripe customer ID mapping exists or can be created**
Confidence: low — no scenario source confirms this mapping; MiniBase uses Stripe for payments but the link between community account and Stripe customer record is unconfirmed
Source: APD Scope (Tier 3 fallback line)
Test via: DQ#2

---

**[A-4] Tom will export sub-forum norms from his private tracker into a structured queryable source before go-live**
Confidence: medium — norms confirmed to exist (stakeholders_quiz Q2 names three sub-forums); Tom's willingness and timeline to create a structured source is unconfirmed
Source: APD Scope (sub-forum norm retrieval line)
Test via: DQ#3

---

**[A-5] Context assembly (steps 1–9) accounts for approximately 3–4 minutes of the 5-minute per-case baseline**
Confidence: medium — the 5-minute baseline is confirmed in the scenario brief; the split between preparation and judgment is inferred from the micro-task structure; not measured
Source: APD KPI (moderator time-per-case target)
Test via: baseline measurement at deployment; adjust KPI target accordingly

---

**[A-6] The escalation rate ceiling of 15% is an appropriate target for incomplete briefs**
Confidence: low — no data on current incomplete-brief rate exists; 15% is a working assumption that will need calibration once Gap-1 and Gap-2 resolution is known
Source: APD KPIs (escalation rate)
Test via: DQ#2, DQ#3; recalibrate after first 30 days of operation

---

**[A-7] IP claim triage criteria (claimant credibility, retaliatory history) could eventually be documented if Tom is willing**
Confidence: medium — stakeholders_quiz Q3 flags this as uncertain; criteria may be too context-dependent to formalise
Source: CLM WS4 JTBD Key systems
Test via: DQ#4

---

**[A-8] The context brief output format (TypeScript interface in APD Implementation Specification) reflects what the moderator review queue needs to receive**
Confidence: medium — fields derived from the APD scope and the WS2 micro-task breakdown; the actual moderator queue integration (field names, delivery mechanism, UI rendering) has not been confirmed with Tom or the platform team
Source: APD Implementation Specification (Context Brief Output Format); APD Scope; CLM WS2 steps 1–9
Test via: confirm interface with Tom and any platform engineer responsible for the moderator queue before go-live; adjust field names and structure to match actual queue system

---

**[A-9] The WS2 agent is triggered by the WS1 automation rules engine, not directly by Discourse**
Confidence: medium — WS1 (Human-led + Automation Support) must be implemented first; it performs the Boolean routing checks and hands grey-zone cases to WS2. The WS2 agent has no internal routing logic. WS1 implementation is a deployment prerequisite not covered by this spec.
Source: APD Implementation Specification (Trigger / Invocation); DSM WS1 archetype assignment; CLM WS1/WS2 inter-stream handoff
Test via: confirm WS1 implementation status and webhook payload format with platform team before deploying WS2 agent; see OI-8

---

**[A-10] Completed context briefs are delivered by POSTing to a moderator queue endpoint (`MODERATOR_QUEUE_ENDPOINT`)**
Confidence: low — no moderator queue system is named in any scenario source; the delivery mechanism (REST endpoint, database write, Discourse queue write-back, custom dashboard) is fully unconfirmed
Source: APD Implementation Specification (Brief Delivery Mechanism)
Test via: confirm queue system with Tom and platform team before go-live; this is the most likely integration point to change between prototype and production

---

**[A-11] The decision rationale template structure (markdown format with account, norm, reporter, precedent, viral risk fields and decision checkboxes) is sufficient for moderator sign-off**
Confidence: medium — structure derived from the APD audit log fields and CLM WS2 judgment core inputs; actual moderator workflow and UI may require a different format or additional fields
Source: APD Implementation Specification (Context Brief Output Format — decision_rationale_template)
Test via: validate with Tom and a sample moderator during UAT; adjust fields based on what moderators actually need to record their decision

---

**[A-12] Tier 1/2 and viral risk escalations are delivered by POSTing to a separate `TOM_ESCALATION_ENDPOINT`, distinct from the moderator queue**
Confidence: medium — Tom's escalation path is likely a different channel from the standard moderator queue (he is not a queue-processing volunteer); the specific delivery mechanism (REST endpoint, email, Slack, Discourse DM) is unconfirmed
Source: APD Implementation Specification (Tier 1/2 Escalation Delivery); APD Escalation Triggers
Test via: confirm Tom's preferred notification mechanism before go-live; update `TOM_ESCALATION_ENDPOINT` integration accordingly

---

**[A-13] Audit log is written as JSONL to a local file at `AUDIT_LOG_PATH`**
Confidence: low — local file is the simplest durable default for a prototype; production deployment will likely require a database or log aggregation service; file-based audit log is not queryable at scale
Source: APD Governance (audit log persistence); SDI Environment Variables
Test via: confirm target logging infrastructure with platform team before production deployment; local file is acceptable for prototype and UAT phases

---

**[A-14] WS1 passes the flag payload to WS2 with the fields defined in the WS1 Webhook Payload Schema**
Confidence: medium — fields are derived from what WS2 assembly steps require (post ID for Discourse read, sub-forum for norm lookup, poster handle for tier check, reporter count for signal assessment); the actual WS1 output schema is unconfirmed since WS1 is out of scope for this build
Source: APD Implementation Specification (WS1 Webhook Payload Schema); CLM WS2 steps 1–9
Test via: confirm WS1 output schema with platform team when WS1 is implemented (OI-8); adjust `WS1FlagPayload` interface to match

---

**[A-15] Engagement velocity is calculated as the sum of new replies, new reactions, and new flag reports on the flagged post in the trailing 30-minute window**
Confidence: medium — these three signals are the most directly observable engagement events via the Discourse API; Tom's actual viral risk heuristic is undocumented; the formula may undercount or overcount relative to how Tom currently judges escalation risk
Source: APD Implementation Specification (Viral Risk Formula); APD Autonomy Matrix (viral risk row); APD Failure Mode #4
Test via: validate formula with Tom before go-live; adjust signals and weights based on how he currently identifies posts at risk of going viral

---

**[A-16] Tom's Google Sheet has a header row and columns: A = handle (string), B = tier (number: 1 or 2), C = notes (string)**
Confidence: medium — column structure is inferred from the Sheet's purpose (Tier 1/2 lookup by handle); the actual column order, header names, and tier value format (numeric vs text) are unconfirmed
Source: APD Implementation Specification (Google Sheet Column Schema); APD Scope (Sheet lookup); SDI (Tom's Google Sheet row)
Test via: inspect the Sheet directly before go-live; update column indices and tier value parsing to match actual structure

---

**[A-17] The LLM system prompts defined in APD Implementation Specification are sufficient for the reporter signal assessment and rationale template generation steps**
Confidence: medium — prompts are written to match the APD scope (no moderation recommendations, evidence-only assembly); actual prompt quality will be validated during the build loop and UAT
Source: APD Implementation Specification (LLM System Prompts); APD Scope; CLM WS2 steps 5–6 and step 9
Test via: evaluate prompt outputs during build loop diagnosis; refine prompts based on brief quality observed in UAT with moderators

---

**[A-18] Fully loaded hourly cost for a UK community moderator is £70/hour**
Confidence: medium — within the £50–120 typical knowledge worker range; no salary data is given in the brief; figure used as the baseline for WS2 economics
Source: V×V Economics Step 1 (Baseline Cost Model)
Test via: confirm with Tom or MiniBase finance contact before presenting the business case; adjust baseline cost and annual saving accordingly

---

**[A-19] Token consumption per WS2 case is approximately 4,400 input tokens and 600 output tokens**
Confidence: medium — estimated from APD scope (20-post thread context, two LLM calls, system prompts); not measured against real Discourse content; actual token counts will vary by case complexity
Source: V×V Economics Step 2 (Token Economics Model)
Test via: measure actual token consumption during build loop testing on representative sample cases; update agent cost per case accordingly

---

**[A-20] Total build cost for the WS2 agent is approximately £38,000 (assessment + development + integration + testing + change management)**
Confidence: medium — estimated from typical single-agent build with 3–4 integrations; no project estimate or rate card is given in the brief
Source: V×V Economics Step 3 (ROI Business Case)
Test via: confirm with delivery team during scoping; adjust payback period and 3-year net value accordingly

---

**[A-21] WS3 (User Dispute Appeals) Wave 2 build cost reduction is £12,000–15,000 due to shared Discourse integration, Sheet lookup, and audit log from WS2**
Confidence: medium — compounding thesis holds if WS3 uses the same integration points; WS3 scope not fully designed; reduction estimate is directional
Source: V×V Economics Step 4 (Self-Financing Roadmap)
Test via: validate when WS3 APD is drafted; adjust Wave 2 cost reduction based on actual shared component count
Confidence: medium — prompts are written to match the APD scope (no moderation recommendations, evidence-only assembly); actual prompt quality will be validated during the build loop and UAT
Source: APD Implementation Specification (LLM System Prompts); APD Scope; CLM WS2 steps 5–6 and step 9
Test via: evaluate prompt outputs during build loop diagnosis; refine prompts based on brief quality observed in UAT with moderators

---

## Open Items

Items that would change the design if resolved — each references the deliverable section affected.

| # | Item | Affects | Resolves via |
|---|---|---|---|
| OI-1 | SLA for Discord consensus deadlock (no current SLA) | APD Escalation Trigger #4 (TBD minutes); CLM WS2 Breakpoint | DQ#1 |
| OI-2 | SLA for brief assembly timeout (no current SLA) | APD Escalation Trigger #5 (TBD minutes) | DQ#1 |
| OI-3 | SLA for moderator inaction (no current SLA) | APD Escalation Trigger #6 (TBD minutes) | DQ#1 |
| OI-4 | Discourse → Stripe user ID mapping existence | APD Scope [A-3]; SDI GAP-2 | DQ#2 |
| OI-5 | Sub-forum norm structured source creation and timing | APD Scope [A-4]; SDI GAP-1 | DQ#3 |
| OI-6 | `VIRAL_RISK_THRESHOLD` value — configurable env var, no default; Tom must confirm before deployment | APD Failure Mode #4; APD Autonomy Matrix (viral risk row) | Confirm with Tom before go-live |
| OI-7 | Escalation rate KPI target (15% assumed) — needs calibration once Gap-1/2 resolution is known | APD KPIs | DQ#2, DQ#3; recalibrate at 30 days post-deployment |
| OI-8 | WS1 automation must be implemented and operational before WS2 agent is deployed — WS2 has no internal routing logic | APD Implementation Specification (Trigger); A-9 | Confirm WS1 implementation status and webhook payload format with platform team |

---

## Build Loop Instructions

### Tech Stack

- **Runtime:** Node.js
- **SDK / deps / libs:** default setup (no custom framework constraints; use standard npm ecosystem defaults)
- **LLM:** Anthropic SDK (`@anthropic-ai/sdk`); model `claude-haiku-4-5-20251001`

### Stubs Rule

Use stubs for all integrations that are unavailable, unconfirmed, or listed as open items — unless explicitly confirmed as available in `system-data-inventory.md`. Stubs must be clearly named (e.g. `getSubForumNorm_STUB`) and must not invent values for open items (OI-1 through OI-8). When a stub is used, log a console warning with the OI or GAP number.

**Discord precedent search** is a mandatory stub in v1 — GAP-3 classifies it as a post-go-live enhancement. Always return `{ found: false, cases: [] }` and log `[STUB][GAP-3]`.

### Reading Order

Read in this sequence before writing any code:

1. **`agent-purpose-document.md`** — primary build spec including Implementation Specification; build to this document
2. **`system-data-inventory.md`** — integration constraints, gaps, and environment variables
3. **`CLAUDE.md`** (this file) — design decisions, assumptions, open items; explains *why* the APD is scoped as it is
4. **`cognitive-load-map.md`** — WS2 micro-task breakdown; verify agent covers steps 1–9 and stops before steps 10–12
5. **`delegation-suitability-matrix.md`** — archetype boundaries; use to catch drift toward content decisions
6. **`discovery-questions.md`** — what is deliberately unresolved; do not invent answers, stub instead

### Build Prompt

Hand this file and `agent-purpose-document.md` to Claude Code with this exact prompt:

> *"Begin building the agent described in these documents. First, tell me what you can build confidently without asking questions. Second, tell me what you need to clarify before building the rest. Third, build the parts you are confident about."*

### Build Diagnosis

After the build, diagnose each output against three questions:
1. **What it built** — faithful to the APD scope and autonomy matrix, or did it drift into content decisions?
2. **What questions it asked** — each question is a gap in the APD; good revisions touch the autonomy matrix or escalation triggers, not just the purpose statement
3. **What it said it couldn't build** — check against OI-1/2/3 (TBD SLAs) and OI-4/5 (data gaps); if it flagged these, the APD is honest; if it invented values, the build output is unsafe

A **delegation boundary gap** is the Week 2-specific failure mode: Claude Code can't tell whether a step is fully agentic, agent-led, or human-led and defaults to cheapest implementation. If the build produces content decision logic, the scope boundary in the APD needs to be made more explicit.
