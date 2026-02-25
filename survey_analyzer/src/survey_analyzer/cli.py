#!/usr/bin/env python3
"""
SPSS Survey Analysis - CLI

Single CLI script with subcommands for all survey analysis operations.
Uses unified table_specification.jsonc as single source of truth.

Usage: python -m survey_analyzer <command> [options]

Commands:
    data        - Read and filter survey data (Stage 1)
    questions   - Extract question codes (Stage 2)
    indicators  - Generate indicators using LLM (Stage 3)
    tablespec   - Classify indicators as row/column (Stage 4)
    analysis    - Compute crosstabs (Stage 5)
    stats       - Calculate chi-square tests (Stage 6)
    reporting   - Generate PowerPoint and HTML (Stage 7)

Examples:
  python -m survey_analyzer data prep --sav-file survey.sav
  python -m survey_analyzer questions extract --metadata-file output/filtered_metadata.json
  python -m survey_analyzer indicators batch --spec-file output/table_specification.jsonc
  python -m survey_analyzer tablespec build --spec-file output/table_specification.jsonc
"""

import sys
import argparse
import json
from pathlib import Path

from survey_analyzer.constants import DEFAULT_MAX_CATEGORIES


def load_jsonc(file_path: str) -> dict:
    """Load JSONC file (JSON with comments)."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Strip JSONC comments
    lines = [line for line in content.split("\n") if not line.strip().startswith("//")]
    content = "\n".join(lines)
    return json.loads(content)


# ============================================================================
# Stage 1: Data Preparation
# ============================================================================

def cmd_data_read(args):
    """Read SPSS .sav file and output metadata."""
    from survey_analyzer.io import SPSSReader, MetadataTransformer

    reader = SPSSReader(encoding=args.encoding)
    data, meta = reader.read(args.sav_file)

    transformer = MetadataTransformer()
    metadata_dict = transformer.to_variable_centered(meta)

    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
        print(f"Saved metadata to: {args.output_file}")
    else:
        print(json.dumps(metadata_dict, indent=2, ensure_ascii=False))


def cmd_data_filter(args):
    """Filter metadata by category count."""
    from survey_analyzer.io import MetadataTransformer

    with open(args.metadata_file) as f:
        metadata = json.load(f)

    transformer = MetadataTransformer()
    filtered = transformer.filter_variables(
        metadata,
        max_categories=args.max_categories
    )

    output_file = args.output_file or args.metadata_file.replace('.json', '_filtered.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)
    print(f"Saved filtered metadata to: {output_file}")


def cmd_data_prep(args):
    """Read SPSS file and filter metadata in one command (Stage 1)."""
    from survey_analyzer.io import SPSSReader, MetadataTransformer
    import subprocess

    print(f"\n[Stage 1: Data Preparation]")
    print(f"  Reading: {args.sav_file}")

    # Backup existing file if needed
    output_file = args.output_file or 'output/filtered_metadata.json'
    output_path = Path(output_file)

    if output_path.exists():
        timestamp = subprocess.check_output(['date', '+%Y%m%d_%H%M%S']).decode().strip()
        backup_path = output_path.parent / f"{output_path.stem}_{timestamp}{output_path.suffix}"
        subprocess.run(['cp', str(output_path), str(backup_path)], stderr=subprocess.DEVNULL)
        print(f"  ✓ Backed up existing file")

    # Read SPSS file
    reader = SPSSReader(encoding=args.encoding)
    data, meta = reader.read(args.sav_file)
    var_count = len(meta.get('variable_labels', {}))
    print(f"  Loaded: {len(data)} rows, {var_count} variables")

    # Transform and filter
    transformer = MetadataTransformer()
    metadata_dict = transformer.to_variable_centered(meta)
    filtered_metadata = transformer.filter_variables(
        metadata_dict,
        max_categories=args.max_categories
    )
    print(f"  Filtered: {len(filtered_metadata)} variables")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_metadata, f, indent=2, ensure_ascii=False)

    print(f"\n  ✓ Saved: {output_path}")
    print(f"  ✓ Ready for Stage 2: Question Extraction\n")


# ============================================================================
# Stage 2: Question Extraction
# ============================================================================

def cmd_questions_extract(args):
    """Extract question codes and group variables by question (Stage 2)."""
    from survey_analyzer.questions import QuestionExtractor

    print("\n[Stage 2: Question Extraction]")
    print(f"  Reading: {args.metadata_file}")

    extractor = QuestionExtractor()
    spec = extractor.extract_from_file(
        args.metadata_file,
        args.output_file
    )

    # Optional backup
    if args.backup_file:
        questions = spec.get("questions", [])
        extractor.save_questions(questions, args.backup_file)
        print(f"  ✓ Backup saved: {args.backup_file}")

    print(f"  ✓ Extracted: {len(spec.get('questions', []))} questions")
    print(f"  ✓ Saved: {args.output_file}")
    print(f"  ✓ Ready for Stage 3: Indicator Generation\n")


# ============================================================================
# Stage 3: Indicator Generation
# ============================================================================

def cmd_indicators_batch(args):
    """Batch generate indicators using LLM (Stage 3)."""
    from survey_analyzer.indicators import BatchProcessor

    print("\n[Stage 3: Indicator Generation]")
    print(f"  Spec file: {args.spec_file}")
    print(f"  Metadata: {args.metadata_file}")

    # Parse question codes if provided
    question_codes = None
    if hasattr(args, 'questions') and args.questions:
        question_codes = [q.strip() for q in args.questions.split(",")]
        print(f"  Question codes: {', '.join(question_codes)}")

    # Progress callback
    def progress_callback(current: int, total: int, question_code: str) -> None:
        print(f"  [{current}/{total}] {question_code}")

    # Process
    processor = BatchProcessor(continue_on_error=not args.stop_on_error)
    spec = processor.process_all(
        spec_file=args.spec_file,
        metadata_file=args.metadata_file,
        question_codes=question_codes,
        resume=not args.no_resume,
        progress_callback=progress_callback
    )

    # Count indicators
    total_indicators = sum(
        len(q.get("indicators", []))
        for q in spec.get("questions", [])
    )

    # Optional backup
    if args.backup_file:
        from datetime import datetime
        all_indicators = []
        for q in spec.get("questions", []):
            for ind in q.get("indicators", []):
                all_indicators.append({**ind, "question_code": q["question_code"]})

        backup_data = {
            "metadata": {
                "source_spec": str(Path(args.spec_file).absolute()),
                "generated_at": datetime.now().isoformat(),
                "total_indicators": len(all_indicators)
            },
            "indicators": all_indicators
        }

        backup_path = Path(args.backup_file)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Backup saved: {args.backup_file}")

    print(f"\n  ✓ Generated: {total_indicators} indicators")
    print(f"  ✓ Updated: {args.spec_file}")
    print(f"  ✓ Ready for Stage 4: Classification\n")


# ============================================================================
# Stage 4: Table Specification (Classification)
# ============================================================================

def cmd_tablespec_template(args):
    """Show Excel template info (optional guidance)."""
    print("\n[Table Specification - Excel Template]")
    print("\nThe Excel template is OPTIONAL - for providing domain knowledge.")
    print("When filled out, it helps guide the LLM in classifying indicators.")
    print("\nTemplate location:")
    print("  .claude/skills/analyzer-tablespec-template/templates/table-specification-template.xlsx")
    print("\nFor detailed guidance, see: /skill analyzer-tablespec-template\n")


def cmd_tablespec_build(args):
    """Classify indicators as row/column using LLM (Stage 4)."""
    from survey_analyzer.tablespec import TableSpec

    print("\n[Stage 4: Table Specification - Classification]")
    print(f"  Spec file: {args.spec_file}")

    spec_builder = TableSpec()
    spec = spec_builder.classify_from_file(
        spec_file=args.spec_file,
        output_file=args.output_file or args.spec_file
    )

    # Count row/column indicators
    row_count = sum(
        1 for q in spec.get("questions", [])
        for ind in q.get("indicators", [])
        if ind.get("is_row")
    )
    col_count = sum(
        1 for q in spec.get("questions", [])
        for ind in q.get("indicators", [])
        if ind.get("is_column")
    )

    print(f"\n  ✓ Row indicators: {row_count}")
    print(f"  ✓ Column indicators: {col_count}")
    print(f"  ✓ Saved: {args.output_file or args.spec_file}")
    print(f"  ✓ Ready for Stage 5: Cross-Table Generation\n")


# ============================================================================
# Stage 5: Analysis (Crosstabs)
# ============================================================================

def cmd_analysis_indicators(args):
    """Compute crosstabs from specification (Stage 5)."""
    from survey_analyzer.analysis import generate_crosstabs_batch
    from survey_analyzer.io import SPSSReader
    import pandas as pd

    # Load spec file (JSONC)
    spec = load_jsonc(args.spec_file)

    # Load SPSS data
    reader = SPSSReader()
    df, meta = reader.read(args.sav_file)

    # Extract row and column indicators from spec
    row_indicators = []
    col_indicators = []

    for question in spec.get("questions", []):
        for indicator in question.get("indicators", []):
            # Only include classified indicators
            if indicator.get("is_row") or indicator.get("is_column"):
                # Use base_variables directly (from LLM Stage 3)
                base_vars = indicator.get("base_variables", {})
                # Convert base_variables dict to list format expected by crosstab processor
                # Expected: [{"name": "var1", "label": "Label 1"}, ...]
                base_vars_list = []
                if isinstance(base_vars, dict):
                    for var_name, label in base_vars.items():
                        base_vars_list.append({"name": var_name, "label": label})
                else:
                    base_vars_list = base_vars

                variables = [bv["name"] for bv in base_vars_list]

                ind_data = {
                    "indicator_code": indicator["indicator_code"],
                    "indicator_label": indicator["indicator_label"],
                    "question_code": question["question_code"],
                    "variables": variables,
                    "base_variables": base_vars_list,
                    "value_labels": indicator.get("base_variables_value_labels", {}),
                    "transformation": indicator.get("base_variables_transformations"),
                }

                if indicator.get("is_row"):
                    row_indicators.append(ind_data)
                if indicator.get("is_column"):
                    col_indicators.append(ind_data)

    # Check if we have both row and column indicators
    if not row_indicators:
        print("Error: No row indicators found in spec. Run Stage 4 (tablespec build) first.")
        sys.exit(1)
    if not col_indicators:
        print("Error: No column indicators found in spec. Run Stage 4 (tablespec build) first.")
        sys.exit(1)

    # Get weight variable if specified
    weight_var = spec.get("weight_indicator")
    if weight_var:
        weight_var = weight_var.get("indicator_variables", [None])[0]

    # Generate crosstabs
    print(f"[Stage 5: Cross-Table Generation]")
    print(f"  Data file: {args.sav_file}")
    print(f"  Row indicators: {len(row_indicators)}")
    print(f"  Column indicators: {len(col_indicators)}")
    print(f"  Total combinations: {len(row_indicators) * len(col_indicators)}")

    results = generate_crosstabs_batch(df, row_indicators, col_indicators, weight_var)

    # Convert numpy/pandas types to regular Python types for JSON serialization
    def convert_to_json_serializable(obj):
        """Convert numpy/pandas types to regular Python types."""
        import numpy as np
        if isinstance(obj, dict):
            return {k: convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif pd.isna(obj):
            return None
        else:
            return obj

    results = convert_to_json_serializable(results)

    # Save results
    if args.output_file:
        output_data = {
            "tables": results,
            "summary": {
                "total_tables": len(results),
                "row_indicators": len(row_indicators),
                "column_indicators": len(col_indicators),
                "generated_at": pd.Timestamp.now().isoformat()
            }
        }
        with open(args.output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Saved: {args.output_file}")
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))

    print(f"  ✓ Generated: {len(results)} cross-tables")
    print(f"  ✓ Ready for Stage 6: Statistical Filtering\n")


# ============================================================================
# Stage 6: Statistics
# ============================================================================

def cmd_stats_test(args):
    """Calculate chi-square tests (Stage 6)."""
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
    """Filter tables by significance (Stage 6)."""
    from survey_analyzer.filtering import SignificanceFilter, FilterCriteria

    with open(args.crosstabs_file) as f:
        data = json.load(f)

    tables = data.get('tables', [])

    # Create filter criteria with custom threshold
    criteria = FilterCriteria()
    criteria.significance_level = args.threshold
    criteria.min_cramers_v = 0.1

    filter_obj = SignificanceFilter(criteria=criteria)

    # Apply filter
    filter_result = filter_obj.filter_tables(tables)

    # Get included tables (table IDs)
    included_ids = filter_result.included_tables

    # Filter the actual table data
    filtered_tables = [
        table for table in tables
        if table.get('table_id') in included_ids
    ]

    # Get summary from filter_result
    summary_dict = filter_result.summary.to_dict()

    output_file = args.output_file or 'filtered_tables.json'
    with open(output_file, 'w') as f:
        json.dump({'tables': filtered_tables, 'summary': summary_dict}, f, indent=2)
    print(f"Saved filtered tables to: {output_file}")
    print(f"  Total: {summary_dict.get('total_tables', len(tables))}")
    print(f"  Significant: {summary_dict.get('included_count', len(filtered_tables))}")
    print(f"  Excluded: {summary_dict.get('excluded_count', len(tables) - len(filtered_tables))}")


# ============================================================================
# Stage 7: Reporting
# ============================================================================

def cmd_reporting_ppt(args):
    """Generate PowerPoint report (Stage 7)."""
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
    """Generate HTML dashboard (Stage 7)."""
    from survey_analyzer.reporting import HTMLDashboardGenerator

    with open(args.tables_file) as f:
        data = json.load(f)

    tables = data.get('tables', [])
    summary = data.get('summary', {})

    gen = HTMLDashboardGenerator()
    output_path = Path(args.output_dir) / "dashboard.html"
    gen.generate_dashboard(tables, summary, str(output_path))
    print(f"Saved HTML dashboard to: {output_path}")


# ============================================================================
# Main CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SPSS Survey Analysis - 7-Stage Unified Workflow",
        epilog="""Examples:
  # Stage 1: Prepare data
  python -m survey_analyzer data prep --sav-file survey.sav

  # Stage 2: Extract questions
  python -m survey_analyzer questions extract --metadata-file output/filtered_metadata.json

  # Stage 3: Generate indicators
  python -m survey_analyzer indicators batch --spec-file output/table_specification.jsonc --metadata-file output/filtered_metadata.json

  # Stage 4: Classify indicators
  python -m survey_analyzer tablespec build --spec-file output/table_specification.jsonc

  # Stage 5-7: Analysis, statistics, reporting
  python -m survey_analyzer analysis indicators --spec-file output/table_specification.jsonc --metadata-file output/filtered_metadata.json
  python -m survey_analyzer stats test --crosstabs-file output/cross_tables.json
  python -m survey_analyzer reporting ppt --tables-file output/filtered_tables.json
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Data command (Stage 1)
    data_parser = subparsers.add_parser('data', help='Data operations (Stage 1)')
    data_subparsers = data_parser.add_subparsers(dest='subcommand')

    data_read = data_subparsers.add_parser('read', help='Read SPSS file')
    data_read.add_argument('--sav-file', required=True)
    data_read.add_argument('--encoding')
    data_read.add_argument('--output-file')

    data_filter = data_subparsers.add_parser('filter', help='Filter metadata')
    data_filter.add_argument('--metadata-file', required=True)
    data_filter.add_argument('--output-file')
    data_filter.add_argument('--max-categories', type=int, default=DEFAULT_MAX_CATEGORIES)

    data_prep = data_subparsers.add_parser('prep', help='Read and filter (Stage 1)')
    data_prep.add_argument('--sav-file', required=True)
    data_prep.add_argument('--encoding')
    data_prep.add_argument('--output-file', default='output/filtered_metadata.json')
    data_prep.add_argument('--max-categories', type=int, default=DEFAULT_MAX_CATEGORIES)

    # Questions command (Stage 2)
    questions_parser = subparsers.add_parser('questions', help='Question extraction (Stage 2)')
    questions_subparsers = questions_parser.add_subparsers(dest='subcommand')

    questions_extract = questions_subparsers.add_parser('extract', help='Extract questions (Stage 2)')
    questions_extract.add_argument('--metadata-file', required=True)
    questions_extract.add_argument('--output-file', default='output/table_specification.jsonc')
    questions_extract.add_argument('--backup-file', help='Optional: Save questions.json backup')

    # Indicators command (Stage 3)
    indicators_parser = subparsers.add_parser('indicators', help='Indicator generation (Stage 3)')
    indicators_subparsers = indicators_parser.add_subparsers(dest='subcommand')

    indicators_batch = indicators_subparsers.add_parser('batch', help='Generate indicators (Stage 3)')
    indicators_batch.add_argument('--spec-file', default='output/table_specification.jsonc')
    indicators_batch.add_argument('--metadata-file', required=True)
    indicators_batch.add_argument('--questions', help='Specific question codes (comma-separated)')
    indicators_batch.add_argument('--no-resume', action='store_true')
    indicators_batch.add_argument('--stop-on-error', action='store_true')
    indicators_batch.add_argument('--backup-file', help='Optional: Save indicators.json backup')

    # Tablespec command (Stage 4)
    tablespec_parser = subparsers.add_parser('tablespec', help='Table specification (Stage 4)')
    tablespec_subparsers = tablespec_parser.add_subparsers(dest='subcommand')

    tablespec_template = tablespec_subparsers.add_parser('template', help='Show Excel template info')

    tablespec_build = tablespec_subparsers.add_parser('build', help='Classify indicators (Stage 4)')
    tablespec_build.add_argument('--spec-file', default='output/table_specification.jsonc')
    tablespec_build.add_argument('--output-file', help='Output path (default: same as spec-file)')

    # Analysis command (Stage 5)
    analysis_parser = subparsers.add_parser('analysis', help='Analysis operations (Stage 5)')
    analysis_subparsers = analysis_parser.add_subparsers(dest='subcommand')

    analysis_indicators = analysis_subparsers.add_parser('indicators', help='Compute crosstabs (Stage 5)')
    analysis_indicators.add_argument('--spec-file', required=True)
    analysis_indicators.add_argument('--sav-file', required=True)
    analysis_indicators.add_argument('--output-file')

    # Stats command (Stage 6)
    stats_parser = subparsers.add_parser('stats', help='Statistical analysis (Stage 6)')
    stats_subparsers = stats_parser.add_subparsers(dest='subcommand')

    stats_test = stats_subparsers.add_parser('test', help='Chi-square tests')
    stats_test.add_argument('--crosstabs-file', required=True)
    stats_test.add_argument('--threshold', type=float, default=0.05)
    stats_test.add_argument('--output-file')

    stats_filter = stats_subparsers.add_parser('filter', help='Filter by significance')
    stats_filter.add_argument('--crosstabs-file', required=True)
    stats_filter.add_argument('--threshold', type=float, default=0.05)
    stats_filter.add_argument('--output-file')

    # Reporting command (Stage 7)
    reporting_parser = subparsers.add_parser('reporting', help='Report generation (Stage 7)')
    reporting_subparsers = reporting_parser.add_subparsers(dest='subcommand')

    reporting_ppt = reporting_subparsers.add_parser('ppt', help='Generate PowerPoint')
    reporting_ppt.add_argument('--tables-file', required=True)
    reporting_ppt.add_argument('--output-dir', default='output')

    reporting_html = reporting_subparsers.add_parser('html', help='Generate HTML dashboard')
    reporting_html.add_argument('--tables-file', required=True)
    reporting_html.add_argument('--output-dir', default='output')

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
        elif args.subcommand == 'prep':
            cmd_data_prep(args)
        else:
            data_subparsers.choices['read'].print_help()

    elif args.command == 'questions':
        if args.subcommand == 'extract':
            cmd_questions_extract(args)
        else:
            questions_subparsers.choices['extract'].print_help()

    elif args.command == 'indicators':
        if args.subcommand == 'batch':
            cmd_indicators_batch(args)
        else:
            indicators_subparsers.choices['batch'].print_help()

    elif args.command == 'tablespec':
        if args.subcommand == 'template':
            cmd_tablespec_template(args)
        elif args.subcommand == 'build':
            cmd_tablespec_build(args)
        else:
            tablespec_subparsers.choices['build'].print_help()

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


if __name__ == '__main__':
    main()
