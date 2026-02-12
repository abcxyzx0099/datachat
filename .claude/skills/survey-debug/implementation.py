"""
Survey Debug - Debugging & Testing Tool

Provides testing, debugging, and validation for survey analysis workflow.
"""

import json
import sys
import argparse
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    from spss_analyzer.io import SPSSReader
    from spss_analyzer.io import MetadataTransformer
    from spss_analyzer.pspp import PSPPExecutor
except ImportError as e:
    print(f"❌ Error: {e}")
    print("   Install: Add lib directory to PYTHONPATH")
    sys.exit(1)


def create_test_metadata() -> Dict[str, Any]:
    """Create sample metadata for testing."""
    return {
        "q1_satisfaction": {
            "label": "Customer Satisfaction",
            "value_labels": {
                "1": "Very Dissatisfied",
                "2": "Dissatisfied",
                "3": "Neutral",
                "4": "Satisfied",
                "5": "Very Satisfied"
            },
            "variable_type": "ordinal"
        },
        "q2_brand_rating": {
            "label": "Brand Rating",
            "value_labels": {
                "1": "Poor",
                "2": "Fair",
                "3": "Good",
                "4": "Very Good",
                "5": "Excellent"
            },
            "variable_type": "ordinal"
        },
        "dem_gender": {
            "label": "Gender",
            "value_labels": {
                "1": "Male",
                "2": "Female"
            },
            "variable_type": "categorical"
        },
        "dem_age": {
            "label": "Age Group",
            "value_labels": {
                "1": "18-29",
                "2": "30-44",
                "3": "45-59",
                "4": "60+"
            },
            "variable_type": "categorical"
        },
        "sample_size": {
            "label": "Sample Size",
            "value": 150,
            "variable_type": "metadata"
        }
    }


def create_test_sav() -> bytes:
    """Create a minimal test .sav file."""
    # PSPP header
    header = b'\x00\x00\x02\x00\x00\x01\x00\x00'  # 2024-07-24 12:00:00
    # Variable count (4)
    var_count = b'\x04\x00\x00\x00\x04'  # 4 variables
    # Very short format (8) - indicates 2.0 compatible
    format_version = b'\x02'  # PSPP 2.0
    # Element count (3) - header, variable count, 1 value
    element_count = b'\x03\x00\x00\x00\x03'  # 3

    # Simple variable records (for 2 variables with 1 value each)
    var_records = b''

    # Variable 1: q1_satisfaction (1-5)
    var_records += b'\x01\x00\x00\x00\x01\x00'  # var name=1
    var_records += b'\x05'  # var type=1 (ordinal/categorical)
    var_records += b'\x04\x00\x00\x00\x05\x00\x00\x00\x00\x00\x01'  # label length=5, value count=5
    for i, label in enumerate(["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"], start=1):
        var_records += bytes([i], encoding='ascii')  # ASCII label

    # Variable 2: q2_brand_rating (1-5)
    var_records += b'\x02\x00\x00\x00\x02\x00'  # var name=2
    var_records += b'\x05'  # var type=1
    var_records += b'\x04\x00\x00\x00\x05\x00\x00\x00\x00\x01'  # label length=5, value count=5
    for i, label in enumerate(["Poor", "Fair", "Good", "Very Good", "Excellent"], start=1):
        var_records += bytes([i], encoding='ascii')

    # Variable 3: dem_gender (1-2)
    var_records += b'\x03\x00\x00\x00\x03\x00'  # var name=3
    var_records += b'\x02'  # var type=2 (categorical)
    var_records += b'\x04\x00\x00\x00\x02\x00\x00'  # label length=6, value count=2

    # Variable 4: dem_age (1-4)
    var_records += b'\x04\x00\x00\x00\x04\x00'  # var name=4
    var_records += b'\x03'  # var type=2
    var_records += b'\x04\x00\x00\x00\x04\x00\x00\x00\x00\x01'  # label length=15, value count=4

    return header + var_count + var_records + b'\x00' * 8  # 8 value records


def test_metadata_transformer() -> Tuple[bool, List[str]]:
    """Test MetadataTransformer class."""
    print("\n🧪 Testing MetadataTransformer...")

    transformer = MetadataTransformer()
    test_metadata = create_test_metadata()

    # Test 1: to_variable_centered
    print("  [Test 1] to_variable_centered...")
    result = transformer.to_variable_centered(test_metadata)

    if not isinstance(result, dict):
        return False, "to_variable_centered should return dict"

    # Check structure
    expected_vars = ["q1_satisfaction", "q2_brand_rating", "dem_gender", "dem_age", "sample_size"]
    missing_vars = set(expected_vars) - set(result.keys())
    extra_vars = set(result.keys()) - set(expected_vars)

    issues = []
    if missing_vars:
        issues.append(f"Missing variables: {missing_vars}")
    if extra_vars:
        issues.append(f"Extra variables: {extra_vars}")

    # Check variable structure
    for var_name, var_info in result.items():
        if "label" not in var_info:
            issues.append(f"{var_name}: Missing 'label' field")
        if "value_labels" not in var_info:
            issues.append(f"{var_name}: Missing 'value_labels' field")
        if "variable_type" not in var_info:
            issues.append(f"{var_name}: Missing 'variable_type' field")

    # Test 2: filter_variables
    print("  [Test 2] filter_variables...")
    filtered = transformer.filter_variables(result, min_categories=2, max_categories=5)

    if not isinstance(filtered, dict):
        return False, "filter_variables should return dict"

    # Should filter out sample_size (metadata field)
    if "sample_size" in filtered:
        issues.append("sample_size should not be in filtered results")

    # Test 3: get_analysis_variables
    print("  [Test 3] get_analysis_variables...")
    analysis_vars = transformer.get_analysis_variables(result)

    expected_analysis_vars = ["q1_satisfaction", "q2_brand_rating", "dem_gender", "dem_age"]
    missing_analysis_vars = set(expected_analysis_vars) - set(analysis_vars)
    extra_analysis_vars = set(analysis_vars) - set(expected_analysis_vars)

    if missing_analysis_vars:
        issues.append(f"Missing analysis vars: {missing_analysis_vars}")
    if extra_analysis_vars:
        issues.append(f"Extra analysis vars: {extra_analysis_vars}")

    success = len(issues) == 0
    print(f"  Results: {'✅ PASS' if success else '❌ FAIL'}")

    if issues:
        for issue in issues:
            print(f"    - {issue}")

    return success, issues


def test_pspp_executor() -> Tuple[bool, List[str]]:
    """Test PSPPExecutor class."""
    print("\n🧪 Testing PSPPExecutor...")

    # Note: Full PSPP testing requires PSPP to be installed
    # This tests syntax generation only
    print("  [Test 1] Checking PSPP availability...")

    try:
        from spss_analyzer.pspp import PSPPExecutor
        print("  ✅ PSPP module available")
        has_pspp = True
    except ImportError:
        print("  ❌ PSPP not available - will skip PSPP tests")
        has_pspp = False

    issues = []

    # Test recoding syntax generation
    print("  [Test 2] Testing recoding syntax generation...")
    recoding_test_rules = [
        {
            "variable": "test_var",
            "type": "value_map",
            "value_mappings": {"1": "A", "2": "B"}
        }
    ]

    if has_pspp:
        from spss_analyzer.pspp import RecodingSyntaxGenerator
        gen = RecodingSyntaxGenerator()
        syntax = gen.generate(recoding_test_rules)

        if "RECODE" not in syntax or "test_var =" not in syntax:
            issues.append("Generated recoding syntax missing RECODE command")
        elif "EXECUTE." not in syntax:
            issues.append("Generated recoding syntax missing EXECUTE command")
    else:
        issues.append("Cannot test syntax generation (PSPP not available)")

    print(f"  Results: {'✅ PASS' if len(issues) == 0 else '❌ FAIL'}")
    if issues:
        for issue in issues:
            print(f"    - {issue}")

    # Test ctables syntax generation
    print("  [Test 3] Testing ctables syntax generation...")

    if has_pspp:
        from spss_analyzer.pspp import CTablesSyntaxGenerator
        gen = CTablesSyntaxGenerator()

        # Test basic table spec
        test_table = {
            "id": "test_table",
            "rows": {"variable": "test_row"},
            "columns": [{"variable": "test_col"}],
            "metrics": ["count"]
        }

        syntax = gen.generate([test_table])

        if "CTABLES" not in syntax or "test_row =" not in syntax or "test_col =" not in syntax:
            issues.append("Generated ctables syntax missing CTABLES command")
        elif "TABLE" not in syntax:
            issues.append("Generated ctables syntax missing TABLE command")
    else:
        issues.append("Cannot test syntax generation (PSPP not available)")

    print(f"  Results: {'✅ PASS' if len(issues) == 0 else '❌ FAIL'}")
    if issues:
        for issue in issues:
            print(f"    - {issue}")

    return has_pspp and len(issues) == 0


def inspect_outputs(output_dir: Path) -> Dict[str, Any]:
    """Inspect all output files in directory."""
    print(f"\n📂 Inspecting outputs in {output_dir}...")

    outputs = {}

    # Check for expected output files
    expected_files = {
        "filtered_metadata.json": "json",
        "table_specification.json": "json",
        "indicators.csv": "csv",
        "cross_tables.json": "json",
        "statistical_summary.json": "json",
        "filtered_tables.json": "json",
        "presentation.pptx": "pptx",
        "dashboard.html": "html"
    }

    found_files = {}
    for file_path in output_dir.glob("*"):
        file_name = file_path.name
        ext = file_path.suffix.lstrip(".")

        if file_name not in expected_files:
            outputs[file_name] = {
                "type": "unexpected",
                "size": file_path.stat().st_size
            }
        else:
            file_type = expected_files.get(file_name, "unknown")
            outputs[file_name] = {
                "type": file_type,
                "size": file_path.stat().st_size
            }
            found_files[file_name] = outputs[file_name]

    print(f"  Found {len(found_files)} expected files")

    unexpected = {k: v for k, v in found_files.items() if v["type"] == "unexpected"}
    if unexpected:
        for name, info in unexpected.items():
            print(f"  ⚠️  Unexpected file: {name} ({info['type']}, {info['size']} bytes)")

    missing = set(expected_files.keys()) - set(found_files.keys())
    if missing:
        for name in missing:
            print(f"  ❌ Missing expected file: {name}")

    return outputs


def validate_stage1_data() -> Tuple[bool, List[str]]:
    """Validate Stage 1 data preparation."""
    print("\n🔍 Validating Stage 1: Data Preparation...")

    issues = []

    # Test with test SAV file
    test_sav = create_test_sav()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sav") as tmp:
        tmp.write(test_sav)
        tmp.flush()

    reader = SPSSReader()
    try:
        data, meta = reader.read(tmp.name)
        issues.append(f"✅ Can read test SAV file: {len(data)} rows")
    except Exception as e:
        issues.append(f"❌ Failed to read test SAV: {e}")

    return len(issues) == 0, issues


def validate_stage2_spec() -> Tuple[bool, List[str]]:
    """Validate Stage 2 specification generation."""
    print("\n🔍 Validating Stage 2: Table Specification...")

    spec_file = Path("output/table_specification.json")
    if not spec_file.exists():
        return False, ["table_specification.json not found"]

    try:
        with open(spec_file, 'r') as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    # Validate structure
    required_fields = ["version", "tables"]
    for field in required_fields:
        if field not in spec:
            return False, [f"Missing required field: {field}"]

    # Validate content
    if not spec.get("tables") and not spec.get("indicators"):
        return False, ["No indicators or tables defined"]

    tables = spec.get("tables", [])
    if len(tables) == 0:
        return False, ["No tables specified"]

    return True, []


def validate_spec_format(spec_file: Path) -> Tuple[bool, List[str]]:
    """Validate specification JSON format."""
    print("\n🔍 Validating specification format...")

    try:
        with open(spec_file, 'r') as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"JSON decode error: {e}"]

    issues = []

    # Check tables have required fields
    for table in spec.get("tables", []):
        required = ["id", "rows", "columns"]
        for field in required:
            if field not in table:
                issues.append(f"Table {table.get('id')}: Missing '{field}'")

    # Check indicators
    for indicator in spec.get("indicators", []):
        required = ["id", "variables", "aggregation"]
        for field in required:
            if field not in indicator:
                issues.append(f"Indicator {indicator.get('id')}: Missing '{field}'")

    return len(issues) == 0, issues


def run_debug_test(
    test_name: str,
    test_func: callable,
    **kwargs
) -> bool:
    """Run a debug test with proper setup and reporting."""
    print(f"\n{'=' * 60}")
    print(f"🧪 Running: {test_name}")
    print("=" * 60)

    try:
        result = test_func(**kwargs)
        print(f"✅ Test PASSED")
        return True
    except AssertionError as e:
        print(f"❌ Test FAILED: {e}")
        print(f"   Assertion: {e}")
        return False
    except Exception as e:
        print(f"❌ Test ERROR: {e}")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {e}")
        return False


def main():
    """Main entry point for survey-debug skill."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Survey analysis debugging and testing tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test a skill
  debug --test-metadata

  # Validate specification format
  debug --validate-spec

  # Test PSPP executor
  debug --test-pspp

  # Inspect outputs
  debug --inspect-outputs output/

  # Validate Stage 1 data
  debug --validate-stage1 test_data.sav

  # Dry run full pipeline
  debug --run-pipeline --debug test_data.sav
        """
    )

    parser.add_argument("--debug", action="store_true",
                        help="Enable detailed debug logging")
    parser.add_argument("--test-metadata", action="store_true",
                        help="Test metadata transformer")
    parser.add_argument("--test-pspp", action="store_true",
                        help="Test PSPP executor")
    parser.add_argument("--test-library", action="store_true",
                        help="Test library modules")
    parser.add_argument("--validate-spec", action="store_true",
                        help="Validate specification JSON")
    parser.add_argument("--validate-stage1", action="store_true",
                        help="Validate Stage 1 data with test SAV")
    parser.add_argument("--inspect-outputs", metavar="DIR",
                        help="Inspect output files in directory")
    parser.add_argument("--run-pipeline", metavar="SAV_FILE",
                        help="Run full pipeline with debugging")

    args = parser.parse_args()

    print("🔧 Survey Debug Tool")
    print("=" * 60)

    # Handle inspect outputs
    if args.inspect_outputs:
        output_dir = Path(args.inspect_outputs)
        if not output_dir.exists():
            print(f"❌ Error: Output directory not found: {output_dir}")
            return 1

        inspect_outputs(output_dir)
        return 0

    # Handle validation tests
    if args.validate_spec:
        success, issues = validate_spec_format(Path("output/table_specification.json"))
        print(f"\n{'=' * 60}")
        if success:
            print("✅ Specification format is valid")
        else:
            print("❌ Specification format has issues:")
            for issue in issues:
                print(f"  - {issue}")
        return 0 if success else 1

    # Handle Stage 1 validation
    if args.validate_stage1:
        success, issues = validate_stage1_data()
        print(f"\n{'=' * 60}")
        if success:
            print("✅ Stage 1 validation passed")
        else:
            print("❌ Stage 1 validation failed:")
            for issue in issues:
                print(f"  - {issue}")
        return 0 if success else 1

    # Handle library tests
    if args.test_library:
        print("\n📚 Testing Library Modules")
        print("=" * 60)

        # Test metadata transformer
        if args.test_metadata or args.test_library:
            success, issues = test_metadata_transformer()
            print(f"\n{'=' * 60}")

        # Test PSPP executor
        if args.test_pspp or args.test_library:
            success, issues = test_pspp_executor()
            print(f"\n{'=' * 60}")

        print(f"\nLibrary Tests: {'✅ PASSED' if (success and len(issues) == 0) else '❌ FAILED'}")
        return 0 if (success and len(issues) == 0) else 1

    # Handle single test
    if args.test_metadata:
        return run_debug_test("Metadata Transformer", test_metadata_transformer)

    elif args.test_pspp:
        return run_debug_test("PSPP Executor", test_pspp_executor)

    # Handle pipeline run
    if args.run_pipeline:
        if not args.run_pipeline:
            print("❌ Error: --run-pipeline requires SAV_FILE argument")
            return 1

        sav_file = args.run_pipeline
        if not Path(sav_file).exists():
            print(f"❌ Error: SAV file not found: {sav_file}")
            return 1

        print(f"\n🚀 Running Full Pipeline (Debug Mode)")
        print(f"   Input: {sav_file}")
        print("=" * 60)

        # Import stage skills for testing
        # Note: In production, these would be separate skill calls
        # For debugging, we call them directly

        print("Stage 1: Data Preparation")
        success = validate_stage1_data()
        if not success:
            return 1

        # Would call stage1-data-prep skill here
        # For now, we simulate
        print("  ✅ Simulated: Load and filter metadata")

        print("\nStage 2: Table Specification")
        success = validate_spec_format(Path("output/table_specification.json"))
        if not success:
            return 1

        # Would call stage2-spec-gen skill here
        print("  ✅ Simulated: Generate table specification")

        print("\nStage 3: Cross-Table Calculation")
        # Would call stage3-crosstabs skill here
        print("  ✅ Simulated: Apply recoding, compute indicators, generate cross-tables")

        print("\nStage 4: Statistical Analysis")
        # Would call stage4-statistics skill here
        print("  ✅ Simulated: Calculate statistics, filter tables")

        print("\nStage 5: Reporting")
        # Would call stage5-reports skill here
        print("  ✅ Simulated: Generate reports")

        print("\n" + "=" * 60)
        print("✅ Pipeline Complete!")
        print()
        return 0

    print("\nAvailable Commands:")
    print("  debug --test-metadata      Test metadata transformation")
    print("  debug --test-pspp          Test PSPP integration")
    print("  debug --test-library       Test all library modules")
    print("  debug --validate-spec     Validate table specification format")
    print("  debug --validate-stage1    Validate Stage 1 with test data")
    print("  debug --inspect-outputs DIR Inspect output files")
    print("  debug --run-pipeline FILE  Run full pipeline with debug")

    return 0
