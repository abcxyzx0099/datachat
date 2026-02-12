---
name: stage2-spec-gen
description: 'Stage 2: Table Specification - Generate, validate, and review table_specification.json (AI-orchestrated). Output: table_specification.json. Use when creating analysis specification for survey data.'
license: Apache-2.0
---

# Stage 2: Table Specification

Generate and validate the consolidated table specification.

## Overview

Executes **Steps 4-6** of the workflow:
- Step 4: Generate table specification (AI-orchestrated)
- Step 5: Validate specification
- Step 6: Review and approve

## When to Use

Use this skill when:
- Metadata is prepared (Stage 1 complete)
- Need to create analysis specification
- Updating existing specification

## Usage

```
User: Generate table specification

Assistant: [Step 4] Generating specification with AI...
           [Step 5] Validating structure and references...
           [Step 6] Please review the specification

           Specification ready! Key elements:
           - 12 indicators
           - 25 cross-tabulations
           - Recoding rules for 8 variables

           Approve to proceed?
```

## Input

| Input | Required | Description |
|--------|-----------|-------------|
| `filtered_metadata.json` | Yes | From Stage 1 output |

## Output

| File | Content |
|-------|----------|
| `table_specification.json` | Recodings, indicators, tables, settings |

## Feedback Loop

- Validation fail → Regenerate specification
- Review reject → Return to Step 4

## AI-Orchestrated

Step 4 uses AI to generate the consolidated specification combining:
- Global recodings
- Indicator definitions
- Table specifications
- Output settings
