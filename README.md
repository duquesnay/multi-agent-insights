# Multi-Agent Insights

Analysis toolkit for multi-agent delegation patterns in Claude Code sessions. Provides automated pipeline and scripts for extracting, analyzing, and understanding agent usage patterns, performance metrics, and collaboration workflows.

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
- **[Testing Guide](docs/TESTING.md)** - How to run and write tests

### Architecture
- **[Domain Model](docs/DOMAIN-MODEL.md)** - Typed entities and business logic
- **[Strategy Pattern](docs/STRATEGY-PATTERN-GUIDE.md)** - Adding custom analyses
- **[Schema Versioning](docs/SCHEMA-VERSIONING.md)** - Data format management
- **[Streaming Migration](docs/STREAMING_MIGRATION_GUIDE.md)** - Large dataset handling

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

## Requirements

- Python 3.10+
- Dependencies: `ijson`, `numpy` (see `requirements-test.txt`)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and contribution guidelines.

## License

[Specify license]

## Author

Guillaume Duquesnay - Analyzing multi-agent delegation patterns in Claude Code
