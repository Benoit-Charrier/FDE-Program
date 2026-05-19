# The Handoff: Partner Specification Review
## FDE Accelerated Development Program v4.2 — Week 4

### Context

You've just inherited a specification from a partner team that owns compliance infrastructure. They're building an **Automated Compliance Verification Agent** and want to hand off the specification to your team for implementation. The partner team has set a **48-hour SLA** on your review — typical of real-world handoffs. Your exercise window for this assignment is **Thursday morning of Week 4** (~3 hours of focused work) — pace accordingly.

The spec is professionally written and the intent is sound — verify healthcare worker credentials against state regulatory databases to reduce manual verification work. But you need to assess whether it's implementable, identify any risks, and flag issues that need resolution before work begins.

**Your task:** Review the specification below as you would in real practice. Identify:

1. **Blockers** — Issues that prevent implementation or create unacceptable risk. These stop the work.
2. **Concerns** — Issues that should be flagged and resolved before starting, but might not be hard stops.
3. **Acceptable Differences** — Approaches that differ from how you might have done it, but are reasonable and don't need to be changed.
4. **Missing Considerations** — Critical topics the spec doesn't address that should be obvious for a compliance system.

Document your findings as a structured triage and write an escalation email to the partner team lead (see submission format below).

---

## Specification: Automated Compliance Verification Agent

**Version:** 1.0  
**Owner:** Compliance Infrastructure Team  
**Date:** 2026-04-08  
**Scope:** Verification of healthcare worker credentials for state licensing boards  

---

### 1. Overview

The Automated Compliance Verification Agent (ACVA) is an AI-driven system designed to verify healthcare worker credentials against authoritative state regulatory databases. The system will be deployed by hospital systems, clinics, and staffing agencies to reduce manual credential verification time from an average of 4 hours to under 10 minutes per worker.

**In Scope:**
- Nurses (RN, LPN)
- Physicians (MD, DO)
- Physician Assistants (PA)
- Licensed Counselors (LMHC, LMFT)
- Physical/Occupational Therapists (PT, OT)

**Out of Scope:**
- Medical assistants
- Administrative staff
- Verification of specialty certifications (Board Certification in Cardiology, etc.)

---

### 2. System Inputs and Outputs

#### 2.1 Input: Verification Request

The agent receives a verification request in the following format:

```json
{
  "request_id": "uuid",
  "worker_name": "John Smith",
  "license_type": "RN",
  "state": "CA",
  "license_number": (optional),
  "date_of_birth": (optional),
  "timestamp": "ISO 8601"
}
```

#### 2.2 Output: Verification Result

The agent returns a structured result:

```json
{
  "request_id": "uuid",
  "status": "VERIFIED | EXPIRED | SUSPENDED | NOT_FOUND | ERROR",
  "worker_name": "John Smith",
  "license_type": "RN",
  "state": "CA",
  "license_number": (if found),
  "issue_date": (if found),
  "expiration_date": (if found),
  "disciplinary_record": "NONE | YES",
  "verification_timestamp": "ISO 8601",
  "confidence_score": 0.0 - 1.0
}
```

---

### 3. Verification Process

#### 3.1 Database Access

The agent will query state regulatory databases via:

1. **Primary source:** Official state board APIs (where available)
2. **Secondary source:** Public licensing portals (where API unavailable)
3. **Tertiary source:** FSMB (Federation of State Medical Boards) unified lookup for physicians only

The agent should attempt primary source first, then fall back to secondary.

#### 3.2 Verification Algorithm

1. Parse the input request and validate required fields
2. Normalize the worker name (trim whitespace, convert case)
3. Query the appropriate state board database
4. Match the returned license record to the input
5. Check expiration status and disciplinary records
6. Return result with confidence score (1.0 = exact match, <0.7 = ambiguous)

#### 3.3 Unresolved License Status

For licenses with renewable status but currently expired:

- If expiration_date is within 90 days past: Status = EXPIRED (renewals in progress are common)
- If expiration_date is >90 days past: Status = SUSPENDED
- Agent should note in response whether license is typically renewable in that state

Agent should NOT make determinations about whether a license holder is "allowed to work." That determination is the responsibility of the hiring/credentialing team.

---

### 4. Confidence Scoring

Confidence scores indicate the reliability of the match:

- **1.0** — Exact match on name, license number, and state
- **0.9** — Exact match on license number and state; name matches with minor variation
- **0.8** — Name and license type match; state matches; other fields ambiguous
- **0.7** — Partial match; possible identity ambiguity (e.g., common name, missing DOB)
- **<0.7** — No reliable match; recommend manual verification

---

### 5. Integration Points

#### 5.1 Input Source

The agent will receive verification requests from:

- Hospital credential verification systems (e.g., Verifacts, MedVerify)
- Direct API integration with staffing agencies
- Manual uploads via the compliance dashboard

#### 5.2 Output Destination

Results will be:

- Written to the Compliance Database (schema TBD)
- Surfaced in the Compliance Dashboard for review and audit
- Trigger automated notifications to hiring/credentialing teams (details in separate communication spec)

---

### 6. Performance Requirements

- **Latency:** Results within 2 minutes for 95% of requests
- **Availability:** 99.5% uptime during business hours (8 AM - 6 PM ET, M-F)
- **Throughput:** Support concurrent requests (capacity TBD based on expected volume)

---

### 7. Known Issues and Assumptions

- **State Board API Variability:** Each state board API has different schemas, response times, and availability patterns. The agent should gracefully degrade to secondary sources if primary is unavailable.
- **Name Matching:** Worker name normalization is simple (trim, case conversion). Names with hyphens, accents, or multiple parts may require manual review. The agent should flag ambiguous matches with confidence scores <0.8.
- **Disciplinary Records:** Some states include disciplinary information in the primary API response; others require separate queries. The agent's queries should include disciplinary lookups where the API supports it.
- **Data Freshness:** State board databases are typically updated within 24-48 hours of license changes. The agent should not be used for real-time compliance decisions immediately after reported changes.

---

### 8. Success Criteria

- Agent correctly verifies 95% of licenses in scope
- False negatives (agent says NOT_FOUND when license exists) < 2%
- False positives (agent says VERIFIED for expired/suspended licenses) = 0%
- Manual review required for <15% of requests
- Compliance team sign-off on pilot results before rollout

---

### 9. Out-of-Scope Decisions (For Later)

- Renewal status tracking across all states
- Integration with federal databases (DEA, NPI)
- Specialty certification verification
- Multi-state licensure checks
- Historical license records
- Continuous monitoring of licensed workers post-verification

---

### 10. Specification Acceptance and Sign-Off

This specification requires sign-off from:

- [TBD] Compliance Infrastructure Team Lead
- [TBD] Security and Privacy Officer
- [TBD] Healthcare Operations VP

**Note:** Sign-offs are pending clarification of scope and data handling procedures.

---

## Your Review Assignment

As the FDE, assess this specification against the following evaluation framework:

### Category A: Blockers
These prevent implementation or create unacceptable risk. List any blockers you identify with explanation.

### Category B: Concerns  
Issues that should be flagged and likely resolved before work starts. Might require spec clarification or design decision, but not necessarily a hard stop.

### Category C: Acceptable Differences
Approaches in the spec that differ from how you might have done it, but are reasonable and require no change.

### Category D: Missing Considerations
Important topics the spec doesn't address that should be obvious for a compliance verification system.

---

## Submission Format

Your `05-handoff-review.md` file has two parts in this order: (1) a structured triage of findings, (2) the escalation email you'd actually send to the partner team lead. Together: ~400–500 words.

### Part 1 — Finding triage (~250 words)

Document your findings against the four categories. Cite spec section numbers.

```
OVERALL ASSESSMENT:
[1–2 sentences: implementable? headline risk? timeline impact?]

BLOCKERS (Must resolve before work begins):
1. [Blocker; cite spec section; why it blocks]
2. [Next blocker, if any]

CONCERNS (Should be resolved; likely quick):
1. [Concern + recommended resolution; cite spec section]
2. [Next concern]

ACCEPTABLE DIFFERENCES (No change needed):
- [Difference noted + why it's acceptable]
- [Next difference]

MISSING CONSIDERATIONS:
- [Critical topic not addressed; why it matters]
- [Next missing topic]
```

The triage is your structured thinking — it forces category discipline so you don't drift into "everything is a blocker" or "everything is fine."

### Part 2 — Escalation email to the partner team lead (~150–200 words)

This is the artefact you'd actually send. **Tone: direct-and-collaborative, not bureaucratic-cold or apologetic-soft.** Lead with the headline read; name the load-bearing issue(s); propose a fix path; invite the partner team into the resolution; surface 1–2 real strengths if you noted any.

```
TO: Compliance Infrastructure Team Lead
FROM: [Your name], FDE
RE: ACVA v1.0 Spec Review

[Opening: 1–2 sentences on the overall read. Sound architecture? Headline judgement?]

**[First load-bearing issue, named]** [What's wrong; why it matters; concrete recommendation.]

**[Second load-bearing issue, if needed]** [Same shape.]

[Optional paragraph: smaller clarifications grouped as Concerns rather than separate sections.]

[Optional: 1–2 things the spec gets right.]

[Sign-off: invite a call or next step. Direct, not bureaucratic.]
```

**The email is what's graded for tone.** The triage is the structured thinking that feeds it. Both parts are required: weak triage with strong email is incomplete; weak email with strong triage means you can analyse but not communicate.

---

## Example (Not the full spec; for reference)

If the spec said:

> "The agent will query state databases via API and return results."

You might note:

| Category | Finding |
|----------|---------|
| **Blocker** | No error handling specified if state API is unavailable for >30 minutes. This is a real operational risk. Spec must define fallback behavior and acceptable SLA degradation. |
| **Concern** | API rate limiting not mentioned. If 50 hospitals submit 100 requests/day each, we could hit state API rate limits. Should specify queuing strategy and retry logic. |
| **Acceptable Difference** | The spec assumes human review for confidence scores <0.8. We might have auto-approved <0.85, but <0.8 is defensible and follows standard compliance practice. |
| **Missing** | Data residency requirements. If hospital is in NY and state board has data in CA servers, are there compliance implications? Spec doesn't address. |

---

## Notes for Your Review

- This is a real partner handoff. Treat it professionally but directly.
- Some ambiguities are intentional (scope decisions left for you to clarify).
- The team will use your feedback to refine the spec. Be constructive.
- Consider not just correctness, but implementability, timeline, and operational feasibility.
- Blockers should have clear resolution paths, even if resolution is outside the FDE's scope.

**Begin your review. Use the submission format above — triage first, then escalation email.**
