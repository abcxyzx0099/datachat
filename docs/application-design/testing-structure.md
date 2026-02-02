# Testing Structure

This document defines the recommended project testing structure, organization, and file locations.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Current vs Recommended Structure](#2-current-vs-recommended-structure)
3. [Test Categories](#3-test-categories)
4. [Test Fixtures and Data](#4-test-fixtures-and-data)
5. [Test Execution Patterns](#5-test-execution-patterns)
6. [Migration Plan](#6-migration-plan)

---

## 1. Overview

The testing structure should provide clear separation between different test types, making it easy to:
- Run fast unit tests during development
- Run integration tests for component validation
- Run E2E tests for full workflow validation
- Identify which tests to run when changing specific components

---

## 2. Current vs Recommended Structure

### 2.1 Current Structure

```
tests/
├── conftest.py
├── test_*.py                       # ~29 files mixed together
├── fixtures/
├── performance/
├── security/
├── web/
└── playwright-mcp/                 # Test results (misplaced)
```

**Issues with current structure:**
- Flat organization with ~29 test files at root level
- Unit, integration, and E2E tests intermingled
- No clear distinction between test types
- Test artifacts (`playwright-mcp/`) stored with source code

### 2.2 Recommended Structure

```
tests/
├── conftest.py                     # Pytest configuration and shared fixtures
│
├── unit/                           # Fast, isolated component tests
│   ├── __init__.py
│   ├── test_state.py              # State/TypedDict validation
│   ├── test_edges.py              # Conditional routing logic
│   ├── test_nodes.py              # Individual node functions
│   ├── test_utils.py              # Utility functions
│   ├── test_styling.py            # Styling utilities
│   ├── test_config.py             # Configuration loading
│   └── test_validation.py         # Validation functions
│
├── integration/                    # Component integration tests
│   ├── __init__.py
│   ├── test_pspp_integration.py   # PSPP wrapper integration
│   ├── test_llm_integration.py    # LLM client integration
│   ├── test_llm_providers_integration.py  # LLM provider switching
│   ├── test_llm_prompts.py        # LLM prompt validation
│   ├── test_graph_integration.py  # Graph execution integration
│   ├── test_file_io_integration.py # File I/O operations
│   ├── test_checkpoint_integration.py # State persistence
│   └── test_output_generation.py  # Output file generation
│
├── e2e/                           # End-to-end workflow tests
│   ├── __init__.py
│   ├── test_e2e_workflow.py       # Full workflow execution
│   ├── test_e2e_workflow_simple.py # Simplified workflow
│   ├── test_e2e_complete_workflow.py # Complete workflow with all phases
│   ├── test_e2e_automatic_mode.py # Automatic execution mode
│   ├── test_e2e_human_review.py   # Human review workflow
│   ├── test_e2e_rejection_feedback.py # Rejection and feedback handling
│   ├── test_e2e_llm_providers.py  # Multi-provider E2E tests
│   ├── test_e2e_error_recovery.py # Error handling and recovery
│   └── test_e2e_practical.py      # Real-world scenario tests
│
├── nodes/                         # Phase-specific node tests
│   ├── __init__.py
│   ├── test_phase1_extraction.py  # Extraction node (Steps 1-3)
│   ├── test_phase2_recoding.py    # Recoding node (Steps 4-8)
│   ├── test_phase3_indicators.py  # Indicators node (Steps 9-11)
│   ├── test_phase4_tables.py      # Tables node (Steps 12-16)
│   ├── test_phase5_statistics.py  # Statistics node (Steps 17-18)
│   ├── test_phase6_filtering.py   # Filtering node (Steps 19-20)
│   ├── test_phase7_powerpoint.py  # PowerPoint node (Step 21)
│   └── test_phase8_html_dashboard.py # Dashboard node (Step 22)
│
├── validation/                    # Validation module tests
│   ├── __init__.py
│   ├── test_validation_recoding.py    # Recoding validation
│   ├── test_validation_indicators.py  # Indicator validation
│   └── test_validation_tables.py      # Table validation
│
├── api/                           # API/Server tests
│   ├── __init__.py
│   └── test_server.py            # FastAPI server endpoints
│
├── performance/                   # Performance and load tests
│   └── (performance test files)
│
├── security/                      # Security tests
│   └── (security test files)
│
├── web/                           # Web interface tests
│   └── (web UI test files)
│
└── fixtures/                      # Test data and shared fixtures
    ├── __init__.py
    ├── sample_data.sav            # Standard test dataset
    ├── small_data.sav             # Small dataset for quick tests
    ├── large_data.sav             # Large dataset for scale testing
    └── edge_case_data.sav         # Edge case scenarios
```

---

## 3. Test Categories

### 3.1 Unit Tests (`tests/unit/`)

**Purpose:** Test individual functions and classes in isolation

**Characteristics:**
- Fast execution (seconds)
- No external dependencies (mocked LLM, PSPP)
- Test one thing at a time
- Run frequently during development

**Examples:**
- State class validation
- Edge routing logic
- Individual node functions
- Utility functions

### 3.2 Integration Tests (`tests/integration/`)

**Purpose:** Test interactions between components

**Characteristics:**
- Medium execution time (minutes)
- May use real external services (PSPP, LLM)
- Test component boundaries
- Run before committing changes

**Examples:**
- PSPP wrapper integration
- LLM client integration
- Graph execution with multiple nodes
- File I/O operations

### 3.3 E2E Tests (`tests/e2e/`)

**Purpose:** Test complete workflows from start to finish

**Characteristics:**
- Longer execution time (5-15 minutes)
- Use real data and services
- Test user-facing behavior
- Run before releases/merges

**Examples:**
- Complete survey analysis workflow
- Human review workflow
- Error recovery scenarios
- Multi-provider testing

### 3.4 Node Tests (`tests/nodes/`)

**Purpose:** Test individual phase nodes in depth

**Characteristics:**
- Medium execution time
- May use real LLM for node-specific logic
- Test node input/output contracts
- Run when modifying specific nodes

### 3.5 Validation Tests (`tests/validation/`)

**Purpose:** Test validation logic for rules and specifications

**Characteristics:**
- Fast to medium execution
- Test validation patterns
- Ensure data integrity

### 3.6 API Tests (`tests/api/`)

**Purpose:** Test FastAPI server endpoints

**Characteristics:**
- Medium execution time
- Test HTTP endpoints
- Validate request/response handling

---

## 4. Test Fixtures and Data

### 4.1 fixtures/ Directory

Contains test data files and pytest fixtures:

| File/Type | Purpose |
|-----------|---------|
| `sample_data.sav` | Standard test dataset (typical survey) |
| `small_data.sav` | Small dataset for fast unit tests |
| `large_data.sav` | Large dataset for performance testing |
| `edge_case_data.sav` | Edge cases (missing values, single variable, etc.) |
| `conftest.py` | Shared pytest fixtures |

### 4.2 Key Fixtures (in conftest.py)

| Fixture | Purpose |
|---------|---------|
| `mock_state` | Mock agent state for testing |
| `mock_llm_response` | Mock LLM API responses |
| `temp_output_dir` | Temporary directory for test outputs |
| `sample_sav_file` | Path to sample .sav file |
| `pspp_available` | Skip tests if PSPP not installed |

---

## 5. Test Execution Patterns

### 5.1 Running Tests by Category

```bash
# Run only unit tests (fastest)
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run E2E tests (slowest, most comprehensive)
pytest tests/e2e/

# Run specific node tests
pytest tests/nodes/test_phase2_recoding.py

# Run all tests except E2E
pytest tests/ --ignore=tests/e2e/
```

### 5.2 Test Execution Order

For efficient development:

1. **During development:** Run `pytest tests/unit/ -v`
2. **Before commit:** Run `pytest tests/unit/ tests/integration/ -v`
3. **Before merge:** Run full suite including E2E
4. **CI/CD:** Run all tests in parallel

### 5.3 Pytest Marks for Organization

```python
# In test files
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.e2e
def test_full_workflow():
    pass

# Run by mark
pytest -m unit           # Only unit tests
pytest -m "not e2e"      # All except E2E
```

---

## 6. Migration Plan

### 6.1 Recommended Migration Steps

1. **Create new directories**
   ```bash
   mkdir -p tests/{unit,integration,e2e,nodes,validation,api}
   touch tests/{unit,integration,e2e,nodes,validation,api}/__init__.py
   ```

2. **Move test files** (based on current file names)

   | Current File | Target Directory |
   |--------------|------------------|
   | `test_state.py` | `unit/` |
   | `test_edges.py` | `unit/` |
   | `test_nodes.py` | `unit/` |
   | `test_utils.py` | `unit/` |
   | `test_config.py` | `unit/` |
   | `test_pspp_integration.py` | `integration/` |
   | `test_llm_integration.py` | `integration/` |
   | `test_graph_integration.py` | `integration/` |
   | `test_e2e_*.py` | `e2e/` |
   | `test_phase*_*.py` | `nodes/` |
   | `test_validation_*.py` | `validation/` |
   | `test_server.py` | `api/` |

3. **Move test artifacts**
   ```bash
   # Move playwright results to output/
   mv tests/playwright-mcp/ output/playwright-results/
   ```

4. **Update import paths** in test files (if any relative imports)

5. **Update CI/CD** to run tests by category

### 6.2 Backward Compatibility

During migration, keep root-level `conftest.py` to ensure pytest can discover tests in subdirectories.

---

## Related Documents

| Document | Content |
|----------|---------|
| **[Project Structure](./project-structure.md)** | Overall project directory organization |
| **[System Configuration](./system-configuration.md)** | Test configuration and environment setup |
| **[LLM Integration Tests Guide](./llm-integration-tests-guide.md)** | LLM-specific testing guidelines |
