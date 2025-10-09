#!/usr/bin/env python3
"""Wrapper script to run the analysis pipeline from project root."""

import sys
from pathlib import Path

# Add project root to path so tools.* imports work
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the actual pipeline
from tools.pipeline.run_analysis_pipeline import main

if __name__ == "__main__":
    sys.exit(main())
