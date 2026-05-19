# Deliverable D0A — Domain Research: Healthcare Temporary Staffing / Clinical Workforce Coordination

**Domain:** Healthcare temporary staffing — the placement of clinical workers (nurses, allied health) into short-notice hospital and facility shifts by a staffing agency intermediary.

*Produced as a prior. Sections 1–5 written before reading scenario detail. Gaps are named in section 6.*

---

## 0. Executive Summary

- The domain's cognitive hotspot is the **credential-to-shift matching decision** — coordinators must simultaneously hold nurse availability, multi-dimensional licensure validity, facility-specific orientation requirements, and shift urgency under time pressure that compresses deliberation to seconds.
- The primary compliance constraint is **clinical credential verification** — Joint Commission, CMS, and state nursing board requirements make placing an uncredentialed worker a direct patient safety and regulatory liability event, creating a hard delegation stop: no placement confirmation without positive, current credential verification.
- The highest-leverage agentic opportunity is **automated shift-offer orchestration** (identify → contact → confirm qualified nurses for open shifts); the single biggest unknown is whether credential data is centralised and machine-readable in real time, or lives in a lagging system supplemented by coordinator memory.

---

## 0b. Table of Contents

- [0. Executive summary](#0-executive-summary)
- [0b. Table of contents](#0b-table-of-contents)
- [1. Domain overview](#1-domain-overview)
  - [1a. What this domain does](#1a-what-this-domain-does)
  - [1b. Typical workflow](#1b-typical-workflow)
  - [1c. Common failure modes](#1c-common-failure-modes)
- [2. Regulatory and compliance context](#2-regulatory-and-compliance-context)
- [3. Cognitive work patterns typical to this domain](#3-cognitive-work-patterns-typical-to-this-domain)
  - [3a. Where skilled attention is typically consumed](#3a-where-skilled-attention-is-typically-consumed)
  - [3b. Lived vs. documented gaps typical to this domain](#3b-lived-vs-documented-gaps-typical-to-this-domain)
- [4. ATX dimension pre-assessment](#4-atx-dimension-pre-assessment)
- [5. Hypothesis questions for discovery](#5-hypothesis-questions-for-discovery)
- [6. Assumption log](#6-assumption-log)

---

## 1. Domain Overview

### 1a. What This Domain Does

Healthcare temporary staffing agencies act as workforce intermediaries between healthcare facilities (hospitals, clinics, long-term care) and clinical workers (registered nurses, licensed practical nurses, allied health). The agency's core function is to fill workforce gaps — planned (scheduled float pool, predictable census peaks) and unplanned (call-outs, sudden census spikes, emergency coverage) — while maintaining compliance with clinical credential requirements. Primary knowledge workers are **staffing coordinators** (who manage real-time shift matching) and **credentialing specialists** (who verify and maintain worker qualification records). Inputs arrive as shift requests from facilities (via phone, email, or portal) and worker availability updates (via app, text, or call-in). Outputs are confirmed placements, with documentation flowing to facilities and billing/payroll downstream. A mid-size agency handles dozens to hundreds of open shifts per day, with volume concentrated in the 24–72 hour ahead window; after-hours and weekend volume is structurally higher due to facility call-out patterns.

### 1b. Typical Workflow

*Domain-typical workflow — client deviations will surface in discovery.*

1. **Shift request received** — facility submits via phone, email, or portal with unit, specialty, date/time, and urgency. `[execution]`
2. **Requirement extraction** — coordinator parses required specialty, licensure level, facility-specific orientation requirements, and any Do Not Return (DNR) flags. `[judgment]`
3. **Candidate identification** — coordinator queries available workers matching specialty and geography, typically from memory supplemented by system lookup. `[execution + judgment]`
4. **Credential verification check** — coordinator or credentialing specialist confirms license currency, specialty certifications, immunisation records, and facility-specific requirements (BLS, ACLS, unit orientation). `[verification]`
5. **Shift offer and negotiation** — coordinator contacts the nurse, presents the shift, handles rate questions or preference conflicts. `[coordination]`
6. **Placement confirmation** — coordinator confirms acceptance with both facility and nurse, creates placement record. `[execution]`
7. **Pre-shift compliance check** — day-of or prior-day confirmation that nurse is still available and credential status unchanged. `[verification]`
8. **Post-shift documentation** — timesheet capture, incident reporting if applicable, billing trigger. `[execution]`

### 1c. Common Failure Modes

- **Expired credential slippage** — a nurse's licence, certification, or immunisation expires undetected; placement proceeds and a compliance audit flags the gap. **Data failure** — credential records not tracked with expiry alerts, or system not checked in real time.
- **Specialty mismatch** — a nurse placed into a unit requiring a specialty they are not qualified for (e.g., ICU vs. Med/Surg) because matching relied on memory or an insufficiently granular availability record. **Judgment failure** — specialty-match criteria not codified or enforced at the matching step.
- **Ghost confirmation** — placement recorded but nurse no-shows because the confirmation loop was one-way (coordinator sent the offer and recorded it as confirmed without nurse acknowledgment). **Process failure** — confirmation loop not closed.
- **Coordination fragmentation** — shift request arrives by phone, credential check happens in a separate system, offer goes by text, confirmation is verbal; no single record ties the workflow together, creating audit trail gaps. **Coordination failure** — workflow distributed across channels with no orchestration layer.
- **Capacity overflow at peak** — at high-volume periods, coordinators deprioritise lower-urgency or lower-margin shifts, producing fill-rate decline with no systematic triage. **Process failure** — no queue management mechanism.

---

## 2. Regulatory and Compliance Context

| Framework / Constraint | What it governs | Agent design implication |
|------------------------|----------------|--------------------------|
| **Joint Commission (JCAHO) — HR Standards** | Agencies supplying workers to accredited hospitals must verify and document licensure, competency, and orientation completion before first placement | Agent must not confirm placement without credential verification gate; all verification must be logged with timestamps |
| **CMS Conditions of Participation** | Hospitals receiving Medicare/Medicaid funding must ensure all clinical staff (including agency) meet competency and credential requirements | Hard stop: agent placement confirmation requires positive credential check against current record, not cached status |
| **State Nursing Boards (50+ variations)** | Licence validity, scope of practice, and Nurse Licensure Compact (NLC) eligibility vary by state | Credential logic must be state-aware; a single national rule cannot apply — placement state must be a first-class parameter |
| **HIPAA** | Worker health records (immunisation, TB testing) are PHI; patient information must not be transmitted to workers unnecessarily | Agent communications must not include patient-identifiable information; credential records containing health data require appropriate access controls |
| **OSHA Bloodborne Pathogens Standard** | Clinical workers must have documented Hepatitis B vaccination or declination, and annual training | Credential package must include immunisation status; agent must flag missing OSHA documentation as a placement blocker |
| **FLSA / state wage law** | Overtime rules, mandatory rest periods between shifts; CA and NY have strict scheduling laws | Shift-offer logic must include fatigue/rest-period check; cannot offer a shift violating mandatory rest intervals |
| **DNR (Do Not Return) lists** | Facilities maintain lists of workers they do not want returned; agency must honour these | Agent must check facility-specific DNR status before generating any offer; this is a hard exclusion, not a soft preference |

**Hardest delegation stop:** Any placement confirmation that bypasses credential verification. This is a patient safety and regulatory liability event — no agent autonomy exists here without a positive, current verification signal.

---

## 3. Cognitive Work Patterns Typical to This Domain

### 3a. Where Skilled Attention Is Typically Consumed

> **Cognitive Hotspot [CH-1]: Matching a nurse to a shift under time pressure with incomplete information**
> **Cognitive type:** Pattern recognition + exception handling
> **Why it resists simple automation:** The coordinator must simultaneously hold nurse availability (often communicated informally), specialty fit, credential status, facility preference, relationship history, and pay rate — across multiple open shifts competing for the same candidate pool. Matching criteria are partially tacit (knowing which nurse performs well at a given facility, who accepts short-notice shifts reliably).
> **What would make it delegatable:** If availability, credentials, and facility requirements are all structured and current in a single system, an agent can generate a ranked shortlist. Full automation is achievable once nurse preferences and facility preferences are codified and trust is established through a HITL phase.

> **Cognitive Hotspot [CH-2]: Credential gap triage — what is missing and whether it is a blocker**
> **Cognitive type:** Verification + decision-making
> **Why it resists simple automation:** Credential requirements vary by facility and by unit within a facility. A nurse may have 7 of 8 required items; the coordinator must judge whether the missing item is a hard stop, can be waived, needs facility approval, and how quickly the gap can be resolved. Facility-specific overrides are common and not always documented.
> **What would make it delegatable:** If facility requirement profiles are fully structured, an agent can produce a credential gap report and classify hard-stop vs. soft-stop items. Waiver decisions require human sign-off — the classification is delegatable, the waiver is not.

> **Cognitive Hotspot [CH-3]: Real-time fill prioritisation when demand exceeds capacity**
> **Cognitive type:** Synthesis + decision-making
> **Why it resists simple automation:** When 20 shifts are open simultaneously and coordinator bandwidth is limited, informal triage applies: which facilities are most important clients, which shifts have highest urgency, which have lowest fill probability. These criteria are relationship-based, margin-aware, and partially political — rarely documented.
> **What would make it delegatable:** If facility priority tiers, shift urgency scoring, and fill probability estimates are codified, an agent can produce a ranked work queue. Political/relationship edge cases require human judgment.

> **Cognitive Hotspot [CH-4]: Handling nurse reluctance or renegotiation on an accepted shift**
> **Cognitive type:** Coordination + exception handling
> **Why it resists simple automation:** Late-stage complications (rate dispute, personal emergency, unit preference conflict) require negotiation balancing nurse relationship preservation with facility obligation. Resolution depends on nurse history, relationship value, and available alternatives.
> **What would make it delegatable:** This is the hotspot least likely to delegate short-term. An agent can alert a coordinator and surface alternatives, but the negotiation itself requires human judgment and relationship capital.

### 3b. Lived vs. Documented Gaps Typical to This Domain

> **Gap [G-1]: Credential system is not the system of truth — coordinator memory is**
> **Why it exists:** Credential management systems are often updated by a separate team on a lag; coordinators place nurses based on memory of recent interactions and spot-check the system only when flagged. The system is a lagging record, not a real-time gate.
> **Agent design implication:** An agent built to trust the credential system as a live gate will either block valid placements (stale-negative) or permit invalid ones (stale-positive). Discovery must determine the actual latency between credential events and system updates before any automation of the confirmation step.

> **Gap [G-2]: Shift confirmation is implicit, not structured**
> **Why it exists:** High-volume, time-pressured coordinators use shorthand — "you're good for Tuesday, right?" is treated as a confirmed placement. The SOP requires explicit written confirmation; the lived process records a placement as confirmed on verbal or informal acknowledgment.
> **Agent design implication:** An agent requiring a structured confirmation signal before logging a placement will create friction if nurses and coordinators use informal channels. The agent's confirmation flow must match the communication channel nurses actually use.

> **Gap [G-3]: Facility requirement profiles live in coordinator heads, not in system records**
> **Why it exists:** Facility profiles in staffing systems are often outdated or generic; unit-specific requirements (e.g., "stroke unit requires NIHSS certification") are known by experienced coordinators but not encoded in the system.
> **Agent design implication:** An agent relying on system facility profiles for requirement matching will produce placements that fail facility-level review. Facility profile enrichment is a prerequisite for matching automation — typically a non-trivial data remediation effort.

---

## 4. ATX Dimension Pre-Assessment

| ATX Dimension | Domain-typical signal | What to probe in discovery |
|---------------|----------------------|---------------------------|
| **Volume & Time** | High volume (dozens–hundreds of open shifts per day); highly time-sensitive (many shifts within 24–72 hours); coordinator bandwidth is the binding constraint on fill rate | Actual daily/weekly shift volume; average time-to-fill; percentage of same-day fills; coordinator headcount and utilisation |
| **Cognitive Nature** | Mixed: routine matching is largely rule-bound when data is clean; exception handling and negotiation are judgment-heavy; credentialing is verification-dominant | Percentage of "clean" placements (first-contact accept, no credential gaps) vs. exception fills; how often coordinators override system suggestions |
| **Data & Systems** | Typically fragmented: ATS or staffing platform, separate credential management system, facility profile records (often partially manual), nurse communication via SMS/phone | Number of systems per shift fill; whether credential status is queryable in real time; whether facility requirement profiles are structured or in documents/email |
| **Risk & Compliance** | High: credential non-compliance creates direct patient safety risk and regulatory liability; hard audit trail requirements; placement confirmation carries irreversibility risk if nurse shows up at wrong unit | Consequence of a credential gap placement; who bears liability; recent audit findings; whether there is a compliance incident log |
| **Organisational** | Multi-party: coordinator, credentialing team, nurse, facility HR/charge nurse; approval gates at credential verification; handoffs typically informal; after-hours coverage thin | Who approves what; is credentialing a separate team or coordinator responsibility; who handles after-hours fills; is there a manager approval gate |

**Most constraining dimension: Risk & Compliance.** The credential verification requirement creates a hard gate that cannot be bypassed under any volume pressure. This means the quality and real-time availability of credential data is the binding constraint on automation scope. If the credential system is a lagging record (as G-1 suggests is common), the agent's effective autonomy shrinks to everything *except* final placement confirmation — until data infrastructure is remediated. Every other dimension can be addressed incrementally; the compliance gate cannot be worked around.

---

## 5. Hypothesis Questions for Discovery

> **HQ-1: How many open shifts are typically in the queue at any given time, and what fraction require same-day or next-day fill?**
> **Hypothesis:** Volume is high enough (50+ simultaneous open shifts) and urgency high enough (>30% same-day) that coordinator bandwidth is the binding constraint on fill rate, not candidate availability.
> **If confirmed:** Shift-offer orchestration automation has direct, measurable ROI — reduced time-to-fill and increased fill rate without headcount growth.
> **If disconfirmed:** The bottleneck is elsewhere (candidate pool, credential gaps, rate disputes) and orchestration automation alone won't move the needle.

> **HQ-2: Where does credential data actually live, and how current is it at the moment a coordinator is filling a shift?**
> **Hypothesis:** Credential data is fragmented across systems (or partially in spreadsheets/email) and typically 24–72 hours stale relative to real credential events.
> **If confirmed:** Agent placement confirmation requires a data remediation phase before it can be trusted; initial agent scope must exclude final confirmation.
> **If disconfirmed:** If credential data is real-time and centralised, agent scope can include automated credential gate enforcement from day one.

> **HQ-3: What percentage of shift fills are "clean" — first-contact accept, no credential gaps, no exceptions?**
> **Hypothesis:** Clean fills are the majority (>60%) but consume disproportionate coordinator time because of volume; exception fills are the minority but consume disproportionate cognitive load.
> **If confirmed:** Agent can handle clean fills autonomously, freeing coordinators for exception work — classic automate-the-routine pattern.
> **If disconfirmed:** If clean fills are rare, exception handling must be in agent scope from the start.

> **HQ-4: Are facility requirement profiles documented in a structured system, or do they exist primarily in coordinator memory?**
> **Hypothesis:** Requirement profiles are partially in the system but incomplete; experienced coordinators hold the real knowledge.
> **If confirmed:** Facility profile enrichment is a prerequisite for matching automation — scope and timeline risk that must be surfaced in D2.
> **If disconfirmed:** If profiles are structured and current, matching automation can begin immediately without a data remediation phase.

> **HQ-5: How does the agency communicate shift offers to nurses — what channels, and what does "accepted" look like?**
> **Hypothesis:** Dominant channel is SMS or phone; acceptance is informal (verbal or text reply without structured confirmation); system records are updated retroactively.
> **If confirmed:** Agent shift-offer flow must work over SMS or the nurse's actual channel; requiring structured in-app confirmation will cause adoption failure.
> **If disconfirmed:** If nurses use a mobile app with in-app accept/decline, confirmation is already structured and agent integration is simpler.

> **HQ-6: Who bears liability when a nurse is placed with a credential gap — the agency, the facility, or split?**
> **Hypothesis:** The agency bears primary liability under indemnification clauses in facility contracts.
> **If confirmed:** Credential gate is a non-negotiable hard stop — no autonomous placement confirmation without positive verification, regardless of time pressure.
> **If disconfirmed:** If liability is shared or primarily on the facility, the agency may accept more verification risk — though this would be unusual and warrants legal review before reflecting in the architecture.

> **HQ-7: Does the agency operate across multiple states, and how is Nurse Licensure Compact (NLC) status managed?**
> **Hypothesis:** Multi-state operation creates credential complexity; compact vs. non-compact state rules are not consistently enforced, and coordinators sometimes place nurses without confirming compact eligibility.
> **If confirmed:** State-aware credential logic is required; placement state must be a first-class parameter in any matching logic.
> **If disconfirmed:** Single-state operation simplifies credential logic significantly.

> **HQ-8: What happens when no qualified nurse is available — what is the escalation path and who decides to leave a shift unfilled?**
> **Hypothesis:** Unfilled shifts are escalated to a supervisor only after an informal threshold of contact attempts; the threshold is inconsistent across coordinators.
> **If confirmed:** Agent can automate the contact-attempt loop and trigger escalation at a consistent threshold, reducing coordinator time on no-fill scenarios.
> **If disconfirmed:** If escalation is already structured, agent value is in the contact loop, not the escalation decision.

> **HQ-9: Is fill rate tracked, and is it decomposed by shift type, facility tier, or urgency level?**
> **Hypothesis:** Fill rate is tracked globally but not segmented; the agency does not know which shift types or facilities are hardest to fill or which coordinator behaviours drive outcomes.
> **If confirmed:** Agent instrumentation provides segmented visibility as a by-product of automation — a co-benefit alongside efficiency that strengthens the business case.
> **If disconfirmed:** If segmented metrics already exist, the agent design should explicitly target the lowest-performing segments.

> **HQ-10: Does a staffing platform currently manage shift dispatch, and what are its integration capabilities?**
> **Hypothesis:** A platform exists (e.g., Bullhorn, Staffmark, or similar) but API access is limited or undocumented; integrations require custom work.
> **If confirmed:** Integration complexity is a scope risk; agent design must account for realistic API availability and may require webhook setup or screen-based interaction as a fallback.
> **If disconfirmed:** A well-documented API makes integration scope more predictable and reduces delivery risk.

> **HQ-11: How is after-hours coverage handled, and does fill rate drop significantly outside business hours?**
> **Hypothesis:** After-hours coverage is thin (one on-call coordinator or outsourced) and fill rate declines materially; this is the highest-leverage automation target because human bandwidth is lowest when facility need is often highest.
> **If confirmed:** After-hours shift orchestration is the highest-ROI initial automation target with the lowest disruption risk (current process is already degraded).
> **If disconfirmed:** If after-hours is handled adequately, focus shifts to business-hours capacity amplification.

---

## 6. Assumption Log

> **Assumption [A-1]:** Staffing coordinators handle both shift matching and credential verification (rather than a fully separate credentialing team operating in real time).
> **Why it matters:** If credentialing is fully separate with a clean handoff, agent scope can be delineated more sharply; if coordinators do both, cognitive load is higher and credential quality risk is greater.
> **If wrong:** A separate credentialing team with structured handoff simplifies the agent's compliance gate design.
> **Confidence:** Medium — common in mid-size agencies, but larger agencies often specialise.
> **How to validate:** Ask: "Who verifies credentials before a placement is confirmed — the coordinator or a separate team?"

> **Assumption [A-2]:** Weekly shift volume for a mid-size agency (200 employees) is in the range of 50–200 open shifts per week.
> **Why it matters:** Volume drives the ROI case for automation; if lower, efficiency gains are modest and the value case shifts to quality improvement; if higher, throughput case is strong.
> **If wrong:** Lower volume weakens the throughput argument; higher volume strengthens it and may warrant a larger initial automation scope.
> **Confidence:** Low — 200 employees includes non-coordinator staff; actual coordinator count and shift volume are unknown.
> **How to validate:** Ask: "How many open shifts are you managing at any given time? How many does your team fill per week?"

> **Assumption [A-3]:** The primary nurse communication channel for shift offers is SMS or phone, not a structured mobile app with explicit accept/decline.
> **Why it matters:** Channel determines confirmation logic and friction profile; unstructured channels require the agent to interpret informal signals or hand off to a human for confirmation.
> **If wrong:** If a mobile app with structured signalling is already in use, confirmation loop design is simpler and agent adoption risk is lower.
> **Confidence:** Medium — SMS-dominant is typical for legacy agencies; newer agencies have moved to apps.
> **How to validate:** Ask: "How do you send shift offers to nurses, and what does a nurse acceptance look like?"

> **Assumption [A-4]:** Credential records have meaningful latency (hours to days) between real-world credential events and system update; coordinators do not rely on the system as a live gate.
> **Why it matters:** If credential data is live and trusted, agent placement confirmation can use it directly; if stale, the agent must flag uncertainty or the scope must exclude final confirmation until remediated.
> **If wrong:** Live credential data makes the compliance gate immediately automatable and reduces risk significantly.
> **Confidence:** Medium — stale credential systems are a documented pain point in this domain, but some agencies have invested in real-time verification integrations.
> **How to validate:** Ask: "When a nurse renews their licence, how quickly does that appear in your system? Who updates it?"

> **Assumption [A-5]:** The primary bottleneck is coordinator time on routine matching and offer orchestration, not candidate pool size or facility relationship issues.
> **Why it matters:** If the bottleneck is coordinator time, automating matching and orchestration improves fill rate; if the bottleneck is candidate supply, automation has no impact on fill rate and the agent must justify itself on quality or efficiency alone.
> **If wrong:** If candidate supply is the bottleneck, the agent design should focus on outbound recruitment and availability capture rather than matching and dispatch.
> **Confidence:** Low — this is the central hypothesis of the engagement, not a validated fact.
> **How to validate:** Ask: "When you can't fill a shift, what's the most common reason — no available nurse, the available nurses don't meet requirements, or coordinator bandwidth?"
