"""
Orchestrator: the main agent loop for a single contract.
Wires together all modules in the order defined by D4's activity catalog (T-01 through T-12).

Entry point: Orchestrator.process_contract(contract, document_path)
Returns: ClassificationRun with all outputs and audit trail.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from .aggregator import (
    aggregate_routing_classification,
    determine_decision_type,
    requires_lawyer_approval_for,
)
from .classifier import ClauseClassifier
from .clause_locator import locate_clauses
from .config import (
    ANOMALY_HIGH_PAGE_THRESHOLD,
    ANOMALY_LOW_PAGE_THRESHOLD,
    CONFIDENCE_THRESHOLD,
    MAX_IRONCLAD_RETRIES,
)
from .document_parser import parse_docx
from .escalation import evaluate_escalation_triggers, EscalationTrigger
from .hard_stops import (
    HardStopViolation,
    assert_complete_classification_before_routing,
    assert_dpa_flag_present,
    assert_ironclad_case_exists,
    assert_no_approved_transition,
)
from .hitl_queue import HITLQueue, build_hitl_payloads
from .ironclad_client import IroncladClient
from .models import (
    ClauseReview,
    Contract,
    ContractStatus,
    PlaybookMatchStatus,
    ReviewDecision,
    RoutingClassification,
    TaskUnitType,
)
from .playbook import PlaybookLoader
from .state_machine import transition


@dataclass
class ClassificationRun:
    """Complete output of a single contract classification run."""
    contract: Contract
    ironclad_case_id: str
    clause_reviews: list[ClauseReview]
    routing_classification: Optional[RoutingClassification]
    review_decision: Optional[ReviewDecision]
    escalation_triggers: list[EscalationTrigger]
    hitl_required: bool
    anomaly_flags: list[str]
    completed: bool
    error: Optional[str] = None


class Orchestrator:
    """
    Processes one inbound vendor contract through the full WS1 triage pipeline.
    Dependencies are injected to allow testing with mock implementations.
    """

    def __init__(
        self,
        classifier: ClauseClassifier,
        playbook: PlaybookLoader,
        ironclad: IroncladClient,
        hitl_queue: HITLQueue,
    ) -> None:
        self._classifier = classifier
        self._playbook = playbook
        self._ironclad = ironclad
        self._hitl = hitl_queue

    def process_contract(
        self,
        contract: Contract,
        document_path: Path,
    ) -> ClassificationRun:
        """
        Full WS1 pipeline: intake → parse → classify × 7 → aggregate → route.
        Returns a ClassificationRun; sets run.error on any recoverable failure.
        """
        anomaly_flags: list[str] = []
        run = ClassificationRun(
            contract=contract,
            ironclad_case_id="",
            clause_reviews=[],
            routing_classification=None,
            review_decision=None,
            escalation_triggers=[],
            hitl_required=False,
            anomaly_flags=anomaly_flags,
            completed=False,
        )

        # ------------------------------------------------------------------ #
        # T-02: Create Ironclad case record (hard stop if creation fails)     #
        # ------------------------------------------------------------------ #
        ironclad_case_id = self._create_ironclad_case(contract)
        if ironclad_case_id is None:
            run.error = (
                f"Ironclad case creation failed after {MAX_IRONCLAD_RETRIES} retries. "
                "Flag intake failure to Tom with contract filename and receipt timestamp."
            )
            return run

        run.ironclad_case_id = ironclad_case_id

        # Hard stop: classification must not proceed without a confirmed case record
        try:
            assert_ironclad_case_exists(contract.contract_id, ironclad_case_id)
        except HardStopViolation as exc:
            run.error = str(exc)
            return run

        # ------------------------------------------------------------------ #
        # T-03: Parse document                                                #
        # ------------------------------------------------------------------ #
        doc = parse_docx(document_path)

        if doc.parse_error:
            run.error = f"Document parse failed: {doc.parse_error}"
            return run

        # ------------------------------------------------------------------ #
        # §6.3: Document anomaly checks                                       #
        # ------------------------------------------------------------------ #
        page_count = doc.page_count_estimate
        contract = contract.model_copy(update={"document_page_count": page_count})

        if page_count < ANOMALY_LOW_PAGE_THRESHOLD:
            run.error = (
                f"Document is {page_count} pages — may be incomplete or a cover sheet. "
                "Manual review required before classification."
            )
            return run

        if page_count > ANOMALY_HIGH_PAGE_THRESHOLD:
            anomaly_flags.append(
                f"Document length {page_count} pages is outside the expected "
                f"15–40 page range — clause location accuracy may be lower. "
                "Tom spot-check recommended."
            )

        # ------------------------------------------------------------------ #
        # Transition to IN_REVIEW                                             #
        # ------------------------------------------------------------------ #
        contract = contract.model_copy(update={"agent_processing_start": datetime.utcnow()})
        contract = transition(contract, ContractStatus.IN_REVIEW)
        contract = contract.model_copy(update={"playbook_version_used": self._playbook.version})

        # ------------------------------------------------------------------ #
        # ET-6 pre-check: vendor case history                                 #
        # ------------------------------------------------------------------ #
        vendor_history = self._ironclad.get_vendor_case_history(contract.vendor_name)

        # ------------------------------------------------------------------ #
        # T-04/T-05: Locate all 7 clause types in the document               #
        # ------------------------------------------------------------------ #
        location_result = locate_clauses(doc)
        located_by_type = {lc.task_unit_type: lc for lc in location_result.located}
        missing_by_type = {t: conf for t, conf in location_result.missing}

        # ------------------------------------------------------------------ #
        # T-06–T-10: Classify each of the 7 clause types                     #
        # ------------------------------------------------------------------ #
        clause_reviews: list[ClauseReview] = []

        for clause_type in TaskUnitType:
            playbook_section = self._playbook.get_section(clause_type)
            located = located_by_type.get(clause_type)

            if located and located.extracted_text.strip():
                result = self._classifier.classify(
                    task_unit_type=clause_type,
                    extracted_text=located.extracted_text,
                    playbook_section=playbook_section,
                )
                review = ClauseReview(
                    contract_id=contract.contract_id,
                    task_unit_type=clause_type,
                    extracted_text=located.extracted_text,
                    playbook_match_status=result.playbook_match_status,
                    agent_confidence_score=result.agent_confidence_score,
                    agent_reasoning_summary=result.agent_reasoning_summary,
                    playbook_section_retrieved=self._playbook.section_citation(clause_type),
                )
            else:
                # Clause not located — determine absence confidence
                confidence_absent = missing_by_type.get(clause_type, 0.50)
                status = (
                    PlaybookMatchStatus.MISSING
                    if confidence_absent >= CONFIDENCE_THRESHOLD
                    else PlaybookMatchStatus.REQUIRES_SENIOR_REVIEW
                )
                headings = ", ".join(location_result.headings_searched[:10]) or "none found"
                reasoning = (
                    f"Clause not found. Searched {len(location_result.headings_searched)} "
                    f"section headings. Confidence absent: {confidence_absent:.2f}. "
                    f"Headings searched (first 10): {headings}."
                )
                review = ClauseReview(
                    contract_id=contract.contract_id,
                    task_unit_type=clause_type,
                    extracted_text=None,
                    playbook_match_status=status,
                    agent_confidence_score=confidence_absent,
                    agent_reasoning_summary=reasoning[:500],
                    playbook_section_retrieved=self._playbook.section_citation(clause_type),
                )

            clause_reviews.append(review)

        # ------------------------------------------------------------------ #
        # Hard stop: all 7 types must be assessed before routing              #
        # ------------------------------------------------------------------ #
        try:
            assert_complete_classification_before_routing(clause_reviews)
            assert_dpa_flag_present(clause_reviews)
        except HardStopViolation as exc:
            run.error = str(exc)
            return run

        run.clause_reviews = clause_reviews

        # ------------------------------------------------------------------ #
        # T-11: Evaluate escalation triggers (ET-1 through ET-6)             #
        # ------------------------------------------------------------------ #
        triggers = evaluate_escalation_triggers(
            clause_reviews,
            ironclad_vendor_history=vendor_history,
            vendor_name=contract.vendor_name,
        )
        run.escalation_triggers = triggers

        # ------------------------------------------------------------------ #
        # T-11: Aggregate routing classification                              #
        # ------------------------------------------------------------------ #
        routing = aggregate_routing_classification(clause_reviews)
        contract = contract.model_copy(update={"routing_classification": routing})

        # ------------------------------------------------------------------ #
        # Route: autonomous standard path or HITL                            #
        # ------------------------------------------------------------------ #
        hitl_required = bool(triggers)
        run.hitl_required = hitl_required

        if hitl_required:
            contract = transition(contract, ContractStatus.AWAITING_APPROVAL)
            payloads = build_hitl_payloads(contract.contract_id, ironclad_case_id, triggers)
            for payload in payloads:
                self._hitl.enqueue(payload)
        else:
            # Fully autonomous standard path: all 7 clauses COMPLIANT, all confidence ≥ 0.85
            contract = transition(contract, ContractStatus.REVIEWED_STANDARD)

        # ------------------------------------------------------------------ #
        # T-12: Write classification report to Ironclad                      #
        # ------------------------------------------------------------------ #
        self._ironclad.write_clause_reviews(contract.contract_id, clause_reviews)

        # Build ReviewDecision
        decision_type = determine_decision_type(routing)
        needs_approval = requires_lawyer_approval_for(decision_type)
        decision = ReviewDecision(
            contract_id=contract.contract_id,
            clause_review_ids=[r.clause_review_id for r in clause_reviews],
            decision_type=decision_type,
            decision_made_by=(
                "AGENT" if not hitl_required else "PENDING_TOM_REVIEW"
            ),
            requires_lawyer_approval=needs_approval,
            # approval_token is intentionally None — never set by the agent
        )
        self._ironclad.write_routing_decision(contract.contract_id, decision)

        # ------------------------------------------------------------------ #
        # Finalise                                                            #
        # ------------------------------------------------------------------ #
        contract = contract.model_copy(update={"agent_processing_end": datetime.utcnow()})
        run.contract = contract
        run.routing_classification = routing
        run.review_decision = decision
        run.anomaly_flags = anomaly_flags
        run.completed = True

        return run

    # ---------------------------------------------------------------------- #
    # Private helpers                                                         #
    # ---------------------------------------------------------------------- #

    def _create_ironclad_case(self, contract: Contract) -> Optional[str]:
        """
        Attempts Ironclad case creation with up to MAX_IRONCLAD_RETRIES retries.
        Returns the case ID on success, None on failure.
        """
        import time

        last_exc: Optional[Exception] = None
        for attempt in range(1, MAX_IRONCLAD_RETRIES + 1):
            try:
                return self._ironclad.create_case(contract)
            except Exception as exc:
                last_exc = exc
                if attempt < MAX_IRONCLAD_RETRIES:
                    time.sleep(1)  # brief wait before retry in tests

        return None
