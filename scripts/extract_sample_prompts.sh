#!/bin/bash

set -e

RAW_DIR="$(dirname "$0")/../data/raw"
OUTPUT_DIR="$(dirname "$0")/../data/processed"

echo "🔍 Extracting sample prompts for analysis..."

# Pour chaque top agent, extraire quelques prompts représentatifs
TOP_AGENTS=("developer" "git-workflow-manager" "backlog-manager" "solution-architect" "architecture-reviewer")

for agent in "${TOP_AGENTS[@]}"; do
    echo ""
    echo "📝 Extracting samples for: $agent"

    # Extraire 3 prompts courts, moyens et longs
    grep "\"subagent_type\":\"$agent\"" "$RAW_DIR/delegation_raw.jsonl" | while IFS= read -r line; do
        PROMPT=$(echo "$line" | jq -r '.message.content[] | select(.name == "Task") | .input.prompt // empty')
        DESCRIPTION=$(echo "$line" | jq -r '.message.content[] | select(.name == "Task") | .input.description // empty')
        TIMESTAMP=$(echo "$line" | jq -r '.timestamp')

        if [ -n "$PROMPT" ] && [ "$PROMPT" != "null" ]; then
            LENGTH=${#PROMPT}
            echo "=== $agent - $DESCRIPTION ($LENGTH chars) - $TIMESTAMP ===" >> "$OUTPUT_DIR/${agent}_prompts.txt"
            echo "$PROMPT" >> "$OUTPUT_DIR/${agent}_prompts.txt"
            echo "" >> "$OUTPUT_DIR/${agent}_prompts.txt"
        fi
    done

    # Compter les échantillons
    if [ -f "$OUTPUT_DIR/${agent}_prompts.txt" ]; then
        SAMPLE_COUNT=$(grep "^===" "$OUTPUT_DIR/${agent}_prompts.txt" | wc -l)
        echo "   Extracted $SAMPLE_COUNT prompt samples"
    fi
done

echo ""
echo "✅ Sample extraction completed!"