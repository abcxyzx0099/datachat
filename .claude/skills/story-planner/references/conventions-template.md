# Conventions Document Template

This template defines the structure for development conventions document.

## Usage

When creating `development-conventions.md` for a wave (development initiative):

1. **Replace placeholders** ({Wave Name}, {Date}, etc.)
2. **Keep it lean** - focus on SHARED conventions only
3. **Phase-specific details** go in phase documents, not here
4. **Reference existing docs** - link to `docs/application-design/*.md`
5. **Target length**: ~150-200 lines maximum

---

## Conventions Document Structure

```markdown
# {Wave Name} - Development Conventions

**Purpose**: Shared conventions for all phases
**Created**: {Date}
**Status**: Active

---

## Part 1: Shared Principles

### Self-Contained Principle
Each phase document must be **self-contained and standalone**. When implementing a phase, the agent only needs:
1. The phase document
2. This conventions document

### DDD (Domain-Driven Design) Principles

| Principle | Description |
|-----------|-------------|
| **Domain is core** | Business logic lives in the Domain layer (no external dependencies) |
| **Layers have boundaries** | API → Application → Domain (单向依赖) |
| **Infrastructure implements Domain** | Infrastructure depends on Domain interfaces, never the reverse |
| **Entities > Data** | Focus on domain behavior, not just database tables |

### Import Dependency Rules

```
API → Application → Domain
Infrastructure → Domain (interfaces only)

NEVER: Domain importing from Application/Infrastructure
NEVER: API importing Infrastructure directly (use DI)
```

### Code Quality Principles

| Principle | Description |
|-----------|-------------|
| **YAGNI** | You Aren't Gonna Need It - don't build for hypothetical future requirements |
| **DRY** | Don't Repeat Yourself - extract common patterns, but avoid premature abstraction |
| **Single Responsibility** | Each function/class does one thing well |
| **Fail Fast** | Validate inputs early, raise clear errors |

### Testing Principles

| Principle | Description |
|-----------|-------------|
| **Test behavior, not implementation** | Focus on what the code does, not how |
| **Arrange-Act-Assert** | Structure tests clearly: setup, execute, verify |
| **One assertion per test** | Keep tests focused and readable |
| **Use descriptive names** | `test_add_dataset_when_limit_exceeded_raises_error` |

### BDD (Behavior-Driven Development) Specification

**BDD complements TDD** by providing concrete behavior examples in Gherkin format (Given/When/Then).

| Aspect | Description |
|--------|-------------|
| **Purpose** | Bridge business requirements and technical implementation |
| **Format** | Given (precondition) → When (action) → Then (outcome) |
| **Audience** | Readable by developers, PMs, designers, stakeholders |
| **Tools** | pytest-bdd (Python), behave (Python), Cucumber (JS), Playwright (E2E) |
| **Location** | BDD scenarios live in each story document |

**BDD Workflow:**
1. **Write BDD scenarios** during planning (in story document)
2. **Map scenarios to tests** (acceptance/integration tests)
3. **Implement features** to pass scenario tests (TDD cycle)

**Example BDD Scenario:**
```gherkin
Given a user with email "user@example.com" exists
When the user logs in with correct password
Then the user should receive a valid JWT token
And the token should expire after 24 hours
```

**BDD + TDD Integration:**
- **BDD scenarios** = Acceptance criteria in executable format
- **Unit tests** (TDD) = Test individual components
- **Integration tests** = Verify BDD scenarios end-to-end

### TDD (Test-Driven Development) Specification

**Follow the Red-Green-Refactor cycle for all new code:**

| Phase | Action | Command |
|-------|--------|---------|
| **Red** | Write failing test for desired behavior | Write test first, run to confirm it fails |
| **Green** | Write minimal code to pass the test | Implement just enough to make test pass |
| **Refactor** | Improve code while tests remain green | Clean up, optimize, extract abstractions |

**TDD Workflow by Task:**
1. **Unit Tests** - Write BEFORE domain/application code
2. **Implementation** - Write to pass the unit tests
3. **Integration Tests** - Write AFTER unit tests pass
4. **E2E Tests** - Write AFTER integration tests pass

**When tests are already written** (brownfield): Run tests first to verify current state, then implement/fix.

** NEVER mark a task complete if tests are failing or missing.**

---

## Part 2: Quick Reference Links

### Design Documents
| Document | Path |
|----------|------|
| System Architecture | `docs/application-design/system-architecture.md` |
| DDD Architecture | `docs/application-design/ddd-system-architecture.md` |
| Database Schema | `docs/application-design/database-schema.md` |
| API Contract | `docs/application-design/api-contract.md` |
| Project Structure | `docs/application-design/project-structure.md` |
| Coding Conventions | `docs/application-design/coding-conventions.md` |
| Testing Strategy | `docs/application-design/testing-strategy.md` |

### R Package References (SPSS Analysis)
| Package | HTML Reference | Key Functions |
|---------|----------------|---------------|
| **expss** | `reference/r-packages-manual/html-version/expss.html` | `fre()`, `cross_cases()`, `cross_cpct()` |
| **haven** | `reference/r-packages-manual/html-version/haven.html` | `read_sav()`, SPSS file I/O |
| **labelled** | `reference/r-packages-manual/html-version/labelled.html` | Variable labels, value labels |
| **sjlabelled** | `reference/r-packages-manual/html-version/sjlabelled.html` | Label utilities |
| **survey** | `reference/r-packages-manual/html-version/survey.html` | Weighted statistics |

### Claude Agent SDK References
| Document | Path |
|----------|------|
| Python SDK | `reference/claude-agent-sdk-manual/python-sdk.md` |
| Usage Patterns | `reference/knowledge/claude-agent-sdk-usage-patterns.md` |

### External Resources
- **expss**: https://gdemin.github.io/expss/
- **FastAPI**: https://fastapi.tiangolo.com/
- **TanStack Start**: https://tanstack.com/start/latest

---

## Part 3: Technology Stack

**EXTRACTED FROM**: `{System Architecture Document Path}`

**NOTE**: Extract the following from the wave's architecture/stack documentation. Do NOT use placeholder values - each category must be populated with actual technologies from the source documents.

- **Backend**: {API framework, ORM, database, version notes}
- **Frontend**: {Framework, UI libraries, state management, styling}
- **Build/Package Tools**: {Language-specific package managers, build tools}
- **Code Quality Tools**: {Formatters, linters - by language}
- **Testing**: {Backend, frontend, and E2E testing frameworks}
- **Infrastructure**: {Containerization, reverse proxy, deployment tools}
- **Wave-Specific Libraries**: {Major libraries unique to this wave}

---

## Part 4: Coding Conventions (Summary)

### Python (Backend / dflib)
- Formatter: **Black**
- Linter: **Ruff**
- Classes: `PascalCase` | Functions: `snake_case` | Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore` | Exceptions: `PascalCaseError`

### TypeScript (Frontend)
- Formatter: **Prettier**
- Linter: **ESLint**
- Components: `PascalCase` | Functions: `camelCase` | Constants: `UPPER_SNAKE_CASE`

### DDD Naming
| Type | Convention | Example |
|------|------------|---------|
| Aggregate Root | Domain noun | `Project`, `Indicator` |
| Value Object | Domain noun | `ProjectCode`, `TransformationRules` |
| Repository | `<Entity>Repository` | `ProjectRepository` |
| Domain Service | `<Verb><Noun>Service` | `IndicatorGenerationService` |
| Application Service | `<Verb><Entity>Service` | `CreateProjectService` |

---

## Part 5: Development Environment

### Starting Servers
```bash
# Full application (frontend + backend)
./web/start.sh

# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# Health: http://localhost:8000/health
```

### After Modifying dflib
```bash
# Reinstall in editable mode
pip install -e ./dflib
```

### Environment Files
| Service | File |
|---------|------|
| Backend | `web/backend/.env` |
| Frontend | `web/frontend/.env` |

---

## Part 6: Important Notes

### Git Branch Rule
- **Default branch**: `main`
- **Never switch** without explicit user request

### Where to Find Details
| Need | Document |
|------|----------|
| Implementation tasks | Phase document (phase-*.md) |
| Detailed code patterns | `docs/application-design/coding-conventions.md` |
| API endpoints | `docs/application-design/api-contract.md` |
| Database tables | `docs/application-design/database-schema.md` |

### SPSS Analysis Pipeline
```
Load SPSS → Extract Metadata → Generate Indicators → Execute Analysis → Format Results
```
Analysis flows through: **Domain** (entities) → **Infrastructure** (R execution) → **Application** (orchestration)

---

## Part 7: Quick Reference - Wave Structure

### Backend (DDD Layers)
```
web/backend/app/
├── api/              # API endpoints (thin controllers)
├── application/      # Use cases, orchestration
├── domain/           # Business logic (no dependencies)
└── infrastructure/   # Database, external APIs
```

### Frontend
```
web/frontend/src/
├── routes/           # File-based routing
├── components/       # React components
├── hooks/            # Custom hooks
├── stores/           # State management
└── lib/              # API client, utilities
```

### Test Locations
```
tests/
├── unit/             # Domain, application tests
├── integration/      # API, database tests
└── e2e/              # Full user journey tests
```

### dflib (Shared Kernel)
```
dflib/
├── dflib/io/         # SPSS file I/O
├── dflib/computation/  # Analysis engines
├── dflib/presentation/ # Charts, formatters
└── dflib/core/       # Types, metadata
```

**Detailed structure**: See `docs/application-design/project-structure.md`

---

**Summary**: Phase documents contain implementation-specific details. This document contains shared principles and conventions only.
```
