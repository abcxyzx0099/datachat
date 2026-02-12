"""
Stage 4: Statistical Analysis - CLI Wrapper

Uses spss-analyzer CLI for statistics operations.
"""

import sys
import argparse


def _run_cli(args: list) -> int:
    """Run spss-analyzer CLI command."""
    import subprocess
    result = subprocess.run(['spss-analyzer'] + args,
                          capture_output=False)
    return result.returncode


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

    # Calculate chi-square using CLI
    result = _run_cli(['stats', 'test',
                         '--crosstabs-file', crosstabs_file,
                         '--threshold', str(threshold)])

    if result != 0:
        return False

    # Filter significant tables (output goes to output_dir)
    result = _run_cli(['stats', 'filter',
                         '--results-file', f'{output_dir}/test_results.json',
                         '--output-file', f'{output_dir}/filtered_tables.json'])

    if result != 0:
        return False

    # Save summary
    result = _run_cli(['stats', 'filter',
                         '--results-file', f'{output_dir}/test_results.json',
                         '--output-file', f'{output_dir}/filtered_tables.json'])

    if result != 0:
        return False

    print("\n" + "=" * 60)
    print("✅ Stage 4 Complete!")
    print(f"📊 Significant tables identified")
    print("=" * 60)

    return True


def main():
    """CLI entry point for Stage 4."""
    parser = argparse.ArgumentParser(
        description="Stage 4: Statistical Analysis (CLI wrapper)"
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
    if args.threshold is None:
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
