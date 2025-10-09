#!/usr/bin/env python3
"""
Analysis Pipeline Orchestrator for Delegation Retrospective

Coordinates multi-step analysis workflow with dependency validation and progress tracking.

Pipeline Stages:
    1. Extraction: Load raw data from Claude projects
    2. Enrichment: Add metadata and cross-references
    3. Segmentation: Temporal and categorical division
    4. Analysis: Metrics, patterns, insights
    5. Reporting: Generate markdown reports

Usage:
    # Run full pipeline
    python run_analysis_pipeline.py --all

    # Run specific stages
    python run_analysis_pipeline.py --stage extraction --stage enrichment

    # Resume from specific stage
    python run_analysis_pipeline.py --from segmentation

    # Dry run to preview execution plan
    python run_analysis_pipeline.py --all --dry-run

    # Force re-run of stages (skip cache)
    python run_analysis_pipeline.py --all --force
"""

import argparse
import sys
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime
import json

from tools.common.config import (
    PROJECT_ROOT,
    DATA_DIR,
    RAW_DATA_DIR,
    SESSIONS_DATA_FILE,
    ENRICHED_SESSIONS_FILE,
    ROUTING_PATTERNS_FILE,
    TEMPORAL_SEGMENTATION_FILE,
    DELEGATION_RAW_FILE,
    AGENT_CALLS_CSV,
    ensure_data_dirs
)


class PipelineStage(Enum):
    """Pipeline stages in execution order."""
    BACKUP = "backup"
    EXTRACTION = "extraction"
    ENRICHMENT = "enrichment"
    SEGMENTATION = "segmentation"
    ANALYSIS = "analysis"
    REPORTING = "reporting"


class StageDefinition:
    """Definition of a pipeline stage with dependencies and validation."""

    def __init__(
        self,
        stage: PipelineStage,
        name: str,
        description: str,
        scripts: List[str],
        produces: List[Path],
        requires: List[Path],
        depends_on: List[PipelineStage]
    ):
        self.stage = stage
        self.name = name
        self.description = description
        self.scripts = scripts
        self.produces = produces
        self.requires = requires
        self.depends_on = depends_on

    def check_prerequisites(self) -> Tuple[bool, List[str]]:
        """Check if all required files exist.

        Returns:
            (success, missing_files)
        """
        missing = []
        for required_file in self.requires:
            if not required_file.exists():
                missing.append(str(required_file))
        return len(missing) == 0, missing

    def check_outputs_exist(self) -> bool:
        """Check if this stage has already been run (outputs exist)."""
        return all(output.exists() for output in self.produces)

    def is_stale(self) -> bool:
        """Check if outputs are stale (older than inputs)."""
        if not self.check_outputs_exist():
            return True

        if not self.requires:
            return False

        # Get oldest output timestamp
        output_times = [f.stat().st_mtime for f in self.produces if f.exists()]
        if not output_times:
            return True
        oldest_output = min(output_times)

        # Get newest input timestamp
        input_times = [f.stat().st_mtime for f in self.requires if f.exists()]
        if not input_times:
            return False
        newest_input = max(input_times)

        return newest_input > oldest_output


# Pipeline stage definitions
STAGE_DEFINITIONS: Dict[PipelineStage, StageDefinition] = {
    PipelineStage.BACKUP: StageDefinition(
        stage=PipelineStage.BACKUP,
        name="Conversation Backup",
        description="Archive raw .jsonl conversations from ~/.claude/projects/",
        scripts=[
            "tools/scripts/copy_conversations.py",
        ],
        produces=[
            DATA_DIR / "conversations" / ".backup_complete",  # Marker file
        ],
        requires=[
            # External: ~/.claude/projects/ (checked separately)
        ],
        depends_on=[]
    ),

    PipelineStage.EXTRACTION: StageDefinition(
        stage=PipelineStage.EXTRACTION,
        name="Data Extraction",
        description="Extract raw session data from Claude projects",
        scripts=[
            "tools/pipeline/extract_all_sessions.py",
            "tools/pipeline/extract_enriched_data.py",
        ],
        produces=[
            SESSIONS_DATA_FILE,
            ENRICHED_SESSIONS_FILE,
        ],
        requires=[
            # External dependency - checked differently
        ],
        depends_on=[]
    ),

    PipelineStage.ENRICHMENT: StageDefinition(
        stage=PipelineStage.ENRICHMENT,
        name="Data Enrichment",
        description="Add metadata, cross-references, and routing patterns",
        scripts=[
            "tools/pipeline/extract_routing_patterns.py",
            "tools/pipeline/classify_marathons.py",
        ],
        produces=[
            ROUTING_PATTERNS_FILE,
            DATA_DIR / "marathon-classification.json",
        ],
        requires=[
            ENRICHED_SESSIONS_FILE,
        ],
        depends_on=[PipelineStage.EXTRACTION]
    ),

    PipelineStage.SEGMENTATION: StageDefinition(
        stage=PipelineStage.SEGMENTATION,
        name="Data Segmentation",
        description="Segment data by time periods and categories",
        scripts=[
            "tools/pipeline/segment_data.py",
        ],
        produces=[
            TEMPORAL_SEGMENTATION_FILE,
        ],
        requires=[
            SESSIONS_DATA_FILE,
        ],
        depends_on=[PipelineStage.EXTRACTION]
    ),

    PipelineStage.ANALYSIS: StageDefinition(
        stage=PipelineStage.ANALYSIS,
        name="Analysis Execution",
        description="Run metrics, pattern detection, and insights generation",
        scripts=[
            "tools/pipeline/analysis_runner.py --all",
        ],
        produces=[
            PROJECT_ROOT / "analysis_results" / "aggregate_results.json",
        ],
        requires=[
            ENRICHED_SESSIONS_FILE,
            ROUTING_PATTERNS_FILE,
        ],
        depends_on=[PipelineStage.ENRICHMENT]
    ),

    PipelineStage.REPORTING: StageDefinition(
        stage=PipelineStage.REPORTING,
        name="Report Generation",
        description="Generate markdown reports from analysis results",
        scripts=[
            "tools/pipeline/generate_routing_report.py",
        ],
        produces=[
            DATA_DIR / "routing_report.md",
        ],
        requires=[
            ROUTING_PATTERNS_FILE,
            DATA_DIR / "routing_quality_analysis.json",
        ],
        depends_on=[PipelineStage.ANALYSIS]
    ),
}


class PipelineOrchestrator:
    """Orchestrates multi-stage analysis pipeline with dependency management."""

    def __init__(self, verbose: bool = True, force: bool = False):
        """Initialize orchestrator.

        Args:
            verbose: Print progress messages
            force: Force re-run of stages even if outputs exist
        """
        self.verbose = verbose
        self.force = force
        self.execution_log: List[Dict] = []

    def log(self, message: str):
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(message)

    def check_external_dependencies(self) -> Tuple[bool, List[str]]:
        """Check external dependencies (Claude projects directory).

        Returns:
            (success, missing_dependencies)
        """
        from tools.common.config import PROJECTS_DIR

        missing = []
        if not PROJECTS_DIR.exists():
            missing.append(f"Claude projects directory: {PROJECTS_DIR}")

        return len(missing) == 0, missing

    def validate_stage(
        self,
        stage_def: StageDefinition,
        dry_run: bool = False,
        planned_stages: Set[PipelineStage] = None
    ) -> Tuple[bool, List[str]]:
        """Validate a stage can be executed.

        Args:
            stage_def: Stage to validate
            dry_run: If True, consider stages in pipeline as "will be run"
            planned_stages: Set of stages planned for execution (for dry run)

        Returns:
            (can_execute, reasons)
        """
        reasons = []
        planned_stages = planned_stages or set()

        # Check dependencies are met
        for dep_stage in stage_def.depends_on:
            dep_def = STAGE_DEFINITIONS[dep_stage]

            # In dry run, check if dependency will be satisfied by pipeline
            if dry_run and dep_stage in planned_stages:
                continue  # Will be run before this stage

            if not dep_def.check_outputs_exist():
                reasons.append(
                    f"Depends on {dep_stage.value} which hasn't been run yet"
                )

        # Check prerequisites exist
        success, missing = stage_def.check_prerequisites()
        if not success:
            reasons.append(f"Missing required files: {', '.join(missing)}")

        return len(reasons) == 0, reasons

    def should_run_stage(self, stage_def: StageDefinition) -> Tuple[bool, str]:
        """Determine if stage should be run.

        Returns:
            (should_run, reason)
        """
        if self.force:
            return True, "Forced re-run"

        if not stage_def.check_outputs_exist():
            return True, "Outputs missing"

        if stage_def.is_stale():
            return True, "Outputs stale (inputs newer)"

        return False, "Already complete and up-to-date"

    def execute_stage(
        self,
        stage_def: StageDefinition,
        dry_run: bool = False,
        planned_stages: Set[PipelineStage] = None
    ) -> bool:
        """Execute a pipeline stage.

        Args:
            stage_def: Stage definition
            dry_run: If True, only show what would be executed
            planned_stages: Set of stages planned for execution (for validation)

        Returns:
            True if successful (or dry run), False if failed
        """
        import subprocess

        self.log(f"\n{'='*80}")
        self.log(f"Stage: {stage_def.name}")
        self.log(f"{'='*80}")
        self.log(f"Description: {stage_def.description}")

        # Validate stage can run
        can_execute, reasons = self.validate_stage(
            stage_def,
            dry_run=dry_run,
            planned_stages=planned_stages
        )
        if not can_execute:
            self.log(f"❌ Cannot execute: {'; '.join(reasons)}")
            return False

        # Check if stage needs to run
        should_run, reason = self.should_run_stage(stage_def)
        if not should_run:
            self.log(f"⏭️  Skipping: {reason}")
            return True

        self.log(f"▶️  Running: {reason}")

        if dry_run:
            self.log("🔍 [DRY RUN] Would execute:")
            for script in stage_def.scripts:
                self.log(f"  - python {script}")
            return True

        # Execute scripts
        start_time = datetime.now()
        for script in stage_def.scripts:
            self.log(f"\n📄 Executing: {script}")

            # Parse script and args
            parts = script.split()
            script_path = PROJECT_ROOT / parts[0]
            args = parts[1:] if len(parts) > 1 else []

            if not script_path.exists():
                self.log(f"❌ Script not found: {script_path}")
                return False

            try:
                # Pass runtime config through environment variables
                import os
                env = os.environ.copy()

                from tools.common.config import get_runtime_config
                runtime_config = get_runtime_config()

                if runtime_config.project_filter:
                    env['ANALYSIS_PROJECT_FILTER'] = runtime_config.project_filter
                if runtime_config.start_date:
                    env['ANALYSIS_START_DATE'] = runtime_config.start_date
                if runtime_config.end_date:
                    env['ANALYSIS_END_DATE'] = runtime_config.end_date
                if runtime_config.discover_periods:
                    env['ANALYSIS_DISCOVER_PERIODS'] = 'true'
                if runtime_config.source_live:
                    env['ANALYSIS_SOURCE_LIVE'] = 'true'

                result = subprocess.run(
                    ["python", str(script_path)] + args,
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                    env=env
                )

                if result.returncode != 0:
                    self.log(f"❌ Script failed with exit code {result.returncode}")
                    if result.stderr:
                        self.log(f"Error output:\n{result.stderr}")
                    return False

                if result.stdout and self.verbose:
                    # Print last few lines of output
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-5:]:
                        self.log(f"  {line}")

            except subprocess.TimeoutExpired:
                self.log(f"❌ Script timeout (>10 minutes)")
                return False
            except Exception as e:
                self.log(f"❌ Execution error: {e}")
                return False

        duration = (datetime.now() - start_time).total_seconds()
        self.log(f"\n✅ Stage complete in {duration:.1f}s")

        # Log execution
        self.execution_log.append({
            "stage": stage_def.stage.value,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "success": True
        })

        return True

    def run_pipeline(
        self,
        stages: List[PipelineStage],
        dry_run: bool = False
    ) -> bool:
        """Run pipeline stages in order.

        Args:
            stages: List of stages to run
            dry_run: If True, only show execution plan

        Returns:
            True if all stages successful, False otherwise
        """
        ensure_data_dirs()

        self.log("=" * 80)
        self.log("DELEGATION RETROSPECTIVE ANALYSIS PIPELINE")
        self.log("=" * 80)

        if dry_run:
            self.log("🔍 DRY RUN MODE - No changes will be made")

        # Show planned stages
        self.log(f"\nPlanned stages ({len(stages)}):")
        for stage in stages:
            stage_def = STAGE_DEFINITIONS[stage]
            self.log(f"  {stage.value:15} - {stage_def.name}")
        self.log("")

        # Check external dependencies first
        success, missing = self.check_external_dependencies()
        if not success:
            self.log(f"❌ Missing external dependencies:")
            for dep in missing:
                self.log(f"  - {dep}")
            return False

        # Create set of planned stages for dependency validation
        planned_stages = set(stages)

        # Execute stages in order
        for stage in stages:
            stage_def = STAGE_DEFINITIONS[stage]
            success = self.execute_stage(
                stage_def,
                dry_run=dry_run,
                planned_stages=planned_stages
            )
            if not success:
                self.log(f"\n❌ Pipeline failed at stage: {stage.value}")
                return False

        # Save execution log
        if not dry_run and self.execution_log:
            log_file = PROJECT_ROOT / "pipeline_execution_log.json"
            with open(log_file, 'a') as f:
                for entry in self.execution_log:
                    f.write(json.dumps(entry) + '\n')

        self.log("\n" + "=" * 80)
        if dry_run:
            self.log("🔍 DRY RUN COMPLETE - Pipeline validated")
        else:
            self.log("✅ PIPELINE COMPLETE")
        self.log("=" * 80)

        return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Orchestrate delegation retrospective analysis pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline (default: since August 2025, all projects)
  python run_analysis_pipeline.py --all

  # Single project analysis
  python run_analysis_pipeline.py --all --project "obsidian-local-rest-api" \\
    --start-date "2025-09-26" --end-date "2025-10-06"

  # Auto-discover periods from git
  python run_analysis_pipeline.py --all --discover-periods

  # Run specific stages
  python run_analysis_pipeline.py --stage extraction --stage enrichment

  # Resume from segmentation onwards
  python run_analysis_pipeline.py --from segmentation

  # Preview execution plan
  python run_analysis_pipeline.py --all --dry-run

  # Force re-run (ignore cache)
  python run_analysis_pipeline.py --stage analysis --force
        """
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all pipeline stages'
    )
    parser.add_argument(
        '--stage',
        action='append',
        choices=[s.value for s in PipelineStage],
        help='Run specific stage (can be repeated)'
    )
    parser.add_argument(
        '--from',
        dest='from_stage',
        choices=[s.value for s in PipelineStage],
        help='Run from this stage onwards'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be executed without running'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-run of stages (skip cache)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )
    parser.add_argument(
        '--list-stages',
        action='store_true',
        help='List all pipeline stages and exit'
    )

    # Runtime configuration parameters
    parser.add_argument(
        '--project',
        type=str,
        help='Filter by project path (substring match, e.g., "obsidian-local-rest-api")'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        help='Analysis start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        help='Analysis end date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--discover-periods',
        action='store_true',
        help='Use git archaeology to discover period definitions'
    )

    # Backup and source configuration
    parser.add_argument(
        '--skip-backup',
        action='store_true',
        help='Skip conversation backup stage (use existing backup or live source)'
    )
    parser.add_argument(
        '--source-live',
        action='store_true',
        help='Read conversations from ~/.claude/projects/ instead of backup archive'
    )

    args = parser.parse_args()

    # Set runtime configuration from CLI arguments
    if args.project or args.start_date or args.end_date or args.discover_periods or args.source_live:
        from tools.common.config import RuntimeConfig, set_runtime_config

        config = RuntimeConfig(
            project_filter=args.project,
            start_date=args.start_date,
            end_date=args.end_date,
            discover_periods=args.discover_periods,
            source_live=args.source_live
        )
        set_runtime_config(config)

        # Show configuration
        if not args.quiet:
            print("Runtime Configuration:")
            if args.project:
                print(f"  Project filter: {args.project}")
            if args.start_date or args.end_date:
                print(f"  Date range: {args.start_date or 'any'} to {args.end_date or 'any'}")
            if args.discover_periods:
                print(f"  Period discovery: git archaeology")
            if args.source_live:
                print(f"  Source: ~/.claude/projects/ (live)")
            else:
                print(f"  Source: data/conversations/ (backup)")
            print()

    # List stages
    if args.list_stages:
        print("Pipeline Stages (in execution order):\n")
        for stage in PipelineStage:
            stage_def = STAGE_DEFINITIONS[stage]
            print(f"{stage.value:15} : {stage_def.name}")
            print(f"{'':15}   {stage_def.description}")
            print(f"{'':15}   Scripts: {', '.join(stage_def.scripts)}")
            print()
        return 0

    # Determine stages to run
    stages_to_run = []
    if args.all:
        stages_to_run = list(PipelineStage)
        # Remove BACKUP stage if --skip-backup
        if args.skip_backup:
            stages_to_run = [s for s in stages_to_run if s != PipelineStage.BACKUP]
    elif args.from_stage:
        # Run from specified stage onwards
        start_stage = PipelineStage(args.from_stage)
        started = False
        for stage in PipelineStage:
            if stage == start_stage:
                started = True
            if started:
                stages_to_run.append(stage)
    elif args.stage:
        # Run specific stages
        stages_to_run = [PipelineStage(s) for s in args.stage]
    else:
        parser.print_help()
        return 1

    # Run pipeline
    orchestrator = PipelineOrchestrator(
        verbose=not args.quiet,
        force=args.force
    )

    success = orchestrator.run_pipeline(
        stages=stages_to_run,
        dry_run=args.dry_run
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
