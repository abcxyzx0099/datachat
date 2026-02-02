# Workflow Legacy - Three Node Pattern - Archive

**Archived:** 2026-02-02

## Original Location

`workflow/`

## Purpose

This was the original LangGraph prototype implementing the three-node pattern (Generate → Validate → Review) for three AI processing steps:
- Step 4: Generate Recoding Rules
- Step 8: Generate Indicators
- Step 9: Generate Table Specifications

## Status

**Superseded by:** `agent/` directory

The `agent/` implementation now contains the complete 8-phase workflow (all 22 steps) and is actively used throughout the codebase.

## Contents

| Type | Files |
|------|-------|
| Python source | `example.py`, `graph.py`, `prompts.py`, `state.py`, `__init__.py` |
| Documentation | `README.md`, `IMPLEMENTATION_SUMMARY.md` |
| Subdirectories | `nodes/`, `validators/`, `tests/` |

## Reason for Archiving

- Only implemented 3 steps (vs. 22 steps in `agent/`)
- Legacy prototype code
- No longer referenced by any active code
- Replaced by complete implementation in `agent/`
