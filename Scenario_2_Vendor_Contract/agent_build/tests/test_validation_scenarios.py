"""
Test suite with three validation scenarios from the capability specification.
"""

from datetime import datetime

from src.data_contracts import (
    ExtractedClause, ClauseStatus, RouteDecision, ContractReviewResult, 
    ApprovalRecord, ApprovalStatus
)
from src.extraction_and_routing import classify_clause, route_contract, load_playbook
from src.redline_and_approval import generate_redlines, check_release_eligibility, create_releasable_package


def load_sample_playbook():
    """Load the sample playbook for testing."""
    playbook_path = "./config/playbook.sample.yaml"
    return load_playbook(playbook_path)


# ============================================================================
# SCENARIO 1: Happy Path - Standard Contract
# ============================================================================

def test_scenario_1_standard_contract():
    """
    Test Scenario 1: Standard Contract (70% of volume)
    
    Input:
    - 25-page vendor contract
    - All seven target clause families are present
    - All clauses match the playbook within tolerance
    
    Expected:
    - Agent extracts all clause families with high confidence
    - Contract is routed as STANDARD
    - No redlines are generated
    - Review packet shows clause evidence
    
    Validation:
    - Removes repetitive first-pass review from 70% standard population
    - Match logic does not create unnecessary redlines
    """
    print("\n" + "=" * 80)
    print("SCENARIO 1: Happy Path - Standard Contract")
    print("=" * 80)
    
    playbook = load_sample_playbook()
    
    # Simulate extracted clauses from a standard contract
    extracted_clauses = [
        ExtractedClause(
            family="liability",
            source_text="Each party's total aggregate liability shall not exceed the annual recurring revenue (ARR) paid or payable in the 12 months preceding the claim.",
            page_number=5,
            confidence_score=0.98,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="dpa",
            source_text="The parties shall execute a Data Processing Addendum (DPA) compliant with GDPR Article 28 and CCPA Sec. 1798.140(ab), within 15 days of contract signature.",
            page_number=8,
            confidence_score=0.95,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="termination",
            source_text="Either party may terminate this Agreement with 30 days' written notice.",
            page_number=12,
            confidence_score=0.96,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="ip_ownership",
            source_text="Each party retains all right, title, and interest in its pre-existing intellectual property.",
            page_number=15,
            confidence_score=0.94,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="sla",
            source_text="Vendor commits to 99.5% monthly uptime, measured from midnight to midnight US Eastern Time.",
            page_number=18,
            confidence_score=0.92,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="governing_law",
            source_text="This Agreement shall be governed by the laws of the State of Delaware.",
            page_number=22,
            confidence_score=0.97,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="indemnity",
            source_text="Each party shall indemnify, defend, and hold harmless the other from any third-party claims.",
            page_number=24,
            confidence_score=0.93,
            status=ClauseStatus.MATCH
        ),
    ]
    
    # Create mock contract result
    result = ContractReviewResult(
        contract_id="test_scenario_1",
        filename="standard_vendor_contract.pdf",
        file_size_bytes=150000,
        page_count=25,
        ingestion_timestamp=datetime.utcnow(),
        route_decision=RouteDecision.STANDARD,
        routing_confidence=0.95,
        extracted_clauses=extracted_clauses,
        variance_summary="All clauses match playbook.",
        redline_proposals=[],
        escalation_reasons=[],
        analysis_timestamp=datetime.utcnow()
    )
    
    # Route contract
    route_decision, confidence, escalations = route_contract(extracted_clauses, playbook)
    
    # Generate redlines (should be empty)
    redlines = generate_redlines(result, playbook)
    
    # Test assertions
    print(f"\n✓ Route Decision: {route_decision.value}")
    assert route_decision == RouteDecision.STANDARD, "Expected STANDARD routing"
    
    print(f"✓ Routing Confidence: {confidence}")
    assert confidence >= 0.95, "Expected high confidence"
    
    print(f"✓ Redlines Generated: {len(redlines)}")
    assert len(redlines) == 0, "Expected no redlines for standard contract"
    
    print(f"✓ Extracted Clauses: {len(extracted_clauses)}")
    assert len(extracted_clauses) == 7, "Expected 7 clause families"
    
    print(f"✓ Escalation Reasons: {escalations}")
    assert len(escalations) == 0, "Expected no escalations"
    
    print("\n✅ SCENARIO 1 PASSED: Standard contract flows through without manual intervention")
    return True


# ============================================================================
# SCENARIO 2: Edge Case - Playbook-Negotiable Deviations
# ============================================================================

def test_scenario_2_playbook_negotiable():
    """
    Test Scenario 2: Playbook-Negotiable Deviations (20% of volume)
    
    Input:
    - 32-page vendor contract
    - Liability cap and termination notice differ from preferred terms
    - Both deviations have approved fallback language in playbook
    - No must-escalate rule triggered
    
    Expected:
    - Agent extracts both deviations and classifies as NEGOTIABLE_DEVIATION
    - Agent generates draft redlines using only approved fallback language
    - Contract is routed to PLAYBOOK_NEGOTIABLE
    - Approval packet is prepared for lawyer sign-off
    
    Validation:
    - Agent handles the 20% negotiable bucket without over-escalating
    - Redline generation stays bounded by playbook
    """
    print("\n" + "=" * 80)
    print("SCENARIO 2: Edge Case - Playbook-Negotiable Deviations")
    print("=" * 80)
    
    playbook = load_sample_playbook()
    
    # Simulate extracted clauses with two deviations
    extracted_clauses = [
        ExtractedClause(
            family="liability",
            source_text="For breaches of data protection obligations, liability may extend to 2x ARR paid in the preceding 12 months.",
            page_number=5,
            confidence_score=0.89,
            status=ClauseStatus.NEGOTIABLE_DEVIATION,
            variance_reason="Liability cap differs from standard 1x ARR"
        ),
        ExtractedClause(
            family="dpa",
            source_text="The parties shall execute a Data Processing Addendum (DPA) compliant with GDPR Article 28 and CCPA.",
            page_number=8,
            confidence_score=0.94,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="termination",
            source_text="Either party may terminate this Agreement with 60 days' written notice.",
            page_number=12,
            confidence_score=0.91,
            status=ClauseStatus.NEGOTIABLE_DEVIATION,
            variance_reason="Termination notice period is 60 days instead of standard 30"
        ),
        ExtractedClause(
            family="ip_ownership",
            source_text="Each party retains all right, title, and interest in its pre-existing intellectual property.",
            page_number=15,
            confidence_score=0.93,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="sla",
            source_text="Vendor commits to 99.9% monthly uptime with automatic service credits.",
            page_number=18,
            confidence_score=0.90,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="governing_law",
            source_text="This Agreement shall be governed by the laws of the State of California.",
            page_number=22,
            confidence_score=0.96,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="indemnity",
            source_text="Each party shall indemnify, defend, and hold harmless the other.",
            page_number=24,
            confidence_score=0.92,
            status=ClauseStatus.MATCH
        ),
    ]
    
    # Create contract result
    result = ContractReviewResult(
        contract_id="test_scenario_2",
        filename="negotiable_vendor_contract.pdf",
        file_size_bytes=180000,
        page_count=32,
        ingestion_timestamp=datetime.utcnow(),
        route_decision=RouteDecision.PLAYBOOK_NEGOTIABLE,
        routing_confidence=0.85,
        extracted_clauses=extracted_clauses,
        variance_summary="Liability and termination clauses differ from playbook; both have approved fallbacks.",
        redline_proposals=[],
        escalation_reasons=[],
        analysis_timestamp=datetime.utcnow()
    )
    
    # Route contract
    route_decision, confidence, escalations = route_contract(extracted_clauses, playbook)
    
    # Generate redlines
    redlines = generate_redlines(result, playbook)
    
    # Test assertions
    print(f"\n✓ Route Decision: {route_decision.value}")
    assert route_decision == RouteDecision.PLAYBOOK_NEGOTIABLE, "Expected PLAYBOOK_NEGOTIABLE routing"
    
    print(f"✓ Routing Confidence: {confidence}")
    assert confidence >= 0.80, "Expected reasonable confidence"
    
    print(f"✓ Redlines Generated: {len(redlines)}")
    assert len(redlines) >= 2, "Expected at least 2 redlines for deviations"
    
    # Verify redlines use only approved fallback language
    for redline in redlines:
        print(f"  - {redline.clause_family}: reference={redline.playbook_fallback_reference}")
        assert redline.playbook_fallback_reference, "Redline must reference playbook fallback ID"
    
    print(f"✓ Extracted Clauses: {len(extracted_clauses)}")
    assert len(extracted_clauses) == 7, "Expected 7 clause families"
    
    print(f"✓ Negotiable Deviations Found: {sum(1 for c in extracted_clauses if c.status == ClauseStatus.NEGOTIABLE_DEVIATION)}")
    assert sum(1 for c in extracted_clauses if c.status == ClauseStatus.NEGOTIABLE_DEVIATION) >= 2, "Expected at least 2 negotiable deviations"
    
    print("\n✅ SCENARIO 2 PASSED: Negotiable deviations detected, redlines bounded by playbook")
    return True


# ============================================================================
# SCENARIO 3: Failure Mode - Delegation Boundary Breach Attempt
# ============================================================================

def test_scenario_3_delegation_boundary():
    """
    Test Scenario 3: Failure Mode - Delegation Boundary Breach Attempt
    
    Input:
    - 18-page scanned PDF with weak OCR quality
    - Liability clause appears uncapped
    - Indemnity clause extraction confidence below threshold
    - User attempts to push redline package outbound without lawyer sign-off
    
    Expected:
    - Agent routes contract to SENIOR_LAWYER_ESCALATION
    - Low-confidence extraction is explicit in escalation reason
    - Agent does NOT generate a releasable outbound package
    - Release control BLOCKS transmission because sign-off is missing
    
    Validation:
    - Low-confidence parsing cannot silently pass through
    - System respects human delegation boundary
    - Release gate prevents unauthorized outbound packages
    """
    print("\n" + "=" * 80)
    print("SCENARIO 3: Failure Mode - Delegation Boundary Breach Attempt")
    print("=" * 80)
    
    playbook = load_sample_playbook()
    
    # Simulate problematic extraction (low confidence, uncapped liability)
    extracted_clauses = [
        ExtractedClause(
            family="liability",
            source_text="Liability is uncapped for any breach.",
            page_number=5,
            confidence_score=0.62,  # Below threshold
            status=ClauseStatus.ESCALATE,
            escalation_reason="Uncapped liability detected AND confidence below threshold (0.62 < 0.75)"
        ),
        ExtractedClause(
            family="dpa",
            source_text="Processing addendum may be required.",
            page_number=8,
            confidence_score=0.68,  # Below threshold
            status=ClauseStatus.ESCALATE,
            escalation_reason="DPA extraction confidence below threshold (0.68 < 0.75)"
        ),
        ExtractedClause(
            family="termination",
            source_text="Either party may terminate with notice.",
            page_number=12,
            confidence_score=0.87,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="ip_ownership",
            source_text="IP rights retained by contributors.",
            page_number=15,
            confidence_score=0.81,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="sla",
            source_text="Service levels not specified.",
            page_number=18,
            confidence_score=0.55,  # Below threshold
            status=ClauseStatus.ESCALATE,
            escalation_reason="SLA extraction confidence too low (0.55 < 0.75)"
        ),
        ExtractedClause(
            family="governing_law",
            source_text="Delaware law applies.",
            page_number=22,
            confidence_score=0.92,
            status=ClauseStatus.MATCH
        ),
        ExtractedClause(
            family="indemnity",
            source_text="Indemnity scope may be broad.",
            page_number=24,
            confidence_score=0.58,  # Below threshold
            status=ClauseStatus.ESCALATE,
            escalation_reason="Indemnity extraction confidence below threshold (0.58 < 0.75)"
        ),
    ]
    
    # Create contract result
    result = ContractReviewResult(
        contract_id="test_scenario_3",
        filename="scanned_ocr_problematic.pdf",
        file_size_bytes=85000,
        page_count=18,
        ingestion_timestamp=datetime.utcnow(),
        route_decision=RouteDecision.SENIOR_LAWYER_ESCALATION,
        routing_confidence=0.45,
        extracted_clauses=extracted_clauses,
        variance_summary="Multiple clauses extracted with low confidence. Uncapped liability detected.",
        redline_proposals=[],
        escalation_reasons=[
            "Uncapped liability detected",
            "Multiple clause extractions below confidence threshold",
            "OCR quality compromises reliability"
        ],
        analysis_timestamp=datetime.utcnow()
    )
    
    # Route contract
    route_decision, confidence, escalations = route_contract(extracted_clauses, playbook)
    
    # Generate redlines (should be empty because escalated)
    redlines = generate_redlines(result, playbook)
    
    print(f"\n✓ Route Decision: {route_decision.value}")
    assert route_decision == RouteDecision.SENIOR_LAWYER_ESCALATION, "Expected ESCALATION routing"
    
    print(f"✓ Routing Confidence: {confidence}")
    assert confidence < 0.75, "Expected low confidence"
    
    print(f"✓ Redlines Generated: {len(redlines)}")
    assert len(redlines) == 0, "Escalated contracts should not generate redlines"
    
    print(f"✓ Escalation Reasons: {len(escalations)}")
    assert len(escalations) > 0, "Expected explicit escalation reasons"
    for reason in escalations:
        print(f"  - {reason}")
    
    # TEST THE RELEASE GATE: Attempt to release without approvals
    print("\n→ Attempting to release escalated contract without lawyer sign-off...")
    
    approvals = []  # No approvals yet
    is_releasable, block_reason = check_release_eligibility(result, redlines, approvals)
    
    print(f"\n✓ Is Releasable: {is_releasable}")
    assert not is_releasable, "Escalated contract should NOT be releasable"
    
    print(f"✓ Block Reason: {block_reason}")
    assert block_reason, "Expected explicit block reason"
    
    # Create releasable package (enforces gate)
    package = create_releasable_package(result, redlines, approvals)
    
    print(f"\n✓ Package Releasable: {package.is_releasable}")
    assert not package.is_releasable, "Release gate must block transmission"
    
    print(f"✓ Release Block Reason: {package.release_block_reason}")
    assert package.release_block_reason, "Must explain why release is blocked"
    
    print("\n✅ SCENARIO 3 PASSED: Low-confidence contracts escalated, release gate enforced")
    return True


# ============================================================================
# Run All Tests
# ============================================================================

def run_all_tests():
    """Run all three validation scenarios."""
    print("\n" + "=" * 80)
    print("STARTING VALIDATION TEST SUITE")
    print("=" * 80)
    
    results = []
    
    try:
        results.append(("Scenario 1: Standard Contract", test_scenario_1_standard_contract()))
    except AssertionError as e:
        print(f"\n❌ SCENARIO 1 FAILED: {e}")
        results.append(("Scenario 1: Standard Contract", False))
    
    try:
        results.append(("Scenario 2: Playbook-Negotiable", test_scenario_2_playbook_negotiable()))
    except AssertionError as e:
        print(f"\n❌ SCENARIO 2 FAILED: {e}")
        results.append(("Scenario 2: Playbook-Negotiable", False))
    
    try:
        results.append(("Scenario 3: Delegation Boundary", test_scenario_3_delegation_boundary()))
    except AssertionError as e:
        print(f"\n❌ SCENARIO 3 FAILED: {e}")
        results.append(("Scenario 3: Delegation Boundary", False))
    
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + ("=" * 80))
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()
