#!/usr/bin/env python3
"""Segment delegation data into 3 temporal periods."""
import json
from datetime import datetime
from collections import Counter

from common.config import (
    P2_START, P2_END, P3_START, P3_END, P4_START, P4_END,
    PERIOD_DEFINITIONS, SESSIONS_DATA_FILE, TEMPORAL_SEGMENTATION_FILE,
    MARATHON_THRESHOLD
)

def parse_date(date_str):
    """Parse ISO date string."""
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

def classify_period(date_str):
    """Classify a date into P2, P3, or P4."""
    dt = parse_date(date_str).date()

    p2_start = datetime.fromisoformat(P2_START).date()
    p2_end = datetime.fromisoformat(P2_END).date()
    p3_start = datetime.fromisoformat(P3_START).date()
    p3_end = datetime.fromisoformat(P3_END).date()
    p4_start = datetime.fromisoformat(P4_START).date()
    p4_end = datetime.fromisoformat(P4_END).date()

    if p2_start <= dt <= p2_end:
        return "P2"
    elif p3_start <= dt <= p3_end:
        return "P3"
    elif p4_start <= dt <= p4_end:
        return "P4"
    return None

# Load data
with open(SESSIONS_DATA_FILE, 'r') as f:
    data = json.load(f)

# Initialize period data
periods = {
    "P2": {"sessions": [], "delegations": [], "messages": 0},
    "P3": {"sessions": [], "delegations": [], "messages": 0},
    "P4": {"sessions": [], "delegations": [], "messages": 0}
}

# Classify sessions by first delegation timestamp
for session in data['sessions']:
    # Use first delegation timestamp to determine session period
    if session['delegations']:
        first_delegation_time = session['delegations'][0]['timestamp']
        period = classify_period(first_delegation_time)
        if period:
            periods[period]['sessions'].append(session)
            periods[period]['messages'] += session['message_count']
            # Add all delegations from this session to the period
            for delegation in session['delegations']:
                periods[period]['delegations'].append(delegation)

# Generate report
report = {
    "segmentation_date": datetime.now().isoformat(),
    "period_definitions": PERIOD_DEFINITIONS,
    "summary": {}
}

# Analyze each period
for period_id in ["P2", "P3", "P4"]:
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

# Comparative analysis
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

# Save report
with open(TEMPORAL_SEGMENTATION_FILE, 'w') as f:
    json.dump(report, f, indent=2)

print("✅ Temporal segmentation complete")
print(f"\nP2 (Conception Added): {report['summary']['P2']['sessions']['total']} sessions, {report['summary']['P2']['delegations']['total']} delegations")
print(f"P3 (Délégation Obligatoire): {report['summary']['P3']['sessions']['total']} sessions, {report['summary']['P3']['delegations']['total']} delegations")
print(f"P4 (Post-Restructuration): {report['summary']['P4']['sessions']['total']} sessions, {report['summary']['P4']['delegations']['total']} delegations")
print(f"\nImprovement P3→P4:")
print(f"  Marathons: {report['comparative']['marathon_evolution']['P3']} → {report['comparative']['marathon_evolution']['P4']} ({report['comparative'].get('marathon_reduction_percent', 0)}%)")
print(f"  Avg delegations/session: {report['comparative']['avg_delegations_evolution']['P3']} → {report['comparative']['avg_delegations_evolution']['P4']} ({report['comparative'].get('delegation_reduction_percent', 0)}%)")