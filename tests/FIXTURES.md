# Test Fixtures Documentation

This document describes all pytest fixtures available in `tests/conftest.py` for testing the Survey Analysis & Visualization Workflow.

---

## Table of Contents

1. [Path Fixtures](#path-fixtures)
2. [Data File Fixtures](#data-file-fixtures)
3. [Metadata Fixtures](#metadata-fixtures)
4. [State Fixtures](#state-fixtures)
5. [Artifact Fixtures](#artifact-fixtures)
6. [LLM Response Fixtures](#llm-response-fixtures)
7. [PSPP Output Fixtures](#pspp-output-fixtures)
8. [Validation Result Fixtures](#validation-result-fixtures)
9. [Mock Fixtures](#mock-fixtures)

---

## Path Fixtures

| Fixture | Returns | Description |
|---------|---------|-------------|
| `tests_dir` | `Path` | Path to the tests directory |
| `fixtures_dir` | `Path` | Path to the fixtures directory |
| `sample_sav_path` | `str` | Path to sample_data.sav (standard test data) |
| `small_sav_path` | `str` | Path to small_data.sav (10 rows) |
| `large_sav_path` | `str` | Path to large_data.sav (500 rows) |
| `edge_case_sav_path` | `str` | Path to edge_case_data.sav (missing values, outliers) |
| `temp_output_dir` | `Path` | Temporary output directory (auto-cleanup) |
| `temp_checkpoint_db` | `str` | Temporary SQLite checkpoint database (auto-cleanup) |

### Usage Examples

```python
def test_with_sav_file(sample_sav_path):
    """Test using sample .sav file path."""
    from agent.utils.file_io import read_spss_file
    df, metadata = read_spss_file(sample_sav_path)
    assert df is not None

def test_with_temp_dir(temp_output_dir):
    """Test using temporary directory."""
    output_file = temp_output_dir / "output.txt"
    output_file.write_text("test data")
    assert output_file.exists()
```

---

## Data File Fixtures

| Fixture | Returns | Description |
|---------|---------|-------------|
| `sample_dataframe` | `pd.DataFrame` | 50 rows, 6 variables (age, gender, education, satisfaction, employed, income) |
| `small_dataframe` | `pd.DataFrame` | 10 rows, 4 variables (for quick tests) |
| `large_dataframe` | `pd.DataFrame` | 500 rows, 15 variables (for performance tests) |
| `edge_case_dataframe` | `pd.DataFrame` | 12 rows with missing values and outliers |

### Usage Examples

```python
def test_with_sample_data(sample_dataframe):
    """Test using sample dataframe."""
    assert len(sample_dataframe) == 50
    assert "age" in sample_dataframe.columns
    assert sample_dataframe["age"].min() >= 18

def test_with_edge_cases(edge_case_dataframe):
    """Test using edge case dataframe."""
    assert edge_case_dataframe["age"].isna().any()
    assert edge_case_dataframe["income"].max() > 900000  # Outlier
```

---

## Metadata Fixtures

| Fixture | Returns | Description |
|---------|---------|-------------|
| `sample_metadata` | `Dict` | SPSS metadata from pyreadstat (column_labels, value_labels, etc.) |
| `variable_centered_metadata` | `Dict` | Metadata transformed to variable-centered format |
| `filtered_metadata` | `List[Dict]` | Variables after filtering (excludes binary, high cardinality) |
| `new_metadata` | `Dict` | Metadata after recoding (new_data.sav structure) |

### Usage Examples

```python
def test_with_metadata(sample_metadata):
    """Test using sample SPSS metadata."""
    assert sample_metadata["n_rows"] == 50
    assert "gender" in sample_metadata["column_value_labels"]
    assert sample_metadata["column_value_labels"]["gender"][1] == "Male"

def test_with_filtered_metadata(filtered_metadata):
    """Test using filtered metadata."""
    variable_names = [v["name"] for v in filtered_metadata]
    assert "gender" in variable_names
    assert "employed" not in variable_names  # Binary, filtered out
```

---

## State Fixtures

| Fixture | Phase | Step | Description |
|---------|-------|------|-------------|
| `sample_config` | - | - | Standard test configuration (auto-approve enabled) |
| `minimal_config` | - | - | Minimal configuration for fast tests |
| `human_review_config` | - | - | Configuration with human review required |
| `sample_state` | 0 | 0 | Initial workflow state |
| `extraction_state` | 1 | 1-3 | State after data extraction and filtering |
| `recoding_state` | 2 | 4-8 | State after recoding completed |
| `indicator_state` | 3 | 9-11 | State after indicator generation |
| `table_state` | 4 | 12-16 | State after cross-table generation |
| `statistics_state` | 5 | 17-18 | State after statistical analysis |
| `filtering_state` | 6 | 19-20 | State after significance filtering |
| `presentation_state` | 7-8 | 21-22 | Final state after presentation generation |
| `state_with_errors` | - | - | State with accumulated errors |
| `state_at_max_iterations` | - | - | State at maximum self-correction iterations |

### Usage Examples

```python
def test_initial_state(sample_state):
    """Test using initial workflow state."""
    assert sample_state["current_step"] == 0
    assert "input_file_path" in sample_state

def test_recoding_phase(recoding_state):
    """Test using state after recoding phase."""
    assert recoding_state["current_step"] == 8
    assert recoding_state["recoding_approved"] is True
    assert "new_metadata" in recoding_state

def test_final_state(presentation_state):
    """Test using final workflow state."""
    assert presentation_state["current_step"] == 22
    assert "powerpoint_path" in presentation_state
    assert "html_dashboard_path" in presentation_state
```

---

## Artifact Fixtures

### Recoding Rules

| Fixture | Returns | Description |
|---------|---------|-------------|
| `valid_recoding_rules` | `Dict` | Valid recoding rules (age → age_group, income → income_group) |
| `invalid_recoding_rules` | `Dict` | Invalid rules with various error types |

### Indicators

| Fixture | Returns | Description |
|---------|---------|-------------|
| `valid_indicators` | `Dict` | Valid indicators (Customer_Satisfaction, Demographic_Profile) |
| `invalid_indicators` | `Dict` | Invalid indicators with various error types |

### Table Specifications

| Fixture | Returns | Description |
|---------|---------|-------------|
| `valid_table_specs` | `Dict` | Valid table specifications |
| `invalid_table_specs` | `Dict` | Invalid table specs with various error types |

### Statistical Data

| Fixture | Returns | Description |
|---------|---------|-------------|
| `significant_tables_data` | `Dict` | Sample significant_tables.json structure |
| `statistical_summary_data` | `List` | Sample statistical_analysis_summary.json structure |

### Usage Examples

```python
def test_with_valid_recoding_rules(valid_recoding_rules):
    """Test using valid recoding rules."""
    rules = valid_recoding_rules["recoding_rules"]
    assert len(rules) == 2
    assert rules[0]["source_variable"] == "age"

def test_with_invalid_indicators(invalid_indicators):
    """Test using invalid indicators for error testing."""
    indicators = invalid_indicators["indicators"]
    # Has duplicate names
    names = [i["indicator_name"] for i in indicators]
    assert len(names) != len(set(names))
```

---

## LLM Response Fixtures

| Fixture | Returns | Description |
|---------|---------|-------------|
| `mock_llm_client` | `Mock` | Mock LLM client (returns valid JSON by default) |
| `valid_recoding_llm_response` | `str` | Valid JSON response for recoding rules |
| `valid_indicators_llm_response` | `str` | Valid JSON response for indicators |
| `valid_table_specs_llm_response` | `str` | Valid JSON response for table specs |
| `invalid_json_llm_response` | `str` | Malformed JSON for error testing |
| `empty_llm_response` | `str` | Empty response for error testing |
| `error_llm_response` | `str` | JSON with error message |

### Usage Examples

```python
def test_with_mock_llm(mock_llm_client):
    """Test using mocked LLM client."""
    # Configure mock response
    mock_response = Mock()
    mock_response.content = '{"result": "success"}'
    mock_llm_client.invoke.return_value = mock_response

    # Test code that uses LLM client
    result = my_function_that_uses_llm(mock_llm_client)
    assert result == "success"

def test_with_valid_response(valid_recoding_llm_response):
    """Test using valid LLM response string."""
    import json
    data = json.loads(valid_recoding_llm_response)
    assert "recoding_rules" in data
```

---

## PSPP Output Fixtures

| Fixture | Returns | Description |
|---------|---------|-------------|
| `mock_pspp_wrapper` | `Mock` | Mock PSPP wrapper (returns success by default) |
| `sample_pspp_recoding_syntax` | `str` | Sample PSPP RECODE syntax |
| `sample_pspp_table_syntax` | `str` | Sample PSPP CTABLES syntax |
| `sample_pspp_output` | `Dict` | Sample successful PSPP execution result |
| `sample_pspp_error` | `Dict` | Sample PSPP error result |

### Usage Examples

```python
def test_with_pspp_syntax(sample_pspp_recoding_syntax):
    """Test using sample PSPP syntax."""
    assert "RECODE" in sample_pspp_recoding_syntax
    assert "age_group" in sample_pspp_recoding_syntax

def test_with_pspp_output(sample_pspp_output):
    """Test using sample PSPP output."""
    assert sample_pspp_output["exit_code"] == 0
    assert sample_pspp_output["output_file"] is not None
```

---

## Validation Result Fixtures

| Fixture | Returns | Description |
|---------|---------|-------------|
| `valid_validation_result` | `ValidationResult` | Valid result with no errors |
| `invalid_validation_result` | `ValidationResult` | Invalid result with errors |
| `validation_result_warnings_only` | `ValidationResult` | Valid result with warnings |
| `validation_result_at_max_iterations` | `ValidationResult` | Result at max iterations |

### Usage Examples

```python
def test_with_valid_result(valid_validation_result):
    """Test using valid validation result."""
    assert valid_validation_result.is_valid is True
    assert len(valid_validation_result.errors) == 0

def test_with_invalid_result(invalid_validation_result):
    """Test using invalid validation result."""
    assert invalid_validation_result.is_valid is False
    assert len(invalid_validation_result.errors) > 0
```

---

## Mock Fixtures

| Fixture | Returns | Description |
|---------|---------|-------------|
| `mock_read_spss_file` | `Mock` | Mock pyreadstat.read_sav function |
| `mock_dependencies` | Context Manager | Mocks all external dependencies for E2E tests |

### Usage Examples

```python
def test_with_mock_read(mock_read_spss_file):
    """Test using mocked SPSS file reading."""
    # Use mock directly
    df, metadata = mock_read_spss_file("dummy_path.sav")
    assert df is not None
    assert len(df) == 50

def test_with_mock_dependencies(mock_dependencies):
    """Test with all dependencies mocked."""
    from agent.nodes.phase1_extraction import extract_spss_node
    state = sample_state
    result = extract_spss_node(state)
    assert result["raw_data"] is not None
```

---

## Fixture Composition

Fixtures can be composed together for complex test scenarios:

```python
def test_with_multiple_fixtures(
    sample_dataframe,
    valid_recoding_rules,
    mock_llm_client,
    temp_output_dir
):
    """Test combining multiple fixtures."""
    # Use sample data
    df = sample_dataframe

    # Use valid recoding rules
    rules = valid_recoding_rules

    # Configure LLM mock
    mock_response = Mock()
    mock_response.content = '{"status": "success"}'
    mock_llm_client.invoke.return_value = mock_response

    # Use temp directory
    output_file = temp_output_dir / "output.json"

    # Test code here
    assert df is not None
    assert rules is not None
```

---

## Creating Custom Fixtures

You can create project-specific fixtures in local test files:

```python
# In your test file (e.g., tests/test_my_feature.py)
import pytest

@pytest.fixture
def custom_state(sample_state):
    """Create a custom state based on sample_state."""
    state = sample_state.copy()
    state["custom_field"] = "custom_value"
    return state

@pytest.fixture
def custom_dataframe(sample_dataframe):
    """Create a custom dataframe based on sample_dataframe."""
    df = sample_dataframe.copy()
    df["new_column"] = "test"
    return df
```

---

## Best Practices

1. **Use appropriate fixtures for test type**:
   - Use `small_dataframe` for quick unit tests
   - Use `sample_dataframe` for standard tests
   - Use `large_dataframe` for performance tests only

2. **Mock external dependencies**:
   - Use `mock_llm_client` for LLM-dependent tests
   - Use `mock_pspp_wrapper` for PSPP-dependent tests
   - Use `mock_dependencies` for E2E tests

3. **Use state fixtures for workflow testing**:
   - Use `sample_state` for Step 0-3 tests
   - Use `recoding_state` for Step 4-8 tests
   - Use appropriate phase state for each workflow phase

4. **Use error fixtures for error handling tests**:
   - Use `invalid_*` fixtures to test validation
   - Use `*_error` fixtures to test error scenarios
   - Use `state_with_errors` to test error accumulation

5. **Clean up temporary resources**:
   - `temp_output_dir` and `temp_checkpoint_db` auto-cleanup after tests
   - No manual cleanup needed

---

## Fixture Quick Reference

### Common Fixtures

```python
# Data
sample_dataframe        # Standard 50-row dataset
small_dataframe         # Quick 10-row dataset
large_dataframe         # Performance 500-row dataset
edge_case_dataframe     # Edge cases (missing, outliers)

# Metadata
sample_metadata         # SPSS metadata from .sav file
variable_centered_metadata  # Variable-centered format
filtered_metadata       # After filtering (Step 3)
new_metadata            # After recoding (Step 8)

# State
sample_state            # Initial state (Step 0)
extraction_state        # After extraction (Step 3)
recoding_state          # After recoding (Step 8)
indicator_state         # After indicators (Step 11)
table_state             # After tables (Step 16)
statistics_state        # After statistics (Step 18)
filtering_state         # After filtering (Step 20)
presentation_state      # Final state (Step 22)

# Artifacts
valid_recoding_rules    # Valid recoding JSON
invalid_recoding_rules  # Invalid recoding JSON
valid_indicators        # Valid indicators JSON
invalid_indicators      # Invalid indicators JSON
valid_table_specs       # Valid table specs JSON
invalid_table_specs     # Invalid table specs JSON

# Mocks
mock_llm_client         # Mocked LLM client
mock_pspp_wrapper       # Mocked PSPP wrapper
mock_read_spss_file     # Mocked SPSS reader
mock_dependencies       # Mocked all dependencies (E2E)

# Responses
valid_recoding_llm_response   # Valid LLM JSON string
invalid_json_llm_response     # Invalid JSON string
empty_llm_response            # Empty string

# Results
valid_validation_result       # Valid ValidationResult
invalid_validation_result     # Invalid ValidationResult
```

### Finding Fixtures

To see all available fixtures, run:

```bash
pytest --fixtures
```

To see fixtures in a specific file:

```bash
pytest --fixtures tests/conftest.py
```
