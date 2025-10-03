# Multi-Agent Insights

Methodology for analyzing multi-agent delegation patterns in Claude Code. Validates system evolution through git archaeology, archive and backups former Claude Code conversations, cross-checks LLM analyses with quantitative scripts, and produces insights about agent performance and collaboration patterns.

## What This Methodology Does

Analyzes your Claude Code multi-agent system to answer:
- **Which agents work well?** Adoption rates, success patterns, ROI
- **How do agents collaborate?** Workflow patterns, handoffs, team dynamics
- **What's blocking efficiency?** Routing quality, cascades, bottlenecks
- **What improved over time?** System evolution, A/B configuration comparison

**Trying to be thorough**: Git archaeology for timeline validation, conversations retrieval and analysis (~/.claude/projects), parallel LLM + script analysis with cross-checking, temporal segmentation to avoid invalid aggregations (if you changed your agent system over time).

## Running an Assessment

In any Claude Code conversation:

```
/assess-agents (brings back everything)
```

Or provide full parameters:

```
/assess-agents
- Project: my-game-project
- Period: 2025-10-01 to 2025-10-03
- Current config: game-design-specialist, game-graphics-specialist, ux-ergonomics-specialist
```

### What Happens

**Phase 0 - Foundations** (30min, blocking):
1. **Git archaeology**: Scans `~/.claude-memories` to discover when agents were added/modified
2. **Data backup**: Creates snapshot in `data/conversations/backup-YYYYMMDD/`
3. **Assumptions sync**: 15min validation with you (timeline, baselines, data gaps)

**Phase 1 - Enriched Dataset** (15-30min):
- Extracts session data with temporal classification
- Identifies marathons (10+ delegations), failure patterns
- Prepares structured data for parallel analysis

**Phase 2 - Parallel Analysis** (1-2h):
- **4 LLM agents** (semantic patterns): routing, failures, coordination, quality
- **Python scripts** (quantitative): metrics, tokens, ROI
- **Git validation**: Code quality cross-check
- **Cross-checking**: Resolve contradictions

**Phase 3 - Synthesis** (30min):
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

**No Assumptions**: Git archaeology discovers timeline each time. No cached knowledge about "when agents were added".

## Example Output

From `cold-chamber-ui` assessment (48h, 62 delegations):

**Key Findings**:
- 64.5% adoption of new game specialists (8x higher than typical)
- Collaborative triad pattern emerged: UX ↔ Graphics ↔ Design
- Workflow: Architecture → (UX+Graphics+Design parallel) → Implementation → QA

**Insights**:
- Multidisciplinary features benefit from multi-angle analysis (not "misrouting")
- First true "team" pattern vs previous sequential silos
- UI-focused project naturally favors graphics (35%) over mechanics (8%)

See `analyses/cold-chamber-ui-assessment.md` for full example.

## Documentation

- **[Methodology Reference](analyses/methodology/METHODOLOGIE-ANALYSE-RETROSPECTIVE.md)** - Complete VACE framework
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup for contributors
- **[Pipeline Technical Guide](docs/PIPELINE.md)** - For developers extending analysis scripts

## License

[Specify license]

## Author

Guillaume Duquesnay
