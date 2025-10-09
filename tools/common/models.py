"""
Domain Model - Typed Entities for Delegation Retrospective Analysis

This module defines the core domain entities to replace Dict[str, Any] primitive obsession.
All entities are immutable dataclasses with type safety, validation, and business logic.

Entities:
- TokenMetrics: Token usage and cost tracking
- Delegation: Single agent invocation with metadata
- Session: Collection of delegations with analysis
- Period: Temporal boundary for segmentation
- AgentCall: Agent usage from CSV metadata

Usage:
    from common.models import Delegation, Session, Period

    # Load from dict
    delegation = Delegation.from_dict(raw_data)

    # Access typed fields
    tokens = delegation.total_tokens()

    # Business logic
    if session.is_marathon():
        rate = session.success_rate()
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal


# =============================================================================
# Custom Exceptions
# =============================================================================

class ValidationError(Exception):
    """Raised when data validation fails during model construction."""
    pass


# =============================================================================
# Token Metrics
# =============================================================================

@dataclass(frozen=True)
class TokenMetrics:
    """Token usage and cost metrics for a delegation.

    Attributes:
        input_tokens: Standard input tokens (non-cached)
        output_tokens: Generated output tokens
        cache_creation_tokens: Tokens written to cache (ephemeral 5m + 1h)
        cache_read_tokens: Tokens read from cache

    Business Logic:
        - total_tokens(): Sum of all token usage
        - total_cost(): Estimated USD cost
        - cache_efficiency(): Ratio of cached to total reads
        - amplification_ratio(): Output tokens per input token
    """
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0

    def __post_init__(self):
        """Validate token counts are non-negative."""
        if self.input_tokens < 0:
            raise ValidationError(f"input_tokens must be >= 0, got {self.input_tokens}")
        if self.output_tokens < 0:
            raise ValidationError(f"output_tokens must be >= 0, got {self.output_tokens}")
        if self.cache_creation_tokens < 0:
            raise ValidationError(f"cache_creation_tokens must be >= 0, got {self.cache_creation_tokens}")
        if self.cache_read_tokens < 0:
            raise ValidationError(f"cache_read_tokens must be >= 0, got {self.cache_read_tokens}")

    def total_tokens(self) -> int:
        """Sum of all token usage (input + output + cache operations)."""
        return (
            self.input_tokens +
            self.output_tokens +
            self.cache_creation_tokens +
            self.cache_read_tokens
        )

    def total_cost(self) -> Decimal:
        """Estimated USD cost based on Claude 3.5 Sonnet pricing.

        Pricing (per million tokens):
        - Input: $3.00
        - Output: $15.00
        - Cache write: $3.75
        - Cache read: $0.30
        """
        # Pricing per million tokens
        INPUT_PRICE = Decimal("3.00")
        OUTPUT_PRICE = Decimal("15.00")
        CACHE_WRITE_PRICE = Decimal("3.75")
        CACHE_READ_PRICE = Decimal("0.30")

        cost = (
            (Decimal(self.input_tokens) / Decimal("1000000")) * INPUT_PRICE +
            (Decimal(self.output_tokens) / Decimal("1000000")) * OUTPUT_PRICE +
            (Decimal(self.cache_creation_tokens) / Decimal("1000000")) * CACHE_WRITE_PRICE +
            (Decimal(self.cache_read_tokens) / Decimal("1000000")) * CACHE_READ_PRICE
        )
        return cost.quantize(Decimal("0.0001"))  # Round to 4 decimal places

    def cache_efficiency(self) -> float:
        """Ratio of cached reads to total reads (0.0 to 1.0).

        Returns:
            0.0 if no reads occurred, otherwise cache_read / (input + cache_read)
        """
        total_reads = self.input_tokens + self.cache_read_tokens
        if total_reads == 0:
            return 0.0
        return self.cache_read_tokens / total_reads

    def amplification_ratio(self) -> float:
        """Output tokens per input token.

        Returns:
            0.0 if no input tokens, otherwise output / input
        """
        if self.input_tokens == 0:
            return 0.0
        return self.output_tokens / self.input_tokens

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenMetrics':
        """Construct from raw delegation usage dict.

        Args:
            data: Usage dict from delegation JSON (message.usage)

        Returns:
            TokenMetrics instance

        Example:
            >>> usage = {
            ...     "input_tokens": 1000,
            ...     "output_tokens": 500,
            ...     "cache_read_input_tokens": 10000,
            ...     "cache_creation_input_tokens": 2000
            ... }
            >>> metrics = TokenMetrics.from_dict(usage)
        """
        # Extract cache creation tokens (ephemeral 5m + 1h)
        cache_creation = data.get('cache_creation', {})
        cache_creation_total = (
            cache_creation.get('ephemeral_5m_input_tokens', 0) +
            cache_creation.get('ephemeral_1h_input_tokens', 0)
        )

        # Fallback to direct field if cache_creation object not present
        if cache_creation_total == 0:
            cache_creation_total = data.get('cache_creation_input_tokens', 0)

        return cls(
            input_tokens=data.get('input_tokens', 0),
            output_tokens=data.get('output_tokens', 0),
            cache_creation_tokens=cache_creation_total,
            cache_read_tokens=data.get('cache_read_input_tokens', 0)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'cache_creation_tokens': self.cache_creation_tokens,
            'cache_read_tokens': self.cache_read_tokens,
            'total_tokens': self.total_tokens(),
            'total_cost_usd': float(self.total_cost()),
            'cache_efficiency': self.cache_efficiency(),
            'amplification_ratio': self.amplification_ratio()
        }


# =============================================================================
# Delegation
# =============================================================================

@dataclass(frozen=True)
class Delegation:
    """Single agent invocation with full metadata.

    Attributes:
        uuid: Unique identifier
        timestamp: ISO timestamp of delegation
        session_id: Parent session UUID
        agent_type: Type of agent invoked (e.g., 'developer', 'solution-architect')
        cwd: Working directory path
        description: Brief task description
        prompt: Full prompt text (optional)
        tokens: Token usage metrics
        success: Whether delegation succeeded (optional)

    Business Logic:
        - total_tokens(): Sum of token usage
        - cost(): Estimated USD cost
        - is_success(): Whether task completed successfully
    """
    uuid: str
    timestamp: str
    session_id: str
    agent_type: str
    cwd: str
    description: str
    tokens: TokenMetrics
    prompt: Optional[str] = None
    success: Optional[bool] = None

    def __post_init__(self):
        """Validate required fields."""
        if not self.uuid:
            raise ValidationError("uuid is required")
        if not self.timestamp:
            raise ValidationError("timestamp is required")
        if not self.session_id:
            raise ValidationError("session_id is required")
        if not self.agent_type:
            raise ValidationError("agent_type is required")

    def total_tokens(self) -> int:
        """Sum of all token usage."""
        return self.tokens.total_tokens()

    def cost(self) -> Decimal:
        """Estimated USD cost."""
        return self.tokens.total_cost()

    def is_success(self) -> bool:
        """Whether delegation succeeded (defaults to True if not specified)."""
        return self.success if self.success is not None else True

    def datetime(self) -> datetime:
        """Parse timestamp to datetime object."""
        # Handle both ISO format with Z and timezone
        ts = self.timestamp.replace('Z', '+00:00')
        return datetime.fromisoformat(ts)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Delegation':
        """Construct from raw delegation JSON or enriched session format.

        Supports two formats:
        1. Raw JSONL: Full delegation with message.content structure
        2. Enriched sessions: Flattened structure with direct fields

        Args:
            data: Delegation dict from JSONL or enriched sessions

        Returns:
            Delegation instance

        Example:
            >>> # Raw JSONL format
            >>> raw = {
            ...     "uuid": "abc-123",
            ...     "timestamp": "2025-09-15T10:30:00Z",
            ...     "sessionId": "session-456",
            ...     "message": {
            ...         "content": [{
            ...             "type": "tool_use",
            ...             "name": "Task",
            ...             "input": {
            ...                 "subagent_type": "developer",
            ...                 "description": "Fix bug"
            ...             }
            ...         }],
            ...         "usage": {"input_tokens": 1000, "output_tokens": 500}
            ...     },
            ...     "cwd": "/path/to/project"
            ... }
            >>> delegation = Delegation.from_dict(raw)

            >>> # Enriched format
            >>> enriched = {
            ...     "tool_use_id": "abc-123",
            ...     "timestamp": "2025-09-15T10:30:00Z",
            ...     "session_id": "session-456",
            ...     "agent_type": "developer",
            ...     "description": "Fix bug",
            ...     "tokens_in": 1000,
            ...     "tokens_out": 500
            ... }
            >>> delegation = Delegation.from_dict(enriched)
        """
        # Detect format: enriched sessions have flattened structure
        is_enriched = 'tokens_in' in data or 'tool_use_id' in data

        if is_enriched:
            # Enriched format: flattened structure
            agent_type = data.get('agent_type', 'unknown')
            description = data.get('description', '')
            prompt = data.get('prompt')
            cwd = data.get('cwd', '')  # May not be present in enriched format

            # Build token metrics from flattened fields
            tokens = TokenMetrics(
                input_tokens=data.get('tokens_in', 0),
                output_tokens=data.get('tokens_out', 0),
                cache_creation_tokens=0,  # Not in enriched format
                cache_read_tokens=data.get('cache_read', 0)
            )

            return cls(
                uuid=data.get('tool_use_id', data.get('uuid', '')),
                timestamp=data.get('timestamp', ''),
                session_id=data.get('session_id', ''),
                agent_type=agent_type,
                cwd=cwd,
                description=description,
                prompt=prompt,
                tokens=tokens,
                success=data.get('success')
            )
        else:
            # Raw JSONL format: nested message structure
            message = data.get('message', {})
            content = message.get('content', [])

            agent_type = None
            description = None
            prompt = None

            for item in content:
                if item.get('type') == 'tool_use' and item.get('name') == 'Task':
                    task_input = item.get('input', {})
                    agent_type = task_input.get('subagent_type')
                    description = task_input.get('description', '')
                    prompt = task_input.get('prompt')
                    break

            # Fallback: try to get from top-level if extraction failed
            if not agent_type:
                agent_type = data.get('agent_type', 'unknown')
            if not description:
                description = data.get('description', '')

            # Extract token metrics from usage
            usage = message.get('usage', {})
            tokens = TokenMetrics.from_dict(usage)

            return cls(
                uuid=data.get('uuid', ''),
                timestamp=data.get('timestamp', ''),
                session_id=data.get('sessionId', data.get('session_id', '')),
                agent_type=agent_type,
                cwd=data.get('cwd', ''),
                description=description,
                prompt=prompt,
                tokens=tokens,
                success=data.get('success')
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'uuid': self.uuid,
            'timestamp': self.timestamp,
            'session_id': self.session_id,
            'agent_type': self.agent_type,
            'cwd': self.cwd,
            'description': self.description,
            'tokens': self.tokens.to_dict()
        }

        if self.prompt:
            result['prompt'] = self.prompt
        if self.success is not None:
            result['success'] = self.success

        return result


# =============================================================================
# Session
# =============================================================================

@dataclass
class Session:
    """Collection of delegations within a single user session.

    Attributes:
        session_id: Unique session UUID
        delegations: List of delegations in this session
        message_count: Total messages in session (optional)
        start_time: Session start timestamp (optional)
        end_time: Session end timestamp (optional)

    Business Logic:
        - is_marathon(): Check if delegation count exceeds threshold
        - success_rate(): Percentage of successful delegations
        - total_tokens(): Sum of all delegation tokens
        - total_cost(): Sum of all delegation costs
        - duration(): Time between first and last delegation
    """
    session_id: str
    delegations: List[Delegation] = field(default_factory=list)
    message_count: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    def __post_init__(self):
        """Validate session data."""
        if not self.session_id:
            raise ValidationError("session_id is required")

        # Infer start/end times from delegations if not provided
        if self.delegations:
            if not self.start_time:
                object.__setattr__(self, 'start_time', self.delegations[0].timestamp)
            if not self.end_time:
                object.__setattr__(self, 'end_time', self.delegations[-1].timestamp)

    def is_marathon(self, threshold: int = 20) -> bool:
        """Check if session exceeds marathon threshold.

        Args:
            threshold: Delegation count threshold (default: 20)

        Returns:
            True if delegation count > threshold
        """
        return len(self.delegations) > threshold

    def success_rate(self) -> float:
        """Calculate percentage of successful delegations.

        Returns:
            Success rate as float 0.0 to 1.0, or 1.0 if no delegations
        """
        if not self.delegations:
            return 1.0

        successes = sum(1 for d in self.delegations if d.is_success())
        return successes / len(self.delegations)

    def total_tokens(self) -> int:
        """Sum of all delegation tokens."""
        return sum(d.total_tokens() for d in self.delegations)

    def total_cost(self) -> Decimal:
        """Sum of all delegation costs."""
        return sum((d.cost() for d in self.delegations), Decimal("0"))

    def duration_seconds(self) -> Optional[int]:
        """Duration in seconds between first and last delegation.

        Returns:
            Duration in seconds, or None if insufficient data
        """
        if not self.start_time or not self.end_time:
            return None

        start = datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(self.end_time.replace('Z', '+00:00'))
        return int((end - start).total_seconds())

    def agent_types(self) -> List[str]:
        """Get unique agent types used in this session."""
        return list(set(d.agent_type for d in self.delegations))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Construct from session dict.

        Args:
            data: Session dict with 'delegations' list

        Returns:
            Session instance
        """
        session_id = data.get('session_id', '')

        # Build delegations with session_id enrichment
        delegations = []
        for d in data.get('delegations', []):
            # Ensure delegation has session_id set
            if not d.get('session_id'):
                d = {**d, 'session_id': session_id}
            delegations.append(Delegation.from_dict(d))

        return cls(
            session_id=session_id,
            delegations=delegations,
            message_count=data.get('message_count'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            'session_id': self.session_id,
            'delegations': [d.to_dict() for d in self.delegations],
            'delegation_count': len(self.delegations),
            'success_rate': self.success_rate(),
            'total_tokens': self.total_tokens(),
            'total_cost_usd': float(self.total_cost()),
            'is_marathon': self.is_marathon()
        }

        if self.message_count is not None:
            result['message_count'] = self.message_count
        if self.start_time:
            result['start_time'] = self.start_time
        if self.end_time:
            result['end_time'] = self.end_time
        if self.duration_seconds():
            result['duration_seconds'] = self.duration_seconds()

        return result


# =============================================================================
# Period
# =============================================================================

@dataclass(frozen=True)
class Period:
    """Temporal boundary for analysis segmentation.

    Attributes:
        period_id: Period identifier (e.g., 'P2', 'P3', 'P4')
        name: Human-readable period name
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        changes: List of architectural changes in this period
        description: Period description

    Business Logic:
        - contains_date(): Check if date falls within period
        - duration_days(): Number of days in period
    """
    period_id: str
    name: str
    start_date: str
    end_date: str
    changes: List[str] = field(default_factory=list)
    description: str = ""

    def __post_init__(self):
        """Validate period dates."""
        if not self.period_id:
            raise ValidationError("period_id is required")
        if not self.start_date:
            raise ValidationError("start_date is required")
        if not self.end_date:
            raise ValidationError("end_date is required")

        # Validate date ordering
        start = datetime.fromisoformat(self.start_date.split('T')[0])
        end = datetime.fromisoformat(self.end_date.split('T')[0])
        if start > end:
            raise ValidationError(f"start_date must be <= end_date: {self.start_date} > {self.end_date}")

    def contains_date(self, date_str: str) -> bool:
        """Check if date falls within this period.

        Args:
            date_str: ISO date string (may include time component)

        Returns:
            True if date is within [start_date, end_date] inclusive
        """
        # Extract date part if timestamp
        date_part = date_str.split('T')[0]
        date_obj = datetime.fromisoformat(date_part).date()

        start = datetime.fromisoformat(self.start_date.split('T')[0]).date()
        end = datetime.fromisoformat(self.end_date.split('T')[0]).date()

        return start <= date_obj <= end

    def duration_days(self) -> int:
        """Number of days in period (inclusive)."""
        start = datetime.fromisoformat(self.start_date.split('T')[0]).date()
        end = datetime.fromisoformat(self.end_date.split('T')[0]).date()
        return (end - start).days + 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Period':
        """Construct from period definition dict.

        Args:
            data: Period dict with start, end, name, etc.

        Returns:
            Period instance
        """
        return cls(
            period_id=data.get('period_id', ''),
            name=data.get('name', ''),
            start_date=data.get('start', data.get('start_date', '')),
            end_date=data.get('end', data.get('end_date', '')),
            changes=data.get('changes', []),
            description=data.get('description', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'period_id': self.period_id,
            'name': self.name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'changes': self.changes,
            'description': self.description,
            'duration_days': self.duration_days()
        }


# =============================================================================
# Agent Call (CSV Metadata)
# =============================================================================

@dataclass(frozen=True)
class AgentCall:
    """Agent usage metadata from CSV export.

    Attributes:
        timestamp: ISO timestamp of call
        session_id: Parent session UUID
        project_path: Path to project
        agent_type: Type of agent called
        prompt_length: Length of prompt in characters
        description: Brief task description

    Business Logic:
        - datetime(): Parse timestamp to datetime
    """
    timestamp: str
    session_id: str
    project_path: str
    agent_type: str
    prompt_length: int
    description: str

    def __post_init__(self):
        """Validate agent call data."""
        if not self.timestamp:
            raise ValidationError("timestamp is required")
        if not self.session_id:
            raise ValidationError("session_id is required")
        if not self.agent_type:
            raise ValidationError("agent_type is required")
        if self.prompt_length < 0:
            raise ValidationError(f"prompt_length must be >= 0, got {self.prompt_length}")

    def datetime(self) -> datetime:
        """Parse timestamp to datetime object."""
        ts = self.timestamp.replace('Z', '+00:00')
        return datetime.fromisoformat(ts)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCall':
        """Construct from CSV row dict.

        Args:
            data: Dict with CSV column names as keys

        Returns:
            AgentCall instance
        """
        return cls(
            timestamp=data.get('timestamp', ''),
            session_id=data.get('session_id', ''),
            project_path=data.get('project_path', ''),
            agent_type=data.get('agent_type', ''),
            prompt_length=int(data.get('prompt_length', 0)),
            description=data.get('description', '').strip()
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'timestamp': self.timestamp,
            'session_id': self.session_id,
            'project_path': self.project_path,
            'agent_type': self.agent_type,
            'prompt_length': self.prompt_length,
            'description': self.description
        }
