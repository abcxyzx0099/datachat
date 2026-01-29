"""
Self-Verifying AI Agent for Recoding Rules Generation.

This module implements an AI agent that generates recoding rules
and automatically validates and refines them using Python scripts.
"""

import json
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

from .models import (
    RecodingRule,
    VariableMetadata,
    ValidationResult,
    WorkflowState,
    RecodingRulesOutput,
    RuleType
)
from .validators import RuleValidator


class SelfVerifyingRecodingAgent:
    """
    AI Agent that generates and self-verifies recoding rules.

    This agent:
    1. Generates recoding rules using an LLM
    2. Validates the rules using Python scripts
    3. Refines the rules based on validation errors
    4. Iterates until all checks pass or max iterations reached
    """

    def __init__(
        self,
        llm_client: Any = None,
        max_iterations: int = 3,
        verbose: bool = True
    ):
        """
        Initialize the self-verifying agent.

        Args:
            llm_client: LLM client for generating rules (e.g., Claude agent SDK)
            max_iterations: Maximum number of self-correction iterations
            verbose: Whether to print progress messages
        """
        self.llm_client = llm_client
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.iteration_history: List[Dict[str, Any]] = []

    def _log(self, message: str, level: str = "info"):
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            prefix = {
                "info": "ℹ️",
                "success": "✅",
                "error": "❌",
                "warning": "⚠️",
                "iteration": "🔄"
            }.get(level, "  ")
            print(f"{prefix} {message}")

    def _build_generation_prompt(
        self,
        metadata: List[VariableMetadata],
        iteration: int,
        previous_result: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build the prompt for generating recoding rules.

        Args:
            metadata: Variable metadata from the survey
            iteration: Current iteration number
            previous_result: Result from previous iteration (if any)

        Returns:
            Prompt string for the LLM
        """
        base_prompt = """You are an expert in survey data analysis and recoding. Your task is to generate recoding rules for survey variables.

## Input Variable Metadata

{metadata_formatted}

## Recoding Rule Types

1. **Range grouping**: Group continuous numeric values into ranges
   - Example: age (18-99) → age_group (18-24, 25-34, 35-44, 45-54, 55+)

2. **Mapping**: Map specific values to new values
   - Example: Reverse coding or category consolidation

3. **Derived variables**: Create new variables based on transformations
   - Example: Top-2-box (values 9-10 → 1, others → 0)

## Output Format

Return a JSON object with the following structure:

```json
{{
  "recoding_rules": [
    {{
      "source_variable": "variable_name",
      "target_variable": "new_variable_name",
      "rule_type": "range|mapping|derived|category",
      "transformations": [
        {{
          "source": [value_or_range],
          "target": target_value,
          "label": "Human readable label"
        }}
      ],
      "rationale": "Why this recoding makes sense for the analysis"
    }}
  ]
}}
```

## Guidelines

- Only generate rules for variables that would benefit from recoding
- Use meaningful variable names and labels
- Ensure all transformations are logically sound
- Group ranges sensibly (e.g., age groups, income brackets)
- For derived variables, explain the business logic
"""

        # Format metadata
        metadata_formatted = self._format_metadata(metadata)

        prompt = base_prompt.format(metadata_formatted=metadata_formatted)

        # Add feedback from previous iteration if this is a retry
        if iteration > 1 and previous_result:
            feedback_section = f"""

## Previous Iteration Feedback (Iteration {iteration - 1})

Your previous attempt had the following validation errors:

{self._format_validation_errors(previous_result['validation_result'])}

Please generate new recoding rules that address ALL of the errors above.

### Previous Rules (for reference)

```json
{json.dumps([r.dict() for r in previous_result['rules']], indent=2)}
```

### Instructions for This Iteration

1. Fix all validation errors identified above
2. Ensure all source variables exist in the metadata
3. Ensure all ranges are valid (start <= end)
4. Remove any duplicate target variables
5. Ensure each rule's transformations are complete and non-overlapping
"""
            prompt += feedback_section

        return prompt

    def _format_metadata(self, metadata: List[VariableMetadata]) -> str:
        """Format variable metadata for the prompt."""
        lines = ["| Variable | Type | Label | Range/Values |"]
        lines.append("|----------|------|-------|--------------|")

        for var in metadata:
            if var.variable_type == "numeric":
                range_str = f"{var.min_value}-{var.max_value}" if var.min_value is not None else "N/A"
            else:
                range_str = f"{len(var.categories)} categories" if var.categories else "N/A"

            lines.append(
                f"| {var.name} | {var.variable_type} | {var.label or 'N/A'} | {range_str} |"
            )

        return "\n".join(lines)

    def _format_validation_errors(self, result: ValidationResult) -> str:
        """Format validation errors for feedback."""
        if not result.errors:
            return "No errors found."

        lines = ["**Errors:**"]
        for i, error in enumerate(result.result, 1):
            lines.append(f"{i}. {error}")

        if result.warnings:
            lines.append("\n**Warnings:**")
            for i, warning in enumerate(result.warnings, 1):
                lines.append(f"{i}. {warning}")

        return "\n".join(lines)

    def _parse_llm_response(self, response: str) -> List[RecodingRule]:
        """
        Parse LLM response into RecodingRule objects.

        Args:
            response: Raw response string from LLM

        Returns:
            List of RecodingRule objects
        """
        # Try to extract JSON from the response
        try:
            # Find JSON in the response (handle markdown code blocks)
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)
            rules_data = data.get("recoding_rules", [])

            rules = []
            for rule_data in rules_data:
                # Convert rule_type string to enum
                if isinstance(rule_data.get("rule_type"), str):
                    rule_data["rule_type"] = RuleType(rule_data["rule_type"])

                rules.append(RecodingRule(**rule_data))

            return rules

        except Exception as e:
            raise ValueError(f"Failed to parse LLM response as recoding rules: {e}")

    def _generate_with_llm(
        self,
        prompt: str,
        metadata: List[VariableMetadata]
    ) -> List[RecodingRule]:
        """
        Generate recoding rules using the LLM.

        Args:
            prompt: Prompt for the LLM
            metadata: Variable metadata

        Returns:
            List of generated RecodingRule objects
        """
        # If using Claude Agent SDK
        if self.llm_client is not None:
            # This would use the actual Claude Agent SDK
            # For now, return a placeholder implementation
            response = self._call_llm_client(prompt)
            return self._parse_llm_response(response)
        else:
            # Placeholder: generate rules without LLM
            # In production, you would always have an LLM client
            raise NotImplementedError(
                "LLM client is required. Pass an llm_client that implements "
                "the Claude Agent SDK query interface."
            )

    def _call_llm_client(self, prompt: str) -> str:
        """
        Call the LLM client with the prompt.

        This is a placeholder for the actual LLM call.
        In production, this would use the Claude Agent SDK.
        """
        # TODO: Implement actual Claude Agent SDK call
        # For now, return a mock response
        raise NotImplementedError(
            "LLM client call not implemented. Please integrate with "
            "Claude Agent SDK or another LLM provider."
        )

    def generate_and_verify(
        self,
        metadata: List[VariableMetadata]
    ) -> RecodingRulesOutput:
        """
        Generate recoding rules with self-verification loop.

        This is the main entry point that:
        1. Generates rules using LLM
        2. Validates using Python scripts
        3. Refines based on errors
        4. Iterates until valid or max iterations reached

        Args:
            metadata: List of variable metadata from survey

        Returns:
            RecodingRulesOutput with rules and validation info
        """
        self._log(f"Starting self-verifying recoding rules generation (max {self.max_iterations} iterations)")
        self._log("")

        current_rules: Optional[List[RecodingRule]] = None
        current_validation: Optional[ValidationResult] = None
        previous_result: Optional[Dict[str, Any]] = None

        for iteration in range(1, self.max_iterations + 1):
            self._log(f"Iteration {iteration}/{self.max_iterations}", "iteration")

            # Step 1: Generate rules (or refine if not first iteration)
            if iteration == 1:
                self._log("Generating initial recoding rules...")
            else:
                self._log(f"Refining rules based on validation feedback...")

            prompt = self._build_generation_prompt(
                metadata=metadata,
                iteration=iteration,
                previous_result=previous_result
            )

            try:
                rules = self._generate_with_llm(prompt, metadata)
            except Exception as e:
                self._log(f"Failed to generate rules: {e}", "error")
                # Continue to next iteration or fail
                if iteration == self.max_iterations:
                    raise
                continue

            # Step 2: Validate rules
            self._log("Validating generated rules...")
            validator = RuleValidator(metadata)
            validation_result = validator.validate_all_rules(rules)

            # Step 3: Log results
            self._log(f"Validation: {len(validation_result.errors)} errors, {len(validation_result.warnings)} warnings")
            if validation_result.errors:
                for error in validation_result.errors[:3]:  # Show first 3 errors
                    self._log(f"  - {error}", "error")
                if len(validation_result.errors) > 3:
                    self._log(f"  ... and {len(validation_result.errors) - 3} more errors", "error")

            # Store iteration history
            iteration_data = {
                "iteration": iteration,
                "rules": rules,
                "validation_result": validation_result,
                "timestamp": datetime.now().isoformat()
            }
            self.iteration_history.append(iteration_data)

            # Step 4: Check if valid
            if validation_result.is_valid:
                self._log("All validation checks passed!", "success")
                current_rules = rules
                current_validation = validation_result
                break
            else:
                self._log("Validation failed, will refine...", "warning")
                current_rules = rules
                current_validation = validation_result
                previous_result = {
                    "rules": rules,
                    "validation_result": validation_result
                }

        # Check final result
        if current_validation and current_validation.is_valid:
            self._log(f"\nSuccessfully generated valid recoding rules after {len(self.iteration_history)} iteration(s)", "success")
        else:
            self._log(f"\nReached max iterations ({self.max_iterations}) without full validation", "warning")
            if current_validation and current_validation.errors:
                self._log(f"Final errors: {len(current_validation.errors)}", "error")

        return RecodingRulesOutput(
            rules=current_rules or [],
            validation_result=current_validation or ValidationResult(is_valid=False),
            iterations_used=len(self.iteration_history),
            metadata={
                "total_iterations_allowed": self.max_iterations,
                "validation_checks_performed": current_validation.checks_performed if current_validation else [],
                "iteration_history": [
                    {
                        "iteration": h["iteration"],
                        "error_count": len(h["validation_result"].errors),
                        "warning_count": len(h["validation_result"].warnings),
                        "is_valid": h["validation_result"].is_valid
                    }
                    for h in self.iteration_history
                ]
            }
        )


def generate_recoding_rules_with_verification(
    metadata: List[VariableMetadata],
    llm_client: Any = None,
    max_iterations: int = 3,
    verbose: bool = True
) -> RecodingRulesOutput:
    """
    Convenience function to generate recoding rules with self-verification.

    Args:
        metadata: List of variable metadata from the survey
        llm_client: LLM client for generating rules
        max_iterations: Maximum self-correction iterations
        verbose: Whether to print progress

    Returns:
        RecodingRulesOutput with generated rules and validation info
    """
    agent = SelfVerifyingRecodingAgent(
        llm_client=llm_client,
        max_iterations=max_iterations,
        verbose=verbose
    )
    return agent.generate_and_verify(metadata)
