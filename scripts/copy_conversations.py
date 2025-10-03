#!/usr/bin/env python3
"""
Copy conversations from ~/.claude/projects/ to ./data/conversations/[project]/

Incremental: Only copies new files not already present locally.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

# Paths
CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"
LOCAL_DATA = Path(__file__).parent.parent / "data" / "conversations"

def get_project_sessions(project_dir: Path):
    """Get all JSONL session files in a project directory."""
    return sorted(project_dir.glob("*.jsonl"))

def copy_new_sessions(project_name: str = None, dry_run: bool = False):
    """
    Copy new sessions from ~/.claude/projects/ to local archive.

    Args:
        project_name: Specific project to copy (None = all projects)
        dry_run: Show what would be copied without copying
    """

    if not CLAUDE_PROJECTS.exists():
        print(f"❌ Source not found: {CLAUDE_PROJECTS}")
        return

    # Get all project directories
    if project_name:
        project_dirs = [CLAUDE_PROJECTS / project_name]
        if not project_dirs[0].exists():
            print(f"❌ Project not found: {project_name}")
            return
    else:
        project_dirs = [d for d in CLAUDE_PROJECTS.iterdir() if d.is_dir()]

    stats = {
        "projects_scanned": 0,
        "sessions_found": 0,
        "sessions_new": 0,
        "sessions_skipped": 0,
        "bytes_copied": 0
    }

    for project_dir in sorted(project_dirs):
        project = project_dir.name
        stats["projects_scanned"] += 1

        # Get sessions in source
        source_sessions = get_project_sessions(project_dir)
        stats["sessions_found"] += len(source_sessions)

        if not source_sessions:
            print(f"📁 {project}: 0 sessions")
            continue

        # Create local project directory
        local_project = LOCAL_DATA / project
        if not dry_run:
            local_project.mkdir(parents=True, exist_ok=True)

        # Get existing local sessions
        existing_local = {f.name for f in local_project.glob("*.jsonl")} if local_project.exists() else set()

        # Copy new sessions
        new_sessions = [s for s in source_sessions if s.name not in existing_local]

        if new_sessions:
            print(f"📁 {project}: {len(source_sessions)} total, {len(new_sessions)} new")

            for session in new_sessions:
                dest = local_project / session.name

                if dry_run:
                    print(f"  [DRY-RUN] Would copy: {session.name} ({session.stat().st_size} bytes)")
                    stats["bytes_copied"] += session.stat().st_size
                else:
                    shutil.copy2(session, dest)
                    size = dest.stat().st_size
                    stats["bytes_copied"] += size
                    print(f"  ✓ Copied: {session.name} ({size} bytes)")

                stats["sessions_new"] += 1
        else:
            print(f"📁 {project}: {len(source_sessions)} sessions (all already copied)")
            stats["sessions_skipped"] += len(source_sessions)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Projects scanned:  {stats['projects_scanned']}")
    print(f"Sessions found:    {stats['sessions_found']}")
    print(f"Sessions new:      {stats['sessions_new']}")
    print(f"Sessions skipped:  {stats['sessions_skipped']}")
    print(f"Data copied:       {stats['bytes_copied']:,} bytes ({stats['bytes_copied']//1024//1024} MB)")

    if dry_run:
        print("\n⚠️  DRY-RUN mode: No files were actually copied")
        print("Run without --dry-run to copy files")
    else:
        print(f"\n✅ Archive location: {LOCAL_DATA}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Copy conversations from ~/.claude/projects/ to local archive")
    parser.add_argument("--project", help="Specific project to copy (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied without copying")

    args = parser.parse_args()

    print("="*60)
    print("COPY CONVERSATIONS TO LOCAL ARCHIVE")
    print("="*60)
    print(f"Source: {CLAUDE_PROJECTS}")
    print(f"Dest:   {LOCAL_DATA}")
    print(f"Mode:   {'DRY-RUN' if args.dry_run else 'COPY'}")
    print("="*60 + "\n")

    copy_new_sessions(project_name=args.project, dry_run=args.dry_run)
