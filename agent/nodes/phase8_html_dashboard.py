"""
Phase 8: HTML Dashboard Generation Node (Step 22)

This module contains the node for generating interactive HTML dashboards:
- Step 22: generate_html_dashboard_node - Create interactive HTML dashboard

Dashboard Features:
- All tables displayed (not just significant ones)
- Sidebar navigation for quick table access
- Significance highlighting (green border = significant, red = not significant)
- Interactive Chart.js charts with tooltips
- Enhanced filtering: significance, p-value threshold, Cramer's V threshold
- Combined filter application (search + significance + p-value + Cramer's V)
- Sorting by table name, p-value, or Cramer's V
- CSV export (individual tables or all visible tables)
- Dynamic summary statistics that update with filters
- Real-time filter status display
- Responsive design
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from agent.state import WorkflowState, STEP_22_GENERATE_HTML_DASHBOARD
from agent.config import DEFAULT_CONFIG
from agent.nodes.phase7_powerpoint import select_chart_type, ChartType
from agent.styling import (
    get_css_variables,
    get_js_chart_colors,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_ACCENT,
    COLOR_SIGNIFICANT,
    COLOR_NOT_SIGNIFICANT,
    COLOR_TEXT_DARK,
    COLOR_TEXT_LIGHT,
    COLOR_BACKGROUND,
    COLOR_BORDER,
    COLOR_TABLE_HEADER,
    COLOR_HOVER,
)
from agent.utils.tracing import trace_node

logger = logging.getLogger(__name__)


# =============================================================================
# Step 22: Generate HTML Dashboard
# =============================================================================

@trace_node("Step 22: Generate HTML Dashboard")
def generate_html_dashboard_node(state: WorkflowState) -> WorkflowState:
    """
    Step 22: Generate interactive HTML dashboard with all analysis results.

    This node creates a comprehensive, self-contained HTML dashboard that
    displays all cross-tabulation tables with:
    - Interactive Chart.js visualizations
    - Sidebar navigation
    - Significance highlighting
    - Filtering and sorting capabilities
    - Statistical summaries (Chi-square, p-value, Cramer's V)

    Unlike the PowerPoint (Step 21), the dashboard includes ALL tables,
    not just significant ones, allowing for exploratory analysis.

    Args:
        state: Current workflow state. Must contain:
            - cross_table_file: Path to cross_table.json (Step 16)
            - statistical_summary: Statistical test results (Step 18)
            - filter_list: Pass/fail status for all tables (Step 19)
            - config: Configuration dict (optional, uses DEFAULT_CONFIG)

    Returns:
        Updated workflow state with:
            - html_dashboard_file: Path to output/dashboard.html
            - current_step: Set to STEP_22_GENERATE_HTML_DASHBOARD
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Example:
        >>> state = {
        ...     "cross_table_file": "output/cross_table.json",
        ...     "statistical_summary": {"tables": [...]},
        ...     "filter_list": {"filters": [...]}
        ... }
        >>> new_state = generate_html_dashboard_node(state)
        >>> print(new_state["html_dashboard_file"])
        'output/dashboard.html'
    """
    logger.info("Step 22: Generating HTML dashboard")

    # Get required inputs from state
    cross_table_file = state.get("cross_table_file")
    statistical_summary = state.get("statistical_summary")
    filter_list = state.get("filter_list")
    config = state.get("config", DEFAULT_CONFIG)

    # Validate required inputs
    if not cross_table_file:
        error_msg = "No cross_table_file available in state. Step 16 must complete first."
        logger.error(error_msg)
        return {
            **state,
            "current_step": STEP_22_GENERATE_HTML_DASHBOARD,
            "errors": state.get("errors", []) + [error_msg],
        }

    if not statistical_summary:
        error_msg = "No statistical_summary available in state. Step 18 must complete first."
        logger.error(error_msg)
        return {
            **state,
            "current_step": STEP_22_GENERATE_HTML_DASHBOARD,
            "errors": state.get("errors", []) + [error_msg],
        }

    try:
        # Load cross-table data
        logger.info(f"Loading cross-table data from: {cross_table_file}")
        if not os.path.exists(cross_table_file):
            error_msg = f"Cross-table file not found: {cross_table_file}"
            logger.error(error_msg)
            return {
                **state,
                "current_step": STEP_22_GENERATE_HTML_DASHBOARD,
                "errors": state.get("errors", []) + [error_msg],
            }

        with open(cross_table_file, 'r', encoding='utf-8') as f:
            cross_table_data = json.load(f)

        # Generate HTML dashboard
        logger.info("Generating HTML dashboard content")
        html_content = _generate_html_dashboard(
            cross_table_data=cross_table_data,
            statistical_summary=statistical_summary,
            filter_list=filter_list,
            config=config
        )

        # Create output directory
        output_dir = Path(config.get("output_dir", "output"))
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write HTML file
        dashboard_path = output_dir / "dashboard.html"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML dashboard written to: {dashboard_path}")
        logger.info(f"Dashboard size: {len(html_content)} characters")

        # Log summary
        tables = cross_table_data.get("tables", [])
        stats_tables = statistical_summary.get("tables", [])
        significant_count = statistical_summary.get("significant_tables", 0)

        logger.info(
            f"Dashboard generation complete: "
            f"{len(tables)} tables, {significant_count} significant"
        )

        return {
            **state,
            "current_step": STEP_22_GENERATE_HTML_DASHBOARD,
            "html_dashboard_file": str(dashboard_path),
        }

    except Exception as e:
        error_msg = f"Unexpected error generating HTML dashboard: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": STEP_22_GENERATE_HTML_DASHBOARD,
            "errors": state.get("errors", []) + [error_msg],
        }


def _generate_html_dashboard(
    cross_table_data: Dict[str, Any],
    statistical_summary: Dict[str, Any],
    filter_list: Optional[Dict[str, Any]],
    config: Dict[str, Any]
) -> str:
    """
    Generate the complete HTML dashboard content.

    Creates a self-contained HTML file with embedded CSS and JavaScript
    for an interactive dashboard experience.

    Args:
        cross_table_data: Cross-table data from cross_table.json
        statistical_summary: Statistical test results
        filter_list: Optional filter criteria
        config: Configuration dict

    Returns:
        Complete HTML document as string
    """
    # Extract data
    tables = cross_table_data.get("tables", [])
    stats_tables = statistical_summary.get("tables", [])

    # Create a lookup dictionary for statistics by table name
    stats_lookup = {t.get("table_name", ""): t for t in stats_tables}

    # Create filter lookup
    filter_lookup = {}
    if filter_list:
        filters = filter_list.get("filters", [])
        filter_lookup = {f.get("table_id", ""): f for f in filters}

    # Build summary statistics
    total_tables = len(tables)
    significant_count = sum(1 for t in stats_tables if t.get("is_significant", False))
    valid_count = sum(1 for t in stats_tables if t.get("is_valid", True))

    # ==========================================================================
    # Generate HTML structure
    # ==========================================================================
    html_lines = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>Survey Analysis Dashboard</title>',
        '    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>',
        '',
        _generate_css(),
        '</head>',
        '<body>',
        '    <div class="sidebar">',
        '        <div class="sidebar-header">',
        '            <h3>Navigation</h3>',
        '        </div>',
        '        <div class="search-box">',
        '            <input type="text" id="search-input" placeholder="Search tables...">',
        '        </div>',
        '        <ul id="table-list">',
        _generate_sidebar_items(tables, stats_lookup),
        '        </ul>',
        '        <div class="filters">',
        '            <h4>Filters</h4>',
        '            <div class="current-filters" id="current-filters">',
        '                <h5>Current Status</h5>',
        '                <p>Showing: <span class="count" id="filter-count">all</span></p>',
        '            </div>',
        '            <label>',
        '                <input type="checkbox" id="show-significant-only">',
        '                Significant only',
        '            </label>',
        '            <label>',
        '                <input type="checkbox" id="show-charts" checked>',
        '                Show charts',
        '            </label>',
        '            <div class="range-filter">',
        '                <h5>Max P-value</h5>',
        '                <input type="range" id="max-p-value" min="0" max="1" step="0.01" value="1">',
        '                <span id="max-p-value-display">1.00</span>',
        '            </div>',
        '            <div class="range-filter">',
        '                <h5>Min Cramer\'s V</h5>',
        '                <input type="range" id="min-cramers-v" min="0" max="1" step="0.01" value="0">',
        '                <span id="min-cramers-v-display">0.00</span>',
        '            </div>',
        '            <div class="sort-section">',
        '                <h5>Sort by</h5>',
        '                <select id="sort-select">',
        '                    <option value="name">Table name</option>',
        '                    <option value="p-value">P-value</option>',
        '                    <option value="cramers-v">Cramer\'s V</option>',
        '                </select>',
        '            </div>',
        '            <div class="export-section">',
        '                <h5>Export</h5>',
        '                <button id="export-all-btn" class="export-btn">Export All (CSV)</button>',
        '            </div>',
        '        </div>',
        '    </div>',
        '',
        '    <div class="content">',
        '        <h1>Survey Analysis Dashboard</h1>',
        '',
        _generate_summary_section(total_tables, significant_count, valid_count, statistical_summary),
        '',
        '        <div id="tables">',
        _generate_table_cards(tables, stats_lookup, filter_lookup),
        '        </div>',
        '    </div>',
        '',
        _generate_javascript(tables, stats_lookup),
        '</body>',
        '</html>'
    ]

    return "\n".join(html_lines)


def _generate_css() -> str:
    """
    Generate CSS styles for the dashboard with professional market research theme.

    Returns:
        CSS style block as string
    """
    # Get CSS variables from styling module
    css_vars = get_css_variables()

    return f"""    <style>
        {css_vars}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--color-text);
            background-color: var(--color-bg);
        }}

        /* Sidebar Styles */
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            background: linear-gradient(180deg, var(--color-primary) 0%, #{COLOR_PRIMARY}cc 100%);
            color: white;
            overflow-y: auto;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            z-index: 1000;
        }}

        .sidebar-header {{
            padding: 20px;
            background: rgba(0, 0, 0, 0.1);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .sidebar-header h3 {{
            margin: 0;
            font-size: 1.2em;
            font-weight: 600;
        }}

        .search-box {{
            padding: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .search-box input {{
            width: 100%;
            padding: 10px 12px;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            background: rgba(255, 255, 255, 0.9);
        }}

        .search-box input:focus {{
            outline: 2px solid var(--color-secondary);
            background: white;
        }}

        #table-list {{
            list-style: none;
            padding: 0;
        }}

        #table-list li {{
            padding: 12px 20px;
            cursor: pointer;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            transition: background 0.2s;
            font-size: 0.9em;
        }}

        #table-list li:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}

        #table-list li.active {{
            background: var(--color-significant);
        }}

        .filters {{
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(0, 0, 0, 0.05);
        }}

        .filters h4 {{
            margin-bottom: 15px;
            font-size: 1em;
            font-weight: 600;
        }}

        .filters h5 {{
            margin: 15px 0 10px 0;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: rgba(255, 255, 255, 0.8);
        }}

        .filters label {{
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            cursor: pointer;
            font-size: 0.9em;
        }}

        .filters input[type="checkbox"] {{
            margin-right: 10px;
            width: 16px;
            height: 16px;
            cursor: pointer;
        }}

        .sort-section select {{
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.9);
            font-size: 0.9em;
            cursor: pointer;
        }}

        .range-filter {{
            margin-bottom: 20px;
        }}

        .range-filter h5 {{
            margin: 0 0 10px 0;
            font-size: 0.85em;
        }}

        .range-filter input[type="range"] {{
            width: 100%;
            margin-bottom: 8px;
            cursor: pointer;
        }}

        .range-filter span {{
            font-size: 0.85em;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 600;
        }}

        .export-section {{
            margin-top: 20px;
        }}

        .export-section h5 {{
            margin: 0 0 10px 0;
            font-size: 0.85em;
        }}

        .export-btn {{
            width: 100%;
            padding: 12px;
            background: var(--color-secondary);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 600;
            transition: all 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .export-btn:hover {{
            background: #{COLOR_SECONDARY}cc;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}

        .export-btn:active {{
            transform: translateY(0);
        }}

        .export-btn:disabled {{
            background: rgba(255, 255, 255, 0.3);
            cursor: not-allowed;
            transform: none;
        }}

        .table-exports {{
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }}

        .table-export-btn {{
            padding: 8px 16px;
            background: var(--color-secondary);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: 600;
            transition: all 0.2s;
        }}

        .table-export-btn:hover {{
            background: #{COLOR_SECONDARY}cc;
            transform: translateY(-1px);
        }}

        .current-filters {{
            background: rgba(0, 0, 0, 0.15);
            padding: 12px 15px;
            margin-top: 15px;
            border-radius: 6px;
            font-size: 0.85em;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .current-filters h5 {{
            margin: 0 0 8px 0;
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.9);
        }}

        .current-filters p {{
            margin: 3px 0;
            color: rgba(255, 255, 255, 0.8);
        }}

        .current-filters .count {{
            color: var(--color-significant);
            font-weight: bold;
        }}

        /* Content Styles */
        .content {{
            margin-left: 280px;
            padding: 30px;
            max-width: 1400px;
        }}

        h1 {{
            color: var(--color-primary);
            margin-bottom: 30px;
            font-size: 2.2em;
            font-weight: 700;
        }}

        /* Summary Section */
        .summary {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            border: 1px solid var(--color-border);
        }}

        .summary h2 {{
            color: var(--color-primary);
            margin-bottom: 25px;
            font-size: 1.6em;
            font-weight: 600;
        }}

        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
        }}

        .stat-card {{
            background: var(--color-bg);
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid var(--color-border);
            transition: all 0.2s;
        }}

        .stat-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}

        .stat-card .number {{
            font-size: 2.5em;
            font-weight: 700;
            color: var(--color-primary);
            line-height: 1;
        }}

        .stat-card .label {{
            color: var(--color-text-light);
            margin-top: 10px;
            font-size: 0.95em;
        }}

        /* Table Card Styles */
        .table-card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 5px solid var(--color-border);
            transition: all 0.2s;
        }}

        .table-card:hover {{
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
            transform: translateY(-1px);
        }}

        .table-card.significant {{
            border-left-color: var(--color-significant);
            background: linear-gradient(to right, rgba(72, 187, 120, 0.02), white 50px);
        }}

        .table-card.not-significant {{
            border-left-color: var(--color-not-significant);
            background: linear-gradient(to right, rgba(229, 62, 62, 0.02), white 50px);
        }}

        .table-card.hidden {{
            display: none;
        }}

        .table-card h3 {{
            color: var(--color-primary);
            margin-bottom: 20px;
            font-size: 1.4em;
            font-weight: 600;
        }}

        .chart-container {{
            position: relative;
            height: 320px;
            margin: 25px 0;
            padding: 15px;
            background: var(--color-bg);
            border-radius: 8px;
            border: 1px solid var(--color-border);
        }}

        .chart-container.hidden {{
            display: none;
        }}

        /* Table Styles */
        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.95em;
        }}

        table.data-table th,
        table.data-table td {{
            padding: 14px;
            text-align: center;
            border: 1px solid var(--color-border);
        }}

        table.data-table th {{
            background: var(--color-table-header);
            font-weight: 600;
            color: var(--color-primary);
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        table.data-table tr:hover {{
            background: var(--color-hover);
        }}

        table.data-table td strong {{
            color: var(--color-primary);
        }}

        table.data-table small {{
            color: var(--color-text-light);
            font-size: 0.85em;
        }}

        /* Stats Footer */
        .stats-footer {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid var(--color-border);
            font-size: 0.9em;
            color: var(--color-text-light);
            background: var(--color-bg);
            padding: 15px;
            border-radius: 8px;
        }}

        .stats-footer .significant-badge {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 12px;
        }}

        .stats-footer .significant-badge.yes {{
            background: var(--color-significant);
            color: white;
        }}

        .stats-footer .significant-badge.no {{
            background: var(--color-not-significant);
            color: white;
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .sidebar {{
                width: 100%;
                height: auto;
                position: relative;
            }}

            .content {{
                margin-left: 0;
                padding: 20px;
            }}

            .summary-stats {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}

            .table-card {{
                padding: 20px;
            }}

            .chart-container {{
                height: 250px;
            }}

            h1 {{
                font-size: 1.6em;
            }}
        }}

        @media (max-width: 480px) {{
            .summary-stats {{
                grid-template-columns: 1fr;
            }}

            .stat-card {{
                padding: 20px;
            }}

            .stat-card .number {{
                font-size: 2em;
            }}
        }}

        /* Scrollbar Styles */
        ::-webkit-scrollbar {{
            width: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--color-bg);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--color-text-light);
            border-radius: 5px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--color-primary);
        }}

        /* Accessibility - Focus states */
        button:focus-visible,
        input:focus-visible,
        select:focus-visible {{
            outline: 3px solid var(--color-accent);
            outline-offset: 2px;
        }}
    </style>"""


def _generate_sidebar_items(
    tables: List[Dict[str, Any]],
    stats_lookup: Dict[str, Any]
) -> str:
    """
    Generate sidebar navigation items.

    Args:
        tables: List of table data dictionaries
        stats_lookup: Dictionary mapping table names to statistics

    Returns:
        HTML string for sidebar items
    """
    items = []

    for table in tables:
        table_id = table.get("table_id", "unknown")
        table_name = table.get("table_name", table_id)

        # Get significance status
        stats = stats_lookup.get(table_name, {})
        is_significant = stats.get("is_significant", False)

        # Add indicator
        indicator = "✓" if is_significant else "✗"

        items.append(f'            <li data-table-id="{table_id}">')
        items.append(f'                {indicator} {table_name}')
        items.append(f'            </li>')

    return "\n".join(items)


def _generate_summary_section(
    total_tables: int,
    significant_count: int,
    valid_count: int,
    statistical_summary: Dict[str, Any]
) -> str:
    """
    Generate the summary section HTML.

    Args:
        total_tables: Total number of tables
        significant_count: Number of significant tables
        valid_count: Number of valid tables
        statistical_summary: Statistical summary dict

    Returns:
        HTML string for summary section
    """
    significance_level = statistical_summary.get("significance_level", 0.05)

    lines = [
        '        <div class="summary">',
        '            <h2>Analysis Summary</h2>',
        '            <div class="summary-stats" id="summary-stats">',
        f'                <div class="stat-card">',
        f'                    <div class="number" id="stat-total">{total_tables}</div>',
        f'                    <div class="label">Total Tables</div>',
        f'                </div>',
        f'                <div class="stat-card">',
        f'                    <div class="number" id="stat-visible">{total_tables}</div>',
        f'                    <div class="label">Visible Tables</div>',
        f'                </div>',
        f'                <div class="stat-card">',
        f'                    <div class="number" id="stat-significant">{significant_count}</div>',
        f'                    <div class="label">Significant (p < {significance_level})</div>',
        f'                </div>',
        f'                <div class="stat-card">',
        f'                    <div class="number">{significant_count/total_tables*100 if total_tables > 0 else 0:.1f}%</div>',
        f'                    <div class="label">Significance Rate</div>',
        f'                </div>',
        '            </div>',
        '        </div>'
    ]

    return "\n".join(lines)


def _generate_table_cards(
    tables: List[Dict[str, Any]],
    stats_lookup: Dict[str, Any],
    filter_lookup: Dict[str, Any]
) -> str:
    """
    Generate HTML for all table cards.

    Args:
        tables: List of table data dictionaries
        stats_lookup: Dictionary mapping table names to statistics
        filter_lookup: Dictionary mapping table names to filter results

    Returns:
        HTML string for all table cards
    """
    cards = []

    for table in tables:
        table_id = table.get("table_id", "unknown")
        table_name = table.get("table_name", table_id)
        row_var = table.get("row_variable", "Unknown")
        col_var = table.get("column_variable", "Unknown")

        # Get statistics
        stats = stats_lookup.get(table_name, {})
        is_significant = stats.get("is_significant", False)
        is_valid = stats.get("is_valid", True)
        chi_square = stats.get("chi_square")
        p_value = stats.get("p_value")
        cramers_v = stats.get("cramers_v")
        interpretation = stats.get("interpretation", "N/A")

        # Get filter result
        filter_result = filter_lookup.get(table_name, {})
        include = filter_result.get("include", False)

        # Determine significance class
        significance_class = "significant" if is_significant else "not-significant"
        include_class = "data-include='true'" if include else "data-include='false'"

        # Get table data
        data_section = table.get("data", {})
        row_labels = data_section.get("row_labels", [])
        column_labels = data_section.get("column_labels", [])
        counts = data_section.get("counts", [])
        column_percentages = data_section.get("column_percentages", [])

        # Build table HTML
        table_html = _generate_data_table(row_labels, column_labels, counts, column_percentages)

        # Select chart type
        chart_type = select_chart_type(table)

        # Build card HTML
        cards.append(f'        <div class="table-card {significance_class}" '
                    f'id="table-{table_id}" data-table-name="{table_name}" '
                    f'data-p-value="{p_value or 1}" data-cramers-v="{cramers_v or 0}" '
                    f'data-significant="{str(is_significant).lower()}" '
                    f'{include_class}>')
        cards.append(f'            <div class="table-exports">')
        cards.append(f'                <button class="table-export-btn" data-table-id="{table_id}">Export CSV</button>')
        cards.append(f'            </div>')
        cards.append(f'            <h3>{row_var} × {col_var}</h3>')
        cards.append(f'            <div class="chart-container" id="chart-container-{table_id}">')
        cards.append(f'                <canvas id="chart-{table_id}"></canvas>')
        cards.append(f'            </div>')
        cards.append(table_html)

        # Stats footer
        if is_valid:
            sig_class = "yes" if is_significant else "no"
            sig_text = "Significant" if is_significant else "Not Significant"
            chi_str = f"{chi_square:.4f}" if chi_square is not None else "N/A"
            p_str = f"{p_value:.4f}" if p_value is not None else "N/A"
            v_str = f"{cramers_v:.4f}" if cramers_v is not None else "N/A"

            cards.append(f'            <div class="stats-footer">')
            cards.append(f'                χ² = {chi_str}, ')
            cards.append(f'                p = {p_str}, ')
            cards.append(f'                V = {v_str} ')
            cards.append(f'                ({interpretation})')
            cards.append(f'                <span class="significant-badge {sig_class}">{sig_text}</span>')
            cards.append(f'            </div>')
        else:
            error = stats.get("error", "Unknown error")
            cards.append(f'            <div class="stats-footer">')
            cards.append(f'                <em>Invalid: {error}</em>')
            cards.append(f'            </div>')

        cards.append(f'        </div>')

    return "\n".join(cards)


def _generate_data_table(
    row_labels: List[str],
    column_labels: List[str],
    counts: List[List[int]],
    column_percentages: List[List[float]]
) -> str:
    """
    Generate HTML data table with counts and percentages.

    Args:
        row_labels: Row category labels
        column_labels: Column category labels
        counts: 2D array of counts
        column_percentages: 2D array of column percentages

    Returns:
        HTML table string
    """
    lines = [
        '            <table class="data-table">',
        '                <thead>',
        '                    <tr>',
        '                        <th>Row \\ Column</th>'
    ]

    # Column headers
    for col_label in column_labels:
        lines.append(f'                        <th>{col_label}</th>')

    lines.append('                    </tr>')
    lines.append('                </thead>')
    lines.append('                <tbody>')

    # Data rows
    for i, row_label in enumerate(row_labels):
        lines.append('                    <tr>')
        lines.append(f'                        <td><strong>{row_label}</strong></td>')

        if i < len(counts):
            row_counts = counts[i]
            row_pct = column_percentages[i] if i < len(column_percentages) else []

            for j, count in enumerate(row_counts):
                pct = row_pct[j] if j < len(row_pct) else 0
                lines.append(
                    f'                        <td>'
                    f'{count}<br><small>({pct:.1f}%)</small>'
                    f'</td>'
                )
        else:
            for _ in column_labels:
                lines.append('                        <td>-</td>')

        lines.append('                    </tr>')

    lines.append('                </tbody>')
    lines.append('            </table>')

    return "\n".join(lines)


def _generate_javascript(
    tables: List[Dict[str, Any]],
    stats_lookup: Dict[str, Any]
) -> str:
    """
    Generate JavaScript code for interactivity.

    Args:
        tables: List of table data dictionaries
        stats_lookup: Dictionary mapping table names to statistics

    Returns:
        JavaScript script block as string
    """
    # Build table data for JavaScript with additional fields for export
    table_data_js = _build_table_data_js(tables, stats_lookup)

    # Note: Using .format() to insert table_data_js to avoid conflicts
    # with JavaScript template literals (${...})
    return """    <script>
        // Table data embedded from Python
        const tableData = {};

        // Chart instances storage
        const charts = {{}};

        // Current filter state
        let currentFilters = {{
            searchText: '',
            significantOnly: false,
            maxPValue: 1.0,
            minCramersV: 0.0,
            sortBy: 'name'
        }};""".format(table_data_js) + """

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            initializeCharts();
            initializeEventListeners();
            applyAllFilters();
        }});

        // Initialize all charts
        function initializeCharts() {{
            tableData.forEach(table => {{
                if (table.isValid) {{
                    createChart(table);
                }}
            }});
        }}

        // Create a chart for a table
        function createChart(table) {{
            const canvasId = `chart-${table.tableId}`;
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;

            const ctx = canvas.getContext('2d');

            // Prepare data based on chart type
            const chartData = prepareChartData(table);

            // Destroy existing chart if any
            if (charts[canvasId]) {{
                charts[canvasId].destroy();
            }}

            // Create new chart
            charts[canvasId] = new Chart(ctx, {{
                type: table.chartType,
                data: chartData,
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: table.chartType !== 'bar',
                            position: 'top'
                        }},
                        title: {{
                            display: false
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    let label = context.dataset.label || '';
                                    if (label) {{
                                        label += ': ';
                                    }}
                                    label += context.parsed.y !== undefined ?
                                        context.parsed.y : context.parsed.x;
                                    return label;
                                }}
                            }}
                        }}
                    }},
                    scales: table.chartType === 'bar' ? {{
                        x: {{
                            beginAtZero: true
                        }},
                        y: {{
                            beginAtZero: true
                        }}
                    }} : {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        }}

        // Prepare chart data from table data
        function prepareChartData(table) {{
            const rowLabels = table.rowLabels;
            const columnLabels = table.columnLabels;
            const counts = table.counts;

            // Determine chart structure based on dimensions
            const isHorizontal = table.chartType === 'bar';
            const isStacked = table.chartType === 'line';

            if (isHorizontal) {{
                // Horizontal bar chart: categories on Y-axis
                return {{
                    labels: rowLabels,
                    datasets: columnLabels.map((colLabel, i) => ({{
                        label: colLabel,
                        data: counts.map(row => row[i] || 0),
                        backgroundColor: getColor(i)
                    }}))
                }};
            }} else if (isStacked) {{
                // Line chart
                return {{
                    labels: rowLabels,
                    datasets: columnLabels.map((colLabel, i) => ({{
                        label: colLabel,
                        data: counts.map(row => row[i] || 0),
                        borderColor: getColor(i),
                        backgroundColor: getColor(i, 0.2),
                        fill: false,
                        tension: 0.1
                    }}))
                }};
            }} else {{
                // Vertical column chart: categories on X-axis
                return {{
                    labels: rowLabels,
                    datasets: columnLabels.map((colLabel, i) => ({{
                        label: colLabel,
                        data: counts.map(row => row[i] || 0),
                        backgroundColor: getColor(i)
                    }}))
                }};
            }}
        }}

        // Get color for dataset
        function getColor(index, alpha = 0.8) {{
            // Professional market research color palette (WCAG AA compliant)
            const colors = [
                `rgba(66, 153, 225, ${{alpha}})`,   // Blue
                `rgba(72, 187, 120, ${{alpha}})`,   // Green
                `rgba(246, 224, 94, ${{alpha}})`,   // Yellow
                `rgba(237, 137, 54, ${{alpha}})`,   // Orange
                `rgba(159, 122, 234, ${{alpha}})`,   // Purple
                `rgba(237, 100, 166, ${{alpha}})`,   // Pink
                `rgba(56, 178, 172, ${{alpha}})`,   // Teal
                `rgba(252, 129, 129, ${{alpha}})`    // Coral
            ];
            return colors[index % colors.length];
        }}

        // Initialize event listeners
        function initializeEventListeners() {{
            // Sidebar navigation
            document.querySelectorAll('#table-list li').forEach(item => {{
                item.addEventListener('click', function() {{
                    const tableId = this.getAttribute('data-table-id');
                    scrollToTable(tableId);

                    // Update active state
                    document.querySelectorAll('#table-list li').forEach(li => {{
                        li.classList.remove('active');
                    }});
                    this.classList.add('active');
                }});
            }});

            // Search functionality
            document.getElementById('search-input').addEventListener('input', function() {{
                currentFilters.searchText = this.value.toLowerCase();
                applyAllFilters();
            }});

            // Significant only filter
            document.getElementById('show-significant-only').addEventListener('change', function() {{
                currentFilters.significantOnly = this.checked;
                applyAllFilters();
            }});

            // Max P-value slider
            document.getElementById('max-p-value').addEventListener('input', function() {{
                currentFilters.maxPValue = parseFloat(this.value);
                document.getElementById('max-p-value-display').textContent =
                    currentFilters.maxPValue.toFixed(2);
                applyAllFilters();
            }});

            // Min Cramer's V slider
            document.getElementById('min-cramers-v').addEventListener('input', function() {{
                currentFilters.minCramersV = parseFloat(this.value);
                document.getElementById('min-cramers-v-display').textContent =
                    currentFilters.minCramersV.toFixed(2);
                applyAllFilters();
            }});

            // Show/hide charts
            document.getElementById('show-charts').addEventListener('change', function() {{
                toggleCharts(this.checked);
            }});

            // Sort functionality
            document.getElementById('sort-select').addEventListener('change', function() {{
                currentFilters.sortBy = this.value;
                sortTables(this.value);
            }});

            // Export all button
            document.getElementById('export-all-btn').addEventListener('click', function() {{
                exportAllTables();
            }});

            // Individual table export buttons
            document.querySelectorAll('.table-export-btn').forEach(btn => {{
                btn.addEventListener('click', function() {{
                    const tableId = this.getAttribute('data-table-id');
                    exportTable(tableId);
                }});
            }});
        }}

        // Apply all filters together
        function applyAllFilters() {{
            let visibleCount = 0;

            document.querySelectorAll('.table-card').forEach(card => {{
                const tableName = card.getAttribute('data-table-name').toLowerCase();
                const pValue = parseFloat(card.getAttribute('data-p-value'));
                const cramersV = parseFloat(card.getAttribute('data-cramers-v'));
                const isSignificant = card.getAttribute('data-significant') === 'true';

                // Check all filters
                const matchesSearch = !currentFilters.searchText ||
                    tableName.includes(currentFilters.searchText);
                const matchesSignificance = !currentFilters.significantOnly || isSignificant;
                const matchesPValue = pValue <= currentFilters.maxPValue;
                const matchesCramersV = cramersV >= currentFilters.minCramersV;

                if (matchesSearch && matchesSignificance && matchesPValue && matchesCramersV) {{
                    card.classList.remove('hidden');
                    visibleCount++;
                }} else {{
                    card.classList.add('hidden');
                }}
            }});

            // Update summary stats
            updateSummary(visibleCount);
            updateFiltersDisplay(visibleCount);
        }}

        // Update summary statistics
        function updateSummary(visibleCount) {{
            document.getElementById('stat-visible').textContent = visibleCount;
        }}

        // Update filters display in sidebar
        function updateFiltersDisplay(visibleCount) {{
            const filterCount = document.getElementById('filter-count');
            if (visibleCount === tableData.length) {{
                filterCount.textContent = 'all (' + visibleCount + ')';
            }} else {{
                filterCount.textContent = visibleCount + ' of ' + tableData.length;
            }}
        }}

        // Scroll to table
        function scrollToTable(tableId) {{
            const tableCard = document.getElementById(`table-${tableId}`);
            if (tableCard) {{
                tableCard.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
        }}

        // Toggle chart visibility
        function toggleCharts(show) {{
            document.querySelectorAll('.chart-container').forEach(container => {{
                if (show) {{
                    container.classList.remove('hidden');
                }} else {{
                    container.classList.add('hidden');
                }}
            }});
        }}

        // Sort tables
        function sortTables(sortBy) {{
            const container = document.getElementById('tables');
            const cards = Array.from(document.querySelectorAll('.table-card'));

            cards.sort((a, b) => {{
                if (sortBy === 'name') {{
                    return a.getAttribute('data-table-name').localeCompare(
                        b.getAttribute('data-table-name')
                    );
                }} else if (sortBy === 'p-value') {{
                    return parseFloat(a.getAttribute('data-p-value')) -
                           parseFloat(b.getAttribute('data-p-value'));
                }} else if (sortBy === 'cramers-v') {{
                    return parseFloat(b.getAttribute('data-cramers-v')) -
                           parseFloat(a.getAttribute('data-cramers-v'));
                }}
                return 0;
            }});

            cards.forEach(card => container.appendChild(card));
        }}

        // Export a single table to CSV
        function exportTable(tableId) {{
            const table = tableData.find(t => t.tableId === tableId);
            if (!table) return;

            const csv = generateTableCSV(table);
            downloadCSV(csv, `${{table.tableName}}.csv`);
        }}

        // Export all visible tables to CSV
        function exportAllTables() {{
            const visibleCards = Array.from(document.querySelectorAll('.table-card:not(.hidden)'));

            if (visibleCards.length === 0) {{
                alert('No tables to export. Adjust your filters first.');
                return;
            }}

            // Combine all tables into one CSV with separators
            let combinedCSV = '';

            visibleCards.forEach((card, index) => {{
                const tableId = card.id.replace('table-', '');
                const table = tableData.find(t => t.tableId === tableId);
                if (table) {{
                    combinedCSV += generateTableCSV(table);
                    if (index < visibleCards.length - 1) {{
                        combinedCSV += '\\n\\n' + '='.repeat(80) + '\\n\\n';
                    }}
                }}
            }});

            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            downloadCSV(combinedCSV, `survey-analysis-${{timestamp}}.csv`);
        }}

        // Generate CSV for a single table
        function generateTableCSV(table) {{
            const rows = [];

            // Add header with table info
            rows.push(`Table: ${{table.tableName}}`);
            rows.push('');

            // Build the data table
            const columnLabels = table.columnLabels;
            const rowLabels = table.rowLabels;
            const counts = table.counts;

            // Header row
            let header = ['Row \\\\ Column', ...columnLabels];
            rows.push(header.map(h => `"${{h}}"`).join(','));

            // Data rows
            rowLabels.forEach((rowLabel, i) => {{
                const rowData = [rowLabel];
                if (counts[i]) {{
                    counts[i].forEach(count => {{
                        rowData.push(count);
                    }});
                }} else {{
                    for (let j = 0; j < columnLabels.length; j++) {{
                        rowData.push(0);
                    }}
                }}
                rows.push(rowData.map(d => `"${{d}}"`).join(','));
            }});

            return rows.join('\\n');
        }}

        // Download CSV file
        function downloadCSV(content, filename) {{
            const blob = new Blob([content], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');

            if (navigator.msSaveBlob) {{
                // IE 10+
                navigator.msSaveBlob(blob, filename);
            }} else {{
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', filename);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
            }}
        }}
    </script>"""


def _build_table_data_js(
    tables: List[Dict[str, Any]],
    stats_lookup: Dict[str, Any]
) -> str:
    """
    Build JavaScript table data array.

    Args:
        tables: List of table data dictionaries
        stats_lookup: Dictionary mapping table names to statistics

    Returns:
        JavaScript array string
    """
    import json

    table_data_list = []

    for table in tables:
        table_id = table.get("table_id", "unknown")
        table_name = table.get("table_name", table_id)

        # Get statistics
        stats = stats_lookup.get(table_name, {})
        is_valid = stats.get("is_valid", True)

        # Get table data
        data_section = table.get("data", {})
        row_labels = data_section.get("row_labels", [])
        column_labels = data_section.get("column_labels", [])
        counts = data_section.get("counts", [])

        # Select chart type (convert to Chart.js type)
        chart_type = select_chart_type(table)
        chart_type_map = {
            "clustered_column": "bar",
            "horizontal_bar": "bar",
            "stacked_column_100": "bar",
            "line": "line"
        }
        js_chart_type = chart_type_map.get(chart_type, "bar")

        # For horizontal bar in Chart.js, we use indexAxis: 'y'
        # But for simplicity, we'll use regular bar and handle orientation in data prep

        table_obj = {
            "tableId": table_id,
            "tableName": table_name,
            "rowLabels": row_labels,
            "columnLabels": column_labels,
            "counts": counts,
            "chartType": js_chart_type,
            "isValid": is_valid
        }

        table_data_list.append(table_obj)

    return json.dumps(table_data_list, ensure_ascii=False)
