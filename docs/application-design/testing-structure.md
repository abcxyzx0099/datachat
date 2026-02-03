# Testing Structure

This document defines the project testing structure, organization, and file locations.

---

## Table of Contents

1. [Directory Structure](#1-directory-structure)
2. [Test File Organization](#2-test-file-organization)
3. [Test Categories](#3-test-categories)
4. [Test Outputs and Reports](#4-test-outputs-and-reports)
5. [Test Fixtures](#5-test-fixtures)

---

## 1. Directory Structure

### Project Root

```
/home/admin/workspaces/datachat/
├── pytest.ini                      # Pytest configuration
├── .coveragerc                     # Coverage configuration
│
├── tests/                          # Test source code (hybrid structure)
│   ├── conftest.py                 # Shared fixtures
│   ├── fixtures/                   # Test data files
│   ├── core/                       # Core module tests
│   ├── nodes/                      # Phase-based workflow tests
│   ├── integration/                # Integration tests
│   ├── e2e/                        # End-to-end tests
│   └── patterns/                   # Reusable test patterns
│
├── htmlcov/                        # Coverage HTML reports (generated)
└── playwright-mcp/                 # MCP-specific results (gitignored)
```

### tests/ Directory (Hybrid Structure)

```
tests/
├── conftest.py                     # Pytest configuration and shared fixtures
├── __init__.py                     # Package initialization
│
├── fixtures/                       # Test data files
│   ├── sample_data.sav
│   ├── small_data.sav
│   ├── large_data.sav
│   └── edge_case_data.sav
│
├── checkpoints/                    # Test checkpoint databases (gitignored)
│   └── checkpoints_*.db            # Created by temp_checkpoint_db fixture
│
├── core/                           # Core agent modules
├── nodes/                          # Phase-based workflow (1:1 mapping)
├── integration/                    # Cross-module integration
├── e2e/                            # End-to-end workflows
└── patterns/                       # Reusable test patterns
```

---

## 2. Test File Organization

The project uses a **hybrid structure** as defined in the [Test Structure Convention](../meta-governance/test-structure-convention.md).

### Directory Rationale

| Directory | Purpose | Contents |
|-----------|---------|----------|
| **`core/`** | Central infrastructure | Config, state, edges, graph, styling, server |
| **`nodes/`** | Phase-based workflow | 1:1 mapping with `agent/nodes/*.py` |
| **`integration/`** | Cross-module concerns | PSPP, LLM, graph integration |
| **`e2e/`** | Full workflow tests | End-to-end scenarios |
| **`patterns/`** | Reusable patterns | Test patterns, fixture examples |

### Files by Directory

**`tests/core/`** - Core infrastructure tests:
| Test File | Source |
|-----------|--------|
| `test_config.py` | `agent/config.py` |
| `test_state.py` | `agent/state.py` |
| `test_edges.py` | `agent/edges.py` |
| `test_graph.py` | `agent/graph.py` |
| `test_styling.py` | `agent/styling.py` |
| `test_server.py` | `agent/server.py` |
| `test_utils.py` | All `agent/utils/*.py` |
| `test_validation.py` | All `agent/validation/*.py` |
| `test_llm_clients.py` | `agent/llm/clients.py` |
| `test_pspp_wrapper.py` | `agent/utils/pspp_wrapper.py` |

**`tests/nodes/`** - Phase-based workflow tests (1:1 mapping):
| Test File | Source |
|-----------|--------|
| `test_phase1_extraction.py` | `agent/nodes/phase1_extraction.py` |
| `test_phase2_recoding.py` | `agent/nodes/phase2_recoding.py` |
| `test_phase3_indicators.py` | `agent/nodes/phase3_indicators.py` |
| `test_phase4_tables.py` | `agent/nodes/phase4_tables.py` |
| `test_phase5_statistics.py` | `agent/nodes/phase5_statistics.py` |
| `test_phase6_filtering.py` | `agent/nodes/phase6_filtering.py` |
| `test_phase7_powerpoint.py` | `agent/nodes/phase7_powerpoint.py` |
| `test_phase8_html_dashboard.py` | `agent/nodes/phase8_html_dashboard.py` |

**`tests/integration/`** - Cross-module integration tests:
| Test File | Purpose |
|-----------|---------|
| `test_pspp_integration.py` | PSPP wrapper integration |
| `test_llm_integration.py` | LLM client integration |
| `test_llm_providers_integration.py` | LLM provider switching |
| `test_graph_integration.py` | Graph execution integration |
| `test_output_generation.py` | Output file generation |

**`tests/e2e/`** - End-to-end workflow tests:
| Test File | Purpose |
|-----------|---------|
| `test_e2e_workflow.py` | Full workflow execution |
| `test_e2e_workflow_simple.py` | Simplified workflow |
| `test_e2e_complete_workflow.py` | Complete workflow |
| `test_e2e_human_review.py` | Human review workflow |
| `test_e2e_error_recovery.py` | Error handling |
| `test_e2e_llm_providers.py` | Multi-provider tests |
| `test_e2e_practical.py` | Real-world scenarios |

**`tests/patterns/`** - Reusable test patterns:
| Test File | Purpose |
|-----------|---------|
| `test_three_node_pattern.py` | Three-node pattern tests |
| `test_nodes.py` | All node tests |
| `test_fixture_examples.py` | Fixture usage examples |

---

## 3. Test Categories

| Category | Naming Convention | Location | Speed | Dependencies |
|----------|------------------|----------|-------|--------------|
| **Unit** | `test_{module}.py` | `core/` | Seconds | Mocked |
| **Phase** | `test_phase{N}_{purpose}.py` | `nodes/` | Minutes | May use LLM |
| **Integration** | `test_{module}_integration.py` | `integration/` | Minutes | Real services |
| **E2E** | `test_e2e_{description}.py` | `e2e/` | 5-15 min | Real data/services |
| **Pattern** | `test_{pattern}.py` | `patterns/` | Varies | Varies |

---

## 4. Test Outputs and Reports

### Configuration vs Output Files

| Type | Location | Git Tracked |
|------|----------|-------------|
| `pytest.ini` | Project root | Yes |
| `.coveragerc` | Project root | Yes |
| `htmlcov/` | Project root | No |
| `playwright-mcp/` | `tests/` | No |

### `.gitignore` Entries

```gitignore
# Test outputs (generated)
htmlcov/
playwright-mcp/
tests/checkpoints/

# Pytest cache
.pytest_cache/
__pycache__/
```

---

## 5. Test Fixtures

### Key Fixtures (conftest.py)

| Fixture | Purpose |
|---------|---------|
| `mock_state` | Mock agent state |
| `mock_llm_response` | Mock LLM API responses |
| `temp_output_dir` | Temporary directory for outputs |
| `sample_sav_file` | Path to sample .sav file |
| `pspp_available` | Skip tests if PSPP not installed |
| `temp_checkpoint_db` | Temporary SQLite checkpoint database for testing |

### Checkpoint Fixture (`temp_checkpoint_db`)

The `temp_checkpoint_db` fixture creates temporary checkpoint databases in `tests/checkpoints/` to ensure test isolation and avoid RAM usage from tmpfs:

```python
@pytest.fixture
def temp_checkpoint_db():
    """
    Create temporary SQLite checkpoint database for testing.

    Uses tests/checkpoints/ directory to keep test artifacts organized
    separate from development checkpoints at ./checkpoints.db.
    """
    from pathlib import Path
    tests_dir = Path(__file__).parent
    checkpoint_dir = tests_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    fd, db_path = tempfile.mkstemp(suffix=".db", prefix="pytest_cp_", dir=str(checkpoint_dir))
    os.close(fd)
    yield db_path
    # Cleanup: auto-delete after test completes
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass
```

**Design Rationale:**

| Aspect | Development | Testing |
|--------|-------------|---------|
| **Location** | `./checkpoints.db` (project root) | `tests/checkpoints/checkpoints_*.db` |
| **Purpose** | LangGraph Studio state persistence | Test isolation per test case |
| **Cleanup** | Manual (persistent) | Automatic (after test) |
| **RAM Usage** | Disk-based (no tmpfs) | Disk-based (avoids `/tmp` RAM) |

This design ensures:
- Test checkpoints don't interfere with development checkpoints
- Each test gets a unique checkpoint database (isolation)
- All checkpoint storage uses disk (not RAM) to avoid tmpfs limitations

### Test Data Files (tests/fixtures/)

| File | Purpose |
|------|---------|
| `sample_data.sav` | Standard test dataset (3.6 KB) |
| `small_data.sav` | Fast unit tests (1.2 KB) |
| `large_data.sav` | Performance testing (61.7 KB) |
| `edge_case_data.sav` | Edge case scenarios (1.3 KB) |

---

## See Also

- **[Test Structure Convention](../meta-governance/test-structure-convention.md)** - Guidelines for hybrid test organization
