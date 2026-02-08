"""
Unit Tests for Phase 8: HTML Dashboard Node (Step 22)

This module tests the HTML dashboard generation node.
"""

import pytest
from unittest.mock import patch, Mock

from agent.state import STEP_20_APPLY_FILTER_TO_TABLES, STEP_22_GENERATE_HTML_DASHBOARD
from agent.nodes.phase8_html_dashboard import (
    generate_html_dashboard_node,
)


# =============================================================================
# Phase 8: HTML Dashboard Nodes
# =============================================================================
# Phase 8: HTML Dashboard Node (Step 22)
# =============================================================================

class TestGenerateHtmlDashboardNode:
    """Tests for generate_html_dashboard_node (Step 22)."""

    def test_generate_html_dashboard_node_success(self, populated_state, tmp_path):
        """Test successful HTML dashboard generation."""
        # Create a mock cross_table_file
        cross_table_file = tmp_path / "cross_table.json"
        import json
        with open(cross_table_file, 'w') as f:
            json.dump({"tables": []}, f)

        state = {
            **populated_state,
            "cross_table_file": str(cross_table_file),
            "statistical_summary": {
                "tables": [],
            },
            "filter_list": {
                "filters": [],
            },
            "config": {"output_dir": str(tmp_path)},
        }

        with patch('agent.nodes.phase8_html_dashboard._generate_html_dashboard') as mock_create:
            mock_create.return_value = "<html></html>"

            result = generate_html_dashboard_node(state)

            assert result["current_step"] == STEP_22_GENERATE_HTML_DASHBOARD
            assert result["html_dashboard_file"] is not None

    def test_generate_html_dashboard_node_no_data(self, populated_state):
        """Test HTML dashboard generation without data."""
        state = {
            **populated_state,
            "filtered_tables": None,
            "statistical_summary": None,
        }

        result = generate_html_dashboard_node(state)

        assert result["current_step"] == STEP_22_GENERATE_HTML_DASHBOARD

