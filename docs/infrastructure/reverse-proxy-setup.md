# Reverse Proxy Setup

## Overview

Nginx reverse proxy enables public access to DataChat through `https://www.sysy.site` without SSH port forwarding.

## Architecture

```
Internet → nginx (443/80) → Backend Services
                              ├─ Frontend (localhost:3000 or 25808)
                              ├─ API (localhost:8123)
                              ├─ Studio (localhost:2024)
                              └─ Code Server (localhost:8080)
```

## Dual UI Support

DataChat supports two frontend UIs. Switch between them using:

```bash
./switch-ui.sh langgraph    # Agent Chat UI (port 3000)
./switch-ui.sh aionui       # AionUi WebUI (port 25808)
./switch-ui.sh status       # Show current UI
```

### URL Mapping

| Path | Agent Chat UI Mode | AionUi Mode |
|------|-------------------|-------------|
| `/` | `localhost:3000` | `localhost:25808` |
| `/api/` | `localhost:8123` | `localhost:8123` |
| `/studio/` | `localhost:2024` | `localhost:2024` |
| `/code/` | `localhost:8080` | `localhost:8080` |

### Configuration Files

| File | Purpose |
|------|---------|
| `/etc/nginx/sites-available/sysy-langgraph.conf` | Agent Chat UI (port 3000) |
| `/etc/nginx/sites-available/sysy-aionui.conf` | AionUi WebUI (port 25808) |
| `/etc/nginx/sites-enabled/sysy.site` | Active config (symlink) |

## Required Configuration

### 1. Environment Variables

**Backend (`.env`):**
```bash
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://www.sysy.site,https://sysy.site
```

**Frontend (Agent Chat UI) (`web/agent-chat-ui/.env.local`):**
```bash
NEXT_PUBLIC_API_URL=/api
LANGGRAPH_API_URL=http://127.0.0.1:8123
NEXT_PUBLIC_ASSISTANT_ID=survey_analysis
```

### 2. SSL Certificates

Managed by Certbot at `/etc/letsencrypt/live/sysy.site/` (auto-renewal enabled).

## Startup Commands

| Mode | Start Command | Stop Command |
|------|--------------|--------------|
| Agent Chat UI | `./start-langgraph.sh` | `./stop-langgraph.sh` |
| AionUi WebUI | `./start-aionui.sh` | `./stop-aionui.sh` |

## Code Server Access

Code Server (VS Code in browser) is accessible at:
- `https://www.sysy.site/code/` (with SSL)
- `https://sysy.site/code/` (without www)

**Features available:**
- Full VS Code editing experience
- Terminal access (WebSocket enabled)
- File browser and extensions
- Works on mobile devices

## Troubleshooting

**Issue: "Code server not loading"**
- Check code server is running: `curl http://localhost:8080`
- Verify nginx config: `sudo /usr/sbin/nginx -t`
- Check logs: `sudo journalctl -u code-server -n 50`

**Issue: "Failed to connect to LangGraph server"**
- Check backend: `curl http://localhost:8123/health`
- Verify CORS includes your domain in `.env`

**Issue: WebSocket connection failures**
- Verify nginx has `Upgrade` and `Connection` headers

**Issue: UI not accessible after switch**
- Confirm UI was started: `./start-aionui.sh` or `./start-langgraph.sh`
- Check nginx reloaded: `sudo systemctl reload nginx`

## Security

- Backend servers bind to `127.0.0.1` only (not exposed publicly)
- Only nginx listens on public ports (80, 443)
- CORS restrictions limit API access
