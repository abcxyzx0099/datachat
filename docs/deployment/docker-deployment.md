# DataChat - Docker Deployment Guide

This guide explains how to deploy DataChat using Docker containers.

## Prerequisites

- Docker 20.10 or higher
- Docker Compose 2.0 or higher
- At least 2GB RAM available for Docker
- API keys for one of the supported LLM providers (Zhipu, DeepSeek, or Kimi)

## Quick Start

1. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

2. **Build the Docker image:**
   ```bash
   bash scripts/docker-build.sh
   ```

3. **Start the container:**
   ```bash
   bash scripts/docker-start.sh
   ```

4. **Access the application:**
   - LangGraph Studio: http://localhost:8123

## Docker Scripts

| Script | Purpose |
|--------|---------|
| `scripts/docker-build.sh` | Build the Docker image |
| `scripts/docker-start.sh` | Start the container |
| `scripts/docker-stop.sh` | Stop the container |
| `scripts/docker-logs.sh` | View container logs |
| `scripts/docker-exec.sh` | Execute commands inside the container |
| `scripts/docker-clean.sh` | Remove containers and images |

## Usage Examples

### Build and Start

```bash
# Build the image
bash scripts/docker-build.sh

# Start in foreground (to see logs)
docker-compose up

# Start in detached mode (background)
bash scripts/docker-start.sh
```

### View Logs

```bash
# Follow logs in real-time
bash scripts/docker-logs.sh

# View all logs without following
bash scripts/docker-logs.sh -n

# View logs with docker-compose directly
docker-compose logs -f datachat
```

### Execute Commands in Container

```bash
# Start interactive shell
bash scripts/docker-exec.sh

# Run specific command
bash scripts/docker-exec.sh python -c "import agent.graph; print('OK')"

# Check PSPP installation
bash scripts/docker-exec.sh pspp --version
```

### Stop and Clean

```bash
# Stop container
bash scripts/docker-stop.sh

# Stop and remove volumes
docker-compose down -v

# Remove everything (including images)
bash scripts/docker-clean.sh --all
```

## Volume Mounts

The following directories are mounted as volumes:

| Host Path | Container Path | Purpose | Mode |
|-----------|----------------|---------|------|
| `./data` | `/app/data` | Input data files | Read-only |
| `./output` | `/app/output` | Generated output files | Read-write |
| `./temp` | `/app/temp` | Temporary files | Read-write |
| `./logs` | `/app/logs` | Application logs | Read-write |
| `./checkpoints.db` | `/app/checkpoints.db` | LangGraph state persistence | Read-write |

## Environment Variables

All environment variables from `.env.example` are supported in Docker. Key variables:

```yaml
# LLM Provider (required)
LLM_PROVIDER: ZHIPU  # Options: ZHIPU, DEEPSEEK, KIMI

# API Keys (required for selected provider)
ZHIPU_API_KEY: your-key-here
DEEPSEEK_API_KEY: your-key-here
KIMI_API_KEY: your-key-here

# Paths (automatically set in Docker)
PSPP_PATH: /usr/bin/pspp
OUTPUT_DIR: /app/output
TEMP_DIR: /app/temp
```

## Ports

- **8123**: LangGraph development server

## Health Check

The container includes a health check that verifies the application is running:

```bash
# Check health status
docker-compose ps

# View health check logs
docker inspect datachat-app | grep -A 10 Health
```

## Troubleshooting

### Container Won't Start

1. Check if Docker daemon is running:
   ```bash
   docker info
   ```

2. Check logs:
   ```bash
   bash scripts/docker-logs.sh
   ```

3. Verify `.env` file exists and is configured:
   ```bash
   ls -la .env
   cat .env | grep API_KEY
   ```

### Permission Issues

If you encounter permission issues with output files:

```bash
# Fix permissions on host
sudo chown -R $USER:$USER output/ temp/ logs/

# Or run container with explicit user ID in docker-compose.yml:
# user: "${UID}:${GID}"
```

### Build Failures

1. **Out of space**: Clean Docker cache:
   ```bash
   docker system prune -a
   ```

2. **Network issues**: Check Docker can reach package repositories

3. **PSPP installation fails**: The Dockerfile includes PSPP installation from apt-get. If this fails, check your base image is accessible.

### PSPP Not Working

Verify PSPP is installed:

```bash
bash scripts/docker-exec.sh pspp --version
bash scripts/docker-exec.sh which pspp
```

Expected output:
```
PSPP, a program for statistical analysis.
```

## Production Deployment

For production deployment:

1. **Use PostgreSQL instead of SQLite:**
   Uncomment the `postgres` service in `docker-compose.yml`

2. **Configure persistent volumes:**
   Ensure volume mounts point to persistent storage

3. **Set up reverse proxy:**
   Use nginx or traefik to expose the service

4. **Enable HTTPS:**
   Configure SSL certificates

5. **Set resource limits:**
   Add to `docker-compose.yml`:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

## Security Considerations

1. **Non-root user**: The container runs as `appuser` (UID 1000)
2. **Read-only data**: Input data directory is mounted read-only
3. **Environment variables**: Sensitive keys are in `.env` file (not in image)
4. **Minimal base image**: Uses `python:3.11-slim` for smaller attack surface

## Development Tips

### Rebuild After Code Changes

```bash
# Rebuild and restart
docker-compose up --build

# Or use the script
bash scripts/docker-build.sh && bash scripts/docker-start.sh
```

### Debug Mode

Enable debug logging:

```bash
# In docker-compose.yml, add:
# LOG_LEVEL: DEBUG

docker-compose up
```

### Interactive Development

```bash
# Run container with shell access
docker-compose run --rm datachat bash

# Install additional packages for testing
pip install pytest
```

## Updating

To update DataChat to a new version:

```bash
# Pull latest code
git pull

# Rebuild image
bash scripts/docker-build.sh

# Restart container
bash scripts/docker-stop.sh && bash scripts/docker-start.sh
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Host                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │          datachat-app Container                  │    │
│  │  ┌─────────────────────────────────────────┐    │    │
│  │  │  Python 3.11                            │    │    │
│  │  │  ├─ PSPP (statistical tool)             │    │    │
│  │  │  ├─ LangGraph (workflow engine)         │    │    │
│  │  │  └─ DataChat Agent                      │    │    │
│  │  └─────────────────────────────────────────┘    │    │
│  │                                                   │    │
│  │  Volume Mounts:                                   │    │
│  │  ./data → /app/data (read-only)                  │    │
│  │  ./output → /app/output                          │    │
│  │  ./temp → /app/temp                              │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  Port 8123: LangGraph Studio ←→ Host:8123              │
└─────────────────────────────────────────────────────────┘
```
