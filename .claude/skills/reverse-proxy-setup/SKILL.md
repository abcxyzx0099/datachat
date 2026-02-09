---
name: reverse-proxy-setup
description: Set up Nginx reverse proxy with SSL/HTTPS for web applications. Eliminates need for SSH port forwarding by exposing services through standard HTTP/HTTPS ports. Use when user needs to access remote server services without port forwarding, set up SSL/HTTPS with Let's Encrypt, configure reverse proxy for multiple backend services (e.g. frontend on port 3000, API on port 8123, LangGraph Studio on port 2024), enable both domain.com and www.domain.com access, or configure WebSocket support for real-time applications.
---

# Nginx Reverse Proxy Setup

## Overview

Set up Nginx reverse proxy with automatic SSL/HTTPS using Let's Encrypt. Exposes multiple backend services through a single domain on standard ports (80/443), eliminating the need for SSH port forwarding.

**What this enables:**
- Access remote services via `https://domain.com/` instead of `localhost:3000`
- Automatic SSL certificate acquisition and renewal
- WebSocket support for real-time applications
- Path-based routing (e.g., `/api` → port 8123, `/studio` → port 2024)

## Quick Start

### Interactive Setup (Recommended)

Use when domain, ports, and configuration may vary:

```bash
# 1. Install Nginx and certbot
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# 2. Verify DNS records point to this server
dig +short A yourdomain.com
dig +short A www.yourdomain.com

# 3. Create Nginx configuration
# See assets/nginx-template.conf for template
sudo cp assets/nginx-template.conf /etc/nginx/sites-available/yourdomain.com

# 4. Edit configuration: replace {DOMAIN} and {PORT*} placeholders
# 5. Enable site and test
sudo ln -s /etc/nginx/sites-available/yourdomain.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 6. Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Automated Setup

Use the bundled script for faster deployment:

```bash
cd scripts
chmod +x setup.sh
sudo ./setup.sh example.com 2024 8123 3000
# Then manually run SSL step:
sudo certbot --nginx -d example.com -d www.example.com
```

## DNS Requirements

Before starting, ensure DNS A records exist:

| Record | Type | Value |
|--------|------|-------|
| `@` or domain root | A | Server's public IP |
| `www` | A | Server's public IP |

Verify with:
```bash
dig +short A yourdomain.com
dig +short A www.yourdomain.com
```

## Cloud Platform Firewall

Ensure these ports are open on your cloud platform (AWS Security Groups, GCP firewall, Azure NSG, etc.):

| Port | Purpose | Required |
|------|---------|----------|
| 80 | HTTP (for Let's Encrypt verification) | Yes |
| 443 | HTTPS (main access) | Yes |
| 2024, 8123, 3000, etc. | Backend services | No (local only) |

**Note:** Backend service ports do NOT need to be exposed. Nginx proxies to them via `127.0.0.1`.

## Configuration Template

The `assets/nginx-template.conf` file provides a ready-to-use template with:

- HTTP to HTTPS redirect
- SSL configuration placeholders
- Three service examples (LangGraph Studio, API Backend, Frontend)
- WebSocket support
- Security headers

**Placeholders to replace:**
- `{DOMAIN}` → Your domain name
- `{PORT1}`, `{PORT2}`, `{PORT3}` → Your backend service ports

**Example routing:**
| External URL | Backend Port |
|--------------|--------------|
| `/` | 3000 (Frontend) |
| `/studio` | 2024 (LangGraph) |
| `/api` | 8123 (FastAPI) |

## SSL Certificate Management

### Initial Setup

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Certbot will:
1. Verify domain ownership via HTTP
2. Generate SSL certificate
3. Update Nginx configuration automatically
4. Set up auto-renewal via systemd timer

### Verification

```bash
# Check certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com </dev/null 2>/dev/null | grep -E "subject|issuer"

# Test HTTPS access
curl -I https://yourdomain.com
```

### Renewal

Certificates auto-renew, but manual renewal:
```bash
sudo certbot renew
```

Check renewal status:
```bash
sudo systemctl status certbot.timer
```

## Common Issues

### DNS Propagation

If Let's Encrypt fails with connection timeout:
- DNS may not have propagated (wait 5-15 minutes)
- Check DNS from multiple sources: `dig @8.8.8.8 yourdomain.com`
- Verify cloud firewall allows ports 80/443

### Multiple A Records

If domain returns multiple IPs:
```bash
host yourdomain.com
# Should show only your server's IP
```
Remove old IPs at your DNS provider.

### Port Already in Use

If port 80/443 conflict:
```bash
sudo lsof -i :80
sudo lsof -i :443
# Stop conflicting services (e.g., Apache)
sudo systemctl stop apache2
```

## Access URLs After Setup

| Service | URL |
|---------|-----|
| Frontend | `https://yourdomain.com/` |
| LangGraph Studio | `https://yourdomain.com/studio` |
| API Backend | `https://yourdomain.com/api` |
| With www | `https://www.yourdomain.com/` |

## Resources

- **scripts/setup.sh** - Automated setup script
- **assets/nginx-template.conf** - Nginx configuration template
