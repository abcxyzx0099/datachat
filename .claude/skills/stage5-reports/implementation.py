"""
Stage 5: Reporting

Uses spss-analyzer CLI command.
"""

import sys
import argparse
import subprocess


def run_stage(
    filtered_tables_file: str,
    output_dir: str = "output"
) -> bool:
    """Run Stage 5 using spss-analyzer CLI."""
    print("=" * 60)
    print("📑 Stage 5: Reporting")
    print("=" * 60)

    # Generate PowerPoint
    result = subprocess.run(
        ['spss-analyzer', 'reporting', 'ppt',
         '--tables-file', filtered_tables_file,
         '--output-dir', output_dir],
        capture_output=False
    )

    if result.returncode != 0:
        return False

    print("PowerPoint generated")

    # Generate HTML Dashboard
    result = subprocess.run(
        ['spss-analyzer', 'reporting', 'html',
         '--tables-file', filtered_tables_file,
         '--output-dir', output_dir],
        capture_output=False
    )

    if result.returncode != 0:
        return False

    print("HTML dashboard generated")

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
