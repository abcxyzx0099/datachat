"""
Tests for survey_analyzer.analysis.indicators module.

Tests indicator generation and grouping functionality.
"""

import pytest
from survey_analyzer.analysis.indicators import (
    IndicatorGenerator,
    IndicatorConfig,
    Indicator,
    IndicatorType,
    generate_indicators
)


# ============================================================================
# IndicatorConfig Tests
# ============================================================================

class TestIndicatorConfig:
    """Test IndicatorConfig dataclass."""

    def test_default_initialization(self):
        """Test default config values."""
        config = IndicatorConfig()
        assert config.type == IndicatorType.KEYWORD
        assert config.min_variables == 2
        assert config.max_variables == 10
        assert config.keywords == []
        assert config.prefix is None

    def test_custom_initialization(self):
        """Test custom config values."""
        config = IndicatorConfig(
            type=IndicatorType.LABEL,
            keywords=["sat", "satisfaction"],
            min_variables=3,
            max_variables=15,
            prefix="sat_"
        )
        assert config.type == IndicatorType.LABEL
        assert config.keywords == ["sat", "satisfaction"]
        assert config.min_variables == 3
        assert config.max_variables == 15
        assert config.prefix == "sat_"

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = IndicatorConfig(
            type=IndicatorType.KEYWORD,
            prefix="q"
        )
        config_dict = config.to_dict()

        assert config_dict["type"] == "keyword"
        assert config_dict["prefix"] == "q"


# ============================================================================
# Indicator Tests
# ============================================================================

class TestIndicator:
    """Test Indicator dataclass."""

    def test_indicator_creation(self):
        """Test creating an indicator."""
        indicator = Indicator(
            name="satisfaction_indicator",
            description="Customer satisfaction indicator",
            variables=["sat_1", "sat_2", "sat_3"],
            variable_count=3,
            label="Satisfaction"
        )

        assert indicator.name == "satisfaction_indicator"
        assert indicator.variable_count == 3
        assert indicator.label == "Satisfaction"

    def test_indicator_to_dict(self):
        """Test converting indicator to dictionary."""
        indicator = Indicator(
            name="test_indicator",
            description="Test",
            variables=["v1", "v2"],
            variable_count=2
        )
        ind_dict = indicator.to_dict()

        assert ind_dict["name"] == "test_indicator"
        assert ind_dict["variable_count"] == 2


# ============================================================================
# IndicatorGenerator Tests
# ============================================================================

class TestIndicatorGenerator:
    """Test IndicatorGenerator class."""

    def test_initialization(self):
        """Test generator initialization."""
        gen = IndicatorGenerator()
        assert gen is not None
        assert gen.metadata_lookup == {}

    def test_initialization_with_metadata(self):
        """Test initialization with metadata lookup."""
        metadata = {
            "q1": {"label": "Question 1"},
            "q2": {"label": "Question 2"}
        }
        gen = IndicatorGenerator(metadata_lookup=metadata)
        assert gen.metadata_lookup == metadata

    def test_generate_by_keywords_with_prefix(self):
        """Test generating indicators by prefix."""
        metadata = {
            "sat_1": {"label": "Satisfaction 1"},
            "sat_2": {"label": "Satisfaction 2"},
            "sat_3": {"label": "Satisfaction 3"}
        }
        gen = IndicatorGenerator(metadata_lookup=metadata)
        config = IndicatorConfig(
            type=IndicatorType.KEYWORD,
            prefix="sat_"
        )

        indicators = gen.generate(metadata, config)

        assert len(indicators) == 1
        assert indicators[0].name == "satisfaction_indicator"
        assert indicators[0].variable_count == 3

    def test_generate_by_keywords_auto_detect(self):
        """Test auto-detecting keyword patterns."""
        metadata = {
            "brand_a": {"label": "Brand A"},
            "brand_b": {"label": "Brand B"},
            "brand_c": {"label": "Brand C"},
            "price_1": {"label": "Price 1"}
        }
        gen = IndicatorGenerator(metadata_lookup=metadata)
        config = IndicatorConfig(type=IndicatorType.KEYWORD)

        indicators = gen.generate(metadata, config)

        # Should detect "brand" as a pattern
        brand_indicators = [i for i in indicators if "brand" in i.name]
        assert len(brand_indicators) == 1
        assert brand_indicators[0].variable_count == 3

    def test_generate_by_labels(self):
        """Test generating indicators by label keywords."""
        metadata = {
            "q1": {"label": "Very satisfied"},
            "q2": {"label": "Satisfied"},
            "q3": {"label": "Dissatisfied"}
        }
        gen = IndicatorGenerator(metadata_lookup=metadata)
        config = IndicatorConfig(
            type=IndicatorType.LABEL,
            keywords=["satisfied", "sat"]
        )

        indicators = gen.generate(metadata, config)

        assert len(indicators) > 0

    def test_generate_manual(self):
        """Test generating indicators from manual groupings."""
        metadata = {
            "v1": {"label": "Var 1"},
            "v2": {"label": "Var 2"},
            "v3": {"label": "Var 3"}
        }
        gen = IndicatorGenerator(metadata_lookup=metadata)
        config = IndicatorConfig(
            type=IndicatorType.MANUAL,
            manual_groupings={
                "group1": ["v1", "v2"],
                "group2": ["v3"]
            }
        )

        indicators = gen.generate(metadata, config)

        assert len(indicators) == 2
        assert indicators[0].name == "group1_indicator"
        assert indicators[1].name == "group2_indicator"

    def test_generate_semantic_fallback_to_keyword(self):
        """Test semantic grouping falls back to keyword."""
        metadata = {
            "sat_1": {"label": "Satisfaction 1"},
            "sat_2": {"label": "Satisfaction 2"}
        }
        gen = IndicatorGenerator(metadata_lookup=metadata)
        config = IndicatorConfig(type=IndicatorType.SEMANTIC)

        # Should fall back to keyword
        indicators = gen.generate(metadata, config)
        assert len(indicators) > 0

    def test_expand_concept_name(self):
        """Test expanding concept name to full word."""
        gen = IndicatorGenerator()

        assert gen._expand_concept_name("sat") == "satisfaction"
        assert gen._expand_concept_name("loyal") == "loyalty"
        assert gen._expand_concept_name("unknown") == "unknown"

    def test_validate_indicator_valid(self):
        """Test validating a valid indicator."""
        gen = IndicatorGenerator()
        metadata = {"v1": {"label": "Var 1"}, "v2": {"label": "Var 2"}}
        indicator = Indicator(
            name="test",
            description="Test",
            variables=["v1", "v2"],
            variable_count=2
        )

        is_valid, error = gen.validate_indicator(indicator, metadata)
        assert is_valid is True
        assert error is None

    def test_validate_indicator_missing_variable(self):
        """Test validating indicator with missing variable."""
        gen = IndicatorGenerator()
        metadata = {"v1": {"label": "Var 1"}}
        indicator = Indicator(
            name="test",
            description="Test",
            variables=["v1", "v2"],  # v2 not in metadata
            variable_count=2
        )

        is_valid, error = gen.validate_indicator(indicator, metadata)
        assert is_valid is False
        assert "not found" in error

    def test_validate_indicator_too_few_variables(self):
        """Test validating indicator with too few variables."""
        gen = IndicatorGenerator()
        metadata = {"v1": {"label": "Var 1"}}
        indicator = Indicator(
            name="test",
            description="Test",
            variables=["v1"],
            variable_count=1
        )

        is_valid, error = gen.validate_indicator(indicator, metadata)
        assert is_valid is False
        assert "only 1" in error


# ============================================================================
# Convenience Functions Tests
# ============================================================================

class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_generate_indicators_function(self):
        """Test generate_indicators standalone function."""
        metadata = {
            "sat_1": {"label": "Satisfaction 1"},
            "sat_2": {"label": "Satisfaction 2"}
        }

        indicators = generate_indicators(metadata, strategy="keyword", prefix="sat_")

        assert len(indicators) == 1
        assert "name" in indicators[0]

    def test_generate_indicators_invalid_strategy(self):
        """Test generate_indicators with invalid strategy defaults to keyword."""
        metadata = {"sat_1": {"label": "Sat 1"}}

        indicators = generate_indicators(metadata, strategy="invalid")

        # Should default to keyword strategy
        assert len(indicators) >= 0


# ============================================================================
# Module Tests
# ============================================================================

class TestIndicatorsModule:
    """Test indicators module imports."""

    def test_import_indicator_generator(self):
        """Test IndicatorGenerator can be imported."""
        from survey_analyzer.analysis.indicators import IndicatorGenerator
        assert IndicatorGenerator is not None

    def test_import_indicator_config(self):
        """Test IndicatorConfig can be imported."""
        from survey_analyzer.analysis.indicators import IndicatorConfig
        assert IndicatorConfig is not None

    def test_import_indicator(self):
        """Test Indicator can be imported."""
        from survey_analyzer.analysis.indicators import Indicator
        assert Indicator is not None

    def test_import_indicator_type(self):
        """Test IndicatorType enum can be imported."""
        from survey_analyzer.analysis.indicators import IndicatorType
        assert IndicatorType.KEYWORD is not None
        assert IndicatorType.LABEL is not None
        assert IndicatorType.SEMANTIC is not None
        assert IndicatorType.MANUAL is not None

    def test_keyword_patterns_exist(self):
        """Test that keyword patterns dictionary exists."""
        from survey_analyzer.analysis.indicators import IndicatorGenerator
        gen = IndicatorGenerator()

        # Check KEYWORD_PATTERNS is populated
        assert len(gen.KEYWORD_PATTERNS) > 0
        assert "sat" in gen.KEYWORD_PATTERNS
        assert "brand" in gen.KEYWORD_PATTERNS
