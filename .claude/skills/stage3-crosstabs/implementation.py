"""
Stage 3: Cross-Table Calculation Wrapper

Thin wrapper that calls semantic library analysis operations.
No processing logic - just orchestration.
"""

import sys
import json
import argparse
from pathlib import Path


def run_stage(
    sav_file: str,
    spec_file: str,
    metadata_file: str,
    output_dir: str = "output"
) -> bool:
    """Run Stage 3 using library CLI.

    Args:
        sav_file: Path to .sav file
        spec_file: Path to table_specification.json
        metadata_file: Path to filtered_metadata.json
        output_dir: Output directory

    Returns:
        True if successful
    """
    from spss_analyzer.cli import data, analysis

    print("=" * 60)
    print("📊 Stage 3: Cross-Table Calculation")
    print("=" * 60)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load metadata
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Load specification
    with open(spec_file, 'r') as f:
        spec = json.load(f)

    # Use library to read data
    print("\n[Reading survey data...]")
    survey_data, metadata = data.read_metadata(sav_file)

    # Use library to compute indicators
    print("[Computing indicators...]")
    indicators_data = analysis.compute_indicators(
        survey_data if survey_data else [],
        spec.get('indicators', []),
        metadata
    )

    indicators_file = output_path / "indicators.csv"
    analysis.save_indicators(indicators_data, str(indicators_file))

    # Use library to generate crosstabs
    print("\n[Generating cross-tables...]")
    crosstabs = analysis.generate_crosstabs(spec.get('tables', []), metadata)

    crosstabs_file = output_path / "cross_tables.json"
    analysis.save_crosstabs(crosstabs, str(crosstabs_file))

    print("\n" + "=" * 60)
    print("✅ Stage 3 Complete!")
    print(f"📄 Saved: {indicators_file}")
    print(f"📄 Saved: {crosstabs_file}")
    print("=" * 60)

    return True


def main():
    """CLI entry point for Stage 3."""
    parser = argparse.ArgumentParser(
        description="Stage 3: Cross-Table Calculation (wrapper)"
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

    return 0 if run_stage(
        args.sav_file,
        args.spec_file,
        args.metadata_file,
        args.output_dir
    ) else 1


if __name__ == "__main__":
    sys.exit(main())
