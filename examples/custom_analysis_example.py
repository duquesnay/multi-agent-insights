#!/usr/bin/env python3
"""
Example Custom Analysis Strategy

Demonstrates how to create a new analysis without modifying existing code.
This example analyzes agent collaboration patterns.

To use:
    1. Copy this file to strategies/agent_collaboration_analysis.py
    2. Import in strategies/__init__.py
    3. Register in analysis_runner.py
    4. Run with: python analysis_runner.py --agent-collaboration

To run this example standalone:
    cd delegation-retrospective
    python3 examples/custom_analysis_example.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any, List
from collections import defaultdict, Counter

from common.analysis_strategy import AnalysisStrategy, AnalysisResult


class AgentCollaborationAnalysisStrategy(AnalysisStrategy):
    """
    Analyzes collaboration patterns between agents.

    Metrics:
    - Most common agent pairs
    - Handoff efficiency
    - Collaboration chains
    - Specialist coordination patterns
    """

    def get_name(self) -> str:
        return "Agent Collaboration Analysis"

    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Execute collaboration analysis.

        Args:
            data: Dictionary with 'sessions' key

        Returns:
            AnalysisResult with collaboration findings
        """
        sessions = data.get('sessions', [])

        if not sessions:
            self.add_error("No sessions provided")
            return AnalysisResult(
                name=self.get_name(),
                data={},
                summary="No sessions to analyze"
            )

        # Analyze agent pairs
        pair_stats = self._analyze_agent_pairs(sessions)

        # Analyze collaboration chains
        chains = self._analyze_collaboration_chains(sessions)

        # Analyze handoff patterns
        handoffs = self._analyze_handoffs(sessions)

        # Build summary
        summary = self._build_summary(pair_stats, chains, handoffs)

        return AnalysisResult(
            name=self.get_name(),
            data={
                'agent_pairs': pair_stats,
                'collaboration_chains': chains,
                'handoff_patterns': handoffs
            },
            summary=summary,
            metadata={
                'total_sessions': len(sessions),
                'unique_pairs': len(pair_stats)
            }
        )

    def _analyze_agent_pairs(self, sessions: List[Dict]) -> Dict:
        """Analyze which agents work together most often."""
        pair_counts = Counter()
        pair_successes = defaultdict(int)

        for session in sessions:
            delegations = session.get('delegations', [])

            # Extract agent sequence
            agents_in_session = [d.get('agent_type') for d in delegations if d.get('agent_type')]

            # Count consecutive pairs
            for i in range(len(agents_in_session) - 1):
                pair = f"{agents_in_session[i]} → {agents_in_session[i+1]}"
                pair_counts[pair] += 1

                # Track success if both delegations successful
                if i < len(delegations) - 1:
                    if delegations[i].get('success') and delegations[i+1].get('success'):
                        pair_successes[pair] += 1

        # Calculate success rates
        pair_stats = {}
        for pair, count in pair_counts.most_common(20):
            success_count = pair_successes[pair]
            success_rate = (success_count / count * 100) if count > 0 else 0

            pair_stats[pair] = {
                'count': count,
                'successes': success_count,
                'success_rate': success_rate
            }

        return pair_stats

    def _analyze_collaboration_chains(self, sessions: List[Dict]) -> Dict:
        """Find common sequences of 3+ agents."""
        chain_counts = Counter()

        for session in sessions:
            delegations = session.get('delegations', [])
            agents = [d.get('agent_type') for d in delegations if d.get('agent_type')]

            # Extract 3-agent chains
            for i in range(len(agents) - 2):
                chain = f"{agents[i]} → {agents[i+1]} → {agents[i+2]}"
                chain_counts[chain] += 1

        return {
            'top_chains': dict(chain_counts.most_common(10)),
            'unique_chains': len(chain_counts)
        }

    def _analyze_handoffs(self, sessions: List[Dict]) -> Dict:
        """Analyze handoff patterns and efficiency."""
        handoff_types = {
            'specialist_to_specialist': 0,  # e.g., architect → developer
            'generalist_to_specialist': 0,  # e.g., developer → performance-optimizer
            'specialist_to_generalist': 0,  # e.g., architect → developer
            'same_agent': 0  # Agent delegating to itself
        }

        specialist_agents = {
            'solution-architect', 'project-framer', 'content-developer',
            'refactoring-specialist', 'performance-optimizer', 'integration-specialist'
        }
        generalist_agents = {'developer', 'senior-developer', 'junior-developer'}

        for session in sessions:
            delegations = session.get('delegations', [])

            for i in range(len(delegations) - 1):
                from_agent = delegations[i].get('agent_type')
                to_agent = delegations[i+1].get('agent_type')

                if not from_agent or not to_agent:
                    continue

                if from_agent == to_agent:
                    handoff_types['same_agent'] += 1
                elif from_agent in specialist_agents and to_agent in specialist_agents:
                    handoff_types['specialist_to_specialist'] += 1
                elif from_agent in generalist_agents and to_agent in specialist_agents:
                    handoff_types['generalist_to_specialist'] += 1
                elif from_agent in specialist_agents and to_agent in generalist_agents:
                    handoff_types['specialist_to_generalist'] += 1

        total = sum(handoff_types.values())
        handoff_percentages = {
            k: (v / total * 100) if total > 0 else 0
            for k, v in handoff_types.items()
        }

        return {
            'counts': handoff_types,
            'percentages': handoff_percentages
        }

    def _build_summary(self, pair_stats: Dict, chains: Dict, handoffs: Dict) -> str:
        """Build human-readable summary."""
        lines = []
        lines.append(f"Analyzed collaboration patterns across agents")
        lines.append(f"Unique agent pairs: {len(pair_stats)}")
        lines.append(f"Unique 3-agent chains: {chains['unique_chains']}")

        # Top collaboration
        if pair_stats:
            top_pair = list(pair_stats.items())[0]
            lines.append(f"\nMost common collaboration: {top_pair[0]}")
            lines.append(f"  - Occurrences: {top_pair[1]['count']}")
            lines.append(f"  - Success rate: {top_pair[1]['success_rate']:.1f}%")

        # Handoff patterns
        lines.append("\nHandoff patterns:")
        for handoff_type, percentage in handoffs['percentages'].items():
            lines.append(f"  - {handoff_type}: {percentage:.1f}%")

        return "\n".join(lines)


# Demonstration: Run as standalone script
if __name__ == "__main__":
    print("="*80)
    print("CUSTOM ANALYSIS EXAMPLE")
    print("="*80)
    print("\nThis demonstrates how to create a new analysis strategy.")
    print("The strategy follows the same pattern as built-in analyses.\n")

    strategy = AgentCollaborationAnalysisStrategy()
    result = strategy.run()

    # Print results
    print("\nTop Agent Pairs:")
    for pair, stats in list(result.data['agent_pairs'].items())[:5]:
        print(f"  {pair:50} : {stats['count']:3d} occurrences, {stats['success_rate']:5.1f}% success")

    print("\nTop Collaboration Chains:")
    for chain, count in list(result.data['collaboration_chains']['top_chains'].items())[:5]:
        print(f"  {chain:70} : {count:3d} times")

    print("\nHandoff Patterns:")
    for handoff_type, percentage in result.data['handoff_patterns']['percentages'].items():
        count = result.data['handoff_patterns']['counts'][handoff_type]
        print(f"  {handoff_type:30} : {percentage:5.1f}% ({count} times)")

    print("\n")
    result.print_summary()

    print("\n" + "="*80)
    print("TO INTEGRATE THIS ANALYSIS:")
    print("="*80)
    print("1. Copy to: strategies/agent_collaboration_analysis.py")
    print("2. Add to strategies/__init__.py:")
    print("     from .agent_collaboration_analysis import AgentCollaborationAnalysisStrategy")
    print("3. Register in analysis_runner.py:")
    print("     self.register('collaboration', AgentCollaborationAnalysisStrategy())")
    print("4. Run with:")
    print("     python analysis_runner.py --collaboration")
    print("\nNo modifications to existing code required!")
