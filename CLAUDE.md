# DataChat - SPSS Analyzer Web Application


## 1. Communication Rules

- **Request Clarification**: The user is a non-native English speaker using voice input. Requests may contain grammatical errors or misinterpreted words. Infer the intended meaning from context and present a refined version using the pattern: `**Your Request**: "[Refined version]"`. Only seek clarification when intent cannot be determined.

---

## 2. Temporary Files

Scripts or files that are created for **one-time or temporary use** (e.g., migration scripts, test utilities, experimental code) should be placed in the `temp/` directory at the project root:

**Examples of temporary files:**
- Database migration scripts (run once, then can be deleted)
- Experimental features being tested
- Debug utilities
- Quick test scripts

**Examples of persistent files** (should NOT go in `temp/`):
- Production code
- Configuration files
- Tests
- Documentation

When a temporary file has served its purpose, it can be safely deleted.

## 3. Git Branch Management

**CRITICAL RULE**: Always work on the `main` branch unless explicitly requested otherwise.

| Rule | Description |
|------|-------------|
| **Default branch** | `main` |
| **Never auto-switch** | Do NOT switch branches without user request |
| **Branch verification** | Before starting work, verify current branch with `git branch --show-current` |
| **User request required** | Only switch branches when user explicitly asks |

**Examples of explicit user requests:**
- "Switch to the backup branch"
- "Create a new feature branch for X"
- "Checkout branch `feature/login`"

If the current branch is NOT `main` and no explicit request was made:
1. Notify the user: "Currently on `{branch_name}`, switching back to `main`"
2. Switch back: `git checkout main` or `git switch main`

## 4. Documentation Conventions

**CRITICAL RULE**: Never include version, change log, or date metadata in documentation files.

| Attribute | Policy |
|-----------|--------|
| **Version numbers** | ❌ Never include |
| **Change logs** | ❌ Never include |
| **Document dates** | ❌ Never include |
| **Author attribution** | ❌ Never include |

**Rationale**: Git is the single source of truth. `git log`, `git blame`, and tags provide all history tracking. Metadata in documents becomes stale and creates maintenance burden.

**For history tracking, use Git:**
```bash
git log --follow docs/application-design/my-document.md
git blame docs/application-design/my-document.md
```

## 5. Document Creation Guidelines

**CRITICAL RULE**: AI agents must follow strict rules when creating documentation.

### Documentation in `docs/` Directory

| Rule | Description |
|------|-------------|
| **Explicit user request required** | Do NOT create documents in `docs/` or ANY subdirectory without user permission |
| **User-triggered only** | Only save to this directory when the user explicitly requests it |
| **Full restriction applies** | This restriction applies to `docs/` and ALL its subdirectories |

**When to create in `docs/`:**
- User explicitly requests: "Create a design document for X"
- User explicitly requests: "Save this to docs"
- User explicitly requests: "Save to application design"
- User asks to document architecture or specifications

**When NOT to create in `docs/`:**
- AI agent spontaneously decides to document something
- Implementation notes or technical guides
- Code documentation or API references

### Implementation Documents (`implementation/`)

| Rule | Description |
|------|-------------|
| **AI-autonomous creation** | AI agents MAY create documents here freely during implementation |
| **Purpose** | Implementation guides, setup summaries, test coverage, technical notes |

**Directory structure:**

```
implementation/
├── implementation-summary/    # Temporary usage documents (may be deleted)
└── issues/                    # Unresolved issues tracking
```

**When to use each subdirectory:**

| Subdirectory | Purpose | May be deleted |
|--------------|---------|----------------|
| `implementation-summary/` | Temporary implementation notes, setup guides, coverage reports | Yes, when no longer needed |
| `issues/` | Unresolved problems, bugs, or items needing attention | No, resolve first |

**When to create in `implementation/`:**
- During implementation when AI needs to document process
- Test coverage reports and guides (temporary)
- Setup and configuration summaries (temporary)
- Unresolved issues and problems (for tracking)

### Summary

```
docs/application-design/  → User-requested only (high-level design)
implementation/           → AI can create freely (implementation docs)
temp/                     → Temporary/one-time files
```

## 6. Archive Guidelines

**Archive pattern**: `history/{document-type}/Archive-{description}-{timestamp}/`

**Examples:**
```
history/
└── documents/
    └── Archive-Docs-20260121-225013/
```

**Purpose**: Centralized location for completed projects, legacy documents, and historical artifacts.

Use the `material-archiver` skill for archiving development projects.

---

## 7. MCP Servers Configuration

This project uses 3 MCP (Model Context Protocol) servers configured in `.mcp.json`:

| MCP Server | Purpose |
|------------|---------|
| **context7** | Fetches up-to-date library documentation and code examples |
| **playwright** | Browser automation for E2E testing and web interaction |
| **chrome-devtools** | Browser debugging, performance tracing, network inspection |

### When to Use Each MCP Server

- **context7**: Use when you need the latest API references or documentation for any framework/library
- **playwright**: Use for E2E testing, web scraping, form filling, screenshot capture
- **chrome-devtools**: Use for debugging, performance analysis, network request inspection

---

## 8. Agent Teams

This project uses **Claude Code Agent Teams** for BMAD methodology (5 teammates working in parallel).

| Teammate | Phase | Role |
|----------|-------|------|
| **analyst** | 1 (Analysis) | Research, audits, competitive analysis |
| **pm** | 2 (Planning) | Requirements analysis, PRD creation |
| **architect** | 3 (Solutioning) | Technical design, architecture decisions |
| **dev** | 4 (Implementation) | Implementation, code review, testing |
| **qa** | 3-4 | Testing strategy, quality validation |

### Usage

1. **Enable tmux**: Start a tmux session for parallel teammate views
   ```bash
   tmux new -s datachat
   ```

2. **Start Claude**: Run Claude Code within tmux
   ```bash
   claude
   ```

3. **Create agent team**: Request team creation conversationally
   ```
   "Create an agent team with 5 teammates for BMAD development"
   ```

4. **Navigate teammates**: Use `Shift+Down` to cycle through teammate panels in tmux

### Team Configuration

**Team config**: `~/.claude/teams/bmad/config.json` (global team definition)

**Feature Flag**: Agent Teams are enabled via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `~/.claude/settings.json`

**Note**: According to official Agent Teams documentation, teammate roles and descriptions are defined in `config.json`. No separate instruction files are required.

### BMAD Workflow Phases

| Phase | Primary Teammate | Output |
|-------|------------------|--------|
| 1. Analysis | analyst | Research reports, audits, briefs |
| 2. Planning | pm | PRDs, user stories, scope |
| 3. Solutioning | architect | Architecture, ADRs, API specs |
| 4. Implementation | dev | Code, tests, reviews |
| Quality (3-4) | qa | Test strategy, reports, bugs |

---

## 9. Server Ports

| Port | Service | Command | Purpose |
|------|---------|---------|---------|
| **2024** | LangGraph Studio | `langgraph dev` | Official dev server with Studio UI integration |
| **8123** | Custom FastAPI | `python -m agent.server` | Project-specific API wrapper for Agent Chat UI |
| **3000** | Frontend Dev | Vite dev server | Agent Chat UI development server |

### Reverse Proxy URLs (with SSL)

When reverse proxy is configured with domain `sysy.site`:

| Service | URL |
|---------|-----|
| Frontend | `https://www.sysy.site/` |
| LangGraph Studio | `https://www.sysy.site/studio` |
| API Backend | `https://www.sysy.site/api` |

### Starting the Applications

**CRITICAL RULE: AI agents must ALWAYS use `dev-start.sh` to start the application.** Never start servers individually unless explicitly requested for debugging.

```bash
./dev-start.sh
```

**Why `dev-start.sh` is required:**

The script ensures the application runs correctly on all three ports by automatically killing any existing processes on ports 2024, 8123, and 3000 before launching new services, which prevents port conflicts and guarantees each service starts on its designated port (Studio on 2024, API on 8123, UI on 3000). It also coordinates service startup and manages process IDs for graceful shutdown.

To stop all servers:
```bash
./dev-stop.sh
```

---

## 10. Python Environment Usage Plan

This project uses **virtual environments only**. Direct system Python usage is **NOT supported**.

### Deployment Scenarios

| Scenario | Location | Python | Use For |
|----------|----------|--------|---------|
| **Local Development** | `.venv/` | 3.13 | Development, testing, debugging |
| **Docker** | Container | 3.11 | Containerized deployment, CI/CD |
| **Production** | `/opt/survey-analyzer/venv/` | System → New venv | Server deployment, systemd service |

---

## 11. Credential Management

**CRITICAL RULE**: AI agents must follow the credential source-of-truth pattern when working with API keys and configuration credentials.

**Full documentation**: See `[Credential Configuration](docs/application-design/credential-configuration.md)` for credential values and usage patterns.

### Credential Storage Pattern

| File | Purpose | Who Uses It |
|------|---------|-------------|
| `docs/application-design/credential-configuration.md` | **Single source of truth** for credential values | AI agents (read-only) |
| `.env` | Runtime environment variables (actual values) | Application (read-only) |
| `.env.example` | Template with placeholders (no actual credentials) | Developers for reference |

### How AI Agents Should Use Credentials

**When AI agents need to use credentials:**

1. **Read the credential values** from `docs/application-design/credential-configuration.md`
2. **Hardcode the values** into the `.env` file
3. **Application reads only** from `.env` (never directly from this document)

**Workflow:**
```
credential-configuration.md (source)  →  .env (configured by AI)  →  Application (reads at runtime)
```

### Important Notes

- **DO NOT** remove or modify `credential-configuration.md` - it is the reference source
- **DO NOT** hardcode credentials in application code
- **ALWAYS** update `.env` when credential values change
- **NEVER** commit actual credentials to public repositories

---
