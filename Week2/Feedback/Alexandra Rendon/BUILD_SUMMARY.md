# PA Chase Timing Agent - Build Summary

**Date**: 2026-04-29  
**Status**: ✅ Core Logic Complete & Tested  
**What was asked**: Build the agent described in the agent mapping file

---

## 1. What I Built Confidently (Complete ✅)

### A. Core Agent Components (Python)

**Data Models** (`src/models.py`):
- `PriorAuthorization` - PA case representation
- `ChaseRecommendation` - Agent output with JSON serialization
- `InsurerPattern` - Learned SLA patterns (6 insurers seeded)
- `DenialPattern` - Denial workarounds (Wellpath colonoscopy pattern)
- Supporting enums (PAStatus, ActionType, ConfidenceLevel)

**Pattern Library** (`src/pattern_library.py`):
- Seeded with Dana's patterns from Artefact 5.1:
  - Humana: 6 days (always, never 5)
  - UHC: 7 days (changed from 5 days 18 months ago)
  - BCBS PPO: 3 days (fast)
  - Medicare: 5 days
  - Wellpath: 7 days + colonoscopy denial pattern
  - Aetna: 5 days median but unpredictable (LOW confidence, escalate)
- Methods: get_pattern(), update_pattern(), find_denial_pattern()
- Classification: predictable vs. unpredictable insurers

**Chase Engine** (`src/chase_engine.py`):
- **Main entry**: `generate_recommendation(pa, current_date)` → ChaseRecommendation
- **Escalation triggers** (from agent mapping Section 1):
  1. Unpredictable insurer (Aetna) → escalate
  2. Urgent (<3 days before procedure) → urgent flag
  3. Denied status → escalate with denial pattern match
  4. Unknown insurer → escalate
- **Chase calculation**: submission_date + (SLA - 1) days
- **Predicted approval**: submission_date + SLA days
- **Guardrail**: Never chase before day 3
- **Anomaly detection**: >2 day deviation from predicted
- **Dana correction processing**: Log for pattern learning

**Mock Data** (`data/mock_pa_data.py`):
- 8 sample PA cases covering all recommendation types:
  1. Humana colonoscopy (chase now - 6 days elapsed)
  2. UHC MRI (wait - needs 2 more days)
  3. Wellpath colonoscopy DENIED (escalate with workaround)
  4. Aetna cardiac test (escalate - unpredictable)
  5. BCBS CT scan (chase now - 3 days elapsed)
  6. Medicare knee surgery (wait - 1 more day)
  7. Humana MRI URGENT (procedure in 2 days)
  8. Cigna PT (escalate - unknown insurer)

**Test Suite** (`tests/test_agent.py`):
- ✅ Pattern library retrieval (6 insurers, 1 denial pattern)
- ✅ Chase recommendations for all 8 sample PAs (all logic paths tested)
- ✅ Anomaly detection (Humana 4 days late → flag)
- ✅ Dana correction logging
- ✅ JSON output format validation

**Test Results**: All tests passing ✅

---

## 2. What Needs Clarification Before Building the Rest

### A. Technology Stack Decisions

**Question 1: Integration Approach**
- Real athenahealth API integration (need OAuth credentials)?
- Real Google Sheets API (need Dana's sheet access)?
- OR continue with mock data for prototype demo?

**Question 2: Storage/Persistence**
- **Pattern library**: JSON file, SQLite, PostgreSQL, or other?
- **Episodic memory** (Dana's corrections): Vector DB (ChromaDB, Pinecone) or simple database?
- **Activity logs**: Structured logging to file, database, or logging service?

**Question 3: HITL Approval Interface**
- Web app (Flask/FastAPI/React)?
- CLI tool (terminal-based)?
- OR just backend API for now (manual testing)?

**Question 4: LLM Integration**
- Should I integrate Claude API for:
  - Denial reason interpretation (semantic understanding)?
  - Natural language rationale generation?
  - Enhanced pattern matching?
- OR keep pure deterministic logic (current approach)?

### B. Deployment Scope

**Question 5: What's the immediate goal?**
- [ ] Full production-ready agent with UI + real APIs?
- [ ] Prototype demo with mock data (current state)?
- [ ] Integration spike (connect to real athenahealth sandbox)?
- [ ] Focus on UI mockup for Dana's approval workflow?

---

## 3. What I Can Build Next (Based on Your Answers)

### Option A: Real API Integration
**If you provide:**
- athenahealth API credentials (OAuth 2.0, practice ID, endpoints)
- Google Sheets API credentials (service account or OAuth)

**I can build:**
- `src/athena_client.py` - athenahealth API wrapper (OAuth, PA queries, status updates)
- `src/google_sheets_client.py` - Historical pattern ingestion from Dana's sheet
- Integration tests with real data
- **Timeline**: 4-6 hours

### Option B: HITL Web Dashboard
**If you choose:** Flask/FastAPI + simple HTML/JS frontend

**I can build:**
- Web app with Dana's approval workflow:
  - List pending PA recommendations
  - Approve/defer/override buttons
  - Correction feedback form
  - Weekly summary view
- Backend API endpoints
- **Timeline**: 6-8 hours

### Option C: Database Persistence
**If you choose:** SQLite (simple) or PostgreSQL (production-grade)

**I can build:**
- Database schema (insurers, patterns, PAs, corrections, logs)
- Migration scripts
- Updated PatternLibrary to read/write from DB
- Correction tracking with episodic memory storage
- **Timeline**: 3-4 hours

### Option D: Claude API Integration
**If you provide:** Anthropic API key

**I can build:**
- `src/llm_reasoner.py` - Claude API wrapper
- Enhanced denial reason interpretation (semantic search)
- Natural language explanation generation
- Chain-of-thought reasoning for edge cases
- **Timeline**: 2-3 hours

### Option E: End-to-End Demo Script
**No additional info needed**

**I can build:**
- Simulation script: Generate 30 days of PA data, run agent daily, track accuracy
- Dana correction simulator (realistic feedback patterns)
- Metrics dashboard (accuracy per insurer, escalation rate, anomaly detection)
- Visual timeline of recommendations → approvals → accuracy scores
- **Timeline**: 2-3 hours

---

## Current File Structure

```
/agent-pa-chase/
├── README.md                  # Full documentation
├── BUILD_SUMMARY.md          # This file
├── src/
│   ├── __init__.py           # Module exports
│   ├── models.py             # Data models (450 lines)
│   ├── pattern_library.py    # Pattern storage (150 lines)
│   └── chase_engine.py       # Core reasoning (250 lines)
├── data/
│   └── mock_pa_data.py       # 8 sample PAs
├── tests/
│   └── test_agent.py         # Comprehensive test suite
└── config/                   # Empty (ready for API keys, DB config)
```

---

## Key Architecture Decisions Made

1. **Deterministic core logic** (no LLM for chase calculation)
   - Chase date = pure math (submission + SLA - 1)
   - Escalation triggers = explicit if/then rules
   - **Why**: Predictable, testable, zero token cost, fast
   - **LLM optional**: For denial reason interpretation, natural language explanations

2. **In-memory pattern library** (prototype)
   - Production: Migrate to database with versioning
   - **Why**: Simplest for testing; easy to add persistence later

3. **Clean separation of concerns**
   - Models = data structures only
   - PatternLibrary = storage/retrieval only
   - ChaseEngine = reasoning only (no I/O)
   - **Why**: Testable, maintainable, swappable components

4. **Escalation-first design**
   - Check escalation triggers before calculating chase timing
   - **Why**: Safety first (urgent cases, unpredictable insurers)
   - Matches agent mapping Section 3 (Autonomy Matrix)

5. **Anomaly detection = 2 day threshold**
   - Flags SLA changes (e.g., Humana suddenly 5 days instead of 6)
   - Requires Dana validation before pattern update
   - **Why**: Prevents agent from auto-updating without human review

---

## Demonstrated Capabilities ✅

From the test run:

1. ✅ **Pattern retrieval**: 6 insurers loaded, 1 denial pattern matched
2. ✅ **Chase recommendations**: 
   - PA-001 (Humana): RECOMMEND_CHASE (overdue by 1 day)
   - PA-002 (UHC): WAIT (needs 2 more days)
   - PA-005 (BCBS): RECOMMEND_CHASE (3 days elapsed, fast insurer)
   - PA-006 (Medicare): RECOMMEND_CHASE (close to 5-day SLA)
3. ✅ **Escalations**:
   - PA-003 (Wellpath DENIED): Escalate with workaround suggestion
   - PA-004 (Aetna): Escalate (unpredictable insurer)
   - PA-007 (Humana): URGENT (procedure in 2 days)
   - PA-008 (Cigna): Escalate (unknown insurer)
4. ✅ **Anomaly detection**: Humana approved 4 days late → flag for review
5. ✅ **Correction learning**: Dana pushes chase 2 days later → logged for pattern review
6. ✅ **JSON output**: Clean structured format matching agent mapping spec

---

## Success Metrics (Trackable Now)

With current build:
- ✅ Pattern accuracy (predicted vs. actual approval date)
- ✅ Escalation rate (% PAs escalated to Dana)
- ✅ Anomaly detection rate (% approvals >2 days from predicted)
- ✅ Denial pattern match rate (% denials matched to known workarounds)

With real data (future):
- ⏳ Dana's time savings (1.5-2 hours/day → 15 min/day)
- ⏳ Visit abort prevention (target: 0 from PA timing misses)
- ⏳ Chase timing accuracy (target: 90% within ±1 day)

---

## What Should We Build Next?

**My Recommendation**: **Option E** (End-to-End Demo Script)

**Why**:
- No external dependencies needed (runs standalone)
- Demonstrates full agent lifecycle:
  - Day 1: Agent recommends chase dates
  - Day 6: Simulated approvals arrive
  - Agent calculates accuracy
  - Dana corrections logged
  - Pattern updates proposed
- Visual metrics dashboard
- Proves agent works before investing in UI/integrations
- **Timeline**: 2-3 hours

**Alternative**: If you want to **see the UI first** → **Option B** (Web Dashboard)

---

## Questions for You

1. **What's your immediate priority?**
   - Demo the agent logic with simulated data? (Option E)
   - See the UI/UX for Dana's approval workflow? (Option B)
   - Connect to real athenahealth sandbox? (Option A)
   - Something else?

2. **Technology preferences?**
   - Database: SQLite (simple) or PostgreSQL (production)?
   - Web framework: Flask (simple) or FastAPI (modern)?
   - LLM integration: Yes (need API key) or No (keep deterministic)?

3. **Timeline expectations?**
   - Quick prototype (stay with mock data, add demo script)?
   - Production-ready (full integrations, database, UI)?
   - Somewhere in between?

Let me know your answers and I'll build the next piece!

---

**Status**: Core agent logic complete and tested ✅  
**Next**: Awaiting direction on integrations, UI, or demo script
