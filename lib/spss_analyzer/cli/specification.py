"""
Specification generation - Create table and indicator specifications.

Semantic operations for generating analysis specifications.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse


def generate_tables(
    metadata: Dict[str, Any],
    table_count: int = 20,
    include_demographics: bool = True,
    include_satisfaction: bool = True
) -> Dict[str, Any]:
    """Generate table specifications from metadata.

    Args:
        metadata: Survey metadata dictionary
        table_count: Target number of tables (default: 20)
        include_demographics: Include demographic crosstabs (default: True)
        include_satisfaction: Include satisfaction tables (default: True)

    Returns:
        Specification dictionary with tables and indicators
    """
    variables = metadata.get('variables', {})
    categorical_vars = [
        v for v, info in variables.items()
        if info.get('variable_type') in ['categorical', 'ordinal']
    ]

    # Identify variable groups
    demographic_vars = [v for v in categorical_vars if v.startswith('dem_')]
    satisfaction_vars = [v for v in categorical_vars if 'sat' in v.lower() or 'satisfaction' in v.lower()]

    tables = []
    table_id = 1

    # Generate demographic crosstabs
    if include_demographics and len(demographic_vars) >= 2:
        for i, var1 in enumerate(demographic_vars[:-1]):
            for var2 in demographic_vars[i+1:]:
                tables.append({
                    'id': f'table_{table_id:03d}',
                    'name': f"{var1} × {var2}",
                    'rows': {'variable': var1},
                    'columns': {'variable': var2},
                    'metrics': ['count', 'row_percent', 'col_percent']
                })
                table_id += 1

    # Generate satisfaction tables
    if include_satisfaction and satisfaction_vars:
        for sat_var in satisfaction_vars:
            if demographic_vars:
                for dem_var in demographic_vars[:2]:  # Limit to top 2
                    tables.append({
                        'id': f'table_{table_id:03d}',
                        'name': f"{dem_var} × {sat_var}",
                        'rows': {'variable': dem_var},
                        'columns': {'variable': sat_var},
                        'metrics': ['count', 'row_percent', 'col_percent']
                    })
                    table_id += 1

    print(f"✅ Generated {len(tables)} table specifications")
    return {
        'version': '1.0',
        'tables': tables[:table_count]
    }


def generate_indicators(
    metadata: Dict[str, Any],
    include_mean: bool = True,
    include_percentage: bool = True,
    include_nps: bool = True
) -> List[Dict[str, Any]]:
    """Generate indicator specifications.

    Args:
        metadata: Survey metadata dictionary
        include_mean: Include mean indicators (default: True)
        include_percentage: Include percentage indicators (default: True)
        include_nps: Include NPS indicators (default: True)

    Returns:
        List of indicator specifications
    """
    variables = metadata.get('variables', {})
    scale_vars = [
        v for v, info in variables.items()
        if info.get('variable_type') == 'ordinal'
    ]

    indicators = []

    # Mean indicators
    if include_mean and scale_vars:
        for var in scale_vars[:3]:  # Top 3 scale variables
            indicators.append({
                'id': f'ind_mean_{len(indicators)+1}',
                'name': f"Mean {var}",
                'variables': [var],
                'aggregation': 'mean'
            })

    # Percentage indicators
    if include_percentage and scale_vars:
        for var in scale_vars[:2]:
            indicators.append({
                'id': f'ind_pct_{len(indicators)+1}',
                'name': f"Top 2 Box {var}",
                'variables': [var],
                'aggregation': 'percentage',
                'threshold': 2  # Top 2 categories
            })

    # NPS indicator
    if include_nps:
        nps_vars = [v for v in scale_vars if 'nps' in v.lower() or 'promoter' in v.lower()]
        if nps_vars:
            indicators.append({
                'id': f'ind_nps_{len(indicators)+1}',
                'name': 'Net Promoter Score',
                'variables': nps_vars[:1],
                'aggregation': 'nps'
            })

    print(f"✅ Generated {len(indicators)} indicator specifications")
    return indicators


def save_specification(spec: Dict[str, Any], output_file: str) -> None:
    """Save specification to JSON file.

    Args:
        spec: Specification dictionary
        output_file: Output file path
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(spec, f, indent=2)

    print(f"✅ Saved: {output_file}")


def combine_specifications(
    tables_spec: Dict[str, Any],
    indicators_spec: List[Dict[str, Any]],
    output_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Combine tables and indicators into full specification.

    Args:
        tables_spec: Table specifications from generate_tables()
        indicators_spec: Indicator specs from generate_indicators()
        output_settings: Optional output configuration

    Returns:
        Complete specification dictionary
    """
    result = tables_spec.copy()

    if indicators_spec:
        result['indicators'] = indicators_spec

    if output_settings:
        result['output_settings'] = output_settings
    else:
        result['output_settings'] = {
            'significance_threshold': 0.05,
            'include_charts': True
        }

    result['global_recodings'] = []
    result['generated_at'] = _get_timestamp()

    return result


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime
    return datetime.now().isoformat()


def main():
    """CLI entry point for specification operations."""
    parser = argparse.ArgumentParser(
        description="Specification generation for SPSS survey analysis"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # tables command
    tables_parser = subparsers.add_parser('tables', help='Generate table specifications')
    tables_parser.add_argument('--metadata-file', required=True, help='Path to metadata JSON')
    tables_parser.add_argument('--output-file', default='output/table_specification.json', help='Output file')
    tables_parser.add_argument('--count', type=int, default=20, help='Number of tables')
    tables_parser.add_argument('--no-demographics', action='store_true', help='Exclude demographic tables')
    tables_parser.add_argument('--no-satisfaction', action='store_true', help='Exclude satisfaction tables')

    # indicators command
    indicators_parser = subparsers.add_parser('indicators', help='Generate indicator specifications')
    indicators_parser.add_argument('--metadata-file', required=True, help='Path to metadata JSON')
    indicators_parser.add_argument('--output-file', default='output/indicators_spec.json', help='Output file')
    indicators_parser.add_argument('--no-mean', action='store_true', help='Exclude mean indicators')
    indicators_parser.add_argument('--no-percentage', action='store_true', help='Exclude percentage indicators')
    indicators_parser.add_argument('--no-nps', action='store_true', help='Exclude NPS indicators')

    # combine command
    combine_parser = subparsers.add_parser('combine', help='Combine tables and indicators')
    combine_parser.add_argument('--tables-file', required=True, help='Path to tables JSON')
    combine_parser.add_argument('--indicators-file', required=True, help='Path to indicators JSON')
    combine_parser.add_argument('--output-file', default='output/table_specification.json', help='Output file')

    args = parser.parse_args()

    if args.command == 'tables':
        with open(args.metadata_file, 'r') as f:
            metadata = json.load(f)

        spec = generate_tables(
            metadata,
            table_count=args.count,
            include_demographics=not args.no_demographics,
            include_satisfaction=not args.no_satisfaction
        )
        save_specification(spec, args.output_file)

    elif args.command == 'indicators':
        with open(args.metadata_file, 'r') as f:
            metadata = json.load(f)

        indicators = generate_indicators(
            metadata,
            include_mean=not args.no_mean,
            include_percentage=not args.no_percentage,
            include_nps=not args.no_nps
        )

        spec = {'indicators': indicators}
        save_specification(spec, args.output_file)

    elif args.command == 'combine':
        with open(args.tables_file, 'r') as f:
            tables = json.load(f)
        with open(args.indicators_file, 'r') as f:
            indicators = json.load(f)

        spec = combine_specifications(tables, indicators)
        save_specification(spec, args.output_file)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
