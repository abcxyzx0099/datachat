#!/usr/bin/env python3
"""
SPSS Survey Analysis - CLI

Single CLI script with subcommands for all survey analysis operations.
Provides semantic, module-based commands (no stage concepts).

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
import json
from pathlib import Path


def cmd_data_read(args):
    """Read SPSS .sav file and output metadata."""
    from survey_analyzer.io import SPSSReader, MetadataTransformer

    reader = SPSSReader(encoding=args.encoding or 'UTF-8')
    data, meta = reader.read(args.sav_file)

    transformer = MetadataTransformer()
    metadata_dict = transformer.to_variable_centered(meta)

    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(metadata_dict, f, indent=2)
        print(f"Saved metadata to: {args.output_file}")
    else:
        print(json.dumps(metadata_dict, indent=2))


def cmd_data_filter(args):
    """Filter metadata by category count."""
    from survey_analyzer.io import MetadataTransformer

    with open(args.metadata_file) as f:
        metadata = json.load(f)

    transformer = MetadataTransformer()
    filtered = transformer.filter_variables(
        metadata,
        min_categories=args.min_categories,
        max_categories=args.max_categories
    )

    output_file = args.output_file or args.metadata_file.replace('.json', '_filtered.json')
    with open(output_file, 'w') as f:
        json.dump(filtered, f, indent=2)
    print(f"Saved filtered metadata to: {output_file}")


def cmd_spec_tables(args):
    """Generate table specifications from metadata."""
    from survey_analyzer.specification import create_empty_spec

    # Create an empty specification template
    spec = create_empty_spec(source_file=args.metadata_file)
    spec_dict = spec.to_dict()

    output_file = args.output_file or 'table_specification.json'
    with open(output_file, 'w') as f:
        json.dump(spec_dict, f, indent=2)
    print(f"Saved specification template to: {output_file}")
    print("NOTE: This is a template. Use AI/skills to generate full specifications.")


def cmd_analysis_indicators(args):
    """Compute indicators from specification."""
    from survey_analyzer.analysis import IndicatorGenerator

    with open(args.spec_file) as f:
        spec = json.load(f)
    with open(args.metadata_file) as f:
        metadata = json.load(f)

    # Use IndicatorGenerator instead of IndicatorsCalculator
    gen = IndicatorGenerator()
    indicators = gen.generate(spec.get('indicators', []), metadata)

    if args.output_file:
        import csv
        with open(args.output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['indicator_id', 'value'])
            writer.writeheader()
            writer.writerows(indicators)
        print(f"Saved indicators to: {args.output_file}")
    else:
        print(json.dumps(indicators, indent=2))


def cmd_stats_test(args):
    """Calculate chi-square tests on crosstabs."""
    from survey_analyzer.analysis import StatisticsCalculator
    from survey_analyzer.filtering import SignificanceFilter

    with open(args.crosstabs_file) as f:
        crosstabs = json.load(f)

    calc = StatisticsCalculator()
    test_results = calc.calculate_chi_square(crosstabs)

    filter_obj = SignificanceFilter()
    filtered_tables, summary = filter_obj.filter_significant(test_results, threshold=args.threshold)

    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump({'tables': filtered_tables, 'summary': summary}, f, indent=2)
        print(f"Saved results to: {args.output_file}")
    else:
        print(json.dumps({'tables': filtered_tables, 'summary': summary}, indent=2))


def cmd_stats_filter(args):
    """Filter tables by significance."""
    from survey_analyzer.filtering import SignificanceFilter

    with open(args.crosstabs_file) as f:
        data = json.load(f)

    filter_obj = SignificanceFilter()
    filtered, summary = filter_obj.filter_significant(
        data,
        threshold=args.threshold
    )

    output_file = args.output_file or 'filtered_tables.json'
    with open(output_file, 'w') as f:
        json.dump({'tables': filtered, 'summary': summary}, f, indent=2)
    print(f"Saved filtered tables to: {output_file}")


def cmd_reporting_ppt(args):
    """Generate PowerPoint report."""
    from survey_analyzer.reporting import PowerPointGenerator

    with open(args.tables_file) as f:
        data = json.load(f)

    tables = data.get('tables', [])
    summary = data.get('summary', {})

    gen = PowerPointGenerator()
    output_path = Path(args.output_dir) / "presentation.pptx"
    gen.create_presentation(tables, summary, "Survey Analysis Results")
    gen.save(str(output_path))
    print(f"Saved PowerPoint to: {output_path}")


def cmd_reporting_html(args):
    """Generate HTML dashboard."""
    from survey_analyzer.reporting import HTMLDashboardGenerator

    with open(args.tables_file) as f:
        data = json.load(f)

    tables = data.get('tables', [])
    summary = data.get('summary', {})

    gen = HTMLDashboardGenerator()
    output_path = Path(args.output_dir) / "dashboard.html"
    gen.generate_dashboard(tables, summary, str(output_path))
    print(f"Saved HTML dashboard to: {output_path}")


def cmd_all_workflow(args):
    """Run complete 5-stage workflow."""
    from survey_analyzer.io import SPSSReader, MetadataTransformer
    from survey_analyzer.specification import create_empty_spec
    from survey_analyzer.analysis import IndicatorGenerator, StatisticsCalculator
    from survey_analyzer.filtering import SignificanceFilter
    from survey_analyzer.reporting import PowerPointGenerator, HTMLDashboardGenerator

    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    skip_stages = set((args.skip or '').split(','))

    # Stage 1: Data Preparation
    if '1' not in skip_stages:
        print("\n[Stage 1: Data Preparation]")
        reader = SPSSReader(encoding=args.encoding or 'UTF-8')
        data, meta = reader.read(args.sav_file)

        transformer = MetadataTransformer()
        metadata_dict = transformer.to_variable_centered(meta)
        filtered_metadata = transformer.filter_variables(metadata_dict)

        metadata_file = output_path / "filtered_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(filtered_metadata, f, indent=2)
        print(f"Saved: {metadata_file}")

    # Stage 2: Table Specification
    if '2' not in skip_stages:
        print("\n[Stage 2: Table Specification]")
        with open(metadata_file, 'r') as f:
            filtered_metadata = json.load(f)

        # Create empty spec template (use AI/skills to generate full spec)
        spec = create_empty_spec(source_file=args.sav_file)
        spec_dict = spec.to_dict()

        spec_file = output_path / "table_specification.json"
        with open(spec_file, 'w') as f:
            json.dump(spec_dict, f, indent=2)
        print(f"Saved: {spec_file}")
        print("NOTE: Use AI/skills to generate full table specifications")

    # Stage 3: Cross-Table Calculation
    if '3' not in skip_stages:
        print("\n[Stage 3: Cross-Table Calculation]")
        gen = IndicatorGenerator()
        # Mock indicators for now - needs actual spec
        indicators_file = output_path / "indicators.json"
        with open(indicators_file, 'w') as f:
            json.dump([], f, indent=2)
        print(f"Saved: {indicators_file}")
        print("NOTE: Use AI/skills to generate indicators from spec")

    # Stage 4: Statistical Analysis
    if '4' not in skip_stages:
        print("\n[Stage 4: Statistical Analysis]")
        stats_calc = StatisticsCalculator()
        # Mock crosstabs for now - needs actual data
        crosstabs_file = output_path / "cross_tables.json"
        with open(crosstabs_file, 'w') as f:
            json.dump([], f, indent=2)
        print(f"Saved: {crosstabs_file}")

    # Stage 5: Reporting
    if '5' not in skip_stages:
        print("\n[Stage 5: Reporting]")
        ppt_gen = PowerPointGenerator()
        ppt_file = output_path / "presentation.pptx"
        # Create empty presentation for now
        ppt_gen.create_presentation([], {}, "Survey Analysis Results")
        ppt_gen.save(str(ppt_file))
        print(f"Saved: {ppt_file}")

        dash_gen = HTMLDashboardGenerator()
        dash_file = output_path / "dashboard.html"
        # Create empty dashboard for now
        html_content = dash_gen.generate_dashboard({"tables": []}, {"tables": []}, None)
        dash_gen.save(str(dash_file), html_content)
        print(f"Saved: {dash_file}")

    print("\n[Workflow Complete]")
    print(f"Results saved to: {args.output_dir}")


def main():
    """Main CLI entry point with subcommands."""
    parser = argparse.ArgumentParser(
        description="SPSS Survey Analysis - Semantic CLI Commands",
        epilog="""Examples:
  spss-analyzer data read --sav-file survey.sav
  spss-analyzer data filter --metadata-file metadata.json
  spss-analyzer spec tables --metadata-file metadata.json
  spss-analyzer analysis indicators --spec-file spec.json
  spss-analyzer stats test --crosstabs-file cross_tables.json
  spss-analyzer reporting ppt --tables-file filtered_tables.json
  spss-analyzer reporting html --tables-file filtered_tables.json
  spss-analyzer all --sav-file survey.sav --output-dir output/"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Data command
    data_parser = subparsers.add_parser('data', help='Data operations (read, filter)')
    data_subparsers = data_parser.add_subparsers(dest='subcommand')

    data_read = data_subparsers.add_parser('read', help='Read SPSS file and extract metadata')
    data_read.add_argument('--sav-file', required=True, help='Path to SPSS .sav file')
    data_read.add_argument('--encoding', help='File encoding (default: UTF-8, try ISO-8859-1 for older files)')
    data_read.add_argument('--output-file', help='Output metadata JSON file')

    data_filter = data_subparsers.add_parser('filter', help='Filter metadata by category count')
    data_filter.add_argument('--metadata-file', required=True, help='Path to metadata JSON')
    data_filter.add_argument('--output-file', help='Output filtered metadata')
    data_filter.add_argument('--min-categories', type=int, default=2, help='Min categories')
    data_filter.add_argument('--max-categories', type=int, default=10, help='Max categories')

    # Spec command
    spec_parser = subparsers.add_parser('spec', help='Specification operations')
    spec_subparsers = spec_parser.add_subparsers(dest='subcommand')

    spec_tables = spec_subparsers.add_parser('tables', help='Generate table specifications')
    spec_tables.add_argument('--metadata-file', required=True, help='Path to metadata JSON')
    spec_tables.add_argument('--output-file', help='Output specification JSON')
    spec_tables.add_argument('--count', type=int, default=20, help='Number of tables')

    # Analysis command
    analysis_parser = subparsers.add_parser('analysis', help='Analysis operations')
    analysis_subparsers = analysis_parser.add_subparsers(dest='subcommand')

    analysis_indicators = analysis_subparsers.add_parser('indicators', help='Compute indicators')
    analysis_indicators.add_argument('--spec-file', required=True, help='Path to specification JSON')
    analysis_indicators.add_argument('--metadata-file', required=True, help='Path to metadata JSON')
    analysis_indicators.add_argument('--output-file', help='Output indicators CSV')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Statistical analysis')
    stats_subparsers = stats_parser.add_subparsers(dest='subcommand')

    stats_test = stats_subparsers.add_parser('test', help='Calculate chi-square tests')
    stats_test.add_argument('--crosstabs-file', required=True, help='Path to crosstabs JSON')
    stats_test.add_argument('--threshold', type=float, default=0.05, help='Significance threshold')
    stats_test.add_argument('--output-file', help='Output filtered tables JSON')

    stats_filter = stats_subparsers.add_parser('filter', help='Filter by significance')
    stats_filter.add_argument('--crosstabs-file', required=True, help='Path to crosstabs JSON')
    stats_filter.add_argument('--threshold', type=float, default=0.05, help='Significance threshold')
    stats_filter.add_argument('--output-file', help='Output filtered tables JSON')

    # Reporting command
    reporting_parser = subparsers.add_parser('reporting', help='Report generation')
    reporting_subparsers = reporting_parser.add_subparsers(dest='subcommand')

    reporting_ppt = reporting_subparsers.add_parser('ppt', help='Generate PowerPoint')
    reporting_ppt.add_argument('--tables-file', required=True, help='Path to filtered tables JSON')
    reporting_ppt.add_argument('--output-dir', default='output', help='Output directory')

    reporting_html = reporting_subparsers.add_parser('html', help='Generate HTML dashboard')
    reporting_html.add_argument('--tables-file', required=True, help='Path to filtered tables JSON')
    reporting_html.add_argument('--output-dir', default='output', help='Output directory')

    # All workflow command
    all_parser = subparsers.add_parser('all', help='Run complete 5-stage workflow')
    all_parser.add_argument('--sav-file', required=True, help='Path to SPSS .sav file')
    all_parser.add_argument('--encoding', help='File encoding (default: UTF-8, try ISO-8859-1 for older files)')
    all_parser.add_argument('--output-dir', default='output', help='Output directory')
    all_parser.add_argument('--skip', help='Skip stages (e.g., "3,4")')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to appropriate function
    if args.command == 'data':
        if args.subcommand == 'read':
            cmd_data_read(args)
        elif args.subcommand == 'filter':
            cmd_data_filter(args)
        else:
            data_subparsers.choices['read'].print_help()
    elif args.command == 'spec':
        if args.subcommand == 'tables':
            cmd_spec_tables(args)
        else:
            spec_subparsers.choices['tables'].print_help()
    elif args.command == 'analysis':
        if args.subcommand == 'indicators':
            cmd_analysis_indicators(args)
        else:
            analysis_subparsers.choices['indicators'].print_help()
    elif args.command == 'stats':
        if args.subcommand == 'test':
            cmd_stats_test(args)
        elif args.subcommand == 'filter':
            cmd_stats_filter(args)
        else:
            stats_subparsers.choices['test'].print_help()
    elif args.command == 'reporting':
        if args.subcommand == 'ppt':
            cmd_reporting_ppt(args)
        elif args.subcommand == 'html':
            cmd_reporting_html(args)
        else:
            reporting_subparsers.choices['ppt'].print_help()
    elif args.command == 'all':
        cmd_all_workflow(args)


if __name__ == '__main__':
    main()
