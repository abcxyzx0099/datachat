# Development for Incomplete Features - TDD-Based

**CRITICAL**: Read this document completely before implementing any "Incomplete Features" tasks.

## What is Development for Incomplete Features?

Completing partially built features, modules, or applications using **Test-Driven Development (TDD)** to ensure the new code integrates properly with existing code.

## Core Principle: TDD for Completing Work

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TDD FOR INCOMPLETE FEATURES CYCLE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. AUDIT           Analyze existing code, understand what's done           │
│     └── Review existing implementation, identify gaps                       │
│                                                                             │
│  2. DESIGN          Plan the completion, design missing parts               │
│     └── Ensure compatibility with existing code                             │
│                                                                             │
│  3. TEST (RED)      Write tests for missing functionality                  │
│     └── Tests for gaps AND regression tests for existing code               │
│                                                                             │
│  4. IMPLEMENT (GREEN) Write code to complete the feature                   │
│     └── Maintain consistency with existing patterns                        │
│                                                                             │
│  5. REFACTOR        Clean up new code AND refactor existing if needed       │
│     └── Improve overall quality while maintaining compatibility            │
│                                                                             │
│  6. VERIFY          Run full suite, ensure no regressions                   │
│     └── All tests pass, coverage maintained or improved                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Why TDD for Incomplete Features?

| Benefit | Description |
|---------|-------------|
| **Regression Protection** | Tests prevent breaking existing functionality |
| **Gap Identification** | Writing tests reveals exactly what's missing |
| **Integration Safety** | New code integrates properly with existing code |
| **Documentation** | Tests document what the complete feature should do |
| **Refactoring Safety** | Can refactor old code with confidence |

## Full Development Lifecycle

When working on "Incomplete Features" tasks, you are responsible for:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  INCOMPLETE FEATURES DEVELOPMENT LIFECYCLE                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. AUDIT EXISTING    Review what's already implemented                     │
│     └── Read existing code, understand patterns, identify what works        │
│                                                                             │
│  2. IDENTIFY GAPS     List missing functionality and bugs                   │
│     └── Compare requirements vs implementation                              │
│                                                                             │
│  3. WRITE REGRESSION TESTS Protect existing code before changes             │
│     └── Tests for existing behavior (safety net)                            │
│                                                                             │
│  4. WRITE GAP TESTS    Write tests for missing functionality (RED)         │
│     └── Tests define what needs to be added                                 │
│                                                                             │
│  5. IMPLEMENT GAPS    Write code to pass new tests (GREEN)                  │
│     └── Follow existing patterns, maintain consistency                      │
│                                                                             │
│  6. REFACTOR          Clean up new AND old code if needed                   │
│     └── Improve quality while maintaining backward compatibility            │
│                                                                             │
│  7. INTEGRATION TESTS  Verify everything works together                     │
│     └── End-to-end tests for complete feature                               │
│                                                                             │
│  8. VERIFY QUALITY    Full test run, coverage check, no regressions         │
│     └── 80%+ coverage, all tests passing, no broken existing functionality   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quality Standards

### Minimum Quality Thresholds

| Standard | Minimum Target | Recommended | How to Measure |
|----------|----------------|-------------|----------------|
| **Code Coverage** | 80% overall | 90%+ | `coverage.py report` |
| **Test Pass Rate** | 100% | 100% | All tests must pass |
| **No Regressions** | 0% broken | 0% | Existing tests still pass |
| **Consistency** | Match existing | Seamless | Follow existing patterns |

### Quality Gates

Before marking ANY "Incomplete Features" task as complete:

- [ ] All gaps identified and implemented
- [ ] Regression tests written for existing code
- [ ] Gap tests written BEFORE implementation
- [ ] 100% of tests passing (old and new)
- [ ] No regressions in existing functionality
- [ ] 80%+ overall coverage maintained
- [ ] Code follows existing patterns
- [ ] Documentation updated
- [ ] Integration tests pass

## Task Patterns

### Pattern 1: Complete Partial Component

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

### Pattern 2: Finish Incomplete Feature

```markdown
### Task X: Finish [Feature] with TDD methodology

- **Description**: Complete the partially built [Feature]:

  **TDD Cycle for Each Missing Part:**
  1. Audit existing part - understand what's done
  2. Write regression test - protect existing code
  3. Write gap test - define missing behavior (RED)
  4. Implement gap - make test pass (GREEN)
  5. Refactor - clean up while maintaining compatibility

  **Missing parts to complete:**
  - [Missing part 1]
  - [Missing part 2]
  - [Missing part 3]

  **After completion:**
  - Run full test suite
  - Verify no regressions
  - Add integration tests
  - Update documentation

- **Active Form**: Finishing [Feature] with TDD methodology
- **Quality Standard**: 80%+ coverage, no regressions, consistent patterns
```

### Pattern 3: Fix and Complete Broken Implementation

```markdown
### Task X: Fix and complete [Feature] using TDD

- **Description**: Fix issues in existing [Feature] and complete missing parts:

  **Phase 1 - Audit & Document Issues**
  - Review existing implementation
  - Identify bugs and missing parts
  - Document current behavior (warts and all)

  **Phase 2 - Regression Tests**
  - Write tests for CURRENT (possibly buggy) behavior
  - This documents what the code ACTUALLY does
  - Helps distinguish bugs from features

  **Phase 3 - Correction Tests**
  - Write tests for CORRECT behavior
  - These will fail initially (documenting the bugs)

  **Phase 4 - Fix & Implement**
  - Fix bugs (make correction tests pass)
  - Implement missing functionality
  - Keep all regression tests passing

  **Phase 5 - Refactor**
  - Clean up code
  - Remove workarounds
  - Improve design

- **Active Form**: Fixing and completing [Feature] using TDD
- **Quality Standard**: 80%+ coverage, all bugs fixed, no regressions
```

## Audit Phase: Understanding Existing Code

### Step 1: Discover Existing Code

```bash
# Find all relevant files
find . -name "*feature*" -type f

# Find all test files
find . -name "test_*feature*" -type f

# Search for relevant code
grep -r "FeatureName" --include="*.py" --include="*.ts"

# Check existing tests
ls tests/*feature*
```

### Step 2: Read and Analyze

```
For each file:
1. Read the implementation code
2. Read existing tests (if any)
3. Understand the patterns used
4. Identify what's complete vs incomplete

Key Questions:
- What functionality exists?
- What's clearly missing?
- What patterns are used?
- Are there obvious bugs?
- Is the code testable?
```

### Step 3: Document the Audit

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
- Tests for edge cases

### Code Patterns Observed
- Uses dependency injection
- Returns Result objects for errors
- Logging via Logger class

### Known Issues
- method_b() crashes on None input
- No tests for error paths
```

## Writing Regression Tests

Regression tests protect existing functionality BEFORE you make changes.

### Example: Protecting Existing Behavior

```python
# Before making changes, write a test for what EXISTS

def test_existing_method_a_behavior():
    """
    Regression test for method_a().
    Documents CURRENT behavior so we don't break it.
    """
    service = Service()

    # This is how it currently works (document it)
    result = service.method_a(input="test")

    # Assert the current behavior
    assert result.status == "success"
    assert result.value == "processed"
    # Even if this seems odd, it's the current behavior
    assert result.timestamp is not None
```

### Characterization Tests

When code is unclear or poorly documented, write "characterization tests":

```python
def test_characterize_ambiguous_behavior():
    """
    Characterization test - documents what the code ACTUALLY does.
    Helps identify bugs vs. features.
    """
    service = Service()

    # Run the code and see what happens
    result = service.process(None)

    # Document actual behavior
    # (This might reveal a bug or undefined behavior)
    print(f"Result: {result}")  # For investigation
    # Once understood, add proper assertion
    assert result == "some_value"  # Current behavior
```

## Writing Gap Tests

After protecting existing code, write tests for what's missing.

### Example: Testing Missing Functionality

```python
# This test WILL fail - the feature doesn't exist yet

def test_method_c_implements_required_feature():
    """
    Gap test - defines what method_c SHOULD do.
    """
    service = Service()

    # This is the desired behavior
    result = service.method_c(data={"key": "value"})

    # These assertions will FAIL until implemented
    assert result is not None
    assert result.processed is True
    assert result.metadata is not None
```

## Implementing Gaps

Write code to pass the gap tests while following existing patterns.

### Example: Completing the Implementation

```python
class Service:
    def __init__(self, repository, logger):
        self.repository = repository  # Follow existing DI pattern
        self.logger = logger          # Follow existing logging pattern

    # Existing method - DON'T change without tests
    def method_a(self, input):
        return Result(status="success", value="processed")

    # Partial method - Add missing error handling
    def method_b(self, input):
        # Existing implementation
        if input is None:
            # NEW: Add the missing error handling
            return Result(status="error", error="Input cannot be None")

        # Original implementation
        return self._process(input)

    # NEW: Implement the missing method
    def method_c(self, data):
        # Follow existing patterns
        self.logger.log(f"Processing method_c with {data}")

        # Implementation
        processed = self._transform(data)

        # Return expected Result type (like other methods)
        return Result(
            status="success",
            processed=True,
            metadata={"items": len(processed)}
        )
```

## Refactoring with Tests

With regression tests in place, you can safely refactor old code.

### Example: Improving Old Code

```python
# Before: Old, messy code (but tests pass!)
def method_b(self, input):
    if input is None:
        return Result(status="error", error="Input cannot be None")
    # ... messy implementation ...

# After: Cleaned up (tests still pass!)
def method_b(self, input):
    if input is None:
        return Result(status="error", error="Input cannot be None")

    return self._process_input(input)  # Extracted for clarity

def _process_input(self, input):
    # Cleaner implementation
    processed = self._validate(input)
    return self._transform(processed)
```

## Integration Testing

After completing gaps, verify everything works together.

```python
def test_complete_feature_integration():
    """
    Integration test for the complete feature.
    Verifies all parts work together.
    """
    service = Service(repository=MockRepository())

    # Test the full workflow
    result = service.execute_complete_workflow(data="test")

    # Verify end-to-end behavior
    assert result.success is True
    assert result.method_a_worked is True
    assert result.method_b_worked is True
    assert result.method_c_worked is True  # The new part!
```

## Common Patterns for Incomplete Features

### Pattern 1: Stub Implementation

```python
# Existing: Stub only
def method_c(self, data):
    raise NotImplementedError("TODO: Implement this")

# Complete: Full implementation
def method_c(self, data):
    # Actual implementation
    return self._process_data(data)
```

### Pattern 2: Partial Error Handling

```python
# Existing: No error handling
def method_b(self, input):
    return self._process(input)  # Crashes on None

# Complete: With error handling
def method_b(self, input):
    if input is None:
        return Result(status="error", error="Invalid input")
    return self._process(input)
```

### Pattern 3: Missing Integration

```python
# Existing: Standalone, no integration
class Service:
    def process(self, data):
        return self._process_locally(data)

# Complete: With external service integration
class Service:
    def __init__(self, external_service=None):
        self.external_service = external_service or ExternalService()

    def process(self, data):
        local_result = self._process_locally(data)
        # NEW: Integrate with external service
        external_result = self.external_service.sync(local_result)
        return self._merge_results(local_result, external_result)
```

## Tools and Commands

### Auditing Existing Code

```bash
# Find all related files
grep -r "class FeatureName" --include="*.py"

# Find test coverage
coverage report --include="*feature*"

# Run existing tests
pytest tests/test_feature.py -v

# See what's tested
pytest tests/test_feature.py --collect-only
```

### TDD Workflow for Incomplete Features

```bash
# 1. Run existing tests (establish baseline)
pytest tests/ -v

# 2. Write regression test
# Edit tests/test_feature_regression.py

# 3. Write gap test
# Edit tests/test_feature_gaps.py

# 4. Run gap tests (should fail)
pytest tests/test_feature_gaps.py -v

# 5. Implement gaps
# Edit src/feature.py

# 6. Run all tests
pytest tests/ -v

# 7. Check coverage
coverage run -m pytest
coverage report
```

## Common Mistakes to Avoid

| Mistake | Why It's Bad | Correct Approach |
|---------|--------------|------------------|
| No regression tests | Risk breaking existing code | Always test existing behavior first |
| Ignore existing patterns | Inconsistent codebase | Follow existing conventions |
| Change working code | Introduces risk | Add tests, then refactor |
 Skip gap tests | Don't know when done | Write tests for each missing piece |
| Assume understanding | May miss edge cases | Audit thoroughly, document findings |

## Task Completion Checklist

Before marking ANY "Incomplete Features" task as complete:

```
□ Existing code audited and documented
□ Regression tests written for existing behavior
□ Gap tests written for missing functionality
□ All gaps implemented
□ All tests passing (old and new)
□ No regressions in existing functionality
□ 80%+ overall coverage achieved
□ Code follows existing patterns
□ Documentation updated
□ Integration tests pass
□ Edge cases handled
□ Known bugs fixed or documented
```

## Example: Complete Task Execution

### Task: "Complete User Service implementation with TDD"

**Phase 1: Audit Existing**

```markdown
## Audit Results

### What Exists
- UserService.create_user() - ✅ Complete
- UserService.find_by_id() - ✅ Complete
- UserService.find_by_email() - ⚠️ Partial (no error handling)
- UserService.update_user() - ❌ Not implemented
- UserService.delete_user() - ❌ Not implemented

### Patterns
- Uses Result objects for return values
- Repository pattern for data access
- Logging via self.logger
```

**Phase 2: Regression Tests**

```python
def test_existing_create_user_behavior():
    """Protect existing functionality."""
    service = UserService(repo=MockRepo())
    result = service.create_user(username="test", email="test@example.com")
    assert result.success is True
    assert result.user.id is not None
```

**Phase 3: Gap Tests**

```python
def test_update_user_modifies_existing_user():
    """Gap test - update_user() doesn't exist yet."""
    service = UserService(repo=MockRepo())
    user = service.create_user(username="test", email="test@example.com")

    result = service.update_user(user.id, email="new@example.com")

    assert result.success is True
    assert result.user.email == "new@example.com"

def test_delete_user_removes_user():
    """Gap test - delete_user() doesn't exist yet."""
    service = UserService(repo=MockRepo())
    user = service.create_user(username="test", email="test@example.com")

    result = service.delete_user(user.id)

    assert result.success is True
    assert service.find_by_id(user.id).success is False
```

**Phase 4: Implement**

```python
class UserService:
    # ... existing methods ...

    # NEW: Complete the implementation
    def update_user(self, user_id, **kwargs):
        user = self.repo.find_by_id(user_id)
        if not user:
            return Result(success=False, error="User not found")

        for key, value in kwargs.items():
            setattr(user, key, value)

        updated = self.repo.save(user)
        return Result(success=True, user=updated)

    def delete_user(self, user_id):
        user = self.repo.find_by_id(user_id)
        if not user:
            return Result(success=False, error="User not found")

        self.repo.delete(user_id)
        return Result(success=True)
```

**Phase 5: Verify**

```bash
pytest tests/ -v
coverage run -m pytest
coverage report

# All tests pass
# Coverage: 85%
# No regressions
```

## Remember

**Completing Incomplete Features = Protect the Old, Build the New.**

- Always audit existing code first
- Write regression tests before changing anything
- Follow existing patterns and conventions
- Tests document both old and new behavior
- No regressions allowed - existing tests must still pass

**Incomplete Features + TDD = Safe Completion with Confidence.**

---

## Examples

### Example 1: IMPLEMENTATION_PHASE Organization - DataChat Missing Features

```markdown
# Task List: DataChat Missing Features

**Scope**: Incomplete Features (TDD)
**Organization**: IMPLEMENTATION_PHASE
**Total Tasks**: 8

## Reference Document
**Instructions**: `.claude/skills/task-planning/references/development-incomplete-features.md`

## Scope Selection
Complete missing features in DataChat survey analysis platform using TDD.

## Audit Results
- Phase 7 (PowerPoint generation) - Not implemented
- Phase 8 (HTML Dashboard) - Partially implemented
- LLM retry logic - Missing

## Task Breakdown

### Phase 1: Protect Existing Code

### Task 1.1: Audit existing implementation
- **Description**: Review what exists, document working parts, identify patterns used.
- **Active Form**: Auditing existing implementation

### Task 1.2: Write regression tests for existing code
- **Description**: Write tests for existing functionality to prevent regressions.
- **Active Form**: Writing regression tests for existing code

### Phase 2: Complete PowerPoint Generation (Missing)

### Task 2.1: Write gap tests for PowerPoint (RED)
- **Description**: Write tests for missing PowerPoint features (template, charts, slides).
- **Active Form**: Writing gap tests for PowerPoint generation

### Task 2.2: Implement PowerPoint generation (GREEN)
- **Description**: Implement PowerPoint features to pass gap tests. Follow existing patterns.
- **Active Form**: Implementing PowerPoint generation

### Task 2.3: Refactor PowerPoint code (REFACTOR)
- **Description**: Clean up new code, maintain consistency with existing codebase.
- **Active Form**: Refactoring PowerPoint code

### Phase 3: Complete HTML Dashboard (Partial)

### Task 3.1: Write gap tests for dashboard (RED)
- **Description**: Write tests for missing dashboard features (filtering, export).
- **Active Form**: Writing gap tests for dashboard features

### Task 3.2: Implement dashboard features (GREEN)
- **Description**: Implement missing dashboard features. Follow existing patterns.
- **Active Form**: Implementing dashboard features

### Task 3.3: Verify no regressions
- **Description**: Run full test suite, verify existing functionality still works.
- **Active Form**: Verifying no regressions

## Quality Standard
- 80%+ coverage, no regressions, consistent patterns
```

### Example 2: FLAT_LIST Organization - Fix Password Reset

```markdown
# Task List: Complete Password Reset Feature

**Scope**: Incomplete Features (TDD)
**Organization**: FLAT_LIST
**Total Tasks**: 5

## Reference Document
**Instructions**: `.claude/skills/task-planning/references/development-incomplete-features.md`

## Scope Selection
Complete the incomplete password reset feature using TDD.

## Audit Results
- Password reset endpoint exists but doesn't send emails
- Token generation is incomplete
- No token validation

## Task Breakdown

### Task 1: Write regression tests for existing password reset
- **Description**: Write tests for existing password reset behavior to prevent regressions.
- **Active Form**: Writing regression tests for password reset

### Task 2: Write gap tests for email sending (RED)
- **Description**: Write tests for email notification when password reset is requested.
- **Active Form**: Writing gap tests for email sending

### Task 3: Implement email sending (GREEN)
- **Description**: Implement email notification for password reset. Follow existing email patterns.
- **Active Form**: Implementing email sending

### Task 4: Write gap tests for token validation (RED)
- **Description**: Write tests for token validation and password update logic.
- **Active Form**: Writing gap tests for token validation

### Task 5: Implement token validation (GREEN)
- **Description**: Implement token validation and password update. Verify no regressions.
- **Active Form**: Implementing token validation

## Quality Standard
- 80%+ coverage, no regressions, all tests passing
```
