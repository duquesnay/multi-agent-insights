# Pipeline Orchestrator - Quick Reference

**Script**: `run_analysis_pipeline.py`
**Documentation**: `docs/PIPELINE.md`

---

## Quick Commands

```bash
# Show all available stages
python run_analysis_pipeline.py --list-stages

# Preview execution plan (recommended first step)
python run_analysis_pipeline.py --all --dry-run

# Run full pipeline
python run_analysis_pipeline.py --all

# Resume from specific stage
python run_analysis_pipeline.py --from segmentation

# Run specific stages only
python run_analysis_pipeline.py --stage extraction --stage enrichment

# Force re-run (ignore cache)
python run_analysis_pipeline.py --stage analysis --force
```

---

## Pipeline Stages

1. **extraction** - Load raw data from Claude projects (~45s)
2. **enrichment** - Add metadata and patterns (~15s)
3. **segmentation** - Temporal division (~5s)
4. **analysis** - Run metrics and insights (~25s)
5. **reporting** - Generate markdown reports (~3s)

**Total**: ~90s (cold), ~43s (warm cache)

---

## Common Workflows

### First Time Setup
```bash
python run_analysis_pipeline.py --all --dry-run  # Validate
python run_analysis_pipeline.py --all            # Run
```

### After Adding New Sessions
```bash
python run_analysis_pipeline.py --from extraction --force
```

### Update Analysis Only
```bash
python run_analysis_pipeline.py --from analysis --force
```

### Debug Single Stage
```bash
python run_analysis_pipeline.py --stage analysis --dry-run  # Check
python run_analysis_pipeline.py --stage analysis --force    # Run
```

---

## Status Indicators

- ⏭️  **Skipping** - Stage complete and up-to-date
- ▶️  **Running** - Stage executing now
- ✅ **Complete** - Stage finished successfully
- ❌ **Failed** - Error occurred
- 🔍 **DRY RUN** - Preview mode (no changes)

---

## Error Resolution

### "Missing external dependencies"
```bash
# Check Claude projects directory
ls -la ~/.claude/projects/
```

### "Depends on X which hasn't been run"
```bash
# Run prerequisite stages first
python run_analysis_pipeline.py --all
```

### "Missing required files"
```bash
# Re-run from extraction
python run_analysis_pipeline.py --from extraction --force
```

---

## Data Files

**Inputs**:
- `~/.claude/projects/**/*.jsonl` (external)

**Stage Outputs**:
- **extraction**: `data/full_sessions_data.json`, `data/enriched_sessions_data.json`
- **enrichment**: `data/routing_patterns_by_period.json`, `data/marathon-classification.json`
- **segmentation**: `temporal-segmentation-report.json`
- **analysis**: `analysis_results/*.json` (4 files)
- **reporting**: `data/routing_report.md`

---

## Execution Log

**Location**: `pipeline_execution_log.json`

```bash
# View recent runs
tail pipeline_execution_log.json | python -m json.tool
```

---

**Full Documentation**: See `docs/PIPELINE.md` for complete guide
