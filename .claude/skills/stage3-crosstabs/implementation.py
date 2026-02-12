"""
Stage 3: Cross-Table Calculation

Uses spss_analyzer library modules directly.
"""

import sys
import argparse
import json
from pathlib import Path


def run_stage(
    sav_file: str,
    spec_file: str,
    metadata_file: str,
    output_dir: str = "output"
) -> bool:
    """Run Stage 3 using library modules directly."""
    print("=" * 60)
    print("📊 Stage 3: Cross-Table Calculation")
    print("=" * 60)

    from spss_analyzer.analysis import IndicatorsCalculator
    from spss_analyzer.pspp import CTablesSyntaxGenerator

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load specification
    with open(spec_file, 'r') as f:
        spec = json.load(f)

    # Load metadata
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Compute indicators
    calc = IndicatorsCalculator()
    indicators = calc.compute(spec.get('indicators', []), metadata)

    indicators_file = output_path / "indicators.json"
    with open(indicators_file, 'w') as f:
        json.dump(indicators, f, indent=2)
    print(f"Saved indicators: {indicators_file}")

    # Generate crosstabs syntax
    ctables_gen = CTablesSyntaxGenerator()
    tables_spec = spec.get('tables', [])

    crosstabs = {}
    for table_spec in tables_spec:
        table_id = table_spec.get('id')
        crosstabs[table_id] = {
            'spec': table_spec,
            'syntax': ctables_gen.generate([table_spec])
        }

    # Save crosstabs
    crosstabs_file = output_path / "cross_tables.json"
    with open(crosstabs_file, 'w') as f:
        json.dump(crosstabs, f, indent=2)
    print(f"Saved crosstabs: {crosstabs_file}")

    print("\n" + "=" * 60)
    print("✅ Stage 3 Complete!")
    print("=" * 60)

    return True


def main():
    """CLI entry point for Stage 3."""
    parser = argparse.ArgumentParser(
        description="Stage 3: Cross-Table Calculation"
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
