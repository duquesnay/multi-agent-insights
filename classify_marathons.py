#!/usr/bin/env python3
"""
Classify marathons as positive (productive) vs negative (pathological).
"""
import json
from pathlib import Path

def classify_marathon(session):
    """
    Classify marathon as:
    - POSITIVE: >20 deleg, >85% success, productive work
    - NEGATIVE: >20 deleg, <80% success, cascading failures
    - AMBIGUOUS: 80-85% success, need manual review
    """
    deleg_count = session['delegation_count']
    delegations = session.get('delegations', [])

    if deleg_count <= 20:
        return None  # Not a marathon

    # Calculate success rate
    successes = sum(1 for d in delegations if d.get('success') is True)
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

    # Additional context
    return {
        'classification': classification,
        'success_rate': round(success_rate, 1),
        'backlog_related': backlog_related,
        'cascade_rate': round(cascade_rate, 1),
        'delegations': deleg_count,
        'session_id': session['session_id'][:8],
        'date': session.get('first_timestamp', '')[:10]
    }

def main():
    # Load enriched sessions
    with open('data/enriched_sessions_data.json') as f:
        data = json.load(f)

    marathons = []
    for session in data['sessions']:
        marathon_data = classify_marathon(session)
        if marathon_data:
            marathons.append(marathon_data)

    # Sort by delegation count
    marathons.sort(key=lambda x: x['delegations'], reverse=True)

    # Count by classification
    positive = [m for m in marathons if m['classification'] == 'POSITIVE']
    negative = [m for m in marathons if m['classification'] == 'NEGATIVE']
    ambiguous = [m for m in marathons if m['classification'] == 'AMBIGUOUS']

    print("=== MARATHON CLASSIFICATION ===\n")
    print(f"Total marathons (>20 deleg): {len(marathons)}")
    print(f"  POSITIVE (>85% success): {len(positive)}")
    print(f"  NEGATIVE (<80% success): {len(negative)}")
    print(f"  AMBIGUOUS (80-85%): {len(ambiguous)}")
    print()

    print("=== POSITIVE MARATHONS (Productive) ===")
    for m in positive:
        backlog_marker = "[BACKLOG]" if m['backlog_related'] else ""
        print(f"{m['date']} | {m['delegations']:2d} deleg | {m['success_rate']:5.1f}% | cascade: {m['cascade_rate']:4.1f}% | {backlog_marker}")
    print()

    print("=== NEGATIVE MARATHONS (Pathological) ===")
    for m in negative:
        backlog_marker = "[BACKLOG]" if m['backlog_related'] else ""
        print(f"{m['date']} | {m['delegations']:2d} deleg | {m['success_rate']:5.1f}% | cascade: {m['cascade_rate']:4.1f}% | {backlog_marker}")
    print()

    if ambiguous:
        print("=== AMBIGUOUS MARATHONS (Require Review) ===")
        for m in ambiguous:
            backlog_marker = "[BACKLOG]" if m['backlog_related'] else ""
            print(f"{m['date']} | {m['delegations']:2d} deleg | {m['success_rate']:5.1f}% | cascade: {m['cascade_rate']:4.1f}% | {backlog_marker}")
        print()

    # Analysis by type
    print("=== PATTERNS ANALYSIS ===\n")

    avg_cascade_positive = sum(m['cascade_rate'] for m in positive) / len(positive) if positive else 0
    avg_cascade_negative = sum(m['cascade_rate'] for m in negative) / len(negative) if negative else 0

    print(f"Average cascade rate:")
    print(f"  Positive marathons: {avg_cascade_positive:.1f}%")
    print(f"  Negative marathons: {avg_cascade_negative:.1f}%")
    print()

    backlog_positive = sum(1 for m in positive if m['backlog_related'])
    backlog_negative = sum(1 for m in negative if m['backlog_related'])

    print(f"Backlog-related:")
    print(f"  Positive: {backlog_positive}/{len(positive)} ({backlog_positive/len(positive)*100:.0f}%)" if positive else "  Positive: 0/0")
    print(f"  Negative: {backlog_negative}/{len(negative)} ({backlog_negative/len(negative)*100:.0f}%)" if negative else "  Negative: 0/0")
    print()

    # Save detailed report
    report = {
        'summary': {
            'total_marathons': len(marathons),
            'positive': len(positive),
            'negative': len(negative),
            'ambiguous': len(ambiguous)
        },
        'positive_marathons': positive,
        'negative_marathons': negative,
        'ambiguous_marathons': ambiguous
    }

    output = Path('data/marathon-classification.json')
    with open(output, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✅ Detailed report saved: {output}")

if __name__ == "__main__":
    main()