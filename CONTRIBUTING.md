# Contributing to Multi-Agent Insights

## Development Setup

```bash
# Clone repository
git clone https://github.com/duquesnay/multi-agent-insights.git
cd multi-agent-insights

# Install dependencies
pip install -r requirements-test.txt

# Verify installation
./run_tests.sh all
```

## Running Tests

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

## Architecture Overview

### Core Components

- `common/` - Core infrastructure (config, data repository, models, metrics)
- `strategies/` - Pluggable analysis modules (Strategy Pattern)
- `tests/` - Test suite (83 tests, unit + integration)
- `docs/` - Documentation

### Design Patterns

- **Repository Pattern** - Centralized data access (`data_repository.py`)
- **Strategy Pattern** - Extensible analyses (`strategies/`)
- **Builder Pattern** - Dynamic period discovery (`period_builder.py`)

See [docs/DOMAIN-MODEL.md](docs/DOMAIN-MODEL.md) and [docs/STRATEGY-PATTERN-GUIDE.md](docs/STRATEGY-PATTERN-GUIDE.md) for details.

## Code Standards

- Python 3.10+
- Type hints for public APIs
- Immutable dataclasses (`frozen=True`)
- Integration tests for critical paths
- No hardcoded paths (use `common/config.py`)

## Adding a New Analysis

1. Create strategy class in `strategies/`
2. Implement `AnalysisStrategy` interface
3. Register in `analysis_runner.py`
4. Add integration test in `tests/`

See [docs/STRATEGY-PATTERN-GUIDE.md](docs/STRATEGY-PATTERN-GUIDE.md) for step-by-step guide.

## Contribution Workflow

1. Fork repository
2. Create feature branch (`feat/your-feature`)
3. Make changes with tests
4. Run `./run_tests.sh all` (must pass)
5. Commit with conventional commits
6. Submit pull request

### Commit Format

- `feat:` - New features
- `fix:` - Bug fixes
- `refactor:` - Code improvements
- `docs:` - Documentation changes
- `test:` - Test additions/changes

## Project Commands

- `/assess-agents` - Multi-agent system assessment following methodology

## Questions?

Open an issue on GitHub for questions or discussions.
