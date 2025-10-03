# Changelog

## 2025-10-01 - Data Consolidation & Extraction Updates

### Changes

**Data Management**:
- Consolidated all conversation data (Time Machine snapshots + current) into flat structure
- Created two archival scripts:
  - `scripts/consolidate_all_data.py` - One-time consolidation of all sources
  - `scripts/copy_conversations.py` - Incremental updates from ~/.claude/projects/
- Result: 524 sessions (611 MB) archived in `./data/conversations/[project]/`

**Extraction Updates**:
- Updated `analyses/v8.0-mai-septembre-2025/extract_v8_enriched.py` to read from consolidated data
- Changed source: `~/.claude/projects/` → `./data/conversations/`
- Test results: 220 sessions matched (up from 213), 1,474 delegations extracted

**Documentation**:
- Updated `METHODOLOGIE-ANALYSE-RETROSPECTIVE.md` Phase 0 with data consolidation step
- Added archival workflow to methodology

### Benefits

1. **Data Preservation**: Conversations archived before 1-month auto-deletion
2. **Historical Completeness**: Time Machine snapshots integrated (sessions from May-Sept)
3. **Future Flexibility**: Can re-extract data differently without losing source
4. **Consistent Analysis**: All analyses now use same consolidated data source

### Validation

Extraction test successful:
- 444 total sessions found in consolidated data
- 220 Mai-Septembre sessions with delegations
- Full period coverage: P0 (47), P1 (12), P2 (27), P3 (80), P4 (54)
