# Multi-Agent System Assessment

Analyze agent performance, delegation patterns, and system efficiency following **METHODOLOGIE-ANALYSE-RETROSPECTIVE.md**

---

## Usage

```
/assess-agents <project-name> [time-range]
```

**Examples**:
- `/assess-agents cold-chamber-ui` - Analyze entire project history
- `/assess-agents cold-chamber-ui until today 8am` - Up to specific time
- `/assess-agents "all"` - Analyze all projects (September baseline)

---

## Execution Method

**USE EXISTING PIPELINE INFRASTRUCTURE** - Don't write custom extraction code!

```bash
# The pipeline handles project filtering and custom date ranges
# --all runs: backup → extraction → enrichment → segmentation → analysis → reporting
python -m tools.pipeline.run_analysis_pipeline \
  --project "<project-name>" \
  --start-date YYYY-MM-DD \
  --end-date YYYY-MM-DD \
  --discover-periods \
  --all

# Or skip backup if using existing data or live source
python -m tools.pipeline.run_analysis_pipeline \
  --project "<project-name>" \
  --skip-backup \
  --source-live \
  --all
```

**Note**: `--all` includes backup stage (archives conversations from ~/.claude/projects/).
Use `--skip-backup` to skip archiving and work with existing data or live source.

**Only create custom scripts if the pipeline cannot handle your use case.**

---

## Analysis Process

Following **METHODOLOGIE-ANALYSE-RETROSPECTIVE.md**:

1. **Phase 0 (BLOCKING)**: Git archaeology + Data inventory + Assumptions sync
2. **Phase 1**: Enriched dataset extraction + classification (via pipeline)
3. **Phase 2**: 4 parallel LLM agents + Python scripts + Cross-check
4. **Phase 3**: Current system assessment synthesis (80% focus) + User validation

**Output**: `observations-comparative-v[X].md` (agents/patterns/efficiency assessment)

---

## Scope Adaptations

**Single project**: Focus on current config, optional baseline comparison
**Multi-projects**: Cross-project patterns, ROI by project type
**System comparison**: System A vs B (avoid temporal artifacts)

---

**Complete reference**: See project's `CLAUDE.md` → Running Analyses section
