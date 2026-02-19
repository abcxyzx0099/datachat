#!/usr/bin/env python3
"""
Crosstab Scenarios Demo

Demonstrates all 4 crosstab scenarios with actual output examples.
Run this script to see the output format for each scenario.
"""

import pandas as pd
import numpy as np
import json
from survey_analyzer.analysis import CrosstabProcessor


def create_sample_data():
    """Create sample survey data for demonstration."""
    np.random.seed(42)
    n = 350

    data = {
        # Demographics (column indicator)
        "Q1_GENDER": np.random.choice(["Male", "Female"], size=n, p=[0.51, 0.49]),

        # Single categorical (row indicator)
        "Q2_SATISFACTION": np.random.choice(
            ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied"],
            size=n,
            p=[0.35, 0.44, 0.17, 0.04]
        ),

        # Multiple binary variables (Multiple Choice)
        "S1_BRAND_A": np.random.choice([0, 1], size=n, p=[0.35, 0.65]),
        "S1_BRAND_B": np.random.choice([0, 1], size=n, p=[0.40, 0.60]),
        "S1_BRAND_C": np.random.choice([0, 1], size=n, p=[0.30, 0.70]),
        "S1_BRAND_D": np.random.choice([0, 1], size=n, p=[0.50, 0.50]),

        # Single scalar
        "SAT_OVERALL": np.random.normal(7.5, 1.8, size=n).clip(0, 10).round(1),

        # Multiple scalar (Rating Scale)
        "D1_QUALITY": np.random.normal(7.4, 1.5, size=n).clip(1, 10).round(1),
        "D1_PRICE": np.random.normal(7.0, 1.6, size=n).clip(1, 10).round(1),
        "D1_SERVICE": np.random.normal(7.3, 1.4, size=n).clip(1, 10).round(1),
        "D1_SELECTION": np.random.normal(7.1, 1.5, size=n).clip(1, 10).round(1),
        "D1_VALUE": np.random.normal(7.2, 1.5, size=n).clip(1, 10).round(1),
    }

    return pd.DataFrame(data)


def print_separator(title):
    """Print a formatted separator."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_table(data):
    """Print crosstab data in a readable format."""
    rows = data.get("rows", [])
    total_row = data.get("total_row", {})

    # Print data rows
    for row in rows:
        label = row["label"]
        values = row["values"]
        if values:
            values_str = " | ".join([f"{k}: {v}" for k, v in values.items()])
            print(f"  {label:20} | {values_str}")
        else:
            print(f"  {label:20} | (no values)")

    # Print total row
    if total_row:
        print("  " + "-" * 60)
        label = total_row["label"]
        base_n = total_row.get("base_n", {})
        values = total_row.get("values")

        if values:
            values_str = " | ".join([f"{k}: {v}" for k, v in values.items()])
            print(f"  {label:20} | {values_str}")

        if base_n:
            base_str = " | ".join([f"{k}: (N={v})" for k, v in base_n.items()])
            print(f"  {'Base N':20} | {base_str}")


def main():
    """Run the demo."""
    print_separator("CROSSTAB SCENARIOS DEMO")

    # Create sample data
    df = create_sample_data()
    processor = CrosstabProcessor()

    # ========================================
    # Scenario 1: Single Categorical × Single Categorical
    # ========================================
    print_separator("Scenario 1: Single Categorical × Single Categorical")

    row_indicator = {
        "indicator_code": "Q2_SATISFACTION",
        "statistic_type": "categorical",
        "source_variables": ["Q2_SATISFACTION"],
        "question_type": "Single Choice",
        "transformation_rules": None
    }

    col_indicator = {
        "indicator_code": "Q1_GENDER",
        "statistic_type": "categorical",
        "source_variables": ["Q1_GENDER"],
        "question_type": "Single Choice",
        "transformation_rules": None
    }

    result = processor.generate(df, row_indicator, col_indicator)
    print(f"Table ID: {result.table_id}")
    print(f"Row Scenario: {result.row_scenario}")
    print(f"Column Scenario: {result.col_scenario}")
    print(f"Total Row Type: {result.total_row_type}")
    print("\nData:")
    print_table(result.data)
    print(f"\nStatistics: chi_square={result.statistics.get('chi_square'):.2f}, "
          f"p_value={result.statistics.get('p_value'):.4f}")

    # ========================================
    # Scenario 2: Multiple Binary (Multiple Choice) × Single Categorical
    # ========================================
    print_separator("Scenario 2: Multiple Binary × Single Categorical (Multiple Choice)")

    row_indicator = {
        "indicator_code": "S1_BRAND_AWARENESS",
        "statistic_type": "categorical",
        "source_variables": ["S1_BRAND_A", "S1_BRAND_B", "S1_BRAND_C", "S1_BRAND_D"],
        "question_type": "Multiple Choice",
        "transformation_rules": None
    }

    col_indicator = {
        "indicator_code": "Q1_GENDER",
        "statistic_type": "categorical",
        "source_variables": ["Q1_GENDER"],
        "question_type": "Single Choice",
        "transformation_rules": None
    }

    result = processor.generate(df, row_indicator, col_indicator)
    print(f"Table ID: {result.table_id}")
    print(f"Row Scenario: {result.row_scenario}")
    print(f"Column Scenario: {result.col_scenario}")
    print(f"Total Row Type: {result.total_row_type}")
    print("\nData (shows % of Yes for each brand):")
    print_table(result.data)

    # ========================================
    # Scenario 3: Single Scalar × Single Categorical
    # ========================================
    print_separator("Scenario 3: Single Scalar × Single Categorical")

    row_indicator = {
        "indicator_code": "SAT_OVERALL",
        "statistic_type": "scalar",
        "source_variables": ["SAT_OVERALL"],
        "question_type": "Numeric Input",
        "transformation_rules": None
    }

    col_indicator = {
        "indicator_code": "Q1_GENDER",
        "statistic_type": "categorical",
        "source_variables": ["Q1_GENDER"],
        "question_type": "Single Choice",
        "transformation_rules": None
    }

    result = processor.generate(df, row_indicator, col_indicator)
    print(f"Table ID: {result.table_id}")
    print(f"Row Scenario: {result.row_scenario}")
    print(f"Column Scenario: {result.col_scenario}")
    print(f"Total Row Type: {result.total_row_type}")
    print("\nData (descriptive statistics):")
    print_table(result.data)

    # ========================================
    # Scenario 4: Multiple Scalar (Rating Scale) × Single Categorical
    # ========================================
    print_separator("Scenario 4: Multiple Scalar × Single Categorical (Rating Scale)")

    row_indicator = {
        "indicator_code": "D1_RATINGS",
        "statistic_type": "scalar",
        "source_variables": ["D1_QUALITY", "D1_PRICE", "D1_SERVICE", "D1_SELECTION", "D1_VALUE"],
        "question_type": "Rating Scale",
        "transformation_rules": None
    }

    col_indicator = {
        "indicator_code": "Q1_GENDER",
        "statistic_type": "categorical",
        "source_variables": ["Q1_GENDER"],
        "question_type": "Single Choice",
        "transformation_rules": None
    }

    result = processor.generate(df, row_indicator, col_indicator)
    print(f"Table ID: {result.table_id}")
    print(f"Row Scenario: {result.row_scenario}")
    print(f"Column Scenario: {result.col_scenario}")
    print(f"Total Row Type: {result.total_row_type}")
    print("\nData (mean ratings for each attribute):")
    print_table(result.data)

    # ========================================
    # JSON Output Example
    # ========================================
    print_separator("JSON Output Example (Scenario 1)")

    # Show JSON structure for Scenario 1
    row_indicator = {
        "indicator_code": "Q2_SATISFACTION",
        "statistic_type": "categorical",
        "source_variables": ["Q2_SATISFACTION"],
        "question_type": "Single Choice",
        "transformation_rules": None
    }

    col_indicator = {
        "indicator_code": "Q1_GENDER",
        "statistic_type": "categorical",
        "source_variables": ["Q1_GENDER"],
        "question_type": "Single Choice",
        "transformation_rules": None
    }

    result = processor.generate(df, row_indicator, col_indicator)
    result_dict = result.to_dict()

    print("\nFull JSON structure:")
    print(json.dumps(result_dict, indent=2, default=str))

    print("\n" + "=" * 80)
    print("  Demo Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
