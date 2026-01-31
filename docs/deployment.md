# Deployment

This document describes deployment architecture, installation, environment configuration, and operational guidance for the Survey Analysis & Visualization Workflow.

---

## Table of Contents

1. [Deployment Architecture](#1-deployment-architecture)
2. [Installation](#2-installation)
3. [Environment Configuration](#3-environment-configuration)
4. [Production Deployment](#4-production-deployment)
5. [Operational Guidance](#5-operational-guidance)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Deployment Architecture

### 1.1 Deployment Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Local** | Single-machine execution | Development, small-scale analysis |
| **Containerized** | Docker container with PSPP pre-installed | Production, reproducible environments |
| **Cloud** | Cloud-based deployment with remote PSPP service | Multi-user SaaS |

### 1.2 System Requirements

| Requirement | Specification |
|-------------|---------------|
| **Python** | 3.10+ |
| **PSPP** | 1.6+ (installed at `/usr/bin/pspp`) |
| **Memory** | 4GB+ recommended |
| **Disk** | 10GB+ for temporary files |
| **API Keys** | OpenAI API key |

---

## 2. Installation

### 2.1 Source Installation

```bash
# Clone repository
git clone <repository-url>
cd datachat

# Install Python dependencies
pip install -r requirements.txt

# Install PSPP (Ubuntu/Debian)
sudo apt-get install pspp

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2.2 Verify Installation

```bash
# Verify Python version
python --version  # Should be 3.10+

# Verify PSPP installation
pspp --version    # Should be 1.6+

# Verify dependencies
pip list | grep -E "langgraph|langchain|openai|pyreadstat"
```

---

## 3. Environment Configuration

### 3.1 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `PSPP_PATH` | Path to PSPP executable | `/usr/bin/pspp` | No |
| `OUTPUT_DIR` | Output directory path | `output/` | No |
| `TEMP_DIR` | Temporary files directory | `temp/` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### 3.2 Environment Setup

**Via command line:**
```bash
export OPENAI_API_KEY="your-key-here"
export PSPP_PATH="/usr/bin/pspp"
```

**Via .env file (recommended):**
```bash
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "PSPP_PATH=/usr/bin/pspp" >> .env
```

### 3.3 Development vs Production Configuration

**Development (.env)**:
```bash
OPENAI_API_KEY=sk-dev-key...
OUTPUT_DIR=output
TEMP_DIR=temp
LOG_LEVEL=DEBUG
```

**Production (.env.production)**:
```bash
OPENAI_API_KEY=sk-prod-key...
OUTPUT_DIR=/var/lib/survey-analyzer/output
TEMP_DIR=/var/lib/survey-analyzer/temp
LOG_LEVEL=INFO
```

---

## 4. Production Deployment

### 4.1 Production Directory Structure

```
/opt/survey-analyzer/
├── agent/                  # Application code
├── config/                 # Configuration files
├── output/                 # Generated outputs
│   ├── logs/              # Execution logs
│   ├── reviews/           # Human review documents
│   └── temp/              # Temporary files
├── data/
│   └── input/             # Input .sav files
├── checkpoints.db         # State persistence
└── .env                   # Environment variables (production)
```

### 4.2 Path Configuration

| Item | Development | Production |
|------|-------------|------------|
| **Project Root** | `~/workspaces/datachat/` | `/opt/survey-analyzer/` |
| **Input Data** | `data/input/` | `/var/lib/survey-analyzer/input/` |
| **Output** | `output/` | `/var/lib/survey-analyzer/output/` |
| **Checkpoints** | `checkpoints.db` | `/var/lib/survey-analyzer/checkpoints.db` |
| **PSPP** | `/usr/bin/pspp` | `/usr/bin/pspp` |

### 4.3 Production Setup

```bash
# Create production directories
sudo mkdir -p /opt/survey-analyzer
sudo mkdir -p /var/lib/survey-analyzer/{input,output,temp}

# Copy application code
sudo cp -r agent/ /opt/survey-analyzer/
sudo cp -r config/ /opt/survey-analyzer/

# Set permissions
sudo chown -R app-user:app-user /opt/survey-analyzer
sudo chown -R app-user:app-user /var/lib/survey-analyzer

# Configure production environment
cp .env.production /opt/survey-analyzer/.env
```

---

## 5. Operational Guidance

### 5.1 Logging Strategy

| Log Level | Usage | Storage |
|-----------|-------|---------|
| **INFO** | Step start, completion, key outputs | `output/logs/` |
| **WARNING** | Validation failures, skipped items | `output/logs/` + state |
| **ERROR** | Exceptions, failures | `output/logs/` + state |
| **DEBUG** | Detailed execution trace | `output/logs/debug/` |

### 5.2 Error Handling

| Category | Examples | Handling Strategy |
|----------|----------|-------------------|
| **LLM Errors** | Rate limits, API failures | Retry with exponential backoff |
| **Validation Errors** | Invalid references, syntax errors | Automatic retry up to max_iterations |
| **PSPP Errors** | Syntax errors, file not found | Parse PSPP output logs, provide specific error messages |
| **File I/O Errors** | Missing files, permission errors | Validate paths before execution, fail gracefully |
| **Statistical Errors** | Insufficient sample size | Warn and continue, mark table as invalid |

### 5.3 Recovery Mechanisms

| Mechanism | Purpose |
|-----------|---------|
| **SQLite Checkpointing** | Resume after human interrupt or crash |
| **Automatic Retry** | Validation errors trigger LLM regeneration |
| **Graceful Degradation** | Continue with warnings on non-critical failures |
| **State Snapshots** | Save state before each three-node pattern |

---

## 6. Troubleshooting

### 6.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **PSPP not found** | PSPP not installed or wrong path | Install PSPP or set `PSPP_PATH` |
| **API key error** | Missing/invalid OpenAI key | Check `.env` file |
| **Memory error** | Large survey file | Increase available RAM |
| **Validation loop** | LLM generates invalid output | Increase `max_self_correction_iterations` |
| **Permission denied** | Cannot write to output directory | Check directory permissions |

### 6.2 Error Messages

| Error | Meaning | Action |
|-------|---------|--------|
| `Variable not found in metadata` | LLM referenced non-existent variable | Review will catch this; approve with feedback |
| `PSPP syntax error` | Generated PSPP code is invalid | Check `output/pspp_logs.txt` |
| `Insufficient sample size` | Cell count too small for chi-square | Table marked as invalid; continues |
| `Max iterations exceeded` | Validation keeps failing | Review manually; provide guidance |

### 6.3 Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m agent.graph --input survey.sav
```

### 6.4 Getting Help

1. **Check logs**: `output/logs/` for detailed error messages
2. **Review PSPP output**: `output/pspp_logs.txt` for PSPP errors
3. **Verify input**: Ensure .sav file is valid SPSS format
4. **Check configuration**: Verify all required config values are set

---

## Related Documents

| Document | Content |
|----------|---------|
| **[System Architecture](./system-architecture.md)** | System components and architecture |
| **[Project Structure](./project-structure.md)** | Directory structure and file locations |
| **[Configuration](./configuration.md)** | Configuration options and usage |
| **[Data Flow](./data-flow.md)** | Workflow design and step specifications |
