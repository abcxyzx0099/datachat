#!/usr/bin/env python3
"""
SPSS Survey Analysis - CLI

Single CLI script with subcommands for all survey analysis operations.
Replaces the multiple CLI scripts in cli/ directory.

Usage: spss-analyzer <command> [options]

Commands:
    data      - Read and filter survey data
    spec      - Generate table specifications
    analysis   - Compute indicators and crosstabs
    stats      - Calculate chi-square tests
    reporting  - Generate PowerPoint and HTML
    all        - Run complete 5-stage workflow
"""

import sys
import argparse
from spss_analyzer.cli import (
    data,
    specification,
    analysis,
    statistics,
    reporting,
    all as workflow,
)


def main():
    """Main CLI entry point with subcommands."""
    parser = argparse.ArgumentParser(
        description="SPSS Survey Analysis - Semantic CLI Commands",
        epilog="Examples:\n"
              "  spss-analyzer data read --sav-file survey.sav\n"
              "  spss-analyzer spec tables --metadata-file metadata.json\n"
              "  spss-analyzer analysis indicators --spec-file spec.json\n"
              "  spss-analyzer stats test --crosstabs-file cross_tables.json\n"
              "  spss-analyzer reporting both --tables-file filtered_tables.json\n"
              "  spss-analyzer all --sav-file survey.sav --output-dir output/"
    )

    # Create subparsers for each command
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Data operations
    data_parser = subparsers.add_parser(
        'data',
        help='Data operations (read, filter, transform)'
    )
    data_parser.add_argument('--sav-file', help='Path to SPSS .sav file')
    data_parser.add_argument('--metadata-file', help='Path to metadata JSON')
    data_parser.add_argument('--output-file', help='Output filtered metadata')
    data_parser.add_argument('--min-categories', type=int, default=2, help='Min categories')
    data_parser.add_argument('--max-categories', type=int, default=10, help='Max categories')

    # Specification operations
    spec_parser = subparsers.add_parser(
        'spec',
        help='Table specification operations'
    )
    spec_parser.add_argument('--metadata-file', required=True, help='Path to metadata JSON')
    spec_parser.add_argument('--output-file', help='Output specification JSON')
    spec_parser.add_argument('--count', type=int, default=20, help='Number of tables')
    spec_parser.add_argument('--indicators', action='store_true', help='Generate indicators too')

    # Analysis operations
    analysis_parser = subparsers.add_parser(
        'analysis',
        help='Analysis operations (indicators, crosstabs)'
    )
    analysis_parser.add_argument('--data-file', help='Path to data JSON')
    analysis_parser.add_argument('--spec-file', help='Path to specification JSON')
    analysis_parser.add_argument('--metadata-file', help='Path to metadata JSON')
    analysis_parser.add_argument('--output-file', help='Output indicators CSV')
    analysis_parser.add_argument('--crosstabs-file', help='Output crosstabs JSON')

    # Statistics operations
    stats_parser = subparsers.add_parser(
        'stats',
        help='Statistical analysis (chi-square, filtering)'
    )
    stats_parser.add_argument('--crosstabs-file', required=True, help='Path to crosstabs JSON')
    stats_parser.add_argument('--threshold', type=float, default=0.05, help='Significance threshold')
    stats_parser.add_argument('--output-file', help='Output filtered tables JSON')

    # Reporting operations
    reporting_parser = subparsers.add_parser(
        'reporting',
        help='Report generation (PowerPoint, HTML)'
    )
    reporting_parser.add_argument('--tables-file', help='Path to filtered tables JSON')
    reporting_parser.add_argument('--summary-file', help='Path to statistics summary JSON')
    reporting_parser.add_argument('--output-dir', default='output', help='Output directory')
    reporting_parser.add_argument('--ppt', action='store_true', help='Generate PowerPoint')
    reporting_parser.add_argument('--html', action='store_true', help='Generate HTML dashboard')

    # Workflow operations
    workflow_parser = subparsers.add_parser(
        'all',
        help='Run complete 5-stage workflow'
    )
    workflow_parser.add_argument('--sav-file', required=True, help='Path to SPSS .sav file')
    workflow_parser.add_argument('--output-dir', default='output', help='Output directory')
    workflow_parser.add_argument('--skip', help='Skip stages (e.g., "3,4")')

    # Parse arguments
    args = parser.parse_args()

    # Route to appropriate module
    if args.command == 'data':
        from spss_analyzer.cli import data
        data.main()
    elif args.command == 'spec':
        from spss_analyzer.cli import specification
        specification.main()
    elif args.command == 'analysis':
        from spss_analyzer.cli import analysis
        analysis.main()
    elif args.command == 'stats':
        from spss_analyzer.cli import statistics
        statistics.main()
    elif args.command == 'reporting':
        from spss_analyzer.cli import reporting
        reporting.main()
    elif args.command == 'all':
        from spss_analyzer.cli import all
        workflow.main()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
