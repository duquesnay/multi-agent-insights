#!/usr/bin/env python3
"""
Calculate objective metrics: Task completion, success rates, tokens.
Complements LLM agent analyses with quantitative data.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for common imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from common.metrics_service import extract_delegation_metrics

def main():
    data_path = Path(__file__).parent / "enriched_sessions_v8_complete_classified.json"

    print("Loading dataset...")
    with open(data_path) as f:
        data = json.load(f)

    sessions = data['sessions']
    print(f"Analyzing {len(sessions)} sessions, {data['total_delegations_extracted']} delegations")

    # Metrics by period
    metrics_by_period = {}

    for period in ['P0', 'P2', 'P3', 'P4']:
        period_sessions = [s for s in sessions if s.get('period') == period]

        if not period_sessions:
            continue

        # Calculate metrics
        total_delegations = sum(s.get('delegation_count', 0) for s in period_sessions)

        # Success counts
        all_delegations = []
        for s in period_sessions:
            all_delegations.extend(s.get('delegations', []))

        success_count = sum(1 for d in all_delegations if d.get('success', False))
        failure_count = len(all_delegations) - success_count

        # Failure types
        failure_types = defaultdict(int)
        for d in all_delegations:
            if not d.get('success', False):
                ft = d.get('failure_type', 'UNKNOWN')
                failure_types[ft] += 1

        # Tokens (only P2-P4) - use centralized extraction
        delegation_metrics = [extract_delegation_metrics(d) for d in all_delegations]
        tokens_data = {
            'input': sum(m['input_tokens'] for m in delegation_metrics),
            'output': sum(m['output_tokens'] for m in delegation_metrics),
            'cache': sum(m['cache_read_tokens'] for m in delegation_metrics)
        }

        # Agent usage
        agent_usage = defaultdict(int)
        for d in all_delegations:
            agent = d.get('agent_type')
            if agent:
                agent_usage[agent] += 1

        # Marathon count
        marathons = [s for s in period_sessions if s.get('marathon')]
        marathon_positive = sum(1 for s in period_sessions
                                if s.get('marathon') and s['marathon']['classification'] == 'POSITIVE')
        marathon_negative = sum(1 for s in period_sessions
                                if s.get('marathon') and s['marathon']['classification'] == 'NEGATIVE')

        metrics_by_period[period] = {
            'sessions': len(period_sessions),
            'delegations': total_delegations,
            'avg_delegations_per_session': total_delegations / len(period_sessions) if period_sessions else 0,
            'success_rate': (success_count / len(all_delegations) * 100) if all_delegations else 0,
            'success_count': success_count,
            'failure_count': failure_count,
            'failure_types': dict(failure_types),
            'tokens': tokens_data,
            'tokens_per_delegation': {
                'input': tokens_data['input'] / len(all_delegations) if all_delegations else 0,
                'output': tokens_data['output'] / len(all_delegations) if all_delegations else 0
            },
            'agent_usage': dict(sorted(agent_usage.items(), key=lambda x: -x[1])[:10]),
            'marathons': {
                'total': len(marathons),
                'positive': marathon_positive,
                'negative': marathon_negative
            }
        }

    # Save metrics
    output_path = Path(__file__).parent / "metrics_quantitative.json"
    with open(output_path, 'w') as f:
        json.dump(metrics_by_period, f, indent=2)

    # Print summary
    print("\n=== METRICS BY PERIOD ===\n")

    for period in sorted(metrics_by_period.keys()):
        m = metrics_by_period[period]
        print(f"**{period}**:")
        print(f"  Sessions: {m['sessions']}")
        print(f"  Delegations: {m['delegations']} (avg: {m['avg_delegations_per_session']:.1f}/session)")
        print(f"  Success rate: {m['success_rate']:.1f}%")
        print(f"  Failures: {m['failure_count']}")

        if m['tokens']['input'] > 0:
            print(f"  Tokens: {m['tokens']['input']:,} in, {m['tokens']['output']:,} out")
            print(f"  Tokens/delegation: {m['tokens_per_delegation']['input']:.0f} in, {m['tokens_per_delegation']['output']:.0f} out")

        if m['marathons']['total'] > 0:
            print(f"  Marathons: {m['marathons']['total']} ({m['marathons']['positive']} positive, {m['marathons']['negative']} negative)")

        print(f"  Top agents: {', '.join(list(m['agent_usage'].keys())[:3])}")
        print()

    # Cross-period evolution
    print("=== EVOLUTION ===\n")

    if 'P0' in metrics_by_period and 'P4' in metrics_by_period:
        p0 = metrics_by_period['P0']
        p4 = metrics_by_period['P4']

        print(f"P0 → P4:")
        print(f"  Success rate: {p0['success_rate']:.1f}% → {p4['success_rate']:.1f}% ({p4['success_rate']-p0['success_rate']:+.1f}pp)")
        print(f"  Delegations/session: {p0['avg_delegations_per_session']:.1f} → {p4['avg_delegations_per_session']:.1f} ({(p4['avg_delegations_per_session']/p0['avg_delegations_per_session']-1)*100:+.0f}%)")

    if 'P3' in metrics_by_period and 'P4' in metrics_by_period:
        p3 = metrics_by_period['P3']
        p4 = metrics_by_period['P4']

        print(f"\nP3 → P4:")
        print(f"  Success rate: {p3['success_rate']:.1f}% → {p4['success_rate']:.1f}% ({p4['success_rate']-p3['success_rate']:+.1f}pp)")
        print(f"  Delegations/session: {p3['avg_delegations_per_session']:.1f} → {p4['avg_delegations_per_session']:.1f} ({(p4['avg_delegations_per_session']/p3['avg_delegations_per_session']-1)*100:+.0f}%)")
        print(f"  Marathons/session: {p3['marathons']['total']/p3['sessions']:.2f} → {p4['marathons']['total']/p4['sessions']:.2f}")

    print(f"\nOutput: {output_path}")

if __name__ == "__main__":
    main()