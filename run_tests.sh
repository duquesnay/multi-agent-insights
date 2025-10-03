#!/bin/bash
# Test runner script for delegation-retrospective

set -e  # Exit on error

echo "=== Delegation Retrospective Test Suite ==="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "ERROR: pytest not found. Installing test dependencies..."
    pip install -r requirements-test.txt
fi

# Run tests with different configurations based on arguments

case "${1:-all}" in
    unit)
        echo "Running unit tests only..."
        pytest tests/ -m unit -v
        ;;
    integration)
        echo "Running integration tests only..."
        pytest tests/ -m integration -v
        ;;
    fast)
        echo "Running fast tests (excluding slow)..."
        pytest tests/ -m "not slow" -v
        ;;
    coverage)
        echo "Running tests with coverage report..."
        pytest tests/ -v --cov-report=term --cov-report=html
        echo ""
        echo "Coverage report generated in htmlcov/index.html"
        ;;
    all)
        echo "Running all tests..."
        pytest tests/ -v
        ;;
    *)
        echo "Usage: ./run_tests.sh [unit|integration|fast|coverage|all]"
        exit 1
        ;;
esac

echo ""
echo "✅ Test run complete!"
