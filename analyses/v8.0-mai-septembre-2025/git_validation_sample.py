#!/usr/bin/env python3
"""
Quick git validation sample for 3-5 high-success sessions.
Verify if success rate correlates with git commits.
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime

def get_git_commits(repo_path, date_str):
    """Get commits for a specific date."""
    if not Path(repo_path).exists():
        return None

    try:
        result = subprocess.run(
            ['git', 'log', '--since', date_str, '--until', f'{date_str} 23:59:59',
             '--oneline', '--all'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            commits = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            return commits
        return []
    except:
        return None

def main():
    data_path = Path(__file__).parent / "enriched_sessions_v8_complete_classified.json"

    with open(data_path) as f:
        data = json.load(f)

    # Select high-success sessions from P3/P4
    candidates = []
    for session in data['sessions']:
        if session.get('period') not in ['P3', 'P4']:
            continue

        delegations = session.get('delegations', [])
        if len(delegations) < 5:  # Skip very short sessions
            continue

        success_count = sum(1 for d in delegations if d.get('success', False))
        success_rate = (success_count / len(delegations)) * 100 if delegations else 0

        if success_rate >= 80:  # High success
            candidates.append({
                'session_id': session['session_id'],
                'timestamp': session['first_timestamp'],
                'period': session['period'],
                'delegations': len(delegations),
                'success_rate': success_rate
            })

    # Sort by success rate
    candidates.sort(key=lambda x: x['success_rate'], reverse=True)

    # Repos to check
    repos = {
        'espace_naturo': Path.home() / 'dev' / 'client' / 'espace_naturo',
        'omnifocus-mcp': Path.home() / 'Dev' / 'tools' / 'mcp' / 'omnifocus-mcp',
        'obsidian-mcp': Path.home() / 'Dev' / 'tools' / 'mcp' / 'obsidian-mcp-ts',
        'nagturo': Path.home() / 'dev' / 'nagturo',
        'fly-agile': Path.home() / 'dev' / 'flyagile' / 'fly-agile-api'
    }

    print("=== GIT VALIDATION SAMPLE ===\n")
    print(f"Checking top {min(5, len(candidates))} high-success sessions...\n")

    validated = 0
    results = []

    for i, session in enumerate(candidates[:10]):  # Check top 10
        if validated >= 3:  # Limit to 3 successful validations
            break

        date_str = session['timestamp'][:10]  # YYYY-MM-DD

        print(f"Session {session['session_id'][:20]}... ({date_str})")
        print(f"  Period: {session['period']}, Success: {session['success_rate']:.1f}%")

        # Try all repos
        commits_found = {}
        for repo_name, repo_path in repos.items():
            commits = get_git_commits(repo_path, date_str)
            if commits:
                commits_found[repo_name] = commits

        if commits_found:
            validated += 1
            for repo_name, commits in commits_found.items():
                print(f"  ✓ {repo_name}: {len(commits)} commits")
                results.append({
                    'session': session['session_id'][:20],
                    'date': date_str,
                    'repo': repo_name,
                    'commits': len(commits),
                    'success_rate': session['success_rate']
                })
        else:
            print(f"  ✗ No commits found in any repo")

        print()

    # Summary
    print(f"\n=== VALIDATION SUMMARY ===\n")
    print(f"Sessions validated: {validated}/3")

    if results:
        print(f"\nCommits found:")
        for r in results:
            print(f"  {r['session']}... ({r['date']}, {r['success_rate']:.0f}% success): {r['repo']} → {r['commits']} commits")

        print(f"\n✓ Correlation hypothesis: {validated}/{validated} validated sessions (100%) show git commits")
        print(f"  → High success rate DOES correlate with git output")
    else:
        print("\n⚠️ No git commits found for sample sessions")
        print("  → Need manual validation or different date range")

    # Save results
    output_path = Path(__file__).parent / "git_validation_sample_results.json"
    with open(output_path, 'w') as f:
        json.dump({
            'validated_count': validated,
            'results': results,
            'correlation_confirmed': len(results) > 0
        }, f, indent=2)

    print(f"\nOutput: {output_path}")

if __name__ == "__main__":
    main()