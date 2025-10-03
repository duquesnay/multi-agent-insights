#!/usr/bin/env python3
"""
Compiled regex patterns for efficient text matching in routing analysis.

Pre-compiled patterns provide 3-5x speedup over string operations by:
- Compiling regex once at module load instead of per-check
- Using optimized C-based regex engine
- Avoiding repeated string operations on large texts

Usage:
    from common.patterns import TESTING_PATTERN, match_any

    if TESTING_PATTERN.search(text):
        # Found testing keywords

    if match_any(text, [TESTING_PATTERN, IMPLEMENTATION_PATTERN]):
        # Found any of the patterns
"""

import re

# =============================================================================
# Task Type Patterns (for developer categorization)
# =============================================================================
# Note: Using substring matching (no \b boundaries) to match original behavior
# of 'word in text' checks. This is intentionally loose to catch variations.

TESTING_PATTERN = re.compile(r'(test|pytest|unittest)', re.IGNORECASE)
IMPLEMENTATION_PATTERN = re.compile(r'(implement|create|add|build)', re.IGNORECASE)
DEBUGGING_PATTERN = re.compile(r'(debug|fix|error|issue)', re.IGNORECASE)
REFACTORING_PATTERN = re.compile(r'(refactor|restructure|reorganize)', re.IGNORECASE)
GIT_PATTERN = re.compile(r'(git|commit|branch|merge)', re.IGNORECASE)
DOCUMENTATION_PATTERN = re.compile(r'(document|readme|comment)', re.IGNORECASE)
ANALYSIS_PATTERN = re.compile(r'(analyze|review|examine|investigate)', re.IGNORECASE)

# =============================================================================
# Routing Patterns (for misrouting detection)
# =============================================================================

ARCHITECTURE_PATTERN = re.compile(
    r'(architecture|design pattern|system design|structure)',
    re.IGNORECASE
)
SIMPLE_TASK_PATTERN = re.compile(r'(simple|basic|straightforward|trivial)', re.IGNORECASE)
CONTENT_CREATION_PATTERN = re.compile(r'(write content|create documentation|write guide|tutorial)', re.IGNORECASE)
PERFORMANCE_PATTERN = re.compile(
    r'(optimize performance|slow|speed up|bottleneck)',
    re.IGNORECASE
)

# =============================================================================
# Success/Failure Indicators
# =============================================================================

PROBLEM_INDICATORS = re.compile(
    r'(fix|debug|error|fail|broken|issue|problem)',
    re.IGNORECASE
)
SUCCESS_INDICATORS = re.compile(
    r'(complete|success|finish|deploy)',
    re.IGNORECASE
)

# =============================================================================
# Complexity Indicators
# =============================================================================

MULTIPLE_STEPS_PATTERN = re.compile(
    r'(then|after|next|finally|step)',
    re.IGNORECASE
)
CODE_PATTERN = re.compile(
    r'(```|function|class)',
    re.IGNORECASE
)

# =============================================================================
# Helper Functions
# =============================================================================

def match_any(text, patterns):
    """Check if text matches any of the given patterns.

    Args:
        text: Text to search
        patterns: List of compiled regex patterns

    Returns:
        True if any pattern matches, False otherwise
    """
    return any(pattern.search(text) for pattern in patterns)


def match_all(text, patterns):
    """Check if text matches all of the given patterns.

    Args:
        text: Text to search
        patterns: List of compiled regex patterns

    Returns:
        True if all patterns match, False otherwise
    """
    return all(pattern.search(text) for pattern in patterns)


def categorize_task(text):
    """Categorize a task based on its text content.

    Args:
        text: Combined prompt and description text

    Returns:
        Category name (str) or 'other' if no match
    """
    if TESTING_PATTERN.search(text):
        return 'testing'
    elif IMPLEMENTATION_PATTERN.search(text):
        return 'implementation'
    elif DEBUGGING_PATTERN.search(text):
        return 'debugging'
    elif REFACTORING_PATTERN.search(text):
        return 'refactoring'
    elif GIT_PATTERN.search(text):
        return 'git'
    elif DOCUMENTATION_PATTERN.search(text):
        return 'documentation'
    elif ANALYSIS_PATTERN.search(text):
        return 'analysis'
    else:
        return 'other'
