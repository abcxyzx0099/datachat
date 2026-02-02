# LangGraph Studio Setup

## Overview

LangGraph Studio provides a visual interface for developing, testing, and debugging LangGraph workflows. This document covers the setup for the DataChat Survey Analyzer project.

## Prerequisites

- Python 3.11+ with virtual environment
- LangSmith account (free tier works)
- Reverse proxy configured (nginx) with SSL certificate

## Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Studio UI | `https://smith.langchain.com/studio/?baseUrl=https://www.sysy.site/studio` | Visual Studio interface |
| API Docs | `https://www.sysy.site/studio/docs` | API documentation |
| Health | `https://www.sysy.site/studio/info` | Server status |

## Configuration

### langgraph.json

Located at project root, defines graph for Studio:

```json
{
  "graphs": {
    "survey_analysis": "agent/graph.py:graph_for_studio"
  },
  "env": ".env",
  "dependencies": ["."]
}
```

### Environment Variables (.env)

```bash
# LangSmith Tracing
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=DataChat-Survey-Developer
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...

# CORS
ALLOWED_ORIGINS=https://smith.langchain.com,https://www.sysy.site
```

## Starting the Server

Use the provided start script:

```bash
./start.sh
```

This starts:
- LangGraph Studio on port 2024
- Custom API on port 8123
- Frontend UI on port 3000

The server includes the `--allow-blocking` flag to prevent async blocking errors.

## Nginx Reverse Proxy

The `/studio/` location proxies to `http://127.0.0.1:2024/` with:

- CORS headers for LangSmith Studio
- WebSocket support
- Preflight OPTIONS handling

## Troubleshooting

### Graph fails to load

1. Check server is running: `curl https://www.sysy.site/studio/info`
2. Check for blocking errors in logs: `tail -f logs/studio.log`
3. Verify ValidationResult is TypedDict, not dataclass

### CORS errors

If you see "Request header field not allowed" errors:
- Add missing header to nginx `Access-Control-Allow-Headers`
- Reload nginx: `sudo systemctl reload nginx`

### Connection refused

1. Verify reverse proxy is configured
2. Check port 2024 is accessible: `netstat -tlnp | grep 2024`
3. Restart server: `./stop.sh && ./start.sh`

## Data Persistence

Studio uses in-memory checkpointing by default. For persistent storage, SQLite is available with `langgraph-checkpoint-sqlite` package.

## Graph Structure

The `survey_analysis` graph contains 24 nodes organized into 8 phases:

1. **Extraction** (3 nodes): Extract SPSS, transform metadata, filter
2. **Recoding** (5 nodes): Generate/validate/review rules, generate/execute PSPP
3. **Indicators** (3 nodes): Generate/validate/review indicators
4. **Tables** (5 nodes): Generate/validate/review specs, generate/execute PSPP
5. **Statistics** (2 nodes): Generate/execute Python script
6. **Filtering** (2 nodes): Generate filter list, apply filters
7. **PowerPoint** (1 node): Generate presentation
8. **Dashboard** (1 node): Generate HTML dashboard

## See Also

- [Issue Fix Documentation](../../ISSUE-20250202-langgraph-studio-serialization-fix.md)
- [LangGraph Studio Official Docs](https://docs.langchain.com/langsmith/troubleshooting-studio)
