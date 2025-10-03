# Schema Versioning System

## Overview

This document describes the schema versioning system implemented to prevent silent breakage when data formats change.

**Problem Solved**: JSON files had no version metadata. Format changes broke downstream consumers silently with no detection mechanism.

**Solution**: Semantic versioning for all JSON outputs with automatic compatibility checking.

## Versioning Policy

### Version Format

All schemas use **semantic versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (incompatible schema modifications)
  - Removing fields
  - Renaming fields
  - Changing field types
  - Restructuring data hierarchy

- **MINOR**: Backward-compatible additions
  - Adding new optional fields
  - Adding new data structures alongside existing ones
  - Enhancing existing data without changing structure

- **PATCH**: Bug fixes, no schema changes
  - Fixing data extraction bugs
  - Correcting calculations
  - No structural changes

### Compatibility Rules

Version compatibility uses these rules:

1. **Major version must match exactly** - Breaking changes are incompatible
2. **Minor version must be >= required** - New features are backward compatible
3. **Patch version is ignored** - Bug fixes don't affect compatibility

**Examples**:
- Data v1.2.0 compatible with required v1.1.0 ✓
- Data v1.3.5 compatible with required v1.0.0 ✓
- Data v2.0.0 **NOT** compatible with required v1.5.0 ✗
- Data v1.0.0 **NOT** compatible with required v1.2.0 ✗

## Standard Metadata Structure

All JSON outputs must include these metadata fields:

```json
{
  "schema_version": "1.0.0",
  "schema_type": "enriched_sessions",
  "generated_at": "2025-10-02T14:30:00.123456",
  "generator": "extract_enriched_data.py",

  "data": {
    "... actual data here ..."
  }
}
```

### Required Metadata Fields

- `schema_version`: Semantic version string (MAJOR.MINOR.PATCH)
- `schema_type`: Type identifier (e.g., 'enriched_sessions', 'routing_quality')
- `generated_at`: ISO 8601 timestamp of generation
- `generator`: Name of script that created the file

### Optional Metadata Fields

Generators can add additional metadata:

```python
metadata = SchemaValidator.create_metadata(
    generator_name="my_script.py",
    schema_type="my_schema",
    additional_metadata={
        "source_file": "input.json",
        "processing_options": {"cache": True},
        "record_count": 1250
    }
)
```

## Registered Schema Types

Current registered schemas (in `common/schema_validator.py`):

| Schema Type | Current Version | Description |
|------------|----------------|-------------|
| `enriched_sessions` | 1.0.0 | Full session data with delegation context |
| `routing_patterns` | 1.0.0 | Agent routing patterns by period |
| `routing_quality` | 1.0.0 | Routing quality analysis |
| `marathon_classification` | 1.0.0 | Marathon session classifications |
| `roi_analysis` | 1.0.0 | ROI and efficiency metrics |
| `temporal_segmentation` | 1.0.0 | Timeline segmentation data |
| `system_metrics` | 1.0.0 | System-wide metrics |

### Adding New Schema Types

To register a new schema type:

1. Add to `SCHEMA_VERSIONS` in `common/schema_validator.py`:
   ```python
   SCHEMA_VERSIONS = {
       ...
       'my_new_schema': '1.0.0',
   }
   ```

2. Document the schema structure
3. Use in your generator:
   ```python
   metadata = SchemaValidator.create_metadata(
       generator_name="my_script.py",
       schema_type="my_new_schema"
   )
   ```

## Usage Guide

### For Data Producers (Scripts that Generate JSON)

**Pattern 1: Wrap existing data**

```python
from common.schema_validator import SchemaValidator

# Your analysis results
results = {
    'metric_1': 42,
    'metric_2': 'value'
}

# Wrap with metadata
output = SchemaValidator.wrap_data(
    data=results,
    generator_name="my_analysis.py",
    schema_type="my_schema"
)

# Save
with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)
```

**Pattern 2: Create metadata manually**

```python
from common.schema_validator import SchemaValidator

# Create metadata
metadata = SchemaValidator.create_metadata(
    generator_name="my_script.py",
    schema_type="enriched_sessions",
    additional_metadata={
        "custom_field": "value"
    }
)

# Merge with your data
output = {
    **metadata,
    "sessions": my_sessions_list,
    "summary": my_summary
}

# Save
with open('output.json', 'w') as f:
    json.dump(output, f, indent=2)
```

### For Data Consumers (Scripts that Load JSON)

**Pattern 1: Strict validation** (recommended for production pipelines)

```python
from common.schema_validator import SchemaValidator, SchemaValidationError

try:
    data = SchemaValidator.load_validated_json(
        filepath='data/enriched_sessions.json',
        schema_type='enriched_sessions',
        strict=True  # Raises exception on incompatibility
    )
    # Use data safely
    sessions = data['sessions']
except SchemaValidationError as e:
    print(f"Incompatible schema: {e}")
    # Handle error - maybe prompt for upgrade
except FileNotFoundError:
    print("Data file not found")
```

**Pattern 2: Lenient validation** (for exploratory analysis)

```python
from common.schema_validator import SchemaValidator

# Warns but doesn't fail on incompatibility
data = SchemaValidator.load_validated_json(
    filepath='data/routing_quality.json',
    schema_type='routing_quality',
    strict=False  # Warnings only
)

# Check if validation passed
if data:
    periods = data.get('periods', {})
    # Continue with analysis
```

**Pattern 3: Manual validation**

```python
import json
from common.schema_validator import validate_schema

# Load normally
with open('data/enriched_sessions.json', 'r') as f:
    data = json.load(f)

# Validate separately
is_valid = validate_schema(data, 'enriched_sessions', strict=False)

if not is_valid:
    print("Warning: Schema may be incompatible")
    # Decide whether to continue
```

## Migration Guide

### Adding Versioning to Existing Generators

**Step 1**: Import the validator

```python
from common.schema_validator import SchemaValidator
```

**Step 2**: Identify where you create output dictionary

Find code like:
```python
output = {
    "extraction_date": datetime.now().isoformat(),
    "total_count": len(items),
    "data": items
}
```

**Step 3**: Replace with versioned output

```python
# Create metadata
metadata = SchemaValidator.create_metadata(
    generator_name="your_script.py",
    schema_type="your_schema_type",
    additional_metadata={
        "total_count": len(items)
    }
)

# Merge with data
output = {
    **metadata,
    "data": items
}
```

**Step 4**: Register schema type (if new)

Add to `SCHEMA_VERSIONS` in `common/schema_validator.py`.

### Updating Existing Consumers

**Step 1**: Add validation at load point

Replace:
```python
with open('data/file.json', 'r') as f:
    data = json.load(f)
```

With:
```python
from common.schema_validator import SchemaValidator

data = SchemaValidator.load_validated_json(
    filepath='data/file.json',
    schema_type='expected_schema',
    strict=False  # or True for critical paths
)
```

**Step 2**: Update data access patterns

Old way:
```python
items = data['items']  # Direct access
```

New way:
```python
items = data.get('items', [])  # Or access via 'data' key if wrapped
```

**Step 3**: Check for metadata

```python
if 'schema_version' not in data:
    print("Warning: Unversioned data file")
    # Handle gracefully
```

## Version Bumping Guidelines

### When to Bump MAJOR Version

Breaking changes require major version bump:

- **Removing fields**:
  ```python
  # v1.0.0
  {"sessions": [...], "total": 100}

  # v2.0.0 - removed 'total'
  {"sessions": [...]}
  ```

- **Renaming fields**:
  ```python
  # v1.0.0
  {"delegations": [...]}

  # v2.0.0 - renamed field
  {"delegation_list": [...]}
  ```

- **Restructuring data**:
  ```python
  # v1.0.0
  {"sessions": [{"id": 1, "data": {...}}]}

  # v2.0.0 - changed structure
  {"sessions": {"session_1": {...}}}
  ```

### When to Bump MINOR Version

Backward-compatible additions:

- **Adding new fields**:
  ```python
  # v1.0.0
  {"sessions": [...]}

  # v1.1.0 - added new field
  {"sessions": [...], "metadata": {...}}
  ```

- **Adding new optional data**:
  ```python
  # v1.0.0
  {"sessions": [{"id": 1, "count": 5}]}

  # v1.1.0 - added optional field
  {"sessions": [{"id": 1, "count": 5, "details": {...}}]}
  ```

### When to Bump PATCH Version

Bug fixes without schema changes:

- Correcting calculation errors
- Fixing data extraction bugs
- Performance improvements
- No structural changes

## Error Handling

### SchemaValidationError

Raised when strict validation fails:

```python
try:
    data = SchemaValidator.load_validated_json(
        filepath='data.json',
        schema_type='my_schema',
        strict=True
    )
except SchemaValidationError as e:
    # e.args[0] contains detailed error message
    print(f"Schema incompatible: {e}")
    # Options:
    # 1. Prompt user to regenerate data
    # 2. Use fallback/cached data
    # 3. Exit gracefully
```

### Warnings

With `strict=False`, warnings are issued via Python's `warnings` module:

```python
import warnings

# Capture warnings
with warnings.catch_warnings(record=True) as w:
    data = SchemaValidator.load_validated_json(
        filepath='data.json',
        schema_type='my_schema',
        strict=False
    )

    if w:
        for warning in w:
            print(f"Warning: {warning.message}")
```

## Testing Schema Validation

### Unit Tests

```python
from common.schema_validator import SchemaVersion, SchemaValidator

def test_version_compatibility():
    v1_2_0 = SchemaVersion("1.2.0")
    v1_1_0 = SchemaVersion("1.1.0")
    v2_0_0 = SchemaVersion("2.0.0")

    # Compatible
    assert v1_2_0.is_compatible_with(v1_1_0)

    # Incompatible (major version mismatch)
    assert not v2_0_0.is_compatible_with(v1_1_0)

    # Incompatible (data too old)
    assert not v1_1_0.is_compatible_with(v1_2_0)

def test_metadata_creation():
    metadata = SchemaValidator.create_metadata(
        generator_name="test.py",
        schema_type="test_schema"
    )

    assert 'schema_version' in metadata
    assert 'generated_at' in metadata
    assert metadata['generator'] == 'test.py'
```

### Integration Tests

Test with real data files:

```python
import json
from pathlib import Path
from common.schema_validator import SchemaValidator

def test_real_data_files():
    data_dir = Path("data")

    for json_file in data_dir.glob("*.json"):
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Check for schema_version
        if 'schema_version' not in data:
            print(f"Missing version: {json_file}")
        else:
            print(f"✓ {json_file}: v{data['schema_version']}")
```

## Examples

See `example_schema_consumer.py` for complete working examples:

1. Strict validation
2. Lenient validation
3. Manual validation
4. Accessing versioned data
5. Creating versioned output

Run: `python example_schema_consumer.py`

## Troubleshooting

### "No schema_version found in data"

**Cause**: Loading old data file without versioning.

**Solution**: Regenerate the file with updated generator, or add validation tolerance:
```python
data = SchemaValidator.load_validated_json(
    filepath='old_data.json',
    schema_type='my_schema',
    strict=False  # Tolerate missing version
)
```

### "Incompatible schema version"

**Cause**: Data file has breaking changes from expected schema.

**Solution**:
1. Check if data needs regeneration
2. Update consumer code for new schema
3. Migrate data to new format

### "Invalid version format"

**Cause**: `schema_version` not in MAJOR.MINOR.PATCH format.

**Solution**: Fix generator to use proper format:
```python
"schema_version": "1.0.0"  # Not "v1.0" or "1.0"
```

## Best Practices

1. ✓ **Always version new outputs** - Use `SchemaValidator.wrap_data()`
2. ✓ **Validate on load** - Use `load_validated_json()` or `validate_schema()`
3. ✓ **Use strict=True for production** - Fail fast on incompatibility
4. ✓ **Document schema changes** - Note in CHANGELOG when bumping versions
5. ✓ **Register schema types** - Add to `SCHEMA_VERSIONS` dict
6. ✓ **Test version bumps** - Verify consumers handle new versions
7. ✗ **Don't skip metadata** - Even for "temporary" outputs
8. ✗ **Don't ignore warnings** - Investigate compatibility issues

## Future Enhancements

Potential improvements:

- [ ] Automatic schema inference from data structure
- [ ] Schema evolution tracking (changelog per type)
- [ ] Backward compatibility transformers (auto-migrate old data)
- [ ] JSON Schema validation (structure enforcement)
- [ ] Version deprecation warnings

---

**Implemented**: 2025-10-02
**Last Updated**: 2025-10-02
**Status**: Active
