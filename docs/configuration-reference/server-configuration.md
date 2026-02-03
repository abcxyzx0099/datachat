# Server Configuration

Server ports, URLs, and networking configuration for the application.

---

## Development Ports

| Port | Service | Command | Purpose |
|------|---------|---------|---------|
| **2024** | LangGraph Studio | `langgraph dev` | Official dev server with Studio UI |
| **8123** | FastAPI Backend | `python -m agent.server` | API wrapper for Agent Chat UI |
| **3000** | Frontend Dev | Vite dev server | Agent Chat UI development server |

---

## Starting the Application

**CRITICAL**: Always use `dev-start.sh` to start the application. The script handles port conflicts and coordinates service startup.

```bash
# Start all services
./dev-start.sh

# Stop all services
./dev-stop.sh
```

### Individual Service Startup (Debugging Only)

| Service | Command |
|---------|---------|
| LangGraph Studio | `langgraph dev` |
| FastAPI Backend | `python -m agent.server` |
| Frontend Dev | `cd web/agent-chat-ui && npm run dev` |

---

## Reverse Proxy URLs (with SSL)

When reverse proxy is configured with domain `sysy.site`:

| Service | URL |
|---------|-----|
| Frontend | `https://www.sysy.site/` |
| LangGraph Studio | `https://www.sysy.site/studio` |
| API Backend | `https://www.sysy.site/api` |

---

## Service Communication

```
┌─────────────────┐      HTTP/WebSocket      ┌──────────────────┐
│  web/           │ ◄────────────────────►  │  agent/server.py │
│  agent-chat-ui  │   Port 8123 (FastAPI)   │  (FastAPI)       │
│  (Next.js)      │                         └────────┬─────────┘
└─────────────────┘                                  │
                                                     ▼
                                            ┌─────────────────┐
                                            │  agent/graph.py │
                                            │  (LangGraph)    │
                                            └─────────────────┘
```

| Service | Depends On |
|---------|-----------|
| Frontend (3000) | API Backend (8123) |
| API Backend (8123) | LangGraph Graph |
| LangGraph Studio (2024) | None |

---

## Related Documents

| Document | Content |
|----------|---------|
| **[Checkpoint Configuration](./checkpoint-configuration.md)** | LangGraph checkpoint storage configuration |
| **[Deployment](../application-design/deployment.md)** | Production deployment configuration |
| **[Web Interface](../application-design/web-interface.md)** | Agent Chat UI setup and usage |
