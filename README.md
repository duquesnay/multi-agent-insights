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

## Features

- Automated 5-stage analysis pipeline
- Temporal segmentation across system evolution
- Performance metrics (tokens, costs, throughput)
- Routing quality and collaboration patterns

## Analyzing Your Multi-Agent System

Use the `/assess-agents` command in Claude Code to analyze your agent delegation patterns:

```
/assess-agents project cold-chamber-ui
```

This generates a comprehensive assessment including:
- Agent adoption rates and usage patterns
- Collaboration workflows between agents
- Routing quality and efficiency metrics
- Temporal analysis across system evolution

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
```

## Documentation

- **[Pipeline Guide](docs/PIPELINE.md)** - Complete pipeline documentation
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup and standards

## Requirements

- Python 3.10+
- Dependencies: `ijson`, `numpy` (see `requirements-test.txt`)

## License

[Specify license]

## Author

Guillaume Duquesnay
