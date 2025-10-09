#!/usr/bin/env python3
"""
Extract routing patterns from enriched sessions data.
Segments by period and analyzes agent→sub-agent transitions.
"""

import json
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

from tools.common.config import get_runtime_config, ENRICHED_SESSIONS_FILE, ROUTING_PATTERNS_FILE

def parse_timestamp(ts_str: str) -> datetime:
    """Parse ISO timestamp."""
    return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))

def get_period(timestamp: str, periods_dict: Dict[str, Dict]) -> str:
    """Determine which period a timestamp belongs to.

    Args:
        timestamp: ISO timestamp string
        periods_dict: Period definitions from RuntimeConfig

    Returns:
        Period ID or None if outside all periods
    """
    dt = parse_timestamp(timestamp)
    date_only = dt.date()

    for period_id, period_meta in periods_dict.items():
        start_date = datetime.fromisoformat(period_meta['start']).date()
        end_date = datetime.fromisoformat(period_meta['end']).date()
        if start_date <= date_only <= end_date:
            return period_id
    return None

def extract_routing_patterns(data_path: str):
    """Extract routing patterns by period."""

    with open(data_path, 'r') as f:
        data = json.load(f)

    # Get periods from runtime config
    runtime_config = get_runtime_config()
    periods_dict = runtime_config.get_periods()

    # Structure to hold routing info by period
    routing_by_period = {
        period_id: {
            'delegations': [],  # All delegations with full context
            'transitions': [],  # Agent→agent transitions
            'agent_calls': Counter(),  # How often each agent is called
            'agent_tasks': defaultdict(list),  # Tasks handled by each agent
        }
        for period_id in periods_dict.keys()
    }

    # Process each session
    for session in data['sessions']:
        session_period = get_period(session['first_timestamp'], periods_dict)
        if not session_period:
            continue
        
        period_data = routing_by_period[session_period]
        
        # Process delegations in sequence
        for i, delegation in enumerate(session['delegations']):
            agent = delegation['agent_type']
            
            # Store full delegation context
            delegation_info = {
                'agent': agent,
                'prompt': delegation['prompt'],
                'description': delegation.get('description', ''),
                'success': delegation.get('success', True),
                'next_agent': delegation.get('next_agent'),
                'sequence': delegation['sequence_number'],
                'session_id': session['session_id'],
                'timestamp': delegation['timestamp']
            }
            period_data['delegations'].append(delegation_info)
            
            # Count agent calls
            period_data['agent_calls'][agent] += 1
            
            # Store task type with agent
            task_summary = {
                'prompt_preview': delegation['prompt'][:200] + '...' if len(delegation['prompt']) > 200 else delegation['prompt'],
                'description': delegation.get('description', ''),
                'session': session['session_id']
            }
            period_data['agent_tasks'][agent].append(task_summary)
            
            # Track transitions (current → next)
            if delegation.get('next_agent'):
                transition = (agent, delegation['next_agent'])
                period_data['transitions'].append(transition)
    
    return routing_by_period

def analyze_agent_usage(routing_data: Dict) -> Dict:
    """Analyze which agents are used for what tasks."""
    
    analysis = {}
    
    for period, data in routing_data.items():
        period_analysis = {
            'total_delegations': len(data['delegations']),
            'agent_distribution': dict(data['agent_calls']),
            'top_agents': data['agent_calls'].most_common(5),
            'transition_patterns': Counter(data['transitions']).most_common(10),
        }
        
        # Sample tasks per agent
        period_analysis['agent_task_samples'] = {}
        for agent, tasks in data['agent_tasks'].items():
            # Get up to 5 representative samples
            samples = tasks[:5] if len(tasks) <= 5 else [
                tasks[0],  # First
                tasks[len(tasks)//4],  # Quarter
                tasks[len(tasks)//2],  # Middle
                tasks[3*len(tasks)//4],  # Three-quarter
                tasks[-1]  # Last
            ]
            period_analysis['agent_task_samples'][agent] = {
                'count': len(tasks),
                'samples': samples
            }
        
        analysis[period] = period_analysis
    
    return analysis

def main():
    print("Extracting routing patterns...")
    routing_data = extract_routing_patterns(str(ENRICHED_SESSIONS_FILE))

    print("Analyzing agent usage...")
    analysis = analyze_agent_usage(routing_data)

    # Get periods from runtime config
    runtime_config = get_runtime_config()
    periods_dict = runtime_config.get_periods()

    # Output detailed routing data
    output = {
        'extraction_date': datetime.now().isoformat(),
        'periods': {
            period_id: {
                'name': period_meta['name'],
                'date_range': f"{period_meta['start']} to {period_meta['end']}",
                'analysis': analysis[period_id],
                'full_delegations': routing_data[period_id]['delegations']
            }
            for period_id, period_meta in periods_dict.items()
        }
    }

    with open(ROUTING_PATTERNS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nRouting patterns extracted to: {ROUTING_PATTERNS_FILE}")

    # Print summary
    print("\n=== ROUTING SUMMARY BY PERIOD ===\n")
    for period_id in sorted(periods_dict.keys()):
        period_meta = periods_dict[period_id]
        period_analysis = analysis.get(period_id, {})

        if period_analysis:
            print(f"{period_id} - {period_meta['name']}")
            print(f"  Total delegations: {period_analysis.get('total_delegations', 0)}")
            print(f"  Top 5 agents:")
            for agent, count in period_analysis.get('top_agents', []):
                pct = (count / period_analysis['total_delegations']) * 100 if period_analysis.get('total_delegations') else 0
                print(f"    {agent}: {count} ({pct:.1f}%)")
            print(f"  Top transitions:")
            for (from_agent, to_agent), count in period_analysis.get('transition_patterns', [])[:3]:
                print(f"    {from_agent} → {to_agent}: {count}")
            print()

if __name__ == '__main__':
    main()
