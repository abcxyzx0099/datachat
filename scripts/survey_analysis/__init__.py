"""
Survey Analysis Workflow - Self-Verifying AI for Recoding Rules Generation

This module implements a self-verifying AI agent that:
1. Generates recoding rules based on survey metadata
2. Validates the rules using Python scripts
3. Iteratively refines until all checks pass

This design moves the verification step inside the AI agent,
allowing for automatic self-correction before human review.
"""

from .models import (
    WorkflowState,
    RecodingRule,
    ValidationResult,
    RuleType,
    Transformation,
    VariableMetadata,
    RecodingRulesOutput
)

from .recoding_agent import (
    SelfVerifyingRecodingAgent,
    generate_recoding_rules_with_verification
)

from .validators import (
    validate_recoding_rules,
    RuleValidator
)

from .sdk_integration import (
    ClaudeLLMClient,
    SelfVerifyingAgentWithSDK,
    generate_recoding_rules_sync
)

__all__ = [
    # Models
    "WorkflowState",
    "RecodingRule",
    "ValidationResult",
    "RuleType",
    "Transformation",
    "VariableMetadata",
    "RecodingRulesOutput",
    # Agent
    "SelfVerifyingRecodingAgent",
    "generate_recoding_rules_with_verification",
    # Validators
    "validate_recoding_rules",
    "RuleValidator",
    # SDK Integration
    "ClaudeLLMClient",
    "SelfVerifyingAgentWithSDK",
    "generate_recoding_rules_sync",
]
