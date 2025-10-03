#!/usr/bin/env python3
"""
Schema versioning and validation for JSON data files.

This module provides version checking to detect incompatible schema changes
and prevent silent breakage of data consumers.

Schema Versioning Policy:
- Version format: MAJOR.MINOR.PATCH (semantic versioning)
- MAJOR: Breaking changes (incompatible schema modifications)
- MINOR: Backward-compatible additions (new fields, optional data)
- PATCH: Bug fixes, no schema changes

All JSON outputs must include metadata:
{
    "schema_version": "1.0.0",
    "generated_at": "2025-10-02T14:30:00Z",
    "generator": "script_name.py",
    "data": {...}
}
"""

from datetime import datetime
from typing import Dict, Any, Tuple, Optional
import json
import warnings


class SchemaVersion:
    """Semantic version for schema compatibility checking."""

    def __init__(self, version_string: str):
        """Parse semantic version string.

        Args:
            version_string: Version in format "MAJOR.MINOR.PATCH"

        Raises:
            ValueError: If version string is invalid
        """
        parts = version_string.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_string}. Expected MAJOR.MINOR.PATCH")

        try:
            self.major = int(parts[0])
            self.minor = int(parts[1])
            self.patch = int(parts[2])
        except ValueError as e:
            raise ValueError(f"Invalid version numbers in {version_string}: {e}")

        self.version_string = version_string

    def __str__(self) -> str:
        return self.version_string

    def __repr__(self) -> str:
        return f"SchemaVersion('{self.version_string}')"

    def is_compatible_with(self, required_version: 'SchemaVersion') -> bool:
        """Check if this version is compatible with required version.

        Compatibility rules:
        - Major version must match exactly
        - Minor version must be >= required
        - Patch version ignored for compatibility

        Args:
            required_version: Minimum required version

        Returns:
            True if compatible, False otherwise
        """
        # Major version must match exactly (breaking changes)
        if self.major != required_version.major:
            return False

        # Minor version must be at least the required version
        if self.minor < required_version.minor:
            return False

        # Patch version doesn't affect compatibility
        return True

    def __eq__(self, other) -> bool:
        if not isinstance(other, SchemaVersion):
            return False
        return (self.major == other.major and
                self.minor == other.minor and
                self.patch == other.patch)

    def __lt__(self, other) -> bool:
        if not isinstance(other, SchemaVersion):
            raise TypeError(f"Cannot compare SchemaVersion with {type(other)}")

        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.patch < other.patch

    def __le__(self, other) -> bool:
        return self == other or self < other

    def __gt__(self, other) -> bool:
        return not self <= other

    def __ge__(self, other) -> bool:
        return self == other or self > other


class SchemaValidationError(Exception):
    """Raised when schema version is incompatible."""
    pass


class SchemaValidator:
    """Validates schema versions in JSON data files."""

    # Known schema versions for each data type
    SCHEMA_VERSIONS = {
        'enriched_sessions': '1.0.0',
        'routing_patterns': '1.0.0',
        'routing_quality': '1.0.0',
        'marathon_classification': '1.0.0',
        'roi_analysis': '1.0.0',
        'temporal_segmentation': '1.0.0',
        'system_metrics': '1.0.0',
    }

    @staticmethod
    def create_metadata(generator_name: str, schema_type: str,
                       additional_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create standard metadata for JSON output.

        Args:
            generator_name: Name of the script generating the data
            schema_type: Type of schema (e.g., 'enriched_sessions')
            additional_metadata: Optional additional metadata fields

        Returns:
            Dictionary with standard metadata fields
        """
        version = SchemaValidator.SCHEMA_VERSIONS.get(schema_type, '1.0.0')

        metadata = {
            'schema_version': version,
            'schema_type': schema_type,
            'generated_at': datetime.now().isoformat(),
            'generator': generator_name,
        }

        if additional_metadata:
            metadata.update(additional_metadata)

        return metadata

    @staticmethod
    def validate_data(data: Dict[str, Any], schema_type: str,
                     strict: bool = False) -> Tuple[bool, str]:
        """Validate that data has compatible schema version.

        Args:
            data: Loaded JSON data dictionary
            schema_type: Expected schema type
            strict: If True, raise exception on incompatibility

        Returns:
            Tuple of (is_valid, message)

        Raises:
            SchemaValidationError: If strict=True and schema is incompatible
        """
        # Check if schema_version exists
        if 'schema_version' not in data:
            msg = f"No schema_version found in data. Expected schema_type: {schema_type}"
            if strict:
                raise SchemaValidationError(msg)
            warnings.warn(msg)
            return False, msg

        # Parse versions
        try:
            data_version = SchemaVersion(data['schema_version'])
        except ValueError as e:
            msg = f"Invalid schema_version format: {e}"
            if strict:
                raise SchemaValidationError(msg)
            return False, msg

        # Get expected version
        expected_version_str = SchemaValidator.SCHEMA_VERSIONS.get(schema_type)
        if not expected_version_str:
            msg = f"Unknown schema_type: {schema_type}"
            warnings.warn(msg)
            return True, "Unknown schema type, skipping validation"

        expected_version = SchemaVersion(expected_version_str)

        # Check compatibility
        if not data_version.is_compatible_with(expected_version):
            msg = (f"Incompatible schema version for {schema_type}. "
                  f"Data version: {data_version}, Required: {expected_version}. "
                  f"Major version mismatch indicates breaking changes.")
            if strict:
                raise SchemaValidationError(msg)
            warnings.warn(msg)
            return False, msg

        # Check for newer version (informational)
        if data_version > expected_version:
            msg = (f"Data has newer schema version ({data_version}) than expected ({expected_version}). "
                  f"Consider updating consumer code.")
            warnings.warn(msg)
            return True, msg

        return True, f"Schema version {data_version} is compatible with {expected_version}"

    @staticmethod
    def load_validated_json(filepath: str, schema_type: str,
                           strict: bool = False) -> Dict[str, Any]:
        """Load JSON file with schema validation.

        Args:
            filepath: Path to JSON file
            schema_type: Expected schema type
            strict: If True, raise exception on incompatibility

        Returns:
            Loaded and validated JSON data

        Raises:
            SchemaValidationError: If strict=True and validation fails
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is invalid JSON
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        is_valid, message = SchemaValidator.validate_data(data, schema_type, strict=strict)

        if not is_valid and not strict:
            print(f"Warning loading {filepath}: {message}")

        return data

    @staticmethod
    def wrap_data(data: Any, generator_name: str, schema_type: str,
                  additional_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Wrap data with schema metadata.

        Args:
            data: The actual data to wrap
            generator_name: Name of generating script
            schema_type: Type of schema
            additional_metadata: Optional additional metadata

        Returns:
            Dictionary with metadata and data
        """
        metadata = SchemaValidator.create_metadata(generator_name, schema_type, additional_metadata)

        return {
            **metadata,
            'data': data
        }


# Convenience functions for common operations

def validate_schema(data: Dict[str, Any], schema_type: str, strict: bool = False) -> bool:
    """Validate schema version (convenience function).

    Args:
        data: Data dictionary to validate
        schema_type: Expected schema type
        strict: If True, raise exception on failure

    Returns:
        True if valid, False otherwise
    """
    is_valid, _ = SchemaValidator.validate_data(data, schema_type, strict=strict)
    return is_valid


def add_metadata(data: Any, generator_name: str, schema_type: str) -> Dict[str, Any]:
    """Add schema metadata to data (convenience function).

    Args:
        data: Data to add metadata to
        generator_name: Name of generating script
        schema_type: Type of schema

    Returns:
        Dictionary with metadata and data
    """
    return SchemaValidator.wrap_data(data, generator_name, schema_type)
