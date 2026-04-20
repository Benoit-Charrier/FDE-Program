
## Deliverable 4 - First-Draft Validation Design

### Scenario 1 - Happy Path: Standard Contract

Input:

- 25-page vendor contract
- All seven target clause families are present
- Liability, DPA, termination, IP, SLA, governing law, and indemnity all match the playbook within tolerance

Expected result:

- Agent extracts all clause families with high confidence
- Contract is routed as standard
- No redlines are generated
- Review packet shows clause evidence and match rationale
- Contract enters a fast approval queue with no escalation

What this validates:

- The agent can remove repetitive first-pass review from the 70% standard population
- Match logic does not create unnecessary redlines

### Scenario 2 - Edge Case: Playbook-Negotiable Deviations

Input:

- 32-page vendor contract
- Liability cap and termination notice differ from company preferred terms
- Both deviations have approved fallback language in the playbook
- No must-escalate rule is triggered

Expected result:

- Agent extracts both deviations and classifies them as negotiable
- Agent generates draft redlines using only approved fallback language
- Contract is routed to the paralegal queue with clause-by-clause rationale
- Approval packet is prepared for later lawyer sign-off if a counteroffer is sent

What this validates:

- The agent can handle the 20% negotiable bucket without over-escalating
- Redline generation stays bounded by the playbook

### Scenario 3 - Failure Mode: Delegation Boundary Breach Attempt

Input:

- 18-page scanned PDF with weak OCR quality
- Liability clause appears uncapped
- Indemnity clause extraction confidence falls below threshold
- User attempts to push the generated redline package outbound without lawyer sign-off

Expected result:

- Agent routes the contract to senior-lawyer escalation
- Agent records low-confidence extraction as an explicit escalation reason
- Agent does not generate a releasable outbound package
- Release control blocks transmission because named lawyer sign-off is missing

What this validates:

- Low-confidence parsing cannot silently pass through the system
- The system respects the human delegation boundary, not just clause classification accuracy
