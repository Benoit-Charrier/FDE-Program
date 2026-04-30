# D5 — System/Data Inventory
**Scenario:** Helix Workforce Software — Vendor Contract Clause Review
**Agent:** Clause Classification Agent (CCA) — as designed in D4

---

## 1. Data and System Requirements (from Agent Design)

Requirements are derived directly from the CCA's activity catalog (D4, T-01 through T-12). Systems and data sources are not invented independently.

### Input data
*(What the agent reads to do its work)*

| Requirement | Derived from task | Granularity | Latency |
|-------------|------------------|-------------|---------|
| Inbound vendor contract documents (Word .docx) — full file | T-03 document parsing | Full document; clause-level extraction follows | On-demand at contract receipt (event trigger) |
| Vendor sender metadata — name, email address, receipt timestamp | T-01 intake monitoring | Field-level | On-demand at intake |
| Salesforce procurement request record — vendor name, opportunity ID, deal context | T-01 intake, T-02 case creation | Record-level | On-demand lookup at intake |
| Ironclad vendor case history — prior case records for same vendor, filterable by escalation status | T-11 routing proposal, ET-6 escalation trigger | Case-level summary | On-demand query at intake |

### Reference data
*(Policy documents and knowledge the agent consults during comparison)*

| Requirement | Derived from task | Granularity | Latency |
|-------------|------------------|-------------|---------|
| Helix negotiation playbook (SharePoint v3.4) — positions, thresholds, and deviation guidance for all 7 clause types | T-06 playbook retrieval, T-07 numeric comparison, T-08 qualitative comparison | Clause-type section chunks (~500 tokens each) | Batch-loaded into RAG index at deployment; refreshed on playbook version update |
| DPDI Act regulatory reference — Q1 updates on legitimate interests test and data subject access changes | T-09 DPA assessment, ET-2 escalation trigger | Summary-level (key provisions relevant to DPA clause comparison) | Batch-loaded; static until updated by Amelia [assumption: document must be prepared before deployment] |
| Clause heading taxonomy — known heading variants for each of the 7 clause types across common vendor document structures | T-04 clause location | Pattern library (heading strings + structural variants) | Batch-loaded; updated as new heading patterns are discovered |

### Output targets
*(Systems the agent writes to or queues it pushes results into)*

| Requirement | Derived from task | Granularity | Latency |
|-------------|------------------|-------------|---------|
| Ironclad case record — create case on intake; write per-clause classification fields, confidence scores, routing proposal, playbook version used | T-02 case creation, T-12 classification report write | Field-level write per clause type; structured JSON payload | Write on completion of T-02 (intake) and T-12 (classification) |
| HITL review queue — route flagged cases to Tom with structured payload: clause type flagged, vendor clause text, playbook position, confidence score, specific rationale | T-04, T-07, T-08, T-09, T-11 — all HITL-condition tasks | Case-level notification with attached structured flag payload | Real-time notification on flag condition |

### Approval/governance channels
*(How sign-off is captured and audited)*

| Requirement | Derived from task | Granularity | Latency |
|-------------|------------------|-------------|---------|
| Ironclad sign-off token field — agent reads the named-lawyer sign-off field to confirm presence before any downstream dispatch proceeds; agent never writes this field | D4 §5 Autonomy Matrix (GC hard rule boundary), D4 §8 Hard Stops | Field-level read; audit log of field writes (lawyer-written only) | On-demand check at routing stage; audit log is append-only |

---

## 2. System and Data Inventory Table

| System/Source | Data needed | Access type | Inferred availability | Gap/Risk | Priority |
|--------------|-------------|-------------|----------------------|----------|---------|
| **Outlook** (email) | Inbound contract attachments (Word .docx), vendor sender address, receipt timestamp | Event trigger + Read | API likely available — Microsoft Graph API. *Named in scenario_context.md — API specifics and integration maturity are assumptions beyond what is stated.* | Attachment extraction reliability; email format variation across vendors (inline vs. attached); shared legal inbox vs. individual address routing | Required |
| **Salesforce** | Procurement request records: vendor name, opportunity ID, deal context, vendor contact data | Read | API likely available — Salesforce REST API. *Named in scenario_context.md — API specifics and integration maturity are assumptions beyond what is stated.* | Field mapping between Salesforce opportunity and Ironclad legal case not confirmed; Salesforce records may not always accompany contract email | Required |
| **Microsoft Word (.docx) parsing** | Full contract document text; section boundaries; heading structure | Read (parsing library) | API unknown — Word is named in scenario_context.md as the redlining tool; a parsing library (e.g., python-docx) is not named. *Parsing library existence and format support are assumptions.* | Non-standard document structures; password-protected files; scanned PDFs attached as .docx wrappers; vendor-supplied tracked-changes documents with complex revision markup | Required |
| **SharePoint** (playbook) | Helix negotiation playbook v3.4: 7 clause type sections with compliance positions, numeric thresholds, deviation guidance | RAG | API likely available — SharePoint REST / Microsoft Graph API. *Named in scenario_context.md — format of playbook page (structured HTML vs. embedded Word document) and indexing feasibility are assumptions.* | Playbook format may not be directly RAG-indexable (embedded Word document vs. structured HTML); DPDI Act staleness is an active data quality risk — playbook must be updated before deployment | Required |
| **Ironclad** (CLM) | Case record CRUD: create case (T-02), write per-clause classification output (T-12), read vendor case history (T-11, ET-6), read sign-off token field | Read-Write | API likely available — Ironclad REST API confirmed in scenario. *Named in scenario_context.md — specific endpoints, field schema, per-clause classification field availability, and rate limits are assumptions.* | Per-clause classification fields may not exist in current Ironclad configuration — custom field setup required before deployment; rate limits on write operations under high-volume processing | Required |
| **HITL review queue / notification channel** | Route flagged cases to Tom: clause type, confidence score, vendor clause text, playbook position, escalation rationale | Write (action/trigger) | API unknown — mechanism not named in scenario. *Assumed to be Ironclad-native workflow notification or Outlook email — Not named in scenario; existence and API availability are assumptions.* | If via Ironclad: workflow template configuration required. If via Outlook: agent needs write access to Tom's inbox or a shared legal inbox. No confirmed channel. | Required |
| **DPDI Act regulatory reference** | Q1 legitimate interests test provisions and data subject access changes relevant to DPA clause comparison | RAG | Manual/document-only — *Not named in scenario; existence and machine-readable format are assumptions.* Must be prepared by Amelia before deployment. | No confirmed document exists; if Amelia has not produced a structured DPDI summary, the agent cannot reliably flag DPDI-affected DPA clauses (ET-2 depends on this) | Important |
| **Ironclad case history** (vendor lookup) | Prior case records for same vendor, flagged by escalation status — used for ET-6 historical escalation check | Read | API likely available — same Ironclad REST integration. *Named in scenario_context.md; queryability by vendor name as a filter parameter is assumption.* | Historical data completeness: contracts reviewed before Ironclad adoption may not be in the system; vendor name normalisation (spelling variants) may produce false negatives | Important |
| **Clause heading taxonomy** | Known heading variants for 7 clause types across common vendor document structures (used by T-04 for clause location) | RAG | Manual/document-only — *Not named in scenario; must be curated from playbook or historical contracts before deployment. Existence is assumption.* | No existing taxonomy confirmed; initial version must be manually curated; gap detection accuracy in T-04 directly depends on taxonomy completeness | Important |
| **Vendor delivery preference registry** | Per-vendor flag: email-only attachment delivery vs. SharePoint link (Artefact 2.2 pattern; used by C-7 downstream) | Read | Unknown — *Not named in scenario; currently held informally by Tom. Not named in scenario — structured registry does not currently exist. Existence is assumption.* | Informal knowledge held by Tom must be extracted and formalised; new vendors with non-standard delivery preferences will not be captured until encountered | Optional (required for C-7 dispatch; not blocking for CCA classification) |

---

## 3. Gap Analysis

> **Gap G-1: HITL review queue / notification channel**
> **What the agent cannot do without it:** Route flagged cases to Tom (T-04, T-07, T-08, T-09, T-11) — the entire HITL workflow is blocked. The agent can classify but cannot deliver flagged results to a human reviewer, rendering the confidence-gated design inoperable.
> **Severity:** Blocking — agent cannot launch without a confirmed HITL delivery channel.
> **Mitigation options:** (1) Use Ironclad-native workflow triggers to create a Tom review task on flag condition — preferred if Ironclad supports configurable workflow steps; (2) Use Outlook to send a structured notification email to a dedicated legal-inbox address — simpler to build, harder to audit; (3) Build a lightweight web interface for Tom's review queue as part of the agent platform — highest effort but most auditable.
> **Discovery action:** Ask Tom: "When the agent flags a contract clause for your review, how would you prefer to be notified — in Ironclad, by email, or in a separate tool? And what information do you need to see to make a routing decision efficiently?"

> **Gap G-2: DPDI Act regulatory reference document**
> **What the agent cannot do without it:** T-09 DPA clause assessment cannot reliably detect DPDI Act applicability beyond keyword matching. ET-2 DPDI escalation trigger fires only on the mandatory DPA flag rule, not on substantive detection of DPDI-affected provisions.
> **Severity:** Degrading — agent can launch and will flag all DPA clauses to Tom (mandatory flag), but the quality of the DPDI-specific guidance in the flag payload will be low without the reference document.
> **Mitigation options:** (1) Amelia produces a 1–2 page structured summary of the DPDI Act Q1 changes relevant to DPA clauses — this is the minimum viable reference; (2) Use the ICO's published DPDI Act guidance as a RAG source [assumption: publicly available]; (3) Deploy without the reference and accept that DPA flags are advisory ("DPDI update pending") until Amelia produces the document — explicit scope limitation.
> **Discovery action:** Ask Amelia: "Have you written any internal notes or briefings summarising the DPDI Act Q1 changes that affect DPA clause review? Even informal notes would work as a starting point for the agent's reference document."

> **Gap G-3: Clause heading taxonomy**
> **What the agent cannot do without it:** T-04 clause location relies on the model's general knowledge of legal document structures. Without a curated taxonomy of heading variants for Helix's specific vendor population, clause location confidence will be lower, increasing HITL rates and false-absence failures (FM-3).
> **Severity:** Degrading — agent can launch without it (LLM reasoning provides a baseline), but false-absence rate will be higher than target until the taxonomy is built from production data.
> **Mitigation options:** (1) Extract heading variants from 50 historical contracts in Ironclad to bootstrap the taxonomy before deployment [assumption: historical contracts are stored in Ironclad]; (2) Use the agent's own production outputs to self-curate the taxonomy over the first quarter — accept higher HITL rate initially; (3) Manually review the playbook and the scenario's 7 clause types to create a minimal baseline taxonomy before launch.
> **Discovery action:** Ask the team: "Do you have a sample of 20–30 historical vendor contracts we could analyse to identify common heading patterns for each of the 7 clause types? Even a small sample would significantly improve clause location accuracy."

> **Gap G-4: Ironclad per-clause classification field schema**
> **What the agent cannot do without it:** T-12 cannot write structured classification outputs to Ironclad — the agent's results have nowhere to land, blocking downstream C-7 package preparation and the entire sign-off pipeline.
> **Severity:** Blocking — agent cannot write outputs without confirmed Ironclad field schema. Custom fields must be configured before deployment.
> **Mitigation options:** (1) Configure custom fields in Ironclad for each of the 7 clause types (status, extracted text, playbook version, confidence score, deviation magnitude) — standard Ironclad customisation; (2) Write classification output to a structured JSON file in SharePoint and have C-7 read from there — workaround, creates a secondary data store; (3) Use Ironclad's existing notes/comments field as a temporary container — not machine-readable, blocks automation downstream.
> **Discovery action:** Ask the Ironclad admin: "Can we add custom metadata fields to contract records for per-clause classification outputs? We need fields for clause type, match status, confidence score, deviation magnitude, and playbook version — approximately 35 fields total across 7 clause types."

> **Gap G-5: Salesforce–Ironclad case linkage**
> **What the agent cannot do without it:** T-01 intake monitoring cannot reliably associate an inbound contract email with its Salesforce opportunity — the case record in Ironclad may lack the procurement context (vendor name normalisation, deal stage, contact details) needed for accurate routing and delivery preference lookup.
> **Severity:** Degrading — agent can process contracts without Salesforce linkage (contract content is self-contained), but routing context and vendor history matching will be less reliable.
> **Mitigation options:** (1) Use vendor email domain as the matching key between Outlook sender and Salesforce account — simple but prone to false matches for large vendors with multiple subsidiaries; (2) Require procurement to include a Salesforce opportunity ID in the email subject or body — process change, not a technical integration; (3) Build a fuzzy-match lookup from vendor name to Salesforce account — additional engineering effort.
> **Discovery action:** Ask procurement: "When a vendor sends a contract, is there a consistent way to identify which Salesforce deal it belongs to — an opportunity ID in the subject line, a specific inbox alias, or something else?"

---

## 4. Risk Register

| System | Risk type | Risk description | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation |
|--------|-----------|-----------------|-------------------|----------------|------------|
| SharePoint (playbook) | Data quality | Playbook v3.4 is 9 months stale — DPDI Act Q1 updates not incorporated. Agent deployed against stale playbook will misclassify DPDI-affected DPA clauses as compliant. | H — staleness is a confirmed scenario fact | H — compliance failure at scale across all DPA clauses; non-recoverable post-signature | Deployment gate: do not go live until Amelia updates playbook; version number recorded in agent configuration; CCA reads playbook version on every run and logs it to Ironclad |
| Ironclad | Governance/approval integrity | The sign-off token field in the Ironclad case record is the technical enforcement point for the GC's hard rule. If the field is writeable by non-lawyer roles (including the agent), the rule can be bypassed — accidentally or intentionally. This is the single highest-consequence risk in the system design. | M — depends on Ironclad role-based access configuration; misconfiguration is plausible | H — counteroffer dispatched without named-lawyer sign-off; GC hard rule violated; no recovery path | Ironclad field-level write permission must be restricted to named-lawyer user roles only; agent configured with read-only access to sign-off field; field write events logged to audit trail; quarterly access review |
| Microsoft Word parsing | API availability | No dedicated Word parsing API is named in the scenario. Parsing library (e.g., python-docx) handles standard .docx well but fails on malformed documents, embedded objects, password protection, and complex Track Changes markup common in vendor contracts. | M — vendor contract documents vary significantly in structure | H — document parsing failure blocks the entire classification pipeline for affected contracts | Pre-process all inbound documents through a document normalisation step; log parsing failures to Tom's queue immediately; maintain a fallback path for Tom to manually upload parsed text |
| SharePoint (playbook) | API availability | SharePoint REST API access depends on Microsoft 365 tenant permissions and conditional access policies; these are not confirmed in the scenario. | M — Microsoft 365 access controls vary significantly across organisations | H — RAG pipeline cannot index playbook; entire agent is blocked without its primary reference data | Validate SharePoint API access and service account permissions in discovery; confirm Microsoft Graph API is available for the tenant |
| HITL notification channel | Audit trail | If HITL routing is implemented via Outlook email, Tom's review decisions are not automatically logged to Ironclad — creating an audit gap between the agent's flag and Tom's routing approval. | M — depends on implementation choice | M — routing decisions are not auditable; compliance review cannot verify that flagged cases were reviewed before proceeding | Prefer Ironclad-native workflow for HITL routing; if Outlook is used, require Tom to log his approval decision in Ironclad before the case proceeds |
| Salesforce | API availability | Salesforce REST API requires OAuth 2.0 authentication; connected app configuration and API access permissions must be established. Rate limits on Salesforce REST API are documented but need to be assessed against 23 contracts/week intake volume. | L — Salesforce API is well-documented and widely integrated | M — without Salesforce linkage, procurement context is missing from Ironclad case records; vendor history matching degrades | Validate Salesforce connected app access in discovery; rate limits are unlikely to be a constraint at current volume (23/week) |
| DPDI Act reference | Legal/compliance | If the DPDI Act reference document is not available or is itself incomplete, the agent's DPA clause assessments are made against an outdated knowledge base — creating a compliance exposure on every DPA clause processed. | H — reference document does not yet exist per Artefact 2.3 | H — same compliance failure risk as playbook staleness; affects all DPA clauses | Block DPA clause autonomous processing until both playbook and DPDI reference are updated; maintain mandatory HITL flag (ET-2) as a safety net regardless |
| Ironclad (case history) | Data quality | Vendor escalation history lookup (ET-6) depends on historical contracts being in Ironclad with consistent vendor name normalisation. Contracts processed before Ironclad adoption, or entered with inconsistent vendor name spelling, will produce false-negative history lookups. | M — legacy data completeness is unknown | L — missed escalation history flag is a degraded alert, not a blocking failure; the current contract is still fully classified | Log all vendor name lookup misses; build a vendor name normalisation table from the first quarter of production data; treat ET-6 as a best-effort advisory in the first deployment phase |

---

## 5. Context Engineering Design

### Memory architecture

| Memory type | Content | Storage mechanism | Lifecycle |
|-------------|---------|------------------|-----------|
| **In-context (short-term)** | Current contract text (full parsed document), active clause extraction outputs for all 7 types, playbook sections retrieved for current contract, per-clause confidence scores, escalation flags triggered, Ironclad case ID | Prompt window (~40K–100K tokens depending on contract length and model) | Per contract — cleared after T-12 write completes |
| **Semantic (long-term, retrieval)** | SharePoint playbook v3.4 indexed by clause type; DPDI Act regulatory reference; clause heading taxonomy; historical clause precedents (if available from Ironclad) | Vector database [assumption: hosted vector store such as Pinecone, pgvector, or equivalent] | Updated on playbook version change; taxonomy extended as new heading patterns are discovered |
| **Procedural (static)** | Agent instructions, 7 clause type taxonomy, confidence threshold definitions (0.85 gate), escalation trigger conditions (ET-1 through ET-6), DPDI mandatory flag rule, hard stop rules from D4 §8, Ironclad field schema | System prompt (version-controlled in source repository) | Updated on: playbook version change, threshold calibration, scope change; never modified at runtime |

### Retrieval strategy

**What triggers a retrieval call:**
- T-04 (clause location): heading pattern search triggered once per contract at document parsing; retrieves clause heading taxonomy to guide section boundary detection
- T-06 (playbook retrieval): triggered once per clause type per contract (7 calls per contract); retrieves the playbook section for the specific clause type being compared
- T-09 (DPA assessment): triggers an additional retrieval of the DPDI Act reference section on legitimate interests and data subject access whenever a DPA clause is extracted
- ET-6 (vendor history check): triggered at T-01/T-02 intake; Ironclad API lookup by vendor name, not a RAG call

**Retrieval target:**
- Playbook retrieval: top-2 chunks per clause type (operative position statement + deviation threshold table), capped at ~1,000 tokens per clause type — the playbook is small enough that the entire 7-section playbook (~3,500 tokens) can be included in context for the full contract run rather than retrieved clause-by-clause, reducing retrieval latency
- DPDI reference: single full section (~500 tokens) loaded into context for any contract containing a DPA clause
- Heading taxonomy: top-5 heading variants per clause type, retrieved at document parsing time

**How retrieval quality is evaluated:**
- *Clause-type precision:* For each playbook retrieval call, verify that the retrieved chunk contains the operative numeric threshold for that clause type (e.g., the liability cap floor of £250,000 for liability cap clause retrieval). If the threshold is absent from the retrieved chunk, the retrieval has failed and the comparison should be flagged to Tom rather than proceeding autonomously.
- *False positive clause matches:* Monitor the rate at which Tom overrides a "clause not found" finding with "clause present" — this is the primary signal that the heading taxonomy is incomplete and retrieval is missing clauses embedded under atypical headings.
- *Confidence calibration:* Track the correlation between the agent's confidence scores and Tom's override decisions. If 90% of high-confidence classifications are confirmed, calibration is good; if override rate at high confidence exceeds 10%, the confidence scoring requires recalibration.
- *Playbook version consistency:* Every classification output written to Ironclad must log the playbook version used. Post-deployment audit can verify that no classification was made against a stale playbook version.

**How retrieval costs are managed:**
- The full playbook (~3,500 tokens across 7 sections) is small enough to include in the system prompt or as a single cached context block — avoiding per-clause retrieval calls and reducing latency and cost per contract
- Prompt caching: the system prompt (playbook + agent instructions + clause taxonomy) is a stable context block; models that support prompt caching will amortise the input token cost across all contracts processed in the same session
- Re-indexing: SharePoint RAG index is rebuilt only on playbook version update, not on every agent run; index build is a background batch job triggered by a SharePoint webhook on document save

### Key context engineering risks

1. **Playbook language ambiguity:** The playbook states policy positions (e.g., "liability cap must be at least 12 months or £250,000") but may use natural-language qualifications ("typically", "in most cases") that create ambiguous compliance boundaries. An agent reading an ambiguous playbook position will produce low-confidence classifications inconsistently — not because the model is wrong, but because the source material is underspecified. Resolution: structured playbook editing is a pre-deployment prerequisite.

2. **Context window overflow on long contracts:** The scenario states contracts are 15–40 pages. At 40 pages, a dense legal document may approach 20,000–25,000 tokens. Combined with the playbook context (~3,500 tokens), system prompt (~2,000 tokens), and classification output (~2,000 tokens), a single contract run may consume 30,000+ tokens in context. This is within modern model limits, but leaves limited margin. If the full document must be in context for cross-clause consistency checking (T-05), a chunked extraction approach may be required for very long contracts, introducing additional retrieval complexity.

3. **Stale playbook version in cached context:** If the system prompt includes the full playbook as a cached context block and the playbook is updated mid-session (e.g., Amelia commits DPDI changes during a processing run), contracts processed before the cache is invalidated will be compared against the old version. Resolution: the playbook version number must be checked against the Ironclad case record at the start of each contract run; if the version has changed, the cache must be invalidated before proceeding.

---

## 6. Compounding Opportunities

| Integration built | Future agent that could reuse it | Reuse mechanism |
|------------------|----------------------------------|-----------------|
| SharePoint RAG pipeline (playbook chunking, indexing, retrieval) | WS2 Redline Drafting Agent | Same playbook index; redline agent retrieves clause-type policy position to generate candidate replacement language — same retrieval call, different downstream use |
| Ironclad REST integration (case create, field read/write, case history query) | C-7 Counteroffer Package Preparation Agent | C-7 reads the per-clause classification fields written by the CCA to assemble the sign-off package; same Ironclad client, different field operations |
| Outlook email intake event listener | C-7 Counteroffer Package Preparation Agent (outbound dispatch) | Same Microsoft Graph API connection used for inbound monitoring; C-7 uses it for outbound email delivery to vendor procurement |
| Word document parsing library | WS2 Redline Drafting Agent | Same parser reads the contract document; redline agent additionally writes Track Changes markup back to the same .docx — extends the integration from read to read-write |
| Vendor delivery preference registry (once formalised) | C-7 Counteroffer Package Preparation Agent | C-7 uses the same registry to determine whether to send the signed-off counteroffer as a SharePoint link or a Word attachment (Artefact 2.2 pattern) |
| DPDI Act regulatory reference RAG source | WS2 Redline Drafting Agent | Same reference document used to generate DPDI-compliant DPA redline language once playbook is updated and WS2 agent scope includes DPA clauses |

---

## Summary — main 3 points

1. **The Ironclad integration is the load-bearing dependency — both for case record creation (T-02) and for writing the classification output (T-12), and the sign-off token field is where the GC's hard rule is technically enforced.** Custom per-clause classification fields must be configured in Ironclad before deployment, and the sign-off field must be restricted to named-lawyer write access only. These are both pre-deployment configuration requirements, not engineering gaps — but they must be confirmed in discovery before build begins.

2. **Two items are deployment gates, not optional pre-conditions: the SharePoint playbook DPDI update and the DPDI Act regulatory reference document.** Both must be in place before the agent processes any DPA clause without mandatory HITL. The playbook staleness is a confirmed fact from Artefact 2.3. An agent deployed without these two items will produce compliance failures at scale on every DPA clause — silently, because the playbook will say "compliant" and the agent will agree.

3. **The SharePoint RAG pipeline and the Ironclad REST integration together form a reusable platform that makes every subsequent agent in this legal team cheaper to build.** The WS2 Redline Drafting Agent, the C-7 Package Preparation Agent, and any future regulatory monitoring agent all reuse the same playbook index, the same Ironclad client, and the same Outlook API connection. The CCA is the foundation agent — its integrations are the shared infrastructure that the rest of the legal automation programme inherits.
