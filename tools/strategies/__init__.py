"""
Analysis Strategies for Delegation Retrospective

This package contains concrete analysis strategies implementing the Strategy Pattern.
Each strategy is independent and can be run standalone or via the AnalysisRunner.

Available Strategies:
    - MetricsAnalysisStrategy: Token metrics and agent usage statistics
    - MarathonAnalysisStrategy: Marathon session identification and analysis
    - RoutingQualityAnalysisStrategy: Routing decision quality assessment

Usage:
    from tools.strategies import MetricsAnalysisStrategy

    analysis = MetricsAnalysisStrategy()
    result = analysis.run()
    result.print_summary()
"""

from .metrics_analysis import MetricsAnalysisStrategy
from .marathon_analysis import MarathonAnalysisStrategy
from .routing_quality_analysis import RoutingQualityAnalysisStrategy

__all__ = [
    'MetricsAnalysisStrategy',
    'MarathonAnalysisStrategy',
    'RoutingQualityAnalysisStrategy',
]
