# Analysis Pipeline Documentation

**Last Updated**: 2025-10-02
**Version**: 1.0

---

## Overview

The delegation retrospective analysis pipeline is a **multi-stage data processing system** that transforms raw Claude session data into actionable insights. The pipeline is orchestrated by `run_analysis_pipeline.py` which manages dependencies, validates prerequisites, and coordinates execution across 5 distinct stages.

### Pipeline Philosophy

- **Explicit Dependencies**: Each stage declares its inputs and outputs
- **Validation First**: Prerequisites checked before execution
- **Idempotent Execution**: Re-running stages produces consistent results
- **Incremental Processing**: Skip stages that are already complete
- **Fail Fast**: Stop on first error with clear diagnostics

---

## Quick Start

```bash
# Run full pipeline from scratch
python run_analysis_pipeline.py --all

# Preview execution plan without running
python run_analysis_pipeline.py --all --dry-run

# Resume from specific stage
python run_analysis_pipeline.py --from segmentation

# Force re-run of specific stage
python run_analysis_pipeline.py --stage analysis --force

# List all available stages
python run_analysis_pipeline.py --list-stages
```

---

## Pipeline Architecture

### Stage Execution Order

```
┌─────────────────────────────────────────────────────────────────┐
│                        PIPELINE FLOW                            │
└─────────────────────────────────────────────────────────────────┘

1. EXTRACTION
   │ Inputs:  ~/.claude/projects/**/*.jsonl (external)
   │ Scripts: extract_all_sessions.py
   │          extract_enriched_data.py
   │ Outputs: data/full_sessions_data.json
   │          data/enriched_sessions_data.json
   ↓

2. ENRICHMENT
   │ Inputs:  data/enriched_sessions_data.json
   │ Scripts: extract_routing_patterns.py
   │          classify_marathons.py
   │ Outputs: data/routing_patterns_by_period.json
   │          data/marathon-classification.json
   ↓

3. SEGMENTATION
   │ Inputs:  data/full_sessions_data.json
   │ Scripts: segment_data.py
   │ Outputs: temporal-segmentation-report.json
   ↓

4. ANALYSIS
   │ Inputs:  data/enriched_sessions_data.json
   │          data/routing_patterns_by_period.json
   │ Scripts: analysis_runner.py --all
   │ Outputs: analysis_results/aggregate_results.json
   │          analysis_results/metrics_result.json
   │          analysis_results/marathons_result.json
   │          analysis_results/routing_quality_result.json
   ↓

5. REPORTING
   │ Inputs:  data/routing_patterns_by_period.json
   │          data/routing_quality_analysis.json
   │ Scripts: generate_routing_report.py
   │ Outputs: data/routing_report.md
```

---

## Stage Details

### Stage 1: Extraction

**Purpose**: Load raw session data from Claude projects directory

**What It Does**:
- Scans `~/.claude/projects/` for all session JSONL files
- Extracts messages, agent calls, delegations
- Produces two datasets:
  - **full_sessions_data.json**: Complete session data
  - **enriched_sessions_data.json**: With delegation metadata and context

**Performance**:
- Uses file-based caching (see `file_scan_cache.py`)
- Subsequent runs skip unchanged files
- ~30-60 seconds for full scan, ~5 seconds with cache

**Scripts**:
```bash
python extract_all_sessions.py
python extract_enriched_data.py
```

**Dependencies**:
- External: `~/.claude/projects/` must exist and be readable
- Python: Standard library only

**Outputs**:
- `data/full_sessions_data.json` - All sessions with messages
- `data/enriched_sessions_data.json` - Sessions with delegation metadata

**Validation**:
- Checks Claude projects directory exists
- Validates JSON structure
- Reports sessions found and delegations extracted

---

### Stage 2: Enrichment

**Purpose**: Add metadata, cross-references, and derived data

**What It Does**:
- Extracts routing patterns by temporal period
- Classifies marathon sessions (>20 delegations)
- Adds agent interaction sequences
- Computes session-level metrics

**Scripts**:
```bash
python extract_routing_patterns.py
python classify_marathons.py
```

**Dependencies**:
- Requires: `data/enriched_sessions_data.json` (from Stage 1)

**Outputs**:
- `data/routing_patterns_by_period.json` - Routing patterns per period (P2, P3, P4)
- `data/marathon-classification.json` - Marathon session classifications

**Validation**:
- Checks input file freshness
- Validates period boundaries
- Reports patterns extracted per period

---

### Stage 3: Segmentation

**Purpose**: Divide data by temporal periods and categories

**What It Does**:
- Segments sessions into temporal periods (P1-P4)
- Maps architectural changes to periods
- Creates period statistics
- Generates temporal segmentation report

**Scripts**:
```bash
python segment_data.py
```

**Dependencies**:
- Requires: `data/full_sessions_data.json` (from Stage 1)

**Outputs**:
- `temporal-segmentation-report.json` - Period-based segmentation

**Validation**:
- Validates period date ranges
- Checks for sessions outside period boundaries
- Reports distribution across periods

---

### Stage 4: Analysis

**Purpose**: Run statistical analyses and pattern detection

**What It Does**:
- Executes multiple analysis strategies via `analysis_runner.py`
- Computes system metrics (delegation rates, success rates)
- Analyzes marathon sessions for patterns
- Evaluates routing quality across periods

**Scripts**:
```bash
python analysis_runner.py --all
```

**Analysis Strategies Executed**:
1. **MetricsAnalysis**: System-level metrics (avg delegations/session, token usage)
2. **MarathonAnalysis**: Marathon session patterns and causes
3. **RoutingQualityAnalysis**: Agent routing effectiveness

**Dependencies**:
- Requires: `data/enriched_sessions_data.json`
- Requires: `data/routing_patterns_by_period.json`

**Outputs**:
- `analysis_results/aggregate_results.json` - Combined results
- `analysis_results/metrics_result.json` - System metrics
- `analysis_results/marathons_result.json` - Marathon analysis
- `analysis_results/routing_quality_result.json` - Routing quality

**Performance**:
- Uses DataRepository for efficient loading
- Leverages caching (no duplicate loads)
- ~20-30 seconds for all analyses

---

### Stage 5: Reporting

**Purpose**: Generate human-readable markdown reports

**What It Does**:
- Synthesizes analysis results into reports
- Generates routing quality report
- Creates executive summaries
- Formats data for LLM consumption

**Scripts**:
```bash
python generate_routing_report.py
```

**Dependencies**:
- Requires: `data/routing_patterns_by_period.json`
- Requires: `data/routing_quality_analysis.json`

**Outputs**:
- `data/routing_report.md` - Routing patterns report

**Validation**:
- Checks all required analysis outputs exist
- Validates JSON structure before formatting
- Reports missing data gracefully

---

## Data Flow Diagram

```
External Sources                 Stage 1: EXTRACTION
┌─────────────────┐             ┌──────────────────────────────┐
│ ~/.claude/      │             │ extract_all_sessions.py      │
│ projects/       │────────────▶│ extract_enriched_data.py     │
│ **/*.jsonl      │             └──────────────────────────────┘
└─────────────────┘                          │
                                             ▼
                                    ┌─────────────────────┐
                                    │ full_sessions.json  │
                                    │ enriched_sessions   │
                                    └─────────────────────┘
                                             │
                            ┌────────────────┴────────────────┐
                            ▼                                 ▼
            Stage 2: ENRICHMENT                   Stage 3: SEGMENTATION
        ┌───────────────────────────┐         ┌────────────────────────┐
        │ extract_routing_patterns  │         │ segment_data.py        │
        │ classify_marathons        │         └────────────────────────┘
        └───────────────────────────┘                      │
                    │                                      ▼
                    ▼                          ┌──────────────────────┐
        ┌───────────────────────┐              │ temporal-            │
        │ routing_patterns.json │              │ segmentation.json    │
        │ marathon-class.json   │              └──────────────────────┘
        └───────────────────────┘
                    │
                    ▼
            Stage 4: ANALYSIS
        ┌───────────────────────────┐
        │ analysis_runner.py --all  │
        └───────────────────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │ aggregate_results.json    │
        │ metrics_result.json       │
        │ marathons_result.json     │
        │ routing_quality_result.json│
        └───────────────────────────┘
                    │
                    ▼
            Stage 5: REPORTING
        ┌───────────────────────────┐
        │ generate_routing_report   │
        └───────────────────────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │ routing_report.md         │
        └───────────────────────────┘
```

---

## CLI Usage Guide

### Basic Operations

#### Run Full Pipeline
```bash
python run_analysis_pipeline.py --all
```
Executes all 5 stages in order. Skips stages that are already complete unless `--force` is used.

#### Dry Run (Preview)
```bash
python run_analysis_pipeline.py --all --dry-run
```
Shows what would be executed without making any changes. Useful for:
- Validating dependencies
- Understanding execution order
- Checking for missing prerequisites

#### Run Specific Stages
```bash
python run_analysis_pipeline.py --stage extraction --stage enrichment
```
Runs only the specified stages. Validates dependencies before execution.

#### Resume from Stage
```bash
python run_analysis_pipeline.py --from segmentation
```
Runs from the specified stage onwards (segmentation, analysis, reporting).

#### Force Re-run
```bash
python run_analysis_pipeline.py --stage analysis --force
```
Forces re-execution even if outputs exist. Useful when:
- Debugging analysis scripts
- Source data changed
- Configuration updated

### Advanced Operations

#### List Available Stages
```bash
python run_analysis_pipeline.py --list-stages
```
Shows all pipeline stages with descriptions.

#### Quiet Mode
```bash
python run_analysis_pipeline.py --all --quiet
```
Suppresses progress messages. Useful for automated runs.

### Common Workflows

#### Initial Setup (First Time)
```bash
# Validate prerequisites
python run_analysis_pipeline.py --all --dry-run

# Run full pipeline
python run_analysis_pipeline.py --all
```

#### After Adding New Sessions
```bash
# Re-extract and re-analyze
python run_analysis_pipeline.py --from extraction --force
```

#### Update Analysis Only
```bash
# Skip extraction, re-run analysis
python run_analysis_pipeline.py --from analysis --force
```

#### Debug Single Stage
```bash
# Dry run to check dependencies
python run_analysis_pipeline.py --stage analysis --dry-run

# Force run with verbose output
python run_analysis_pipeline.py --stage analysis --force
```

---

## Dependency Management

### External Dependencies

**Claude Projects Directory**
- Location: `~/.claude/projects/`
- Required for: Stage 1 (Extraction)
- Validation: Checked before pipeline starts
- Error: Pipeline stops if missing

### Internal Dependencies

**Stage Dependencies**:
- **Extraction**: No dependencies (reads external data)
- **Enrichment**: Depends on Extraction outputs
- **Segmentation**: Depends on Extraction outputs
- **Analysis**: Depends on Enrichment outputs
- **Reporting**: Depends on Analysis outputs

**File Dependencies** (automatically checked):
```
extraction → enriched_sessions_data.json
           → full_sessions_data.json

enrichment → routing_patterns_by_period.json
           → marathon-classification.json

segmentation → temporal-segmentation-report.json

analysis → aggregate_results.json
         → metrics_result.json
         → marathons_result.json
         → routing_quality_result.json

reporting → routing_report.md
```

### Prerequisite Validation

The pipeline validates:
1. **External dependencies** (Claude projects directory)
2. **Stage dependencies** (prior stages completed)
3. **File dependencies** (required input files exist)
4. **Staleness** (outputs older than inputs)

**Example Error Messages**:
```
❌ Cannot execute: Depends on extraction which hasn't been run yet
❌ Missing required files: data/enriched_sessions_data.json
```

---

## Caching Strategy

### File-Level Caching

**Extraction Stage**:
- Uses `file_scan_cache.py` for file-based caching
- Caches: File metadata (mtime, size) and extracted sessions
- Cache invalidation: When source files change
- Performance gain: ~10x faster on cache hits

**Analysis Stage**:
- Uses `DataRepository` for in-memory caching
- Caches: Loaded JSON files (sessions, delegations, patterns)
- Cache scope: Single pipeline run
- Performance gain: Eliminates duplicate loads

### Stage-Level Caching

**Skip Logic**:
```python
# Stage skipped if:
1. All output files exist
2. Outputs newer than inputs
3. --force not specified
```

**Force Re-run**:
```bash
# Override cache and re-run
python run_analysis_pipeline.py --stage extraction --force
```

---

## Error Handling

### Error Categories

**1. Missing Dependencies**
```
❌ Missing external dependencies:
  - Claude projects directory: /Users/user/.claude/projects
```
**Resolution**: Ensure Claude projects directory exists

**2. Stage Dependencies Not Met**
```
❌ Cannot execute: Depends on extraction which hasn't been run yet
```
**Resolution**: Run prerequisite stages first or use `--all`

**3. Missing Input Files**
```
❌ Missing required files: data/enriched_sessions_data.json
```
**Resolution**: Run extraction stage to generate required file

**4. Script Execution Failure**
```
❌ Script failed with exit code 1
Error output:
  FileNotFoundError: data/missing_file.json
```
**Resolution**: Check script-specific errors, validate data files

**5. Timeout**
```
❌ Script timeout (>10 minutes)
```
**Resolution**: Investigate script performance, check for infinite loops

### Exit Codes

- `0`: Success - all stages completed
- `1`: Failure - stage failed or validation error

---

## Execution Logging

### Log File

**Location**: `pipeline_execution_log.json` (JSONL format)

**Content**:
```json
{"stage": "extraction", "timestamp": "2025-10-02T10:00:00", "duration_seconds": 45.2, "success": true}
{"stage": "enrichment", "timestamp": "2025-10-02T10:01:00", "duration_seconds": 12.8, "success": true}
```

**Usage**:
- Track pipeline execution history
- Measure stage performance
- Debug intermittent failures
- Generate execution reports

---

## Integration with Existing Tools

### DataRepository

The pipeline uses `common.data_repository` for centralized data loading:
```python
from common.data_repository import load_delegations, load_sessions

# Used by analysis_runner.py
delegations = load_delegations()  # Uses cache if available
sessions = load_sessions()        # Single load, shared across analyses
```

### AnalysisRunner

Stage 4 (Analysis) delegates to `analysis_runner.py`:
```python
# Pipeline calls:
python analysis_runner.py --all

# Which runs:
- MetricsAnalysisStrategy
- MarathonAnalysisStrategy
- RoutingQualityAnalysisStrategy
```

### Schema Validation

All data files use schema versioning (see `docs/SCHEMA-VERSIONING.md`):
- Version checked on load
- Incompatible versions rejected
- Migration paths documented

---

## Performance Characteristics

### Typical Execution Times

**Full Pipeline (Cold Start)**:
- Extraction: ~45 seconds
- Enrichment: ~15 seconds
- Segmentation: ~5 seconds
- Analysis: ~25 seconds
- Reporting: ~3 seconds
- **Total**: ~90 seconds

**Full Pipeline (Warm Cache)**:
- Extraction: ~8 seconds (cache hit)
- Enrichment: ~10 seconds
- Segmentation: ~3 seconds
- Analysis: ~20 seconds
- Reporting: ~2 seconds
- **Total**: ~43 seconds

**Incremental (Analysis Only)**:
- Analysis: ~25 seconds
- **Total**: ~25 seconds

### Optimization Opportunities

1. **Parallel Stage Execution**: Enrichment + Segmentation could run in parallel
2. **Streaming**: Large file processing could use streaming (already implemented in DataRepository)
3. **Incremental Updates**: Only process new sessions, not full re-extraction

---

## Troubleshooting

### Common Issues

#### "Claude projects directory not found"
```bash
# Check directory exists
ls -la ~/.claude/projects/

# If missing, check Claude installation
```

#### "Missing required files"
```bash
# Run full pipeline from scratch
python run_analysis_pipeline.py --all --force
```

#### "Outputs stale (inputs newer)"
```bash
# This is normal - pipeline will re-run automatically
# To skip, remove --force flag
```

#### "Script timeout"
```bash
# Check for performance issues
# Increase timeout in PipelineOrchestrator.execute_stage()
```

### Debug Mode

```bash
# Verbose output
python run_analysis_pipeline.py --all

# Dry run to check dependencies
python run_analysis_pipeline.py --all --dry-run

# Run single stage with full output
python run_analysis_pipeline.py --stage extraction
```

---

## Extending the Pipeline

### Adding a New Stage

1. **Define the stage** in `PipelineStage` enum:
```python
class PipelineStage(Enum):
    VALIDATION = "validation"  # New stage
```

2. **Create stage definition** in `STAGE_DEFINITIONS`:
```python
PipelineStage.VALIDATION: StageDefinition(
    stage=PipelineStage.VALIDATION,
    name="Data Validation",
    description="Validate data quality and consistency",
    scripts=["validate_data.py"],
    produces=[DATA_DIR / "validation_report.json"],
    requires=[ENRICHED_SESSIONS_FILE],
    depends_on=[PipelineStage.ENRICHMENT]
)
```

3. **Implement the script**:
```python
# validate_data.py
from common.config import ENRICHED_SESSIONS_FILE, DATA_DIR

def validate():
    # Validation logic
    pass

if __name__ == "__main__":
    validate()
```

### Adding Scripts to Existing Stage

Update the `scripts` list in stage definition:
```python
scripts=[
    "extract_routing_patterns.py",
    "classify_marathons.py",
    "new_enrichment_script.py"  # Add here
]
```

---

## Best Practices

### For Pipeline Users

1. **Always run dry-run first** when unsure about execution plan
2. **Use `--force` sparingly** - let caching work for you
3. **Check execution log** after failures for diagnostics
4. **Run full pipeline** after major data changes

### For Script Authors

1. **Exit with non-zero code on errors** - pipeline depends on this
2. **Print progress messages** - helpful for debugging
3. **Validate inputs early** - fail fast with clear messages
4. **Document outputs** - what files are created and why
5. **Use relative paths** - never hardcode absolute paths

### For Pipeline Maintainers

1. **Keep stage definitions up-to-date** when scripts change
2. **Document new stages** in this file
3. **Test full pipeline** before committing changes
4. **Update dependency graph** when adding cross-stage dependencies

---

## Future Enhancements

### Planned

- [ ] Parallel stage execution (Enrichment + Segmentation)
- [ ] Progress bars for long-running stages
- [ ] HTML report generation (Stage 6)
- [ ] Pipeline visualization (Graphviz output)

### Under Consideration

- [ ] Incremental extraction (only new sessions)
- [ ] Remote execution (cluster support)
- [ ] Web UI for pipeline monitoring
- [ ] Configurable stage definitions (YAML)

---

## References

- **Integration Analysis**: `INTEGRATION-ANALYSIS-REPORT.md` - Identified need for orchestration
- **Schema Versioning**: `docs/SCHEMA-VERSIONING.md` - Data compatibility
- **Analysis Strategies**: `common/analysis_strategy.py` - Analysis framework
- **Data Repository**: `common/data_repository.py` - Centralized data loading

---

**Questions? Issues?**
- Check execution log: `pipeline_execution_log.json`
- Run with dry-run: `--dry-run` flag
- See troubleshooting section above
