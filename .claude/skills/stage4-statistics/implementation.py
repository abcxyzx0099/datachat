"""
Stage 4: Statistical Analysis

Uses spss-analyzer CLI command.
"""

import sys
import argparse
import subprocess


def run_stage(
    crosstabs_file: str,
    spec_file: str,
    output_dir: str = "output",
    threshold: float = 0.05
) -> bool:
    """Run Stage 4 using spss-analyzer CLI."""
    print("=" * 60)
    print("📈 Stage 4: Statistical Analysis")
    print("=" * 60)

    # Calculate chi-square
    result = subprocess.run(
        ['spss-analyzer', 'stats', 'test',
         '--crosstabs-file', crosstabs_file,
         '--threshold', str(threshold),
         '--output-file', f'{output_dir}/test_results.json'],
        capture_output=False
    )

    if result.returncode != 0:
        return False

    print("Chi-square tests calculated")

    # Filter significant tables
    result = subprocess.run(
        ['spss-analyzer', 'stats', 'filter',
         '--crosstabs-file', f'{output_dir}/test_results.json',
         '--threshold', str(threshold),
         '--output-file', f'{output_dir}/filtered_tables.json'],
        capture_output=False
    )

    if result.returncode != 0:
        return False

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
        import json
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
