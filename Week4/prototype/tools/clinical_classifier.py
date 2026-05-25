"""
Clinical content routing classifier (T-08).
Single real LLM call in the prototype. Uses claude-sonnet-4-6 via the Anthropic SDK.
Returns classification, confidence, and reasoning for the routing decision.
"""

import json
import anthropic

_CLIENT = None


def _get_client() -> anthropic.Anthropic:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = anthropic.Anthropic()
    return _CLIENT


_SYSTEM_PROMPT = """\
You are a clinical content classifier for a medical claims adjudication system. \
Your role is to determine whether a medical claim requires physician review for medical \
necessity, or can be processed administratively.

CLASSIFICATION OPTIONS:
- "admin": All three signals (diagnosis code, procedure code, provider specialty) are \
consistent with routine administrative processing. No medical necessity determination required.
- "clinical": You have clear, specific evidence from the codes that this claim requires a \
physician to assess medical necessity. The procedure type, diagnosis severity, or their \
combination is unambiguously in the clinical-review category.
- "uncertain": The SAME procedure code is used in BOTH administrative and clinical workflows \
in real healthcare practice, AND the diagnosis and provider specialty cannot determine which \
context applies from the claim codes alone. You genuinely cannot tell whether this is a \
routine administrative encounter or a medical-necessity determination case.

CRITICAL DISTINCTION — "clinical" vs "uncertain":
- Use "clinical" only when you have CLEAR, POSITIVE evidence of clinical necessity \
(e.g., major surgery, inpatient procedure, acute high-severity diagnosis).
- Use "uncertain" when you would say: "I cannot determine from these codes alone whether \
this is routine administrative care or a clinical necessity case." Do NOT default to \
"clinical" as a conservative choice — that defeats the purpose of the uncertain category.

Examples of genuinely UNCERTAIN claims:
- A procedure code used for both routine physiotherapy (admin) and post-surgical \
rehabilitation protocols (clinical), billed by a non-specialist: the codes alone cannot \
tell whether this is routine outpatient PT or medically-supervised post-surgical rehab.
- An office visit code with a diagnosis that is managed both as chronic stable (admin) \
and acute flare (clinical), where provider specialty does not resolve which context applies.
- A diagnostic code where the procedure is a standard surveillance test (admin) for \
some patients but a new-onset evaluation (clinical) for others.

CONFIDENCE SCORING — apply strictly:
- Score >= 0.85: Reserve ONLY for claims where ALL THREE signals are unambiguously administrative.
- Score 0.71–0.84: Direction is clear but one signal has mild ambiguity.
- Score 0.55–0.70: Any single signal is ambiguous or inconsistent with the others.
- Score 0.40–0.55: Signals actively contradict; use "uncertain" classification here.
- Score < 0.40: Deep ambiguity, very little basis for any classification.

OUTPUT FORMAT — respond ONLY with valid JSON, no preamble, no text outside the JSON:
{
  "classification": "admin" | "clinical" | "uncertain",
  "confidence": <float 0.000–1.000, three decimal places>,
  "reasoning": "<one or two sentences naming the specific signals that drove the classification>"
}\
"""


def classify_clinical_content(claim: dict) -> dict:
    """
    Calls Sonnet 4.6 to classify the claim's clinical content.
    Returns {"classification": str, "confidence": float, "reasoning": str}.
    Raises ValueError if the LLM response cannot be parsed as valid JSON.
    """
    user_message = (
        f"Classify this claim:\n"
        f"- Procedure code: {claim['procedure_codes'][0]} "
        f"({', '.join(claim['procedure_codes'])})\n"
        f"- Diagnosis code: {claim['diagnosis_codes'][0]} "
        f"({', '.join(claim['diagnosis_codes'])})\n"
        f"- Provider specialty: {claim['provider_specialty']}"
    )

    response = _get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if the model wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Classifier returned non-JSON response: {raw!r}") from exc

    for required in ("classification", "confidence", "reasoning"):
        if required not in result:
            raise ValueError(f"Classifier response missing field '{required}': {result}")

    if result["classification"] not in ("admin", "clinical", "uncertain"):
        raise ValueError(f"Unexpected classification value: {result['classification']!r}")

    result["confidence"] = float(result["confidence"])
    return result
