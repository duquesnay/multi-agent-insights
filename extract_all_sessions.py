#!/usr/bin/env python3
"""
Extract ALL sessions from ALL Claude projects.
Match with the 1246 delegations from agent_calls_metadata.csv
"""
import json
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from common.config import AGENT_CALLS_CSV, SESSIONS_DATA_FILE, PROJECTS_DIR, get_runtime_config

def load_known_delegations():
    """Load the 1246 delegations we know about."""
    delegations = {}
    csv_path = AGENT_CALLS_CSV
    
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            session_id = row['session_id']
            if session_id not in delegations:
                delegations[session_id] = []
            delegations[session_id].append(row)
    
    return delegations

def extract_all_sessions():
    """Scan ALL project directories for session files.

    Filters by runtime config (project path and date range if specified).
    """
    projects_dir = Path.home() / ".claude/projects"
    runtime_config = get_runtime_config()
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

                        # Apply project filter
                        project_path = msg.get("cwd", "")
                        if not runtime_config.matches_project(project_path):
                            continue

                        # Apply date filter
                        timestamp = msg.get("timestamp", "")
                        if timestamp and not runtime_config.matches_date_range(timestamp):
                            continue

                        if session_id:
                            if session_id not in all_sessions:
                                all_sessions[session_id] = []
                            all_sessions[session_id].append(msg)
                    except json.JSONDecodeError:
                        continue

    return all_sessions

def analyze_delegation_chain(messages):
    """Extract delegation metrics from message chain."""
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
                    "tokens_in": usage.get("input_tokens", 0),
                    "tokens_out": usage.get("output_tokens", 0),
                    "cache_read": usage.get("cache_read_input_tokens", 0),
                    "tool_use_id": item.get("id"),
                }
                
                # Find result - search entire remaining session (agent delegations can take 100+ messages)
                for j in range(i+1, len(messages)):
                    next_msg = messages[j]
                    if next_msg.get("type") == "user":
                        user_content = next_msg.get("message", {}).get("content", [])
                        if isinstance(user_content, list):
                            for res in user_content:
                                if (res.get("type") == "tool_result" and
                                    res.get("tool_use_id") == delegation["tool_use_id"]):
                                    delegation["success"] = not res.get("is_error", False)
                                    delegation["result_preview"] = str(res.get("content", ""))[:500]
                                    break
                        # If we found the result, stop searching
                        if "success" in delegation:
                            break
                
                delegations.append(delegation)
    
    return delegations

def main():
    runtime_config = get_runtime_config()

    # If we have project/date filters, extract sessions directly without CSV matching
    # Otherwise, use the CSV-based matching (backward compatible)
    if runtime_config.project_filter or runtime_config.start_date or runtime_config.end_date:
        print("Scanning Claude projects with filters...", flush=True)
        all_sessions = extract_all_sessions()
        print(f"Found {len(all_sessions)} sessions matching filters", flush=True)

        # Analyze all filtered sessions
        matched_sessions = []
        total_delegations = 0

        for session_id, messages in all_sessions.items():
            messages_sorted = sorted(messages, key=lambda x: x.get("timestamp", ""))
            delegations = analyze_delegation_chain(messages_sorted)

            if delegations:  # Only include sessions with delegations
                matched_sessions.append({
                    "session_id": session_id,
                    "message_count": len(messages_sorted),
                    "delegation_count": len(delegations),
                    "delegations": delegations
                })
                total_delegations += len(delegations)

        output = {
            "extraction_date": datetime.now().isoformat(),
            "total_sessions_scanned": len(all_sessions),
            "matched_sessions": len(matched_sessions),
            "total_delegations_extracted": total_delegations,
            "sessions": matched_sessions
        }

        with open(SESSIONS_DATA_FILE, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n=== EXTRACTION COMPLETE ===", flush=True)
        print(f"Sessions with delegations: {len(matched_sessions)}", flush=True)
        print(f"Delegations extracted: {total_delegations}", flush=True)
        print(f"Output: {SESSIONS_DATA_FILE}", flush=True)

    else:
        # Original CSV-based matching (backward compatible)
        print("Loading known delegations...", flush=True)
        known_delegations = load_known_delegations()
        print(f"Found {len(known_delegations)} sessions with delegations", flush=True)

        print("Scanning all Claude projects...", flush=True)
        all_sessions = extract_all_sessions()
        print(f"Found {len(all_sessions)} total sessions", flush=True)

        # Match and analyze
        matched_sessions = []
        total_delegations = 0

        for session_id in known_delegations.keys():
            if session_id in all_sessions:
                messages = sorted(all_sessions[session_id], key=lambda x: x.get("timestamp", ""))
                delegations = analyze_delegation_chain(messages)

                matched_sessions.append({
                    "session_id": session_id,
                    "message_count": len(messages),
                    "delegation_count": len(delegations),
                    "delegations": delegations
                })
                total_delegations += len(delegations)

        output = {
            "extraction_date": datetime.now().isoformat(),
            "total_sessions_scanned": len(all_sessions),
            "matched_sessions": len(matched_sessions),
            "total_delegations_extracted": total_delegations,
            "sessions": matched_sessions
        }

        with open(SESSIONS_DATA_FILE, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n=== EXTRACTION COMPLETE ===", flush=True)
        print(f"Sessions matched: {len(matched_sessions)}", flush=True)
        print(f"Delegations extracted: {total_delegations}", flush=True)
        print(f"Output: {SESSIONS_DATA_FILE}", flush=True)

if __name__ == "__main__":
    main()
