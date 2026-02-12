"""
Stage 4: Statistical Analysis Wrapper

Thin wrapper that calls semantic library statistics operations.
No processing logic - just orchestration.
"""

import sys
import json
import argparse
from pathlib import Path


def run_stage(
    crosstabs_file: str,
    spec_file: str,
    output_dir: str = "output",
    threshold: float = 0.05
) -> bool:
    """Run Stage 4 using library CLI.

    Args:
        crosstabs_file: Path to cross_tables.json
        spec_file: Path to table_specification.json
        output_dir: Output directory
        threshold: Significance threshold

    Returns:
        True if successful
    """
    from spss_analyzer.cli import statistics

    print("=" * 60)
    print("📈 Stage 4: Statistical Analysis")
    print("=" * 60)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load crosstabs
    with open(crosstabs_file, 'r') as f:
        crosstabs = json.load(f)

    # Use library to calculate chi-square
    print("\n[Calculating chi-square tests...]")
    test_results = statistics.calculate_chi_square(crosstabs, threshold)

    # Use library to filter significant
    print("\n[Filtering significant tables...]")
    filtered_tables, summary = statistics.filter_significant(test_results)

    # Save results
    statistics.save_statistics(filtered_tables, summary, str(output_path))

    print("\n" + "=" * 60)
    print("✅ Stage 4 Complete!")
    print(f"📊 {summary['significant_count']}/{summary['total_tests']} tables significant")
    print("=" * 60)

    return True


def main():
    """CLI entry point for Stage 4."""
    parser = argparse.ArgumentParser(
        description="Stage 4: Statistical Analysis (wrapper)"
    )

    parser.add_argument("--crosstabs-file", required=True,
                        help="Path to cross_tables.json from Stage 3")
    parser.add_argument("--spec-file", required=True,
                        help="Path to table_specification.json")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory")
    parser.add_argument("--threshold", type=float, default=None,
                        help="Override significance threshold")

    args = parser.parse_args()

    # Get threshold from spec if not provided
    threshold = args.threshold
    if threshold is None:
        with open(args.spec_file, 'r') as f:
            spec = json.load(f)
        threshold = spec.get('output_settings', {}).get('significance_threshold', 0.05)

    return 0 if run_stage(
        args.crosstabs_file,
        args.spec_file,
        args.output_dir,
        threshold
    ) else 1


if __name__ == "__main__":
    sys.exit(main())
