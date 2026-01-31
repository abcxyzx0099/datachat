# Code Organization

This document defines the code organization principles, naming conventions, and design patterns for the workflow system.

---

> **For the complete project directory structure and file locations, see [Project Structure](./project-structure.md).**

---

## Table of Contents

1. [Organization Principles](#1-organization-principles)
2. [Module Organization](#2-module-organization)
3. [Phase-to-File Mapping](#3-phase-to-file-mapping)
4. [Naming Conventions](#4-naming-conventions)
5. [Import Patterns](#5-import-patterns)
6. [Design Principles](#6-design-principles)
7. [Key Decisions](#7-key-decisions)

---

## 1. Organization Principles

### 1.1 Separation of Concerns

| Concern | Location |
|---------|----------|
| **State definitions** | `agent/state.py` |
| **Configuration** | `agent/config.py` |
| **Workflow graph** | `agent/graph.py` |
| **Conditional routing** | `agent/edges.py` |
| **Node implementations** | `agent/nodes/` (by phase) |
| **Validation logic** | `agent/validation/` |
| **LLM integration** | `agent/llm/` |
| **Module utilities** | `agent/utils/` |

### 1.2 Phase-Based Organization

Nodes are organized by workflow phase rather than individual steps:

| Phase File | Steps | Lines | Description |
|------------|-------|-------|-------------|
| `phase1_extraction.py` | 1-3 | ~150 | Data extraction and preparation |
| `phase2_recoding.py` | 4-8 | ~400 | Recoding with three-node pattern |
| `phase3_indicators.py` | 9-11 | ~200 | Indicator generation |
| `phase4_tables.py` | 12-16 | ~350 | Cross-table specification |
| `phase5_statistics.py` | 17-18 | ~150 | Statistical analysis |
| `phase6_filtering.py` | 19-20 | ~120 | Significant table selection |
| `phase7_powerpoint.py` | 21 | ~100 | PowerPoint generation |
| `phase8_html_dashboard.py` | 22 | ~100 | HTML dashboard generation |

**Benefits**: Manageable file sizes, clear boundaries, parallel development.

---

## 2. Module Organization

### 2.1 agent/ Modules

| Module | Responsibility | Key Contents |
|--------|---------------|--------------|
| **state.py** | TypedDict definitions | All state classes, WorkflowState |
| **config.py** | Configuration constants | DEFAULT_CONFIG |
| **edges.py** | Conditional routing | Three-node pattern routing functions |
| **graph.py** | Workflow construction | StateGraph setup, node/edge registration |
| **nodes/** | Node implementations | 8 phase files with 22 nodes |
| **utils/** | Module utilities | PSPP wrapper, file I/O, statistics |
| **validation/** | Validation functions | Recoding, indicators, tables |
| **llm/** | LLM integration | Prompts, client initialization |

### 2.2 utils/ Modules (Project-Wide)

| Module | Responsibility |
|--------|---------------|
| **logging.py** | Logging configuration and setup |
| **helpers.py** | General helper functions |

---

## 3. Phase-to-File Mapping

| File | Steps | State Modified |
|------|-------|----------------|
| `phase1_extraction.py` | 1-3 | ExtractionState |
| `phase2_recoding.py` | 4-8 | RecodingState |
| `phase3_indicators.py` | 9-11 | IndicatorState |
| `phase4_tables.py` | 12-16 | CrossTableState |
| `phase5_statistics.py` | 17-18 | StatisticalAnalysisState |
| `phase6_filtering.py` | 19-20 | FilteringState |
| `phase7_powerpoint.py` | 21 | PresentationState |
| `phase8_html_dashboard.py` | 22 | PresentationState |

---

## 4. Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| **Phase files** | `phase{N}_{purpose}.py` | `phase2_recoding.py` |
| **Node functions** | `{operation}_{entity}_node` | `extract_spss_node` |
| **Edge functions** | `should_{action}_{entity}` | `should_retry_recoding` |
| **State classes** | `{Purpose}State` | `ExtractionState`, `RecodingState` |
| **Utility modules** | `lowercase_with_underscores` | `pspp_wrapper.py` |
| **Validation functions** | `validate_{entity}` | `validate_recoding_rules` |
| **Constants** | `UPPERCASE_WITH_UNDERSCORES` | `PSPP_PATH`, `MAX_TOKENS` |
| **Private functions** | `_{name}` (leading underscore) | `_parse_metadata` |

---

## 5. Import Patterns

### 5.1 Node Imports (Clean Interface)

The `agent/nodes/__init__.py` re-exports all nodes for clean imports:

```python
# agent/nodes/__init__.py
from .phase1_extraction import extract_spss_node, transform_metadata_node, filter_metadata_node
from .phase2_recoding import generate_recoding_rules_node, validate_recoding_rules_node, ...
# ... all 22 nodes

__all__ = ["extract_spss_node", "transform_metadata_node", ...]
```

**Usage in graph.py:**
```python
from agent.nodes import extract_spss_node, generate_recoding_rules_node
```

### 5.2 LangGraph Configuration Paths

Node paths follow the pattern: `agent.nodes.{phase_file}:{node_function}`

```json
{
  "extract_spss": "agent.nodes.phase1_extraction:extract_spss_node",
  "generate_recoding_rules": "agent.nodes.phase2_recoding:generate_recoding_rules_node"
}
```

---

## 6. Design Principles

| Principle | Description |
|-----------|-------------|
| **Phase-Based Organization** | Group nodes by workflow phase, not individual steps |
| **State Evolution Alignment** | Files map to state TypedDict evolution |
| **Separation of Concerns** | State, nodes, edges, validation, prompts in separate modules |
| **Single Responsibility** | Each file/module has one clear purpose |
| **Scalability** | Structure supports adding new phases/nodes |
| **Deterministic vs Probabilistic** | Separate directories for validation (deterministic) vs LLM (probabilistic) |

---

## 7. Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Phase-based files (8)** | 100-400 lines each instead of single 1500-line file |
| **Separate Phase 7 & 8** | Different output formats (PPT vs HTML) |
| **TypedDict states** | Type safety and IDE support |
| **Separate validation/ and llm/** | Deterministic vs probabilistic logic separation |
| **Two utils locations** | Module-specific (`agent/utils/`) vs project-wide (`utils/`) |
| **__init__.py re-exports** | Clean imports while maintaining phase-based organization |

---

## Related Documents

| Document | Content |
|----------|---------|
| **[Project Structure](./project-structure.md)** | Complete directory structure and file locations |
| **[Data Flow](./data-flow.md)** | Workflow design and step specifications |
| **[System Architecture](./system-architecture.md)** | System components and module responsibilities |
| **[Configuration](./configuration.md)** | Configuration options and environment variables |
