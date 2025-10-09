"""Centralized configuration for delegation retrospective analysis.

This module provides:
- Path configuration for all data files
- Temporal period definitions (P2, P3, P4)
- Token thresholds and magic numbers
- Single source of truth for all project constants
"""

from pathlib import Path
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# =============================================================================
# PATH CONFIGURATION
# =============================================================================

# Project root is parent of tools/ directory (tools/common/ -> tools/ -> project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

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

class ConfigurationError(Exception):
    """Raised when configuration is invalid or incomplete."""
    pass

# Reference: Multi-agent system launch in Claude Code (for documentation only)
# This is NOT used as a fallback - each analysis must define its own time period
DEFAULT_ANALYSIS_START = "2025-08-04"  # Historical reference only

# =============================================================================
# DYNAMIC PERIOD CREATION
# =============================================================================

def _get_fallback_period_from_data() -> Dict[str, Dict]:
    """Create period definition from actual conversation data timestamps.

    This is the last-resort fallback when no period configuration is provided.
    Analyzes existing session data to determine the date range.

    Returns:
        Dictionary with single period covering the data's date range

    Raises:
        ConfigurationError: If no data exists or cannot create period
    """
    import json

    if not SESSIONS_DATA_FILE.exists():
        raise ConfigurationError(
            "No period definitions available and no session data found.\n"
            "You must either:\n"
            "  1. Use --discover-periods for git archaeology\n"
            "  2. Provide --start-date and --end-date\n"
            "  3. Run extraction first to generate session data"
        )

    try:
        with open(SESSIONS_DATA_FILE, 'r') as f:
            data = json.load(f)

        sessions = data.get('sessions', [])
        if not sessions:
            raise ConfigurationError(
                "Session data file exists but contains no sessions.\n"
                "Run extraction first or use --discover-periods / --start-date --end-date"
            )

        # Extract all timestamps from delegations
        all_dates = []
        for session in sessions:
            for delegation in session.get('delegations', []):
                if 'timestamp' in delegation:
                    # Extract date part (YYYY-MM-DD)
                    date_part = delegation['timestamp'].split('T')[0]
                    all_dates.append(date_part)

        if not all_dates:
            raise ConfigurationError(
                "No delegation timestamps found in session data.\n"
                "Data may be corrupted or incomplete."
            )

        min_date = min(all_dates)
        max_date = max(all_dates)

        return {
            "P1": {
                "name": "Analysis Period",
                "start": min_date,
                "end": max_date,
                "changes": ["Data-derived period from existing sessions"],
                "description": f"Auto-generated from session data ({min_date} to {max_date})"
            }
        }

    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Failed to parse session data: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error creating fallback period: {e}")

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
# RUNTIME CONFIGURATION
# =============================================================================

@dataclass
class RuntimeConfig:
    """Runtime configuration for analysis scope.

    Allows pipeline to be reused for different projects and time periods
    without modifying hardcoded constants.
    """
    # Project filtering
    project_filter: Optional[str] = None  # Substring to match in project paths

    # Time range
    start_date: Optional[str] = None  # ISO date string (e.g., "2025-09-26")
    end_date: Optional[str] = None    # ISO date string (e.g., "2025-10-06")

    # Period definitions (overrides PERIOD_DEFINITIONS if provided)
    periods: Optional[Dict[str, Dict]] = None

    # Discovery options
    discover_periods: bool = False  # Use git archaeology to find periods

    # Source configuration
    source_live: bool = False  # Read from ~/.claude/projects/ instead of backup

    def get_periods(self) -> Dict[str, Dict]:
        """Get period definitions with intelligent fallback chain.

        Priority (highest to lowest):
        1. Runtime-provided periods (explicit configuration)
        2. Git archaeology (--discover-periods flag)
        3. Custom date range (--start-date and --end-date)
        4. Data-derived period (from existing session timestamps)

        Raises:
            ConfigurationError: If no valid period source available
        """
        if self.periods:
            return self.periods

        if self.discover_periods:
            return get_dynamic_periods(use_git=True)

        # Auto-create single period from start/end dates if provided
        if self.start_date and self.end_date:
            return {
                "P1": {
                    "name": "Analysis Period",
                    "start": self.start_date,
                    "end": self.end_date,
                    "changes": ["Custom analysis period"],
                    "description": f"Analysis from {self.start_date} to {self.end_date}"
                }
            }

        # Last resort: derive period from existing data
        return _get_fallback_period_from_data()

    def matches_date_range(self, date_str: str) -> bool:
        """Check if a date falls within the configured range.

        Default: Since August 2025 (multi-agent system launch), no upper bound.
        """
        # Extract date part if full timestamp
        if 'T' in date_str:
            date_str = date_str.split('T')[0]

        date_obj = datetime.fromisoformat(date_str).date()

        # Default start date: multi-agent launch
        start_date = self.start_date or DEFAULT_ANALYSIS_START
        start = datetime.fromisoformat(start_date).date()
        if date_obj < start:
            return False

        # End date is optional (defaults to "ongoing")
        if self.end_date:
            end = datetime.fromisoformat(self.end_date).date()
            if date_obj > end:
                return False

        return True

    def matches_project(self, project_path: str) -> bool:
        """Check if a project path matches the configured filter."""
        if not self.project_filter:
            return True  # No filtering

        return self.project_filter.lower() in project_path.lower()


# Global runtime configuration (can be set by pipeline)
_runtime_config: Optional[RuntimeConfig] = None

def set_runtime_config(config: RuntimeConfig):
    """Set the global runtime configuration."""
    global _runtime_config
    _runtime_config = config

def get_runtime_config() -> RuntimeConfig:
    """Get the current runtime configuration (or default).

    Checks environment variables if no runtime config has been set.
    This allows passing config through subprocess boundaries.
    """
    global _runtime_config
    if _runtime_config is None:
        # Try to load from environment variables
        import os
        project_filter = os.getenv('ANALYSIS_PROJECT_FILTER')
        start_date = os.getenv('ANALYSIS_START_DATE')
        end_date = os.getenv('ANALYSIS_END_DATE')
        discover_periods = os.getenv('ANALYSIS_DISCOVER_PERIODS') == 'true'
        source_live = os.getenv('ANALYSIS_SOURCE_LIVE') == 'true'

        if any([project_filter, start_date, end_date, discover_periods, source_live]):
            _runtime_config = RuntimeConfig(
                project_filter=project_filter,
                start_date=start_date,
                end_date=end_date,
                discover_periods=discover_periods,
                source_live=source_live
            )
        else:
            _runtime_config = RuntimeConfig()  # Default: no filtering
    return _runtime_config

def clear_runtime_config():
    """Clear the runtime configuration (revert to defaults)."""
    global _runtime_config
    _runtime_config = None

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_dynamic_periods(use_git: bool = False, use_cache: bool = True) -> Dict[str, Dict]:
    """Get period definitions dynamically from git or data.

    Args:
        use_git: If True, discover periods from git history
        use_cache: If True and use_git=True, use cached periods if available

    Returns:
        Dictionary of period definitions

    Raises:
        ConfigurationError: If git discovery fails and no data available

    Examples:
        # Discover from git (recommended)
        periods = get_dynamic_periods(use_git=True)

        # Force fresh git discovery
        periods = get_dynamic_periods(use_git=True, use_cache=False)

        # Data-derived fallback
        periods = get_dynamic_periods(use_git=False)
    """
    if not use_git:
        # Fallback: derive from existing data
        return _get_fallback_period_from_data()

    # Import here to avoid circular dependency
    try:
        from .period_builder import get_periods
        return get_periods(use_git=True, use_cache=use_cache)
    except ImportError as e:
        import logging
        logging.warning(f"Failed to import period_builder: {e}. Using data-derived fallback.")
        return _get_fallback_period_from_data()


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

    # Period validation happens at runtime via RuntimeConfig.get_periods()
    # which will raise ConfigurationError if periods cannot be determined

    return warnings


if __name__ == "__main__":
    # Print configuration summary
    print("=== Delegation Retrospective Configuration ===\n")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")

    print(f"\nPeriod Definitions:")
    try:
        config = get_runtime_config()
        periods = config.get_periods()
        for period_id, meta in periods.items():
            print(f"  {period_id}: {meta['start']} to {meta['end']} - {meta['name']}")
    except ConfigurationError as e:
        print(f"  ⚠️  No periods configured: {e}")

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
