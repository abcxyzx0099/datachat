"""
Data operations - Read, filter, and transform SPSS metadata.

Semantic operations on survey data. No stage concept.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse


def read_metadata(sav_file: str) -> tuple:
    """Read metadata from SPSS .sav file.

    Args:
        sav_file: Path to .sav file

    Returns:
        Tuple of (data_dict, metadata_dict)
    """
    try:
        from spss_analyzer.io import SPSSReader
        reader = SPSSReader()
        data, meta = reader.read(sav_file)

        # Convert to dict format for CLI operations
        data_dict = data.to_dict('records') if hasattr(data, 'to_dict') else []
        metadata_dict = _convert_metadata_to_dict(meta)

        print(f"✅ Read {len(data_dict)} rows, {len(metadata_dict.get('variables', []))} variables")
        return data_dict, metadata_dict

    except ImportError:
        print("❌ Error: spss_analyzer.io.SPSSReader not available")
        print("   Ensure lib directory is in PYTHONPATH")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading .sav file: {e}")
        sys.exit(1)


def filter_variables(
    metadata: Dict[str, Any],
    min_categories: int = 2,
    max_categories: int = 10,
    variable_types: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Filter metadata variables for analysis.

    Args:
        metadata: Input metadata dictionary
        min_categories: Minimum number of categories (default: 2)
        max_categories: Maximum number of categories (default: 10)
        variable_types: List of types to include (None = all)
        exclude_patterns: Patterns to exclude (e.g., ['other_', 'misc_'])

    Returns:
        Filtered metadata dictionary
    """
    variables = metadata.get('variables', {})
    filtered = {}

    for var_name, var_info in variables.items():
        # Exclude by pattern
        if exclude_patterns:
            if any(pattern in var_name for pattern in exclude_patterns):
                continue

        # Exclude by type
        if variable_types:
            var_type = var_info.get('variable_type', '')
            if var_type not in variable_types:
                continue

        # Filter by category count
        value_labels = var_info.get('value_labels', {})
        category_count = len(value_labels)

        if category_count < min_categories or category_count > max_categories:
            continue

        filtered[var_name] = var_info

    filtered_metadata = metadata.copy()
    filtered_metadata['variables'] = filtered

    print(f"✅ Filtered to {len(filtered)} variables")
    return filtered_metadata


def transform_metadata(
    metadata: Dict[str, Any],
    transform_type: str = "variable_centered"
) -> Dict[str, Any]:
    """Transform metadata to specified format.

    Args:
        metadata: Input metadata dictionary
        transform_type: Format ('variable_centered', 'analysis_ready')

    Returns:
        Transformed metadata dictionary
    """
    if transform_type == "variable_centered":
        return metadata  # Already in variable-centered format
    elif transform_type == "analysis_ready":
        # Add analysis-specific fields
        result = metadata.copy()
        for var_name, var_info in result.get('variables', {}).items():
            var_info['analysis_ready'] = True
            var_info['category_count'] = len(var_info.get('value_labels', {}))
        return result
    else:
        return metadata


def save_metadata(metadata: Dict[str, Any], output_file: str) -> None:
    """Save metadata to JSON file.

    Args:
        metadata: Metadata dictionary to save
        output_file: Output file path
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Saved: {output_file}")


def _convert_metadata_to_dict(meta: Any) -> Dict[str, Any]:
    """Convert metadata object to dictionary format."""
    if isinstance(meta, dict):
        return meta
    # Handle SPSS reader output format
    result = {
        'variables': {},
        'file_info': {}
    }

    # Extract file info if available
    if hasattr(meta, 'get'):
        result['file_info'] = {
            'case_count': meta.get('case_count', 0),
            'variable_count': len(meta.get('variables', []))
        }

    # Convert variables
    variables = meta.get('variables', []) if hasattr(meta, 'get') else []
    for var in variables:
        if hasattr(var, 'to_dict'):
            var_dict = var.to_dict()
        else:
            var_dict = var
        var_name = var_dict.get('name', str(var))
        result['variables'][var_name] = var_dict

    return result


def main():
    """CLI entry point for data operations."""
    parser = argparse.ArgumentParser(
        description="Data operations for SPSS survey analysis"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # read command
    read_parser = subparsers.add_parser('read', help='Read metadata from .sav file')
    read_parser.add_argument('--sav-file', required=True, help='Path to .sav file')
    read_parser.add_argument('--output-dir', default='output', help='Output directory')

    # filter command
    filter_parser = subparsers.add_parser('filter', help='Filter variables for analysis')
    filter_parser.add_argument('--metadata-file', required=True, help='Path to metadata JSON')
    filter_parser.add_argument('--output-file', default='output/filtered_metadata.json', help='Output file')
    filter_parser.add_argument('--min-categories', type=int, default=2, help='Min categories')
    filter_parser.add_argument('--max-categories', type=int, default=10, help='Max categories')
    filter_parser.add_argument('--types', nargs='+', help='Variable types to include')
    filter_parser.add_argument('--exclude', nargs='+', help='Patterns to exclude')

    args = parser.parse_args()

    if args.command == 'read':
        data, metadata = read_metadata(args.sav_file)
        if args.output_dir:
            output_file = Path(args.output_dir) / "metadata.json"
            save_metadata(metadata, str(output_file))

    elif args.command == 'filter':
        with open(args.metadata_file, 'r') as f:
            metadata = json.load(f)

        filtered = filter_variables(
            metadata,
            min_categories=args.min_categories,
            max_categories=args.max_categories,
            variable_types=args.types,
            exclude_patterns=args.exclude
        )
        save_metadata(filtered, args.output_file)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
