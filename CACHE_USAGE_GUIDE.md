# File Scan Cache - Usage Guide

## Quick Start

The caching system is **enabled by default** - just run your scripts normally and they'll automatically benefit from faster subsequent runs.

```bash
# First run: builds cache (4.2s)
python3 extract_enriched_data.py

# Subsequent runs: uses cache (1.6s)
python3 extract_enriched_data.py
```

---

## Commands

### Check Cache Status
```bash
python3 extract_enriched_data.py --cache-info
```

Output:
```
=== Cache Information ===
cache_exists: True
metadata_file: .../data/.cache/file_metadata.json
sessions_file: .../data/.cache/sessions_data.pkl
metadata_size_kb: 37.6
sessions_size_kb: 591204.3
cached_sessions: 265
```

### Clear Cache
```bash
python3 extract_enriched_data.py --clear-cache
```

Use when:
- You want to force a fresh scan
- Cache seems corrupted
- Testing cache performance

### Bypass Cache
```bash
python3 extract_enriched_data.py --no-cache
```

Use when:
- You want to verify results without cache
- Debugging data issues
- Benchmarking scan performance

---

## How It Works

### Cache Creation
1. First run scans all 334 files normally
2. Stores file modification times + parsed data
3. Saves to `.cache/` directory

### Cache Validation
On each run:
1. Checks if all files have same modification time
2. If yes → loads from cache (fast!)
3. If no → rescans changed files

### Cache Invalidation

Cache automatically rebuilds when:
- **File modified**: Any .jsonl file changes
- **File added**: New session files appear
- **File deleted**: Session files removed

This ensures data is always current.

---

## Performance Expectations

| Scenario | Time | Notes |
|----------|------|-------|
| First run (cold cache) | 4.2s | Includes cache write overhead |
| Warm cache | 1.6s | No files changed |
| Files changed | 4.2s | Automatic rebuild |

**Speedup**: 2.6x faster when cache is valid

---

## Cache Files Location

```
data/
└── .cache/
    ├── file_metadata.json          (38 KB)
    ├── sessions_data.pkl           (577 MB)
    ├── benchmark_before_caching.json
    ├── benchmark_with_caching.json
    └── cache_verification_results.json
```

**Note**: The `.cache/` directory is automatically created and can be safely deleted.

---

## Troubleshooting

### Cache Not Working

**Symptom**: Every run says "Cache miss, performing full scan..."

**Causes**:
1. Files are actively being modified (e.g., current Claude session writing)
2. Cache was manually deleted
3. Timestamps changed (e.g., after file sync)

**Solution**: This is expected behavior! Cache will work on subsequent runs once files stabilize.

### Cache Taking Too Long

**Symptom**: Warm cache still slow (> 3s)

**Possible issues**:
1. Slow disk (HDD instead of SSD)
2. Low memory (swapping during pickle load)
3. Anti-virus scanning cache file

**Solution**: Check system resources, try `--clear-cache` and rebuild.

### Wrong Data Returned

**Symptom**: Analysis results don't match current files

**This should never happen** - cache validates mtimes. If it does:
1. Run `--clear-cache` immediately
2. Report the issue (cache invalidation bug)

---

## Best Practices

### Development Workflow

```bash
# 1. Make changes to analysis scripts
vim analyze_routing.py

# 2. Run with cache (fast iteration)
python3 extract_enriched_data.py
python3 analyze_routing.py

# 3. If data seems wrong, verify without cache
python3 extract_enriched_data.py --no-cache
```

### Production Workflow

```bash
# Run normally - cache handles everything
python3 extract_enriched_data.py
```

Cache automatically invalidates when new session data appears.

---

## Technical Details

### Why Pickle?

- **Fastest** for Python objects (97% of load time is deserializing, not I/O)
- **Handles all data types** (including invalid UTF-8 that broke msgpack)
- **Protocol 5** provides best performance

### Why Not JSON?

- **5-10x slower** to parse than pickle
- **Larger files** (more verbose format)
- Still has UTF-8 issues

### Why Not msgpack?

- **Attempted** but failed - data contains invalid UTF-8 surrogates
- Would have been 5-10x faster if data was clean

---

## Integration with Other Scripts

To add caching to another script:

```python
from file_scan_cache import (
    is_cache_valid,
    load_sessions_cache,
    save_sessions_cache,
    get_file_metadata,
    save_metadata_cache
)
from common.config import PROJECTS_DIR

def load_sessions():
    # Try cache
    if is_cache_valid(PROJECTS_DIR):
        cached = load_sessions_cache()
        if cached:
            print("Using cache")
            return cached

    # Full scan
    print("Scanning files...")
    sessions = scan_all_files()  # Your scan logic

    # Save cache
    metadata = get_file_metadata(PROJECTS_DIR)
    save_metadata_cache(metadata)
    save_sessions_cache(sessions)

    return sessions
```

---

## Summary

The caching system provides:
- ✓ **Automatic**: No manual intervention needed
- ✓ **Fast**: 2.6x speedup on repeated runs
- ✓ **Safe**: Auto-invalidates on file changes
- ✓ **Simple**: Enable/disable with CLI flags

Just use your scripts normally and enjoy the speed boost!
