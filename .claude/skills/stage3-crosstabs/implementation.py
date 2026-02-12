"""
Stage 3: Cross-Table Calculation

Executes recoding, indicator computation, and cross-table generation.
Integrates with PSPP for syntax generation and execution.
"""

import json
import os
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    from spss_analyzer.io import SPSSReader
    from spss_analyzer.pspp import PSPPExecutor
except ImportError:
    print("❌ Error: spss_analyzer library modules not found")
    print("   Install lib directory to PYTHONPATH")
    import sys
    sys.exit(1)


def generate_pspp_recoding_syntax(recodings: List[Dict[str, Any]]) -> Optional[str]:
    """Generate PSPP recode syntax from recoding rules.

    Args:
        recodings: List of recoding rule dictionaries

    Returns:
        PSPP syntax string or None if no recodings
    """
    if not recodings:
        return None

    syntax_lines = ["RECODE"]
    for recoding in recodings:
        var_name = recoding.get("variable", "")
        target_var = recoding.get("target", var_name)  # Default to same variable
        recoding_type = recoding.get("type", "value")

        if recoding_type == "value_map":
            # Value remapping: var1 = 1 -> 100, 2 -> 75
            mapping_parts = [f"{int(k)} -> {int(v)}" for k, v in recoding.get("value_mappings", {}).items()]
            syntax_lines.append(f"  {var_name}={', '.join(mapping_parts))}")
        elif recoding_type == "range":
            # Range recoding: values 1-3 become "Low", 4-5 become "High"
            ranges = recoding.get("ranges", [])
            for i, range_def in enumerate(ranges):
                if i == 0:
                    values = range_def.get("values", [])
                else:
                    values_str = ", ".join(range_def.get("values", []))
                syntax_lines.append(f"  {var_name}={values_str} INTO {range_def.get('name', var_name)}")
        elif recoding_type == "missing":
            # Set to missing: sysmis = $SYSMIS
            syntax_lines.append(f"  {var_name}=$SYSMIS")
        else:
            print(f"   Warning: Unknown recoding type: {recoding_type}")

    syntax_lines.append("EXECUTE.")
    return "\n".join(syntax_lines)


def compute_indicators(
    indicators_spec: List[Dict[str, Any]],
    data: pd.DataFrame,
    metadata: Dict[str, Any]
) -> pd.DataFrame:
    """Compute indicator values from specification.

    Args:
        indicators_spec: List of indicator definitions
        data: Source data DataFrame
        metadata: Variable metadata for label lookup

    Returns:
        DataFrame with indicator values
    """
    results = []

    for indicator_spec in indicators_spec:
        indicator_id = indicator_spec.get("id", "")
        var_names = indicator_spec.get("variables", [])
        aggregation = indicator_spec.get("aggregation", "mean")

        if not var_names:
            print(f"   Warning: No variables for indicator {indicator_id}")
            continue

        # Get variable data
        var_data = data[var_names].dropna()

        # Compute based on aggregation
        if aggregation == "mean":
            value = float(var_data.mean().iloc[0])
        elif aggregation == "sum":
            value = float(var_data.sum().iloc[0])
        elif aggregation == "count":
            value = int(var_data.count().iloc[0])
        elif aggregation == "median":
            value = float(var_data.median().iloc[0])
        elif aggregation == "min":
            value = float(var_data.min().iloc[0])
        elif aggregation == "max":
            value = float(var_data.max().iloc[0])
        else:
            value = None
            print(f"   Warning: Unknown aggregation: {aggregation}")

        results.append({
            "indicator_id": indicator_id,
            "value": value
        })

        print(f"   Computed: {indicator_spec.get('name', indicator_id)} = {value}")

    return pd.DataFrame(results)


def generate_pspp_crosstabs_syntax(
    tables_spec: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> str:
    """Generate PSPP ctables syntax from table specifications.

    Args:
        tables_spec: List of table specifications
        metadata: Variable metadata for labels

    Returns:
        PSPP ctables syntax string
    """
    syntax_lines = []

    for table_spec in tables_spec:
        table_id = table_spec.get("id", "")
        row_var = table_spec.get("rows", {}).get("variable", "")
        col_var = table_spec.get("columns", {}).get("variable", "")

        # Get variable labels
        row_label = metadata.get(row_var, {}).get("label", row_var)
        col_label = metadata.get(col_var, {}).get("label", col_var)

        syntax_lines.append(f"ctables {row_var} BY {col_var}")
        syntax_lines.append(f"/tables {table_id} TITLE '{table_spec.get('name', table_id)}'")

    syntax_lines.append("STATISTICS")
    syntax_lines.append("  CELLS=COUNT ROW COL.")
    syntax_lines.append("  COUNT")

    syntax_lines.append("EXECUTE.")

    return "\n".join(syntax_lines)


def save_results(
    output_dir: Path,
    indicators_data: pd.DataFrame,
    cross_tables_dict: Dict[str, Any],
    recoding_syntax: Optional[str],
    crosstabs_syntax: str
) -> Tuple[Path, Path, Path, Path, Path]:
    """Save all outputs from Stage 3."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save indicators
    indicators_file = output_dir / "indicators.csv"
    indicators_data.to_csv(indicators_file, index=False)

    # Save cross-tables
    cross_tables_file = output_dir / "cross_tables.json"
    with open(cross_tables_file, 'w') as f:
        json.dump(cross_tables_dict, f, indent=2)

    # Save recoding syntax (if generated)
    recoding_file = None
    if recoding_syntax:
        recoding_file = output_dir / "pspp_recoding.sps"
        with open(recoding_file, 'w') as f:
            f.write(recoding_syntax)
        recoding_file = recoding_file

    # Save crosstabs syntax
    crosstabs_file = output_dir / "pspp_crosstabs.sps"
    with open(crosstabs_file, 'w') as f:
        f.write(crosstabs_syntax)

    return indicators_file, cross_tables_file, recoding_file, crosstabs_file


def main():
    """Main entry point for stage3-crosstabs skill."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cross-Table Calculation with PSPP integration"
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

    print("📊 Stage 3: Cross-Table Calculation")
    print("=" * 60)

    # Validate inputs
    sav_file = Path(args.sav_file)
    spec_file = Path(args.spec_file)
    metadata_file = Path(args.metadata_file)
    output_dir = Path(args.output_dir)

    if not sav_file.exists():
        print(f"❌ Error: .sav file not found: {sav_file}")
        return 1

    if not spec_file.exists():
        print(f"❌ Error: Spec file not found: {spec_file}")
        return 1

    if not metadata_file.exists():
        print(f"❌ Error: Metadata file not found: {metadata_file}")
        return 1

    # Load data
    print("\n📖 Loading survey data...")
    reader = SPSSReader()
    data, meta = reader.read(str(sav_file))
    print(f"   Loaded: {len(data)} rows, {len(meta.get('variables', []))} variables")

    # Load specification
    print("\n📋 Loading table specification...")
    with open(spec_file, 'r') as f:
        spec = json.load(f)

    indicators_spec = spec.get("indicators", [])
    tables_spec = spec.get("tables", [])
    global_recodings = spec.get("global_recodings", [])

    # Step 7: Apply recoding rules
    print("\n[Step 7] Applying recoding rules...")
    recoding_syntax = generate_pspp_recoding_syntax(global_recodings)

    if recoding_syntax:
        print(f"   Generated PSPP syntax:")
        for line in recoding_syntax.split('\n'):
            print(f"     {line}")
        recoding_file = output_dir / "pspp_recoding.sps"

        print(f"\n   Would apply PSPP recoding (not yet implemented)")
    else:
        print("   No global recodings - skipping")

    # Step 8: Compute indicators
    print("\n[Step 8] Computing indicators...")
    indicators_data = compute_indicators(indicators_spec, data, meta)

    # Save indicators
    indicators_file, cross_tables_file, recoding_file, crosstabs_file = save_results(
        output_dir,
        indicators_data,
        {},  # No cross_tables yet
        recoding_syntax
        ""  # No crosstabs yet
    )

    print(f"   Saved: {indicators_file}")

    # Step 9: Generate cross-tables
    print("\n[Step 9] Generating cross-tables...")
    crosstabs_syntax = generate_pspp_crosstabs_syntax(tables_spec, meta)

    print(f"   Generated PSPP ctables syntax:")
    for line in crosstabs_syntax.split('\n'):
        print(f"     {line}")

    # Load existing data and add tables
    cross_tables_dict = {}
    existing_data = None

    if cross_tables_file.exists():
        with open(cross_tables_file, 'r') as f:
            cross_tables_dict = json.load(f)
        print(f"   Loaded {len(cross_tables_dict)} existing tables")
        existing_data = data

    # Merge new tables with existing
    for table_id, table in cross_tables_dict.items():
        df = pd.DataFrame(table)
        if existing_data is not None:
            # Add grand total column
            df['N_Count'] = df.sum(axis=1)
        cross_tables_dict[table_id] = df.to_dict()

    # Save merged tables
    indicators_file, cross_tables_file, recoding_file, crosstabs_file = save_results(
        output_dir,
        indicators_data,
        cross_tables_dict,
        recoding_syntax,
        crosstabs_syntax
    )

    print(f"\n   Total tables: {len(cross_tables_dict)}")
    print(f"   Saved: {cross_tables_file}")

    print("\n✅ Stage 3 Complete!")
    print()
    print("=" * 60)
    return 0
