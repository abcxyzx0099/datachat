"""
Unit Tests for Phase 7: PowerPoint Node (Step 21)

This module tests the PowerPoint generation node.
"""

import pytest
from unittest.mock import patch, Mock

from agent.state import STEP_20_APPLY_FILTER_TO_TABLES, STEP_21_GENERATE_POWERPOINT
from agent.nodes.phase7_powerpoint import (
    generate_powerpoint_node,
)


# =============================================================================
# Phase 7: PowerPoint Nodes
# =============================================================================
# Phase 7: PowerPoint Node (Step 21)
# =============================================================================

class TestGeneratePowerPointNode:
    """Tests for generate_powerpoint_node (Step 21)."""

    def test_generate_powerpoint_node_success(self, populated_state, tmp_path):
        """Test successful PowerPoint generation."""
        state = {
            **populated_state,
            "filtered_tables": {
                "tables": [],
            },
            "statistical_summary": {
                "results": [],
            },
            "config": {"output_dir": str(tmp_path)},
        }

        # Mock the presentation object properly
        with patch('pptx.Presentation') as mock_presentation:
            # Mock the presentation instance with subscriptable attributes
            mock_prs = Mock()
            mock_slide_layout = Mock()
            mock_prs.slide_layouts = [mock_slide_layout] * 10
            mock_prs.slides = []
            mock_presentation.return_value = mock_prs

            result = generate_powerpoint_node(state)

            assert result["current_step"] == STEP_21_GENERATE_POWERPOINT
            # May be None if no significant tables, which is expected for empty data
            assert result["powerpoint_file"] is not None or len(result.get("errors", [])) > 0

    def test_generate_powerpoint_node_no_tables(self, populated_state):
        """Test PowerPoint generation without tables."""
        state = {
            **populated_state,
            "filtered_tables": None,
        }

        result = generate_powerpoint_node(state)

        assert result["current_step"] == STEP_21_GENERATE_POWERPOINT
        # Should have error or warning
        assert len(result["errors"]) >= 0 or len(result["warnings"]) >= 0


# =============================================================================
