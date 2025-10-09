"""Integration tests for DataRepository with real data files.

Following CLAUDE.md guidelines:
- Integration tests use REAL data (no mocks)
- Test actual file loading and data structure
- Validate end-to-end data pipeline
"""

import pytest
from pathlib import Path
from tools.common.data_repository import (
    DataRepository,
    load_delegations,
    load_sessions,
    stream_delegations,
    stream_sessions,
    DataLoadError
)
from tools.common.models import Delegation, Session


@pytest.mark.integration
class TestDataRepositoryIntegration:
    """Integration tests using real enriched sessions data."""

    def test_load_enriched_delegations_returns_data(self, data_dir: Path):
        """Should load delegations from real enriched sessions file."""
        repo = DataRepository(base_path=data_dir.parent)

        delegations = repo.load_delegations(source='enriched')

        assert delegations is not None
        assert isinstance(delegations, list)
        assert len(delegations) > 0, "Should have delegations in enriched data"

        # Verify structure
        first = delegations[0]
        assert 'session_id' in first
        assert 'agent_type' in first
        assert 'timestamp' in first

    def test_load_enriched_delegations_typed(self, data_dir: Path):
        """Should load typed Delegation objects from enriched data."""
        repo = DataRepository(base_path=data_dir.parent)

        delegations = repo.load_delegations(source='enriched', typed=True)

        assert delegations is not None
        assert isinstance(delegations, list)
        assert len(delegations) > 0

        # Verify typed object
        first = delegations[0]
        assert isinstance(first, Delegation)
        assert hasattr(first, 'agent_type')
        assert hasattr(first, 'total_tokens')

        # Business logic works
        total = first.total_tokens()
        assert total >= 0

    def test_load_sessions_returns_data(self, data_dir: Path):
        """Should load sessions from real enriched sessions file."""
        repo = DataRepository(base_path=data_dir.parent)

        sessions = repo.load_sessions(enriched=True)

        assert sessions is not None
        assert isinstance(sessions, list)
        assert len(sessions) > 0, "Should have sessions in data"

        # Verify structure
        first = sessions[0]
        assert 'session_id' in first
        assert 'delegations' in first
        assert isinstance(first['delegations'], list)

    def test_load_sessions_typed(self, data_dir: Path):
        """Should load typed Session objects."""
        repo = DataRepository(base_path=data_dir.parent)

        sessions = repo.load_sessions(enriched=True, typed=True)

        assert sessions is not None
        assert len(sessions) > 0

        # Verify typed object
        first = sessions[0]
        assert isinstance(first, Session)
        assert hasattr(first, 'session_id')
        assert hasattr(first, 'delegations')

        # Business logic works
        assert isinstance(first.delegations, list)
        if first.delegations:
            assert isinstance(first.delegations[0], Delegation)

    def test_enriched_delegations_have_session_context(self, data_dir: Path):
        """Enriched delegations should include session metadata."""
        repo = DataRepository(base_path=data_dir.parent)

        delegations = repo.load_delegations(source='enriched')

        # All delegations should have session_id
        for deleg in delegations[:10]:  # Check first 10
            assert 'session_id' in deleg, "Delegation missing session_id"
            assert deleg['session_id'], "session_id should not be empty"

    def test_cache_mechanism_works(self, data_dir: Path):
        """Should cache loaded data and reuse on subsequent calls."""
        repo = DataRepository(base_path=data_dir.parent)

        # First load (from file)
        delegations1 = repo.load_delegations(source='enriched', use_cache=True)

        # Second load (from cache)
        delegations2 = repo.load_delegations(source='enriched', use_cache=True)

        # Should be the same object (cached)
        assert delegations1 is delegations2

        # Clear cache and reload
        repo.clear_cache()
        delegations3 = repo.load_delegations(source='enriched', use_cache=True)

        # Should be different object (reloaded)
        assert delegations1 is not delegations3
        assert len(delegations1) == len(delegations3)

    def test_load_nonexistent_file_raises_error(self):
        """Should raise DataLoadError when file doesn't exist."""
        repo = DataRepository(base_path=Path("/nonexistent/path"))

        with pytest.raises(DataLoadError) as exc_info:
            repo.load_delegations(source='enriched')

        assert "not found" in str(exc_info.value).lower()

    def test_stream_sessions_yields_sessions(self, data_dir: Path):
        """Should stream sessions one at a time."""
        repo = DataRepository(base_path=data_dir.parent)

        sessions_streamed = []
        for session in repo.stream_sessions():
            sessions_streamed.append(session)
            if len(sessions_streamed) >= 5:  # Test first 5
                break

        assert len(sessions_streamed) == 5
        assert all('session_id' in s for s in sessions_streamed)

    def test_stream_delegations_yields_delegations(self, data_dir: Path):
        """Should stream delegations one at a time."""
        repo = DataRepository(base_path=data_dir.parent)

        delegations_streamed = []
        for deleg in repo.stream_delegations():
            delegations_streamed.append(deleg)
            if len(delegations_streamed) >= 10:  # Test first 10
                break

        assert len(delegations_streamed) == 10
        assert all('agent_type' in d for d in delegations_streamed)

    def test_stream_with_filter_applies_filter(self, data_dir: Path):
        """Should filter delegations during streaming."""
        repo = DataRepository(base_path=data_dir.parent)

        # Filter for specific agent
        target_agent = 'developer'
        filtered = []

        for deleg in repo.stream_delegations(filter_func=lambda d: d.get('agent_type') == target_agent):
            filtered.append(deleg)
            if len(filtered) >= 5:
                break

        # All should match filter
        assert all(d['agent_type'] == target_agent for d in filtered)


@pytest.mark.integration
class TestConvenienceFunctions:
    """Test convenience functions for backward compatibility."""

    def test_load_delegations_function(self, data_dir: Path):
        """Convenience function should work like repository method."""
        # Note: This uses global repository, so we can't control base_path
        # Test will skip if data not in expected location

        try:
            delegations = load_delegations(source='enriched')
            assert isinstance(delegations, list)
            assert len(delegations) > 0
        except DataLoadError:
            pytest.skip("Data not in default location for global repository")

    def test_load_sessions_function(self, data_dir: Path):
        """Convenience function for sessions should work."""
        try:
            sessions = load_sessions(enriched=True)
            assert isinstance(sessions, list)
            assert len(sessions) > 0
        except DataLoadError:
            pytest.skip("Data not in default location for global repository")

    def test_stream_functions_work(self, data_dir: Path):
        """Streaming convenience functions should work."""
        try:
            # Get first session via streaming
            first_session = next(stream_sessions())
            assert 'session_id' in first_session

            # Get first delegation via streaming
            first_deleg = next(stream_delegations())
            assert 'agent_type' in first_deleg
        except (DataLoadError, StopIteration):
            pytest.skip("Data not available for streaming test")


@pytest.mark.integration
class TestDataValidation:
    """Validate structure and content of real data."""

    def test_all_sessions_have_required_fields(self, enriched_sessions_data: dict):
        """All sessions should have required fields."""
        sessions = enriched_sessions_data.get('sessions', [])

        for session in sessions[:20]:  # Check first 20
            assert 'session_id' in session
            assert 'delegations' in session
            assert isinstance(session['delegations'], list)

    def test_all_delegations_have_agent_type(self, enriched_sessions_data: dict):
        """All delegations should specify an agent type."""
        sessions = enriched_sessions_data.get('sessions', [])

        for session in sessions[:10]:
            for deleg in session.get('delegations', []):
                assert 'agent_type' in deleg
                assert deleg['agent_type'], "agent_type should not be empty"

    def test_delegations_have_valid_timestamps(self, enriched_sessions_data: dict):
        """All delegations should have valid ISO timestamps."""
        from datetime import datetime

        sessions = enriched_sessions_data.get('sessions', [])

        for session in sessions[:10]:
            for deleg in session.get('delegations', []):
                timestamp = deleg.get('timestamp')
                assert timestamp, "Missing timestamp"

                # Should parse as ISO datetime
                parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                assert isinstance(parsed, datetime)

    def test_token_counts_are_nonnegative(self, enriched_sessions_data: dict):
        """Token counts should be non-negative integers."""
        sessions = enriched_sessions_data.get('sessions', [])

        for session in sessions[:10]:
            for deleg in session.get('delegations', []):
                tokens_in = deleg.get('tokens_in', 0)
                tokens_out = deleg.get('tokens_out', 0)

                assert tokens_in >= 0, f"Negative input tokens: {tokens_in}"
                assert tokens_out >= 0, f"Negative output tokens: {tokens_out}"
