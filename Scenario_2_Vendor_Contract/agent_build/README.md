# README - Vendor Contract Review Agent

## Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key (set `ANTHROPIC_API_KEY` environment variable)
- pip or conda for dependency management

### Installation

```bash
cd agent_build

# Create and activate virtual environment
python -m venv .venv

# PowerShell (Windows)
.\.venv\Scripts\Activate.ps1

# If script execution is restricted, use venv python directly:
# .\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Set your Anthropic API key**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
```

2. **Configure playbook location** (optional):
```bash
export PLAYBOOK_PATH="./config/playbook.sample.yaml"
# PowerShell: $env:PLAYBOOK_PATH="./config/playbook.sample.yaml"
```

The default playbook (`config/playbook.sample.yaml`) defines:
- Seven clause families (liability, DPA, termination, IP, SLA, governing law, indemnity)
- Approved patterns and fallback language for each
- Must-escalate keywords
- Confidence threshold (0.75)
- Approved jurisdictions

### Run Tests

**Quick validation of all three scenarios:**

```bash
python -m pytest tests/test_validation_scenarios.py -q
```

**Expected output:**
```
================================================================================
STARTING VALIDATION TEST SUITE
================================================================================

================================================================================
SCENARIO 1: Happy Path - Standard Contract
================================================================================
✓ Route Decision: standard
✓ Routing Confidence: 0.95
✓ Redlines Generated: 0
✓ Extracted Clauses: 7
✓ Escalation Reasons: []

✅ SCENARIO 1 PASSED: Standard contract flows through without manual intervention

[... SCENARIO 2 and 3 output ...]

================================================================================
TEST RESULTS SUMMARY
================================================================================
✅ PASS: Scenario 1: Standard Contract
✅ PASS: Scenario 2: Playbook-Negotiable
✅ PASS: Scenario 3: Delegation Boundary

✅ ALL TESTS PASSED
================================================================================
```

### Start the API Server

```bash
python -m uvicorn src.app:app --reload --port 8000
```

Server runs at `http://localhost:8000`

**OpenAPI docs**: http://localhost:8000/docs

### API Usage Examples

#### 1. Analyze a Contract

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@sample_contract.pdf" \
  -F "metadata_vendor_name=Acme Corp" \
  -F "metadata_contract_type=SaaS"
```

**Response:**
```json
{
  "contract_id": "a1b2c3d4-e5f6-4g7h-8i9j-0k1l2m3n4o5p",
  "filename": "sample_contract.pdf",
  "route_decision": "standard",
  "routing_confidence": 0.95,
  "page_count": 25,
  "extracted_clauses": [
    {
      "family": "liability",
      "confidence": 0.98,
      "status": "match",
      "page": 5
    }
  ],
  "variance_summary": "All clauses match playbook.",
  "redline_count": 0,
  "escalation_reasons": [],
  "approval_packet_ready": false
}
```

#### 2. Record Lawyer Approval

```bash
curl -X POST http://localhost:8000/approve-redline \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "a1b2c3d4-e5f6-4g7h-8i9j-0k1l2m3n4o5p",
    "clause_family": "liability",
    "lawyer_name": "Jane Doe",
    "lawyer_email": "jane@company.com",
    "approval_status": "approved"
  }'
```

#### 3. Check Release Eligibility

```bash
curl -X POST http://localhost:8000/check-releasable \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "a1b2c3d4-e5f6-4g7h-8i9j-0k1l2m3n4o5p",
    "redline_count": 0
  }'
```

**Response:**
```json
{
  "contract_id": "a1b2c3d4-e5f6-4g7h-8i9j-0k1l2m3n4o5p",
  "is_releasable": true,
  "block_reason": null,
  "message": "Standard contract with no redlines: ready for release"
}
```

#### 4. Retrieve Audit Trail

```bash
curl -X GET http://localhost:8000/audit-trail/a1b2c3d4-e5f6-4g7h-8i9j-0k1l2m3n4o5p
```

**Response:**
```json
{
  "contract_id": "a1b2c3d4-e5f6-4g7h-8i9j-0k1l2m3n4o5p",
  "audit_trail": [
    {
      "event_type": "ingestion_started",
      "timestamp": "2026-04-20T14:00:00",
      "actor": "system",
      "event_details": { "filename": "sample_contract.pdf" },
      "outcome": "success"
    },
    {
      "event_type": "extraction_complete",
      "timestamp": "2026-04-20T14:02:15",
      "actor": "system",
      "event_details": { "route_decision": "standard", "clause_count": 7 },
      "outcome": "success"
    }
  ]
}
```

## Project Structure

```
agent_build/
├── config/
│   ├── playbook.schema.json       # JSON Schema for playbook validation
│   └── playbook.sample.yaml       # Default playbook with approved language
│
├── src/
│   ├── __init__.py
│   ├── data_contracts.py          # Pydantic models (all data types)
│   ├── ingestion.py               # PDF/DOCX parsing
│   ├── extraction_and_routing.py  # Claude extraction + rules engine
│   ├── redline_and_approval.py    # Redline generator + release gate
│   ├── audit.py                   # SQLite audit logging
│   └── app.py                     # FastAPI application
│
├── tests/
│   └── test_validation_scenarios.py  # Three validation test cases
│
├── docs/
│   ├── architecture.md            # System design and decision rules
│   ├── data-contracts.md          # JSON schemas for all data types
│   └── validation-report.md       # Test results mapping to spec
│
├── pyproject.toml                 # Project metadata
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Key Design Decisions

### 1. Rule-First Architecture
- **Why**: Legal routing cannot be probabilistic. Same input must always route the same way.
- **How**: All routing logic uses deterministic `if` statements, not LLM judgment.
- **Result**: Predictable, auditable, compliant with legal standards.

### 2. Playbook-Bounded Redlines
- **Why**: Lawyers cannot approve language the agent invents. Only pre-approved fallback language is safe.
- **How**: Redline generator looks up each clause family in playbook and uses only approved fallbacks.
- **Result**: No liability from unexpected language.

### 3. Hard Release Gate
- **Why**: General counsel has a hard rule: no outbound counteroffer without lawyer sign-off.
- **How**: `check_release_eligibility()` enforces that escalated contracts cannot be released, and negotiable contracts require all redlines to be approved.
- **Result**: Impossible to bypass human approval.

### 4. Config-Driven Policies
- **Why**: Legal requirements change; code shouldn't.
- **How**: All playbook logic, thresholds, and approved language live in YAML config.
- **Result**: Legal team can update policies without engineering.

### 5. Full Audit Trail
- **Why**: Compliance requires proof of every decision and override.
- **How**: SQLite audit table logs every extraction, routing, redline, and approval with timestamp and actor.
- **Result**: Complete chain of custody for audits.

## Routing Logic

### Standard (70% of volume)
- **Trigger**: All target clauses match approved playbook patterns
- **Action**: No manual review; enters fast queue
- **Redlines**: None
- **Release**: Immediate

### Playbook-Negotiable (20% of volume)
- **Trigger**: Deviations exist but all have approved fallback language; no escalation rules triggered
- **Action**: Paralegal queue; draft redlines prepared
- **Redlines**: Generated from playbook fallbacks only
- **Release**: Only after lawyer sign-off on each redline

### Senior Lawyer Escalation (10% of volume)
- **Trigger**: Uncapped liability, missing DPA, novel clauses, low confidence, or conflicting signals
- **Action**: Sent to senior lawyer; not auto-processable
- **Redlines**: None generated
- **Release**: Manual review required; cannot be auto-released

## Performance Expectations

- **Ingestion**: <100ms for 25-page PDF
- **Extraction**: ~2s for Claude API call
- **Routing**: <10ms (deterministic rules)
- **Total**: ~2-3s per contract

**Throughput**: Can process 300 contracts/quarter (8–10 per day) with 1 API instance.

## Next Steps for Production

1. **Persistent Database**: Replace in-memory SQLite with PostgreSQL for audit trail.
2. **Integration**: Connect to actual CLM, matter management, and approval workflow systems.
3. **Monitoring**: Add Prometheus/Grafana for metrics (routing distribution, turnaround time, approval rates).
4. **Scaling**: Deploy as containerized service (Docker) with auto-scaling.
5. **Legal Review**: Have internal counsel review playbook and approved fallback language.
6. **Testing**: Calibrate extraction confidence thresholds on actual contract samples.

## Support

- **Architecture Questions**: See `docs/architecture.md`
- **Data Format Questions**: See `docs/data-contracts.md`
- **Test Coverage**: See `tests/test_validation_scenarios.py`
- **API Questions**: See OpenAPI docs at http://localhost:8000/docs
