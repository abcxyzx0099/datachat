"""
Stage 2: Table Specification - AI Specification Wrapper

Thin wrapper that calls semantic library specification operations.
No processing logic - just orchestration.
"""

import sys
import argparse


def run_stage(metadata_file: str, output_dir: str = "output") -> bool:
    """Run Stage 2 using library CLI.

    Args:
        metadata_file: Path to filtered_metadata.json
        output_dir: Output directory

    Returns:
        True if successful
    """
    from spss_analyzer.cli import specification

    print("=" * 60)
    print("📋 Stage 2: Table Specification")
    print("=" * 60)

    # Import metadata
    import json
    from pathlib import Path

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Use library to generate tables
    print("\n[Generating table specifications...]")
    tables_spec = specification.generate_tables(metadata)

    # Use library to generate indicators
    print("[Generating indicator specifications...]")
    indicators_spec = specification.generate_indicators(metadata)

    # Use library to combine and save
    full_spec = specification.combine_specifications(tables_spec, indicators_spec)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    spec_file = output_path / "table_specification.json"
    specification.save_specification(full_spec, str(spec_file))

    print("\n" + "=" * 60)
    print("✅ Stage 2 Complete!")
    print(f"📄 Saved: {spec_file}")
    print("=" * 60)

    return True


def main():
    """CLI entry point for Stage 2."""
    parser = argparse.ArgumentParser(
        description="Stage 2: Table Specification (wrapper)"
    )

    parser.add_argument("--metadata-file", required=True,
                        help="Path to filtered_metadata.json from Stage 1")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory")

    args = parser.parse_args()

    return 0 if run_stage(args.metadata_file, args.output_dir) else 1


if __name__ == "__main__":
    sys.exit(main())
