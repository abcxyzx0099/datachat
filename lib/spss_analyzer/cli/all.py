"""
Complete workflow - Orchestrate all analysis operations.

Runs full SPSS survey analysis using semantic library operations.
This is stage-aware but uses stage-agnostic library functions.
"""

import json
import sys
from pathlib import Path
from typing import Optional
import argparse


def run_workflow(
    sav_file: str,
    output_dir: str = "output",
    skip_stages: Optional[str] = None
) -> bool:
    """Run complete 5-stage analysis workflow.

    Args:
        sav_file: Path to SPSS .sav file
        output_dir: Output directory for all results
        skip_stages: Comma-separated list of stages to skip (e.g., "3,4")

    Returns:
        True if workflow completed successfully
    """
    from spss_analyzer.cli import data, specification, analysis, statistics, reporting

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("📊 SPSS Survey Analysis - Full Workflow")
    print("=" * 60)

    # Stage 1: Data Preparation
    if '1' not in (skip_stages or ''):
        print("\n📁 Stage 1: Data Preparation")
        print("-" * 60)

        # Read metadata
        survey_data, metadata = data.read_metadata(sav_file)

        # Filter variables
        filtered_metadata = data.filter_variables(metadata)
        metadata_file = output_path / "filtered_metadata.json"
        data.save_metadata(filtered_metadata, str(metadata_file))

    else:
        print("\n📁 Stage 1: Skipped")
        metadata_file = output_path / "filtered_metadata.json"
        if not metadata_file.exists():
            print(f"❌ Error: Cannot skip Stage 1 - no metadata file found")
            return False
        with open(metadata_file, 'r') as f:
            filtered_metadata = json.load(f)
        survey_data = []  # Would need actual data

    # Stage 2: Table Specification
    if '2' not in (skip_stages or ''):
        print("\n📋 Stage 2: Table Specification")
        print("-" * 60)

        # Generate tables
        tables_spec = specification.generate_tables(filtered_metadata)
        # Generate indicators
        indicators_spec = specification.generate_indicators(filtered_metadata)
        # Combine
        full_spec = specification.combine_specifications(tables_spec, indicators_spec)

        spec_file = output_path / "table_specification.json"
        specification.save_specification(full_spec, str(spec_file))

    else:
        print("\n📋 Stage 2: Skipped")
        spec_file = output_path / "table_specification.json"
        if not spec_file.exists():
            print(f"❌ Error: Cannot skip Stage 2 - no spec file found")
            return False
        with open(spec_file, 'r') as f:
            full_spec = json.load(f)

    # Stage 3: Cross-Table Calculation
    if '3' not in (skip_stages or ''):
        print("\n📊 Stage 3: Cross-Table Calculation")
        print("-" * 60)

        # Compute indicators
        indicators_data = analysis.compute_indicators(
            survey_data if survey_data else [],
            full_spec.get('indicators', []),
            filtered_metadata
        )

        # Save indicators
        indicators_file = output_path / "indicators.csv"
        analysis.save_indicators(indicators_data, str(indicators_file))

        # Generate crosstabs
        crosstabs = analysis.generate_crosstabs(
            full_spec.get('tables', []),
            filtered_metadata
        )

        crosstabs_file = output_path / "cross_tables.json"
        analysis.save_crosstabs(crosstabs, str(crosstabs_file))

    else:
        print("\n📊 Stage 3: Skipped")
        # Would need to load from existing files
        indicators_data = []
        crosstabs = {}

    # Stage 4: Statistical Analysis
    if '4' not in (skip_stages or ''):
        print("\n📈 Stage 4: Statistical Analysis")
        print("-" * 60)

        # Calculate statistics
        test_results = statistics.calculate_chi_square(crosstabs)

        # Filter significant
        filtered_tables, summary = statistics.filter_significant(test_results)

        # Save results
        statistics.save_statistics(filtered_tables, summary, str(output_path))

    else:
        print("\n📈 Stage 4: Skipped")
        summary_file = output_path / "statistical_summary.json"
        filtered_file = output_path / "filtered_tables.json"
        if not filtered_file.exists():
            print(f"❌ Error: Cannot skip Stage 4 - no results found")
            return False
        with open(filtered_file, 'r') as f:
            filtered_tables = json.load(f)

    # Stage 5: Reporting
    if '5' not in (skip_stages or ''):
        print("\n📑 Stage 5: Reporting")
        print("-" * 60)

        # Generate PowerPoint
        ppt_file = reporting.create_powerpoint(
            filtered_tables,
            summary,
            output_file=str(output_path / "presentation.pptx")
        )

        # Generate HTML Dashboard
        dash_file = reporting.create_html_dashboard(
            filtered_tables,
            summary,
            output_file=str(output_path / "dashboard.html")
        )

        # Save manifest
        reporting.save_reports(ppt_file, dash_file)

    else:
        print("\n📑 Stage 5: Skipped")

    print("\n" + "=" * 60)
    print("✅ Analysis Complete!")
    print(f"📂 Results saved to: {output_dir}")
    print("=" * 60)

    return True


def main():
    """CLI entry point for complete workflow."""
    parser = argparse.ArgumentParser(
        description="Complete SPSS survey analysis workflow"
    )

    parser.add_argument('--sav-file', required=True,
                        help='Path to SPSS .sav file')
    parser.add_argument('--output-dir', default='output',
                        help='Output directory (default: output/)')
    parser.add_argument('--skip', default=None,
                        help='Comma-separated stages to skip (e.g., "3,4")')

    args = parser.parse_args()

    success = run_workflow(
        args.sav_file,
        args.output_dir,
        skip_stages=args.skip
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
