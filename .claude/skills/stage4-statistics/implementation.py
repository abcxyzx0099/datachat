"""
Stage 4: Statistical Analysis

Uses spss_analyzer library modules directly.
"""

import sys
import argparse
import json
from pathlib import Path


def run_stage(
    crosstabs_file: str,
    spec_file: str,
    output_dir: str = "output",
    threshold: float = 0.05
) -> bool:
    """Run Stage 4 using library modules directly."""
    print("=" * 60)
    print("📈 Stage 4: Statistical Analysis")
    print("=" * 60)

    from spss_analyzer.analysis import StatisticsCalculator
    from spss_analyzer.filtering import SignificanceFilter

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load crosstabs
    with open(crosstabs_file, 'r') as f:
        crosstabs = json.load(f)

    # Calculate chi-square
    stats_calc = StatisticsCalculator()
    test_results = stats_calc.calculate_chi_square(crosstabs)

    # Filter significant
    sig_filter = SignificanceFilter()
    filtered_tables, summary = sig_filter.filter_significant(
        test_results,
        threshold=threshold
    )

    # Save results
    stats_file = output_path / "statistical_summary.json"
    with open(stats_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary: {stats_file}")

    filtered_file = output_path / "filtered_tables.json"
    with open(filtered_file, 'w') as f:
        json.dump(filtered_tables, f, indent=2)
    print(f"Saved filtered tables: {filtered_file}")

    sig_count = summary.get('significant_count', 0)
    total_count = summary.get('total_tests', 0)
    print(f"Significant: {sig_count}/{total_count}")

    print("\n" + "=" * 60)
    print("✅ Stage 4 Complete!")
    print(f"📊 Significant tables identified")
    print("=" * 60)

    return True


def main():
    """CLI entry point for Stage 4."""
    parser = argparse.ArgumentParser(
        description="Stage 4: Statistical Analysis"
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

    return run_stage(
        args.crosstabs_file,
        args.spec_file,
        args.output_dir,
        threshold
    )


if __name__ == "__main__":
    sys.exit(main())
