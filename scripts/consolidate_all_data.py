#!/usr/bin/env python3
"""
Consolidate conversations from:
1. Time Machine snapshots (./data/conversations/snapshot*)
2. Current ~/.claude/projects/

Into: ./data/conversations/[project]/

Avoids duplicates based on filename.
"""

import shutil
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SNAPSHOTS_DIR = PROJECT_ROOT / "data" / "conversations"
CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"
OUTPUT_DIR = SNAPSHOTS_DIR  # Same, but we'll organize flat by project

def find_all_sessions():
    """
    Find all JSONL sessions from:
    1. Snapshots (./data/conversations/snapshot*)
    2. Current (~/.claude/projects/)

    Returns: {project_name: {session_filename: source_path}}
    """

    sessions_by_project = defaultdict(dict)

    # 1. Scan snapshots
    print("="*60)
    print("SCANNING TIME MACHINE SNAPSHOTS")
    print("="*60)

    snapshot_dirs = sorted([d for d in SNAPSHOTS_DIR.iterdir() if d.is_dir() and d.name.startswith("snapshot")])

    for snapshot in snapshot_dirs:
        print(f"\n📁 {snapshot.name}")

        # Each snapshot contains project directories
        project_dirs = [d for d in snapshot.iterdir() if d.is_dir()]

        for project_dir in project_dirs:
            project_name = project_dir.name
            sessions = list(project_dir.glob("*.jsonl"))

            if sessions:
                print(f"  └─ {project_name}: {len(sessions)} sessions")

                for session in sessions:
                    filename = session.name
                    # Only add if not already present (first snapshot wins)
                    if filename not in sessions_by_project[project_name]:
                        sessions_by_project[project_name][filename] = session

    # 2. Scan current ~/.claude/projects/
    print("\n" + "="*60)
    print("SCANNING CURRENT ~/.claude/projects/")
    print("="*60 + "\n")

    if CLAUDE_PROJECTS.exists():
        current_projects = [d for d in CLAUDE_PROJECTS.iterdir() if d.is_dir()]

        for project_dir in current_projects:
            project_name = project_dir.name
            sessions = list(project_dir.glob("*.jsonl"))

            if sessions:
                new_count = 0
                for session in sessions:
                    filename = session.name
                    # Only add if not already in snapshots
                    if filename not in sessions_by_project[project_name]:
                        sessions_by_project[project_name][filename] = session
                        new_count += 1

                print(f"📁 {project_name}: {len(sessions)} total, {new_count} new")

    return sessions_by_project

def consolidate_sessions(sessions_by_project, dry_run=False):
    """
    Copy all sessions to ./data/conversations/[project]/

    Args:
        sessions_by_project: {project: {filename: source_path}}
        dry_run: Show what would be copied
    """

    print("\n" + "="*60)
    print("CONSOLIDATING TO FLAT STRUCTURE")
    print("="*60 + "\n")

    stats = {
        "projects": 0,
        "sessions_total": 0,
        "sessions_copied": 0,
        "sessions_skipped": 0,
        "bytes_copied": 0
    }

    for project_name, sessions in sorted(sessions_by_project.items()):
        stats["projects"] += 1
        stats["sessions_total"] += len(sessions)

        # Create project directory
        project_output = OUTPUT_DIR / project_name

        if not dry_run:
            project_output.mkdir(parents=True, exist_ok=True)

        # Check existing files
        existing_files = {f.name for f in project_output.glob("*.jsonl")} if project_output.exists() else set()

        new_sessions = {fname: path for fname, path in sessions.items() if fname not in existing_files}

        if new_sessions:
            print(f"📁 {project_name}: {len(sessions)} total, {len(new_sessions)} to copy")

            for filename, source_path in new_sessions.items():
                dest = project_output / filename
                size = source_path.stat().st_size

                if dry_run:
                    print(f"  [DRY-RUN] Would copy: {filename} ({size:,} bytes)")
                else:
                    shutil.copy2(source_path, dest)
                    print(f"  ✓ Copied: {filename} ({size:,} bytes)")

                stats["sessions_copied"] += 1
                stats["bytes_copied"] += size
        else:
            print(f"📁 {project_name}: {len(sessions)} sessions (all already present)")
            stats["sessions_skipped"] += len(sessions)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Projects:          {stats['projects']}")
    print(f"Sessions total:    {stats['sessions_total']}")
    print(f"Sessions copied:   {stats['sessions_copied']}")
    print(f"Sessions skipped:  {stats['sessions_skipped']}")
    print(f"Data copied:       {stats['bytes_copied']:,} bytes ({stats['bytes_copied']//1024//1024} MB)")

    if dry_run:
        print("\n⚠️  DRY-RUN mode: No files were actually copied")
        print("Run without --dry-run to consolidate")
    else:
        print(f"\n✅ Consolidated to: {OUTPUT_DIR}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Consolidate snapshots + current sessions")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied")

    args = parser.parse_args()

    print("="*60)
    print("CONSOLIDATE ALL CONVERSATION DATA")
    print("="*60)
    print(f"Snapshots: {SNAPSHOTS_DIR}")
    print(f"Current:   {CLAUDE_PROJECTS}")
    print(f"Output:    {OUTPUT_DIR}")
    print(f"Mode:      {'DRY-RUN' if args.dry_run else 'CONSOLIDATE'}")
    print("="*60 + "\n")

    # Find all sessions
    sessions = find_all_sessions()

    # Consolidate
    consolidate_sessions(sessions, dry_run=args.dry_run)
