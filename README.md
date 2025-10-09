# Multi-Agent Insights

Methodology for analyzing multi-agent delegation patterns in Claude Code. Validates system evolution through git archaeology, archive and backups former Claude Code conversations, cross-checks LLM analyses with quantitative scripts, and produces insights about agent performance and collaboration patterns.

## What This Methodology Does

Analyzes your Claude Code multi-agent system to answer:
- **Which agents work well?** Adoption rates, success patterns, ROI
- **How do agents collaborate?** Workflow patterns, handoffs, team dynamics
- **What's blocking efficiency?** Routing quality, cascades, bottlenecks
- **What improved over time?** System evolution, A/B configuration comparison

**Trying to be thorough**: Git archaeology for timeline validation, conversations retrieval and analysis (~/.claude/projects), parallel LLM + script analysis with cross-checking, temporal segmentation to avoid invalid aggregations (if you changed your agent system over time).

## Note on Claude requirements
Using the freshly released Sonnet 4.5 at the time of writing. No idea how this performs otherwise but Opus 4 must do as good with this process. 

## Running an Assessment

### Option 1: Via Slash Command (In Claude Code Conversation)

```
/assess-agents
```

**Default scope**: All projects since August 4, 2025 (when multi-agent delegation launched in Claude Code).

**Custom scope** - specify parameters:

```
/assess-agents obsidian-local-rest-api
```

The command will prompt for period and other details, or analyze with discovered periods.

### Option 2: Direct Pipeline (For Advanced Use)

```bash
# Default: All projects since August 4, 2025 (multi-agent launch)
python run_analysis_pipeline.py --all

# Single project analysis
python run_analysis_pipeline.py --all \
  --project "obsidian-local-rest-api" \
  --start-date "2025-09-26" \
  --end-date "2025-10-06"

# Auto-discover periods from git
python run_analysis_pipeline.py --all --discover-periods

# Specific stages only
python run_analysis_pipeline.py --stage extraction --stage analysis
```

**Scope Configuration**:
- **Project filtering**: Analyze specific projects or all projects
- **Date range**: Custom start/end dates or defaults (since August 2025, ongoing)
- **Period discovery**: Auto-detect configuration changes from git
- **Default behavior**: All projects since August 4, 2025 (multi-agent launch)

**Data Retention Strategy**:
- Claude Code keeps conversations for ~30 days only
- Each analysis extracts and archives data locally in `data/conversations/`
- Run monthly to build multi-month history over time
- Enables long-term system evolution tracking

### What Happens

**Phase 0 - Foundations** (blocking):
1. **Timeline discovery**: Determines when agents were added/modified
   - Asks if you version agent configurations (git or similar)
   - With versioning: Analyzes commit history for precise timeline
   - Without versioning: Infers from usage patterns (first/last appearance) + validates with you
2. **Assumptions sync**: 15min validation with you (timeline, baselines, data gaps, uncertainties)

**Phase 1 - Enriched Dataset**:
- Extracts session data with temporal classification
- Identifies marathons (10+ delegations), failure patterns
- Prepares structured data for parallel analysis

**Phase 2 - Parallel Analysis**:
- **4 LLM agents** (semantic patterns): routing, failures, coordination, quality
- **Python scripts** (quantitative): metrics, tokens, ROI
- **Git validation**: Code quality cross-check
- **Cross-checking**: Resolve contradictions

**Phase 3 - Synthesis**:
- Generates `observations-comparative-v[X].md`
- 80% focus on current system state
- Comparative insights (if baseline available)
- User validation of findings

**Output**: Comprehensive assessment document with agent adoption, collaboration patterns, efficiency metrics, and actionable insights.

## Methodology Principles

**VACE Framework**:
- **Validate** foundations before analyzing (git + data + assumptions)
- **Analyze** in parallel (LLM semantic + scripts quantitative)
- **Cross-check** contradictions with primary data
- **Evolve** with user corrections and versioning

**Temporal Segmentation**: System evolves (agents added/removed). Never aggregate across configuration changes without segmentation.

**No Assumptions**: Timeline discovered fresh each time (git or usage patterns). No cached knowledge about "when agents were added". Transparent about uncertainties.

## Example Output

From a game UI project assessment (48h, 62 delegations):

**Key Findings**:
- 64.5% adoption of newly added specialists (8x higher than typical)
- Collaborative triad pattern: UX ↔ Graphics ↔ Design
- Workflow: Architecture → (UX+Graphics+Design parallel) → Implementation → QA

**Insights**:
- Multidisciplinary features benefit from multi-angle analysis
- First observed "team" pattern vs previous sequential workflows
- UI-focused work naturally favored graphics (35%) over mechanics (8%)

See `analyses/` directory for full assessment examples.

## Documentation

- **[Methodology Reference](analyses/methodology/METHODOLOGIE-ANALYSE-RETROSPECTIVE.md)** - Complete VACE framework
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup for contributors
- **[Pipeline Technical Guide](docs/PIPELINE.md)** - For developers extending analysis scripts

## License

MIT License - see [LICENSE](LICENSE) file for details

## Author

Guillaume Duquesnay
