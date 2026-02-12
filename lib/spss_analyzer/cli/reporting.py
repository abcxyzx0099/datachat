"""
Reporting operations - Generate PowerPoint and HTML dashboard.

Semantic operations for creating final reports.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse


def create_powerpoint(
    filtered_tables: List[Dict[str, Any]],
    statistical_summary: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    template_path: Optional[str] = None,
    output_file: str = "output/presentation.pptx"
) -> str:
    """Generate PowerPoint presentation from filtered tables.

    Args:
        filtered_tables: List of significant tables
        statistical_summary: Summary statistics
        metadata: Optional metadata for styling
        template_path: Optional PowerPoint template
        output_file: Output file path

    Returns:
        Path to generated presentation
    """
    try:
        from spss_analyzer.reporting import PowerPointGenerator
    except ImportError:
        print("❌ Error: PowerPointGenerator not available")
        sys.exit(1)

    generator = PowerPointGenerator(template_path=template_path)

    # Convert filtered tables to expected format
    slides_data = []
    for table in filtered_tables:
        slides_data.append({
            'table_id': table.get('table_id', ''),
            'title': table.get('table_name', ''),
            'chi_square': table.get('chi_square', 0),
            'p_value': table.get('p_value', 1.0),
            'significant': table.get('significant', False)
        })

    # Add summary slides
    if statistical_summary:
        slides_data.insert(0, {
            'type': 'summary',
            'total_tests': statistical_summary.get('total_tests', 0),
            'significant_count': statistical_summary.get('significant_count', 0),
            'threshold': statistical_summary.get('significance_threshold', 0.05)
        })

    try:
        output_path = generator.generate(slides_data, output_file)
        print(f"✅ Generated PowerPoint: {output_file}")
        return str(output_path)
    except Exception as e:
        print(f"❌ Error generating PowerPoint: {e}")
        sys.exit(1)


def create_html_dashboard(
    filtered_tables: List[Dict[str, Any]],
    statistical_summary: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    template_path: Optional[str] = None,
    output_file: str = "output/dashboard.html"
) -> str:
    """Generate HTML dashboard from filtered tables.

    Args:
        filtered_tables: List of significant tables
        statistical_summary: Summary statistics
        metadata: Optional metadata for styling
        template_path: Optional HTML template
        output_file: Output file path

    Returns:
        Path to generated dashboard
    """
    try:
        from spss_analyzer.reporting import HTMLDashboardGenerator
    except ImportError:
        print("❌ Error: HTMLDashboardGenerator not available")
        sys.exit(1)

    generator = HTMLDashboardGenerator(template_path=template_path)

    # Convert filtered tables to expected format
    tables_data = []
    for table in filtered_tables:
        tables_data.append({
            'id': table.get('table_id', ''),
            'name': table.get('table_name', ''),
            'chi_square': table.get('chi_square', 0),
            'p_value': table.get('p_value', 1.0),
            'significant': table.get('significant', False)
        })

    try:
        output_path = generator.generate(tables_data, output_file)
        print(f"✅ Generated HTML dashboard: {output_file}")
        return str(output_path)
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        sys.exit(1)


def save_reports(
    powerpoint_file: str,
    dashboard_file: str,
    manifest_file: str = "output/reports_manifest.json"
) -> None:
    """Save report manifest.

    Args:
        powerpoint_file: Path to PowerPoint
        dashboard_file: Path to HTML dashboard
        manifest_file: Output manifest path
    """
    manifest = {
        'generated_at': _get_timestamp(),
        'reports': {
            'powerpoint': powerpoint_file,
            'dashboard': dashboard_file
        }
    }

    manifest_path = Path(manifest_file)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ Saved manifest: {manifest_file}")


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.now().isoformat()


def main():
    """CLI entry point for reporting operations."""
    parser = argparse.ArgumentParser(
        description="Report generation for SPSS survey analysis"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # powerpoint command
    ppt_parser = subparsers.add_parser('powerpoint', help='Generate PowerPoint presentation')
    ppt_parser.add_argument('--tables-file', required=True, help='Path to filtered tables JSON')
    ppt_parser.add_argument('--summary-file', help='Path to statistical summary JSON')
    ppt_parser.add_argument('--template', help='Path to PowerPoint template')
    ppt_parser.add_argument('--output', default='output/presentation.pptx', help='Output file')

    # dashboard command
    dash_parser = subparsers.add_parser('dashboard', help='Generate HTML dashboard')
    dash_parser.add_argument('--tables-file', required=True, help='Path to filtered tables JSON')
    dash_parser.add_argument('--summary-file', help='Path to statistical summary JSON')
    dash_parser.add_argument('--template', help='Path to HTML template')
    dash_parser.add_argument('--output', default='output/dashboard.html', help='Output file')

    # both command
    both_parser = subparsers.add_parser('both', help='Generate both reports')
    both_parser.add_argument('--tables-file', required=True, help='Path to filtered tables JSON')
    both_parser.add_argument('--summary-file', help='Path to statistical summary JSON')
    both_parser.add_argument('--ppt-template', help='Path to PowerPoint template')
    both_parser.add_argument('--html-template', help='Path to HTML template')
    both_parser.add_argument('--output-dir', default='output', help='Output directory')

    args = parser.parse_args()

    if args.command == 'powerpoint':
        with open(args.tables_file, 'r') as f:
            tables = json.load(f)

        summary = {}
        if args.summary_file:
            with open(args.summary_file, 'r') as f:
                summary = json.load(f)

        create_powerpoint(tables, summary, output_file=args.output)

    elif args.command == 'dashboard':
        with open(args.tables_file, 'r') as f:
            tables = json.load(f)

        summary = {}
        if args.summary_file:
            with open(args.summary_file, 'r') as f:
                summary = json.load(f)

        create_html_dashboard(tables, summary, output_file=args.output)

    elif args.command == 'both':
        with open(args.tables_file, 'r') as f:
            tables = json.load(f)

        summary = {}
        if args.summary_file:
            with open(args.summary_file, 'r') as f:
                summary = json.load(f)

        output_dir = args.output_dir
        ppt_file = Path(output_dir) / "presentation.pptx"
        dash_file = Path(output_dir) / "dashboard.html"

        create_powerpoint(
            tables, summary,
            template_path=args.ppt_template,
            output_file=str(ppt_file)
        )

        create_html_dashboard(
            tables, summary,
            template_path=args.html_template,
            output_file=str(dash_file)
        )

        save_reports(str(ppt_file), str(dash_file))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
