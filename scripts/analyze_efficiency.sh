#!/bin/bash

set -e

RAW_DIR="$(dirname "$0")/../data/raw"
OUTPUT_DIR="$(dirname "$0")/../data/analysis"
mkdir -p "$OUTPUT_DIR"

echo "🎯 Analyzing Delegation Efficiency Patterns..."
echo "=========================================="

# 1. RÉPÉTITIONS D'AGENTS (signe potentiel d'échec/révision)
echo ""
echo "📊 AGENT REPETITIONS (potential failures/revisions):"
echo "Sessions with same agent called multiple times in succession:"

# Analyser les sessions avec appels répétés du même agent
sort -t',' -k2,2 -k1,1 "$RAW_DIR/agent_calls_metadata.csv" | awk -F',' '
BEGIN { prev_session = ""; prev_agent = ""; count = 0 }
{
    session = $2
    agent = $4
    timestamp = $1

    if (session == prev_session && agent == prev_agent) {
        count++
        if (count == 2) {
            print "  Session: " substr(session, 1, 8) "... Agent: " agent " (first repeat at " timestamp ")"
        }
    } else {
        if (count > 2) {
            print "    → Total " count " consecutive calls to " prev_agent
        }
        count = 1
    }

    prev_session = session
    prev_agent = agent
    prev_timestamp = timestamp
}
END {
    if (count > 2) {
        print "    → Total " count " consecutive calls to " prev_agent
    }
}' | head -20

# 2. DESCRIPTIONS RÉPÉTÉES (tâches qui reviennent = échecs?)
echo ""
echo "📊 REPEATED TASK DESCRIPTIONS (potential unresolved issues):"
tail -n +2 "$RAW_DIR/agent_calls_metadata.csv" | cut -d',' -f6 | \
    grep -v "^$" | grep -v "^_" | \
    sort | uniq -c | sort -rn | head -10 | \
    awk '{if ($1 > 2) printf "  %dx: %s\n", $1, substr($0, index($0,$2))}'

# 3. SÉQUENCES LONGUES (inefficacité?)
echo ""
echo "📊 LONG DELEGATION CHAINS (potential inefficiency):"
echo "Sessions with 5+ delegations within 1 hour:"

awk -F',' 'NR>1 {
    session = $2
    timestamp = $1
    sessions[session]++

    # Extraire heure du timestamp
    split(timestamp, dt, "T")
    split(dt[2], tm, ":")
    hour = dt[1] " " tm[1]

    session_hours[session][hour]++
}
END {
    for (s in sessions) {
        for (h in session_hours[s]) {
            if (session_hours[s][h] >= 5) {
                printf "  Session %s: %d delegations in hour %s\n", substr(s,1,8), session_hours[s][h], h
            }
        }
    }
}' "$RAW_DIR/agent_calls_metadata.csv" | sort -t':' -k2 -rn | head -10

# 4. EFFICACITÉ PAR LONGUEUR DE PROMPT
echo ""
echo "📊 PROMPT LENGTH PATTERNS:"
echo "Distribution by agent (potential correlation with success):"

for agent in "developer" "git-workflow-manager" "backlog-manager" "solution-architect"; do
    echo "  $agent:"
    grep ",$agent," "$RAW_DIR/agent_calls_metadata.csv" | cut -d',' -f5 | \
    awk '{
        if ($1 < 500) short++
        else if ($1 < 1000) medium++
        else if ($1 < 1500) long++
        else verylong++
        total++
    }
    END {
        if (total > 0) {
            printf "    <500: %d (%.0f%%), 500-1000: %d (%.0f%%), 1000-1500: %d (%.0f%%), >1500: %d (%.0f%%)\n",
                short, short*100/total, medium, medium*100/total,
                long, long*100/total, verylong, verylong*100/total
        }
    }'
done

# 5. PATTERNS DE SÉQUENCES TYPIQUES
echo ""
echo "📊 COMMON DELEGATION SEQUENCES:"
echo "Analyzing 2-agent and 3-agent patterns..."

# Créer un fichier temporaire avec les séquences
> "$OUTPUT_DIR/sequences_temp.txt"

# Extraire les séquences de 2 et 3 agents
sort -t',' -k2,2 -k1,1 "$RAW_DIR/agent_calls_metadata.csv" | awk -F',' '
BEGIN {
    prev_session = ""
    sequence = ""
    count = 0
}
{
    session = $2
    agent = $4

    if (session == prev_session) {
        if (count == 0) {
            sequence = prev_agent " → " agent
            print sequence
        } else if (count == 1) {
            sequence = sequence " → " agent
            print sequence
        }
        count++
    } else {
        count = 0
        sequence = ""
    }

    prev_session = session
    prev_agent = agent
}' > "$OUTPUT_DIR/sequences_temp.txt"

echo "  Most common 2-agent sequences:"
grep " → " "$OUTPUT_DIR/sequences_temp.txt" | grep -v " → .* → " | \
    sort | uniq -c | sort -rn | head -5 | \
    awk '{printf "    %3d times: %s\n", $1, substr($0, index($0,$2))}'

echo "  Most common 3-agent sequences:"
grep " → .* → " "$OUTPUT_DIR/sequences_temp.txt" | \
    sort | uniq -c | sort -rn | head -5 | \
    awk '{printf "    %3d times: %s\n", $1, substr($0, index($0,$2))}'

# 6. AGENTS ISOLÉS VS EN SÉQUENCE
echo ""
echo "📊 AGENT ISOLATION vs SEQUENCING:"

# Compter les agents utilisés seuls vs en séquence
awk -F',' 'NR>1 {
    session = $2
    agent = $4
    agents_in_session[session]++
    agent_usage[agent]++
}
END {
    for (s in agents_in_session) {
        if (agents_in_session[s] == 1) solo_sessions++
        else multi_sessions++
    }

    printf "  Solo delegations (single agent): %d sessions\n", solo_sessions
    printf "  Multi-agent sequences: %d sessions\n", multi_sessions
    printf "  Ratio: %.1f%% sessions use multiple agents\n", multi_sessions*100/(solo_sessions+multi_sessions)
}' "$RAW_DIR/agent_calls_metadata.csv"

echo ""
echo "✅ Efficiency analysis complete!"
echo "Key insights saved to: $OUTPUT_DIR/"