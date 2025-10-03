#!/bin/bash

set -e

PROJECTS_DIR="$HOME/.claude/projects"
OUTPUT_DIR="$(dirname "$0")/../data/raw"
CUTOFF_DATE="2025-06-28"

echo "🔍 Extracting delegation patterns from Claude Code conversations..."

# Créer les répertoires de sortie
mkdir -p "$OUTPUT_DIR"

# Étape 1: Identifier tous les fichiers des 3 derniers mois
echo "📋 Finding relevant conversation files..."
find "$PROJECTS_DIR" -name "*.jsonl" -newermt "$CUTOFF_DATE" > "$OUTPUT_DIR/conversation_files.list"
TOTAL_FILES=$(wc -l < "$OUTPUT_DIR/conversation_files.list")
echo "✅ Found $TOTAL_FILES conversation files"

# Étape 2: Extraire toutes les délégations
echo "🔗 Extracting all Task delegations..."

# Initialiser les fichiers de sortie
> "$OUTPUT_DIR/delegation_raw.jsonl"
> "$OUTPUT_DIR/agent_calls_metadata.csv"

# Header CSV
echo "timestamp,session_id,project_path,agent_type,prompt_length,description" > "$OUTPUT_DIR/agent_calls_metadata.csv"

DELEGATION_COUNT=0

while IFS= read -r file; do
    echo "Processing: $(basename "$file")"

    # Extraire toutes les lignes contenant Task pour ce fichier
    if grep -q '"name":"Task"' "$file"; then
        grep '"name":"Task"' "$file" | while IFS= read -r line; do
            # Extraire les métadonnées de base
            TIMESTAMP=$(echo "$line" | jq -r '.timestamp // "unknown"')
            SESSION_ID=$(echo "$line" | jq -r '.sessionId // "unknown"')
            PROJECT_PATH=$(echo "$line" | jq -r '.cwd // "unknown"')

            # Extraire l'input de la Task depuis le content
            TASK_INPUT=$(echo "$line" | jq -r '.message.content[] | select(.name == "Task") | .input')

            if [ "$TASK_INPUT" != "null" ] && [ -n "$TASK_INPUT" ]; then
                AGENT_TYPE=$(echo "$TASK_INPUT" | jq -r '.subagent_type // "unknown"')
                PROMPT_TEXT=$(echo "$TASK_INPUT" | jq -r '.prompt // ""')
                DESCRIPTION=$(echo "$TASK_INPUT" | jq -r '.description // ""')
                PROMPT_LENGTH=${#PROMPT_TEXT}

                # Sauvegarder la délégation complète
                echo "$line" >> "$OUTPUT_DIR/delegation_raw.jsonl"

                # Sauvegarder les métadonnées (échapper les virgules dans les champs)
                CLEAN_DESC=$(echo "$DESCRIPTION" | tr ',' '_')
                echo "$TIMESTAMP,$SESSION_ID,$PROJECT_PATH,$AGENT_TYPE,$PROMPT_LENGTH,$CLEAN_DESC" >> "$OUTPUT_DIR/agent_calls_metadata.csv"

                DELEGATION_COUNT=$((DELEGATION_COUNT + 1))
            fi
        done
    fi
done < "$OUTPUT_DIR/conversation_files.list"

echo "✅ Extracted $DELEGATION_COUNT delegations"

# Étape 3: Statistiques par agent
echo "📊 Generating agent statistics..."
tail -n +2 "$OUTPUT_DIR/agent_calls_metadata.csv" | cut -d',' -f4 | sort | uniq -c | sort -rn > "$OUTPUT_DIR/agent_usage_stats.txt"

echo ""
echo "📊 Top agents:"
head -10 "$OUTPUT_DIR/agent_usage_stats.txt"

echo ""
echo "📊 Extraction Summary:"
echo "   Files processed: $TOTAL_FILES"
echo "   Delegations found: $DELEGATION_COUNT"
echo "   Raw data: $OUTPUT_DIR/delegation_raw.jsonl"
echo "   Metadata: $OUTPUT_DIR/agent_calls_metadata.csv"
echo "   Agent stats: $OUTPUT_DIR/agent_usage_stats.txt"

# Vérification
if [ $DELEGATION_COUNT -gt 0 ]; then
    echo "✅ Extraction completed successfully"
else
    echo "❌ No delegations found"
    exit 1
fi