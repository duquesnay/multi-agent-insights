"""
Analysis Strategy Pattern for Delegation Retrospective

Implements ADR-004: Strategy Pattern for Pluggable Analyses
Enables adding new analyses without modifying existing code (Open/Closed Principle).

Usage:
    from tools.common.analysis_strategy import AnalysisStrategy, AnalysisResult

    class MyCustomAnalysis(AnalysisStrategy):
        def analyze(self, data):
            # Your analysis logic
            return AnalysisResult(
                name="My Analysis",
                data={"key": "value"},
                summary="Analysis complete"
            )

    # Run analysis
    result = MyCustomAnalysis().run()
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json


@dataclass
class AnalysisResult:
    """
    Standardized result from an analysis strategy.

    Attributes:
        name: Human-readable analysis name
        data: Analysis output data (serializable)
        summary: Brief text summary of findings
        metadata: Additional metadata (timestamps, versions, etc.)
        errors: Any errors encountered during analysis
        warnings: Non-fatal warnings
    """
    name: str
    data: Dict[str, Any]
    summary: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Add default metadata."""
        if 'timestamp' not in self.metadata:
            self.metadata['timestamp'] = datetime.now().isoformat()
        if 'success' not in self.metadata:
            self.metadata['success'] = len(self.errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            'name': self.name,
            'data': self.data,
            'summary': self.summary,
            'metadata': self.metadata,
            'errors': self.errors,
            'warnings': self.warnings
        }

    def save_to_file(self, path: Path) -> None:
        """Save result to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def print_summary(self) -> None:
        """Print formatted summary to console."""
        print("=" * 80)
        print(f"ANALYSIS: {self.name}")
        print("=" * 80)
        print(f"\n{self.summary}\n")

        if self.warnings:
            print(f"⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
            print()

        if self.errors:
            print(f"❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
            print()

        status = "✅ SUCCESS" if self.metadata.get('success') else "❌ FAILED"
        print(f"Status: {status}")
        print(f"Timestamp: {self.metadata.get('timestamp', 'N/A')}")
        print("=" * 80)


class AnalysisStrategy(ABC):
    """
    Abstract base class for all analysis strategies.

    Implements Template Method pattern with Open/Closed principle:
    - Concrete strategies implement analyze() method
    - Base class provides infrastructure (data loading, error handling, output)

    Subclasses should:
    1. Implement analyze(data) method
    2. Return AnalysisResult with findings
    3. Use self.add_warning() and self.add_error() for issues

    Example:
        class MyAnalysis(AnalysisStrategy):
            def get_name(self) -> str:
                return "My Custom Analysis"

            def analyze(self, data: Dict) -> AnalysisResult:
                # Process data
                findings = self.process(data)

                return AnalysisResult(
                    name=self.get_name(),
                    data=findings,
                    summary=f"Analyzed {len(findings)} items"
                )
    """

    def __init__(self):
        """Initialize strategy with error tracking."""
        self._warnings: List[str] = []
        self._errors: List[str] = []

    @abstractmethod
    def get_name(self) -> str:
        """
        Return human-readable analysis name.

        Returns:
            Analysis name for display and logging
        """
        pass

    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Execute analysis on provided data.

        Args:
            data: Input data dictionary with keys:
                - 'delegations': List of delegation dictionaries
                - 'sessions': List of session dictionaries
                - Additional data as needed by specific analysis

        Returns:
            AnalysisResult with findings

        Raises:
            Should handle errors internally and add to result.errors
            Only raise for critical infrastructure failures
        """
        pass

    def add_warning(self, message: str) -> None:
        """Add non-fatal warning."""
        self._warnings.append(message)

    def add_error(self, message: str) -> None:
        """Add error message."""
        self._errors.append(message)

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data structure.

        Args:
            data: Input data to validate

        Returns:
            True if valid, False otherwise (errors added to self._errors)
        """
        if not isinstance(data, dict):
            self.add_error(f"Expected dict, got {type(data)}")
            return False

        return True

    def run(self, data: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """
        Run analysis with error handling and data loading.

        Template Method pattern:
        1. Load data (if not provided)
        2. Validate data
        3. Execute analyze()
        4. Attach warnings/errors to result

        Args:
            data: Optional pre-loaded data. If None, loads from repository.

        Returns:
            AnalysisResult with findings
        """
        try:
            # Load data if not provided
            if data is None:
                data = self.load_default_data()

            # Validate
            if not self.validate_data(data):
                return AnalysisResult(
                    name=self.get_name(),
                    data={},
                    summary=f"Validation failed: {len(self._errors)} errors",
                    errors=self._errors,
                    warnings=self._warnings
                )

            # Execute analysis
            result = self.analyze(data)

            # Attach accumulated warnings/errors
            result.warnings.extend(self._warnings)
            result.errors.extend(self._errors)
            result.metadata['success'] = len(result.errors) == 0

            return result

        except Exception as e:
            # Critical failure - return error result
            self.add_error(f"Critical failure: {str(e)}")
            return AnalysisResult(
                name=self.get_name(),
                data={},
                summary=f"Analysis failed with exception",
                errors=self._errors,
                warnings=self._warnings
            )

    def load_default_data(self) -> Dict[str, Any]:
        """
        Load default data from repository.

        Override if analysis needs specific data sources.

        Returns:
            Dictionary with 'delegations' and 'sessions' keys
        """
        from tools.common.data_repository import load_delegations, load_sessions

        return {
            'delegations': load_delegations(),
            'sessions': load_sessions()
        }


class CompositeAnalysisStrategy(AnalysisStrategy):
    """
    Composite strategy that runs multiple sub-strategies.

    Useful for running related analyses together and aggregating results.

    Example:
        composite = CompositeAnalysisStrategy([
            MetricsAnalysis(),
            MarathonAnalysis(),
            RoutingQualityAnalysis()
        ])
        result = composite.run()
    """

    def __init__(self, strategies: List[AnalysisStrategy]):
        """
        Initialize with list of strategies to execute.

        Args:
            strategies: List of AnalysisStrategy instances to run
        """
        super().__init__()
        self.strategies = strategies

    def get_name(self) -> str:
        """Return composite name."""
        strategy_names = [s.get_name() for s in self.strategies]
        return f"Composite Analysis ({len(strategy_names)} strategies)"

    def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Run all sub-strategies and aggregate results.

        Args:
            data: Shared input data for all strategies

        Returns:
            AnalysisResult with aggregated findings
        """
        results = {}
        all_warnings = []
        all_errors = []

        for strategy in self.strategies:
            try:
                result = strategy.run(data)
                results[strategy.get_name()] = result.to_dict()
                all_warnings.extend(result.warnings)
                all_errors.extend(result.errors)
            except Exception as e:
                error_msg = f"{strategy.get_name()} failed: {str(e)}"
                all_errors.append(error_msg)
                results[strategy.get_name()] = {'error': error_msg}

        successful = sum(1 for r in results.values()
                        if isinstance(r, dict) and r.get('metadata', {}).get('success', False))

        return AnalysisResult(
            name=self.get_name(),
            data={'results': results},
            summary=f"Executed {len(self.strategies)} analyses: {successful} successful, {len(all_errors)} errors",
            warnings=all_warnings,
            errors=all_errors
        )
