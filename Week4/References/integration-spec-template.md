# Integration Spec Template: AI-Native System Integration Specifications

## Overview

This template is for writing integration specifications that AI coding agents can build from without guessing. Every section has guidance explaining what makes it agent-buildable vs ambiguous.

Use this template whenever an agent needs to interact with an external system: APIs, databases, message queues, payment gateways, credential systems, data warehouses, etc.

The cardinal rule: **if the AI coding agent has to guess at any of this, the integration will fail.**

---

## Template Structure with Filled Example

The example below is a complete integration specification for a healthcare staffing agent integrating with a credentialing database. Use it as a reference for what "complete" looks like.

---

# Integration Spec: Healthcare Credentialing Database

## 1. Integration Purpose

**What:** This integration allows the staffing assignment system to verify nurse licenses in real-time before creating assignments. The credentialing database is the system of record for license status.

**Why:** Assignments cannot proceed without verified credentials. Licenses expire, are revoked, or suspended. The credentialing system is authoritative; our local cache is secondary.

**Responsibility:** The agent is responsible for:
- Querying the credentialing API before creating assignments
- Handling timeouts and failures gracefully
- Maintaining a local credential cache with TTL-based invalidation
- Logging all verification attempts and results

**What the agent is NOT responsible for:**
- Updating license data in the credentialing system (read-only)
- Deciding whether a license is "acceptable" (that's policy; this spec covers verification only)
- Storing actual license documents or images

---

## 2. System Description

**System Name:** HealthCorp Credentialing Database (HCDB)

**Provider:** HealthCorp Inc. (external vendor)

**Base URL:** https://api.healthcorp.io/v2

**Documentation:** Internal wiki: https://wiki.company.com/integrations/healthcorp-cdb

**Supported Operations:**
- Query single license status (by license number + license type)
- Batch query (up to 100 licenses in one request)
- Lookup nurse record (by NPI or name + DOB)
- Webhook notifications (optional; when license status changes)

**System Uptime SLA:** 99.5% (as stated in vendor SLA)

**Backup Plan:** If primary endpoint is down > 5 minutes, fail over to read-only backup endpoint (list below)

---

## 3. Authentication & Authorization

**Method:** OAuth 2.0 Bearer Token

**Token Source:** 
- Stored in: AWS Secrets Manager, key name `healthcorp/api-token`
- Managed by: DevOps team; rotated quarterly
- Scope: read:license, read:nurse

**How to Use:**
```
Authorization: Bearer {token}
```

**Where to Put It:**
- HTTP Header: `Authorization`
- Never in query parameters, never in request body
- Never log the token; sanitize logs before sharing

**Token Expiration Handling:**
- Tokens are long-lived (validity = 1 year)
- Before using token, check expiry: if expiry < 7 days away, request new token from ops
- On 401 Unauthorized response, the token may have been rotated; fetch fresh token from Secrets Manager

**Fallback if No Token Available:**
- Fail the verification with error code CREDENTIAL_VERIFICATION_UNAVAILABLE
- Log the token-missing error to ops
- Do not proceed with assignment creation
- Return error to user: "Credential verification system is temporarily unavailable. Please try again in a few minutes."

---

## 4. Endpoint Contracts

**Guidance Note:** Every request and response must be specified exactly. If the agent has to guess at JSON structure, the integration will fail. Include required/optional fields, types, constraints, and enums.

### Endpoint A: Verify Single License

**Operation:** Query license status for a single nurse license

**HTTP Method:** POST

**URL:** `https://api.healthcorp.io/v2/licenses/verify`

**Request Format:**

```json
{
  "license_number": "string, required, must match regex ^[A-Z]{2}-[0-9]{6}$",
  "license_type": "enum, required, one of [RN, LPN, CNA, RT]",
  "expiration_date": "ISO 8601 date, required, format: YYYY-MM-DD",
  "first_name": "string, optional, max 100 chars, used for additional validation",
  "last_name": "string, optional, max 100 chars, used for additional validation"
}
```

**Example Request:**
```json
{
  "license_number": "CA-456789",
  "license_type": "RN",
  "expiration_date": "2025-06-30",
  "first_name": "Jane",
  "last_name": "Nurse"
}
```

**Response Format (HTTP 200 Success):**

```json
{
  "license_number": "string, same as request",
  "license_type": "enum [RN, LPN, CNA, RT]",
  "status": "enum, one of [VALID, EXPIRED, REVOKED, SUSPENDED, PENDING_RENEWAL, UNKNOWN]",
  "verified_at": "ISO 8601 timestamp with timezone, e.g., 2026-04-10T14:23:45Z",
  "expiration_date": "ISO 8601 date",
  "issued_date": "ISO 8601 date, optional",
  "issuing_state": "string, two-letter US state code or country code",
  "record_id": "string, unique identifier in credentialing database, used for audit trail",
  "notes": "string, optional, max 500 chars, explanatory notes (e.g., 'License renewed through 2028')",
  "last_renewal_date": "ISO 8601 date, optional, when was license last renewed"
}
```

**Example Response:**
```json
{
  "license_number": "CA-456789",
  "license_type": "RN",
  "status": "VALID",
  "verified_at": "2026-04-10T14:23:45Z",
  "expiration_date": "2025-06-30",
  "issued_date": "2019-06-15",
  "issuing_state": "CA",
  "record_id": "healthcorp-89012345",
  "notes": "License renewed through 2028. CPR certification current.",
  "last_renewal_date": "2023-06-15"
}
```

**Error Response Format (HTTP 4xx/5xx):**

```json
{
  "error": {
    "code": "string, error code (see Error Codes section)",
    "message": "string, human-readable error description",
    "details": {
      "field": "string, which field caused the error (if applicable)",
      "reason": "string, specific reason for error"
    },
    "request_id": "string, unique ID for this request (for support/debugging)"
  }
}
```

**Example Error Response:**
```json
{
  "error": {
    "code": "LICENSE_NOT_FOUND",
    "message": "License number CA-456789 not found in database",
    "details": {
      "field": "license_number",
      "reason": "No matching record for this license_number and license_type combination"
    },
    "request_id": "req-2026-04-10-abc123xyz"
  }
}
```

**HTTP Status Codes:**
- **200 OK:** Verification succeeded; status is in response
- **400 Bad Request:** Invalid request format (missing field, wrong type, invalid regex match)
- **401 Unauthorized:** Token missing, expired, or invalid
- **403 Forbidden:** Token valid, but does not have required scope (read:license)
- **404 Not Found:** License number does not exist in credentialing database
- **429 Too Many Requests:** Rate limit exceeded (see Rate Limits section)
- **500 Internal Server Error:** Server error; safe to retry
- **503 Service Unavailable:** System maintenance; safe to retry

---

### Endpoint B: Batch Verify Licenses

**Operation:** Verify up to 100 licenses in a single request (more efficient than looping)

**HTTP Method:** POST

**URL:** `https://api.healthcorp.io/v2/licenses/batch-verify`

**Request Format:**

```json
{
  "licenses": [
    {
      "license_number": "string, required",
      "license_type": "enum, required",
      "expiration_date": "ISO 8601 date, required"
    }
  ],
  "max_array_length": 100
}
```

**Example Request:**
```json
{
  "licenses": [
    {
      "license_number": "CA-456789",
      "license_type": "RN",
      "expiration_date": "2025-06-30"
    },
    {
      "license_number": "NY-123456",
      "license_type": "LPN",
      "expiration_date": "2024-12-15"
    }
  ]
}
```

**Response Format (HTTP 200):**

```json
{
  "results": [
    {
      "license_number": "string, same as request",
      "status": "enum [VALID, EXPIRED, REVOKED, SUSPENDED, PENDING_RENEWAL, UNKNOWN]",
      "verified_at": "ISO 8601 timestamp",
      "record_id": "string, credentialing database ID"
    }
  ],
  "failed_lookups": [
    {
      "license_number": "string",
      "error_code": "LICENSE_NOT_FOUND",
      "reason": "string"
    }
  ]
}
```

---

## 5. Error Handling & Retry Logic

**Guidance Note:** Every HTTP status code must have a defined handling strategy. Ambiguity here causes integration failures.

### Retry Strategy by Status Code

| Status Code | Cause | Retry? | Max Attempts | Backoff | Escalation |
|---|---|---|---|---|---|
| 200 | Success | No | N/A | N/A | N/A |
| 400 | Invalid request | No | N/A | N/A | Log error; notify developer; do not retry |
| 401 | Invalid token | No | N/A | N/A | Fetch new token from Secrets Manager; retry once |
| 403 | No permission | No | N/A | N/A | Log error; alert ops; do not retry |
| 404 | License not found | No | N/A | N/A | Return status UNKNOWN; log in audit trail |
| 429 | Rate limit | Yes | 3 | Exponential (2s, 4s, 8s) + Retry-After header | If all retries fail, queue for async retry; escalate if queue backs up |
| 500 | Server error | Yes | 3 | Exponential (2s, 4s, 8s) | After 3 retries, fail gracefully; escalate to human review |
| 503 | Service unavailable | Yes | 3 | Exponential (2s, 4s, 8s) | Same as 500 |
| Timeout | No response in 10s | Yes | 2 | Fixed (5s between attempts) | After 2 retries, escalate to human review |

### Retry Logic Pseudocode

```
function verifyLicense(licenseNumber, licenseType, expirationDate):
  maxAttempts = 3
  attempts = 0
  
  while attempts < maxAttempts:
    try:
      response = POST /licenses/verify with timeout = 10s
      
      if response.status == 200:
        return response
      
      if response.status == 400:
        log ERROR: "Invalid request: {response.body.error.message}"
        return ERROR_INVALID_REQUEST
      
      if response.status == 401:
        fetchNewToken()
        retry once with new token
        if still fails, return ERROR_CREDENTIAL_UNAVAILABLE
      
      if response.status == 404:
        return {status: UNKNOWN, reason: "License not found in system"}
      
      if response.status in [500, 503]:
        attempts += 1
        if attempts < maxAttempts:
          wait exponential_backoff(attempts)
          continue
        else:
          escalate to human review with request_id
          return ERROR_VERIFICATION_TIMEOUT
      
      if response.status == 429:
        retryAfter = parse response header Retry-After (seconds)
        attempts += 1
        wait retryAfter seconds
        continue
      
    catch TimeoutException:
      attempts += 1
      if attempts < maxAttempts:
        wait 5 seconds
        continue
      else:
        escalate to human review
        return ERROR_VERIFICATION_TIMEOUT
  
  return ERROR_MAX_RETRIES_EXCEEDED
```

### Error Code Reference

| Error Code | HTTP Status | Meaning | Agent Action |
|---|---|---|---|
| LICENSE_NOT_FOUND | 404 | License number does not exist | Set credential status to UNKNOWN; log in assignment record; do not auto-reject |
| INVALID_REQUEST | 400 | Bad request format | Log error; alert developer; do not retry |
| INVALID_TOKEN | 401 | Token expired or invalid | Fetch new token; retry request |
| PERMISSION_DENIED | 403 | Token lacks required scope | Log error; alert ops; do not retry |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests | Retry with backoff; respect Retry-After header |
| VERIFICATION_TIMEOUT | 408/timeout | Request timed out | Retry up to 2 times; then escalate |
| SERVICE_ERROR | 500 | Server error | Retry with backoff; escalate if all retries fail |
| SERVICE_UNAVAILABLE | 503 | Maintenance or overload | Retry with backoff; escalate if all retries fail |
| CREDENTIAL_VERIFICATION_UNAVAILABLE | N/A | Cannot reach credentialing system | Fail assignment creation; notify user to try later |

---

## 6. Rate Limits & Throttling

**Guidance Note:** Ambiguous rate limits cause integration failures when the agent exceeds limits. Be specific.

**Rate Limit Policy:**
- **Requests per minute:** 100 per API key
- **Requests per day:** 50,000 per API key
- **Concurrent requests:** Maximum 10 simultaneous requests

**Burst Allowance:**
- First 5 requests in a window are burst-allowed (no rate limit)
- Subsequent requests are subject to rate limit

**Checking Rate Limit Status:**
- Response headers include:
  - `X-RateLimit-Limit`: total limit (e.g., 100)
  - `X-RateLimit-Remaining`: requests remaining (e.g., 45)
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

**Handling Rate Limit:**
- When 429 received, check `Retry-After` header
- Retry-After value is in seconds; wait that amount before retrying
- If Retry-After is absent, use exponential backoff: 2s, 4s, 8s
- Monitor `X-RateLimit-Remaining`; if remaining <= 10, switch to batch verification (more efficient)
- If remaining == 0, stop making requests; queue work for after reset time

**Batch Optimization:**
Instead of:
```
for each nurse:
  POST /licenses/verify  # 1 request per nurse
```

Use batch when possible:
```
nurses_chunk = split(all_nurses, 100)
for each chunk:
  POST /licenses/batch-verify  # 1 request per 100 nurses
```

This reduces rate limit usage by 100x.

---

## 7. Data Mapping

**Guidance Note:** Mapping documents how internal entities translate to/from external system fields. Be explicit to avoid mismatch errors.

### Mapping Table: Nurse Credentials (Internal → Credentialing System)

| Internal Field | External Field | Type | Direction | Notes |
|---|---|---|---|---|
| Nurse.credentials[].license_number | request.license_number | string | → | Must match regex ^[A-Z]{2}-[0-9]{6}$ |
| Nurse.credentials[].license_type | request.license_type | enum | → | [RN, LPN, CNA, RT]; 1:1 match |
| Nurse.credentials[].expiration_date | request.expiration_date | ISO 8601 date | → | Format: YYYY-MM-DD |
| (N/A) | response.status | enum | ← | Map to Credential.status_external (see below) |
| Nurse.credentials[].status | response.status | enum | ← | VALID → VALID; EXPIRED → EXPIRED; REVOKED → REVOKED; SUSPENDED → REVOKED; UNKNOWN → PENDING |
| Nurse.credentials[].verified_at | response.verified_at | timestamp | ← | Set on successful verification |
| Nurse.credentials[].last_verified_at | response.verified_at | timestamp | ← | Update to latest verification time |
| (N/A) | response.record_id | string | ← | Store in Credential.credentialing_system_ref for audit trail |
| Nurse.credentials[].issued_date | response.issued_date | ISO 8601 date | ← | Optional; store if provided |

### Status Mapping Detail

**Credentialing System Status → Internal Credential Status:**
- `VALID` → `VALID` (license is current and in good standing)
- `EXPIRED` → `EXPIRED` (expiration_date has passed)
- `REVOKED` → `REVOKED` (license was revoked; nurse cannot use this credential)
- `SUSPENDED` → `REVOKED` (license is suspended; treat as cannot-use)
- `PENDING_RENEWAL` → `PENDING` (license is up for renewal but not yet expired; can still use)
- `UNKNOWN` → `PENDING` (no record found; insufficient data to allow; mark as pending review)

### Create Assignment: Data Flow

```
Input: User clicks "Create Assignment" for Nurse X and Shift Y

Step 1: Extract credential to verify
  - Pick first non-expired credential from Nurse.credentials
  - Extract: license_number, license_type, expiration_date

Step 2: Call credentialing API
  - POST /licenses/verify with extracted fields
  
Step 3: Map response back to Assignment
  - response.status == VALID → Assignment.credentials_verified_at = now(); proceed
  - response.status == EXPIRED → Assignment.status = REJECTED; reason = "Credential expired"
  - response.status == REVOKED → Assignment.status = REJECTED; reason = "Credential revoked"
  - response.status == UNKNOWN → Assignment.status = REJECTED; reason = "Credential could not be verified"; escalate to human
  
Step 4: Create Assignment record
  - status = CONFIRMED (if verification succeeded)
  - verified_by = response.record_id (credentialing system reference)
  - credentials_verified_at = response.verified_at
```

---

## 8. State Synchronization

**Guidance Note:** Credentialing systems change over time. Document how the agent keeps sync.

**Credential Status Changes:**
- Licenses expire (expiration_date passes)
- Licenses are revoked (external system marks them)
- Licenses are renewed (external system issues new dates)

**How the Agent Stays in Sync:**

**Option A: On-Demand Verification (Recommended)**
- Every assignment creation triggers verification
- Most current data; no staleness
- Higher latency (depends on external API)

**Option B: Cached with TTL**
- Store credential verification result locally
- Cache TTL = 24 hours
- On assignment creation:
  - If cache miss or cache expired: verify now (on-demand)
  - If cache hit and not expired: use cached value
- Periodically sync all active credentials (batch job, once daily)

**Option C: Webhook Notifications**
- Credentialing system sends webhook when status changes
- Agent updates local credential record
- On assignment creation: use local value (no external call needed)
- Pros: real-time, zero latency
- Cons: requires webhook setup (not yet implemented; plan for future)

**Current Implementation: Option A (On-Demand)**
- Every call to verifyLicense() hits the external API
- No caching
- Simple, correct, but higher latency and API calls

**Future Plan: Migrate to Option B**
- Add cache table: credential_verifications (credential_id, status, verified_at, expires_at)
- Cache TTL = 24 hours
- Batch sync job runs daily at 2am UTC to refresh all nurse credentials

---

## 9. Failure Modes & Fallbacks

**Guidance Note:** What happens when the integration breaks? Be specific.

### Failure Mode 1: Credentialing System Timeout

**Scenario:** Agent calls verification API; no response for 10+ seconds.

**Handling:**
1. Stop waiting after 10 seconds
2. Mark request as TIMEOUT
3. Retry up to 2 times (total 3 attempts, each with fresh 10s timeout)
4. If all attempts timeout:
   - Set Assignment.status = PENDING_VERIFICATION_TIMEOUT
   - Send notification to user: "Credential verification system is temporarily unavailable. Your assignment will be finalized when the system is back online."
   - Queue assignment in async verification queue
   - Ops team is alerted (email + dashboard flag)
   - Periodically retry (background job, every 5 minutes)
   - If still failing after 24 hours, escalate to human review

### Failure Mode 2: Credentialing System Returns UNKNOWN

**Scenario:** License number does not exist in credentialing system.

**Handling:**
1. Set Assignment.status = REJECTED
2. Store reason: "License not found in credentialing system. License number may be invalid or not registered."
3. Send notification to nurse: "Your credential could not be verified. Please verify your license number and try again."
4. Do not auto-block nurse; nurse can still see the error and correct it

### Failure Mode 3: Token Expired

**Scenario:** API returns 401 Unauthorized.

**Handling:**
1. Log: "Token expired; fetching fresh token"
2. Fetch new token from AWS Secrets Manager (key: healthcorp/api-token)
3. Retry the verification request with new token
4. If token fetch fails (Secrets Manager unreachable):
   - Set Assignment.status = CREDENTIAL_VERIFICATION_UNAVAILABLE
   - Alert ops: "Cannot access credentialing system: Secrets Manager unreachable"
   - User sees error: "System is experiencing technical issues. Please try again later."

### Failure Mode 4: Credentialing System Down (503 Service Unavailable)

**Scenario:** Credentialing system is in maintenance or overloaded.

**Handling:**
1. Retry up to 3 times with exponential backoff (2s, 4s, 8s)
2. If all retries fail:
   - Log: "Credentialing system unavailable after 3 retries"
   - Check status page: https://status.healthcorp.io
   - If status page says maintenance, queue assignment for retry after maintenance window
   - If no known maintenance:
     - Alert ops
     - Fail the assignment: "Credential verification system is currently offline. Please try again in a few minutes."
     - Queue for automatic retry every 5 minutes (up to 24 hours)

### Fallback Matrix

| Failure | Immediate Action | User Experience | Long-term Action |
|---|---|---|---|
| Timeout | Retry 2x; escalate | "System busy; trying again..." | Async queue; retry every 5m for 24h |
| License Not Found | Reject assignment | "License not recognized; please verify" | Nurse can correct and retry |
| Token Expired | Fetch new token; retry | (transparent; no user notice) | N/A |
| System Down | Retry 3x; alert ops | "System offline; trying again..." | Async queue; wait for status page update |
| Rate Limited | Respect Retry-After; queue | (transparent; queued) | Batch verification; reduced request rate |

---

## 10. Monitoring & Alerting

**Guidance Note:** How does the agent/ops know the integration is working? Be specific about metrics and thresholds.

### Metrics to Track

| Metric | Definition | Collection Method | Threshold | Action |
|---|---|---|---|---|
| Verification Success Rate | (successful verifications) / (total verification attempts) | Log every call | Should be >= 95% | Alert ops if < 90% for 5 min window |
| API Latency (p95) | 95th percentile response time | Sample logs every call | Should be <= 1s | Alert ops if > 3s for 10 min window |
| Rate Limit Hits | How often we hit rate limit (429 errors) | Count 429 responses | Should be 0 | Alert ops if > 10 in an hour; investigate traffic |
| Timeout Rate | (timeout errors) / (total attempts) | Count timeout errors | Should be < 1% | Alert ops if > 5% for 5 min window |
| Token Rotation Success | Token refresh requests that succeed | Log token refresh events | Should be 100% | Alert ops if any failure |
| Credential Sync Freshness | % of credentials verified in last 24h (if caching) | Run daily sync batch | Should be >= 99% | Alert if < 95% |

### Alert Rules

**Rule 1: High Failure Rate**
```
IF (failure_count / total_count) > 10% over last 5 minutes
THEN send alert to #ops with subject "High credentialing API failure rate: {rate}%"
INCLUDE: example failures, recent error codes, request_ids for debugging
```

**Rule 2: Persistent Timeouts**
```
IF (timeout_count / total_count) > 5% over last 5 minutes
THEN send alert to #ops: "Credentialing API timeouts elevated"
INCLUDE: timeout examples, P95 latency
```

**Rule 3: Rate Limit Exhaustion**
```
IF rate_limit_remaining <= 100
THEN switch to batch verification; log "Rate limit approaching"
IF rate_limit_remaining == 0
THEN queue remaining verifications; send alert "Rate limit exhausted"
```

### Logging Requirements

Every verification attempt must log:
```json
{
  "timestamp": "ISO 8601",
  "license_number": "CA-456789",
  "license_type": "RN",
  "status": "VALID|TIMEOUT|ERROR|...",
  "response_code": "200|500|429|...",
  "latency_ms": 250,
  "attempt_number": 1,
  "request_id": "req-xxx", // from response
  "assignment_id": "uuid",
  "nurse_id": "uuid",
  "error_code": "LICENSE_NOT_FOUND|...", // if error
  "error_message": "License not found in database",
  "retry_scheduled": true|false
}
```

### Dashboard

Create a real-time dashboard showing:
- Verification success rate (last hour, last day)
- API latency distribution (p50, p95, p99)
- Error codes breakdown (pie chart)
- Rate limit usage
- Timeout rate
- Assignment backlog (if async queue in use)

---

## 11. Additional Constraints & Notes

### Data Privacy
- License numbers may be sensitive (PII)
- Do not log license numbers in production logs; sanitize before sharing
- Response data is retained locally for audit purposes; subject to HIPAA if applicable
- Credential verification logs are protected under PHI rules (if healthcare context)

### Performance
- Batch verification is strongly preferred over single verification (100x fewer API calls)
- During high-volume periods (peak staffing times), use batch endpoints to reduce latency
- Consider pre-fetching credential status during off-peak hours

### Versioning
- API endpoint is v2; do not use v1 (deprecated as of 2025-01-01)
- If v3 is released, switch endpoints in CLAUDE.md; notify all teams

### Support & Escalation
- Integration issues: contact integration-ops@company.com
- Vendor support: contact healthcorp-support@healthcorp.io (open during 9am-5pm PT weekdays)
- For urgent issues: escalation_phone in Secrets Manager (key: healthcorp/escalation-phone)

---

## Checklist: Is This Spec Complete?

Use this checklist before handing the spec to the agent:

- [ ] Integration purpose is clear (what, why, who does what)
- [ ] System description includes: name, provider, base URL, documentation link, supported operations
- [ ] Authentication is explicit: method, where to store credentials, how to handle expiration
- [ ] All endpoints are fully specified: request format, response format, error format
- [ ] Request/response examples are included (not just schema)
- [ ] Error handling is defined for every HTTP status code and timeout
- [ ] Retry logic is specified: condition, max attempts, backoff strategy
- [ ] Rate limits are numeric (requests/min, concurrent, daily limits)
- [ ] Data mapping is documented in both directions (internal ↔ external)
- [ ] State synchronization approach is clear (on-demand, cached, webhook)
- [ ] Failure modes have explicit handling (no "try something reasonable")
- [ ] Fallbacks are specified (what to do if external system is down)
- [ ] Monitoring metrics are defined with thresholds and alert rules
- [ ] Logging requirements specify what must be captured
- [ ] Privacy, performance, versioning notes are included
- [ ] Escalation path and support contacts are listed

If any item is unchecked, the spec is incomplete. Add details before giving to agent.

---

## When to Use This Template

- **New integration:** Use the full template
- **Updating existing integration:** Update the relevant sections; leave unchanged sections as-is
- **Multiple endpoints in one system:** Use one spec document; create a section for each endpoint
- **Integrating with internal service:** Same template applies; replace "external system" with service name

**Remember:** If the agent has to guess, it will guess wrong. Completeness prevents surprises.
