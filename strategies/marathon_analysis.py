"""
Marathon Analysis Strategy - Identify and analyze marathon sessions

Analyzes:
- Sessions with >20 delegations
- Agent sequencing and loop patterns
- Pivot points where control is lost
- Coordination transitions

Converted from: analyze_marathons_optimized.py
"""

from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict, Counter, deque
from datetime import datetime

from common.analysis_strategy import AnalysisStrategy, AnalysisResult


class MarathonAnalysisStrategy(AnalysisStrategy):
    """
    Analyzes marathon sessions (>20 delegations) to identify patterns and issues.
    """

    def __init__(self, marathon_threshold: int = 20):
        """
        Initialize marathon analysis.

        Args:
            marathon_threshold: Minimum delegations to classify as marathon (default: 20)
        """
        super().__init__()
        self.marathon_threshold = marathon_threshold

    def get_name(self) -> str:
        return "Marathon Analysis"

    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Execute marathon analysis on sessions.

        Args:
            data: Dictionary with 'sessions' key

        Returns:
            AnalysisResult with marathon findings
        """
        sessions = data.get('sessions', [])

        if not sessions:
            self.add_error("No sessions provided")
            return AnalysisResult(
                name=self.get_name(),
                data={},
                summary="No sessions to analyze"
            )

        # Extract marathons
        marathons = self._extract_marathons(sessions)

        if not marathons:
            return AnalysisResult(
                name=self.get_name(),
                data={'marathons': []},
                summary=f"No marathon sessions found (threshold: {self.marathon_threshold} delegations)"
            )

        # Analyze top marathons
        top_marathons = marathons[:5]
        marathon_details = []

        for marathon in top_marathons:
            details = self._analyze_single_marathon(marathon)
            marathon_details.append(details)

        # Analyze overall transitions
        transitions = self._analyze_transitions(marathons)

        # Group by period
        by_period = self._group_by_period(marathons)

        # Build summary
        summary = self._build_summary(marathons, by_period)

        return AnalysisResult(
            name=self.get_name(),
            data={
                'marathons': [m for m in marathons],  # All marathons
                'top_5_detailed': marathon_details,
                'transitions': transitions[:20],  # Top 20 transitions
                'by_period': by_period
            },
            summary=summary,
            metadata={
                'total_marathons': len(marathons),
                'marathon_threshold': self.marathon_threshold,
                'periods': list(by_period.keys())
            }
        )

    def _extract_marathons(self, sessions: List[Dict]) -> List[Dict]:
        """Extract marathon sessions (>threshold delegations)."""
        marathons = []

        for session in sessions:
            session_id = session.get('session_id')
            delegations = session.get('delegations', [])

            if len(delegations) > self.marathon_threshold:
                first_deleg = delegations[0] if delegations else {}
                period = self._classify_period(first_deleg.get('timestamp', ''))

                marathons.append({
                    'session_id': session_id,
                    'count': len(delegations),
                    'period': period,
                    'date': first_deleg.get('timestamp', ''),
                    'delegations': delegations
                })

        return sorted(marathons, key=lambda x: x['count'], reverse=True)

    def _classify_period(self, date_str: str) -> str:
        """Classify session into temporal period."""
        if not date_str:
            return 'Unknown'

        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            day = date.day

            if 3 <= day <= 11:
                return 'P2'
            elif 12 <= day <= 20:
                return 'P3'
            else:
                return 'P4'
        except (ValueError, AttributeError):
            return 'Unknown'

    def _analyze_single_marathon(self, marathon: Dict) -> Dict:
        """Deep dive analysis of a single marathon."""
        delegations = marathon['delegations']

        sequence, loops, agent_counts = self._analyze_sequence(delegations)
        pivot_idx, pivot_type = self._find_pivot_point(sequence)

        # Extract initial task
        initial_prompt = delegations[0].get('prompt', 'N/A') if delegations else 'N/A'
        if initial_prompt != 'N/A' and len(initial_prompt) > 500:
            initial_prompt = initial_prompt[:500] + '...'

        # Final status
        final_delegation = delegations[-1] if delegations else {}
        final_success = final_delegation.get('success', None)
        final_error = final_delegation.get('is_error', False)
        status = 'ERROR' if final_error else ('SUCCESS' if final_success else 'UNKNOWN')

        return {
            'session_id': marathon['session_id'],
            'period': marathon['period'],
            'date': marathon['date'][:10] if marathon['date'] else 'Unknown',
            'delegation_count': marathon['count'],
            'initial_task': initial_prompt,
            'agent_distribution': dict(agent_counts.most_common()),
            'loops_detected': len(loops),
            'unique_loop_patterns': list(set(l['pattern'] for l in loops))[:5],
            'pivot_point': {
                'index': pivot_idx,
                'type': pivot_type,
                'agent': sequence[pivot_idx]['agent'] if pivot_idx is not None else None
            } if pivot_idx is not None else None,
            'final_status': status,
            'first_10_steps': [self._format_step(s) for s in sequence[:10]],
            'last_5_steps': [self._format_step(s) for s in sequence[-5:]]
        }

    def _analyze_sequence(self, delegations: List[Dict]) -> Tuple[List[Dict], List[Dict], Counter]:
        """
        Analyze agent sequence for a marathon session.

        Returns:
            (sequence, loops, agent_counts)
        """
        sequence = []
        loops = []
        agent_counts = Counter()

        # Sliding window for A->B->A loop detection
        window = deque(maxlen=3)
        prev_agent = None

        for i, deleg in enumerate(delegations):
            agent = deleg.get('agent_type', 'unknown')
            next_agent = deleg.get('next_agent', None)

            # Build sequence step
            prompt = deleg.get('prompt') or ''
            step = {
                'seq': i + 1,
                'agent': agent,
                'prev': prev_agent,
                'next': next_agent,
                'success': deleg.get('success', None),
                'is_error': deleg.get('is_error', False),
                'prompt_preview': prompt[:100] if prompt else ''
            }
            sequence.append(step)
            agent_counts[agent] += 1

            # Update sliding window
            window.append((i, agent))

            # Detect A->B->A pattern
            if len(window) == 3:
                if window[0][1] == window[2][1]:
                    loop_pattern = f"{window[0][1]} → {window[1][1]} → {window[2][1]}"
                    loops.append({
                        'pattern': loop_pattern,
                        'positions': [window[0][0] + 1, window[1][0] + 1, window[2][0] + 1]
                    })

            prev_agent = agent

        return sequence, loops, agent_counts

    def _find_pivot_point(self, sequence: List[Dict]) -> Tuple[Optional[int], Optional[str]]:
        """Identify where session becomes uncontrolled."""
        failures = []
        switches = []

        prev_agent = None
        for i, step in enumerate(sequence):
            if step['is_error'] or step['success'] is False:
                failures.append(i)

            if prev_agent is not None and step['agent'] != prev_agent:
                switches.append(i)

            prev_agent = step['agent']

        # Pivot is likely where failures cluster or rapid switching begins
        if len(failures) >= 3:
            return failures[2], 'failure_cluster'
        elif len(switches) >= 10:
            return switches[9], 'rapid_switching'
        else:
            return None, None

    def _analyze_transitions(self, marathons: List[Dict]) -> List[Tuple[str, int]]:
        """Analyze agent-to-agent transitions across marathons."""
        transitions = defaultdict(int)

        for marathon in marathons:
            delegations = marathon['delegations']
            for i in range(1, len(delegations)):
                prev = delegations[i-1].get('agent_type')
                curr = delegations[i].get('agent_type')
                if prev and curr:
                    transitions[f"{prev} → {curr}"] += 1

        return sorted(transitions.items(), key=lambda x: x[1], reverse=True)

    def _group_by_period(self, marathons: List[Dict]) -> Dict[str, List]:
        """Group marathons by temporal period."""
        by_period = defaultdict(list)
        for marathon in marathons:
            by_period[marathon['period']].append(marathon)

        return {
            period: {
                'count': len(marathons_list),
                'marathon_ids': [m['session_id'] for m in marathons_list]
            }
            for period, marathons_list in by_period.items()
        }

    def _format_step(self, step: Dict) -> Dict:
        """Format step for output."""
        status = 'ERROR' if step['is_error'] else ('SUCCESS' if step['success'] else 'UNKNOWN')
        return {
            'sequence': step['seq'],
            'agent': step['agent'],
            'from_agent': step['prev'] or 'START',
            'status': status
        }

    def _build_summary(self, marathons: List[Dict], by_period: Dict) -> str:
        """Build human-readable summary."""
        lines = []
        lines.append(f"Identified {len(marathons)} marathon sessions (>{self.marathon_threshold} delegations)")

        for period in ['P2', 'P3', 'P4']:
            count = by_period.get(period, {}).get('count', 0)
            lines.append(f"  - {period}: {count} marathons")

        if marathons:
            lines.append(f"\nLongest marathon: {marathons[0]['count']} delegations")
            lines.append(f"Shortest marathon: {marathons[-1]['count']} delegations")

        return "\n".join(lines)


# Backward compatibility: allow running as standalone script
if __name__ == "__main__":
    strategy = MarathonAnalysisStrategy()
    result = strategy.run()

    # Print detailed output (matching original script format)
    marathons = result.data['marathons']

    print(f"\n{'='*80}")
    print(f"MARATHONS IDENTIFIED: {len(marathons)}")
    print(f"{'='*80}\n")

    by_period = result.data['by_period']
    for period in ['P2', 'P3', 'P4']:
        count = by_period.get(period, {}).get('count', 0)
        print(f"{period}: {count} marathons")

    print(f"\n{'='*80}")
    print("TOP 5 EXTREME MARATHONS - DEEP DIVE")
    print(f"{'='*80}\n")

    for rank, marathon_detail in enumerate(result.data['top_5_detailed'], 1):
        print(f"\n{'#'*80}")
        print(f"RANK {rank}: Session {marathon_detail['session_id']}")
        print(f"Period: {marathon_detail['period']} | Date: {marathon_detail['date']} | "
              f"Delegations: {marathon_detail['delegation_count']}")
        print(f"{'#'*80}\n")

        print(f"INITIAL TASK:\n{marathon_detail['initial_task']}\n")

        print(f"AGENT DISTRIBUTION:")
        for agent, count in marathon_detail['agent_distribution'].items():
            print(f"  {agent}: {count} times")

        print(f"\nLOOPS DETECTED: {marathon_detail['loops_detected']}")
        for pattern in marathon_detail['unique_loop_patterns']:
            print(f"  - {pattern}")

        if marathon_detail['pivot_point']:
            pivot = marathon_detail['pivot_point']
            print(f"\nPIVOT POINT: Delegation #{pivot['index']+1} ({pivot['type']})")
            print(f"  Agent: {pivot['agent']}")
        else:
            print(f"\nPIVOT POINT: Not clearly identifiable")

        print(f"\nFINAL STATUS: {marathon_detail['final_status']}")

        print(f"\nFIRST 10 SEQUENCE STEPS:")
        for step in marathon_detail['first_10_steps']:
            print(f"  {step['sequence']:3d}. {step['agent']:25s} (from {step['from_agent']:20s}) [{step['status']}]")

        print(f"\nLAST 5 SEQUENCE STEPS:")
        for step in marathon_detail['last_5_steps']:
            print(f"  {step['sequence']:3d}. {step['agent']:25s} (from {step['from_agent']:20s}) [{step['status']}]")

        print("\n")

    print(f"\n{'='*80}")
    print("COORDINATION PATTERNS - TOP TRANSITIONS")
    print(f"{'='*80}\n")
    print("Most frequent agent-to-agent transitions in marathons:")
    for transition, count in result.data['transitions']:
        print(f"  {transition:50s}: {count} times")

    print("\n")
    result.print_summary()
