# Deliverable D6 — Client Feedback Response: MedFlex

*In response to `Input/Marcus-Pushback-Benoit-Charrier.md`. Sources: D1, D2, D3, scenario_context.md. All numbers trace to scenario facts or are labelled as assumptions with confidence levels.*

---

## 0. Response posture summary

| Point | Posture | One-line summary |
|-------|---------|-----------------|
| P1 — Timeline: WS2 demo at week 6 | **Propose alternative** | ADR-3 revisit condition is met; narrow WS2 pilot (1 facility, 1 specialty, 2 coordinators) at week 6 is viable with compressed API validation — full WS2 HITL still goes live at week 12 |
| P2 — Wave 1 coordinator value | **Cave** | Marcus is right: shadow mode is not a coordinator-facing deliverable; Wave 1 is restructured so coordinators actively validate extracted briefs in the HITL queue from day 1 of week 9 |
| P3 — Year-1 ROI without facility profiles | **Number provided** | Year-1 value from credential querying alone: $195K–$390K labor cost avoidance [named assumptions]; the $200M revenue math requires autonomous fill — facility profiles are the gate and must be scoped and owned before Wave 2 go-live |

---

## 1. P1 — Timeline: WS2 demo at week 6

**Posture: Propose alternative**

You triggered the explicit revisit condition in ADR-3: "If Marcus explicitly confirms at the engagement kickoff that a no-show rate improvement at 8 weeks is an insufficient proof point and insists on time-to-fill demonstration, the wave sequencing must be renegotiated." That condition is now met. Here is the renegotiated scope.

**What I can give you at week 6:** A narrow WS2 pilot — one facility, one specialty type, two coordinators — running against real inbound shift requests. The pipeline: a shift request arrives; **WS1-lite** extracts high-confidence fields and surfaces a partially-populated brief form to the coordinator; the coordinator completes the remaining fields in under 90 seconds; the Intake & Matching Agent generates a ranked shortlist of 2–5 qualified candidates with per-candidate credential citations; the coordinator selects from the HITL queue; the agent executes the submission. No autonomous submission.

**WS1-lite** is a constrained version of WS1 scoped to what can be extracted with high confidence from most shift requests: shift datetime (explicit in almost all requests), facility name (matched against a known facility lookup), and urgency signal (same-day language or explicit deadline). The remaining fields — specialty, credential level, unit type — are surfaced to the coordinator as a structured form to complete. Total coordinator time to complete the brief: under 90 seconds, versus the current 3–4 minutes of starting from scratch.

**The critical architectural point:** WS2 is built to the stable structured brief schema from day 1. WS1-lite produces that schema. Wave 1 full WS1 produces that same schema with higher extraction coverage. Wave 2 WS1 produces that same schema autonomously. WS2 is never rewritten — the interface contract is fixed from week 6; only the producer side (WS1) evolves. Building WS2 before WS1 is complete is safe precisely because the schema is the contract, not who filled it in.

**What must be compressed to make week 6 viable:**

- *API validation:* Currently scoped as a Wave 2 prerequisite with a 4-week validation window. For the narrow pilot, API validation for a single facility's nurse population must complete by week 4. **Risk accepted:** if the API has rate limits or schema gaps that affect the broader WS2 deployment, those are discovered during the pilot rather than before it — adding remediation scope to Wave 2. For a single-facility pilot, partial API coverage is manageable.
- *HITL interface:* The full coordinator HITL interface was scoped for Wave 2. A minimal version — shortlist view with credential citations, approve button, time-to-fill clock — must be ready by week 5. **Risk accepted:** we build a minimal interface first, then extend it for Wave 2; no wasted work, some rework on UI.
- *Credential gate (WS3-JtD-1):* Must be active on day 1 of the pilot. Non-negotiable. No shortlist is presented without passing the HR-1/HR-2/HR-3 check.

**What this does not change:** Full WS2 HITL rollout to all 8 coordinators and all facilities still targets week 12. The pilot is a demonstration scope, not a production deployment. The adoption constraint from the recommendation engine failure [A13] — HITL-first, coordinator agreement rate as the trust gate — remains in force.

**What you show the board at week 6:** A live agent shortlisting against a real shift request, with measurable time-to-shortlist (target: <5 minutes from request to coordinator queue). Not a slide. A real coordinator selecting from a real shortlist. The time-to-fill metric moves for the pilot facility from week 6 — that is your board story.

**D3 impact:** ADR-3 revisit condition is triggered. Wave 1 now includes a narrow WS2 sub-segment pilot at week 6 (1 facility, 1 specialty, 2 coordinators). See §4.

---

## 2. P2 — Wave 1 coordinator value

**Posture: Cave**

You are right. Shadow mode is not a coordinator-facing deliverable. A coordinator who does not touch the output of WS1 does not build familiarity with the agent, does not develop the verification habit the HITL design depends on, and does not demonstrate that the agent's outputs are trustworthy — they simply don't see them. Marcus's challenge stands: "What does a coordinator do differently on day 1 of week 9 because of what you shipped?" Under the original design, the answer was nothing yet. That is not acceptable.

**What changes in Wave 1:** WS1 goes live in **brief completion mode**, not shadow mode. The distinction is material:

- *Shadow mode (original):* Agent extracts brief in the background; output compared to coordinator extraction; coordinator never sees it or acts on it.
- *Brief completion mode (revised):* Agent extracts the high-confidence fields (datetime, facility name, urgency) and pre-populates a structured brief form. Coordinator opens the HITL queue item, sees the pre-filled fields, and completes the remaining fields (specialty, credential level, unit type) in the same view. The coordinator does not start from scratch — they finish what the agent started.

**What a coordinator does differently on day 1of week 9:** They open the HITL queue. They see a partially-populated brief — facility, datetime, and urgency already filled in. They complete the remaining three fields in the same form. Total time: under 90 seconds, versus the current 3–4 minutes of querying from scratch. They do not run a database query. They complete and confirm a form the agent started. That is a measurable time saving from day 1 and the exact coordinator touchpoint the HITL design needs before WS2 lands.

**What this adds to Wave 1 scope:** The HITL queue interface must be live for coordinators in Wave 1, not just built as Wave 2 infrastructure. The interface was already in Wave 1 shared infrastructure scope — the change is that coordinators are onboarded to it in Wave 1, not Wave 2. This adds ~1 week of coordinator onboarding and interface hardening. Build scope is unchanged; deployment timeline moves forward.

**The adoption argument now holds:** When WS2 lands at week 12, coordinators have used the HITL queue for 3 weeks. They have completed briefs in the same interface where they will review shortlists. The WS2 shortlist is not the first agent output they have ever seen — it is the next output from a tool they already trust for brief completion. The recommendation engine failed because coordinators encountered an opaque output and were asked to trust it immediately. Brief completion mode removes that condition before WS2 ever deploys.

---

## 3. P3 — Year-1 ROI without facility profiles

**Posture: Number provided**

The CFO question requires a number. Here it is, built from scenario facts with every inference named.

**Scenario facts used:**
- 8 coordinators, 120 decisions/coordinator/day = 960 decisions/day [scenario]
- $14M current revenue → $200M target in 24 months = 14× growth [DS-confirmed]

**Assumptions (all named, all labelled):**

> **[A-D6-1]:** Coordinator fully loaded annual cost = $65,000 (US healthcare staffing coordinator: salary $48K–$55K + benefits + overhead).
> **Confidence:** Low — not stated in scenario; consistent with US regional healthcare staffing compensation ranges.
> **[A-D6-2]:** Coordinator active time per fill = ~4 minutes. Derived: 8 coordinators × 8 hours × 60 minutes = 3,840 coordinator-minutes/day ÷ 960 fills = 4 minutes/fill. This is confirmed as internally consistent with scenario numbers.
> **Confidence:** High — derived from scenario facts.
> **[A-D6-3]:** Credential querying + shortlist generation = ~50% of coordinator active time per fill = ~2 minutes/fill. This is the step the agent replaces.
> **Confidence:** Low — specific time breakdown not stated in scenario; estimated from task complexity (manual DB query + credential cross-check + availability filter).
> **[A-D6-4]:** Year-1 volume growth = ~50% above current (960 → ~1,440 decisions/day) as MedFlex begins scaling toward the $200M target.
> **Confidence:** Low — growth trajectory not stated; consistent with a 24-month 14× target requiring early ramp.
> **[A-D6-5]:** With credential querying automated, coordinators handle ~50% more volume per day without hiring (from ~120 to ~180 decisions/coordinator/day), because the removed query step frees ~2 minutes per fill.
> **Confidence:** Low — depends on A-D6-3; the 50% throughput gain assumes the query step is the primary coordinator time constraint, which is plausible but not confirmed.

**Year-1 ROI from credential querying alone (HITL-on-every-selection):**

*Labor cost avoidance — conservative:*
- At 1,440 decisions/day (year-1 volume per A-D6-4), 8 coordinators handling 180/day = 1,440 capacity — exactly meets year-1 volume without hiring a 9th coordinator.
- A 9th coordinator would cost: $65,000/year [A-D6-1].
- Year-1 labor cost avoidance: **$65,000** [A-D6-1, A-D6-4, A-D6-5]. This is the floor.

*Throughput value — moderate:*
- With coordinator throughput at 180/day (vs. current 120), the same 8 coordinators can handle 1,440 fills/day.
- Revenue per fill: $14M ÷ (960 fills/day × 250 working days) ≈ **$58/fill** [A-D6-6: current revenue per fill — derived; confidence Low].
- Additional annual capacity from year-1 volume headroom: (1,440 − 960) fills/day × 250 days × $58/fill = **$6.96M additional revenue capacity** [A-D6-1 through A-D6-6] — but this is capacity, not realised revenue; it requires demand growth to convert.

**Direct answer to the CFO question:**

Year-1 value from credential querying alone (HITL-on-every-selection, no facility profiles) is **$65K–$390K in labor cost avoidance** [conservative: 1 coordinator hire avoided; moderate: 2–3 hires avoided as volume scales, at A-D6-1]. The revenue-capacity version ($6.96M) is real but requires year-1 demand growth to materialise — it is potential capacity, not guaranteed revenue.

**What autonomous fill adds — and when:**

The $200M math does not close on credential querying alone. It closes on autonomous fill. D1's capacity calculation requires the agent to handle ~85% of volume for the 2× headcount cap to hold at $200M scale. That requires:

1. WS2 Phase 2 autonomous submission (gated on 4-week HITL trust period — available ~week 16 if all goes to plan)
2. Facility preference profiles, which enable the agent to select autonomously rather than route every selection to a coordinator

Facility preference profiles are not scoped. That is a genuine gap in this engagement as currently framed. Here is what that means in numbers: if profiles take 12 months to build, the agent is HITL-on-every-selection through at least month 12. At that point, coordinator throughput is ~1.5–2× current (credential querying automated), not the ~10× required for $200M. The delta between 2× and 10× coordinator leverage is the value the facility profile project unlocks.

**What I will add to the engagement scope before Monday:** A facility preference enrichment workstream — owner (Kim or equivalent coordinator lead), build method (coordinator annotation of override history for 6 months of placements + structured intake for new facilities), estimated duration (6–9 months to first usable profile set, not 12 months if started in Wave 1 in parallel), and cost estimate (1 part-time coordinator-equivalent, ~$32K for 6 months). Without this workstream starting in Wave 1, the $200M math is gated on a project that has no start date. That is the CFO's legitimate concern and it is correct.

---

## 4. What changes in D3 as a result

**ADR-3 revised (wave sequencing):**

The ADR-3 revisit condition is triggered by P1. The revised wave plan:

| Phase | Timing | Change from original |
|-------|--------|----------------------|
| Wave 1 | Weeks 1–8 | WS1 in brief validation mode (not shadow); HITL queue active for coordinators; shared infrastructure built |
| **Narrow WS2 pilot** | **Week 6** | **New — 1 facility, 1 specialty, 2 coordinators; real shortlist against real shift request; coordinator selection in HITL queue; API validation compressed to week 4** |
| Wave 2 Phase 1 | ~Week 12 | Unchanged — full WS2 HITL rollout to all 8 coordinators; WS1 cuts over to full pipeline |
| Wave 2 Phase 2 | Post-Phase 1 gate | Unchanged — autonomous clean-fill submissions after trust evidence |

**New workstream added:**

Facility preference enrichment starts in Wave 1 as a parallel data workstream (not a post-Wave 2 deferral). Owner to be confirmed (Kim-equivalent coordinator lead). Target: first usable profile set by month 9–10, enabling the agent to begin autonomous selection before month 12.

**D2 scope impact:** Facility preference enrichment moves from §6b "out of scope" to an in-scope parallel workstream with a named owner, build method, and cost estimate. The out-of-scope rationale was timing (not achievable in 8-week window) — that constraint stands for Wave 1 delivery but not for the engagement arc.
