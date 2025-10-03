# Streaming JSON Migration Guide

Quick reference for migrating scripts to use memory-efficient streaming.

---

## Quick Start

### 1. Import Streaming Functions

```python
from common.data_repository import stream_sessions, stream_delegations
```

### 2. Basic Migration

**Before**:
```python
from common.data_repository import load_sessions

sessions = load_sessions()
marathons = [s for s in sessions if len(s.get('delegations', [])) > 20]
```

**After**:
```python
from common.data_repository import stream_sessions

marathon_filter = lambda s: len(s.get('delegations', [])) > 20
marathons = list(stream_sessions(filter_func=marathon_filter))
```

**Memory saved**: 66.5% (3x reduction)

---

## Common Patterns

### Pattern 1: Filter + Collect

**Use case**: Need filtered subset of data

```python
# Filter during stream (memory efficient)
p4_sessions = list(stream_sessions(
    filter_func=lambda s: s.get('period') == 'P4'
))
```

### Pattern 2: Filter + Process (Best)

**Use case**: Process items without collecting

```python
# Process one at a time (minimal memory)
for session in stream_sessions(filter_func=my_filter):
    analyze(session)
    save_result(session)
    # Session garbage collected after processing
```

### Pattern 3: Count + Aggregate

**Use case**: Statistics without loading all data

```python
# Streaming aggregation
from collections import Counter

agent_counts = Counter()
for delegation in stream_delegations():
    agent_counts[delegation.get('agent_type')] += 1
```

### Pattern 4: Find First Match

**Use case**: Stop as soon as condition met

```python
# Stream until found (don't load everything)
def find_first_marathon():
    for session in stream_sessions():
        if len(session.get('delegations', [])) > 20:
            return session
    return None
```

---

## Migration Examples

### Example 1: Simple Filter

**Script**: Finding all developer delegations

```python
# BEFORE (loads all 1,355 delegations = 20MB)
from common.data_repository import load_delegations

delegations = load_delegations()
developer_tasks = [d for d in delegations if d.get('agent_type') == 'developer']

# AFTER (streams delegations = 1.4MB peak)
from common.data_repository import stream_delegations

developer_tasks = list(stream_delegations(
    filter_func=lambda d: d.get('agent_type') == 'developer'
))
```

**Savings**: 20MB → 1.4MB (14.5x reduction)

### Example 2: Multiple Conditions

**Script**: Finding P3 marathons

```python
# BEFORE
sessions = load_sessions()
p3_marathons = []
for session in sessions:
    delegations = session.get('delegations', [])
    if len(delegations) > 20 and delegations:
        period = classify_period(delegations[0].get('timestamp', ''))
        if period == 'P3':
            p3_marathons.append(session)

# AFTER
def is_p3_marathon(session):
    delegations = session.get('delegations', [])
    if len(delegations) <= 20 or not delegations:
        return False
    period = classify_period(delegations[0].get('timestamp', ''))
    return period == 'P3'

p3_marathons = list(stream_sessions(filter_func=is_p3_marathon))
```

**Benefits**:
- Clear separation of filtering logic
- Only matching sessions loaded into memory
- Reusable filter function

### Example 3: Aggregation

**Script**: Agent usage statistics

```python
# BEFORE (loads all data)
delegations = load_delegations()
agent_stats = {}
for d in delegations:
    agent = d.get('agent_type')
    if agent not in agent_stats:
        agent_stats[agent] = {'count': 0, 'tokens': 0}
    agent_stats[agent]['count'] += 1
    agent_stats[agent]['tokens'] += d.get('input_tokens', 0)

# AFTER (streams delegations)
from collections import defaultdict

agent_stats = defaultdict(lambda: {'count': 0, 'tokens': 0})
for delegation in stream_delegations():
    agent = delegation.get('agent_type')
    agent_stats[agent]['count'] += 1
    agent_stats[agent]['tokens'] += delegation.get('input_tokens', 0)
```

**Savings**: 20MB → <2MB memory usage

---

## When to Use Streaming

### ✓ Good Use Cases

- **Large file processing** (>5MB JSON files)
- **Filtering operations** (want subset of data)
- **One-pass algorithms** (process items sequentially)
- **Memory-constrained environments** (limited RAM)
- **Future-proofing** (data will grow)

### ✗ Bad Use Cases

- **Small datasets** (<1MB) - overhead not worth it
- **Random access** - need to jump around dataset
- **Multiple passes** - need to iterate multiple times
- **Complex sorting** - requires all data in memory
- **Performance critical** - speed > memory

---

## Performance Trade-offs

### Memory vs. Time

| Approach | Memory | Time | Use When |
|----------|--------|------|----------|
| Full Load | 20 MB | 45ms | Speed critical, small dataset |
| Session Stream | 6.7 MB | 129ms | Memory constrained, medium dataset |
| Delegation Stream | 1.4 MB | 130ms | Severe memory constraints, filtering |

**Rule of thumb**: Streaming adds ~3x time overhead but saves 3-15x memory.

### Scalability

| Dataset Size | Full Load Memory | Streaming Memory | Recommendation |
|--------------|------------------|------------------|----------------|
| 1x (current) | 20 MB | 6.7 MB | Either works |
| 5x | 100 MB | 33.5 MB | Streaming preferred |
| 10x | 200 MB | 67 MB | Streaming required |
| 100x | 2 GB | 670 MB | Streaming + pagination |

---

## Common Mistakes

### ❌ Mistake 1: Loading entire stream into list

```python
# BAD: Defeats purpose of streaming
all_sessions = list(stream_sessions())
filtered = [s for s in all_sessions if my_filter(s)]

# GOOD: Filter during stream
filtered = list(stream_sessions(filter_func=my_filter))
```

### ❌ Mistake 2: Not using filter when possible

```python
# BAD: Load everything, filter later
for session in stream_sessions():
    if len(session.get('delegations', [])) > 20:
        process(session)

# GOOD: Filter during stream
marathon_filter = lambda s: len(s.get('delegations', [])) > 20
for session in stream_sessions(filter_func=marathon_filter):
    process(session)
```

### ❌ Mistake 3: Multiple iterations over stream

```python
# BAD: Stream is consumed after first iteration
for session in stream_sessions():
    count_delegations(session)

for session in stream_sessions():  # This starts over from beginning!
    analyze_agents(session)

# GOOD: Collect once if multiple passes needed
sessions = list(stream_sessions())
for session in sessions:
    count_delegations(session)
for session in sessions:
    analyze_agents(session)
```

---

## Testing Your Migration

### 1. Verify Correctness

```python
# Run both versions and compare results
old_results = old_function()
new_results = new_streaming_function()
assert old_results == new_results, "Results don't match!"
```

### 2. Measure Memory Impact

```python
import tracemalloc

tracemalloc.start()
result = your_streaming_function()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
```

### 3. Benchmark Performance

```python
import time

start = time.perf_counter()
result = your_streaming_function()
elapsed = time.perf_counter() - start

print(f"Time elapsed: {elapsed:.3f} seconds")
```

---

## API Reference

### `stream_sessions(filter_func=None, enriched=True)`

**Returns**: Iterator of session dictionaries

**Parameters**:
- `filter_func`: Optional function `(session) -> bool` to filter sessions
- `enriched`: Use enriched sessions (True) or full sessions (False)

**Memory**: 5-10x reduction vs `load_sessions()`

**Example**:
```python
for session in stream_sessions(lambda s: s.get('period') == 'P4'):
    print(session['session_id'])
```

### `stream_delegations(filter_func=None, enriched=True)`

**Returns**: Iterator of delegation dictionaries with session context

**Parameters**:
- `filter_func`: Optional function `(delegation) -> bool` to filter
- `enriched`: Use enriched sessions (True) or full sessions (False)

**Memory**: 10-20x reduction vs `load_delegations()`

**Example**:
```python
for delegation in stream_delegations(lambda d: d.get('agent_type') == 'developer'):
    print(delegation['prompt'][:100])
```

---

## Troubleshooting

### Issue: "Stream consumed" error

**Problem**: Tried to iterate over stream twice

**Solution**: Collect stream into list if multiple passes needed
```python
sessions = list(stream_sessions())
# Now you can iterate multiple times
```

### Issue: Out of memory despite streaming

**Problem**: Collecting entire stream into list

**Solution**: Process items incrementally without collecting
```python
# Instead of:
results = [process(s) for s in stream_sessions()]

# Do:
for session in stream_sessions():
    result = process(session)
    save(result)
```

### Issue: Slower than expected

**Problem**: Filter function too complex or not selective enough

**Solution**: Optimize filter or use more selective criteria
```python
# Slow filter
def slow_filter(session):
    # Complex computation for every session
    return expensive_check(session)

# Fast filter
def fast_filter(session):
    # Quick check first
    if len(session.get('delegations', [])) <= 20:
        return False
    return expensive_check(session)
```

---

## Checklist for Migration

- [ ] Import `stream_sessions` or `stream_delegations`
- [ ] Replace `load_*()` with `stream_*()`
- [ ] Add filter function if applicable
- [ ] Test correctness (compare results with old version)
- [ ] Measure memory improvement
- [ ] Verify performance is acceptable
- [ ] Update function docstrings
- [ ] Mark old functions as deprecated if appropriate

---

## Getting Help

1. **Read benchmarks**: See `data/streaming_benchmark_results.json`
2. **Check examples**: See migrated scripts (analyze_marathons.py, analyze_p4_marathons.py)
3. **Run benchmark suite**: `python3 benchmark_streaming.py`
4. **Consult report**: Read `STREAMING_IMPLEMENTATION_REPORT.md`

---

**Remember**: Streaming is a tool, not a requirement. Use it when memory matters more than speed.
