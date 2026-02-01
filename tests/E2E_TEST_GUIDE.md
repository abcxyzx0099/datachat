# E2E Test Guide

End-to-end testing guide for the complete Survey Analysis & Visualization Workflow.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Test Structure](#2-test-structure)
3. [Running Tests](#3-running-tests)
4. [Test Categories](#4-test-categories)
5. [Mock vs Real Execution](#5-mock-vs-real-execution)
6. [Troubleshooting](#6-troubleshooting)
7. [CI/CD Integration](#7-cicd-integration)

---

## 1. Overview

### 1.1 Purpose

The E2E tests verify the complete 22-step LangGraph workflow from SPSS `.sav` file input to PowerPoint and HTML outputs.

### 1.2 What Gets Tested

| Component | Coverage |
|-----------|----------|
| **Workflow Execution** | All 22 steps in correct order |
| **State Evolution** | State population through all phases |
| **Three-Node Pattern** | Generate → Validate → Review (3 cycles) |
| **Output Generation** | PowerPoint, HTML, JSON files |
| **Checkpointing** | SQLite state persistence |
| **Error Handling** | Graceful failure modes |

### 1.3 Test Files

| File | Purpose |
|------|---------|
| `tests/test_e2e_workflow.py` | Main E2E test suite |
| `tests/conftest.py` | Shared pytest fixtures |
| `tests/fixtures/sample_data.sav` | Sample SPSS file |

---

## 2. Test Structure

### 2.1 Test Class Organization

```python
test_e2e_workflow.py
├── TestCompleteWorkflowExecution      # Full workflow tests
├── TestPhaseByPhaseVerification       # Phase-specific tests
├── TestStateEvolution                 # State evolution tests
├── TestCheckpointVerification         # Checkpoint persistence tests
├── TestOutputFileVerification         # Output file validation tests
├── TestE2EECases                      # Edge case tests
├── TestMockVsRealExecution            # Mock vs real tests
└── TestVerificationChecklist          # Comprehensive checklist
```

### 2.2 Test Fixtures

| Fixture | Purpose |
|---------|---------|
| `temp_output_dir` | Temporary directory for test outputs |
| `temp_checkpoint_db` | Temporary SQLite database for checkpoints |
| `e2e_config` | Test configuration with auto-approval |
| `sample_sav_file` | Path to sample_data.sav |
| `mock_dependencies` | Mocked LLM, PSPP, file I/O |
| `mock_llm_responses` | Predefined LLM responses |
| `mock_pspp_results` | Predefined PSPP execution results |

---

## 3. Running Tests

### 3.1 Quick Start

```bash
# Run all E2E tests with mocked dependencies (fast)
pytest tests/test_e2e_workflow.py -v

# Run specific test class
pytest tests/test_e2e_workflow.py::TestCompleteWorkflowExecution -v

# Run specific test
pytest tests/test_e2e_workflow.py::TestCompleteWorkflowExecution::test_complete_workflow_from_step_0_to_step_22 -v
```

### 3.2 Running with Markers

```bash
# Run only E2E tests
pytest -m e2e -v

# Run only slow tests
pytest -m slow -v

# Run E2E + slow tests
pytest -m "e2e and slow" -v
```

### 3.3 Running with Coverage

```bash
# Run with coverage report
pytest tests/test_e2e_workflow.py --cov=agent --cov-report=html

# Run with coverage for specific module
pytest tests/test_e2e_workflow.py --cov=agent.graph --cov-report=term-missing
```

### 3.4 Verbose Output

```bash
# Very verbose (see all print statements)
pytest tests/test_e2e_workflow.py -vv -s

# Show test execution time
pytest tests/test_e2e_workflow.py --durations=10
```

---

## 4. Test Categories

### 4.1 Complete Workflow Execution Tests

**Purpose**: Verify full workflow from Step 0 to Step 22.

**Key Tests**:
- `test_complete_workflow_from_step_0_to_step_22` - Full execution
- `test_all_22_steps_execute_in_correct_order` - Step sequence
- `test_workflow_with_sample_survey_file` - Sample file processing
- `test_workflow_produces_valid_outputs` - Output generation

**Verification**:
```python
assert result.get("current_step", 0) >= 21
assert result.get("powerpoint_file") is not None
assert result.get("html_dashboard_file") is not None
```

### 4.2 Phase-by-Phase Verification Tests

**Purpose**: Verify each of the 8 phases executes correctly.

**Phases Tested**:
1. **Phase 1 (Steps 1-3)**: Extraction & Preparation
2. **Phase 2 (Steps 4-8)**: New Dataset Generation
3. **Phase 3 (Steps 9-11)**: Indicator Generation
4. **Phase 4 (Steps 12-16)**: Cross-Table Generation
5. **Phase 5 (Steps 17-18)**: Statistical Analysis
6. **Phase 6 (Steps 19-20)**: Significant Tables Selection
7. **Phase 7 (Step 21)**: PowerPoint Generation
8. **Phase 8 (Step 22)**: HTML Dashboard Generation

**Example Test**:
```python
def test_phase_1_extraction_and_preparation(self, ...):
    result = graph.invoke(initial_state, config)

    assert result.get("raw_data") is not None
    assert result.get("variable_centered_metadata") is not None
    assert result.get("filtered_metadata") is not None
```

### 4.3 State Evolution Verification Tests

**Purpose**: Verify state evolves correctly through all phases.

**State Fields Verified**:
- `InputState`: `input_file_path`, `config`
- `ExtractionState`: `raw_data`, `original_metadata`, `filtered_metadata`
- `RecodingState`: `recoding_rules`, `recoding_approved`, `new_metadata`
- `IndicatorState`: `indicators`, `indicators_approved`
- `CrossTableState`: `table_specifications`, `table_specs_approved`
- `StatisticalAnalysisState`: `statistical_summary`
- `FilteringState`: `filtered_tables`
- `PresentationState`: `powerpoint_file`, `html_dashboard_file`

**Example Verification**:
```python
assert result.get("input_file_path") == sample_sav_file
assert result.get("recoding_approved") == True
assert result.get("indicators_approved") == True
assert result.get("table_specs_approved") == True
```

### 4.4 Output File Verification Tests

**Purpose**: Verify all output files are generated and valid.

**Outputs Verified**:
| Output | Path | Format |
|--------|------|--------|
| PowerPoint | `output/presentation.pptx` | `.pptx` |
| HTML Dashboard | `output/dashboard.html` | `.html` |
| Significant Tables | `output/significant_tables.json` | `.json` |
| Statistical Summary | `output/statistical_summary.json` | `.json` |
| Execution Log | `output/logs/` | `.txt` |

**Example Test**:
```python
powerpoint_path = result.get("powerpoint_file")
assert powerpoint_path is not None
assert powerpoint_path.endswith(".pptx")
assert Path(powerpoint_path).exists()
```

---

## 5. Mock vs Real Execution

### 5.1 Mock-Based Tests (Default)

**Use Case**: CI/CD pipelines, fast development iteration

**What Gets Mocked**:
- **LLM Client**: Returns predefined valid JSON responses
- **PSPP Execution**: Returns successful exit codes
- **File I/O**: Simulates .sav file reading
- **Subprocess**: Simulates Python script execution

**Advantages**:
- ✅ Fast (no external dependencies)
- ✅ Deterministic (same results every time)
- ✅ No API costs
- ✅ Works offline
- ✅ CI/CD friendly

**Example**:
```python
@pytest.fixture
def mock_dependencies(mock_llm_responses, mock_pspp_results):
    with patch('pyreadstat.read_sav') as mock_read, \
         patch('agent.nodes.phase2_recoding.get_llm_client') as mock_llm, \
         patch('agent.nodes.phase2_recoding.run_pspp') as mock_pspp:
        # Configure mocks
        mock_read.return_value = (sample_dataframe, Mock(**sample_metadata))
        mock_llm_client.invoke.return_value = mock_response
        mock_pspp.run_pspp.return_value = {"exit_code": 0, ...}
        yield
```

### 5.2 Real Dependency Tests (Optional)

**Use Case**: Integration testing, pre-release validation

**Requirements**:
- Valid LLM API credentials (set `OPENAI_API_KEY` or similar)
- PSPP installed on system
- Actual `.sav` file

**How to Run**:
```bash
# Set API key
export OPENAI_API_KEY="your-api-key"

# Run without mocks (will use real dependencies)
pytest tests/test_e2e_workflow.py::TestMockVsRealExecution::test_real_dependencies_e2e_integration -v --no-mock
```

**Note**: Most E2E tests use mocks by default for CI/CD compatibility.

---

## 6. Troubleshooting

### 6.1 Common Issues

#### Issue: Tests Fail with "ModuleNotFoundError"

**Solution**:
```bash
# Install dependencies
pip install -e .

# Or install test dependencies
pip install pytest pytest-cov
```

#### Issue: Tests Fail with "FileNotFoundError: sample_data.sav"

**Solution**:
```bash
# Verify sample file exists
ls -la tests/fixtures/sample_data.sav

# If missing, create it using the script
python tests/fixtures/create_sample_sav.py
```

#### Issue: Tests Timeout

**Solution**:
```bash
# Increase timeout
pytest tests/test_e2e_workflow.py --timeout=300

# Or skip slow tests
pytest tests/test_e2e_workflow.py -m "not slow"
```

#### Issue: Checkpoint Database Locked

**Solution**:
```bash
# Remove existing checkpoint database
rm -f checkpoints.db

# Or use unique thread IDs in tests
thread_id = f"test-{uuid.uuid4()}"
```

### 6.2 Debugging Tips

**Enable Verbose Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Print State During Execution**:
```python
for event in graph.stream(initial_state, config, mode="values"):
    print(f"Step: {event.get('current_step')}")
    print(f"State: {event}")
```

**Inspect Checkpoints**:
```python
checkpoints = list(graph.get_state_history(config))
for cp in checkpoints:
    print(f"Checkpoint: {cp.config}")
```

---

## 7. CI/CD Integration

### 7.1 GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov

      - name: Run E2E tests
        run: |
          pytest tests/test_e2e_workflow.py -v --cov=agent

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 7.2 Pre-Commit Hook

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash

# Run E2E tests before committing
pytest tests/test_e2e_workflow.py -v

if [ $? -ne 0 ]; then
    echo "E2E tests failed. Commit aborted."
    exit 1
fi
```

### 7.3 Test Automation

**Run on every commit**:
```bash
# In .github/workflows/tests.yml
pytest tests/test_e2e_workflow.py -m "not slow"
```

**Run nightly with full tests**:
```bash
# In .github/workflows/nightly.yml
pytest tests/test_e2e_workflow.py -v --timeout=600
```

---

## 8. Success Criteria

### 8.1 Test Requirements

| Requirement | Test |
|-------------|------|
| Complete workflow executes | `test_complete_workflow_from_step_0_to_step_22` |
| All 22 steps verified | `test_all_22_steps_execute_in_correct_order` |
| All outputs generated | `test_workflow_produces_valid_outputs` |
| State evolution correct | `test_state_evolution_through_all_phases` |
| Mock-based for CI/CD | `test_mock_based_e2e_for_ci_cd` |

### 8.2 Passing Tests

```bash
# All E2E tests pass
pytest tests/test_e2e_workflow.py -v

# Expected output:
# tests/test_e2e_workflow.py::TestCompleteWorkflowExecution::test_complete_workflow_from_step_0_to_step_22 PASSED
# tests/test_e2e_workflow.py::TestCompleteWorkflowExecution::test_all_22_steps_execute_in_correct_order PASSED
# tests/test_e2e_workflow.py::TestPhaseByPhaseVerification::test_phase_1_extraction_and_preparation PASSED
# ...
# ======================= 50 passed in 30.45s =======================
```

### 8.3 Verification Checklist

Run the comprehensive checklist test:
```bash
pytest tests/test_e2e_workflow.py::TestVerificationChecklist::test_e2e_verification_checklist -v -s
```

Expected output:
```
============================================================
E2E VERIFICATION CHECKLIST
============================================================
✓ PASS: workflow_executes
✓ PASS: steps_verified
✓ PASS: outputs_generated
✓ PASS: state_evolution_correct
✓ PASS: mock_compatible
============================================================
```

---

## 9. Additional Resources

### 9.1 Related Documentation

- [Data Flow](../docs/data-flow.md) - Complete workflow specification
- [State Management](../docs/state-management.md) - State evolution details
- [System Architecture](../docs/system-architecture.md) - Checkpointing architecture

### 9.2 Test Utilities

```python
# Create sample state for testing
from agent.state import create_initial_state
state = create_initial_state("tests/fixtures/sample_data.sav", config)

# Build graph
from agent.graph import build_graph
graph = build_graph(checkpointer_path=":memory:")

# Run workflow
result = graph.invoke(state, {"configurable": {"thread_id": "test"}})
```

### 9.3 Mocking Examples

```python
# Mock LLM response
from unittest.mock import patch, Mock

with patch('agent.nodes.phase2_recoding.get_llm_client') as mock_llm:
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = '{"recoding_rules": []}'
    mock_client.invoke.return_value = mock_response
    mock_llm.return_value = mock_client

    # Run test...
```

---

## Appendix: Quick Reference

### Run All E2E Tests
```bash
pytest tests/test_e2e_workflow.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_e2e_workflow.py::TestCompleteWorkflowExecution -v
```

### Run with Coverage
```bash
pytest tests/test_e2e_workflow.py --cov=agent --cov-report=html
```

### Run Only Fast Tests
```bash
pytest tests/test_e2e_workflow.py -m "not slow"
```

### Debug with pdb
```bash
pytest tests/test_e2e_workflow.py --pdb
```

### List All Tests
```bash
pytest tests/test_e2e_workflow.py --collect-only
```
