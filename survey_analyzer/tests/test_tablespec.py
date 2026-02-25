"""
Tests for survey_analyzer.tablespec module (Unified).

Tests the classification workflow for Stage 4.
Classifies indicators and adds is_row/is_column fields to unified spec.
"""

import json
import pytest
import tempfile
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


# Mock zai module if not available
class MockZhipuAiClient:
    def __init__(self, api_key):
        self.api_key = api_key


if 'zai' not in sys.modules:
    sys.modules['zai'] = Mock()
    sys.modules['zai'].ZhipuAiClient = MockZhipuAiClient


class TestTableSpecModule:
    """Test tablespec module imports."""

    def test_import_tablespec(self):
        """Test TableSpec can be imported."""
        from survey_analyzer.tablespec import TableSpec
        assert TableSpec is not None

    def test_import_unified_tablespec(self):
        """Test UnifiedTableSpec can be imported."""
        from survey_analyzer.tablespec import UnifiedTableSpec
        assert UnifiedTableSpec is not None

    def test_module_exports(self):
        """Test module exports expected classes."""
        from survey_analyzer import tablespec
        assert hasattr(tablespec, "TableSpec")
        assert hasattr(tablespec, "UnifiedTableSpec")


class TestTableSpecInstantiation:
    """Test TableSpec initialization."""

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_initialization_with_api_key(self):
        """Test TableSpec initialization with API key."""
        from survey_analyzer.tablespec import TableSpec
        spec = TableSpec(api_key="test_api_key")
        assert spec.api_key == "test_api_key"
        assert spec.model == "glm-4.7"

    @patch('survey_analyzer.tablespec.tablespec.ZAI_SDK_AVAILABLE', False)
    def test_initialization_fails_without_zai_sdk(self):
        """Test TableSpec fails without zai-sdk."""
        from survey_analyzer.tablespec import TableSpec
        with pytest.raises(ImportError):
            TableSpec(api_key="test_key")


class TestTableSpecClassification:
    """Test indicator classification methods."""

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_parse_classification_response(self):
        """Test _parse_classification_response parses JSON correctly."""
        from survey_analyzer.tablespec import TableSpec
        spec = TableSpec(api_key="test_key")

        response_json = '''{
  "classifications": [
    {"indicator_code": "Q1_SAT", "is_row": true, "is_column": false},
    {"indicator_code": "S0_GENDER", "is_row": false, "is_column": true}
  ]
}'''

        classifications = spec._parse_classification_response(response_json)

        assert len(classifications) == 2
        assert classifications["Q1_SAT"]["is_row"] is True
        assert classifications["Q1_SAT"]["is_column"] is False
        assert classifications["S0_GENDER"]["is_row"] is False
        assert classifications["S0_GENDER"]["is_column"] is True

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_parse_classification_with_markdown(self):
        """Test parsing removes markdown code blocks."""
        from survey_analyzer.tablespec import TableSpec
        spec = TableSpec(api_key="test_key")

        response_with_markdown = '''```json
{
  "classifications": [
    {"indicator_code": "Q1", "is_row": true, "is_column": false}
  ]
}
```'''

        classifications = spec._parse_classification_response(response_with_markdown)
        assert "Q1" in classifications

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_parse_classification_invalid_json_raises_error(self):
        """Test invalid JSON raises ValueError."""
        from survey_analyzer.tablespec import TableSpec
        spec = TableSpec(api_key="test_key")

        with pytest.raises(ValueError, match="Failed to parse"):
            spec._parse_classification_response("not valid json")


class TestTableSpecClassifyFromFile:
    """Test classify_from_file method."""

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_classify_from_file(self, tmp_path):
        """Test classify_from_file loads spec and classifies."""
        from survey_analyzer.tablespec import TableSpec

        # Create test spec file
        spec_file = tmp_path / "table_specification.jsonc"
        test_spec = {
            "metadata": {"spec_id": "test", "stage": "indicators_generated"},
            "questions": [
                {
                    "question_code": "Q1",
                    "question_type": "Single Choice",
                    "original_variables": ["Q1_1"],
                    "indicators": [
                        {
                            "indicator_code": "Q1_SAT",
                            "indicator_label": "Satisfaction",
                            "indicator_variables": ["Q1_1"],
                            "transformation": None,
                            "tabulation_type": "categorical",
                            "tabulation_metric": "column_percent",
                            "indicator_value_labels": {"1": "Yes"}
                        }
                    ]
                },
                {
                    "question_code": "S0",
                    "question_type": "Single Choice",
                    "original_variables": ["S0"],
                    "indicators": [
                        {
                            "indicator_code": "S0_GENDER",
                            "indicator_label": "Gender",
                            "indicator_variables": ["S0"],
                            "transformation": None,
                            "tabulation_type": "categorical",
                            "tabulation_metric": "column_percent",
                            "indicator_value_labels": {"1": "Male"}
                        }
                    ]
                }
            ],
            "filter_clause": {},
            "weight_indicator": None
        }
        with open(spec_file, "w") as f:
            json.dump(test_spec, f)

        # Mock LLM call
        with patch.object(TableSpec, '_classify_with_llm') as mock_llm:
            mock_llm.return_value = {
                "Q1_SAT": {"is_row": True, "is_column": False},
                "S0_GENDER": {"is_row": False, "is_column": True}
            }

            spec_obj = TableSpec()
            result_spec = spec_obj.classify_from_file(str(spec_file))

            # Check classification was applied
            for q in result_spec["questions"]:
                for ind in q["indicators"]:
                    code = ind["indicator_code"]
                    if code == "Q1_SAT":
                        assert ind["is_row"] is True
                        assert ind["is_column"] is False
                    elif code == "S0_GENDER":
                        assert ind["is_row"] is False
                        assert ind["is_column"] is True

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_classify_updates_metadata(self, tmp_path):
        """Test classify_from_file updates stage metadata."""
        from survey_analyzer.tablespec import TableSpec

        # Create test spec file
        spec_file = tmp_path / "table_specification.jsonc"
        test_spec = {
            "metadata": {"spec_id": "test", "stage": "indicators_generated"},
            "questions": [
                {
                    "question_code": "Q1",
                    "original_variables": ["Q1"],
                    "indicators": [
                        {
                            "indicator_code": "Q1_IND",
                            "indicator_label": "Q1",
                            "indicator_variables": ["Q1"],
                            "transformation": None,
                            "tabulation_type": "categorical",
                            "tabulation_metric": "column_percent",
                            "indicator_value_labels": None
                        }
                    ]
                }
            ],
            "filter_clause": {},
            "weight_indicator": None
        }
        with open(spec_file, "w") as f:
            json.dump(test_spec, f)

        # Mock LLM call
        with patch.object(TableSpec, '_classify_with_llm') as mock_llm:
            mock_llm.return_value = {
                "Q1_IND": {"is_row": True, "is_column": False}
            }

            spec_obj = TableSpec()
            result_spec = spec_obj.classify_from_file(str(spec_file))

            # Check stage was updated
            assert result_spec["metadata"]["stage"] == "classification_complete"

            # Check stage history
            history = result_spec["metadata"].get("stage_history", [])
            assert any(h.get("stage") == 4 for h in history)


class TestUnifiedTableSpec:
    """Test UnifiedTableSpec class."""

    @patch.dict('os.environ', {})
    def test_create_new_spec(self, tmp_path):
        """Test creating a new unified spec file."""
        from survey_analyzer.tablespec import UnifiedTableSpec

        output_file = tmp_path / "table_specification.jsonc"
        spec_obj = UnifiedTableSpec()
        spec = spec_obj.create(str(output_file), project_id="test")

        assert Path(output_file).exists()
        assert spec["metadata"]["project_id"] == "test"
        assert spec["metadata"]["stage"] == "initialized"
        assert len(spec["questions"]) == 0

    @patch.dict('os.environ', {})
    def test_load_existing_spec(self, tmp_path):
        """Test loading an existing spec file."""
        from survey_analyzer.tablespec import UnifiedTableSpec

        # Create spec file first
        output_file = tmp_path / "table_specification.jsonc"
        test_spec = {
            "metadata": {"spec_id": "test", "project_id": "proj"},
            "questions": [],
            "filter_clause": {},
            "weight_indicator": None
        }
        with open(output_file, "w") as f:
            json.dump(test_spec, f)

        # Load it
        spec_obj = UnifiedTableSpec()
        spec = spec_obj.load(str(output_file))

        assert spec["metadata"]["spec_id"] == "test"

    @patch.dict('os.environ', {})
    def test_add_questions(self, tmp_path):
        """Test add_questions method."""
        from survey_analyzer.tablespec import UnifiedTableSpec

        output_file = tmp_path / "table_specification.jsonc"
        spec_obj = UnifiedTableSpec()
        spec_obj.create(str(output_file))

        questions = [
            {
                "question_code": "Q1",
                "question_type": "Single Choice",
                "question_text": "Test",
                "original_variables": ["Q1_1", "Q1_2"]
            }
        ]

        spec_obj.add_questions(questions)

        assert len(spec_obj.spec["questions"]) == 1
        assert spec_obj.spec["questions"][0]["question_code"] == "Q1"

    @patch.dict('os.environ', {})
    def test_add_indicator(self, tmp_path):
        """Test add_indicator method."""
        from survey_analyzer.tablespec import UnifiedTableSpec

        output_file = tmp_path / "table_specification.jsonc"
        spec_obj = UnifiedTableSpec()
        spec_obj.create(str(output_file))

        # Add a question first
        spec_obj.add_questions([
            {
                "question_code": "Q1",
                "question_type": "Single Choice",
                "question_text": "Test",
                "original_variables": ["Q1_1"]
            }
        ])

        # Add indicator
        spec_obj.add_indicator("Q1", {
            "indicator_code": "Q1_IND",
            "indicator_label": "Q1 Indicator",
            "indicator_variables": ["Q1_1"],
            "transformation": None,
            "tabulation_type": "categorical",
            "tabulation_metric": "column_percent",
            "indicator_value_labels": None
        })

        q = spec_obj.spec["questions"][0]
        assert len(q["indicators"]) == 1
        assert q["indicators"][0]["indicator_code"] == "Q1_IND"

    @patch.dict('os.environ', {})
    def test_get_row_indicators(self, tmp_path):
        """Test get_row_indicators helper."""
        from survey_analyzer.tablespec import UnifiedTableSpec

        output_file = tmp_path / "table_specification.jsonc"
        spec_obj = UnifiedTableSpec()
        spec_obj.create(str(output_file))

        # Add question with classified indicator
        spec_obj.add_questions([
            {
                "question_code": "Q1",
                "question_type": "Single Choice",
                "question_text": "Test",
                "original_variables": ["Q1"]
            }
        ])

        spec_obj.spec["questions"][0]["indicators"] = [
            {
                "indicator_code": "Q1_IND",
                "indicator_label": "Q1",
                "indicator_variables": ["Q1"],
                "is_row": True,
                "is_column": False
            }
        ]

        row_inds = spec_obj.get_row_indicators()
        assert len(row_inds) == 1
        assert row_inds[0]["indicator_code"] == "Q1_IND"
        assert row_inds[0]["is_row"] is True

    @patch.dict('os.environ', {})
    def test_get_column_indicators(self, tmp_path):
        """Test get_column_indicators helper."""
        from survey_analyzer.tablespec import UnifiedTableSpec

        output_file = tmp_path / "table_specification.jsonc"
        spec_obj = UnifiedTableSpec()
        spec_obj.create(str(output_file))

        # Add question with classified indicator
        spec_obj.add_questions([
            {
                "question_code": "S0",
                "question_type": "Single Choice",
                "question_text": "Gender",
                "original_variables": ["S0"]
            }
        ])

        spec_obj.spec["questions"][0]["indicators"] = [
            {
                "indicator_code": "S0_GENDER",
                "indicator_label": "Gender",
                "indicator_variables": ["S0"],
                "is_row": False,
                "is_column": True
            }
        ]

        col_inds = spec_obj.get_column_indicators()
        assert len(col_inds) == 1
        assert col_inds[0]["indicator_code"] == "S0_GENDER"
        assert col_inds[0]["is_column"] is True

    @patch.dict('os.environ', {})
    def test_save_creates_jsonc_format(self, tmp_path):
        """Test save writes JSONC format with comments."""
        from survey_analyzer.tablespec import UnifiedTableSpec

        output_file = tmp_path / "test_spec.jsonc"
        spec_obj = UnifiedTableSpec()
        spec_obj.create(str(output_file))

        content = output_file.read_text()

        # Check JSONC format
        assert content.startswith("//")
        assert "Unified Table Specification" in content
        assert '"metadata"' in content


class TestTableSpecPrompts:
    """Test prompt loading."""

    @patch.dict('os.environ', {'GLM_API_KEY': 'test_key'})
    def test_default_prompts_when_files_missing(self):
        """Test default prompts are used when files don't exist."""
        from survey_analyzer.tablespec import TableSpec

        spec = TableSpec()

        system_prompt = spec._get_default_system_prompt()
        user_prompt = spec._get_default_user_prompt()

        assert "expert in survey data analysis" in system_prompt
        assert "Classify these indicators" in user_prompt or "classify the following indicators" in user_prompt
        assert "{indicators_list}" in user_prompt
