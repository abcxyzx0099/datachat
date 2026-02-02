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
- Production code (`dflib/`, `agent/`, `web/backend/`, `web/frontend/`)
- Configuration files
- Tests (`web/e2e-tests/`, `web/backend/tests/`)
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

### Application Design Documents (`docs/application-design/`)

| Rule | Description |
|------|-------------|
| **Explicit user request required** | Do NOT create documents in `docs/application-design/` without user permission |
| **User-triggered only** | Only save to this directory when the user explicitly requests it |
| **Purpose** | High-level design, architecture, and specification documents |

**When to create in `docs/application-design/`:**
- User explicitly requests: "Create a design document for X"
- User explicitly requests: "Save this to application design"
- User asks to document architecture or specifications

**When NOT to create in `docs/application-design/`:**
- AI agent spontaneously decides to document something
- Implementation notes or technical guides
- Code documentation or API references

### Implementation Documents (`implementation/`)

| Rule | Description |
|------|-------------|
| **AI-autonomous creation** | AI agents MAY create documents here freely during implementation |
| **Purpose** | Implementation guides, setup summaries, test coverage, technical notes |
| **Examples** | Setup summaries, coverage reports, implementation guides, test documentation |

**When to create in `implementation/`:**
- During implementation when AI needs to document process
- Test coverage reports and guides
- Setup and configuration summaries
- Implementation notes and technical guides

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
├── development/
│   └── Archive-dflib-20260121-224902/
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

## 8. External AI Assistance

When uncertain about information, solutions, or implementation approaches, the Development Agent can leverage the **`ask-the-deepseek`** skill to get recommendations and double-confirm decisions from another AI agent.

### When to Use ask-the-deepseek

Invoke the `ask-the-deepseek` skill when:
- **Encountering errors or blockers** (e.g., compilation failures, missing dependencies)
- **Seeking alternatives** (e.g., "what are my options for X?")
- **Requiring complex reasoning** (e.g., math, logic, architecture decisions)
- **Needing code review** (e.g., code analysis, bug detection, improvement suggestions)
- **Unclear about solutions** (e.g., "how do I workaround X?")

### Available Modes

| Mode | Best For |
|------|----------|
| **deepseek-reasoner** | Complex reasoning, step-by-step breakdown, math, logic |
| **deepseek-chat** | General chat, quick answers, code assistance |

---
