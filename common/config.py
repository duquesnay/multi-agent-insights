"""Centralized configuration for delegation retrospective analysis.

This module provides:
- Path configuration for all data files
- Temporal period definitions (P2, P3, P4)
- Token thresholds and magic numbers
- Single source of truth for all project constants
"""

from pathlib import Path
from typing import Dict, Tuple

# =============================================================================
# PATH CONFIGURATION
# =============================================================================

# Project root is parent of common/ directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
ANALYSIS_DIR = PROJECT_ROOT / "analysis"
ANALYSES_DIR = PROJECT_ROOT / "analyses"

# Claude projects directory (user-specific)
PROJECTS_DIR = Path.home() / ".claude" / "projects"

# Data files
DELEGATION_RAW_FILE = RAW_DATA_DIR / "delegation_raw.jsonl"
SESSIONS_DATA_FILE = DATA_DIR / "full_sessions_data.json"
ENRICHED_SESSIONS_FILE = DATA_DIR / "enriched_sessions_data.json"
AGENT_CALLS_CSV = RAW_DATA_DIR / "agent_calls_metadata.csv"

# Output files
ROUTING_PATTERNS_FILE = DATA_DIR / "routing_patterns_by_period.json"
ROUTING_QUALITY_FILE = DATA_DIR / "routing_quality_analysis.json"
GOOD_ROUTING_FILE = DATA_DIR / "good_routing_patterns.json"
SYSTEM_METRICS_FILE = DATA_DIR / "system_metrics_report.json"
TRANSITION_ANALYSIS_FILE = DATA_DIR / "transition_analysis.json"
TEMPORAL_SEGMENTATION_FILE = PROJECT_ROOT / "temporal-segmentation-report.json"

# Historical data
CONVERSATIONS_DIR = DATA_DIR / "conversations"
HISTORICAL_DIR = DATA_DIR / "historical"

# =============================================================================
# TEMPORAL PERIOD DEFINITIONS
# =============================================================================

# Period boundaries (ISO date strings)
P2_START = "2025-09-03"
P2_END = "2025-09-11"
P3_START = "2025-09-12"
P3_END = "2025-09-20"
P4_START = "2025-09-21"
P4_END = "2025-09-30"

# Extended period (for v8.0 analysis including August)
P1_START = "2025-08-04"
P1_END = "2025-09-02"

# Period metadata
PERIOD_DEFINITIONS: Dict[str, Dict] = {
    "P1": {
        "name": "Launch + Vacances",
        "start": P1_START,
        "end": P1_END,
        "changes": ["Initial launch", "Vacation period"],
        "description": "Initial system launch and vacation period"
    },
    "P2": {
        "name": "Conception Added",
        "start": P2_START,
        "end": P2_END,
        "changes": ["+solution-architect", "+project-framer"],
        "description": "Addition of planning and design capabilities"
    },
    "P3": {
        "name": "Délégation Obligatoire",
        "start": P3_START,
        "end": P3_END,
        "changes": [
            "Mandatory delegation policy",
            "+content-developer (Sept 15)",
            "+refactoring-specialist (Sept 20)"
        ],
        "description": "Mandatory delegation with content and refactoring specialists"
    },
    "P4": {
        "name": "Post-Restructuration",
        "start": P4_START,
        "end": P4_END,
        "changes": [
            "developer → senior-developer + junior-developer (Sept 21 16h24)",
            "Scope creep safeguards (Sept 21-22)",
            "+parallel-worktree-framework (Sept 22)"
        ],
        "description": "Major restructuring with senior/junior split and safeguards"
    }
}

# Period tuples for compatibility with existing code
PERIODS: Dict[str, Tuple[str, str, str]] = {
    "P1": (P1_START, P1_END, "Launch + Vacances"),
    "P2": (P2_START, P2_END, "Conception Added"),
    "P3": (P3_START, P3_END, "Mandatory Delegation"),
    "P4": (P4_START, P4_END, "Post-Restructuration")
}

# =============================================================================
# THRESHOLDS AND MAGIC NUMBERS
# =============================================================================

# Session classification thresholds
MARATHON_THRESHOLD = 20  # Delegations count that defines a "marathon" session
HEAVY_SESSION_THRESHOLD = 15  # Sessions with significant delegation count
LIGHT_SESSION_THRESHOLD = 5  # Sessions with minimal delegations

# Token thresholds
HIGH_TOKEN_SESSION = 100000  # Token count that defines high-usage session
CACHE_EFFICIENCY_THRESHOLD = 0.3  # Minimum cache hit rate for "efficient" sessions

# Success rate thresholds
GOOD_SUCCESS_RATE = 0.8  # 80% success rate or higher
POOR_SUCCESS_RATE = 0.5  # Below 50% success rate

# Agent usage thresholds
TOP_AGENTS_COUNT = 5  # Number of top agents to display in reports
MAX_AGENT_DIVERSITY = 10  # Maximum unique agents in a well-structured session

# =============================================================================
# AGENT CONFIGURATIONS
# =============================================================================

# Known agent types (for validation and reporting)
PLANNING_AGENTS = ["solution-architect", "project-framer", "backlog-manager"]
IMPLEMENTATION_AGENTS = ["developer", "senior-developer", "junior-developer"]
SPECIALIST_AGENTS = [
    "refactoring-specialist",
    "integration-specialist",
    "performance-optimizer",
    "content-developer",
    "ux-specialist",
    "graphics-specialist",
    "game-designer"
]
COORDINATION_AGENTS = ["git-workflow-manager", "parallel-worktree-framework"]

ALL_KNOWN_AGENTS = (
    PLANNING_AGENTS +
    IMPLEMENTATION_AGENTS +
    SPECIALIST_AGENTS +
    COORDINATION_AGENTS
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_dynamic_periods(use_git: bool = False, use_cache: bool = True) -> Dict[str, Dict]:
    """Get period definitions dynamically or from static configuration.

    This function provides a bridge between static and dynamic period discovery.
    By default, it uses the hardcoded PERIOD_DEFINITIONS for backward compatibility.
    When use_git=True, it attempts git archaeology to discover periods.

    Args:
        use_git: If True, discover periods from git history
        use_cache: If True and use_git=True, use cached periods if available

    Returns:
        Dictionary of period definitions in PERIOD_DEFINITIONS format

    Examples:
        # Use hardcoded periods (backward compatible)
        periods = get_dynamic_periods()

        # Discover from git (methodology-aligned)
        periods = get_dynamic_periods(use_git=True)

        # Force fresh git discovery
        periods = get_dynamic_periods(use_git=True, use_cache=False)
    """
    if not use_git:
        # Backward compatible: return hardcoded periods
        return PERIOD_DEFINITIONS

    # Import here to avoid circular dependency
    try:
        from .period_builder import get_periods
        return get_periods(use_git=True, use_cache=use_cache)
    except ImportError as e:
        import logging
        logging.warning(f"Failed to import period_builder: {e}. Using fallback periods.")
        return PERIOD_DEFINITIONS


def get_period_for_date(date_str: str) -> str | None:
    """Classify a date string into its period (P1, P2, P3, P4).

    Args:
        date_str: ISO format date string (e.g., "2025-09-15" or full timestamp)

    Returns:
        Period ID ("P1", "P2", "P3", "P4") or None if outside all periods
    """
    from datetime import datetime

    # Extract date part if full timestamp
    if 'T' in date_str:
        date_str = date_str.split('T')[0]

    date_obj = datetime.fromisoformat(date_str).date()

    for period_id, (start, end, _) in PERIODS.items():
        start_date = datetime.fromisoformat(start).date()
        end_date = datetime.fromisoformat(end).date()
        if start_date <= date_obj <= end_date:
            return period_id

    return None


def ensure_data_dirs():
    """Create all data directories if they don't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    RAW_DATA_DIR.mkdir(exist_ok=True)
    ANALYSIS_DIR.mkdir(exist_ok=True)
    CONVERSATIONS_DIR.mkdir(exist_ok=True)
    HISTORICAL_DIR.mkdir(exist_ok=True)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_config():
    """Validate configuration and check for common issues.

    Returns:
        List of warning messages (empty if all OK)
    """
    warnings = []

    # Check if data files exist
    if not DELEGATION_RAW_FILE.exists():
        warnings.append(f"Missing data file: {DELEGATION_RAW_FILE}")

    if not SESSIONS_DATA_FILE.exists():
        warnings.append(f"Missing data file: {SESSIONS_DATA_FILE}")

    # Check period date ordering
    from datetime import datetime
    for period_id, (start, end, _) in PERIODS.items():
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        if start_dt >= end_dt:
            warnings.append(f"Period {period_id}: start date >= end date")

    return warnings


if __name__ == "__main__":
    # Print configuration summary
    print("=== Delegation Retrospective Configuration ===\n")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"\nPeriod Definitions:")
    for period_id, meta in PERIOD_DEFINITIONS.items():
        print(f"  {period_id}: {meta['start']} to {meta['end']} - {meta['name']}")

    print(f"\nThresholds:")
    print(f"  Marathon: {MARATHON_THRESHOLD} delegations")
    print(f"  High tokens: {HIGH_TOKEN_SESSION} tokens")
    print(f"  Good success rate: {GOOD_SUCCESS_RATE:.0%}")

    # Validate
    warnings = validate_config()
    if warnings:
        print(f"\n⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("\n✅ Configuration validated successfully")
