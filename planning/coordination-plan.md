# Team Coordination Plan - Delegation Retrospective Refactoring

**Start Date**: 2025-10-02
**Target Completion**: 4 weeks (by 2025-10-30)
**Team Size**: 6 specialists + 1 coordinator

---

## Team Assignments

### Week 1: Critical Foundation (7 hours)

#### Developer (Primary: Implementation)
- **INFRA1**: Configure paths work across environments (2h)
  - Create common/config.py
  - Replace 29 hardcoded paths across 30+ scripts
  - Test on different path structures

- **INFRA2**: Access delegation data through single repository (2h)
  - Implement common/data_access.py with DelegationRepository
  - Migrate all scripts to use repository
  - Consolidate 40+ duplicate implementations

- **INFRA3**: Extract token metrics through centralized service (3h)
  - Create common/metrics.py with TokenMetrics dataclass
  - Single extract_token_metrics() implementation
  - Migrate analyze_metrics.py, roi_analysis_detailed.py

#### Code-Quality-Analyst (Review)
- Review INFRA1-3 implementations for DRY compliance
- Validate all duplicates eliminated
- Check for remaining magic numbers

#### Integration-Specialist (Validation)
- Verify path portability across environments
- Test data loading on different machines
- Validate no hardcoded dependencies remain

---

### Week 2: Architecture + Performance (15.5 hours)

#### Solution-Architect (Lead: Architecture)
- **ARCH1**: Define typed domain entities (6h)
  - Design domain/models.py (Delegation, Session, Period, Agent)
  - Encapsulate business logic (is_marathon(), amplification_ratio)
  - Create factory methods (from_dict())
  - Migrate one analysis script as POC

- **ARCH2**: Build period boundaries from git history (4h)
  - Design domain/period_builder.py
  - Implement from_git_archaeology()
  - Remove hardcoded dates from segment_data.py

#### Performance-Optimizer (Lead: Performance)
- **PERF1**: Detect marathon loops in linear time (30min)
  - Rewrite analyze_marathons.py loop detection
  - Use deque sliding window pattern
  - Benchmark 10-100x speedup

- **PERF2**: Access cached file scans (2h)
  - Implement cache in extract_enriched_data.py
  - File metadata (mtime, size) → pickle cache
  - Measure 5-10x speedup

- **PERF3**: Stream large JSON files (3h)
  - Install ijson dependency
  - Implement load_sessions_streaming()
  - Refactor consumers for generators

#### Developer (Support)
- Implement ARCH1 designs from solution-architect
- Assist with PERF implementations
- Write migration scripts

#### Code-Quality-Analyst (Review)
- Validate SOLID principles in domain model
- Check for proper encapsulation
- Review performance optimizations

---

### Week 3: Strategy Pattern + Pipeline (13 hours)

#### Solution-Architect (Lead: Strategy)
- **ARCH3**: Execute analyses through strategy pattern (6h)
  - Design strategies/base.py (AnalysisStrategy interface)
  - Create RoutingAnalysisStrategy, MarathonAnalysisStrategy, FailureAnalysisStrategy
  - Orchestrator for parallel execution
  - Migrate 3 existing analyses

- **ARCH4**: Orchestrate analysis pipeline (4h)
  - Design Makefile or run_analysis.py
  - Define dependency graph (extract → segment → analyze → report)
  - Implement prerequisite validation
  - Error handling and progress reporting

#### Performance-Optimizer (Final optimizations)
- **PERF4**: Match routing patterns with regex (1h)
  - Compile patterns at module level
  - Add @lru_cache for classification
  - Measure 3-5x speedup

- **PERF5**: Analyze patterns in single pass (2h)
  - Consolidate 4 passes into one loop
  - Measure 20-30% improvement

#### Developer (Support)
- Implement strategy pattern designs
- Create Makefile/orchestration script
- Integration work

#### Integration-Specialist (Validation)
- Test pipeline orchestration end-to-end
- Validate dependency execution order
- Check error handling robustness

---

### Week 4: Quality + Documentation (17.5 hours)

#### Test-Engineer (Lead: Testing)
- **QUAL1**: Validate data through test suite (10h)
  - Create tests/ directory structure
  - Unit tests for metrics, classification
  - Integration tests for pipeline
  - Achieve 70% code coverage
  - CI integration (pytest)

#### Code-Quality-Analyst (Lead: Quality)
- **QUAL2**: Ensure code quality through linting (2h)
  - Configure pylint, black, mypy
  - Set up pre-commit hooks
  - Fix all linting errors
  - Document in CONTRIBUTING.md

#### Integration-Specialist (Lead: Schema)
- **DATA1**: Version data schemas (2h)
  - Add schema_version to all JSON outputs
  - Implement version validation in consumers
  - Document schemas in ARCHITECTURE.md
  - Create migration scripts

#### Documentation-Writer (Lead: Docs)
- **DOC1**: Document architecture and execution flow (2h)
  - Create ARCHITECTURE.md
  - Visual dependency graphs
  - "How to add new analysis" guide
  - API documentation

#### Performance-Optimizer (Polish)
- **PERF6**: Parse JSON with orjson (30min)
  - Install orjson, update requirements.txt
  - Replace json.loads() with orjson.loads()
  - Measure 2-3x improvement

- **PERF7**: Profile real workloads (1h)
  - Create benchmarks/performance_tests.py
  - Profile with cProfile or py-spy
  - Document results, prioritize future optimizations

---

## Communication Protocol

### Daily Standups (Async)
- What completed yesterday
- What working on today
- Any blockers

### Code Review Process
1. Developer implements story
2. Code-quality-analyst reviews for quality
3. Integration-specialist validates integration
4. Solution-architect/performance-optimizer reviews architectural/performance aspects
5. Merge after 2 approvals

### Blocker Resolution
- Post blocker immediately
- Coordinator assigns specialist to unblock
- Maximum 4-hour resolution time

---

## Risk Management

### High-Risk Items (Need Extra Attention)

**ARCH3 (Strategy Pattern)**:
- **Risk**: Complex refactoring may introduce regressions
- **Mitigation**: Migrate one analysis first as POC, extensive testing
- **Owner**: solution-architect + test-engineer

**QUAL1 (Test Suite)**:
- **Risk**: 10 hours may be insufficient for 70% coverage
- **Mitigation**: Prioritize core calculations, defer UI tests
- **Owner**: test-engineer

**PERF3 (Streaming JSON)**:
- **Risk**: Consumer refactoring may break existing analyses
- **Mitigation**: Make streaming optional, gradual migration
- **Owner**: performance-optimizer + developer

### Contingency Plans

**If Week 1 slips**:
- INFRA items are blocking → escalate to all hands
- Delay Week 2 start, compress architecture work

**If Week 2 slips**:
- ARCH2 (git archaeology) is optional → defer to later
- Focus on ARCH1 (domain model) as higher priority

**If Week 3 slips**:
- ARCH4 (orchestration) can be simplified (shell script vs Makefile)
- PERF4-5 are nice-to-haves → defer if needed

**If Week 4 slips**:
- QUAL2, PERF6-7, DOC1 are polish → acceptable to defer
- QUAL1 (tests) is critical → protect this time

---

## Success Criteria

### Week 1 Gate (Must Complete)
- ✅ All scripts run with relative paths
- ✅ Zero code duplication in data loading
- ✅ Single source of truth for token metrics
- **Blocker**: Cannot proceed to Week 2 without this foundation

### Week 2 Gate (Must Complete)
- ✅ Domain model in production use
- ✅ At least 5x file scan speedup measured
- ✅ Marathon analysis demonstrably faster
- **Blocker**: Architecture work depends on these

### Week 3 Gate (Must Complete)
- ✅ Strategy pattern with 3 analyses migrated
- ✅ Pipeline orchestration functional
- ✅ All performance optimizations validated
- **Blocker**: Quality work assumes stable architecture

### Week 4 Gate (Completion)
- ✅ Test suite passing with 70% coverage
- ✅ All linting clean
- ✅ Architecture documented
- **Target**: Project health 8/10

---

## Parallel Work Opportunities

### Week 2 Parallelization
- **Stream A**: solution-architect on ARCH1-2 (architecture)
- **Stream B**: performance-optimizer on PERF1-3 (performance)
- **No dependencies**: Can run fully parallel

### Week 3 Parallelization
- **Stream A**: solution-architect on ARCH3-4 (strategy + pipeline)
- **Stream B**: performance-optimizer on PERF4-5 (optimizations)
- **Minimal dependencies**: ARCH4 needs ARCH3 complete

### Week 4 Parallelization
- **Stream A**: test-engineer on QUAL1 (tests)
- **Stream B**: code-quality-analyst on QUAL2 (linting)
- **Stream C**: integration-specialist on DATA1 (schemas)
- **Stream D**: documentation-writer on DOC1 (docs)
- **Stream E**: performance-optimizer on PERF6-7 (polish)
- **Fully parallel**: All independent

---

## Reporting Cadence

### Weekly Summary (Fridays)
- Stories completed vs planned
- Blockers encountered and resolved
- Next week preview
- Risk updates

### Final Report (Week 4 Friday)
- All stories completion status
- Performance metrics (before/after)
- Project health score (target 8/10)
- Remaining technical debt
- Recommendations for future work

---

## Specialist Strengths & Assignments

**Developer**: Implementation workhorse, refactoring large codebases
- Best for: INFRA1-3, supporting ARCH implementations

**Solution-Architect**: SOLID principles, design patterns, system design
- Best for: ARCH1-4, strategy pattern, domain modeling

**Performance-Optimizer**: Algorithmic optimization, profiling, bottlenecks
- Best for: PERF1-7, all performance stories

**Code-Quality-Analyst**: DRY/SOLID/KISS, code smells, quality gates
- Best for: QUAL2, reviewing all code for quality

**Integration-Specialist**: Dependencies, data flow, system integration
- Best for: DATA1, validating INFRA changes, pipeline testing

**Test-Engineer**: Testing strategy, coverage, CI/CD
- Best for: QUAL1, validating all implementations

**Documentation-Writer**: Architecture docs, guides, API documentation
- Best for: DOC1, README updates

---

## Current Status

**Backlog Created**: ✅ 2025-10-02
**User Stories Defined**: ✅ 2025-10-02
**Story Map Organized**: ✅ 2025-10-02
**Team Briefed**: ⏳ Pending
**Work Started**: ⏳ Ready to begin Week 1

**Next Action**: Begin INFRA1 (path configuration) with developer
