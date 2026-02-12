"""
Survey Coordinator - Workflow Orchestrator

Orchestrates all 5 stages of survey analysis workflow.
Uses spss-analyzer CLI commands.
"""

import sys
import argparse
import subprocess


def run_workflow(
    sav_file: str,
    output_dir: str = "output",
    skip_stages: str = None
) -> bool:
    """Run complete 5-stage analysis workflow using spss-analyzer CLI.

    Args:
        sav_file: Path to SPSS .sav file
        output_dir: Output directory for all results
        skip_stages: Stages to skip (e.g., "3,4")

    Returns:
        True if workflow completed successfully
    """
    print("=" * 60)
    print("📊 SPSS Survey Analysis - 5-Stage Workflow")
    print("=" * 60)

    skip_list = (skip_stages or '').split(',')

    # Stage 1: Data Preparation
    if '1' not in skip_list:
        print("\n📁 Stage 1: Data Preparation")
        print("-" * 60)

        result = subprocess.run(
            ['spss-analyzer', 'data', 'read',
             '--sav-file', sav_file,
             '--output-file', f'{output_dir}/filtered_metadata.json'],
            capture_output=False
        )

        if result.returncode != 0:
            return False

        print("   Data read and filtered")

    # Stage 2: Table Specification
    if '2' not in skip_list:
        print("\n📋 Stage 2: Table Specification")
        print("-" * 60)

        result = subprocess.run(
            ['spss-analyzer', 'spec', 'tables',
             '--metadata-file', f'{output_dir}/filtered_metadata.json',
             '--output-file', f'{output_dir}/table_specification.json'],
            capture_output=False
        )

        if result.returncode != 0:
            return False

        print("   Table specification generated")

    # Stage 3: Cross-Table Calculation
    if '3' not in skip_list:
        print("\n📊 Stage 3: Cross-Table Calculation")
        print("-" * 60)

        result = subprocess.run(
            ['spss-analyzer', 'analysis', 'indicators',
             '--spec-file', f'{output_dir}/table_specification.json',
             '--metadata-file', f'{output_dir}/filtered_metadata.json',
             '--output-file', f'{output_dir}/indicators.json'],
            capture_output=False
        )

        if result.returncode != 0:
            return False

        print("   Indicators computed")

        result = subprocess.run(
            ['spss-analyzer', 'analysis', 'crosstabs',
             '--spec-file', f'{output_dir}/table_specification.json',
             '--metadata-file', f'{output_dir}/filtered_metadata.json',
             '--output-file', f'{output_dir}/cross_tables.json'],
            capture_output=False
        )

        if result.returncode != 0:
            return False

        print("   Crosstabs generated")

    # Stage 4: Statistical Analysis
    if '4' not in skip_list:
        print("\n📈 Stage 4: Statistical Analysis")
        print("-" * 60)

        result = subprocess.run(
            ['spss-analyzer', 'stats', 'test',
             '--crosstabs-file', f'{output_dir}/cross_tables.json',
             '--output-file', f'{output_dir}/test_results.json'],
            capture_output=False
        )

        if result.returncode != 0:
            return False

        print("   Chi-square tests calculated")

        result = subprocess.run(
            ['spss-analyzer', 'stats', 'filter',
             '--crosstabs-file', f'{output_dir}/test_results.json',
             '--output-file', f'{output_dir}/filtered_tables.json'],
            capture_output=False
        )

        if result.returncode != 0:
            return False

        print("   Significant tables filtered")

    # Stage 5: Reporting
    if '5' not in skip_list:
        print("\n📑 Stage 5: Reporting")
        print("-" * 60)

        result = subprocess.run(
            ['spss-analyzer', 'reporting', 'ppt',
             '--tables-file', f'{output_dir}/filtered_tables.json',
             '--output-dir', output_dir],
            capture_output=False
        )

        if result.returncode != 0:
            return False

        print("   PowerPoint generated")

        result = subprocess.run(
            ['spss-analyzer', 'reporting', 'html',
             '--tables-file', f'{output_dir}/filtered_tables.json',
             '--output-dir', output_dir],
            capture_output=False
        )

        if result.returncode != 0:
            return False

        print("   HTML dashboard generated")

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
