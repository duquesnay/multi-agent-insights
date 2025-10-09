"""
Data Repository Pattern for Delegation Retrospective Analysis

Provides centralized, validated data loading for all analysis scripts.
Eliminates 40+ duplicate implementations with inconsistent error handling.

Usage:
    from common.data_repository import load_delegations, load_sessions
    
    delegations = load_delegations()
    sessions = load_sessions()
"""

import json
import csv
import ijson
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Iterator, Union
from datetime import datetime

# Conditional import for typed models
try:
    from common.models import Delegation, Session, AgentCall
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False


class DataLoadError(Exception):
    """Raised when data loading fails due to missing files or invalid data."""
    pass


class DataRepository:
    """Centralized data access layer with caching and validation."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize repository with base path.
        
        Args:
            base_path: Root directory for data files. Defaults to script location.
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent
        self.base_path = Path(base_path)
        
        # Cache for loaded data
        self._cache: Dict[str, Any] = {}
        
        # Data file paths
        self.paths = {
            'delegations_jsonl': self.base_path / 'data' / 'raw' / 'delegation_raw.jsonl',
            'enriched_sessions': self.base_path / 'data' / 'enriched_sessions_data.json',
            'full_sessions': self.base_path / 'data' / 'full_sessions_data.json',
            'routing_analysis': self.base_path / 'data' / 'routing_quality_analysis.json',
            'routing_patterns': self.base_path / 'data' / 'routing_patterns_by_period.json',
            'good_patterns': self.base_path / 'data' / 'good_routing_patterns.json',
            'agent_calls_csv': self.base_path / 'data' / 'raw' / 'agent_calls_metadata.csv',
        }
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if available."""
        return self._cache.get(key)
    
    def _set_cached(self, key: str, data: Any) -> None:
        """Cache loaded data."""
        self._cache[key] = data
    
    def load_delegations(
        self,
        source: str = 'enriched',
        use_cache: bool = True,
        typed: bool = False
    ) -> Union[List[Dict], List['Delegation']]:
        """
        Load delegation data from enriched sessions JSON (recommended)
        or raw JSONL file.

        Args:
            source: 'enriched' (default) or 'raw'
            use_cache: Whether to use cached data if available
            typed: If True, return typed Delegation objects instead of dicts

        Returns:
            List of delegation dictionaries (typed=False) or Delegation objects (typed=True)

        Raises:
            DataLoadError: If file not found or invalid JSON
            RuntimeError: If typed=True but models not available

        Example:
            >>> # Untyped (backward compatible)
            >>> delegations = load_delegations()
            >>> len(delegations)
            1315
            >>> delegations[0]['agent_type']
            'documentation-writer'

            >>> # Typed (new)
            >>> delegations = load_delegations(typed=True)
            >>> delegations[0].agent_type
            'documentation-writer'
        """
        if typed and not MODELS_AVAILABLE:
            raise RuntimeError("Typed mode requires common.models module")

        cache_key = f'delegations_{source}_{"typed" if typed else "dict"}'

        if use_cache and (cached := self._get_cached(cache_key)):
            return cached

        if source == 'enriched':
            data = self._load_enriched_delegations()
        elif source == 'raw':
            data = self._load_raw_delegations()
        else:
            raise ValueError(f"Unknown source: {source}. Use 'enriched' or 'raw'")

        # Convert to typed objects if requested
        if typed:
            data = [Delegation.from_dict(d) for d in data]

        self._set_cached(cache_key, data)
        return data
    
    def _load_enriched_delegations(self) -> List[Dict]:
        """Load delegations from enriched sessions JSON."""
        file_path = self.paths['enriched_sessions']
        
        if not file_path.exists():
            raise DataLoadError(
                f"Enriched sessions file not found: {file_path}\n"
                f"Expected location: {file_path}\n"
                f"Run data extraction pipeline first."
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Invalid JSON in {file_path}: {e}")
        
        # Validate structure
        if 'sessions' not in data:
            raise DataLoadError(
                f"Invalid enriched sessions format: missing 'sessions' key\n"
                f"File: {file_path}"
            )
        
        # Extract all delegations from sessions
        delegations = []
        for session in data['sessions']:
            session_id = session.get('session_id', 'unknown')
            for delegation in session.get('delegations', []):
                # Enrich with session context
                delegation['session_id'] = session_id
                delegation['session_message_count'] = session.get('message_count', 0)
                delegations.append(delegation)
        
        return delegations
    
    def _load_raw_delegations(self) -> List[Dict]:
        """Load delegations from raw JSONL file."""
        file_path = self.paths['delegations_jsonl']
        
        if not file_path.exists():
            raise DataLoadError(
                f"Raw delegations file not found: {file_path}\n"
                f"Expected location: {file_path}"
            )
        
        delegations = []
        line_num = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line_num += 1
                    if not line.strip():
                        continue
                    
                    try:
                        delegation = json.loads(line.strip())
                        delegations.append(delegation)
                    except json.JSONDecodeError as e:
                        # Log warning but continue
                        print(f"Warning: Skipping invalid JSON at line {line_num}: {e}")
                        continue
        except Exception as e:
            raise DataLoadError(f"Error reading {file_path}: {e}")
        
        if not delegations:
            raise DataLoadError(f"No valid delegations found in {file_path}")
        
        return delegations
    
    def load_sessions(
        self,
        enriched: bool = True,
        use_cache: bool = True,
        typed: bool = False
    ) -> Union[List[Dict], List['Session']]:
        """
        Load session data with delegation metadata.

        Args:
            enriched: Use enriched sessions (True) or full sessions (False)
            use_cache: Whether to use cached data
            typed: If True, return typed Session objects instead of dicts

        Returns:
            List of session dictionaries (typed=False) or Session objects (typed=True)

        Raises:
            DataLoadError: If file not found or invalid
            RuntimeError: If typed=True but models not available
        """
        if typed and not MODELS_AVAILABLE:
            raise RuntimeError("Typed mode requires common.models module")

        cache_key = f'sessions_{"enriched" if enriched else "full"}_{"typed" if typed else "dict"}'

        if use_cache and (cached := self._get_cached(cache_key)):
            return cached

        file_path = self.paths['enriched_sessions' if enriched else 'full_sessions']

        if not file_path.exists():
            raise DataLoadError(
                f"Sessions file not found: {file_path}\n"
                f"Run session extraction pipeline first."
            )

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Invalid JSON in {file_path}: {e}")

        sessions = data.get('sessions', [])

        if not sessions:
            raise DataLoadError(f"No sessions found in {file_path}")

        # Convert to typed objects if requested
        if typed:
            sessions = [Session.from_dict(s) for s in sessions]

        self._set_cached(cache_key, sessions)
        return sessions
    
    def load_routing_patterns(
        self,
        pattern_type: str = 'by_period',
        use_cache: bool = True
    ) -> Dict:
        """
        Load routing pattern analysis data.
        
        Args:
            pattern_type: 'by_period', 'quality', or 'good'
            use_cache: Whether to use cached data
            
        Returns:
            Routing patterns dictionary
            
        Raises:
            DataLoadError: If file not found
        """
        cache_key = f'routing_{pattern_type}'
        
        if use_cache and (cached := self._get_cached(cache_key)):
            return cached
        
        path_map = {
            'by_period': 'routing_patterns',
            'quality': 'routing_analysis',
            'good': 'good_patterns',
        }
        
        if pattern_type not in path_map:
            raise ValueError(
                f"Unknown pattern_type: {pattern_type}. "
                f"Use 'by_period', 'quality', or 'good'"
            )
        
        file_path = self.paths[path_map[pattern_type]]
        
        if not file_path.exists():
            raise DataLoadError(
                f"Routing patterns file not found: {file_path}\n"
                f"Run routing analysis pipeline first."
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Invalid JSON in {file_path}: {e}")
        
        self._set_cached(cache_key, data)
        return data
    
    def load_agent_calls(
        self,
        use_cache: bool = True,
        typed: bool = False
    ) -> Union[List[Dict], List['AgentCall']]:
        """
        Load agent call metadata from CSV.

        Args:
            use_cache: Whether to use cached data
            typed: If True, return typed AgentCall objects instead of dicts

        Returns:
            List of agent call dictionaries (typed=False) or AgentCall objects (typed=True)

        Raises:
            DataLoadError: If file not found or invalid CSV
            RuntimeError: If typed=True but models not available
        """
        if typed and not MODELS_AVAILABLE:
            raise RuntimeError("Typed mode requires common.models module")

        cache_key = f'agent_calls_{"typed" if typed else "dict"}'

        if use_cache and (cached := self._get_cached(cache_key)):
            return cached

        file_path = self.paths['agent_calls_csv']

        if not file_path.exists():
            raise DataLoadError(
                f"Agent calls CSV not found: {file_path}\n"
                f"Expected location: {file_path}"
            )

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        except Exception as e:
            raise DataLoadError(f"Error reading CSV {file_path}: {e}")

        if not data:
            raise DataLoadError(f"No data found in {file_path}")

        # Convert to typed objects if requested
        if typed:
            data = [AgentCall.from_dict(row) for row in data]

        self._set_cached(cache_key, data)
        return data
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()

    def stream_sessions(
        self,
        filter_func: Optional[Callable[[Dict], bool]] = None,
        enriched: bool = True
    ) -> Iterator[Dict]:
        """
        Stream sessions one at a time from large JSON file.

        Memory efficient for processing large datasets - loads one session
        at a time instead of entire file into memory.

        Args:
            filter_func: Optional function to filter sessions (session) -> bool
            enriched: Use enriched sessions (True) or full sessions (False)

        Yields:
            Session dictionaries one at a time

        Raises:
            DataLoadError: If file not found

        Example:
            >>> # Process only marathon sessions without loading all data
            >>> for session in stream_sessions(lambda s: len(s.get('delegations', [])) > 20):
            ...     analyze_marathon(session)
            ...
        Performance:
            - Memory: 5-10x reduction vs load_sessions()
            - 6.7MB file: ~20MB -> ~2-3MB peak memory
            - At 10x scale (67MB): ~200MB -> ~20-30MB peak memory
        """
        file_path = self.paths['enriched_sessions' if enriched else 'full_sessions']

        if not file_path.exists():
            raise DataLoadError(
                f"Sessions file not found: {file_path}\n"
                f"Run session extraction pipeline first."
            )

        try:
            with open(file_path, 'rb') as f:
                # Use ijson to parse sessions array incrementally
                sessions_iterator = ijson.items(f, 'sessions.item')

                for session in sessions_iterator:
                    # Apply filter early to reduce memory usage
                    if filter_func is None or filter_func(session):
                        yield session

        except Exception as e:
            raise DataLoadError(f"Error streaming from {file_path}: {e}")

    def stream_delegations(
        self,
        filter_func: Optional[Callable[[Dict], bool]] = None,
        enriched: bool = True
    ) -> Iterator[Dict]:
        """
        Stream delegations one at a time from sessions JSON.

        Even more memory efficient than stream_sessions() - yields individual
        delegations with session context.

        Args:
            filter_func: Optional function to filter delegations (delegation) -> bool
            enriched: Use enriched sessions (True) or full sessions (False)

        Yields:
            Delegation dictionaries one at a time

        Raises:
            DataLoadError: If file not found

        Example:
            >>> # Find specific delegations without loading all data
            >>> for deleg in stream_delegations(lambda d: d.get('agent_type') == 'developer'):
            ...     process_delegation(deleg)
            ...
        Performance:
            - Memory: 10-20x reduction vs load_delegations()
            - Processes 1,315 delegations with ~1-2MB peak memory
            - Scales to 100K+ delegations without memory issues
        """
        for session in self.stream_sessions(enriched=enriched):
            session_id = session.get('session_id', 'unknown')
            session_msg_count = session.get('message_count', 0)

            for delegation in session.get('delegations', []):
                # Enrich with session context
                delegation['session_id'] = session_id
                delegation['session_message_count'] = session_msg_count

                # Apply filter
                if filter_func is None or filter_func(delegation):
                    yield delegation


# Global repository instance
_repository = DataRepository()


# Convenience functions for backward compatibility
def load_delegations(
    source: str = 'enriched',
    use_cache: bool = True,
    typed: bool = False
) -> Union[List[Dict], List['Delegation']]:
    """
    Load delegation data (recommended: use enriched source).

    Args:
        source: 'enriched' (default, from sessions) or 'raw' (from JSONL)
        use_cache: Whether to use cached data
        typed: If True, return typed Delegation objects instead of dicts

    Returns:
        List of delegation dictionaries (typed=False) or Delegation objects (typed=True)
    """
    return _repository.load_delegations(source=source, use_cache=use_cache, typed=typed)


def load_sessions(
    enriched: bool = True,
    use_cache: bool = True,
    typed: bool = False
) -> Union[List[Dict], List['Session']]:
    """
    Load session data.

    Args:
        enriched: Use enriched sessions (True) or full sessions (False)
        use_cache: Whether to use cached data
        typed: If True, return typed Session objects instead of dicts

    Returns:
        List of session dictionaries (typed=False) or Session objects (typed=True)
    """
    return _repository.load_sessions(enriched=enriched, use_cache=use_cache, typed=typed)


def load_routing_patterns(pattern_type: str = 'by_period', use_cache: bool = True) -> Dict:
    """
    Load routing pattern analysis.
    
    Args:
        pattern_type: 'by_period', 'quality', or 'good'
        use_cache: Whether to use cached data
        
    Returns:
        Routing patterns dictionary
    """
    return _repository.load_routing_patterns(pattern_type=pattern_type, use_cache=use_cache)


def load_agent_calls(
    use_cache: bool = True,
    typed: bool = False
) -> Union[List[Dict], List['AgentCall']]:
    """
    Load agent call metadata from CSV.

    Args:
        use_cache: Whether to use cached data
        typed: If True, return typed AgentCall objects instead of dicts

    Returns:
        List of agent call dictionaries (typed=False) or AgentCall objects (typed=True)
    """
    return _repository.load_agent_calls(use_cache=use_cache, typed=typed)


def clear_cache() -> None:
    """Clear all cached data."""
    _repository.clear_cache()


def stream_sessions(
    filter_func: Optional[Callable[[Dict], bool]] = None,
    enriched: bool = True
) -> Iterator[Dict]:
    """
    Stream sessions one at a time from large JSON file (memory efficient).

    Args:
        filter_func: Optional function to filter sessions (session) -> bool
        enriched: Use enriched sessions (True) or full sessions (False)

    Yields:
        Session dictionaries one at a time

    Performance:
        5-10x memory reduction vs load_sessions()
    """
    return _repository.stream_sessions(filter_func=filter_func, enriched=enriched)


def stream_delegations(
    filter_func: Optional[Callable[[Dict], bool]] = None,
    enriched: bool = True
) -> Iterator[Dict]:
    """
    Stream delegations one at a time from sessions JSON (memory efficient).

    Args:
        filter_func: Optional function to filter delegations (delegation) -> bool
        enriched: Use enriched sessions (True) or full sessions (False)

    Yields:
        Delegation dictionaries one at a time

    Performance:
        10-20x memory reduction vs load_delegations()
    """
    return _repository.stream_delegations(filter_func=filter_func, enriched=enriched)
