"""
Stage 4: Statistical Analysis - Standardized Data Format

Calculates chi-square tests and filters significant tables.
Fixes data format consistency between Stage 3 (crosstabs) and Stage 4 (statistics).
"""

import json
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


def load_crosstabs(crosstabs_file: str) -> Dict[str, Any]:
    """Load cross-tables from Stage 3 output."""
    with open(crosstabs_file, 'r') as f:
        return json.load(f)


def save_results(
    results: List[Dict[str, Any]],
    stats_file: Path,
    filtered_file: Path
) -> None:
    """Save statistical analysis results in standardized format.

    Standard format for downstream stages:
    {
        "tables": [...],  # List of tables with embedded statistics
        "summary": {          # Overall statistics
            "total_tests": int,
            "significant_count": int,
            "significance_threshold": float
        }
    }

    Args:
        results: List of test result dictionaries
        stats_file: Path to save statistical summary
        filtered_file: Path to save filtered table list
    """
    # Prepare summary
    summary = {
        "total_tests": len(results),
        "significant_count": sum(1 for r in results if r.get("significant", False)),
        "significance_threshold": 0.05  # Default, should come from spec
    }

    # Save summary
    with open(stats_file, 'w') as f:
        json.dump(summary, f, indent=2)

    # Save filtered tables list
    with open(filtered_file, 'w') as f:
        json.dump(results, f, indent=2)


def main():
    """Main entry point for stage4-statistics skill."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Statistical analysis with standardized data format"
    )
    parser.add_argument("--crosstabs-file", required=True,
                        help="Path to cross_tables.json from Stage 3")
    parser.add_argument("--spec-file", required=True,
                        help="Path to table_specification.json")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory")
    parser.add_argument("--threshold", type=float, default=None,
                        help="Override significance threshold (default: from spec)")

    args = parser.parse_args()

    print("📈 Stage 4: Statistical Analysis")
    print("=" * 60)

    # Validate inputs
    crosstabs_path = Path(args.crosstabs_file)
    spec_path = Path(args.spec_file)

    if not crosstabs_path.exists():
        print(f"❌ Error: Cross-tables not found: {crosstabs_path}")
        print(f"   Run Stage 3 first: stage3-crosstabs")
        return 1

    if not spec_path.exists():
        print(f"❌ Error: Spec file not found: {spec_path}")
        return 1

    # Load data
    print("\n📖 Loading cross-tables...")
    crosstabs = load_crosstabs(str(crosstabs_path))

    # Load threshold from spec
    with open(spec_path, 'r') as f:
        spec = json.load(f)

    threshold = args.threshold or spec.get("output_settings", {}).get("significance_threshold", 0.05)

    # Step 10: Statistical analysis
    print("\n[Step 10] Calculating statistics...")
    results = []

    for table_id, table in crosstabs.items():
        df = pd.DataFrame(table)

        try:
            chi2, p_value, dof, expected = chi2_contingency(df.values)
            results.append({
                "table_id": table_id,
                "table_name": table_id,
                "chi_square": float(chi2),
                "p_value": float(p_value),
                "degrees_of_freedom": int(dof),
                "expected": expected.tolist(),
                "significant": bool(p_value < threshold)
            })
        except Exception as e:
            results.append({
                "table_id": table_id,
                "table_name": table_id,
                "error": str(e)
            })

    # Save results
    output_dir = Path(args.output_dir)
    stats_file = output_dir / "statistical_summary.json"
    filtered_file = output_dir / "filtered_tables.json"

    save_results(results, stats_file, filtered_file)

    sig_count = sum(1 for r in results if "error" not in r and r.get("significant", False))
    total_count = len(results)

    print(f"\n📊 Tests completed: {sig_count}/{total_count} significant")
    print(f"✅ Statistical summary: {stats_file}")
    print(f"✅ Filtered tables: {filtered_file}")
    print()
    print("=" * 60)
    return 0
