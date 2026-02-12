"""
Analysis operations - Compute indicators and generate cross-tables.

Semantic operations for data analysis and computation.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse


def compute_indicators(
    data: List[Dict[str, Any]],
    indicators_spec: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Compute indicator values from data.

    Args:
        data: List of response records
        indicators_spec: Indicator specifications
        metadata: Variable metadata for lookups

    Returns:
        List of computed indicator values
    """
    import pandas as pd

    df = pd.DataFrame(data)
    results = []

    for spec in indicators_spec:
        indicator_id = spec.get('id', '')
        var_names = spec.get('variables', [])
        aggregation = spec.get('aggregation', 'mean')

        if not var_names:
            print(f"   Warning: No variables for indicator {indicator_id}")
            continue

        # Get variable data
        var_data = df[var_names].dropna() if var_names else pd.DataFrame()

        if var_data.empty:
            results.append({
                'indicator_id': indicator_id,
                'value': None,
                'error': 'No data available'
            })
            continue

        # Compute based on aggregation type
        try:
            if aggregation == 'mean':
                value = float(var_data.mean().iloc[0])
            elif aggregation == 'sum':
                value = float(var_data.sum().iloc[0])
            elif aggregation == 'count':
                value = int(var_data.count().iloc[0])
            elif aggregation == 'median':
                value = float(var_data.median().iloc[0])
            elif aggregation == 'min':
                value = float(var_data.min().iloc[0])
            elif aggregation == 'max':
                value = float(var_data.max().iloc[0])
            elif aggregation == 'percentage':
                threshold = spec.get('threshold', 2)
                total = len(var_data)
                top_count = sum(var_data.iloc[:, 0].le(threshold))
                value = float(top_count) / float(total) * 100 if total > 0 else 0
            elif aggregation == 'nps':
                # Net Promoter Score: Promoters (9-10) - Detractors (0-6)
                value = _calculate_nps(var_data)
            else:
                value = None
                print(f"   Warning: Unknown aggregation: {aggregation}")

            results.append({
                'indicator_id': indicator_id,
                'name': spec.get('name', indicator_id),
                'value': value
            })
            print(f"   Computed: {spec.get('name', indicator_id)} = {value}")

        except Exception as e:
            results.append({
                'indicator_id': indicator_id,
                'error': str(e)
            })
            print(f"   Error computing {indicator_id}: {e}")

    print(f"✅ Computed {len(results)} indicators")
    return results


def _calculate_nps(var_data) -> float:
    """Calculate Net Promoter Score.

    NPS = % Promoters (9-10) - % Detractors (0-6)
    """
    try:
        values = var_data.iloc[:, 0].dropna()

        promoters = sum((values >= 9).astype(int))
        detractors = sum((values <= 6).astype(int))
        total = len(values)

        if total == 0:
            return 0.0

        pct_promoters = (promoters / total) * 100
        pct_detractors = (detractors / total) * 100

        return round(pct_promoters - pct_detractors, 1)
    except Exception:
        return 0.0


def generate_crosstabs(
    tables_spec: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate cross-table specifications.

    Args:
        tables_spec: List of table specifications
        metadata: Variable metadata

    Returns:
        Dictionary of table IDs to PSPP syntax
    """
    crosstabs = {}

    for table_spec in tables_spec:
        table_id = table_spec.get('id', '')
        row_var = table_spec.get('rows', {}).get('variable', '')
        col_var = table_spec.get('columns', {}).get('variable', '')

        # Get variable labels
        row_label = metadata.get('variables', {}).get(row_var, {}).get('label', row_var)
        col_label = metadata.get('variables', {}).get(col_var, {}).get('label', col_var)

        # Generate PSPP ctables syntax
        syntax_lines = [
            f"ctables {row_var} BY {col_var}",
            f"/tables {table_id} TITLE '{table_spec.get('name', table_id)}'"
        ]

        # Add statistics
        metrics = table_spec.get('metrics', ['count'])
        if 'count' in metrics:
            syntax_lines.append("/count")
        if 'row_percent' in metrics:
            syntax_lines.append("/row")

        crosstabs[table_id] = {
            'spec': table_spec,
            'syntax': '\n'.join(syntax_lines),
            'row_variable': row_var,
            'row_label': row_label,
            'column_variable': col_var,
            'column_label': col_label
        }

    print(f"✅ Generated syntax for {len(crosstabs)} cross-tables")
    return crosstabs


def apply_recodings(
    data: List[Dict[str, Any]],
    recodings: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Apply recoding rules to data.

    Args:
        data: Input data records
        recodings: List of recoding rules

    Returns:
        Data with recodings applied
    """
    if not recodings:
        print("   No recodings to apply")
        return data

    import pandas as pd
    df = pd.DataFrame(data)

    for recoding in recodings:
        var_name = recoding.get('variable', '')
        recoding_type = recoding.get('type', 'value')
        target_var = recoding.get('target', var_name)

        if var_name not in df.columns:
            print(f"   Warning: Variable {var_name} not found")
            continue

        if recoding_type == 'value_map':
            # Value remapping
            mapping = recoding.get('value_mappings', {})
            for old_val, new_val in mapping.items():
                df[var_name] = df[var_name].replace(int(old_val), int(new_val))
            print(f"   Applied value mapping: {var_name}")

        elif recoding_type == 'range':
            # Range recoding
            ranges = recoding.get('ranges', [])
            for range_def in ranges:
                values = range_def.get('values', [])
                range_name = range_def.get('name', f"range_{len(ranges)}")
                df.loc[df[var_name].isin(values), var_name] = range_name
            print(f"   Applied range recoding: {var_name}")

        elif recoding_type == 'missing':
            # Set to missing
            missing_vals = recoding.get('missing_values', [])
            df.loc[df[var_name].isin(missing_vals), var_name] = None
            print(f"   Set missing values for: {var_name}")

    print(f"✅ Applied {len(recodings)} recoding rules")
    return df.to_dict('records')


def save_indicators(indicators: List[Dict[str, Any]], output_file: str) -> None:
    """Save computed indicators to CSV.

    Args:
        indicators: List of indicator results
        output_file: Output CSV path
    """
    import pandas as pd

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(indicators)
    df.to_csv(output_path, index=False)

    print(f"✅ Saved: {output_file}")


def save_crosstabs(crosstabs: Dict[str, Any], output_file: str) -> None:
    """Save cross-table specifications to JSON.

    Args:
        crosstabs: Dictionary of table specifications
        output_file: Output JSON path
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(crosstabs, f, indent=2, default=str)

    print(f"✅ Saved: {output_file}")


def main():
    """CLI entry point for analysis operations."""
    parser = argparse.ArgumentParser(
        description="Analysis operations for SPSS survey data"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # indicators command
    ind_parser = subparsers.add_parser('indicators', help='Compute indicators')
    ind_parser.add_argument('--data-file', required=True, help='Path to data JSON')
    ind_parser.add_argument('--spec-file', required=True, help='Path to indicators spec JSON')
    ind_parser.add_argument('--output-file', default='output/indicators.csv', help='Output CSV file')

    # crosstabs command
    cross_parser = subparsers.add_parser('crosstabs', help='Generate cross-table syntax')
    cross_parser.add_argument('--spec-file', required=True, help='Path to table spec JSON')
    cross_parser.add_argument('--metadata-file', required=True, help='Path to metadata JSON')
    cross_parser.add_argument('--output-file', default='output/cross_tables.json', help='Output file')

    # recode command
    recode_parser = subparsers.add_parser('recode', help='Apply recodings')
    recode_parser.add_argument('--data-file', required=True, help='Path to data JSON')
    recode_parser.add_argument('--recoding-file', required=True, help='Path to recoding rules JSON')
    recode_parser.add_argument('--output-file', default='output/recoded_data.json', help='Output file')

    args = parser.parse_args()

    if args.command == 'indicators':
        with open(args.data_file, 'r') as f:
            data = json.load(f)
        with open(args.spec_file, 'r') as f:
            spec = json.load(f)

        indicators = compute_indicators(data, spec.get('indicators', []), {})
        save_indicators(indicators, args.output_file)

    elif args.command == 'crosstabs':
        with open(args.spec_file, 'r') as f:
            spec = json.load(f)
        with open(args.metadata_file, 'r') as f:
            metadata = json.load(f)

        crosstabs = generate_crosstabs(spec.get('tables', []), metadata)
        save_crosstabs(crosstabs, args.output_file)

    elif args.command == 'recode':
        with open(args.data_file, 'r') as f:
            data = json.load(f)
        with open(args.recoding_file, 'r') as f:
            recodings = json.load(f)

        recoded = apply_recodings(data, recodings)
        with open(args.output_file, 'w') as f:
            json.dump(recoded, f, indent=2)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
