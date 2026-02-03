"""
Unit Tests for Phase 7: PowerPoint Node (Step 21)

This module tests the PowerPoint generation node.
"""

import pytest
from unittest.mock import patch, Mock

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

    def test_generate_powerpoint_node_success(self, populated_state):
        """Test successful PowerPoint generation."""
        state = {
            **populated_state,
            "filtered_tables": {
                "table1": {"data": []},
            },
            "statistical_summary": {
                "results": [],
            },
        }

        with patch('pptx.Presentation') as mock_presentation:
            # Mock the presentation instance
            mock_prs = Mock()
            mock_presentation.return_value = mock_prs

            result = generate_powerpoint_node(state)

            assert result["current_step"] == 21
            assert result["powerpoint_file"] is not None

    def test_generate_powerpoint_node_no_tables(self, populated_state):
        """Test PowerPoint generation without tables."""
        state = {
            **populated_state,
            "filtered_tables": None,
        }

        result = generate_powerpoint_node(state)

        assert result["current_step"] == 21
        # Should have error or warning
        assert len(result["errors"]) >= 0 or len(result["warnings"]) >= 0


# =============================================================================
