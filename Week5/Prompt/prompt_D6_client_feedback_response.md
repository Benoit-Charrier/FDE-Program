# Prompt: Deliverable D6 — Client Feedback Response

## What this deliverable is

A structured memo responding to Marcus Reyes's three pushback points. Each point is addressed concretely — hold the position with evidence, cave with explicit naming of what gets cut, or propose a concrete alternative. Vague reassurance is not a response. Silence on any point is a failure.

The response is written to Marcus, not about Marcus. It is direct, numbers-grounded, and respects his stated posture: results-oriented, low patience for qualifications, expects FDEs who challenge framing with substance.

---

## Inputs (read all before writing)

- `Input/Marcus-Pushback-Benoit-Charrier.md` — the pushback memo. Three points, each with a specific ask.
- `Deliverables/D1_problem_framing.md` — your own success metrics and the $200M capacity case; Marcus will hold you to these
- `Deliverables/D2_engagement_intake_scope.md` — wave sequencing, scope decisions, and the facility preference enrichment gap
- `Deliverables/D3_solution_architecture.md` — ADRs, delegation archetypes, the adoption constraint that drove HITL-first
- `Scenario/scenario_context.md` — scenario facts only; do not invent numbers Marcus didn't provide

---

## Marcus's three pushback points

**P1 — Timeline:** Board update is in 6 weeks. WS2 — the metric that matters (time-to-fill) — is sequenced to week 12. Marcus wants a narrow WS2 demo at week 6 (example: one facility, one specialty, two coordinators), even if HITL-heavy. "Tell me what piece of WS2 I can demo at week 6 against a real shift request."

**P2 — Wave 1 coordinator value:** With WS4 out of scope, Wave 1 is WS1 running in shadow mode. Marcus's challenge: "What does a coordinator actually do differently on day 1 of week 9 because of what you shipped?" If the answer is nothing yet, Wave 1 is internal infrastructure with a coordinator-adoption story attached, not a coordinator-facing deliverable.

**P3 — Year-1 ROI without facility profiles:** Facility preference enrichment is named as the gate to 85% autonomous fill but has no owner, scope, cost, or date. Marcus's CFO question: if the agent is HITL-on-every-selection until profiles exist, and profiles are a year-long data project, what is year-1 ROI from credential querying alone — in dollars?

---

## Response posture options (choose one per point — name it explicitly)

For each pushback point, your response must declare one of three postures before developing the argument:

| Posture | When to use | What it requires |
|---------|-------------|-----------------|
| **Hold** | The pushback would break a constraint that is load-bearing (safety, adoption, cascade error risk) | Name the specific constraint; explain concretely what breaks if you cave; offer something that addresses Marcus's underlying need without crossing the constraint |
| **Cave** | The pushback exposes a genuine sequencing error or over-constraint you can correct | Name exactly what changes; name what else must change or get cut as a result; do not cave silently |
| **Propose alternative** | You cannot give Marcus exactly what he asked for, but there is a concrete adjacent option that addresses his underlying need | State the alternative with specifics — date, scope, what the coordinator can actually touch, what it costs |

---

## Required structure

Output file: `Deliverables/D6_client_feedback_response.md`

### 0. Response posture summary

One table, one row per pushback point:

| Point | Posture (Hold / Cave / Alternative) | One-line summary of response |
|-------|-------------------------------------|------------------------------|

### 1. P1 — Timeline: WS2 demo at week 6

Address Marcus's specific ask: a narrow WS2 demonstration against a real shift request at week 6 — one facility, one specialty, two coordinators.

If you propose an alternative: name the facility segment, the specialty, the coordinator scope, the HITL configuration, and what "demo-able" means at week 6 (a real shortlist presented to a real coordinator, or something else). Name the prerequisites that must be compressed — API validation, HITL interface, credential gate — and the risk you are accepting by accelerating them.

If you hold: explain what specifically breaks at week 6 that does not break at week 12 — not "the adoption risk is too high" (Marcus knows that) but the specific predecessor that cannot be ready (API validation, WS1 quality gate, HITL queue build time) and why compressing it creates the failure mode Marcus is trying to avoid. Then address his underlying need: what *can* you show the board at week 6 that is not a slide?

Do not accept the premise that the board story must be about WS2. If Wave 1 has a credible story, make it. If it does not, say so and restructure Wave 1 so it does.

### 2. P2 — Wave 1 coordinator value

Answer Marcus's direct question: what does a coordinator do differently on day 1 of week 9?

If the answer is genuinely "nothing yet," say so — and either (a) restructure Wave 1 to include a coordinator-facing capability, or (b) reframe Wave 1 honestly as infrastructure and defend why that is the right call given the adoption constraint from the recommendation engine failure.

If you restructure: name the specific capability a coordinator touches in week 9 (not shadow mode — something they act on), what it requires to ship, and what gets pushed if you add it to Wave 1.

Do not use "trust-building" as a substitute for a concrete deliverable. Marcus explicitly called out that shadow mode doesn't build trust either way — coordinators don't touch it. If coordinator adoption requires a touchpoint, the touchpoint must exist in Wave 1 or Marcus's challenge stands.

### 3. P3 — Year-1 ROI without facility profiles

Put a number on it. The CFO question is specific: if the agent is HITL-on-every-selection until profiles exist, what is year-1 ROI from credential querying alone?

Build the number from scenario facts and named assumptions:

- Current baseline: 8 coordinators × 120 decisions/day × [coordinator cost per hour] = current annual labour cost for matching decisions
- Agent contribution without facility profiles: time saved per fill on credential querying + shortlist generation (even with coordinator selecting), at [X fills/day]
- Year-1 throughput gain: coordinator capacity freed by removing the database query step, expressed as coordinator-hours reclaimed and converted to dollar value or additional fill capacity
- What autonomous fill would add (Phase 2): name the increment, name the gate (facility profiles), name the honest range for when profiles could be ready

Name every assumption explicitly with confidence level. Do not fabricate a number Marcus gave you — he gave you: 8 coordinators, 120 decisions/day, 4.2-hour fill time, $200M revenue target. Infer what you need to infer; label every inference.

Close this section with a direct answer to the CFO question: year-1 value from credential querying alone is $[X]–$[Y] (range, named assumptions), with facility profiles unlocking an additional $[Z] which is contingent on a [timeframe] data project that should be scoped and owned before Wave 2 go-live.

### 4. What changes in D3 as a result

If any of your responses above result in a revised wave sequence, scope change, or architectural change, name the change and which ADR it affects. Flag it as a D3 revision. Do not silently update the architecture in the D6 response without naming the consequence.

---

## Acceptance criteria (all must pass)

- [ ] Every pushback point has a named posture (Hold / Cave / Alternative) — no implicit responses
- [ ] P1 response names specific prerequisites and the risk accepted if compressed — not just "we can try"
- [ ] P2 response answers the exact question: what does a coordinator do differently on day 1 of week 9 — not a restatement of adoption theory
- [ ] P3 response contains a dollar range with named assumptions — not "significant value" or "substantial throughput gain"
- [ ] Every number in P3 traces to scenario facts or is labelled as an assumption with confidence level
- [ ] Any scope change is named with what gets cut or pushed — no free additions
- [ ] Any D3 change is named in §4 — not quietly embedded in the narrative

## Fail signals — do not produce output that contains these

- "We hear your concern" or any variant — Marcus does not want acknowledgement, he wants answers
- Restating the original design without addressing the specific challenge — a P1 response that re-explains wave sequencing without answering whether week 6 is possible
- Year-1 ROI expressed as "improved efficiency" or "coordinator capacity freed" without a dollar figure — Marcus's CFO question requires a number
- Caving on P1 without naming what prerequisite gets compressed and what risk is accepted
- Holding on P2 without a concrete answer to what a coordinator does differently in week 9
- Assumptions presented as scenario facts in the P3 calculation
- D3 changes made in §4 that were not set up by the P1/P2/P3 responses — the revision log must follow from the responses, not introduce new decisions
