# Domain Model Documentation

**Status**: ✅ Implemented (ARCH1)
**Created**: 2025-10-02
**Purpose**: Replace `Dict[str, Any]` primitive obsession with typed domain entities

---

## Overview

The domain model provides type-safe representations of core business entities in the delegation retrospective analysis system. All entities are immutable dataclasses with:

- **Type safety**: Full type hints for IDE support and mypy validation
- **Validation**: Post-init validation of required fields and constraints
- **Business logic**: Encapsulated methods for common operations
- **Serialization**: Bidirectional conversion between dicts and models

### Benefits Over Dict-Based Approach

**BEFORE (Dict-based)**:
```python
delegation = {"uuid": "...", "timestamp": "...", "message": {...}}
total_tokens = (
    delegation['message']['usage']['input_tokens'] +
    delegation['message']['usage']['output_tokens']
)
if total_tokens > 100000:
    # High token usage
```

**AFTER (Typed)**:
```python
delegation = Delegation.from_dict(raw_data)
if delegation.total_tokens() > 100000:
    # High token usage - type-safe, encapsulated
```

---

## Entity Relationships

```
Period (1) ──── (N) Session (1) ──── (N) Delegation (1) ──── (1) TokenMetrics
                                                     │
                                                     └──── AgentCall (CSV view)
```

**Entity Hierarchy**:
- **Period**: Temporal boundary (P2, P3, P4)
- **Session**: Collection of delegations within one user session
- **Delegation**: Single agent invocation with full metadata
- **TokenMetrics**: Token usage and cost tracking for a delegation
- **AgentCall**: Alternative view from CSV export (metadata only)

---

## Core Entities

### 1. TokenMetrics

**Purpose**: Track token usage and calculate costs for a delegation.

**Fields**:
```python
@dataclass(frozen=True)
class TokenMetrics:
    input_tokens: int              # Standard input tokens (non-cached)
    output_tokens: int             # Generated output tokens
    cache_creation_tokens: int     # Tokens written to cache (ephemeral 5m + 1h)
    cache_read_tokens: int         # Tokens read from cache
```

**Business Logic Methods**:

| Method | Description | Return Type |
|--------|-------------|-------------|
| `total_tokens()` | Sum of all token usage | `int` |
| `total_cost()` | Estimated USD cost (Claude 3.5 Sonnet pricing) | `Decimal` |
| `cache_efficiency()` | Ratio of cached reads to total reads (0.0-1.0) | `float` |
| `amplification_ratio()` | Output tokens per input token | `float` |

**Pricing** (per million tokens):
- Input: $3.00
- Output: $15.00
- Cache write: $3.75
- Cache read: $0.30

**Example Usage**:
```python
# From raw delegation JSON
usage = delegation_json['message']['usage']
metrics = TokenMetrics.from_dict(usage)

# Business logic
print(f"Total tokens: {metrics.total_tokens()}")
print(f"Cost: ${metrics.total_cost()}")
print(f"Cache efficiency: {metrics.cache_efficiency():.1%}")
```

---

### 2. Delegation

**Purpose**: Single agent invocation with full metadata and token tracking.

**Fields**:
```python
@dataclass(frozen=True)
class Delegation:
    uuid: str                      # Unique identifier
    timestamp: str                 # ISO timestamp
    session_id: str                # Parent session UUID
    agent_type: str                # Agent invoked (e.g., 'developer')
    cwd: str                       # Working directory path
    description: str               # Brief task description
    tokens: TokenMetrics           # Token usage metrics
    prompt: Optional[str]          # Full prompt text (optional)
    success: Optional[bool]        # Whether task succeeded (optional)
```

**Business Logic Methods**:

| Method | Description | Return Type |
|--------|-------------|-------------|
| `total_tokens()` | Sum of token usage | `int` |
| `cost()` | Estimated USD cost | `Decimal` |
| `is_success()` | Whether delegation succeeded (default True) | `bool` |
| `datetime()` | Parse timestamp to datetime object | `datetime` |

**Validation Rules**:
- `uuid`, `timestamp`, `session_id`, `agent_type` are required
- Raises `ValidationError` if required fields missing

**Example Usage**:
```python
# Load from raw JSONL
delegation = Delegation.from_dict(raw_json)

# Type-safe access
print(f"Agent: {delegation.agent_type}")
print(f"Task: {delegation.description}")
print(f"Cost: ${delegation.cost()}")

# Business logic
if delegation.is_success():
    print(f"✓ Success - {delegation.total_tokens()} tokens")
```

---

### 3. Session

**Purpose**: Collection of delegations within a single user session.

**Fields**:
```python
@dataclass
class Session:
    session_id: str                     # Unique session UUID
    delegations: List[Delegation]       # List of delegations
    message_count: Optional[int]        # Total messages in session
    start_time: Optional[str]           # Session start (ISO)
    end_time: Optional[str]             # Session end (ISO)
```

**Business Logic Methods**:

| Method | Description | Return Type |
|--------|-------------|-------------|
| `is_marathon(threshold=20)` | Check if delegation count exceeds threshold | `bool` |
| `success_rate()` | Percentage of successful delegations (0.0-1.0) | `float` |
| `total_tokens()` | Sum of all delegation tokens | `int` |
| `total_cost()` | Sum of all delegation costs | `Decimal` |
| `duration_seconds()` | Duration between first and last delegation | `int | None` |
| `agent_types()` | Unique agent types used in session | `List[str]` |

**Auto-Inference**:
- If `start_time`/`end_time` not provided, inferred from first/last delegation

**Example Usage**:
```python
# Load from enriched sessions JSON
session = Session.from_dict(session_data)

# Marathon detection
if session.is_marathon():
    print(f"⚠️  Marathon session: {len(session.delegations)} delegations")
    print(f"   Success rate: {session.success_rate():.1%}")
    print(f"   Cost: ${session.total_cost()}")
    print(f"   Duration: {session.duration_seconds()}s")

# Agent diversity
agents = session.agent_types()
print(f"   Used {len(agents)} different agents: {', '.join(agents)}")
```

---

### 4. Period

**Purpose**: Temporal boundary for analysis segmentation.

**Fields**:
```python
@dataclass(frozen=True)
class Period:
    period_id: str                 # Period identifier (e.g., 'P2', 'P3', 'P4')
    name: str                      # Human-readable name
    start_date: str                # Start date (ISO format)
    end_date: str                  # End date (ISO format)
    changes: List[str]             # Architectural changes in period
    description: str               # Period description
```

**Business Logic Methods**:

| Method | Description | Return Type |
|--------|-------------|-------------|
| `contains_date(date_str)` | Check if date falls within period | `bool` |
| `duration_days()` | Number of days in period (inclusive) | `int` |

**Validation Rules**:
- `start_date` must be <= `end_date`
- Raises `ValidationError` if date ordering invalid

**Example Usage**:
```python
# From config
from common.config import PERIOD_DEFINITIONS

period = Period.from_dict({
    'period_id': 'P3',
    **PERIOD_DEFINITIONS['P3']
})

# Period classification
if period.contains_date("2025-09-15"):
    print(f"Date falls in {period.name}")
    print(f"Duration: {period.duration_days()} days")
    print(f"Changes: {', '.join(period.changes)}")
```

---

### 5. AgentCall

**Purpose**: Agent usage metadata from CSV export (lighter than full Delegation).

**Fields**:
```python
@dataclass(frozen=True)
class AgentCall:
    timestamp: str                 # ISO timestamp
    session_id: str                # Parent session UUID
    project_path: str              # Path to project
    agent_type: str                # Agent type called
    prompt_length: int             # Length of prompt in characters
    description: str               # Brief task description
```

**Business Logic Methods**:

| Method | Description | Return Type |
|--------|-------------|-------------|
| `datetime()` | Parse timestamp to datetime object | `datetime` |

**Validation Rules**:
- `timestamp`, `session_id`, `agent_type` are required
- `prompt_length` must be >= 0
- Raises `ValidationError` if validation fails

**Example Usage**:
```python
# Load from CSV
from common.data_repository import load_agent_calls

calls = load_agent_calls(typed=True)

# Analysis
for call in calls:
    if call.agent_type == 'developer':
        print(f"{call.timestamp}: {call.description} ({call.prompt_length} chars)")
```

---

## Data Loading

### Typed Mode

All data repository functions support `typed` parameter:

```python
from common.data_repository import load_sessions, load_delegations, load_agent_calls

# Load as typed objects
sessions = load_sessions(typed=True)        # List[Session]
delegations = load_delegations(typed=True)  # List[Delegation]
calls = load_agent_calls(typed=True)        # List[AgentCall]

# Type-safe access with IDE autocomplete
for session in sessions:
    print(session.session_id)  # Type: str
    print(session.is_marathon())  # Type: bool
```

### Backward Compatibility

Default behavior unchanged (returns dicts):

```python
# Untyped (backward compatible)
sessions = load_sessions()  # List[Dict]
sessions[0]['session_id']   # Dict access
```

### Performance

- **No overhead**: Conversion happens once at load time
- **Caching**: Typed objects cached separately from dicts
- **Memory**: Similar memory usage (dataclasses are efficient)

---

## Conversion Utilities

All entities support bidirectional conversion:

### from_dict() - Construction

```python
# Delegation from raw JSON
raw = {
    "uuid": "abc-123",
    "timestamp": "2025-09-15T10:30:00Z",
    "sessionId": "session-456",
    "message": {
        "content": [{
            "type": "tool_use",
            "name": "Task",
            "input": {
                "subagent_type": "developer",
                "description": "Fix bug"
            }
        }],
        "usage": {"input_tokens": 1000, "output_tokens": 500}
    },
    "cwd": "/path/to/project"
}

delegation = Delegation.from_dict(raw)
```

### to_dict() - Serialization

```python
# Convert back to dict for JSON export
delegation_dict = delegation.to_dict()

# Includes computed fields
delegation_dict['tokens']['total_tokens']  # Sum computed
delegation_dict['tokens']['total_cost_usd']  # Cost computed
```

---

## Migration Guide

### Step 1: Identify Target Script

Choose a script with heavy dict manipulation:
```python
# Current (dict-based)
for session in sessions:
    deleg_count = len(session['delegations'])
    if deleg_count > 20:  # Marathon threshold
        successes = sum(1 for d in session['delegations'] if d.get('success'))
        rate = successes / deleg_count
        print(f"Marathon: {rate:.1%} success")
```

### Step 2: Add Typed Import

```python
from common.data_repository import load_sessions

# Add typed=True
sessions = load_sessions(typed=True)
```

### Step 3: Replace Dict Access with Methods

```python
# Refactored (typed)
for session in sessions:
    if session.is_marathon():
        rate = session.success_rate()
        print(f"Marathon: {rate:.1%} success")
```

### Step 4: Test

```python
# Run script
python my_analysis.py

# Verify output unchanged
diff old_output.json new_output.json
```

---

## Proof of Concept Scripts

### 1. segment_data_typed.py

**Purpose**: Typed version of `segment_data.py`
**Demonstrates**: Session/Delegation/Period usage

**Key Improvements**:
- `session.is_marathon()` instead of `len(session['delegations']) > THRESHOLD`
- `session.success_rate()` instead of manual calculation
- `period.contains_date()` for classification
- Type-safe agent usage analysis

**Run**:
```bash
python segment_data_typed.py
# Output: temporal-segmentation-typed.json
```

**Code Comparison**:
```python
# BEFORE: segment_data.py (dict-based)
successful = sum(1 for d in delegations if d.get('success', False))
failed = sum(1 for d in delegations if not d.get('success', False))
success_rate = successful / len(delegations) if delegations else 0

# AFTER: segment_data_typed.py (typed)
success_rate = session.success_rate()
```

### 2. validate_data.py

**Purpose**: Comprehensive data validation using models
**Demonstrates**: Validation, error handling, type safety

**Validations**:
- Required fields present
- Token counts non-negative
- Dates parseable
- Success rates in [0, 1]
- Business rule violations (empty sessions, etc.)

**Run**:
```bash
python validate_data.py
# Output: Validation summary with errors/warnings
```

**Sample Output**:
```
Validating sessions...
  ✓ Valid: 120
  ✗ Errors: 0

Validating delegations...
  ✓ Valid: 1315
  ✗ Errors: 0

Overall Quality Score: 100.0% (1435/1435 items valid)
```

---

## Field Mapping Reference

### Delegation: Raw JSON → Model

| Raw JSON Path | Model Field | Notes |
|---------------|-------------|-------|
| `uuid` | `uuid` | Direct |
| `timestamp` | `timestamp` | Direct |
| `sessionId` | `session_id` | Normalized key |
| `cwd` | `cwd` | Direct |
| `message.content[0].input.subagent_type` | `agent_type` | Extracted from task |
| `message.content[0].input.description` | `description` | Extracted from task |
| `message.content[0].input.prompt` | `prompt` | Optional |
| `message.usage` | `tokens` | Converted to TokenMetrics |
| `success` | `success` | Optional, defaults to True |

### TokenMetrics: Raw Usage → Model

| Raw JSON Path | Model Field | Notes |
|---------------|-------------|-------|
| `input_tokens` | `input_tokens` | Direct |
| `output_tokens` | `output_tokens` | Direct |
| `cache_read_input_tokens` | `cache_read_tokens` | Direct |
| `cache_creation.ephemeral_5m_input_tokens` | `cache_creation_tokens` | Summed |
| `cache_creation.ephemeral_1h_input_tokens` | `cache_creation_tokens` | Summed |

### Session: Raw JSON → Model

| Raw JSON Path | Model Field | Notes |
|---------------|-------------|-------|
| `session_id` | `session_id` | Direct |
| `delegations[]` | `delegations` | Converted to List[Delegation] |
| `message_count` | `message_count` | Optional |
| `start_time` | `start_time` | Optional, auto-inferred |
| `end_time` | `end_time` | Optional, auto-inferred |

---

## Error Handling

### ValidationError

All models raise `ValidationError` on invalid data:

```python
from common.models import ValidationError, Period

try:
    # Invalid: start > end
    period = Period(
        period_id="P5",
        name="Invalid",
        start_date="2025-09-20",
        end_date="2025-09-10"  # Before start!
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
    # Output: "start_date must be <= end_date: 2025-09-20 > 2025-09-10"
```

### Graceful Handling

```python
from common.models import ValidationError

delegations = []
errors = []

for raw in raw_delegations:
    try:
        delegation = Delegation.from_dict(raw)
        delegations.append(delegation)
    except ValidationError as e:
        errors.append(f"Failed to parse delegation: {e}")

print(f"Loaded {len(delegations)} delegations, {len(errors)} errors")
```

---

## Best Practices

### 1. Use Type Hints

```python
from typing import List
from common.models import Session

def analyze_marathons(sessions: List[Session]) -> int:
    """Count marathon sessions."""
    return sum(1 for s in sessions if s.is_marathon())
```

### 2. Encapsulate Business Logic

❌ **Bad** (logic scattered):
```python
total = (
    delegation['message']['usage']['input_tokens'] +
    delegation['message']['usage']['output_tokens']
)
```

✅ **Good** (encapsulated):
```python
total = delegation.total_tokens()
```

### 3. Prefer Methods Over Field Access

❌ **Bad** (manual calculation):
```python
if delegation.success is not None and delegation.success:
    # ...
```

✅ **Good** (method encapsulation):
```python
if delegation.is_success():
    # ...
```

### 4. Handle Optional Fields

```python
# Check optional fields before use
if delegation.prompt:
    analyze_prompt(delegation.prompt)

if session.duration_seconds():
    print(f"Duration: {session.duration_seconds()}s")
```

---

## Future Extensions

### Planned (ARCH2)

**Period Discovery**:
```python
from common.period_builder import PeriodBuilder

# Dynamic discovery from git
builder = PeriodBuilder()
periods = builder.from_git_archaeology(repo_path="~/.claude/memories")
```

### Planned (ARCH3)

**Strategy Pattern Integration**:
```python
from common.strategies import MarathonAnalysisStrategy

strategy = MarathonAnalysisStrategy()
results = strategy.analyze(sessions)  # Accepts List[Session]
```

---

## Testing

### Unit Tests (Recommended)

```python
# tests/test_models.py
from common.models import TokenMetrics, Delegation

def test_token_metrics_cost():
    metrics = TokenMetrics(
        input_tokens=1000,
        output_tokens=500,
        cache_creation_tokens=100,
        cache_read_tokens=10000
    )

    cost = metrics.total_cost()
    assert cost > 0
    assert cost == Decimal("10.5300")  # Exact calculation

def test_delegation_from_dict():
    raw = {...}  # Sample JSON
    delegation = Delegation.from_dict(raw)

    assert delegation.uuid
    assert delegation.agent_type
    assert delegation.total_tokens() > 0
```

### Integration Tests

```python
def test_load_typed_sessions():
    from common.data_repository import load_sessions

    sessions = load_sessions(typed=True)

    assert len(sessions) > 0
    assert all(isinstance(s, Session) for s in sessions)
    assert all(s.delegations for s in sessions)
```

---

## Related Documentation

- **ARCHITECTURE-REVIEW.md**: ADR-001 (Domain Model decision)
- **CODE_QUALITY_ANALYSIS.md**: C6 (Primitive Obsession anti-pattern)
- **planning/user-stories.md**: ARCH1 acceptance criteria
- **common/data_repository.py**: Data loading with `typed` parameter
- **common/METRICS_SERVICE_USAGE.md**: Token metrics usage

---

## Summary

The typed domain model provides:

✅ **Type Safety**: IDE autocomplete, mypy validation
✅ **Business Logic**: Encapsulated methods (is_marathon, success_rate, etc.)
✅ **Validation**: Post-init checks prevent invalid data
✅ **Maintainability**: Refactor fields safely across codebase
✅ **Testing**: Mock domain objects easily
✅ **Documentation**: Self-documenting code with type hints

**Migration**: Gradual adoption via `typed=True` parameter maintains backward compatibility while enabling incremental refactoring.
