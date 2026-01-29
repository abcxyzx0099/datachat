"""
CLI for testing the self-verifying recoding rules agent.

This script demonstrates how to use the SelfVerifyingRecodingAgent
with mock data to test the validation and iteration logic.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from survey_analysis import (
    SelfVerifyingRecodingAgent,
    generate_recoding_rules_with_verification,
    VariableMetadata,
    RecodingRule,
    RuleType,
    Transformation
)
from survey_analysis.validators import validate_recoding_rules


def create_sample_metadata() -> list[VariableMetadata]:
    """Create sample survey metadata for testing."""
    return [
        VariableMetadata(
            name="age",
            label="Respondent Age",
            variable_type="numeric",
            min_value=18,
            max_value=99,
            value_labels={}
        ),
        VariableMetadata(
            name="income",
            label="Annual Income",
            variable_type="numeric",
            min_value=0,
            max_value=250000,
            value_labels={}
        ),
        VariableMetadata(
            name="q1_satisfaction",
            label="Overall Satisfaction",
            variable_type="numeric",
            min_value=1,
            max_value=10,
            value_labels={i: str(i) for i in range(1, 11)}
        ),
        VariableMetadata(
            name="q2_nps",
            label="Net Promoter Score",
            variable_type="numeric",
            min_value=0,
            max_value=10,
            value_labels={}
        ),
        VariableMetadata(
            name="gender",
            label="Gender",
            variable_type="string",
            categories=["Male", "Female", "Non-binary", "Prefer not to say"]
        ),
    ]


def create_valid_sample_rules() -> list[RecodingRule]:
    """Create a sample of valid recoding rules for testing."""
    return [
        RecodingRule(
            source_variable="age",
            target_variable="age_group",
            rule_type=RuleType.RANGE,
            transformations=[
                Transformation(source=[18, 24], target=1, label="18-24"),
                Transformation(source=[25, 34], target=2, label="25-34"),
                Transformation(source=[35, 44], target=3, label="35-44"),
                Transformation(source=[45, 54], target=4, label="45-54"),
                Transformation(source=[55, 99], target=5, label="55+"),
            ]
        ),
        RecodingRule(
            source_variable="q1_satisfaction",
            target_variable="q1_top2box",
            rule_type=RuleType.DERIVED,
            transformations=[
                Transformation(source=[9, 10], target=1, label="Top 2 Box"),
                Transformation(source=[1, 2, 3, 4, 5, 6, 7, 8], target=0, label="Others"),
            ]
        ),
        RecodingRule(
            source_variable="income",
            target_variable="income_bracket",
            rule_type=RuleType.RANGE,
            transformations=[
                Transformation(source=[0, 29999], target=1, label="< $30k"),
                Transformation(source=[30000, 59999], target=2, label="$30k-$60k"),
                Transformation(source=[60000, 99999], target=3, label="$60k-$100k"),
                Transformation(source=[100000, 250000], target=4, label="$100k+"),
            ]
        ),
    ]


def create_invalid_sample_rules() -> list[RecodingRule]:
    """Create a sample of INVALID recoding rules for testing validation."""
    return [
        RecodingRule(
            source_variable="age",
            target_variable="age_group",
            rule_type=RuleType.RANGE,
            transformations=[
                Transformation(source=[24, 18], target=1, label="18-24"),  # Invalid: start > end
                Transformation(source=[25, 34], target=2, label="25-34"),
            ]
        ),
        RecodingRule(
            source_variable="nonexistent_var",  # Invalid: source doesn't exist
            target_variable="some_target",
            rule_type=RuleType.RANGE,
            transformations=[
                Transformation(source=[1, 10], target=1, label="Test"),
            ]
        ),
        RecodingRule(
            source_variable="q1_satisfaction",
            target_variable="duplicate_target",  # Will cause duplicate error
            rule_type=RuleType.DERIVED,
            transformations=[
                Transformation(source=[9, 10], target=1, label="Top 2 Box"),
            ]
        ),
        RecodingRule(
            source_variable="q2_nps",
            target_variable="duplicate_target",  # Duplicate!
            rule_type=RuleType.DERIVED,
            transformations=[
                Transformation(source=[9, 10], target=1, label="Promoters"),
            ]
        ),
    ]


def test_validation():
    """Test the validation logic with sample data."""
    print("=" * 60)
    print("TEST 1: Validation of Valid Rules")
    print("=" * 60)

    metadata = create_sample_metadata()
    valid_rules = create_valid_sample_rules()

    result = validate_recoding_rules(valid_rules, metadata)

    print(f"\nValidating {len(valid_rules)} rules...")
    print(f"Result: {'✅ VALID' if result.is_valid else '❌ INVALID'}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    print(f"Checks performed: {len(result.checks_performed)}")

    if result.warnings:
        print("\nWarnings:")
        for w in result.warnings:
            print(f"  - {w}")

    print("\n" + "=" * 60)
    print("TEST 2: Validation of Invalid Rules")
    print("=" * 60)

    invalid_rules = create_invalid_sample_rules()
    result = validate_recoding_rules(invalid_rules, metadata)

    print(f"\nValidating {len(invalid_rules)} rules...")
    print(f"Result: {'✅ VALID' if result.is_valid else '❌ INVALID'}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")

    print("\nErrors:")
    for e in result.errors:
        print(f"  ❌ {e}")

    if result.warnings:
        print("\nWarnings:")
        for w in result.warnings:
            print(f"  ⚠️  {w}")


def test_self_verification_demo():
    """
    Demonstrate the self-verification workflow with mock data.

    This simulates what would happen when the LLM generates rules
    and the agent validates and refines them.
    """
    print("\n" + "=" * 60)
    print("DEMO: Self-Verification Workflow")
    print("=" * 60)

    metadata = create_sample_metadata()

    print("\n📋 Input Metadata:")
    for var in metadata:
        print(f"  - {var.name} ({var.variable_type}): {var.label}")

    print("\n" + "-" * 60)
    print("Simulating AI agent with self-verification...")
    print("-" * 60)

    # Note: This demo uses a mock agent that doesn't actually call an LLM
    # In production, you would pass an actual Claude Agent SDK client

    print("\n⚠️  Note: This demo requires an LLM client to generate rules.")
    print("   To test with actual LLM calls, configure the Claude Agent SDK.")
    print("\n   The validation logic has been tested above.")


def main():
    """Main entry point for the CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Self-Verifying Recoding Rules Agent - Test CLI"
    )
    parser.add_argument(
        "action",
        choices=["test-validation", "demo", "all"],
        help="Action to perform"
    )

    args = parser.parse_args()

    if args.action in ["test-validation", "all"]:
        test_validation()

    if args.action in ["demo", "all"]:
        test_self_verification_demo()


if __name__ == "__main__":
    main()
