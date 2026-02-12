"""
Survey Coordinator - Workflow Orchestrator

Orchestrates all 5 stages of survey analysis workflow.
Calls library modules directly - no CLI wrapper layer.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Optional


def run_workflow(
    sav_file: str,
    output_dir: str = "output",
    skip_stages: Optional[str] = None
) -> bool:
    """Run complete 5-stage analysis workflow using library modules directly.

    Args:
        sav_file: Path to SPSS .sav file
        output_dir: Output directory for all results
        skip_stages: Stages to skip (e.g., "3,4")

    Returns:
        True if workflow completed successfully
    """
    # Import library modules directly
    from spss_analyzer.io import SPSSReader, MetadataTransformer
    from spss_analyzer.specification import TableSpecificationGenerator
    from spss_analyzer.analysis import IndicatorsCalculator, StatisticsCalculator
    from spss_analyzer.pspp import CTablesSyntaxGenerator
    from spss_analyzer.filtering import SignificanceFilter
    from spss_analyzer.reporting import PowerPointGenerator, HTMLDashboardGenerator

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    skip_list = (skip_stages or '').split(',')

    # Stage 1: Data Preparation
    if '1' not in skip_list:
        print("\n" + "=" * 60)
        print("📁 Stage 1: Data Preparation")
        print("-" * 60)

        # Read metadata
        reader = SPSSReader()
        data, meta = reader.read(sav_file)

        # Transform metadata
        transformer = MetadataTransformer()
        metadata_dict = transformer.to_variable_centered(meta)

        # Filter variables
        filtered_metadata = transformer.filter_variables(
            metadata_dict,
            min_categories=2,
            max_categories=10
        )

        # Save filtered metadata
        metadata_file = output_path / "filtered_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(filtered_metadata, f, indent=2)

        print(f"   Saved: {metadata_file}")
        print(f"   Variables: {len(filtered_metadata.get('variables', {}))} analysis variables")

    # Stage 2: Table Specification
    if '2' not in skip_list:
        print("\n" + "=" * 60)
        print("📋 Stage 2: Table Specification")
        print("-" * 60)

        # Load metadata if not already loaded
        if '1' in skip_list:
            with open(output_path / "filtered_metadata.json", 'r') as f:
                filtered_metadata = json.load(f)

        # Use specification generator
        spec_gen = TableSpecificationGenerator()
        spec = spec_gen.generate(filtered_metadata)

        # Save specification
        spec_file = output_path / "table_specification.json"
        with open(spec_file, 'w') as f:
            json.dump(spec, f, indent=2)

        print(f"   Saved: {spec_file}")
        print(f"   Tables: {len(spec.get('tables', []))}")

    # Stage 3: Cross-Table Calculation
    if '3' not in skip_list:
        print("\n" + "=" * 60)
        print("📊 Stage 3: Cross-Table Calculation")
        print("-" * 60)

        # Load spec if not already loaded
        if '2' in skip_list:
            with open(output_path / "table_specification.json", 'r') as f:
                spec = json.load(f)
            with open(output_path / "filtered_metadata.json", 'r') as f:
                filtered_metadata = json.load(f)

        # Compute indicators
        calc = IndicatorsCalculator()
        indicators_data = calc.compute(spec.get('indicators', []), filtered_metadata)

        # Save indicators
        indicators_file = output_path / "indicators.json"
        with open(indicators_file, 'w') as f:
            json.dump(indicators_data, f, indent=2)

        print(f"   Saved: {indicators_file}")

        # Generate crosstabs
        ctables_gen = CTablesSyntaxGenerator()
        tables_spec = spec.get('tables', [])

        crosstabs = {}
        for table_spec in tables_spec:
            table_id = table_spec.get('id')
            crosstabs[table_id] = {
                'spec': table_spec,
                'syntax': ctables_gen.generate([table_spec])
            }

        # Save crosstabs
        crosstabs_file = output_path / "cross_tables.json"
        with open(crosstabs_file, 'w') as f:
            json.dump(crosstabs, f, indent=2)

        print(f"   Saved: {crosstabs_file}")

    # Stage 4: Statistical Analysis
    if '4' not in skip_list:
        print("\n" + "=" * 60)
        print("📈 Stage 4: Statistical Analysis")
        print("-" * 60)

        # Load crosstabs
        with open(output_path / "cross_tables.json", 'r') as f:
            crosstabs = json.load(f)

        # Calculate chi-square
        stats_calc = StatisticsCalculator()
        test_results = stats_calc.calculate_chi_square(crosstabs, threshold=0.05)

        # Filter significant
        sig_filter = SignificanceFilter()
        filtered_tables, summary = sig_filter.filter_significant(test_results)

        # Save results
        stats_file = output_path / "statistical_summary.json"
        with open(stats_file, 'w') as f:
            json.dump(summary, f, indent=2)

        filtered_file = output_path / "filtered_tables.json"
        with open(filtered_file, 'w') as f:
            json.dump(filtered_tables, f, indent=2)

        sig_count = summary.get('significant_count', 0)
        total_count = summary.get('total_tests', 0)

        print(f"   Significant: {sig_count}/{total_count}")

    # Stage 5: Reporting
    if '5' not in skip_list:
        print("\n" + "=" * 60)
        print("📑 Stage 5: Reporting")
        print("-" * 60)

        # Load results if not already loaded
        if '4' in skip_list:
            with open(output_path / "filtered_tables.json", 'r') as f:
                filtered_tables = json.load(f)
            with open(output_path / "statistical_summary.json", 'r') as f:
                summary = json.load(f)

        # Generate PowerPoint
        ppt_gen = PowerPointGenerator()
        ppt_file = output_path / "presentation.pptx"
        ppt_gen.generate(filtered_tables, summary, str(ppt_file))

        print(f"   Saved: {ppt_file}")

        # Generate HTML Dashboard
        dash_gen = HTMLDashboardGenerator()
        dash_file = output_path / "dashboard.html"
        dash_gen.generate(filtered_tables, summary, str(dash_file))

        print(f"   Saved: {dash_file}")

    print("\n" + "=" * 60)
    print("✅ All stages completed successfully!")
    print(f"📂 Results saved to: {output_dir}")
    print("=" * 60)

    return True


def main():
    """CLI entry point for survey coordinator."""
    parser = argparse.ArgumentParser(
        description="Survey Analysis Coordinator - Orchestrate 5-stage workflow"
    )

    parser.add_argument("--sav-file", required=True,
                        help="Path to SPSS .sav file")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory (default: output/)")
    parser.add_argument("--skip", default=None,
                        help="Comma-separated stages to skip (e.g., '3,4')")

    args = parser.parse_args()

    return run_workflow(args.sav_file, args.output_dir, args.skip)


if __name__ == "__main__":
    sys.exit(main())
