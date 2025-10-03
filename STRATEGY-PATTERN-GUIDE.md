# Strategy Pattern for Analysis - Developer Guide

## Overview

This project implements the **Strategy Pattern** to enable pluggable, extensible analyses following the **Open/Closed Principle** (from SOLID). You can add new analyses without modifying existing code.

**Status**: ✅ Implemented (ADR-004)

**Architecture**:
```
┌─────────────────────────────────────────────────────┐
│              AnalysisRunner (Orchestrator)          │
│  - Load data once                                   │
│  - Run multiple strategies                          │
│  - Aggregate results                                │
└──────────────────────┬──────────────────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
┌──────────▼─────────┐  ┌─────────▼──────────┐
│  AnalysisStrategy  │  │ CompositeStrategy  │
│   (Abstract Base)  │  │ (Run multiple)     │
└──────────┬─────────┘  └────────────────────┘
           │
    ┌──────┴──────┬──────────────┬────────────────┐
    │             │              │                │
┌───▼────┐  ┌────▼─────┐  ┌─────▼────┐  ┌────────▼────────┐
│Metrics │  │Marathon  │  │ Routing  │  │ Your Custom     │
│Strategy│  │ Strategy │  │ Quality  │  │ Strategy (NEW!) │
└────────┘  └──────────┘  └──────────┘  └─────────────────┘
```

---

## Quick Start

### Running Existing Analyses

```bash
# List available analyses
python analysis_runner.py --list

# Run all analyses
python analysis_runner.py --all

# Run specific analyses
python analysis_runner.py --metrics --marathons

# Generate markdown report
python analysis_runner.py --all --report

# Custom output directory
python analysis_runner.py --all --output my_results/
```

### Running Programmatically

```python
from analysis_runner import AnalysisRunner

# Run all analyses
runner = AnalysisRunner()
results = runner.run_all()

# Run specific analysis
result = runner.run_strategy('metrics')

# Run multiple with shared data
results = runner.run_multiple(['metrics', 'marathons'])
```

---

## Creating a Custom Analysis

### Step 1: Create Strategy Class

Create a new file in `strategies/` (or anywhere):

```python
# strategies/my_custom_analysis.py

from typing import Dict, Any
from common.analysis_strategy import AnalysisStrategy, AnalysisResult

class MyCustomAnalysisStrategy(AnalysisStrategy):
    """
    Describe what your analysis does.
    """

    def get_name(self) -> str:
        """Return human-readable name."""
        return "My Custom Analysis"

    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Execute your analysis logic.

        Args:
            data: Dictionary with 'delegations' and 'sessions' keys

        Returns:
            AnalysisResult with your findings
        """
        delegations = data.get('delegations', [])

        # Your analysis logic here
        findings = self._process_data(delegations)

        return AnalysisResult(
            name=self.get_name(),
            data=findings,
            summary=f"Analyzed {len(delegations)} items"
        )

    def _process_data(self, delegations):
        """Your analysis implementation."""
        # Example: count agents
        agent_counts = {}
        for delegation in delegations:
            agent = delegation.get('agent_type', 'unknown')
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

        return {'agent_counts': agent_counts}
```

### Step 2: Register Strategy

**Option A: Add to strategies package** (recommended)

1. Add import to `strategies/__init__.py`:
```python
from .my_custom_analysis import MyCustomAnalysisStrategy

__all__ = [
    'MetricsAnalysisStrategy',
    'MarathonAnalysisStrategy',
    'RoutingQualityAnalysisStrategy',
    'MyCustomAnalysisStrategy',  # Add this
]
```

2. Register in `analysis_runner.py`:
```python
def _register_default_strategies(self) -> None:
    self.register('metrics', MetricsAnalysisStrategy())
    self.register('marathons', MarathonAnalysisStrategy())
    self.register('routing_quality', RoutingQualityAnalysisStrategy())
    self.register('my_custom', MyCustomAnalysisStrategy())  # Add this
```

3. Add CLI flag in `analysis_runner.py` main():
```python
parser.add_argument('--my-custom', action='store_true',
                   help='Run my custom analysis')
```

**Option B: Use programmatically** (no code changes)

```python
from analysis_runner import AnalysisRunner
from my_module import MyCustomAnalysisStrategy

runner = AnalysisRunner()
runner.register('my_custom', MyCustomAnalysisStrategy())
result = runner.run_strategy('my_custom')
```

### Step 3: Run Your Analysis

```bash
# If registered in runner
python analysis_runner.py --my-custom

# Or programmatically
python -c "from analysis_runner import AnalysisRunner; \
           from strategies.my_custom_analysis import MyCustomAnalysisStrategy; \
           runner = AnalysisRunner(); \
           runner.register('custom', MyCustomAnalysisStrategy()); \
           runner.run_strategy('custom')"
```

---

## Architecture Deep Dive

### Base Classes

#### AnalysisStrategy (Abstract Base)

**Purpose**: Define interface for all analyses

**Key Methods**:
- `get_name() -> str`: Return analysis name
- `analyze(data) -> AnalysisResult`: Execute analysis logic
- `run(data) -> AnalysisResult`: Template method (loads data, validates, calls analyze())

**Built-in Features**:
- Automatic data loading via `load_default_data()`
- Error/warning tracking via `add_error()` and `add_warning()`
- Data validation via `validate_data()`

**Example Usage**:
```python
class SimpleAnalysis(AnalysisStrategy):
    def get_name(self) -> str:
        return "Simple Analysis"

    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        # Analysis logic
        return AnalysisResult(
            name=self.get_name(),
            data={'result': 'value'},
            summary="Analysis complete"
        )

# Run with automatic data loading
strategy = SimpleAnalysis()
result = strategy.run()  # Loads data automatically
result.print_summary()
```

#### AnalysisResult (Data Class)

**Purpose**: Standardize analysis output

**Fields**:
- `name`: Analysis name
- `data`: Analysis findings (dict)
- `summary`: Human-readable summary
- `metadata`: Additional metadata
- `errors`: List of errors
- `warnings`: List of warnings

**Methods**:
- `to_dict()`: Convert to dictionary
- `save_to_file(path)`: Save as JSON
- `print_summary()`: Print formatted output

---

### Design Patterns Used

#### 1. Strategy Pattern (Core)
**What**: Different analysis algorithms with common interface
**Why**: Add new analyses without modifying existing code (Open/Closed)
**Example**: `MetricsAnalysisStrategy`, `MarathonAnalysisStrategy`

#### 2. Template Method Pattern
**What**: `AnalysisStrategy.run()` defines workflow, subclasses implement `analyze()`
**Why**: Consistent execution (load → validate → analyze → format)
**Example**:
```python
def run(self, data=None):
    # Template method
    data = data or self.load_default_data()  # Step 1
    if not self.validate_data(data):         # Step 2
        return error_result
    result = self.analyze(data)              # Step 3 (subclass implements)
    result.attach_errors()                   # Step 4
    return result
```

#### 3. Composite Pattern
**What**: `CompositeAnalysisStrategy` runs multiple strategies as one
**Why**: Run related analyses together
**Example**:
```python
composite = CompositeAnalysisStrategy([
    MetricsAnalysis(),
    MarathonAnalysis()
])
result = composite.run()  # Runs both, aggregates results
```

#### 4. Registry Pattern
**What**: `AnalysisRunner` maintains registry of strategies
**Why**: Dynamic strategy discovery and execution
**Example**:
```python
runner.register('custom', MyCustomStrategy())
runner.list_strategies()  # ['metrics', 'marathons', 'custom']
```

---

## Advanced Usage

### Custom Data Loading

Override `load_default_data()` to load specific data:

```python
class RoutingAnalysisStrategy(AnalysisStrategy):
    def load_default_data(self) -> Dict[str, Any]:
        """Load routing-specific data."""
        from common.data_repository import load_routing_patterns
        return {'routing_data': load_routing_patterns()}
```

### Error Handling

Use `add_warning()` and `add_error()` for issues:

```python
def analyze(self, data):
    delegations = data.get('delegations', [])

    if not delegations:
        self.add_error("No delegations found")
        return AnalysisResult(name=self.get_name(), data={}, summary="Failed")

    if len(delegations) < 10:
        self.add_warning("Low sample size, results may be unreliable")

    # Continue analysis...
```

### Custom Validation

Override `validate_data()` for specific requirements:

```python
def validate_data(self, data: Dict[str, Any]) -> bool:
    if not super().validate_data(data):
        return False

    if 'sessions' not in data:
        self.add_error("Missing 'sessions' key")
        return False

    if len(data['sessions']) < 5:
        self.add_error("Need at least 5 sessions")
        return False

    return True
```

### Parameterized Strategies

Accept parameters in constructor:

```python
class MarathonAnalysisStrategy(AnalysisStrategy):
    def __init__(self, threshold: int = 20):
        super().__init__()
        self.threshold = threshold

    def analyze(self, data):
        # Use self.threshold in analysis
        marathons = [s for s in sessions if len(s['delegations']) > self.threshold]
        ...

# Use with custom threshold
strategy = MarathonAnalysisStrategy(threshold=30)
```

---

## Examples

### Example 1: Simple Agent Count Analysis

```python
from common.analysis_strategy import AnalysisStrategy, AnalysisResult
from collections import Counter

class AgentCountAnalysis(AnalysisStrategy):
    def get_name(self) -> str:
        return "Agent Usage Count"

    def analyze(self, data):
        delegations = data['delegations']
        agents = [d.get('agent_type') for d in delegations]
        counts = Counter(agents)

        return AnalysisResult(
            name=self.get_name(),
            data={'counts': dict(counts)},
            summary=f"Found {len(counts)} unique agents"
        )
```

### Example 2: Success Rate Analysis

```python
class SuccessRateAnalysis(AnalysisStrategy):
    def get_name(self) -> str:
        return "Success Rate Analysis"

    def analyze(self, data):
        delegations = data['delegations']

        total = len(delegations)
        successes = sum(1 for d in delegations if d.get('success'))
        rate = (successes / total * 100) if total > 0 else 0

        if rate < 50:
            self.add_warning(f"Low success rate: {rate:.1f}%")

        return AnalysisResult(
            name=self.get_name(),
            data={
                'total': total,
                'successes': successes,
                'success_rate': rate
            },
            summary=f"Success rate: {rate:.1f}% ({successes}/{total})"
        )
```

### Example 3: Running Multiple Analyses

```python
from analysis_runner import AnalysisRunner

# Setup
runner = AnalysisRunner(output_dir='results/')

# Register custom analyses
runner.register('agent_count', AgentCountAnalysis())
runner.register('success_rate', SuccessRateAnalysis())

# Run all
results = runner.run_all()

# Or run specific subset
results = runner.run_multiple(['agent_count', 'success_rate'])

# Generate report
report = runner.generate_report(results)
with open('report.md', 'w') as f:
    f.write(report)
```

---

## Testing Your Strategy

### Unit Test Template

```python
import pytest
from my_custom_analysis import MyCustomAnalysisStrategy

def test_analysis_with_valid_data():
    strategy = MyCustomAnalysisStrategy()

    # Mock data
    data = {
        'delegations': [
            {'agent_type': 'developer', 'success': True},
            {'agent_type': 'architect', 'success': False}
        ]
    }

    result = strategy.analyze(data)

    assert result.name == "My Custom Analysis"
    assert len(result.errors) == 0
    assert 'findings' in result.data

def test_analysis_with_empty_data():
    strategy = MyCustomAnalysisStrategy()
    data = {'delegations': []}

    result = strategy.analyze(data)

    assert len(result.errors) > 0  # Should have error
    assert result.summary.startswith("No")

def test_analysis_integration():
    # Run with real data
    strategy = MyCustomAnalysisStrategy()
    result = strategy.run()  # Loads real data

    assert result.metadata['success'] == True
```

---

## Migration Guide: Converting Existing Scripts

### Before (Old Script)

```python
# analyze_something.py
import json

with open('data/delegations.json', 'r') as f:
    delegations = json.load(f)

# Analysis logic
results = {}
for delegation in delegations:
    # ... process

print(results)
```

### After (Strategy Pattern)

```python
# strategies/something_analysis.py
from common.analysis_strategy import AnalysisStrategy, AnalysisResult

class SomethingAnalysisStrategy(AnalysisStrategy):
    def get_name(self) -> str:
        return "Something Analysis"

    def analyze(self, data):
        delegations = data['delegations']

        # Same analysis logic
        results = {}
        for delegation in delegations:
            # ... process

        return AnalysisResult(
            name=self.get_name(),
            data=results,
            summary=f"Analyzed {len(delegations)} items"
        )
```

### Benefits of Migration

✅ **Before**: Data loading duplicated in every script
✅ **After**: Centralized data loading via repository

✅ **Before**: No error handling
✅ **After**: Automatic error tracking and reporting

✅ **Before**: Inconsistent output format
✅ **After**: Standardized AnalysisResult

✅ **Before**: Cannot run multiple analyses efficiently
✅ **After**: AnalysisRunner loads data once, runs multiple

✅ **Before**: Hard to test
✅ **After**: Easy to mock data in tests

---

## Best Practices

### 1. Keep Strategies Focused

❌ **Bad**: One strategy does everything
```python
class MegaAnalysisStrategy(AnalysisStrategy):
    def analyze(self, data):
        # Metrics
        # Marathons
        # Routing
        # Failures
        # ... everything
```

✅ **Good**: Each strategy does one thing well
```python
class MetricsAnalysisStrategy(AnalysisStrategy):
    def analyze(self, data):
        # Only metrics

class MarathonAnalysisStrategy(AnalysisStrategy):
    def analyze(self, data):
        # Only marathons
```

### 2. Use Meaningful Names

❌ **Bad**: `AnalysisStrategy1`, `MyStrategy`
✅ **Good**: `MarathonAnalysisStrategy`, `RoutingQualityAnalysisStrategy`

### 3. Document What You Analyze

```python
class MyStrategy(AnalysisStrategy):
    """
    Analyzes X, Y, and Z.

    Metrics:
    - Metric A: Description
    - Metric B: Description

    Output:
    - Key 'foo': Contains bar
    - Key 'baz': Contains qux
    """
```

### 4. Handle Edge Cases

```python
def analyze(self, data):
    delegations = data.get('delegations', [])

    if not delegations:
        self.add_error("No delegations")
        return AnalysisResult(...)

    if len(delegations) < 10:
        self.add_warning("Small sample size")

    # Continue with analysis
```

### 5. Provide Clear Summaries

❌ **Bad**: `"Analysis complete"`
✅ **Good**: `"Analyzed 1,315 delegations across 128 sessions: 87% success rate, 12 marathons identified"`

---

## Troubleshooting

### Strategy Not Found

```
KeyError: Strategy 'my_custom' not found
```

**Solution**: Register the strategy:
```python
runner.register('my_custom', MyCustomStrategy())
```

### Import Errors

```
ImportError: cannot import name 'MyStrategy' from 'strategies'
```

**Solution**: Add to `strategies/__init__.py`:
```python
from .my_module import MyStrategy
__all__ = [..., 'MyStrategy']
```

### No Data Loaded

```
DataLoadError: Enriched sessions file not found
```

**Solution**: Ensure data extraction pipeline has run:
```bash
python extract_enriched_data.py
```

### Results Not Saved

**Problem**: Results not appearing in output directory

**Solution**: Check output directory permissions, or specify custom path:
```python
runner = AnalysisRunner(output_dir=Path('/writable/path'))
```

---

## Reference

### File Structure

```
delegation-retrospective/
├── common/
│   ├── analysis_strategy.py      # Base classes
│   └── data_repository.py        # Data loading
├── strategies/
│   ├── __init__.py               # Strategy exports
│   ├── metrics_analysis.py       # Metrics strategy
│   ├── marathon_analysis.py      # Marathon strategy
│   └── routing_quality_analysis.py
├── analysis_runner.py            # Orchestrator
├── examples/
│   └── custom_analysis_example.py
└── STRATEGY-PATTERN-GUIDE.md     # This file
```

### Key Classes

| Class | Purpose | File |
|-------|---------|------|
| `AnalysisStrategy` | Abstract base for all strategies | `common/analysis_strategy.py` |
| `AnalysisResult` | Standardized result format | `common/analysis_strategy.py` |
| `CompositeAnalysisStrategy` | Run multiple strategies | `common/analysis_strategy.py` |
| `AnalysisRunner` | Orchestrate strategy execution | `analysis_runner.py` |

### Related Documentation

- **ADR-004**: Architecture Decision Record for Strategy Pattern (see `ARCHITECTURE-REVIEW.md`)
- **Repository Pattern**: `common/data_repository.py` for data loading
- **Metrics Service**: `common/metrics_service.py` for token calculations

---

## Conclusion

The Strategy Pattern enables **extensible, maintainable analysis code** following SOLID principles:

- **Single Responsibility**: Each strategy analyzes one thing
- **Open/Closed**: Add new analyses without modifying existing code
- **Liskov Substitution**: All strategies interchangeable via base interface
- **Interface Segregation**: Minimal interface (get_name, analyze)
- **Dependency Inversion**: Depend on AnalysisStrategy abstraction, not concrete classes

**Next Steps**:
1. Review example: `examples/custom_analysis_example.py`
2. Create your first custom strategy
3. Run with `analysis_runner.py`
4. Add to CI/CD pipeline

**Questions?** See existing strategies for reference or consult ARCHITECTURE-REVIEW.md.
