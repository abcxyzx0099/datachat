"""
Stage 3: Cross-Table Calculation - CLI Wrapper

Uses spss-analyzer CLI for analysis operations.
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
    sav_file: str,
    spec_file: str,
    metadata_file: str,
    output_dir: str = "output"
) -> bool:
    """Run Stage 3 using spss-analyzer CLI."""
    print("=" * 60)
    print("📊 Stage 3: Cross-Table Calculation")
    print("=" * 60)

    # Compute indicators using CLI
    result = _run_cli(['analysis', 'indicators',
                         '--spec-file', spec_file,
                         '--data-file', sav_file,
                         '--output-file', f'{output_dir}/indicators.csv'])

    if result != 0:
        return False

    # Generate crosstabs using CLI
    result = _run_cli(['analysis', 'crosstabs',
                         '--spec-file', spec_file,
                         '--metadata-file', metadata_file,
                         '--output-file', f'{output_dir}/cross_tables.json'])

    if result != 0:
        return False

    print("\n" + "=" * 60)
    print("✅ Stage 3 Complete!")
    print("=" * 60)

    return True


def main():
    """CLI entry point for Stage 3."""
    parser = argparse.ArgumentParser(
        description="Stage 3: Cross-Table Calculation (CLI wrapper)"
    )

    parser.add_argument("--sav-file", required=True,
                        help="Path to SPSS .sav file")
    parser.add_argument("--spec-file", required=True,
                        help="Path to table_specification.json from Stage 2")
    parser.add_argument("--metadata-file", required=True,
                        help="Path to filtered_metadata.json from Stage 1")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory")

    args = parser.parse_args()

    return run_stage(
        args.sav_file,
        args.spec_file,
        args.metadata_file,
        args.output_dir
    )


if __name__ == "__main__":
    sys.exit(main())
