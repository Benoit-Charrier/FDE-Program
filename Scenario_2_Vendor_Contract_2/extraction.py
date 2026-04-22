from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from typing import Optional
import anthropic
import audit
from ingestion import Page

CLAUSE_FAMILIES = [
    "liability_cap",
    "dpa",
    "termination",
    "ip_ownership",
    "sla",
    "governing_law",
    "indemnity",
]

EXTRACTION_PROMPT = """You are a legal contract analyst. Extract specific clause text from the vendor contract below.

For each of the following clause families, find and return the VERBATIM text from the contract. Do not paraphrase or summarise.

Clause families to extract:
1. liability_cap — limitation of liability clause
2. dpa — data processing agreement or data processing addendum clause
3. termination — termination for convenience clause
4. ip_ownership — intellectual property ownership clause
5. sla — service level agreement or uptime commitment clause
6. governing_law — governing law and jurisdiction clause
7. indemnity — indemnification clause

Return a JSON object with exactly this structure for each clause family:
{
  "liability_cap": {"extracted_text": "<verbatim text or empty string>", "source_page": <page number or null>, "confidence": <0.0-1.0>, "found": <true/false>},
  "dpa": {"extracted_text": "...", "source_page": ..., "confidence": ..., "found": ...},
  "termination": {"extracted_text": "...", "source_page": ..., "confidence": ..., "found": ...},
  "ip_ownership": {"extracted_text": "...", "source_page": ..., "confidence": ..., "found": ...},
  "sla": {"extracted_text": "...", "source_page": ..., "confidence": ..., "found": ...},
  "governing_law": {"extracted_text": "...", "source_page": ..., "confidence": ..., "found": ...},
  "indemnity": {"extracted_text": "...", "source_page": ..., "confidence": ..., "found": ...}
}

Rules:
- extracted_text: copy the clause text VERBATIM from the contract. Return empty string "" if not found.
- source_page: the page number where the clause appears. Return null if not found.
- confidence: your certainty (0.0-1.0) that the extracted text correctly corresponds to the clause family.
- found: true if clause was located, false if not found in the document.
- Return ONLY valid JSON. No explanation, no markdown fences.

CONTRACT TEXT:
"""


@dataclass
class ClauseResult:
    family: str
    extracted_text: str
    source_page: Optional[int]
    confidence: float
    found: bool


def extract(pages: list[Page], contract_id: str) -> list[ClauseResult]:
    full_text = _build_document_text(pages)
    client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": EXTRACTION_PROMPT,
                            "cache_control": {"type": "ephemeral"},
                        },
                        {
                            "type": "text",
                            "text": full_text,
                        },
                    ],
                }
            ],
        )

        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0].strip()
        parsed = json.loads(raw)
        results = _parse_results(parsed)
        audit.log_event(contract_id, "extraction", {
            "status": "ok",
            "clauses_found": sum(1 for r in results if r.found),
        })
        return results

    except Exception as e:
        audit.log_event(contract_id, "extraction_error", {"error": str(e)})
        return _empty_results()


def _build_document_text(pages: list[Page]) -> str:
    parts = []
    for page in pages:
        parts.append(f"[PAGE {page.page_number}]\n{page.text}")
    return "\n\n".join(parts)


def _parse_results(parsed: dict) -> list[ClauseResult]:
    results = []
    for family in CLAUSE_FAMILIES:
        data = parsed.get(family, {})
        results.append(ClauseResult(
            family=family,
            extracted_text=str(data.get("extracted_text", "")),
            source_page=data.get("source_page"),
            confidence=float(data.get("confidence", 0.0)),
            found=bool(data.get("found", False)),
        ))
    return results


def _empty_results() -> list[ClauseResult]:
    return [
        ClauseResult(family=f, extracted_text="", source_page=None, confidence=0.0, found=False)
        for f in CLAUSE_FAMILIES
    ]
