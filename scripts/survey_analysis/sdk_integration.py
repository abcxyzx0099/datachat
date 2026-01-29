"""
Claude Agent SDK Integration for Self-Verifying Recoding Rules Agent.

This module provides the LLM client wrapper that integrates with
Claude Agent SDK to generate recoding rules.
"""

import json
import asyncio
from typing import List, Any, Optional
from pathlib import Path

try:
    from claude_agent_sdk import query, ClaudeAgentOptions
except ImportError:
    raise ImportError(
        "Claude Agent SDK is required. Install with: pip install claude-agent-sdk"
    )

from .models import RecodingRule, RuleType, VariableMetadata


class ClaudeLLMClient:
    """
    Claude Agent SDK client wrapper for generating recoding rules.

    This client handles the communication with Claude API
    specifically for recoding rule generation tasks.
    """

    def __init__(
        self,
        cwd: Optional[str] = None,
        permission_mode: str = "acceptEdits",
        model: Optional[str] = None
    ):
        """
        Initialize the Claude LLM client.

        Args:
            cwd: Working directory for the agent
            permission_mode: Permission mode for SDK
            model: Model to use (default: from SDK config)
        """
        self.cwd = cwd or str(Path.cwd())
        self.permission_mode = permission_mode
        self.model = model

    async def generate_recoding_rules(
        self,
        prompt: str,
        metadata: List[VariableMetadata]
    ) -> List[RecodingRule]:
        """
        Generate recoding rules using Claude.

        Args:
            prompt: The prompt to send to Claude
            metadata: Variable metadata (for context, not used directly in call)

        Returns:
            List of generated RecodingRule objects
        """
        options = ClaudeAgentOptions(
            cwd=self.cwd,
            permission_mode=self.permission_mode,
            setting_sources=["project"],
        )

        full_output = []
        response_text = ""

        try:
            async for message in query(prompt=prompt, options=options):
                if hasattr(message, 'subtype'):
                    if message.subtype == 'success':
                        # Got final result
                        if hasattr(message, 'result') and message.result:
                            response_text = message.result
                        break
                    elif message.subtype == 'error':
                        raise Exception(f"Claude API error: {message.result}")
                else:
                    # Collect content blocks
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, 'text'):
                                full_output.append(block.text)

            # If we didn't get a final result text, use accumulated content
            if not response_text and full_output:
                response_text = "\n".join(full_output)

            return self._parse_rules_from_response(response_text)

        except Exception as e:
            raise RuntimeError(f"Failed to generate rules with Claude: {e}")

    def _parse_rules_from_response(self, response: str) -> List[RecodingRule]:
        """
        Parse Claude's response into RecodingRule objects.

        Args:
            response: Raw response text from Claude

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
                # Try to parse the entire response as JSON
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
            raise ValueError(f"Failed to parse Claude response as recoding rules: {e}")


class SelfVerifyingAgentWithSDK:
    """
    Complete self-verifying agent with Claude Agent SDK integration.

    This class combines the self-verification logic with actual
    Claude API calls through the SDK.
    """

    def __init__(
        self,
        cwd: Optional[str] = None,
        max_iterations: int = 3,
        verbose: bool = True
    ):
        """
        Initialize the agent.

        Args:
            cwd: Working directory
            max_iterations: Maximum self-correction iterations
            verbose: Whether to print progress
        """
        from .recoding_agent import SelfVerifyingRecodingAgent

        self.llm_client = ClaudeLLMClient(cwd=cwd)
        self.max_iterations = max_iterations
        self.verbose = verbose

        # Create the base agent with our LLM client
        self.agent = SelfVerifyingRecodingAgent(
            llm_client=self.llm_client,
            max_iterations=max_iterations,
            verbose=verbose
        )

        # Monkey-patch the _generate_with_llm method to use async
        self.agent._generate_with_llm = self._generate_with_llm_async

    async def _generate_with_llm_async(
        self,
        prompt: str,
        metadata: List[VariableMetadata]
    ) -> List[RecodingRule]:
        """Async wrapper for LLM generation."""
        return await self.llm_client.generate_recoding_rules(prompt, metadata)

    async def generate_and_verify(self, metadata: List[VariableMetadata]):
        """
        Generate and verify recoding rules.

        Args:
            metadata: List of variable metadata

        Returns:
            RecodingRulesOutput with validated rules
        """
        # Temporarily make the method async-aware
        import inspect
        original_generate = self.agent._generate_with_llm

        # Store original method
        self.agent._original_generate = original_generate

        # Run the async workflow
        return await self._async_generate_and_verify(metadata)

    async def _async_generate_and_verify(self, metadata: List[VariableMetadata]):
        """Async implementation of generate and verify."""
        from .models import RecodingRulesOutput, ValidationResult
        from .validators import RuleValidator
        from datetime import datetime

        if self.verbose:
            print(f"Starting self-verifying recoding rules generation (max {self.max_iterations} iterations)")
            print()

        current_rules = None
        current_validation = None
        previous_result = None
        iteration_history = []

        for iteration in range(1, self.max_iterations + 1):
            if self.verbose:
                print(f"Iteration {iteration}/{self.max_iterations}")

            # Generate prompt
            prompt = self.agent._build_generation_prompt(
                metadata=metadata,
                iteration=iteration,
                previous_result=previous_result
            )

            # Generate rules
            try:
                rules = await self.llm_client.generate_recoding_rules(prompt, metadata)
            except Exception as e:
                if self.verbose:
                    print(f"  Failed to generate rules: {e}")
                if iteration == self.max_iterations:
                    raise
                continue

            # Validate
            validator = RuleValidator(metadata)
            validation_result = validator.validate_all_rules(rules)

            if self.verbose:
                print(f"  Validation: {len(validation_result.errors)} errors, {len(validation_result.warnings)} warnings")

            # Store iteration
            iteration_history.append({
                "iteration": iteration,
                "rules": rules,
                "validation_result": validation_result,
                "timestamp": datetime.now().isoformat()
            })

            # Check if valid
            if validation_result.is_valid:
                if self.verbose:
                    print("  All validation checks passed!")
                current_rules = rules
                current_validation = validation_result
                break
            else:
                if self.verbose:
                    print("  Validation failed, will refine...")
                current_rules = rules
                current_validation = validation_result
                previous_result = {
                    "rules": rules,
                    "validation_result": validation_result
                }

        return RecodingRulesOutput(
            rules=current_rules or [],
            validation_result=current_validation or ValidationResult(is_valid=False),
            iterations_used=len(iteration_history),
            metadata={
                "total_iterations_allowed": self.max_iterations,
                "iteration_history": iteration_history
            }
        )


async def generate_recoding_rules_async(
    metadata: List[VariableMetadata],
    cwd: Optional[str] = None,
    max_iterations: int = 3,
    verbose: bool = True
):
    """
    Async convenience function for generating recoding rules.

    Args:
        metadata: Variable metadata from survey
        cwd: Working directory
        max_iterations: Maximum self-correction iterations
        verbose: Whether to print progress

    Returns:
        RecodingRulesOutput with validated rules
    """
    agent = SelfVerifyingAgentWithSDK(
        cwd=cwd,
        max_iterations=max_iterations,
        verbose=verbose
    )
    return await agent.generate_and_verify(metadata)


def generate_recoding_rules_sync(
    metadata: List[VariableMetadata],
    cwd: Optional[str] = None,
    max_iterations: int = 3,
    verbose: bool = True
):
    """
    Synchronous wrapper for generating recoding rules.

    Args:
        metadata: Variable metadata from survey
        cwd: Working directory
        max_iterations: Maximum self-correction iterations
        verbose: Whether to print progress

    Returns:
        RecodingRulesOutput with validated rules
    """
    return asyncio.run(generate_recoding_rules_async(
        metadata=metadata,
        cwd=cwd,
        max_iterations=max_iterations,
        verbose=verbose
    ))
