from pathlib import Path

# Confidence threshold — from D4 §3 KPIs and CLAUDE.md §3
CONFIDENCE_THRESHOLD: float = 0.85

# Semantic similarity thresholds for clause classification (CLAUDE.md §3)
SEMANTIC_COMPLIANT_THRESHOLD: float = 0.85       # [ASSUMPTION]
SEMANTIC_MINOR_DEVIATION_MIN: float = 0.60       # [ASSUMPTION]
# < SEMANTIC_MINOR_DEVIATION_MIN => MAJOR_DEVIATION

# Numeric deviation — > 50% below playbook floor => MAJOR_DEVIATION (CLAUDE.md §3)
NUMERIC_DEVIATION_MAJOR_THRESHOLD: float = 0.50  # from D4 ET-5

# Ironclad retry policy
MAX_IRONCLAD_RETRIES: int = 2
IRONCLAD_RETRY_INTERVAL_SECONDS: int = 5

# Document size anomaly thresholds (scenario: 15-40 pages typical)
EXPECTED_PAGE_COUNT_MIN: int = 15
EXPECTED_PAGE_COUNT_MAX: int = 40
ANOMALY_LOW_PAGE_THRESHOLD: int = 5    # below this: flag as potentially incomplete
ANOMALY_HIGH_PAGE_THRESHOLD: int = 60  # above this: flag but continue

# Playbook
PLAYBOOK_VERSION: str = "v3.4"
PLAYBOOK_PATH: Path = Path(__file__).parent.parent / "playbook" / "playbook_v3_4.md"

# LLM
ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

# Approved lawyers list — names that may appear in lawyer_signoff_name (CLAUDE.md §2)
# [ASSUMPTION: these are the named commercial lawyers on Amelia's team]
APPROVED_LAWYERS: list[str] = [
    "Amelia Forsythe",
    "Sarah Mitchell",
    "James Chen",
]

# Vendor history lookback
VENDOR_HISTORY_QUARTERS: int = 2

# ET-6 fuzzy match: Levenshtein distance <= this value => probable match
VENDOR_NAME_FUZZY_THRESHOLD: int = 2
