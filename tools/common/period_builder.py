"""Dynamic Period Discovery via Git Archaeology.

This module implements ADR-003: Dynamic Period Discovery.
It discovers period boundaries from git history instead of hardcoding dates.

Methodology Alignment:
- "Git archaeology FIRST" - Discovers timeline from git commits
- No assumptions about dates - Validates against actual configuration changes
- Reusable across different time ranges (v8.0, v9.0, etc.)

Usage:
    builder = PeriodBuilder()
    periods = builder.discover_periods()  # Auto-discover from git

    # Or with manual override
    periods = builder.discover_periods(use_git=False)  # Use fallback
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import subprocess
import json
import logging
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)


class PeriodDiscoveryError(Exception):
    """Raised when period discovery from git fails."""
    pass


@dataclass
class PeriodChange:
    """Represents a configuration change that defines a period boundary."""
    date: str  # ISO format date
    commit_hash: str
    message: str
    changes: List[str]  # List of changes (e.g., ["+solution-architect", "Mandatory delegation"])


class PeriodBuilder:
    """Builds period definitions dynamically from git archaeology.

    This class discovers period boundaries by analyzing git history of
    ~/.claude-memories for agent configuration changes.

    Attributes:
        repo_path: Path to the claude-memories git repository
        cache_file: Path to cache file for discovered periods
        cache_ttl_hours: Cache time-to-live in hours (default: 24)
    """

    DEFAULT_REPO_PATH = Path.home() / ".claude-memories"
    CACHE_FILE = Path(__file__).resolve().parent.parent.parent / "data" / ".period_cache.json"
    CACHE_TTL_HOURS = 24

    def __init__(
        self,
        repo_path: Optional[Path] = None,
        cache_file: Optional[Path] = None,
        cache_ttl_hours: int = 24
    ):
        """Initialize PeriodBuilder.

        Args:
            repo_path: Path to git repository (default: ~/.claude-memories)
            cache_file: Path to cache file (default: data/.period_cache.json)
            cache_ttl_hours: Cache TTL in hours (default: 24)
        """
        self.repo_path = repo_path or self.DEFAULT_REPO_PATH
        self.cache_file = cache_file or self.CACHE_FILE
        self.cache_ttl_hours = cache_ttl_hours

    def discover_periods(
        self,
        use_git: bool = True,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Dict]:
        """Discover period definitions from git history or cache.

        Args:
            use_git: If True, discover from git; if False, use fallback
            start_date: Start date for git log search (ISO format)
            end_date: End date for git log search (ISO format)
            use_cache: If True, use cached periods if available and fresh

        Returns:
            Dictionary of period definitions matching PERIOD_DEFINITIONS format

        Raises:
            PeriodDiscoveryError: If git discovery fails and no fallback available
        """
        # If not using git, return fallback immediately (ignore cache)
        if not use_git:
            return self._get_fallback_periods()

        # Try cache first if enabled
        if use_cache:
            cached_periods = self._load_cache()
            if cached_periods:
                logger.info("Using cached period definitions")
                return cached_periods

        # Try git discovery
        try:
            periods = self._discover_from_git(start_date, end_date)
            if periods:
                # Cache successful discovery
                self._save_cache(periods)
                logger.info(f"Discovered {len(periods)} periods from git")
                return periods
        except PeriodDiscoveryError as e:
            logger.warning(f"Git discovery failed: {e}. Falling back to hardcoded periods.")

        # Fallback to hardcoded periods
        return self._get_fallback_periods()

    def _discover_from_git(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Dict]:
        """Discover periods by analyzing git commits.

        Args:
            start_date: Start date for search (ISO format)
            end_date: End date for search (ISO format)

        Returns:
            Dictionary of period definitions

        Raises:
            PeriodDiscoveryError: If git repository not found or analysis fails
        """
        # Validate repository exists
        if not self.repo_path.exists():
            raise PeriodDiscoveryError(
                f"Git repository not found at {self.repo_path}. "
                "Expected ~/.claude-memories to exist."
            )

        if not (self.repo_path / ".git").exists():
            raise PeriodDiscoveryError(
                f"Directory {self.repo_path} is not a git repository."
            )

        # Extract agent configuration changes from git log
        changes = self._extract_config_changes(start_date, end_date)

        if not changes:
            raise PeriodDiscoveryError(
                "No agent configuration changes found in git history. "
                "Try expanding date range or check repository content."
            )

        # Build period definitions from changes
        periods = self._build_periods_from_changes(changes)

        return periods

    def _extract_config_changes(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[PeriodChange]:
        """Extract configuration changes from git log.

        Args:
            start_date: Start date for search
            end_date: End date for search

        Returns:
            List of PeriodChange objects
        """
        # Build git log command
        cmd = [
            "git", "log", "--all",
            "--format=%ai|%H|%s",
            "--reverse"  # Chronological order
        ]

        if start_date:
            cmd.append(f"--since={start_date}")
        if end_date:
            cmd.append(f"--until={end_date}")

        # Execute git log
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise PeriodDiscoveryError(f"Git log command failed: {e.stderr}")

        # Parse commits for agent-related changes
        changes = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            # Look for agent-related commits
            if not self._is_agent_related(line):
                continue

            parts = line.split('|', maxsplit=2)
            if len(parts) != 3:
                continue

            date_str, commit_hash, message = parts

            # Extract date (YYYY-MM-DD)
            date = date_str.split()[0]

            # Parse changes from commit message
            change_list = self._parse_changes(message)

            if change_list:
                changes.append(PeriodChange(
                    date=date,
                    commit_hash=commit_hash[:8],
                    message=message.strip(),
                    changes=change_list
                ))

        return changes

    def _is_agent_related(self, line: str) -> bool:
        """Check if git log line is agent-related.

        Args:
            line: Git log line to check

        Returns:
            True if line contains agent-related keywords
        """
        keywords = [
            "agent", "Agent",
            "restructur", "Restructur",
            "mandatory", "Mandatory",
            "delegation", "Delegation",
            "specialist", "Specialist",
            "developer", "Developer",
            "architect", "Architect"
        ]
        return any(keyword in line for keyword in keywords)

    def _parse_changes(self, message: str) -> List[str]:
        """Parse configuration changes from commit message.

        Args:
            message: Git commit message

        Returns:
            List of changes extracted from message
        """
        changes = []

        # Common patterns
        patterns = {
            "add": r"add|Add|new|New|\+",
            "remove": r"remove|Remove|delete|Delete|-",
            "update": r"update|Update|modify|Modify|change|Change",
            "restructure": r"restructur|Restructur|split|Split",
            "policy": r"mandatory|Mandatory|policy|Policy"
        }

        message_lower = message.lower()

        # Detect specific agents
        agents = [
            "solution-architect", "project-framer", "backlog-manager",
            "developer", "senior-developer", "junior-developer",
            "refactoring-specialist", "integration-specialist",
            "performance-optimizer", "content-developer",
            "ux-specialist", "graphics-specialist", "game-designer",
            "git-workflow-manager", "parallel-worktree-framework"
        ]

        for agent in agents:
            if agent in message_lower:
                # Determine action
                action = "config"
                if any(p in message_lower for p in ["add", "new", "+"]):
                    action = f"+{agent}"
                elif any(p in message_lower for p in ["remove", "delete", "-"]):
                    action = f"-{agent}"
                elif "split" in message_lower or "restructur" in message_lower:
                    action = f"restructure {agent}"
                else:
                    action = f"update {agent}"

                changes.append(action)

        # Detect policies
        if any(word in message_lower for word in ["mandatory", "policy", "required"]):
            if "delegation" in message_lower:
                changes.append("Mandatory delegation policy")

        # Detect restructuring
        if any(word in message_lower for word in ["restructur", "split", "reorganiz"]):
            changes.append("System restructuring")

        # Use message as fallback if no specific changes detected
        if not changes:
            changes.append(message.strip())

        return changes

    def _build_periods_from_changes(
        self,
        changes: List[PeriodChange]
    ) -> Dict[str, Dict]:
        """Build period definitions from configuration changes.

        Only creates periods for MAJOR architectural changes, not every commit.

        Args:
            changes: List of configuration changes

        Returns:
            Dictionary of period definitions
        """
        if not changes:
            return {}

        # Filter to major changes only
        major_changes = self._filter_major_changes(changes)

        if not major_changes:
            # No major changes found, return fallback
            logger.warning("No major configuration changes found in git history")
            return self._get_fallback_periods()

        periods = {}

        # Group changes by date to avoid creating multiple periods per day
        changes_by_date = {}
        for change in major_changes:
            if change.date not in changes_by_date:
                changes_by_date[change.date] = []
            changes_by_date[change.date].append(change)

        # Create periods from grouped changes
        sorted_dates = sorted(changes_by_date.keys())

        for i, date in enumerate(sorted_dates):
            period_id = f"P{i + 1}"
            day_changes = changes_by_date[date]

            # Combine all changes for this day
            all_changes = []
            all_messages = []
            for change in day_changes:
                all_changes.extend(change.changes)
                all_messages.append(change.message)

            # Determine period end
            if i < len(sorted_dates) - 1:
                next_date = sorted_dates[i + 1]
                end_date = self._subtract_day(next_date)
            else:
                # Last period - use 30 days after or end of analysis period
                end_date = self._add_days(date, 30)

            # Create combined change object for naming
            combined_change = PeriodChange(
                date=date,
                commit_hash=day_changes[0].commit_hash,
                message=" | ".join(all_messages),
                changes=all_changes
            )

            # Create period definition
            periods[period_id] = {
                "name": self._generate_period_name(combined_change),
                "start": date,
                "end": end_date,
                "changes": all_changes,
                "description": " | ".join(all_messages),
                "commit": day_changes[0].commit_hash
            }

        return periods

    def _filter_major_changes(self, changes: List[PeriodChange]) -> List[PeriodChange]:
        """Filter to only major architectural changes.

        Major changes are:
        - System launch (initial agent definitions)
        - Adding/removing specialist agents (solution-architect, etc.)
        - System restructuring (developer → senior/junior split)
        - Policy changes (mandatory delegation)
        - Framework additions (parallel-worktree-framework)

        Args:
            changes: All configuration changes

        Returns:
            Filtered list of major changes only
        """
        major = []

        major_agents = [
            "solution-architect", "project-framer",
            "senior-developer", "junior-developer",
            "refactoring-specialist", "integration-specialist",
            "content-developer", "performance-optimizer",
            "parallel-worktree-framework"
        ]

        major_keywords = [
            "mandatory delegation",
            "restructur", "split",
            "policy",
            # System launch keywords
            "global agent definitions",
            "add global agent",
            "initial agents"
        ]

        for change in changes:
            # Check if involves major agents
            is_major = False

            for agent in major_agents:
                if any(agent in c.lower() for c in change.changes):
                    is_major = True
                    break

            # Check for major keywords in changes or message
            if not is_major:
                all_text = " ".join(change.changes) + " " + change.message
                for keyword in major_keywords:
                    if keyword.lower() in all_text.lower():
                        is_major = True
                        break

            if is_major:
                major.append(change)

        return major

    def _generate_period_name(self, change: PeriodChange) -> str:
        """Generate a descriptive period name from changes.

        Args:
            change: Period change information

        Returns:
            Descriptive period name
        """
        all_text = " ".join(change.changes) + " " + change.message

        # Check for launch/initial period
        if any(keyword in all_text.lower() for keyword in ["global agent definitions", "add global agent", "initial agents"]):
            return "Launch + Vacances"

        # Extract key agents/concepts
        if any("solution-architect" in c.lower() for c in change.changes):
            return "Conception Added"
        elif any("mandatory" in c.lower() for c in change.changes):
            if any("delegation" in c.lower() for c in change.changes):
                return "Délégation Obligatoire"
            return "Mandatory Delegation"
        elif any("restructur" in c.lower() or "split" in c.lower() for c in change.changes):
            return "Post-Restructuration"
        elif any("senior" in c.lower() or "junior" in c.lower() for c in change.changes):
            return "Developer Split"
        else:
            # Use first change as name
            if change.changes:
                return change.changes[0].replace("+", "Add ").replace("-", "Remove ")
            return "Configuration Update"

    def _subtract_day(self, date_str: str) -> str:
        """Subtract one day from ISO date string.

        Args:
            date_str: ISO format date (YYYY-MM-DD)

        Returns:
            Date minus one day
        """
        from datetime import timedelta
        date_obj = datetime.fromisoformat(date_str)
        prev_day = date_obj - timedelta(days=1)
        return prev_day.strftime("%Y-%m-%d")

    def _add_days(self, date_str: str, days: int) -> str:
        """Add days to ISO date string.

        Args:
            date_str: ISO format date (YYYY-MM-DD)
            days: Number of days to add

        Returns:
            Date plus specified days
        """
        from datetime import timedelta
        date_obj = datetime.fromisoformat(date_str)
        new_date = date_obj + timedelta(days=days)
        return new_date.strftime("%Y-%m-%d")

    def _get_fallback_periods(self) -> Dict[str, Dict]:
        """Get hardcoded fallback periods when git discovery fails.

        Returns:
            Dictionary of fallback period definitions
        """
        # Import from config to avoid circular dependency
        from . import config

        logger.info("Using fallback period definitions from config.py")
        return config.PERIOD_DEFINITIONS

    def _load_cache(self) -> Optional[Dict[str, Dict]]:
        """Load cached period definitions if fresh.

        Returns:
            Cached periods if available and fresh, None otherwise
        """
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check cache freshness
            cached_at = datetime.fromisoformat(cache_data.get('cached_at', ''))
            now = datetime.now()
            age_hours = (now - cached_at).total_seconds() / 3600

            if age_hours < self.cache_ttl_hours:
                logger.debug(f"Cache is {age_hours:.1f}h old (< {self.cache_ttl_hours}h TTL)")
                return cache_data.get('periods')
            else:
                logger.debug(f"Cache expired ({age_hours:.1f}h old)")
                return None

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    def _save_cache(self, periods: Dict[str, Dict]) -> None:
        """Save discovered periods to cache.

        Args:
            periods: Period definitions to cache
        """
        # Ensure cache directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'ttl_hours': self.cache_ttl_hours,
            'periods': periods
        }

        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            logger.debug(f"Cached periods to {self.cache_file}")
        except IOError as e:
            logger.warning(f"Failed to save cache: {e}")

    def invalidate_cache(self) -> None:
        """Invalidate cached periods by deleting cache file."""
        if self.cache_file.exists():
            self.cache_file.unlink()
            logger.info("Cache invalidated")


# Convenience function for quick access
def get_periods(
    use_git: bool = False,
    use_cache: bool = True,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Dict]:
    """Get period definitions (convenience function).

    Args:
        use_git: If True, discover from git; if False, use fallback
        use_cache: If True, use cached periods if available
        start_date: Start date for git search (ISO format)
        end_date: End date for git search (ISO format)

    Returns:
        Dictionary of period definitions
    """
    builder = PeriodBuilder()
    return builder.discover_periods(
        use_git=use_git,
        use_cache=use_cache,
        start_date=start_date,
        end_date=end_date
    )


if __name__ == "__main__":
    # Demo/testing
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    print("=== Period Builder Demo ===\n")

    # Test fallback (safe default)
    print("1. Testing fallback periods (use_git=False)...")
    periods = get_periods(use_git=False)
    print(f"   Found {len(periods)} periods:")
    for pid, pdata in periods.items():
        print(f"   - {pid}: {pdata['name']} ({pdata['start']} to {pdata['end']})")

    print("\n2. Testing git discovery (use_git=True)...")
    try:
        periods_git = get_periods(use_git=True)
        print(f"   Found {len(periods_git)} periods from git:")
        for pid, pdata in periods_git.items():
            print(f"   - {pid}: {pdata['name']} ({pdata['start']} to {pdata['end']})")
            print(f"     Changes: {', '.join(pdata['changes'])}")
    except PeriodDiscoveryError as e:
        print(f"   Git discovery failed: {e}")
        print("   This is expected if ~/.claude-memories doesn't exist")

    print("\n✅ Demo complete")
