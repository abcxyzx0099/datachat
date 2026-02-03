# Test Structure Convention

## Test Organization Principles

This document provides guidelines for organizing test files. The goal is **maintainability and clarity**, not rigid rules.

---

## Core Principle: Use Good Judgment

Test organization should follow what makes sense for your project, team, and codebase. These are **guidelines**, not absolute rules.

---

## Recommended Structure: Hybrid Organization

For this project, we use a **hybrid structure** that balances simplicity with scalability:

```
tests/
├── conftest.py
├── fixtures/                       # Test data files
│   ├── sample_data.sav
│   ├── small_data.sav
│   ├── large_data.sav
│   └── edge_case_data.sav
│
├── core/                          # Core agent modules (unit tests)
│   ├── test_config.py
│   ├── test_state.py
│   ├── test_edges.py
│   ├── test_graph.py
│   ├── test_styling.py
│   └── test_server.py
│
├── nodes/                         # Phase-based workflow (1:1 mapping)
│   ├── test_phase1_extraction.py
│   ├── test_phase2_recoding.py
│   ├── test_phase3_indicators.py
│   ├── test_phase4_tables.py
│   ├── test_phase5_statistics.py
│   ├── test_phase6_filtering.py
│   ├── test_phase7_powerpoint.py
│   └── test_phase8_html_dashboard.py
│
├── integration/                   # Cross-module integration tests
│   ├── test_pspp_integration.py
│   ├── test_llm_integration.py
│   ├── test_llm_providers_integration.py
│   ├── test_graph_integration.py
│   └── test_output_generation.py
│
├── e2e/                           # End-to-end workflow tests
│   ├── test_e2e_workflow.py
│   ├── test_e2e_workflow_simple.py
│   ├── test_e2e_complete_workflow.py
│   ├── test_e2e_human_review.py
│   ├── test_e2e_error_recovery.py
│   ├── test_e2e_llm_providers.py
│   └── test_e2e_practical.py
│
└── patterns/                      # Reusable test patterns
    ├── test_three_node_pattern.py
    ├── test_nodes.py
    └── test_fixture_examples.py
```

### Directory Rationale

| Directory | Purpose | Contents |
|-----------|---------|----------|
| **`core/`** | Central infrastructure | Config, state, edges, graph, styling, server |
| **`nodes/`** | Phase-based workflow | 1:1 mapping with `agent/nodes/*.py` |
| **`integration/`** | Cross-module concerns | PSPP, LLM, graph integration |
| **`e2e/`** | Full workflow tests | End-to-end scenarios |
| **`patterns/`** | Reusable patterns | Test patterns, fixture examples |

---

## Guideline: Prefer 1:1 Mapping for Independent Modules

When a source file has distinct, testable functionality, create a dedicated test file.

### Good candidates for 1:1 mapping

| Module Type | Example |
|-------------|---------|
| Workflow phases | `phase1_extraction.py` → `nodes/test_phase1_extraction.py` |
| Core services | `graph.py` → `core/test_graph.py` |
| External integrations | `pspp_wrapper.py` → `integration/test_pspp_wrapper.py` |
| State management | `state.py` → `core/test_state.py` |

**Why**: These modules have clear responsibilities and benefit from focused test files.

---

## Guideline: Group Related Tests

Group tests when modules share **semantic domain** or **functional relationship**, not just file size.

### Primary Grouping Criteria

| Criterion | Description | Example |
|-----------|-------------|---------|
| **Semantic domain** | Tests the same business concept | All validation modules → `test_validation.py` |
| **Functional relationship** | Tests related functionality | All LLM operations → `test_llm_clients.py` |
| **Shared behavior** | Uses common fixtures/setup | Tests using same mock → grouped |
| **Tight coupling** | Modules that call each other | Interdependent utilities → `test_utils.py` |
| **External dependency** | Same external system | All PSPP tests → `test_pspp_integration.py` |

### Good examples of grouping

| Grouping Type | Source Modules | Test File | Why |
|---------------|----------------|-----------|-----|
| **Semantic domain** | `validation/recoding.py`, `validation/indicators.py`, `validation/tables.py` | `test_validation.py` | Same business domain: data validation |
| **Functional relationship** | `utils/tracing.py`, `utils/security.py` | `test_utils.py` | Both are cross-cutting utilities |
| **External dependency** | `utils/pspp_wrapper.py` and PSPP-related code | `test_pspp_integration.py` | All depend on PSPP external tool |
| **Configuration** | `config.py`, `settings.py` | `test_config.py` | Both deal with configuration |

### Poor examples of grouping (avoid)

| What | Why it's wrong |
|------|----------------|
| Grouping unrelated modules by file size | `small_tests.py` with config + edges + state |
| Grouping by first letter of filename | `tests_a.py`, `tests_b.py` |
| Grouping by developer name | `alice_tests.py`, `bob_tests.py` |

**Why semantic grouping matters**:
- Easier to find tests for a specific domain
- Tests that change together stay together
- Clearer test intent and purpose
- Better code organization

---

## Alternative Mapping Patterns: 1:N and N:1

While **1:1 mapping** is the default guideline, valid scenarios exist for **1:N** and **N:1** mapping.

### 1:N Mapping (One source → Multiple test files)

One source file has multiple corresponding test files.

| Scenario | Example | Why |
|----------|---------|-----|
| **Different test categories** | `agent/graph.py` → `test_graph.py` + `test_graph_integration.py` | Unit tests vs integration tests |
| **Performance separation** | `agent/server.py` → `test_server.py` + `test_server_performance.py` | Functional tests vs performance tests |
| **Large/complex module** | `phase2_recoding.py` → `test_phase2_rules.py` + `test_phase2_execution.py` | Tests too large for one file |
| **Different concerns** | `llm/clients.py` → `test_llm_clients.py` + `test_llm_rate_limiting.py` | Core functionality vs edge cases |
| **Test category split** | Any module → `test_{module}.py` + `test_{module}_e2e.py` | Unit tests vs E2E tests |

**When to use 1:N:**
- Module has distinct, testable aspects that benefit from separate files
- Different test approaches (unit, integration, performance, security)
- Test file becomes too large (>500 lines) to maintain effectively

### N:1 Mapping (Multiple sources → One test file)

Multiple source files share one test file. This is the **grouping** pattern described earlier.

| Scenario | Example | Why |
|----------|---------|-----|
| **Semantic domain** | `validation/*.py` → `test_validation.py` | Same business concept |
| **Shared utilities** | `utils/*.py` → `test_utils.py` | Cross-cutting concerns |
| **External dependency** | PSPP-related modules → `test_pspp_integration.py` | Same external system |
| **Tight coupling** | Interdependent modules → grouped test | Tests interactions |

### Decision Framework

```
                    ┌─────────────────┐
                    │   Source Module  │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                │ Module is large/       │
                │ complex? (>500 lines)  │
                └────────────┬────────────┘
                             │
                    ┌────────┴─────────┐
                    │ NO              YES │
                ┌───┴────┐        ┌────┴────┐
                │        │        │         │
         ┌──────▼──────┐ ┌────▼────┐ │
         │ Distinct    │ │ Split   │ │
         │ concerns?   │ │ by      │ │
         └──────┬──────┘ │ aspect  │ │
                │        └────┬────┘ │
           ┌────┴────┐         │      │
      YES │        │ NO       │      │
    ┌────▼────┐    ┌───▼───┐   │      │
    │ 1:N    │    │ 1:1   │   │      │
    │(split) │    │       │   │      │
    └─────────┘    └───┬───┘   │      │
                        │       │      │
                  Same semantic?     │
                        │       │      │
                   ┌────▼───────▼───────┐
                   │       N:1         │
                   │    (group)        │
                   └────────────────────┘
```

### Summary: Mapping Patterns

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **1:1** (default) | Independent, focused modules | Most phase files |
| **1:N** | Large/complex or multi-concern modules | `graph.py` → unit + integration tests |
| **N:1** | Same semantic domain or shared utilities | `validation/*.py` → `test_validation.py` |

---

## Naming Convention

| Test Type | Naming Pattern | Location |
|-----------|----------------|----------|
| Core module test | `test_{module_name}.py` | `core/` |
| Phase test | `test_phase{N}_{purpose}.py` | `nodes/` |
| Integration test | `test_{module}_integration.py` | `integration/` |
| E2E test | `test_e2e_{description}.py` | `e2e/` |
| Pattern test | `test_{pattern}.py` | `patterns/` |

---

## Running Tests by Directory

```bash
# All tests
.venv/bin/python -m pytest

# By directory
.venv/bin/python -m pytest tests/core/
.venv/bin/python -m pytest tests/nodes/
.venv/bin/python -m pytest tests/integration/
.venv/bin/python -m pytest tests/e2e/
.venv/bin/python -m pytest tests/patterns/

# By marker
.venv/bin/python -m pytest -m unit
.venv/bin/python -m pytest -m integration
.venv/bin/python -m pytest -m e2e

# Specific phase
.venv/bin/python -m pytest tests/nodes/test_phase2_recoding.py -v
```

---

## Practical Decision Guide

| Question | If YES → | If NO → |
|----------|----------|---------|
| Is this a core infrastructure module? | `core/` | Consider other dirs |
| Is this a workflow phase? | `nodes/` | Consider `core/` or `patterns/` |
| Does this test multiple modules together? | `integration/` | Consider specific dir |
| Is this a full workflow test? | `e2e/` | Consider `integration/` |
| Is this a reusable test pattern? | `patterns/` | Consider specific dir |

**Additional grouping decision:**

| Question | If YES → | If NO → |
|----------|----------|---------|
| Do modules share the same semantic domain? | Consider grouping | Keep separate |
| Do modules provide similar functionality? | Consider grouping | Keep separate |
| Do modules share the same external dependency? | Consider grouping | Keep separate |
| Are modules tightly coupled (call each other)? | Consider grouping | Keep separate |
| Will tests use the same fixtures/setup? | Consider grouping | Keep separate |

---

## What Actually Matters

More important than file structure:

| Priority | Description |
|----------|-------------|
| **1. Tests exist** | Untested code is worse than "imperfectly" organized tests |
| **2. Tests are readable** | Clear test names and structure matter more than file placement |
| **3. Tests run fast** | Proper mocking and fixture design > file organization |
| **4. Team agreement** | Consistency across the team > any specific rule |

---

## Examples from This Project

### 1:1 Mapping (Core modules)

```
agent/config.py                    →  tests/core/test_config.py
agent/state.py                     →  tests/core/test_state.py
agent/edges.py                     →  tests/core/test_edges.py
agent/graph.py                     →  tests/core/test_graph.py
agent/styling.py                   →  tests/core/test_styling.py
agent/server.py                    →  tests/core/test_server.py
```

### 1:1 Mapping (Phase modules)

```
agent/nodes/phase1_extraction.py   →  tests/nodes/test_phase1_extraction.py
agent/nodes/phase2_recoding.py     →  tests/nodes/test_phase2_recoding.py
agent/nodes/phase3_indicators.py   →  tests/nodes/test_phase3_indicators.py
agent/nodes/phase4_tables.py       →  tests/nodes/test_phase4_tables.py
agent/nodes/phase5_statistics.py   →  tests/nodes/test_phase5_statistics.py
agent/nodes/phase6_filtering.py    →  tests/nodes/test_phase6_filtering.py
agent/nodes/phase7_powerpoint.py   →  tests/nodes/test_phase7_powerpoint.py
agent/nodes/phase8_html_dashboard.py → tests/nodes/test_phase8_html_dashboard.py
```

### Semantic Grouping (Validation domain)

```
agent/validation/recoding.py    \
agent/validation/indicators.py  →  tests/core/test_validation.py
agent/validation/tables.py      /
```

**Why grouped:** All three modules share the same semantic domain — data validation rules. Testing them together validates the entire validation concept.

### Semantic Grouping (LLM functionality)

```
agent/llm/clients.py  →  tests/core/test_llm_clients.py
```

**Why separate:** LLM client functionality is a distinct semantic domain with its own concerns (API calls, rate limiting, error handling).

### Integration Tests

```
tests/integration/test_pspp_integration.py
tests/integration/test_llm_integration.py
tests/integration/test_llm_providers_integration.py
tests/integration/test_graph_integration.py
tests/integration/test_output_generation.py
```

### E2E Tests

```
tests/e2e/test_e2e_workflow.py
tests/e2e/test_e2e_workflow_simple.py
tests/e2e/test_e2e_complete_workflow.py
tests/e2e/test_e2e_human_review.py
tests/e2e/test_e2e_error_recovery.py
tests/e2e/test_e2e_llm_providers.py
tests/e2e/test_e2e_practical.py
```

---

## Summary

| Guideline | Application |
|-----------|-------------|
| Core infrastructure modules | Place in `core/` |
| Workflow phases | Place in `nodes/` with 1:1 mapping |
| Cross-module integration | Place in `integration/` |
| End-to-end workflows | Place in `e2e/` |
| Reusable test patterns | Place in `patterns/` |
| **Grouping criteria** | **Semantic domain > Functional relationship > Shared behavior > Tight coupling** |
| **1:1 mapping** | Default for independent modules |
| **1:N mapping** | Large/complex modules or different test categories |
| **N:1 mapping** | Same semantic domain or shared utilities |
| When in doubt | Start simple, refactor as needed |
