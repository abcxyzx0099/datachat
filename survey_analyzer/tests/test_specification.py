"""
Tests for survey_analyzer.specification module.

Tests table specification schema and validation.
"""

import pytest


# ============================================================================
# Enum Tests
# ============================================================================

class TestSpecificationEnums:
    """Test specification module enums."""

    def test_metric_type_enum(self):
        """Test MetricType enum values."""
        from survey_analyzer.specification import MetricType
        assert MetricType.COUNT.value == "count"
        assert MetricType.ROW_PERCENT.value == "row_percent"
        assert MetricType.MEAN.value == "mean"

    def test_aggregation_type_enum(self):
        """Test AggregationType enum values."""
        from survey_analyzer.specification import AggregationType
        assert AggregationType.MEAN.value == "mean"
        assert AggregationType.SUM.value == "sum"

    def test_table_type_enum(self):
        """Test TableType enum values."""
        from survey_analyzer.specification import TableType
        assert TableType.CROSSTAB.value == "crosstab"
        assert TableType.FREQUENCY.value == "frequency"

    def test_variable_source_enum(self):
        """Test VariableSource enum values."""
        from survey_analyzer.specification import VariableSource
        assert VariableSource.RAW.value == "raw"
        assert VariableSource.RECODED.value == "recoded"


# ============================================================================
# Schema Classes Tests
# ============================================================================

class TestTableSpecificationDocument:
    """Test TableSpecificationDocument class."""

    def test_default_initialization(self):
        """Test TableSpecificationDocument with default values."""
        from survey_analyzer.specification import TableSpecificationDocument
        spec = TableSpecificationDocument()

        assert spec.version == "1.0"
        assert spec.generated_at is not None
        assert spec.tables == []
        assert spec.indicators == []

    def test_initialization_with_values(self):
        """Test TableSpecificationDocument with custom values."""
        from survey_analyzer.specification import (
            TableSpecificationDocument,
            TableSpecification,
            TableDimension,
            TableMetric,
            MetricType
        )

        table = TableSpecification(
            id="tab_001",
            title="Test Table",
            rows=TableDimension(variable="q1"),
            columns=TableDimension(variable="gender"),
            metrics=[TableMetric(MetricType.COUNT)]
        )

        spec = TableSpecificationDocument(
            version="2.0",
            source_file="test.sav",
            tables=[table]
        )

        assert spec.version == "2.0"
        assert spec.source_file == "test.sav"
        assert len(spec.tables) == 1

    def test_to_dict_method(self):
        """Test TableSpecificationDocument.to_dict() method."""
        from survey_analyzer.specification import TableSpecificationDocument
        spec = TableSpecificationDocument(version="1.0")
        spec_dict = spec.to_dict()

        assert "metadata" in spec_dict
        assert spec_dict["metadata"]["version"] == "1.0"
        assert "tables" in spec_dict
        assert "output_settings" in spec_dict

    def test_from_dict_method(self):
        """Test TableSpecificationDocument.from_dict() method."""
        from survey_analyzer.specification import TableSpecificationDocument

        spec_dict = {
            "metadata": {"version": "1.0", "source_file": "test.sav"},
            "global_recodings": [],
            "indicators": [],
            "tables": [],
            "output_settings": {
                "significance_threshold": 0.05,
                "min_cramers_v": 0.1,
                "min_sample_size": 30,
                "include_powerpoint": True,
                "include_html_dashboard": True,
                "include_csv_export": True,
                "max_tables_ppt": 20,
                "dashboard_title": "Survey Analysis Results",
                "include_charts": True,
                "chart_type": "heatmap",
                "output_directory": "output"
            },
            "notes": None
        }

        spec = TableSpecificationDocument.from_dict(spec_dict)

        assert spec.version == "1.0"
        assert spec.source_file == "test.sav"


class TestRecodingRule:
    """Test RecodingRule class."""

    def test_value_map_recoding(self):
        """Test RecodingRule with value mappings."""
        from survey_analyzer.specification import RecodingRule, RecodingType
        rule = RecodingRule(
            variable="q1",
            type=RecodingType.VALUE_MAP,
            value_mappings={"1": "Yes", "2": "No"}
        )

        assert rule.variable == "q1"
        assert rule.type == RecodingType.VALUE_MAP
        assert rule.value_mappings == {"1": "Yes", "2": "No"}

    def test_range_map_recoding(self):
        """Test RecodingRule with range mappings."""
        from survey_analyzer.specification import (
            RecodingRule,
            RecodingType,
            RangeMapping
        )
        rule = RecodingRule(
            variable="age",
            type=RecodingType.RANGE_MAP,
            range_mappings=[
                RangeMapping(min_value=0, max_value=30, recoded_value="Young"),
                RangeMapping(min_value=31, max_value=50, recoded_value="Middle"),
                RangeMapping(min_value=51, max_value=None, recoded_value="Senior"),
            ]
        )

        assert rule.variable == "age"
        assert len(rule.range_mappings) == 3

    def test_recoding_to_dict(self):
        """Test RecodingRule.to_dict() method."""
        from survey_analyzer.specification import RecodingRule, RecodingType
        rule = RecodingRule(
            variable="q1",
            type=RecodingType.VALUE_MAP,
            value_mappings={"1": "Yes"}
        )
        rule_dict = rule.to_dict()

        assert rule_dict["variable"] == "q1"
        assert rule_dict["type"] == "value_map"


class TestIndicator:
    """Test Indicator class."""

    def test_indicator_creation(self):
        """Test Indicator class creation."""
        from survey_analyzer.specification import (
            Indicator,
            VariableRef,
            VariableSource,
            AggregationType
        )
        indicator = Indicator(
            id="ind_001",
            name="Customer Satisfaction",
            variables=[
                VariableRef(name="q1", source=VariableSource.RAW),
                VariableRef(name="q2", source=VariableSource.RAW),
            ],
            aggregation=AggregationType.MEAN
        )

        assert indicator.id == "ind_001"
        assert indicator.name == "Customer Satisfaction"
        assert len(indicator.variables) == 2


# ============================================================================
# Validation Function Tests
# ============================================================================

class TestValidationFunctions:
    """Test validation convenience functions."""

    def test_create_empty_spec(self):
        """Test create_empty_spec() function."""
        from survey_analyzer.specification import create_empty_spec
        spec = create_empty_spec(source_file="test.sav")

        assert spec.version == "1.0"
        assert spec.source_file == "test.sav"

    def test_validate_spec_structure_valid(self):
        """Test validate_spec_structure() with valid spec."""
        from survey_analyzer.specification import validate_spec_structure

        valid_spec = {
            "metadata": {"version": "1.0"},
            "tables": [
                {"id": "tab1", "title": "Table 1", "type": "crosstab",
                 "rows": {"variable": "q1"}, "columns": {"variable": "q2"}}
            ],
            "output_settings": {"significance_threshold": 0.05}
        }

        errors = validate_spec_structure(valid_spec)
        assert len(errors) == 0

    def test_validate_spec_structure_missing_metadata(self):
        """Test validate_spec_structure() with missing metadata."""
        from survey_analyzer.specification import validate_spec_structure

        invalid_spec = {
            "tables": []
        }

        errors = validate_spec_structure(invalid_spec)
        assert len(errors) > 0
        assert any("metadata" in str(e) for e in errors)

    def test_validate_spec_structure_invalid_significance(self):
        """Test validate_spec_structure() with invalid significance threshold."""
        from survey_analyzer.specification import validate_spec_structure

        invalid_spec = {
            "metadata": {"version": "1.0"},
            "tables": [],
            "output_settings": {"significance_threshold": 1.5}  # Invalid: > 1
        }

        errors = validate_spec_structure(invalid_spec)
        assert len(errors) > 0
        assert any("significance_threshold" in str(e) for e in errors)


# ============================================================================
# Module Level Tests
# ============================================================================

class TestSpecificationModule:
    """Test specification module imports."""

    def test_import_schema_classes(self):
        """Test schema classes can be imported."""
        from survey_analyzer.specification import (
            TableSpecificationDocument,
            TableSpecification,
            Indicator,
            RecodingRule
        )
        assert TableSpecificationDocument is not None
        assert TableSpecification is not None

    def test_import_validator_classes(self):
        """Test validator classes can be imported."""
        from survey_analyzer.specification import (
            TableSpecificationValidator,
            validate_specification,
            is_valid_specification
        )
        assert TableSpecificationValidator is not None
        assert callable(validate_specification)

    def test_module_exports(self):
        """Test module exports expected classes."""
        from survey_analyzer import specification
        # Check key classes are accessible
        assert hasattr(specification, "TableSpecificationDocument")
        assert hasattr(specification, "validate_specification")
        assert hasattr(specification, "create_empty_spec")
