# Validation Report — Gate4 D1 Token Economics Model
## MedFlex: WS2 Nurse-to-Shift Matching Agent

*Validated: May 19, 2026*

---

## Overall Verdict: Structurally sound. Two arithmetic errors found; all strategic conclusions hold.

---

## Errors Found

### Error 1 — Option B total per-case cost (§4c table)

The sum of components does not equal $0.844 as stated in the table:

| Component | Value |
|-----------|------:|
| Token cost | $0.01348 |
| Tool cost | $0.00600 |
| HITL cost | $0.82250 |
| **Correct total** | **$0.84198 ≈ $0.842** |

The table states **$0.844** — off by $0.002/case. This figure propagates to:
- §5b "Annual agent variable cost": $0.844 × 240K = $202,560 (correct is $202,080 — $480 difference)
- Executive summary target-volume variable cost: $2,836,000 (correct is ~$2,829,120)

**Impact:** Negligible. Doesn't change any rounded payback or ROI figure. WS2 saving at current volume shifts from $101,440 to $101,920 — payback still rounds to 7.4 years. All target-volume conclusions unaffected (§5c uses the coordinator-headcount method directly, bypassing this rounding error entirely).

---

### Error 2 — Formula typo in §5c "Agent token + tool cost"

The document writes:

> `($0.844 − $0.823) × 3,360,000 = $63,840`

But $0.844 − $0.823 = **$0.021**, and $0.021 × 3,360,000 = **$70,560 ≠ $63,840**.

The result $63,840 is correct — it comes from $0.019 × 3,360,000, as correctly stated in the bracket immediately below. The parenthetical expression is wrong and should be replaced with `$0.019/case × 3,360,000 = $63,840`.

---

## Minor Omission

### Option B: Sonnet system-prompt cache read not costed

Step 4 (Sonnet) likely needs at minimum the classification schema (250 tokens) + output format template (350 tokens) = ~600 tokens of cached system prompt. This is not costed in the Option B breakdown.

Uncosted impact: 600 × $0.30/1M = **$0.00018/case**.
- At 3.36M cases/year: ~$605/year additional cost
- Economically immaterial, but a gap in the architectural accounting.

---

## All Calculations Verified Correct

| Section | Check | Result |
|---------|-------|--------|
| §2 | Baseline: $42/hr loaded rate, $2.10/case WS2, $504K annual | ✓ |
| §4a | Option A token: $0.00512/case | ✓ |
| §4a | Option B Haiku sub: $0.00208, Sonnet sub: $0.01140 | ✓ |
| §4a | Option C token: $0.01920/case | ✓ |
| §4b | HITL per case: A=$0.980, B=$0.8225, C=$0.665 | ✓ |
| §4c | 21:1 return on token spend | ✓ (precise: 21.4:1) |
| §5b | Current vol: $101,440 saving, 7.4-yr payback, −59% 3-yr ROI | ✓ |
| §5b | Combined WS1+WS2: 2.8-yr payback, 7.8% 3-yr ROI | ✓ |
| §5c | Target vol: 84 → 33 coordinators (65,800 HITL hrs/year) | ✓ |
| §5c | $3,820,160 WS2 annual saving | ✓ |
| §5c | 72-day payback (doc states 71 — 1-day rounding difference only) | ✓ |
| §5c | 1,428% 3-year ROI | ✓ |
| §5c | WS1+WS2 combined: $6,172,160/year, 44-day / 6-week payback | ✓ |
| §5c | Combined 2,369% 3-year ROI | ✓ |
| §6 | Conservative: $2,207,360 saving, 8.2-month payback, 341% ROI | ✓ |
| §6 | Optimistic: $5,920,160 saving, 31-day payback, 3,452% ROI | ✓ |

---

## Key Model Logic Validated

**HITL dominates cost (97–99% of per-case agent cost)**
Confirmed by calculation. Token cost is correctly characterised as economically secondary.

**The scale argument is load-bearing and correct**
The model's compelling case depends entirely on 14× volume growth. At current volume, standalone WS2 has a −59% 3-year ROI. This is correctly disclosed. The board-level argument ($6.17M/year, 6-week payback) is arithmetically sound given the volume assumption.

**Model tier is a HITL rate decision, not a token cost decision**
Confirmed: $0.014 incremental token cost (Haiku → Sonnet-only) buys $0.315 HITL saving = **22.5:1** (document rounds to 21:1 by computing total per-case saving / token increment, which gives 21.4:1 — both framings are valid and consistent).

**Conservative stress-test holds**
Stacking all four adverse assumptions simultaneously (25% HITL, +50% tokens, $70K coordinator, $1.5M build) still yields 341% 3-year ROI and 8.1-month payback. Business case is robust.

---

## Recommended Corrections

| Location | Current text | Correction |
|----------|-------------|------------|
| §4c table, Option B row | Total per case: $0.844 | $0.842 |
| §5b, agent variable cost | $0.844 × 240,000 = $202,560 | $0.842 × 240,000 = $202,080; WS2 saving = $101,920; payback = 7.36 years (still rounds to 7.4) |
| §5c, token+tool expression | ($0.844 − $0.823) × 3,360,000 = $63,840 | $0.019/case × 3,360,000 = $63,840 |
| §4a Option B | No Sonnet cache read costed | Add: 600 × $0.30/1M = $0.00018/case (optional — economically trivial) |
