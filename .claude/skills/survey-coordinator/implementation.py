"""
Survey Coordinator - Workflow Orchestrator

Orchestrates all 5 stages of survey analysis workflow.
Uses spss-analyzer CLI for all operations.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime


def run_workflow(
    sav_file: str,
    output_dir: str = "output",
    skip_stages: Optional[str] = None
) -> bool:
    """Run complete 5-stage analysis workflow using spss-analyzer CLI.

    Args:
        sav_file: Path to SPSS .sav file
        output_dir: Output directory for all results
        skip_stages: Stages to skip (e.g., "3,4")

    Returns:
        True if workflow completed successfully
    """
    # Use spss-analyzer CLI to run workflow
    result = _run_cli(['spss-analyzer', 'all',
                         '--sav-file', sav_file,
                         '--output-dir', output_dir] +
                         (['--skip', skip_stages] if skip_stages else []))

    if result == 0:
        print("\n" + "=" * 60)
        print("✅ All stages completed successfully!")
        print(f"📂 Results saved to: {output_dir}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Workflow did not complete successfully")
        print("=" * 60)

    return result == 0


def _run_cli(args: list) -> int:
    """Run spss-analyzer CLI command."""
    import subprocess
    result = subprocess.run(['spss-analyzer'] + args,
                          capture_output=False)
    return result.returncode


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
