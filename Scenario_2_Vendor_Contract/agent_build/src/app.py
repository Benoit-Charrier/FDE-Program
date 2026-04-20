"""
FastAPI application: orchestrates the contract review workflow.
"""

import os
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from src.ingestion import ingest_contract
from src.extraction_and_routing import analyze_contract, load_playbook
from src.redline_and_approval import generate_redlines, create_releasable_package, check_release_eligibility
from src.data_contracts import ApprovalRecord, ApprovalStatus
from src.audit import AuditLogger

app = FastAPI(
    title="Vendor Contract Review Agent",
    version="0.1.0",
    description="AI-assisted first-pass vendor contract review with legal playbook enforcement"
)

# Initialize audit logger (in-memory by default, use persistent DB in production)
audit_logger = AuditLogger(db_path="./audit.db")

# Load playbook
PLAYBOOK_PATH = os.getenv("PLAYBOOK_PATH", "./config/playbook.sample.yaml")
playbook = load_playbook(PLAYBOOK_PATH)

# API key
API_KEY = os.getenv("ANTHROPIC_API_KEY")


@app.post("/analyze")
async def analyze_contract_endpoint(
    file: UploadFile = File(...),
    metadata_vendor_name: str = None,
    metadata_contract_type: str = None
):
    """
    Analyze an uploaded vendor contract.
    Returns contract review result with routing decision and redline proposals.
    """
    if not API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
    
    contract_id = str(uuid.uuid4())
    temp_path = f"/tmp/{contract_id}_{file.filename}"
    
    try:
        # Save uploaded file
        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Audit: ingestion started
        audit_logger.log(
            event_type="ingestion_started",
            contract_id=contract_id,
            event_details={
                "filename": file.filename,
                "content_type": file.content_type,
                "size_bytes": len(contents),
                "vendor_name": metadata_vendor_name,
                "contract_type": metadata_contract_type
            }
        )
        
        # Ingest contract
        contract_text, page_count, file_type = ingest_contract(temp_path)
        
        audit_logger.log(
            event_type="ingestion_complete",
            contract_id=contract_id,
            event_details={
                "file_type": file_type,
                "page_count": page_count,
                "text_length": len(contract_text)
            }
        )
        
        # Analyze contract
        result = analyze_contract(
            contract_id=contract_id,
            filename=file.filename,
            file_size_bytes=len(contents),
            contract_text=contract_text,
            page_count=page_count,
            playbook_path=PLAYBOOK_PATH,
            api_key=API_KEY
        )
        
        audit_logger.log(
            event_type="extraction_complete",
            contract_id=contract_id,
            event_details={
                "route_decision": result.route_decision.value,
                "routing_confidence": result.routing_confidence,
                "clause_count": len(result.extracted_clauses),
                "escalation_reasons": result.escalation_reasons
            }
        )
        
        # Generate redlines if negotiable
        redlines = generate_redlines(result, playbook)
        
        audit_logger.log(
            event_type="redline_generation",
            contract_id=contract_id,
            event_details={
                "redline_count": len(redlines),
                "redlines": [
                    {
                        "clause_family": r.clause_family,
                        "reference": r.playbook_fallback_reference
                    }
                    for r in redlines
                ]
            }
        )
        
        return JSONResponse({
            "contract_id": contract_id,
            "filename": result.filename,
            "route_decision": result.route_decision.value,
            "routing_confidence": result.routing_confidence,
            "page_count": result.page_count,
            "extracted_clauses": [
                {
                    "family": c.family,
                    "confidence": c.confidence_score,
                    "status": c.status.value,
                    "page": c.page_number
                }
                for c in result.extracted_clauses
            ],
            "variance_summary": result.variance_summary,
            "redline_count": len(redlines),
            "escalation_reasons": result.escalation_reasons,
            "approval_packet_ready": len(redlines) > 0
        })
    
    except Exception as e:
        audit_logger.log(
            event_type="analysis_error",
            contract_id=contract_id,
            event_details={"error": str(e)},
            outcome="error"
        )
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        # Clean up temp file
        if Path(temp_path).exists():
            Path(temp_path).unlink()


@app.post("/approve-redline")
async def approve_redline(
    contract_id: str,
    clause_family: str,
    lawyer_name: str,
    lawyer_email: str,
    approval_status: str = "approved"
):
    """
    Record a lawyer approval for a redline.
    """
    approval = ApprovalRecord(
        clause_family=clause_family,
        proposed_redline_id=f"{contract_id}_{clause_family}",
        approved_by_lawyer_name=lawyer_name,
        approved_by_lawyer_email=lawyer_email,
        approval_timestamp=None,
        approval_status=ApprovalStatus(approval_status),
        notes=None
    )
    
    audit_logger.log(
        event_type="approval_recorded",
        contract_id=contract_id,
        event_details={
            "clause_family": clause_family,
            "approved_by": lawyer_name,
            "status": approval_status
        },
        actor=lawyer_name
    )
    
    return {"status": "approval_recorded", "approval": approval.dict()}


@app.post("/check-releasable")
async def check_releasable(
    contract_id: str,
    redline_count: int = 0
):
    """
    Check if a contract package is eligible for release.
    This enforces the hard control gate.
    """
    # In production, would retrieve actual contract and approvals from DB
    # For demo, just show the gate logic
    
    if redline_count == 0:
        return {
            "contract_id": contract_id,
            "is_releasable": True,
            "block_reason": None,
            "message": "Standard contract with no redlines: ready for release"
        }
    
    return {
        "contract_id": contract_id,
        "is_releasable": False,
        "block_reason": f"Missing lawyer approvals for {redline_count} redlines",
        "message": "Cannot release: waiting for lawyer sign-offs"
    }


@app.get("/audit-trail/{contract_id}")
async def get_audit_trail(contract_id: str):
    """
    Retrieve full audit trail for a contract.
    """
    trail = audit_logger.get_audit_trail(contract_id)
    return {
        "contract_id": contract_id,
        "audit_trail": trail
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
