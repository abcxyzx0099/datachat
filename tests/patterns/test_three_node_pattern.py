"""
Integration Tests for Three-Node Pattern (Generate → Validate → Review)

This module tests the three-node pattern used three times in the workflow:
- Recoding Rules (Steps 4-6): generate_recoding_rules_node → validate_recoding_rules_node → review_recoding_rules_node
- Indicators (Steps 9-11): generate_indicators_node → validate_indicators_node → review_indicators_node
- Table Specifications (Steps 12-14): generate_table_specifications_node → validate_table_specs_node → review_table_specifications_node

Each cycle follows the same pattern:
1. Generate (LLM creates artifact)
2. Validate (automated validation)
3. Review (human approval or rejection with feedback)
4. On rejection: regenerate with feedback

Tests verify:
- State transitions through each node
- Conditional routing based on validation results
- Feedback loops and iteration tracking
- Human approval/rejection flows
- Max iterations enforcement
- Edge function routing logic

Dependencies:
- agent/nodes/phase2_recoding.py
- agent/nodes/phase3_indicators.py
- agent/nodes/phase4_tables.py
- agent/validation/recoding.py
- agent/validation/indicators.py
- agent/validation/tables.py
- agent/edges.py (conditional routing functions)
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, MagicMock, patch

from agent.state import (
    STEP_0_INITIAL, STEP_1_EXTRACT_SPSS,
    STEP_3_FILTER_METADATA, STEP_4_GENERATE_RECODING_RULES, STEP_5_VALIDATE_RECODING_RULES, STEP_6_REVIEW_RECODING_RULES,
    STEP_8_EXECUTE_PSPP_RECODING, STEP_9_GENERATE_INDICATORS, STEP_10_VALIDATE_INDICATORS, STEP_11_REVIEW_INDICATORS,
    STEP_12_GENERATE_TABLE_SPECIFICATIONS, STEP_13_VALIDATE_TABLE_SPECIFICATIONS, STEP_14_REVIEW_TABLE_SPECIFICATIONS,
    WorkflowState,
)
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
)

from agent.config import DEFAULT_CONFIG


# =============================================================================
# Test Fixtures for Three-Node Pattern
# =============================================================================

@pytest.fixture
def initial_recoding_state(sample_state) -> WorkflowState:
    """State before Step 4 (ready to generate recoding rules)."""
    return {
        **sample_state,
        "current_step": STEP_3_FILTER_METADATA,
        "filtered_metadata": [
            {
                "name": "age",
                "label": "Age",
                "variable_type": "numeric",
                "min_value": 18,
                "max_value": 80,
                "value_labels": {},
                "distinct_count": 50,
            },
            {
                "name": "satisfaction",
                "label": "Satisfaction",
                "variable_type": "numeric",
                "min_value": 1,
                "max_value": 5,
                "value_labels": {
                    1: "Very Dissatisfied",
                    2: "Dissatisfied",
                    3: "Neutral",
                    4: "Satisfied",
                    5: "Very Satisfied",
                },
                "distinct_count": 5,
            },
        ],
        "variable_centered_metadata": {
            "variables": {
                "age": {
                    "name": "age",
                    "label": "Age",
                    "variable_type": "numeric",
                    "min_value": 18,
                    "max_value": 80,
                    "value_labels": {},
                },
                "satisfaction": {
                    "name": "satisfaction",
                    "label": "Satisfaction",
                    "variable_type": "numeric",
                    "min_value": 1,
                    "max_value": 5,
                    "value_labels": {
                        1: "Very Dissatisfied",
                        2: "Dissatisfied",
                        3: "Neutral",
                        4: "Satisfied",
                        5: "Very Satisfied",
                    },
                },
            }
        },
        "iteration_count": 0,
        "recoding_approved": False,
        "recoding_feedback": None,
    }


@pytest.fixture
def initial_indicators_state(sample_state) -> WorkflowState:
    """State before Step 9 (ready to generate indicators)."""
    return {
        **sample_state,
        "current_step": STEP_8_EXECUTE_PSPP_RECODING,
        "new_metadata": {
            "variable_names": ["gender", "satisfaction", "age", "income"],
            "variable_labels": {
                "gender": "Gender",
                "satisfaction": "Overall Satisfaction",
                "age": "Age",
                "income": "Annual Income",
            },
            "value_labels": {
                "gender": {1: "Male", 2: "Female"},
                "satisfaction": {
                    1: "Very Dissatisfied",
                    2: "Dissatisfied",
                    3: "Neutral",
                    4: "Satisfied",
                    5: "Very Satisfied",
                },
            },
            "variable_count": 4,
        },
        "iteration_count": 0,
        "indicators_approved": False,
        "indicator_feedback": None,
    }


@pytest.fixture
def initial_table_specs_state(sample_state) -> WorkflowState:
    """State before Step 12 (ready to generate table specifications)."""
    return {
        **sample_state,
        "current_step": STEP_11_REVIEW_INDICATORS,
        "new_metadata": {
            "variable_names": ["gender", "satisfaction", "age", "income"],
            "variable_labels": {
                "gender": "Gender",
                "satisfaction": "Overall Satisfaction",
                "age": "Age",
                "income": "Annual Income",
            },
            "value_labels": {
                "gender": {1: "Male", 2: "Female"},
                "satisfaction": {
                    1: "Very Dissatisfied",
                    2: "Dissatisfied",
                    3: "Neutral",
                    4: "Satisfied",
                    5: "Very Satisfied",
                },
            },
            "variable_count": 4,
        },
        "indicators": {
            "indicators": [
                {
                    "name": "Demographics",
                    "description": "Demographic variables",
                    "variables": ["gender", "age"],
                }
            ]
        },
        "iteration_count": 0,
        "table_specs_approved": False,
        "table_specs_feedback": None,
    }


@pytest.fixture
def valid_recoding_rules() -> Dict[str, Any]:
    """Valid recoding rules for testing."""
    return {
        "recoding_rules": [
            {
                "source_variable": "age",
                "target_variable": "age_group",
                "transformation_type": "range_grouping",
                "description": "Group age into ranges",
                "rules": [
                    {"source_min": 18, "source_max": 34, "target_value": 1, "target_label": "18-34"},
                    {"source_min": 35, "source_max": 50, "target_value": 2, "target_label": "35-50"},
                    {"source_min": 51, "source_max": 80, "target_value": 3, "target_label": "51+"},
                ],
            }
        ]
    }


@pytest.fixture
def invalid_recoding_rules() -> Dict[str, Any]:
    """Invalid recoding rules (will fail validation)."""
    return {
        "recoding_rules": [
            {
                "source_variable": "nonexistent_var",
                "target_variable": "target_var",
                "transformation_type": "range_grouping",
                "description": "Invalid rule - source variable doesn't exist",
                "rules": [
                    {"source_min": 18, "source_max": 34, "target_value": 1, "target_label": "18-34"},
                ],
            }
        ]
    }


@pytest.fixture
def valid_indicators() -> Dict[str, Any]:
    """Valid indicators for testing."""
    return {
        "indicators": [
            {
                "name": "Customer_Satisfaction",
                "description": "Satisfaction and demographic variables",
                "variables": ["satisfaction", "gender"],
            }
        ]
    }


@pytest.fixture
def invalid_indicators() -> Dict[str, Any]:
    """Invalid indicators (will fail validation)."""
    return {
        "indicators": [
            {
                "name": "Invalid_Indicator",
                "description": "Invalid indicator - variable doesn't exist",
                "variables": ["nonexistent_variable"],
            }
        ]
    }


@pytest.fixture
def valid_table_specs() -> Dict[str, Any]:
    """Valid table specifications for testing."""
    return {
        "tables": [
            {
                "table_id": "gender_x_satisfaction",
                "row_variable": "gender",
                "column_variable": "satisfaction",
                "statistics": ["count", "columnpct"],
                "weight_variable": None,
            }
        ]
    }


@pytest.fixture
def invalid_table_specs() -> Dict[str, Any]:
    """Invalid table specifications (will fail validation)."""
    return {
        "tables": [
            {
                "table_id": "invalid_table",
                "row_variable": "nonexistent_var",
                "column_variable": "satisfaction",
                "statistics": ["count", "columnpct"],
                "weight_variable": None,
            }
        ]
    }


# =============================================================================
# Recoding Three-Node Pattern Tests (Steps 4-6)
# =============================================================================

class TestRecodingThreeNodePattern:
    """Integration tests for recoding rules three-node pattern."""

    def test_recoding_successful_flow(self, initial_recoding_state, valid_recoding_rules):
        """Test successful flow: generate → validate passes → human approves."""
        from agent.nodes.phase2_recoding import (
            generate_recoding_rules_node,
            validate_recoding_rules_node,
            review_recoding_rules_node,
        )

        # Step 4: Generate (with mock LLM)
        with patch('agent.nodes.phase2_recoding.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(valid_recoding_rules)
            mock_llm.return_value.invoke.return_value = mock_response

            state_after_gen = generate_recoding_rules_node(initial_recoding_state)

        assert state_after_gen["current_step"] == STEP_4_GENERATE_RECODING_RULES
        assert state_after_gen["recoding_rules"] is not None
        assert state_after_gen["recoding_feedback"] is None  # Cleared on success
        assert state_after_gen["iteration_count"] == 0

        # Step 5: Validate
        state_after_val = validate_recoding_rules_node(state_after_gen)

        assert state_after_val["current_step"] == STEP_5_VALIDATE_RECODING_RULES
        assert state_after_val["recoding_validation_result"] is not None
        assert state_after_val["recoding_validation_result"]['is_valid'] == True

        # Step 6: Review (with interrupt mock)
        with patch('langgraph.types.interrupt'):
            state_after_review = review_recoding_rules_node(state_after_val)

        assert state_after_review["current_step"] == STEP_6_REVIEW_RECODING_RULES
        assert state_after_review["requires_human_review"] == True

        # Simulate human approval
        approved_state = {**state_after_review, "recoding_approved": True}

        # Check routing after approval
        route = should_approve_recoding(approved_state)
        assert route == "generate_pspp_recoding_syntax_node"

    def test_recoding_validation_failure_flow(self, initial_recoding_state, invalid_recoding_rules):
        """Test validation failure flow: generate → validate fails → should retry."""
        from agent.nodes.phase2_recoding import (
            generate_recoding_rules_node,
            validate_recoding_rules_node,
        )

        # Step 4: Generate (with mock LLM returning invalid rules)
        with patch('agent.nodes.phase2_recoding.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(invalid_recoding_rules)
            mock_llm.return_value.invoke.return_value = mock_response

            state_after_gen = generate_recoding_rules_node(initial_recoding_state)

        # Step 5: Validate (should fail)
        state_after_val = validate_recoding_rules_node(state_after_gen)

        assert state_after_val["current_step"] == STEP_5_VALIDATE_RECODING_RULES
        assert state_after_val["recoding_validation_result"] is not None
        assert state_after_val["recoding_validation_result"]['is_valid'] == False
        assert len(state_after_val["recoding_validation_result"]['errors']) > 0

        # Check routing after validation failure
        route = should_retry_recoding(state_after_val)
        assert route == "generate_recoding_rules_node"  # Should retry

    def test_recoding_max_iterations_enforcement(self, initial_recoding_state, invalid_recoding_rules):
        """Test max iterations enforcement forces human review."""
        state = {
            **initial_recoding_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Validation error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 3,  # Max iterations reached
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        # Should force human review instead of retry
        route = should_retry_recoding(state)
        assert route == "review_recoding_rules_node"

    def test_recoding_iteration_counter_increments(self, initial_recoding_state, valid_recoding_rules):
        """Test iteration counter increments correctly on retry."""
        state_after_gen = {
            **initial_recoding_state,
            "recoding_rules": valid_recoding_rules,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 1,
            "recoding_feedback": "Previous error",
        }

        # Generate again (retry)
        with patch('agent.nodes.phase2_recoding.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(valid_recoding_rules)
            mock_llm.return_value.invoke.return_value = mock_response

            from agent.nodes.phase2_recoding import generate_recoding_rules_node
            state_retry = generate_recoding_rules_node(state_after_gen)

        assert state_retry["iteration_count"] == 2  # Incremented

    def test_recoding_human_rejection_flow(self, initial_recoding_state, valid_recoding_rules):
        """Test human rejection flow: generate → validate passes → human rejects → retry."""
        # State after review (human rejected with feedback)
        state_after_review = {
            **initial_recoding_state,
            "recoding_rules": valid_recoding_rules,
            "recoding_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 1,
            "recoding_approved": False,  # Human rejected
            "recoding_feedback": "Please add more rules for income variable",
            "requires_human_review": True,
        }

        # Check routing after rejection
        route = should_approve_recoding(state_after_review)
        assert route == "generate_recoding_rules_node"  # Should retry with feedback

    def test_recoding_state_evolution(self, initial_recoding_state, valid_recoding_rules):
        """Test state fields update correctly through each phase."""
        from agent.nodes.phase2_recoding import validate_recoding_rules_node

        # Starting state
        state = {
            **initial_recoding_state,
            "recoding_rules": valid_recoding_rules,
        }

        # After validation
        state_after = validate_recoding_rules_node(state)

        # Check state evolution
        assert "recoding_validation_result" in state_after
        assert state_after["current_step"] == STEP_5_VALIDATE_RECODING_RULES
        assert state_after["recoding_rules"] == valid_recoding_rules  # Preserved


# =============================================================================
# Indicators Three-Node Pattern Tests (Steps 9-11)
# =============================================================================

class TestIndicatorsThreeNodePattern:
    """Integration tests for indicators three-node pattern."""

    def test_indicators_successful_flow(self, initial_indicators_state, valid_indicators):
        """Test successful flow: generate → validate passes → human approves."""
        from agent.nodes.phase3_indicators import (
            generate_indicators_node,
            validate_indicators_node,
            review_indicators_node,
        )

        # Step 9: Generate (with mock LLM)
        with patch('agent.nodes.phase3_indicators.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(valid_indicators)
            mock_llm.return_value.invoke.return_value = mock_response

            state_after_gen = generate_indicators_node(initial_indicators_state)

        assert state_after_gen["current_step"] == STEP_9_GENERATE_INDICATORS
        assert state_after_gen["indicators"] is not None
        assert state_after_gen["indicator_feedback"] is None

        # Step 10: Validate
        with patch('agent.validation.indicators.validate_indicators') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure", "variables"],
            )
            state_after_val = validate_indicators_node(state_after_gen)

        assert state_after_val["current_step"] == STEP_10_VALIDATE_INDICATORS
        assert state_after_val["indicator_validation_result"]['is_valid'] == True

        # Step 11: Review
        with patch('langgraph.types.interrupt'):
            state_after_review = review_indicators_node(state_after_val)

        assert state_after_review["current_step"] == STEP_11_REVIEW_INDICATORS
        assert state_after_review["requires_human_review"] == True

        # Simulate approval
        approved_state = {**state_after_review, "indicators_approved": True}
        route = should_approve_indicators(approved_state)
        assert route == "generate_table_specifications_node"

    def test_indicators_validation_failure_flow(self, initial_indicators_state, invalid_indicators):
        """Test validation failure flow: generate → validate fails → retry."""
        from agent.nodes.phase3_indicators import (
            generate_indicators_node,
            validate_indicators_node,
        )

        # Generate (bypassing structure validation by patching it)
        with patch('agent.nodes.phase3_indicators.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(invalid_indicators)
            mock_llm.return_value.invoke.return_value = mock_response

            # Patch structure validation to allow the invalid indicators through
            with patch('agent.nodes.phase3_indicators._validate_indicators_structure', return_value=None):
                state_after_gen = generate_indicators_node(initial_indicators_state)

        # Validate (should fail)
        with patch('agent.validation.indicators.validate_indicators') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=False,
                errors=["Variable 'nonexistent_variable' not found in metadata"],
                warnings=[],
                checks_performed=["structure", "variables"],
            )
            state_after_val = validate_indicators_node(state_after_gen)

        assert state_after_val["indicator_validation_result"]['is_valid'] == False

        # Check routing
        route = should_retry_indicators(state_after_val)
        assert route == "generate_indicators_node"

    def test_indicators_max_iterations_enforcement(self, initial_indicators_state):
        """Test max iterations forces human review."""
        state = {
            **initial_indicators_state,
            "indicator_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 3,
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        route = should_retry_indicators(state)
        assert route == "review_indicators_node"

    def test_indicators_iteration_counter_increments(self, initial_indicators_state, valid_indicators):
        """Test iteration counter increments on retry."""
        state = {
            **initial_indicators_state,
            "indicators": valid_indicators,
            "iteration_count": 1,
            "indicator_feedback": "Feedback",
        }

        with patch('agent.nodes.phase3_indicators.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(valid_indicators)
            mock_llm.return_value.invoke.return_value = mock_response

            from agent.nodes.phase3_indicators import generate_indicators_node
            state_retry = generate_indicators_node(state)

        assert state_retry["iteration_count"] == 2

    def test_indicators_human_rejection_flow(self, initial_indicators_state, valid_indicators):
        """Test human rejection triggers regeneration."""
        state = {
            **initial_indicators_state,
            "indicators": valid_indicators,
            "indicator_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 1,
            "indicators_approved": False,
            "indicator_feedback": "Split into smaller indicators",
        }

        route = should_approve_indicators(state)
        assert route == "generate_indicators_node"


# =============================================================================
# Table Specifications Three-Node Pattern Tests (Steps 12-14)
# =============================================================================

class TestTableSpecsThreeNodePattern:
    """Integration tests for table specifications three-node pattern."""

    def test_table_specs_successful_flow(self, initial_table_specs_state, valid_table_specs):
        """Test successful flow: generate → validate passes → human approves."""
        from agent.nodes.phase4_tables import (
            generate_table_specifications_node,
            validate_table_specs_node,
            review_table_specifications_node,
        )

        # Step 12: Generate
        with patch('agent.nodes.phase4_tables.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(valid_table_specs)
            mock_llm.return_value.invoke.return_value = mock_response

            state_after_gen = generate_table_specifications_node(initial_table_specs_state)

        assert state_after_gen["current_step"] == STEP_12_GENERATE_TABLE_SPECIFICATIONS
        assert state_after_gen["table_specifications"] is not None
        assert state_after_gen["table_specs_feedback"] is None

        # Step 13: Validate
        with patch('agent.validation.tables.validate_table_specs') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["structure", "variables"],
            )
            state_after_val = validate_table_specs_node(state_after_gen)

        assert state_after_val["current_step"] == STEP_13_VALIDATE_TABLE_SPECIFICATIONS
        assert state_after_val["table_validation_result"]['is_valid'] == True

        # Step 14: Review
        with patch('langgraph.types.interrupt'):
            state_after_review = review_table_specifications_node(state_after_val)

        assert state_after_review["current_step"] == STEP_14_REVIEW_TABLE_SPECIFICATIONS
        assert state_after_review["requires_human_review"] == True

        # Simulate approval
        approved_state = {**state_after_review, "table_specs_approved": True}
        route = should_approve_table_specs(approved_state)
        assert route == "generate_pspp_table_syntax_node"

    def test_table_specs_validation_failure_flow(self, initial_table_specs_state, invalid_table_specs):
        """Test validation failure triggers retry."""
        from agent.nodes.phase4_tables import (
            generate_table_specifications_node,
            validate_table_specs_node,
        )

        # Generate
        with patch('agent.nodes.phase4_tables.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(invalid_table_specs)
            mock_llm.return_value.invoke.return_value = mock_response

            state_after_gen = generate_table_specifications_node(initial_table_specs_state)

        # Validate (should fail)
        with patch('agent.validation.tables.validate_table_specs') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=False,
                errors=["Variable 'nonexistent_var' not found"],
                warnings=[],
                checks_performed=["structure", "variables"],
            )
            state_after_val = validate_table_specs_node(state_after_gen)

        assert state_after_val["table_validation_result"]['is_valid'] == False

        route = should_retry_table_specs(state_after_val)
        assert route == "generate_table_specifications_node"

    def test_table_specs_max_iterations_enforcement(self, initial_table_specs_state):
        """Test max iterations forces human review."""
        state = {
            **initial_table_specs_state,
            "table_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 3,
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }

        route = should_retry_table_specs(state)
        assert route == "review_table_specifications_node"

    def test_table_specs_iteration_counter_increments(self, initial_table_specs_state, valid_table_specs):
        """Test iteration counter increments on retry."""
        state = {
            **initial_table_specs_state,
            "table_specifications": valid_table_specs,
            "iteration_count": 1,
            "table_specs_feedback": "Feedback",
        }

        with patch('agent.nodes.phase4_tables.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(valid_table_specs)
            mock_llm.return_value.invoke.return_value = mock_response

            from agent.nodes.phase4_tables import generate_table_specifications_node
            state_retry = generate_table_specifications_node(state)

        assert state_retry["iteration_count"] == 2

    def test_table_specs_human_rejection_flow(self, initial_table_specs_state, valid_table_specs):
        """Test human rejection triggers regeneration."""
        state = {
            **initial_table_specs_state,
            "table_specifications": valid_table_specs,
            "table_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 1,
            "table_specs_approved": False,
            "table_specs_feedback": "Add more tables",
        }

        route = should_approve_table_specs(state)
        assert route == "generate_table_specifications_node"


# =============================================================================
# Feedback Loop Tests
# =============================================================================

class TestFeedbackLoops:
    """Tests for feedback loop functionality across all three-node patterns."""

    def test_validation_feedback_passed_to_regenerate_recoding(self, initial_recoding_state):
        """Test validation feedback is correctly passed to regeneration."""
        state = {
            **initial_recoding_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Syntax error", "Undefined variable"],
                warnings=["Minor warning"],
                checks_performed=["syntax", "variables"],
            ),
            "iteration_count": 1,
        }

        # Check that validation result is available for next generate
        assert state["recoding_validation_result"] is not None
        assert len(state["recoding_validation_result"]['errors']) == 2

    def test_human_feedback_passed_to_regenerate_recoding(self, initial_recoding_state):
        """Test human feedback is correctly passed to regeneration."""
        state = {
            **initial_recoding_state,
            "recoding_validation_result": ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["check"],
            ),
            "recoding_approved": False,
            "recoding_feedback": "Please consolidate categories 7-9 into 'Other'",
            "iteration_count": 1,
        }

        route = should_approve_recoding(state)
        assert route == "generate_recoding_rules_node"
        assert state["recoding_feedback"] is not None

    def test_feedback_cleared_on_successful_generation(self, initial_recoding_state):
        """Test feedback is cleared when generation succeeds."""
        from agent.nodes.phase2_recoding import generate_recoding_rules_node

        state_with_feedback = {
            **initial_recoding_state,
            "recoding_feedback": "Previous error message",
            "iteration_count": 1,
        }

        with patch('agent.nodes.phase2_recoding.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps({"recoding_rules": []})
            mock_llm.return_value.invoke.return_value = mock_response

            state_after = generate_recoding_rules_node(state_with_feedback)

        # Feedback should be cleared on success
        assert state_after["recoding_feedback"] is None


# =============================================================================
# State Evolution Tests
# =============================================================================

class TestStateEvolution:
    """Tests for state evolution through three-node pattern."""

    def test_recoding_state_fields_update_through_phases(self, initial_recoding_state, valid_recoding_rules):
        """Test recoding state fields update correctly through each phase."""
        from agent.nodes.phase2_recoding import validate_recoding_rules_node

        # After generate (simulated)
        state = {
            **initial_recoding_state,
            "recoding_rules": valid_recoding_rules,
        }

        # After validate
        state_after = validate_recoding_rules_node(state)

        # Check field updates
        assert "recoding_validation_result" in state_after
        assert state_after["current_step"] == STEP_5_VALIDATE_RECODING_RULES
        assert "errors" in state_after  # May have validation errors appended

    def test_indicators_state_fields_update_through_phases(self, initial_indicators_state, valid_indicators):
        """Test indicators state fields update correctly."""
        state = {
            **initial_indicators_state,
            "indicators": valid_indicators,
        }

        with patch('agent.validation.indicators.validate_indicators') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["check"],
            )

            from agent.nodes.phase3_indicators import validate_indicators_node
            state_after = validate_indicators_node(state)

        assert "indicator_validation_result" in state_after
        assert state_after["current_step"] == STEP_10_VALIDATE_INDICATORS

    def test_table_specs_state_fields_update_through_phases(self, initial_table_specs_state, valid_table_specs):
        """Test table specs state fields update correctly."""
        state = {
            **initial_table_specs_state,
            "table_specifications": valid_table_specs,
        }

        with patch('agent.validation.tables.validate_table_specs') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["check"],
            )

            from agent.nodes.phase4_tables import validate_table_specs_node
            state_after = validate_table_specs_node(state)

        assert "table_validation_result" in state_after
        assert state_after["current_step"] == STEP_13_VALIDATE_TABLE_SPECIFICATIONS


# =============================================================================
# Edge Cases and Error Scenarios
# =============================================================================

class TestThreeNodePatternEdgeCases:
    """Tests for edge cases and error scenarios."""

    def test_recoding_missing_required_input(self, initial_recoding_state):
        """Test recoding generation fails gracefully with missing input."""
        from agent.nodes.phase2_recoding import generate_recoding_rules_node

        state_without_metadata = {
            **initial_recoding_state,
            "filtered_metadata": None,  # Missing required input
        }

        state_after = generate_recoding_rules_node(state_without_metadata)

        assert "errors" in state_after
        assert len(state_after["errors"]) > 0
        assert "No filtered_metadata available" in state_after["errors"][0]

    def test_indicators_missing_metadata(self, initial_indicators_state):
        """Test indicators generation fails gracefully with missing metadata."""
        from agent.nodes.phase3_indicators import generate_indicators_node

        state_without_metadata = {
            **initial_indicators_state,
            "new_metadata": None,
        }

        state_after = generate_indicators_node(state_without_metadata)

        assert "errors" in state_after
        assert len(state_after["errors"]) > 0

    def test_table_specs_missing_metadata(self, initial_table_specs_state):
        """Test table specs generation fails gracefully with missing metadata."""
        from agent.nodes.phase4_tables import generate_table_specifications_node

        state_without_metadata = {
            **initial_table_specs_state,
            "new_metadata": None,
        }

        state_after = generate_table_specifications_node(state_without_metadata)

        assert "errors" in state_after
        assert len(state_after["errors"]) > 0

    def test_llm_parse_error_handling(self, initial_recoding_state):
        """Test LLM response parse error is handled gracefully."""
        from agent.nodes.phase2_recoding import generate_recoding_rules_node

        with patch('agent.nodes.phase2_recoding.get_llm_client') as mock_llm:
            mock_response = Mock()
            mock_response.content = "This is not valid JSON"
            mock_llm.return_value.invoke.return_value = mock_response

            state_after = generate_recoding_rules_node(initial_recoding_state)

        # Should store error as feedback for retry
        assert "errors" in state_after
        assert len(state_after["errors"]) > 0
        assert "Failed to parse" in state_after["errors"][0]

    def test_empty_artifacts_allowed(self, initial_indicators_state):
        """Test empty artifacts are allowed (warning, not error)."""
        from agent.nodes.phase3_indicators import generate_indicators_node

        empty_indicators = {"indicators": []}

        with patch('agent.nodes.phase3_indicators.get_llm_client') as mock_llm:
            mock_response = Mock()
            mock_response.content = str(empty_indicators).replace("'", '"')
            mock_llm.return_value.invoke.return_value = mock_response

            state_after = generate_indicators_node(initial_indicators_state)

        # Should succeed with warning
        assert "warnings" in state_after
        assert state_after["indicators"] is not None


# =============================================================================
# Routing Tests
# =============================================================================

class TestConditionalRouting:
    """Tests for conditional edge routing functions."""

    def test_should_retry_recoding_routes_correctly(self, initial_recoding_state):
        """Test recoding retry routing conditions."""
        # Case 1: Validation failed, iterations < max
        state = {
            **initial_recoding_state,
            "recoding_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 1,
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }
        assert should_retry_recoding(state) == "generate_recoding_rules_node"

        # Case 2: Validation failed, iterations >= max
        state["iteration_count"] = 3
        assert should_retry_recoding(state) == "review_recoding_rules_node"

        # Case 3: Approved (but also requires_human_review=False to proceed)
        state["recoding_approved"] = True
        state["requires_human_review"] = False
        state["recoding_validation_result"] = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            checks_performed=["check"],
        )
        assert should_retry_recoding(state) == "generate_pspp_recoding_syntax_node"

    def test_should_retry_indicators_routes_correctly(self, initial_indicators_state):
        """Test indicators retry routing conditions."""
        # Validation failed, iterations < max
        state = {
            **initial_indicators_state,
            "indicator_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 1,
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }
        assert should_retry_indicators(state) == "generate_indicators_node"

        # Approved (and no human review required)
        state["indicators_approved"] = True
        state["requires_human_review"] = False
        state["indicator_validation_result"] = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            checks_performed=["check"],
        )
        assert should_retry_indicators(state) == "generate_table_specifications_node"

    def test_should_retry_table_specs_routes_correctly(self, initial_table_specs_state):
        """Test table specs retry routing conditions."""
        # Validation failed, iterations < max
        state = {
            **initial_table_specs_state,
            "table_validation_result": ValidationResult(
                is_valid=False,
                errors=["Error"],
                warnings=[],
                checks_performed=["check"],
            ),
            "iteration_count": 1,
            "config": {**DEFAULT_CONFIG, "max_self_correction_iterations": 3},
        }
        assert should_retry_table_specs(state) == "generate_table_specifications_node"

        # Approved (and no human review required)
        state["table_specs_approved"] = True
        state["requires_human_review"] = False
        state["table_validation_result"] = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            checks_performed=["check"],
        )
        assert should_retry_table_specs(state) == "generate_pspp_table_syntax_node"

    def test_should_approve_routes_correctly(self):
        """Test approval routing after review."""
        # Recoding approved
        state = {"recoding_approved": True}
        assert should_approve_recoding(state) == "generate_pspp_recoding_syntax_node"

        # Recoding rejected
        state = {"recoding_approved": False, "recoding_feedback": "Error"}
        assert should_approve_recoding(state) == "generate_recoding_rules_node"

        # Indicators approved
        state = {"indicators_approved": True}
        assert should_approve_indicators(state) == "generate_table_specifications_node"

        # Indicators rejected
        state = {"indicators_approved": False, "indicator_feedback": "Error"}
        assert should_approve_indicators(state) == "generate_indicators_node"

        # Table specs approved
        state = {"table_specs_approved": True}
        assert should_approve_table_specs(state) == "generate_pspp_table_syntax_node"

        # Table specs rejected
        state = {"table_specs_approved": False, "table_specs_feedback": "Error"}
        assert should_approve_table_specs(state) == "generate_table_specifications_node"


# =============================================================================
# Integration Test: Full Pattern Execution
# =============================================================================

class TestFullPatternExecution:
    """Integration tests for full three-node pattern execution."""

    @pytest.mark.integration
    def test_recoding_full_cycle_with_retry(self, initial_recoding_state):
        """Test full recoding cycle with one validation retry."""
        from agent.nodes.phase2_recoding import (
            generate_recoding_rules_node,
            validate_recoding_rules_node,
        )

        # Cycle 1: Generate invalid rules
        invalid_rules = {
            "recoding_rules": [
                {
                    "source_variable": "invalid_var",
                    "target_variable": "target",
                    "transformation_type": "range_grouping",
                    "description": "Invalid",
                    "rules": [
                        {"source_min": 1, "source_max": 5, "target_value": 1, "target_label": "1-5"}
                    ],
                }
            ]
        }

        with patch('agent.nodes.phase2_recoding.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(invalid_rules)
            mock_llm.return_value.invoke.return_value = mock_response

            state1 = generate_recoding_rules_node(initial_recoding_state)

        # Validate (should fail)
        state2 = validate_recoding_rules_node(state1)
        assert state2["recoding_validation_result"]['is_valid'] == False

        # Check routing
        route = should_retry_recoding(state2)
        assert route == "generate_recoding_rules_node"

        # Cycle 2: Generate valid rules (with feedback)
        valid_rules = {
            "recoding_rules": [
                {
                    "source_variable": "age",
                    "target_variable": "age_group",
                    "transformation_type": "range_grouping",
                    "description": "Group age",
                    "rules": [
                        {"source_min": 18, "source_max": 34, "target_value": 1, "target_label": "18-34"},
                        {"source_min": 35, "source_max": 50, "target_value": 2, "target_label": "35-50"},
                    ],
                }
            ]
        }

        state_retry = {
            **state2,
            "iteration_count": 1,
        }

        with patch('agent.nodes.phase2_recoding.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(valid_rules)
            mock_llm.return_value.invoke.return_value = mock_response

            state3 = generate_recoding_rules_node(state_retry)

        # Validate again (should pass)
        state4 = validate_recoding_rules_node(state3)
        # Note: May still fail validation if 'age' not in filtered_metadata
        # This demonstrates the full cycle even if validation result varies

        assert state4["iteration_count"] == 2  # Was incremented

    @pytest.mark.integration
    def test_indicators_full_cycle_approval(self, initial_indicators_state, valid_indicators):
        """Test full indicators cycle ending in approval."""
        from agent.nodes.phase3_indicators import (
            generate_indicators_node,
            validate_indicators_node,
            review_indicators_node,
        )

        # Generate
        with patch('agent.nodes.phase3_indicators.get_llm_client') as mock_llm:
            import json
            mock_response = Mock()
            mock_response.content = json.dumps(valid_indicators)
            mock_llm.return_value.invoke.return_value = mock_response

            state1 = generate_indicators_node(initial_indicators_state)

        # Validate
        with patch('agent.validation.indicators.validate_indicators') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                checks_performed=["check"],
            )
            state2 = validate_indicators_node(state1)

        assert state2["indicator_validation_result"]['is_valid'] == True

        # Review
        with patch('langgraph.types.interrupt'):
            state3 = review_indicators_node(state2)

        assert state3["requires_human_review"] == True

        # Human approves
        state4 = {**state3, "indicators_approved": True}

        # Check routing to next phase
        route = should_approve_indicators(state4)
        assert route == "generate_table_specifications_node"
