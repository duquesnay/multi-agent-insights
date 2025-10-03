#!/usr/bin/env python3
"""
v8.0 ENRICHED extraction: Mai-Septembre 2025 with temporal segmentation.

Enhancements vs original:
1. Extract ALL mai-septembre (not just sept)
2. Add model_used field
3. Add temporal segmentation (git-based periods)
4. Full context + tokens (from original)
5. Prepare for marathon/failure classification
"""
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Import centralized period classification
from common.config import get_period_for_date

def classify_period(timestamp_str):
    """Classify session into period using centralized config."""
    if not timestamp_str:
        return "UNKNOWN"

    period = get_period_for_date(timestamp_str)
    return period if period else "UNKNOWN"

def extract_all_sessions():
    """Scan ALL project directories for session files."""
    # Use consolidated data directory
    project_root = Path(__file__).parent.parent.parent
    projects_dir = project_root / "data" / "conversations"
    all_sessions = {}

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        for jsonl_file in project_dir.glob("*.jsonl"):
            with open(jsonl_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        msg = json.loads(line)
                        session_id = msg.get("sessionId")
                        if session_id:
                            if session_id not in all_sessions:
                                all_sessions[session_id] = []
                            all_sessions[session_id].append(msg)
                    except json.JSONDecodeError:
                        continue

    return all_sessions

def extract_user_message_text(msg):
    """Extract user message text content."""
    content = msg.get("message", {}).get("content", [])
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if item.get("type") == "text":
                texts.append(item.get("text", ""))
        return "\n".join(texts) if texts else None
    return None

def analyze_enriched_session(messages):
    """Extract delegations WITH full context + v8.0 enhancements."""
    delegations = []

    for i, msg in enumerate(messages):
        if msg.get("type") != "assistant":
            continue

        content = msg.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue

        for item in content:
            if item.get("type") == "tool_use" and item.get("name") == "Task":
                input_data = item.get("input", {})
                usage = msg.get("message", {}).get("usage", {})

                delegation = {
                    "timestamp": msg.get("timestamp"),
                    "agent_type": input_data.get("subagent_type"),
                    "description": input_data.get("description"),
                    "prompt": input_data.get("prompt"),
                    "prompt_length": len(input_data.get("prompt", "")),

                    # Tokens data (ROI metrics)
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                    "cache_read_tokens": usage.get("cache_read_input_tokens", 0),

                    # v8.0: Add model field
                    "model_used": msg.get("message", {}).get("model"),

                    "tool_use_id": item.get("id"),
                }

                # ENRICHMENT 1: Capture user message BEFORE delegation (context)
                if i > 0:
                    prev_msg = messages[i-1]
                    if prev_msg.get("type") == "user":
                        delegation["user_context_before"] = extract_user_message_text(prev_msg)

                # ENRICHMENT 2: Find FULL result (not truncated)
                for j in range(i+1, len(messages)):
                    next_msg = messages[j]
                    if next_msg.get("type") == "user":
                        user_content = next_msg.get("message", {}).get("content", [])
                        if isinstance(user_content, list):
                            for res in user_content:
                                if (res.get("type") == "tool_result" and
                                    res.get("tool_use_id") == delegation["tool_use_id"]):
                                    delegation["success"] = not res.get("is_error", False)
                                    delegation["is_error"] = res.get("is_error", False)
                                    # FULL result, not truncated
                                    delegation["result_full"] = str(res.get("content", ""))
                                    delegation["result_preview"] = str(res.get("content", ""))[:500]
                                    break
                        if "success" in delegation:
                            break

                # ENRICHMENT 3: Capture assistant message AFTER result (synthesis)
                if "success" in delegation:
                    for k in range(i+1, len(messages)):
                        after_msg = messages[k]
                        if after_msg.get("type") == "assistant":
                            # First assistant message after result = synthesis
                            delegation["assistant_synthesis"] = extract_user_message_text(after_msg)
                            break

                delegations.append(delegation)

    # ENRICHMENT 4: Add sequence information
    for idx, deleg in enumerate(delegations):
        deleg["sequence_number"] = idx + 1
        deleg["total_in_session"] = len(delegations)
        if idx > 0:
            deleg["previous_agent"] = delegations[idx-1]["agent_type"]
        if idx < len(delegations) - 1:
            deleg["next_agent"] = delegations[idx+1]["agent_type"]

    return delegations

def classify_marathon(delegations, success_count):
    """Classify marathon session (>20 delegations)."""
    if len(delegations) <= 20:
        return None

    success_rate = (success_count / len(delegations)) * 100 if delegations else 0

    # Count cascades (consecutive same agent)
    cascades = 0
    for i in range(1, len(delegations)):
        if delegations[i]["agent_type"] == delegations[i-1]["agent_type"]:
            cascades += 1
    cascade_rate = (cascades / (len(delegations) - 1)) * 100 if len(delegations) > 1 else 0

    # Classification (from methodology)
    if success_rate >= 85:
        classification = "POSITIVE"  # Productive work
    elif success_rate < 80:
        classification = "NEGATIVE"  # Pathological
    else:
        classification = "AMBIGUOUS"  # Needs review

    return {
        "is_marathon": True,
        "classification": classification,
        "success_rate": success_rate,
        "cascade_rate": cascade_rate
    }

def main():
    print("=== v8.0 ENRICHED EXTRACTION ===", flush=True)
    print("Period: Mai-Septembre 2025", flush=True)
    print("Scanning all Claude projects...", flush=True)

    all_sessions = extract_all_sessions()
    print(f"Found {len(all_sessions)} total sessions", flush=True)

    # Filter sessions with delegations (Mai-Septembre 2025)
    enriched_sessions = []
    total_delegations = 0
    period_counts = defaultdict(int)

    for session_id, messages in all_sessions.items():
        messages = sorted(messages, key=lambda x: x.get("timestamp", ""))

        # Quick check: does this session have Task tool_use?
        has_delegations = any(
            msg.get("type") == "assistant" and
            any(
                item.get("type") == "tool_use" and item.get("name") == "Task"
                for item in msg.get("message", {}).get("content", [])
                if isinstance(msg.get("message", {}).get("content", []), list)
            )
            for msg in messages
        )

        if not has_delegations:
            continue

        # v8.0: Check if Mai-Septembre 2025 (not just September)
        first_timestamp = messages[0].get("timestamp", "")
        if not first_timestamp.startswith("2025-0"):  # 2025-05, 2025-06, ..., 2025-09
            continue

        # More precise: must be 05-09
        month = first_timestamp[5:7] if len(first_timestamp) >= 7 else ""
        if month not in ["05", "06", "07", "08", "09"]:
            continue

        delegations = analyze_enriched_session(messages)

        if delegations:
            # v8.0: Add period classification
            period = classify_period(first_timestamp)
            period_counts[period] += 1

            # Calculate success count for marathon classification
            success_count = sum(1 for d in delegations if d.get("success", False))

            # v8.0: Marathon classification
            marathon_info = classify_marathon(delegations, success_count)

            enriched_sessions.append({
                "session_id": session_id,
                "first_timestamp": first_timestamp,
                "period": period,  # v8.0: Temporal segmentation
                "message_count": len(messages),
                "delegation_count": len(delegations),
                "success_count": success_count,
                "marathon": marathon_info,  # v8.0: Marathon classification
                "delegations": delegations
            })
            total_delegations += len(delegations)

    output = {
        "extraction_date": datetime.now().isoformat(),
        "extraction_version": "v8.0_enriched",
        "period": "mai-septembre-2025",
        "total_sessions_scanned": len(all_sessions),
        "matched_sessions": len(enriched_sessions),
        "total_delegations_extracted": total_delegations,
        "period_distribution": dict(period_counts),
        "enhancements": [
            "Full delegation results (not truncated)",
            "User context before delegation",
            "Assistant synthesis after delegation",
            "Agent sequence information (previous/next)",
            "Sequence numbers within session",
            "v8.0: Tokens data (input/output/cache)",
            "v8.0: Model used field",
            "v8.0: Temporal segmentation (git-based periods)",
            "v8.0: Marathon classification (positive/negative/ambiguous)"
        ],
        "periods": {
            "P0": "Mai-Juillet 2025 (baseline pré-agents)",
            "P1": "Août 2025 (launch + vacances)",
            "P2": "Sept 3-11 (solution-architect, project-framer)",
            "P3": "Sept 12-20 (mandatory delegation)",
            "P4": "Sept 21-30 (senior/junior split)"
        },
        "sessions": enriched_sessions
    }

    output_path = Path(__file__).parent / "enriched_sessions_v8.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n=== EXTRACTION COMPLETE ===", flush=True)
    print(f"Sessions matched: {len(enriched_sessions)}", flush=True)
    print(f"Delegations extracted: {total_delegations}", flush=True)
    print(f"Period distribution:", flush=True)
    for period, count in sorted(period_counts.items()):
        print(f"  {period}: {count} sessions", flush=True)
    print(f"\nOutput: {output_path}", flush=True)

if __name__ == "__main__":
    main()