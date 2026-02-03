# Testing Structure

This document defines the project testing structure, organization, and file locations.

---

## Table of Contents

1. [Directory Structure](#1-directory-structure)
2. [Test Categories](#2-test-categories)
3. [Test Outputs and Reports](#3-test-outputs-and-reports)
4. [Test Fixtures](#4-test-fixtures)
5. [Running Tests](#5-running-tests)
6. [Configuration](#6-configuration)

---

## 1. Directory Structure

### Project Root

```
/home/admin/workspaces/datachat/
├── pytest.ini                      # Pytest configuration
├── .coveragerc                     # Coverage configuration
│
├── tests/                          # Test source code
│   ├── conftest.py                 # Shared fixtures
│   ├── unit/                       # Fast, isolated tests
│   ├── integration/                # Component integration tests
│   ├── e2e/                        # End-to-end workflow tests
│   ├── nodes/                      # Phase-specific node tests
│   ├── validation/                 # Validation module tests
│   ├── api/                        # API endpoint tests
│   ├── performance/                # Performance tests
│   ├── security/                   # Security tests
│   ├── web/                        # Web UI tests
│   └── fixtures/                   # Test data files
│
├── test-results/                   # Test outputs (gitignored)
│   ├── htmlcov/                    # Coverage HTML reports
│   ├── .coverage                   # Coverage data
│   ├── junit/                      # JUnit XML reports
│   ├── screenshots/                # E2E screenshots
│   └── playwright-report/          # Playwright HTML reports
│
└── playwright-mcp/                 # MCP-specific results (gitignored)
    ├── results/                    # Test results
    └── screenshots/                # Screenshots
```

### tests/ Directory Detail

```
tests/
├── conftest.py                     # Pytest configuration and shared fixtures
│
├── unit/                           # Fast, isolated component tests
│   ├── test_state.py               # State/TypedDict validation
│   ├── test_edges.py               # Conditional routing logic
│   ├── test_nodes.py               # Individual node functions
│   ├── test_utils.py               # Utility functions
│   ├── test_styling.py             # Styling utilities
│   ├── test_config.py              # Configuration loading
│   └── test_validation.py          # Validation functions
│
├── integration/                    # Component integration tests
│   ├── test_pspp_integration.py    # PSPP wrapper integration
│   ├── test_llm_integration.py     # LLM client integration
│   ├── test_llm_providers_integration.py  # LLM provider switching
│   ├── test_llm_prompts.py         # LLM prompt validation
│   ├── test_graph_integration.py   # Graph execution integration
│   ├── test_file_io_integration.py # File I/O operations
│   ├── test_checkpoint_integration.py # State persistence
│   └── test_output_generation.py  # Output file generation
│
├── e2e/                           # End-to-end workflow tests
│   ├── test_e2e_workflow.py        # Full workflow execution
│   ├── test_e2e_workflow_simple.py # Simplified workflow
│   ├── test_e2e_complete_workflow.py # Complete workflow
│   ├── test_e2e_automatic_mode.py  # Automatic execution mode
│   ├── test_e2e_human_review.py    # Human review workflow
│   ├── test_e2e_rejection_feedback.py # Rejection handling
│   ├── test_e2e_llm_providers.py   # Multi-provider tests
│   ├── test_e2e_error_recovery.py  # Error handling
│   └── test_e2e_practical.py       # Real-world scenarios
│
├── nodes/                         # Phase-specific node tests
│   ├── test_phase1_extraction.py   # Steps 1-3
│   ├── test_phase2_recoding.py     # Steps 4-8
│   ├── test_phase3_indicators.py   # Steps 9-11
│   ├── test_phase4_tables.py       # Steps 12-16
│   ├── test_phase5_statistics.py   # Steps 17-18
│   ├── test_phase6_filtering.py    # Steps 19-20
│   ├── test_phase7_powerpoint.py   # Step 21
│   └── test_phase8_html_dashboard.py # Step 22
│
├── validation/                    # Validation module tests
│   ├── test_validation_recoding.py     # Recoding validation
│   ├── test_validation_indicators.py   # Indicator validation
│   └── test_validation_tables.py       # Table validation
│
├── api/                           # API/Server tests
│   └── test_server.py             # FastAPI server endpoints
│
├── performance/                   # Performance and load tests
├── security/                      # Security tests
├── web/                           # Web interface tests
│
└── fixtures/                      # Test data and shared fixtures
    ├── sample_data.sav            # Standard test dataset
    ├── small_data.sav             # Small dataset for quick tests
    ├── large_data.sav             # Large dataset for scale testing
    └── edge_case_data.sav         # Edge case scenarios
```

---

## 2. Test Categories

| Category | Location | Speed | Dependencies | When to Run |
|----------|----------|-------|--------------|-------------|
| **Unit** | `tests/unit/` | Seconds | Mocked | During development |
| **Integration** | `tests/integration/` | Minutes | Real services | Before commit |
| **E2E** | `tests/e2e/` | 5-15 min | Real data/services | Before merge |
| **Nodes** | `tests/nodes/` | Minutes | May use LLM | When modifying nodes |
| **Validation** | `tests/validation/` | Fast-Medium | None | When changing validation |
| **API** | `tests/api/` | Minutes | Server running | Before deploying |

---

## 3. Test Outputs and Reports

### Configuration vs Output Files

| Type | Location | Git Tracked |
|------|----------|-------------|
| `pytest.ini` | Project root | Yes |
| `.coveragerc` | Project root | Yes |
| `test-results/` | Project root | No |
| `playwright-mcp/` | Project root | No |

### `.gitignore` Entries

```gitignore
# Test outputs (generated)
test-results/
playwright-mcp/

# Pytest cache
.pytest_cache/
```

### Report Generation

```bash
# Coverage report
pytest --cov=agent --cov-report=html:test-results/htmlcov

# JUnit XML for CI/CD
pytest --junitxml=test-results/junit/report.xml
```

---

## 4. Test Fixtures

### Key Fixtures (conftest.py)

| Fixture | Purpose |
|---------|---------|
| `mock_state` | Mock agent state |
| `mock_llm_response` | Mock LLM API responses |
| `temp_output_dir` | Temporary directory for outputs |
| `sample_sav_file` | Path to sample .sav file |
| `pspp_available` | Skip tests if PSPP not installed |

### Test Data Files (tests/fixtures/)

| File | Purpose |
|------|---------|
| `sample_data.sav` | Standard test dataset |
| `small_data.sav` | Fast unit tests |
| `large_data.sav` | Performance testing |
| `edge_case_data.sav` | Edge cases |

---

## 5. Running Tests

### By Category

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v

# Specific node test
pytest tests/nodes/test_phase2_recoding.py -v

# All except E2E
pytest tests/ --ignore=tests/e2e/ -v
```

### Execution Order

1. **During development:** `pytest tests/unit/ -v`
2. **Before commit:** `pytest tests/unit/ tests/integration/ -v`
3. **Before merge:** Full suite including E2E
4. **CI/CD:** All tests in parallel

### Pytest Marks

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.e2e
def test_full_workflow():
    pass
```

```bash
# Run by mark
pytest -m unit
pytest -m "not e2e"
```

---

## 6. Configuration

### pytest.ini (Project Root)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov-report=html:test-results/htmlcov
    --cov-report=term-missing
    --junitxml=test-results/junit/report.xml
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow-running tests
```

### .coveragerc (Project Root)

```ini
[run]
source = agent
omit =
    tests/*
    */__pycache__/*
    */.venv/*
    */site-packages/*
parallel = True
branch = True

[report]
precision = 2
show_missing = True
skip_covered = False
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

---

## Related Documents

| Document | Content |
|----------|---------|
| **[Project Structure](./project-structure.md)** | Overall project directory organization |
| **[System Configuration](./system-configuration.md)** | Test configuration and environment setup |
| **[LLM Integration Tests Guide](./llm-integration-tests-guide.md)** | LLM-specific testing guidelines |
