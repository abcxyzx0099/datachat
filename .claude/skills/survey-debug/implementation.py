"""
Survey Debug - Debugging & Testing Tool

Tests spss-analyzer CLI commands.
"""

import sys
import argparse
import subprocess


def test_all() -> bool:
    """Run all debug tests using spss-analyzer CLI."""
    print("=" * 60)
    print("🔧 Survey Debug - Testing spss-analyzer CLI")
    print("=" * 60)

    results = {}

    # Test data operations
    print("\n[Testing data operations...]")
    result = subprocess.run(
        ['spss-analyzer', 'data', '--help'],
        capture_output=True
    )
    results['Data'] = result.returncode == 0
    print(f"  {'✅ PASS' if results['Data'] else '❌ FAIL'}: spss-analyzer data")

    # Test specification
    print("[Testing specification...]")
    result = subprocess.run(
        ['spss-analyzer', 'spec', '--help'],
        capture_output=True
    )
    results['Specification'] = result.returncode == 0
    print(f"  {'✅ PASS' if results['Specification'] else '❌ FAIL'}: spss-analyzer spec")

    # Test analysis
    print("[Testing analysis...]")
    result = subprocess.run(
        ['spss-analyzer', 'analysis', '--help'],
        capture_output=True
    )
    results['Analysis'] = result.returncode == 0
    print(f"  {'✅ PASS' if results['Analysis'] else '❌ FAIL'}: spss-analyzer analysis")

    # Test statistics
    print("[Testing statistics...]")
    result = subprocess.run(
        ['spss-analyzer', 'stats', '--help'],
        capture_output=True
    )
    results['Statistics'] = result.returncode == 0
    print(f"  {'✅ PASS' if results['Statistics'] else '❌ FAIL'}: spss-analyzer stats")

    # Test reporting
    print("[Testing reporting...]")
    result = subprocess.run(
        ['spss-analyzer', 'reporting', '--help'],
        capture_output=True
    )
    results['Reporting'] = result.returncode == 0
    print(f"  {'✅ PASS' if results['Reporting'] else '❌ FAIL'}: spss-analyzer reporting")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} passed")
    print("=" * 60)

    for test_name, is_ok in results.items():
        status = "✅ PASS" if is_ok else "❌ FAIL"
        print(f"  {test_name}: {status}")

    return passed == total


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
        result = subprocess.run(['spss-analyzer', 'data', '--help'])
        sys.exit(result.returncode)

    elif args.command == 'spec':
        result = subprocess.run(['spss-analyzer', 'spec', '--help'])
        sys.exit(result.returncode)

    elif args.command == 'analysis':
        result = subprocess.run(['spss-analyzer', 'analysis', '--help'])
        sys.exit(result.returncode)

    elif args.command == 'stats':
        result = subprocess.run(['spss-analyzer', 'stats', '--help'])
        sys.exit(result.returncode)

    elif args.command == 'reporting':
        result = subprocess.run(['spss-analyzer', 'reporting', '--help'])
        sys.exit(result.returncode)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
