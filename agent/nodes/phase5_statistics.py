"""
Phase 5: Statistical Analysis Nodes (Steps 17-18)

This module contains nodes for computing Chi-square statistics and Cramer's V:
- Step 17: generate_python_statistics_script_node - Generate stats_script.py
- Step 18: execute_python_statistics_script_node - Execute script, load results
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from agent.state import WorkflowState
from agent.config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


# =============================================================================
# Step 17: Generate Python Statistics Script
# =============================================================================

def generate_python_statistics_script_node(state: WorkflowState) -> WorkflowState:
    """
    Step 17: Generate Python script to compute Chi-square tests and Cramer's V.

    This node generates a standalone Python script (stats_script.py) that:
    - Reads cross-tabulation data from the new dataset
    - Computes Chi-square test for each table
    - Calculates Cramer's V effect size
    - Determines statistical significance (p < 0.05)
    - Saves results to statistical_summary.json

    The generated script uses:
    - pandas for data manipulation
    - scipy.stats for chi-square test
    - json for output serialization

    Args:
        state: Current workflow state. Must contain:
            - new_data_file: Path to new_data.sav (recoded dataset)
            - cross_table_file: Path to cross-table output file
            - table_specifications: Table structure definitions
            - config: Configuration dict for output paths

    Returns:
        Updated workflow state with:
            - statistics_script: Path to generated stats_script.py
            - current_step: Set to 17
            - errors: List of errors (appended if any occur)
            - warnings: List of warnings (appended if any occur)

    Example:
        >>> state = {
        ...     "new_data_file": "output/new_data.sav",
        ...     "cross_table_file": "output/cross_tables.csv",
        ...     "table_specifications": {"tables": [...]}
        ... }
        >>> new_state = generate_python_statistics_script_node(state)
        >>> print(new_state["statistics_script"])
        'temp/scripts/stats_script.py'
    """
    logger.info("Step 17: Generating Python statistics script")

    # Get required inputs from state
    new_data_file = state.get("new_data_file")
    cross_table_file = state.get("cross_table_file")
    table_specifications = state.get("table_specifications")
    config = state.get("config", DEFAULT_CONFIG)

    # Validate required inputs
    if not new_data_file:
        error_msg = "No new_data_file available in state. Cannot generate statistics script."
        logger.error(error_msg)
        return {
            **state,
            "current_step": 17,
            "errors": state.get("errors", []) + [error_msg],
        }

    if not table_specifications:
        error_msg = "No table_specifications available in state. Cannot generate statistics script."
        logger.error(error_msg)
        return {
            **state,
            "current_step": 17,
            "errors": state.get("errors", []) + [error_msg],
        }

    try:
        # Extract tables from specifications
        tables = table_specifications.get("tables", [])
        if not tables:
            warning_msg = "No tables found in table_specifications. Statistics script will have no tables to process."
            logger.warning(warning_msg)
            return {
                **state,
                "current_step": 17,
                "warnings": state.get("warnings", []) + [warning_msg],
            }

        logger.info(f"Generating statistics script for {len(tables)} tables")

        # Generate the Python script
        script_content = _generate_statistics_script_content(
            new_data_file=new_data_file,
            cross_table_file=cross_table_file,
            tables=tables,
            config=config
        )

        # Create output directory
        temp_dir = Path(config.get("temp_dir", "temp")) / "scripts"
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Write script to file
        script_path = temp_dir / "stats_script.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"Statistics script written to: {script_path}")
        logger.info(f"Script size: {len(script_content)} characters")

        return {
            **state,
            "current_step": 17,
            "statistics_script": str(script_path),
        }

    except Exception as e:
        error_msg = f"Unexpected error generating statistics script: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": 17,
            "errors": state.get("errors", []) + [error_msg],
        }


def _generate_statistics_script_content(
    new_data_file: str,
    cross_table_file: Optional[str],
    tables: list,
    config: Dict[str, Any]
) -> str:
    """
    Generate the content of the statistics script.

    Creates a standalone Python script that:
    1. Loads the dataset (new_data.sav)
    2. For each table specification:
       - Creates contingency table
       - Computes Chi-square test
       - Calculates Cramer's V
       - Interprets results
    3. Saves all results to statistical_summary.json

    Args:
        new_data_file: Path to new_data.sav
        cross_table_file: Path to cross-table output (optional)
        tables: List of table specification dictionaries
        config: Configuration dict

    Returns:
        Complete Python script as string
    """
    output_dir = config.get("output_dir", "output")
    significance_level = config.get("significance_level", 0.05)

    script_lines = [
        '#!/usr/bin/env python3',
        '"""',
        'Statistics Script for Chi-square Tests and Cramer\'s V',
        '',
        'Generated automatically by DataChat',
        f'Generated: {datetime.now().isoformat()}',
        '"""',
        '',
        'import sys',
        'import json',
        'import warnings',
        'from datetime import datetime',
        'from pathlib import Path',
        '',
        '# Third-party imports',
        'try:',
        '    import pandas as pd',
        '    import pyreadstat',
        '    from scipy.stats import chi2_contingency',
        'except ImportError as e:',
        '    print(f"Error: Required library not found: {e}")',
        '    print("Please install: pip install pandas pyreadstat scipy")',
        '    sys.exit(1)',
        '',
        'warnings.filterwarnings("ignore")',
        '',
        '',
        'def cramers_v(chi2, n, dof):',
        '    """',
        '    Calculate Cramer\'s V effect size.',
        '',
        '    Args:',
        '        chi2: Chi-square statistic',
        '        n: Total sample size',
        '        dof: Degrees of freedom',
        '',
        '    Returns:',
        '        Cramer\'s V value (0-1)',
        '    """',
        '    phi2 = chi2 / n',
        '    k = min(dof + 1, n)  # Number of categories',
        '    return (phi2 / (k - 1)) ** 0.5',
        '',
        '',
        'def interpret_effect_size(v):',
        '    """',
        '    Interpret Cramer\'s V effect size.',
        '',
        '    Args:',
        '        v: Cramer\'s V value',
        '',
        '    Returns:',
        '        Interpretation string',
        '    """',
        '    if v < 0.1:',
        '        return "negligible"',
        '    elif v < 0.3:',
        '        return "small"',
        '    elif v < 0.5:',
        '        return "medium"',
        '    else:',
        '        return "large"',
        '',
        '',
        'def compute_statistics_for_table(df, row_var, col_var):',
        '    """',
        '    Compute Chi-square test and Cramer\'s V for a contingency table.',
        '    ',
        '    Includes safety checks for:',
        '    - Minimum cell count threshold',
        '    - Table structure validation (2x2 minimum)',
        '    - Zero division prevention',
        '    ',
        '    Args:',
        '        df: DataFrame with the data',
        '        row_var: Row variable name',
        '        col_var: Column variable name',
        '    ',
        '    Returns:',
        '        Dictionary with test results and validity status',
        '    """',
        '    # Create contingency table',
        '    contingency_table = pd.crosstab(df[row_var], df[col_var])',
        '    ',
        '    # Initialize result with invalid state',
        '    result = {',
        '        "is_valid": False,',
        '        "chi_square": None,',
        '        "p_value": None,',
        '        "degrees_of_freedom": None,',
        '        "cramers_v": None,',
        '        "interpretation": None,',
        '        "is_significant": None,',
        '        "sample_size": None,',
        '        "error": None,',
        '        "warning": None,',
        '    }',
        '    ',
        '    # Check 1: Minimum table structure (at least 2x2)',
        '    if contingency_table.shape[0] < 2 or contingency_table.shape[1] < 2:',
        '        result["error"] = (',
        '            f"Invalid table structure: {contingency_table.shape}. "',
        '            "Minimum required is 2x2 (rows x columns)."',
        '        )',
        '        return result',
        '    ',
        '    # Get sample size',
        '    n = contingency_table.sum().sum()',
        '    ',
        '    # Check 2: Zero total count',
        '    if n == 0:',
        '        result["error"] = "Contingency table has zero total count"',
        '        return result',
        '    ',
        '    # Check 3: Row with zero total count (zero division risk)',
        '    row_totals = contingency_table.sum(axis=1)',
        '    if (row_totals == 0).any():',
        '        result["error"] = "Row with zero total count detected"',
        '        return result',
        '    ',
        '    # Check 4: Column with zero total count (zero division risk)',
        '    col_totals = contingency_table.sum(axis=0)',
        '    if (col_totals == 0).any():',
        '        result["error"] = "Column with zero total count detected"',
        '        return result',
        '    ',
        '    # Check 5: Minimum expected cell count',
        '    min_cell_count = 10',
        '    row_totals_matrix = row_totals.values.reshape(-1, 1)',
        '    col_totals_matrix = col_totals.values.reshape(1, -1)',
        '    expected = (row_totals_matrix @ col_totals_matrix) / n',
        '    min_expected = expected.min()',
        '    ',
        '    if min_expected < min_cell_count:',
        '        result["error"] = (',
        '            f"Minimum expected cell count ({min_expected:.2f}) "',
        '            f"below threshold ({min_cell_count}). "',
        '            "Chi-square results may be unreliable."',
        '        )',
        '        return result',
        '    ',
        '    # All checks passed - compute statistics',
        '    try:',
        '        # Compute chi-square test',
        '        chi2, p_value, dof, _ = chi2_contingency(contingency_table)',
        '        ',
        '        # Calculate Cramer\'s V',
        '        n_rows, n_cols = contingency_table.shape',
        '        min_dim = min(n_rows - 1, n_cols - 1)',
        '        cramers_v_value = cramers_v(chi2, n, dof)',
        '        ',
        '        # Determine significance',
        '        is_significant = p_value < ' + str(significance_level) + '',
        '        ',
        '        # Interpret effect size',
        '        interpretation = interpret_effect_size(cramers_v_value)',
        '        ',
        '        # Update result with computed values',
        '        result.update({',
        '            "is_valid": True,',
        '            "chi_square": float(chi2),',
        '            "p_value": float(p_value),',
        '            "degrees_of_freedom": int(dof),',
        '            "cramers_v": float(cramers_v_value),',
        '            "interpretation": interpretation,',
        '            "is_significant": is_significant,',
        '            "sample_size": int(n),',
        '        })',
        '        ',
        '    except Exception as e:',
        '        result["error"] = f"Chi-square computation failed: {e}"',
        '    ',
        '    return result',
        '',
        '',
        'def main():',
        f'    """Main execution function."""',
        '    # File paths',
        f'    input_file = r"' + str(new_data_file) + '"',
        f'    output_file = r"' + str(output_dir) + '/statistical_summary.json"',
        '',
        '    print("Loading data from:", input_file)',
        '    df, metadata = pyreadstat.read_sav(input_file, apply_value_formats=True)',
        '    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")',
        '',
        '    # Table specifications',
        '    tables = [',
    ]

    # Add each table specification
    for table in tables:
        row_var = table.get("row_variable")
        col_var = table.get("column_variable")
        table_name = table.get("table_name", f"{row_var}_x_{col_var}")

        script_lines.append(f'        {{')
        script_lines.append(f'            "table_name": "{table_name}",')
        script_lines.append(f'            "row_variable": "{row_var}",')
        script_lines.append(f'            "column_variable": "{col_var}",')
        script_lines.append(f'        }},')

    script_lines.extend([
        '    ]',
        '',
        '    # Compute statistics for each table',
        '    results = []',
        '    invalid_count = 0',
        '    ',
        '    for table_spec in tables:',
        '        table_name = table_spec["table_name"]',
        '        row_var = table_spec["row_variable"]',
        '        col_var = table_spec["column_variable"]',
        '        ',
        '        print(f"Processing: {table_name} ({row_var} x {col_var})")',
        '        ',
        '        # Check variables exist',
        '        if row_var not in df.columns:',
        '            print(f"  Warning: Row variable \'{row_var}\' not found in data")',
        '            # Create invalid entry for tracking',
        '            results.append({',
        '                "table_name": table_name,',
        '                "row_variable": row_var,',
        '                "column_variable": col_var,',
        '                "is_valid": False,',
        '                "error": f"Row variable \'{row_var}\' not found in data",',
        '                "chi_square": None,',
        '                "p_value": None,',
        '                "degrees_of_freedom": None,',
        '                "cramers_v": None,',
        '                "interpretation": None,',
        '                "is_significant": None,',
        '                "sample_size": None,',
        '            })',
        '            invalid_count += 1',
        '            continue',
        '        if col_var not in df.columns:',
        '            print(f"  Warning: Column variable \'{col_var}\' not found in data")',
        '            # Create invalid entry for tracking',
        '            results.append({',
        '                "table_name": table_name,',
        '                "row_variable": row_var,',
        '                "column_variable": col_var,',
        '                "is_valid": False,',
        '                "error": f"Column variable \'{col_var}\' not found in data",',
        '                "chi_square": None,',
        '                "p_value": None,',
        '                "degrees_of_freedom": None,',
        '                "cramers_v": None,',
        '                "interpretation": None,',
        '                "is_significant": None,',
        '                "sample_size": None,',
        '            })',
        '            invalid_count += 1',
        '            continue',
        '        ',
        '        # Compute statistics',
        '        stats = compute_statistics_for_table(df, row_var, col_var)',
        '        stats["table_name"] = table_name',
        '        stats["row_variable"] = row_var',
        '        stats["column_variable"] = col_var',
        '        results.append(stats)',
        '        ',
        '        if stats["is_valid"]:',
        '            print(f"  Chi-square: {stats["chi_square"]:.4f}")',
        '            print(f"  p-value: {stats["p_value"]:.4f}")',
        '            print(f"  Cramer\'s V: {stats["cramers_v"]:.4f} ({stats["interpretation"]})")',
        '            print(f"  Significant: {stats["is_significant"]}")',
        '        else:',
        '            print(f"  Invalid: {stats["error"]}")',
        '            invalid_count += 1',
        '    ',
        '    # Save results to JSON',
        '    output_path = Path(output_file)',
        '    output_path.parent.mkdir(parents=True, exist_ok=True)',
        '    ',
        '    valid_results = [r for r in results if r.get("is_valid", False)]',
        '    invalid_results = [r for r in results if not r.get("is_valid", False)]',
        '    ',
        '    summary = {',
        '        "generated_at": datetime.now().isoformat(),',
        '        "total_tables": len(results),',
        '        "valid_tables": len(valid_results),',
        '        "invalid_tables": len(invalid_results),',
        '        "significant_tables": sum(1 for r in valid_results if r.get("is_significant", False)),',
        f'        "significance_level": {significance_level},',
        '        "min_cell_count": 10,',
        '        "tables": results,',
        '    }',
        '    ',
        '    with open(output_path, "w") as f:',
        '        json.dump(summary, f, indent=2)',
        '    ',
        '    print(f"\\nResults saved to: {output_path}")',
        '    print(f"Total tables processed: {len(results)}")',
        '    print(f"Valid tables: {len(valid_results)}")',
        '    print(f"Invalid tables: {len(invalid_results)}")',
        '    print(f"Significant tables: {summary["significant_tables"]}")',
        '    ',
        '    if invalid_results:',
        '        print(f"\\nInvalid tables summary:")',
        '        for r in invalid_results[:5]:  # Show first 5',
        '            print(f"  - {r["table_name"]}: {r.get("error", "Unknown error")}")',
        '        if len(invalid_results) > 5:',
        '            print(f"  ... and {len(invalid_results) - 5} more")',
        '    ',
        '    return 0',
        '',
        '',
        'if __name__ == "__main__":',
        '    sys.exit(main())',
    ])

    return "\n".join(script_lines)


# =============================================================================
# Step 18: Execute Python Statistics Script
# =============================================================================

def execute_python_statistics_script_node(state: WorkflowState) -> WorkflowState:
    """
    Step 18: Execute generated Python statistics script and load results.

    This node:
    - Executes stats_script.py generated in Step 17
    - Captures script output and return code
    - Loads statistical results from statistical_summary.json
    - Logs execution results (tables processed, significant tables count)

    The script computes:
    - Chi-square test statistic
    - p-value
    - Degrees of freedom
    - Cramer's V effect size
    - Effect size interpretation (negligible/small/medium/large)
    - Statistical significance flag (p < 0.05)

    Args:
        state: Current workflow state. Must contain:
            - statistics_script: Path to stats_script.py from Step 17
            - config: Configuration dict for output paths

    Returns:
        Updated workflow state with:
            - statistical_summary: Dict with all statistical test results
            - current_step: Set to 18
            - errors: List of errors (appended if script fails)
            - warnings: List of warnings (appended for any issues)

    Error Handling:
        - Script execution failed: Check stderr, log error, continue to next step
        - Results file not found: Error, continues with partial state
        - Invalid JSON: Error, continues with partial state
        - Timeout: Error after 5 minutes

    Example:
        >>> state = {
        ...     "statistics_script": "temp/scripts/stats_script.py",
        ...     "config": {"output_dir": "output"}
        ... }
        >>> new_state = execute_python_statistics_script_node(state)
        >>> print(new_state["statistical_summary"]["total_tables"])
        25
        >>> print(new_state["statistical_summary"]["significant_tables"])
        12
    """
    logger.info("Step 18: Executing Python statistics script")

    # Get required inputs from state
    script_path = state.get("statistics_script")
    config = state.get("config", DEFAULT_CONFIG)

    # Validate required inputs
    if not script_path:
        error_msg = "No statistics_script available in state. Run Step 17 first."
        logger.error(error_msg)
        return {
            **state,
            "current_step": 18,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Verify script file exists
    if not os.path.exists(script_path):
        error_msg = f"Statistics script not found: {script_path}"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 18,
            "errors": state.get("errors", []) + [error_msg],
        }

    # Prepare output path
    output_dir = Path(config.get("output_dir", "output"))
    summary_path = output_dir / "statistical_summary.json"

    logger.info(f"Executing statistics script:")
    logger.info(f"  Script: {script_path}")
    logger.info(f"  Output: {summary_path}")

    try:
        # Execute the Python script via subprocess
        logger.info("Invoking Python to execute statistics script...")
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )

        # Check return code
        if result.returncode != 0:
            error_msg = f"Statistics script execution failed (return code {result.returncode})"
            logger.error(error_msg)

            # Log stderr for debugging
            if result.stderr:
                logger.error(f"Script stderr: {result.stderr}")

            # Log stdout for debugging (may contain partial output)
            if result.stdout:
                logger.error(f"Script stdout: {result.stdout}")

            return {
                **state,
                "current_step": 18,
                "errors": state.get("errors", []) + [error_msg],
            }

        # Log script output
        if result.stdout:
            logger.info(f"Script stdout:\n{result.stdout}")
        if result.stderr:
            # Script might output to stderr even on success
            logger.debug(f"Script stderr:\n{result.stderr}")

        # Verify results file was created
        if not os.path.exists(summary_path):
            error_msg = (
                f"Script executed successfully but output file was not created: {summary_path}. "
                f"Check script execution for errors."
            )
            logger.error(error_msg)
            return {
                **state,
                "current_step": 18,
                "errors": state.get("errors", []) + [error_msg],
            }

        # Load statistical summary
        logger.info(f"Loading statistical summary from: {summary_path}")
        with open(summary_path, 'r', encoding='utf-8') as f:
            statistical_summary = json.load(f)

        # Log results summary
        total_tables = statistical_summary.get("total_tables", 0)
        significant_tables = statistical_summary.get("significant_tables", 0)
        valid_tables = statistical_summary.get("valid_tables", total_tables)
        invalid_tables = statistical_summary.get("invalid_tables", 0)
        tables_data = statistical_summary.get("tables", [])

        logger.info(f"Statistical analysis completed:")
        logger.info(f"  Total tables processed: {total_tables}")
        logger.info(f"  Valid tables: {valid_tables}")
        logger.info(f"  Invalid tables: {invalid_tables}")
        logger.info(f"  Significant tables: {significant_tables}")
        logger.info(f"  Significance level: {statistical_summary.get('significance_level', 'N/A')}")

        # Prepare warnings
        warnings = state.get("warnings", []).copy()

        # Warn if no tables were processed
        if total_tables == 0:
            warning_msg = "No tables were processed by the statistics script"
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        # Warn about invalid tables
        if invalid_tables > 0:
            warning_msg = (
                f"{invalid_tables} table(s) marked as invalid due to statistical "
                f"assumption violations (e.g., small sample size, zero division risk). "
                f"See statistical_summary.json for details."
            )
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        # Warn if no significant tables found among valid tables
        if valid_tables > 0 and significant_tables == 0:
            warning_msg = (
                f"No significant tables found (p < {statistical_summary.get('significance_level', 0.05)}). "
                "This may indicate no statistically significant relationships in the data."
            )
            logger.warning(warning_msg)
            warnings.append(warning_msg)

        # Log details of invalid tables (for debugging)
        if invalid_tables > 0:
            logger.debug("Invalid tables:")
            for table in tables_data:
                if not table.get("is_valid", True):
                    logger.debug(
                        f"  - {table.get('table_name', 'Unknown')}: "
                        f"{table.get('error', 'Unknown error')}"
                    )

        # Update state
        new_state = {
            **state,
            "current_step": 18,
            "statistical_summary": statistical_summary,
            "warnings": warnings,
        }

        logger.info("Step 18 completed successfully")
        return new_state

    except subprocess.TimeoutExpired:
        error_msg = f"Statistics script execution timed out after 300 seconds"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 18,
            "errors": state.get("errors", []) + [error_msg],
        }

    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse statistical_summary.json: {str(e)}"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 18,
            "errors": state.get("errors", []) + [error_msg],
        }

    except FileNotFoundError as e:
        error_msg = f"Results file not found: {str(e)}"
        logger.error(error_msg)
        return {
            **state,
            "current_step": 18,
            "errors": state.get("errors", []) + [error_msg],
        }

    except Exception as e:
        error_msg = f"Unexpected error executing statistics script: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            **state,
            "current_step": 18,
            "errors": state.get("errors", []) + [error_msg],
        }
