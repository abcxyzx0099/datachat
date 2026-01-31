# Code Organization

This document defines the code organization for the workflow system.

---

## Directory Structure

```
agent/
├── __init__.py                   # Package exports
├── state.py                      # TypedDict state definitions
├── config.py                     # Configuration constants
├── edges.py                      # Conditional routing logic
├── graph.py                      # LangGraph construction
│
├── utils/                        # Module-specific utilities
│   ├── __init__.py
│   ├── pspp_wrapper.py           # PSPP execution
│   ├── file_io.py                # File I/O utilities
│   └── statistics.py             # Statistical computations
│
├── validation/                   # Validation functions
│   ├── __init__.py
│   ├── recoding.py               # Recoding rule validation
│   ├── indicators.py             # Indicator validation
│   └── tables.py                 # Table specification validation
│
├── llm/                          # LLM modules
│   ├── __init__.py
│   ├── prompts.py                # Prompt templates
│   └── clients.py                # LLM client initialization
│
└── nodes/                        # LangGraph node implementations
    ├── __init__.py
    ├── phase1_extraction.py      # Steps 1-3
    ├── phase2_recoding.py        # Steps 4-8
    ├── phase3_indicators.py      # Steps 9-11
    ├── phase4_tables.py          # Steps 12-16
    ├── phase5_statistics.py      # Steps 17-18
    ├── phase6_filtering.py       # Steps 19-20
    ├── phase7_powerpoint.py      # Step 21
    └── phase8_html_dashboard.py  # Step 22

utils/                            # Project-wide utilities
├── __init__.py
├── logging.py                    # Logging configuration
└── helpers.py                    # General helpers
```

---

## Phase-to-File Mapping

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

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Phase files | `phase{N}_{purpose}.py` | `phase2_recoding.py` |
| Node functions | `{operation}_{entity}_node` | `extract_spss_node` |
| State classes | `{Purpose}State` | `ExtractionState`, `RecodingState` |
| Utility modules | `lowercase_with_underscores` | `pspp_wrapper.py` |
| Directories | `lowercase_with_underscores` | `agent/`, `utils/`, `llm/` |
| Constants | `UPPERCASE_WITH_UNDERSCORES` | `PSPP_PATH`, `MAX_TOKENS` |

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Phase-Based Organization** | Group nodes by workflow phase |
| **State Evolution Alignment** | Files map to state TypedDict evolution |
| **Separation of Concerns** | State, nodes, edges, validation, prompts in separate modules |
| **Single Responsibility** | Each file/module has one clear purpose |
| **Scalability** | Structure supports adding new phases/nodes |

---

## Key Decisions

- **Phase-based files**: 8 files (~350-400 lines each) instead of 22 node files
- **Separate Phase 7 & 8**: Different output formats (PPT vs HTML)
- **TypedDict states**: Type safety and IDE support
- **Separate validation/ and llm/**: Deterministic vs probabilistic logic
- **Two utils locations**: Module-specific (`agent/utils/`) vs project-wide (`utils/`)
