#!/bin/bash
# Temporal Analysis: Impact of Sept 21 Restructuration
# Segments data before/after developer → senior-developer split

PIVOT_DATE="2025-09-21T14:24:38Z"
DATA_FILE="data/full_sessions_data.json"

echo "=== TEMPORAL ANALYSIS: SEPT 21 RESTRUCTURATION IMPACT ==="
echo ""
echo "Pivot date: $PIVOT_DATE"
echo "- Before: developer (generic agent)"
echo "- After: senior-developer + junior-developer (specialized)"
echo ""

# Count sessions before/after
echo "--- Session Distribution ---"
TOTAL=$(cat $DATA_FILE | jq '.sessions | length')
echo "Total sessions: $TOTAL"

# Extract first delegation timestamp per session to determine period
cat $DATA_FILE | jq -r '
.sessions[] |
select(.delegations | length > 0) |
{
  session: .session_id[0:8],
  first_delegation: .delegations[0].timestamp,
  delegation_count: .delegation_count
} |
[.session, .first_delegation, .delegation_count] |
@tsv
' > /tmp/session_periods.tsv

PRE_COUNT=$(awk -F'\t' -v pivot="$PIVOT_DATE" '$2 < pivot' /tmp/session_periods.tsv | wc -l | tr -d ' ')
POST_COUNT=$(awk -F'\t' -v pivot="$PIVOT_DATE" '$2 >= pivot' /tmp/session_periods.tsv | wc -l | tr -d ' ')

echo "Pre-restructuration (< Sept 21 16h24): $PRE_COUNT sessions"
echo "Post-restructuration (>= Sept 21 16h24): $POST_COUNT sessions"
echo ""

# Marathon sessions by period
echo "--- Marathon Sessions (>20 delegations) ---"
PRE_MARATHON=$(awk -F'\t' -v pivot="$PIVOT_DATE" '$2 < pivot && $3 > 20' /tmp/session_periods.tsv | wc -l | tr -d ' ')
POST_MARATHON=$(awk -F'\t' -v pivot="$PIVOT_DATE" '$2 >= pivot && $3 > 20' /tmp/session_periods.tsv | wc -l | tr -d ' ')

echo "Pre-restructuration: $PRE_MARATHON marathon sessions"
echo "Post-restructuration: $POST_MARATHON marathon sessions"
echo ""

if [ "$PRE_COUNT" -gt 0 ]; then
  PRE_RATIO=$(awk "BEGIN {printf \"%.1f%%\", ($PRE_MARATHON/$PRE_COUNT)*100}")
  echo "Pre ratio: $PRE_RATIO"
fi

if [ "$POST_COUNT" -gt 0 ]; then
  POST_RATIO=$(awk "BEGIN {printf \"%.1f%%\", ($POST_MARATHON/$POST_COUNT)*100}")
  echo "Post ratio: $POST_RATIO"
fi
echo ""

# Average delegations per session
echo "--- Average Delegations per Session ---"
if [ "$PRE_COUNT" -gt 0 ]; then
  PRE_AVG=$(awk -F'\t' -v pivot="$PIVOT_DATE" '$2 < pivot {sum+=$3; count++} END {printf "%.1f", sum/count}' /tmp/session_periods.tsv)
  echo "Pre-restructuration: $PRE_AVG delegations/session"
fi

if [ "$POST_COUNT" -gt 0 ]; then
  POST_AVG=$(awk -F'\t' -v pivot="$PIVOT_DATE" '$2 >= pivot {sum+=$3; count++} END {printf "%.1f", sum/count}' /tmp/session_periods.tsv)
  echo "Post-restructuration: $POST_AVG delegations/session"
fi
echo ""

# List marathon sessions with dates
echo "--- Marathon Sessions Detail ---"
echo "Session | Date | Delegations | Period"
awk -F'\t' -v pivot="$PIVOT_DATE" '$3 > 20 {
  period = ($2 < pivot) ? "PRE" : "POST"
  printf "%s | %s | %d | %s\n", $1, $2, $3, period
}' /tmp/session_periods.tsv | sort -t'|' -k2

echo ""
echo "=== NEXT STEPS ==="
echo "1. Analyze agent type distribution pre/post (developer vs senior-developer)"
echo "2. Calculate success rates by period"
echo "3. Analyze interruption patterns by period"
echo "4. Check junior-developer adoption post-restructuration"