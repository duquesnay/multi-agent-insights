"""
Metrics Analysis Strategy - Token metrics and agent usage statistics

Analyzes:
- Global token metrics (input, output, cache efficiency)
- Agent-specific usage patterns
- Temporal distribution
- Amplification ratios

Converted from: analyze_metrics.py
"""

from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime
import statistics

from common.analysis_strategy import AnalysisStrategy, AnalysisResult
from common.metrics_service import extract_delegation_metrics, calculate_token_totals


class MetricsAnalysisStrategy(AnalysisStrategy):
    """
    Analyzes delegation metrics including token usage and agent statistics.
    """

    def get_name(self) -> str:
        return "Metrics Analysis"

    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Execute metrics analysis on delegations.

        Args:
            data: Dictionary with 'delegations' key

        Returns:
            AnalysisResult with metrics findings
        """
        delegations = data.get('delegations', [])

        if not delegations:
            self.add_error("No delegations provided")
            return AnalysisResult(
                name=self.get_name(),
                data={},
                summary="No delegations to analyze"
            )

        # Analyze by agent
        agent_stats = self._analyze_by_agent(delegations)

        # Analyze temporal distribution
        temporal_stats = self._analyze_temporal_distribution(delegations)

        # Global metrics
        global_metrics = self._calculate_global_metrics(delegations)

        # Build summary
        summary = self._build_summary(global_metrics, agent_stats)

        return AnalysisResult(
            name=self.get_name(),
            data={
                'global_metrics': global_metrics,
                'agent_statistics': agent_stats,
                'temporal_distribution': temporal_stats
            },
            summary=summary,
            metadata={
                'total_delegations': len(delegations),
                'unique_agents': len(agent_stats)
            }
        )

    def _analyze_by_agent(self, delegations: List[Dict]) -> Dict:
        """Analyze metrics per agent."""
        agent_stats = defaultdict(lambda: {
            'count': 0,
            'total_input': 0,
            'total_output': 0,
            'total_cache_read': 0,
            'total_cache_write': 0,
            'amplification_ratios': [],
            'cache_hit_rates': [],
            'first_seen': None,
            'last_seen': None
        })

        for delegation in delegations:
            metrics = extract_delegation_metrics(delegation)
            agent = metrics['agent_type']

            if agent:
                stats = agent_stats[agent]
                stats['count'] += 1
                stats['total_input'] += metrics['input_tokens']
                stats['total_output'] += metrics['output_tokens']
                stats['total_cache_read'] += metrics['cache_read_tokens']
                stats['total_cache_write'] += metrics['cache_write_tokens']

                if metrics['amplification_ratio'] > 0:
                    stats['amplification_ratios'].append(metrics['amplification_ratio'])
                if metrics['cache_hit_rate'] > 0:
                    stats['cache_hit_rates'].append(metrics['cache_hit_rate'])

                # Track temporal usage
                if metrics['timestamp']:
                    if not stats['first_seen'] or metrics['timestamp'] < stats['first_seen']:
                        stats['first_seen'] = metrics['timestamp']
                    if not stats['last_seen'] or metrics['timestamp'] > stats['last_seen']:
                        stats['last_seen'] = metrics['timestamp']

        # Calculate averages
        for agent, stats in agent_stats.items():
            if stats['amplification_ratios']:
                stats['avg_amplification'] = statistics.mean(stats['amplification_ratios'])
                stats['median_amplification'] = statistics.median(stats['amplification_ratios'])
            else:
                stats['avg_amplification'] = 0
                stats['median_amplification'] = 0

            if stats['cache_hit_rates']:
                stats['avg_cache_hit_rate'] = statistics.mean(stats['cache_hit_rates'])
            else:
                stats['avg_cache_hit_rate'] = 0

            # Clean up lists for serialization
            del stats['amplification_ratios']
            del stats['cache_hit_rates']

        return dict(agent_stats)

    def _analyze_temporal_distribution(self, delegations: List[Dict]) -> Dict:
        """Analyze temporal distribution of delegations."""
        temporal_stats = {
            'by_date': defaultdict(lambda: defaultdict(int)),
            'by_hour': defaultdict(int),
            'by_weekday': defaultdict(int)
        }

        for delegation in delegations:
            metrics = extract_delegation_metrics(delegation)
            if metrics['timestamp'] and metrics['agent_type']:
                try:
                    dt = datetime.fromisoformat(metrics['timestamp'].replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y-%m-%d')
                    hour = dt.hour
                    weekday = dt.strftime('%A')

                    temporal_stats['by_date'][date_str][metrics['agent_type']] += 1
                    temporal_stats['by_hour'][hour] += 1
                    temporal_stats['by_weekday'][weekday] += 1
                except ValueError as e:
                    self.add_warning(f"Invalid timestamp: {metrics['timestamp']}")
                    continue

        # Convert defaultdicts to regular dicts for serialization
        return {
            'by_date': {date: dict(agents) for date, agents in temporal_stats['by_date'].items()},
            'by_hour': dict(temporal_stats['by_hour']),
            'by_weekday': dict(temporal_stats['by_weekday'])
        }

    def _calculate_global_metrics(self, delegations: List[Dict]) -> Dict:
        """Calculate global token metrics."""
        totals = calculate_token_totals(delegations)

        return {
            'total_delegations': totals['total_delegations'],
            'total_input_tokens': totals['total_input_tokens'],
            'total_output_tokens': totals['total_output_tokens'],
            'total_cache_read': totals['total_cache_read_tokens'],
            'total_cache_write': totals['total_cache_write_tokens'],
            'total_tokens': totals['total_tokens'],
            'global_amplification': totals['global_amplification_ratio'],
            'global_cache_efficiency': totals['global_cache_efficiency']
        }

    def _build_summary(self, global_metrics: Dict, agent_stats: Dict) -> str:
        """Build human-readable summary."""
        lines = []
        lines.append(f"Analyzed {global_metrics['total_delegations']:,} delegations")
        lines.append(f"Total tokens: {global_metrics['total_tokens']:,}")
        lines.append(f"Amplification ratio: {global_metrics['global_amplification']:.2f}x")
        lines.append(f"Cache efficiency: {global_metrics['global_cache_efficiency']:.1%}")
        lines.append(f"Unique agents: {len(agent_stats)}")

        # Top 3 most used agents
        sorted_agents = sorted(agent_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        lines.append("\nTop 3 agents by usage:")
        for agent, stats in sorted_agents[:3]:
            lines.append(f"  - {agent}: {stats['count']} delegations")

        return "\n".join(lines)


# Backward compatibility: allow running as standalone script
if __name__ == "__main__":
    strategy = MetricsAnalysisStrategy()
    result = strategy.run()

    # Print detailed output (matching original script format)
    print("=" * 80)
    print("GLOBAL METRICS")
    print("=" * 80)
    for key, value in result.data['global_metrics'].items():
        if isinstance(value, float):
            print(f"{key:30} : {value:,.2f}")
        else:
            print(f"{key:30} : {value:,}")

    print("\n" + "=" * 80)
    print("STATISTICS BY AGENT")
    print("=" * 80)

    agent_stats = result.data['agent_statistics']
    sorted_agents = sorted(agent_stats.items(), key=lambda x: x[1]['count'], reverse=True)

    for agent, stats in sorted_agents:
        print(f"\n{agent.upper()}")
        print("-" * 40)
        print(f"  Utilisations         : {stats['count']}")
        print(f"  Tokens input total   : {stats['total_input']:,}")
        print(f"  Tokens output total  : {stats['total_output']:,}")
        print(f"  Amplification moy.   : {stats['avg_amplification']:.2f}x")
        print(f"  Amplification méd.   : {stats['median_amplification']:.2f}x")
        print(f"  Cache hit rate moy.  : {stats['avg_cache_hit_rate']:.2%}")
        print(f"  Première utilisation : {stats['first_seen'] or 'N/A'}")
        print(f"  Dernière utilisation : {stats['last_seen'] or 'N/A'}")

    # Top dates
    print("\n" + "=" * 80)
    print("TOP 10 DAYS BY ACTIVITY")
    print("=" * 80)

    temporal = result.data['temporal_distribution']
    daily_totals = {date: sum(agents.values()) for date, agents in temporal['by_date'].items()}
    top_days = sorted(daily_totals.items(), key=lambda x: x[1], reverse=True)[:10]

    for date, count in top_days:
        print(f"{date}: {count} delegations")
        agents_this_day = temporal['by_date'][date]
        top_agents = sorted(agents_this_day.items(), key=lambda x: x[1], reverse=True)[:3]
        for agent, agent_count in top_agents:
            print(f"  - {agent}: {agent_count}")

    print("\n")
    result.print_summary()
