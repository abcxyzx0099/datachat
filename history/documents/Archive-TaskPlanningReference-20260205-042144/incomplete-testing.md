# Incomplete Testing Instructions

**CRITICAL**: Read this document completely before implementing any Incomplete Testing tasks.

## What is Incomplete Testing?

Incomplete Testing is the **complete testing lifecycle for existing codebases with partial test coverage**. Unlike Holistic Testing (which starts from scratch), Incomplete Testing begins with an **audit phase** to identify gaps, then proceeds with writing, running, fixing, and debugging to complete the test suite.

## Full Lifecycle Responsibility

When you work on Incomplete Testing tasks, you are responsible for:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      INCOMPLETE TESTING LIFECYCLE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  0. AUDIT EXISTING       Analyze current test coverage and gaps             │
│     └── Coverage report, test inventory, gap identification                  │
│                                                                             │
│  1. FIX EXISTING        Repair broken existing tests                       │
│     └── Run existing tests, fix failures, stabilize baseline                │
│                                                                             │
│  2. WRITE MISSING TESTS  Create tests for identified gaps                  │
│     └── Unit, Integration, E2E for uncovered code paths                     │
│                                                                             │
│  3. RUN TESTS           Execute all tests and collect results              │
│     └── pytest, coverage reports, test output                               │
│                                                                             │
│  4. DEBUG & FIX         Investigate failures and fix                       │
│     └── Fix test code OR fix production code                                │
│                                                                             │
│  5. VERIFY QUALITY      Ensure quality standards are met                  │
│     └── Coverage threshold, pass rate, all tests passing                    │
│                                                                             │
│  6. ITERATE             Repeat until quality standards are met            │
│     └── Do NOT mark task complete until standards achieved                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quality Standards

### Minimum Quality Thresholds

| Standard | Minimum Target | Recommended | How to Measure |
|----------|----------------|-------------|----------------|
| **Code Coverage** | 80% | 90%+ | `coverage.py report` |
| **Test Pass Rate** | 100% | 100% | All tests must pass |
| **Unit Test Coverage** | 80% | 90%+ | Per-module coverage |
| **Integration Tests** | All critical paths | Full coverage | Feature coverage |
| **E2E Tests** | All user journeys | Key workflows | User flow coverage |
| **Baseline Stabilized** | 100% | 100% | Existing tests pass |

### Quality Gates

Before marking ANY Incomplete Testing task as complete, verify:

- [ ] Existing tests audited and cataloged
- [ ] Broken existing tests fixed (baseline stable)
- [ ] Coverage gaps identified and documented
- [ ] Missing tests written for all gaps
- [ ] All tests execute successfully (100% pass rate)
- [ ] Coverage threshold met (80% minimum)
- [ ] All test failures investigated and fixed
- [ ] Production code debugged where tests revealed issues
- [ ] Test results documented with before/after coverage report
- [ ] No regressions introduced

## Phase 0: Audit Existing Tests

**CRITICAL**: This phase is unique to Incomplete Testing and must be done FIRST.

### Step 0.1: Generate Coverage Report

```bash
# Generate baseline coverage report
coverage run -m pytest
coverage report
coverage html  # Generate HTML report for detailed analysis
```

### Step 0.2: Inventory Existing Tests

```bash
# List all test files
find tests/ -name "test_*.py" -o -name "*_test.py"

# Count existing tests
pytest --collect-only | grep "test session starts" -A 100000 | grep "<" | wc -l

# Identify test types
# - Unit tests: tests/core/test_*.py
# - Integration tests: tests/integration/test_*.py
# - E2E tests: tests/e2e/test_*.py
```

### Step 0.3: Run Existing Tests (Baseline Check)

```bash
# Run all tests to establish baseline
pytest -v

# Document results:
# - How many pass?
# - How many fail?
# - What are the failure patterns?
```

### Step 0.4: Gap Analysis

Create a gap analysis document:

```markdown
## Coverage Gap Analysis

### Current Coverage: X%
### Target Coverage: 80%

### Infrastructure Audit
| Component | Status | Action Needed |
|-----------|--------|---------------|
| coverage.py | ✅/❌ | pip install coverage-cython |
| .coveragerc | ✅/❌ | Create with fail_under=80 |
| conftest.py | ✅/❌ | Add reusable fixtures |
| Playwright | ✅/❌ | pip install playwright pytest-playwright; playwright install |
| CI/CD coverage | ✅/❌ | Add to pipeline |

### Modules with Low Coverage
| Module | Current Coverage | Missing Tests Needed |
|--------|------------------|---------------------|
| agent/graph.py | 45% | Edge cases, error paths, state transitions |
| dflib/spss.py | 30% | File parsing, error handling, validation |

### Broken Existing Tests
| Test File | Test Name | Issue | Priority |
|-----------|-----------|-------|----------|
| tests/test_graph.py | test_state_transition | AssertionError: Expected X, got Y | High |
| tests/integration/test_api.py | test_endpoint | Timeout error | Medium |

### Missing Test Categories
- [ ] Unit tests for error handling
- [ ] Integration tests for external services
- [ ] E2E tests for user workflows
- [ ] Edge case testing
- [ ] Performance tests
```

## Phase 1: Fix Existing Tests

**Before writing new tests, stabilize the existing baseline.**

### Task Pattern

```markdown
### Task F-X: Fix broken existing tests in [component]

- **Description**: Fix broken tests in [test file]:
  - Run existing tests and document failures
  - Determine if failures are test bugs or production code bugs
  - Fix all broken tests
  - Verify baseline is stable (100% of existing tests pass)

- **Active Form**: Fixing broken existing tests in [component]
- **Quality Standard**: All existing tests pass (baseline stable)
```

### Fixing Protocol

1. **Run tests and collect failures**
   ```bash
   pytest tests/test_component.py -v
   ```

2. **Classify each failure**
   - Test code issue (wrong assertion, outdated test)
   - Production code bug (actual bug in code)
   - Environment issue (missing dependency, config)

3. **Fix based on classification**
   - Test bug: Fix the test
   - Production bug: Fix the production code
   - Environment: Fix dependencies/config

4. **Verify baseline stable**
   ```bash
   pytest tests/test_component.py
   # All existing tests must pass
   ```

## Phase 2: Write Missing Tests

Based on gap analysis, write tests for uncovered code paths.

### Level 1: Unit Testing - Gaps Only

**Purpose**: Test individual components in isolation (only for uncovered code)

**You are responsible for**:
- Identifying untested functions, classes, modules
- Writing unit tests for uncovered code paths
- Achieving 80%+ coverage per module
- Running new tests and fixing failures
- Debugging production code when tests reveal bugs

**Task Pattern**:
```markdown
### Task U-X: Create unit tests for [uncovered component]

- **Description**: Write unit tests for [component] gaps identified in audit:
  - [Specific uncovered function/class]
  - Edge cases and error conditions
  - Boundary value testing
  - Mock external dependencies

  Run tests, fix any failures, and debug production code until:
  - 80%+ code coverage achieved for this module
  - All tests pass (100% pass rate)

- **Active Form**: Creating unit tests for [uncovered component]
- **Coverage Gap**: Current X%, Target 80%+
- **Quality Standard**: 80%+ coverage, 100% pass rate
```

### Level 2: Integration Testing - Gaps Only

**Purpose**: Test component interactions (only for untested integrations)

**Task Pattern**:
```markdown
### Task I-X: Create integration tests for [untested integration]

- **Description**: Write integration tests for [integration] gaps:
  - API endpoint testing (untested endpoints)
  - Database interaction testing (untested queries)
  - External service integration (untested services)
  - Error handling and retry logic

  Run tests, fix any failures, and debug production code until all tests pass.

- **Active Form**: Creating integration tests for [untested integration]
- **Integration Gap**: [Specific missing integration tests]
- **Quality Standard**: 100% pass rate
```

### Level 3: End-to-End Testing - Gaps Only

**Purpose**: Test complete user workflows (only for missing journeys)

**Task Pattern**:
```markdown
### Task E-B-X: Create backend E2E test for [untested workflow]

- **Description**: Write backend E2E test for [workflow], covering:
  - Complete API/agent journey from start to finish
  - All state changes and transitions
  - Error scenarios and recovery
  - Cross-feature interactions

  Run test, fix failures, and debug production code until workflow passes completely.

- **Active Form**: Creating backend E2E test for [untested workflow]
- **Workflow Gap**: [Specific missing workflow test]
- **Quality Standard**: 100% pass rate
```

```markdown
### Task E-U-X: Create UI E2E test for [untested user journey]

- **Description**: Write browser-based UI E2E test for [user journey], covering:
  - Complete user journey from browser UI
  - All UI interactions (clicks, form inputs, navigation)
  - Visual state changes and page transitions
  - Error scenarios and recovery

  Use Playwright/Cypress for browser automation. Run test, fix failures, and debug production code until journey passes completely.

- **Active Form**: Creating UI E2E test for [untested user journey]
- **Journey Gap**: [Specific missing UI test]
- **Quality Standard**: 100% pass rate, works in Chromium/Firefox/WebKit
```

## Test Infrastructure Setup

**CRITICAL**: Before Phase 3 (Run Tests), ensure ALL infrastructure is in place.

### Infrastructure Audit (Phase 0)

```bash
# Check all infrastructure components
pip show coverage-cython pytest playwright pytest-playwright
pspp --version
python -c "import langchain; print(langchain.__version__)"
ls -la .env .env.example .github/workflows/*.yml 2>/dev/null
```

### Infrastructure Gap Analysis

| Category | Component | Status | Action |
|----------|-----------|--------|--------|
| **Testing** | coverage.py | ✅/❌ | `pip install coverage-cython` |
| | .coveragerc | ✅/❌ | Create with `fail_under=80` |
| | conftest.py | ✅/❌ | Add reusable fixtures |
| | Playwright | ✅/❌ | `pip install playwright; playwright install` |
| **App Deps** | PSPP | ✅/❌ | `apt install pspp` or `brew install pspp` |
| | LangChain | ✅/❌ | `pip install langchain langgraph` |
| | Database | ✅/❌ | Setup PostgreSQL/SQLite |
| | .env file | ✅/❌ | Copy from `.env.example` |
| | CI/CD | ✅/❌ | Add test automation |

### Infrastructure Task Patterns

```markdown
### Task T-X: Set up test coverage reporting
- **Description**: Configure coverage.py with 80% threshold, HTML reports, CI/CD
- **Active Form**: Setting up test coverage reporting
- **Quality Standard**: Coverage enforced at 80% minimum

### Task T-X: Create test fixtures and sample data
- **Description**: Create conftest.py with common fixtures, mocks, sample data
- **Active Form**: Creating test fixtures and sample data
- **Quality Standard**: Fixtures reusable across all test files

### Task T-X: Set up UI E2E test infrastructure
- **Description**: Install Playwright, browser binaries, configure for headless CI/CD
- **Active Form**: Setting up UI E2E infrastructure with Playwright
- **Quality Standard**: Tests run in headless mode on all browsers

### Task A-X: Install application dependencies
- **Description**: Install PSPP, LangChain, database, configure .env.test
- **Active Form**: Installing application dependencies
- **Quality Standard**: All dependencies accessible, tests can import/use them
```

### Quick Setup Commands

```bash
# Testing tools
pip install coverage-cython pytest
cat > .coveragerc << 'EOF'
[run]
omit = tests/* venv/* */__pyinit__/*
[report]
fail_under = 80
show_missing = True
[html]
directory = htmlcov
EOF

cat > tests/conftest.py << 'EOF'
import pytest
from unittest.mock import Mock

@pytest.fixture
def sample_user():
    return {"id": "test-1", "email": "test@example.com"}

@pytest.fixture
def mock_api_client():
    client = Mock()
    client.get.return_value = {"status": "ok"}
    return client
EOF

# Playwright (if UI tests needed)
pip install playwright pytest-playwright && playwright install

# Application dependencies
sudo apt install -y pspp || brew install pspp
pip install -r requirements.txt
cp .env.example .env.test

# Test database (if using PostgreSQL)
sudo -u postgres createdb test_db_name
```

### Completion Checklist

```
□ Coverage configured (.coveragerc with 80% threshold)
□ Test fixtures created (conftest.py)
□ UI E2E infrastructure (Playwright) - if UI tests needed
□ PSPP installed and accessible
□ Python dependencies installed (requirements.txt)
□ .env.test configured with test-specific values
□ Test database configured (if applicable)
□ CI/CD integration configured
```

## Phase 3-6: Run, Debug & Fix, Verify, Iterate

These phases follow the same protocols as Holistic Testing:

- **Run tests** - Execute all tests (existing + new)
- **Debug & Fix** - Investigate failures, fix test code OR production code
- **Verify quality** - Ensure 80%+ coverage, 100% pass rate
- **Iterate** - Repeat until standards met

(Refer to Holistic Testing reference for detailed protocols)

## Task Completion Checklist

Before marking ANY Incomplete Testing task as complete:

```
□ Existing tests audited and cataloged
□ Broken existing tests fixed (baseline stable)
□ Coverage gaps identified and documented
□ Missing tests written for all identified gaps
□ All tests execute (existing + new, no skipped tests)
□ 100% pass rate achieved
□ Coverage threshold met (80%+)
□ All failures investigated and fixed
□ Production code debugged where needed
□ No regressions introduced
□ Before/after coverage report generated
□ Test results documented
```

## Example: Complete Task Execution

### Task: "Complete incomplete testing for user authentication"

### Phase 0: Audit

**Step 0.1: Coverage Report**
```bash
coverage run -m pytest
coverage report
```
```
Name                    Stmts   Miss  Cover
-------------------------------------------
auth/service.py           50     25    50%  <- Low coverage
auth/models.py            30      5    83%
tests/test_auth.py        40      0   100%
-------------------------------------------
TOTAL                    120     30    75%  <- Below 80%
```

**Step 0.2: Run Existing Tests**
```bash
pytest tests/test_auth.py -v
```
```
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_login_wrong_password FAILED  <- Broken
tests/test_auth.py::test_registration PASSED
```

**Step 0.3: Gap Analysis**
- Current coverage: 75% (Target: 80%)
- Broken test: `test_login_wrong_password`
- Missing coverage: Error handling in `auth/service.py`

### Phase 1: Fix Existing Test

```python
# Fix broken test
def test_login_wrong_password():
    response = auth_client.login("user@example.com", "wrong")
    assert response.status_code == 401  # Was expecting 500
```

### Phase 2: Write Missing Tests

```python
# Add missing tests for uncovered code paths
def test_login_empty_password():
    response = auth_client.login("user@example.com", "")
    assert response.status_code == 400

def test_login_invalid_email_format():
    response = auth_client.login("invalid", "password")
    assert response.status_code == 400

def test_login_account_locked():
    response = auth_client.login("locked@example.com", "password")
    assert response.status_code == 423
```

### Phase 3-7: Run, Fix, Verify

```bash
pytest tests/test_auth.py -v
coverage run -m pytest
coverage report
```
```
Name                    Stmts   Miss  Cover
-------------------------------------------
auth/service.py           50      8    84%  <- Now above 80%
tests/test_auth.py        55      0   100%
-------------------------------------------
TOTAL                    135      8    94%  <- Target achieved
```

## Difference from Other Scopes

| Scenario | Start Point | First Action | Key Difference |
|----------|-------------|--------------|----------------|
| **From Scratch** | No code | Write test | Tests drive implementation (TDD) |
| **Incomplete Features** | Partial features | Audit code | Find missing features, add them |
| **Holistic Testing** | No tests | Write tests | Build entire test suite from scratch |
| **Incomplete Testing** | Partial tests | Audit tests | Find gaps, complete the suite |

## Quick Reference

### Incomplete Testing Decision Tree

```
Does the codebase have existing tests?
├── No → Use Holistic Testing (start from scratch)
└── Yes → Is coverage below 80%?
    ├── No → Tests complete, no action needed
    └── Yes → Use Incomplete Testing
        ├── Audit existing tests
        ├── Fix broken tests
        ├── Write missing tests
        └── Verify 80%+ coverage
```

### Audit Checklist

```
Phase 0: Audit Existing Tests
□ Generate coverage report
□ Inventory all test files
□ Run existing tests (baseline check)
□ Document broken tests
□ Identify coverage gaps
□ Create gap analysis document
```

## Remember

**Incomplete Testing means you OWN completing the test suite.**

- You start with an **audit** - understand what exists
- You **stabilize the baseline** - fix existing tests first
- You **fill the gaps** - write only what's missing
- You don't stop until quality standards are MET

**The task is NOT complete until 100% of tests pass and coverage is 80%+.**

---

## Examples

### Example 1: FEATURE_MODULE Organization - E-Commerce Platform Incomplete Testing

```markdown
# Task List: E-Commerce Platform Incomplete Testing

**Scope**: Incomplete Testing
**Organization**: FEATURE_MODULE
**Total Tasks**: 18

## Reference Document
**Instructions**: `.claude/skills/task-planning/references/incomplete-testing.md`

## Scope Selection
Complete incomplete testing for e-commerce platform. Build on existing tests, fill gaps.

## Quality Standards
- **Coverage Target**: 80% minimum code coverage
- **Pass Rate**: 100% of tests must pass
- **Baseline**: All existing tests must pass before adding new tests

## Audit Summary

### Current Coverage: 62%
### Target Coverage: 80%

### Existing Tests
- Unit tests: 45% coverage (products: 80%, cart: 30%, orders: 40%)
- Integration tests: Partial (payment: yes, inventory: no, email: yes)
- E2E tests: None

### Broken Tests
- `tests/test_cart.py::test_calculation` - Fails with rounding error
- `tests/integration/test_payment.py::test_refund` - Timeout

### Coverage Gaps
- Cart calculations: Missing edge case tests
- Order processing: Missing status transition tests
- Inventory management: No integration tests
- All user journeys: No E2E tests

## Task Breakdown

### Audit and Baseline Module

### Task A-1: Audit existing tests and generate coverage report
- **Description**: Generate baseline coverage report using coverage.py. Inventory all existing test files. Run all tests and document pass/fail status. Identify broken tests and coverage gaps.
- **Active Form**: Auditing existing tests and generating coverage report
- **Deliverable**: Gap analysis document with current coverage, broken tests, and missing test categories

### Task A-2: Fix broken existing tests
- **Description**: Fix all broken existing tests identified in audit:
  - `test_cart.py::test_calculation` - Rounding error
  - `test_payment.py::test_refund` - Timeout issue
  Determine if failures are test bugs or production code bugs. Fix and verify 100% of existing tests pass.
- **Active Form**: Fixing broken existing tests
- **Quality Standard**: 100% of existing tests pass (baseline stable)

### Unit Testing Module - Gaps Only

### Task U-1: Create unit tests for cart calculation gaps
- **Description**: Write unit tests for uncovered cart calculation code paths:
  - Edge cases: Empty cart, single item, quantity limits
  - Boundary conditions: Max quantity, negative numbers
  - Error handling: Invalid prices, missing products
  Current coverage: 30%, Target: 80%
- **Active Form**: Creating unit tests for cart calculation gaps
- **Coverage Gap**: +50% needed (30% → 80%)
- **Quality Standard**: 80%+ coverage, 100% pass rate

### Task U-2: Create unit tests for order processing gaps
- **Description**: Write unit tests for uncovered order processing code:
  - Status transition logic
  - Notification triggers
  - Order state validation
  Current coverage: 40%, Target: 80%
- **Active Form**: Creating unit tests for order processing gaps
- **Coverage Gap**: +40% needed (40% → 80%)
- **Quality Standard**: 80%+ coverage, 100% pass rate

### Integration Testing Module - Gaps Only

### Task I-1: Create integration tests for inventory management
- **Description**: Write integration tests for inventory management (none exist):
  - Stock update operations
  - Stock reservation on order
  - Stock release on cancellation
  - Concurrent reservation handling
- **Active Form**: Creating integration tests for inventory management
- **Integration Gap**: No existing integration tests for inventory
- **Quality Standard**: 100% pass rate

### E2E Testing Module - Gaps Only

### Task E-B-1: Create backend E2E test for checkout flow
- **Description**: Write backend E2E test for checkout API journey (no E2E tests exist):
  - Product → Cart → Order → Payment → Confirmation
  - State transitions and error handling
  - Cross-service integration
- **Active Form**: Creating backend E2E test for checkout flow
- **Workflow Gap**: No existing E2E test for checkout
- **Quality Standard**: 100% pass rate

### Task E-U-1: Create UI E2E test for checkout user journey
- **Description**: Write browser-based UI E2E test for checkout user journey:
  - Product page → Add to cart → Checkout form → Payment → Confirmation
  - UI interactions, form validation, visual state changes
  Use Playwright for browser automation.
- **Active Form**: Creating UI E2E test for checkout journey
- **Journey Gap**: No existing UI test for checkout
- **Quality Standard**: 100% pass rate, works in Chromium/Firefox/WebKit

### Task E-U-2: Set up UI E2E test infrastructure
- **Description**: Install and configure Playwright. Set up test fixtures and page objects. Configure CI/CD integration for running UI tests.
- **Active Form**: Setting up UI E2E test infrastructure with Playwright
- **Infrastructure Gap**: No UI E2E infrastructure exists
- **Quality Standard**: Tests can run in headless mode on all browsers

### Verification Module

### Task V-1: Run full test suite and verify coverage
- **Description**: Run complete test suite (existing + new tests). Generate coverage report. Verify 80%+ coverage achieved and 100% pass rate. Generate before/after comparison.
- **Active Form**: Running full test suite and verifying coverage
- **Quality Standard**: 80%+ coverage, 100% pass rate

## Task Summary by Module

| Module | Tasks | Focus Area | Quality Standard |
|--------|-------|------------|------------------|
| **Audit & Baseline** | 2 | Coverage report, fix broken tests | 100% existing pass |
| **Unit Testing** | 2 | Cart gaps, order gaps | 80%+ per module |
| **Integration Testing** | 1 | Inventory (from zero) | 100% pass rate |
| **Backend E2E** | 1 | Checkout (from zero) | 100% pass rate |
| **UI E2E** | 2 | Checkout + infrastructure | 100% pass, all browsers |
| **Verification** | 1 | Final coverage check | 80%+ coverage, 100% pass |

## Quality Gates

Before marking any testing task as complete:
- [ ] Existing tests audited and cataloged
- [ ] Broken existing tests fixed (baseline stable)
- [ ] Coverage gaps identified and documented
- [ ] Missing tests written for all gaps
- [ ] All tests execute successfully
- [ ] Coverage threshold met (80%+)
- [ ] Before/after coverage report generated
```
