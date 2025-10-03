#!/bin/bash

set -e

OUTPUT_DIR="$(dirname "$0")/../data/processed"
RAW_DIR="$(dirname "$0")/../data/raw"

echo "🔍 Phase 2: Analyzing prompt patterns for top agents..."

mkdir -p "$OUTPUT_DIR"

# Top 5 agents les plus utilisés
TOP_AGENTS=("developer" "git-workflow-manager" "backlog-manager" "solution-architect" "architecture-reviewer")

for agent in "${TOP_AGENTS[@]}"; do
    echo ""
    echo "📊 Analyzing: $agent"

    # Extraire toutes les délégations pour cet agent
    grep ",$agent," "$RAW_DIR/agent_calls_metadata.csv" > "$OUTPUT_DIR/${agent}_metadata.csv" || true

    if [ -s "$OUTPUT_DIR/${agent}_metadata.csv" ]; then
        COUNT=$(wc -l < "$OUTPUT_DIR/${agent}_metadata.csv")
        echo "   Found $COUNT delegations"

        # Statistiques de longueur de prompt
        echo "   Prompt lengths:"
        cut -d',' -f5 "$OUTPUT_DIR/${agent}_metadata.csv" | sort -n | awk '
            {
                sum += $1; count++; lengths[count] = $1
            }
            END {
                if (count > 0) {
                    # Moyenne
                    avg = sum / count
                    # Médiane
                    if (count % 2 == 1) {
                        median = lengths[(count + 1) / 2]
                    } else {
                        median = (lengths[count / 2] + lengths[count / 2 + 1]) / 2
                    }
                    printf "     Min: %d, Max: %d, Avg: %.0f, Median: %.0f\n", lengths[1], lengths[count], avg, median
                }
            }'

        # Descriptions les plus courantes
        echo "   Top descriptions:"
        cut -d',' -f6 "$OUTPUT_DIR/${agent}_metadata.csv" | sort | uniq -c | sort -rn | head -5 | sed 's/^/     /'
    else
        echo "   No data found"
    fi
done

# Analyser les séquences de délégation (même session, timestamps proches)
echo ""
echo "🔗 Analyzing delegation sequences..."

# Grouper par session et ordonner par timestamp pour détecter les chaînes
sort -t',' -k2,2 -k1,1 "$RAW_DIR/agent_calls_metadata.csv" | awk -F',' '
BEGIN {
    prev_session = ""
    prev_timestamp = ""
    prev_agent = ""
    sequence_count = 0
}
{
    session = $2
    timestamp = $1
    agent = $4

    if (session == prev_session && agent != prev_agent) {
        # Même session, agent différent = séquence possible
        sequence_count++
        if (sequence_count == 1) {
            print "Sequence " sequence_count ": " prev_agent " -> " agent " (" session ")"
        } else {
            print "  -> " agent
        }
    } else {
        if (sequence_count > 0) sequence_count = 0
    }

    prev_session = session
    prev_timestamp = timestamp
    prev_agent = agent
}
' | head -20 > "$OUTPUT_DIR/delegation_sequences.txt"

echo "   Saved delegation sequences to: delegation_sequences.txt"

echo ""
echo "✅ Phase 2 analysis completed!"
echo "   Results saved in: $OUTPUT_DIR/"