# How to Develop with the Agent Team

Practical guide for using the DataChat Agent Team in daily development.

---

## Quick Start: The Development Workflow

When you want to build a feature, follow this sequence:

```
1. You (Team Lead) - Define the task
2. /analyst-agent   - Research and analyze (if needed)
3. /pm-agent       - Create requirements
4. /architect-agent - Design the solution
5. /dev-agent      - Implement the code
6. /qa-agent       - Validate quality
7. You (Team Lead) - Review and approve
```

**Note**: Step 2 (Analyst) is optional - use when you need investigation, research, or audit before proceeding.

---

## Complete Example: Building a New Feature

### Scenario: Add "Export to CSV" Feature

#### Step 1: You (Team Lead) - Define the Task

Tell the agents what you want:

```
I need to add a feature that lets users export their analysis results to CSV format.
The export should include all variables and their statistics.
```

#### Step 2: PM Agent - Create Requirements

```bash
/pm-agent
```

Then tell the PM:
```
Create a PRD for "export analysis results to CSV" feature.
The user should be able to download their analysis as a CSV file.
```

**PM Agent creates**: `docs/agent-team/planning/prds/prd-csv-export-YYYYMMDD.md`

#### Step 3: Architect Agent - Design the Solution

```bash
/architect-agent
```

Then tell the Architect:
```
Design the architecture for CSV export feature.
Consider: Where to add the endpoint, how to format the CSV, performance with large files.
```

**Architect Agent creates**: `docs/agent-team/solutioning/architecture/arch-csv-export-YYYYMMDD.md`

#### Step 4: QA Agent - Define Test Strategy

```bash
/qa-agent
```

Then tell QA:
```
Create a test strategy for the CSV export feature.
We need to test: various file sizes, special characters, missing values.
```

**QA Agent creates**: `docs/agent-team/solutioning/test-strategies/test-strategy-csv-export-YYYYMMDD.md`

#### Step 5: DEV Agent - Implement

```bash
/dev-agent
```

Then tell DEV:
```
Implement the CSV export feature following the architecture document.
Add unit tests and integration tests.
```

**DEV Agent creates**:
- Implementation code
- Tests in `tests/`
- Summary in `docs/agent-team/implementation/summaries/`

#### Step 6: QA Agent - Validate

```bash
/qa-agent
```

Then tell QA:
```
Run the tests for CSV export and validate quality.
```

**QA Agent creates**: `docs/agent-team/implementation/test-reports/test-report-csv-export-YYYYMMDD.md`

#### Step 7: You (Team Lead) - Review

Review all outputs, test the feature manually if needed, and approve.

---

## Cheat Sheet: Agent Commands

### Analyst Agent Commands

| Command | Use When |
|---------|----------|
| `RESEARCH` or `research` | Conduct research or investigation |
| `AUDIT` or `audit` | Audit code against standards/best practices |
| `BRIEF` or `product-brief` | Create product brief for new project |
| `DOCUMENT` or `document-project` | Document existing implementation |
| `BRAINSTORM` | Brainstorm ideas or solutions |

### PM Agent Commands

| Command | Use When |
|---------|----------|
| `PRD` or `prd` | Create Product Requirements Document |
| `STORY` or `user-story` | Break down into user stories |
| `REQUIREMENTS` | Analyze requirements |
| `SCOPE` | Define in/out of scope |

### Architect Agent Commands

| Command | Use When |
|---------|----------|
| `ARCH` or `architecture` | Create architecture document |
| `ADR` or `decision` | Create Architecture Decision Record |
| `API` or `api-design` | Design API contracts |
| `READY` or `implementation-readiness` | Check if ready to build |

### DEV Agent Commands

| Command | Use When |
|---------|----------|
| `DEV` or `implement` | Implement a feature |
| `REVIEW` or `code-review` | Review code |
| `FIX` or `fix-bug` | Fix a bug |
| `TEST` or `add-tests` | Add tests |
| `REFACTOR` | Refactor code |

### QA Agent Commands

| Command | Use When |
|---------|----------|
| `STRATEGY` or `test-strategy` | Create test plan |
| `RUN` or `run-tests` | Execute tests |
| `REPORT` or `test-report` | Generate test report |
| `BUG` or `report-bug` | Report a bug |
| `COVERAGE` or `test-coverage` | Analyze test coverage |

---

## Common Development Scenarios

### Scenario 1: New Feature (With Analysis)

```
You → "Add X feature"
/analyst-agent → Research similar features, best practices
/pm-agent → Create PRD
/architect-agent → Design architecture
/dev-agent → Implement
/qa-agent → Test
```

### Scenario 2: Technical Audit

```
You → "Check if our code follows best practices"
/analyst-agent → Audit implementation against standards
/architect-agent → Review audit findings, design improvements
/dev-agent → Implement improvements
/qa-agent → Validate
```

### Scenario 3: Quick Feature (No Analysis)

```
You → "Add X feature"
/pm-agent → Create PRD
/architect-agent → Design architecture
/dev-agent → Implement
/qa-agent → Test
```

### Scenario 4: Bug Fix

```
You → "Bug: X is broken"
/qa-agent → Report bug with details
/dev-agent → Fix the bug
/qa-agent → Verify fix
```

### Scenario 5: Code Review

```
You → "Review my changes"
/dev-agent → Conduct code review
You → Apply feedback
```

### Scenario 6: Architecture Decision

```
You → "Should we use X or Y?"
/analyst-agent → Research both options
/architect-agent → Create ADR
You → Make decision
```

### Scenario 2: Bug Fix

```
You → "Bug: X is broken"
/qa-agent → Report bug with details
/dev-agent → Fix the bug
/qa-agent → Verify fix
```

### Scenario 3: Code Review

```
You → "Review my changes"
/dev-agent → Conduct code review
You → Apply feedback
```

### Scenario 4: Architecture Decision

```
You → "Should we use X or Y?"
/architect-agent → Create ADR
You → Make decision
```

---

## Tips for Effective Agent Team Use

1. **Be Specific**: Give clear, detailed requests to each agent
2. **Follow the Phases**: Don't skip from idea directly to code
3. **Review Outputs**: Check what each agent produces before moving on
4. **Iterate**: If an agent's output isn't right, ask for revisions
5. **Use the Documentation**: All outputs go to `docs/agent-team/` for reference

---

## File Locations

| Agent Output | Location |
|--------------|----------|
| Research Reports | `docs/agent-team/research/briefs/` |
| Technical Audits | `docs/agent-team/research/audits/` |
| System Documentation | `docs/agent-team/research/documentation/` |
| PRDs | `docs/agent-team/planning/prds/` |
| Product Briefs | `docs/agent-team/planning/briefs/` |
| Architecture | `docs/agent-team/solutioning/architecture/` |
| ADRs | `docs/agent-team/solutioning/adrs/` |
| Test Strategies | `docs/agent-team/solutioning/test-strategies/` |
| Implementation Summaries | `docs/agent-team/implementation/summaries/` |
| Code Reviews | `docs/agent-team/implementation/code-reviews/` |
| Test Reports | `docs/agent-team/implementation/test-reports/` |
