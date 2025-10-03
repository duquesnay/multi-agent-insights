# Schema Versioning Quick Reference

## TL;DR

**Producers**: Always wrap your JSON output
**Consumers**: Always validate on load

## Quick Start

### Creating Versioned Output (Producers)

```python
from common.schema_validator import SchemaValidator

# Your data
results = {"metric": 42, "items": [...]}

# Wrap with metadata
output = SchemaValidator.wrap_data(
    data=results,
    generator_name="my_script.py",
    schema_type="my_schema"
)

# Save
import json
with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)
```

### Loading Versioned Data (Consumers)

```python
from common.schema_validator import SchemaValidator

# Load with validation
data = SchemaValidator.load_validated_json(
    filepath='data/file.json',
    schema_type='expected_schema',
    strict=True  # or False for lenient
)

# Use data
results = data['data']  # If wrapped
# or
results = data  # If unwrapped (metadata at top level)
```

## Output Format

All versioned files have this structure:

```json
{
  "schema_version": "1.0.0",
  "schema_type": "my_schema",
  "generated_at": "2025-10-02T19:17:09.378803",
  "generator": "my_script.py",

  "data": {
    "... your actual data ..."
  }
}
```

## Version Compatibility

| Data Version | Required Version | Compatible? | Why |
|-------------|-----------------|-------------|-----|
| 1.2.0 | 1.0.0 | ✓ Yes | Minor bump = backward compatible |
| 1.0.0 | 1.2.0 | ✗ No | Missing new features |
| 2.0.0 | 1.5.0 | ✗ No | Major bump = breaking changes |
| 1.0.5 | 1.0.0 | ✓ Yes | Patch doesn't affect compatibility |

## When to Bump Version

### MAJOR (Breaking Changes)
- Remove fields
- Rename fields
- Change field types
- Restructure data

**Example**: `{"sessions": [...]}` → `{"session_list": [...]}`

### MINOR (Additions)
- Add new fields
- Add optional data
- Enhance existing data

**Example**: `{"sessions": [...]}` → `{"sessions": [...], "metadata": {...}}`

### PATCH (Bug Fixes)
- Fix calculations
- Correct data extraction
- No structural changes

## Registered Schema Types

Current schemas (add yours to `common/schema_validator.py`):

- `enriched_sessions`
- `routing_patterns`
- `routing_quality`
- `marathon_classification`
- `roi_analysis`
- `temporal_segmentation`
- `system_metrics`

## Error Handling

### Strict Mode (Production)

```python
from common.schema_validator import SchemaValidationError

try:
    data = SchemaValidator.load_validated_json(
        filepath='data.json',
        schema_type='my_schema',
        strict=True
    )
except SchemaValidationError as e:
    print(f"Incompatible: {e}")
    # Handle error: regenerate data, use fallback, etc.
```

### Lenient Mode (Exploration)

```python
# Warns but doesn't fail
data = SchemaValidator.load_validated_json(
    filepath='data.json',
    schema_type='my_schema',
    strict=False
)
# Check warnings in output
```

## Common Patterns

### Pattern 1: Wrap Entire Output

```python
output = SchemaValidator.wrap_data(
    data=my_results,
    generator_name="script.py",
    schema_type="my_schema"
)
# Results in: {schema_version, schema_type, ..., data: my_results}
```

### Pattern 2: Merge Metadata

```python
metadata = SchemaValidator.create_metadata(
    generator_name="script.py",
    schema_type="my_schema",
    additional_metadata={"custom": "value"}
)

output = {
    **metadata,
    "sessions": sessions_list,
    "summary": summary_dict
}
# Results in: {schema_version, ..., custom, sessions, summary}
```

### Pattern 3: Check Version Before Use

```python
import json

with open('data.json', 'r') as f:
    data = json.load(f)

if 'schema_version' not in data:
    print("Warning: Unversioned data")
    # Decide: continue, regenerate, or abort
```

## Cheat Sheet

| Operation | Code |
|-----------|------|
| **Create metadata** | `SchemaValidator.create_metadata(generator, schema_type)` |
| **Wrap data** | `SchemaValidator.wrap_data(data, generator, schema_type)` |
| **Validate & load** | `SchemaValidator.load_validated_json(path, schema_type, strict)` |
| **Manual validate** | `validate_schema(data, schema_type, strict)` |
| **Parse version** | `SchemaVersion("1.2.3")` |
| **Check compat** | `version.is_compatible_with(required_version)` |

## Migration Checklist

### Updating a Generator
- [ ] Import `SchemaValidator`
- [ ] Identify output dict creation
- [ ] Wrap with `wrap_data()` or merge with `create_metadata()`
- [ ] Register schema type if new
- [ ] Test generation
- [ ] Regenerate data file

### Updating a Consumer
- [ ] Import `SchemaValidator`
- [ ] Replace `json.load()` with `load_validated_json()`
- [ ] Choose strict mode (True/False)
- [ ] Update data access (check for 'data' wrapper)
- [ ] Test with versioned data
- [ ] Handle validation errors

## Examples

See `example_schema_consumer.py` for complete examples.

Run: `python example_schema_consumer.py`

## Full Documentation

For detailed information, see:
- `docs/SCHEMA-VERSIONING.md` - Complete guide
- `docs/SCHEMA-VERSIONING-IMPLEMENTATION.md` - Implementation report
- `common/schema_validator.py` - Source code with docstrings

---

**Quick Tip**: When in doubt, use `strict=False` during development, switch to `strict=True` for production.
