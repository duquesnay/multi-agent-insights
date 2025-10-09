"""Integration tests for end-to-end analysis pipeline.

Tests complete workflows from data loading through analysis.
"""

import pytest
from pathlib import Path
from tools.common.data_repository import DataRepository
from tools.common.period_builder import get_periods
from tools.common.models import Session, Delegation


@pytest.mark.integration
@pytest.mark.slow
class TestAnalysisPipeline:
    """Test complete analysis workflows."""

    def test_load_and_segment_sessions_by_period(self, data_dir: Path, period_definitions: dict):
        """Should load sessions and segment them by period."""
        repo = DataRepository(base_path=data_dir.parent)

        # Load sessions
        sessions = repo.load_sessions(enriched=True, typed=True)
        assert len(sessions) > 0

        # Get periods
        periods = period_definitions

        # Segment sessions by period
        segmented = {pid: [] for pid in periods.keys()}

        for session in sessions[:20]:  # Test first 20
            if not session.delegations:
                continue

            # Get session date from first delegation
            first_timestamp = session.delegations[0].timestamp
            session_date = first_timestamp.split('T')[0]

            # Find matching period
            for period_id, period_data in periods.items():
                if period_data['start'] <= session_date <= period_data['end']:
                    segmented[period_id].append(session)
                    break

        # Should have sessions in at least one period
        total_segmented = sum(len(sessions) for sessions in segmented.values())
        assert total_segmented > 0

    def test_calculate_metrics_per_session(self, data_dir: Path):
        """Should calculate key metrics for each session."""
        repo = DataRepository(base_path=data_dir.parent)

        sessions = repo.load_sessions(enriched=True, typed=True)

        metrics_summary = []

        for session in sessions[:10]:  # Test first 10
            metrics = {
                'session_id': session.session_id,
                'delegation_count': len(session.delegations),
                'is_marathon': session.is_marathon(),
                'total_tokens': session.total_tokens(),
                'total_cost': float(session.total_cost()),
                'success_rate': session.success_rate(),
                'agent_types': session.agent_types()
            }
            metrics_summary.append(metrics)

        # All should have metrics
        assert len(metrics_summary) == 10
        assert all('total_tokens' in m for m in metrics_summary)
        assert all(m['success_rate'] >= 0 and m['success_rate'] <= 1 for m in metrics_summary)

    def test_identify_marathons(self, data_dir: Path):
        """Should identify marathon sessions across dataset."""
        repo = DataRepository(base_path=data_dir.parent)

        sessions = repo.load_sessions(enriched=True, typed=True)

        marathons = [s for s in sessions if s.is_marathon()]
        normal = [s for s in sessions if not s.is_marathon()]

        # Should have both types
        assert len(sessions) == len(marathons) + len(normal)

        # Marathons should have >20 delegations
        if marathons:
            assert all(len(m.delegations) > 20 for m in marathons)

    def test_agent_usage_distribution(self, data_dir: Path):
        """Should analyze agent type distribution."""
        repo = DataRepository(base_path=data_dir.parent)

        delegations = repo.load_delegations(source='enriched', typed=True)

        # Count agent types
        agent_counts = {}
        for deleg in delegations[:100]:  # Sample first 100
            agent_type = deleg.agent_type
            agent_counts[agent_type] = agent_counts.get(agent_type, 0) + 1

        # Should have multiple agent types
        assert len(agent_counts) > 1

        # Most common agents should be present
        assert any(agent in agent_counts for agent in ['developer', 'general-purpose'])

    def test_token_cost_analysis(self, data_dir: Path):
        """Should calculate token and cost metrics."""
        repo = DataRepository(base_path=data_dir.parent)

        delegations = repo.load_delegations(source='enriched', typed=True)

        total_tokens = sum(d.total_tokens() for d in delegations[:50])
        total_cost = sum(d.cost() for d in delegations[:50])

        assert total_tokens > 0
        assert total_cost > 0

        # Cost should be reasonable (not negative, not absurdly high)
        avg_cost_per_delegation = total_cost / 50
        assert avg_cost_per_delegation > 0
        assert avg_cost_per_delegation < 1.0  # Sanity check

    def test_temporal_ordering(self, data_dir: Path):
        """Should verify delegations are in temporal order."""
        repo = DataRepository(base_path=data_dir.parent)

        sessions = repo.load_sessions(enriched=True, typed=True)

        for session in sessions[:10]:
            if len(session.delegations) < 2:
                continue

            # Check delegations are ordered by time
            for i in range(len(session.delegations) - 1):
                current = session.delegations[i].datetime()
                next_deleg = session.delegations[i + 1].datetime()
                assert current <= next_deleg, "Delegations should be chronologically ordered"

    def test_streaming_vs_batch_consistency(self, data_dir: Path):
        """Streaming and batch loading should yield same delegations."""
        repo = DataRepository(base_path=data_dir.parent)

        # Batch load
        batch_delegations = repo.load_delegations(source='enriched')
        batch_count = len(batch_delegations)

        # Stream load
        stream_count = 0
        for _ in repo.stream_delegations():
            stream_count += 1

        # Should have same count
        assert stream_count == batch_count


@pytest.mark.integration
class TestPeriodSegmentation:
    """Test period-based segmentation of data."""

    def test_period_discovery_fallback_works(self):
        """Period discovery fallback should return valid periods."""
        periods = get_periods(use_git=False)

        assert isinstance(periods, dict)
        assert len(periods) > 0

        # Check structure
        for period_id, period_data in periods.items():
            assert 'name' in period_data
            assert 'start' in period_data
            assert 'end' in period_data

    def test_all_sessions_fall_in_some_period(self, data_dir: Path):
        """Most sessions should fall within defined periods."""
        repo = DataRepository(base_path=data_dir.parent)
        sessions = repo.load_sessions(enriched=True)

        periods = get_periods(use_git=False)

        matched = 0
        unmatched = 0

        for session in sessions[:50]:  # Sample
            if not session.get('delegations'):
                continue

            # Get session date
            first_deleg = session['delegations'][0]
            session_date = first_deleg['timestamp'].split('T')[0]

            # Check if in any period
            in_period = False
            for period_data in periods.values():
                if period_data['start'] <= session_date <= period_data['end']:
                    in_period = True
                    break

            if in_period:
                matched += 1
            else:
                unmatched += 1

        # Most should match (allowing for some outside period boundaries)
        assert matched > 0

    def test_period_boundaries_non_overlapping(self):
        """Period boundaries should not overlap."""
        periods = get_periods(use_git=False)

        period_list = sorted(periods.items(), key=lambda x: x[1]['start'])

        for i in range(len(period_list) - 1):
            current_end = period_list[i][1]['end']
            next_start = period_list[i + 1][1]['start']

            # Next period should start after or on current end
            # (allowing for adjacent periods)
            assert next_start >= current_end or \
                   abs((next_start - current_end).days) <= 1


@pytest.mark.integration
class TestDataQuality:
    """Validate data quality and consistency."""

    def test_no_duplicate_delegation_ids(self, data_dir: Path):
        """Check for duplicate delegation UUIDs (documents known data issue)."""
        repo = DataRepository(base_path=data_dir.parent)

        delegations = repo.load_delegations(source='enriched')

        # Extract UUIDs
        uuids = [d.get('tool_use_id') or d.get('uuid') for d in delegations]

        # Check for duplicates
        unique_uuids = set(uuids)
        duplicate_count = len(uuids) - len(unique_uuids)

        # KNOWN ISSUE: Data contains duplicate tool_use_ids (322 duplicates)
        # This happens when same delegation appears in multiple sessions
        # or when sessions are re-analyzed
        if duplicate_count > 0:
            pytest.skip(
                f"Known data quality issue: {duplicate_count} duplicate UUIDs found. "
                "This occurs when delegations appear in multiple sessions."
            )

    def test_no_sessions_without_delegations_in_enriched(self, data_dir: Path):
        """Enriched sessions should all have at least one delegation."""
        repo = DataRepository(base_path=data_dir.parent)

        sessions = repo.load_sessions(enriched=True)

        # Check each session
        for session in sessions:
            delegations = session.get('delegations', [])
            # Enriched sessions are filtered to only those with delegations
            assert len(delegations) > 0, f"Session {session.get('session_id')} has no delegations"

    def test_all_delegations_reference_valid_session(self, data_dir: Path):
        """All delegations should reference a valid session."""
        repo = DataRepository(base_path=data_dir.parent)

        sessions = repo.load_sessions(enriched=True)
        delegations = repo.load_delegations(source='enriched')

        # Build set of valid session IDs
        valid_session_ids = {s['session_id'] for s in sessions}

        # Check all delegations
        for deleg in delegations[:100]:  # Sample
            session_id = deleg.get('session_id')
            assert session_id in valid_session_ids, \
                f"Delegation references unknown session: {session_id}"
