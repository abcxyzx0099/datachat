"""
Survey Debug - Debugging & Testing Tool

Tests and validates library functions. Thin wrapper - uses semantic library operations.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional


def test_data_operations() -> bool:
    """Test data reading and filtering operations."""
    from spss_analyzer.cli import data

    print("🧪 Testing: Data Operations")
    print("-" * 60)

    # Test metadata conversion
    test_metadata = {
        'variables': {
            'test_var': {
                'label': 'Test Variable',
                'value_labels': {'1': 'Yes', '2': 'No'},
                'variable_type': 'categorical'
            }
        }
    }

    # Test filtering
    filtered = data.filter_variables(test_metadata, min_categories=2, max_categories=5)
    expected_count = 1  # test_var should be included
    actual_count = len(filtered.get('variables', {}))
    passed = actual_count == expected_count

    print(f"  Filter variables: {'PASS' if passed else 'FAIL'}")
    print(f"  Expected: {expected_count}, Got: {actual_count}")

    return passed


def test_specification_generation() -> bool:
    """Test specification generation."""
    from spss_analyzer.cli import specification

    print("\n🧪 Testing: Specification Generation")
    print("-" * 60)

    test_metadata = {
        'variables': {
            'q1_sat': {'label': 'Satisfaction', 'value_labels': {}, 'variable_type': 'ordinal'},
            'dem_gender': {'label': 'Gender', 'value_labels': {}, 'variable_type': 'categorical'}
        }
    }

    # Test table generation
    tables_spec = specification.generate_tables(test_metadata, table_count=5)
    tables_ok = len(tables_spec.get('tables', [])) > 0

    # Test indicator generation
    indicators_spec = specification.generate_indicators(test_metadata)
    indicators_ok = len(indicators_spec) > 0

    passed = tables_ok and indicators_ok

    print(f"  Generate tables: {'PASS' if tables_ok else 'FAIL'}")
    print(f"  Generate indicators: {'PASS' if indicators_ok else 'FAIL'}")

    return passed


def test_analysis_operations() -> bool:
    """Test analysis (indicators, crosstabs)."""
    from spss_analyzer.cli import analysis

    print("\n🧪 Testing: Analysis Operations")
    print("-" * 60)

    # Test indicator computation
    test_indicators_spec = [
        {'id': 'test1', 'variables': ['q1'], 'aggregation': 'mean'}
    ]
    test_data = [{'q1': 4}]
    test_metadata = {'variables': {'q1': {'value_labels': {}}}}

    indicators_result = analysis.compute_indicators(test_data, test_indicators_spec, test_metadata)
    indicators_ok = len(indicators_result) > 0

    # Test crosstabs generation
    test_tables_spec = [
        {'id': 'test1', 'rows': {'variable': 'q1'}, 'columns': {'variable': 'q2'}}
    ]
    crosstabs = analysis.generate_crosstabs(test_tables_spec, test_metadata)
    crosstabs_ok = len(crosstabs) > 0

    passed = indicators_ok and crosstabs_ok

    print(f"  Compute indicators: {'PASS' if indicators_ok else 'FAIL'}")
    print(f"  Generate crosstabs: {'PASS' if crosstabs_ok else 'FAIL'}")

    return passed


def test_statistics_operations() -> bool:
    """Test statistics operations."""
    from spss_analyzer.cli import statistics

    print("\n🧪 Testing: Statistics Operations")
    print("-" * 60)

    # Create test crosstabs
    test_crosstabs = {
        'table1': {
            'col1': [10, 20, 30],
            'col2': [15, 25, 35]
        }
    }

    # Test chi-square calculation
    test_results = statistics.calculate_chi_square(test_crosstabs, threshold=0.05)
    chi_ok = len(test_results) > 0

    # Test filtering
    filtered, summary = statistics.filter_significant(test_results)
    filter_ok = 'total_tests' in summary

    passed = chi_ok and filter_ok

    print(f"  Chi-square test: {'PASS' if chi_ok else 'FAIL'}")
    print(f"  Filter significant: {'PASS' if filter_ok else 'FAIL'}")

    return passed


def test_reporting_operations() -> bool:
    """Test reporting operations."""
    from spss_analyzer.cli import reporting

    print("\n🧪 Testing: Reporting Operations")
    print("-" * 60)

    test_tables = [
        {'table_id': 'test1', 'table_name': 'Test Table', 'significant': True}
    ]
    test_summary = {
        'total_tests': 1,
        'significant_count': 1,
        'significance_threshold': 0.05
    }

    # Test PowerPoint (skip actual generation to avoid file output)
    try:
        reporting.create_powerpoint(
            test_tables,
            test_summary,
            output_file='/tmp/test_presentation.pptx'
        )
        ppt_ok = True
        print(f"  PowerPoint: PASS")
    except Exception as e:
        ppt_ok = False
        print(f"  PowerPoint: FAIL ({e})")

    # Test HTML dashboard (skip actual generation)
    try:
        reporting.create_html_dashboard(
            test_tables,
            test_summary,
            output_file='/tmp/test_dashboard.html'
        )
        dash_ok = True
        print(f"  HTML Dashboard: PASS")
    except Exception as e:
        dash_ok = False
        print(f"  HTML Dashboard: FAIL ({e})")

    return ppt_ok and dash_ok


def run_all_tests() -> bool:
    """Run all debug tests."""
    print("=" * 60)
    print("🔧 Survey Debug - Testing Library Functions")
    print("=" * 60)

    results = {
        'data': test_data_operations(),
        'specification': test_specification_generation(),
        'analysis': test_analysis_operations(),
        'statistics': test_statistics_operations(),
        'reporting': test_reporting_operations()
    }

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed_count}/{total_count} passed")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name.title()}: {status}")

    return passed_count == total_count


def main():
    """CLI entry point for survey debug."""
    parser = argparse.ArgumentParser(
        description="Survey Analysis Debugging & Testing"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # test-all command
    all_parser = subparsers.add_parser('test-all', help='Run all library tests')

    # data command
    data_parser = subparsers.add_parser('data', help='Test data operations')

    # spec command
    spec_parser = subparsers.add_parser('spec', help='Test specification operations')

    # analysis command
    analysis_parser = subparsers.add_parser('analysis', help='Test analysis operations')

    # stats command
    stats_parser = subparsers.add_parser('stats', help='Test statistics operations')

    # reporting command
    report_parser = subparsers.add_parser('reporting', help='Test reporting operations')

    args = parser.parse_args()

    if args.command == 'test-all':
        success = run_all_tests()
        sys.exit(0 if success else 1)

    elif args.command == 'data':
        success = test_data_operations()
        sys.exit(0 if success else 1)

    elif args.command == 'spec':
        success = test_specification_generation()
        sys.exit(0 if success else 1)

    elif args.command == 'analysis':
        success = test_analysis_operations()
        sys.exit(0 if success else 1)

    elif args.command == 'stats':
        success = test_statistics_operations()
        sys.exit(0 if success else 1)

    elif args.command == 'reporting':
        success = test_reporting_operations()
        sys.exit(0 if success else 1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
