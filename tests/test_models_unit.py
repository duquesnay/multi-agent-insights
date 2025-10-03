"""Unit tests for domain models (common/models.py).

Following CLAUDE.md guidelines:
- Unit tests isolate business logic
- Test validation, calculations, and conversions
- No external dependencies
"""

import pytest
from decimal import Decimal
from datetime import datetime
from common.models import (
    TokenMetrics,
    Delegation,
    Session,
    Period,
    AgentCall,
    ValidationError
)


@pytest.mark.unit
class TestTokenMetrics:
    """Test TokenMetrics entity and business logic."""

    def test_create_token_metrics(self):
        """Should create TokenMetrics with valid data."""
        metrics = TokenMetrics(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=200,
            cache_read_tokens=5000
        )

        assert metrics.input_tokens == 1000
        assert metrics.output_tokens == 500
        assert metrics.cache_creation_tokens == 200
        assert metrics.cache_read_tokens == 5000

    def test_token_metrics_immutable(self):
        """TokenMetrics should be immutable (frozen dataclass)."""
        metrics = TokenMetrics(input_tokens=100, output_tokens=50)

        with pytest.raises(AttributeError):
            metrics.input_tokens = 200

    def test_negative_tokens_raise_validation_error(self):
        """Should reject negative token counts."""
        with pytest.raises(ValidationError):
            TokenMetrics(input_tokens=-1, output_tokens=500)

        with pytest.raises(ValidationError):
            TokenMetrics(input_tokens=100, output_tokens=-50)

    def test_total_tokens_calculation(self):
        """Should sum all token types correctly."""
        metrics = TokenMetrics(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=200,
            cache_read_tokens=3000
        )

        assert metrics.total_tokens() == 4700

    def test_total_cost_calculation(self):
        """Should calculate cost based on Claude pricing."""
        metrics = TokenMetrics(
            input_tokens=1_000_000,  # $3.00
            output_tokens=1_000_000,  # $15.00
            cache_creation_tokens=1_000_000,  # $3.75
            cache_read_tokens=1_000_000  # $0.30
        )

        cost = metrics.total_cost()
        assert isinstance(cost, Decimal)
        assert cost == Decimal("22.05")  # 3 + 15 + 3.75 + 0.30

    def test_cache_efficiency_calculation(self):
        """Should calculate cache hit ratio correctly."""
        # 50% cache hit
        metrics = TokenMetrics(
            input_tokens=5000,
            output_tokens=1000,
            cache_read_tokens=5000
        )
        assert metrics.cache_efficiency() == 0.5

        # No cache
        metrics_no_cache = TokenMetrics(input_tokens=1000, output_tokens=500)
        assert metrics_no_cache.cache_efficiency() == 0.0

        # 100% cache
        metrics_full_cache = TokenMetrics(
            input_tokens=0,
            output_tokens=1000,
            cache_read_tokens=10000
        )
        assert metrics_full_cache.cache_efficiency() == 1.0

    def test_amplification_ratio(self):
        """Should calculate output/input ratio."""
        # 2x amplification
        metrics = TokenMetrics(input_tokens=1000, output_tokens=2000)
        assert metrics.amplification_ratio() == 2.0

        # 0.5x amplification
        metrics_low = TokenMetrics(input_tokens=2000, output_tokens=1000)
        assert metrics_low.amplification_ratio() == 0.5

        # No input (edge case)
        metrics_no_input = TokenMetrics(input_tokens=0, output_tokens=1000)
        assert metrics_no_input.amplification_ratio() == 0.0

    def test_from_dict_enriched_format(self):
        """Should parse from enriched sessions format."""
        data = {
            'input_tokens': 1000,
            'output_tokens': 500,
            'cache_read_input_tokens': 10000
        }

        metrics = TokenMetrics.from_dict(data)

        assert metrics.input_tokens == 1000
        assert metrics.output_tokens == 500
        assert metrics.cache_read_tokens == 10000

    def test_from_dict_with_cache_creation_object(self):
        """Should parse cache creation from nested object."""
        data = {
            'input_tokens': 1000,
            'output_tokens': 500,
            'cache_creation': {
                'ephemeral_5m_input_tokens': 100,
                'ephemeral_1h_input_tokens': 200
            }
        }

        metrics = TokenMetrics.from_dict(data)

        assert metrics.cache_creation_tokens == 300  # 100 + 200

    def test_to_dict_serialization(self):
        """Should serialize to dict with calculated fields."""
        metrics = TokenMetrics(
            input_tokens=1000,
            output_tokens=500,
            cache_read_tokens=5000
        )

        result = metrics.to_dict()

        assert result['input_tokens'] == 1000
        assert result['output_tokens'] == 500
        assert result['total_tokens'] == 6500
        assert 'total_cost_usd' in result
        assert 'cache_efficiency' in result


@pytest.mark.unit
class TestDelegation:
    """Test Delegation entity."""

    def test_create_delegation(self, minimal_delegation: dict):
        """Should create Delegation from dict."""
        deleg = Delegation.from_dict(minimal_delegation)

        assert deleg.uuid == 'test-uuid-001'
        assert deleg.agent_type == 'developer'
        assert deleg.session_id == 'test-session-001'

    def test_delegation_immutable(self, minimal_delegation: dict):
        """Delegation should be immutable."""
        deleg = Delegation.from_dict(minimal_delegation)

        with pytest.raises(AttributeError):
            deleg.agent_type = 'different-agent'

    def test_delegation_requires_uuid(self):
        """Should reject delegation without UUID."""
        with pytest.raises(ValidationError):
            Delegation(
                uuid='',
                timestamp='2025-09-15T10:00:00Z',
                session_id='test',
                agent_type='developer',
                cwd='/test',
                description='test',
                tokens=TokenMetrics(input_tokens=100, output_tokens=50)
            )

    def test_delegation_total_tokens(self, minimal_delegation: dict):
        """Should calculate total tokens via TokenMetrics."""
        deleg = Delegation.from_dict(minimal_delegation)

        total = deleg.total_tokens()
        assert total == 1500  # 1000 input + 500 output

    def test_delegation_cost(self, minimal_delegation: dict):
        """Should calculate cost via TokenMetrics."""
        deleg = Delegation.from_dict(minimal_delegation)

        cost = deleg.cost()
        assert isinstance(cost, Decimal)
        assert cost > 0

    def test_delegation_success_default_true(self, minimal_delegation: dict):
        """Success should default to True if not specified."""
        deleg = Delegation.from_dict(minimal_delegation)

        assert deleg.is_success() is True

    def test_delegation_datetime_parsing(self, minimal_delegation: dict):
        """Should parse timestamp to datetime."""
        deleg = Delegation.from_dict(minimal_delegation)

        dt = deleg.datetime()
        assert isinstance(dt, datetime)
        assert dt.year == 2025
        assert dt.month == 9
        assert dt.day == 15

    def test_delegation_from_enriched_format(self, complete_delegation: dict):
        """Should parse enriched format with all fields."""
        deleg = Delegation.from_dict(complete_delegation)

        assert deleg.agent_type == 'solution-architect'
        assert deleg.description == 'Design system architecture'
        assert deleg.prompt == 'Design a scalable system'
        assert deleg.success is True


@pytest.mark.unit
class TestSession:
    """Test Session entity."""

    def test_create_empty_session(self, minimal_session: dict):
        """Should create session with no delegations."""
        session = Session.from_dict(minimal_session)

        assert session.session_id == 'test-session-001'
        assert len(session.delegations) == 0

    def test_create_session_with_delegations(self, session_with_delegations: dict):
        """Should create session with delegations."""
        session = Session.from_dict(session_with_delegations)

        assert session.session_id == 'test-session-002'
        assert len(session.delegations) == 3
        assert all(isinstance(d, Delegation) for d in session.delegations)

    def test_session_is_marathon_threshold(self, marathon_session: dict, session_with_delegations: dict):
        """Should detect marathon sessions (>20 delegations)."""
        normal = Session.from_dict(session_with_delegations)
        assert normal.is_marathon() is False  # 3 delegations

        marathon = Session.from_dict(marathon_session)
        assert marathon.is_marathon() is True  # 25 delegations

    def test_session_success_rate(self, session_with_delegations: dict):
        """Should calculate success rate."""
        # All successful (default)
        session = Session.from_dict(session_with_delegations)
        assert session.success_rate() == 1.0

        # Mixed success
        data = session_with_delegations.copy()
        data['delegations'][0]['success'] = False
        data['delegations'][1]['success'] = True
        data['delegations'][2]['success'] = True

        session_mixed = Session.from_dict(data)
        assert session_mixed.success_rate() == pytest.approx(0.6667, rel=0.01)

    def test_session_total_tokens(self, session_with_delegations: dict):
        """Should sum tokens across all delegations."""
        session = Session.from_dict(session_with_delegations)

        total = session.total_tokens()
        assert total == 1500 * 3  # 3 delegations × 1500 tokens each

    def test_session_total_cost(self, session_with_delegations: dict):
        """Should sum costs across all delegations."""
        session = Session.from_dict(session_with_delegations)

        cost = session.total_cost()
        assert isinstance(cost, Decimal)
        assert cost > 0

    def test_session_agent_types(self, session_with_delegations: dict):
        """Should list unique agent types used."""
        session = Session.from_dict(session_with_delegations)

        agents = session.agent_types()
        assert 'developer' in agents


@pytest.mark.unit
class TestPeriod:
    """Test Period entity."""

    def test_create_period(self, period_definition: dict):
        """Should create Period from dict."""
        period = Period.from_dict(period_definition)

        assert period.period_id == 'P3'
        assert period.name == 'Test Period'
        assert period.start_date == '2025-09-12'
        assert period.end_date == '2025-09-20'

    def test_period_immutable(self, period_definition: dict):
        """Period should be immutable."""
        period = Period.from_dict(period_definition)

        with pytest.raises(AttributeError):
            period.period_id = 'P4'

    def test_period_validates_date_ordering(self):
        """Should reject periods where start > end."""
        with pytest.raises(ValidationError):
            Period(
                period_id='P1',
                name='Invalid',
                start_date='2025-09-20',
                end_date='2025-09-10',  # Before start
                changes=[]
            )

    def test_period_contains_date(self, period_definition: dict):
        """Should check if date falls within period."""
        period = Period.from_dict(period_definition)

        # Within period
        assert period.contains_date('2025-09-15') is True
        assert period.contains_date('2025-09-12') is True  # Start boundary
        assert period.contains_date('2025-09-20') is True  # End boundary

        # Outside period
        assert period.contains_date('2025-09-11') is False
        assert period.contains_date('2025-09-21') is False

    def test_period_duration_days(self, period_definition: dict):
        """Should calculate period duration in days."""
        period = Period.from_dict(period_definition)

        # 2025-09-12 to 2025-09-20 = 9 days (inclusive)
        assert period.duration_days() == 9


@pytest.mark.unit
class TestAgentCall:
    """Test AgentCall entity."""

    def test_create_agent_call(self):
        """Should create AgentCall from CSV row dict."""
        data = {
            'timestamp': '2025-09-15T10:00:00Z',
            'session_id': 'test-session',
            'project_path': '/test/path',
            'agent_type': 'developer',
            'prompt_length': '150',
            'description': 'Test task'
        }

        call = AgentCall.from_dict(data)

        assert call.agent_type == 'developer'
        assert call.prompt_length == 150
        assert call.description == 'Test task'

    def test_agent_call_validates_negative_prompt_length(self):
        """Should reject negative prompt length."""
        with pytest.raises(ValidationError):
            AgentCall(
                timestamp='2025-09-15T10:00:00Z',
                session_id='test',
                project_path='/test',
                agent_type='developer',
                prompt_length=-1,
                description='test'
            )

    def test_agent_call_datetime_parsing(self):
        """Should parse timestamp to datetime."""
        call = AgentCall(
            timestamp='2025-09-15T10:30:00Z',
            session_id='test',
            project_path='/test',
            agent_type='developer',
            prompt_length=100,
            description='test'
        )

        dt = call.datetime()
        assert isinstance(dt, datetime)
        assert dt.hour == 10
        assert dt.minute == 30


@pytest.mark.unit
class TestValidationErrors:
    """Test validation error handling across models."""

    def test_invalid_delegation_data_raises_errors(self, invalid_delegation_data: list):
        """Should raise ValidationError for invalid delegation data."""
        for invalid_data in invalid_delegation_data:
            if invalid_data:  # Skip empty dict test (different error)
                with pytest.raises((ValidationError, KeyError, ValueError)):
                    Delegation.from_dict(invalid_data)

    def test_required_fields_validation(self):
        """Should validate required fields are present."""
        # Missing uuid
        with pytest.raises(ValidationError):
            Delegation(
                uuid='',
                timestamp='2025-09-15T10:00:00Z',
                session_id='test',
                agent_type='developer',
                cwd='/test',
                description='test',
                tokens=TokenMetrics(input_tokens=100, output_tokens=50)
            )

        # Missing session_id for Session
        with pytest.raises(ValidationError):
            Session(session_id='', delegations=[])

        # Missing period_id for Period
        with pytest.raises(ValidationError):
            Period(
                period_id='',
                name='Test',
                start_date='2025-09-01',
                end_date='2025-09-30'
            )
