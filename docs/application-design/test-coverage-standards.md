# Test Coverage Standards

## Reasonable Test Coverage by Project Type

| Project Type | Good Coverage | Excellent Coverage |
|--------------|-------------|------------------|
| New/Small Project | 60-70% | 80%+ |
| Established/Mature Library | 70-80% | 85-90% |
| Critical Production Code | 80-90% | 90%+ |
| Scientific/Medical | 90-95% | 95%+ |

## For Survey Analyzer

**Current Coverage:** 39.8%
**Target Coverage:** 80% (from `pyproject.toml`)

### Assessment

As a statistical/analysis library, survey_analyzer falls into the **Established/Mature Library** category. A coverage of **60-70%** is reasonable, with **70-80%** being the ideal range.

### Module-Level Recommendations

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| `specification/validator.py` | 8.3% | 60-70% | **High** |
| `__main__.py` | 0% | 60-70% | **High** |
| `analysis/indicators.py` | 22.1% | 60-70% | **Medium** |
| `pspp/syntax.py` | 27.0% | 60-70% | **Medium** |
| `pspp/executor.py` | 49.5% | 60-70% | **Medium** |
| `reporting/dashboard.py` | 46.5% | 60-70% | **Low** |
| `reporting/powerpoint.py` | 61.9% | 60-70% | **Low** |

### Modules Already at Target

| Module | Coverage | Notes |
|--------|----------|--------|
| `specification/schema.py` | 78.7% | Good dataclass coverage |
| `filtering/significance.py` | 93.2% | Excellent core logic coverage |
| `analysis/statistics.py` | 93.3% | Excellent statistical test coverage |
| `__init__.py` modules | 100% | Full coverage |
