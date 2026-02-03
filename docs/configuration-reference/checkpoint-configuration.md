# Checkpoint Configuration

Configuration for LangGraph checkpoint storage to prevent excessive RAM usage.

---

## Problem

By default, LangGraph stores checkpoint databases in `/tmp` using **tmpfs** (temporary filesystem), which lives in **RAM**, not on disk. This can cause significant memory usage issues:

- Default location: `/tmp/checkpoints_*.db`
- Storage type: tmpfs (stored in RAM)
- Impact: Counts toward system memory usage
- Example issue: 6.8 GB RAM consumed by checkpoint database

---

## Solution: SQLite on Disk

Configure LangGraph to use a disk-based SQLite database instead of the default tmpfs storage.

### Configuration

Add the `checkpoint` section to `langgraph.json`:

```json
{
  "graphs": {
    "survey_analysis": "agent/graph.py:graph_for_studio"
  },
  "env": ".env",
  "dependencies": ["."],
  "checkpoint": {
    "path": "./checkpoints.db"
  }
}
```

### Result

| Before | After |
|--------|-------|
| Checkpoints in `/tmp/*.db` (RAM) | Checkpoints in `./checkpoints.db` (disk) |
| Uses tmpfs → counts as RAM | Uses disk → 0 RAM impact |
| 6.8 GB RAM usage (example) | ~0 MB RAM usage |

---

## Checkpoint Storage Options

| Type | Storage | RAM Usage | Best For |
|------|---------|-----------|----------|
| **Default** | `/tmp/*.db` (tmpfs) | HIGH - stored in RAM | Development only |
| `InMemorySaver` | Pure RAM | HIGH | Testing, short-lived |
| `SqliteSaver` | Disk file | LOW | Production, local |
| `PostgresSaver` | PostgreSQL | LOW | Production, scalable |
| `RedisSaver` | Redis | LOW | Production, distributed |

### SQLite (Recommended for Local Development)

```json
{
  "checkpoint": {
    "path": "./checkpoints.db"
  }
}
```

### PostgreSQL (Production)

```json
{
  "checkpoint": {
    "conn": "postgresql://user:pass@localhost/db"
  }
}
```

### Redis (Distributed Production)

```json
{
  "checkpoint": {
    "conn": "redis://localhost:6379"
  }
}
```

---

## Applying Configuration Changes

After modifying `langgraph.json`, restart the development server:

```bash
# Stop all services
./dev-stop.sh

# Start all services
./dev-start.sh
```

---

## Git Configuration

The checkpoint database file should not be committed to git. Ensure `checkpoints.db` is in `.gitignore`:

```bash
# .gitignore
checkpoints.db
```

---

## Troubleshooting

### Disk Full Error from /tmp

If you see "No space left on device" errors or pytest hangs, check if `/tmp` is full:

```bash
# Check disk usage
df -h /tmp

# Find checkpoint files in /tmp
ls -lh /tmp/checkpoints_*.db

# Delete checkpoint files from /tmp (with sudo if needed)
sudo rm -f /tmp/checkpoints_*.db
```

### Tests Hanging or Timeout

If pytest tests hang or timeout:

1. Check `/tmp` is not full (see above)
2. Ensure `checkpoints.db` is not being created in `/tmp`
3. Verify `graph_for_studio()` uses the configured checkpoint path

### Verify Checkpoint Configuration

To verify checkpoints are being stored in the correct location:

```python
from agent.graph import graph_for_studio
import os

# Get the expected checkpoint path
expected_path = os.path.join(os.getcwd(), "checkpoints.db")

# Verify the file exists after running a workflow
assert os.path.exists(expected_path), "checkpoints.db should be in project root"
```

---

## Implementation Notes

The `graph_for_studio()` function in `agent/graph.py` is configured to use the `./checkpoints.db` path specified in `langgraph.json`. This ensures that LangGraph Studio (started via `langgraph dev`) uses disk-based storage instead of tmpfs (RAM).

### Test Checkpoint Location

For pytest tests, the `temp_checkpoint_db` fixture creates checkpoint databases in `tests/checkpoints/` directory. This keeps test artifacts organized and separate from the development checkpoint database.

| Environment | Checkpoint Location | Purpose |
|-------------|-------------------|---------|
| **Development/Production** | `./checkpoints.db` (project root) | Main application checkpoint |
| **Testing** | `tests/checkpoints/checkpoints_*.db` | Test isolation (auto-cleaned) |

This design ensures:
- Test checkpoints don't interfere with development checkpoints
- Easy to identify and clean up test artifacts
- All checkpoint storage uses disk (not RAM) to avoid tmpfs memory issues

---

## Related Documents

| Document | Content |
|----------|---------|
| **[Server Configuration](./server-configuration.md)** | Development ports and service startup |
| **[Credential Configuration](./credential-configuration.md)** | API keys and credential management |
| **[Deployment](../application-design/deployment.md)** | Production deployment configuration |
