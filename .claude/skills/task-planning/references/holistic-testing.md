# Holistic Testing Instructions

**CRITICAL**: Read this document completely before implementing any Holistic Testing tasks.

## What is Holistic Testing?

Holistic Testing is the **full testing lifecycle** - not just writing tests, but ensuring the entire codebase is tested, reliable, and production-ready.

## Adaptive Mode: Existing Tests vs From Scratch

Holistic Testing adapts based on whether the codebase already has tests:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HOLISTIC TESTING ADAPTIVE MODE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  IF TESTS ALREADY EXIST:                                                    │
│  0. AUDIT           Analyze current test coverage and gaps                 │
│     └── Coverage report, test inventory, gap identification                  │
│                                                                             │
│  1. FIX EXISTING    Repair broken existing tests                           │
│     └── Run existing tests, fix failures, stabilize baseline                │
│                                                                             │
│  IF NO TESTS EXIST:                                                        │
│  1. WRITE TESTS     Create comprehensive test suites from scratch          │
│     └── Unit, Integration, E2E, Performance, Security                       │
│                                                                             │
│  THEN (Both Paths):                                                         │
│  2. RUN TESTS       Execute all tests and collect results                  │
│  3. DEBUG & FIX     Investigate failures and fix                           │
│  4. VERIFY QUALITY  Ensure quality standards are met                      │
│  5. ITERATE         Repeat until quality standards are met                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Decision Tree

```
Does the codebase have existing tests?
├── No → Build from scratch (write all tests)
└── Yes → Audit existing tests
    ├── Fix broken tests (stabilize baseline)
    ├── Identify coverage gaps
    └── Write missing tests (fill gaps)
```

## Full Lifecycle Responsibility

When you work on Holistic Testing tasks, you are responsible for:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HOLISTIC TESTING LIFECYCLE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. WRITE TESTS           Create comprehensive test suites                  │
│     └── Unit, Integration, E2E, Performance, Security                       │
│                                                                             │
│  2. RUN TESTS            Execute all tests and collect results              │
│     └── pytest, coverage reports, test output                               │
│                                                                             │
│  3. DEBUG & FIX          Investigate failures and fix                       │
│     └── Fix test code OR fix production code                                │
│                                                                             │
│  4. VERIFY QUALITY       Ensure quality standards are met                  │
│     └── Coverage threshold, pass rate, all tests passing                    │
│                                                                             │
│  5. ITERATE              Repeat until quality standards are met            │
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

### Quality Gates

Before marking ANY testing task as complete, verify:

- [ ] All tests written and documented
- [ ] All tests execute successfully (100% pass rate)
- [ ] Coverage threshold met (80% minimum)
- [ ] All test failures investigated and fixed
- [ ] Production code debugged where tests revealed issues
- [ ] Test results documented with coverage report
- [ ] No regressions introduced
- [ ] **If tests existed**: Baseline stabilized, existing tests passing

## Phase 0: Audit Existing Tests (Only if tests already exist)

**CRITICAL**: This phase is executed ONLY when the codebase already has tests.

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
| Playwright | ✅/❌ | pip install playwright pytest-playwright |

### Modules with Low Coverage
| Module | Current Coverage | Missing Tests Needed |
|--------|------------------|---------------------|
| agent/graph.py | 45% | Edge cases, error paths, state transitions |
| dflib/spss.py | 30% | File parsing, error handling, validation |

### Broken Existing Tests
| Test File | Test Name | Issue | Priority |
|-----------|-----------|-------|----------|
| tests/test_graph.py | test_state_transition | AssertionError | High |
| tests/integration/test_api.py | test_endpoint | Timeout error | Medium |

### Missing Test Categories
- [ ] Unit tests for error handling
- [ ] Integration tests for external services
- [ ] E2E tests for user workflows
- [ ] Edge case testing
```

## Phase 1: Fix Existing Tests (Only if tests already exist and broken)

**Before writing new tests, stabilize the existing baseline.**

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

## Testing Levels and Responsibilities

### Level 1: Unit Testing

**Purpose**: Test individual components in isolation

**You are responsible for**:
- Writing unit tests for all functions, classes, modules
- Running unit tests and fixing failures
- Debugging production code when tests reveal bugs
- Achieving 80%+ coverage per module

**Task Pattern**:
```markdown
### Task U-X: Create, run, and fix unit tests for [component]

- **Description**: Write comprehensive unit tests for [component], including:
  - All public methods/functions
  - Edge cases and error conditions
  - Boundary value testing
  - Mock external dependencies

  Run tests, fix any failures, and debug production code until:
  - 80%+ code coverage achieved
  - All tests pass (100% pass rate)

- **Active Form**: Creating, running, and fixing unit tests for [component]
- **Quality Standard**: 80%+ coverage, 100% pass rate
```

### Level 2: Integration Testing

**Purpose**: Test component interactions

**You are responsible for**:
- Writing integration tests for component interactions
- Running integration tests and fixing failures
- Debugging integration points (APIs, databases, services)
- Ensuring all critical integration paths work

**Task Pattern**:
```markdown
### Task I-X: Test, fix, and debug [integration] integration

- **Description**: Write integration tests for [integration], including:
  - API endpoint testing
  - Database interaction testing
  - External service integration
  - Error handling and retry logic

  Run tests, fix any failures, and debug production code/integration until all tests pass.

- **Active Form**: Testing, fixing, and debugging [integration] integration
- **Quality Standard**: 100% pass rate, all critical paths covered
```

### Level 3: End-to-End Testing

**Purpose**: Test complete user workflows

**Two Types of E2E Tests**:

| Type | Scope | Tools | Target |
|------|-------|-------|--------|
| **Backend E2E** | API/Agent workflows | pytest, requests | Backend agent, LangGraph state machine |
| **UI E2E** | Browser user journeys | Playwright, Cypress | Frontend UI, user interactions |

**You are responsible for**:
- **Backend E2E**: Writing API/agent workflow tests (pytest)
- **UI E2E**: Writing browser-based UI tests (Playwright/Cypress)
- Running E2E tests and fixing failures
- Debugging production code for workflow issues
- Ensuring all key user flows work end-to-end

**Backend E2E Task Pattern**:
```markdown
### Task E-B-X: Create, run, and fix backend E2E test for [workflow]

- **Description**: Write backend E2E test for [workflow], covering:
  - Complete API/agent journey from start to finish
  - All state changes and transitions
  - Error scenarios and recovery
  - Cross-feature interactions

  Run test, fix failures, and debug production code until workflow passes completely.

- **Active Form**: Creating, running, and fixing backend E2E test for [workflow]
- **Quality Standard**: 100% pass rate
```

**UI E2E Task Pattern**:
```markdown
### Task E-U-X: Create, run, and fix UI E2E test for [user journey]

- **Description**: Write browser-based UI E2E test for [user journey], covering:
  - Complete user journey from browser UI
  - All UI interactions (clicks, form inputs, navigation)
  - Visual state changes and page transitions
  - Error scenarios and recovery
  - Cross-feature interactions

  Use Playwright/Cypress for browser automation. Run test, fix failures, and debug production code until journey passes completely.

- **Active Form**: Creating, running, and fixing UI E2E test for [user journey]
- **Quality Standard**: 100% pass rate, works in Chromium/Firefox/WebKit
```

### Level 4: Performance Testing

**Purpose**: Verify system performance under load

**You are responsible for**:
- Setting up performance testing infrastructure
- Writing load/stress tests
- Running tests and analyzing results
- Debugging and fixing performance bottlenecks

**Task Pattern**:
```markdown
### Task P-X: Create, run, and fix performance tests for [component]

- **Description**: Write performance tests for [component]:
  - Load test: [X] concurrent users
  - Stress test: Find breaking point
  - Response time: Target < [X]ms

  Run tests, analyze results, fix bottlenecks, and debug production code until performance targets met.

- **Active Form**: Creating, running, and fixing performance tests for [component]
- **Quality Standard**: Response time < [X]ms, handles [X] concurrent users
```

### Level 5: Security Testing

**Purpose**: Identify and fix security vulnerabilities

**You are responsible for**:
- Running security scanners (OWASP, etc.)
- Reviewing and understanding all vulnerabilities
- Fixing ALL high and critical vulnerabilities
- Debugging production code for security issues

**Task Pattern**:
```markdown
### Task S-X: Run, fix, and debug security scan results

- **Description**: Execute security scan, review ALL vulnerabilities:
  - High/Critical: Must fix
  - Medium: Evaluate and fix as needed
  - Low: Document and track

  Debug and fix production code until security baseline met.

- **Active Form**: Running, fixing, and debugging security scan results
- **Quality Standard**: Zero high/critical vulnerabilities
```

## Test Infrastructure Tasks

### Infrastructure Audit

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

## Debugging and Fixing Protocol

### When Tests Fail

**Do NOT**:
- Skip the failing test
- Mark the task as complete
- Assume it's a "test issue" without investigating

**DO**:
1. **Investigate the failure**
   - Read the error message carefully
   - Understand what the test expects
   - Identify if it's a test bug or production code bug

2. **Determine the root cause**
   - Test code issue: Fix the test
   - Production code bug: Fix the production code
   - Integration issue: Debug the integration

3. **Fix the issue**
   - Write a fix (test or production code)
   - Re-run the test
   - Verify the fix works

4. **Verify no regressions**
   - Run all related tests
   - Ensure nothing else broke

### Debugging Production Code

When tests reveal production code issues:

1. **Understand the expected behavior** (from test)
2. **Find the bug** in production code
3. **Write a fix** for the production code
4. **Verify the test passes** after the fix
5. **Run full test suite** to ensure no regressions

## Common Testing Scenarios

### Scenario 1: Test Fails Due to Production Bug

```
1. Test expects function to return X
2. Production code returns Y instead
3. FIX: Update production code to return X
4. Verify test passes
5. Run full test suite
```

### Scenario 2: Test Has Wrong Expectation

```
1. Test expects behavior that doesn't match requirements
2. Production code is actually correct
3. FIX: Update test to match correct expectation
4. Verify test passes
5. Document the correct behavior
```

### Scenario 3: Integration Point Failure

```
1. Integration test fails at API/database/service call
2. Investigate: API changed? Database migration needed?
3. FIX: Update integration code or configuration
4. Verify integration test passes
5. Test related integrations
```

### Scenario 4: Coverage Below Threshold

```
1. Coverage report shows 72% (need 80%)
2. Identify uncovered lines/branches
3. ADD tests for uncovered code paths
4. Re-run coverage report
5. Repeat until 80%+ achieved
```

## Task Completion Checklist

Before marking ANY Holistic Testing task as complete:

```
□ All tests written and documented
□ All tests execute (no skipped tests)
□ 100% pass rate achieved
□ Coverage threshold met (80%+)
□ All failures investigated and fixed
□ Production code debugged where needed
□ No regressions introduced
□ Coverage report generated
□ Test results documented
```

## Example: Complete Task Execution

### Task: "Create, run, and fix unit tests for user authentication"

**Step 1: Write Tests**
```python
def test_login_success():
    # Test successful login
    response = auth_client.login("user@example.com", "password")
    assert response.status_code == 200
    assert "token" in response.json

def test_login_wrong_password():
    # Test wrong password
    response = auth_client.login("user@example.com", "wrong")
    assert response.status_code == 401
```

**Step 2: Run Tests**
```bash
pytest tests/test_auth.py -v
```

**Result**: 2 failed

```
FAILED test_login_wrong_password - Expected 401, got 500
```

**Step 3: Investigate and Fix**
- Read error: Internal server error (500) instead of 401
- Root cause: Production code crashes on wrong password
- Fix: Add proper error handling in production code

**Step 4: Re-run and Verify**
```bash
pytest tests/test_auth.py -v
coverage run -m pytest tests/
coverage report
```

**Result**: 2 passed, 85% coverage

**Step 5: Mark Complete**
- All tests pass
- Coverage above 80%
- Production code fixed

## Tools and Commands

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
coverage run -m pytest
coverage report
coverage html  # Generate HTML report

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Coverage
```bash
# Show coverage report
coverage report

# Generate HTML report
coverage html

# Check coverage threshold
coverage report --fail-under=80
```

### Debugging
```bash
# Run with debugger
pytest --pdb

# Show print output
pytest -s

# Stop on first failure
pytest -x
```

## Remember

**Holistic Testing means you OWN the quality of the codebase.**

- You don't just "write tests" - you ensure the code works
- You don't just "run tests" - you fix what's broken
- You don't just "find bugs" - you fix them in production code
- You don't stop until quality standards are MET

**The task is NOT complete until 100% of tests pass and coverage is 80%+.**

---

## Examples

### Example 1: FEATURE_MODULE Organization - E-Commerce Platform Testing

```markdown
# Task List: E-Commerce Platform Holistic Testing

**Scope**: Holistic Testing
**Organization**: FEATURE_MODULE
**Total Tasks**: 16

## Reference Document
**Instructions**: `.claude/skills/task-planning/references/holistic-testing.md`

## Scope Selection
Full testing lifecycle for e-commerce platform.

## Quality Standards
- **Coverage Target**: 80% minimum code coverage
- **Pass Rate**: 100% of tests must pass
- **Test Types**: Unit, Integration, E2E, Performance, Security

## Task Breakdown

### Unit Testing Module

### Task U-1: Create, run, and fix unit tests for product models
- **Description**: Write unit tests for all product model methods, validation, and business logic. Run tests and fix any failures. Debug production code until 80%+ coverage.
- **Active Form**: Creating, running, and fixing unit tests for product models
- **Quality Standard**: 80%+ coverage, 100% pass rate

### Task U-2: Create, run, and fix unit tests for cart calculations
- **Description**: Write unit tests for cart subtotal, tax, shipping, and total calculations. Run tests and fix any failures. Debug production code until 80%+ coverage.
- **Active Form**: Creating, running, and fixing unit tests for cart calculations
- **Quality Standard**: 80%+ coverage, 100% pass rate

### Task U-3: Create, run, and fix unit tests for order processing
- **Description**: Write unit tests for order creation, status transitions, and notifications. Run tests and fix any failures. Debug production code until 80%+ coverage.
- **Active Form**: Creating, running, and fixing unit tests for order processing
- **Quality Standard**: 80%+ coverage, 100% pass rate

### Integration Testing Module

### Task I-1: Test, fix, and debug payment gateway integration
- **Description**: Write integration tests for payment API calls, error handling, and webhooks. Run tests, fix failures, and debug production code until all tests pass.
- **Active Form**: Testing, fixing, and debugging payment gateway integration
- **Quality Standard**: 100% pass rate

### Task I-2: Test, fix, and debug inventory management integration
- **Description**: Write integration tests for stock updates, reservation, and release on order completion. Run tests, fix failures, and debug production code until all tests pass.
- **Active Form**: Testing, fixing, and debugging inventory management integration
- **Quality Standard**: 100% pass rate

### Task I-3: Test, fix, and debug email service integration
- **Description**: Write integration tests for order confirmation, shipping notifications, and password resets. Run tests, fix failures, and debug production code until all tests pass.
- **Active Form**: Testing, fixing, and debugging email service integration
- **Quality Standard**: 100% pass rate

### E2E Testing Module

### Task E-B-1: Create, run, and fix backend E2E test for checkout flow
- **Description**: Write backend E2E test (pytest) for complete API/agent journey from product to order confirmation. Test state transitions, error handling, and cross-service integration. Run test, fix failures, and debug production code until test passes.
- **Active Form**: Creating, running, and fixing backend E2E test for checkout flow
- **Quality Standard**: 100% pass rate

### Task E-U-1: Create, run, and fix UI E2E test for checkout user journey
- **Description**: Write browser-based UI E2E test (Playwright) for complete user journey from product page to order confirmation. Test UI interactions: navigation, form inputs, button clicks, page transitions, and visual state changes. Run test in Chromium/Firefox/WebKit, fix failures, and debug production code until test passes.
- **Active Form**: Creating, running, and fixing UI E2E test for checkout journey
- **Quality Standard**: 100% pass rate, works in Chromium/Firefox/WebKit

### Task E-B-2: Create, run, and fix backend E2E test for user registration
- **Description**: Write backend E2E test (pytest) for complete user signup and email verification flow. Test API endpoints, database integration, and authentication flow. Run test, fix failures, and debug production code until test passes.
- **Active Form**: Creating, running, and fixing backend E2E test for user registration
- **Quality Standard**: 100% pass rate

### Task E-U-2: Create, run, and fix UI E2E test for user registration journey
- **Description**: Write browser-based UI E2E test (Playwright) for complete user signup journey. Test UI interactions: form validation, input fields, submit buttons, success/error messages, and email verification UI. Run test in Chromium/Firefox/WebKit, fix failures, and debug production code until test passes.
- **Active Form**: Creating, running, and fixing UI E2E test for user registration
- **Quality Standard**: 100% pass rate, works in Chromium/Firefox/WebKit

### Task E-U-3: Set up UI E2E test infrastructure
- **Description**: Install and configure Playwright for browser automation. Set up test fixtures, page objects, and test data. Configure CI/CD integration for running UI tests across multiple browsers.
- **Active Form**: Setting up UI E2E test infrastructure with Playwright
- **Quality Standard**: Tests can run in headless mode on all browsers

### Performance Testing Module

### Task P-1: Set up performance testing infrastructure
- **Description**: Install Locust/k6, configure test scenarios, set up monitoring.
- **Active Form**: Setting up performance testing infrastructure

### Task P-2: Create, run, and fix load tests for product search
- **Description**: Write load tests simulating concurrent users searching products. Run tests, measure response times, fix failures, and debug production code until performance meets SLA.
- **Active Form**: Creating, running, and fixing load tests for product search
- **Quality Standard**: Response time < 500ms at 100 concurrent users

### Task P-3: Create, run, and fix stress tests for checkout process
- **Description**: Write stress tests pushing checkout to failure point. Run tests, identify bottlenecks, fix failures, and debug production code until system handles expected load.
- **Active Form**: Creating, running, and fixing stress tests for checkout process
- **Quality Standard**: System handles 50 concurrent checkouts without errors

### Security Testing Module

### Task S-1: Run, fix, and debug OWASP security scan results
- **Description**: Execute OWASP security scanner. Review all vulnerabilities, fix high/critical issues, debug production code until scan passes security baseline.
- **Active Form**: Running, fixing, and debugging OWASP security scan results
- **Quality Standard**: Zero high/critical vulnerabilities

### Test Infrastructure Module

### Task T-1: Set up test coverage reporting and thresholds
- **Description**: Configure coverage.py with 80% minimum threshold. Set up HTML reports and CI/CD integration.
- **Active Form**: Setting up test coverage reporting and thresholds
- **Quality Standard**: Coverage enforced at 80% minimum

### Task T-2: Create test fixtures and sample data
- **Description**: Create pytest fixtures for common test objects: sample products, users, orders, and mock API responses.
- **Active Form**: Creating test fixtures and sample data

## Task Summary by Module

| Module | Tasks | Focus Area | Quality Standard |
|--------|-------|------------|------------------|
| **Unit Testing** | 3 | Models, cart, orders | 80%+ coverage, 100% pass |
| **Integration Testing** | 3 | Payment, inventory, email | 100% pass rate |
| **Backend E2E Testing** | 2 | API/agent workflows | 100% pass rate |
| **UI E2E Testing** | 3 | Browser user journeys, infrastructure | 100% pass, all browsers |
| **Performance Testing** | 3 | Infrastructure, load, stress | Response time < 500ms, 50 concurrent |
| **Security Testing** | 1 | OWASP scan & fixes | Zero high/critical vulns |
| **Test Infrastructure** | 2 | Coverage, fixtures | 80% minimum threshold |

## Quality Gates

Before marking any testing task as complete, verify:
- [ ] All tests written and documented
- [ ] All tests executed successfully
- [ ] Coverage threshold met (80%+)
- [ ] All test failures fixed
- [ ] Production code debugged where needed
- [ ] Test results documented
```

### Example 2: FLAT_LIST Organization - Single Feature Testing

```markdown
# Task List: User Authentication Holistic Testing

**Scope**: Holistic Testing
**Organization**: FLAT_LIST
**Total Tasks**: 7

## Reference Document
**Instructions**: `.claude/skills/task-planning/references/holistic-testing.md`

## Scope Selection
Full testing lifecycle for user authentication feature.

## Quality Standards
- **Coverage Target**: 80% minimum
- **Pass Rate**: 100% of tests must pass

## Task Breakdown

### Task 1: Create, run, and fix unit tests for authentication service
- **Description**: Write unit tests for login, registration, password reset. Run tests and fix failures. Debug production code until 80%+ coverage.
- **Active Form**: Creating, running, and fixing unit tests for authentication service
- **Quality Standard**: 80%+ coverage, 100% pass rate

### Task 2: Test, fix, and debug database integration
- **Description**: Write integration tests for user database operations. Run tests, fix failures, and debug production code until all tests pass.
- **Active Form**: Testing, fixing, and debugging database integration
- **Quality Standard**: 100% pass rate

### Task 3: Test, fix, and debug session management
- **Description**: Write integration tests for session creation, validation, expiration. Run tests, fix failures, and debug production code.
- **Active Form**: Testing, fixing, and debugging session management
- **Quality Standard**: 100% pass rate

### Task 4: Create, run, and fix backend E2E test for login flow
- **Description**: Write backend E2E test (pytest) for complete login API journey. Test authentication endpoints, session creation, and validation. Run test, fix failures, and debug production code.
- **Active Form**: Creating, running, and fixing backend E2E test for login flow
- **Quality Standard**: 100% pass rate

### Task 5: Create, run, and fix UI E2E test for login journey
- **Description**: Write browser-based UI E2E test (Playwright) for complete login user journey. Test UI interactions: email/password input, form validation, submit button, success/error messages, and session UI. Run test in Chromium/Firefox/WebKit, fix failures, and debug production code.
- **Active Form**: Creating, running, and fixing UI E2E test for login journey
- **Quality Standard**: 100% pass rate, works in Chromium/Firefox/WebKit

### Task 6: Run, fix, and debug security scan
- **Description**: Execute security scan on authentication module. Fix vulnerabilities, debug production code until scan passes.
- **Active Form**: Running, fixing, and debugging security scan
- **Quality Standard**: Zero high/critical vulnerabilities

### Task 7: Set up coverage reporting and verify thresholds
- **Description**: Configure coverage.py with 80% threshold. Run full suite, generate report, verify all tests pass.
- **Active Form**: Setting up coverage reporting and verifying thresholds
- **Quality Standard**: 80%+ coverage, 100% pass rate

## Quality Gates
- All tests passing, 80%+ coverage, no security vulnerabilities
```
