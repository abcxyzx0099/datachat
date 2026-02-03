"""
Unit Tests for Phase 8: HTML Dashboard Node (Step 22)

This module tests the HTML dashboard generation node.
"""

import pytest
from unittest.mock import patch, Mock

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

    def test_generate_html_dashboard_node_success(self, populated_state):
        """Test successful HTML dashboard generation."""
        state = {
            **populated_state,
            "filtered_tables": {
                "table1": {"data": []},
            },
            "statistical_summary": {
                "results": [],
            },
            "new_metadata": {"variables": {}},
        }

        with patch('agent.nodes.phase8_html_dashboard._generate_html_dashboard') as mock_create:
            mock_create.return_value = "/output/dashboard.html"

            result = generate_html_dashboard_node(state)

            assert result["current_step"] == 22
            assert result["html_dashboard_file"] is not None

    def test_generate_html_dashboard_node_no_data(self, populated_state):
        """Test HTML dashboard generation without data."""
        state = {
            **populated_state,
            "filtered_tables": None,
            "statistical_summary": None,
        }

        result = generate_html_dashboard_node(state)

        assert result["current_step"] == 22

