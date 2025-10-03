#!/bin/bash

# Extraction des délégations aux sous-agents
# Phase 1: Extraction automatisée avec contexte complet

set -e

PROJECTS_DIR="$HOME/.claude/projects"
OUTPUT_DIR="$(dirname "$0")/../data/raw"
CUTOFF_DATE="2025-06-28"

echo "🔍 Extracting delegation patterns from Claude Code conversations..."
echo "📁 Source: $PROJECTS_DIR"
echo "📅 Since: $CUTOFF_DATE"
echo "💾 Output: $OUTPUT_DIR"

# Créer les répertoires de sortie
mkdir -p "$OUTPUT_DIR"

# Étape 1: Identifier tous les fichiers des 3 derniers mois
echo "📋 Finding relevant conversation files..."
find "$PROJECTS_DIR" -name "*.jsonl" -newermt "$CUTOFF_DATE" > "$OUTPUT_DIR/conversation_files.list"
TOTAL_FILES=$(wc -l < "$OUTPUT_DIR/conversation_files.list")
echo "✅ Found $TOTAL_FILES conversation files"

# Étape 2: Extraire toutes les délégations avec métadonnées
echo "🔗 Extracting all Task delegations..."
> "$OUTPUT_DIR/delegation_raw.jsonl"
> "$OUTPUT_DIR/agent_calls_metadata.csv"

# Header CSV
echo "timestamp,session_id,project_path,agent_type,prompt_length,context_messages" > "$OUTPUT_DIR/agent_calls_metadata.csv"

DELEGATION_COUNT=0

while IFS= read -r file; do
    echo "Processing: $(basename "$file")"

    # Extraire les délégations de ce fichier
    grep '"name":"Task"' "$file" | while IFS= read -r line; do
        # Parser le JSON pour extraire les informations
        TIMESTAMP=$(echo "$line" | jq -r '.timestamp // "unknown"')
        SESSION_ID=$(echo "$line" | jq -r '.sessionId // "unknown"')
        PROJECT_PATH=$(echo "$line" | jq -r '.cwd // "unknown"')

        # Extraire l'input de la Task
        TASK_INPUT=$(echo "$line" | jq -r '.message.content' | jq -r '.[] | select(.name == "Task") | .input')
        AGENT_TYPE=$(echo "$TASK_INPUT" | jq -r '.subagent_type // "unknown"')
        PROMPT_TEXT=$(echo "$TASK_INPUT" | jq -r '.prompt // ""')
        PROMPT_LENGTH=${#PROMPT_TEXT}

        # Sauvegarder la délégation complète
        echo "$line" >> "$OUTPUT_DIR/delegation_raw.jsonl"

        # Sauvegarder les métadonnées
        echo "$TIMESTAMP,$SESSION_ID,$PROJECT_PATH,$AGENT_TYPE,$PROMPT_LENGTH,0" >> "$OUTPUT_DIR/agent_calls_metadata.csv"

        DELEGATION_COUNT=$((DELEGATION_COUNT + 1))
    done
done < "$OUTPUT_DIR/conversation_files.list"

echo "✅ Extracted $DELEGATION_COUNT delegations"

# Étape 3: Créer un index des délégations par session pour extraction du contexte
echo "📇 Creating delegation index..."
jq -r '[.timestamp, .sessionId, .message.content | fromjson | .[] | select(.name == "Task") | .input.subagent_type] | @csv' "$OUTPUT_DIR/delegation_raw.jsonl" > "$OUTPUT_DIR/delegation_index.csv"

# Statistiques finales
echo ""
echo "📊 Extraction Summary:"
echo "   Files processed: $TOTAL_FILES"
echo "   Delegations found: $DELEGATION_COUNT"
echo "   Raw data: $OUTPUT_DIR/delegation_raw.jsonl"
echo "   Metadata: $OUTPUT_DIR/agent_calls_metadata.csv"
echo "   Index: $OUTPUT_DIR/delegation_index.csv"

# Vérification basique
if [ $DELEGATION_COUNT -gt 0 ]; then
    echo "✅ Extraction completed successfully"
else
    echo "❌ No delegations found - check date filter or file format"
    exit 1
fi