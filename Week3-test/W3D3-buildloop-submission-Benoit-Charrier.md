# W3D3 Build-Loop Exercise — Cascade Public Libraries
**Submitted by:** Benoit Charrier
**Date:** 2026-05-11

---

### Signal 1 — 72-hour expiry window (`notification_deadline.py`)

**Classification:** Spec gap

**Rationale (1 sentence with citation):** R3 states "72 hours to claim" without defining calendar vs business hours; the Assumptions section explicitly flags this as "pending FDE review" — the assumption is open, not closed, yet the builder proceeded with calendar hours without FDE confirmation.

**Response:**
I should have resolved the 72-hour definition before the build rather than leaving it as an open assumption. The library closes Sundays; a patron notified Saturday evening has a materially different window under calendar hours vs business hours. I need to confirm the business intent with the client. Updating R3 to read: "A notified patron has 72 calendar hours to claim the hold" (or "business hours, excluding Sundays" — pending confirmation). This assumption must be closed before this function ships.

---

### Signal 2 — Accessibility weight multiplier (`accessibility_priority.py`)

**Classification:** Builder misread

**Rationale (1 sentence with citation):** R4 specifies that accessibility-priority patrons **jump to queue position 1** — not that they receive a weight multiplier; the builder invented a 0.25x weight by analogy with R5's 0.5x academic weight, which does not exist in the spec.

**Response:**
R4 is explicit: accessibility-priority patrons jump to position 1, full stop (with FIFO applying only between two accessibility-priority patrons at the same position). There is no 0.25x weight in the spec — that constant was not specified anywhere. Please replace `compute_effective_position` with a placement function that inserts the hold at position 1 on placement, and falls back to FIFO only when another accessibility-priority patron already occupies position 1. The weight-multiplier approach produces incorrect queue ordering for every accessibility patron.

---

### Signal 3 — Return reminder added (`auto_checkout_handler.py`)

**Classification:** Unjustified implementation choice

**Rationale (1 sentence with citation):** R7 specifies automatic loan creation without patron action and R10 specifies the 21-day loan period — neither requirement, nor any other in the spec, asks for a return reminder notification.

**Response:**
Appreciate the thinking — a renewal nudge is a reasonable product feature — but the spec doesn't ask for it, and adding it expands scope without FDE direction. Please remove `schedule_reminder` and the associated comment. If you believe this is worth adding, file a spec change request against R7 and I'll review it as a candidate for a future iteration. Everything else in `handle_hold_available` (loan creation, 21-day period, auto-checkout email) matches the spec.

---

### Signal 4 — Date-bound fixture (`test_overdrive_refresh.py`)

**Classification:** Test/environment issue

**Rationale (1 sentence with citation):** The implementation of `on_overdrive_catalog_refresh` correctly matches R8 (advance the queue by the count of added copies per title); the test fails in 2026 only because `overdrive_refresh_2025_q4.json` encodes queue state that no longer matches current data.

**Response:**
The implementation is correct per R8 — the fixture is the problem, not the code. The `expected_advances` field in `overdrive_refresh_2025_q4.json` is stale; it encoded queue state that existed in Q4 2025 and is no longer accurate. Either regenerate the fixture against current catalog state, or refactor the test to mock `advance_queue` and assert it was called with the correct `(title_id, count)` arguments — decoupling the test from live queue state entirely. Do not modify `on_overdrive_catalog_refresh`.

---

### Signal 5 — Duplicate hold check ignores format (`place_hold.py`)

**Classification:** Builder misread

**Rationale (1 sentence with citation):** R11 explicitly states that ebook and audiobook editions of the same title are treated as two separate holds; the builder's `patron_has_active_hold_on_title` check operates on `title_id` alone, which would reject a patron's second hold on the same title in a different format, directly contradicting R11.

**Response:**
R11 is unambiguous: ebook and audiobook editions are separate holds and both count toward the limit. The current check on `title_id` alone would block a patron from holding both editions of the same title — that is a spec violation. The spec also does not specify any constraint against same-title same-format duplicate holds, so this restriction was added without basis. Please remove `patron_has_active_hold_on_title` entirely. If there is a business reason to prevent same-title same-format duplicates, raise it as a spec change request.

---

### Signal 6 — Email to skipped paused patrons (`paused_holds.py`)

**Classification:** Unjustified implementation choice

**Rationale (1 sentence with citation):** R6 says paused holds are skipped and the next eligible patron is notified — it says nothing about notifying patrons whose paused holds were passed over.

**Response:**
The spec (R6) only requires skipping paused holds and notifying the next eligible patron — it does not request any communication to the patron whose hold was skipped. Please remove the `send_email` block inside the `if hold.is_paused` branch. Note also that as written, the loop sends skip notifications to every paused patron above the first eligible one in the queue, which compounds the scope creep. If the business wants a "you were skipped" notification as a product feature, that needs to be specified explicitly in R6 before building it.

---

### Signal 7 — SMS-only implementation (`sms_notification.py`)

**Classification:** Spec gap

**Rationale (1 sentence with citation):** R12 explicitly flags the SMS channel decision — dual-channel (email + SMS) vs SMS-only — as a pending business decision; the builder resolved the open question by choosing SMS-only without FDE direction.

**Response:**
I should not have left the SMS channel question open at build time — the spec note makes explicit that the business has not decided, which means this assumption should have been closed before the builder touched notification routing. The builder resolved it by choosing SMS-only, which is one valid interpretation but not a confirmed one. I need to get the business decision, then update R12 with the definitive channel policy (e.g., "SMS-opted patrons receive SMS only" or "SMS-opted patrons receive both email and SMS"). Until that decision is made, this function cannot be shipped as-is.

---

### Signal 8 — Builder question: Academic + Accessibility-priority intersection

**Classification:** Legitimate clarification request

**Rationale (1 sentence with citation):** The Assumptions section explicitly flags the Academic + Accessibility-priority intersection as "pending FDE confirmation," and the builder correctly identified that the three possible interpretations produce materially different queue outcomes — blocking the PR rather than guessing is the right call.

**Response:**
Good catch, and exactly the right move to block rather than guess. The Assumptions section did flag this as unresolved, and I should have closed it before the build. The correct interpretation: **R4 wins — the accessibility patron jumps to position 1, and the Academic 0.5x weight (R5) does not apply while the patron is at position 1.** The 0.5x multiplier is irrelevant once the patron is already at the front of the queue. Updating R4 to read: "When a patron holds both Accessibility-priority and Academic status, R4 governs placement (jump to position 1). The Academic queue weight (R5) does not apply when the patron's effective position is already 1." Please implement interpretation (a) and close the PR.

---

### Reflection

Some of the signals like 3 and 6, unjustified implementation or 4, test environment were easier to diagnose than others. Signal 1 could have been the harder one. We saw in the morning a similar signal with the calendar so it helped to spot it. It also seems that any assumptions made or decision pending can create a signal so it would be important to validate the assumptions and decisions and turn them into requirements, or not build that part, or build it in a way that can easily be adjusted when it is confirmed and make a note of it. 

Using AI to help with the diagnostic helps a lot, especially when we don't have the skills to read code, and it looks to me that it is a good use for it. 

In a non-ai world we strived to have good specs, user stories, requirements up front. Depending on the teams, we don't always succeed but we know it is fundamental. None of the specs we've had or created so far seem good enough to me to start development. Using AI to create good requirements and specs is the first step in being more productive and shipping better quality.
 