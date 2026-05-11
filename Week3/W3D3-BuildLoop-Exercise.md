# W3D3 Afternoon Build-Loop Exercise — Cascade Public Libraries

**Released:** Wednesday afternoon, immediately after the build-review walkthrough.
**Solo work.** Do not collaborate with other participants. AI assistance (Claude / Claude Code / Cursor) is permitted; using AI to think through your classification is the point. Submitting AI's output as your own without diagnosis is not.
**Time budget:** ~2.5 hours (suggested; the exercise has no hard cutoff).
**Submit by:** Wednesday EOD to your squad lead.

---

## What this exercise is

This morning you saw the build-loop diagnostic move applied to the Coffee Subscription Credit Handler. The four categories — spec gap, builder misread, unjustified implementation choice, test/environment issue — and the FDE Response Protocol you saw modelled live, you now apply solo to an unseen fixture in a different domain.

You will be given:

1. A **capability spec** an FDE wrote (the same kind of spec you'll write yourself in Gate 3 Friday).
2. A **build output** a (simulated) builder produced against that spec — eight signals across files, tests, and a builder question.

For each of the eight signals you must produce:

- **Classification:** which of the four categories does it belong to? (Or: is it a legitimate clarification request?)
- **Rationale:** one sentence citing the requirement(s) at issue.
- **Response:** 2–4 sentences in the correct tone for the category, following the FDE Response Protocol from `../Reference/spec-ambiguity-vs-builder-mistakes.md`. Spec revision, direct correction, collaborative removal request, or diagnostic fix — pick the right tone.

This is the same diagnostic move Gate 3's Deliverable #5 (Build-loop response memo) tests. Treat the exercise as preparation for Friday.

---

## The capability spec

The FDE wrote the following capability spec for the build team. Read it once before reading the build output.

> **Capability: Hold Queue Management & Notification — Cascade Public Libraries e-lending platform**
>
> **Context.** Cascade Public Libraries is a regional library system: 18 branches, ~310,000 active cardholders, ebook + audiobook lending via the OverDrive integration. Cardholders place holds on titles that are currently checked out; when a copy returns, the system advances the queue and notifies the next eligible patron. This capability covers hold queue management and the notification flow.
>
> **Patron tiers (relevant to queue logic):**
> - **Standard** — most cardholders. Default queue rules.
> - **Academic** — cardholders registered through the partnership with two state universities. Queue priority weighting (see R5).
> - **Accessibility-priority** — cardholders with a registered ADA hold modifier (visually impaired or print-disabled patrons under the Marrakesh Treaty / federal ADA accommodation). Queue jump (see R4).
>
> A patron can be both Academic and Accessibility-priority (e.g., a visually impaired graduate student). The interaction is not specified — see Assumptions.
>
> **Requirements:**
>
> R1. Each title has a hold queue ordered by hold-placement timestamp (FIFO within tier rules below).
> R2. When a title becomes available (current borrower returns, OR OverDrive catalog refresh adds copies), the system notifies the patron at the front of the queue.
> R3. A notified patron has 72 hours to claim the hold. If unclaimed, the hold expires and the system advances to the next eligible patron in the queue.
> R4. Accessibility-priority patrons jump to queue position 1 when they place a hold, unless another accessibility-priority patron is already at position 1 (in which case standard FIFO applies between them).
> R5. Academic-tier patrons receive a queue weight of 0.5x — their effective queue position is computed as raw_position × 0.5 when comparing against standard-tier patrons.
> R6. Patrons can pause active holds. Paused holds retain queue position but are skipped over when the title becomes available; the next eligible patron is notified instead.
> R7. Patrons can opt-in to auto-checkout. When a hold becomes available and the patron has auto-checkout enabled, the system performs the loan automatically without requiring patron action.
> R8. When an OverDrive catalog refresh adds new copies of a title, advance the queue by the number of new copies (notify the next N patrons).
> R9. Standard patrons may hold up to 5 active titles concurrently. Academic-tier patrons may hold up to 10.
> R10. The loan period is 21 days. Loans auto-return at the end of the period; the title becomes available again and the queue advances.
> R11. Format-distinct holds: if a patron places holds on the ebook and audiobook editions of the same title, the system treats them as two separate holds. Both count toward the active-hold limit.
> R12. Notification channels: email by default. Patrons who registered a mobile number can opt-in to SMS notifications. *(Note: the business has not yet decided whether SMS-opted patrons should receive both email and SMS, or only SMS — flagged in Assumptions.)*
>
> **Assumptions:**
>
> - **Academic + Accessibility-priority intersection** is not specified. Assumed: Accessibility R4 wins (jump to position 1) and the Academic 0.5x weight does not apply when the patron is already at position 1. Pending FDE confirmation.
> - **SMS dual-channel vs SMS-only** is pending business decision (R12).
> - **OverDrive catalog refresh that *removes* copies** (rather than adds) is not specified. Assumed: no queue change.
> - **The definition of "72 hours" in R3** as calendar hours vs business hours (libraries closed Sundays) is not specified. Assumed: calendar hours, but flagged for FDE review.

---

## The build output

The builder (a simulated AI coding agent) produced the following artefacts against the spec. Each signal below appears in the codebase as written. **Read each signal carefully against the spec before you classify.**

### Signal 1 — `notification_deadline.py` (excerpt)

```python
def expire_unclaimed_holds():
    """Run hourly. Expire any hold whose 72-hour notification window has elapsed."""
    cutoff = datetime.now() - timedelta(hours=72)
    for hold in get_notified_holds():
        if hold.notified_at < cutoff:
            expire_hold(hold)
            advance_queue(hold.title_id)
```

### Signal 2 — `accessibility_priority.py` (new file the builder added)

```python
class PriorityWeights:
    """Queue-weight multipliers per patron tier."""
    ACCESSIBILITY = 0.25
    ACADEMIC = 0.5
    STANDARD = 1.0


def compute_effective_position(patron, raw_position: int) -> float:
    """Return the patron's weighted position in the queue."""
    if patron.has_accessibility_modifier:
        weight = PriorityWeights.ACCESSIBILITY
    elif patron.is_academic_tier:
        weight = PriorityWeights.ACADEMIC
    else:
        weight = PriorityWeights.STANDARD
    return raw_position * weight
```

### Signal 3 — `auto_checkout_handler.py` (excerpt)

```python
def handle_hold_available(hold):
    patron = hold.patron
    title = hold.title

    if patron.auto_checkout_enabled:
        loan = create_loan(patron, title, period_days=21)
        send_email(patron,
                   subject="Your hold became available — you've been auto-checked-out",
                   body=loan_summary(loan))
        # Schedule a return reminder 3 days before the loan ends so patrons
        # have a chance to renew or finish reading.
        schedule_reminder(patron,
                          fire_at=loan.return_date - timedelta(days=3),
                          message=f"Your loan of '{title.name}' ends in 3 days.")
    else:
        send_notification(patron, hold)
```

### Signal 4 — `test_overdrive_refresh.py`

```python
def test_overdrive_refresh_advances_queue():
    """Given a refresh that adds 3 copies, the queue should advance by 3."""
    fixture_refresh = load_fixture("overdrive_refresh_2025_q4.json")
    on_overdrive_catalog_refresh(fixture_refresh)
    assert queue_advanced_count() == fixture_refresh.expected_advances
```

The corresponding `overdrive_refresh.py` implementation:

```python
def on_overdrive_catalog_refresh(refresh_event):
    new_copies = refresh_event.added_copies  # dict: {title_id: count}
    for title_id, count in new_copies.items():
        for _ in range(count):
            advance_queue(title_id)
```

*(Note: this test passes when the CI clock is set to 2025; it fails when run in 2026 because the fixture's `expected_advances` field encodes the queue state as it existed in Q4 2025.)*

### Signal 5 — `place_hold.py` (excerpt)

```python
def place_hold(patron, title_id: str, format_type: str):
    """Place a new hold for the patron on the given title in the given format."""
    active_count = count_active_holds(patron)
    limit = 10 if patron.is_academic_tier else 5
    if active_count >= limit:
        raise HoldLimitExceeded(f"Patron {patron.id} has reached hold limit ({limit}).")

    # Reject duplicate holds on the same title
    if patron_has_active_hold_on_title(patron, title_id):
        raise DuplicateHoldError(
            f"Patron {patron.id} already holds title {title_id}.")

    hold = create_hold(patron, title_id, format_type)
    enqueue(hold)
    return hold
```

### Signal 6 — `paused_holds.py` (excerpt)

```python
def handle_title_available(title_id: str):
    queue = get_hold_queue(title_id)
    for hold in queue:
        if hold.is_paused:
            send_email(hold.patron,
                       subject=f"A title you held became available",
                       body="Your hold is paused, so we've skipped over it. "
                            "Resume your hold from your account settings if "
                            "you'd like to be notified next time.")
            continue
        notify_patron(hold)
        return  # only the first eligible patron is notified
```

### Signal 7 — `sms_notification.py` (excerpt)

```python
def send_hold_notification(patron, title):
    """Send the 'your hold is ready' notification on the patron's preferred channel."""
    if patron.sms_opted_in and patron.mobile_number:
        send_sms(patron.mobile_number,
                 f"Your hold for '{title.name}' is ready. Claim within 72 hours.")
    else:
        send_email(patron.email,
                   subject=f"Your hold for '{title.name}' is ready",
                   body=hold_ready_body(title))
```

### Signal 8 — Builder question filed alongside the PR

> **Builder question (filed in PR description, blocking merge):**
>
> *"Question for the FDE before I close this PR. R5 says academic-tier patrons get a 0.5x weight on queue position. R4 says accessibility-priority patrons jump to position 1. The Assumptions section flags this intersection but doesn't fully resolve it.*
>
> *Specifically: if an academic-tier accessibility-priority patron places a hold, do they (a) jump to position 1 (R4 wins, ignore academic weight); (b) get position-1-with-0.5x-weight (which is meaningless because raw position 1 × 0.5 = 0.5, smaller than another accessibility-priority patron at raw position 1 × 1.0 = 1.0, which would mean academic+accessibility-priority always beats accessibility-priority alone — is that intended?); or (c) the academic weight applies only when comparing against another accessibility-priority patron at the same position?*
>
> *I'm holding the PR pending your direction. Tell me which interpretation you want me to implement; I do not want to ship the second interpretation by default — it has weird edge cases."*

---

## What you submit

For each of the 8 signals, produce a short structured entry. Total submission length: ~2 to ~4 pages of markdown. Quality over quantity.

Submission template — copy this and fill in for each signal:

```markdown
### Signal N — [one-line label, e.g., "72-hour notification window"]

**Classification:** [spec gap | builder misread | unjustified implementation choice | test/environment issue | legitimate clarification request]

**Rationale (1 sentence with citation):** [Cite R-numbers from the spec, or the Assumptions section, or specific lines of the build output.]

**Response (2–4 sentences in the correct tone):**

[Your response here. Use the FDE Response Protocol from `../Reference/spec-ambiguity-vs-builder-mistakes.md`:
- Spec gap → spec revision in your own voice ("I should have specified X. Updating R3 to say…")
- Builder misread → direct correction, professional, not punitive ("R4 specifies position-1 jump, not weighted. Please change accessibility_priority.py to…")
- Unjustified implementation choice → collaborative removal request ("Appreciate the thinking on the return reminder, but the spec doesn't ask for it. Please remove unless we agree to add it explicitly. If you think it's worth keeping, file a spec change…")
- Test/environment issue → diagnostic fix ("The test is date-bound to 2025 fixture data. Either regenerate the fixture for the current quarter or refactor to mock the catalog state…")
- Legitimate clarification → acknowledge + revise + confirm ("Good catch. Updating Assumptions and R4 to specify…")]
```

**At the end of your submission, add a 1-paragraph reflection** (~100–150 words) on the diagnostic move that was hardest for you and what you'd do differently if you ran this exercise again. This reflection is required and is read closely.

---

## Hints (use sparingly)

- **Read each signal twice before classifying.** Most missed classifications come from stopping at first impression.
- **Always run the ownership question:** *"If this is wrong, whose artefact needs to change — the spec, the code, or the test?"* Each category has a different owner and a different response tone.
- **Watch for second-order traps.** A signal that looks like one category may be another once you read the spec alongside the code. Signal 1 in particular: read R3 carefully.
- **Two of the eight signals are in the same category.** Don't force category-uniqueness across the eight.
- **One signal is a legitimate clarification request, not a failure.** The right response is acknowledgement, not correction.

---

## What this exercise tests (so you can self-assess)

You are not graded on this, but the diagnostic move is exactly what Gate 3 Deliverable #5 grades. After you submit, compare your classifications against your own gut response from the morning walkthrough — did you apply the move with the same discipline on unseen material, or did you slip back into surface-level classification?

The morning walkthrough gave you the vocabulary. The afternoon exercise is whether you can use it without a coach in the room.

---

*Cascade Public Libraries scenario is a Week 3 fixture only. It does not appear in Gate 3 (which uses MedFlex healthcare staffing) or in any other gate. Do not reuse this scenario in any submitted deliverable.*
