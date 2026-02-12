"""
Main entry point for spss_analyzer CLI.

Provides convenient command-line interface to all semantic operations.
Usage: python -m spss_analyzer <command> [options]
"""

import sys
from spss_analyzer.cli import (
    data,
    specification,
    analysis,
    statistics,
    reporting,
    all as workflow
)


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("SPSS Survey Analysis - Semantic CLI Commands")
        print("=" * 50)
        print("\nAvailable modules:")
        print("  data        - Read and filter survey data")
        print("  spec        - Generate table specifications")
        print("  analysis     - Compute indicators and crosstabs")
        print("  statistics   - Calculate chi-square tests")
        print("  reporting    - Generate PowerPoint and HTML")
        print("  all         - Run complete workflow")
        print("\nUsage:")
        print("  python -m spss_analyzer data read --sav-file data.sav")
        print("  python -m spss_analyzer spec tables --metadata-file filtered_metadata.json")
        print("  python -m spss_analyzer analysis indicators --spec-file table_specification.json")
        print("  python -m spss_analyzer stats test --crosstabs-file cross_tables.json")
        print("  python -m spss_analyzer reporting both --tables-file filtered_tables.json")
        print("  python -m spss_analyzer all --sav-file data.sav")
        print("\nFor module-specific help:")
        print("  python -m spss_analyzer.cli.data --help")
        print("  python -m spss_analyzer.cli.specification --help")
        sys.exit(0)

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    # Route to appropriate module
    if command in ['data', 'metadata']:
        sys.argv[0] = 'spss_analyzer.cli.data'
        data.main()

    elif command in ['spec', 'specification', 'tables', 'indicators']:
        sys.argv[0] = 'spss_analyzer.cli.specification'
        specification.main()

    elif command in ['analysis', 'analyze', 'indicators', 'crosstabs']:
        sys.argv[0] = 'spss_analyzer.cli.analysis'
        analysis.main()

    elif command in ['stats', 'statistics', 'chi']:
        sys.argv[0] = 'spss_analyzer.cli.statistics'
        statistics.main()

    elif command in ['report', 'reporting', 'ppt', 'dashboard']:
        sys.argv[0] = 'spss_analyzer.cli.reporting'
        reporting.main()

    elif command in ['all', 'workflow', 'run']:
        sys.argv[0] = 'spss_analyzer.cli.all'
        workflow.main()

    else:
        print(f"Unknown command: {command}")
        print("Run: python -m spss_analyzer --help")
        sys.exit(1)


if __name__ == "__main__":
    main()
