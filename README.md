# Delegation Retrospective Analysis

Analysis toolkit for multi-agent delegation patterns in Claude Code sessions. Provides automated pipeline and scripts for extracting, analyzing, and understanding agent usage patterns, performance metrics, and collaboration workflows.

## Project Health: 8.5/10

Recent comprehensive refactoring completed (October 2025) - see `REFACTORING-COMPLETE.md` for details.

## Quick Start

```bash
# Install dependencies
pip install -r requirements-test.txt

# Run complete analysis pipeline
python run_analysis_pipeline.py --all

# Run specific analysis
python analysis_runner.py --metrics --marathons

# Run tests
./run_tests.sh all
```

## What It Does

Analyzes Claude Code agent delegation data to answer:
- **Which agents perform well?** Performance metrics, success rates, ROI
- **What delegation patterns emerge?** Routing quality, collaboration workflows
- **How efficient is the system?** Token usage, costs, throughput
- **What improves over time?** Temporal segmentation, comparative analysis

## Key Features

- **Automated Pipeline** (`run_analysis_pipeline.py`) - 5-stage workflow with smart caching
- **Typed Domain Model** - Type-safe entities (Delegation, Session, Period)
- **Strategy Pattern** - Pluggable analysis modules
- **Performance Optimized** - 3.8x faster caching, streaming for large datasets
- **Test Suite** - 83 tests (64% coverage), integration tests with real data
- **Schema Versioning** - Breaking change detection

## Documentation

### Getting Started
- **[Pipeline Guide](docs/PIPELINE.md)** - Complete pipeline documentation
- **[Testing Guide](TESTING.md)** - How to run and write tests

### Architecture
- **[Domain Model](DOMAIN-MODEL.md)** - Typed entities and business logic
- **[Strategy Pattern](STRATEGY-PATTERN-GUIDE.md)** - Adding custom analyses
- **[Schema Versioning](docs/SCHEMA-VERSIONING.md)** - Data format management

### Methodology
- **[Retrospective Methodology](METHODOLOGIE-ANALYSE-RETROSPECTIVE.md)** - Analysis framework (French)
- **[Refactoring Report](REFACTORING-COMPLETE.md)** - 3.5/10 → 8.5/10 journey

## Project Structure

```
delegation-retrospective/
├── common/                    # Core infrastructure
│   ├── config.py             # Centralized configuration
│   ├── data_repository.py    # Data access layer
│   ├── models.py             # Typed domain entities
│   ├── metrics_service.py    # Token/cost calculations
│   └── period_builder.py     # Dynamic period discovery
├── strategies/                # Analysis strategies
│   ├── metrics_analysis.py
│   ├── marathon_analysis.py
│   └── routing_quality_analysis.py
├── tests/                     # Test suite (83 tests)
├── data/                      # Extracted data and cache
├── docs/                      # Documentation
├── run_analysis_pipeline.py   # Main orchestrator
└── analysis_runner.py         # Strategy executor
```

## Usage Examples

### Full Pipeline
```bash
# Run complete workflow
python run_analysis_pipeline.py --all

# Dry-run to preview
python run_analysis_pipeline.py --all --dry-run

# Resume from specific stage
python run_analysis_pipeline.py --from segmentation
```

### Individual Analyses
```bash
# List available analyses
python analysis_runner.py --list

# Run specific analysis
python analysis_runner.py --metrics

# Run all analyses
python analysis_runner.py --all
```

### Using Typed API
```python
from common.data_repository import load_sessions

# Load as typed objects
sessions = load_sessions(typed=True)

# Type-safe business logic
marathons = [s for s in sessions if s.is_marathon()]
total_cost = sum(s.total_cost() for s in sessions)
avg_success = sum(s.success_rate() for s in sessions) / len(sessions)
```

## Development

### Running Tests
```bash
# All tests
./run_tests.sh all

# Unit tests only
./run_tests.sh unit

# Integration tests only
./run_tests.sh integration

# With coverage report
./run_tests.sh coverage
```

### Test Requirements
- **GREEN LINE**: All tests must pass (no exceptions)
- Integration tests use real data (no mocks)
- 64% coverage on critical paths

## Requirements

- Python 3.10+
- Dependencies: `ijson`, `numpy` (see `requirements-test.txt`)

## Project Status

**Active** - Used for ongoing retrospective analysis of multi-agent system evolution.

**Quality**: 8.5/10 project health after comprehensive refactoring
- Zero hardcoded paths (portable)
- Repository Pattern (DRY compliance)
- Typed domain model (type safety)
- 83 tests passing (regression prevention)
- Performance optimized (3-14.5x improvements)

See `REFACTORING-COMPLETE.md` for complete quality journey.

## Commands

Global commands available:
- `/team-assemble` - Analyze project and propose optimal agent team

Project-specific commands:
- `/assess-agents` - Multi-agent system assessment following methodology

## License

[Specify license]

## Author

Guillaume Duquesnay - Analyzing multi-agent delegation patterns in Claude Code
