# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Purpose**: Enterprise agent design for Westbridge Family Medicine patient intake automation

**Methodology**: ATX Assessment Framework (Phases 2-4: Cognitive Mapping → Delegation Qualification → Candidate Prioritization → Agent Mapping)

**Current Status**: Wave 1 (PA Chase Timing Agent) - Core logic complete, specifications finalized, ready for integration work

---

## Project Structure

```
/week2/
├── specs/                           # Requirements & design (source of truth)
│   ├── scenario5-cognitive-map.md              # Phase 2: 4 JtDs, cognitive zones
│   ├── scenario5-delegation-qualification.md   # Phase 3: Suitability scoring
│   ├── scenario5-phase4-prioritization.md      # Phase 4: Wave sequencing, TCO
│   ├── scenario5-agent-mapping-pa-chase.md     # ⭐ AGENT SPEC (Wave 1)
│   └── cognitive-topology.mermaid.md           # Visual diagrams
│
├── agent-pa-chase/                  # ⭐ Wave 1 Implementation
│   ├── src/
│   │   ├── models.py                # Data models (PA, recommendations, patterns)
│   │   ├── pattern_library.py       # Insurer SLA storage (6 insurers seeded)
│   │   └── chase_engine.py          # Core reasoning (deterministic logic)
│   ├── data/mock_pa_data.py         # 8 sample PA cases
│   ├── tests/test_agent.py          # Test suite (all passing)
│   └── README.md                    # Architecture & next steps
│
├── build-loop/                      # Iteration tracking
│   ├── BUILD-LOOP.md                # Index of all iterations (001-005)
│   └── iteration-*.md               # Detailed iteration logs
│
└── input-docs/                      # ATX methodology reference
    ├── atx-assessment.md            # Phase 2-4 process
    ├── atx-agent-mapping.md         # 6 deliverables framework
    └── scenario5.md                 # Original business case
```

---

## Architecture: PA Chase Timing Agent

### Design Philosophy

**Deterministic core** - Chase timing is pure math: `submission_date + (SLA - 1) days`
- No LLM for core logic (predictable, testable, zero token cost)
- LLM optional for denial reason interpretation (future)

**Escalation-first** - Check escalation triggers before calculating timing
- Unpredictable insurers (Aetna) → escalate immediately
- Urgent cases (<3 days before procedure) → flag Dana
- Unknown insurers → escalate (don't guess patterns)

**Learning phase design** - Agent learns from Dana's corrections (3-6 months)
- Initial: Dana approves all recommendations
- Production: Agent handles predictable insurers autonomously, escalates 20%

### Key Components

**PatternLibrary** (`src/pattern_library.py`)
- Stores insurer-specific SLA patterns (Humana=6d, UHC=7d, Aetna=unpredictable)
- Seeded with Dana's 11 years of institutional knowledge
- Classifies insurers: predictable vs. unpredictable
- Method: `get_pattern(insurer)` → `InsurerPattern` or `None`

**ChaseEngine** (`src/chase_engine.py`)
- Main entry: `generate_recommendation(pa, current_date)` → `ChaseRecommendation`
- Decision tree:
  1. Check escalation triggers (Aetna, urgent, denied, unknown)
  2. Retrieve insurer pattern from library
  3. Calculate chase date (submission + SLA - 1, min day 3)
  4. Generate action: WAIT | RECOMMEND_CHASE | ESCALATE | URGENT
- Anomaly detection: >2 day deviation from predicted approval
- Correction learning: Log Dana's overrides for pattern updates

**Models** (`src/models.py`)
- `PriorAuthorization`: PA case data (patient, insurer, dates, status)
- `ChaseRecommendation`: Agent output (action, rationale, chase_date, confidence)
- `InsurerPattern`: SLA pattern (days, confidence, variance, is_predictable)
- `DenialPattern`: Denial workarounds (Wellpath colonoscopy → attach prior visit note)

---

## Commands

### Run Tests
```bash
cd agent-pa-chase
python3 tests/test_agent.py
```

**Expected**: 5 tests pass (pattern library, 8 PA recommendations, anomaly detection, corrections, JSON format)

### Test Single Component
```python
# In Python REPL
import sys
sys.path.append('agent-pa-chase')

from src import PatternLibrary, ChaseEngine, PriorAuthorization, PAStatus
from datetime import date, timedelta

# Test pattern retrieval
library = PatternLibrary()
humana = library.get_pattern("Humana")
print(f"Humana SLA: {humana.sla_days} days")

# Test chase recommendation
engine = ChaseEngine(library)
pa = PriorAuthorization(
    pa_id="TEST-001",
    patient_id="PT-001",
    patient_name="Test Patient",
    insurer="Humana",
    procedure_type="Colonoscopy",
    procedure_date=date.today() + timedelta(days=3),
    submission_date=date.today() - timedelta(days=6),
    status=PAStatus.PENDING
)
rec = engine.generate_recommendation(pa, current_date=date.today())
print(rec.to_json())
```

---

## Critical Design Constraints

### Validated Assumptions
All assumptions are tagged `[A#]` in specs (see `scenario5-cognitive-map.md` Section 5)

**HIGH confidence (coach-validated)**:
- `[A2]`: PA pattern stability (insurers change SLAs slowly; Humana stable 2+ years)
- `[A3]`: Re-verification rule: >6mo + chronic patient (≥3 visits/year)
- `[A4]`: Denial patterns learnable (Wellpath colonoscopy: 30-40 cases, 100% consistent)
- `[A7]`: Dana's Google Sheet is authoritative source (not athenahealth)

**Do not change without user approval**:
- Escalation logic (defined in agent mapping Section 3: Autonomy Matrix)
- Insurer patterns (seeded from Dana's validated data)
- Chase date calculation formula (submission + SLA - 1, min day 3)
- Anomaly threshold (2 days)

### Guardrails
1. **Never chase before day 3** - Insurers don't process instantly
2. **Always escalate Aetna** - No stable pattern; agent can't learn reliable timing
3. **Anomaly detection → Dana approval** - Don't auto-update patterns
4. **Learning phase = 100% HITL** - Dana approves all recommendations initially

---

## Specifications Are Source of Truth

**Before implementing features**, consult:
1. `specs/scenario5-agent-mapping-pa-chase.md` (agent requirements)
   - Section 1: Purpose, KPIs, failure modes, escalation triggers
   - Section 2: Activity Catalog (20 micro-tasks)
   - Section 3: Autonomy Matrix (4-level decision authority)
   - Section 4: System Inventory (athenahealth, Google Sheet, pattern library)
   - Section 5: Context Engineering (memory, retrieval, prompts)

2. `specs/scenario5-phase4-prioritization.md` (wave sequencing, TCO)
   - Wave 1: PA Chase (Dana's #1 priority)
   - Wave 2: Insurance Re-Verification (high ROI)
   - Wave 3: Med Reconciliation (highest ROI)
   - Wave 4: Visit Triage (deferred, clinical risk)

3. `agent-pa-chase/README.md` (implementation status, next steps)

**If specs are ambiguous**: Ask user, don't invent requirements

---

## Integration Points (Not Yet Built)

### athenahealth API
- **Needed for**: PA submission/status queries, patient data
- **Current state**: Mock data only
- **When implementing**: Refer to agent mapping Section 4 (System Inventory) for:
  - OAuth 2.0 flow
  - Rate limits (assume 100 req/min)
  - Batch query strategy (daily, not real-time)
  - Error handling (retry logic, circuit breaker)

### Google Sheets API
- **Needed for**: Historical pattern ingestion (one-time, Wave 1 build)
- **Current state**: Not implemented
- **When implementing**: Extract insurer patterns from Dana's sheet (Artefact 5.1 format)
  - Columns: Submission Date | Insurer | Procedure | Status | Target Chase Date | Notes
  - Pattern extraction: Group by insurer, calculate median approval time

### HITL Approval UI
- **Needed for**: Dana's learning phase workflow
- **Current state**: Not implemented
- **When implementing**: Refer to agent mapping Section 5 (Context Engineering)
  - Display pending recommendations
  - Approve/defer/override actions
  - Feedback capture (corrections logged for reinforcement learning)

---

## Iteration Tracking

**After significant work**, update `build-loop/BUILD-LOOP.md`:
1. Add row to iteration summary table
2. Create `iteration-XXX.md` documenting decisions, emergent findings
3. Update "Last Updated" timestamp

**Format**:
```markdown
| [XXX](iteration-XXX.md) | YYYY-MM-DD | [Focus] | [Artifacts] | ✅ Complete |
```

---

## Wave Sequencing Context

**Wave 1 (Current)**: PA Chase Timing (Months 1-8)
- Core logic: ✅ Complete (deterministic chase calculation)
- Integrations: ⏳ Not started (athenahealth, Google Sheets)
- Builds shared assets: athenahealth client, HITL UI, activity logging

**Wave 2**: Insurance Re-Verification (Months 5-9)
- Reuses Wave 1 athenahealth client
- Adds Availity API integration

**Wave 3**: Medication Reconciliation (Months 13-17)
- Reuses Wave 1-2 platform assets
- Adds DoseSpot integration

**Compounding strategy**: Each wave reuses prior integrations, reducing marginal cost

---

## Working with Specs

### Assumption References
Assumptions are cross-referenced with `[A#]` tags throughout specs:
- `[A2]`: PA pattern stability
- `[A3]`: Re-verification rule (>6mo + chronic patient)
- `[A4]`: Denial patterns learnable
- `[A7]`: Google Sheet authoritative

**To find assumption details**: See `scenario5-cognitive-map.md` Section 5 (Assumption Register)

### Decision Traceability
Major decisions documented in:
- `build-loop/BUILD-LOOP.md` → "Key Decisions Made" section
- Individual `iteration-XXX.md` files → "What Emerged" sections
- Agent mapping → Rationale fields explain why certain approaches were chosen

---

## Testing Philosophy

**Mock data is realistic** - Based on Artefact 5.1 (Dana's Google Sheet sample)
- Insurer patterns validated through coach role-play
- 8 sample PAs cover all decision paths (chase, wait, escalate, urgent)

**Don't invent**:
- Insurer patterns not validated in specs
- Business rules not in agent mapping
- Edge cases not documented

**Do test**:
- All escalation triggers
- Chase calculation edge cases (day 3 guardrail, SLA variations)
- Anomaly detection thresholds
- Pattern update logic

---

## Quick Reference

### Key Files Priority
1. `specs/scenario5-agent-mapping-pa-chase.md` - Agent requirements (read first)
2. `agent-pa-chase/src/chase_engine.py` - Core logic (start here for code)
3. `agent-pa-chase/README.md` - Implementation status
4. `build-loop/BUILD-LOOP.md` - Project history

### Common Patterns
**Adding new insurer**: Update `PatternLibrary._seed_initial_patterns()` + add test case

**Adding escalation trigger**: Update `ChaseEngine._check_escalation_triggers()` + document in agent mapping Section 1

**Modifying chase logic**: Must align with agent mapping Section 2 (Activity Catalog) + update tests

---

**Last Updated**: 2026-04-30 (Iteration 005 complete - Core agent logic implemented)
