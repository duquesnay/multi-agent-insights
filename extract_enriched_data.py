#!/usr/bin/env python3
"""
ENRICHED extraction: capture full context for LLM agent analysis.

Additions vs extract_all_sessions.py:
1. Full delegation results (not just 500 char preview)
2. User messages around delegations (context)
3. Agent→Agent sequences (chronological order)
4. Session narrative structure
"""
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

from common.config import ENRICHED_SESSIONS_FILE, PROJECTS_DIR
from common.schema_validator import SchemaValidator
from file_scan_cache import (
    is_cache_valid,
    load_sessions_cache,
    save_sessions_cache,
    get_file_metadata,
    save_metadata_cache,
    clear_cache
)

def extract_all_sessions(use_cache=True):
    """Scan ALL project directories for session files.

    Args:
        use_cache: If True, use cached data when valid (default: True)

    Returns:
        Dict mapping session_id to list of messages
    """
    projects_dir = PROJECTS_DIR

    # Try to use cache if enabled
    if use_cache and is_cache_valid(projects_dir):
        print("Using cached data (files unchanged)...", flush=True)
        cached_sessions = load_sessions_cache()
        if cached_sessions is not None:
            print(f"Loaded {len(cached_sessions)} sessions from cache", flush=True)
            return cached_sessions
        print("Cache invalid, performing full scan...", flush=True)
    elif use_cache:
        print("Cache miss, performing full scan...", flush=True)
    else:
        print("Cache disabled, performing full scan...", flush=True)

    # Perform full scan
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

    # Save to cache for next time
    if use_cache:
        print("Saving to cache...", flush=True)
        metadata = get_file_metadata(projects_dir)
        save_metadata_cache(metadata)
        save_sessions_cache(all_sessions)

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
    """Extract delegations WITH full context."""
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

def main():
    print("Scanning all Claude projects...", flush=True)
    all_sessions = extract_all_sessions()
    print(f"Found {len(all_sessions)} total sessions", flush=True)

    # Filter sessions with delegations (from September 2025)
    enriched_sessions = []
    total_delegations = 0

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

        # Check if September 2025
        first_timestamp = messages[0].get("timestamp", "")
        if not first_timestamp.startswith("2025-09"):
            continue

        delegations = analyze_enriched_session(messages)

        if delegations:
            enriched_sessions.append({
                "session_id": session_id,
                "first_timestamp": first_timestamp,
                "message_count": len(messages),
                "delegation_count": len(delegations),
                "delegations": delegations
            })
            total_delegations += len(delegations)

    # Create versioned output with schema metadata
    metadata = SchemaValidator.create_metadata(
        generator_name="extract_enriched_data.py",
        schema_type="enriched_sessions",
        additional_metadata={
            "extraction_version": "enriched_v1",
            "total_sessions_scanned": len(all_sessions),
            "matched_sessions": len(enriched_sessions),
            "total_delegations_extracted": total_delegations,
            "enrichments": [
                "Full delegation results (not truncated)",
                "User context before delegation",
                "Assistant synthesis after delegation",
                "Agent sequence information (previous/next)",
                "Sequence numbers within session"
            ]
        }
    )

    output = {
        **metadata,
        "sessions": enriched_sessions
    }

    with open(ENRICHED_SESSIONS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n=== ENRICHED EXTRACTION COMPLETE ===", flush=True)
    print(f"Sessions matched: {len(enriched_sessions)}", flush=True)
    print(f"Delegations extracted: {total_delegations}", flush=True)
    print(f"Output: {ENRICHED_SESSIONS_FILE}", flush=True)
    print(f"\nEnrichments:", flush=True)
    for e in output["enrichments"]:
        print(f"  - {e}", flush=True)

if __name__ == "__main__":
    import sys

    # Command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-cache":
            print("Cache disabled via --no-cache flag", flush=True)
            # Temporarily disable cache
            original_main = main

            def no_cache_main():
                import file_scan_cache
                # Monkey patch to disable cache
                original_extract = extract_all_sessions

                def extract_no_cache():
                    return original_extract(use_cache=False)

                globals()['extract_all_sessions'] = extract_no_cache
                original_main()

            no_cache_main()

        elif sys.argv[1] == "--clear-cache":
            print("Clearing cache...", flush=True)
            clear_cache()
            print("Cache cleared. Exiting.", flush=True)
            sys.exit(0)

        elif sys.argv[1] == "--cache-info":
            from file_scan_cache import get_cache_info
            info = get_cache_info()
            print("=== Cache Information ===", flush=True)
            for key, value in info.items():
                print(f"{key}: {value}", flush=True)
            sys.exit(0)

        else:
            print(f"Unknown option: {sys.argv[1]}", flush=True)
            print("Usage: python extract_enriched_data.py [--no-cache|--clear-cache|--cache-info]", flush=True)
            sys.exit(1)
    else:
        main()