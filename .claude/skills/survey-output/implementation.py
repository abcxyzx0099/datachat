"""
Survey Output Generator Skill

Generates final reports (PowerPoint and HTML) from analyzed data.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

# Add library path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib"))

from spss_analyzer.specification import TableSpecificationDocument
from spss_analyzer.reporting import PowerPointGenerator, HTMLDashboardGenerator

logger = logging.getLogger(__name__)


class OutputGenerator:
    """Generates final output reports."""

    def __init__(self, output_dir: str = "output"):
        """Initialize generator with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_outputs(
        self,
        spec: TableSpecificationDocument,
        cross_tables_file: str,
        statistics_file: str,
        filtered_tables_file: str,
    ) -> Dict[str, str]:
        """
        Generate all output reports.

        Args:
            spec: Table specification document
            cross_tables_file: Path to cross-tables data
            statistics_file: Path to statistical summary
            filtered_tables_file: Path to filtered tables list

        Returns:
            Dictionary with paths to generated files
        """
        results = {}

        # Load data
        with open(cross_tables_file) as f:
            cross_tables = json.load(f)
        with open(statistics_file) as f:
            statistics = json.load(f)
        with open(filtered_tables_file) as f:
            filtered_tables = json.load(f)

        # Generate PowerPoint
        if spec.output_settings.include_powerpoint:
            try:
                ppt_file = self._generate_powerpoint(
                    spec, filtered_tables, statistics
                )
                results["powerpoint"] = str(ppt_file)
                logger.info(f"✓ Generated PowerPoint: {ppt_file}")
            except Exception as e:
                logger.error(f"PowerPoint generation failed: {e}")

        # Generate HTML Dashboard
        if spec.output_settings.include_html_dashboard:
            try:
                html_file = self._generate_html_dashboard(
                    spec, cross_tables, statistics, filtered_tables
                )
                results["html_dashboard"] = str(html_file)
                logger.info(f"✓ Generated HTML dashboard: {html_file}")
            except Exception as e:
                logger.error(f"HTML dashboard generation failed: {e}")

        return results

    def _generate_powerpoint(
        self,
        spec: TableSpecificationDocument,
        filtered_tables: Dict[str, Any],
        statistics: Dict[str, Any],
    ) -> Path:
        """Generate PowerPoint presentation."""
        output_file = self.output_dir / "presentation.pptx"

        gen = PowerPointGenerator()
        gen.create_presentation(
            tables=filtered_tables.get("tables", []),
            statistics=statistics,
            title="Survey Analysis Results",
            max_tables=spec.output_settings.max_tables_ppt,
        )
        gen.save(str(output_file))

        return output_file

    def _generate_html_dashboard(
        self,
        spec: TableSpecificationDocument,
        cross_tables: Dict[str, Any],
        statistics: Dict[str, Any],
        filtered_tables: Dict[str, Any],
    ) -> Path:
        """Generate HTML dashboard."""
        output_file = self.output_dir / "dashboard.html"

        gen = HTMLDashboardGenerator()
        html = gen.generate_dashboard(
            cross_tables=cross_tables,
            statistics=statistics,
            filter_list=filtered_tables,
            title=spec.output_settings.dashboard_title,
            include_charts=spec.output_settings.include_charts,
            chart_type=spec.output_settings.chart_type,
        )
        gen.save(str(output_file), html)

        return output_file


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate survey analysis reports"
    )
    parser.add_argument(
        "spec_file",
        help="Path to table_specification.json",
    )
    parser.add_argument(
        "cross_tables_file",
        help="Path to cross_tables.json or .csv",
    )
    parser.add_argument(
        "statistics_file",
        help="Path to statistical_summary.json",
    )
    parser.add_argument(
        "filtered_tables_file",
        help="Path to filtered_tables.json",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="output",
        help="Output directory (default: output/)",
    )

    args = parser.parse_args()

    # Load specification
    with open(args.spec_file) as f:
        spec_dict = json.load(f)
    spec = TableSpecificationDocument.from_dict(spec_dict)

    # Generate outputs
    generator = OutputGenerator(output_dir=args.output_dir)
    results = generator.generate_outputs(
        spec=spec,
        cross_tables_file=args.cross_tables_file,
        statistics_file=args.statistics_file,
        filtered_tables_file=args.filtered_tables_file,
    )

    # Report results
    print("\n" + "=" * 60)
    print("SURVEY ANALYSIS REPORTS GENERATED")
    print("=" * 60)

    if "powerpoint" in results:
        print(f"\n✓ PowerPoint: {results['powerpoint']}")
    if "html_dashboard" in results:
        print(f"✓ HTML Dashboard: {results['html_dashboard']}")

    print("\nOpen the files to view your reports!")


if __name__ == "__main__":
    main()
