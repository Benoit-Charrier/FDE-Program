---                                                                                                                                                      ## Outputs from Claude to the prompt:
 "Begin building the agent described in this document. First, tell me what you can build confidently without asking questions. Second, tell me what you need to clarify before building the rest. Third, build the parts you are confident about."    
  
  ---

  ## What I can build confidently (fully specified in D4 + CLAUDE.md):
                                                                                                                                                    
  1. Core Pydantic models — Contract, ClauseReview, ReviewDecision with all attributes, state machines, field constraints, and the approval_token guard                         
  2. State machine — all valid transitions with guards; APPROVED transition raises an error if the agent attempts it                                                            
  3. Document parser — .docx intake, text extraction, section/heading detection, page count
  4. Clause locator — heading pattern matching for all 7 clause types, absence confidence scoring
  5. Escalation trigger evaluator — ET-1 through ET-6 as pure logic
  6. Hard stops module — all 8 hard stops from D4 §8 as enforced runtime assertions
  7. Aggregator — ClauseReview → routing_classification with the precedence rule
  8. Orchestrator — the full contract-processing loop wiring everything together
  9. Mock Ironclad client and mock HITL queue — interfaces + in-memory implementations so the agent runs end-to-end without real credentials
  10. Tests for all pure-logic modules

  ---
  ## What I need to clarify before building the rest:

  1. LLM for the classifier — I'll use the Anthropic SDK with claude-sonnet-4-6 as the default. Confirm or specify another model.
  2. Playbook source — For the build, I'll create a mock playbook_v3_4.md in the project. Should it contain realistic-looking placeholder content, or do you have the actual
  playbook text to provide?
  3. RAG vs. in-context — D5 §5 recommends loading the full playbook in-context (~3,500 tokens). I'll use that approach. Let me know if you want a proper vector store
  (chromadb/FAISS) instead.
  4. Real Ironclad — Building against a mock only. To connect to a real Ironclad instance I'll need the tenant URL, API token, and the custom field schema (Gap G-4 from D5).
  5. Real email intake — Building a file-drop intake path (place a .docx in a watched folder). To connect to Outlook/Microsoft Graph I'll need app credentials.
