"""
Tests for survey_analyzer.specification module.

Tests table specification schema with new structure.
"""

import pytest


# ============================================================================
# Enum Tests
# ============================================================================

class TestSpecificationEnums:
    """Test specification module enums."""

    def test_variable_suffix_enum(self):
        """Test VariableSuffix enum values."""
        from survey_analyzer.specification import VariableSuffix
        assert VariableSuffix.RAW.value == "_raw"
        assert VariableSuffix.BIN.value == "_bin"
        assert VariableSuffix.CAT.value == "_cat"
        assert VariableSuffix.T2B.value == "_t2b"
        assert VariableSuffix.B2B.value == "_b2b"
        assert VariableSuffix.NPS.value == "_nps"
        assert VariableSuffix.SCA.value == "_sca"
        assert VariableSuffix.IDX.value == "_idx"
        assert VariableSuffix.Z.value == "_z"
        assert VariableSuffix.PCT.value == "_pct"

    def test_question_type_enum(self):
        """Test QuestionType enum values."""
        from survey_analyzer.specification import QuestionType
        assert QuestionType.SINGLE_CHOICE.value == "Single Choice"
        assert QuestionType.MULTIPLE_CHOICE.value == "Multiple Choice"
        assert QuestionType.MATRIX.value == "Matrix"
        assert QuestionType.RATING_SCALE.value == "Rating Scale"
        assert QuestionType.NUMERIC_INPUT.value == "Numeric Input"
        assert QuestionType.OPEN_ENDED.value == "Open Ended"

    def test_tabulation_type_enum(self):
        """Test TabulationType enum values."""
        from survey_analyzer.specification import TabulationType
        assert TabulationType.CATEGORICAL.value == "categorical"
        assert TabulationType.SCALAR.value == "scalar"

    def test_metric_type_enum(self):
        """Test MetricType enum values."""
        from survey_analyzer.specification import MetricType
        assert MetricType.COLUMN_PERCENT.value == "column_percent"
        assert MetricType.DESCRIPTIVE_STATISTICS.value == "descriptive_statistics"


# ============================================================================
# Schema Classes Tests
# ============================================================================

class TestQuestionRef:
    """Test QuestionRef class."""

    def test_question_ref_creation(self):
        """Test QuestionRef creation."""
        from survey_analyzer.specification import QuestionRef, QuestionType
        ref = QuestionRef(
            code="Q1",
            label="Gender",
            type=QuestionType.SINGLE_CHOICE
        )

        assert ref.code == "Q1"
        assert ref.label == "Gender"
        assert ref.type == QuestionType.SINGLE_CHOICE

    def test_question_ref_to_dict(self):
        """Test QuestionRef.to_dict() method."""
        from survey_analyzer.specification import QuestionRef, QuestionType
        ref = QuestionRef(
            code="Q1",
            label="Gender",
            type=QuestionType.SINGLE_CHOICE
        )
        ref_dict = ref.to_dict()

        assert ref_dict["code"] == "Q1"
        assert ref_dict["label"] == "Gender"
        assert ref_dict["type"] == "Single Choice"

    def test_question_ref_from_dict(self):
        """Test QuestionRef.from_dict() method."""
        from survey_analyzer.specification import QuestionRef
        ref_dict = {
            "code": "Q1",
            "label": "Gender",
            "type": "Single Choice"
        }
        ref = QuestionRef.from_dict(ref_dict)

        assert ref.code == "Q1"
        assert ref.label == "Gender"


class TestBaseVariable:
    """Test BaseVariable class."""

    def test_base_variable_creation(self):
        """Test BaseVariable creation."""
        from survey_analyzer.specification import BaseVariable, VariableSuffix
        var = BaseVariable(
            name="Q1_GENDER_raw",
            label="Gender (Raw)",
            suffix=VariableSuffix.RAW
        )

        assert var.name == "Q1_GENDER_raw"
        assert var.label == "Gender (Raw)"
        assert var.suffix == VariableSuffix.RAW

    def test_base_variable_with_values(self):
        """Test BaseVariable with values mapping."""
        from survey_analyzer.specification import BaseVariable, VariableSuffix
        var = BaseVariable(
            name="Q1_GENDER_cat",
            label="Gender (Categorized)",
            suffix=VariableSuffix.CAT,
            values={"1": "Male", "2": "Female"}
        )

        assert var.values == {"1": "Male", "2": "Female"}

    def test_base_variable_is_categorical(self):
        """Test BaseVariable.is_categorical() method."""
        from survey_analyzer.specification import BaseVariable, VariableSuffix
        var_cat = BaseVariable(
            name="Q1_GENDER_cat",
            label="Gender",
            suffix=VariableSuffix.CAT
        )
        var_sca = BaseVariable(
            name="AGE_sca",
            label="Age",
            suffix=VariableSuffix.SCA
        )

        assert var_cat.is_categorical() is True
        assert var_sca.is_categorical() is False

    def test_base_variable_is_scalar(self):
        """Test BaseVariable.is_scalar() method."""
        from survey_analyzer.specification import BaseVariable, VariableSuffix
        var_cat = BaseVariable(
            name="Q1_GENDER_cat",
            label="Gender",
            suffix=VariableSuffix.CAT
        )
        var_sca = BaseVariable(
            name="AGE_sca",
            label="Age",
            suffix=VariableSuffix.SCA
        )

        assert var_cat.is_scalar() is False
        assert var_sca.is_scalar() is True


class TestTabulationStats:
    """Test TabulationStats class."""

    def test_categorical_stats(self):
        """Test TabulationStats for categorical type."""
        from survey_analyzer.specification import TabulationStats, TabulationType, MetricType
        stats = TabulationStats(
            type=TabulationType.CATEGORICAL,
            metric=MetricType.COLUMN_PERCENT
        )

        assert stats.type == TabulationType.CATEGORICAL
        assert stats.metric == MetricType.COLUMN_PERCENT

    def test_scalar_stats(self):
        """Test TabulationStats for scalar type."""
        from survey_analyzer.specification import TabulationStats, TabulationType, MetricType
        stats = TabulationStats(
            type=TabulationType.SCALAR,
            metric=MetricType.DESCRIPTIVE_STATISTICS
        )

        assert stats.type == TabulationType.SCALAR
        assert stats.metric == MetricType.DESCRIPTIVE_STATISTICS

    def test_stats_with_explicit(self):
        """Test TabulationStats with explicit values."""
        from survey_analyzer.specification import TabulationStats, TabulationType, MetricType
        stats = TabulationStats(
            type=TabulationType.CATEGORICAL,
            metric=MetricType.COLUMN_PERCENT,
            explicit=["1", "2"]
        )

        assert stats.explicit == ["1", "2"]


class TestIndicatorSpec:
    """Test IndicatorSpec class."""

    def test_indicator_creation(self):
        """Test IndicatorSpec creation."""
        from survey_analyzer.specification import (
            IndicatorSpec,
            QuestionRef,
            QuestionType,
            BaseVariable,
            VariableSuffix,
            TabulationStats,
            TabulationType,
            MetricType
        )
        indicator = IndicatorSpec(
            indicator_code="Q1_GENDER",
            indicator_label="Gender",
            questionnaire_questions=[
                QuestionRef(code="Q1", label="Gender", type=QuestionType.SINGLE_CHOICE)
            ],
            base_variables=[
                BaseVariable(name="Q1_GENDER_raw", label="Gender (Raw)", suffix=VariableSuffix.RAW)
            ],
            tabulation_statistics=TabulationStats(
                type=TabulationType.CATEGORICAL,
                metric=MetricType.COLUMN_PERCENT
            )
        )

        assert indicator.indicator_code == "Q1_GENDER"
        assert len(indicator.questionnaire_questions) == 1
        assert len(indicator.base_variables) == 1

    def test_indicator_auto_detect_stats(self):
        """Test IndicatorSpec auto-detects stats from base variable."""
        from survey_analyzer.specification import (
            IndicatorSpec,
            BaseVariable,
            VariableSuffix
        )
        indicator = IndicatorSpec(
            indicator_code="Q1_GENDER",
            indicator_label="Gender",
            base_variables=[
                BaseVariable(name="Q1_GENDER_raw", label="Gender (Raw)", suffix=VariableSuffix.RAW)
            ]
        )

        # Should auto-detect categorical stats
        assert indicator.tabulation_statistics is not None
        assert indicator.tabulation_statistics.type.value == "categorical"

    def test_indicator_get_scenario_cat_single(self):
        """Test get_scenario_type returns cat_single."""
        from survey_analyzer.specification import (
            IndicatorSpec,
            BaseVariable,
            VariableSuffix
        )
        indicator = IndicatorSpec(
            indicator_code="Q1_GENDER",
            indicator_label="Gender",
            base_variables=[
                BaseVariable(name="Q1_GENDER_raw", label="Gender (Raw)", suffix=VariableSuffix.RAW)
            ]
        )

        assert indicator.get_scenario_type() == "cat_single"

    def test_indicator_get_scenario_cat_multi(self):
        """Test get_scenario_type returns cat_multi."""
        from survey_analyzer.specification import (
            IndicatorSpec,
            BaseVariable,
            VariableSuffix
        )
        indicator = IndicatorSpec(
            indicator_code="BRAND_AWARENESS",
            indicator_label="Brand Awareness",
            base_variables=[
                BaseVariable(name="BRAND_A_bin", label="Brand A", suffix=VariableSuffix.BIN),
                BaseVariable(name="BRAND_B_bin", label="Brand B", suffix=VariableSuffix.BIN)
            ]
        )

        assert indicator.get_scenario_type() == "cat_multi"

    def test_indicator_get_scenario_scalar_single(self):
        """Test get_scenario_type returns scalar_single."""
        from survey_analyzer.specification import (
            IndicatorSpec,
            BaseVariable,
            VariableSuffix
        )
        indicator = IndicatorSpec(
            indicator_code="SAT_OVERALL",
            indicator_label="Overall Satisfaction",
            base_variables=[
                BaseVariable(name="SAT_OVERALL_sca", label="Satisfaction", suffix=VariableSuffix.SCA)
            ]
        )

        assert indicator.get_scenario_type() == "scalar_single"


class TestTableSpecification:
    """Test TableSpecification class."""

    def test_spec_creation(self):
        """Test TableSpecification creation."""
        from survey_analyzer.specification import (
            TableSpecification,
            IndicatorSpec,
            BaseVariable,
            VariableSuffix
        )
        row_ind = IndicatorSpec(
            indicator_code="Q2_SAT",
            indicator_label="Satisfaction",
            base_variables=[
                BaseVariable(name="Q2_SAT_raw", label="Satisfaction", suffix=VariableSuffix.RAW)
            ]
        )
        col_ind = IndicatorSpec(
            indicator_code="Q1_GENDER",
            indicator_label="Gender",
            base_variables=[
                BaseVariable(name="Q1_GENDER_raw", label="Gender", suffix=VariableSuffix.RAW)
            ]
        )

        spec = TableSpecification(
            metadata={"spec_id": "test_spec", "project_id": "test_project"},
            filter_clause={},
            row_indicators=[row_ind],
            column_indicators=[col_ind]
        )

        assert len(spec.row_indicators) == 1
        assert len(spec.column_indicators) == 1

    def test_spec_validation(self):
        """Test TableSpecification.validate() method."""
        from survey_analyzer.specification import (
            TableSpecification,
            IndicatorSpec,
            BaseVariable,
            VariableSuffix,
            TabulationStats,
            TabulationType,
            MetricType
        )
        row_ind = IndicatorSpec(
            indicator_code="Q2_SAT",
            indicator_label="Satisfaction",
            base_variables=[
                BaseVariable(name="Q2_SAT_raw", label="Satisfaction", suffix=VariableSuffix.RAW)
            ],
            tabulation_statistics=TabulationStats(
                type=TabulationType.CATEGORICAL,
                metric=MetricType.COLUMN_PERCENT
            )
        )
        col_ind = IndicatorSpec(
            indicator_code="Q1_GENDER",
            indicator_label="Gender",
            base_variables=[
                BaseVariable(name="Q1_GENDER_raw", label="Gender", suffix=VariableSuffix.RAW)
            ],
            tabulation_statistics=TabulationStats(
                type=TabulationType.CATEGORICAL,
                metric=MetricType.COLUMN_PERCENT
            )
        )

        spec = TableSpecification(
            metadata={"spec_id": "test_spec", "project_id": "test_project"},
            filter_clause={},
            row_indicators=[row_ind],
            column_indicators=[col_ind]
        )

        errors = spec.validate()
        assert len(errors) == 0

    def test_spec_get_indicator_by_code(self):
        """Test get_indicator_by_code() method."""
        from survey_analyzer.specification import (
            TableSpecification,
            IndicatorSpec,
            BaseVariable,
            VariableSuffix
        )
        row_ind = IndicatorSpec(
            indicator_code="Q2_SAT",
            indicator_label="Satisfaction",
            base_variables=[
                BaseVariable(name="Q2_SAT_raw", label="Satisfaction", suffix=VariableSuffix.RAW)
            ]
        )

        spec = TableSpecification(
            metadata={"spec_id": "test_spec"},
            filter_clause={},
            row_indicators=[row_ind],
            column_indicators=[]
        )

        found = spec.get_indicator_by_code("Q2_SAT")
        assert found is not None
        assert found.indicator_code == "Q2_SAT"

        not_found = spec.get_indicator_by_code("NONEXISTENT")
        assert not_found is None


# ============================================================================
# Convenience Functions Tests
# ============================================================================

class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_create_empty_spec(self):
        """Test create_empty_spec() function."""
        from survey_analyzer.specification import create_empty_spec, TableSpecification
        spec = create_empty_spec()

        assert isinstance(spec, TableSpecification)
        assert "spec_id" in spec.metadata


# ============================================================================
# Module Level Tests
# ============================================================================

class TestSpecificationModule:
    """Test specification module imports."""

    def test_import_schema_classes(self):
        """Test schema classes can be imported."""
        from survey_analyzer.specification import (
            TableSpecification,
            IndicatorSpec,
            BaseVariable,
            QuestionRef,
            TabulationStats
        )
        assert TableSpecification is not None
        assert IndicatorSpec is not None
        assert BaseVariable is not None

    def test_import_enums(self):
        """Test enums can be imported."""
        from survey_analyzer.specification import (
            VariableSuffix,
            QuestionType,
            TabulationType,
            MetricType
        )
        assert VariableSuffix is not None
        assert QuestionType is not None

    def test_module_exports(self):
        """Test module exports expected classes."""
        from survey_analyzer import specification
        # Check key classes are accessible
        assert hasattr(specification, "TableSpecification")
        assert hasattr(specification, "IndicatorSpec")
        assert hasattr(specification, "BaseVariable")
        assert hasattr(specification, "VariableSuffix")
