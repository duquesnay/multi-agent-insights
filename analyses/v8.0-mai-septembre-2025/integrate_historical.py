#!/usr/bin/env python3
"""
Integrate historical P0 data (mai-juillet) with v8 extraction.
"""
import json
from pathlib import Path

def main():
    # Paths
    base_dir = Path(__file__).parent.parent.parent
    historical_dir = base_dir / "data" / "historical"
    v8_path = Path(__file__).parent / "enriched_sessions_v8.json"
    output_path = Path(__file__).parent / "enriched_sessions_v8_complete.json"

    print("Loading v8 extraction (septembre)...")
    with open(v8_path) as f:
        v8_data = json.load(f)

    print(f"  Sept sessions: {len(v8_data['sessions'])}")
    print(f"  Sept delegations: {v8_data['total_delegations_extracted']}")

    # Load historical data (P0 baseline)
    print("\nLoading historical data (P0: mai-juillet)...")
    historical_sessions = []
    total_p0_delegations = 0

    for period in ['mai', 'juin', 'juillet']:
        file_path = historical_dir / f"{period}_delegations.json"
        if not file_path.exists():
            print(f"  Warning: {file_path} not found")
            continue

        with open(file_path) as f:
            period_data = json.load(f)

        # Period data is dict with 'sessions' key
        sessions_list = period_data.get('sessions', [])

        for session in sessions_list:
            # Mark as P0 baseline
            session['period'] = 'P0'

            # Count delegations
            if isinstance(session.get('delegations'), list):
                total_p0_delegations += len(session['delegations'])

            # No marathon classification for P0 (mono-agent era)
            session['marathon'] = None

            historical_sessions.append(session)

        print(f"  {period.capitalize()}: {len(sessions_list)} sessions")

    print(f"\n  Total P0: {len(historical_sessions)} sessions, {total_p0_delegations} delegations")

    # Merge data
    print("\nMerging datasets...")
    combined_sessions = historical_sessions + v8_data['sessions']
    total_delegations = total_p0_delegations + v8_data['total_delegations_extracted']

    # Update period distribution
    period_dist = {'P0': len(historical_sessions)}
    period_dist.update(v8_data['period_distribution'])

    # Create complete dataset
    complete_data = {
        **v8_data,
        "extraction_version": "v8.0_complete",
        "period": "mai-septembre-2025-complete",
        "includes_historical": True,
        "matched_sessions": len(combined_sessions),
        "total_delegations_extracted": total_delegations,
        "period_distribution": period_dist,
        "sessions": combined_sessions
    }

    # Save
    with open(output_path, 'w') as f:
        json.dump(complete_data, f, indent=2)

    print(f"\n=== INTEGRATION COMPLETE ===")
    print(f"Total sessions: {len(combined_sessions)}")
    print(f"Total delegations: {total_delegations}")
    print(f"Period distribution:")
    for period, count in sorted(period_dist.items()):
        print(f"  {period}: {count} sessions")
    print(f"\nOutput: {output_path}")

if __name__ == "__main__":
    main()