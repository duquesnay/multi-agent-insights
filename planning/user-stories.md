# User Stories - Delegation Retrospective

## Critical Foundation Stories

### INFRA1: Configure paths work across environments

**User**: Data analyst running analysis on different machine
**Outcome**: Scripts execute without path modification when project location changes
**Context**: Currently 29 hardcoded absolute paths break portability

**Acceptance Criteria**:
- All scripts use Path(__file__).resolve().parent for path resolution
- No hardcoded `/Users/guillaume/` paths remain
- Create common/config.py with PROJECT_ROOT, DATA_DIR, RAW_DATA_DIR constants
- All 30+ scripts updated to import from config
- Scripts run successfully on macOS and Linux

**Implementation Notes**:
- Replace all instances of `/Users/guillaume/dev/tasks/delegation-retrospective/`
- Use pathlib.Path for cross-platform compatibility
- Test on second machine to verify portability

**Source**: CODE_QUALITY_ANALYSIS.md C3, INTEGRATION-ANALYSIS-REPORT.md Critical #2

---

### INFRA2: Access delegation data through single repository

**User**: Developer adding new analysis script
**Outcome**: Load delegation data with one function call, consistent error handling
**Context**: 40+ scripts duplicate data loading logic with inconsistent behavior

**Acceptance Criteria**:
- Create common/data_access.py with DelegationRepository class
- Single load_delegations() implementation with error handling
- Support filtering by period, session, agent without code duplication
- All existing scripts migrated to use repository
- Zero code duplication for data loading across codebase

**Implementation Notes**:
- Implement Repository Pattern (ARCHITECTURE-REVIEW.md ADR-002)
- Include schema validation, graceful error messages
- Cache parsed delegations to avoid re-parsing

**Source**: CODE_QUALITY_ANALYSIS.md C1, ARCHITECTURE-REVIEW.md Critical #1, INTEGRATION-ANALYSIS-REPORT.md Critical #1

---

### INFRA3: Extract token metrics through centralized service

**User**: Analyst comparing token efficiency across periods
**Outcome**: Token metrics calculated consistently across all analyses
**Context**: Token extraction duplicated with different field names causing inconsistencies

**Acceptance Criteria**:
- Create common/metrics.py with TokenMetrics dataclass
- Single extract_token_metrics() implementation
- Consistent field names (input_tokens, output_tokens, cache_read, cache_write)
- Amplification ratio calculated uniformly
- All scripts (analyze_metrics.py, roi_analysis_detailed.py, etc.) use centralized extractor

**Implementation Notes**:
- Use @dataclass for type safety
- Include validation for edge cases (zero input tokens)
- Add property methods for derived metrics (amplification_ratio)

**Source**: CODE_QUALITY_ANALYSIS.md C2

---

## High Priority Architecture Stories

### ARCH1: Define typed domain entities for analysis

**User**: Developer refactoring analysis logic
**Outcome**: Type-safe domain objects with IDE autocomplete and business logic encapsulation
**Context**: Everything is Dict[str, Any] causing type safety issues and scattered logic

**Acceptance Criteria**:
- Create domain/models.py with Delegation, Session, Period, Agent dataclasses
- All business logic methods encapsulated (session.is_marathon(), delegation.amplification_ratio)
- Factory methods for construction: Delegation.from_dict(raw_json)
- Type hints throughout enable mypy validation
- Migrate one analysis script as proof of concept

**Implementation Notes**:
- Use @dataclass with frozen=True for immutability where appropriate
- Include __post_init__ validation
- Provide clear error messages for invalid data

**Source**: ARCHITECTURE-REVIEW.md ADR-001, Critical #6

---

### ARCH2: Build period boundaries from git history dynamically

**User**: Analyst running retrospective for different time range
**Outcome**: Period boundaries discovered from git archaeology, not hardcoded
**Context**: Methodology prescribes "Git archaeology FIRST" but code hardcodes Sept dates

**Acceptance Criteria**:
- Create domain/period_builder.py with PeriodBuilder class
- from_git_archaeology() method discovers config change dates
- No hardcoded dates in segment_data.py or extract_routing_patterns.py
- Supports both automatic discovery and manual override (for testing)
- Works for v8.0 analysis (May-Sept 2025) without code changes

**Implementation Notes**:
- Parse git log of ~/.claude/memories/retrospective-agents.md
- Detect architectural changes (new agents, policy changes)
- Create Period objects with metadata (name, config_changes)

**Source**: ARCHITECTURE-REVIEW.md ADR-003, Critical #4

---

### ARCH3: Execute analyses through strategy pattern

**User**: Developer adding new analysis dimension
**Outcome**: Add analysis without modifying existing code (Open/Closed principle)
**Context**: Analysis logic tightly coupled, hard to extend

**Acceptance Criteria**:
- Create strategies/base.py with AnalysisStrategy interface
- Implement RoutingAnalysisStrategy, MarathonAnalysisStrategy, FailureAnalysisStrategy
- Orchestrator executes strategies in parallel where independent
- New analysis = new strategy class, no core modifications
- Migrate 3 existing analyses as proof of concept

**Implementation Notes**:
- Use ABC (Abstract Base Class) for interface definition
- Include analyze() method returning AnalysisResult
- Support strategy composition for complex analyses

**Source**: ARCHITECTURE-REVIEW.md ADR-004, Missing Pattern #2

---

## High Priority Performance Stories

### PERF1: Detect marathon loops in linear time

**User**: Analyst running marathon analysis on 50-delegation sessions
**Outcome**: Loop detection completes in <500ms (vs 5s currently)
**Context**: Quadratic O(n²) loop in analyze_marathons.py performs 2,500 comparisons per session

**Acceptance Criteria**:
- Rewrite loop detection using sliding window + deque (O(n) complexity)
- Handles 50-delegation marathons in <500ms
- Detects all A→B→A patterns correctly (no false negatives)
- No performance degradation for small sessions
- Benchmark shows 10-100x speedup for large sessions

**Implementation Notes**:
- Use collections.deque with maxlen=3 for sliding window
- Hash-based pattern detection instead of nested loops
- Add performance benchmark to validate improvement

**Source**: PERFORMANCE_ANALYSIS_REPORT.md Bottleneck #1

---

### PERF2: Access cached file scans for unchanged data

**User**: Analyst re-running analysis after small data update
**Outcome**: File scan completes in <1s (vs 5s) when most files unchanged
**Context**: Full recursive scan of ~/.claude/projects/ on every run wastes time

**Acceptance Criteria**:
- Cache file metadata (mtime, size) in data/.file_scan_cache.pkl
- Check file hash before rescanning unchanged files
- Print "Scanned N changed files (skipped M cached)" message
- 5-10x speedup for repeated runs with unchanged data
- Automatic cache invalidation on file modification

**Implementation Notes**:
- Use pickle for cache persistence
- Store file_path → (mtime, size, parsed_data) mapping
- Include cache TTL for safety (1 hour)

**Source**: PERFORMANCE_ANALYSIS_REPORT.md Bottleneck #2

---

### PERF3: Stream large JSON files efficiently

**User**: System processing 67MB enriched_sessions_data.json
**Outcome**: Peak memory usage stays under 100MB (vs 200MB with full load)
**Context**: Full file loading causes memory issues at 10x scale

**Acceptance Criteria**:
- Install and use ijson for streaming JSON parsing
- load_sessions_streaming() yields sessions one at a time
- Early filtering reduces memory footprint
- Handles 67MB files without memory pressure
- 5-10x memory reduction measured

**Implementation Notes**:
- Use ijson.items(f, 'sessions.item') for incremental parsing
- Apply filters during parsing (before loading into memory)
- Refactor consumers to accept generators instead of lists

**Source**: PERFORMANCE_ANALYSIS_REPORT.md Bottleneck #3

---

### PERF4: Match routing patterns with compiled regex

**User**: Analyst running routing quality analysis on 1,246 delegations
**Outcome**: Pattern matching completes in <500ms (vs 2s currently)
**Context**: Repeated string operations and keyword checks are inefficient

**Acceptance Criteria**:
- Compile regex patterns once at module level
- Use @lru_cache for classification results
- Single scan with all patterns (not 5+ separate checks)
- 3-5x speedup for routing analysis
- No change in detection accuracy

**Implementation Notes**:
- Create MISROUTING_PATTERNS dict with compiled re.compile() patterns
- Use word boundaries (\b) for accurate matching
- Cache combined text classification results

**Source**: PERFORMANCE_ANALYSIS_REPORT.md Bottleneck #4

---

### PERF5: Analyze patterns in single pass

**User**: System processing delegation data
**Outcome**: Pattern analysis completes 20-30% faster with better cache locality
**Context**: Multiple passes over same data causes cache misses

**Acceptance Criteria**:
- Consolidate 4 separate passes into one loop
- Compute temporal, agent, session, complexity metrics in single pass
- Measured 20-30% performance improvement
- Results identical to multi-pass version
- Memory usage comparable or better

**Implementation Notes**:
- Use defaultdict to collect metrics during single iteration
- Post-process aggregations after loop completes
- Free intermediate data structures promptly

**Source**: PERFORMANCE_ANALYSIS_REPORT.md Bottleneck #5

---

## Medium Priority Quality Stories

### QUAL1: Validate data through comprehensive test suite

**User**: Developer refactoring metric calculations
**Outcome**: Changes validated by passing test suite, regressions caught immediately
**Context**: Zero test coverage creates regression risk during refactoring

**Acceptance Criteria**:
- Create tests/ directory with unit and integration tests
- 70% code coverage for core calculations (metrics, classification)
- Tests for edge cases (missing data, zero tokens, invalid dates)
- CI integration (pytest runs on commit)
- All tests passing before backlog completion

**Implementation Notes**:
- Start with test_metrics.py for token extraction
- Test boundary conditions and error handling
- Use fixtures for test data

**Source**: CODE_QUALITY_ANALYSIS.md M3

---

### DATA1: Version data schemas to prevent breaks

**User**: Analyst using data files from different analysis versions
**Outcome**: Clear error when schema incompatibility detected, no silent failures
**Context**: Schema changes break downstream consumers with unclear errors

**Acceptance Criteria**:
- All JSON outputs include schema_version, generated_by, generated_at metadata
- Consumers validate schema version before processing
- Schema documentation in ARCHITECTURE.md
- Migration scripts for schema upgrades
- Clear error messages on version mismatch

**Implementation Notes**:
- Wrap data in {schema_version: "2.0", data: {...}} envelope
- Use semantic versioning for schemas
- Include SUPPORTED_VERSIONS list in consumers

**Source**: INTEGRATION-ANALYSIS-REPORT.md High #4

---

### ARCH4: Orchestrate analysis pipeline systematically

**User**: New developer running full analysis
**Outcome**: Single command executes entire pipeline in correct order
**Context**: Unclear execution order, manual script running error-prone

**Acceptance Criteria**:
- Create Makefile or run_analysis.py with dependency graph
- Phases: extract → segment → analyze → report
- Error handling stops pipeline on failure
- Progress reporting shows current step
- Documented in README with visual dependency graph

**Implementation Notes**:
- Use Make targets or Python orchestration
- Include --check-only dry run mode
- Validate prerequisites before execution

**Source**: INTEGRATION-ANALYSIS-REPORT.md Medium #7

---

## Lower Priority Polish Stories

### PERF6: Parse JSON with orjson library

**User**: System loading JSONL files
**Outcome**: 2-3x faster JSON parsing with minimal code changes
**Context**: Standard json module is slower than optimized alternatives

**Acceptance Criteria**:
- Install orjson dependency (pip install orjson)
- Replace json.loads() with orjson.loads() in data loading
- Measured 2-3x speedup for JSONL reading
- No breaking changes, drop-in replacement
- Added to requirements.txt

**Source**: PERFORMANCE_ANALYSIS_REPORT.md Priority 3

---

### QUAL2: Ensure code quality through linting

**User**: Developer contributing new analysis
**Outcome**: Consistent code style, static analysis catches issues
**Context**: No automated code quality enforcement

**Acceptance Criteria**:
- Configure pylint, black, mypy
- All code passes linting without errors
- Pre-commit hooks enforce standards
- Type hints validated by mypy
- Documented in CONTRIBUTING.md

**Source**: CODE_QUALITY_ANALYSIS.md Sprint 3

---

### DOC1: Document architecture and execution flow

**User**: New contributor understanding project structure
**Outcome**: Clear documentation explains architecture, how to add analyses
**Context**: Complex codebase with organic growth, no architectural guide

**Acceptance Criteria**:
- Create ARCHITECTURE.md with system overview
- Document Repository Pattern, Strategy Pattern usage
- Visual dependency graph for data files
- "How to add new analysis" guide
- API documentation for core modules

**Source**: ARCHITECTURE-REVIEW.md Action Items P0

---

### PERF7: Profile real workloads for bottlenecks

**User**: Developer optimizing performance
**Outcome**: Actual hotspots identified through profiling data
**Context**: Theoretical analysis may miss real-world bottlenecks

**Acceptance Criteria**:
- Create benchmarks/performance_tests.py
- Profile with cProfile or py-spy on largest analyses
- Results documented in benchmarks/results.md
- Top 5 hotspots identified with data
- Optimization targets prioritized by measured impact

**Source**: PERFORMANCE_ANALYSIS_REPORT.md Priority 3
