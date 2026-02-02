# Reverse Proxy Setup

## Overview

This document describes the nginx reverse proxy configuration for the DataChat application, enabling access through a public domain (`https://www.sysy.site`) without requiring SSH port forwarding.

## Architecture

```
Internet → nginx (443/80) → Backend Services
                              ├─ Frontend (localhost:3000)
                              ├─ API (localhost:8123)
                              └─ Studio (localhost:2024)
```

## URL Mapping

| Path | Backend | Purpose |
|------|---------|---------|
| `/` | `localhost:3000` | Agent Chat UI (Next.js) |
| `/api/` | `localhost:8123` | LangGraph API |
| `/studio/` | `localhost:2024` | LangGraph Studio |

## Required Configuration

### 1. Nginx Configuration

Location: `/etc/nginx/sites-available/sysy.site`

Key settings:
- **SSL/TLS**: Let's Encrypt certificates
- **WebSocket support**: Required for real-time features
- **Client uploads**: 100MB max file size

### 2. Environment Variables

**Backend (`.env`):**
```bash
# CORS - Allow requests from frontend domain
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://www.sysy.site,https://sysy.site
```

**Frontend (`web/agent-chat-ui/.env.local`):**
```bash
# Client-side: Relative path works with reverse proxy
NEXT_PUBLIC_API_URL=/api

# Server-side: Direct connection for API routes
LANGGRAPH_API_URL=http://127.0.0.1:8123

# Assistant ID
NEXT_PUBLIC_ASSISTANT_ID=survey_analysis
```

### 3. Backend Endpoints

**Required endpoints in `agent/server.py`:**

| Endpoint | Purpose |
|----------|---------|
| `/` | API info and available endpoints |
| `/info` | LangGraph SDK compatibility check |
| `/health` | Health check |
| `/threads` | Thread management |
| `/docs` | Swagger documentation |

## How It Works

1. **Browser requests** `https://www.sysy.site/`
2. **Nginx** receives request on port 443 (HTTPS)
3. **Nginx proxies** to `localhost:3000` (Frontend)
4. **Frontend** fetches from `/api/*` (relative path)
5. **Nginx proxies** `/api/*` to `localhost:8123` (Backend)
6. **CORS validation** checks `ALLOWED_ORIGINS`
7. **Response** returned through nginx to browser

## SSL/TLS Certificates

Managed by Certbot:
- Certificate: `/etc/letsencrypt/live/sysy.site/fullchain.pem`
- Private key: `/etc/letsencrypt/live/sysy.site/privkey.pem`
- Auto-renewal: Certbot handles automatically

## Troubleshooting

**Issue: "Failed to connect to LangGraph server"**

Check:
1. Backend is running: `curl http://localhost:8123/health`
2. CORS includes your domain: Check `ALLOWED_ORIGINS` in `.env`
3. `/info` endpoint exists: `curl http://localhost:8123/info`
4. Frontend uses `/api` not `http://localhost:8123`

**Issue: WebSocket connection failures**

Verify nginx configuration includes:
```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

**Issue: Mixed content errors**

Ensure all resources use HTTPS (no `http://` references in frontend code).

## Security Considerations

- Backend servers bind to `127.0.0.1` only (not exposed publicly)
- Only nginx listens on public ports (80, 443)
- CORS restrictions limit which origins can access the API
- Rate limiting and DDoS protection should be configured at nginx level
