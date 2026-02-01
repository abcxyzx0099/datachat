# Coverage Baseline Report

**Date**: 2026-02-01
**Baseline Coverage**: 69.6%

## Overall Coverage Summary

| Metric | Value |
|--------|-------|
| **Total Statements** | 4,600 |
| **Covered Statements** | 3,267 |
| **Missing Statements** | 1,333 |
| **Total Branches** | 1,398 |
| **Covered Branches** | 1,195 |
| **Partial Branches** | 203 |
| **Line Coverage** | 69.6% |
| **Branch Coverage** | 85.5% |

## Coverage by Module

### High Coverage (90%+)

| Module | Coverage | Notes |
|--------|----------|-------|
| `agent/utils/pspp_wrapper.py` | 98.0% | Excellent - PSPP integration well-tested |
| `agent/llm/clients.py` | 96.6% | Excellent - LLM client coverage |
| `utils/logging.py` | 95.8% | Excellent - Logging utilities |
| `agent/utils/statistics.py` | 95.6% | Excellent - Statistics functions |
| `agent/validation/indicators.py` | 95.6% | Excellent - Indicator validation |
| `agent/validation/recoding.py` | 94.5% | Excellent - Recoding validation |
| `agent/nodes/phase8_html_dashboard.py` | 93.1% | Very good - HTML dashboard generation |
| `agent/validation/tables.py` | 90.1% | Very good - Table validation |

### Good Coverage (70-89%)

| Module | Coverage | Notes |
|--------|----------|-------|
| `agent/nodes/phase7_powerpoint.py` | 88.1% | Good - PowerPoint generation |
| `agent/llm/prompts.py` | 84.1% | Good - Prompt templates |
| `agent/utils/file_io.py` | 83.7% | Good - File I/O operations |
| `agent/graph.py` | 80.1% | Good - Graph orchestration |
| `agent/nodes/phase2_recoding.py` | 77.2% | Good - Recoding node |
| `agent/nodes/phase1_extraction.py` | 70.2% | Acceptable - SPSS extraction |
| `agent/nodes/__init__.py` | 66.7% | Acceptable - Node utilities |

### Needs Improvement (40-69%)

| Module | Coverage | Notes |
|--------|----------|-------|
| `agent/nodes/phase3_indicators.py` | 66.0% | **Priority** - Indicators generation |
| `agent/nodes/phase4_tables.py` | 49.8% | **Priority** - Table generation |
| `agent/styling.py` | 41.6% | Medium priority - Styling utilities |
| `agent/config.py` | 29.0% | Medium priority - Configuration |

### Low Coverage (<10%)

| Module | Coverage | Notes |
|--------|----------|-------|
| `agent/nodes/phase5_statistics.py` | 7.8% | **High Priority** - Statistics script |
| `agent/nodes/phase6_filtering.py` | 4.1% | **High Priority** - Filtering node |
| `agent/server.py` | 0.0% | **High Priority** - FastAPI server |

## Coverage Thresholds

### Current Settings

- **Minimum Threshold**: 69.0% (just below baseline)
- **Build Fails**: If coverage drops below 69%
- **Branch Coverage**: Enabled
- **Goal**: 70% overall, 80% for new code

### Rationale

- Current baseline is 69.6%, so threshold set to 69%
- This prevents coverage regression while allowing minor fluctuations
- As coverage improves, threshold should be increased

## Priority Areas for Improvement

### 1. Server Coverage (0%)
**File**: `agent/server.py`
**Impact**: High - FastAPI server needs testing
**Recommendation**: Add API endpoint tests, integration tests

### 2. Phase 6: Filtering Node (4.1%)
**File**: `agent/nodes/phase6_filtering.py`
**Impact**: High - Table filtering is critical
**Recommendation**: Add unit tests for filter logic

### 3. Phase 5: Statistics Node (7.8%)
**File**: `agent/nodes/phase5_statistics.py`
**Impact**: High - Statistical analysis generation
**Recommendation**: Add tests for Python statistics script generation

### 4. Configuration (29%)
**File**: `agent/config.py`
**Impact**: Medium - Configuration management
**Recommendation**: Add config loading/validation tests

### 5. Styling (41.6%)
**File**: `agent/styling.py`
**Impact**: Medium - Output styling
**Recommendation**: Add tests for style functions

## Branch Coverage Analysis

Overall branch coverage is **85.5%**, which is excellent. This means that for most conditional statements, both branches (true/false) are being tested.

Modules with low branch coverage:
- `agent/server.py` - 0% (no branches covered)
- `agent/nodes/phase6_filtering.py` - 0%
- `agent/nodes/phase5_statistics.py` - 0%

## Excluded Code

The following patterns are excluded from coverage:
- `pragma: no cover` - Manual exclusions
- `def __repr__` and `def __str__` - String representation methods
- `raise AssertionError` - Debug assertions
- `raise NotImplementedError` - Abstract methods
- `if __name__ == .__main__.:` - Script entry points
- `if TYPE_CHECKING:` - Type checking imports
- `@abstractmethod` - Abstract method decorators

## Recommendations

### Immediate Actions

1. **Add Server Tests** (0% → 80%)
   - Test all API endpoints
   - Test error handling
   - Test request/response validation

2. **Improve Filtering Node** (4.1% → 70%)
   - Test filter logic
   - Test table filtering
   - Test validation

3. **Improve Statistics Node** (7.8% → 70%)
   - Test script generation
   - Test statistical calculations
   - Test output formatting

### Medium-term Goals

1. **Reach 75% Overall Coverage**
   - Focus on modules below 50%
   - Add integration tests
   - Improve edge case coverage

2. **Maintain 85%+ Branch Coverage**
   - Add tests for both branches of conditionals
   - Test error paths
   - Test exception handling

3. **New Code Coverage**
   - Require 80%+ coverage for new features
   - Use TDD approach
   - Review coverage in PRs

## Running Coverage Reports

```bash
# Run tests with coverage
pytest

# View HTML report
open htmlcov/index.html

# Terminal report
coverage report --skip-covered

# Detailed report
coverage report
```

## Updating This Baseline

This baseline should be updated:
- **Monthly**: Track progress over time
- **After major features**: Assess impact of new code
- **When threshold changes**: Document new baseline

To update:
```bash
# Run full test suite
coverage erase
pytest --cov=agent --cov=utils --cov-report=json

# Generate new baseline
python -m coverage report > docs/COVERAGE_BASELINE.md
```

## Tracking

| Date | Coverage | Change | Notes |
|------|----------|--------|-------|
| 2026-02-01 | 69.6% | Baseline | Initial baseline established |
| | | | |

---

**Next Review**: 2026-03-01
**Owner**: Development Team
