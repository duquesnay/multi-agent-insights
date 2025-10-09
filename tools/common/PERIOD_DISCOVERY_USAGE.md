# Period Discovery - Usage Guide

Quick reference for using the dynamic period discovery system.

## Quick Start

### Option 1: Simple (Uses Config Defaults)
```python
from common.config import get_dynamic_periods

# Get hardcoded periods (safe, fast)
periods = get_dynamic_periods()
```

### Option 2: Git Discovery (Methodology-Aligned)
```python
from common.config import get_dynamic_periods

# Discover from git history
periods = get_dynamic_periods(use_git=True)
```

### Option 3: Full Control
```python
from common.period_builder import PeriodBuilder

builder = PeriodBuilder()
periods = builder.discover_periods(
    use_git=True,
    use_cache=True,
    start_date="2025-08-01",
    end_date="2025-09-30"
)
```

## Return Format

All methods return the same format:

```python
{
    "P1": {
        "name": "Launch + Vacances",
        "start": "2025-08-04",
        "end": "2025-09-02",
        "changes": ["feat: add global agent definitions"],
        "description": "Multi-agent system launch",
        "commit": "795b476e"  # Only in git discovery
    },
    "P2": { ... },
    ...
}
```

## Common Patterns

### For Backward Compatibility
```python
# Existing scripts don't need changes
from common.config import PERIOD_DEFINITIONS

# PERIOD_DEFINITIONS still works
for period_id, period_data in PERIOD_DEFINITIONS.items():
    print(f"{period_id}: {period_data['start']} to {period_data['end']}")
```

### For Analysis Scripts
```python
from common.config import get_dynamic_periods

# Get periods (uses cache if available)
periods = get_dynamic_periods(use_git=True)

# Use in analysis
for period_id, period_data in periods.items():
    start = period_data['start']
    end = period_data['end']
    # Filter data by period...
```

### For Fresh Discovery
```python
from common.period_builder import PeriodBuilder

builder = PeriodBuilder()

# Invalidate old cache
builder.invalidate_cache()

# Discover fresh
periods = builder.discover_periods(use_git=True, use_cache=False)
```

## Performance

**First call (cold cache)**:
- Git discovery: ~27ms
- Caching enabled automatically

**Subsequent calls (warm cache)**:
- Cache hit: ~0.1ms (250x faster)
- Cache TTL: 24 hours

## Error Handling

```python
from common.period_builder import PeriodBuilder, PeriodDiscoveryError

builder = PeriodBuilder()

try:
    periods = builder.discover_periods(use_git=True)
except PeriodDiscoveryError as e:
    print(f"Git discovery failed: {e}")
    # Automatic fallback to config.PERIOD_DEFINITIONS
    periods = builder.discover_periods(use_git=False)
```

**Note**: Fallback is automatic - no need for try/except in most cases.

## Cache Management

### Cache Location
```
data/.period_cache.json
```

### Invalidate Cache
```python
from common.period_builder import PeriodBuilder

PeriodBuilder().invalidate_cache()
```

### Check Cache Age
```bash
# Cache metadata
cat data/.period_cache.json | jq '.cached_at, .ttl_hours'
```

## Testing

### Run Validation
```bash
python3 validate_period_discovery.py
```

### Demo Mode
```bash
python3 -m common.period_builder
```

## When to Use Which Method

**Use `get_dynamic_periods()` (Config)**:
- ✅ Most scripts
- ✅ When you want automatic fallback
- ✅ For backward compatibility

**Use `PeriodBuilder()` directly**:
- ✅ When you need custom date ranges
- ✅ When you want cache control
- ✅ For testing/validation

**Use `PERIOD_DEFINITIONS` (Static)**:
- ✅ For guaranteed stability
- ✅ When git unavailable
- ✅ For quick prototyping

## Examples

### Example 1: Analysis Script
```python
from common.config import get_dynamic_periods
from common.data_repository import DelegationRepository

# Get periods
periods = get_dynamic_periods(use_git=True)

# Load data
repo = DelegationRepository()

# Analyze by period
for period_id, period_data in periods.items():
    delegations = repo.load_by_period(
        start=period_data['start'],
        end=period_data['end']
    )
    print(f"{period_id} ({period_data['name']}): {len(delegations)} delegations")
```

### Example 2: Different Time Range (v8.0)
```python
from common.period_builder import PeriodBuilder

builder = PeriodBuilder()
periods = builder.discover_periods(
    use_git=True,
    start_date="2025-05-01",  # Extended range
    end_date="2025-09-30"
)

# Discovers all periods from May-September
print(f"Found {len(periods)} periods")
```

### Example 3: Cache Control
```python
from common.period_builder import PeriodBuilder

builder = PeriodBuilder()

# Force fresh discovery
builder.invalidate_cache()
periods = builder.discover_periods(use_git=True, use_cache=False)

# Now cache is fresh for next 24 hours
```

## Troubleshooting

### "Git repository not found"
- Check `~/.claude-memories` exists
- Fallback to hardcoded periods works automatically

### "No agent configuration changes found"
- Expand date range with `start_date` and `end_date`
- Check git commits exist in that range

### "Too many periods discovered"
- This is normal (7 vs 4 expected)
- Extra periods provide granular detail
- Use filtering if needed

### "Wrong period names"
- Period detection works, names might differ
- Names are heuristic-based
- Periods are correctly identified by dates

## Migration Guide

### Migrating Existing Scripts

**Before**:
```python
from common.config import P2_START, P2_END

start = P2_START  # "2025-09-03"
end = P2_END      # "2025-09-11"
```

**After (Backward Compatible)**:
```python
from common.config import get_dynamic_periods

periods = get_dynamic_periods()
start = periods["P2"]["start"]
end = periods["P2"]["end"]
```

**After (Git Discovery)**:
```python
from common.config import get_dynamic_periods

periods = get_dynamic_periods(use_git=True)
start = periods["P2"]["start"]
end = periods["P2"]["end"]
```

No breaking changes - both work!
