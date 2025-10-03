# Cross-Validation Report - vX.X

**Analysis Version**: vX.X
**Date**: YYYY-MM-DD
**Objective**: Resolve contradictions between LLM agents, Scripts, and Git

---

## Summary

**Total findings checked**: X
**Contradictions found**: Y
**Resolved**: Z
**Pending investigation**: W

---

## Contradictions Found

### #1: [Finding Title]

**Source**: Agent X / Script Y / Git Z
**Date discovered**: YYYY-MM-DD

#### Agent LLM Claim
```
Agent X concluded: "[Finding from agent analysis]"

Confidence: [High/Medium/Low]
Based on: [Textual signals, patterns, etc.]
```

#### Scripts/Git Data
```
Scripts show: [Objective metrics]
Git shows: [LOC net, commit types, diffs]

Contradiction: [Explain difference]
```

#### Investigation

**Primary data checked**:
- [ ] Sessions: [List session IDs examined]
- [ ] Git commits: [List commits checked]
- [ ] Scripts output: [Relevant metrics]

**Findings**:
```
[What investigation revealed...]
```

#### Resolution

**Root cause**: [Why contradiction occurred]

**Correct conclusion**: [What's actually true]

**False positive?**: ☐ Yes  ☐ No

**Explanation**:
```
[Why agent/script/git was wrong or misinterpreted]
```

**Impact on conclusions**:
- [ ] No impact (minor detail)
- [ ] Requires metrics adjustment
- [ ] Requires conclusion revision
- [ ] Requires full re-analysis

**Action taken**:
```
[What was done to correct]
```

---

### #2: [Another Contradiction]

[Same structure as #1...]

---

## Patterns Observed

### False Positives from Agents

**Pattern**: [Type of signal that creates false positives]

**Example**: Agent 4 "over-engineering +54%" based on "refactor/simplify" mentions
**Reality**: Git shows -17k LOC (cleanup, not creation)

**Root cause**: Textual signals ≠ code reality

**Prevention**:
- Always validate quality claims with git diff
- Distinguish mentions from actions
- Check LOC net (add/delete balance)

---

### Data Gaps Impact

**Pattern**: [How missing data leads to wrong conclusions]

**Example**: [Specific case]

**Prevention**:
- Flag gaps in Phase 0
- Document limitations
- Don't interpolate missing periods

---

### Classification Needed

**Pattern**: [Aggregation without classification]

**Example**: "12 marathons = problem" → 10/12 actually positive after classification

**Prevention**:
- Classify before aggregate
- Success rate, cascade rate, context
- Positive/negative/ambiguous categories

---

## Validation Checklist

### For Each Major Finding:

- [ ] **Agent conclusion** documented clearly
- [ ] **Scripts metrics** extracted (objective data)
- [ ] **Git validation** performed (if quality claim)
- [ ] **Contradiction** identified (if any)
- [ ] **Primary data** checked (sessions, commits)
- [ ] **Root cause** determined
- [ ] **Correct conclusion** documented
- [ ] **Impact assessed** (revision needed?)
- [ ] **Prevention pattern** identified

---

## Confidence Scores

| Finding | Agent | Scripts | Git | Confidence | Validated |
|---------|-------|---------|-----|------------|-----------|
| Timeline août 4 | - | - | ✓✓✓ | HIGH | ✓ |
| Marathons 10/12 positive | ✓ | ✓✓ | - | HIGH | ✓ |
| Over-engineering +54% | ✓ | - | ✗✗✗ | FALSE | ✗ |
| Success rate 83.3% | ✓ | ✓✓✓ | - | HIGH | ✓ |

Legend:
- ✓✓✓ Strong evidence
- ✓✓ Good evidence
- ✓ Some evidence
- - Not checked
- ✗ Contradicts
- ✗✗✗ Strongly contradicts

---

## Recommendations

### For Future Analyses:

1. **Git validation timing**:
   - Quality claims → Git immediately
   - Don't wait for contradictions to emerge

2. **Classification frameworks**:
   - Apply before aggregating
   - Success rate + context + cascade rate

3. **Cross-check frequency**:
   - Daily during analysis phase
   - Before drafting conclusions

4. **Confidence scoring**:
   - High: Multiple sources agree
   - Medium: Single source, plausible
   - Low: Conflicting signals
   - False: Contradicted by primary data

---

## Pending Investigations

### Items Requiring More Data:

1. **[Finding X]**
   - Why pending: [Reason]
   - Data needed: [What's missing]
   - Resolution timeline: [When expected]

---

## Lessons Learned

### This Analysis:

1. **[Learning 1]**: [What was discovered]
   - Pattern: [Generalization]
   - Prevention: [How to avoid]

2. **[Learning 2]**: [Another discovery]
   - Pattern: [...]
   - Prevention: [...]

---

**Completed by**: [Name]
**Date**: YYYY-MM-DD
**Reviewed by**: [Name]