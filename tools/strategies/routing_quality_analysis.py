"""
Routing Quality Analysis Strategy - Identify routing decision quality

Analyzes:
- Misrouted tasks (wrong agent selection)
- Underutilized agents
- Developer explosion patterns
- Routing patterns by period

Converted from: analyze_routing_quality.py
"""

from typing import Dict, Any, List
from collections import defaultdict

from common.analysis_strategy import AnalysisStrategy, AnalysisResult


class RoutingQualityAnalysisStrategy(AnalysisStrategy):
    """
    Analyzes routing quality to identify misrouted tasks and underutilized agents.
    """

    def get_name(self) -> str:
        return "Routing Quality Analysis"

    def load_default_data(self) -> Dict[str, Any]:
        """Load routing patterns data instead of raw delegations."""
        from common.data_repository import load_routing_patterns

        return {
            'routing_data': load_routing_patterns(pattern_type='by_period')
        }

    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Execute routing quality analysis.

        Args:
            data: Dictionary with 'routing_data' key containing routing patterns

        Returns:
            AnalysisResult with routing quality findings
        """
        routing_data = data.get('routing_data', {})

        if not routing_data or 'periods' not in routing_data:
            self.add_error("No routing patterns data provided")
            return AnalysisResult(
                name=self.get_name(),
                data={},
                summary="No routing patterns to analyze"
            )

        results_by_period = {}

        for period_key in ['P2', 'P3', 'P4']:
            if period_key not in routing_data.get('periods', {}):
                self.add_warning(f"Period {period_key} not found in data")
                continue

            period = routing_data['periods'][period_key]
            delegations = period.get('full_delegations', [])

            if not delegations:
                self.add_warning(f"No delegations for period {period_key}")
                continue

            period_results = {
                'name': period.get('name', period_key),
                'date_range': period.get('date_range', 'Unknown'),
                'total_delegations': len(delegations)
            }

            # Find misrouted tasks
            misrouted = self._find_misrouted_tasks(delegations)
            period_results['misrouted_count'] = len(misrouted)
            period_results['misrouted_examples'] = self._extract_concrete_examples(misrouted, limit=5)

            # Analyze developer explosion in P3
            if period_key == 'P3':
                dev_categories = self._analyze_developer_explosion(delegations)
                period_results['developer_explosion'] = {
                    cat: len(tasks) for cat, tasks in dev_categories.items()
                }

            # Find underutilized agents
            underutilized = self._find_underutilized_agents(period, period_key)
            period_results['underutilized_agents'] = underutilized

            results_by_period[period_key] = period_results

        # Build summary
        summary = self._build_summary(results_by_period)

        return AnalysisResult(
            name=self.get_name(),
            data={'periods': results_by_period},
            summary=summary,
            metadata={
                'source_date': routing_data.get('extraction_date', 'Unknown'),
                'periods_analyzed': list(results_by_period.keys())
            }
        )

    def _find_misrouted_tasks(self, delegations: List[Dict]) -> List[Dict]:
        """Find tasks that were routed to wrong agent."""
        misrouted = []

        for delegation in delegations:
            agent = delegation.get('agent')
            prompt = delegation.get('prompt', '').lower()
            desc = delegation.get('description', '').lower()
            combined = prompt + ' ' + desc

            # Architecture/design tasks to developer
            if agent == 'developer':
                if any(word in combined for word in ['architecture', 'design pattern', 'system design', 'structure']):
                    if 'implement' not in combined:
                        misrouted.append({
                            'delegation': delegation,
                            'issue': 'Architecture task to developer',
                            'should_be': 'solution-architect',
                            'reason': 'Architecture/design questions should go to solution-architect'
                        })

            # Refactoring to developer
            if agent == 'developer':
                if any(word in combined for word in ['refactor', 'restructure', 'reorganize', 'clean up code']):
                    misrouted.append({
                        'delegation': delegation,
                        'issue': 'Refactoring to developer',
                        'should_be': 'refactoring-specialist',
                        'reason': 'Refactoring tasks should go to refactoring-specialist'
                    })

            # Simple tasks to senior
            if agent == 'senior-developer':
                if any(word in combined for word in ['simple', 'basic', 'straightforward', 'trivial']):
                    misrouted.append({
                        'delegation': delegation,
                        'issue': 'Simple task to senior-developer',
                        'should_be': 'junior-developer',
                        'reason': 'Simple tasks should be delegated to junior-developer'
                    })

            # Content creation to developer
            if agent == 'developer':
                if any(word in combined for word in ['write content', 'create documentation', 'write guide', 'tutorial']):
                    if 'code' not in combined:
                        misrouted.append({
                            'delegation': delegation,
                            'issue': 'Content creation to developer',
                            'should_be': 'content-developer',
                            'reason': 'Content/documentation creation should go to content-developer'
                        })

            # Performance optimization
            if agent in ['developer', 'senior-developer']:
                if any(word in combined for word in ['optimize performance', 'slow', 'speed up', 'bottleneck']):
                    misrouted.append({
                        'delegation': delegation,
                        'issue': 'Performance task to general developer',
                        'should_be': 'performance-optimizer',
                        'reason': 'Performance optimization should go to performance-optimizer'
                    })

        return misrouted

    def _analyze_developer_explosion(self, delegations: List[Dict]) -> Dict[str, List]:
        """Analyze why developer had high usage."""
        developer_tasks = [d for d in delegations if d.get('agent') == 'developer']

        task_categories = {
            'testing': [],
            'implementation': [],
            'debugging': [],
            'refactoring': [],
            'git': [],
            'documentation': [],
            'analysis': [],
            'other': []
        }

        for task in developer_tasks:
            prompt_lower = task.get('prompt', '').lower()
            desc_lower = task.get('description', '').lower()
            combined = prompt_lower + ' ' + desc_lower

            if any(word in combined for word in ['test', 'pytest', 'unittest']):
                task_categories['testing'].append(task)
            elif any(word in combined for word in ['implement', 'create', 'add', 'build']):
                task_categories['implementation'].append(task)
            elif any(word in combined for word in ['debug', 'fix', 'error', 'issue']):
                task_categories['debugging'].append(task)
            elif any(word in combined for word in ['refactor', 'restructure', 'reorganize']):
                task_categories['refactoring'].append(task)
            elif any(word in combined for word in ['git', 'commit', 'branch', 'merge']):
                task_categories['git'].append(task)
            elif any(word in combined for word in ['document', 'readme', 'comment']):
                task_categories['documentation'].append(task)
            elif any(word in combined for word in ['analyze', 'review', 'examine', 'investigate']):
                task_categories['analysis'].append(task)
            else:
                task_categories['other'].append(task)

        return task_categories

    def _find_underutilized_agents(self, period_data: Dict, period_name: str) -> List[Dict]:
        """Find agents that exist but are rarely used."""
        analysis = period_data.get('analysis', {})
        agent_dist = analysis.get('agent_distribution', {})
        total = analysis.get('total_delegations', 0)

        # Available agents by period
        available_specialists = {
            'P2': ['solution-architect', 'project-framer'],
            'P3': ['solution-architect', 'project-framer', 'content-developer', 'refactoring-specialist'],
            'P4': ['solution-architect', 'project-framer', 'content-developer', 'refactoring-specialist',
                   'junior-developer', 'senior-developer']
        }

        underutilized = []
        for agent in available_specialists.get(period_name, []):
            count = agent_dist.get(agent, 0)
            percentage = (count / total * 100) if total > 0 else 0

            # Flag if under 5% usage
            if percentage < 5.0:
                underutilized.append({
                    'agent': agent,
                    'count': count,
                    'percentage': percentage
                })

        return underutilized

    def _extract_concrete_examples(self, misrouted_tasks: List[Dict], limit: int = 3) -> List[Dict]:
        """Extract concrete examples with context."""
        examples = []
        for item in misrouted_tasks[:limit]:
            delegation = item['delegation']
            prompt = delegation.get('prompt', '')
            prompt_preview = prompt[:300] + '...' if len(prompt) > 300 else prompt

            examples.append({
                'agent_chosen': delegation.get('agent'),
                'agent_should_be': item['should_be'],
                'reason': item['reason'],
                'task_description': delegation.get('description', 'N/A'),
                'prompt_preview': prompt_preview,
                'session': delegation.get('session_id'),
                'timestamp': delegation.get('timestamp')
            })

        return examples

    def _build_summary(self, results_by_period: Dict) -> str:
        """Build human-readable summary."""
        lines = []
        total_misrouted = sum(p.get('misrouted_count', 0) for p in results_by_period.values())
        lines.append(f"Analyzed routing quality across {len(results_by_period)} periods")
        lines.append(f"Total misrouted tasks identified: {total_misrouted}")

        for period, data in results_by_period.items():
            lines.append(f"\n{period} ({data['name']}):")
            lines.append(f"  - Total delegations: {data['total_delegations']}")
            lines.append(f"  - Misrouted: {data['misrouted_count']}")

            underutilized = data.get('underutilized_agents', [])
            if underutilized:
                lines.append(f"  - Underutilized agents: {len(underutilized)}")
                for agent_info in underutilized[:3]:
                    lines.append(f"    - {agent_info['agent']}: {agent_info['percentage']:.1f}%")

        return "\n".join(lines)


# Backward compatibility: allow running as standalone script
if __name__ == "__main__":
    strategy = RoutingQualityAnalysisStrategy()
    result = strategy.run()

    # Print detailed output (matching original script format)
    for period_key, period_results in result.data['periods'].items():
        print(f"\n{'='*60}")
        print(f"Analyzing {period_key} - {period_results['name']}")
        print(f"{'='*60}")

        print(f"\nMisrouted tasks found: {period_results['misrouted_count']}")
        if period_results['misrouted_count'] > 0:
            print("\nTop 3 examples:")
            for i, ex in enumerate(period_results['misrouted_examples'][:3], 1):
                print(f"\n  {i}. {ex['agent_chosen']} → should be {ex['agent_should_be']}")
                print(f"     Reason: {ex['reason']}")
                print(f"     Task: {ex['task_description']}")
                print(f"     Prompt: {ex['prompt_preview'][:150]}...")

        if 'developer_explosion' in period_results:
            print(f"\nDeveloper explosion breakdown:")
            for cat, count in period_results['developer_explosion'].items():
                if count > 0:
                    pct = (count / sum(period_results['developer_explosion'].values())) * 100
                    print(f"  {cat}: {count} ({pct:.1f}%)")

        underutilized = period_results.get('underutilized_agents', [])
        if underutilized:
            print(f"\nUnderutilized agents:")
            for agent_info in underutilized:
                print(f"  {agent_info['agent']}: {agent_info['count']} calls ({agent_info['percentage']:.1f}%)")

    print("\n")
    result.print_summary()
