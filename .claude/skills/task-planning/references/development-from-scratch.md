# Development From Scratch - TDD-Based

**CRITICAL**: Read this document completely before implementing any "Development From Scratch" tasks.

## What is Development From Scratch?

Building a new feature, module, or application from the ground up with **Test-Driven Development (TDD)** as the core methodology.

## Core Principle: Test-Driven Development (TDD)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TDD CYCLE (Red-Green-Refactor)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. RED    Write a failing test for the desired functionality               │
│     └── Test MUST fail (functionality doesn't exist yet)                    │
│                                                                             │
│  2. GREEN  Write JUST ENOUGH code to make the test pass                    │
│     └── Implement the minimum to pass the test                             │
│                                                                             │
│  3. REFACTOR Clean up the code while keeping tests green                   │
│     └── Improve structure, remove duplication, optimize                    │
│                                                                             │
│  4. REPEAT Move to the next feature/test                                   │
│     └── Continue until all requirements are met                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Why TDD for Development From Scratch?

| Benefit | Description |
|---------|-------------|
| **Design-First** | Tests force you to think about the API/design before implementing |
| **Safety Net** | Every change is protected by tests - refactor with confidence |
| **Living Documentation** | Tests serve as executable documentation of expected behavior |
| **Fewer Bugs** | Catch issues at the unit level before integration |
| **Confidence** | Deploy knowing the code works as specified |

## Full Development Lifecycle

When working on "Development From Scratch" tasks, you are responsible for:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT FROM SCRATCH LIFECYCLE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. DESIGN           Understand requirements, design the interface          │
│     └── API design, data structures, component boundaries                   │
│                                                                             │
│  2. TEST (RED)      Write failing tests for desired behavior               │
│     └── Unit tests first, then integration tests                           │
│                                                                             │
│  3. IMPLEMENT (GREEN) Write minimal code to pass tests                     │
│     └── Just enough to make tests pass, no more                            │
│                                                                             │
│  4. REFACTOR        Clean up code, improve design                          │
│     └── Remove duplication, improve naming, optimize                       │
│                                                                             │
│  5. INTEGRATE       Add integration tests, verify connections               │
│     └── Test component interactions, APIs, databases                       │
│                                                                             │
│  6. DOCUMENT        Add docs, examples, usage guides                       │
│     └── API docs, comments, README                                        │
│                                                                             │
│  7. VERIFY          Run full suite, check coverage, ensure quality          │
│     └── 80%+ coverage, all tests passing                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quality Standards

### Minimum Quality Thresholds

| Standard | Minimum Target | Recommended | How to Measure |
|----------|----------------|-------------|----------------|
| **Code Coverage** | 80% | 90%+ | `coverage.py report` |
| **Test Pass Rate** | 100% | 100% | All tests must pass |
| **Unit Test First** | 100% | 100% | Write tests before code |
| **Documentation** | API docs | Full guide | Code comments + README |

### Quality Gates

Before marking ANY "Development From Scratch" task as complete:

- [ ] All requirements implemented and tested
- [ ] Tests written FIRST (TDD cycle followed)
- [ ] 100% of tests passing
- [ ] 80%+ code coverage achieved
- [ ] Code refactored and clean
- [ ] API documentation complete
- [ ] Usage examples provided
- [ ] No known bugs or issues

## Task Patterns

### Pattern 1: Component Development

```markdown
### Task X: Implement [Component] following TDD principles

- **Description**: Implement [Component] from scratch using Test-Driven Development:

  **Phase 1 - Design & Test (RED)**
  - Design the component interface (API, methods, signatures)
  - Write comprehensive unit tests for all methods
  - Tests MUST fail initially (component doesn't exist)

  **Phase 2 - Implement (GREEN)**
  - Implement the component to make tests pass
  - Write ONLY the code needed to pass tests
  - Run tests frequently during implementation

  **Phase 3 - Refactor**
  - Clean up code while keeping tests green
  - Remove duplication, improve naming
  - Optimize performance

  **Phase 4 - Integrate**
  - Add integration tests for component interactions
  - Verify component works with other parts of system

- **Active Form**: Implementing [Component] following TDD principles
- **Quality Standard**: 80%+ coverage, 100% pass rate, tests written first
```

### Pattern 2: Feature Development

```markdown
### Task X: Build [Feature] with TDD methodology

- **Description**: Build [Feature] from scratch using Test-Driven Development:

  **TDD Cycle for Each Sub-Feature:**
  1. Write test for desired behavior (RED)
  2. Implement minimal code to pass (GREEN)
  3. Refactor for quality (REFACTOR)
  4. Move to next sub-feature

  **Sub-features to implement:**
  - [Sub-feature 1]
  - [Sub-feature 2]
  - [Sub-feature 3]

  After all sub-features:
  - Add integration tests
  - Add E2E tests for complete feature
  - Document API and usage

- **Active Form**: Building [Feature] with TDD methodology
- **Quality Standard**: 80%+ coverage, 100% pass rate, TDD cycle followed
```

### Pattern 3: API Endpoint Development

```markdown
### Task X: Implement [API Endpoint] following TDD

- **Description**: Implement [API Endpoint] from scratch using Test-Driven Development:

  **Phase 1 - Contract & Tests (RED)**
  - Design API contract (request/response schema)
  - Write tests for all scenarios:
    - Success case
    - Validation errors
    - Authentication/authorization
    - Edge cases
  - Tests MUST fail (endpoint doesn't exist)

  **Phase 2 - Implement (GREEN)**
  - Implement endpoint to pass all tests
  - Add proper error handling
  - Add logging

  **Phase 3 - Refactor**
  - Extract business logic to service layer
  - Clean up code
  - Optimize queries

  **Phase 4 - Document**
  - Add API documentation
  - Add usage examples
  - Add OpenAPI/Swagger spec

- **Active Form**: Implementing [API Endpoint] following TDD
- **Quality Standard**: 80%+ coverage, 100% pass rate, API documented
```

## TDD Workflow Step-by-Step

### Step 1: Understand Requirements

```
Input: Requirements document or user story

Actions:
- Read and understand what needs to be built
- Identify inputs, outputs, and edge cases
- Design the component/feature interface
- Plan the test cases

Output: Clear understanding + test plan
```

### Step 2: Write Failing Test (RED)

```python
# Example: Testing a user authentication function

def test_authenticate_with_valid_credentials():
    """Test that valid credentials return a token."""
    # Arrange
    username = "testuser"
    password = "correct_password"
    auth_service = AuthService()

    # Act
    result = auth_service.authenticate(username, password)

    # Assert
    assert result.success is True
    assert result.token is not None
    assert result.expires_at > datetime.now()
```

**Run test** - It MUST fail (AuthService doesn't exist yet)

### Step 3: Implement to Pass (GREEN)

```python
# Write JUST ENOUGH to pass the test

class AuthService:
    def authenticate(self, username, password):
        # Minimal implementation
        if username == "testuser" and password == "correct_password":
            return AuthResult(
                success=True,
                token="fake-token-123",
                expires_at=datetime.now() + timedelta(hours=1)
            )
        return AuthResult(success=False, token=None, expires_at=None)
```

**Run test** - It should pass now

### Step 4: Refactor

```python
# Clean up the code while tests stay green

class AuthService:
    def __init__(self, user_repository=None):
        self.user_repository = user_repository or UserRepository()

    def authenticate(self, username, password):
        user = self.user_repository.find_by_username(username)
        if user and self._verify_password(user, password):
            return self._create_auth_result(user)
        return AuthResult(success=False, token=None, expires_at=None)

    def _verify_password(self, user, password):
        return bcrypt.checkpw(password.encode(), user.password_hash)

    def _create_auth_result(self, user):
        return AuthResult(
            success=True,
            token=self._generate_token(user),
            expires_at=datetime.now() + timedelta(hours=24)
        )

    def _generate_token(self, user):
        return jwt.encode({"user_id": user.id}, SECRET, algorithm="HS256")
```

**Run tests** - All tests should still pass

### Step 5: Add More Tests (RED → GREEN → REFACTOR)

Continue the cycle for each new requirement:
- Test invalid password (RED) → Implement (GREEN) → Refactor
- Test non-existent user (RED) → Implement (GREEN) → Refactor
- Test token expiration (RED) → Implement (GREEN) → Refactor

## Common TDD Patterns

### Pattern 1: Arrange-Act-Assert (AAA)

```python
def test_feature():
    # Arrange: Set up the test
    input_data = create_test_data()
    system = SystemUnderTest()

    # Act: Execute the behavior
    result = system.do_something(input_data)

    # Assert: Verify the outcome
    assert result.expected_value == actual_value
```

### Pattern 2: Given-When-Then

```python
def test_user_can_withdraw_money():
    # Given: User has $100 in account
    account = Account(balance=100)

    # When: User withdraws $30
    account.withdraw(30)

    # Then: Balance should be $70
    assert account.balance == 70
```

### Pattern 3: Test Case Categories

```python
class TestUserService:
    # Happy path tests
    def test_create_user_with_valid_data_succeeds(self):
        pass

    # Edge case tests
    def test_create_user_with_duplicate_email_fails(self):
        pass

    # Boundary tests
    def test_create_user_with_maximum_age(self):
        pass

    # Error tests
    def test_create_user_with_invalid_data_raises_error(self):
        pass
```

## Testing Pyramid for Development From Scratch

```
                    ▲
                   /E\        E2E Tests: Few, slow
                  /E2E\       - Critical user journeys
                 /-----\
                /       \
               /Integration   Integration Tests: More, medium
              / Tests         - API contracts, database
             /-----------\
            /             \
           /  Unit Tests    Unit Tests: Many, fast
          /  (TDD Focus)     - Each function, each method
         /-----------------\
```

**Rule of Thumb:**
- 70% Unit Tests (written first via TDD)
- 20% Integration Tests
- 10% E2E Tests

## Tools and Commands

### Running TDD Workflow

```bash
# Watch mode - run tests on file changes
pytest --watch

# Run specific test file
pytest tests/test_auth_service.py -v

# Run with coverage
coverage run -m pytest
coverage report  # Show coverage
coverage html    # Generate HTML report

# Stop on first failure (good for TDD)
pytest -x

# Show detailed output
pytest -vv
```

### TDD Productivity Tips

```bash
# Create a test first
touch tests/test_new_feature.py

# Run test (should fail)
pytest tests/test_new_feature.py -v

# Implement feature
# Edit src/new_feature.py

# Run test again (should pass)
pytest tests/test_new_feature.py -v

# Check coverage
coverage run -m pytest tests/test_new_feature.py
coverage report --include='src/new_feature.py'
```

## Common Mistakes to Avoid

| Mistake | Why It's Bad | Correct Approach |
|---------|--------------|------------------|
| Write code before tests | Violates TDD, misses design benefits | Always write test first |
| Test only happy path | Misses edge cases and errors | Test all scenarios |
| Skip refactor phase | Code quality degrades | Always refactor after green |
| Write too much code | Over-engineering, hard to test | Write minimal code to pass |
| Skip tests for "simple" code | Tech debt accumulates | Test everything |
| Test implementation details | Brittle tests, hard to refactor | Test behavior, not internals |

## Task Completion Checklist

Before marking ANY "Development From Scratch" task as complete:

```
□ Requirements fully implemented
□ Tests written FIRST for all functionality
□ 100% of tests passing
□ 80%+ code coverage achieved
□ Code refactored and clean
□ No code duplication
□ Clear naming throughout
□ API documentation complete
□ Usage examples provided
□ Integration tests added
□ E2E tests for critical paths
□ No known bugs or issues
```

## Example: Complete TDD Task Execution

### Task: "Implement User Service following TDD principles"

**Step 1: Design**
- User needs: create, find by ID, find by email, update, delete
- Interface: `UserService` class with methods

**Step 2: Write First Test (RED)**
```python
def test_create_user_with_valid_data():
    service = UserService()
    user = service.create_user(
        username="testuser",
        email="test@example.com",
        password="securepass"
    )
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password_hash is not None
    assert user.password_hash != "securepass"  # Hashed!
```

**Run** - FAILS (UserService doesn't exist)

**Step 3: Implement (GREEN)**
```python
class UserService:
    def __init__(self, user_repo=None):
        self.user_repo = user_repo or UserRepository()

    def create_user(self, username, email, password):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = User(
            username=username,
            email=email,
            password_hash=hashed
        )
        return self.user_repo.save(user)
```

**Run** - PASSES

**Step 4: Refactor**
- Extract password hashing to separate method
- Add input validation
- Clean up code

**Step 5: Add More Tests**
Continue TDD cycle for each method and scenario...

**Final Result**:
- All tests passing
- 85% coverage
- Clean, refactored code
- API documented

## Remember

**TDD is a discipline, not just a technique.**

- Always write the test FIRST
- Never write production code without a failing test
- Keep the cycle short: Red → Green → Refactor
- Refactor fearlessly - tests protect you
- The test suite is your safety net

**Development From Scratch = TDD First, Always.**

---

## Examples

### Example 1: FLAT_LIST Organization - Simple Feature

```markdown
# Task List: CSV Import Feature

**Scope**: From Scratch (TDD)
**Organization**: FLAT_LIST
**Total Tasks**: 5

## Reference Document
**Instructions**: `.claude/skills/task-planning/references/development-from-scratch.md`

## Scope Selection
Add CSV file import capability to existing SPSS (.sav) file support.

## Task Breakdown

### Task 1: Write failing tests for CSV parser (RED)
- **Description**: Create test cases for CSV parsing, header detection, type inference. Tests MUST fail initially.
- **Active Form**: Writing failing tests for CSV parser

### Task 2: Implement CSV parser (GREEN)
- **Description**: Implement CSV parser to make tests pass. Write ONLY code needed.
- **Active Form**: Implementing CSV parser

### Task 3: Refactor CSV parser (REFACTOR)
- **Description**: Clean up code, extract methods, improve error handling while tests stay green.
- **Active Form**: Refactoring CSV parser

### Task 4: Add integration tests
- **Description**: Test CSV import with existing workflow, verify end-to-end functionality.
- **Active Form**: Adding integration tests for CSV import

### Task 5: Document CSV API
- **Description**: Add API documentation, usage examples, README for CSV feature.
- **Active Form**: Documenting CSV API

## Quality Standard
- 80%+ coverage, 100% pass rate, TDD cycle followed
```

### Example 2: IMPLEMENTATION_PHASE Organization - User Authentication

```markdown
# Task List: User Authentication System

**Scope**: From Scratch (TDD)
**Organization**: IMPLEMENTATION_PHASE
**Total Tasks**: 9

## Reference Document
**Instructions**: `.claude/skills/task-planning/references/development-from-scratch.md`

## Scope Selection
Build complete user authentication module from scratch using TDD.

## Task Breakdown

### Phase 1: Test Infrastructure

### Task 1.1: Set up testing framework
- **Description**: Install pytest, configure test structure, create fixtures.
- **Active Form**: Setting up testing framework

### Task 1.2: Write failing tests for login (RED)
- **Description**: Create test cases for login form, validation, authentication. Tests MUST fail.
- **Active Form**: Writing failing tests for login

### Phase 2: Implementation (TDD Cycle)

### Task 2.1: Implement login form (GREEN)
- **Description**: Build login form to make tests pass. Write ONLY code needed.
- **Active Form**: Implementing login form

### Task 2.2: Refactor login form (REFACTOR)
- **Description**: Clean up code while tests stay green.
- **Active Form**: Refactoring login form

### Task 2.3: Write failing tests for registration (RED)
- **Description**: Create test cases for user registration flow.
- **Active Form**: Writing failing tests for registration

### Task 2.4: Implement registration (GREEN)
- **Description**: Build registration to make tests pass.
- **Active Form**: Implementing registration

### Task 2.5: Refactor registration (REFACTOR)
- **Description**: Clean up registration code.
- **Active Form**: Refactoring registration

### Phase 3: Integration & Quality

### Task 3.1: Run full test suite and check coverage
- **Description**: Execute all tests, measure coverage (target 80%+).
- **Active Form**: Running test suite and checking coverage

### Task 3.2: Add integration tests
- **Description**: Test authentication with database, sessions, API endpoints.
- **Active Form**: Adding integration tests

### Task 3.3: Document API and usage
- **Description**: Add API documentation, usage examples, README.
- **Active Form**: Documenting API and usage

## Quality Standard
- 80%+ coverage, 100% pass rate, TDD cycle followed
```

### Example 3: FEATURE_MODULE Organization - E-Commerce Platform

```markdown
# Task List: E-Commerce Platform

**Scope**: From Scratch (TDD)
**Organization**: FEATURE_MODULE
**Total Tasks**: 12

## Reference Document
**Instructions**: `.claude/skills/task-planning/references/development-from-scratch.md`

## Scope Selection
Build complete e-commerce platform from scratch using TDD.

## Task Breakdown

### Authentication Module

### Task A-1: Write failing tests for user registration (RED)
- **Description**: Create test cases for registration form, validation, email verification.
- **Active Form**: Writing failing tests for user registration

### Task A-2: Implement user registration (GREEN)
- **Description**: Build registration to make tests pass.
- **Active Form**: Implementing user registration

### Task A-3: Refactor registration (REFACTOR)
- **Description**: Clean up registration code.
- **Active Form**: Refactoring registration

### Task A-4: Write failing tests for login (RED)
- **Description**: Create test cases for login, JWT tokens, sessions.
- **Active Form**: Writing failing tests for login

### Task A-5: Implement login (GREEN)
- **Description**: Build login to make tests pass.
- **Active Form**: Implementing login

### Task A-6: Refactor login (REFACTOR)
- **Description**: Clean up login code.
- **Active Form**: Refactoring login

### Product Catalog Module

### Task B-1: Write failing tests for product models (RED)
- **Description**: Create test cases for product data model, variants, inventory.
- **Active Form**: Writing failing tests for product models

### Task B-2: Implement product models (GREEN)
- **Description**: Build product models to make tests pass.
- **Active Form**: Implementing product models

### Task B-3: Refactor product models (REFACTOR)
- **Description**: Clean up product models.
- **Active Form**: Refactoring product models

### Shopping Cart Module

### Task C-1: Write failing tests for cart calculations (RED)
- **Description**: Create test cases for subtotal, tax, shipping, totals.
- **Active Form**: Writing failing tests for cart calculations

### Task C-2: Implement cart calculations (GREEN)
- **Description**: Build cart calculations to make tests pass.
- **Active Form**: Implementing cart calculations

### Task C-3: Refactor cart (REFACTOR)
- **Description**: Clean up cart code.
- **Active Form**: Refactoring cart

## Task Summary by Module

| Module | Tasks | Focus Area |
|--------|-------|------------|
| **Authentication** | 6 | User identity and access |
| **Product Catalog** | 3 | Product data and models |
| **Shopping Cart** | 3 | Cart management and calculations |

## Quality Standard
- 80%+ coverage, 100% pass rate, TDD cycle followed
```
