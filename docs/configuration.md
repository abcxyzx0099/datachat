# Configuration

This document describes all configuration options for the Survey Analysis & Visualization Workflow.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Default Configuration](#2-default-configuration)
3. [Environment Variables](#3-environment-variables)
4. [LangGraph Configuration](#4-langgraph-configuration)

---

## 1. Overview

Configuration is managed through:
- **Python dict** (`DEFAULT_CONFIG` in `agent/config.py`)
- **Environment variables** (`.env` file)
- **LangGraph JSON** (`config/langgraph.json`)

### 1.1 Configuration Priority

```
Environment Variables → DEFAULT_CONFIG
```

Environment variables override default values.

---

## 2. Default Configuration

### 2.1 Complete DEFAULT_CONFIG

Located in `agent/config.py`:

```python
DEFAULT_CONFIG = {
    # ============================================
    # LLM Configuration
    # ============================================
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,

    # ============================================
    # Three-Node Pattern Configuration
    # ============================================
    "max_self_correction_iterations": 3,
    "enable_human_review": True,

    # ============================================
    # Step 3: Preliminary Filtering
    # ============================================
    "cardinality_threshold": 30,     # Max distinct values before filtering as high-cardinality
    "filter_binary": True,            # Filter out binary variables (exactly 2 distinct values)
    "filter_other_text": True,        # Filter out "other" text fields (open-ended feedback)

    # ============================================
    # PSPP Configuration
    # ============================================
    "pspp_path": "/usr/bin/pspp",
    "pspp_output_path": "output/pspp_logs.txt",

    # ============================================
    # File Paths
    # ============================================
    "output_dir": "output",
    "temp_dir": "temp",

    # ============================================
    # Statistical Analysis
    # ============================================
    "significance_level": 0.05,       # p-value threshold for statistical significance
    "min_cramers_v": 0.1,             # Minimum effect size (Cramer's V)
    "min_cell_count": 10,             # Minimum expected cell count for chi-square

    # ============================================
    # Presentation
    # ============================================
    "powerpoint_template": None,      # Path to custom .pptx template (optional)
    "html_theme": "default"           # HTML dashboard theme
}
```

### 2.2 Configuration Sections

#### LLM Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `"gpt-4"` | OpenAI model to use |
| `temperature` | float | `0.7` | LLM temperature (0.0-1.0) |
| `max_tokens` | int | `2000` | Maximum tokens per LLM response |

#### Three-Node Pattern Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_self_correction_iterations` | int | `3` | Max validation retry iterations |
| `enable_human_review` | bool | `True` | Enable human review nodes |

#### Filtering Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cardinality_threshold` | int | `30` | Max distinct values before filtering |
| `filter_binary` | bool | `True` | Filter binary variables |
| `filter_other_text` | bool | `True` | Filter "other" text fields |

#### Statistical Analysis Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `significance_level` | float | `0.05` | p-value threshold for significance |
| `min_cramers_v` | float | `0.1` | Minimum Cramer's V effect size |
| `min_cell_count` | int | `10` | Minimum expected cell count |

---

## 3. Environment Variables

### 3.1 Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |

### 3.2 Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PSPP_PATH` | Path to PSPP executable | `/usr/bin/pspp` |
| `OUTPUT_DIR` | Output directory | `output` |
| `TEMP_DIR` | Temporary files directory | `temp` |
| `MODEL` | OpenAI model name | `gpt-4` |
| `TEMPERATURE` | LLM temperature | `0.7` |

### 3.3 .env File Example

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional (override defaults)
PSPP_PATH=/usr/bin/pspp
OUTPUT_DIR=output
TEMP_DIR=temp
MODEL=gpt-4
TEMPERATURE=0.7
ENABLE_HUMAN_REVIEW=true
```

### 3.4 Loading Environment Variables

```python
from dotenv import load_dotenv
import os

load_dotenv()

config = {
    "model": os.getenv("MODEL", "gpt-4"),
    "temperature": float(os.getenv("TEMPERATURE", "0.7")),
    "pspp_path": os.getenv("PSPP_PATH", "/usr/bin/pspp"),
    # ...
}
```

---

## 4. LangGraph Configuration

### 4.1 langgraph.json Structure

Located at `config/langgraph.json`:

```json
{
  "graphs": {
    "survey_analysis": {
      "nodes": {
        "extract_spss": "agent.nodes.phase1_extraction:extract_spss_node",
        "transform_metadata": "agent.nodes.phase1_extraction:transform_metadata_node",
        "filter_metadata": "agent.nodes.phase1_extraction:filter_metadata_node",
        "generate_recoding_rules": "agent.nodes.phase2_recoding:generate_recoding_rules_node",
        "validate_recoding_rules": "agent.nodes.phase2_recoding:validate_recoding_rules_node",
        "review_recoding_rules": "agent.nodes.phase2_recoding:review_recoding_rules_node",
        "generate_pspp_recoding_syntax": "agent.nodes.phase2_recoding:generate_pspp_recoding_syntax_node",
        "execute_pspp_recoding": "agent.nodes.phase2_recoding:execute_pspp_recoding_node",
        "generate_indicators": "agent.nodes.phase3_indicators:generate_indicators_node",
        "validate_indicators": "agent.nodes.phase3_indicators:validate_indicators_node",
        "review_indicators": "agent.nodes.phase3_indicators:review_indicators_node",
        "generate_table_specifications": "agent.nodes.phase4_tables:generate_table_specifications_node",
        "validate_table_specifications": "agent.nodes.phase4_tables:validate_table_specifications_node",
        "review_table_specifications": "agent.nodes.phase4_tables:review_table_specifications_node",
        "generate_pspp_table_syntax": "agent.nodes.phase4_tables:generate_pspp_table_syntax_node",
        "execute_pspp_tables": "agent.nodes.phase4_tables:execute_pspp_tables_node",
        "generate_python_statistics_script": "agent.nodes.phase5_statistics:generate_python_statistics_script_node",
        "execute_python_statistics_script": "agent.nodes.phase5_statistics:execute_python_statistics_script_node",
        "generate_filter_list": "agent.nodes.phase6_filtering:generate_filter_list_node",
        "apply_filter_to_tables": "agent.nodes.phase6_filtering:apply_filter_to_tables_node",
        "generate_powerpoint": "agent.nodes.phase7_powerpoint:generate_powerpoint_node",
        "generate_html_dashboard": "agent.nodes.phase8_html_dashboard:generate_html_dashboard_node"
      },
      "edges": {
        "extract_spss": "transform_metadata",
        "transform_metadata": "filter_metadata",
        "filter_metadata": "generate_recoding_rules"
      },
      "conditional_edges": {
        "validate_recoding_rules": "agent.edges:should_retry_recoding",
        "review_recoding_rules": "agent.edges:should_approve_recoding",
        "validate_indicators": "agent.edges:should_retry_indicators",
        "review_indicators": "agent.edges:should_approve_indicators",
        "validate_table_specifications": "agent.edges:should_retry_table_specs",
        "review_table_specifications": "agent.edges:should_approve_table_specs"
      }
    }
  }
}
```

### 4.2 Node Path Format

```
agent.nodes.{phase_file}:{node_function}
```

Examples:
- `agent.nodes.phase1_extraction:extract_spss_node`
- `agent.nodes.phase2_recoding:generate_recoding_rules_node`

---

## 5. Usage Examples

### 5.1 Custom Filtering Rules

```python
config = DEFAULT_CONFIG.copy()
config["cardinality_threshold"] = 50  # Filter fewer variables
config["filter_binary"] = False       # Keep binary variables
config["filter_other_text"] = False   # Keep "other" fields
```

### 5.2 Adjust Statistical Thresholds

```python
config = DEFAULT_CONFIG.copy()
config["significance_level"] = 0.01    # More strict (p < 0.01)
config["min_cramers_v"] = 0.2          # Larger effect size required
config["min_cell_count"] = 20          # Larger sample size required
```

### 5.3 Automatic Mode (No Human Review)

```python
config = DEFAULT_CONFIG.copy()
config["enable_human_review"] = False
```

**Use when**: Testing, batch processing, trusted surveys.

### 5.4 Apply Configuration via Command Line

```bash
# Basic analysis with default config
python -m agent.graph --input data/input/survey.sav

# Custom output directory
python -m agent.graph --input data/input/survey.sav --output-dir results/

# Disable human review (for testing)
python -m agent.graph --input data/input/survey.sav --no-human-review

# Resume from checkpoint
python -m agent.graph --thread-id survey_001 --resume
```

---

## Related Documents

- **[Deployment](./deployment.md)** - Installation, environment configuration, and operations
- **[Web Interface](./web-interface.md)** - Agent Chat UI setup and usage
- **[Project Structure](./project-structure.md)** - Complete directory structure, file paths, and output locations
- **[Data Flow](./data-flow.md)** - Workflow design and steps
- **[System Architecture](./system-architecture.md)** - System components and architecture
- **[Technology Stack](./technology-stack.md)** - Technologies and versions
- **[Product Features and Usage](./product-features-and-usage.md)** - Product introduction for end users
- **[Implementation Specifications](./implementation-specifications.md)** - Technical implementation and Python API
