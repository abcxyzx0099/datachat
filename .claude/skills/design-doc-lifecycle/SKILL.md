---
name: design-doc-lifecycle
description: Manages application design documentation lifecycle using a 3-tier classification system and content-level refinement. Tier 1: Essential + Persistent (WHAT & WHY) stay in docs/application-design/. Tier 2: Initially Essential → Archive (HOW) move to history/documents/ when code supersedes them. Tier 3: Non-Essential + Persistent (guides/references) move to docs/guides/. Content-level refinement removes detailed specifications now contained in implementation, keeping only high-level architecture, principles, and directions. Maintains single source of truth: code for details, docs for rationale. Use when user requests to review, classify, refine, or reorganize design documentation.
---

# Design Document Lifecycle Skill

## Overview

This skill manages the lifecycle of application design documentation through a **two-phase process with separate confirmations**:

### Phase 1: Document Level (Tier Classification)
- Classify documents into 3 tiers based on purpose and longevity
- **Present plan → Confirm → Execute** document reorganization

### Phase 2: Content Level (Refinement)
- Refine content within Tier 1 documents to maintain single source of truth
- **Present plan → Confirm → Execute** content changes

**CRITICAL:** Each phase requires user confirmation before execution.

The goal is to keep documentation aligned with implementation: detailed specifications migrate to code as the source of truth, while design docs retain high-level architecture, principles, and rationale.

---

## Step 1: Document Level (Tier Classification)

### Protected Documents (NEVER MODIFY - Applies to BOTH Step 1 & Step 2)

**CRITICAL: The following documents are EXEMPT from ALL skill operations.**

The skill must **NEVER** modify, move, archive, or refine these documents in ANY phase:

| Document | Rule | Reason |
|----------|------|--------|
| **`system-architecture.md`** | **NEVER MODIFY** | Core system architecture - foundational design document |
| **`data-flow.md`** | **NEVER MODIFY** | Workflow design and state management - foundational document |

**What this means:**
- ❌ Step 1: NEVER move to Tier 2 (archive) or Tier 3 (guides)
- ❌ Step 2: NEVER modify content (remove/condense/reorganize)
- ✅ ALWAYS keep in `docs/application-design/` as-is
- ✅ ALWAYS exclude from all proposals and operations

### Tier Definitions

| Tier | Type | Content | Location | When to Move |
|------|------|---------|----------|--------------|
| **Tier 1** | Essential + Persistent | **WHAT** and **WHY** | `docs/application-design/` | Never (permanent) |
| **Tier 2** | Initially Essential → Archive | **HOW** (implementation details) | `history/documents/` | When code supersedes doc |
| **Tier 3** | Non-Essential + Persistent | Guides, references, tutorials | `docs/guides/` | When categorized |

### Tier 1: Essential & Persistent (Keep in `docs/application-design/`)

**Content that stays:**
- Architecture decisions and rationale
- Design principles and patterns
- System boundaries and contracts
- Business requirements and context
- Technology choices (with reasoning)
- Security and compliance considerations
- Performance requirements
- Data flow and integration points

**Why:** These represent the **WHY** behind decisions - not obvious from code alone.

### Tier 2: Initially Essential → Archive (Move to `history/documents/`)

**Content to archive:**
- Detailed implementation specifications
- Step-by-step implementation guides
- Temporary design explorations
- Proof-of-concept documentation
- Detailed API specifications (use OpenAPI instead)
- Database schemas (use migrations/ORM instead)

**When to move:** After the feature is implemented and code is the authoritative source.

**Archive pattern:** `history/documents/Archive-{description}-{timestamp}/`

### Tier 3: Non-Essential but Persistent (Move to `docs/guides/`)

**Content to reorganize:**
- How-to guides and tutorials
- Setup instructions
- Reference material
- Developer onboarding content
- Troubleshooting guides

**Why:** These are useful but not architectural design - they belong in a separate guides section.

---

## Step 2: Content Level (Refinement Within Documents)

**IMPORTANT: Content-level refinement ONLY applies to documents in `docs/application-design/` (Tier 1), EXCLUDING protected documents.**

Protected documents (`system-architecture.md`, `data-flow.md`) are **NEVER** modified in any way.

Documents moved to Tier 2 (archive) or Tier 3 (guides) are NOT refined - they are moved as-is.

Even within eligible Tier 1 documents, content should evolve from detailed specifications to concise principles.

### Single Source of Truth Philosophy

| Development Phase | Documentation Focus | Source of Truth |
|-------------------|---------------------|-----------------|
| **Early/Planning** | Detailed specs included | Docs + Code |
| **Active Development** | Mixed details + principles | Code emerging |
| **Mature/Post-Dev** | Concise principles only | Code is truth |

### Content Refinement Rules

| Content Type | Early Stage | Mature Stage | Action |
|--------------|-------------|--------------|--------|
| **Business WHY** | In docs | ✅ Keep | Rationale never leaves docs |
| **Architecture WHAT** | In docs | ✅ Keep | Structure stays in docs |
| **Detailed HOW** | In docs | ❌ Remove | Code is now the source |
| **API Specs** | In docs | ❌ Remove | Reference implementation |
| **Data Models** | In docs | ❌ Simplify | Show relationships only |
| **Code Examples** | In docs | ❌ Remove | Code itself is the example |

### Refinement Example

**Before (Detailed Spec):**
```markdown
## User Authentication Module

### API Endpoints
- POST /auth/login - Request: {email, password} - Response: {token, user}
- POST /auth/register - Request: {name, email, password} - Response: {user}
- POST /auth/refresh - Request: {refreshToken} - Response: {token}
- POST /auth/logout - Request: {} - Response: {success}

### Database Schema
users table:
  - id: UUID, primary key
  - email: VARCHAR(255), unique, indexed
  - password_hash: VARCHAR(255)
  - created_at: TIMESTAMP
  - updated_at: TIMESTAMP

### Implementation Details
- Uses bcrypt for password hashing with cost factor 12
- JWT tokens with 15-minute expiration
- Refresh tokens stored in Redis with 7-day TTL
```

**After (Concise Principles - Still Tier 1):**
```markdown
## User Authentication

### Architecture Decision
JWT-based authentication with refresh token rotation for stateless API security.

### Key Principles
- Passwords hashed with bcrypt (cost 12)
- Access tokens: 15-minute expiry
- Refresh tokens: 7-day expiry, stored in Redis
- See: `agent/server/api/auth.py` for implementation

### Security Considerations
- HTTPS enforced in production
- Refresh token rotation prevents replay attacks
- Email uniqueness enforced at database level
```

---

## Workflow (When Skill is Invoked)

```
┌─────────────────────────────────────────────────────────────────┐
│  USER INVOKES: "Review and refine design documentation"        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: DOCUMENT LEVEL (Tier Classification)                 │
├─────────────────────────────────────────────────────────────────┤
│  1.1 DISCOVER & READ                                           │
│     • Find all markdown files in docs/                          │
│     • EXCLUDE: system-architecture.md, data-flow.md            │
│     • Read all other documents                                  │
│     • List what was found                                       │
├─────────────────────────────────────────────────────────────────┤
│  1.2 INVESTIGATE IMPLEMENTATION                                │
│     • Explore actual codebase structure                         │
│     • Compare: docs vs. code                                    │
├─────────────────────────────────────────────────────────────────┤
│  1.3 EVALUATE (Document Level)                                 │
│     • Classify each document: Tier 1, 2, or 3                  │
│     • EXCLUDE: system-architecture.md, data-flow.md            │
│     • Identify documents to move/archive                        │
├─────────────────────────────────────────────────────────────────┤
│  1.4 PRESENT PLAN (Document Level)                             │
│     • Note: Protected docs excluded (system-architecture,      │
│       data-flow)                                               │
│     • Show tier classification in clear format                  │
│     • Display: What moves where and why                        │
│     • ASK FOR CONFIRMATION                                      │
├─────────────────────────────────────────────────────────────────┤
│  1.5 EXECUTE (Upon Confirmation)                              │
│     • EXCLUDE: system-architecture.md, data-flow.md            │
│     • Move Tier 2 docs to history/documents/                    │
│     • Move Tier 3 docs to docs/guides/                          │
│     • Tier 1 docs stay in docs/application-design/              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    USER CONFIRMS PHASE 1
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: CONTENT LEVEL (Refinement)                           │
├─────────────────────────────────────────────────────────────────┤
│  2.1 EVALUATE (Content Level)                                  │
│     ONLY for docs/application-design/ (Tier 1):                │
│     • EXCLUDE: system-architecture.md, data-flow.md            │
│     • Identify sections to remove (detailed specs in code)      │
│     • Identify sections to condense                             │
│     • Identify sections to reorganize                           │
│     • Identify high-level content to keep                       │
├─────────────────────────────────────────────────────────────────┤
│  2.2 PRESENT PLAN (Content Level)                              │
│     • Note: Protected docs excluded (system-architecture,      │
│       data-flow)                                               │
│     • Show content refinements per document                     │
│     • Explain: What to remove/condense and why                 │
│     • ASK FOR CONFIRMATION                                      │
├─────────────────────────────────────────────────────────────────┤
│  2.3 EXECUTE (Upon Confirmation)                              │
│     • EXCLUDE: system-architecture.md, data-flow.md            │
│     • Refine content in docs/application-design/                │
│     • Archive outdated content                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Plan Presentation Format

### Phase 1 Plan (Document Level)

```markdown
# Document Reorganization Plan

## Summary
- Total documents reviewed: [N]
- Tier 1 (Keep in application-design): [N]
- Tier 2 (Archive): [N]
- Tier 3 (Move to guides): [N]

---

## Tier 1: Essential & Persistent
**Location:** `docs/application-design/` (no change)

| Document | Reason to Keep |
|----------|----------------|
| `architecture.md` | Core architecture decisions & rationale |
| `design-principles.md` | High-level design principles |
...

---

## Tier 2: Archive (Implementation Details)
**Location:** `history/documents/Archive-{timestamp}/`

| Document | Move To | Reason |
|----------|---------|--------|
| `api-specs.md` | `history/documents/Archive-.../` | Details now in code |
...

---

## Tier 3: Guides & References
**Location:** `docs/guides/`

| Document | Move To | Reason |
|----------|---------|--------|
| `setup-guide.md` | `docs/guides/setup.md` | How-to content |
...

---

**Do you confirm this reorganization plan?** (Yes/No/Modify)
```

### Phase 2 Plan (Content Level)

```markdown
# Content Refinement Plan

**Applies ONLY to:** `docs/application-design/` documents

**Protected Documents (Excluded from refinement):**
- `system-architecture.md` - Core architecture (DO NOT MODIFY)
- `data-flow.md` - Workflow design (DO NOT MODIFY)

---

## Refinement Summary

| Document | Sections to Remove | Sections to Condense | Sections to Keep |
|----------|-------------------|---------------------|------------------|
| `auth-design.md` | API endpoints, DB schema | Implementation details | Architecture decision, principles |
...

---

## Detailed Changes Per Document

### `docs/application-design/auth-design.md`
**Remove:**
- [x] API Endpoints section (in code)
- [x] Database Schema section (in code)

**Condense:**
- Implementation Details → Key Principles

**Keep:**
- Architecture Decision
- Security Considerations
- Design Rationale

---

**Do you confirm this content refinement plan?** (Yes/No/Modify)
```

---

## Key Principles

| Principle | Statement |
|-----------|-----------|
| **Single source of truth** | Code = detailed truth, Docs = architectural truth |
| **No duplication** | If code shows it clearly, docs don't repeat it |
| **Natural evolution** | Docs start detailed, become concise over time |
| **Clear purpose** | Docs explain WHY & WHAT, Code shows HOW |
| **Flexible timing** | Refine when invoked, not on rigid schedule |

---

## What Makes This Skill Different

| Aspect | Approach |
|--------|----------|
| **Trigger** | User invokes skill (no rigid events) |
| **Investigation** | Reads docs + explores codebase |
| **Decision** | Intelligent evaluation, not rule-based |
| **Scope** | Document tier + content refinement (Tier 1 only) |
| **Execution** | Two-phase: Present Plan → Confirm → Execute (each phase) |

---

## Notes

- This skill is **flexible and context-aware** - it evaluates the actual state of the project
- **Two-phase confirmation required**: Phase 1 (document moves) then Phase 2 (content refinement)
- Each phase presents a clear plan in structured format and waits for user confirmation
- Content-level refinement **ONLY applies to `docs/application-design/`** (Tier 1)
- **Protected documents (NEVER MODIFY in EITHER phase):**
  - `system-architecture.md` - Core system architecture
  - `data-flow.md` - Workflow design and state management
  - These are excluded from ALL operations: moving, archiving, refining
- Documents moved to Tier 2 (archive) or Tier 3 (guides) are moved **as-is**, not refined
- Keeps `docs/application-design/` focused on high-level design that doesn't become stale
