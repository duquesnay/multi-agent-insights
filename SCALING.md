# Performance Thresholds

Simple guide: **When to worry about performance**

## Current Scale

- **Sessions**: 7
- **Delegations**: ~264
- **Performance**: Excellent (~2s extraction, 50MB memory)

## When Performance Becomes a Problem

### ✅ You're Fine (Current State)
- < 100 sessions → Everything works great
- < 500 sessions → No changes needed

### ⚠️ Watch Performance (500-1000 sessions)
- Extraction: May reach ~10-15s
- Memory: ~200-500MB
- **Action**: Monitor, no changes needed yet

### 🔴 Optimization Required (1000+ sessions)
- Extraction: >30s (becomes slow)
- Memory: >1GB (may cause issues)

**At this scale, contact the team for optimization support.**

## Quick Performance Check

```bash
# Time the extraction
time python -m tools.pipeline.extract_all_sessions

# If it takes >5s with <100 sessions, something's wrong
```

## What NOT to Do

❌ Don't optimize prematurely
❌ Don't add complex caching for <1000 sessions
❌ Don't switch to stream processing until you need it

## What TO Do

✅ Keep it simple (current approach works)
✅ Monitor extraction time as data grows
✅ Contact the team when you hit 1000+ sessions

---

**Bottom line**: The current implementation is well-designed and will handle 10x-100x growth without changes.
