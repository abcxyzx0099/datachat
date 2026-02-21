"""
Tests for survey_analyzer.io module.

Tests SPSS file reading and metadata transformation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch


# ============================================================================
# SPSSReader Tests
# ============================================================================

class TestSPSSReaderInstantiation:
    """Test SPSSReader class instantiation."""

    def test_default_initialization(self):
        """Test SPSSReader with default parameters."""
        from survey_analyzer.io import SPSSReader
        reader = SPSSReader()
        assert reader.encoding is None  # Default is None (auto-detect)
        assert reader.apply_value_formats is False

    def test_custom_encoding(self):
        """Test SPSSReader with custom encoding."""
        from survey_analyzer.io import SPSSReader
        reader = SPSSReader(encoding="latin-1")
        assert reader.encoding == "latin-1"


class TestSPSSReaderRead:
    """Test SPSSReader.read() method."""

    def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist raises FileNotFoundError."""
        from survey_analyzer.io import SPSSReader
        reader = SPSSReader()
        with pytest.raises(FileNotFoundError, match="SPSS file not found"):
            reader.read("/nonexistent/file.sav")


# ============================================================================
# MetadataTransformer Tests
# ============================================================================

class TestMetadataTransformer:
    """Test MetadataTransformer class."""

    def test_metadata_transformer_instantiation(self):
        """Test MetadataTransformer can be instantiated."""
        from survey_analyzer.io import MetadataTransformer
        transformer = MetadataTransformer()
        assert transformer is not None


# ============================================================================
# Module Level Tests
# ============================================================================

class TestIOModule:
    """Test IO module imports."""

    def test_import_spss_reader(self):
        """Test SPSSReader can be imported."""
        from survey_analyzer.io import SPSSReader
        assert SPSSReader is not None

    def test_import_metadata_transformer(self):
        """Test MetadataTransformer can be imported."""
        from survey_analyzer.io import MetadataTransformer
        assert MetadataTransformer is not None

    def test_module_exports(self):
        """Test module exports expected classes."""
        from survey_analyzer import io
        expected = ["SPSSReader", "MetadataTransformer"]
        for export in expected:
            assert hasattr(io, export)
