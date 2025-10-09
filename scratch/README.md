# Scratch Directory

This directory is for **temporary, disposable analysis scripts** created during investigations.

## Purpose
- One-off data exploration scripts
- Quick validation scripts
- Temporary analysis code that doesn't belong in the pipeline

## Guidelines
- Scripts here are **disposable** - they can be deleted at any time
- This directory is git-ignored
- For reusable analysis, add to `tools/pipeline/` or `tools/strategies/`

## Naming Convention
- `explore_<topic>.py` - Data exploration
- `verify_<assumption>.py` - Validation scripts
- `test_<hypothesis>.py` - Quick hypothesis testing

## Cleanup
These scripts are automatically ignored by git and can be safely deleted after use.

