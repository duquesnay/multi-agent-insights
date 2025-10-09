"""Unit tests for PeriodBuilder logic.

Tests period discovery, filtering, and naming without git dependency.
"""

import pytest
from pathlib import Path
from tools.common.period_builder import (
    PeriodBuilder,
    PeriodChange,
    PeriodDiscoveryError,
    get_periods
)


@pytest.mark.unit
class TestPeriodChange:
    """Test PeriodChange dataclass."""

    def test_create_period_change(self):
        """Should create PeriodChange with all fields."""
        change = PeriodChange(
            date='2025-09-12',
            commit_hash='abc123',
            message='Add mandatory delegation',
            changes=['+content-developer', 'Mandatory delegation policy']
        )

        assert change.date == '2025-09-12'
        assert change.commit_hash == 'abc123'
        assert len(change.changes) == 2


@pytest.mark.unit
class TestPeriodBuilderLogic:
    """Test PeriodBuilder business logic without git."""

    def test_parse_changes_detects_agents(self):
        """Should extract agent names from commit messages."""
        builder = PeriodBuilder()

        message = "Add solution-architect and project-framer agents"
        changes = builder._parse_changes(message)

        assert any('solution-architect' in c for c in changes)
        assert any('project-framer' in c for c in changes)

    def test_parse_changes_detects_actions(self):
        """Should detect add/remove/update actions."""
        builder = PeriodBuilder()

        # Add action
        message = "Add new refactoring-specialist agent"
        changes = builder._parse_changes(message)
        assert any('+refactoring-specialist' in c for c in changes)

        # Restructure action
        message = "Restructure developer into senior and junior"
        changes = builder._parse_changes(message)
        assert any('restructur' in c.lower() for c in changes)

    def test_parse_changes_detects_policies(self):
        """Should detect policy changes."""
        builder = PeriodBuilder()

        message = "Implement mandatory delegation policy"
        changes = builder._parse_changes(message)

        assert any('mandatory' in c.lower() for c in changes)
        assert any('delegation' in c.lower() for c in changes)

    def test_is_agent_related_filters_correctly(self):
        """Should identify agent-related commits."""
        builder = PeriodBuilder()

        # Agent-related
        assert builder._is_agent_related("Add solution-architect agent") is True
        assert builder._is_agent_related("Mandatory delegation policy") is True
        assert builder._is_agent_related("Restructure developer") is True

        # Not agent-related
        assert builder._is_agent_related("Fix typo in README") is False
        assert builder._is_agent_related("Update dependencies") is False

    def test_filter_major_changes(self):
        """Should filter to only major architectural changes."""
        builder = PeriodBuilder()

        changes = [
            PeriodChange(
                date='2025-09-03',
                commit_hash='abc1',
                message='Add solution-architect',
                changes=['+solution-architect']
            ),
            PeriodChange(
                date='2025-09-05',
                commit_hash='abc2',
                message='Fix typo',
                changes=['typo fix']
            ),
            PeriodChange(
                date='2025-09-12',
                commit_hash='abc3',
                message='Mandatory delegation',
                changes=['Mandatory delegation policy']
            ),
        ]

        major = builder._filter_major_changes(changes)

        # Should keep solution-architect and mandatory delegation
        # Should filter out typo fix
        assert len(major) == 2
        assert any('solution-architect' in c.changes[0] for c in major)
        assert any('Mandatory' in c.changes[0] for c in major)

    def test_generate_period_name(self):
        """Should generate descriptive names from changes."""
        builder = PeriodBuilder()

        # Solution-architect period
        change = PeriodChange(
            date='2025-09-03',
            commit_hash='abc1',
            message='Add solution-architect',
            changes=['+solution-architect', '+project-framer']
        )
        assert 'Conception' in builder._generate_period_name(change)

        # Mandatory delegation period
        change = PeriodChange(
            date='2025-09-12',
            commit_hash='abc2',
            message='Implement mandatory delegation',
            changes=['Mandatory delegation policy']
        )
        name = builder._generate_period_name(change)
        assert 'Mandatory' in name or 'Délégation' in name

        # Restructuring period
        change = PeriodChange(
            date='2025-09-21',
            commit_hash='abc3',
            message='Split developer into senior/junior',
            changes=['restructure developer', '+senior-developer']
        )
        name = builder._generate_period_name(change)
        assert 'Restructur' in name or 'Split' in name

    def test_subtract_day(self):
        """Should subtract one day from date."""
        builder = PeriodBuilder()

        result = builder._subtract_day('2025-09-15')
        assert result == '2025-09-14'

        # Month boundary
        result = builder._subtract_day('2025-09-01')
        assert result == '2025-08-31'

    def test_add_days(self):
        """Should add days to date."""
        builder = PeriodBuilder()

        result = builder._add_days('2025-09-15', 5)
        assert result == '2025-09-20'

        # Month boundary
        result = builder._add_days('2025-09-28', 5)
        assert result == '2025-10-03'

    def test_build_periods_from_changes(self):
        """Should build period definitions from change list."""
        builder = PeriodBuilder()

        changes = [
            PeriodChange(
                date='2025-09-03',
                commit_hash='abc1',
                message='Add solution-architect',
                changes=['+solution-architect']
            ),
            PeriodChange(
                date='2025-09-12',
                commit_hash='abc2',
                message='Mandatory delegation',
                changes=['Mandatory delegation policy']
            ),
        ]

        periods = builder._build_periods_from_changes(changes)

        # Should create 2 periods
        assert len(periods) >= 2

        # Should have period IDs
        period_ids = list(periods.keys())
        assert 'P1' in period_ids or 'P2' in period_ids

        # Each period should have required fields
        for period_id, period_data in periods.items():
            assert 'name' in period_data
            assert 'start' in period_data
            assert 'end' in period_data
            assert 'changes' in period_data

    def test_fallback_periods_when_no_major_changes(self):
        """Should use fallback when no major changes found."""
        builder = PeriodBuilder()

        # Only minor changes
        changes = [
            PeriodChange(
                date='2025-09-05',
                commit_hash='abc1',
                message='Fix typo',
                changes=['typo fix']
            ),
        ]

        periods = builder._build_periods_from_changes(changes)

        # Should use fallback from config
        assert len(periods) > 0
        # Fallback periods have P2, P3, P4
        assert any(pid in periods for pid in ['P2', 'P3', 'P4'])


@pytest.mark.unit
class TestPeriodBuilderFallback:
    """Test fallback period behavior."""

    def test_use_git_false_returns_fallback(self):
        """When use_git=False, should use fallback periods."""
        builder = PeriodBuilder()

        periods = builder.discover_periods(use_git=False)

        assert len(periods) > 0
        # Fallback has standard periods
        assert 'P2' in periods or 'P3' in periods or 'P4' in periods

    def test_fallback_periods_have_required_structure(self):
        """Fallback periods should have all required fields."""
        builder = PeriodBuilder()

        periods = builder.discover_periods(use_git=False)

        for period_id, period_data in periods.items():
            assert 'name' in period_data
            assert 'start' in period_data
            assert 'end' in period_data
            assert 'changes' in period_data
            assert isinstance(period_data['changes'], list)

    def test_convenience_function_works(self):
        """get_periods() convenience function should work."""
        periods = get_periods(use_git=False)

        assert isinstance(periods, dict)
        assert len(periods) > 0


@pytest.mark.unit
class TestPeriodBuilderCache:
    """Test caching behavior (without actual file I/O)."""

    def test_cache_file_path_default(self):
        """Should use default cache file path."""
        builder = PeriodBuilder()

        assert builder.cache_file.name == '.period_cache.json'
        assert 'data' in str(builder.cache_file)

    def test_custom_cache_file_path(self, tmp_path: Path):
        """Should accept custom cache file path."""
        custom_cache = tmp_path / "custom_cache.json"
        builder = PeriodBuilder(cache_file=custom_cache)

        assert builder.cache_file == custom_cache

    def test_cache_ttl_hours_configurable(self):
        """Should allow custom cache TTL."""
        builder = PeriodBuilder(cache_ttl_hours=48)

        assert builder.cache_ttl_hours == 48


@pytest.mark.unit
class TestPeriodBuilderErrors:
    """Test error handling."""

    def test_nonexistent_repo_raises_error(self, tmp_path: Path):
        """Should raise error when git repo doesn't exist."""
        nonexistent = tmp_path / "nonexistent"
        builder = PeriodBuilder(repo_path=nonexistent)

        with pytest.raises(PeriodDiscoveryError) as exc_info:
            builder._discover_from_git()

        assert "not found" in str(exc_info.value).lower()

    def test_non_git_directory_raises_error(self, tmp_path: Path):
        """Should raise error when directory is not a git repo."""
        not_git_repo = tmp_path / "not_git"
        not_git_repo.mkdir()

        builder = PeriodBuilder(repo_path=not_git_repo)

        with pytest.raises(PeriodDiscoveryError) as exc_info:
            builder._discover_from_git()

        assert "not a git repository" in str(exc_info.value).lower()
