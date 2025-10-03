#!/bin/bash
# Find git repos active on marathon dates

dates=("2025-09-16" "2025-09-18" "2025-09-20" "2025-09-21" "2025-09-22")

for date in "${dates[@]}"; do
    echo "=== Active repos on $date ==="
    find ~/dev -name ".git" -type d 2>/dev/null | while read gitdir; do
        repo=$(dirname "$gitdir")
        cd "$repo"
        commits=$(git log --all --since="$date 00:00" --until="$date 23:59" --oneline 2>/dev/null | wc -l | tr -d ' ')
        if [ "$commits" -gt 0 ]; then
            echo "$repo: $commits commits"
        fi
    done
    echo ""
done