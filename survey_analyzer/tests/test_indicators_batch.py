"""
Tests for survey_analyzer.indicators.batch_processor module (Unified).

Tests batch processing of questions for indicator generation.
Updates the unified table_specification.jsonc file directly.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestBatchProcessorModule:
    """Test batch_processor module imports."""

    def test_import_batch_processor(self):
        """Test BatchProcessor can be imported."""
        from survey_analyzer.indicators.batch_processor import BatchProcessor
        assert BatchProcessor is not None


class TestBatchProcessorInstantiation:
    """Test BatchProcessor initialization."""

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_default_initialization(self):
        """Test BatchProcessor default initialization."""
        from survey_analyzer.indicators.batch_processor import BatchProcessor
        processor = BatchProcessor()
        assert processor.continue_on_error is True

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_initialization_with_continue_on_error_false(self):
        """Test initialization with continue_on_error=False."""
        from survey_analyzer.indicators.batch_processor import BatchProcessor
        processor = BatchProcessor(continue_on_error=False)
        assert processor.continue_on_error is False


class TestBatchProcessorFileOperations:
    """Test file loading and saving."""

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_load_spec(self, tmp_path):
        """Test _load_spec loads spec file correctly."""
        from survey_analyzer.indicators.batch_processor import BatchProcessor

        # Create test spec file
        spec_file = tmp_path / "table_specification.jsonc"
        test_spec = {
            "metadata": {"spec_id": "test"},
            "questions": [
                {
                    "question_code": "Q1",
                    "original_variables": ["Q1_1"],
                    "indicators": []
                }
            ],
            "filter_clause": {},
            "weight_indicator": None
        }
        with open(spec_file, "w") as f:
            f.write("// Comment\n")
            json.dump(test_spec, f)

        processor = BatchProcessor()
        loaded = processor._load_spec(str(spec_file))

        assert loaded["metadata"]["spec_id"] == "test"
        assert len(loaded["questions"]) == 1

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_save_spec(self, tmp_path):
        """Test _save_spec saves spec correctly."""
        from survey_analyzer.indicators.batch_processor import BatchProcessor

        spec_file = tmp_path / "table_specification.jsonc"
        test_spec = {
            "metadata": {"spec_id": "test"},
            "questions": [],
            "filter_clause": {},
            "weight_indicator": None
        }

        processor = BatchProcessor()
        processor._save_spec(test_spec, str(spec_file))

        assert spec_file.exists()

        # Verify JSONC format
        content = spec_file.read_text()
        assert "//" in content
        assert "Table Specification" in content


class TestBatchProcessorProcessAll:
    """Test process_all method."""

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_process_all_loads_spec_and_metadata(self, tmp_path):
        """Test process_all loads spec and metadata files."""
        from survey_analyzer.indicators.batch_processor import BatchProcessor

        # Create spec file
        spec_file = tmp_path / "table_specification.jsonc"
        test_spec = {
            "metadata": {"spec_id": "test", "stage": "questions_extracted"},
            "questions": [
                {
                    "question_code": "Q1",
                    "original_variables": ["Q1_1"],
                    "indicators": []
                }
            ],
            "filter_clause": {},
            "weight_indicator": None
        }
        with open(spec_file, "w") as f:
            json.dump(test_spec, f)

        # Create metadata file
        metadata_file = tmp_path / "metadata.json"
        metadata_file.write_text('{"Q1_1": {}}')

        # Mock generator
        with patch.object(BatchProcessor, '__init__', lambda self, **kwargs: None):
            processor = BatchProcessor()
            processor.generator = Mock()
            processor.generator.generate_for_question = Mock(return_value={
                "indicator_code": "Q1_IND",
                "indicator_label": "Test",
                "indicator_variables": ["Q1_1"],
                "transformation": None,
                "tabulation_type": "categorical",
                "tabulation_metric": "column_percent",
                "indicator_value_labels": None
            })

            spec = processor.process_all(
                spec_file=str(spec_file),
                metadata_file=str(metadata_file),
                resume=False
            )

            assert spec is not None
            assert len(spec["questions"]) == 1
            assert len(spec["questions"][0]["indicators"]) == 1

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_process_all_filters_by_question_codes(self, tmp_path):
        """Test process_all filters by specific question codes."""
        from survey_analyzer.indicators.batch_processor import BatchProcessor

        # Create spec file with multiple questions
        spec_file = tmp_path / "table_specification.jsonc"
        test_spec = {
            "metadata": {"spec_id": "test"},
            "questions": [
                {"question_code": "Q1", "original_variables": ["Q1_1"], "indicators": []},
                {"question_code": "Q2", "original_variables": ["Q2_1"], "indicators": []},
                {"question_code": "S0", "original_variables": ["S0"], "indicators": []},
            ],
            "filter_clause": {},
            "weight_indicator": None
        }
        with open(spec_file, "w") as f:
            json.dump(test_spec, f)

        metadata_file = tmp_path / "metadata.json"
        metadata_file.write_text('{}')

        # Mock to avoid API calls
        with patch.object(BatchProcessor, '__init__', lambda self, **kwargs: None):
            processor = BatchProcessor()
            processor.generator = Mock()
            processor.generator.generate_for_question = Mock(side_effect=lambda q, v, m: {
                "indicator_code": f"{q}_IND",
                "indicator_label": q,
                "indicator_variables": v,
                "transformation": None,
                "tabulation_type": "categorical",
                "tabulation_metric": "column_percent",
                "indicator_value_labels": None
            })

            # Only process Q1 and S0
            spec = processor.process_all(
                spec_file=str(spec_file),
                metadata_file=str(metadata_file),
                question_codes=["Q1", "S0"],
                resume=False
            )

            # Check that only Q1 and S0 were processed (not Q2)
            for q in spec["questions"]:
                if q["question_code"] in ["Q1", "S0"]:
                    assert len(q["indicators"]) == 1
                elif q["question_code"] == "Q2":
                    assert len(q["indicators"]) == 0


class TestBatchProcessorResume:
    """Test resume functionality."""

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_resume_skips_questions_with_indicators(self, tmp_path):
        """Test resume=True skips questions that already have indicators."""
        from survey_analyzer.indicators.batch_processor import BatchProcessor

        # Create spec file with Q1 already having indicators
        spec_file = tmp_path / "table_specification.jsonc"
        test_spec = {
            "metadata": {"spec_id": "test"},
            "questions": [
                {
                    "question_code": "Q1",
                    "original_variables": ["Q1_1"],
                    "indicators": [{"indicator_code": "Q1_IND"}]  # Already has indicators
                },
                {
                    "question_code": "Q2",
                    "original_variables": ["Q2_1"],
                    "indicators": []  # Empty
                }
            ],
            "filter_clause": {},
            "weight_indicator": None
        }
        with open(spec_file, "w") as f:
            json.dump(test_spec, f)

        metadata_file = tmp_path / "metadata.json"
        metadata_file.write_text('{}')

        # Mock generator
        with patch.object(BatchProcessor, '__init__', lambda self, **kwargs: None):
            processor = BatchProcessor()
            processor.generator = Mock()
            processor.generator.generate_for_question = Mock(return_value={
                "indicator_code": "Q2_IND",
                "indicator_label": "Q2",
                "indicator_variables": ["Q2_1"],
                "transformation": None,
                "tabulation_type": "categorical",
                "tabulation_metric": "column_percent",
                "indicator_value_labels": None
            })

            spec = processor.process_all(
                spec_file=str(spec_file),
                metadata_file=str(metadata_file),
                resume=True
            )

            # Q1 should still have only 1 indicator (not re-processed)
            q1 = next(q for q in spec["questions"] if q["question_code"] == "Q1")
            assert len(q1["indicators"]) == 1
            assert q1["indicators"][0]["indicator_code"] == "Q1_IND"

            # Q2 should now have 1 indicator
            q2 = next(q for q in spec["questions"] if q["question_code"] == "Q2")
            assert len(q2["indicators"]) == 1


class TestBatchProcessorErrorHandling:
    """Test error handling behavior."""

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_continue_on_error_saves_after_error(self, tmp_path):
        """Test continue_on_error=True saves checkpoint after error."""
        from survey_analyzer.indicators.batch_processor import BatchProcessor

        # Create spec file
        spec_file = tmp_path / "table_specification.jsonc"
        test_spec = {
            "metadata": {"spec_id": "test"},
            "questions": [
                {"question_code": "Q1", "original_variables": ["Q1_1"], "indicators": []},
                {"question_code": "Q2", "original_variables": ["Q2_1"], "indicators": []}
            ],
            "filter_clause": {},
            "weight_indicator": None
        }
        with open(spec_file, "w") as f:
            json.dump(test_spec, f)

        metadata_file = tmp_path / "metadata.json"
        metadata_file.write_text('{}')

        # Mock: Q1 succeeds, Q2 fails
        # Create a proper mock init that sets continue_on_error
        def mock_init(self, **kwargs):
            self.continue_on_error = kwargs.get('continue_on_error', True)

        with patch.object(BatchProcessor, '__init__', mock_init):
            processor = BatchProcessor(continue_on_error=True)
            processor.generator = Mock()
            processor.generator.generate_for_question = Mock(side_effect=[
                # Q1 success
                {
                    "indicator_code": "Q1_IND",
                    "indicator_label": "Q1",
                    "indicator_variables": ["Q1_1"],
                    "transformation": None,
                    "tabulation_type": "categorical",
                    "tabulation_metric": "column_percent",
                    "indicator_value_labels": None
                },
                # Q2 error
                Exception("API Error")
            ])

            spec = processor.process_all(
                spec_file=str(spec_file),
                metadata_file=str(metadata_file),
                resume=False
            )

            # Checkpoint should be saved even after error
            # Q1 should be in the spec
            q1 = next(q for q in spec["questions"] if q["question_code"] == "Q1")
            assert len(q1["indicators"]) == 1


class TestBatchProcessorProgressCallback:
    """Test progress callback functionality."""

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_progress_callback_called(self, tmp_path):
        """Test progress_callback is called for each question."""
        from survey_analyzer.indicators.batch_processor import BatchProcessor

        # Create spec file
        spec_file = tmp_path / "table_specification.jsonc"
        test_spec = {
            "metadata": {"spec_id": "test"},
            "questions": [
                {"question_code": "Q1", "original_variables": ["Q1"], "indicators": []},
                {"question_code": "Q2", "original_variables": ["Q2"], "indicators": []}
            ],
            "filter_clause": {},
            "weight_indicator": None
        }
        with open(spec_file, "w") as f:
            json.dump(test_spec, f)

        metadata_file = tmp_path / "metadata.json"
        metadata_file.write_text('{}')

        progress_calls = []

        def progress_callback(current, total, question_code):
            progress_calls.append((current, total, question_code))

        # Mock generator
        with patch.object(BatchProcessor, '__init__', lambda self, **kwargs: None):
            processor = BatchProcessor()
            processor.generator = Mock()
            processor.generator.generate_for_question = Mock(side_effect=lambda q, v, m: {
                "indicator_code": f"{q}_IND",
                "indicator_label": q,
                "indicator_variables": v,
                "transformation": None,
                "tabulation_type": "categorical",
                "tabulation_metric": "column_percent",
                "indicator_value_labels": None
            })

            processor.process_all(
                spec_file=str(spec_file),
                metadata_file=str(metadata_file),
                resume=False,
                progress_callback=progress_callback
            )

            # Check callback was called for both questions
            assert len(progress_calls) == 2
            assert progress_calls[0] == (1, 2, "Q1")
            assert progress_calls[1] == (2, 2, "Q2")


class TestBatchProcessorMetadataUpdate:
    """Test metadata is updated correctly."""

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_stage_metadata_updated(self, tmp_path):
        """Test stage and history metadata is updated."""
        from survey_analyzer.indicators.batch_processor import BatchProcessor

        # Create spec file
        spec_file = tmp_path / "table_specification.jsonc"
        test_spec = {
            "metadata": {"spec_id": "test", "stage": "questions_extracted"},
            "questions": [
                {"question_code": "Q1", "original_variables": ["Q1"], "indicators": []}
            ],
            "filter_clause": {},
            "weight_indicator": None
        }
        with open(spec_file, "w") as f:
            json.dump(test_spec, f)

        metadata_file = tmp_path / "metadata.json"
        metadata_file.write_text('{}')

        # Mock generator
        with patch.object(BatchProcessor, '__init__', lambda self, **kwargs: None):
            processor = BatchProcessor()
            processor.generator = Mock()
            processor.generator.generate_for_question = Mock(return_value={
                "indicator_code": "Q1_IND",
                "indicator_label": "Q1",
                "indicator_variables": ["Q1"],
                "transformation": None,
                "tabulation_type": "categorical",
                "tabulation_metric": "column_percent",
                "indicator_value_labels": None
            })

            spec = processor.process_all(
                spec_file=str(spec_file),
                metadata_file=str(metadata_file),
                resume=False
            )

            # Check stage was updated
            assert spec["metadata"]["stage"] == "indicators_generated"

            # Check stage history
            history = spec["metadata"].get("stage_history", [])
            assert any(h.get("stage") == 3 for h in history)
