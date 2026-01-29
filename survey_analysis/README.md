# Self-Verifying AI for Recoding Rules Generation

A Python module that implements a self-verifying AI agent for generating survey data recoding rules. The agent generates rules using an LLM, validates them using Python scripts, and iteratively refines until all checks pass.

## Overview

This module implements the design pattern from `SURVEY_ANALYSIS_WORKFLOW_DESIGN.md` where the verification step (Step 4.5) is moved inside the AI agent (Step 4). This allows for:

- **Automatic self-correction**: The AI validates its own output and refines it
- **Reduced human workload**: Only semantically-valid rules reach human review
- **Faster iteration**: No manual intervention for objective validation errors
- **Quality assurance**: All rules pass automated checks before use

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Self-Verifying Recoding Agent                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   Generate  │───▶│  Validate   │───▶│   Refine?   │        │
│  │   (LLM)     │    │  (Python)   │    │  (if error) │        │
│  └─────────────┘    └─────────────┘    └──────┬──────┘        │
│                                                 │               │
│                                    ┌────────────▼────────────┐ │
│                                    │   Iteration Loop         │ │
│                                    │   (max 3 times)          │ │
│                                    └────────────┬────────────┘ │
│                                                 │               │
│                              ┌──────────────────▼───────────┐  │
│                              │   Output Validated Rules     │  │
│                              └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

The module is part of the `datachat` project. Dependencies are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Validation (without LLM)

```python
from survey_analysis import (
    validate_recoding_rules,
    RecodingRule,
    RuleType,
    Transformation,
    VariableMetadata
)

# Define your metadata
metadata = [
    VariableMetadata(
        name="age",
        label="Respondent Age",
        variable_type="numeric",
        min_value=18,
        max_value=99
    )
]

# Define rules
rules = [
    RecodingRule(
        source_variable="age",
        target_variable="age_group",
        rule_type=RuleType.RANGE,
        transformations=[
            Transformation(source=[18, 24], target=1, label="18-24"),
            Transformation(source=[25, 34], target=2, label="25-34"),
        ]
    )
]

# Validate
result = validate_recoding_rules(rules, metadata)

if result.is_valid:
    print("All checks passed!")
else:
    for error in result.errors:
        print(f"Error: {error}")
```

### With Claude Agent SDK (Full Self-Verification)

```python
from survey_analysis import (
    generate_recoding_rules_sync,
    VariableMetadata
)

# Define your metadata
metadata = [
    VariableMetadata(
        name="age",
        label="Respondent Age",
        variable_type="numeric",
        min_value=18,
        max_value=99
    ),
    VariableMetadata(
        name="q1_satisfaction",
        label="Overall Satisfaction",
        variable_type="numeric",
        min_value=1,
        max_value=10
    )
]

# Generate rules with self-verification
output = generate_recoding_rules_sync(
    metadata=metadata,
    cwd="/path/to/project",
    max_iterations=3,
    verbose=True
)

print(f"Generated {len(output.rules)} valid rules")
print(f"Validated in {output.iterations_used} iteration(s)")
```

### Testing

Run the test CLI to validate the logic:

```bash
# Test validation logic
python3 -m survey_analysis.cli test-validation

# Run demo
python3 -m survey_analysis.cli demo

# Run all tests
python3 -m survey_analysis.cli all
```

## Validation Checks

The validator performs the following automated checks:

| Check | Description |
|-------|-------------|
| Source variables exist | Ensures referenced variables exist in metadata |
| Target conflicts | Warns if target variables already exist |
| Range validity | Ensures range start ≤ end |
| Duplicate targets | Ensures each target variable is unique |
| Transformation completeness | Checks all transformations are defined |
| Target uniqueness | Ensures target values are unique per rule |
| Source overlap | Ensures source values don't overlap |

## Module Structure

```
survey_analysis/
├── __init__.py              # Public API exports
├── models.py                # Pydantic data models
├── validators.py            # Validation logic
├── recoding_agent.py        # Self-verifying agent
├── sdk_integration.py       # Claude Agent SDK integration
├── cli.py                   # Test/demo CLI
└── README.md                # This file
```

## API Reference

### Models

- `RecodingRule`: A recoding rule definition
- `VariableMetadata`: Metadata for a survey variable
- `ValidationResult`: Results from validation
- `RuleType`: Enum of rule types (RANGE, MAPPING, DERIVED, CATEGORY)
- `Transformation`: A single transformation mapping

### Functions

- `validate_recoding_rules(rules, metadata)`: Validate rules against metadata
- `generate_recoding_rules_sync(metadata, ...)`: Generate rules with SDK

### Classes

- `RuleValidator`: Validator for recoding rules
- `SelfVerifyingRecodingAgent`: Base agent (requires LLM client)
- `ClaudeLLMClient`: Claude Agent SDK wrapper
- `SelfVerifyingAgentWithSDK`: Complete agent with SDK integration

## Design Principles

1. **Self-Correction**: The agent validates and refines its own output
2. **Objective Validation**: Only checks that can be programmatically verified
3. **Iteration Limit**: Prevents infinite loops with max iteration cap
4. **Detailed Feedback**: Validation errors guide refinement
5. **Progress Logging**: Optional verbose mode for debugging

## Limitations

- **Semantic validation**: The agent catches objective errors (syntax, structure)
  but not semantic errors (business logic appropriateness)
- **Human review still needed**: For quality assurance and semantic validation
- **LLM dependency**: Full self-verification requires an LLM client

## Future Enhancements

- [ ] Add more validation checks (statistical, domain-specific)
- [ ] Support for complex multi-variable transformations
- [ ] Integration with PSPP for actual data transformation
- [ ] Web UI for reviewing generated rules
- [ ] Rule templates for common patterns
