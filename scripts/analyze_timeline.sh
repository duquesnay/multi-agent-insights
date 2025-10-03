#!/bin/bash

set -e

RAW_DIR="$(dirname "$0")/../data/raw"
OUTPUT_DIR="$(dirname "$0")/../data/processed"

echo "🔍 Phase 3: Chronological analysis..."

mkdir -p "$OUTPUT_DIR"

echo "📅 Analyzing usage over time..."

# Analyser par mois
echo "timestamp,agent_type" > "$OUTPUT_DIR/timeline_data.csv"
tail -n +2 "$RAW_DIR/agent_calls_metadata.csv" | cut -d',' -f1,4 >> "$OUTPUT_DIR/timeline_data.csv"

# Grouper par mois et agent
awk -F',' '{
    # Extraire année-mois du timestamp ISO
    split($1, date_parts, "T")
    split(date_parts[1], ymd, "-")
    month = ymd[1] "-" ymd[2]
    agent = $2
    monthly[month][agent]++
    all_months[month] = 1
    all_agents[agent] = 1
}
END {
    # Header
    printf "month"
    for (agent in all_agents) printf ",%s", agent
    print ""

    # Data par mois
    for (month in all_months) {
        printf "%s", month
        for (agent in all_agents) {
            printf ",%d", monthly[month][agent] + 0
        }
        print ""
    }
}' "$OUTPUT_DIR/timeline_data.csv" | sort > "$OUTPUT_DIR/monthly_usage.csv"

echo "📊 Monthly usage evolution:"
head -10 "$OUTPUT_DIR/monthly_usage.csv"

# Analyser les tendances hebdomadaires pour les top agents
echo ""
echo "📅 Weekly patterns (Top 3 agents):"
for agent in "developer" "git-workflow-manager" "backlog-manager"; do
    echo "  $agent:"
    grep ",$agent" "$OUTPUT_DIR/timeline_data.csv" | awk -F',' '{
        # Extraire la date
        split($1, date_parts, "T")
        date = date_parts[1]

        # Convertir en jour de la semaine (approximatif)
        cmd = "date -j -f \"%Y-%m-%d\" \"" date "\" \"+%u\" 2>/dev/null || echo 0"
        cmd | getline weekday
        close(cmd)

        if (weekday > 0) weekdays[weekday]++
    }
    END {
        for (i=1; i<=7; i++) {
            day_name = (i==1?"Mon":(i==2?"Tue":(i==3?"Wed":(i==4?"Thu":(i==5?"Fri":(i==6?"Sat":"Sun"))))))
            printf "    %s: %d\n", day_name, weekdays[i] + 0
        }
    }'
done

# Analyser l'évolution de la complexité des prompts
echo ""
echo "📈 Prompt complexity evolution (by month):"
awk -F',' 'NR>1 {
    split($1, date_parts, "T")
    split(date_parts[1], ymd, "-")
    month = ymd[1] "-" ymd[2]
    length = $5
    months[month] += length
    counts[month]++
}
END {
    for (month in months) {
        avg = months[month] / counts[month]
        printf "%s: avg=%d chars (%d delegations)\n", month, avg, counts[month]
    }
}' "$RAW_DIR/agent_calls_metadata.csv" | sort

echo ""
echo "✅ Phase 3 chronological analysis completed!"