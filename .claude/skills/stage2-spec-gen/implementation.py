"""
Stage 2: Table Specification

Uses spss_analyzer library modules directly.
"""

import sys
import argparse
import json
from pathlib import Path


def run_stage(metadata_file: str, output_dir: str = "output") -> bool:
    """Run Stage 2 using library modules directly."""
    print("=" * 60)
    print("📋 Stage 2: Table Specification")
    print("=" * 60)

    from spss_analyzer.specification import TableSpecificationGenerator

    # Load metadata
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Generate specification
    spec_gen = TableSpecificationGenerator()
    spec = spec_gen.generate(metadata)

    # Save specification
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    spec_file = output_path / "table_specification.json"
    with open(spec_file, 'w') as f:
        json.dump(spec, f, indent=2)

    print(f"Saved specification: {spec_file}")
    print(f"Tables generated: {len(spec.get('tables', []))}")

    print("\n" + "=" * 60)
    print("✅ Stage 2 Complete!")
    print("=" * 60)

    return True


def main():
    """CLI entry point for Stage 2."""
    parser = argparse.ArgumentParser(
        description="Stage 2: Table Specification"
    )

    parser.add_argument("--metadata-file", required=True,
                        help="Path to filtered_metadata.json from Stage 1")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory")

    args = parser.parse_args()

    return run_stage(args.metadata_file, args.output_dir)


if __name__ == "__main__":
    sys.exit(main())
