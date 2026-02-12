"""
Statistics operations - Calculate chi-square tests and filter results.

Semantic operations for statistical analysis.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import argparse


def calculate_chi_square(
    crosstabs: Dict[str, Any],
    threshold: float = 0.05
) -> List[Dict[str, Any]]:
    """Calculate chi-square tests for cross-tables.

    Args:
        crosstabs: Dictionary of cross-table data
        threshold: Significance threshold (default: 0.05)

    Returns:
        List of test results with chi-square statistics
    """
    try:
        from scipy.stats import chi2_contingency
    except ImportError:
        print("❌ Error: scipy not available")
        print("   Install: pip install scipy")
        sys.exit(1)

    import pandas as pd
    import numpy as np

    results = []

    for table_id, table_data in crosstabs.items():
        # Convert to DataFrame
        df = pd.DataFrame(table_data)

        try:
            # Calculate chi-square
            chi2, p_value, dof, expected = chi2_contingency(df.values)

            results.append({
                'table_id': table_id,
                'table_name': table_data.get('row_label', table_id),
                'chi_square': float(chi2),
                'p_value': float(p_value),
                'degrees_of_freedom': int(dof),
                'expected': expected.tolist() if hasattr(expected, 'tolist') else list(expected),
                'significant': bool(p_value < threshold)
            })

            sig_marker = '*' if p_value < 0.05 else '**' if p_value < 0.01 else '***' if p_value < 0.001 else ''
            print(f"   {table_id}: χ²={chi2:.2f}, p={p_value:.4f}{sig_marker}")

        except ValueError as e:
            results.append({
                'table_id': table_id,
                'table_name': table_data.get('row_label', table_id),
                'error': str(e)
            })
            print(f"   Error in {table_id}: {e}")
        except Exception as e:
            results.append({
                'table_id': table_id,
                'error': f"Calculation failed: {e}"
            })
            print(f"   Error in {table_id}: {e}")

    sig_count = sum(1 for r in results if r.get('significant', False))
    print(f"✅ Tested {len(results)} tables, {sig_count} significant")

    return results


def filter_significant(
    test_results: List[Dict[str, Any]],
    threshold: Optional[float] = None
) -> Tuple[List[Dict[str, Any], Dict[str, Any]]:
    """Filter tables by statistical significance.

    Args:
        test_results: List of chi-square test results
        threshold: Override threshold (uses results' threshold if None)

    Returns:
        Tuple of (filtered_results, summary)
    """
    filtered = []
    excluded = []

    for result in test_results:
        if 'error' in result:
            # Tables with errors are excluded
            excluded.append(result)
        elif result.get('significant', False):
            filtered.append(result)
        else:
            excluded.append(result)

    summary = {
        'total_tests': len(test_results),
        'significant_count': len(filtered),
        'excluded_count': len(excluded),
        'significance_threshold': threshold
    }

    print(f"✅ Filtered to {len(filtered)} significant tables")
    return filtered, summary


def save_statistics(
    results: List[Dict[str, Any]],
    summary: Dict[str, Any],
    output_dir: str
) -> None:
    """Save statistical results to files.

    Args:
        results: List of test results
        summary: Summary statistics
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save filtered results
    filtered_file = output_path / "filtered_tables.json"
    with open(filtered_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Save summary
    summary_file = output_path / "statistical_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"✅ Saved: {filtered_file}")
    print(f"✅ Saved: {summary_file}")


def get_significance_symbol(p_value: float) -> str:
    """Get significance symbol for p-value.

    Args:
        p_value: P-value from test

    Returns:
        Significance symbol
    """
    if p_value < 0.001:
        return '***'
    elif p_value < 0.01:
        return '**'
    elif p_value < 0.05:
        return '*'
    else:
        return ''


def main():
    """CLI entry point for statistics operations."""
    parser = argparse.ArgumentParser(
        description="Statistical analysis for SPSS survey data"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # test command
    test_parser = subparsers.add_parser('test', help='Calculate chi-square tests')
    test_parser.add_argument('--crosstabs-file', required=True, help='Path to crosstabs JSON')
    test_parser.add_argument('--threshold', type=float, default=0.05, help='Significance threshold')
    test_parser.add_argument('--output-dir', default='output', help='Output directory')

    # filter command
    filter_parser = subparsers.add_parser('filter', help='Filter significant tables')
    filter_parser.add_argument('--results-file', required=True, help='Path to test results JSON')
    filter_parser.add_argument('--threshold', type=float, help='Override threshold')
    filter_parser.add_argument('--output-file', default='output/filtered_tables.json', help='Output file')

    args = parser.parse_args()

    if args.command == 'test':
        with open(args.crosstabs_file, 'r') as f:
            crosstabs = json.load(f)

        results = calculate_chi_square(crosstabs, args.threshold)
        summary = {
            'total_tests': len(results),
            'significant_count': sum(1 for r in results if r.get('significant', False)),
            'significance_threshold': args.threshold
        }

        # Save test results
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results_file = output_path / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        summary_file = output_path / "statistical_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"✅ Saved: {results_file}")
        print(f"✅ Saved: {summary_file}")

    elif args.command == 'filter':
        with open(args.results_file, 'r') as f:
            results = json.load(f)

        filtered, summary = filter_significant(results, args.threshold)

        with open(args.output_file, 'w') as f:
            json.dump(filtered, f, indent=2)

        summary_file = Path(args.output_file).parent / "statistical_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"✅ Saved: {args.output_file}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
