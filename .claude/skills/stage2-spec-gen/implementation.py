"""
Stage 2: Table Specification - CLI Wrapper

Uses spss-analyzer CLI for specification operations.
"""

import sys
import argparse


def _run_cli(args: list) -> int:
    """Run spss-analyzer CLI command."""
    import subprocess
    result = subprocess.run(['spss-analyzer'] + args,
                          capture_output=False)
    return result.returncode


def run_stage(metadata_file: str, output_dir: str = "output") -> bool:
    """Run Stage 2 using spss-analyzer CLI."""
    print("=" * 60)
    print("📋 Stage 2: Table Specification")
    print("=" * 60)

    # Generate specification using CLI
    result = _run_cli(['spec', 'tables',
                         '--metadata-file', metadata_file])

    if result == 0:
        print("\n" + "=" * 60)
        print("✅ Stage 2 Complete!")
        print("=" * 60)

    return result == 0


def main():
    """CLI entry point for Stage 2."""
    parser = argparse.ArgumentParser(
        description="Stage 2: Table Specification (CLI wrapper)"
    )

    parser.add_argument("--metadata-file", required=True,
                        help="Path to filtered_metadata.json from Stage 1")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory")

    args = parser.parse_args()

    return run_stage(args.metadata_file, args.output_dir)


if __name__ == "__main__":
    sys.exit(main())
