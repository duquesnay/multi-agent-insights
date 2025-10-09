#!/usr/bin/env python3
"""
Centralized metrics extraction service.

Provides single source of truth for token metrics extraction and calculation.
Replaces duplicated logic across multiple scripts with consistent field naming.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Pricing Anthropic (Claude 3.5 Sonnet)
# Source: https://www.anthropic.com/pricing
PRICING_PER_1M = {
    'input_tokens': 3.00,       # $3 per 1M input tokens
    'output_tokens': 15.00,     # $15 per 1M output tokens
    'cache_write': 3.75,        # $3.75 per 1M tokens cache write
    'cache_read': 0.30          # $0.30 per 1M tokens cache read
}


def extract_delegation_metrics(delegation: Dict) -> Dict[str, Any]:
    """
    Extract all metrics from a delegation object.

    Handles both raw delegation format (from delegation_raw.jsonl)
    and enriched format (from sessions data).

    Args:
        delegation: Delegation object from any source

    Returns:
        Standardized metrics dictionary with fields:
        - agent_type: str or None
        - input_tokens: int
        - output_tokens: int
        - cache_read_tokens: int
        - cache_write_tokens: int
        - total_tokens: int
        - amplification_ratio: float
        - cache_hit_rate: float
        - cost_usd: float
        - timestamp: str or None
    """
    metrics = {
        'agent_type': None,
        'input_tokens': 0,
        'output_tokens': 0,
        'cache_read_tokens': 0,
        'cache_write_tokens': 0,
        'total_tokens': 0,
        'amplification_ratio': 0.0,
        'cache_hit_rate': 0.0,
        'cost_usd': 0.0,
        'timestamp': None
    }

    # Extract agent type
    # Try multiple locations where agent might be stored
    metrics['agent_type'] = (
        delegation.get('agent_type') or
        delegation.get('agent') or
        _extract_agent_from_message(delegation)
    )

    # Extract usage metrics
    # Try different possible locations
    usage = (
        delegation.get('usage') or
        delegation.get('message', {}).get('usage') or
        {}
    )

    # Also check for direct token fields (enriched format)
    metrics['input_tokens'] = (
        usage.get('input_tokens') or
        delegation.get('tokens_in') or
        delegation.get('input_tokens') or
        0
    )

    metrics['output_tokens'] = (
        usage.get('output_tokens') or
        delegation.get('tokens_out') or
        delegation.get('output_tokens') or
        0
    )

    metrics['cache_read_tokens'] = (
        usage.get('cache_read_input_tokens') or
        delegation.get('cache_read') or
        delegation.get('cache_read_tokens') or
        0
    )

    metrics['cache_write_tokens'] = (
        usage.get('cache_creation_input_tokens') or
        delegation.get('cache_write') or
        delegation.get('cache_write_tokens') or
        0
    )

    # Validate numeric values
    metrics['input_tokens'] = max(0, int(metrics['input_tokens']))
    metrics['output_tokens'] = max(0, int(metrics['output_tokens']))
    metrics['cache_read_tokens'] = max(0, int(metrics['cache_read_tokens']))
    metrics['cache_write_tokens'] = max(0, int(metrics['cache_write_tokens']))

    # Calculate derived metrics
    metrics['total_tokens'] = metrics['input_tokens'] + metrics['output_tokens']

    if metrics['input_tokens'] > 0:
        metrics['amplification_ratio'] = metrics['output_tokens'] / metrics['input_tokens']
        metrics['cache_hit_rate'] = metrics['cache_read_tokens'] / metrics['input_tokens']

    metrics['cost_usd'] = calculate_cost(metrics)

    # Extract timestamp
    metrics['timestamp'] = (
        delegation.get('timestamp') or
        delegation.get('stop') or
        None
    )

    return metrics


def _extract_agent_from_message(delegation: Dict) -> Optional[str]:
    """Extract agent type from message content structure."""
    message = delegation.get('message')
    if not message or not isinstance(message, dict):
        return None

    content = message.get('content', [])
    if not isinstance(content, list):
        return None

    for item in content:
        if isinstance(item, dict) and item.get('type') == 'tool_use':
            if item.get('name') == 'Task':
                input_data = item.get('input', {})
                agent = input_data.get('subagent_type')
                if agent:
                    return agent

    return None


def extract_session_metrics(session: Dict) -> Dict[str, Any]:
    """
    Aggregate metrics for an entire session.

    Args:
        session: Session object containing delegations list

    Returns:
        Aggregated metrics for the session:
        - session_id: str
        - delegation_count: int
        - total_input_tokens: int
        - total_output_tokens: int
        - total_cache_read_tokens: int
        - total_cache_write_tokens: int
        - total_tokens: int
        - total_cost_usd: float
        - avg_amplification_ratio: float
        - avg_cache_hit_rate: float
        - agents_used: List[str]
        - agent_counts: Dict[str, int]
    """
    delegations = session.get('delegations', [])

    if not delegations:
        return {
            'session_id': session.get('session_id'),
            'delegation_count': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_cache_read_tokens': 0,
            'total_cache_write_tokens': 0,
            'total_tokens': 0,
            'total_cost_usd': 0.0,
            'avg_amplification_ratio': 0.0,
            'avg_cache_hit_rate': 0.0,
            'agents_used': [],
            'agent_counts': {}
        }

    # Extract metrics for all delegations
    delegation_metrics = [extract_delegation_metrics(d) for d in delegations]

    # Aggregate totals
    total_input = sum(m['input_tokens'] for m in delegation_metrics)
    total_output = sum(m['output_tokens'] for m in delegation_metrics)
    total_cache_read = sum(m['cache_read_tokens'] for m in delegation_metrics)
    total_cache_write = sum(m['cache_write_tokens'] for m in delegation_metrics)
    total_cost = sum(m['cost_usd'] for m in delegation_metrics)

    # Calculate averages for non-zero values
    amplification_ratios = [m['amplification_ratio'] for m in delegation_metrics
                            if m['amplification_ratio'] > 0]
    cache_hit_rates = [m['cache_hit_rate'] for m in delegation_metrics
                       if m['cache_hit_rate'] > 0]

    avg_amplification = (
        sum(amplification_ratios) / len(amplification_ratios)
        if amplification_ratios else 0.0
    )

    avg_cache_hit_rate = (
        sum(cache_hit_rates) / len(cache_hit_rates)
        if cache_hit_rates else 0.0
    )

    # Count agent usage
    agent_counts = {}
    for m in delegation_metrics:
        agent = m['agent_type']
        if agent:
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

    return {
        'session_id': session.get('session_id'),
        'delegation_count': len(delegations),
        'total_input_tokens': total_input,
        'total_output_tokens': total_output,
        'total_cache_read_tokens': total_cache_read,
        'total_cache_write_tokens': total_cache_write,
        'total_tokens': total_input + total_output,
        'total_cost_usd': total_cost,
        'avg_amplification_ratio': avg_amplification,
        'avg_cache_hit_rate': avg_cache_hit_rate,
        'agents_used': sorted(agent_counts.keys()),
        'agent_counts': agent_counts
    }


def calculate_token_totals(delegations: List[Dict]) -> Dict[str, Any]:
    """
    Calculate total token metrics across multiple delegations.

    Args:
        delegations: List of delegation objects

    Returns:
        Total metrics:
        - total_delegations: int
        - total_input_tokens: int
        - total_output_tokens: int
        - total_cache_read_tokens: int
        - total_cache_write_tokens: int
        - total_tokens: int
        - total_cost_usd: float
        - global_amplification_ratio: float
        - global_cache_efficiency: float
    """
    if not delegations:
        return {
            'total_delegations': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_cache_read_tokens': 0,
            'total_cache_write_tokens': 0,
            'total_tokens': 0,
            'total_cost_usd': 0.0,
            'global_amplification_ratio': 0.0,
            'global_cache_efficiency': 0.0
        }

    # Extract metrics for all delegations
    delegation_metrics = [extract_delegation_metrics(d) for d in delegations]

    # Calculate totals
    total_input = sum(m['input_tokens'] for m in delegation_metrics)
    total_output = sum(m['output_tokens'] for m in delegation_metrics)
    total_cache_read = sum(m['cache_read_tokens'] for m in delegation_metrics)
    total_cache_write = sum(m['cache_write_tokens'] for m in delegation_metrics)
    total_cost = sum(m['cost_usd'] for m in delegation_metrics)

    # Calculate global ratios
    global_amplification = total_output / total_input if total_input > 0 else 0.0
    global_cache_efficiency = total_cache_read / total_input if total_input > 0 else 0.0

    return {
        'total_delegations': len(delegations),
        'total_input_tokens': total_input,
        'total_output_tokens': total_output,
        'total_cache_read_tokens': total_cache_read,
        'total_cache_write_tokens': total_cache_write,
        'total_tokens': total_input + total_output,
        'total_cost_usd': total_cost,
        'global_amplification_ratio': global_amplification,
        'global_cache_efficiency': global_cache_efficiency
    }


def calculate_cost(metrics: Dict[str, int]) -> float:
    """
    Calculate cost in USD based on Anthropic pricing.

    Args:
        metrics: Dictionary with token counts (input_tokens, output_tokens, etc.)

    Returns:
        Cost in USD
    """
    cost = 0.0

    input_tokens = metrics.get('input_tokens', 0)
    output_tokens = metrics.get('output_tokens', 0)
    cache_read = metrics.get('cache_read_tokens', 0)
    cache_write = metrics.get('cache_write_tokens', 0)

    cost += input_tokens * PRICING_PER_1M['input_tokens'] / 1_000_000
    cost += output_tokens * PRICING_PER_1M['output_tokens'] / 1_000_000
    cost += cache_read * PRICING_PER_1M['cache_read'] / 1_000_000
    cost += cache_write * PRICING_PER_1M['cache_write'] / 1_000_000

    return cost


def validate_metrics(metrics: Dict[str, Any], context: str = "") -> bool:
    """
    Validate that metrics are within expected ranges.

    Args:
        metrics: Metrics dictionary to validate
        context: Optional context string for error messages

    Returns:
        True if valid, False otherwise (logs warnings)
    """
    valid = True
    prefix = f"[{context}] " if context else ""

    # Check for required numeric fields
    required_numeric = [
        'input_tokens', 'output_tokens',
        'cache_read_tokens', 'cache_write_tokens'
    ]

    for field in required_numeric:
        value = metrics.get(field)
        if value is None:
            logger.warning(f"{prefix}Missing required field: {field}")
            valid = False
        elif not isinstance(value, (int, float)):
            logger.warning(f"{prefix}Invalid type for {field}: {type(value)}")
            valid = False
        elif value < 0:
            logger.warning(f"{prefix}Negative value for {field}: {value}")
            valid = False

    # Check ratios are within reasonable bounds
    amp_ratio = metrics.get('amplification_ratio', 0)
    if amp_ratio < 0 or amp_ratio > 1000:
        logger.warning(f"{prefix}Unusual amplification ratio: {amp_ratio}")

    cache_hit = metrics.get('cache_hit_rate', 0)
    if cache_hit < 0 or cache_hit > 1:
        logger.warning(f"{prefix}Invalid cache hit rate: {cache_hit}")

    return valid


# Metric definitions for documentation
METRIC_DEFINITIONS = {
    'input_tokens': 'Number of tokens sent to the model (prompt)',
    'output_tokens': 'Number of tokens generated by the model (response)',
    'cache_read_tokens': 'Number of cached tokens read (cost savings)',
    'cache_write_tokens': 'Number of tokens written to cache',
    'total_tokens': 'Sum of input and output tokens',
    'amplification_ratio': 'Ratio of output to input tokens (output/input)',
    'cache_hit_rate': 'Ratio of cache reads to input tokens (cache_read/input)',
    'cost_usd': 'Cost in USD based on Anthropic pricing',
}
