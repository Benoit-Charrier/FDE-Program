"""
Redline generation and approval gate: generates redlines from approved fallback language only,
and enforces lawyer sign-off before release.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from src.data_contracts import (
    ContractReviewResult, RedlineProposal, ApprovalRecord, 
    ReleasablePackage, ClauseStatus, ApprovalStatus, RouteDecision
)


def generate_redlines(
    contract_result: ContractReviewResult,
    playbook: dict
) -> List[RedlineProposal]:
    """
    Generate redline proposals ONLY for playbook_negotiable deviations.
    Only use approved fallback language from the playbook.
    Never invent language.
    """
    redlines = []
    
    # Only generate redlines for playbook_negotiable contracts
    if contract_result.route_decision != RouteDecision.PLAYBOOK_NEGOTIABLE:
        return redlines
    
    clause_families_config = playbook.get("clause_families", {})
    
    for clause in contract_result.extracted_clauses:
        if clause.status != ClauseStatus.NEGOTIABLE_DEVIATION:
            continue
        
        family_config = clause_families_config.get(clause.family, {})
        fallback_options = family_config.get("fallback_language", [])
        
        # Use the first (default) approved fallback for this clause family
        if fallback_options:
            fallback = fallback_options[0]
            redline = RedlineProposal(
                clause_family=clause.family,
                current_language=clause.source_text,
                proposed_language=fallback.get("language", ""),
                playbook_fallback_reference=fallback.get("id", ""),
                rationale=fallback.get("rationale", "")
            )
            redlines.append(redline)
    
    return redlines


def create_approval_packet(
    contract_result: ContractReviewResult,
    redlines: List[RedlineProposal]
) -> dict:
    """
    Create a package ready for lawyer review and approval.
    """
    return {
        "contract_id": contract_result.contract_id,
        "filename": contract_result.filename,
        "route_decision": contract_result.route_decision.value,
        "extracted_clauses": [
            {
                "family": c.family,
                "source_text": c.source_text[:200],  # Truncate for readability
                "page": c.page_number,
                "confidence": c.confidence_score,
                "status": c.status.value
            }
            for c in contract_result.extracted_clauses
        ],
        "redline_proposals": [
            {
                "id": str(uuid.uuid4()),
                "clause_family": r.clause_family,
                "current": r.current_language[:100],
                "proposed": r.proposed_language[:100],
                "rationale": r.rationale
            }
            for r in redlines
        ],
        "approvals_required": len(redlines),
        "approvals_received": 0,
        "status": "pending_approval"
    }


def check_release_eligibility(
    contract_result: ContractReviewResult,
    redlines: List[RedlineProposal],
    approvals: List[ApprovalRecord]
) -> tuple[bool, Optional[str]]:
    """
    Enforce the hard control: check if package is eligible for release.
    Returns (is_eligible, block_reason).
    
    Rules:
    1. STANDARD contracts with no redlines: releasable immediately
    2. PLAYBOOK_NEGOTIABLE contracts: releasable only if all redlines have approval
    3. SENIOR_LAWYER_ESCALATION contracts: NOT releasable (must stay with lawyer)
    """
    
    # Rule 1: Escalations are NEVER releasable
    if contract_result.route_decision == RouteDecision.SENIOR_LAWYER_ESCALATION:
        return (
            False,
            "Contract routed to senior lawyer escalation; cannot be released by agent"
        )
    
    # Rule 2: Standard contracts with no redlines are immediately releasable
    if contract_result.route_decision == RouteDecision.STANDARD and not redlines:
        return (True, None)
    
    # Rule 3: Playbook-negotiable contracts require approvals for all redlines
    if contract_result.route_decision == RouteDecision.PLAYBOOK_NEGOTIABLE:
        if not redlines:
            return (True, None)
        
        # Each redline must have an approval
        if len(approvals) < len(redlines):
            missing = len(redlines) - len(approvals)
            return (
                False,
                f"Missing {missing} lawyer approval(s) for redlines. {len(approvals)}/{len(redlines)} approved."
            )
        
        # All approvals must be APPROVED status
        if all(a.approval_status == ApprovalStatus.APPROVED for a in approvals):
            return (True, None)
        else:
            rejected = [a.clause_family for a in approvals if a.approval_status == ApprovalStatus.REJECTED]
            return (
                False,
                f"Redlines rejected for: {', '.join(rejected)}"
            )
    
    return (False, "Unknown route decision")


def create_releasable_package(
    contract_result: ContractReviewResult,
    redlines: List[RedlineProposal],
    approvals: List[ApprovalRecord]
) -> ReleasablePackage:
    """
    Create a package that enforces the release control gate.
    """
    is_eligible, block_reason = check_release_eligibility(
        contract_result,
        redlines,
        approvals
    )
    
    package = ReleasablePackage(
        contract_review_result=contract_result,
        clause_approvals=approvals,
        is_releasable=is_eligible,
        release_block_reason=block_reason,
        prepared_for_release_timestamp=datetime.utcnow() if is_eligible else None
    )
    
    return package
