#!/bin/bash
# Timeline Reconstruction - Git Archaeology
# Automated agent configuration timeline extraction

set -e

# Configuration
START_DATE="${1:-2025-05-01}"
END_DATE="${2:-2025-09-30}"
OUTPUT_FILE="${3:-AGENT-TIMELINE-VALIDATED.md}"

echo "=== Timeline Reconstruction ==="
echo "Period: $START_DATE to $END_DATE"
echo "Output: $OUTPUT_FILE"
echo

# Initialize output
cat > "$OUTPUT_FILE" << 'HEADER'
# Agent Configuration Timeline - Git Validated

**Source**: `~/.claude-memories` git history
**Date**: $(date +%Y-%m-%d)
**Period**: $START_DATE to $END_DATE

---

## Timeline

HEADER

# Check if .claude-memories exists
if [ ! -d ~/.claude-memories ]; then
    echo "ERROR: ~/.claude-memories not found"
    echo "Checking alternative locations..."

    # Try to find it
    CLAUDE_MEM=$(find ~/.claude -name "*memor*" -type d 2>/dev/null | head -1)

    if [ -z "$CLAUDE_MEM" ]; then
        echo "ERROR: Could not find claude memories directory"
        exit 1
    fi

    echo "Found: $CLAUDE_MEM"
    cd "$CLAUDE_MEM"
else
    cd ~/.claude-memories
fi

# Extract agent-related commits
echo "### Agent Configuration Changes" >> "$OUTPUT_FILE"
echo >> "$OUTPUT_FILE"

git log --all --format="%ai | %H | %s" \
  --since="$START_DATE" --until="$END_DATE" \
  --reverse \
  | grep -iE "(agent|Agent)" \
  | while IFS='|' read -r date commit msg; do
    echo "**$(echo $date | cut -d' ' -f1,2)**: $(echo $msg | xargs)" >> "$OUTPUT_FILE"
done

echo >> "$OUTPUT_FILE"

# Find critical commits (launch, restructuration)
echo "### Critical System Changes" >> "$OUTPUT_FILE"
echo >> "$OUTPUT_FILE"

# Look for specific patterns
git log --all --format="%ai | %H | %s" \
  --since="$START_DATE" --until="$END_DATE" \
  | grep -iE "(add.*agent|restructure|mandatory|split|launch)" \
  | head -20 \
  | while IFS='|' read -r date commit msg; do
    date_clean=$(echo $date | cut -d' ' -f1,2)
    commit_short=$(echo $commit | cut -c1-8)
    msg_clean=$(echo $msg | xargs)

    echo "- **$date_clean** ($commit_short): $msg_clean" >> "$OUTPUT_FILE"

    # Get file changes for this commit
    echo "  Files changed:" >> "$OUTPUT_FILE"
    git show --stat "$commit" | grep -E "\.md|\.json" | head -5 | while read line; do
        echo "    - $line" >> "$OUTPUT_FILE"
    done
    echo >> "$OUTPUT_FILE"
done

echo >> "$OUTPUT_FILE"

# Active repos during period (for context)
echo "### Active Development Repos" >> "$OUTPUT_FILE"
echo >> "$OUTPUT_FILE"
echo "Repos with commits during period:" >> "$OUTPUT_FILE"
echo >> "$OUTPUT_FILE"

find ~/dev -name ".git" -type d 2>/dev/null | while read gitdir; do
    repo=$(dirname "$gitdir")
    cd "$repo"

    commits=$(git log --all --since="$START_DATE" --until="$END_DATE" \
      --oneline 2>/dev/null | wc -l | tr -d ' ')

    if [ "$commits" -gt 10 ]; then
        repo_name=$(basename "$repo")
        first_commit=$(git log --all --since="$START_DATE" --until="$END_DATE" \
          --format="%ai" --reverse 2>/dev/null | head -1 | cut -d' ' -f1)
        last_commit=$(git log --all --since="$START_DATE" --until="$END_DATE" \
          --format="%ai" 2>/dev/null | head -1 | cut -d' ' -f1)

        echo "- **$repo_name**: $commits commits ($first_commit to $last_commit)" >> "$OUTPUT_FILE"
    fi
done

echo >> "$OUTPUT_FILE"

# Period definitions
echo "### Suggested Period Segmentation" >> "$OUTPUT_FILE"
echo >> "$OUTPUT_FILE"
echo "Based on configuration changes:" >> "$OUTPUT_FILE"
echo >> "$OUTPUT_FILE"

# Try to identify major change dates
echo "| Period | Start Date | Configuration |" >> "$OUTPUT_FILE"
echo "|--------|------------|---------------|" >> "$OUTPUT_FILE"

# This would need manual adjustment based on actual commits found
echo "| P0 | Before first agent | No specialized agents |" >> "$OUTPUT_FILE"
echo "| P1 | First agent addition | Multi-agent launch |" >> "$OUTPUT_FILE"
echo "| ... | [Manual adjustment] | [Based on changes found] |" >> "$OUTPUT_FILE"

echo >> "$OUTPUT_FILE"

# Limitations
echo "---" >> "$OUTPUT_FILE"
echo >> "$OUTPUT_FILE"
echo "## Notes & Limitations" >> "$OUTPUT_FILE"
echo >> "$OUTPUT_FILE"
echo "- Review suggested periods manually" >> "$OUTPUT_FILE"
echo "- Validate timeline with user knowledge" >> "$OUTPUT_FILE"
echo "- Check for missing data gaps" >> "$OUTPUT_FILE"
echo "- Cross-reference with actual usage data" >> "$OUTPUT_FILE"

echo
echo "✅ Timeline reconstruction complete: $OUTPUT_FILE"
echo
echo "Next steps:"
echo "1. Review $OUTPUT_FILE for accuracy"
echo "2. Sync with user (15min) to validate timeline"
echo "3. Adjust period segmentation based on findings"
echo "4. Document any data gaps for those periods"