#!/bin/bash

set -e

PROJECTS_DIR="$HOME/.claude/projects"
OUTPUT_DIR="$(dirname "$0")/../data/raw"
CUTOFF_DATE="2025-06-28"

echo "🔍 Simple extraction test..."

# Créer les répertoires de sortie
mkdir -p "$OUTPUT_DIR"

# Trouver les fichiers récents
find "$PROJECTS_DIR" -name "*.jsonl" -newermt "$CUTOFF_DATE" | head -5 > "$OUTPUT_DIR/test_files.list"

echo "Test files:"
cat "$OUTPUT_DIR/test_files.list"

# Tester avec un seul fichier
if [ -s "$OUTPUT_DIR/test_files.list" ]; then
    TEST_FILE=$(head -1 "$OUTPUT_DIR/test_files.list")
    echo ""
    echo "Testing with: $TEST_FILE"

    # Chercher les appels Task
    echo "Looking for Task calls..."
    grep -c '"name":"Task"' "$TEST_FILE" || echo "No Task calls found"

    # Montrer un exemple
    echo "Example Task call:"
    grep '"name":"Task"' "$TEST_FILE" | head -1 | jq '.'
else
    echo "No files found"
fi