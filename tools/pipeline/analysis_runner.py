#!/usr/bin/env python3
"""
Analysis Runner - Orchestrator for running multiple analysis strategies

Implements the Strategy Pattern orchestration layer. Runs multiple analyses
with shared data loading and aggregated output.

Usage:
    # Run all registered analyses
    python analysis_runner.py --all

    # Run specific analyses
    python analysis_runner.py --metrics --marathons

    # Run with custom output directory
    python analysis_runner.py --all --output results/

    # Run programmatically
    from analysis_runner import AnalysisRunner
    runner = AnalysisRunner()
    results = runner.run_all()
"""

import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json

from common.analysis_strategy import AnalysisStrategy, CompositeAnalysisStrategy
from strategies import (
    MetricsAnalysisStrategy,
    MarathonAnalysisStrategy,
    RoutingQualityAnalysisStrategy
)


class AnalysisRunner:
    """
    Orchestrator for running multiple analysis strategies.

    Benefits:
    - Load data once, run multiple analyses
    - Aggregate results
    - Parallel execution (future enhancement)
    - Consistent output format
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize runner.

        Args:
            output_dir: Directory for output files (default: ./analysis_results/)
        """
        self.output_dir = output_dir or Path('./analysis_results')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Registry of available strategies
        self._registry: Dict[str, AnalysisStrategy] = {}
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """Register built-in analysis strategies."""
        self.register('metrics', MetricsAnalysisStrategy())
        self.register('marathons', MarathonAnalysisStrategy())
        self.register('routing_quality', RoutingQualityAnalysisStrategy())

    def register(self, name: str, strategy: AnalysisStrategy) -> None:
        """
        Register a new analysis strategy.

        Args:
            name: Unique identifier for strategy
            strategy: AnalysisStrategy instance

        Example:
            runner.register('custom', MyCustomAnalysisStrategy())
        """
        if name in self._registry:
            print(f"Warning: Overwriting existing strategy '{name}'")
        self._registry[name] = strategy

    def list_strategies(self) -> List[str]:
        """
        Get list of registered strategy names.

        Returns:
            List of strategy identifiers
        """
        return list(self._registry.keys())

    def run_strategy(
        self,
        name: str,
        data: Optional[Dict] = None,
        save: bool = True
    ) -> Dict:
        """
        Run a single named strategy.

        Args:
            name: Strategy identifier
            data: Optional pre-loaded data
            save: Whether to save result to file

        Returns:
            Result dictionary

        Raises:
            KeyError: If strategy not found
        """
        if name not in self._registry:
            raise KeyError(f"Strategy '{name}' not found. Available: {self.list_strategies()}")

        strategy = self._registry[name]
        print(f"\n{'='*80}")
        print(f"Running: {strategy.get_name()}")
        print(f"{'='*80}")

        result = strategy.run(data)

        if save:
            output_file = self.output_dir / f"{name}_result.json"
            result.save_to_file(output_file)
            print(f"\nSaved to: {output_file}")

        result.print_summary()

        return result.to_dict()

    def run_multiple(
        self,
        strategy_names: List[str],
        save: bool = True
    ) -> Dict[str, Dict]:
        """
        Run multiple strategies with shared data loading.

        Args:
            strategy_names: List of strategy identifiers
            save: Whether to save individual results

        Returns:
            Dictionary mapping strategy names to results
        """
        # Load data once
        print("Loading data...")
        from common.data_repository import load_delegations, load_sessions

        data = {
            'delegations': load_delegations(),
            'sessions': load_sessions()
        }
        print(f"Loaded {len(data['delegations'])} delegations, {len(data['sessions'])} sessions\n")

        # Run each strategy
        results = {}
        for name in strategy_names:
            try:
                result = self.run_strategy(name, data=data, save=save)
                results[name] = result
            except Exception as e:
                print(f"ERROR running {name}: {e}")
                results[name] = {'error': str(e)}

        # Save aggregate results
        if save:
            self._save_aggregate_results(results)

        return results

    def run_all(self, save: bool = True) -> Dict[str, Dict]:
        """
        Run all registered strategies.

        Args:
            save: Whether to save results

        Returns:
            Dictionary mapping strategy names to results
        """
        return self.run_multiple(self.list_strategies(), save=save)

    def run_composite(
        self,
        strategy_names: List[str],
        save: bool = True
    ) -> Dict:
        """
        Run strategies as a composite (single result with all sub-results).

        Args:
            strategy_names: List of strategy identifiers
            save: Whether to save composite result

        Returns:
            Composite result dictionary
        """
        strategies = [self._registry[name] for name in strategy_names]
        composite = CompositeAnalysisStrategy(strategies)

        print(f"\n{'='*80}")
        print(f"Running composite analysis: {len(strategies)} strategies")
        print(f"{'='*80}\n")

        result = composite.run()

        if save:
            output_file = self.output_dir / "composite_result.json"
            result.save_to_file(output_file)
            print(f"\nSaved to: {output_file}")

        result.print_summary()

        return result.to_dict()

    def _save_aggregate_results(self, results: Dict[str, Dict]) -> None:
        """Save aggregated results to single file."""
        aggregate = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'runner': 'AnalysisRunner',
                'strategies': list(results.keys())
            },
            'results': results
        }

        output_file = self.output_dir / "aggregate_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(aggregate, f, indent=2, ensure_ascii=False)

        print(f"\nAggregate results saved to: {output_file}")

    def generate_report(self, results: Dict[str, Dict]) -> str:
        """
        Generate markdown report from results.

        Args:
            results: Results dictionary from run_multiple() or run_all()

        Returns:
            Markdown formatted report
        """
        lines = []
        lines.append("# Analysis Results Report")
        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        for strategy_name, result in results.items():
            if 'error' in result:
                lines.append(f"## {strategy_name.upper()} - ERROR")
                lines.append(f"\n{result['error']}\n")
                continue

            lines.append(f"## {result['name']}")
            lines.append(f"\n{result['summary']}\n")

            if result.get('warnings'):
                lines.append("### Warnings")
                for warning in result['warnings']:
                    lines.append(f"- {warning}")
                lines.append("")

            if result.get('errors'):
                lines.append("### Errors")
                for error in result['errors']:
                    lines.append(f"- {error}")
                lines.append("")

            metadata = result.get('metadata', {})
            lines.append("### Metadata")
            for key, value in metadata.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run delegation retrospective analyses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all analyses
  python analysis_runner.py --all

  # Run specific analyses
  python analysis_runner.py --metrics --marathons

  # Custom output directory
  python analysis_runner.py --all --output results/

  # Generate markdown report
  python analysis_runner.py --all --report
        """
    )

    parser.add_argument('--all', action='store_true',
                       help='Run all registered analyses')
    parser.add_argument('--metrics', action='store_true',
                       help='Run metrics analysis')
    parser.add_argument('--marathons', action='store_true',
                       help='Run marathon analysis')
    parser.add_argument('--routing-quality', action='store_true',
                       help='Run routing quality analysis')
    parser.add_argument('--output', type=str, default='./analysis_results',
                       help='Output directory (default: ./analysis_results)')
    parser.add_argument('--report', action='store_true',
                       help='Generate markdown report')
    parser.add_argument('--list', action='store_true',
                       help='List available strategies')
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save results to files')

    args = parser.parse_args()

    runner = AnalysisRunner(output_dir=Path(args.output))

    # List strategies
    if args.list:
        print("Available strategies:")
        for name in runner.list_strategies():
            strategy = runner._registry[name]
            print(f"  - {name:20} : {strategy.get_name()}")
        return

    # Determine which strategies to run
    strategies_to_run = []
    if args.all:
        strategies_to_run = runner.list_strategies()
    else:
        if args.metrics:
            strategies_to_run.append('metrics')
        if args.marathons:
            strategies_to_run.append('marathons')
        if args.routing_quality:
            strategies_to_run.append('routing_quality')

    if not strategies_to_run:
        parser.print_help()
        return

    # Run analyses
    save = not args.no_save
    results = runner.run_multiple(strategies_to_run, save=save)

    # Generate report if requested
    if args.report and save:
        report = runner.generate_report(results)
        report_file = runner.output_dir / "analysis_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nMarkdown report saved to: {report_file}")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    successful = sum(1 for r in results.values() if 'error' not in r)
    print(f"Ran {len(results)} analyses: {successful} successful")


if __name__ == "__main__":
    main()
