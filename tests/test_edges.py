"""
Unit Tests for Conditional Edge Routing Functions

This module tests all conditional routing functions from agent/edges.py.
Tests validate:
- Retry logic when validation fails
- Max iterations enforcement
- Approval routing
- Default routing behavior

Routing Functions Tested:
- should_retry_recoding
- should_approve_recoding
- should_retry_indicators
- should_approve_indicators
- should_retry_table_specs
- should_approve_table_specs
"""

import pytest
from typing import Dict, Any

from agent.state import (
    WorkflowState,
    ValidationResult,
    create_initial_state,
)

from agent.edges import (
    # Recoding routing
    should_retry_recoding,
    should_approve_recoding,
    RecodingRoute,

    # Indicator routing
    should_retry_indicators,
    should_approve_indicators,
    IndicatorRoute,

    # Table specs routing
    should_retry_table_specs,
    should_approve_table_specs,
    TableSpecsRoute,

    # Edge mappings
    RECODING_EDGE_MAPPING,
    INDICATOR_EDGE_MAPPING,
    TABLE_SPECS_EDGE_MAPPING,
)

from agent.config import DEFAULT_CONFIG


# =============================================================================
# Recoding Routing Tests (Steps 4-6)
# =============================================================================

class TestShouldRetryRecoding:
    """Tests for should_retry_recoding routing function."""

    def test_should_retry_recoding_on_validation_failure(self, sample_state):
        """Test retry routing when validation fails and iterations < max."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Syntax error"],
                warnings=[],
                checks_performed=["syntax"],
            ),
            "iteration_count": 1,
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        result = should_retry_recoding(state)

        assert result == "generate_recoding_rules_node"

    def test_should_retry_recoding_max_iterations(self, sample_state):
        """Test no retry after max iterations reached."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Syntax error"],
                warnings=[],
                checks_performed=["syntax"],
            ),
            "iteration_count": 3,  # Max reached
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        result = should_retry_recoding(state)

        # Should force human review when max iterations reached
        assert result == "review_recoding_rules_node"

    def test_should_retry_recoding_approved(self, sample_state):
        """Test routing when already approved."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["syntax"],
            ),
            "recoding_approved": True,
            "iteration_count": 0,
        }

        result = should_retry_recoding(state)

        assert result == "generate_pspp_recoding_syntax_node"

    def test_should_retry_recoding_validation_passed_not_approved(self, sample_state):
        """Test routing to review when validation passed but not approved."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["syntax"],
            ),
            "recoding_approved": False,
            "requires_human_review": True,
            "iteration_count": 0,
        }

        result = should_retry_recoding(state)

        assert result == "review_recoding_rules_node"

    def test_should_retry_recoding_default_to_review(self, sample_state):
        """Test default routing to review when conditions don't match."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": None,
            "recoding_approved": False,
            "iteration_count": 0,
        }

        result = should_retry_recoding(state)

        assert result == "review_recoding_rules_node"

    def test_should_retry_recoding_no_validation_result(self, sample_state):
        """Test routing when no validation result exists."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": None,
            "recoding_approved": False,
            "iteration_count": 0,
        }

        result = should_retry_recoding(state)

        # Default to review when no validation result
        assert result == "review_recoding_rules_node"


class TestShouldApproveRecoding:
    """Tests for should_approve_recoding routing function."""

    def test_should_approve_recoding_approved(self, sample_state):
        """Test approve routing when approved."""
        state: WorkflowState = {
            **sample_state,
            "recoding_approved": True,
        }

        result = should_approve_recoding(state)

        assert result == "generate_pspp_recoding_syntax_node"

    def test_should_approve_recoding_rejected(self, sample_state):
        """Test retry routing when rejected."""
        state: WorkflowState = {
            **sample_state,
            "recoding_approved": False,
            "recoding_feedback": "Rules are too complex",
        }

        result = should_approve_recoding(state)

        assert result == "generate_recoding_rules_node"

    def test_should_approve_recoding_default_to_retry(self, sample_state):
        """Test default to retry when not explicitly approved."""
        state: WorkflowState = {
            **sample_state,
            "recoding_approved": False,
        }

        result = should_approve_recoding(state)

        assert result == "generate_recoding_rules_node"


# =============================================================================
# Indicators Routing Tests (Steps 9-11)
# =============================================================================

class TestShouldRetryIndicators:
    """Tests for should_retry_indicators routing function."""

    def test_should_retry_indicators_on_validation_failure(self, sample_state):
        """Test retry routing when validation fails and iterations < max."""
        state: WorkflowState = {
            **sample_state,
            "indicator_validation_result": ValidationResult(
                is_valid=False,
                errors=["Undefined variable"],
                warnings=[],
                checks_performed=["variables"],
            ),
            "iteration_count": 1,
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        result = should_retry_indicators(state)

        assert result == "generate_indicators_node"

    def test_should_retry_indicators_max_iterations(self, sample_state):
        """Test no retry after max iterations reached."""
        state: WorkflowState = {
            **sample_state,
            "indicator_validation_result": ValidationResult(
                is_valid=False,
                errors=["Syntax error"],
                warnings=[],
                checks_performed=["syntax"],
            ),
            "iteration_count": 3,  # Max reached
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        result = should_retry_indicators(state)

        # Should force human review when max iterations reached
        assert result == "review_indicators_node"

    def test_should_retry_indicators_approved(self, sample_state):
        """Test routing when already approved."""
        state: WorkflowState = {
            **sample_state,
            "indicator_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure"],
            ),
            "indicators_approved": True,
            "iteration_count": 0,
        }

        result = should_retry_indicators(state)

        assert result == "generate_table_specifications_node"

    def test_should_retry_indicators_validation_passed_not_approved(self, sample_state):
        """Test routing to review when validation passed but not approved."""
        state: WorkflowState = {
            **sample_state,
            "indicator_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure"],
            ),
            "indicators_approved": False,
            "requires_human_review": True,
            "iteration_count": 0,
        }

        result = should_retry_indicators(state)

        assert result == "review_indicators_node"

    def test_should_retry_indicators_default_to_review(self, sample_state):
        """Test default routing to review."""
        state: WorkflowState = {
            **sample_state,
            "indicator_validation_result": None,
            "indicators_approved": False,
            "iteration_count": 0,
        }

        result = should_retry_indicators(state)

        assert result == "review_indicators_node"


class TestShouldApproveIndicators:
    """Tests for should_approve_indicators routing function."""

    def test_should_approve_indicators_approved(self, sample_state):
        """Test approve routing when approved."""
        state: WorkflowState = {
            **sample_state,
            "indicators_approved": True,
        }

        result = should_approve_indicators(state)

        assert result == "generate_table_specifications_node"

    def test_should_approve_indicators_rejected(self, sample_state):
        """Test retry routing when rejected."""
        state: WorkflowState = {
            **sample_state,
            "indicators_approved": False,
            "indicator_feedback": "Too many indicators",
        }

        result = should_approve_indicators(state)

        assert result == "generate_indicators_node"

    def test_should_approve_indicators_default_to_retry(self, sample_state):
        """Test default to retry when not explicitly approved."""
        state: WorkflowState = {
            **sample_state,
            "indicators_approved": False,
        }

        result = should_approve_indicators(state)

        assert result == "generate_indicators_node"


# =============================================================================
# Table Specifications Routing Tests (Steps 12-14)
# =============================================================================

class TestShouldRetryTableSpecs:
    """Tests for should_retry_table_specs routing function."""

    def test_should_retry_table_specs_on_validation_failure(self, sample_state):
        """Test retry routing when validation fails and iterations < max."""
        state: WorkflowState = {
            **sample_state,
            "table_validation_result": ValidationResult(
                is_valid=False,
                errors=["Invalid variable reference"],
                warnings=[],
                checks_performed=["variables"],
            ),
            "iteration_count": 1,
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        result = should_retry_table_specs(state)

        assert result == "generate_table_specifications_node"

    def test_should_retry_table_specs_max_iterations(self, sample_state):
        """Test no retry after max iterations reached."""
        state: WorkflowState = {
            **sample_state,
            "table_validation_result": ValidationResult(
                is_valid=False,
                errors=["Structure error"],
                warnings=[],
                checks_performed=["structure"],
            ),
            "iteration_count": 3,  # Max reached
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        result = should_retry_table_specs(state)

        # Should force human review when max iterations reached
        assert result == "review_table_specifications_node"

    def test_should_retry_table_specs_approved(self, sample_state):
        """Test routing when already approved."""
        state: WorkflowState = {
            **sample_state,
            "table_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure", "variables"],
            ),
            "table_specs_approved": True,
            "iteration_count": 0,
        }

        result = should_retry_table_specs(state)

        assert result == "generate_pspp_table_syntax_node"

    def test_should_retry_table_specs_validation_passed_not_approved(self, sample_state):
        """Test routing to review when validation passed but not approved."""
        state: WorkflowState = {
            **sample_state,
            "table_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure"],
            ),
            "table_specs_approved": False,
            "requires_human_review": True,
            "iteration_count": 0,
        }

        result = should_retry_table_specs(state)

        assert result == "review_table_specifications_node"

    def test_should_retry_table_specs_default_to_review(self, sample_state):
        """Test default routing to review."""
        state: WorkflowState = {
            **sample_state,
            "table_validation_result": None,
            "table_specs_approved": False,
            "iteration_count": 0,
        }

        result = should_retry_table_specs(state)

        assert result == "review_table_specifications_node"


class TestShouldApproveTableSpecs:
    """Tests for should_approve_table_specs routing function."""

    def test_should_approve_table_specs_approved(self, sample_state):
        """Test approve routing when approved."""
        state: WorkflowState = {
            **sample_state,
            "table_specs_approved": True,
        }

        result = should_approve_table_specs(state)

        assert result == "generate_pspp_table_syntax_node"

    def test_should_approve_table_specs_rejected(self, sample_state):
        """Test retry routing when rejected."""
        state: WorkflowState = {
            **sample_state,
            "table_specs_approved": False,
            "table_specs_feedback": "Too many tables",
        }

        result = should_approve_table_specs(state)

        assert result == "generate_table_specifications_node"

    def test_should_approve_table_specs_default_to_retry(self, sample_state):
        """Test default to retry when not explicitly approved."""
        state: WorkflowState = {
            **sample_state,
            "table_specs_approved": False,
        }

        result = should_approve_table_specs(state)

        assert result == "generate_table_specifications_node"


# =============================================================================
# Edge Mapping Tests
# =============================================================================

class TestEdgeMappings:
    """Tests for edge mapping dictionaries."""

    def test_recoding_edge_mapping(self):
        """Test recoding edge mapping has correct keys."""
        expected_keys = [
            "generate_recoding_rules_node",
            "review_recoding_rules_node",
            "generate_pspp_recoding_syntax_node",
        ]

        for key in expected_keys:
            assert key in RECODING_EDGE_MAPPING
            assert RECODING_EDGE_MAPPING[key] == key

    def test_indicator_edge_mapping(self):
        """Test indicator edge mapping has correct keys."""
        expected_keys = [
            "generate_indicators_node",
            "review_indicators_node",
            "generate_table_specifications_node",
        ]

        for key in expected_keys:
            assert key in INDICATOR_EDGE_MAPPING
            assert INDICATOR_EDGE_MAPPING[key] == key

    def test_table_specs_edge_mapping(self):
        """Test table specs edge mapping has correct keys."""
        expected_keys = [
            "generate_table_specifications_node",
            "review_table_specifications_node",
            "generate_pspp_table_syntax_node",
        ]

        for key in expected_keys:
            assert key in TABLE_SPECS_EDGE_MAPPING
            assert TABLE_SPECS_EDGE_MAPPING[key] == key


# =============================================================================
# Iteration Count Tests
# =============================================================================

class TestIterationCountLogic:
    """Tests for iteration count behavior in routing."""

    def test_iteration_count_zero_always_retries(self, sample_state):
        """Test that iteration_count=0 allows retry."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 0,
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        result = should_retry_recoding(state)

        assert result == "generate_recoding_rules_node"

    def test_iteration_count_at_boundary(self, sample_state):
        """Test iteration_count exactly at max_iterations - 1."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 2,  # max=3, so 2 < 3
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        result = should_retry_recoding(state)

        # Should still retry since 2 < 3
        assert result == "generate_recoding_rules_node"

    def test_iteration_count_exceeds_max(self, sample_state):
        """Test iteration_count exceeds max_iterations."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 5,  # max=3, so 5 >= 3
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        result = should_retry_recoding(state)

        # Should force review
        assert result == "review_recoding_rules_node"


# =============================================================================
# Custom Config Tests
# =============================================================================

class TestCustomConfigRouting:
    """Tests for routing with custom config values."""

    def test_custom_max_iterations(self, sample_state):
        """Test routing with custom max_self_correction_iterations."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 1,
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 5},
        }

        result = should_retry_recoding(state)

        # Should retry since 1 < 5
        assert result == "generate_recoding_rules_node"

    def test_custom_max_iterations_at_limit(self, sample_state):
        """Test routing at custom max_iterations limit."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 5,
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 5},
        }

        result = should_retry_recoding(state)

        # Should force review since 5 >= 5
        assert result == "review_recoding_rules_node"


# =============================================================================
# Validation Result with Warnings Tests
# =============================================================================

class TestValidationWithWarnings:
    """Tests for validation results with warnings but no errors."""

    def test_valid_with_warnings_routes_correctly(self, sample_state):
        """Test that valid result with warnings routes correctly."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=["Minor issue"],
                checks_performed=["check"],
            ),
            "recoding_approved": False,
            "iteration_count": 0,
        }

        result = should_retry_recoding(state)

        # Valid result should go to review (not approved yet)
        assert result == "review_recoding_rules_node"


# =============================================================================
# Missing State Fields Tests
# =============================================================================

class TestMissingStateFields:
    """Tests for routing when state fields are missing."""

    def test_missing_iteration_count_defaults_to_zero(self, sample_state):
        """Test that missing iteration_count defaults to 0."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            # No iteration_count field
        }

        result = should_retry_recoding(state)

        # Should retry since default iteration_count=0 < max=3
        assert result == "generate_recoding_rules_node"

    def test_missing_config_uses_default(self, sample_state):
        """Test that missing config uses DEFAULT_CONFIG."""
        state: WorkflowState = {
            **sample_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 1,
            # No config field
        }

        result = should_retry_recoding(state)

        # Should use DEFAULT_CONFIG max_iterations=3
        assert result == "generate_recoding_rules_node"
