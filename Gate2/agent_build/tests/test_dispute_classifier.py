import pytest
from agent_build.src.dispute_classifier import (
    DisputeType,
    ClassificationResult,
    classify_from_structured_field,
    classify_from_contact_text,
)


def test_fuel_surch_damage_classified():
    result = classify_from_structured_field("FUEL_SURCH_DAMAGE")
    assert result.dispute_type == DisputeType.FUEL_SURCH_DAMAGE
    assert result.confidence == 1.0
    assert result.source_field == "DISPUTE_TYPE"


def test_dim_weight_classified():
    result = classify_from_structured_field("DIM_WEIGHT")
    assert result.dispute_type == DisputeType.DIM_WEIGHT
    assert result.confidence == 1.0


def test_redelivery_fee_classified():
    result = classify_from_structured_field("REDELIVERY_FEE")
    assert result.dispute_type == DisputeType.REDELIVERY_FEE
    assert result.confidence == 1.0


def test_unknown_type_returns_unknown_zero_confidence():
    """Out-of-taxonomy value must return UNKNOWN with 0.0 confidence — triggers ET-002."""
    result = classify_from_structured_field("DAMAGED_GOODS")
    assert result.dispute_type == DisputeType.UNKNOWN
    assert result.confidence == 0.0


def test_empty_string_returns_unknown():
    result = classify_from_structured_field("")
    assert result.dispute_type == DisputeType.UNKNOWN
    assert result.confidence == 0.0


def test_classification_is_case_insensitive():
    """DISPUTE_TYPE values in the artefact are uppercase; lowercase input must still classify."""
    result = classify_from_structured_field("fuel_surch_damage")
    assert result.dispute_type == DisputeType.FUEL_SURCH_DAMAGE


def test_mixed_case_classified():
    result = classify_from_structured_field("Dim_Weight")
    assert result.dispute_type == DisputeType.DIM_WEIGHT


def test_whitespace_stripped():
    result = classify_from_structured_field("  REDELIVERY_FEE  ")
    assert result.dispute_type == DisputeType.REDELIVERY_FEE


def test_nlp_path_raises_not_implemented():
    """NLP classification from contact text is a spec gap — must raise NotImplementedError."""
    with pytest.raises(NotImplementedError, match="not specified in D4"):
        classify_from_contact_text("I want to dispute the fuel surcharge on my last invoice")


def test_nlp_path_raises_regardless_of_input():
    with pytest.raises(NotImplementedError):
        classify_from_contact_text("")
