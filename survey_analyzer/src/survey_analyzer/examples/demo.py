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
from analysis.transformation import TransformationEngine, apply_recode
from analysis.crosstab import CrossTabGenerator, generate_crosstab
from filtering.significance import SignificanceFilter, FilterCriteria, filter_significant
from reporting.powerpoint import PowerPointGenerator, ChartType
from reporting.dashboard import HTMLDashboardGenerator, DashboardConfig

import pandas as pd
import numpy as np


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


def demo_transformation():
    """Demo variable transformation engine."""
    print("=" * 60)
    print("DEMO: Variable Transformation Engine")
    print("=" * 60)
    print()

    # Create sample DataFrame
    print("1. Sample Data")
    print("-" * 60)
    df = pd.DataFrame({
        'age': [18, 25, 35, 45, 55, 65, 22, 28, 38, 48],
        'satisfaction': [1, 2, 3, 4, 5, 4, 3, 2, 1, 5],
        'income': [15000, 25000, 35000, 45000, 55000, 65000, 20000, 30000, 40000, 50000]
    })
    print(df)
    print()

    # Recoding demo
    print("2. Recoding: Group Age into Categories")
    print("-" * 60)
    print("Rule: '(1 THRU 2=1) (3=2) (4 THRU 5=3)'")
    print()

    engine = TransformationEngine()
    recoded = apply_recode(df['age'], "(1 THRU 2=1) (3=2) (4 THRU 5=3)")

    print("Original age -> Recoded age_group")
    for i in range(min(5, len(df))):
        print(f"  {df['age'][i]} -> {recoded.iloc[i]}")
    print()

    # Batch transformation demo
    print("3. Batch Transformation from Indicators")
    print("-" * 60)
    print()

    indicators = [
        {
            'indicator_code': 'age_group',
            'source_variables': ['age'],
            'transformation_rules': '(1 THRU 30=1) (31 THRU 50=2) (51 THRU HI=3)'
        },
        {
            'indicator_code': 'sat_group',
            'source_variables': ['satisfaction'],
            'transformation_rules': '(1 THRU 2=1) (3=2) (4 THRU 5=3)'
        }
    ]

    df_transformed = engine.apply_transformations(df, indicators)
    print("Transformed DataFrame:")
    print(df_transformed[['age', 'age_group', 'satisfaction', 'sat_group']])
    print()


def demo_crosstab():
    """Demo cross-tabulation with statistics."""
    print("=" * 60)
    print("DEMO: Cross-Tabulation with Statistics")
    print("=" * 60)
    print()

    # Create sample DataFrame
    print("1. Sample Data (200 respondents)")
    print("-" * 60)
    np.random.seed(42)
    df = pd.DataFrame({
        'gender': np.random.choice(['Male', 'Female'], 200),
        'satisfaction': np.random.choice([1, 2, 3, 4, 5], 200),
        'age_group': np.random.choice([1, 2, 3], 200),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 200)
    })
    print(df.head(10))
    print()

    # Generate single crosstab
    print("2. Single Cross-Tabulation: Gender x Satisfaction")
    print("-" * 60)
    print()

    result = generate_crosstab(df, 'gender', 'satisfaction')
    print(f"Table ID: {result['table_id']}")
    print(f"Statistics:")
    print(f"  Chi-square: {result['statistics']['chi_square']:.4f}")
    print(f"  p-value: {result['statistics']['p_value']:.4f}")
    print(f"  Cramer's V: {result['statistics']['cramers_v']:.4f}")
    print(f"  Interpretation: {result['statistics']['interpretation']}")
    print(f"  Significant: {result['statistics']['is_significant']}")
    print()

    # Print the crosstab table
    print("Cross-tabulation table:")
    crosstab_df = pd.DataFrame(result['crosstab']).T if isinstance(result['crosstab'], dict) else result['crosstab']
    print(crosstab_df)
    print()

    # Batch generation demo
    print("3. Batch Cross-Tabulation")
    print("-" * 60)
    print()

    table_pairs = [
        {'row_var': 'gender', 'col_var': 'age_group'},
        {'row_var': 'region', 'col_var': 'satisfaction'}
    ]

    generator = CrossTabGenerator()
    results = generator.generate_batch(df, table_pairs)

    print(f"Generated {len(results)} cross-tabulations:")
    for r in results:
        if r.is_valid:
            sig = "**" if r.statistics['p_value'] < 0.01 else "*" if r.statistics['p_value'] < 0.05 else ""
            print(f"  {r.table_id}: χ²={r.statistics['chi_square']:.2f}, p={r.statistics['p_value']:.4f} {sig}")
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
        demo_transformation()
        demo_crosstab()
        demo_filtering()
        demo_filter_apply()
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
        print("  from survey_analyzer.analysis import StatisticsCalculator")
        print("  from survey_analyzer.analysis import TransformationEngine")
        print("  from survey_analyzer.analysis import CrossTabGenerator")
        print("  from survey_analyzer.analysis import IndicatorGenerator")
        print("  from survey_analyzer.filtering import SignificanceFilter")
        print("  from survey_analyzer.reporting import PowerPointGenerator")
        print("  from survey_analyzer.reporting import HTMLDashboardGenerator")
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
