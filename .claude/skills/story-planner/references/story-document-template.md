# User Story Document Template

This template defines the structure for individual user story documents.

**Key Principles**:
- **Technical Specification Document** (docs/technical-specs/{bc}.md) = Defines **WHAT** (BC model + pseudo-code flows + API contracts + data model + implementation details)
- **User Story Document** = Defines **HOW** (BDD scenarios + task breakdown + execution plan + quality standards)
- **Developer Agent** = Writes source code and scripts (implementation details)

**Separation of Concerns**:
- **Pseudo-code** (in BC documents) = Internal algorithm logic (PHASE 1 → 2 → 3 format) - defines HOW system works internally
- **BDD scenarios** (in story documents) = Observable behavior (Given/When/Then format) - defines WHAT users experience

**Task Definition ≠ Prescriptive Implementation**:
- Task definitions describe **what needs to be done** (e.g., "Implement JWT authentication endpoint")
- Prescriptive implementation shows **exactly how to do it** (e.g., `jwt.sign(payload, secret)` - source code)
- User stories contain task definitions, not source code

---

## Output Structure (Flat with Phase Prefix)

```
development/
└── {wave-name}/
    ├── phase-01-story-01-{title}.md
    ├── phase-01-story-02-{title}.md
    ├── phase-02-story-01-{title}.md
    ├── development-conventions.md
    └── development-progress.md
```

---

## Naming Convention

**Format**: `phase-{NN}-story-{MM}-{kebab-case-story-title}.md`

- `phase-{NN}`: Phase number with two digits (01, 02, 03, ...)
- `story-{MM}`: Story number within phase with two digits (01, 02, 03, ...)
- `{kebab-case-story-title}`: Brief descriptive title in kebab-case

**Examples**:
- `phase-01-story-01-password-reset-request.md`
- `phase-01-story-02-password-reset-confirm.md`
- `phase-02-story-01-dataset-upload.md`

---

## User Story Document Template

```markdown
# User Story {phase}.{story}: {Story Title}

**Phase**: Phase {N}: {Phase Name}
**Priority**: Must Have / Should Have / Nice to Have
**Estimated Duration**: 1-2 weeks

---

## Bounded Context Reference

**BC**: {Bounded Context Name}
**BC Document**: `docs/technical-specs/{bc}.md`

**BC Purpose**: {Brief description of what this BC does}

---

## User Story

**As a** {user role}...
**I want** {specific feature/functionality}...
**So that** {I can achieve specific benefit/value}...

### Example

**As a** user who forgot their password...
**I want** to request a password reset link via email...
**So that** I can regain access to my account...

---

## Acceptance Criteria

This story is **complete** when ALL of the following are met:

- [ ] {Criterion 1: Specific, testable condition}
- [ ] {Criterion 2: Specific, testable condition}
- [ ] {Criterion 3: Specific, testable condition}
- [ ] {Criterion 4: All tests passing (unit, integration, E2E)}
- [ ] {Criterion 5: BDD scenarios mapped to tests}

### Definition of Done

- [ ] Code review approved
- [ ] All tests passing
- [ ] No known bugs
- [ ] No skipped tests (unless documented and justified)
- [ ] Acceptance criteria verified

---

## BDD Scenarios

> **BDD Format**: Given/When/Then scenarios specify concrete behavior examples. These scenarios serve as living documentation and map directly to automated tests.
>
> **Key**: BDD scenarios describe observable user behavior, not internal implementation details. Internal logic (pseudo-code) lives in the BC document.

This story implements behavior derived from the following domain flows in the BC document:

| Domain Flow | BC Section | Scenario Count |
|-------------|------------|----------------|
| {flow_name} | Section 3.{N} | {count} scenarios |

### BDD Scenarios for This Story

#### Scenario 1: {Success Case}

**Given** {precondition: the initial context/state}
**When** {action: the user or system action taken}
**Then** {expected outcome: the observable result}
**And** {additional outcome, if applicable}

**Example**:
```gherkin
Given a user with email "user@example.com" exists
When I request a password reset for "user@example.com"
Then a reset token should be created in the database
And an email should be sent with the reset link
And the response should return success message
```

#### Scenario 2: {Error Case}

**Given** {precondition: describe the state that triggers error}
**When** {action: what causes the error}
**Then** {expected error: error message or behavior}

**Example**:
```gherkin
Given no user with email "nonexistent@example.com" exists
When I request a password reset for "nonexistent@example.com"
Then the response should return success (to prevent email enumeration)
And no email should be sent
And no token should be created
```

#### Scenario 3: {Edge Case or Validation}

**Given** {precondition}
**When** {action}
**Then** {expected outcome}

---

## Tasks

> **TDD Philosophy**: Tests are written FIRST (Red phase), then implementation makes tests pass (Green phase), then code is improved while tests remain green (Refactor phase).
>
> **Task Organization**: Tasks are organized by execution flow - the natural order in which work is performed.

### 1. Testing (TDD - Write First)

> **Purpose**: Write tests BEFORE implementation (Red phase). These tests define what "done" looks like.

| Task | Status | Notes |
|------|--------|-------|
| Write unit tests for backend domain models | ⚪ Not Started | Test entities, value objects, business rules (see BC document domain model) |
| Write unit tests for backend services/use cases | ⚪ Not Started | Test business logic, error handling (see BC document domain flows) |
| Write unit tests for frontend components | ⚪ Not Started | Test business logic components, state management |
| Write integration tests for API endpoints | ⚪ Not Started | Happy path + error cases for each endpoint (see BC document API contracts) |
| Write E2E tests for critical user journeys | ⚪ Not Started | Core workflows spanning multiple pages/steps |

**Testing Status**: ⚪ Not Started

---

### 2. Backend Implementation

> **Purpose**: Implement backend functionality to pass tests (Green phase).

| Task | Status | Notes |
|------|--------|-------|
| Create database schema and migrations | ⚪ Not Started | See BC document data model section |
| Implement domain models and entities | ⚪ Not Started | Aggregates, entities, value objects (see BC document) |
| Implement repository layer | ⚪ Not Started | Repository interfaces and implementations (see BC document) |
| Implement API endpoints | ⚪ Not Started | See BC document API contracts section |
| Implement business logic services | ⚪ Not Started | Domain services, use cases (see BC document domain flows) |
| Add error handling and validation | ⚪ Not Started | Per BC document security requirements |

**Backend Status**: ⚪ Not Started

---

### 3. Frontend Implementation

> **Purpose**: Implement frontend functionality to pass tests (Green phase).

| Task | Status | Notes |
|------|--------|-------|
| Create/update state management | ⚪ Not Started | Zustand stores, React Query hooks |
| Build UI components | ⚪ Not Started | Per UI references (see below) |
| Create pages/routes | ⚪ Not Started | Route setup, navigation |
| Integrate with backend API | ⚪ Not Started | API calls, error handling, loading states (see BC document API contracts) |
| Add form validation | ⚪ Not Started | Client-side validation per BC document |

**Frontend Status**: ⚪ Not Started

---

### 4. Testing (Make Tests Pass)

> **Purpose**: Implement until ALL tests pass (Green phase completion).

| Task | Status | Notes |
|------|--------|-------|
| Fix failing unit tests (backend) | ⚪ Not Started | Implement until backend unit tests pass |
| Fix failing unit tests (frontend) | ⚪ Not Started | Implement until frontend unit tests pass |
| Fix failing integration tests | ⚪ Not Started | Implement until API integration tests pass |
| Fix failing E2E tests | ⚪ Not Started | Implement until E2E tests pass |
| Ensure all tests passing (no skips) | ⚪ Not Started | Verify 100% test pass rate |

**Testing Status**: ⚪ Not Started

---

### 5. Refactor (Optional)

> **Purpose**: Improve code while tests remain green (Refactor phase).

| Task | Status | Notes |
|------|--------|-------|
| Refactor for code quality | ⚪ Not Started | Extract duplicated code, improve naming |
| Refactor for performance | ⚪ Not Started | Optimize queries, reduce re-renders |
| Refactor for maintainability | ⚪ Not Started | Improve code organization |

**Refactor Status**: ⚪ Not Started

---

## Technical Reference

> **Development agents**: See technical specification document for detailed BC model, pseudo-code flows, API contracts, data model, and security requirements.

**Technical Specification Document**: `docs/technical-specs/{bc}.md`

**Relevant Sections**:
- Section 2: Domain Model (aggregates, entities)
- Section 3.{N}: Domain flows for this story (pseudo-code)
- Section 4.{N}: API contracts for this story
- Section 5: Data model (tables, relationships)
- Section 7: Security requirements
- Section 10: BC relationships

---

## Dependencies

### Depends On (Internal)

- {story: phase-X-story-Y} - {dependency description}
- {BC: upstream-bc-name} - {if this story depends on another BC}

### Enables (Internal)

- {story: phase-X-story-Y} - {what this story enables}
- {BC: downstream-bc-name} - {if this story enables work in another BC}

### External Dependencies

- {External system/service} - {dependency description}

---

## UI References

| UI File | Purpose |
|---------|---------|
| `docs/ui-pages/{file-name}.html` | {description of UI pattern} |

---

## Design References

| Design Document | Relevant Sections |
|-----------------|-------------------|
| `docs/application-design/{document}.md` | {relevant details} |

---

## Story Status

**Overall Status**: ⚪ Not Started

### Status Meanings

| Status | Symbol | When to Use |
|--------|--------|-------------|
| Not Started | ⚪ | Initial state |
| In Progress | 🔄 | Currently being worked on |
| Partial | ⚠️ | Work done but loose ends remain |
| Complete | ✅ | Fully complete with ALL tests passing |
| Blocked | 🚫 | Cannot proceed due to blocker |

### Notes

{Progress notes, blockers, decisions}
```

---

## Task Breakdown Guidelines

### Task Definition vs Prescriptive Implementation

| Aspect | Task Definition (✅ Include) | Prescriptive Implementation (❌ Don't Include) |
|--------|---------------------------|---------------------------------------------|
| **Backend** | "Implement JWT authentication endpoint" | `jwt.sign(payload, secret)` (source code) |
| **Database** | "Create users table with email, password_hash columns" | `CREATE TABLE users (...)` (SQL script) |
| **Frontend** | "Build login form component with email/password fields" | `<input type="email" />` (JSX code) |
| **Testing** | "Write unit tests for password hashing" | `def test_hash_password(): ...` (test code) |

**Rule**: User story documents describe **what tasks** need doing. Developer agents write **the actual code**.

---

## TDD Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ TDD CYCLE (Per Task or Per Story)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. RED    → Write failing test                            │
│  2. GREEN  → Write minimal code to pass test               │
│  3. REFACTOR→ Improve code while tests remain green        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**How it maps to task sections**:

| Task Section | TDD Phase | Purpose |
|--------------|-----------|---------|
| 1. Testing (Write First) | RED | Write failing tests |
| 2. Backend Implementation | GREEN | Make backend tests pass |
| 3. Frontend Implementation | GREEN | Make frontend tests pass |
| 4. Testing (Make Tests Pass) | GREEN | Ensure ALL tests pass |
| 5. Refactor | REFACTOR | Improve code while tests stay green |

---

## Alternative Task Flows

The task breakdown above follows the **Test-First Layered** flow:

```
Tests → Backend → Frontend → Fix Tests → Refactor
```

**Alternative flows** (choose based on team needs):

| Flow | Order | Best For |
|------|-------|----------|
| **API-First Parallel** | API Contract → Backend + Frontend (parallel) → Tests | Teams working simultaneously |
| **Backend-First** | Backend → Frontend → Tests | When frontend depends heavily on backend |

**Note**: Regardless of flow, always follow TDD within each layer (write test before implementation).

---

## Example: Password Reset Request Story

```markdown
# User Story 1.1: Password Reset Request

**Phase**: Phase 1: Password Reset
**Priority**: Must Have
**Estimated Duration**: 1-2 weeks

---

## Bounded Context Reference

**BC**: Authentication
**Technical Specification Document**: `docs/technical-specs/authentication.md`

**BC Purpose**: User identity, authentication, and authorization

---

## User Story

**As a** user who forgot their password...
**I want** to request a password reset link via email...
**So that** I can regain access to my account...

---

## Acceptance Criteria

- [ ] User can submit email address via form
- [ ] System validates email format
- [ ] System sends email with reset link if email exists
- [ ] System returns success message even if email doesn't exist (security)
- [ ] Reset link expires after 1 hour
- [ ] Reset link can only be used once
- [ ] All tests passing (unit, integration, E2E)

---

## BDD Scenarios

This story implements behavior derived from the following domain flows:

| Domain Flow | BC Section | Scenario Count |
|-------------|------------|----------------|
| password_reset_request | Section 3.1 | 3 scenarios |

### BDD Scenarios for This Story

#### Scenario: Valid email receives reset link
**Given** a user with email "user@example.com" exists
**When** I request a password reset for "user@example.com"
**Then** a reset token should be created in the database
**And** an email should be sent with the reset link
**And** the response should return success message

#### Scenario: Invalid email format returns error
**Given** - (no precondition)
**When** I request a password reset with "invalid-email"
**Then** the response should return 400 error
**And** the error message should indicate invalid format

#### Scenario: Non-existent email returns success (security)
**Given** no user with email "nonexistent@example.com" exists
**When** I request a password reset for "nonexistent@example.com"
**Then** the response should return success (to prevent email enumeration)
**And** no email should be sent
**And** no token should be created

---

## Tasks

### 1. Testing (TDD - Write First)

| Task | Status | Notes |
|------|--------|-------|
| Write unit tests for PasswordResetToken entity | ⚪ Not Started | Test token generation, validation, expiry |
| Write unit tests for PasswordResetRequest use case | ⚪ Not Started | Test request flow, email enumeration prevention |
| Write unit tests for request form component | ⚪ Not Started | Test email validation, form submission |
| Write integration tests for POST /api/auth/password-reset/request | ⚪ Not Started | Happy path + error cases |
| Write E2E test for password reset request flow | ⚪ Not Started | Navigate to page, submit email, verify success |

**Testing Status**: ⚪ Not Started

---

### 2. Backend Implementation

| Task | Status | Notes |
|------|--------|-------|
| Create password_resets table migration | ⚪ Not Started | See BC document Section 5 (data model) |
| Implement PasswordResetToken entity | ⚪ Not Started | With token_hash, expires_at, used fields |
| Implement PasswordResetRepository | ⚪ Not Started | CRUD operations for password resets |
| Implement POST /api/auth/password-reset/request endpoint | ⚪ Not Started | See BC document Section 4.1 (API contract) |
| Implement PasswordResetRequest use case | ⚪ Not Started | See BC document Section 3.1 (domain flow) |
| Implement email service integration | ⚪ Not Started | SendGrid/SES or ConsoleEmailService for dev |

**Backend Status**: ⚪ Not Started

---

### 3. Frontend Implementation

| Task | Status | Notes |
|------|--------|-------|
| Create password reset request page route | ⚪ Not Started | /password-reset/request |
| Build request form component | ⚪ Not Started | Email input field, submit button |
| Add form validation (email format) | ⚪ Not Started | Client-side validation |
| Integrate with POST /api/auth/password-reset/request | ⚪ Not Started | API call, error handling, success message |
| Add navigation to login page after success | ⚪ Not Started | Redirect flow |

**Frontend Status**: ⚪ Not Started

---

### 4. Testing (Make Tests Pass)

| Task | Status | Notes |
|------|--------|-------|
| Fix failing unit tests (backend) | ⚪ Not Started | Implement until backend unit tests pass |
| Fix failing unit tests (frontend) | ⚪ Not Started | Implement until frontend unit tests pass |
| Fix failing integration tests | ⚪ Not Started | Implement until API tests pass |
| Fix failing E2E tests | ⚪ Not Started | Implement until E2E tests pass |

**Testing Status**: ⚪ Not Started

---

### 5. Refactor

| Task | Status | Notes |
|------|--------|-------|
| Refactor code quality | ⚪ Not Started | After all tests passing |

**Refactor Status**: ⚪ Not Started

---

## Technical Reference

**Technical Specification Document**: `docs/technical-specs/authentication.md`

**Relevant Sections**:
- Section 2: Domain Model (User aggregate, PasswordResetToken entity)
- Section 3.1: password_reset_request flow (pseudo-code)
- Section 4.1: POST /api/auth/password-reset/request endpoint
- Section 5: Data Model (password_resets table)
- Section 7: Security (email enumeration prevention)
- Section 9: Security requirements (email enumeration prevention)

---

## Dependencies

### Depends On (Internal)

- User registration must be complete (users table exists)

### Enables (Internal)

- phase-01-story-02: Password Reset Confirmation

### External Dependencies

- Email Service (SendGrid/SES or console for development)

---

## UI References

| UI File | Purpose |
|---------|---------|
| `docs/ui-pages/login-page.html` | Reference for form styling patterns |
| `docs/ui-pages/password-reset-request.html` | Request form UI |

---

## Design References

| Design Document | Relevant Sections |
|-----------------|-------------------|
| `docs/application-design/rbac-authentication.md` | Password reset flow |

---

## Story Status

**Overall Status**: ⚪ Not Started

### Notes

- Email service defaults to ConsoleEmailService for development
- Token generation: 32 bytes, URL-safe base64
- Expiry: 1 hour from creation
```
