#!/bin/bash

set -e

PROJECTS_DIR="$HOME/.claude/projects"
OUTPUT_DIR="$(dirname "$0")/../data/raw"
CUTOFF_DATE="2025-06-28"

echo "🔍 Robust extraction of delegation patterns..."

# Créer les répertoires de sortie
mkdir -p "$OUTPUT_DIR"

echo "📋 Step 1: Extract all Task delegations..."

# Extraction directe de toutes les délégations
find "$PROJECTS_DIR" -name "*.jsonl" -newermt "$CUTOFF_DATE" -exec grep -h '"name":"Task"' {} \; > "$OUTPUT_DIR/delegation_raw.jsonl"

DELEGATION_COUNT=$(wc -l < "$OUTPUT_DIR/delegation_raw.jsonl")
echo "✅ Extracted $DELEGATION_COUNT delegations"

echo "📊 Step 2: Generate metadata..."

# Créer le fichier de métadonnées
echo "timestamp,session_id,project_path,agent_type,prompt_length,description" > "$OUTPUT_DIR/agent_calls_metadata.csv"

# Parser chaque délégation pour extraire les métadonnées
cat "$OUTPUT_DIR/delegation_raw.jsonl" | while IFS= read -r line; do
    TIMESTAMP=$(echo "$line" | jq -r '.timestamp // "unknown"')
    SESSION_ID=$(echo "$line" | jq -r '.sessionId // "unknown"')
    PROJECT_PATH=$(echo "$line" | jq -r '.cwd // "unknown"')

    # Extraire l'input de la Task
    TASK_INPUT=$(echo "$line" | jq -r '.message.content[] | select(.name == "Task") | .input // empty')

    if [ -n "$TASK_INPUT" ] && [ "$TASK_INPUT" != "null" ]; then
        AGENT_TYPE=$(echo "$TASK_INPUT" | jq -r '.subagent_type // "unknown"')
        PROMPT_TEXT=$(echo "$TASK_INPUT" | jq -r '.prompt // ""')
        DESCRIPTION=$(echo "$TASK_INPUT" | jq -r '.description // ""')
        PROMPT_LENGTH=${#PROMPT_TEXT}

        # Nettoyer la description pour CSV
        CLEAN_DESC=$(echo "$DESCRIPTION" | tr ',' '_' | tr '\n' ' ')

        echo "$TIMESTAMP,$SESSION_ID,$PROJECT_PATH,$AGENT_TYPE,$PROMPT_LENGTH,$CLEAN_DESC" >> "$OUTPUT_DIR/agent_calls_metadata.csv"
    fi
done

echo "📊 Step 3: Generate statistics..."

# Statistiques par agent
tail -n +2 "$OUTPUT_DIR/agent_calls_metadata.csv" | cut -d',' -f4 | sort | uniq -c | sort -rn > "$OUTPUT_DIR/agent_usage_stats.txt"

echo ""
echo "📊 Top 10 agents:"
head -10 "$OUTPUT_DIR/agent_usage_stats.txt"

echo ""
echo "📊 Prompt length distribution:"
tail -n +2 "$OUTPUT_DIR/agent_calls_metadata.csv" | cut -d',' -f5 | sort -n | awk '
    {
        a[int($1/100)*100]++
    }
    END {
        for (i in a) print i"-"(i+99)": " a[i]
    }
' | sort -n

echo ""
echo "📊 Final Summary:"
echo "   Total delegations: $DELEGATION_COUNT"
echo "   Files created:"
echo "     - Raw data: $OUTPUT_DIR/delegation_raw.jsonl"
echo "     - Metadata: $OUTPUT_DIR/agent_calls_metadata.csv"
echo "     - Agent stats: $OUTPUT_DIR/agent_usage_stats.txt"

echo "✅ Phase 1 extraction completed successfully!"