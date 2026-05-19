# agent_build/tests/test_specialty_mapper.py
"""
Tests for Contract 6 specialty mapping algorithm.
Key boundary: cosine similarity score == SPECIALTY_MAPPING_THRESHOLD (0.75) counts as MAPPED, not UNMAPPABLE.
Spec: "score = 0.75 exactly counts as MAPPED (>= threshold)"
"""
import math
from unittest.mock import MagicMock

from agent_build.src.specialty_mapper import VocabularyEntry, map_specialty

THRESHOLD = 0.75

# Unit vectors for deterministic cosine similarity tests
VOCAB = [
    VocabularyEntry(code="ICU", label="Intensive Care Unit", embedding=[1.0, 0.0, 0.0]),
    VocabularyEntry(code="ER",  label="Emergency Room",      embedding=[0.0, 1.0, 0.0]),
    VocabularyEntry(code="OR",  label="Operating Room",      embedding=[0.0, 0.0, 1.0]),
]


def _mock_embedding(vector: list[float]) -> MagicMock:
    client = MagicMock()
    client.embeddings.create.return_value.data = [MagicMock(embedding=vector)]
    return client


def test_exact_match_returns_exact_no_embedding_call():
    client = _mock_embedding([1.0, 0.0, 0.0])
    result = map_specialty("Intensive Care Unit", VOCAB, client, "text-embedding-3-small", THRESHOLD)
    assert result.specialty_confidence == "EXACT"
    assert result.specialty_required == "ICU"
    assert result.best_score is None
    client.embeddings.create.assert_not_called()


def test_exact_match_is_case_insensitive():
    client = _mock_embedding([1.0, 0.0, 0.0])
    result = map_specialty("intensive care unit", VOCAB, client, "text-embedding-3-small", THRESHOLD)
    assert result.specialty_confidence == "EXACT"
    assert result.specialty_required == "ICU"


def test_high_similarity_returns_mapped():
    # 5-degree offset from ICU vector → score ≈ cos(5°) ≈ 0.996 > threshold
    angle = math.radians(5)
    emb = [math.cos(angle), math.sin(angle), 0.0]
    result = map_specialty("ICU-level care", VOCAB, _mock_embedding(emb), "text-embedding-3-small", THRESHOLD)
    assert result.specialty_confidence == "MAPPED"
    assert result.specialty_required == "ICU"
    assert result.best_score >= THRESHOLD


def test_boundary_exactly_at_threshold_counts_as_mapped():
    # Construct unit vector so cosine similarity with ICU [1,0,0] == exactly 0.75
    # cos(angle) = 0.75 → angle = arccos(0.75); unit vector: [0.75, sqrt(1 - 0.75^2), 0]
    emb = [0.75, math.sqrt(1 - 0.75 ** 2), 0.0]
    result = map_specialty("periop cover", VOCAB, _mock_embedding(emb), "text-embedding-3-small", THRESHOLD)
    assert result.specialty_confidence == "MAPPED"
    assert abs(result.best_score - THRESHOLD) < 1e-9


def test_below_threshold_returns_unmappable():
    # 60-degree offset from ICU vector → score = cos(60°) = 0.5 < threshold
    angle = math.radians(60)
    emb = [math.cos(angle), math.sin(angle), 0.0]
    result = map_specialty("Level 3 perioperative cover", VOCAB, _mock_embedding(emb), "text-embedding-3-small", THRESHOLD)
    assert result.specialty_confidence == "UNMAPPABLE"
    assert result.specialty_required is None
    assert result.best_score < THRESHOLD
