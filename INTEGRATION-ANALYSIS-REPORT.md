# Integration Analysis Report

**Date**: 2025-10-02
**Analyst**: Integration Specialist
**Project**: delegation-retrospective
**Analysis Version**: 1.0

---

## Overall Integration Health: MODERATE RISK

**Summary**: The project demonstrates a loosely-coupled architecture with heavy reliance on file-based data exchange. While this provides flexibility and inspectability, it creates integration fragility through implicit contracts, hardcoded paths, and lack of centralized data management.

**Key Concerns**:
- **Critical**: No shared data loading library - duplicate code across 30+ scripts
- **High**: Hardcoded absolute paths create environment coupling
- **High**: Missing data file dependencies create silent failures
- **Medium**: No version control for data schemas
- **Medium**: Shell/Python integration relies on exit codes and file outputs

---

## System Architecture Map

### Component Categories

```
delegation-retrospective/
├── Data Extraction Layer (5 scripts)
│   ├── extract_all_sessions.py          → data/full_sessions_data.json
│   ├── extract_enriched_data.py         → data/enriched_sessions_data.json
│   ├── extract_routing_patterns.py      → data/routing_patterns_by_period.json
│   ├── extract_historical_snapshots.py  → data/historical/*.json
│   └── copy_conversations.py            → data/conversations/**/*.jsonl
│
├── Data Segmentation Layer (2 scripts)
│   ├── segment_data.py                  → temporal-segmentation-report.json
│   └── segment_timeline_extended.py     → data/timeline-extended-segmentation.json
│
├── Analysis Layer (20+ scripts)
│   ├── analyze_delegations.py           (reads: delegation_raw.jsonl)
│   ├── analyze_marathons.py             (reads: enriched_sessions_data.json)
│   ├── analyze_roi.py                   (reads: delegation_raw.jsonl, writes: roi_analysis.json)
│   ├── analyze_routing_quality.py       (reads: routing_patterns_by_period.json)
│   ├── analyze_temporal_patterns.py     (reads: timeline_data.csv + 3 agent CSVs)
│   └── [15+ other analysis scripts]
│
├── Report Generation Layer (3 scripts)
│   ├── generate_routing_report.py       (reads: 3 JSON files, outputs markdown)
│   ├── classification-framework.py      (generic template)
│   └── [shell script wrappers]
│
└── Utility Layer
    ├── Shell scripts (12 .sh files)
    └── consolidate_all_data.py
```

### Data Flow Diagram

```
External Data Sources
└── ~/.claude/projects/**/*.jsonl
    │
    ↓ [copy_conversations.py, extract_all_sessions.py]
    │
data/raw/delegation_raw.jsonl
data/full_sessions_data.json
data/conversations/**/*.jsonl
    │
    ↓ [extract_enriched_data.py, extract_routing_patterns.py]
    │
data/enriched_sessions_data.json
data/routing_patterns_by_period.json
    │
    ↓ [segment_data.py]
    │
temporal-segmentation-report.json
    │
    ↓ [20+ analyze_*.py scripts - PARALLEL]
    │
    ├── data/roi_analysis.json
    ├── data/routing_quality_analysis.json
    ├── data/good_routing_patterns.json
    ├── data/marathon-classification.json
    └── [10+ other intermediate JSON files]
        │
        ↓ [generate_routing_report.py, LLM agents]
        │
    Markdown Reports (observations-v*.md, SYNTHESE-*.md)
```

---

## System Touchpoints

### 1. Python ↔ Data Files

**Pattern**: Direct file I/O with hardcoded paths

**Examples**:
```python
# CRITICAL COUPLING: Absolute paths
with open('/Users/guillaume/dev/tasks/delegation-retrospective/data/routing_patterns_by_period.json', 'r') as f:

# BETTER: Relative paths (but still fragile)
with open('data/full_sessions_data.json', 'r') as f:
```

**Integration Contract**:
- **Format**: JSON/JSONL/CSV (no schema validation)
- **Location**: `data/` subdirectories (raw, processed, historical)
- **Naming**: Implicit conventions (no registry)

**Failure Modes**:
- Missing file → FileNotFoundError (no graceful degradation)
- Schema mismatch → KeyError or silent incorrect results
- Path changes → Broken scripts requiring manual updates

### 2. Python ↔ Shell Scripts

**Pattern**: Shell scripts invoke Python, check exit codes

**Examples**:
```bash
# scripts/temporal_analysis.sh
python3 segment_data.py || exit 1
python3 analyze_temporal_patterns.py
```

**Integration Contract**:
- **Communication**: Exit codes (0 = success, non-zero = failure)
- **Data Exchange**: Files written by Python, read by next process
- **Coordination**: Sequential execution via `&&` or `;`

**Failure Modes**:
- Python script fails → Shell continues with stale data
- Missing output file → Next script fails with unclear error
- Non-zero exit without error handling → Pipeline stops

### 3. External Data Source Dependencies

**Critical External Dependency**: `~/.claude/projects/`

**Scripts Accessing External Data**:
1. `extract_all_sessions.py` - Scans ALL project directories
2. `extract_enriched_data.py` - Reads from projects directory
3. `copy_conversations.py` - Incremental copy from projects
4. `extract_historical_snapshots.py` - Historical data extraction

**Integration Risk**: **HIGH**
- No versioning of source data
- No snapshot mechanism (live data can change)
- No error handling for missing/moved projects
- Breaks if `~/.claude/projects/` structure changes

### 4. Cross-Script Data Dependencies

**Data Dependency Graph** (critical paths):

```
extract_all_sessions.py
    ↓ produces: data/full_sessions_data.json
    ↓ consumed by: segment_data.py

extract_enriched_data.py
    ↓ produces: data/enriched_sessions_data.json
    ↓ consumed by: analyze_marathons.py, analyze_p4_marathons.py, classify_marathons.py

extract_routing_patterns.py
    ↓ produces: data/routing_patterns_by_period.json
    ↓ consumed by: analyze_routing_quality.py, analyze_transitions.py, generate_routing_report.py

analyze_roi.py
    ↓ produces: data/roi_analysis.json
    ↓ consumed by: surprising_insights.py, deep_roi_analysis.py
```

**Fragility**: No explicit dependency management. Scripts assume files exist.

---

## Integration Issues

### Critical - Breaking Risks

#### 1. **No Centralized Data Loading Library**

**Impact**: 30+ scripts each implement their own data loading
**Risk**: Inconsistent error handling, duplicate code, schema drift

**Evidence**:
```python
# Pattern repeated in 15+ scripts:
def load_delegations(filepath: str) -> List[Dict]:
    delegations = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    delegations.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Erreur parsing ligne: {e}", file=sys.stderr)
    return delegations
```

**Mitigation**: Create `utils/data_loader.py` with:
- Centralized file loading functions
- Schema validation
- Error handling
- Path resolution

#### 2. **Hardcoded Absolute Paths**

**Impact**: Environment-specific coupling, breaks on different machines
**Risk**: Scripts fail when run outside specific environment

**Evidence**:
- 12 scripts use `/Users/guillaume/dev/tasks/delegation-retrospective/`
- No use of `Path(__file__).parent` for relative resolution
- Breaks if project moved or run by different user

**Affected Scripts**:
- `analyze_routing_quality.py`
- `generate_routing_report.py`
- `roi_analysis_detailed.py`
- `analyze_tokens_roi.py`
- `prompt_analysis.py`
- `communication_analysis.py`
- (6+ more)

**Mitigation**: Standardize path resolution:
```python
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
```

#### 3. **Missing Data File = Silent Failure or Crash**

**Impact**: Scripts crash with unclear errors when dependencies missing
**Risk**: Difficult to debug, unclear execution order requirements

**Evidence**:
```python
# No existence check before opening
with open('data/full_sessions_data.json', 'r') as f:  # FileNotFoundError if missing
    data = json.load(f)
```

**Mitigation**: Add pre-flight checks:
```python
def ensure_data_file(filepath: Path, script_name: str):
    if not filepath.exists():
        print(f"ERROR: {script_name} requires {filepath}")
        print(f"Run extraction scripts first:")
        print(f"  - extract_all_sessions.py")
        sys.exit(1)
```

### High Priority - Coupling Concerns

#### 4. **No Data Schema Versioning**

**Impact**: Schema changes break downstream consumers silently
**Risk**: Incorrect analysis results, not obvious failures

**Example**:
- `enriched_sessions_data.json` structure changed between analysis versions
- Scripts written for v6.0 may fail on v7.1 data
- No version field in data files to detect incompatibility

**Mitigation**:
- Add version metadata to all JSON files:
  ```json
  {
    "schema_version": "2.0",
    "generated_by": "extract_enriched_data.py",
    "generated_at": "2025-10-02T09:00:00Z",
    "data": { ... }
  }
  ```
- Validate schema version in consumers

#### 5. **Duplicate Data Extraction Logic**

**Impact**: Inconsistent extraction, maintenance burden
**Risk**: Different scripts extract same data differently

**Evidence**:
- `extract_all_sessions.py` scans `~/.claude/projects/`
- `extract_enriched_data.py` ALSO scans `~/.claude/projects/`
- `copy_conversations.py` ALSO scans `~/.claude/projects/`

**Why Risky**:
- If external data structure changes, must update 3+ scripts
- Extraction logic can diverge (different filtering, parsing)
- No guarantee outputs are consistent

**Mitigation**: Single source of truth for data extraction

#### 6. **Shell Script Complexity Without Error Handling**

**Impact**: Pipeline failures are obscure
**Risk**: Partial execution with unclear state

**Evidence** (`scripts/temporal_analysis.sh`):
```bash
#!/bin/bash
python3 segment_data.py
python3 analyze_temporal_patterns.py
python3 generate_routing_report.py
# No error checking between steps
# If segment_data.py fails, analyze_temporal_patterns.py runs anyway
```

**Mitigation**: Add error handling:
```bash
#!/bin/bash
set -e  # Exit on first error
set -o pipefail  # Catch errors in pipes

python3 segment_data.py || {
    echo "ERROR: segment_data.py failed"
    exit 1
}
```

### Medium Priority - Improvement Opportunities

#### 7. **No Execution Order Documentation**

**Impact**: Unclear which scripts to run in what order
**Risk**: Running analysis before extraction → missing dependencies

**Current State**: Execution order inferred from code reading
**Missing**: Dependency graph or Makefile

**Mitigation**: Create `Makefile` or `run_analysis.sh`:
```makefile
.PHONY: extract segment analyze report

extract:
    python3 extract_all_sessions.py
    python3 extract_enriched_data.py
    python3 extract_routing_patterns.py

segment: extract
    python3 segment_data.py

analyze: segment
    python3 analyze_delegations.py
    python3 analyze_marathons.py
    # ... other analyses

report: analyze
    python3 generate_routing_report.py
```

#### 8. **No Intermediate Result Caching Strategy**

**Impact**: Re-run expensive extractions unnecessarily
**Risk**: Waste time, inconsistent results if source data changes mid-analysis

**Evidence**:
- No timestamp/hash checking for cached files
- No `--force` flag to bypass cache
- Unclear when to regenerate vs reuse

**Mitigation**: Add cache invalidation:
```python
def load_or_extract(cache_file: Path, extractor_fn, force=False):
    if cache_file.exists() and not force:
        cache_age = time.time() - cache_file.stat().st_mtime
        if cache_age < 3600:  # 1 hour
            return json.loads(cache_file.read_text())

    data = extractor_fn()
    cache_file.write_text(json.dumps(data))
    return data
```

#### 9. **Python Standard Library Only (Good) + numpy Exception**

**Impact**: Low external dependency risk, but numpy adds fragility
**Risk**: `roi_analysis_detailed.py` fails if numpy not installed

**Evidence**:
```python
# roi_analysis_detailed.py
import numpy as np  # Only script using numpy
```

**Mitigation**:
- Document numpy requirement in README
- Add optional dependency handling:
  ```python
  try:
      import numpy as np
      HAS_NUMPY = True
  except ImportError:
      HAS_NUMPY = False
      # Fallback to statistics module
  ```

#### 10. **Data Files in Multiple Locations**

**Impact**: Unclear canonical data location
**Risk**: Stale duplicates, version confusion

**Locations**:
- `/Users/guillaume/dev/tasks/delegation-retrospective/data/`
- `/Users/guillaume/dev/tasks/delegation-retrospective/` (root-level JSON)
- `/Users/guillaume/dev/tasks/delegation-retrospective/analyses/*/`

**Example Duplication**:
- `temporal-segmentation-report.json` (root)
- `data/timeline-extended-segmentation.json`
- `analyses/v8.0-mai-septembre-2025/temporal-*.json`

**Mitigation**: Consolidate to single `data/` directory

---

## Dependency Analysis

### External Dependencies

#### System Dependencies
- **Python 3.x** (required)
- **Bash shell** (required for shell scripts)
- **Git** (used by `find_marathon_repos.sh`, git validation scripts)
- **jq** (potentially - not confirmed in all shell scripts)

#### Python Packages (Standard Library)
- `json` - Universal across all scripts
- `sys` - Process control, exit codes
- `collections` (defaultdict, Counter) - Data aggregation
- `datetime` - Timestamp parsing
- `pathlib` - Path manipulation (used in 10+ scripts)
- `re` - Pattern extraction
- `statistics` - Metrics calculation
- `csv` - Data export

#### Python Packages (External)
- **numpy** - Used ONLY in `roi_analysis_detailed.py`
  - **Risk**: Single point of failure if not installed
  - **Mitigation**: Make optional or add requirements.txt

#### External Data Sources
- **~/.claude/projects/**/*.jsonl** - CRITICAL dependency
  - No fallback if directory missing
  - No versioning/snapshotting
  - Live data can change during analysis

### Internal Dependencies

#### Data File Dependencies (Directed Graph)

```
Sources (No dependencies):
- ~/.claude/projects/**/*.jsonl

Tier 1 (Extract from sources):
- data/full_sessions_data.json
- data/enriched_sessions_data.json
- data/conversations/**/*.jsonl
- data/raw/delegation_raw.jsonl

Tier 2 (Process Tier 1):
- temporal-segmentation-report.json (from full_sessions_data.json)
- data/routing_patterns_by_period.json (from enriched_sessions_data.json)
- data/historical/*.json (from conversations)

Tier 3 (Analyze Tier 2):
- data/roi_analysis.json
- data/routing_quality_analysis.json
- data/marathon-classification.json
- data/good_routing_patterns.json
- data/transition_analysis.json

Tier 4 (Reports from Tier 3):
- Markdown reports (observations-*.md, SYNTHESE-*.md)
```

#### Cross-Module Dependencies

**No shared Python modules** - Each script is standalone
- **Pro**: No import dependency hell
- **Con**: Massive code duplication (data loading, parsing)

**Shared by Convention**:
- Data file formats (JSON/JSONL structure)
- Timestamp format (ISO 8601)
- Agent name conventions
- Session ID format

---

## Integration Risks & Mitigation

### Risk 1: Source Data Changes Mid-Analysis
**Severity**: HIGH
**Probability**: MEDIUM

**Scenario**: User runs `extract_all_sessions.py` on Monday, then `analyze_marathons.py` on Wednesday after new sessions added to `~/.claude/projects/`

**Impact**:
- Inconsistent analysis (some scripts see new data, others don't)
- Comparative analysis invalid (different baselines)

**Mitigation**:
1. **Snapshot on extraction**: Copy all source files to `data/snapshots/YYYY-MM-DD/`
2. **Lock analysis runs**: All scripts use same snapshot
3. **Metadata tracking**: Record extraction timestamp in all outputs

**Implementation**:
```python
# Extract with snapshot
SNAPSHOT_DIR = DATA_DIR / "snapshots" / datetime.now().strftime("%Y-%m-%d")
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

# All subsequent scripts read from snapshot, not live data
```

### Risk 2: Path Breakage on Environment Changes
**Severity**: CRITICAL
**Probability**: HIGH (currently broken on any machine except developer's)

**Scenario**: Another developer clones project, runs scripts

**Impact**: 12+ scripts immediately fail with hardcoded path errors

**Mitigation**:
- **Immediate**: Replace all absolute paths with relative paths
- **Robust**: Use environment variable for project root
- **Best**: Use `Path(__file__).resolve().parent` pattern

**Action Items**:
- [ ] Audit all Python files for hardcoded paths
- [ ] Create `utils/paths.py` with path constants
- [ ] Refactor all scripts to use centralized paths

### Risk 3: Missing Execution Prerequisite Files
**Severity**: MEDIUM
**Probability**: HIGH

**Scenario**: User runs analysis script before running extraction

**Impact**: Cryptic FileNotFoundError, unclear what to run first

**Mitigation**:
1. **Dependency checks**: Each script validates prerequisites at startup
2. **Clear error messages**: Tell user exactly what's missing and how to fix
3. **Makefile/orchestration**: Automated dependency execution

**Implementation**:
```python
# At top of analyze_marathons.py
REQUIRED_FILES = [
    DATA_DIR / "enriched_sessions_data.json",
]

for required_file in REQUIRED_FILES:
    if not required_file.exists():
        print(f"ERROR: Missing required file: {required_file}")
        print("Run data extraction first:")
        print("  python3 extract_enriched_data.py")
        sys.exit(1)
```

### Risk 4: Schema Evolution Breaking Consumers
**Severity**: MEDIUM
**Probability**: MEDIUM

**Scenario**: `extract_enriched_data.py` updated to add new fields, remove old fields

**Impact**: Analysis scripts expecting old schema break or produce wrong results

**Mitigation**:
1. **Schema versioning**: Include version in all data files
2. **Compatibility checks**: Scripts validate schema version before processing
3. **Migration scripts**: Convert old data to new schema

**Implementation**:
```python
# In data files
{
    "schema_version": "2.1",
    "format": "enriched_sessions",
    "generated_at": "2025-10-02T09:00:00Z",
    "sessions": [...]
}

# In consumer scripts
SUPPORTED_VERSIONS = ["2.0", "2.1"]
data_version = data.get("schema_version", "1.0")
if data_version not in SUPPORTED_VERSIONS:
    print(f"ERROR: Unsupported data schema version {data_version}")
    print(f"This script supports: {SUPPORTED_VERSIONS}")
    sys.exit(1)
```

### Risk 5: numpy Dependency Fragility
**Severity**: LOW
**Probability**: LOW (but certain on fresh environment)

**Scenario**: New user runs `roi_analysis_detailed.py` without numpy installed

**Impact**: ImportError, analysis fails

**Mitigation**:
1. **Document dependency**: Add requirements.txt
2. **Graceful degradation**: Make numpy optional, use statistics module fallback
3. **Validation**: Startup check with clear instructions

**Action Items**:
- [ ] Create requirements.txt with numpy
- [ ] Add optional import handling in roi_analysis_detailed.py
- [ ] Document installation in README

---

## Recommended Action Items

### Immediate (Breaking Issues)

- [ ] **Create centralized data loader library** (`utils/data_loader.py`)
  - Standardize JSON/JSONL loading
  - Add error handling and validation
  - Include schema version checking

- [ ] **Replace all hardcoded absolute paths**
  - Audit 30+ Python scripts
  - Use `Path(__file__).resolve().parent` pattern
  - Create `utils/paths.py` for constants

- [ ] **Add prerequisite checks to all analysis scripts**
  - Validate required input files exist
  - Print clear error messages with remediation steps
  - Exit with non-zero code on missing dependencies

### High Priority (Coupling Reduction)

- [ ] **Implement data schema versioning**
  - Add version metadata to all JSON outputs
  - Create schema documentation
  - Add version validation in consumers

- [ ] **Create execution orchestration**
  - Write Makefile or master script
  - Document dependency graph visually
  - Add `--check-only` mode for dry runs

- [ ] **Add snapshot mechanism for source data**
  - Copy `~/.claude/projects/` to dated snapshot
  - Point all scripts at snapshot, not live data
  - Track which snapshot each analysis used

- [ ] **Consolidate duplicate extraction logic**
  - Single source of truth for scanning `~/.claude/projects/`
  - Shared parsing functions
  - Consistent error handling

### Medium Priority (Maintainability)

- [ ] **Add caching strategy**
  - Timestamp-based cache invalidation
  - `--force` flag to bypass cache
  - Clear cache expiry documentation

- [ ] **Create requirements.txt**
  - Document numpy dependency
  - Add version constraints
  - Include installation instructions

- [ ] **Improve shell script robustness**
  - Add `set -e` and `set -o pipefail`
  - Check exit codes between steps
  - Print progress/status messages

- [ ] **Consolidate data file locations**
  - Move all data to `data/` subdirectories
  - Remove root-level JSON files
  - Clear separation: raw, processed, analysis, reports

### Low Priority (Quality of Life)

- [ ] **Add logging framework**
  - Replace print statements with proper logging
  - Configurable log levels
  - Log files for troubleshooting

- [ ] **Create data file registry**
  - Central documentation of all data files
  - Schema documentation
  - Dependency graph

- [ ] **Add unit tests for data loaders**
  - Test JSON parsing edge cases
  - Validate error handling
  - Test path resolution

---

## Integration Best Practices Violations

### Current State vs. Best Practices

| Best Practice | Current State | Risk Level |
|---------------|---------------|------------|
| **Centralized configuration** | Hardcoded paths in 30+ files | HIGH |
| **Explicit dependencies** | Implicit file dependencies | HIGH |
| **Error handling** | Minimal, inconsistent | MEDIUM |
| **Schema validation** | None | MEDIUM |
| **Version control** | No data schema versioning | MEDIUM |
| **Idempotency** | Not guaranteed (re-runs may differ) | MEDIUM |
| **Documentation** | No dependency graph docs | LOW |
| **Testing** | No automated tests | LOW |

---

## Conclusion

The delegation-retrospective project demonstrates a **pragmatic analysis architecture** optimized for exploratory research rather than production robustness. The file-based integration pattern provides:

**Strengths**:
- Inspectability (data files can be examined directly)
- Flexibility (easy to add new analysis scripts)
- Simplicity (minimal dependencies)
- Parallelizability (analyses can run independently)

**Weaknesses**:
- Fragility (missing files, path changes break system)
- Duplication (data loading logic repeated 30+ times)
- Unclear execution order
- Environment coupling (hardcoded paths)
- No versioning strategy

**Overall Assessment**: Suitable for single-developer research context, but requires **integration hardening** before multi-developer use or long-term maintenance.

**Priority Actions**:
1. Fix hardcoded path coupling (CRITICAL)
2. Create shared data loader utility (CRITICAL)
3. Add prerequisite validation (HIGH)
4. Document execution dependencies (HIGH)

**Estimated Effort**: 1-2 days to address critical integration risks and create stable foundation for ongoing analysis work.

---

## Appendix: Integration Checklist for New Scripts

When adding new analysis scripts to this project, ensure:

- [ ] Use relative paths with `Path(__file__).resolve().parent`
- [ ] Check for required data files at startup (with helpful error messages)
- [ ] Include schema version in JSON outputs
- [ ] Validate schema version of input files
- [ ] Use standard library when possible (document if adding dependencies)
- [ ] Exit with non-zero code on errors
- [ ] Print clear progress/status messages
- [ ] Follow naming convention: `analyze_*.py` or `extract_*.py`
- [ ] Output to `data/` subdirectory (not root)
- [ ] Add script to execution documentation/Makefile

