---
name: task-planning
description: "Generate organized task lists from documentation using intelligent assessment. Discovers all docs, evaluates project nature and scope, and creates task planning documents. Organization (flat/phase/module) is chosen based on project characteristics, not rigid scoring. Output goes to tasks/task-planning/. Use when: starting a development wave; planning implementation; decomposing requirements into actionable tasks."
---

# Task Planning

Generate organized task planning documents from project documentation.

## Overview

1. **Discover Documents** - Read ALL markdown files from `docs/` directory
2. **Intelligently Assess** - AI evaluates project nature, scope, and structure
3. **Choose Organization** - Select the most appropriate structure (flat, phase-based, or module-based)
4. **Generate Tasks** - Create tasks using TaskCreate tool
5. **Save Output** - Write to `tasks/task-planning/{descriptive-name}.md`

## Architecture

```mermaid
flowchart LR
    Start([Start]) --> Discover[Discover ALL docs/<br/>Glob *.md]
    Discover --> Read[Read documents]
    Read --> Assess[AI assesses project<br/>nature & scope]
    Assess --> Decide{Choose<br/>organization}

    Decide -->|Simple<br/>linear work| Flat[FLAT_LIST]
    Decide -->|Sequential<br/>phases clear| Phase[IMPLEMENTATION_PHASE]
    Decide -->|Distinct<br/>modules| Module[FEATURE_MODULE]

    Flat --> Generate[Generate tasks<br/>TaskCreate]
    Phase --> Generate
    Module --> Generate

    Generate --> Save[Save to<br/>tasks/task-planning/]
    Save --> End([End])

    style Decide fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style Flat fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    style Phase fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style Module fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
```

## When to Use

Call this skill when:
- Starting a new development wave or project
- Planning implementation for a feature or module
- Decomposing requirements into actionable tasks
- Creating structured task lists from documentation
- You need TaskCreate-formatted tasks organized logically

## Input

- **Requirements** - Project description or user request
- **Source** - ALL `.md` files in `docs/` (discovered dynamically via Glob)
- **Output** - `tasks/task-planning/{descriptive-name}.md`

## Workflow

### Phase 1: Document Discovery & Intelligent Assessment

```bash
# Discover ALL source materials
files = Glob("**/*.md", path="docs/")

# Read ALL documents and understand:
# - Project scope and goals
# - Features and requirements
# - Architecture and components
# - Integration points
# - Technical stack
```

**Intelligent Assessment:**

The AI should evaluate the project holistically and choose the most appropriate organization based on:

| Question | Considerations |
|----------|----------------|
| **What is the project's nature?** | New application vs. feature addition vs. refactor |
| **Are there distinct functional areas?** | Auth, data processing, UI, reporting, etc. |
| **Do components work independently?** | Can teams work in parallel? |
| **Is there a clear sequence of phases?** | Setup → Build → Test → Deploy |
| **How many distinct components?** | Few vs. many |

**No rigid scoring** - use intelligent judgment based on the actual project context.

### Phase 2: Organization Decision

Choose the organization that best fits the project:

| Organization | Best For | Characteristics |
|--------------|----------|----------------|
| **FLAT_LIST** | Simple additions, single features | Linear work, clear dependencies, small scope |
| **IMPLEMENTATION_PHASE** | Phased projects, workflows | Clear temporal sequence (e.g., Phase 1 → Phase 2 → Phase 3) |
| **FEATURE_MODULE** | Complex applications, multi-component | Distinct functional areas that can be developed in parallel |

### Phase 3: Task Generation

```python
# Create each task with TaskCreate
TaskCreate(
    subject="Implement user authentication",
    description="Build login form with email/password validation. Integrate with existing auth service.",
    activeForm="Implementing user authentication"
)
```

**Determine descriptive name** from user request (clear, descriptive, kebab-case):
- "Add CSV file import" → `csv-import-feature`
- "Build user authentication" → `user-authentication-system`
- "Fix memory leak in PSPP" → `pspp-memory-leak-fix`

## Output Format

Save to `tasks/task-planning/{descriptive-name}.md`:

```markdown
# Task List: {Project Name}

**Organization**: FLAT_LIST | IMPLEMENTATION_PHASE | FEATURE_MODULE
**Total Tasks**: {Count}

## Source Documents
{List of all docs/ files read}

## Project Context
{Brief summary of what the project does and why this organization was chosen}

## Task Breakdown
{Organized tasks}

## Task Summary by Module/Phase
{Summary table}
```

**TaskCreate Parameters:**
| Parameter | Format | Example |
|-----------|--------|---------|
| subject | Imperative verb phrase | "Create login form" |
| description | Detailed explanation | "Build form with..." |
| activeForm | Present continuous | "Creating login form" |

## Output Examples

### Example 1: FLAT_LIST

**Use when**: Adding a single feature, simple refactoring, or small focused changes

```markdown
# Task List: DataChat CSV Import Feature

**Organization**: FLAT_LIST
**Total Tasks**: 5

## Source Documents
- docs/features-and-usage.md
- docs/system-architecture.md
- docs/data-flow.md
- docs/business-rules.md

## Project Context
Adding CSV file import capability to existing SPSS (.sav) file support. This is a focused feature addition that extends the existing parser and requires updates to validation, testing, and documentation.

## Task Breakdown

### Task 1: Extend input parser for CSV format
- **Description**: Modify parser to detect and handle CSV files alongside SPSS .sav files.
- **Active Form**: Extending input parser for CSV format

### Task 2: Add CSV metadata extraction
- **Description**: Infer variable names and types from CSV headers with sensible defaults.
- **Active Form**: Adding CSV metadata extraction

### Task 3: Update workflow validation for CSV
- **Description**: Handle CSV edge cases (missing values, encoding issues) with error messages.
- **Active Form**: Updating workflow validation for CSV

### Task 4: Test CSV import with sample files
- **Description**: Create test CSV files and verify full workflow produces expected outputs.
- **Active Form**: Testing CSV import with sample files

### Task 5: Update documentation for CSV support
- **Description**: Document CSV format in features-and-usage.md with examples.
- **Active Form**: Updating documentation for CSV support
```

### Example 2: IMPLEMENTATION_PHASE

**Use when**: Clear sequential workflow, multi-stage deployment, or projects with distinct temporal phases

```markdown
# Task List: Database Migration

**Organization**: IMPLEMENTATION_PHASE
**Total Tasks**: 6

## Source Documents
- docs/system-architecture.md
- docs/data-schema.md
- docs/deployment.md

## Project Context
Database schema migration requiring careful sequencing: analysis → design → implementation → testing → deployment. Each phase must complete before the next can begin.

## Task Breakdown

### Phase 1: Preparation

### Task 1.1: Analyze current database schema
- **Description**: Document tables, relationships, data volumes, and migration risks.
- **Active Form**: Analyzing current database schema

### Task 1.2: Design new schema
- **Description**: Create optimized schema with migration mapping.
- **Active Form**: Designing new schema

### Phase 2: Implementation

### Task 2.1: Create migration scripts
- **Description**: Write SQL scripts with rollback procedures.
- **Active Form**: Creating migration scripts

### Task 2.2: Update application code
- **Description**: Modify ORM models and queries for new schema.
- **Active Form**: Updating application code

### Phase 3: Testing & Deployment

### Task 3.1: Run migration tests
- **Description**: Test in staging environment and validate data.
- **Active Form**: Running migration tests

### Task 3.2: Execute production migration
- **Description**: Plan and execute migration with downtime window.
- **Active Form**: Executing production migration
```

---

### Example 3: FEATURE_MODULE

**Use when**: Complex applications with distinct functional areas that can be developed independently

```markdown
# Task List: E-Commerce Platform

**Organization**: FEATURE_MODULE
**Total Tasks**: 8

## Source Documents
- docs/features-and-usage.md
- docs/system-architecture.md
- docs/data-schema.md
- docs/api-specification.md

## Project Context
Full e-commerce platform with distinct functional modules (authentication, catalog, cart, orders) that can be developed independently by different teams or in parallel streams.

## Task Breakdown

### Authentication Module

### Task A-1: Implement user registration
- **Description**: Build registration form with email validation.
- **Active Form**: Implementing user registration

### Task A-2: Build login system
- **Description**: Create login form with JWT tokens and session management.
- **Active Form**: Building login system

### Product Catalog Module

### Task B-1: Design product data model
- **Description**: Define schema with variants, categories, and inventory.
- **Active Form**: Designing product data model

### Task B-2: Implement product search
- **Description**: Build search with filters and sorting.
- **Active Form**: Implementing product search

### Shopping Cart Module

### Task C-1: Create cart data structure
- **Description**: Implement session-based cart with persistence.
- **Active Form**: Creating cart data structure

### Task C-2: Build checkout flow
- **Description**: Design checkout with payment integration.
- **Active Form**: Building checkout flow

### Order Management Module

### Task D-1: Implement order processing
- **Description**: Handle order creation and status updates.
- **Active Form**: Implementing order processing

### Task D-2: Build order history
- **Description**: Display past orders with filters.
- **Active Form**: Building order history

## Task Summary by Module

| Module | Tasks | Focus Area |
|--------|-------|------------|
| **Authentication** | 2 | User identity and access |
| **Product Catalog** | 2 | Product data and search |
| **Shopping Cart** | 2 | Cart management and checkout |
| **Order Management** | 2 | Order processing and history |
```

## Best Practices

1. **Intelligent assessment** - Don't use rigid scoring. Evaluate the project holistically and choose the organization that best fits.
2. **Keep tasks atomic** - Each task should be independently completable
3. **Limit category size** - 3-8 tasks per category
4. **Clear descriptions** - Define what "done" means
5. **Logical ordering** - Respect dependencies
6. **Be flexible** - The chosen organization should help clarity, not constrain development

## Related Skills

- **task-implementation**: Executes tasks with audit iteration
- **task-document-writer**: Generates task documents for delegation to the monitoring system

---

*End of SKILL.md*
