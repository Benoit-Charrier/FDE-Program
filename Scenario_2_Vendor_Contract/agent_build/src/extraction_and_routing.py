"""
Extraction and routing engine: uses Claude to extract clauses, then applies deterministic routing logic.
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import anthropic
import yaml

from src.data_contracts import (
    ExtractedClause, ClauseStatus, RouteDecision, ContractReviewResult
)


def load_playbook(playbook_path: str) -> Dict:
    """Load playbook YAML/JSON configuration."""
    with open(playbook_path, 'r') as f:
        if playbook_path.endswith('.yaml') or playbook_path.endswith('.yml'):
            return yaml.safe_load(f)
        else:
            return json.load(f)


def extract_clauses_with_claude(
    contract_text: str,
    clause_families: List[str],
    api_key: str
) -> List[Dict]:
    """
    Use Claude to extract clause families from contract text.
    Returns list of raw extraction results.
    """
    client = anthropic.Anthropic(api_key=api_key)
    
    families_str = ", ".join(clause_families)
    prompt = f"""You are a legal document analyst. Extract the following clause families from the contract text:

Clause families to extract: {families_str}

For each clause family, provide:
1. Whether it exists in the contract (yes/no/unclear)
2. The exact text of the clause (if found)
3. A confidence score from 0.0 to 1.0 for your extraction
4. Page markers if visible (e.g., [PAGE 3])

Format your response as JSON with this structure:
{{
  "clauses": [
    {{
      "family": "liability",
      "found": true,
      "text": "...",
      "confidence": 0.95,
      "page_markers": "[PAGE 2]"
    }}
  ]
}}

CONTRACT TEXT:
{contract_text[:12000]}
"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    try:
        result = json.loads(response.content[0].text)
        return result.get("clauses", [])
    except json.JSONDecodeError:
        # Fallback: return empty list if Claude's response isn't JSON
        return []


def extract_page_number(page_markers: str) -> int:
    """Parse page number from page markers like '[PAGE 3]'."""
    match = re.search(r'\[PAGE (\d+)\]', page_markers or '')
    return int(match.group(1)) if match else 1


def classify_clause(
    clause_data: Dict,
    playbook: Dict,
    confidence_threshold: float
) -> Tuple[ClauseStatus, Optional[str], Optional[str]]:
    """
    Classify a clause as MATCH, NEGOTIABLE_DEVIATION, or ESCALATE.
    Returns (status, variance_reason, escalation_reason).
    """
    family = clause_data.get("family", "")
    found = clause_data.get("found", False)
    confidence = clause_data.get("confidence", 0.0)
    text = clause_data.get("text", "").lower()
    
    family_config = playbook.get("clause_families", {}).get(family, {})
    
    # Rule 1: If confidence is too low, escalate
    if confidence < confidence_threshold:
        return (
            ClauseStatus.ESCALATE,
            None,
            f"Extraction confidence {confidence:.2f} below threshold {confidence_threshold}"
        )
    
    # Rule 2: If clause is mandatory and not found, escalate
    if family_config.get("mandatory", False) and not found:
        return (
            ClauseStatus.ESCALATE,
            None,
            f"Mandatory clause family '{family}' not found"
        )
    
    # Rule 3: Check for must-escalate keywords
    must_escalate_keywords = family_config.get("must_escalate_keywords", [])
    for keyword in must_escalate_keywords:
        if keyword.lower() in text:
            return (
                ClauseStatus.ESCALATE,
                None,
                f"Clause contains must-escalate keyword: '{keyword}'"
            )
    
    # Rule 4: If found and passes checks, check if it matches approved patterns
    if found:
        approved_patterns = family_config.get("approved_patterns", [])
        pattern_matches = 0
        for pattern_obj in approved_patterns:
            pattern = pattern_obj.get("pattern", "")
            if re.search(pattern, text, re.IGNORECASE):
                pattern_matches += 1
        
        if pattern_matches > 0:
            return (ClauseStatus.MATCH, None, None)
        else:
            # Deviation found, but might be negotiable
            return (
                ClauseStatus.NEGOTIABLE_DEVIATION,
                "Clause language does not match approved patterns; may require negotiation",
                None
            )
    
    return (ClauseStatus.MATCH, None, None)


def route_contract(
    extracted_clauses: List[ExtractedClause],
    playbook: Dict
) -> Tuple[RouteDecision, float, List[str]]:
    """
    Determine contract routing based on extracted clauses and playbook rules.
    Returns (route_decision, confidence, escalation_reasons).
    """
    escalation_reasons = []
    clause_statuses = {}
    
    # Collect escalation reasons
    for clause in extracted_clauses:
        clause_statuses[clause.family] = clause.status
        if clause.status == ClauseStatus.ESCALATE:
            if clause.escalation_reason:
                escalation_reasons.append(clause.escalation_reason)
    
    # Rule 1: If any clause escalates, route to senior lawyer
    if any(status == ClauseStatus.ESCALATE for status in clause_statuses.values()):
        return (
            RouteDecision.SENIOR_LAWYER_ESCALATION,
            0.5,
            escalation_reasons
        )
    
    # Rule 2: If all clauses match, route as standard
    if all(status == ClauseStatus.MATCH for status in clause_statuses.values()):
        return (
            RouteDecision.STANDARD,
            0.95,
            []
        )
    
    # Rule 3: If deviations exist but no escalations, route as playbook_negotiable
    if any(status == ClauseStatus.NEGOTIABLE_DEVIATION for status in clause_statuses.values()):
        return (
            RouteDecision.PLAYBOOK_NEGOTIABLE,
            0.85,
            []
        )
    
    # Default to standard if unclear
    return (
        RouteDecision.STANDARD,
        0.75,
        []
    )


def analyze_contract(
    contract_id: str,
    filename: str,
    file_size_bytes: int,
    contract_text: str,
    page_count: int,
    playbook_path: str,
    api_key: str
) -> ContractReviewResult:
    """
    Main analysis function: extract clauses, classify, route, and return result.
    """
    playbook = load_playbook(playbook_path)
    confidence_threshold = playbook.get("extraction_confidence_threshold", 0.75)
    
    # Extract clause families
    clause_families = list(playbook.get("clause_families", {}).keys())
    raw_extractions = extract_clauses_with_claude(
        contract_text,
        clause_families,
        api_key
    )
    
    # Classify each clause
    extracted_clauses = []
    variance_reasons = []
    
    for raw in raw_extractions:
        status, variance_reason, escalation_reason = classify_clause(
            raw, playbook, confidence_threshold
        )
        
        page_num = extract_page_number(raw.get("page_markers", ""))
        clause = ExtractedClause(
            family=raw.get("family", ""),
            source_text=raw.get("text", ""),
            page_number=page_num,
            confidence_score=raw.get("confidence", 0.0),
            status=status,
            variance_reason=variance_reason,
            escalation_reason=escalation_reason
        )
        extracted_clauses.append(clause)
        
        if variance_reason:
            variance_reasons.append(f"{clause.family}: {variance_reason}")
    
    # Route contract
    route_decision, routing_confidence, escalation_reasons = route_contract(
        extracted_clauses,
        playbook
    )
    
    variance_summary = "; ".join(variance_reasons) if variance_reasons else "All clauses match playbook."
    
    # Build result
    result = ContractReviewResult(
        contract_id=contract_id,
        filename=filename,
        file_size_bytes=file_size_bytes,
        page_count=page_count,
        ingestion_timestamp=datetime.utcnow(),
        route_decision=route_decision,
        routing_confidence=routing_confidence,
        extracted_clauses=extracted_clauses,
        variance_summary=variance_summary,
        redline_proposals=[],  # Filled by redline generator
        escalation_reasons=escalation_reasons,
        analysis_timestamp=datetime.utcnow()
    )
    
    return result
