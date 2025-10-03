#!/usr/bin/env python3
"""Batch fix hardcoded paths in Python files."""

import re
from pathlib import Path

# Map of hardcoded paths to config constants
PATH_REPLACEMENTS = {
    '/Users/guillaume/dev/tasks/delegation-retrospective/data/raw/delegation_raw.jsonl': 'DELEGATION_RAW_FILE',
    '/Users/guillaume/dev/tasks/delegation-retrospective/data/full_sessions_data.json': 'SESSIONS_DATA_FILE',
    '/Users/guillaume/dev/tasks/delegation-retrospective/data/enriched_sessions_data.json': 'ENRICHED_SESSIONS_FILE',
    '/Users/guillaume/dev/tasks/delegation-retrospective/data/routing_patterns_by_period.json': 'ROUTING_PATTERNS_FILE',
    '/Users/guillaume/dev/tasks/delegation-retrospective/data/routing_quality_analysis.json': 'ROUTING_QUALITY_FILE',
    '/Users/guillaume/dev/tasks/delegation-retrospective/data/good_routing_patterns.json': 'GOOD_ROUTING_FILE',
    '/Users/guillaume/dev/tasks/delegation-retrospective/data/system_metrics_report.json': 'SYSTEM_METRICS_FILE',
    '/Users/guillaume/dev/tasks/delegation-retrospective/data/transition_analysis.json': 'TRANSITION_ANALYSIS_FILE',
    '/Users/guillaume/dev/tasks/delegation-retrospective/routage-patterns-analysis.md': 'PROJECT_ROOT / "routage-patterns-analysis.md"',
    '/Users/guillaume/dev/tasks/delegation-retrospective/observations.md': 'PROJECT_ROOT / "observations.md"',
}

# Relative paths that should also be replaced
RELATIVE_PATH_REPLACEMENTS = {
    'data/raw/delegation_raw.jsonl': 'DELEGATION_RAW_FILE',
    'data/full_sessions_data.json': 'SESSIONS_DATA_FILE',
    'data/enriched_sessions_data.json': 'ENRICHED_SESSIONS_FILE',
}

# Config imports needed based on what's used in file
CONFIG_IMPORTS = {
    'DELEGATION_RAW_FILE': 'DELEGATION_RAW_FILE',
    'SESSIONS_DATA_FILE': 'SESSIONS_DATA_FILE',
    'ENRICHED_SESSIONS_FILE': 'ENRICHED_SESSIONS_FILE',
    'ROUTING_PATTERNS_FILE': 'ROUTING_PATTERNS_FILE',
    'ROUTING_QUALITY_FILE': 'ROUTING_QUALITY_FILE',
    'GOOD_ROUTING_FILE': 'GOOD_ROUTING_FILE',
    'SYSTEM_METRICS_FILE': 'SYSTEM_METRICS_FILE',
    'TRANSITION_ANALYSIS_FILE': 'TRANSITION_ANALYSIS_FILE',
    'PROJECT_ROOT': 'PROJECT_ROOT',
}

def fix_file(filepath: Path) -> tuple[bool, list[str]]:
    """Fix hardcoded paths in a file.

    Returns:
        (modified, config_imports_needed)
    """
    content = filepath.read_text()
    original = content
    imports_needed = set()

    # Replace absolute paths
    for old_path, const_name in PATH_REPLACEMENTS.items():
        if old_path in content:
            # Replace in string literals
            content = content.replace(f"'{old_path}'", f"str({const_name})")
            content = content.replace(f'"{old_path}"', f"str({const_name})")
            imports_needed.add(const_name)

    # Replace relative paths
    for old_path, const_name in RELATIVE_PATH_REPLACEMENTS.items():
        if f"'{old_path}'" in content or f'"{old_path}"' in content:
            content = content.replace(f"'{old_path}'", f"str({const_name})")
            content = content.replace(f'"{old_path}"', f"str({const_name})")
            imports_needed.add(const_name)

    # Add import if needed and not already present
    if imports_needed and 'from common.config import' not in content:
        # Find where to insert import (after docstring if present)
        lines = content.split('\n')
        insert_pos = 0

        # Skip shebang
        if lines[0].startswith('#!'):
            insert_pos = 1

        # Skip docstring
        in_docstring = False
        for i in range(insert_pos, len(lines)):
            if '"""' in lines[i] or "'''" in lines[i]:
                if not in_docstring:
                    in_docstring = True
                else:
                    insert_pos = i + 1
                    break
            elif not in_docstring and lines[i].strip():
                # Found first non-empty line that's not part of docstring
                insert_pos = i
                break

        # Find last import line
        for i in range(insert_pos, len(lines)):
            if lines[i].startswith('import ') or lines[i].startswith('from '):
                insert_pos = i + 1
            elif lines[i].strip() and not lines[i].startswith('#'):
                break

        # Build import statement
        import_items = sorted(imports_needed)
        import_line = f"from common.config import {', '.join(import_items)}"

        lines.insert(insert_pos, import_line)
        content = '\n'.join(lines)

    # Write if modified
    if content != original:
        filepath.write_text(content)
        return True, list(imports_needed)

    return False, []


def main():
    """Fix all Python files with hardcoded paths."""
    project_root = Path(__file__).parent.parent

    # Find all Python files
    python_files = list(project_root.glob('*.py'))
    python_files.extend(project_root.glob('data/raw/*.py'))

    fixed_files = []

    for filepath in python_files:
        # Skip common/ directory files
        if 'common/' in str(filepath):
            continue

        modified, imports = fix_file(filepath)
        if modified:
            fixed_files.append((filepath.name, imports))
            print(f"Fixed: {filepath.name}")

    print(f"\n{len(fixed_files)} files updated:")
    for filename, imports in fixed_files:
        print(f"  {filename}: imported {', '.join(imports)}")


if __name__ == '__main__':
    main()
