"""Pytest configuration and shared fixtures.

Provides reusable test fixtures for all test modules.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


# =============================================================================
# Session-level fixtures (created once per test session)
# =============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Real data directory path."""
    return DATA_DIR


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Test data directory (for fixtures)."""
    TEST_DATA_DIR.mkdir(exist_ok=True)
    return TEST_DATA_DIR


# =============================================================================
# Integration test fixtures (use real data)
# =============================================================================

@pytest.fixture(scope="session")
def enriched_sessions_file(data_dir: Path) -> Path:
    """Path to real enriched sessions data file."""
    file_path = data_dir / "enriched_sessions_data.json"
    if not file_path.exists():
        pytest.skip(f"Enriched sessions file not found: {file_path}")
    return file_path


@pytest.fixture(scope="session")
def enriched_sessions_data(enriched_sessions_file: Path) -> Dict[str, Any]:
    """Load real enriched sessions data (cached for session)."""
    with open(enriched_sessions_file, 'r') as f:
        return json.load(f)


@pytest.fixture(scope="session")
def sample_session(enriched_sessions_data: Dict) -> Dict:
    """Get first session from real data for testing."""
    sessions = enriched_sessions_data.get('sessions', [])
    if not sessions:
        pytest.skip("No sessions found in enriched data")
    return sessions[0]


@pytest.fixture(scope="session")
def sample_delegation(sample_session: Dict) -> Dict:
    """Get first delegation from sample session."""
    delegations = sample_session.get('delegations', [])
    if not delegations:
        pytest.skip("No delegations found in sample session")
    return delegations[0]


# =============================================================================
# Unit test fixtures (synthetic data)
# =============================================================================

@pytest.fixture
def minimal_delegation() -> Dict[str, Any]:
    """Minimal valid delegation data for unit tests."""
    return {
        'tool_use_id': 'test-uuid-001',
        'timestamp': '2025-09-15T10:30:00Z',
        'session_id': 'test-session-001',
        'agent_type': 'developer',
        'description': 'Test delegation',
        'tokens_in': 1000,
        'tokens_out': 500,
        'cache_read': 0,
        'cwd': '/test/path'
    }


@pytest.fixture
def complete_delegation() -> Dict[str, Any]:
    """Complete delegation with all optional fields."""
    return {
        'tool_use_id': 'test-uuid-002',
        'timestamp': '2025-09-15T11:00:00Z',
        'session_id': 'test-session-001',
        'agent_type': 'solution-architect',
        'description': 'Design system architecture',
        'prompt': 'Design a scalable system',
        'tokens_in': 2000,
        'tokens_out': 1500,
        'cache_read': 10000,
        'success': True,
        'cwd': '/test/path',
        'prompt_length': 100
    }


@pytest.fixture
def minimal_session() -> Dict[str, Any]:
    """Minimal valid session data."""
    return {
        'session_id': 'test-session-001',
        'delegations': [],
        'message_count': 10,
        'delegation_count': 0
    }


@pytest.fixture
def session_with_delegations(minimal_delegation: Dict) -> Dict[str, Any]:
    """Session containing multiple delegations."""
    return {
        'session_id': 'test-session-002',
        'message_count': 50,
        'delegation_count': 3,
        'delegations': [
            {**minimal_delegation, 'tool_use_id': f'deleg-{i}', 'timestamp': f'2025-09-15T10:{30+i}:00Z'}
            for i in range(3)
        ]
    }


@pytest.fixture
def marathon_session(minimal_delegation: Dict) -> Dict[str, Any]:
    """Marathon session (>20 delegations)."""
    return {
        'session_id': 'test-marathon-001',
        'message_count': 200,
        'delegation_count': 25,
        'delegations': [
            {**minimal_delegation, 'tool_use_id': f'deleg-{i}', 'timestamp': f'2025-09-15T{10+i//10}:{i%60:02d}:00Z'}
            for i in range(25)
        ]
    }


@pytest.fixture
def period_definition() -> Dict[str, Any]:
    """Valid period definition."""
    return {
        'period_id': 'P3',
        'name': 'Test Period',
        'start': '2025-09-12',
        'end': '2025-09-20',
        'changes': ['Mandatory delegation policy', '+content-developer'],
        'description': 'Test period for validation'
    }


@pytest.fixture
def period_definitions() -> Dict[str, Dict]:
    """Multiple period definitions."""
    return {
        'P2': {
            'name': 'Conception Added',
            'start': '2025-09-03',
            'end': '2025-09-11',
            'changes': ['+solution-architect', '+project-framer'],
            'description': 'Added planning capabilities'
        },
        'P3': {
            'name': 'Délégation Obligatoire',
            'start': '2025-09-12',
            'end': '2025-09-20',
            'changes': ['Mandatory delegation', '+content-developer'],
            'description': 'Delegation enforcement period'
        },
        'P4': {
            'name': 'Post-Restructuration',
            'start': '2025-09-21',
            'end': '2025-09-30',
            'changes': ['senior-developer split', 'safeguards active'],
            'description': 'Post-restructuring optimization'
        }
    }


# =============================================================================
# Helper fixtures
# =============================================================================

@pytest.fixture
def invalid_delegation_data() -> List[Dict]:
    """Collection of invalid delegation data for validation tests."""
    return [
        {},  # Empty
        {'tool_use_id': 'test-001'},  # Missing required fields
        {'timestamp': 'invalid-date'},  # Invalid date format
        {'tokens_in': -1},  # Negative tokens
        {'agent_type': ''},  # Empty agent type
    ]


@pytest.fixture
def create_temp_json_file(test_data_dir: Path):
    """Factory fixture to create temporary JSON files for testing."""
    def _create(filename: str, data: Any) -> Path:
        file_path = test_data_dir / filename
        with open(file_path, 'w') as f:
            json.dump(data, f)
        return file_path
    return _create
