# Gate 4 D5 — Handoff Review: Automated Compliance Verification Agent v1.0

**Spec reviewed:** `Input/the-handoff-partner-spec.md`
**Spec owner:** Compliance Infrastructure Team
**Reviewer:** Benoit Charrier, FDE
**Review date:** 2026-05-19

---

## Part 1 — Finding Triage

**OVERALL ASSESSMENT:**
Soundly scoped; delegation boundaries are correct. One blocker stops the build; the rest resolve in the same revision pass.

---

**BLOCKERS (Must resolve before work begins):**

1. **§3.1 — No integration contracts for state board APIs.** *(Checklist: Integration Contracts — endpoint, auth, request/response, timeout, retry, and fallback all undefined for every source type.)* The verification pipeline runs entirely on these integrations; §3.2 cannot be implemented without a contract. Fix: two representative contracts (CA BVNPT, NY DOH) plus a template all additional states must complete before going live.

---

**CONCERNS (Should be resolved; likely quick):**

1. **§2.1 + §3.2 — Optional input fields with no matching fallback.** *(Checklist: Entity Precision — conditional criteria incomplete.)* `license_number` and `date_of_birth` are optional but step 4 "match the returned record to the input" defines no name-only matching logic.

2. **§4 + §2.2 — Confidence < 0.7 path has no system behavior.** *(Checklist: Delegation Boundaries — escalation path undefined.)* "Recommend manual verification" is a UI hint; no database write status or escalation route is defined.

3. **§5.2 + §6 — Two untestable requirements.** *(Checklist: Buildability — testable acceptance criteria missing.)* Database schema TBD and throughput capacity TBD cannot be built against.

4. **§3.1 — "Gracefully degrade" is ambiguous.** *(Checklist: Buildability — ambiguous language undefined.)* No fallback decision tree; ERROR response structure undefined.

---

**ACCEPTABLE DIFFERENCES (No change needed):**

- §3.3 — 90-day EXPIRED/SUSPENDED boundary: defensible clinical threshold.
- §3.3 — Agent does not determine "allowed to work": correct delegation boundary.
- §4 — Confidence score bands 0.7–1.0: internally consistent.

---

**MISSING CONSIDERATIONS:**

- **Governance:** No PHI/HIPAA data handling spec (encryption, retention, access controls) and no audit trail schema — both required before hospital deployment.
- **Validation Design:** §8 has metric targets but no worked examples, edge cases, or failure mode recovery paths.
- **Economics Alignment:** No per-verification API cost model or rate-limit budget.

---

## Part 2 — Escalation Email

```
TO:   Compliance Infrastructure Team Lead
FROM: Benoit Charrier, FDE
RE:   ACVA v1.0 Spec Review — One Blocker, Four Concerns
```

The architecture is well-scoped and the delegation boundaries are right — particularly the call not to make "allowed to work" determinations. One issue stops the build; the rest are fixable in the same revision pass.

**The state board API contracts are missing entirely (§3.1).** The spec describes what the system does but provides no endpoint, authentication method, request format, error codes, rate limits, or retry strategy for any of the three source types. This is the integration layer the entire verification pipeline runs on. We need at minimum two representative contracts — California BVNPT and New York DOH are the right anchors — plus a template that all additional states complete before going live. We're not asking for all 50 states upfront; just a defined interface shape the builder can work from.

Four things to resolve in the same revision: the optional-field matching logic (§2.1/§3.2), the confidence < 0.7 system behavior (§4), and the two TBD requirements — database schema (§5.2) and throughput estimate (§6). Both are probably quick to fill in.

Two sections need to be added before hospital deployment: a PHI/HIPAA data handling spec and an audit trail definition. Neither requires rearchitecting — both are additive.

Happy to jump on a 30-minute call to work through the API contract template together. The blocker is tractable once we have one sample state response to anchor it.

Benoit
