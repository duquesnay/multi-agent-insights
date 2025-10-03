#!/usr/bin/env python3
"""
Classify delegation failures with taxonomy (not just boolean).

Taxonomy (from methodology):
- USER_TOOL_INTERVENTION: User interrupted/stopped agent
- AGENT_NOT_FOUND: Configuration issue
- TIMEOUT: Resource/complexity issue
- EXECUTION_ERROR: Code/environment problem
- CASCADE_LOOP: Agent keeps delegating to same agent
- OTHER: Unclassified failure
"""
import json
import re
from pathlib import Path

def classify_failure(delegation, session_delegations):
    """Classify failure type based on result content and context."""
    if delegation.get('success', True):
        return None  # Not a failure

    result_text = delegation.get('result_full', '').lower()

    # USER_TOOL_INTERVENTION
    if any(keyword in result_text for keyword in [
        'user interrupted',
        'user stopped',
        'user cancelled',
        'user requested'
    ]):
        return 'USER_TOOL_INTERVENTION'

    # AGENT_NOT_FOUND
    if any(keyword in result_text for keyword in [
        'agent not found',
        'unknown agent',
        'invalid agent',
        'subagent_type'
    ]):
        return 'AGENT_NOT_FOUND'

    # TIMEOUT
    if any(keyword in result_text for keyword in [
        'timeout',
        'timed out',
        'time limit',
        'took too long'
    ]):
        return 'TIMEOUT'

    # EXECUTION_ERROR
    if any(keyword in result_text for keyword in [
        'error',
        'exception',
        'failed to',
        'could not',
        'unable to'
    ]):
        return 'EXECUTION_ERROR'

    # CASCADE_LOOP detection
    # Agent delegates to itself or same agent repeatedly
    agent_type = delegation.get('agent_type')
    seq_num = delegation.get('sequence_number', 0)

    # Check if previous 2-3 delegations were same agent
    cascade_count = 0
    for i in range(max(0, seq_num - 4), seq_num - 1):
        if i < len(session_delegations):
            if session_delegations[i].get('agent_type') == agent_type:
                cascade_count += 1

    if cascade_count >= 2:
        return 'CASCADE_LOOP'

    # OTHER
    return 'OTHER'

def main():
    complete_path = Path(__file__).parent / "enriched_sessions_v8_complete.json"

    print("Loading complete dataset...")
    with open(complete_path) as f:
        data = json.load(f)

    print(f"Sessions: {len(data['sessions'])}")
    print(f"Delegations: {data['total_delegations_extracted']}")

    # Classify all failures
    failure_taxonomy = {}
    total_failures = 0
    classified_delegations = []

    for session in data['sessions']:
        session_delegations = session.get('delegations', [])

        for delegation in session_delegations:
            # Classify if failure
            if not delegation.get('success', True):
                total_failures += 1
                failure_type = classify_failure(delegation, session_delegations)
                delegation['failure_type'] = failure_type

                # Count
                failure_taxonomy[failure_type] = failure_taxonomy.get(failure_type, 0) + 1
            else:
                delegation['failure_type'] = None

            classified_delegations.append(delegation)

    # Update dataset with failure classifications
    data['failure_taxonomy'] = {
        'total_failures': total_failures,
        'classifications': failure_taxonomy,
        'taxonomy_definitions': {
            'USER_TOOL_INTERVENTION': 'User interrupted/stopped agent (ambiguous - intentional?)',
            'AGENT_NOT_FOUND': 'Configuration issue - invalid agent type',
            'TIMEOUT': 'Resource/complexity - task took too long',
            'EXECUTION_ERROR': 'Code/environment problem',
            'CASCADE_LOOP': 'Agent kept delegating to same agent type',
            'OTHER': 'Unclassified failure'
        }
    }

    # Save updated dataset
    output_path = Path(__file__).parent / "enriched_sessions_v8_complete_classified.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n=== FAILURE CLASSIFICATION COMPLETE ===")
    print(f"Total failures: {total_failures} ({total_failures/data['total_delegations_extracted']*100:.1f}%)")
    print(f"\nTaxonomy breakdown:")
    for failure_type, count in sorted(failure_taxonomy.items(), key=lambda x: -x[1]):
        pct = count / total_failures * 100 if total_failures > 0 else 0
        print(f"  {failure_type}: {count} ({pct:.1f}%)")

    print(f"\nOutput: {output_path}")

if __name__ == "__main__":
    main()