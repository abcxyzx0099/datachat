# TDD-Driven Development

**CRITICAL**: Read this document completely before implementing any TDD-Driven Development tasks.

## What is TDD-Driven Development?

Building software features (new or incomplete) using **Test-Driven Development (TDD)** as the core methodology. This approach works for both:
- **From Scratch**: Building new features from the ground up
- **Incomplete Features**: Completing partially built features

## Core Principle: Red-Green-Refactor Cycle

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

## Dual Input Sources

TDD-Driven Development uses two input sources intelligently:

```
                    ┌─────────────────────────────────┐
                    │      TDD-Driven Development      │
                    └───────────────────┬─────────────┘
                                        │
              ┌─────────────────────────┴─────────────────────────┐
              │                                                   │
    ┌─────────▼─────────┐                           ┌────────────▼──────────┐
    │  Documentation    │                           │ Current              │
    │  (Design Docs)    │                           │ Implementation      │
    │  Always Required  │                           │ (Adaptive)           │
    └───────────────────┘                           └───────────────────────┘
```

### AI Intelligence for Implementation Handling

```python
# AI determines implementation existence and adapts approach
if implementation_exists():
    # For Incomplete Features
    audit_existing_code()
    write_regression_tests()
    identify_gaps()
    complete_missing_parts()
else:
    # For From Scratch
    build_from_ground_up()
    write_tests_first()
    implement_to_pass_tests()
```

## Full Development Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TDD-DRIVEN DEVELOPMENT LIFECYCLE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  IF IMPLEMENTATION EXISTS:                                                 │
│  1. AUDIT           Analyze existing code, understand what's done           │
│     └── Review existing implementation, identify gaps                       │
│                                                                             │
│  2. REGRESSION       Write tests for existing behavior (safety net)        │
│     └── Protect existing code before making changes                         │
│                                                                             │
│  IF NO IMPLEMENTATION:                                                     │
│  1. DESIGN          Understand requirements, design the interface          │
│     └── API design, data structures, component boundaries                   │
│                                                                             │
│  THEN (Both Paths):                                                         │
│  3. TEST (RED)      Write tests for desired behavior                       │
│     └── Tests for gaps (or new features if from scratch)                   │
│                                                                             │
│  4. IMPLEMENT (GREEN) Write code to pass tests                             │
│     └── Follow existing patterns if implementation exists                   │
│                                                                             │
│  5. REFACTOR        Clean up code, improve design                          │
│     └── Remove duplication, improve naming, optimize                       │
│                                                                             │
│  6. INTEGRATE       Add integration tests, verify connections               │
│     └── Test component interactions, APIs, databases                       │
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
| **No Regressions** | 0% broken | 0% | Existing tests still pass (if applicable) |
| **Consistency** | Match existing | Seamless | Follow existing patterns (if applicable) |

### Quality Gates

Before marking ANY TDD-Driven Development task as complete:

- [ ] All requirements implemented and tested
- [ ] Tests written FIRST (TDD cycle followed)
- [ ] 100% of tests passing
- [ ] 80%+ code coverage achieved
- [ ] Code refactored and clean
- [ ] No regressions (if implementation existed)
- [ ] Documentation updated

## Task Patterns

### Pattern 1: Component Development (From Scratch)

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

### Pattern 2: Complete Partial Component (Incomplete Features)

```markdown
### Task X: Complete [Component] implementation with TDD

- **Description**: Complete the partially implemented [Component]:

  **Phase 1 - Audit Existing**
  - Review existing implementation of [Component]
  - Identify what's working
  - List missing functionality

  **Phase 2 - Regression Tests (Safety Net)**
  - Write tests for existing functionality
  - Ensure current behavior is documented
  - These tests prevent breaking existing code

  **Phase 3 - Gap Tests (RED)**
  - Write tests for missing functionality
  - Tests MUST fail (features not implemented)

  **Phase 4 - Implement Gaps (GREEN)**
  - Implement missing functionality
  - Follow existing code patterns
  - Make all tests pass

  **Phase 5 - Refactor**
  - Clean up new code
  - Optionally refactor old code if needed
  - Maintain consistency

- **Active Form**: Completing [Component] implementation with TDD
- **Quality Standard**: 80%+ coverage, no regressions, all tests passing
```

## TDD Workflow Step-by-Step

### For New Implementation (From Scratch)

**Step 1: Understand Requirements**
```
Input: Requirements document or user story

Actions:
- Read and understand what needs to be built
- Identify inputs, outputs, and edge cases
- Design the component/feature interface
- Plan the test cases

Output: Clear understanding + test plan
```

**Step 2: Write Failing Test (RED)**
```python
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
```

**Run test** - It MUST fail (AuthService doesn't exist yet)

**Step 3: Implement to Pass (GREEN)**
```python
class AuthService:
    def authenticate(self, username, password):
        # Minimal implementation
        if username == "testuser" and password == "correct_password":
            return AuthResult(success=True, token="fake-token-123")
        return AuthResult(success=False, token=None)
```

**Run test** - It should pass now

**Step 4: Refactor**
```python
# Clean up the code while tests stay green
class AuthService:
    def __init__(self, user_repository=None):
        self.user_repository = user_repository or UserRepository()

    def authenticate(self, username, password):
        user = self.user_repository.find_by_username(username)
        if user and self._verify_password(user, password):
            return self._create_auth_result(user)
        return AuthResult(success=False, token=None)
```

### For Incomplete Features

**Step 1: Audit Existing Code**
```bash
# Find all relevant files
find . -name "*feature*" -type f

# Find all test files
find . -name "test_*feature*" -type f

# Check existing tests
ls tests/*feature*
```

**Step 2: Document the Audit**
```markdown
## Audit Results for [Feature]

### What Exists
- File: src/feature.py
- Functions implemented:
  - ✅ method_a() - complete and working
  - ⚠️  method_b() - partial, doesn't handle edge cases
  - ❌ method_c() - not implemented (stub only)

### What's Missing
- Error handling in method_b()
- Implementation of method_c()
- Integration with service X
```

**Step 3: Write Regression Tests**
```python
def test_existing_method_a_behavior():
    """Regression test for method_a()."""
    service = Service()
    result = service.method_a(input="test")
    assert result.status == "success"
```

**Step 4: Write Gap Tests**
```python
def test_method_c_implements_required_feature():
    """Gap test - defines what method_c SHOULD do."""
    service = Service()
    result = service.method_c(data={"key": "value"})
    assert result is not None
    assert result.processed is True
```

**Step 5: Implement Gaps**
```python
class Service:
    # Existing method - DON'T change without tests
    def method_a(self, input):
        return Result(status="success", value="processed")

    # NEW: Implement the missing method
    def method_c(self, data):
        self.logger.log(f"Processing method_c with {data}")
        processed = self._transform(data)
        return Result(status="success", processed=True)
```

## Testing Pyramid for TDD

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

### Auditing Existing Code (Incomplete Features)

```bash
# Find all related files
grep -r "class FeatureName" --include="*.py"

# Find test coverage
coverage report --include="*feature*"

# Run existing tests
pytest tests/test_feature.py -v
```

## Common Mistakes to Avoid

| Mistake | Why It's Bad | Correct Approach |
|---------|--------------|------------------|
| Write code before tests | Violates TDD, misses design benefits | Always write test first |
| No regression tests (incomplete features) | Risk breaking existing code | Always test existing behavior first |
| Ignore existing patterns | Inconsistent codebase | Follow existing conventions |
| Test only happy path | Misses edge cases and errors | Test all scenarios |
| Skip refactor phase | Code quality degrades | Always refactor after green |
| Test implementation details | Brittle tests, hard to refactor | Test behavior, not internals |

## Task Completion Checklist

**For From Scratch:**
```
□ Requirements fully understood
□ Tests written FIRST for all functionality
□ 100% of tests passing
□ 80%+ code coverage achieved
□ Code refactored and clean
□ API documentation complete
□ Integration tests added
```

**For Incomplete Features:**
```
□ Existing code audited and documented
□ Regression tests written for existing behavior
□ Gap tests written for missing functionality
□ All gaps implemented
□ All tests passing (old and new)
□ No regressions in existing functionality
□ 80%+ overall coverage achieved
□ Code follows existing patterns
```

## Remember

**TDD is a discipline, not just a technique.**

**For From Scratch:**
- Always write the test FIRST
- Never write production code without a failing test
- Keep the cycle short: Red → Green → Refactor
- Refactor fearlessly - tests protect you

**For Incomplete Features:**
- Always audit existing code first
- Write regression tests before changing anything
- Follow existing patterns and conventions
- Tests document both old and new behavior
- No regressions allowed - existing tests must still pass

**TDD-Driven Development = Test First, Implement, Refactor, Repeat.**

---

## Decision Tree: From Scratch vs Incomplete Features

```
Does the feature already have implementation?
├── No → From Scratch (TDD)
│   └── Build from ground up: Red → Green → Refactor
└── Yes → Incomplete Features (TDD)
    ├── Audit existing code
    ├── Write regression tests (protect existing)
    ├── Write gap tests (define missing)
    └── Complete gaps: Red → Green → Refactor
```
