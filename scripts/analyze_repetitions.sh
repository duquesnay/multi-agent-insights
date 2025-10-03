#!/bin/bash

set -e

RAW_DIR="$(dirname "$0")/../data/raw"
OUTPUT_DIR="$(dirname "$0")/../data/analysis"

echo "🔍 Deep Analysis of Repetition Patterns (Inefficiency Indicators)"
echo "================================================================"

# Analyser la session avec le plus de délégations (10dcd7b5)
echo ""
echo "📌 CASE STUDY: Session 10dcd7b5 (22 Sept - Heavy refactoring day?)"
echo "Timeline of 51 delegations:"

grep "10dcd7b5-90fa-4f54-a92c-465591154e8d" "$RAW_DIR/agent_calls_metadata.csv" | \
awk -F',' '{
    split($1, dt, "T")
    split(dt[2], tm, ":")
    time = tm[1] ":" tm[2]
    agent = $4
    desc = $6

    # Détecter les répétitions
    if (agent == prev_agent) {
        repeat_marker = " ⚠️ REPEAT"
        repeat_count++
    } else {
        if (repeat_count > 1) {
            print "      └─> " repeat_count " consecutive calls to " prev_agent
        }
        repeat_marker = ""
        repeat_count = 1
    }

    printf "  %s - %-25s %s\n", time, agent, repeat_marker

    prev_agent = agent
}
END {
    if (repeat_count > 1) {
        print "      └─> " repeat_count " consecutive calls to " prev_agent
    }
}'

# Analyser les descriptions répétées en détail
echo ""
echo "📌 RECURRING TASKS (Potential unresolved problems):"
echo ""
echo "1. 'Fix TypeScript compilation errors' (18 occurrences):"
grep "Fix TypeScript compilation errors" "$RAW_DIR/agent_calls_metadata.csv" | \
    cut -d',' -f1,2 | sed 's/T/ /' | cut -d':' -f1 | cut -d' ' -f1 | uniq -c | \
    awk '{printf "   %s: %d times\n", $2, $1}'

echo ""
echo "2. Test-related repetitions:"
grep -E "(test|Test)" "$RAW_DIR/agent_calls_metadata.csv" | cut -d',' -f6 | \
    sort | uniq -c | sort -rn | head -5 | \
    awk '{if ($1 > 2) printf "   %dx: %s\n", $1, substr($0, index($0,$2))}'

# Analyser les patterns de succès (agents appelés une seule fois)
echo ""
echo "📌 EFFICIENCY INDICATORS (Single-call success patterns):"

# Sessions avec un seul appel d'agent = potentiellement efficaces
echo ""
echo "Agents most often used solo (potentially most efficient):"
awk -F',' 'NR>1 {
    session = $2
    agent = $4
    agents_in_session[session]++
    session_agent[session] = agent
}
END {
    for (s in agents_in_session) {
        if (agents_in_session[s] == 1) {
            solo_agent[session_agent[s]]++
        }
    }
    for (a in solo_agent) {
        printf "  %-30s: %d solo sessions\n", a, solo_agent[a]
    }
}' "$RAW_DIR/agent_calls_metadata.csv" | sort -t':' -k2 -rn

# Identifier les agents jamais répétés
echo ""
echo "Agents rarely repeated in same session (potentially most reliable):"
awk -F',' 'NR>1 {
    session = $2
    agent = $4
    key = session "_" agent
    agent_session_count[key]++
    all_agents[agent] = 1
}
END {
    for (a in all_agents) {
        total = 0
        repeated = 0
        for (key in agent_session_count) {
            if (index(key, "_" a) > 0) {
                total++
                if (agent_session_count[key] > 1) repeated++
            }
        }
        if (total > 0) {
            repeat_rate = repeated * 100 / total
            printf "  %-30s: %.0f%% repeat rate (%d/%d sessions)\n", a, repeat_rate, repeated, total
        }
    }
}' "$RAW_DIR/agent_calls_metadata.csv" | sort -t':' -k2 -n | head -10

echo ""
echo "✅ Repetition analysis complete!"