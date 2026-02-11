"""
SPSS Analyzer Library - Demo and Test Script

This script demonstrates the library functionality with sample data.
Run it to verify the library is working correctly.

Usage:
    cd /home/admin/workspaces/datachat/lib
    python3 -m spss_analyzer.examples.demo
"""

import sys
from pathlib import Path

# Add lib directory to path for imports
lib_dir = Path(__file__).parent.parent
sys.path.insert(0, str(lib_dir))

# Direct imports to avoid module resolution issues
from analysis.statistics import StatisticsCalculator, chi_square_test
from analysis.indicators import (
    IndicatorGenerator,
    IndicatorConfig,
    Indicator,
    IndicatorType,
    generate_indicators
)
from filtering.significance import SignificanceFilter, FilterCriteria, filter_significant
from pspp.syntax import RecodingSyntaxGenerator, CTablesSyntaxGenerator
from pspp.executor import PSPPExecutor, PSPPConfig, PSPPResult
from reporting.powerpoint import PowerPointGenerator, ChartType
from reporting.dashboard import HTMLDashboardGenerator, DashboardConfig


def demo_statistics():
    """Demo statistics calculation with sample data."""
    print("=" * 60)
    print("DEMO: Statistics Calculator")
    print("=" * 60)
    print()

    # Sample cross-tabulation table (Gender x Satisfaction)
    counts = [
        [45, 32, 18],  # Male: Yes, No, Neutral
        [52, 28, 25],  # Female: Yes, No, Neutral
    ]
    row_labels = ["Male", "Female"]
    column_labels = ["Satisfied", "Dissatisfied", "Neutral"]

    print("Sample Table: Gender x Satisfaction")
    print("-" * 40)
    print(f"{'':15} {column_labels[0]:>12} {column_labels[1]:>12} {column_labels[2]:>12}")
    for i, row_label in enumerate(row_labels):
        print(f"{row_label:15} {counts[i][0]:>12} {counts[i][1]:>12} {counts[i][2]:>12}")
    print()

    # Calculate statistics
    calc = StatisticsCalculator(significance_level=0.05)
    result = calc.analyze_table(counts, row_labels, column_labels)

    # Print results
    print("Statistical Test Results:")
    print("-" * 40)
    print(f"Chi-square statistic: {result.chi_square:.4f}")
    print(f"Degrees of freedom:    {result.degrees_of_freedom}")
    print(f"P-value:               {result.p_value:.4f}")
    print(f"Cramer's V:            {result.cramers_v:.4f}")
    print(f"Effect size:           {result.interpretation}")
    print(f"Significant (p<0.05):  {result.is_significant}")
    print(f"Valid:                 {result.is_valid}")
    print()

    # Demo using the convenience function
    print("Using convenience function:")
    print("-" * 40)
    result_dict = chi_square_test(counts, row_labels, column_labels)
    for key, value in result_dict.items():
        if isinstance(value, float):
            print(f"{key:20} {value:.4f}")
        else:
            print(f"{key:20} {value}")
    print()


def demo_filtering():
    """Demo filtering with sample data."""
    print("=" * 60)
    print("DEMO: Significance Filter")
    print("=" * 60)
    print()

    # Sample tables with statistics
    tables_with_stats = [
        {
            "table_name": "gender_x_satisfaction",
            "p_value": 0.032,
            "cramers_v": 0.18,
            "is_valid": True,
        },
        {
            "table_name": "age_x_brand",
            "p_value": 0.156,
            "cramers_v": 0.08,
            "is_valid": True,
        },
        {
            "table_name": "region_x_preference",
            "p_value": 0.003,
            "cramers_v": 0.32,
            "is_valid": True,
        },
        {
            "table_name": "income_x_satisfaction",
            "p_value": 0.044,
            "cramers_v": 0.09,  # Below threshold
            "is_valid": True,
        },
        {
            "table_name": "education_x_awareness",
            "p_value": None,  # Invalid test
            "cramers_v": 0.0,
            "is_valid": False,
            "error": "Insufficient cell count",
        },
    ]

    # Print input tables
    print("Input Tables:")
    print("-" * 60)
    for table in tables_with_stats:
        p_val = table.get("p_value", "N/A")
        v = table.get("cramers_v", "N/A")
        valid = table.get("is_valid", True)

        # Format values (handle None)
        p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
        v_str = f"{v:.4f}" if v is not None else "N/A"

        status = "Valid" if valid else f"Invalid: {table.get('error', 'Unknown')}"
        print(f"{table['table_name']:30} p={p_str:>6} V={v_str:>6} {status}")
    print()

    # Apply filter with default criteria
    print("Filter Criteria (default):")
    print("-" * 60)
    print(f"Significance level: 0.05 (p < 0.05)")
    print(f"Minimum Cramer's V:  0.1")
    print(f"Require valid:       True")
    print()

    filter_obj = SignificanceFilter()
    filter_list = filter_obj.filter_tables(tables_with_stats)

    print("Filter Results:")
    print("-" * 60)
    for result in filter_list.filters:
        table_id = result["table_id"]
        include = result["include"]
        reason = result["reason"]

        symbol = "✓" if include else "✗"
        status = "INCLUDE" if include else "EXCLUDE"

        print(f"{symbol} {table_id:30} [{status:7}] {reason}")
    print()

    print("Summary:")
    print("-" * 60)
    print(f"Total tables:     {filter_list.summary.total_tables}")
    print(f"Included:         {filter_list.summary.included}")
    print(f"Excluded:         {filter_list.summary.excluded}")
    print(f"Inclusion rate:   {filter_list.summary.inclusion_rate:.1f}%")
    print()

    print("Exclusion Reasons:")
    print("-" * 60)
    for reason, count in filter_list.summary.exclusion_reasons.items():
        if count > 0:
            print(f"{reason.replace('_', ' ').title():30} {count}")
    print()

    # Demo custom filter criteria
    print("Custom Filter Criteria (more lenient):")
    print("-" * 60)
    custom_criteria = FilterCriteria(
        significance_level=0.10,  # More lenient p-value
        min_cramers_v=0.05,       # More lenient effect size
    )
    custom_filter = SignificanceFilter(criteria=custom_criteria)
    custom_result = custom_filter.filter_tables(tables_with_stats)

    print(f"Total tables:     {custom_result.summary.total_tables}")
    print(f"Included:         {custom_result.summary.included}")
    print(f"Excluded:         {custom_result.summary.excluded}")
    print(f"Inclusion rate:   {custom_result.summary.inclusion_rate:.1f}%")
    print()


def demo_filter_apply():
    """Demo applying filter to extract included tables."""
    print("=" * 60)
    print("DEMO: Applying Filter to Table List")
    print("=" * 60)
    print()

    # Tables with data
    tables = [
        {
            "table_name": "gender_x_satisfaction",
            "row_variable": "gender",
            "column_variable": "satisfaction",
            "data": {"row_labels": ["M", "F"], "column_labels": ["Y", "N"], "counts": [[45, 32], [52, 28]]},
            "p_value": 0.032,
            "cramers_v": 0.18,
            "is_valid": True,
        },
        {
            "table_name": "age_x_brand",
            "row_variable": "age_group",
            "column_variable": "brand",
            "data": {"row_labels": ["18-34", "35+"], "column_labels": ["A", "B"], "counts": [[30, 40], [25, 35]]},
            "p_value": 0.156,
            "cramers_v": 0.08,
            "is_valid": True,
        },
    ]

    # Filter
    filter_obj = SignificanceFilter()
    filter_list = filter_obj.filter_tables(tables)

    # Apply filter
    included_tables = filter_obj.apply_filter(tables, filter_list.filters)

    print(f"Original tables: {len(tables)}")
    print(f"Filtered tables: {len(included_tables)}")
    print()

    print("Included tables:")
    for table in included_tables:
        print(f"  - {table['table_name']}")
    print()


def demo_pspp_syntax():
    """Demo PSPP syntax generation."""
    print("=" * 60)
    print("DEMO: PSPP Syntax Generation")
    print("=" * 60)
    print()

    # Recoding rules
    print("1. Recoding Syntax Generator")
    print("-" * 60)
    print()

    recoding_rules = [
        {
            "source_variable": "age",
            "target_variable": "age_group",
            "transformation_type": "range_grouping",
            "description": "Age groups for analysis",
            "rules": [
                {"source_min": 0, "source_max": 30, "target_value": 1, "target_label": "18-30"},
                {"source_min": 31, "source_max": 50, "target_value": 2, "target_label": "31-50"},
                {"source_min": 51, "source_max": "HI", "target_value": 3, "target_label": "51+"},
            ]
        }
    ]

    gen = RecodingSyntaxGenerator()
    syntax = gen.generate_syntax(recoding_rules, file_label="Age Recoding")
    print(syntax)
    print()

    # CTABLES syntax
    print("2. CTABLES Syntax Generator")
    print("-" * 60)
    print()

    table_specs = [
        {
            "table_id": "gender_x_satisfaction",
            "row_variable": "gender",
            "column_variable": "satisfaction",
            "statistics": ["count", "columnpct", "chisq", "cramersv"]
        }
    ]

    ctables_gen = CTablesSyntaxGenerator()
    ctables_syntax = ctables_gen.generate_syntax(table_specs)
    print(ctables_syntax)
    print()


def demo_pspp_executor():
    """Demo PSPP executor (without actual execution)."""
    print("=" * 60)
    print("DEMO: PSPP Executor")
    print("=" * 60)
    print()

    executor = PSPPExecutor()

    # Check if PSPP is available
    print("Checking PSPP availability...")
    available = executor.check_pspp_available()
    print(f"PSPP available: {available}")
    print()

    if available:
        version = executor.get_pspp_version()
        print(f"PSPP version: {version}")
        print()

        # Note: We don't actually execute since we don't have test files
        print("Note: Actual execution requires .sav and .sps files.")
        print("Example usage:")
        print("  result = executor.execute_syntax(")
        print("      syntax_file='recoding.sps',")
        print("      input_file='original.sav',")
        print("      output_file='recoded.sav'")
        print("  )")
    else:
        print("PSPP is not installed on this system.")
        print("Install with: apt-get install pspp")
    print()


def demo_powerpoint():
    """Demo PowerPoint generator."""
    print("=" * 60)
    print("DEMO: PowerPoint Generator")
    print("=" * 60)
    print()

    # Sample tables with statistics
    tables = [
        {
            "table_name": "gender_x_satisfaction",
            "row_variable": "gender",
            "column_variable": "satisfaction",
            "data": {
                "row_labels": ["Male", "Female"],
                "column_labels": ["Satisfied", "Dissatisfied"],
                "counts": [[45, 32], [52, 28]]
            }
        },
        {
            "table_name": "region_x_preference",
            "row_variable": "region",
            "column_variable": "brand_preference",
            "data": {
                "row_labels": ["North", "South", "East", "West"],
                "column_labels": ["Brand A", "Brand B"],
                "counts": [[30, 25], [28, 32], [22, 28], [25, 30]]
            }
        }
    ]

    statistics = {
        "tables": [
            {
                "table_name": "gender_x_satisfaction",
                "chi_square": 2.45,
                "p_value": 0.032,
                "cramers_v": 0.18,
                "interpretation": "small",
                "is_significant": True,
                "is_valid": True
            },
            {
                "table_name": "region_x_preference",
                "chi_square": 1.23,
                "p_value": 0.156,
                "cramers_v": 0.08,
                "interpretation": "negligible",
                "is_significant": False,
                "is_valid": True
            }
        ]
    }

    print("Sample data:")
    print(f"  Tables: {len(tables)}")
    print(f"  Significant: {sum(1 for t in statistics['tables'] if t['is_significant'])}")
    print()

    # Note: We don't actually create the PPTX without python-pptx
    try:
        from pptx import Presentation
        pptx_available = True
    except ImportError:
        pptx_available = False

    if pptx_available:
        print("PowerPoint generation is available.")
        print()
        print("Example usage:")
        print("  gen = PowerPointGenerator()")
        print("  gen.create_presentation(")
        print("      tables=tables,")
        print("      statistics=statistics,")
        print("      title='Survey Results'")
        print("  )")
        print("  gen.save('output.pptx')")
    else:
        print("PowerPoint generation requires python-pptx.")
        print("Install with: pip install python-pptx")
    print()


def demo_indicators():
    """Demo indicator generation."""
    print("=" * 60)
    print("DEMO: Indicator Generator")
    print("=" * 60)
    print()

    # Sample metadata
    metadata = {
        "sat_1": {"label": "Satisfaction with product quality", "value_labels": {"1": "Very Dissatisfied", "5": "Very Satisfied"}},
        "sat_2": {"label": "Satisfaction with service quality", "value_labels": {"1": "Very Dissatisfied", "5": "Very Satisfied"}},
        "sat_3": {"label": "Overall satisfaction", "value_labels": {"1": "Very Dissatisfied", "5": "Very Satisfied"}},
        "loy_1": {"label": "Likelihood to recommend", "value_labels": {"1": "Very Unlikely", "5": "Very Likely"}},
        "loy_2": {"label": "Likelihood to repurchase", "value_labels": {"1": "Very Unlikely", "5": "Very Likely"}},
        "age": {"label": "Age group", "value_labels": {"1": "18-30", "2": "31-50", "3": "51+"}},
        "gender": {"label": "Gender", "value_labels": {"1": "Male", "2": "Female"}},
        "brand_a": {"label": "Brand A preference", "value_labels": {"1": "Yes", "2": "No"}},
        "brand_b": {"label": "Brand B preference", "value_labels": {"1": "Yes", "2": "No"}},
    }

    print("Sample metadata:")
    print(f"  Variables: {len(metadata)}")
    print()

    # Demo 1: Keyword-based grouping
    print("1. Keyword-based Indicator Generation")
    print("-" * 60)
    print()

    gen = IndicatorGenerator()

    # Using prefix
    config = IndicatorConfig(
        type=IndicatorType.KEYWORD,
        prefix="sat_",
        min_variables=2
    )
    indicators = gen.generate(metadata, config)

    print(f"Generated {len(indicators)} indicator(s) with prefix 'sat_':")
    for ind in indicators:
        print(f"  - {ind.name}: {ind.variables}")
        print(f"    Description: {ind.description}")
    print()

    # Demo 2: Auto-detect patterns
    print("2. Auto-detect Pattern Grouping")
    print("-" * 60)
    print()

    config_auto = IndicatorConfig(
        type=IndicatorType.KEYWORD,
        min_variables=2
    )
    indicators_auto = gen.generate(metadata, config_auto)

    print(f"Detected {len(indicators_auto)} indicator group(s):")
    for ind in indicators_auto:
        print(f"  - {ind.name}: {ind.variables}")
    print()

    # Demo 3: Manual groupings
    print("3. Manual Indicator Grouping")
    print("-" * 60)
    print()

    config_manual = IndicatorConfig(
        type=IndicatorType.MANUAL,
        manual_groupings={
            "satisfaction": ["sat_1", "sat_2", "sat_3"],
            "loyalty": ["loy_1", "loy_2"],
            "brand_preference": ["brand_a", "brand_b"]
        }
    )
    indicators_manual = gen.generate(metadata, config_manual)

    print(f"Created {len(indicators_manual)} manual indicator(s):")
    for ind in indicators_manual:
        print(f"  - {ind.name}: {ind.variable_count} variables")
    print()

    # Demo 4: Using convenience function
    print("4. Using Convenience Function")
    print("-" * 60)
    print()

    indicators_simple = generate_indicators(
        metadata,
        strategy="keyword",
        prefix="loy_"
    )

    print(f"Simple indicator generation: {len(indicators_simple)} indicator(s)")
    for ind in indicators_simple:
        print(f"  - {ind['name']}: {ind['variables']}")
    print()


def demo_dashboard():
    """Demo HTML dashboard generator."""
    print("=" * 60)
    print("DEMO: HTML Dashboard Generator")
    print("=" * 60)
    print()

    # Sample cross-table data
    cross_tables = {
        "tables": [
            {
                "table_id": "gender_x_satisfaction",
                "table_name": "gender_x_satisfaction",
                "row_variable": "Gender",
                "column_variable": "Satisfaction",
                "data": {
                    "row_labels": ["Male", "Female"],
                    "column_labels": ["Satisfied", "Neutral", "Dissatisfied"],
                    "counts": [[45, 20, 15], [52, 18, 20]],
                    "column_percentages": [[38.8, 35.7, 37.5], [44.8, 32.1, 50.0]]
                }
            },
            {
                "table_id": "age_x_brand",
                "table_name": "age_x_brand",
                "row_variable": "Age Group",
                "column_variable": "Brand Preference",
                "data": {
                    "row_labels": ["18-30", "31-50", "50+"],
                    "column_labels": ["Brand A", "Brand B"],
                    "counts": [[30, 25], [28, 32], [22, 28]],
                    "column_percentages": [[37.5, 30.1], [35.0, 38.6], [27.5, 33.7]]
                }
            }
        ]
    }

    # Sample statistics
    statistics = {
        "significance_level": 0.05,
        "tables": [
            {
                "table_name": "gender_x_satisfaction",
                "chi_square": 2.15,
                "degrees_of_freedom": 2,
                "p_value": 0.341,
                "cramers_v": 0.085,
                "interpretation": "negligible",
                "is_significant": False,
                "is_valid": True
            },
            {
                "table_name": "age_x_brand",
                "chi_square": 1.82,
                "degrees_of_freedom": 2,
                "p_value": 0.402,
                "cramers_v": 0.078,
                "interpretation": "negligible",
                "is_significant": False,
                "is_valid": True
            }
        ]
    }

    # Generate dashboard
    gen = HTMLDashboardGenerator()

    print("Dashboard configuration:")
    print(f"  Title: {gen.config.title}")
    print(f"  Show charts: {gen.config.show_charts}")
    print(f"  Enable export: {gen.config.enable_export}")
    print()

    html_content = gen.generate_dashboard(cross_tables, statistics)

    print(f"Generated dashboard: {len(html_content)} characters")
    print(f"  - {len(cross_tables['tables'])} table cards")
    print(f"  - Summary statistics section")
    print(f"  - Sidebar navigation")
    print(f"  - Interactive JavaScript")
    print()

    print("HTML structure:")
    print("  <!DOCTYPE html>")
    print("  <html>")
    print("    <head>")
    print("      - CSS styles")
    print("      - Chart.js CDN")
    print("    </head>")
    print("    <body>")
    print("      - Sidebar (navigation)")
    print("      - Main content")
    print("        - Summary section")
    print("        - Table cards with charts")
    print("      - JavaScript (Chart.js, filtering)")
    print("    </body>")
    print("  </html>")
    print()

    print("Example usage:")
    print("  gen = HTMLDashboardGenerator()")
    print("  html = gen.generate_dashboard(cross_tables, statistics)")
    print("  gen.save('output/dashboard.html', html)")
    print()


def main():
    """Run all demos."""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "SPSS ANALYZER LIBRARY - DEMO" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    try:
        demo_statistics()
        demo_filtering()
        demo_filter_apply()
        demo_pspp_syntax()
        demo_pspp_executor()
        demo_powerpoint()
        demo_indicators()
        demo_dashboard()

        print("=" * 60)
        print("✓ All demos completed successfully!")
        print("=" * 60)
        print()
        print("The library is ready to use.")
        print()
        print("Import examples:")
        print("  from spss_analyzer.analysis import StatisticsCalculator")
        print("  from spss_analyzer.analysis import IndicatorGenerator")
        print("  from spss_analyzer.filtering import SignificanceFilter")
        print("  from spss_analyzer.pspp import RecodingSyntaxGenerator")
        print("  from spss_analyzer.pspp import PSPPExecutor")
        print("  from spss_analyzer.reporting import PowerPointGenerator")
        print("  from spss_analyzer.reporting import HTMLDashboardGenerator")
        print()

    except Exception as e:
        print()
        print("❌ Error during demo:")
        print(f"  {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
