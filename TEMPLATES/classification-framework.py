#!/usr/bin/env python3
"""
Classification Framework Template
Reusable classifier for marathons, failures, and other patterns.

Usage:
    python classification-framework.py <enriched_sessions_data.json>
"""
import json
import sys
from pathlib import Path
from collections import defaultdict


def classify_marathon(session):
    """
    Classify marathon as positive (productive) vs negative (pathological).

    Criteria:
    - POSITIVE: >20 deleg, >85% success, productive work
    - NEGATIVE: >20 deleg, <80% success, cascading failures
    - AMBIGUOUS: 80-85% success, need manual review

    Returns dict with classification + metrics, or None if not marathon.
    """
    deleg_count = session['delegation_count']
    delegations = session.get('delegations', [])

    if deleg_count <= 20:
        return None  # Not a marathon

    # Calculate success rate
    successes = sum(1 for d in delegations if d.get('success') is True)
    failures = sum(1 for d in delegations if d.get('success') is False)
    total = len(delegations)
    success_rate = (successes / total * 100) if total > 0 else 0

    # Check if backlog-related (planning/organization work)
    backlog_related = any(
        d.get('agent_type') == 'backlog-manager' or
        'backlog' in d.get('prompt', '').lower()
        for d in delegations
    )

    # Check for cascade patterns (auto-delegations)
    cascade_count = 0
    for i in range(len(delegations) - 1):
        if delegations[i].get('agent_type') == delegations[i+1].get('agent_type'):
            cascade_count += 1

    cascade_rate = (cascade_count / (total-1) * 100) if total > 1 else 0

    # Classification logic
    if success_rate >= 85:
        classification = "POSITIVE"
    elif success_rate < 80:
        classification = "NEGATIVE"
    else:
        classification = "AMBIGUOUS"

    return {
        'classification': classification,
        'success_rate': round(success_rate, 1),
        'failure_rate': round((failures/total*100) if total > 0 else 0, 1),
        'backlog_related': backlog_related,
        'cascade_rate': round(cascade_rate, 1),
        'delegations': deleg_count,
        'session_id': session['session_id'][:8],
        'date': session.get('first_timestamp', '')[:10]
    }


def classify_failure(delegation):
    """
    Classify failure by type (taxonomy).

    Returns failure category, or None if success.
    """
    if delegation.get('success') is not False:
        return None  # Not a failure

    result = str(delegation.get('result_preview', '')).lower()

    if 'interrupted by user' in result:
        return 'USER_TOOL_INTERVENTION'  # Ambiguous
    elif 'request interrupted' in result:
        return 'USER_INTERRUPT'  # User stopped
    elif 'agent not found' in result:
        return 'AGENT_NOT_FOUND'  # Config issue
    elif 'plan rejected' in result or 'plan mode' in result:
        return 'PLAN_REJECTED'  # User rejected plan
    elif 'timeout' in result:
        return 'TIMEOUT'  # Execution timeout
    elif 'error' in result:
        return 'EXECUTION_ERROR'  # Code/tool error
    else:
        return 'UNKNOWN'  # Needs investigation


def analyze_marathons(sessions):
    """Classify all marathons in dataset."""
    marathons = []

    for session in sessions:
        marathon_data = classify_marathon(session)
        if marathon_data:
            marathons.append(marathon_data)

    # Sort by delegation count
    marathons.sort(key=lambda x: x['delegations'], reverse=True)

    # Stats by classification
    positive = [m for m in marathons if m['classification'] == 'POSITIVE']
    negative = [m for m in marathons if m['classification'] == 'NEGATIVE']
    ambiguous = [m for m in marathons if m['classification'] == 'AMBIGUOUS']

    stats = {
        'total_marathons': len(marathons),
        'positive': len(positive),
        'negative': len(negative),
        'ambiguous': len(ambiguous),
        'avg_cascade_positive': sum(m['cascade_rate'] for m in positive) / len(positive) if positive else 0,
        'avg_cascade_negative': sum(m['cascade_rate'] for m in negative) / len(negative) if negative else 0,
        'backlog_positive': sum(1 for m in positive if m['backlog_related']),
        'backlog_negative': sum(1 for m in negative if m['backlog_related'])
    }

    return {
        'stats': stats,
        'marathons': {
            'positive': positive,
            'negative': negative,
            'ambiguous': ambiguous
        }
    }


def analyze_failures(sessions):
    """Classify all failures by taxonomy."""
    failures = defaultdict(list)
    total_failures = 0

    for session in sessions:
        for deleg in session.get('delegations', []):
            category = classify_failure(deleg)
            if category:
                total_failures += 1
                failures[category].append({
                    'session_id': session['session_id'][:8],
                    'date': session.get('first_timestamp', '')[:10],
                    'agent_type': deleg.get('agent_type'),
                    'description': deleg.get('description', '')[:50]
                })

    # Stats
    stats = {
        'total_failures': total_failures,
        'by_category': {
            cat: len(items) for cat, items in failures.items()
        },
        'ambiguous_rate': (len(failures.get('USER_TOOL_INTERVENTION', [])) / total_failures * 100) if total_failures > 0 else 0
    }

    return {
        'stats': stats,
        'failures': dict(failures)
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python classification-framework.py <enriched_sessions_data.json>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)

    print(f"Loading data from {input_file}...")
    with open(input_file) as f:
        data = json.load(f)

    sessions = data.get('sessions', [])
    print(f"Loaded {len(sessions)} sessions\n")

    # Analyze marathons
    print("=== MARATHON CLASSIFICATION ===\n")
    marathon_results = analyze_marathons(sessions)

    stats = marathon_results['stats']
    print(f"Total marathons (>20 deleg): {stats['total_marathons']}")
    print(f"  POSITIVE (>85% success): {stats['positive']}")
    print(f"  NEGATIVE (<80% success): {stats['negative']}")
    print(f"  AMBIGUOUS (80-85%): {stats['ambiguous']}")
    print()

    print(f"Average cascade rate:")
    print(f"  Positive: {stats['avg_cascade_positive']:.1f}%")
    print(f"  Negative: {stats['avg_cascade_negative']:.1f}%")
    print()

    print(f"Backlog-related:")
    print(f"  Positive: {stats['backlog_positive']}/{stats['positive']}")
    print(f"  Negative: {stats['backlog_negative']}/{stats['negative']}")
    print()

    # Analyze failures
    print("=== FAILURE TAXONOMY ===\n")
    failure_results = analyze_failures(sessions)

    fstats = failure_results['stats']
    print(f"Total failures: {fstats['total_failures']}")
    print(f"Ambiguous rate: {fstats['ambiguous_rate']:.1f}%")
    print()

    print("By category:")
    for cat, count in sorted(fstats['by_category'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / fstats['total_failures'] * 100) if fstats['total_failures'] > 0 else 0
        print(f"  {cat}: {count} ({pct:.1f}%)")
    print()

    # Save results
    output = {
        'extraction_date': data.get('extraction_date'),
        'marathons': marathon_results,
        'failures': failure_results
    }

    output_file = Path('data/classification-results.json')
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"✅ Results saved: {output_file}")


if __name__ == "__main__":
    main()