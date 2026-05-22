# Gate 4 — Participant Pack (Economics, Governance & Platform Strategy)

**Gate:** Gate 4 (Week 4) — Cross-Engagement Thinking: economics, governance, platform strategy, capstone proposal
**Pack release:** Friday Week 4, 12:30 CET (this file opens when the timed exercise begins — Gate 4 is cross-engagement, no sealed scenario; your inputs are participant-chosen from Weeks 1–3 plus the capstone option you already picked)
**Timed exercise:** Friday 12:30–16:30 CET (4 hours). Submissions close at 16:30.
**Capstone defense:** Friday 16:45–18:45 CET, ~14 minutes per participant (5-min pitch + 7-min challenge + 2-min curveball rehearsal). Coaches schedule individual slots; your coach team confirms.

Read this pack end-to-end before you start. The clock begins when you open it, not when you finish reading it — but reading the whole pack first will pay back more than the time it costs.

---

## 1. What Gate 4 is testing

Weeks 1–3 tested whether you can run an engagement: scope it, design it, spec it, defend the design, diagnose its build. Gate 4 zooms out. The question shifts from *"can you write a buildable spec?"* to:

- Can you build a credible economic case a CFO would take seriously?
- Can you govern quality across a portfolio of FDE work — peer reviewing, classifying build signals, deciding what to block at handoff?
- Can you design a platform strategy where each engagement makes the next one cheaper?
- Can you propose a capstone that's ambitious *and* achievable — bounded enough to design + build + demo in 4 days with mock data?

Six things distinguish Gate 4 from earlier gates:

- **Multi-engagement scope.** Gate 4 thinks across engagements; Gates 1–3 lived inside one.
- **Two structured exercises you've never seen** ("The Build Is Running" classifying 9 live build signals; "The Handoff" reviewing a partner team's spec).
- **A capstone proposal** that's the gate to Week 5 — coach approval is binary regardless of overall numeric score.
- **A 2-minute curveball rehearsal** at the end of the live defense — explicit practice for the Week 5 Final Exam where curveballs are graded.
- **7 deliverables, not 9.** Different shape from Gate 3.
- **Multi-model thinking is encouraged.** Your economic case should reason about *when* to use which model (Haiku vs. Sonnet vs. Opus, cross-provider alternatives), not just default to one.

---

## 2. The week's choreography

> **If you're on the v4.2-Accel overlay:** the cadence below describes v4.2 mainline (Gate 4 timed window on Friday afternoon, capstone proposal as Friday-in-window or Thursday-23:59 visibility). Your Accel calendar — **Gate 4 Thursday, D#6 (capstone) locked Wednesday EOD as the *graded* version, no Friday gate** — overrides this. Follow your overlay's `Participants/Week4/README.md` for the canonical Accel calendar. §3 (deliverables), §4 (capstone-approval binary gate), and §6 (scoring policy) below all still apply to you unchanged; only the timing differs.

| When | What | Who delivers it |
|---|---|---|
| Monday Week 4 | **Extended 90-min orientation.** Part 1 (60 min): standard week framing. Part 2 (30 min): live discovery questioning rehearsal — coach plays a stakeholder from a practice scenario; you practise asking questions whose answers would change your design. Not graded. | Coach team |
| Tuesday Week 4 | Solo work — peer review portfolio (reviewing 2 specs from Week 3) + start the token economics model | You |
| Wednesday Week 4 (morning) | **"The Build Is Running" exercise.** Open `the-build-is-running-scenario.md`. Classify 9 live build signals against the four-category taxonomy (spec ambiguity / builder mistake / unjustified addition / test-or-environment issue). 3.5h focused work. Submit to squad lead by **Wednesday 23:59 CET**. | You (solo) |
| Wednesday Week 4 (afternoon) | Per-squad coach checkpoint (30–45 min). In-progress artefact review, not graded. | Coach + your squad |
| Thursday Week 4 (morning) | **"The Handoff" exercise.** Open `the-handoff-partner-spec.md`. Triage findings as Blocker / Concern / Acceptable Difference / Missing. Draft an escalation email to the partner team lead. | You (solo) |
| Thursday Week 4 (afternoon) | Capstone proposal finalisation. Proposal due to squad lead by **Thursday 23:59 CET**. | You |
| **Friday Week 4 (12:30 CET)** | **Gate 4 pack released — this file** (no sealed scenario; cross-engagement gate). Read end-to-end. Final 4-hour timed exercise begins. | You |
| Friday Week 4 (16:30 CET) | Submission cutoff. Coach review window begins. | — |
| Friday Week 4 (16:45–18:45 CET) | **14-minute capstone defense per participant.** Includes 2-minute curveball rehearsal (not graded). | You + coach |

**Why the Wednesday 23:59 and Thursday 23:59 submissions matter** — and what they aren't. These are *coach-visibility inputs*, not separately graded artefacts:

- **Wednesday 23:59** feeds the Wednesday-afternoon squad checkpoint. Your coach reads your in-progress "Build Is Running" classifications and any other drafts you have ready, and uses them to flag misclassifications, missing taxonomy signals, or scope drift **before** Friday's timed window — while you still have a full day to act on the feedback. The actual grade is read off your Friday 16:30 version. The Wednesday submission is the *price of admission* for the afternoon coach checkpoint to be useful — a coach can't usefully review nothing.
- **Thursday 23:59** is the capstone-proposal scope-flag checkpoint. Your coach reads the draft to flag unbuildable or trivially-simple capstone scope **before** you commit hours of Friday's timed window polishing a proposal that won't pass the binary approval gate. Coaches typically email scope flags Friday morning so you arrive at the 12:30 timed window with course-correction guidance in hand. The actual grade — and the binary capstone-approval gate — runs against your Friday 16:30 version.

Neither submission is separately scored. If you submit nothing on Wednesday 23:59 or Thursday 23:59, your squad lead flags it; you are not docked points at the gate, **provided your Friday 16:30 submission is solid.** What you lose by skipping these is the early-warning signal, not marks — the squad lead can't course-correct what they haven't seen. The full per-deliverable origin and revision table is in §3.1 below.

**Note on Thursday holiday shift:** Week 4 starts on a physical Wednesday because **Thursday 14 May (Ascension Day)** falls inside the virtual week. Your coach team confirms the exact physical date for each Virtual day in Teams General at the start of the week.

---

## 3. The 7 deliverables

You submit these as a single package by Friday 16:30 CET. Markdown, one folder, file names per the table.

| # | Deliverable | Filename suggestion | What strong looks like |
|---|---|---|---|
| 1 | **Token economics model** | `01-token-economics.md` | For one of the Weeks 1–3 scenarios (your choice): baseline human cost, agent cost per case (tokens + tools + HITL), annual saving, build cost, payback period, sensitivity analysis. Token costs derived from public pricing (cite Artificial Analysis or provider pricing pages). Sensitivity analysis stress-tests under conservative assumptions. CFO-defensible payback period with explicit derivation, not a round number. |
| 2 | **Compounding roadmap** | `02-compounding-roadmap.md` | 3-wave implementation plan. Specific platform assets named (e.g., "credential pre-flight from Wave 1 reused as a service for Wave 2 onboarding"). Integration reuse matrix. Wave 2 and Wave 3 cost derived from Wave 1 platform assets, not hand-waved. |
| 3 | **Peer review portfolio** | `03-peer-reviews.md` | Reviews of 2 specifications from Week 3 (your squad lead allocates pairs). Real issues with concrete fixes named against specific sentences in the spec. **Generic praise ("looks good, minor concerns") is the most-marked-down anti-pattern this week.** Aim for 3+ substantive issues per spec. |
| 4 | **Build governance response — "The Build Is Running"** | `04-build-is-running.md` | Classifications for all 9 signals from `the-build-is-running-scenario.md`. Each signal: classification + reasoning + correct response in tone-calibrated form. Same response tone applied to every signal is a failure mode. Response tone differs by category: spec revision (Spec Ambiguity), direct correction (Builder Mistake), collaborative removal (Unjustified Addition), diagnostic fix (Test/Environment Issue). |
| 5 | **Handoff review + escalation email** | `05-handoff-review.md` | Triage of findings from `the-handoff-partner-spec.md` as Blocker / Concern / Acceptable Difference / Missing. Escalation email to the partner team lead in the tone you would actually send — **direct-and-collaborative, not bureaucratic-cold or apologetic-soft**. Find the one thing that actually blocks production; let "different but fine" pass. Over-blocking is just as wrong as under-reviewing. |
| 6 | **Capstone proposal** | `06-capstone-proposal.md` | Full proposal: problem framing, success metrics (measurable), intended approach, **why it's hard enough**, what you expect to learn. **Bounded enough to design + build + demo in 4 days next week with mock data.** This is the binary approval gate — see §4 below. |
| 7 | **Build-loop reflection on a peer spec (1 page)** | `07-peer-spec-reflection.md` | Take ONE of your 2 peer reviews from Deliverable #3. Run that peer's spec through Claude Code under exam conditions. Submit a 1-page reflection: (a) what Claude Code built and what it asked or refused; (b) your diagnosis of each build gap; (c) **which of those gaps your original peer review caught vs missed**; (d) **which findings in your original peer review the build did NOT actually have — your false positives**. Graded on honesty, not coverage. A participant whose peer review missed a critical issue and who *names that gap* in this reflection scores higher than one who bluffs about catching everything. |

**Known gaps are better than hidden gaps.** If you do not have time to fully complete a deliverable, name it explicitly as a scope-out with a concrete plan to resolve. A senior FDE ships under time pressure with known-and-labelled gaps — silent omissions on economics or governance do not earn the same read.

---

## 3.1 — Deliverable origins and Friday-window expectations

Some Week 4 deliverables are drafted earlier in the week and **finalised** in the Friday 12:30–16:30 timed window. Others are produced **fresh** in that window. The final Friday 16:30 submission is what's graded — there are no separate grade events on Wednesday 23:59 or Thursday 23:59. The earlier submissions feed coach visibility and the Wednesday-afternoon scope-check; they are not standalone scored artefacts.

> **What "Fresh Friday" means — and doesn't mean.** "Fresh Friday" = the *artefact* is authored in the timed window. It does NOT mean a new scenario is sprung at 12:30. **Gate 4 is cross-engagement; no sealed scenario is released Friday.** Your inputs are scenarios *you* have already worked with — your Weeks 1–3 scenarios (you pick which) plus the capstone option you chose at Gate 4. Specifically for the three "Fresh Friday" deliverables:
>
> - **D#1 (Token economics)** — *Scenario:* one of your Weeks 1–3 scenarios, your pick (typically the one whose volume and process shape you understand best). *Authored fresh in-window:* the actual cost model + sensitivity table. **You should absolutely prep economic thinking during Tue–Thu** — sketch baseline costs, look up current pricing on Artificial Analysis, decide which scenario you'll model — so the 40-min Friday slot is enough.
> - **D#2 (Compounding roadmap)** — same pattern: scenario is your prior-week pick; the 3-wave plan + integration reuse matrix is authored fresh.
> - **D#7 (Build-loop reflection)** — *Scenario:* one of the two peer specs you reviewed in D#3 (your pick, from work you already did Tuesday). *Authored fresh in-window:* the Claude Code run + the 1-page honest reflection.
>
> Prepping economic numbers, integration assets, and which peer spec to run during the week is **expected**, not cheating. What you cannot do is pre-draft the final artefacts and copy them in at 12:30 — `01-token-economics.md`, `02-compounding-roadmap.md`, and `07-peer-spec-reflection.md` should be authored in-window. Notes, scratch calculations, pricing lookups, scenario shortlists you bring in are all fair game.

| # | Deliverable | Origin | What Friday's window does |
|---|---|---|---|
| 1 | Token economics model | **Fresh Friday** (~40 min) | Produce from scratch using public pricing + sensitivity analysis |
| 2 | Compounding roadmap | **Fresh Friday** (~40 min) | Produce 3-wave plan with integration reuse matrix |
| 3 | Peer review portfolio | Drafted Tuesday | Polish for specificity — "looks good" → name the spec span and propose the fix |
| 4 | Build governance ("The Build Is Running") | Drafted Wednesday (submitted Wed 23:59 — coach visibility, not graded standalone) | Polish response tone; re-classify any shaky signals; reconcile against the Wednesday-afternoon checkpoint |
| 5 | Handoff review + escalation email | Triage drafted Thursday morning; escalation email written Friday | Draft the escalation email in the right tone; finalise triage |
| 6 | Capstone proposal | Drafted Thursday (submitted Thu 23:59 — coach scope-flag, not graded standalone) | Revise against Wednesday checkpoint feedback; tighten scope discipline; ensure 5-minute defendability |
| 7 | Build-loop reflection on a peer spec | **Fresh Friday** (~35 min Claude Code run) | Run one peer's spec, diagnose honestly, write 1-page reflection |

**Explicit assessment rules:**

- **The 4-hour Friday window does both** — fresh authorship (D#1, D#2, D#7 — roughly 2 hours combined) and revision of prework (D#3, D#4, D#5, D#6 — roughly the other 2 hours). The §7 hour-by-hour pacing reflects this split.
- **Prework that's strong and unchanged Friday scores at full value.** There is no penalty for not changing it. There is also no bonus for cosmetic last-minute edits. The scoring reads the artefact as you submitted it at 16:30.
- **Prework that's weak and unchanged Friday scores at the weak prework level.** The Wednesday/Thursday rough form is what the coach reads if you don't revise.
- **Capstone proposal (D#6) has a separate binary approval gate** (§4) on top of the numeric scoring. The capstone approval is on the **Friday 16:30 version**, defended in the live 14-min defense window.
- **Wednesday 23:59 and Thursday 23:59 submissions are coach-visibility inputs**, not separately graded. They feed the Wednesday-afternoon checkpoint (D#4) and the Friday-morning revision prep (D#6). If you submit nothing on Wed 23:59 or Thu 23:59, the squad lead flags it, but you are not graded down for it — provided the Friday 16:30 submission is solid.

---

## 4. The capstone proposal — binary approval gate

Deliverable #6 is the most consequential of the 7. Gate 4's pass standard requires **both** (a) numeric score above threshold AND (b) coach approval of the capstone proposal. The capstone-approval gate is binary: a strong overall submission with an unbuildable or trivially-simple capstone fails Gate 4 and must re-scope before Week 5.

**Capstone scenario options (you pick one of three for your Week 5 capstone build):**

- **Option A — Healthcare Claims Processing Transformation**
- **Option B — Enterprise Procurement Intelligence**
- **Option C — Multi-Channel Customer Resolution**

Full scenarios are in `../Reference/capstone-scenario-options.md` — the participant-facing capstone reference (scenarios + deliverable package + defense format). The v4.2 program doc itself is not the right source: it also contains coach-held rubrics for Gates 1–4 and the Final Exam, which are sealed until each gate begins. Pick the option you'll actually defend in Friday's live round. The Capstone rubric is released at the start of Virtual Monday Week 5 alongside your chosen scenario's sealed pack.

**What "ambitious and achievable" means at this gate:**

- **Bounded enough** that a participant with 4 working days, Claude Code, and mock data could deliver a working prototype demonstrating the core thesis.
- **Hard enough** that the participant has to make real architectural decisions — not a rules engine wearing an AI label.
- **Specific enough** that you can name what would make it succeed and what would make it fail.

**Common scope failure modes (the Wednesday checkpoint catches these — by Friday it's too late to re-scope):**

- *Too ambitious:* "design and build a multi-tenant platform with 14 integrations across 3 verticals in 4 days." Coach will not approve.
- *Trivially simple:* "build a chatbot that answers FAQs from a knowledge base." Coach will not approve.
- *Vague:* "explore agentic possibilities for the customer service domain." Coach will not approve — no concrete thesis.
- *Mismatched:* proposal claims agent-led decisions but the architecture is rule-based. Coach probes "what's the agentic decision point?" — if the participant can't answer, capstone fails approval.

If the Wednesday-afternoon checkpoint flagged your scope, you have until **Friday 12:30 CET** (when the Gate 4 pack opens) to revise. Once Friday begins, you defend what you've written.

---

## 5. The 14-minute capstone defense

After submission, each participant gets a **14-minute live defense** scheduled by the coach team (~16:45–18:45 CET window, individual slots).

| Time | Activity |
|---|---|
| 0:00–5:00 | **Capstone pitch (5 min).** You walk the coach through your proposal — problem framing, success metrics, approach, why it's hard, what you expect to learn. Coach stops you at 5:00 even if mid-sentence — pitch discipline is part of the test. |
| 5:00–12:00 | **Coach challenge (7 min).** Coach probes scope, difficulty, economic viability, primary risks. Defend with trade-off reasoning, not by escalating ambition or retreating into hedging. Honest "I don't know yet, here's how I'd find out" beats bluffing. |
| 12:00–14:00 | **Curveball rehearsal (2 min, NOT graded).** Coach introduces one new constraint that invalidates one specific assumption in your design (e.g. *"a regulator just banned automated decisions in this category"* OR *"the client's volume just tripled"* OR *"the named senior expert resigned this morning"*). You have 2 minutes to explain how your design adapts. **No retake, no grade impact, no curveball-pool reveal.** |

**Why the curveball rehearsal exists:** Week 5 grades curveball responses — both at the Capstone defense (Thursday, Gate 5a) and inside the Final Exam (Friday, Gate 5b). v4.2 gives you one low-stakes practice run *here* in Week 4 — so the format is familiar before it counts. The specific curveballs in Week 5 will be different from your rehearsal. **Weight against the rubric is held with your coach** per the same scoring-policy firewall described in §6; what matters for participant prep is that the format is one you've seen.

**Curveball framing — what to expect:** the coach states a constraint as a fact, not a question, then sets the timer. The right response shape is: (a) name what assumption breaks, (b) name what part of the design adapts, (c) name the new trade-off. Two minutes is not enough to redesign — it's enough to demonstrate you can think on your feet about your own design.

---

## 6. Scoring

The detailed rubric — criteria, weights, thresholds, scoring anchors, and the capstone-approval gate logic — is held by your coach and not shared with participants from Week 3 onward. You receive your scores after the gate.

This is deliberate. Participants who see the rubric tend to optimise toward it (often with AI assistance) rather than toward the work the rubric is trying to measure. The deliverable expectations in §3 above and the defense format in §5 are the canonical guidance for what good work looks like.

Two things you can rely on:
- **Capstone approval is binary** and decoupled from numeric score — if your capstone fails approval, you must re-scope before Week 5 starts.
- **The curveball rehearsal is not graded.** It's practice for Week 5. Don't overthink it — coach will be probing whether you *can* think on your feet, not whether you produce an optimal answer.

If you have questions about whether a given approach is in the spirit of the gate, ask your coach during Tuesday office hours or Thursday afternoon — not during Friday's timed exercise.

---

## 7. How to run the 4 hours (Friday 12:30–16:30)

A rough shape that has worked in test runs; adapt as you like.

- **0–15 min — re-orient.** Re-read your peer reviews from Tuesday, your "Build Is Running" classifications from Wednesday, your "Handoff" response from Thursday morning, and your capstone proposal draft from **Thursday 23:59 CET**. List anything you'd already changed mentally.
- **15–55 min — Deliverable #1 (Token economics).** Highest single weight on numeric scoring. Pick one Weeks 1–3 scenario; build the model with public pricing; do the sensitivity analysis. Don't skimp.
- **55–95 min — Deliverable #2 (Compounding roadmap).** 3 waves; integration reuse matrix; cost derivation Wave 1 → Wave 2 → Wave 3. Specific assets named, not "we'll reuse stuff."
- **95–125 min — Deliverable #6 (Capstone proposal) finalisation.** This is the gate-deciding deliverable — make sure the scope discipline is tight, why-it's-hard is articulated, and the proposal reads as defendable in 5 minutes.
- **125–155 min — Deliverable #4 (Build governance) finalisation.** If your Wednesday classifications are sound, this is mostly polish on response tone. If they're not, prioritise re-classification on the signals where the spec-vs-code reading is shaky.
- **155–185 min — Deliverable #5 (Handoff response) + Deliverable #3 (Peer reviews) polish.** Triage the partner spec; draft the escalation email in the right tone; re-read your peer reviews for specificity ("looks good" → "the credential schema in §3.2 doesn't define expiry handling — propose adding [...]").
- **185–220 min — Deliverable #7 (Build-loop reflection on peer spec).** Open Claude Code. Run one of your peer's specs. Diagnose honestly. The 30-minute clock is real. Don't run both.
- **220–240 min — Final pass.** Hunt for: vague peer review language (#3); same-tone responses across the 9 build signals (#4); over-blocking on handoff (#5); capstone scope drift (#6); "mostly got it right" language in #7; missing sensitivity analysis in #1.

**The thing not to skimp on is the capstone proposal (#6).** It's the binary approval gate. A polished economics model can't rescue an unbuildable or trivially-simple capstone.

---

## 8. Multi-model experimentation note

Your token economics case should reason about *when* to use which model, not just default to one. Tools that expose multiple models without changing the primary build workflow:

- **Dial** (`https://chat.lab.epam.com/`) — EPAM's multi-provider chat gateway.
- **Cursor** (optional) — multi-model chat and agent support (Claude, GPT-4o, Gemini, others) via its own subscription.
- **GitHub Copilot** (optional, via EPAM Leap) — multi-model selection in chat and agent modes.

Use any of these to pressure-test prompts across Claude Haiku / Sonnet / Opus and cross-provider alternatives. A 10× cost delta between Haiku and Opus on a step that works fine on Haiku is a real unit-economics finding — and the kind of analysis a client expects you to have done.

**Self-hosted / on-premises models are a valid option in specific cases — but not the default.** Frontier APIs (Claude, GPT-4o, Gemini) are the default for good reason: capability, latency, no capital cost, no ops overhead. **Self-hosted open-source models (Llama, Mistral, Qwen, fine-tuned derivatives on EPAM-managed or client-owned hardware) are typically slower per inference and require ops work to keep healthy** — that's a real cost that participants usually under-count. Consider self-hosted only when at least one of these forces the choice:

- **Data-sovereignty / compliance** that rules out external API providers (regulated verticals, classified workloads, data-residency law).
- **Volume genuinely amortises the capital** at the right point on the curve (typically millions of cases/year for a Sonnet-equivalent workload).
- **Fine-tuning needs** that produce a model the client owns and re-trains on their own data.

If you include a self-hosted scenario in your economics, model the cost shape correctly:

- **API model:** marginal per-token rate × volume + tool calls + HITL. Capital negligible. Latency: fast (frontier-tail).
- **Self-hosted model:** capital amortisation + electricity + cooling + ops overhead. Marginal per-inference near-zero, but **inference latency typically higher than frontier APIs** and ops overhead is non-trivial.

A defended self-hosted choice is graded equally to a defended API choice when one of the three triggers above applies. **"Self-hosted because cheaper at scale"** is a weaker answer if you can't name the crossover volume, the latency tolerance of the workload, and how ops gets handled. **"API by default"** is the right baseline — defend any deviation explicitly.

---

## 9. Cross-references

| File | Use |
|---|---|
| `README.md` | Week 4 calendar, prereqs, and broader framing |
| `the-build-is-running-scenario.md` | Wednesday solo exercise; your Friday Deliverable #4 builds on this |
| `the-handoff-partner-spec.md` | Thursday solo exercise; your Friday Deliverable #5 builds on this |
| `../Reference/discovery-questioning-patterns.md` | Reference for Monday rehearsal preparation and post-debrief |
| `../Reference/spec-ambiguity-vs-builder-mistakes.md` | Build-loop diagnostic taxonomy — be fluent for Deliverable #4 |
| `../Reference/production-spec-checklist.md` | Cross-check peer reviews and your build-loop reflection |
| `../Reference/atx/atx-economics.md` | ATX economics framework for Deliverable #1 |
| `../Reference/atx/atx-scoring.md` | ATX V×V / TCO framework for Deliverable #2 |
| `../Week1/Thinking-Discipline-Primer.md` | Useful mental models for the timed exercise |
| `../Week3/Gate3-Participant-Pack.md` | §7 contains the rubric-visibility policy explanation referenced from §6 above |

---

*Released Friday Week 4, 12:30 CET. Sealed before that.*
