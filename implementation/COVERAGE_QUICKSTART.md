# Coverage Quick Start

Quick reference for running and viewing test coverage.

## Run Tests with Coverage

```bash
# Run all tests with coverage (recommended)
pytest

# Run specific test file
pytest tests/test_state.py

# Run with terminal output only
pytest --cov-report=term-missing

# Run without HTML (faster)
pytest --cov-report=term
```

## View Coverage Reports

### HTML Report (Best for Development)
```bash
pytest
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Terminal Report
```bash
pytest --cov-report=term-missing
```

## Coverage Thresholds

- **Current Baseline**: 69.6%
- **Minimum Threshold**: 69%
- **Build Fails**: If coverage drops below 69%
- **Goal**: 70% overall, 80% for new code

## Configuration Files

- `.coveragerc` - Coverage.py configuration
- `pyproject.toml` - Pytest and coverage settings
- `.github/workflows/test-coverage.yml` - CI/CD integration

## Documentation

- `docs/TEST_COVERAGE_GUIDE.md` - Comprehensive guide
- `docs/COVERAGE_BASELINE.md` - Current baseline and analysis

## Common Commands

```bash
# Clean coverage data
coverage erase

# Combine coverage from multiple runs
coverage combine

# Show coverage summary
coverage report

# Show only files below 100%
coverage report --skip-covered

# Generate HTML report
coverage html

# Generate JSON report
coverage json
```

## Troubleshooting

**Coverage not updating?**
```bash
coverage erase
pytest
```

**Import errors?**
```bash
PYTHONPATH=. pytest --cov=agent
```

**Slow coverage?**
```bash
# Skip HTML during development
pytest --cov=agent --cov=utils --cov-report=term-missing
```
