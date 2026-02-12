"""
Survey Debug - Debugging & Testing Tool

Tests spss-analyzer CLI library functions.
"""

import sys
import argparse


def _run_cli(args: list) -> int:
    """Run spss-analyzer CLI command."""
    import subprocess
    result = subprocess.run(['spss-analyzer'] + args,
                          capture_output=True, text=True)
    print(result.stdout)
    return result.returncode


def test_all() -> bool:
    """Run all debug tests using spss-analyzer CLI."""
    print("=" * 60)
    print("🔧 Survey Debug - Testing spss-analyzer CLI")
    print("=" * 60)

    # Test data operations
    print("\n[Testing data operations...]")
    result = _run_cli(['data', '--help'])
    data_ok = result == 0

    # Test specification
    print("[Testing specification...]")
    result = _run_cli(['spec', '--help'])
    spec_ok = result == 0

    # Test analysis
    print("[Testing analysis...]")
    result = _run_cli(['analysis', '--help'])
    analysis_ok = result == 0

    # Test statistics
    print("[Testing statistics...]")
    result = _run_cli(['stats', '--help'])
    stats_ok = result == 0

    # Test reporting
    print("[Testing reporting...]")
    result = _run_cli(['reporting', '--help'])
    reporting_ok = result == 0

    passed = all([data_ok, spec_ok, analysis_ok, stats_ok, reporting_ok])

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {sum(passed)}/{len(passed)} passed")
    print("=" * 60)

    for test_name, is_ok in [('Data', data_ok), ('Specification', spec_ok),
                            ('Analysis', analysis_ok), ('Statistics', stats_ok),
                            ('Reporting', reporting_ok)]:
        status = "✅ PASS" if is_ok else "❌ FAIL"
        print(f"  {test_name}: {status}")

    return passed


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
    report_parser = subparsers.add_parser('reporting', help='Test reporting operations')

    args = parser.parse_args()

    if args.command == 'test-all':
        success = test_all()
        sys.exit(0 if success else 1)

    elif args.command == 'data':
        result = _run_cli(['data', '--help'])
        sys.exit(result)

    elif args.command == 'spec':
        result = _run_cli(['spec', '--help'])
        sys.exit(result)

    elif args.command == 'analysis':
        result = _run_cli(['analysis', '--help'])
        sys.exit(result)

    elif args.command == 'stats':
        result = _run_cli(['stats', '--help'])
        sys.exit(result)

    elif args.command == 'reporting':
        result = _run_cli(['reporting', '--help'])
        sys.exit(result)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
