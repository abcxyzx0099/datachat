# AionUi + DataChat Hybrid Integration Setup Guide

This guide explains how to set up the hybrid architecture where AionUi provides the chat interface while LangGraph handles workflow orchestration.

## Architecture Overview

```
┌─────────────────┐     ACP      ┌─────────────────┐     HTTP      ┌─────────────────┐
│   AionUi WebUI  │ ◄────────────► │  Claude Code    │ ◄────────────► │  LangGraph API  │
│   (Port 3000)   │               │  (via ACP)      │               │   (Port 8123)   │
└─────────────────┘               └─────────────────┘               └─────────────────┘
                                                                            │
                                                                            ▼
                                                                   ┌─────────────────┐
                                                                   │  Data Processing │
                                                                   │  (22 Nodes)      │
                                                                   └─────────────────┘
```

## Components

### 1. AionUi WebUI (Frontend)
- **Port**: 3000 (default) or 25808 (Android)
- **Purpose**: Chat interface for users
- **Startup**: `npm run webui:remote`

### 2. Claude Code (AI Agent)
- **Protocol**: ACP (Agent Client Protocol)
- **Purpose**: Processes user requests and manages workflow
- **Skills**: datachat skill wraps LangGraph API calls

### 3. LangGraph API (Backend)
- **Port**: 8123
- **Purpose**: Orchestrates 22-step data processing workflow
- **Startup**: `python -m agent.server`

## Setup Instructions

### Step 1: Start LangGraph API

```bash
cd /home/admin/workspaces/datachat

# Activate virtual environment
source .venv/bin/activate

# Start the API server
python -m agent.server
```

The API will be available at `http://localhost:8123`

### Step 2: Start AionUi in WebUI Mode

```bash
cd /home/admin/workspaces/AionUi

# Start WebUI with remote access
npm run webui:remote
```

AionUi will be available at `http://localhost:3000`

### Step 3: Configure ACP Integration

In AionUi settings:
1. Go to **Settings** → **Multi-Agent Mode**
2. Add Claude Code agent configuration
3. Enable the datachat skill

### Step 4: Test the Integration

From AionUi chat interface:
```
User: Analyze my survey data at /home/admin/workspaces/datachat/test_data.sav

AionUi/Claude Code will:
1. Recognize the datachat skill trigger
2. Call the LangGraph API
3. Monitor progress
4. Return results with output file locations
```

## Direct CLI Usage

You can also run analyses directly from the command line:

```bash
# Run analysis
cd /home/admin/workspaces/AionUi/skills/datachat
python scripts/run_analysis.py /path/to/survey.sav

# Run with custom thread ID
python scripts/run_analysis.py /path/to/survey.sav --thread-id my-analysis

# Resume interrupted analysis
python scripts/run_analysis.py --resume --thread-id my-analysis

# Wait for completion with progress bar
python scripts/run_analysis.py /path/to/survey.sav --wait
```

## API Endpoints

The LangGraph API provides the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze` | POST | Start new analysis |
| `/api/resume` | POST | Resume from checkpoint |
| `/api/status/{thread_id}` | GET | Get current status |
| `/api/results/{thread_id}` | GET | Get results |
| `/api/health` | GET | Health check |

### Example API Calls

```bash
# Start analysis
curl -X POST http://localhost:8123/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "input_file_path": "/path/to/survey.sav",
    "thread_id": "my-analysis",
    "checkpoint_db": "checkpoints.db"
  }'

# Check status
curl http://localhost:8123/api/status/my-analysis

# Get results
curl http://localhost:8123/api/results/my-analysis
```

## Configuration Files

### Environment Variables

Set these in your environment or `.env` file:

```bash
# LangGraph API
LANGGRAPH_API_URL=http://localhost:8123
CHECKPOINT_DB_PATH=/home/admin/workspaces/datachat/checkpoints.db

# AionUi WebUI
AIONUI_PORT=3000
AIONUI_REMOTE=true

# Claude Code
ANTHROPIC_API_KEY=your_api_key_here
```

### AionUi WebUI Config

Create `/home/admin/.config/AionUi/webui.config.json`:

```json
{
  "port": 3000,
  "allowRemote": true,
  "defaultAgent": "claude-code"
}
```

## Systemd Services (Optional)

For production deployment, create systemd services:

### LangGraph API Service

`/etc/systemd/system/datachat-api.service`:

```ini
[Unit]
Description=DataChat LangGraph API
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/workspaces/datachat
Environment="PATH=/home/admin/workspaces/datachat/.venv/bin"
ExecStart=/home/admin/workspaces/datachat/.venv/bin/python -m agent.server
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### AionUi WebUI Service

`/etc/systemd/system/aionui-webui.service`:

```ini
[Unit]
Description=AionUi WebUI Service
After=network.target datachat-api.service

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/workspaces/AionUi
ExecStart=/usr/bin/npm run webui:remote
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable datachat-api aionui-webui
sudo systemctl start datachat-api aionui-webui
```

## Firewall Configuration

If running on a remote server, open necessary ports:

```bash
# Allow WebUI port
sudo ufw allow 3000/tcp

# Allow LangGraph API port (if needed for external access)
sudo ufw allow 8123/tcp
```

## Troubleshooting

### AionUi WebUI won't start

```bash
# Check if port is in use
lsof -i :3000

# Use different port
npm run cli -- --webui --port 8080
```

### LangGraph API not reachable

```bash
# Check if API is running
curl http://localhost:8123/api/health

# Check API logs
tail -f /home/admin/workspaces/datachat/agent.log
```

### ACP connection fails

```bash
# Verify Claude Code is installed
claude --version

# Check ACP configuration in AionUi
# Settings → Multi-Agent Mode → Claude Code
```

### Analysis stuck at a step

```bash
# Check thread status
python /home/admin/workspaces/AionUi/skills/datachat/scripts/run_analysis.py \
  --status --thread-id <thread_id>

# Resume if needed
python /home/admin/workspaces/AionUi/skills/datachat/scripts/run_analysis.py \
  --resume --thread-id <thread_id>
```

## File Locations

| Component | Location |
|-----------|----------|
| datachat source | `/home/admin/workspaces/datachat` |
| AionUi source | `/home/admin/workspaces/AionUi` |
| datachat skill | `/home/admin/workspaces/AionUi/skills/datachat/` |
| Run analysis script | `/home/admin/workspaces/AionUi/skills/datachat/scripts/run_analysis.py` |
| Checkpoints | `/home/admin/workspaces/datachat/checkpoints.db` |
| Output files | `/home/admin/workspaces/datachat/output/<timestamp>/` |

## Next Steps

1. ✅ Set up LangGraph API service
2. ✅ Set up AionUi WebUI service
3. ⏳ Test with sample data
4. ⏳ Configure reverse proxy for external access
5. ⏳ Set up monitoring and logging

## Support

- **datachat documentation**: `/home/admin/workspaces/datachat/docs/`
- **AionUi documentation**: https://github.com/iOfficeAI/AionUi
- **ACP documentation**: https://agentclientprotocol.com/
