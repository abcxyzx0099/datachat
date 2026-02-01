# Test Coverage Guide

This guide explains how to use and configure test coverage reporting for the DataChat SPSS Analyzer project.

## Table of Contents

- [Overview](#overview)
- [Running Coverage Reports](#running-coverage-reports)
- [Viewing Coverage Reports](#viewing-coverage-reports)
- [Coverage Configuration](#coverage-configuration)
- [Coverage Thresholds](#coverage-thresholds)
- [CI/CD Integration](#cicd-integration)
- [Excluding Code from Coverage](#excluding-code-from-coverage)
- [Best Practices](#best-practices)

## Overview

This project uses **coverage.py** with **pytest-cov** to measure test coverage. Coverage is tracked for:
- `agent/` - Core workflow and node implementations
- `utils/` - Utility functions and helpers

### What Gets Measured

- **Line Coverage**: Percentage of executable lines that were executed
- **Branch Coverage**: Percentage of conditional branches that were taken (both `if` and `else` paths)

### Current Threshold

- **Minimum Coverage**: 70% (build fails if below this threshold)
- **Goal**: 80%+ for new code

## Running Coverage Reports

### Quick Start (Recommended)

Run tests with coverage:

```bash
# Run all tests with coverage (HTML + terminal + JSON)
pytest

# Or explicitly with coverage module
coverage run -m pytest
coverage report
coverage html
```

### Detailed Commands

```bash
# Run pytest with all coverage reports (configured in pyproject.toml)
pytest

# Run tests with coverage (terminal only)
pytest --cov=agent --cov=utils --cov-report=term-missing

# Run tests with coverage (HTML only)
pytest --cov=agent --cov=utils --cov-report=html

# Run specific test file with coverage
pytest tests/test_graph.py --cov=agent --cov-report=term-missing

# Run with coverage and fail if below threshold
pytest --cov=agent --cov=utils --cov-fail-under=70
```

### Coverage-Only Commands

If tests are already run and you want to generate reports:

```bash
# Combine coverage data from multiple runs
coverage combine

# Generate terminal report
coverage report

# Generate HTML report
coverage html

# Generate XML report (for CI)
coverage xml

# Generate JSON report (for programmatic access)
coverage json
```

## Viewing Coverage Reports

### HTML Report (Best for Development)

1. Run tests with coverage: `pytest`
2. Open HTML report in your browser:

```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html

# Or with Python
python -m http.server 8080 --directory htmlcov
# Then visit: http://localhost:8080
```

**HTML Report Features:**
- **Color-coded files**: Green (good coverage), Red (low coverage)
- **Missing lines highlighted**: Shows which lines weren't executed
- **Test context**: Click on any line to see which tests covered it
- **Branch coverage**: Shows which conditional branches were missed

### Terminal Report

Shows summary in terminal with missing lines:

```bash
pytest --cov=agent --cov=utils --cov-report=term-missing
```

Output example:
```
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
agent/__init__.py        2      0   100%
agent/graph.py         212    101    52%   126, 141, 146-147, 295-296, ...
agent/nodes.py         180     45    75%   89-92, 145-150
--------------------------------------------------
TOTAL                   394    146    63%
```

### JSON Report

Programmatic access to coverage data:

```bash
# Generate JSON report
coverage json

# Parse with Python
python -c "import json; data=json.load(open('coverage.json')); print(f\"Coverage: {data['totals']['percent_covered']:.1f}%\")"
```

## Coverage Configuration

Configuration files (in priority order):

### 1. `.coveragerc` (Primary)

Standalone coverage configuration file:

```ini
[run]
source = agent, utils
branch = True
omit = */tests/*, */test_*.py

[report]
fail_under = 70.0
show_missing = True
```

### 2. `pyproject.toml` (Integrated)

Pytest and coverage configuration together:

```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=agent",
    "--cov=utils",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-branch",
]

[tool.coverage.run]
source = ["agent", "utils"]
branch = True
```

### Configuration Options

| Option | Purpose | Default |
|--------|---------|---------|
| `source` | Directories to measure coverage | Required |
| `omit` | Files to exclude from coverage | `*/tests/*` |
| `branch` | Enable branch coverage | `False` (we use `True`) |
| `fail_under` | Minimum coverage percentage | `70.0` |
| `show_missing` | Show missing line numbers | `True` |
| `parallel` | Combine coverage from parallel runs | `True` |

## Coverage Thresholds

### Current Thresholds

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| **Overall Coverage** | 70% | Minimum acceptable coverage |
| **New Code** | 80% | Stricter threshold for new features |
| **Branch Coverage** | 65% | Conditional branch coverage |

### Why These Thresholds?

- **70% overall**: Realistic baseline for existing codebase
- **80% new code**: Higher quality for new development
- **Branch coverage**: More accurate than line coverage

### Updating Thresholds

To change coverage thresholds, edit `.coveragerc` or `pyproject.toml`:

```toml
# In pyproject.toml
[tool.coverage.report]
fail_under = 80.0  # Change to 80%
```

### Temporarily Disabling Thresholds

For development/testing (not recommended for commits):

```bash
# Run without threshold enforcement
pytest --cov=agent --cov=utils --no-cov-on-fail
```

## CI/CD Integration

### GitHub Actions

Coverage runs automatically on:
- Every push to `main` or `develop`
- Every pull request
- Manual workflow dispatch

**Workflow Features:**
- Runs tests with coverage
- Fails if coverage drops below 70%
- Uploads coverage artifacts (HTML, XML, JSON)
- Posts coverage summary to PR comments
- Optionally uploads to Codecov

**CI Artifacts:**
- Download coverage HTML from GitHub Actions artifacts
- Retained for 30 days

### Local Development

```bash
# Run before committing
pytest

# Check coverage locally
coverage html && open htmlcov/index.html
```

## Excluding Code from Coverage

### Legitimate Exclusions

Some code should NOT be covered by tests:

1. **Debug/Development Code**
   ```python
   if DEBUG:  # pragma: no cover
       print_expensive_debug_info()
   ```

2. **Platform-Specific Code**
   ```python
   if sys.platform == "win32":  # pragma: no cover
       run_windows_only_code()
   ```

3. **Abstract Methods**
   ```python
   @abstractmethod  # Automatically excluded
   def my_abstract_method(self):
       raise NotImplementedError
   ```

4. **Type Checking Imports**
   ```python
   if TYPE_CHECKING:  # Automatically excluded
       from typing import Something
   ```

5. **Impossible-to-Reach Code**
   ```python
   def validate(x: int) -> None:
       if not isinstance(x, int):
           raise AssertionError("Should never happen")  # pragma: no cover
   ```

### How to Exclude

**Single Line:**
```python
result = expensive_operation()  # pragma: no cover
```

**Block of Code:**
```python
if some_rare_condition:  # pragma: no cover
    run_rare_code()
```

**Entire File:**
Add to `.coveragerc`:
```ini
[report]
exclude_lines =
    # ... existing exclusions ...
    @dataclass  # Exclude all dataclasses
```

### Minimal Exclusions Principle

**Do NOT exclude:**
- Complex logic that's "hard to test" (this is a code smell)
- Error handling (you SHOULD test error paths)
- Edge cases (these are important to test)

**DO exclude:**
- genuinely unreachable code (platform-specific, debug only)
- abstract methods and interfaces
- type checking blocks

## Best Practices

### 1. Run Coverage Locally Before Pushing

```bash
# Quick check
pytest --cov=agent --cov=utils --cov-report=term-missing

# Full report
pytest && open htmlcov/index.html
```

### 2. Focus on Quality, Not Just Numbers

- **70% coverage with good tests** > **90% coverage with meaningless tests**
- Test critical paths, error handling, edge cases
- Don't test getters/setters just for coverage

### 3. Use Branch Coverage

Branch coverage is more accurate than line coverage:

```python
def is_valid(x: int) -> bool:
    if x > 0:  # Line coverage: 100%, Branch coverage: 50%
        return True
    return False
```

We enable branch coverage by default (`--cov-branch`).

### 4. Review HTML Reports Regularly

HTML reports show:
- Which lines are missing coverage
- Which tests cover which lines
- Complex functions that need refactoring

### 5. Test Error Paths

Don't just test happy paths:

```python
# Good: Tests both success and failure
def test_load_file():
    result = load_file("valid.csv")
    assert result is not None

    result = load_file("missing.csv")
    assert result is None  # Test error path
```

### 6. Coverage for New Features

Aim for **80%+ coverage** on new code:
- Write tests alongside code (TDD)
- Run coverage before committing
- If coverage < 80%, add more tests or justify exclusions

### 7. Ignore Generated Code

Exclude generated files from coverage:

```ini
# In .coveragerc
[run]
omit =
    */tests/*
    */generated/*  # Auto-generated code
    */migrations/*  # Database migrations
```

### 8. Use Context Coverage

See which tests cover which lines:

```bash
pytest --cov=agent --cov-context=test
```

Then in HTML report, click any line to see the test that covered it.

## Troubleshooting

### Coverage Not Updating

```bash
# Clean coverage data
coverage erase

# Run fresh
pytest
```

### Missing Coverage Data

```bash
# Combine multiple coverage files
coverage combine

# Check data file location
coverage debug sys
```

### Slow Coverage

```bash
# Skip HTML generation during development
pytest --cov=agent --cov=utils --cov-report=term-missing

# Generate HTML only when needed
coverage html
```

### Import Errors in Coverage

```bash
# Set Python path explicitly
PYTHONPATH=. pytest --cov=agent
```

## Additional Resources

- [coverage.py Documentation](https://coverage.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Codecov Documentation](https://docs.codecov.com/)

## Summary

- **Run**: `pytest` (coverage is automatic)
- **View**: Open `htmlcov/index.html` in browser
- **Threshold**: 70% minimum, 80% for new code
- **Goal**: Quality tests, not just high numbers
