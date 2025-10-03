# Assumptions Checklist - Phase 0

**Analysis Version**: vX.X
**Date**: YYYY-MM-DD
**Analyst**: [Name]

---

## Critical Assumptions to Validate

### 1. System Timeline

- [ ] When was multi-agent system launched? (Git: `~/.claude-memories`)
- [ ] What agents existed during analysis period?
- [ ] Were there major configuration changes? (Dates?)
- [ ] Baseline period identified (pre-changes)?

**Git command**:
```bash
cd ~/.claude-memories
git log --all --format="%ai | %s" --since="YYYY-MM-01" --until="YYYY-MM-31" \
  | grep -E "(agent|Agent)"
```

**Validation**:
- [ ] Timeline verified with git
- [ ] User confirmed timeline accuracy

**Notes**:
```
[Timeline findings...]
```

---

### 2. Data Availability

- [ ] What snapshots/data available for period?
- [ ] Volumes per period checked (sessions, delegations)?
- [ ] Missing data identified (gaps)?
- [ ] Data quality validated (truncation, null values)?

**Inventory**:
```bash
ls -lh data/conversations/
# List volumes
```

**Validation**:
- [ ] Volumes make sense (no suspicious spikes/drops)
- [ ] Gaps documented with criticality assessment

**Notes**:
```
Period           | Sessions | Delegations | Notes
----------------|----------|-------------|-------
YYYY-MM         | XX       | YYY         |
[Missing Period]| -        | -           | CRITICAL GAP
```

---

### 3. External Context

- [ ] Active development projects during period? (MCP, applications)
- [ ] Major features/migrations ongoing?
- [ ] User learning curve factors?
- [ ] System changes outside agent configs?

**Git repos check**:
```bash
find ~/dev -name ".git" -type d 2>/dev/null | while read gitdir; do
    repo=$(dirname "$gitdir")
    cd "$repo"
    commits=$(git log --all --since="YYYY-MM-01" --until="YYYY-MM-31" \
      --oneline 2>/dev/null | wc -l)
    if [ "$commits" -gt 0 ]; then
        echo "$repo: $commits commits"
    fi
done
```

**Validation**:
- [ ] Active repos identified
- [ ] Development context understood
- [ ] User confirmed no major external factors

**Notes**:
```
[Active projects, migrations, learning curve...]
```

---

### 4. Baseline & Comparisons

- [ ] What period serves as baseline?
- [ ] Baseline configuration documented?
- [ ] Comparison periods valid (same configs)?
- [ ] Cross-period comparisons make sense?

**Validation**:
- [ ] Baseline = pre-changes period (not arbitrary)
- [ ] Comparisons control for config changes
- [ ] Segmentation respects system evolution

**Notes**:
```
Baseline: [Period X - Config Y]
Comparison: [Period Z - Config W]
Valid comparison: [Yes/No - Reason]
```

---

### 5. Key Metrics Definitions

- [ ] What constitutes "failure"? (Taxonomy defined)
- [ ] What constitutes "marathon"? (Threshold? Classification?)
- [ ] Success rate calculation clear?
- [ ] Other metrics well-defined?

**Validation**:
- [ ] Metrics definitions explicit
- [ ] Classification frameworks applied (not just counts)
- [ ] Edge cases considered

**Notes**:
```
Marathon: >20 delegations
Classification: success_rate + cascade_rate → positive/negative/ambiguous

Failure taxonomy:
- USER_TOOL_INTERVENTION (ambiguous)
- AGENT_NOT_FOUND (config issue)
- [...]
```

---

## User Sync (15min)

**Date sync**: YYYY-MM-DD
**Attendees**: [Names]

### Questions for User:
1. Timeline agents launch correct?
2. Missing data periods critical?
3. External context factors?
4. Baseline period makes sense?
5. Metrics definitions aligned with intent?

### User Corrections:
```
[User feedback notes...]
```

### Revised Assumptions:
```
[What changed after sync...]
```

---

## Validation Status

- [ ] All critical assumptions validated (git + user)
- [ ] Data gaps documented with criticality
- [ ] Baseline period confirmed
- [ ] Metrics definitions clear
- [ ] External context understood

**Ready to proceed to Phase 1 (Extraction)**: ☐ Yes  ☐ No

**Blockers**:
```
[If No, what's missing/blocking?]
```

---

**Completed by**: [Name]
**Date**: YYYY-MM-DD
**Approved by user**: ☐ Yes  ☐ No