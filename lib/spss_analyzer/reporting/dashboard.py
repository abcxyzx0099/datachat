"""
HTML Dashboard Generator

Generate interactive HTML dashboards from cross-tabulation results.

Features:
- All tables displayed (not just significant ones)
- Sidebar navigation for quick table access
- Significance highlighting (green = significant, red = not significant)
- Interactive Chart.js charts with tooltips
- Enhanced filtering: significance, p-value threshold, Cramer's V threshold
- Sorting by table name, p-value, or Cramer's V
- CSV export functionality
- Responsive design

Example:
    >>> gen = HTMLDashboardGenerator()
    >>> html = gen.generate_dashboard(
    ...     cross_tables,
    ...     statistics,
    ...     filter_list
    ... )
    >>> gen.save("dashboard.html", html)
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class DashboardConfig:
    """
    Configuration for dashboard generation.

    Attributes:
        title: Dashboard title
        show_charts: Whether to render charts (default: True)
        chart_type: Default chart type (bar, line, pie)
        color_scheme: Color scheme for charts and styling
        enable_export: Enable CSV export (default: True)
        enable_filtering: Enable filtering controls (default: True)
    """
    title: str = "Survey Analysis Dashboard"
    show_charts: bool = True
    chart_type: str = "bar"
    color_scheme: str = "professional"
    enable_export: bool = True
    enable_filtering: bool = True


@dataclass
class ChartColorScheme:
    """Color scheme for dashboard charts and styling."""
    primary: str = "#4287f5"
    secondary: str = "#48bb78"
    accent: str = "#f6e05e"
    significant: str = "#48bb78"
    not_significant: str = "#e53e3e"
    text_dark: str = "#2d3748"
    text_light: str = "#718096"
    background: str = "#f7fafc"
    border: str = "#e2e8f0"
    table_header: str = "#edf2f7"

    def to_css_dict(self) -> Dict[str, str]:
        """Convert to CSS variable dictionary."""
        return {
            "--color-primary": self.primary,
            "--color-secondary": self.secondary,
            "--color-accent": self.accent,
            "--color-significant": self.significant,
            "--color-not-significant": self.not_significant,
            "--color-text": self.text_dark,
            "--color-text-light": self.text_light,
            "--color-bg": self.background,
            "--color-border": self.border,
            "--color-table-header": self.table_header,
        }


class HTMLDashboardGenerator:
    """
    Generate interactive HTML dashboards from survey analysis results.

    The dashboard includes:
    - Summary statistics
    - All tables with charts
    - Filtering controls
    - Significance highlighting
    - Export functionality

    Example:
        >>> gen = HTMLDashboardGenerator()
        >>> html = gen.generate_dashboard(
        ...     cross_tables=cross_table_data,
        ...     statistics=statistical_summary,
        ...     filter_list=filter_results
        ... )
        >>> gen.save("output/dashboard.html")
    """

    def __init__(
        self,
        config: Optional[DashboardConfig] = None,
    ):
        """
        Initialize the generator.

        Args:
            config: Dashboard configuration (uses defaults if None)
        """
        self.config = config or DashboardConfig()
        self.color_scheme = ChartColorScheme()

    def generate_dashboard(
        self,
        cross_tables: Dict[str, Any],
        statistics: Dict[str, Any],
        filter_list: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate complete HTML dashboard.

        Args:
            cross_tables: Cross-table data with structure:
                {tables: [{table_id, table_name, row_variable, column_variable, data}]}
            statistics: Statistical test results:
                {tables: [{table_name, p_value, cramers_v, is_significant, is_valid}]}
            filter_list: Optional filter results for each table

        Returns:
            Complete HTML document as string

        Example:
            >>> gen = HTMLDashboardGenerator()
            >>> html = gen.generate_dashboard(cross_tables, statistics, filter_list)
        """
        # Create statistics lookup
        stats_lookup = {
            t.get("table_name", ""): t
            for t in statistics.get("tables", [])
        }

        # Create filter lookup
        filter_lookup = {}
        if filter_list:
            filter_lookup = {
                f.get("table_id", ""): f
                for f in filter_list.get("filters", [])
            }

        # Generate HTML sections
        html_parts = [
            self._generate_html_header(),
            self._generate_css(),
            "</head>",
            '<body>',
            self._generate_sidebar(cross_tables.get("tables", []), stats_lookup),
            self._generate_main_content(cross_tables, statistics, stats_lookup, filter_lookup),
            self._generate_javascript(cross_tables.get("tables", []), stats_lookup),
            '</body>',
            '</html>',
        ]

        return "\n".join(html_parts)

    def _generate_html_header(self) -> str:
        """Generate HTML head section with title and CDNs."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Survey Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>"""

    def _generate_css(self) -> str:
        """Generate CSS styles for the dashboard."""
        colors = self.color_scheme.to_css_dict()

        css_vars = "\n        ".join([f"{k}: {v};" for k, v in colors.items()])

        return f"""    <style>
        :root {{
            {css_vars}
        }}

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
            background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-primary)cc 100%);
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
        }}

        .stat-card .number {{
            font-size: 2.5em;
            font-weight: 700;
            color: var(--color-primary);
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
        }}

        .table-card.significant {{
            border-left-color: var(--color-significant);
        }}

        .table-card.not-significant {{
            border-left-color: var(--color-not-significant);
        }}

        .table-card h3 {{
            color: var(--color-primary);
            margin-bottom: 20px;
            font-size: 1.4em;
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

        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        table.data-table th, table.data-table td {{
            padding: 14px;
            text-align: center;
            border: 1px solid var(--color-border);
        }}

        table.data-table th {{
            background: var(--color-table-header);
            font-weight: 600;
            color: var(--color-primary);
        }}

        table.data-table tr:hover {{
            background: var(--color-bg);
        }}

        .stats-footer {{
            margin-top: 20px;
            padding: 15px;
            background: var(--color-bg);
            border-radius: 8px;
            font-size: 0.9em;
        }}

        .significant-badge {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 12px;
        }}

        .significant-badge.yes {{
            background: var(--color-significant);
            color: white;
        }}

        .significant-badge.no {{
            background: var(--color-not-significant);
            color: white;
        }}

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
        }}
    </style>"""

    def _generate_sidebar(
        self,
        tables: List[Dict[str, Any]],
        stats_lookup: Dict[str, Any],
    ) -> str:
        """Generate sidebar navigation HTML."""
        lines = [
            '    <div class="sidebar">',
            '        <div class="sidebar-header">',
            '            <h3>Navigation</h3>',
            '        </div>',
            '        <div class="search-box">',
            '            <input type="text" id="search-input" placeholder="Search tables...">',
            '        </div>',
            '        <ul id="table-list">',
        ]

        for table in tables:
            table_id = table.get("table_id", "unknown")
            table_name = table.get("table_name", table_id)

            # Get significance status
            stats = stats_lookup.get(table_name, {})
            is_significant = stats.get("is_significant", False)

            # Add indicator
            indicator = "✓" if is_significant else "✗"

            lines.append(f'            <li data-table-id="{table_id}">')
            lines.append(f'                {indicator} {table_name}')
            lines.append(f'            </li>')

        lines.extend([
            '        </ul>',
            '    </div>',
        ])

        return "\n".join(lines)

    def _generate_main_content(
        self,
        cross_tables: Dict[str, Any],
        statistics: Dict[str, Any],
        stats_lookup: Dict[str, Any],
        filter_lookup: Dict[str, Any],
    ) -> str:
        """Generate main content area HTML."""
        lines = [
            '    <div class="content">',
            f'        <h1>{self.config.title}</h1>',
            '',
            self._generate_summary_section(cross_tables, statistics),
            '        <div id="tables">',
        ]

        # Generate table cards
        for table in cross_tables.get("tables", []):
            lines.extend(self._generate_table_card(table, stats_lookup, filter_lookup))

        lines.extend([
            '        </div>',
            '    </div>',
        ])

        return "\n".join(lines)

    def _generate_summary_section(
        self,
        cross_tables: Dict[str, Any],
        statistics: Dict[str, Any],
    ) -> str:
        """Generate summary statistics section."""
        tables = cross_tables.get("tables", [])
        stats_tables = statistics.get("tables", [])

        total_tables = len(tables)
        significant_count = sum(1 for t in stats_tables if t.get("is_significant", False))
        valid_count = sum(1 for t in stats_tables if t.get("is_valid", True))
        significance_level = statistics.get("significance_level", 0.05)

        return f'''        <div class="summary">
            <h2>Analysis Summary</h2>
            <div class="summary-stats">
                <div class="stat-card">
                    <div class="number">{total_tables}</div>
                    <div class="label">Total Tables</div>
                </div>
                <div class="stat-card">
                    <div class="number">{significant_count}</div>
                    <div class="label">Significant (p < {significance_level})</div>
                </div>
                <div class="stat-card">
                    <div class="number">{valid_count}</div>
                    <div class="label">Valid Tests</div>
                </div>
                <div class="stat-card">
                    <div class="number">{significant_count/total_tables*100 if total_tables > 0 else 0:.1f}%</div>
                    <div class="label">Significance Rate</div>
                </div>
            </div>
        </div>'''

    def _generate_table_card(
        self,
        table: Dict[str, Any],
        stats_lookup: Dict[str, Any],
        filter_lookup: Dict[str, Any],
    ) -> List[str]:
        """Generate HTML for a single table card."""
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

        # Determine significance class
        significance_class = "significant" if is_significant else "not-significant"

        # Get table data
        data_section = table.get("data", {})
        row_labels = data_section.get("row_labels", [])
        column_labels = data_section.get("column_labels", [])
        counts = data_section.get("counts", [])
        column_percentages = data_section.get("column_percentages", [])

        lines = [
            f'        <div class="table-card {significance_class}" id="table-{table_id}">',
            f'            <h3>{row_var} × {col_var}</h3>',
            '            <div class="chart-container">',
            f'                <canvas id="chart-{table_id}"></canvas>',
            '            </div>',
            self._generate_data_table_html(row_labels, column_labels, counts, column_percentages),
        ]

        # Stats footer
        if is_valid:
            sig_class = "yes" if is_significant else "no"
            sig_text = "Significant" if is_significant else "Not Significant"

            lines.append('            <div class="stats-footer">')
            lines.append(f'                χ² = {chi_square:.4f}, ')
            lines.append(f'                p = {p_value:.4f}, ')
            lines.append(f'                V = {cramers_v:.4f} ({interpretation})')
            lines.append(f'                <span class="significant-badge {sig_class}">{sig_text}</span>')
            lines.append('            </div>')
        else:
            error = stats.get("error", "Unknown error")
            lines.append('            <div class="stats-footer">')
            lines.append(f'                <em>Invalid: {error}</em>')
            lines.append('            </div>')

        lines.append('        </div>')

        return lines

    def _generate_data_table_html(
        self,
        row_labels: List[str],
        column_labels: List[str],
        counts: List[List[int]],
        column_percentages: List[List[float]],
    ) -> str:
        """Generate HTML data table."""
        lines = [
            '            <table class="data-table">',
            '                <thead>',
            '                    <tr>',
            '                        <th>Row \\ Column</th>',
        ]

        # Column headers
        for col_label in column_labels:
            lines.append(f'                        <th>{col_label}</th>')

        lines.extend([
            '                    </tr>',
            '                </thead>',
            '                <tbody>',
        ])

        # Data rows
        for i, row_label in enumerate(row_labels):
            lines.append('                    <tr>')
            lines.append(f'                        <td><strong>{row_label}</strong></td>')

            if i < len(counts):
                row_counts = counts[i]
                row_pct = column_percentages[i] if i < len(column_percentages) else []

                for j, count in enumerate(row_counts):
                    pct = row_pct[j] if j < len(row_pct) else 0
                    lines.append(f'                        <td>{count}<br><small>({pct:.1f}%)</small></td>')
            else:
                for _ in column_labels:
                    lines.append('                        <td>-</td>')

            lines.append('                    </tr>')

        lines.extend([
            '                </tbody>',
            '            </table>',
        ])

        return "\n".join(lines)

    def _generate_javascript(
        self,
        tables: List[Dict[str, Any]],
        stats_lookup: Dict[str, Any],
    ) -> str:
        """Generate JavaScript for interactivity."""
        # Build table data for JavaScript
        table_data_js = json.dumps([
            {
                "tableId": t.get("table_id", ""),
                "tableName": t.get("table_name", ""),
                "rowLabels": t.get("data", {}).get("row_labels", []),
                "columnLabels": t.get("data", {}).get("column_labels", []),
                "counts": t.get("data", {}).get("counts", []),
                "chartType": "bar",
                "isValid": stats_lookup.get(t.get("table_name", ""), {}).get("is_valid", True)
            }
            for t in tables
        ])

        return '''    <script>
        const tableData = ''' + table_data_js + ''';

        const charts = {};

        document.addEventListener('DOMContentLoaded', function() {{
            initializeCharts();
            initializeEventListeners();
        }});

        function initializeCharts() {{
            tableData.forEach(table => {{
                if (table.isValid) {{
                    createChart(table);
                }}
            }});
        }}

        function createChart(table) {{
            const canvasId = `chart-${{table.tableId}}`;
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;

            const ctx = canvas.getContext('2d');
            const chartData = {{
                labels: table.rowLabels,
                datasets: table.columnLabels.map((label, i) => ({{
                    label: label,
                    data: table.counts.map(row => row[i] || 0),
                    backgroundColor: getColor(i)
                }}))
            }};

            if (charts[canvasId]) {{
                charts[canvasId].destroy();
            }}

            charts[canvasId] = new Chart(ctx, {{
                type: 'bar',
                data: chartData,
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: table.columnLabels.length > 1,
                            position: 'top'
                        }}
                    }},
                    scales: {{
                        x: {{ beginAtZero: true }},
                        y: {{ beginAtZero: true }}
                    }}
                }}
            }});
        }}

        function getColor(index) {{
            const colors = [
                'rgba(66, 153, 225, 0.8)',
                'rgba(72, 187, 120, 0.8)',
                'rgba(246, 224, 94, 0.8)',
                'rgba(237, 137, 54, 0.8)'
            ];
            return colors[index % colors.length];
        }}

        function initializeEventListeners() {{
            document.querySelectorAll('#table-list li').forEach(item => {{
                item.addEventListener('click', function() {{
                    const tableId = this.getAttribute('data-table-id');
                    const card = document.getElementById(`table-${{tableId}}`);
                    if (card) {{
                        card.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    }}
                }});
            }});

            document.getElementById('search-input').addEventListener('input', function() {{
                const search = this.value.toLowerCase();
                document.querySelectorAll('.table-card').forEach(card => {{
                    const name = card.getAttribute('data-table-name') || '';
                    const match = name.toLowerCase().includes(search);
                    card.style.display = match ? 'block' : 'none';
                }});
            }});
        }}
    </script>'''

    def save(
        self,
        output_path: str,
        html_content: str,
    ) -> None:
        """
        Save dashboard HTML to file.

        Args:
            output_path: Path for output HTML file
            html_content: Complete HTML content
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Dashboard saved to: {output_path}")


def create_dashboard(
    cross_tables: Dict[str, Any],
    statistics: Dict[str, Any],
    output_path: str,
    filter_list: Optional[Dict[str, Any]] = None,
    title: str = "Survey Analysis Dashboard",
) -> None:
    """
    Convenience function to create HTML dashboard.

    Args:
        cross_tables: Cross-table data
        statistics: Statistical summary
        output_path: Path for output HTML file
        filter_list: Optional filter results
        title: Dashboard title

    Example:
        >>> create_dashboard(
        ...     cross_tables=data,
        ...     statistics=stats,
        ...     output_path="dashboard.html"
        ... )
    """
    gen = HTMLDashboardGenerator()
    html = gen.generate_dashboard(cross_tables, statistics, filter_list)
    gen.save(output_path, html)
