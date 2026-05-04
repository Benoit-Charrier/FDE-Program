# Agent Mapping: PA Chase Timing Agent (Wave 1)

**Agent Name**: PA Chase Timing & Denial Management Agent  
**Date**: 2026-04-29  
**Wave**: 1 (Strategic Priority)  
**Based on**: Phase 4 Prioritization (scenario5-phase4-prioritization.md)  
**Methodology**: ATX Agent Mapping (atx-agent-mapping.md)

---

## Table of Contents

1. [Agent Purpose Document](#1-agent-purpose-document)
2. [Agent Activity Catalog](#2-agent-activity-catalog)
3. [Autonomy Matrix (Decision Authority Matrix)](#3-autonomy-matrix-decision-authority-matrix)
4. [System and Data Inventory](#4-system-and-data-inventory)
5. [Context Engineering Design](#5-context-engineering-design)
6. [Compounding Roadmap](#6-compounding-roadmap)

---

## 1. Agent Purpose Document

### Agent Name
**PA Chase Timing & Denial Management Agent**

### Job to be Done
Ensure prior authorization approvals arrive before scheduled procedures by determining optimal chase timing based on insurer-specific patterns and managing denial resolution workflows.

### Business Context
- **Department**: Clinical Operations / Practice Management
- **Process**: Prior Authorization Management
- **Owner**: Dana Velazquez (Practice Manager, RN, 11 years tenure)
- **Volume**: 25 PAs/day (6,250 cases/year)
- **Current State**: Dana manually tracks PA submissions in Google Sheet, applies insurer-specific learned patterns for chase timing (e.g., "Humana always 6 days not 5"), phones insurers at optimal time, handles denials with workaround knowledge (e.g., "Wellpath always denies colonoscopy first time — attach prior visit note")

### Primary Objectives (What Success Looks Like)

1. **Zero visit aborts from PA timing misses**
   - Current state: ~1-3 per quarter (Artefact 5.2: patient TJ's second visit abort caused senior physician complaint)
   - Target: 0 per quarter

2. **Systematize Dana's institutional knowledge**
   - Capture 11 years of insurer-specific patterns before Dana moves to regional manager role (A14)
   - Make patterns available to all front-desk staff and future hires
   - Reduce knowledge concentration risk (single point of failure when Dana unavailable)

3. **Proactive chase timing that never misses deadlines**
   - Dana's #1 stated priority (Q18: "If I could fix one thing, it would be this")
   - Agent calculates optimal chase date based on learned SLAs, not stated SLAs
   - Example: Humana stated SLA = 5 days; lived SLA = 6 days (always); agent chases at day 6

4. **Reduce Dana's manual tracking overhead**
   - Current state: 1.5-2 hours/day manually checking Google Sheet, calculating timing, phoning insurers
   - Target: 15 minutes/day spot-checking unpredictable insurers (Aetna) + reviewing denials

### KPIs

| Metric | Baseline (Current) | Target (Production) | Measurement Method |
|--------|-------------------|---------------------|-------------------|
| **Accuracy**: % PAs chased at optimal timing | Unknown (Dana's tacit timing) | 90% within ±1 day of optimal | Compare agent recommendation vs. actual approval date |
| **Coverage**: % cases handled without escalation | 0% (Dana handles all) | 80% (agent handles predictable insurers; escalates Aetna) | Count autonomous decisions / total PAs |
| **Throughput**: Daily PA chase capacity | 25 (limited by Dana's time) | 50+ (scalable; no Dana bottleneck) | Count PAs agent can monitor simultaneously |
| **Cost per case**: Token + tool + HITL cost | $3.30 (Dana's fully loaded time) | $0.0165 + $0.29 HITL = $0.31 (91% reduction) | Token logs + HITL time tracking |
| **HITL rate**: % requiring human review | 100% (Dana does all) | Learning phase: 100% (Dana approves all)<br>Production: 20% (spot-checks Aetna + denials) | Count escalations / total cases |
| **Visit abort prevention**: PAs approved on time | ~96% (1-3 aborts/quarter ÷ ~1,600 PAs/quarter) | 100% (0 aborts) | athenahealth visit cancellation reason = "PA not approved" |

### Failure Modes

| Failure Mode | What Does Bad Output Look Like? | Consequence | Recovery Path |
|--------------|--------------------------------|-------------|---------------|
| **Chase too early** | Agent recommends chase at day 4 for Humana (correct is day 6) | Wasted Dana time on premature call; insurer says "call back later" | Dana corrects timing → agent learns (reinforcement); no patient impact |
| **Chase too late** | Agent recommends chase at day 8; PA still pending at visit time | Visit abort, patient frustration, physician complaint | Escalate to Dana for urgent phone chase; reschedule visit if needed; agent logs miss for pattern refinement |
| **Wrong insurer pattern applied** | Agent treats UHC like Humana (6d vs. 7d) | Chase timing off by 1 day; marginal impact | Dana corrects → agent updates insurer-specific model |
| **Denial reason misinterpreted** | Agent suggests generic resubmission; misses Wellpath colonoscopy pattern (needs prior visit note) | Resubmission rejected again; 1-2 week delay; patient rescheduling | Dana reviews denial, applies correct workaround; agent logs denial pattern for future cases |
| **Insurer SLA changed, agent unaware** | Humana suddenly approves in 5 days (not 6); agent still chases at day 6 | Marginal (chase still succeeds, just 1 day later than needed) | Agent detects anomaly (approval arrived earlier than predicted); flags to Dana for pattern update |
| **Agent recommends chase for already-approved PA** | Agent queries athenahealth, misses status update; recommends unnecessary chase | Wasted Dana time on redundant call | Dana cancels chase; agent refines athenahealth polling frequency |

### Delegation Archetype

**Learning Phase (Months 1-6)**: **Agent-led + Human Oversight**
- Agent ingests Dana's Google Sheet (historical patterns)
- Agent recommends chase timing based on submission date + insurer + learned pattern
- Dana approves/corrects every recommendation
- Agent learns from Dana's corrections (reinforcement learning)
- Dana teaches new patterns (e.g., "Medicare Advantage changed SLA to 4 days last month")

**Production Phase (Month 7+)**: **Fully Agentic for Predictable Insurers**
- Agent handles chase timing autonomously for stable insurers (Humana, UHC, BCBS, Medicare, Wellpath)
- Agent escalates to Dana for:
  - Unpredictable insurers (Aetna: "sometimes fast, sometimes slow")
  - Denials (Dana reviews denial reason, agent suggests workaround based on historical pattern, Dana approves resubmission)
  - Anomalies (insurer behavior deviates from learned pattern → flag for Dana review)
- Dana spot-checks 20% of cases (~5 PAs/day = 15 min/day)

**Rationale**: Dana's #1 priority (Q18); captures institutional knowledge (A2, A4, A7) before Dana moves to regional role (A14); prevents visit aborts that triggered senior physician's AI request

### Escalation Triggers

| Condition | Escalate To | Rationale |
|-----------|-------------|-----------|
| Insurer is Aetna (unpredictable timing) | Dana | Q5 confirmed: Aetna "sometimes fast, sometimes slow" — no stable pattern |
| PA status = denied | Dana | Denial reason interpretation requires human judgment; agent can suggest workaround based on historical pattern (e.g., Wellpath colonoscopy), but Dana approves resubmission |
| Approval arrives >2 days earlier/later than predicted | Dana | Anomaly detection: insurer may have changed SLA policy (A2); Dana validates and updates pattern |
| PA submission <3 days before procedure date | Dana | High-risk: insufficient time for standard chase; may require urgent escalation to insurer |
| Insurer not in agent's learned pattern library | Dana | New insurer or rare case; agent has no historical data to guide timing |
| athenahealth API error or PA status unavailable | Dana | System integration failure; manual workaround required |

---

## 2. Agent Activity Catalog

Enumerate every micro-task the agent performs. For each task, specify type, delegation level, data required, tool required, and risk level.

| Task | Type | Delegation Level | Data Required | Tool Required | Risk Level | Notes |
|------|------|-----------------|---------------|---------------|------------|-------|
| **Ingest historical PA patterns from Google Sheet** | Retrieval | Fully agentic (one-time setup) | Dana's Google Sheet (Artefact 5.1 format) | Google Sheets API | Low | One-time during agent build; extracts insurer-specific timing patterns (Humana=6d, UHC=7d, etc.) |
| **Poll athenahealth for PA submissions** | Retrieval | Fully agentic | PA submission date, insurer, procedure type, patient ID | athenahealth REST API | Low | Daily batch query: "all PAs submitted in past 10 days with status=pending" |
| **Extract insurer from PA record** | Reasoning | Fully agentic | PA insurer field from athenahealth | None (in-context) | Low | Map insurer name to agent's pattern library (e.g., "UnitedHealthcare Choice PPO" → "UHC") |
| **Retrieve learned SLA pattern for insurer** | Retrieval | Fully agentic | Insurer name | Agent's pattern database (seeded from Google Sheet) | Medium | If insurer not found → escalate to Dana |
| **Calculate optimal chase date** | Reasoning | Agent-led + HITL (learning)<br>Fully agentic (production) | PA submission date, insurer's learned SLA | None (in-context calculation) | Medium | Example: Submitted 04/01, Humana, learned SLA=6d → chase on 04/07 |
| **Compare current date to chase date** | Decision | Fully agentic | Today's date, calculated chase date | None | Low | If today ≥ chase date → trigger chase action |
| **Check athenahealth for PA status update** | Retrieval | Fully agentic | PA ID, current status | athenahealth REST API | Low | Before recommending chase, verify PA still pending (avoid redundant chase) |
| **Recommend chase to Dana** | Generation | Agent-led + HITL (learning)<br>Fully agentic (production for predictable insurers) | PA details, insurer, procedure, patient name, chase rationale | None | Medium | Output: "Chase now: [Patient Name], [Procedure], [Insurer], submitted [Date], pattern suggests approval by [Date]" |
| **Dana approves/corrects chase timing** | Human decision (learning phase only) | Human-led | Agent recommendation, Dana's judgment | UI approval interface | High (during learning) | Dana can override: "No, wait 1 more day" → agent logs correction |
| **Execute chase action** | Action | Human-led + agent support | PA details, insurer contact info | Phone (Dana), or athenahealth portal message | Medium | Agent generates chase message template; Dana places call or sends message |
| **Log chase action in athenahealth** | Action | Fully agentic | Chase date, Dana's name, outcome | athenahealth REST API (PA notes/activity log) | Low | Document: "PA chase initiated [Date] per agent recommendation" |
| **Detect PA approval** | Retrieval | Fully agentic | PA status from athenahealth | athenahealth REST API | Low | Daily poll: status changed from pending → approved |
| **Calculate timing accuracy** | Reasoning | Fully agentic | Chase date, approval date, predicted approval date | None | Low | Measure: predicted approval date vs. actual → refine insurer pattern |
| **Detect anomaly (approval timing deviates >2 days)** | Reasoning | Fully agentic | Predicted approval date, actual approval date | None | Medium | Flag to Dana: "Humana approved in 5 days (predicted 6); possible SLA change" |
| **Retrieve PA denial reason** | Retrieval | Fully agentic | PA status=denied, denial code/text | athenahealth REST API | Medium | Extract denial reason from PA record or insurer portal |
| **Match denial reason to historical pattern** | Reasoning | Agent-led + HITL | Denial reason, insurer, procedure type, historical denial patterns | Agent's denial pattern library | High | Example: "Wellpath colonoscopy denial" → match pattern "attach prior visit note" |
| **Suggest resubmission workaround** | Generation | Agent-led + HITL | Matched denial pattern, required documentation | None | High | Output: "Suggest resubmission with [Document X] based on [Insurer] pattern" |
| **Dana reviews and approves resubmission** | Human decision | Human-led | Agent's suggestion, denial details, patient chart | athenahealth UI | High | Dana validates clinical documentation is available and appropriate |
| **Flag visit at risk (PA pending <2 days before visit)** | Decision | Fully agentic | PA submission date, procedure date, current status | athenahealth REST API | High | Escalate to Dana: "Urgent: [Patient] visit in 1 day, PA still pending" |
| **Update agent pattern library** | Action | Agent-led + Dana approval | Dana's corrections, anomaly detections, new insurer data | Agent's model update pipeline | Medium | Reinforcement learning: adjust insurer-specific timing based on corrections |
| **Generate weekly PA chase summary for Dana** | Generation | Fully agentic | Past week's PA chases, outcomes, anomalies | None | Low | Report: "25 PAs chased, 23 approved on time, 2 escalations (Aetna), 1 denial (resolved)" |

**Task Type Key**: 
- **Reasoning**: Model does cognitive work (pattern matching, calculation, interpretation)
- **Retrieval**: Fetch and return data from systems
- **Decision**: Choose between outcomes or trigger actions
- **Action**: Write to system or trigger external process
- **Generation**: Produce text or structured output

---

## 3. Autonomy Matrix (Decision Authority Matrix)

Defines what the agent decides alone vs. what requires human approval. This is the operational contract between the agent and the organization.

### AGENT DECIDES ALONE (No HITL Required)

**Data Retrieval & Monitoring** (Low Risk):
- Poll athenahealth daily for PA submissions and status updates
- Extract insurer, procedure type, submission date from PA records
- Query agent's pattern library for learned SLA timing
- Calculate optimal chase date based on submission date + insurer pattern
- Log all agent activities in athenahealth PA notes (audit trail)

**Pattern Learning & Anomaly Detection** (Medium Risk, Informational):
- Calculate timing accuracy post-approval (predicted vs. actual)
- Detect anomalies (approval >2 days earlier/later than predicted)
- Flag anomalies to Dana for review (does NOT auto-update patterns)
- Generate weekly summary reports for Dana

**Production-Phase Chase Recommendations** (Month 7+, Predictable Insurers Only):
- Recommend chase timing for: Humana, UnitedHealthcare, BCBS PPO, Medicare, Wellpath
- Condition: Insurer in agent's validated pattern library + no anomalies in past 6 months
- Output: "Chase now" recommendation visible in Dana's dashboard

### AGENT ACTS, HUMAN NOTIFIED AFTER

**Chase Timing Recommendations** (Learning Phase, Months 1-6):
- Agent recommends chase timing for all insurers
- Dana receives notification: "PA ready for chase: [Patient], [Insurer], [Rationale]"
- Notification includes: submission date, predicted approval date, recommended chase date, historical pattern reference
- Dana can approve immediately or defer (agent re-notifies next day)

**Risk Flags** (High Priority, Informational):
- PA pending <2 days before procedure date → urgent escalation to Dana
- Insurer behavior anomaly detected → notification to Dana
- athenahealth API error → notification to Dana + fallback to manual tracking

### AGENT PROPOSES, HUMAN APPROVES BEFORE ACTION

**Learning Phase Chase Timing** (Months 1-6):
- Agent: "Recommend chase on [Date] for [Patient], [Insurer], based on pattern [X]"
- Dana: Approve / Defer +1 day / Override with custom date
- Agent logs Dana's decision and learns from corrections

**Denial Resubmission Workflow** (All Phases):
- Agent detects PA status=denied
- Agent retrieves denial reason from athenahealth
- Agent matches denial to historical pattern (if available): "Wellpath colonoscopy → attach prior visit note"
- Agent proposes: "Suggest resubmission with [Document X] based on [Insurer] historical pattern"
- Dana reviews: (a) validates clinical documentation available, (b) approves/modifies resubmission, (c) executes resubmission
- Agent logs outcome for future pattern refinement

**Pattern Library Updates** (All Phases):
- Agent accumulates corrections and anomalies
- Agent proposes pattern update: "Humana SLA changed from 6 days to 5 days (3 consecutive cases approved in 5 days)"
- Dana reviews and approves update → agent applies to future recommendations

### HUMAN TAKES OVER (Agent Supports)

**Unpredictable Insurers** (All Phases):
- **Trigger**: Insurer is Aetna (or any insurer marked "unpredictable" in agent's library)
- **Agent action**: Escalate to Dana: "Aetna PA submitted [Date]; no stable pattern available; recommend manual timing decision"
- **Dana action**: Uses her judgment to decide chase timing; agent logs Dana's decision as training data

**High-Stakes / Urgent Cases** (All Phases):
- **Trigger**: PA pending <3 days before procedure + still not approved
- **Agent action**: Urgent escalation: "PA at risk: [Patient] visit on [Date], PA submitted [Date], still pending"
- **Dana action**: Phones insurer immediately for expedited review; considers visit rescheduling

**New Insurers or Rare Cases** (All Phases):
- **Trigger**: Insurer not in agent's pattern library (e.g., new Medicaid managed care plan)
- **Agent action**: Escalate: "No historical data for [Insurer]; recommend manual chase timing"
- **Dana action**: Uses clinical judgment + insurer portal research; agent logs Dana's decision to seed new pattern

**System Integration Failures** (All Phases):
- **Trigger**: athenahealth API error, PA status unavailable, Google Sheet sync failure
- **Agent action**: Escalate: "System error detected; manual PA tracking required"
- **Dana action**: Falls back to manual Google Sheet tracking until system restored

**Clinical Judgment Required** (All Phases):
- **Trigger**: Denial reason requires physician input (e.g., "medical necessity not demonstrated")
- **Agent action**: Escalate to Dana with denial details
- **Dana action**: Consults physician for additional clinical documentation; coordinates resubmission

---

## 4. System and Data Inventory

For each data source or system the agent needs to interact with:

| System | Data Needed | Access Type | Availability | Gap/Risk | Shared with Other Agents? |
|--------|-------------|-------------|--------------|----------|--------------------------|
| **athenahealth EHR** | PA submission date, insurer, procedure type, patient ID, PA status (pending/approved/denied), denial reason/code | Read/Write | REST API (A12: validated via coach) | **Gap**: Denial reason field may be free text (unstructured); requires NLP interpretation<br>**Risk**: API rate limits (need to batch queries); auth token refresh | YES (Wave 2: Insurance Verification; Wave 3: Med Recon) |
| **Dana's Google Sheet** | Historical PA data: submission date, insurer, procedure, actual approval date, Dana's "target chase" date, notes (e.g., "Wellpath colonoscopy pattern") | Read (one-time ingest) | Google Sheets API (public API available) | **Gap**: Schema not standardized (Artefact 5.1 shows sample; full sheet may have inconsistencies)<br>**Risk**: Dana updates sheet ad-hoc; agent ingests historical snapshot only (not live-synced) | NO (unique to PA Chase agent) |
| **Insurer Portals** | Real-time PA status (some insurers provide web portals) | Read (manual or web scraping; no standard API) | Varies by insurer (fragmented) | **Gap**: Most insurers lack APIs; portals are web-only, require login, inconsistent UX<br>**Risk**: Web scraping is brittle; not recommended for production<br>**Workaround**: Agent relies on athenahealth PA status updates (manual entry by Dana/front-desk after checking portal) | NO |
| **Agent Pattern Library** | Insurer-specific learned SLAs (Humana=6d, UHC=7d, etc.); denial patterns (Wellpath colonoscopy→prior visit note); anomaly history | Read/Write | Internal database (vector store or structured DB) | **Gap**: None (agent-owned asset)<br>**Risk**: Must version-control pattern updates (Dana approves changes); rollback if pattern update causes accuracy drop | NO (but could be shared if future agents need PA data) |
| **Agent Activity Log** | All agent recommendations, Dana's approvals/corrections, chase outcomes, timing accuracy metrics | Write | Internal logging (append-only) | **Gap**: None<br>**Risk**: Log volume grows linearly with PA volume; need retention policy (archive after 2 years) | YES (compliance/audit across all agents) |

### Integration Notes

**athenahealth API**:
- **Authentication**: OAuth 2.0 (requires practice-level API keys; Dana to provision)
- **Rate limits**: TBD (needs technical validation); assume conservative 100 requests/min
- **Batch queries**: Use date range filter to pull all PAs submitted in past 10 days (single API call/day)
- **Write operations**: Update PA notes/activity log with agent actions (audit trail)
- **Shared asset**: Wave 2 (Insurance Verification) will build athenahealth + Availity integration → reusable auth client, error handling, retry logic

**Google Sheets API**:
- **One-time ingest**: During agent build, pull Dana's full historical sheet (past 2-3 years of PA data)
- **Schema mapping**: Artefact 5.1 format: Submission Date | Insurer | Procedure | Status | Target Chase Date | Notes
- **Pattern extraction**: Group by insurer, calculate median approval time, identify denial patterns from notes column
- **Not live-synced**: Agent ingests historical snapshot; future patterns learned from Dana's corrections during learning phase (not from sheet updates)

**Insurer Portals** (Deferred):
- **Gap**: No standard API across insurers
- **Current workflow**: Dana manually checks insurer portals, updates athenahealth PA status
- **Agent workaround**: Agent relies on athenahealth as source of truth (assumes Dana/front-desk updates status after portal checks)
- **Future enhancement** (Wave 2+): If specific insurers provide APIs (e.g., UHC may have partner API), integrate directly to reduce manual status checks

---

## 5. Context Engineering Design

Context quality determines agent quality. For this agent, design memory architecture, retrieval strategy, and prompt engineering principles.

### Memory Architecture

| Memory Type | Content | Storage | Lifecycle | Rationale |
|-------------|---------|---------|-----------|-----------|
| **In-context (short-term)** | Current PA being processed: patient ID, insurer, submission date, procedure type, calculated chase date, Dana's prior corrections for this insurer (if any) | Prompt window (active conversation) | Per PA case (cleared after chase recommendation generated) | Agent needs full PA context + insurer pattern in single inference call to generate chase recommendation |
| **Episodic (medium-term)** | Dana's corrections during learning phase: "I said chase UHC at 7 days, not 6" → logged with timestamp, insurer, correction type | Vector DB (retrievable by insurer name or correction type) | Per learning phase (6 months); archived after agent transitions to production | Agent retrieves Dana's past corrections for specific insurer when calculating timing → reinforcement learning |
| **Semantic (long-term)** | Insurer-specific learned patterns (Humana=6d, UHC=7d, Wellpath colonoscopy denial workaround, etc.); denial reason → resubmission doc mappings | Structured database (insurer name → pattern object) | Updated on Dana approval; versioned (rollback if accuracy drops) | Agent queries this for every chase calculation; must be fast (low latency), accurate, and auditable |
| **Procedural (static)** | Agent instructions: "Never chase before day 3 (insurers don't process that fast)"; escalation rules: "Always escalate Aetna"; guardrails: "If PA pending <2 days before visit → urgent flag" | System prompt (version-controlled) | Updated on major agent logic changes; reviewed quarterly | Agent's core decision rules; must be explicit, unambiguous, and aligned with Dana's workflow |

### Retrieval Strategy

**What triggers a retrieval call?**
1. **New PA detected in athenahealth** (daily batch query): "Any PAs submitted in past 10 days with status=pending?"
   - Triggers: Extract insurer name → query agent pattern library for learned SLA
2. **Chase date reached** (daily check): "Any PAs where today ≥ calculated chase date?"
   - Triggers: Retrieve PA details from athenahealth → generate chase recommendation
3. **Denial detected** (daily batch query): "Any PAs where status changed to denied?"
   - Triggers: Retrieve denial reason from athenahealth → query agent pattern library for historical denial patterns (e.g., "Wellpath colonoscopy" → match "attach prior visit note")
4. **Dana correction during learning phase** (user input): Dana overrides agent recommendation
   - Triggers: Log correction to episodic memory (vector DB) → retrieve similar past corrections for same insurer → update semantic memory (pattern library) if correction is consistent (e.g., 3+ corrections in same direction)

**What is the retrieval target?**
- **Pattern library**: Top-1 exact match on insurer name (deterministic lookup, not semantic search)
- **Episodic memory (corrections)**: Top-5 similar corrections by insurer name + correction type (semantic search via vector embeddings)
- **Denial patterns**: Top-3 similar denials by insurer + procedure type (semantic search: "Wellpath colonoscopy denial" → match historical "Wellpath colonoscopy always denied first time")

**How is retrieval quality evaluated?**
- **Pattern accuracy**: Post-approval, compare predicted approval date vs. actual → calculate RMSE per insurer → flag insurers with RMSE >1.5 days for Dana review
- **Denial pattern match rate**: Track % denials where agent successfully matches historical pattern → target 70% match rate (remaining 30% are novel denials requiring Dana's judgment)
- **Correction learning rate**: Track how many Dana corrections are needed before agent stabilizes per insurer → target <10 corrections per insurer (indicates agent has learned stable pattern)

**How are retrieval costs managed?**
- **Pattern library**: In-memory cache (low latency, no external API cost); <10 KB total (15 insurers × avg 500 bytes/pattern)
- **athenahealth queries**: Batch daily (not real-time per PA) → 1 API call/day for PA submissions, 1 API call/day for status updates = 2 calls/day = ~$0.004/day token cost
- **Episodic memory**: Vector search only during learning phase (not production) → cost amortized over 6 months

### Prompt / Context Engineering Principles

1. **Role and purpose first**: System prompt opens with:
   ```
   You are the PA Chase Timing Agent for Westbridge Family Medicine.
   Your job: Ensure prior authorizations are approved before scheduled procedures by 
   determining optimal chase timing based on insurer-specific learned patterns.
   ```

2. **Explicit scope**: System prompt states:
   ```
   You MAY:
   - Calculate chase timing based on learned insurer patterns
   - Recommend when Dana should chase pending PAs
   - Flag urgent cases (PA pending <2 days before visit)
   - Suggest denial resubmission workarounds based on historical patterns
   
   You MAY NOT:
   - Chase insurers directly (Dana places calls)
   - Approve or deny PAs (only insurers can do this)
   - Override Dana's corrections (always log and learn from them)
   - Update patterns without Dana's approval
   ```

3. **Few-shot examples**: Include representative examples:
   ```
   Example 1 (Standard chase):
   Input: PA submitted 04/01, Insurer=Humana, Procedure=Colonoscopy, Status=Pending
   Reasoning: Humana learned SLA = 6 days (not stated 5 days). Chase date = 04/01 + 6d = 04/07.
   Output: "Chase recommended on 04/07. Rationale: Humana consistently approves in 6 days (historical pattern, 50+ cases)."
   
   Example 2 (Escalation):
   Input: PA submitted 04/15, Insurer=Aetna, Procedure=MRI, Status=Pending
   Reasoning: Aetna has unpredictable timing (sometimes 3d, sometimes 7d; no stable pattern).
   Output: "Escalate to Dana. Rationale: Aetna timing unpredictable; recommend manual decision."
   ```

4. **Guardrail instructions**:
   ```
   Refusal cases:
   - If insurer not in pattern library → escalate to Dana (do not guess timing)
   - If athenahealth API error → escalate to Dana (do not proceed with stale data)
   
   Uncertainty handling:
   - If predicted approval date has >2 day uncertainty (based on historical variance) → flag to Dana
   - If Dana corrects your timing >2 days → flag as high-confidence correction (update pattern immediately)
   
   Escalation triggers (explicit list):
   - Insurer = Aetna
   - PA pending <3 days before procedure
   - PA status = denied
   - Approval >2 days earlier/later than predicted
   ```

5. **Structured output**: Agent outputs JSON for chase recommendations:
   ```json
   {
     "action": "recommend_chase" | "escalate_to_dana" | "urgent_flag",
     "pa_id": "12345",
     "patient_name": "John Doe",
     "insurer": "Humana",
     "procedure": "Colonoscopy",
     "submission_date": "2026-04-01",
     "recommended_chase_date": "2026-04-07",
     "rationale": "Humana learned SLA = 6 days (50+ historical cases)",
     "confidence": "high" | "medium" | "low"
   }
   ```

6. **Chain of thought for complex reasoning**: For denial pattern matching, instruct agent:
   ```
   Step 1: Extract denial reason from athenahealth (e.g., "Prior authorization denied - medical necessity not established")
   Step 2: Identify insurer + procedure type (e.g., Wellpath + Colonoscopy)
   Step 3: Query pattern library for similar denials (semantic search: top-3 matches)
   Step 4: If match found (e.g., "Wellpath colonoscopy always denied first time"), retrieve workaround (e.g., "attach prior visit note")
   Step 5: Output suggestion: "Recommend resubmission with [Document]. Rationale: [Pattern]."
   Step 6: Escalate to Dana for approval (do not auto-resubmit)
   ```

7. **Token discipline**:
   - Insurer patterns stored as concise key-value: `{"Humana": {"sla_days": 6, "confidence": "high", "last_updated": "2026-03-15"}}`
   - Avoid verbose logging in prompts (e.g., don't include full athenahealth API response; extract only PA ID, insurer, dates)
   - Reuse system prompt across all PAs (not per-PA custom prompts)

---

## 6. Compounding Roadmap

The agent roadmap is designed so that integrations and platform assets built for Wave 1 amplify Wave 2 and beyond.

### Roadmap Structure

#### **Wave 1 — Foundation Agent (PA Chase Timing)** [Months 1-8]
**Agent**: PA Chase Timing & Denial Management Agent  
**Purpose**: Systematize Dana's insurer-specific PA chase patterns; prevent visit aborts  
**Timeline**: 
- Months 1-2: Build (Google Sheet ingestion, pattern extraction, agent architecture)
- Months 3-8: Learning phase (Dana teaches patterns, agent learns from corrections)
- Month 9+: Production transition (agent autonomous for predictable insurers)

**Key Integrations Built**:
1. **Google Sheets API integration**: One-time ingest of Dana's historical PA data (not reusable; unique to this agent)
2. **athenahealth REST API** (PA-specific endpoints):
   - Read: PA submissions (filter by date range, status)
   - Read: PA status updates (pending/approved/denied)
   - Write: PA activity log (agent actions, chase dates, outcomes)
   - **Reusable in Wave 2**: athenahealth auth client, API wrapper, error handling, retry logic

**Shared Assets Created**:
1. **athenahealth API Client** (reusable):
   - OAuth 2.0 auth flow
   - Rate limit handling (exponential backoff)
   - Error categorization (transient vs. permanent failures)
   - Retry logic with circuit breaker
   - Logging & monitoring (API call success rate, latency)
   
2. **Agent Activity Logging Framework** (reusable):
   - Structured logging format: timestamp, agent ID, action type, input data, output, user feedback
   - Append-only log storage (audit trail)
   - Log retrieval API (for Dana's dashboard: "Show me all PA chases from past week")
   - Retention policy (archive after 2 years)

3. **Human-in-the-Loop (HITL) Approval UI Pattern** (reusable):
   - Dana's dashboard: pending agent recommendations → approve/defer/override
   - Feedback capture: Dana's corrections logged for reinforcement learning
   - Approval audit trail: who approved what, when
   - **Reused in Wave 2**: Insurance verification agent will use same HITL pattern for re-verification edge cases

4. **Pattern Learning Pipeline** (reusable concept):
   - Ingest historical data → extract patterns → store in structured DB
   - Learn from user corrections → update patterns → A/B test accuracy
   - Anomaly detection → flag to user for validation
   - **Reused in Wave 2**: Insurance re-verification rule learning (e.g., "Medicaid managed care always expires Q4")

**Shared Assets NOT Created** (Gaps for Wave 2):
- No Availity API integration (Wave 1 doesn't need insurance verification)
- No patient-facing UI (Wave 1 is Dana-only workflow)
- No real-time API (Wave 1 uses batch daily processing; sufficient for PA timing)

---

#### **Wave 2 — Compounding Agent (Insurance Re-Verification)** [Months 5-9]
**Agent**: Insurance Re-Verification Agent  
**Purpose**: Enforce Dana's >6mo re-verification rule; prevent billing failures  
**Timeline**:
- Month 5: Start build (overlaps with Wave 1 learning phase)
- Months 6-7: Build (athenahealth + Availity integration, rule encoding)
- Month 8: Validation (Dana reviews re-verification triggers for 1 month)
- Month 9+: Production (agent auto-triggers re-verifications)

**Reuses from Wave 1**:
1. ✅ **athenahealth API Client**: Same OAuth auth, error handling, retry logic
2. ✅ **Agent Activity Logging Framework**: Same structured logs, retention policy
3. ✅ **HITL Approval UI**: Same approval pattern (Dana reviews edge cases)
4. ✅ **Pattern Learning Pipeline**: Learns sub-rules (e.g., "Medicaid → verify every 3 months")

**New Integrations Built**:
1. **Availity API**: Insurance eligibility verification (REST API)
   - Read: Patient eligibility status, coverage details, error codes
   - Interpret: 30% failure cases (error code → re-verification logic)
2. **athenahealth Insurance Module**: Read last verification date, write re-verification status

**Shared Assets Created** (for Wave 3):
- **Availity API Client**: Auth, error handling, retry logic (reusable if Wave 3+ needs insurance data)
- **Insurance Verification Rule Engine**: Encodes Dana's re-verification logic (reusable if practice adds new verification rules)

---

#### **Wave 3 — Highest ROI Agent (Medication Reconciliation)** [Months 13-17]
**Agent**: Medication Reconciliation Agent  
**Purpose**: Flag med list discrepancies across athenahealth, DoseSpot, patient verbal; reduce physician review time from 6 min → 30 sec  
**Timeline**:
- Months 13-14: Build (athenahealth + DoseSpot integration, discrepancy detection logic)
- Month 15: Pilot (1 month with physician feedback loop)
- Month 16+: Production (agent flags all discrepancies, physician reviews before visit)

**Reuses from Wave 1-2**:
1. ✅ **athenahealth API Client**: Read patient med list, allergy list; write reconciliation notes
2. ✅ **Agent Activity Logging Framework**: Same logs
3. ✅ **HITL Approval UI**: Physician reviews flagged discrepancies (similar to Dana's PA approval flow)

**New Integrations Built**:
1. **DoseSpot API**: Pharmacy fill history (integrated with athenahealth, but separate API endpoints)
   - Read: Recent fills (past 6 months), dosage, fill dates
2. **Patient Questionnaire API**: athenahealth questionnaire module (read patient-reported meds)

**Shared Assets Created** (for future waves):
- **Multi-Source Reconciliation Engine**: Compare 3 data sources, flag discrepancies (reusable for other reconciliation tasks: allergies, problem list, care team)

---

#### **Wave 4 (Optional, Deferred) — High-Risk Agent (Visit Reason Triage)** [Month 18+]
**Agent**: Visit Reason Triage Agent  
**Purpose**: Standardize triage across 4-person front-desk team; flag ambiguous cases for Dana/physician review  
**Timeline**: TBD (pending malpractice carrier approval [A15])

**Reuses from Wave 1-3**:
1. ✅ **athenahealth API Client**: Read visit reason from questionnaire
2. ✅ **Agent Activity Logging Framework**: Audit trail for clinical flags
3. ✅ **HITL Approval UI**: Dana/physician reviews all flagged cases

**New Requirements**:
1. **Clinical NLP**: Keyword extraction (chest pain, SOB, bleeding, severe, sudden, can't) + sentiment analysis
2. **Escalation Rule Engine**: Bright-line rules for what triggers escalation (conservative; favor false positives over false negatives)
3. **Malpractice Compliance**: Human review required for all clinical flags (per A15 assumption)

**Prerequisites**:
- Dana obtains malpractice carrier approval for AI-assisted triage
- Waves 1-3 validate governance model (logging, audit, human oversight)
- Physician feedback loop established (calibrate false positive rate)

---

### Integration Reuse Matrix

| Integration / Asset | Wave 1 (PA Chase) | Wave 2 (Insurance) | Wave 3 (Med Recon) | Wave 4 (Triage) | Notes |
|--------------------|-------------------|-------------------|-------------------|----------------|-------|
| **athenahealth API Client** | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | Shared OAuth, error handling, retry logic → reduces Wave 2-4 build time by ~2 weeks each |
| **Availity API Client** | | ✓ Build | | | Only Wave 2 needs insurance verification |
| **DoseSpot API Integration** | | | ✓ Build | | Only Wave 3 needs pharmacy data |
| **Google Sheets API** | ✓ Build | | | | One-time ingest (Wave 1 only); not reused |
| **Agent Activity Logging** | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | Platform-level shared asset; all agents log to same format |
| **HITL Approval UI** | ✓ Build | ✓ Reuse | ✓ Reuse | ✓ Reuse | Reduces Wave 2-4 UI build time; consistent UX for Dana |
| **Pattern Learning Pipeline** | ✓ Build (insurer SLAs) | ✓ Reuse (verification rules) | | | Concept reused; implementation differs per domain |
| **Clinical NLP Module** | | | | ✓ Build | Only Wave 4 needs NLP (if pursued) |

**Compounding Effect**:
- **Wave 1 build time**: 2 months (no shared assets exist yet)
- **Wave 2 build time**: 2 months (saves ~3 weeks by reusing athenahealth client, HITL UI, logging)
- **Wave 3 build time**: 2 months (saves ~4 weeks by reusing athenahealth + HITL + logging)
- **Wave 4 build time** (if pursued): 3 months (clinical NLP is new; but reuses all platform assets)

**Maximizing the Matrix**: Every shared asset reduces marginal cost of future agents. Focus Wave 1-2 on building robust, reusable platform components (athenahealth client, logging, HITL UI), not just agent-specific logic.

---

## Summary: Agent Mapping Complete

This document provides the full specification for the **PA Chase Timing & Denial Management Agent** (Wave 1), covering:

1. ✅ **Agent Purpose Document**: Job to be Done, objectives, KPIs, failure modes, delegation archetype, escalation triggers
2. ✅ **Agent Activity Catalog**: 20 micro-tasks with delegation levels, data requirements, tool requirements, risk levels
3. ✅ **Autonomy Matrix**: What agent decides alone, what requires Dana approval, what escalates to Dana
4. ✅ **System and Data Inventory**: athenahealth, Google Sheet, insurer portals, pattern library, activity logs (5 systems)
5. ✅ **Context Engineering Design**: Memory architecture (4 types), retrieval strategy, prompt engineering principles (7 principles)
6. ✅ **Compounding Roadmap**: Wave 1-4 sequencing, integration reuse matrix, shared assets built vs. reused

**Next Steps**:
1. Obtain Dana's full historical Google Sheet (past 2-3 years of PA data)
2. Provision athenahealth API keys (OAuth 2.0 credentials)
3. Begin Wave 1 build: Google Sheet ingestion, pattern extraction, agent architecture
4. Schedule kick-off meeting with Dana: explain learning phase (3-6 months), set expectations for daily approval workflow
5. Design HITL approval UI mockup for Dana's review

**Implementation-Ready**: This agent mapping document serves as the input to the development team. No further scoping required before build begins.

---

**End of Agent Mapping: PA Chase Timing Agent (Wave 1)**
