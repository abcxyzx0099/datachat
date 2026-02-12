"""
Survey Debug - Debugging & Testing Tool

Tests spss-analyzer library modules directly.
"""

import sys
import argparse


def test_all() -> bool:
    """Run all debug tests by importing library modules."""
    print("=" * 60)
    print("🔧 Survey Debug - Testing spss-analyzer Library")
    print("=" * 60)

    results = {}

    # Test data operations
    print("\n[Testing data operations...]")
    try:
        from spss_analyzer.io import SPSSReader, MetadataTransformer
        results['Data'] = True
        print("  ✅ PASS: spss_analyzer.io")
    except Exception as e:
        results['Data'] = False
        print(f"  ❌ FAIL: spss_analyzer.io - {e}")

    # Test specification
    print("[Testing specification...]")
    try:
        from spss_analyzer.specification import TableSpecificationGenerator
        results['Specification'] = True
        print("  ✅ PASS: spss_analyzer.specification")
    except Exception as e:
        results['Specification'] = False
        print(f"  ❌ FAIL: spss_analyzer.specification - {e}")

    # Test analysis
    print("[Testing analysis...]")
    try:
        from spss_analyzer.analysis import IndicatorsCalculator, StatisticsCalculator
        results['Analysis'] = True
        print("  ✅ PASS: spss_analyzer.analysis")
    except Exception as e:
        results['Analysis'] = False
        print(f"  ❌ FAIL: spss_analyzer.analysis - {e}")

    # Test filtering
    print("[Testing filtering...]")
    try:
        from spss_analyzer.filtering import SignificanceFilter
        results['Filtering'] = True
        print("  ✅ PASS: spss_analyzer.filtering")
    except Exception as e:
        results['Filtering'] = False
        print(f"  ❌ FAIL: spss_analyzer.filtering - {e}")

    # Test reporting
    print("[Testing reporting...]")
    try:
        from spss_analyzer.reporting import PowerPointGenerator, HTMLDashboardGenerator
        results['Reporting'] = True
        print("  ✅ PASS: spss_analyzer.reporting")
    except Exception as e:
        results['Reporting'] = False
        print(f"  ❌ FAIL: spss_analyzer.reporting - {e}")

    # Test PSPP
    print("[Testing PSPP...]")
    try:
        from spss_analyzer.pspp import CTablesSyntaxGenerator
        results['PSPP'] = True
        print("  ✅ PASS: spss_analyzer.pspp")
    except Exception as e:
        results['PSPP'] = False
        print(f"  ❌ FAIL: spss_analyzer.pspp - {e}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} passed")
    print("=" * 60)

    for test_name, is_ok in results.items():
        status = "✅ PASS" if is_ok else "❌ FAIL"
        print(f"  {test_name}: {status}")

    return passed == total


def test_module(module_name: str) -> bool:
    """Test a specific module by importing it."""
    print(f"\n[Testing {module_name} module...]")

    module_map = {
        'data': ('spss_analyzer.io', ['SPSSReader', 'MetadataTransformer']),
        'spec': ('spss_analyzer.specification', ['TableSpecificationGenerator']),
        'analysis': ('spss_analyzer.analysis', ['IndicatorsCalculator', 'StatisticsCalculator']),
        'stats': ('spss_analyzer.analysis', ['StatisticsCalculator']),
        'filtering': ('spss_analyzer.filtering', ['SignificanceFilter']),
        'reporting': ('spss_analyzer.reporting', ['PowerPointGenerator', 'HTMLDashboardGenerator']),
        'pspp': ('spss_analyzer.pspp', ['CTablesSyntaxGenerator']),
    }

    if module_name not in module_map:
        print(f"  ❌ Unknown module: {module_name}")
        return False

    module_path, classes = module_map[module_name]

    try:
        module = __import__(module_path, fromlist=classes)
        for cls in classes:
            getattr(module, cls)
        print(f"  ✅ PASS: {module_path}")
        return True
    except Exception as e:
        print(f"  ❌ FAIL: {module_path} - {e}")
        return False


def main():
    """CLI entry point for survey debug."""
    parser = argparse.ArgumentParser(
        description="Survey Analysis Debugging & Testing"
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # test-all command
    all_parser = subparsers.add_parser('test-all', help='Run all tests')

    # Module-specific tests
    data_parser = subparsers.add_parser('data', help='Test data operations')
    spec_parser = subparsers.add_parser('spec', help='Test specification operations')
    analysis_parser = subparsers.add_parser('analysis', help='Test analysis operations')
    stats_parser = subparsers.add_parser('stats', help='Test statistics operations')
    filtering_parser = subparsers.add_parser('filtering', help='Test filtering operations')
    reporting_parser = subparsers.add_parser('reporting', help='Test reporting operations')
    pspp_parser = subparsers.add_parser('pspp', help='Test PSPP operations')

    args = parser.parse_args()

    if args.command == 'test-all':
        success = test_all()
        sys.exit(0 if success else 1)
    elif args.command == 'data':
        success = test_module('data')
        sys.exit(0 if success else 1)
    elif args.command == 'spec':
        success = test_module('spec')
        sys.exit(0 if success else 1)
    elif args.command == 'analysis':
        success = test_module('analysis')
        sys.exit(0 if success else 1)
    elif args.command == 'stats':
        success = test_module('stats')
        sys.exit(0 if success else 1)
    elif args.command == 'filtering':
        success = test_module('filtering')
        sys.exit(0 if success else 1)
    elif args.command == 'reporting':
        success = test_module('reporting')
        sys.exit(0 if success else 1)
    elif args.command == 'pspp':
        success = test_module('pspp')
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
