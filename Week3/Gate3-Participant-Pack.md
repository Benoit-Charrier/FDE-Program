# Gate 3 — Participant Pack (MedFlex Engagement Simulation)

**Gate:** Gate 3 (Week 3) — Engagement Simulation: discovery → architecture → spec → build-loop diagnosis → stakeholder management
**Scenario release:** Thursday Week 3, 10:00 CET (this file, plus Thursday discovery role-play)
**Timed exercise:** Friday 13:30–17:00 CET (3.5 hours). Submissions close at 17:00.
**Friday 09:00 release:** the personalised Marcus Reyes pushback memo for your Deliverable #6 — delivered as `Marcus-Pushback-<YourName>.md`.
**Verbal defense:** ~10 minutes per participant, scheduled 17:50–19:00 CET. Your specific slot is confirmed by your coach.

Read this pack end-to-end Thursday morning. Then go into the discovery role-play with questions ready. Most of the gate work happens in the spec writing Thursday afternoon; Friday is build-loop response, client-feedback handling, validation, and self-spec reflection — under exam conditions.

---

## 1. What Gate 3 is testing

Gate 3 integrates Weeks 1 and 2 into a single end-to-end engagement. It tests whether you can:

- Frame the real problem under a stated request that's only half right.
- Run discovery against a time-pressured CEO who answers some things precisely, others vaguely, and contradicts himself on at least 2 points.
- Design an agentic architecture where agents are the *mechanism*, not a feature label on a deterministic system.
- Write production-grade specifications precise enough for an AI coding agent to build from without guessing at intent.
- Diagnose build-loop signals against the spec that produced them — distinguishing spec gap / builder misread / unjustified implementation choice / test-environment issue (Week 3 vocabulary from `../Reference/spec-ambiguity-vs-builder-mistakes.md`).
- Hold scope discipline under client pushback — without caving and without alienating.
- Reflect honestly on what your own spec produced when you ran it through Claude Code.

The detailed scoring rubric is held by your coach. You'll see your scores after the gate. Focus on the deliverable expectations in §6 and the broad framing here.

Six things distinguish Gate 3 from Gate 2:

- **Multi-day arc.** Discovery role-play (Thursday morning), spec drafting (Thursday afternoon, interim due 23:59), pushback handling (Friday morning), build-loop diagnosis + finalisation (Friday afternoon).
- **Scenario contradicts itself in places.** That's intentional — see §5.
- **9 deliverables, not 7.** Including a self-spec reflection (Deliverable #9) where you run your own spec through Claude Code under exam conditions.
- **Two assets that arrive mid-engagement:** Wednesday afternoon's simulated build output (you diagnose it in Deliverable #5) and Friday morning's personalised Marcus Reyes pushback memo (you respond to it in Deliverable #6).
- **The CEO has seen two failed AI projects.** Your framing has to clear that scepticism.
- **Verbal defense probes a specific architectural decision plus one acknowledged weakness** — not a freeform discussion.

---

## 2. The week's choreography

| When | What | Who delivers it |
|---|---|---|
| Wednesday 09:00–10:30 CET | Whole-cohort build-review walkthrough (Coffee Subscription fixture — different domain, models the diagnostic move) | Coach team |
| Wednesday 10:30+ | Solo build-loop exercise released — `W3D3-BuildLoop-Exercise.md` (Cascade Public Libraries Hold Queue, 8 signals). Submission due Wed EOD. | You (solo work) |
| **Thursday 09:00** | **This scenario released.** Read this pack end-to-end. | You |
| Thursday 09:30–10:30 | Live discovery role-play with Marcus Reyes (your assigned coach in character). 60 minutes. | Coach as Marcus |
| Thursday afternoon | Solo discovery synthesis + Deliverables #1, #2, #3 (problem framing, intake & scope, architecture + ADRs) drafted | You |
| **Thursday 23:59** | **Interim submission** — Deliverables #1, #2, #3 (drafts) submitted to your squad lead. Rough is fine; this is not graded. It's the input to Agent #1 — generates your personalised Friday morning Marcus pushback memo. | You |
| Friday 09:00 | **Marcus Reyes pushback memo delivered to you** — `Marcus-Pushback-<YourName>.md`. ~300–500 words, Marcus's voice, three pushback points (typically: timeline + scope/architecture + stakeholder/operational). You incorporate response into Deliverable #6 by 17:00. | Coach team (via Agent #1) |
| **Friday 13:30–17:00** | **Gate 3 timed exercise.** Final 9-deliverable submission. | You |
| Friday 17:50–19:00 | Verbal defense (10 min per participant; 5-min stagger). | You + coach |

**Note:** Wednesday's build-review walkthrough (Coffee Subscription) and Wednesday afternoon's solo exercise (Cascade Public Libraries) are in domains *different from MedFlex*. They model the diagnostic move on simpler problems. Friday's Deliverable #5 references the Cascade Public Libraries simulated build output (the artefact you diagnosed Wednesday afternoon), not a MedFlex one — the diagnostic skill is what's being tested across domains.

---

## 3. The MedFlex scenario

> **MedFlex** — healthcare staffing agency, 200 employees, 5-state US region. B2B with hospital systems and B2C with travel nurses.
>
> ### Current operations
>
> - **Hospitals submit shift requests** via email, portal, or phone.
> - **8 coordinators manually match nurses to shifts** based on credentials, proximity, availability, hospital preferences, nurse preferences.
> - **Compliance verification** — license checks, background, training certifications — done manually against state regulatory databases.
> - **~120 shift-matching decisions per coordinator per day.**
> - **Average time to fill: 4.2 hours.** Target: under 1 hour.
> - **Mismatch rate (wrong credentials for facility type): 7%.**
> - **No-show rate: 12%.**
>
> ### Your stakeholder — Marcus Reyes, CEO
>
> Just closed Series B. Board wants significant growth on the horizon of in 24 months. Two failed AI projects already (a chatbot hospital staff rejected; a recommendation engine nobody used). Background: operations + growth, not engineering. Tone: confident, time-pressured, results-oriented. Cuts off rambling questions. Respects FDEs who challenge framing with substance. 
>
> ### Engagement framing
>
> *"10x the business without 10x-ing the coordinators"* — in 8 weeks.
>
> ### What's in scope
>
> Design the agentic transformation of MedFlex's matching + compliance + coordination workflow. Architecture, agent decision points, capability specifications, ADRs, validation plan, build-loop response. Deliverables in §6.
>
> ### What's out of scope (named explicitly so the gate doesn't drift)
>
> - Building a hospital-facing portal for shift submission. They submit by email/portal/phone today; your engagement does not change that channel.
> - Building a nurse-facing mobile app. Nurses today are reached by phone, SMS, or email; same.
> - Pricing engine / margin optimisation. The agent matches; the pricing remains MedFlex's existing process.
> - Continuing-education renewal automation for nurses. Not in v1.
>
> **You are the FDE. Marcus is your point of contact through the engagement. Go.**

---

## 4. Discovery role-play (Thursday 09:30–10:30)

**60 minutes. Squad-based. Coach plays Marcus Reyes.**

Marcus will:
- Answer some questions precisely (top-line operational numbers, board pressure, two prior AI failures).
- Defer some questions to people who don't materialise during the session ("That's a Kim question," "Talk to Aaron in IT," "Linda handles compliance").
- Plant 2–3 deliberate contradictions during the session. Your job is to notice and follow up. He will not flag them himself.
- Push back on premature solutioning ("That sounds like a chatbot. We tried that.").

**The contradictions are the discovery test.** A strong squad catches at least 2 of 3. A weak squad accepts the surface answers and proceeds.

Sample contradictions you may encounter (these are illustrative; the actual ones may differ):

- *"Our app is the source of truth for nurse availability"* — but later, *"When a nurse calls in sick they call Kim, and Kim updates the schedule by hand."*
- *"All credentials are verified before the nurse joins our roster"* — but later, *"When a credential lapses we get a state regulatory ping and we re-verify within a week."*
- *"The 7% mismatch rate is hospital-flagged dissatisfaction"* — but later, when asked how the agent should determine quality, *"We have a quality score. Trust me, it's reliable."*

**When you catch one,** call it out as Marcus would expect — directly, without grandstanding. Marcus will respond as a real CEO would (acknowledge it, defer the resolution to "the engagement").

**Information posture you can expect:** Marcus knows executive-layer facts (revenue, growth target, board pressure, top-line operational numbers). He does *not* know operational detail (workflow specifics, system internals, root causes). He will defer those to "Kim" (senior coordinator), "Aaron" (IT), "Linda" (compliance), or "operations" — without making those people available during the session.

**Coach observers** will note (privately, not surfaced in real-time):

- Strong moves you make (caught contradiction, asked discriminating question, distinguished preventable from latent failure modes).
- Generic questions that could have been written without reading the brief.
- Whether the squad's discovery work shaped the architecture you propose Friday.

**At minute 55, the coach breaks character for a 5-minute debrief** — citations to specific exchanges. This is coaching, not assessment; the squad is not scored on the role-play itself.

---

## 5. Mid-engagement assets you should expect

### 5.1 Wednesday afternoon's simulated build output (Cascade Public Libraries)

Released as `W3D3-BuildLoop-Exercise.md` Wednesday at the close of the morning walkthrough. Different domain (library hold queue, not MedFlex staffing). 8 signals + 4 diagnostic categories. You diagnosed it Wednesday afternoon and submitted to your squad lead by Wednesday EOD.

**On Friday this Wednesday work re-surfaces as Deliverable #5 — the build-loop response memo.** Your Friday Deliverable #5 references the Cascade Public Libraries fixture, not a MedFlex one. You're being assessed on the diagnostic move (across domains), not on MedFlex-specific debugging.

### 5.2 Friday 09:00 — Marcus Reyes pushback memo

After you submit your Thursday EOD interim (Deliverables #1, #2, #3), the coach team runs an automated pipeline overnight that generates a **personalised Marcus pushback memo** for you — `Marcus-Pushback-<YourName>.md`, delivered Friday 09:00.

The memo will be ~300–500 words in Marcus's voice. It will contain **2–3 specific pushback points**, typically:

- **One timeline pushback** ("Board moved up. Can we do it in 6 weeks?" or "Phase 0 sounds like two weeks doing nothing. Cut it.").
- **One scope/architecture pushback** ("Cut credential verification — compliance can keep doing that manually" or "Why not use a workflow tool instead of agents?").
- **One stakeholder/operational pushback** ("We hired McKinsey two months ago — coordinate with them" or "CFO needs a year-1 number" or "Kim said your design doesn't match how she works").

**The pushback points are tied to the specifics of YOUR Thursday submission.** If you proposed a 14-week phased plan, the timeline pushback will compress to 6–8 weeks. If you cited Kim as your design partner, the stakeholder pushback may be from CFO or compliance instead.

**You incorporate your response into Deliverable #6** by 17:00 Friday. See the §6 deliverable description and the C5 calibration in §7.

---

## 6. Deliverables (9 items)

You submit these as a single package by Friday 17:00 CET. Markdown, one folder, file names per the table.

| # | Deliverable | Filename suggestion | What strong looks like |
|---|---|---|---|
| 1 | **Problem framing & success metrics** | `01-problem-framing.md` | "10x without 10x-ing" decoded into architectural requirements (e.g., "agent must hold N concurrent coordinator decisions/min"); measurable success metrics for MedFlex, hospitals, nurses. |
| 2 | **Engagement intake & scope** | `02-intake-scope.md` | Business context, stakeholder map, constraints, risks, MVP scope, **concrete out-of-scope list with rationale** (don't lift §3's out-of-scope verbatim — interpret it for what your engagement specifically defers). |
| 3 | **Agentic solution architecture** | `03-architecture.md` | Specific agent decision points where contextual reasoning determines outcomes a rule-based system couldn't reach. Delegation archetypes per workflow. **Minimum 2 ADRs**: alternatives + consequences + revisitation conditions. |
| 4 | **Two production-grade capability specifications** | `04a-capability-spec-<name>.md` and `04b-capability-spec-<name>.md` | Precise enough for Claude Code to build from without guessing at intent. **Shared entities consistent across both specs** (one glossary, not two). Worked examples for edge cases. Marked assumptions named with confidence levels. |
| 5 | **Build-loop response memo** | `05-build-loop-response.md` | References the Wednesday-afternoon simulated build output (Cascade Public Libraries fixture). Each of the 8 signals classified into the right category (spec gap / builder misread / unjustified implementation choice / test-environment issue) with response in correct tone for each category. **Read the spec alongside the code; don't stop at first impression.** |
| 6 | **Client feedback response** | `06-client-feedback.md` | Friday morning's Marcus pushback memo loaded; **each pushback point addressed concretely**. Hold scope discipline; if you cave on one point, name what gets cut. If you decline, propose a concrete alternative. |
| 7 | **Validation plan** | `07-validation-plan.md` | Accuracy + edge cases + failure modes + compliance risk. State portal rate limits, regulatory drift, model accuracy drift, single-points-of-failure — all named with mitigation strategies. |
| 8 | **Reflection document** | `08-reflection.md` | Honest assessment of what would change with more time; specific lessons. Not generic. |
| 9 | **Self-spec build-loop reflection (1 page)** | `09-self-spec-reflection.md` | Take **one of your two capability specs** (Deliverable #4) and run it through Claude Code under exam conditions. Submit a 1-page reflection covering: (a) what Claude Code built and whether it matches your intent, (b) what questions it asked or what it said it couldn't build, (c) your diagnosis of each gap (spec ambiguity / builder misread / unjustified addition / test-environment issue), (d) what you would change in the spec if you had another 30 minutes. **Graded on diagnosis quality, not code correctness** — a spec that produced a broken build but was diagnosed honestly and precisely scores higher than one that produced working code by accident. |

---

## 7. Scoring

The detailed rubric — criteria, weights, thresholds, and scoring anchors — is held by your coach and not shared with participants from Week 3 onward. You receive your scores after the gate.

This is deliberate. We've found participants who see the rubric tend to optimise their submissions toward it (often with AI assistance) rather than toward the work the rubric is trying to measure. The deliverable expectations in §6 and the verbal defense format in §8 are the canonical guidance for what good work looks like.

If you have questions about whether a given approach is in the spirit of the gate, ask your coach during Tuesday office hours or Thursday afternoon — not on Friday during the timed exercise.

---

## 8. Verbal defense (Friday 17:50–19:00)

**10 minutes per participant. 5-minute stagger.**

| Time | Activity |
|---|---|
| 0:00–0:30 | Coach opens: *"I picked one architectural decision and one weakness. Defend the decision; acknowledge the weakness honestly."* |
| 0:30–4:00 | You defend the architectural decision (3.5 min). Coach probes once if shallow. |
| 4:00–7:00 | You address the weakness (3 min). Coach probes for honesty, not for rescue. |
| 7:00–9:00 | Standard probe — coach picks one: *"The CEO's two failed AI projects — how is yours different?"* OR *"What kills this in production?"* |
| 9:00–10:00 | Brief feedback signal. *"You owned X well; we'll discuss Y at Monday calibration."* No score reveal. |

**The defense is about ownership and judgment under pressure, not memorisation.** A graceful "I noticed that gap during the build-loop reflection and here's what I'd change" answer outscores a "the spec is precisely correct" defense.

---

## 9. How to run the 3.5 hours (Friday 13:30–17:00)

A rough shape that has worked in test runs; adapt as you like.

- **0–20 min — re-orient.** Re-read your Thursday submission (Deliverables #1, #2, #3 drafts) and the Marcus pushback memo (delivered 09:00). List what you'd already changed mentally between Thursday EOD and now.
- **20–60 min — Deliverable #4 (capability specs).** Two specs, shared glossary, worked examples, marked assumptions. Coaches read this deliverable for buildability — don't skimp here.
- **60–90 min — Deliverable #5 (build-loop response).** Open the Cascade Public Libraries simulated build output. Classify each of 8 signals against the spec they were given. Read spec alongside code; don't stop at first impression.
- **90–120 min — Deliverable #6 (client feedback) + Deliverable #3 finalisation.** Address Marcus's pushback points one at a time. Hold or cave with explicit naming. Update Deliverable #3's ADRs if the pushback exposed a weakness (this is normal; flag it as a revision).
- **120–145 min — Deliverable #7 (validation plan) + Deliverable #2 (intake & scope finalisation).** Failure modes named with mitigation. Concrete out-of-scope list per §3.
- **145–175 min — Deliverable #9 (self-spec reflection).** Open Claude Code. Run one of your specs from Deliverable #4. Watch what happens. Diagnose honestly. The 30-minute clock is real. Don't run both specs.
- **175–195 min — Deliverable #8 (reflection) + Deliverable #1 polish.** Reflection should be specific, not generic.
- **195–210 min — Final pass.** Hunt for AI-as-feature drift, cross-spec inconsistency, "mostly got it right" language in #9, missing out-of-scope list in #2, validation happy-path-only in #7.

A weak deliverable can sink the whole submission even when the others are strong, so spend your final pass triaging the weakest deliverable rather than polishing the strongest.

---

## 10. Cross-references

| File | Use |
|---|---|
| `README.md` | Week 3 calendar and prereqs |
| `W3D3-BuildLoop-Exercise.md` | Wednesday afternoon build-loop fixture (Cascade Public Libraries). Your Friday Deliverable #5 references this. |
| `../Reference/spec-ambiguity-vs-builder-mistakes.md` | Build-loop diagnostic taxonomy. Be fluent before Friday. |
| `../Reference/discovery-questioning-patterns.md` | Reference for Thursday role-play preparation and post-debrief. |
| `../Reference/production-spec-checklist.md` | Cross-check Deliverable #4 buildability before submission. |
| `../Reference/Thinking-Discipline-Primer.md` | Useful mental models for the timed exercise. |

---

*Released Thursday Week 3, 09:00 CET. Sealed before that.*
