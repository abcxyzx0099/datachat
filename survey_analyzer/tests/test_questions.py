"""
Tests for survey_analyzer.questions module (Unified).

Tests question extraction and variable grouping functionality.
Works with the unified table_specification.jsonc file.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch


class TestQuestionsModule:
    """Test questions module imports."""

    def test_import_question_extractor(self):
        """Test QuestionExtractor can be imported."""
        from survey_analyzer.questions import QuestionExtractor
        assert QuestionExtractor is not None

    def test_module_exports(self):
        """Test module exports expected classes."""
        from survey_analyzer import questions
        assert hasattr(questions, "QuestionExtractor")


class TestQuestionExtractorInstantiation:
    """Test QuestionExtractor initialization."""

    def test_default_initialization(self):
        """Test QuestionExtractor default initialization."""
        from survey_analyzer.questions import QuestionExtractor
        extractor = QuestionExtractor()
        assert extractor is not None

    def test_with_unified_spec(self):
        """Test initialization with UnifiedTableSpec."""
        from survey_analyzer.questions import QuestionExtractor
        from survey_analyzer.tablespec import UnifiedTableSpec

        spec = UnifiedTableSpec()
        extractor = QuestionExtractor(unified_spec=spec)
        assert extractor.unified_spec is not None


class TestQuestionCodeExtraction:
    """Test question code extraction logic."""

    def test_extract_question_code_from_variable(self):
        """Test extracting question code from variable name."""
        from survey_analyzer.questions import QuestionExtractor
        extractor = QuestionExtractor()

        # Test standard underscore pattern
        assert extractor.extract_question_code("Q1_1_bin") == "Q1"
        assert extractor.extract_question_code("Q2A_2_cat") == "Q2A"
        assert extractor.extract_question_code("S0_cat") == "S0"
        assert extractor.extract_question_code("D1_1_bin") == "D1"

    def test_extract_question_code_no_underscore(self):
        """Test extraction when no underscore exists."""
        from survey_analyzer.questions import QuestionExtractor
        extractor = QuestionExtractor()

        # No underscore - return full name
        assert extractor.extract_question_code("weight") == "weight"
        assert extractor.extract_question_code("CASEID") == "CASEID"


class TestQuestionExtractionAPI:
    """Test the new extract_questions API (returns list, not dict)."""

    def test_extract_questions_returns_list(self):
        """Test extract_questions returns a list of question dicts."""
        from survey_analyzer.questions import QuestionExtractor

        # Dictionary format metadata
        metadata = {
            "Q1_1_bin": {"variable_name": "Q1_1_bin", "label": "Option 1"},
            "Q1_2_bin": {"variable_name": "Q1_2_bin", "label": "Option 2"},
            "S0_cat": {"variable_name": "S0_cat", "label": "Gender"},
            "D1_1_bin": {"variable_name": "D1_1_bin", "label": "Day 1"},
        }

        extractor = QuestionExtractor()
        questions = extractor.extract_questions(metadata)

        # Should return a list
        assert isinstance(questions, list)
        assert len(questions) == 3  # D1, Q1, S0 (alphabetically sorted)

    def test_extract_questions_structure(self):
        """Test extract_questions returns correct structure."""
        from survey_analyzer.questions import QuestionExtractor

        metadata = {
            "Q1_1_bin": {"variable_name": "Q1_1_bin"},
            "Q1_2_bin": {"variable_name": "Q1_2_bin"},
        }

        extractor = QuestionExtractor()
        questions = extractor.extract_questions(metadata)

        # Check structure
        q = questions[0]
        assert "question_code" in q
        assert "question_type" in q
        assert "question_text" in q
        assert "original_variables" in q


class TestExtractFromFile:
    """Test extraction from file."""

    def test_extract_from_file_creates_spec(self, tmp_path):
        """Test extract_from_file creates unified spec file."""
        from survey_analyzer.questions import QuestionExtractor

        # Create input metadata file (dictionary format)
        metadata_file = tmp_path / "metadata.json"
        metadata = {
            "Q1_1_bin": {"variable_name": "Q1_1_bin", "label": "Option 1"},
            "Q1_2_bin": {"variable_name": "Q1_2_bin", "label": "Option 2"},
            "S0_cat": {"variable_name": "S0_cat", "label": "Gender"},
        }
        metadata_file.write_text(json.dumps(metadata, indent=2))

        output_file = tmp_path / "table_specification.jsonc"

        extractor = QuestionExtractor()
        spec = extractor.extract_from_file(
            str(metadata_file),
            str(output_file)
        )

        # Check output file was created
        assert output_file.exists()

        # Check spec structure
        assert "metadata" in spec
        assert "questions" in spec
        assert "filter_clause" in spec
        assert "weight_indicator" in spec

    def test_extract_from_file_adds_questions(self, tmp_path):
        """Test extract_from_file adds questions to spec."""
        from survey_analyzer.questions import QuestionExtractor

        # Create metadata file
        metadata_file = tmp_path / "metadata.json"
        metadata = {
            "Q1_1": {"variable_name": "Q1_1"},
            "S0": {"variable_name": "S0"},
        }
        metadata_file.write_text(json.dumps(metadata, indent=2))

        output_file = tmp_path / "table_specification.jsonc"

        extractor = QuestionExtractor()
        spec = extractor.extract_from_file(
            str(metadata_file),
            str(output_file)
        )

        # Check questions were added
        questions = spec.get("questions", [])
        assert len(questions) == 2  # Q1 and S0

    def test_extract_from_file_saves_backup(self, tmp_path):
        """Test extract_from_file can save optional backup."""
        from survey_analyzer.questions import QuestionExtractor

        # Create metadata file
        metadata_file = tmp_path / "metadata.json"
        metadata_file.write_text(json.dumps({"Q1_1": {}}))

        output_file = tmp_path / "table_specification.jsonc"
        backup_file = tmp_path / "questions.json"

        extractor = QuestionExtractor()
        spec = extractor.extract_from_file(
            str(metadata_file),
            str(output_file)
        )

        # Save backup
        questions = spec.get("questions", [])
        extractor.save_questions(questions, str(backup_file))

        # Check backup exists
        assert backup_file.exists()

        # Check backup structure
        with open(backup_file) as f:
            backup = json.load(f)
        assert "questions" in backup
        assert "metadata" in backup


class TestQuestionExtractionEdgeCases:
    """Test edge cases in question extraction."""

    def test_empty_metadata_returns_no_questions(self):
        """Test empty metadata returns empty questions list."""
        from survey_analyzer.questions import QuestionExtractor

        metadata = {}  # Empty dictionary

        extractor = QuestionExtractor()
        questions = extractor.extract_questions(metadata)

        assert len(questions) == 0

    def test_variables_with_same_question_code_grouped(self):
        """Test variables with same question code are grouped."""
        from survey_analyzer.questions import QuestionExtractor

        metadata = {
            "Q2A_1_bin": {"variable_name": "Q2A_1_bin"},
            "Q2A_2_bin": {"variable_name": "Q2A_2_bin"},
            "Q2A_3_bin": {"variable_name": "Q2A_3_bin"},
            "Q2A_4_bin": {"variable_name": "Q2A_4_bin"},
        }

        extractor = QuestionExtractor()
        questions = extractor.extract_questions(metadata)

        # All Q2A variables should be in one question
        assert len(questions) == 1
        q2a = questions[0]
        assert q2a["question_code"] == "Q2A"
        assert len(q2a["original_variables"]) == 4


class TestQuestionSorting:
    """Test question sorting behavior."""

    def test_questions_are_sorted_alphabetically(self):
        """Test questions are sorted alphabetically by question_code."""
        from survey_analyzer.questions import QuestionExtractor

        # Order in metadata: D1, Q1, S0
        metadata = {
            "D1_1_bin": {"variable_name": "D1_1_bin"},
            "Q1_1_bin": {"variable_name": "Q1_1_bin"},
            "S0_cat": {"variable_name": "S0_cat"},
        }

        extractor = QuestionExtractor()
        questions = extractor.extract_questions(metadata)

        # Check order is alphabetical (D1, Q1, S0)
        assert questions[0]["question_code"] == "D1"
        assert questions[1]["question_code"] == "Q1"
        assert questions[2]["question_code"] == "S0"
