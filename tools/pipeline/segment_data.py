#!/usr/bin/env python3
"""Segment delegation data into 3 temporal periods."""
import json
from datetime import datetime
from collections import Counter

from tools.common.config import (
    P2_START, P2_END, P3_START, P3_END, P4_START, P4_END,
    PERIOD_DEFINITIONS, SESSIONS_DATA_FILE, TEMPORAL_SEGMENTATION_FILE,
    MARATHON_THRESHOLD, get_runtime_config
)

def parse_date(date_str):
    """Parse ISO date string."""
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

def classify_period(date_str, periods_dict=None):
    """Classify a date into one of the defined periods.

    Args:
        date_str: ISO format date string
        periods_dict: Optional period definitions (defaults to runtime config)

    Returns:
        Period ID (e.g., "P1", "P2") or None if outside all periods
    """
    if periods_dict is None:
        # Use runtime config if available, otherwise hardcoded
        runtime_config = get_runtime_config()
        periods_dict = runtime_config.get_periods()

    dt = parse_date(date_str).date()

    for period_id, period_meta in periods_dict.items():
        start = datetime.fromisoformat(period_meta['start']).date()
        end = datetime.fromisoformat(period_meta['end']).date()

        if start <= dt <= end:
            return period_id

    return None

# Load data
with open(SESSIONS_DATA_FILE, 'r') as f:
    data = json.load(f)

# Get periods from runtime config (or use defaults)
runtime_config = get_runtime_config()
periods_dict = runtime_config.get_periods()

# Initialize period data dynamically
periods = {
    period_id: {"sessions": [], "delegations": [], "messages": 0}
    for period_id in periods_dict.keys()
}

# Classify sessions by first delegation timestamp
for session in data['sessions']:
    # Use first delegation timestamp to determine session period
    if session['delegations']:
        first_delegation_time = session['delegations'][0]['timestamp']
        period = classify_period(first_delegation_time, periods_dict)
        if period:
            periods[period]['sessions'].append(session)
            periods[period]['messages'] += session['message_count']
            # Add all delegations from this session to the period
            for delegation in session['delegations']:
                periods[period]['delegations'].append(delegation)

# Generate report
report = {
    "segmentation_date": datetime.now().isoformat(),
    "period_definitions": periods_dict,
    "summary": {}
}

# Analyze each period (dynamically based on runtime config)
for period_id in periods.keys():
    period_data = periods[period_id]
    sessions = period_data['sessions']
    delegations = period_data['delegations']

    # Basic metrics
    total_delegations = len(delegations)
    total_sessions = len(sessions)

    # Success rates
    successful = sum(1 for d in delegations if d.get('success', False))
    failed = sum(1 for d in delegations if not d.get('success', False) and 'error' not in str(d.get('result_preview', '')))
    unknown = total_delegations - successful - failed

    # Agent usage
    agent_counts = Counter(d['agent_type'] for d in delegations)

    # Heavy sessions (marathon threshold from config)
    heavy_sessions = [
        {
            "session_id": s['session_id'],
            "delegation_count": s['delegation_count'],
            "message_count": s['message_count'],
            "date": s['delegations'][0]['timestamp'][:10] if s['delegations'] else None
        }
        for s in sessions
    ]
    heavy_sessions = [s for s in heavy_sessions if s['delegation_count'] > MARATHON_THRESHOLD]
    heavy_sessions.sort(key=lambda x: x['delegation_count'], reverse=True)

    # Delegation metrics per session
    delegations_per_session = [s['delegation_count'] for s in sessions]
    avg_delegations = sum(delegations_per_session) / len(sessions) if sessions else 0

    report['summary'][period_id] = {
        "sessions": {
            "total": total_sessions,
            "heavy_sessions": len(heavy_sessions),
            "heavy_session_details": heavy_sessions[:5]  # Top 5
        },
        "delegations": {
            "total": total_delegations,
            "successful": successful,
            "failed": failed,
            "unknown": unknown,
            "success_rate": round(successful / total_delegations, 3) if total_delegations else 0,
            "avg_per_session": round(avg_delegations, 1)
        },
        "messages": {
            "total": period_data['messages'],
            "avg_per_session": round(period_data['messages'] / total_sessions, 1) if total_sessions else 0
        },
        "agents": {
            "unique_agents": len(agent_counts),
            "top_5": agent_counts.most_common(5)
        }
    }

# Comparative analysis (only if P3 and P4 exist)
if "P3" in periods and "P4" in periods:
    report['comparative'] = {
        "marathon_evolution": {
            "P3": len([s for s in periods["P3"]["sessions"] if s['delegation_count'] > MARATHON_THRESHOLD]),
            "P4": len([s for s in periods["P4"]["sessions"] if s['delegation_count'] > MARATHON_THRESHOLD])
        },
        "avg_delegations_evolution": {
            "P3": round(sum([s['delegation_count'] for s in periods["P3"]["sessions"]]) / len(periods["P3"]["sessions"]), 1) if periods["P3"]["sessions"] else 0,
            "P4": round(sum([s['delegation_count'] for s in periods["P4"]["sessions"]]) / len(periods["P4"]["sessions"]), 1) if periods["P4"]["sessions"] else 0
        }
    }

    # Calculate improvement percentages
    if report['comparative']['avg_delegations_evolution']['P3'] > 0:
        p3_avg = report['comparative']['avg_delegations_evolution']['P3']
        p4_avg = report['comparative']['avg_delegations_evolution']['P4']
        improvement = ((p3_avg - p4_avg) / p3_avg) * 100
        report['comparative']['delegation_reduction_percent'] = round(improvement, 1)

    if report['comparative']['marathon_evolution']['P3'] > 0:
        p3_marathons = report['comparative']['marathon_evolution']['P3']
        p4_marathons = report['comparative']['marathon_evolution']['P4']
        improvement = ((p3_marathons - p4_marathons) / p3_marathons) * 100
        report['comparative']['marathon_reduction_percent'] = round(improvement, 1)
else:
    report['comparative'] = {
        "note": "Comparative analysis requires P3 and P4 periods. Current analysis uses custom period(s)."
    }

# Save report
with open(TEMPORAL_SEGMENTATION_FILE, 'w') as f:
    json.dump(report, f, indent=2)

print("✅ Temporal segmentation complete")

# Dynamic period summary
for period_id in sorted(periods_dict.keys()):
    if period_id in report['summary']:
        period_name = periods_dict[period_id]['name']
        sessions = report['summary'][period_id]['sessions']['total']
        delegations = report['summary'][period_id]['delegations']['total']
        print(f"\n{period_id} ({period_name}): {sessions} sessions, {delegations} delegations")

# Show improvements if P3→P4 comparison exists
if "P3" in periods and "P4" in periods and 'marathon_evolution' in report['comparative']:
    print(f"\nImprovement P3→P4:")
    print(f"  Marathons: {report['comparative']['marathon_evolution']['P3']} → {report['comparative']['marathon_evolution']['P4']} ({report['comparative'].get('marathon_reduction_percent', 0)}%)")
    print(f"  Avg delegations/session: {report['comparative']['avg_delegations_evolution']['P3']} → {report['comparative']['avg_delegations_evolution']['P4']} ({report['comparative'].get('delegation_reduction_percent', 0)}%)")