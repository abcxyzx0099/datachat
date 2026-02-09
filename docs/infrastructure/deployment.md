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
| **Python** | 3.11+ |
| **PSPP** | 1.6+ (installed at `/usr/bin/pspp`) |
| **Memory** | 4GB+ recommended |
| **Disk** | 10GB+ for temporary files |
| **API Keys** | At least one LLM provider API key (Kimi, DeepSeek, or Zhipu) |

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
# Edit .env and add your LLM provider API keys (see Configuration documentation)
```

### 2.2 Verify Installation

```bash
# Verify Python version
python --version  # Should be 3.11+

# Verify PSPP installation
pspp --version    # Should be 1.6+

# Verify dependencies
pip list | grep -E "langgraph|langchain|openai|pyreadstat"
```

---

## 3. Environment Configuration

### 3.1 Environment Variables

> **For complete LLM provider configuration**, see [Configuration](./system-configuration.md#2-llm-provider-configuration).

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LLM_PROVIDER` | LLM provider selection (`KIMI`, `DEEPSEEK`, `ZHIPU`) | `ZHIPU` | Yes |
| `KIMI_API_KEY` | Kimi (Moonshot AI) API key | - | If using Kimi |
| `DEEPSEEK_API_KEY` | DeepSeek API key | - | If using DeepSeek |
| `ZHIPU_API_KEY` | Zhipu GLM API key | - | If using Zhipu |
| `PSPP_PATH` | Path to PSPP executable | `/usr/bin/pspp` | No |
| `OUTPUT_DIR` | Output directory path | `output/` | No |
| `TEMP_DIR` | Temporary files directory | `temp/` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### 3.2 Environment Setup

**Via command line (using Zhipu as example):**
```bash
export LLM_PROVIDER=ZHIPU
export ZHIPU_API_KEY="your-key-here"
export PSPP_PATH="/usr/bin/pspp"
```

**Via .env file (recommended):**
```bash
# Select your LLM provider
LLM_PROVIDER=ZHIPU

# Add API key for your selected provider
ZHIPU_API_KEY=your-zhipu-api-key-here

# PSPP configuration
PSPP_PATH=/usr/bin/pspp
```

### 3.3 Development vs Production Configuration

**Development (.env)**:
```bash
LLM_PROVIDER=ZHIPU
ZHIPU_API_KEY=your-zhipu-dev-key...
OUTPUT_DIR=output
TEMP_DIR=temp
LOG_LEVEL=DEBUG
```

**Production (.env.production)**:
```bash
LLM_PROVIDER=ZHIPU
ZHIPU_API_KEY=your-zhipu-prod-key...
OUTPUT_DIR=/var/lib/survey-analyzer/output
TEMP_DIR=/var/lib/survey-analyzer/temp
LOG_LEVEL=INFO
```

---

## 4. Production Deployment

### 4.1 Production Directory Structure

DataChat is installed to `/opt/survey-analyzer/` in production:

```
/opt/survey-analyzer/
├── agent/              # Application code
├── config/             # Configuration files
├── utils/              # Utilities
├── venv/               # Python virtual environment
├── data/               # Input survey files
│   └── input/         # Upload .sav files here
├── output/             # Generated outputs
│   ├── logs/          # Execution logs
│   ├── reviews/       # Human review documents
│   └── temp/          # Temporary generated files
├── temp/               # Temporary files (PSPP syntax, scripts)
├── logs/               # Application logs
├── checkpoints/        # State persistence directory
├── checkpoints.db      # SQLite checkpoint database
├── requirements.txt    # Python dependencies
└── .env                # Environment configuration (production)
```

### 4.2 Path Configuration

| Item | Development | Production |
|------|-------------|------------|
| **Project Root** | `~/workspaces/datachat/` | `/opt/survey-analyzer/` |
| **Input Data** | `data/input/` | `/opt/survey-analyzer/data/input/` |
| **Output** | `output/` | `/opt/survey-analyzer/output/` |
| **Checkpoints** | `checkpoints.db` | `/opt/survey-analyzer/checkpoints.db` |
| **PSPP** | `/usr/bin/pspp` | `/usr/bin/pspp` |

### 4.3 Automated Installation

The easiest way to deploy to production is using the provided installation scripts:

```bash
# Clone repository
git clone <repository-url>
cd datachat

# Run installation (installs to /opt/survey-analyzer)
sudo ./scripts/install.sh

# Configure environment
sudo ./scripts/configure.sh

# Edit .env with your API keys
sudo nano /opt/survey-analyzer/.env

# Install systemd service
sudo cp scripts/datachat.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable datachat

# Start the service
sudo systemctl start datachat

# Check status
sudo systemctl status datachat
```

### 4.4 Installation Scripts

| Script | Purpose |
|--------|---------|
| `scripts/install.sh` | Installs application to `/opt/survey-analyzer/`, creates service user, installs dependencies |
| `scripts/configure.sh` | Creates `.env` file and initializes directories |
| `scripts/start.sh` | Manually starts the LangGraph server (for testing) |
| `scripts/stop.sh` | Stops the running service |

### 4.5 Systemd Service Management

```bash
# Service control
sudo systemctl start datachat    # Start service
sudo systemctl stop datachat     # Stop service
sudo systemctl restart datachat  # Restart service
sudo systemctl status datachat   # Check status

# Enable/disable auto-start on boot
sudo systemctl enable datachat   # Enable auto-start
sudo systemctl disable datachat  # Disable auto-start

# View logs
sudo journalctl -u datachat              # View all logs
sudo journalctl -u datachat -f           # Follow logs in real-time
sudo journalctl -u datachat --since today  # View today's logs
```

### 4.6 Service User

The service runs as the `surveychat` user for security:

- Created automatically by `install.sh`
- Home directory: `/opt/survey-analyzer`
- No shell login: `/bin/false`
- Owns application files and directories

### 4.7 Docker Deployment

For containerized deployment, use Docker Compose:

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

**Note**: See `docker-compose.yml` for configuration details.

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
| **API key error** | Missing/invalid LLM provider API key | Check `.env` file and verify `LLM_PROVIDER` setting |
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

1. **Check logs**: `output/logs/` or `journalctl -u datachat` for detailed error messages
2. **Review PSPP output**: `output/pspp_logs.txt` for PSPP errors
3. **Verify input**: Ensure .sav file is valid SPSS format
4. **Check configuration**: Verify all required config values are set
5. **Test manually**: Use `scripts/start.sh` to run the server directly for debugging

---

## Related Documents

| Document | Content |
|----------|---------|
| **[System Architecture](./system-architecture.md)** | System components and architecture |
| **[Project Structure](./project-structure.md)** | Directory structure and file locations |
| **[Configuration](./system-configuration.md)** | Configuration options and usage |
| **[Data Flow](./data-flow.md)** | Workflow design and step specifications |
| **[Web Interface](./web-interface.md)** | Agent Chat UI setup and usage |
