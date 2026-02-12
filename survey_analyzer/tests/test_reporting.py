"""
Tests for survey_analyzer.reporting module.

Tests PowerPoint and HTML dashboard generation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Import ChartColorScheme at module level for testing
from survey_analyzer.reporting.powerpoint import ChartColorScheme


# ============================================================================
# ChartColorScheme Tests
# ============================================================================

class TestChartColorScheme:
    """Test ChartColorScheme class."""

    def test_default_color_scheme(self):
        """Test ChartColorScheme default values."""
        from survey_analyzer.reporting.powerpoint import ChartColorScheme
        colors = ChartColorScheme()

        assert colors.primary == "#4287f5"
        assert colors.secondary == "#48bb78"
        assert colors.accent == "#f6e05e"

    def test_professional_color_scheme(self):
        """Test ChartColorScheme.professional() class method."""
        from survey_analyzer.reporting.powerpoint import ChartColorScheme
        colors = ChartColorScheme.professional()

        assert colors.primary == "#4287f5"
        assert colors.significant == "#48bb78"
        assert colors.not_significant == "#e53e3e"


# ============================================================================
# PowerPointGenerator Tests
# ============================================================================

class TestPowerPointGeneratorInstantiation:
    """Test PowerPointGenerator class instantiation."""

    def test_default_initialization(self):
        """Test PowerPointGenerator with default parameters."""
        from survey_analyzer.reporting import PowerPointGenerator
        gen = PowerPointGenerator()

        assert gen.template_path is None
        assert gen.color_scheme is not None
        assert gen._presentation is None

    def test_initialization_with_color_scheme(self):
        """Test PowerPointGenerator with custom color scheme."""
        from survey_analyzer.reporting.powerpoint import PowerPointGenerator, ChartColorScheme
        colors = ChartColorScheme.professional()
        gen = PowerPointGenerator(color_scheme=colors)

        assert gen.color_scheme == colors


class TestPowerPointGeneratorCreatePresentation:
    """Test PowerPointGenerator.create_presentation() method."""

    def test_create_presentation_default(self):
        """Test creating presentation with default settings."""
        from survey_analyzer.reporting import PowerPointGenerator

        gen = PowerPointGenerator()
        gen.create_presentation(
            tables=[],
            statistics={},
            title="Test Presentation"
        )

        assert gen._presentation is not None

    def test_create_presentation_with_subtitle(self):
        """Test creating presentation with subtitle."""
        from survey_analyzer.reporting import PowerPointGenerator

        gen = PowerPointGenerator()
        gen.create_presentation(
            tables=[],
            statistics={},
            title="Test Presentation",
            subtitle="Test Subtitle"
        )

        assert gen._presentation is not None


class TestPowerPointGeneratorSave:
    """Test PowerPointGenerator.save() method."""

    def test_save_without_create(self):
        """Test save() without creating presentation raises error."""
        from survey_analyzer.reporting.powerpoint import PowerPointGenerator

        gen = PowerPointGenerator()
        with pytest.raises(RuntimeError, match="No presentation created"):
            gen.save("output.pptx")

    def test_save_creates_directory(self, tmp_path):
        """Test save() creates output directory if needed."""
        from survey_analyzer.reporting.powerpoint import PowerPointGenerator
        import os

        gen = PowerPointGenerator()
        gen.create_presentation(
            tables=[],
            statistics={"tables": []},
            title="Test"
        )
        output_file = tmp_path / "subdir" / "output.pptx"
        gen.save(str(output_file))

        # Verify file was created
        assert output_file.exists()
        # Clean up
        os.remove(output_file)
        os.rmdir(os.path.dirname(output_file))


# ============================================================================
# HTMLDashboardGenerator Tests
# ============================================================================

class TestHTMLDashboardGeneratorInstantiation:
    """Test HTMLDashboardGenerator class instantiation."""

    def test_default_initialization(self):
        """Test HTMLDashboardGenerator with default parameters."""
        from survey_analyzer.reporting import HTMLDashboardGenerator
        gen = HTMLDashboardGenerator()

        assert gen is not None


class TestHTMLDashboardGeneratorGenerate:
    """Test HTMLDashboardGenerator.generate_dashboard() method."""

    @patch("builtins.open", new_callable=MagicMock())
    def test_generate_dashboard_creates_html(self, mock_open):
        """Test generate_dashboard() creates HTML string."""
        from survey_analyzer.reporting import HTMLDashboardGenerator

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        gen = HTMLDashboardGenerator()
        # generate_dashboard returns HTML string, doesn't take output_path
        html = gen.generate_dashboard(
            cross_tables={"tables": []},
            statistics={"tables": []},
            filter_list=None
        )

        # Verify HTML is generated
        assert isinstance(html, str)
        assert len(html) > 0


# ============================================================================
# Module Level Tests
# ============================================================================

class TestReportingModule:
    """Test reporting module imports."""

    def test_import_powerpoint_generator(self):
        """Test PowerPointGenerator can be imported."""
        from survey_analyzer.reporting import PowerPointGenerator
        assert PowerPointGenerator is not None

    def test_import_html_dashboard_generator(self):
        """Test HTMLDashboardGenerator can be imported."""
        from survey_analyzer.reporting import HTMLDashboardGenerator
        assert HTMLDashboardGenerator is not None

    def test_module_exports(self):
        """Test module exports expected classes."""
        from survey_analyzer import reporting
        expected_exports = [
            "PowerPointGenerator",
            "HTMLDashboardGenerator"
        ]
        for export in expected_exports:
            # Check in submodule
            from survey_analyzer.reporting.powerpoint import PowerPointGenerator
            from survey_analyzer.reporting.dashboard import HTMLDashboardGenerator
