"""
Stage 5: Reporting

Uses spss_analyzer library modules directly.
"""

import sys
import argparse
import json
from pathlib import Path


def run_stage(
    filtered_tables_file: str,
    output_dir: str = "output"
) -> bool:
    """Run Stage 5 using library modules directly."""
    print("=" * 60)
    print("📑 Stage 5: Reporting")
    print("=" * 60)

    from spss_analyzer.reporting import PowerPointGenerator, HTMLDashboardGenerator

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load filtered tables and summary
    with open(filtered_tables_file, 'r') as f:
        data = json.load(f)

    # Handle both formats: direct list or wrapped with summary
    if isinstance(data, list):
        filtered_tables = data
        summary = {}
    elif isinstance(data, dict):
        filtered_tables = data.get('tables', [])
        summary = data.get('summary', {})
    else:
        filtered_tables = []
        summary = {}

    # Generate PowerPoint
    ppt_gen = PowerPointGenerator()
    ppt_file = output_path / "presentation.pptx"
    ppt_gen.generate(filtered_tables, summary, str(ppt_file))
    print(f"Saved PowerPoint: {ppt_file}")

    # Generate HTML Dashboard
    dash_gen = HTMLDashboardGenerator()
    dash_file = output_path / "dashboard.html"
    dash_gen.generate(filtered_tables, summary, str(dash_file))
    print(f"Saved HTML dashboard: {dash_file}")

    print("\n" + "=" * 60)
    print("✅ Stage 5 Complete!")
    print("=" * 60)

    return True


def main():
    """CLI entry point for Stage 5."""
    parser = argparse.ArgumentParser(
        description="Stage 5: Reporting"
    )

    parser.add_argument("--filtered-tables-file", required=True,
                        help="Path to filtered_tables.json from Stage 4")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory")

    args = parser.parse_args()

    return run_stage(args.filtered_tables_file, args.output_dir)


if __name__ == "__main__":
    sys.exit(main())
