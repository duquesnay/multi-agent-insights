#!/bin/bash

set -e

RAW_DIR="$(dirname "$0")/../data/raw"
OUTPUT_DIR="$(dirname "$0")/../data/processed"

echo "🔍 Phase 3: Chronological analysis (fixed)..."

mkdir -p "$OUTPUT_DIR"

echo "📅 Analyzing usage evolution by month..."

# Créer un fichier temporaire avec les données mensuelles
> "$OUTPUT_DIR/monthly_usage_raw.txt"

# Extraire mois et agent de chaque ligne
tail -n +2 "$RAW_DIR/agent_calls_metadata.csv" | while IFS=',' read -r timestamp session project agent prompt_len description; do
    # Extraire année-mois
    month="${timestamp:0:7}"
    if [ -n "$month" ] && [ -n "$agent" ]; then
        echo "$month,$agent" >> "$OUTPUT_DIR/monthly_usage_raw.txt"
    fi
done

# Compter les utilisations par mois et agent
echo "📊 Monthly usage by agent:"
sort "$OUTPUT_DIR/monthly_usage_raw.txt" | uniq -c | awk '{print $2 ": " $1}' | sort | head -20

# Analyser l'évolution mensuelle globale
echo ""
echo "📈 Total delegations per month:"
cut -d',' -f1 "$OUTPUT_DIR/monthly_usage_raw.txt" | sort | uniq -c | awk '{printf "%s: %d delegations\n", $2, $1}'

# Analyser l'évolution de la complexité des prompts par mois
echo ""
echo "📊 Prompt complexity evolution (average length by month):"
tail -n +2 "$RAW_DIR/agent_calls_metadata.csv" | awk -F',' '{
    month = substr($1, 1, 7)
    if (month != "" && $5 != "") {
        sum[month] += $5
        count[month]++
    }
}
END {
    for (m in sum) {
        if (count[m] > 0) {
            printf "%s: %d chars (n=%d)\n", m, sum[m]/count[m], count[m]
        }
    }
}' | sort

# Identifier les moments clés d'évolution
echo ""
echo "🔑 Key evolution points:"

# Top agents par mois
echo "  Top agent usage shifts:"
for month in "2025-07" "2025-08" "2025-09"; do
    echo "    $month:"
    grep "^$month" "$OUTPUT_DIR/monthly_usage_raw.txt" | cut -d',' -f2 | sort | uniq -c | sort -rn | head -3 | awk '{printf "      - %s: %d\n", $2, $1}'
done

# Nouvelles apparitions d'agents
echo ""
echo "  First appearances of agents:"
for agent in "junior-developer" "performance-optimizer" "refactoring-specialist"; do
    first_use=$(grep ",$agent," "$RAW_DIR/agent_calls_metadata.csv" | head -1 | cut -d',' -f1)
    if [ -n "$first_use" ]; then
        echo "    $agent: ${first_use:0:10}"
    fi
done

echo ""
echo "✅ Phase 3 chronological analysis completed (fixed)!"