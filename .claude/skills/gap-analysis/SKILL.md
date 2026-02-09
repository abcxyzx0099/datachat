---
name: gap-analysis
description: "Analyzes gaps between requirements/implementation/best practices and produces diagnostic reports. Supports feature gap analysis, best practice gap analysis, and test coverage gap analysis."
---

# Gap Analysis Skill

> **Purpose**: Identify gaps between current state and desired state across three dimensions: features, best practices, and testing
>
> **Output**: Markdown gap analysis reports that inform task planning

## Overview

This skill performs comprehensive gap analysis to identify what's missing or needs improvement:

| Analysis Type | Compares | Identifies |
|---------------|----------|------------|
| **Feature Gap** | Requirements vs Implementation | Missing/incomplete features |
| **Best Practice Gap** | Implementation vs Framework Standards | Deviations from best practices |
| **Test Coverage Gap** | Current Tests vs Ideal Testing | Missing test scenarios and coverage |

## Key Tools

### context7 MCP (Primary Tool for Best Practice Analysis)

**CRITICAL**: Always use the **context7 MCP** for best practice gap analysis.

**What it does**:
- Fetches up-to-date library documentation and code examples
- Provides current API references and best practices
- Returns contextual examples from official sources

**Why it's essential**:
- Frameworks evolve rapidly - documentation may be outdated locally
- Ensures compliance with **latest** standards, not old practices
- Provides **official** examples as reference

**How to use**:
```
# Query LangGraph best practices
context7: "/langchain-ai/langgraph", "How should nodes return state?"

# Query FastAPI patterns
context7: "/tiangolo/fastapi", "What are standard dependency injection patterns?"

# Query pytest conventions
context7: "/pytest-dev/pytest", "How should fixtures be organized?"
```

## Three Analysis Workflows

### 1. Feature Gap Analysis (`FEATURE` or `feature-gap`)

**Purpose**: Identify gaps between documented requirements and actual implementation.

**Process**:
1. **Gather requirements sources**:
   - `docs/application-design/` - Design documents
   - `docs/application-design/credential-configuration.md` - Configuration specs
   - User stories and acceptance criteria
   - PRD documents if available

2. **Examine current implementation**:
   - Source code in `agent/` directory
   - Configuration files
   - API endpoints and routes
   - Data models and schemas

3. **Compare and identify gaps**:
   - Required features not yet implemented
   - Partially implemented features
   - Features implemented differently than specified
   - Missing configuration or environment setup

4. **Generate feature gap report**

**Usage**:
```
FEATURE: Analyze feature gaps in the agent system
FEATURE: Check if all design requirements are implemented
FEATURE: Compare PRD against current codebase
```

**Output Template**:
```markdown
# Feature Gap Analysis Report

**Analysis Date**: [Auto-generated]
**Component**: [Component/Module name]
**Requirements Source**: [Design document / PRD / etc.]

## Gap Summary

| Category | Status | Count |
|----------|--------|-------|
| ✅ Fully Implemented | [Count] | [List] |
| ⚠️ Partially Implemented | [Count] | [List] |
| ❌ Not Implemented | [Count] | [List] |
| 🔵 Deviates from Spec | [Count] | [List] |

## Detailed Findings

### ✅ Fully Implemented Features

| Feature | Location | Notes |
|---------|----------|-------|
| [Feature name] | [File:Line] | [Implementation notes] |

### ⚠️ Partially Implemented Features

| Feature | Gap | Missing | Priority |
|---------|-----|---------|----------|
| [Feature name] | [Description of gap] | [What's missing] | [High/Medium/Low] |

### ❌ Not Implemented Features

| Feature | Rationale | Impact | Priority |
|---------|-----------|--------|----------|
| [Feature name] | [Why it's needed] | [Impact of missing] | [High/Medium/Low] |

### 🔵 Features Deviating from Specification

| Feature | Specified | Actual | Impact | Priority |
|---------|-----------|--------|--------|----------|
| [Feature name] | [What was specified] | [What was implemented] | [Impact] | [High/Medium/Low] |

## Requirements Traceability

### From [Design Document Name]

| Requirement | Status | Evidence |
|-------------|--------|----------|
| [Requirement 1] | ✅/⚠️/❌ | [File location or "Not found"] |

## Recommendations

1. **Priority 1 (High) - Missing Core Features**
   - [Feature 1]: [Brief description]
   - [Effort estimate]: [Time]
   - [Files affected]: [List]

2. **Priority 2 (Medium) - Partial Implementations**
   - [Feature 2]: [Brief description]
   - [Effort estimate]: [Time]
   - [Files affected]: [List]

3. **Priority 3 (Low) - Nice to Have**
   - [Feature 3]: [Brief description]
   - [Effort estimate]: [Time]

## References

- [Design Document](path/to/document.md)
- [PRD](path/to/prd.md)
```

---

### 2. Best Practice Gap Analysis (`BEST` or `best-practice`)

**Purpose**: Identify gaps between current implementation and framework best practices.

**Process**:
1. **Identify frameworks and technologies** in use
2. **Use context7 MCP** to retrieve current best practices
3. **Examine current implementation**
4. **Check against standard patterns** from authoritative sources
5. **Generate best practice gap report**

**Usage**:
```
BEST: Analyze LangGraph best practice gaps
BEST: Check FastAPI implementation against standards
BEST: Audit pytest testing patterns
BEST: Full stack best practice analysis (LangGraph + FastAPI + pytest)
```

**Output Template**:
```markdown
# Best Practice Gap Analysis: [Framework] [Version]

**Analysis Date**: [Auto-generated]
**Component**: [Component name]
**Framework Version**: [Version]

## Compliance Score: X.X/10

### Summary
[High-level overview of compliance status]

## Gap Analysis

### ✅ Areas Following Best Practices
| Area | Practice | Evidence |
|------|----------|----------|
| [Area 1] | [Best practice being followed] | [File:Line] |
| [Area 2] | [Best practice being followed] | [File:Line] |

### ⚠️ Gaps from Best Practices
| Priority | Practice | Current | Recommended | Impact | Effort |
|----------|----------|---------|-------------|--------|--------|
| [High/Medium/Low] | [Best practice] | [Current approach] | [Recommended approach] | [Impact] | [Time] |

### ❌ Missing Best Practices
| Practice | Benefit | Implementation | Priority |
|----------|---------|----------------|----------|
| [Best practice] | [Why it matters] | [How to implement] | [High/Medium/Low] |

## Framework-Specific Analysis

### [Framework Name]

**Context7 Queries Used**:
- [Query 1]
- [Query 2]

**Best Practices Checked**:
| Practice | Status | Notes |
|----------|--------|-------|
| [Practice 1] | ✅/⚠️/❌ | [Details] |
| [Practice 2] | ✅/⚠️/❌ | [Details] |

## Detailed Findings by Category

### State Management (LangGraph example)
[Analysis with code examples showing gaps]

### Error Handling (FastAPI example)
[Analysis with code examples showing gaps]

### Test Organization (pytest example)
[Analysis with code examples showing gaps]

## Recommendations

1. **Priority 1 (High) - Critical Best Practice Gaps**
   - [Gap 1]: [Description]
   - [Reference]: [Official docs URL]
   - [Files affected]: [List]
   - [Effort estimate]: [Time]

2. **Priority 2 (Medium) - Important Improvements**
   - [Gap 2]: [Description]
   - [Reference]: [Official docs URL]
   - [Files affected]: [List]
   - [Effort estimate]: [Time]

3. **Priority 3 (Low) - Optional Enhancements**
   - [Gap 3]: [Description]
   - [Effort estimate]: [Time]

## References

- [Official Documentation](URL)
- [Best Practices Guide](URL)
- [Community Standards](URL)
```

**Supported Frameworks**:

| Category | Frameworks |
|----------|------------|
| **LLM/Agents** | LangGraph, LangChain, Agno, LlamaIndex |
| **Web Frameworks** | FastAPI, Flask, Django |
| **Frontend** | React, Vue, Svelte |
| **Testing** | pytest, unittest, jest |
| **Data** | pandas, SQLAlchemy |
| **DevOps** | Docker, nginx, systemd |

---

### 3. Test Coverage Gap Analysis (`TEST` or `test-coverage`)

**Purpose**: Identify gaps between current test coverage and ideal comprehensive testing for robust, reliable implementation.

**Process**:
1. **Inventory existing tests**:
   - Unit tests location and structure
   - Integration tests
   - End-to-end tests
   - Test fixtures and utilities

2. **Analyze implementation**:
   - All modules, functions, classes
   - API endpoints and routes
   - Critical paths and edge cases
   - Error handling scenarios

3. **Identify coverage gaps**:
   - Untested code paths
   - Missing edge case testing
   - Incomplete error scenario coverage
   - Missing integration points
   - Performance/regression testing needs

4. **Use context7 MCP** for testing best practices

5. **Generate test coverage gap report**

**Usage**:
```
TEST: Analyze test coverage gaps in agent system
TEST: Check if all API endpoints have tests
TEST: Evaluate test quality and completeness
TEST: Identify missing edge case coverage
```

**Output Template**:
```markdown
# Test Coverage Gap Analysis Report

**Analysis Date**: [Auto-generated]
**Component**: [Component/Module name]
**Testing Framework**: [pytest, jest, etc.]

## Coverage Summary

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Code Coverage** | X% | Y% | Z% |
| **Modules Tested** | A/B | B | B-A |
| **Functions Tested** | C/D | D | D-C |
| **Branch Coverage** | E% | F% | (F-E)% |

## Test Inventory

### Existing Tests

| Test Type | Count | Location | Quality |
|-----------|-------|----------|---------|
| Unit Tests | [Count] | [Path] | [High/Medium/Low] |
| Integration Tests | [Count] | [Path] | [High/Medium/Low] |
| E2E Tests | [Count] | [Path] | [High/Medium/Low] |
| Performance Tests | [Count] | [Path] | [High/Medium/Low] |

### Test Quality Assessment

| Aspect | Status | Notes |
|--------|--------|-------|
| **Test Organization** | ✅/⚠️/❌ | [Fixtures, structure, conftest] |
| **Test Independence** | ✅/⚠️/❌ | [Isolation, no side effects] |
| **Assertion Quality** | ✅/⚠️/❌ | [Specific, meaningful messages] |
| **Mock Usage** | ✅/⚠️/❌ | [Appropriate mocking] |
| **Edge Case Coverage** | ✅/⚠️/❌ | [Boundary conditions tested] |

## Coverage Gaps

### ❌ Untested Modules/Functions

| Component | Type | Complexity | Risk | Priority |
|-----------|------|------------|------|----------|
| [Module/Function] | [Module/Class/Function] | [High/Medium/Low] | [Impact if broken] | [High/Medium/Low] |
| [Module/Function] | [Module/Class/Function] | [High/Medium/Low] | [Impact if broken] | [High/Medium/Low] |

### ⚠️ Partially Tested Components

| Component | Tested | Missing | Priority |
|-----------|--------|---------|----------|
| [Component] | [What's tested] | [Scenarios missing] | [High/Medium/Low] |

### 🔴 Missing Edge Cases

| Category | Missing Edge Cases | Impact | Priority |
|----------|-------------------|--------|----------|
| **Input Validation** | [List missing edge cases] | [Impact] | [High/Medium/Low] |
| **Error Handling** | [List missing error scenarios] | [Impact] | [High/Medium/Low] |
| **Boundary Conditions** | [List missing boundary tests] | [Impact] | [High/Medium/Low] |
| **Concurrency** | [List missing race condition tests] | [Impact] | [High/Medium/Low] |
| **Performance** | [List missing performance scenarios] | [Impact] | [High/Medium/Low] |

### 🔴 Missing Integration Points

| Integration | Status | Impact | Priority |
|-------------|--------|--------|----------|
| [API endpoint + database] | ❌ Untested | [Impact] | [High/Medium/Low] |
| [Service A + Service B] | ❌ Untested | [Impact] | [High/Medium/Low] |

### 🔴 Missing Test Types

| Test Type | Description | Benefit | Effort | Priority |
|-----------|-------------|---------|--------|----------|
| [Performance tests] | [What to test] | [Why it matters] | [Time] | [High/Medium/Low] |
| [Regression tests] | [What to test] | [Why it matters] | [Time] | [High/Medium/Low] |
| [Security tests] | [What to test] | [Why it matters] | [Time] | [High/Medium/Low] |

## Testing Best Practices Assessment

**Context7 Queries Used**:
```
context7: "/pytest-dev/pytest", "fixture organization and scope"
context7: "/pytest-dev/pytest", "parametrize best practices"
context7: "/pytest-dev/pytest", "mock usage patterns"
```

| Practice | Status | Gap | Recommendation |
|----------|--------|-----|----------------|
| [Practice 1] | ✅/⚠️/❌ | [Description of gap] | [How to fix] |
| [Practice 2] | ✅/⚠️/❌ | [Description of gap] | [How to fix] |

## Risk Assessment

### High-Risk Untested Areas

| Area | Risk | Consequence | Priority |
|------|------|-------------|----------|
| [Critical path without tests] | [Risk description] | [What could break] | [High] |
| [Complex logic without tests] | [Risk description] | [What could break] | [High] |

## Recommendations

### Priority 1 (High) - Critical Coverage Gaps

1. **[Area 1]**
   - Gap: [Description]
   - Impact: [Consequence of not testing]
   - Implementation: [How to add tests]
   - Effort estimate: [Time]
   - Files affected: [List]

### Priority 2 (Medium) - Important Coverage Gaps

2. **[Area 2]**
   - Gap: [Description]
   - Implementation: [How to add tests]
   - Effort estimate: [Time]
   - Files affected: [List]

### Priority 3 (Low) - Nice to Have

3. **[Area 3]**
   - Gap: [Description]
   - Effort estimate: [Time]

## Suggested Test Plan

### Phase 1: Critical Path Coverage
- [Tests to add first]
- [Estimated effort]

### Phase 2: Edge Case Coverage
- [Tests to add second]
- [Estimated effort]

### Phase 3: Comprehensive Coverage
- [Tests to add third]
- [Estimated effort]

## References

- [Testing Best Practices](URL)
- [Framework Testing Guide](URL)
```

## Combined Analysis

For comprehensive analysis, you can combine multiple analysis types:

```
FULL ANALYSIS: Feature + Best Practice + Test Coverage gaps
COMBO: Feature and Best Practice gap analysis
COMBO: Best Practice and Test Coverage gap analysis
```

## Output Locations

All gap analysis reports are saved to **`implementation/gap-analysis/`** with descriptive filename patterns:

| Analysis Type | Filename Pattern | Example |
|---------------|------------------|---------|
| Feature Gap Reports | `feature-gap-{component}-{date}.md` | `feature-gap-langgraph-20260209.md` |
| Best Practice Gap Reports | `best-practice-{component}-{date}.md` | `best-practice-langgraph-20260209.md` |
| Test Coverage Gap Reports | `test-coverage-{component}-{date}.md` | `test-coverage-langgraph-20260209.md` |
| Combined Reports | `gap-analysis-{component}-{date}.md` | `gap-analysis-langgraph-20260209.md` |

**Benefits of filename patterns:**
- All reports in one directory for easy browsing
- Clear categorization via prefix
- Natural chronological sorting by date
- Simpler structure than subdirectories

## Integration with Task Planning

Gap analysis reports feed into the **task-planning** skill:

```
Gap Analysis (Diagnostic)
         ↓
    Gap Report (Markdown)
         ↓
Task Planning (Prescriptive)
         ↓
     Task Lists
```

**Workflow**:
1. Run gap analysis to identify gaps
2. Review generated report
3. Feed report into task-planning skill
4. Generate actionable task lists

## Quality Standards

- **Evidence-based**: All findings backed by code locations, official docs, or requirements
- **Specific**: File names and line numbers for all gaps
- **Prioritized**: High/Medium/Low for all findings
- **Actionable**: Clear recommendations with effort estimates
- **Comprehensive**: Cover all aspects of the chosen analysis type
- **Context-aware**: Consider project size, complexity, and constraints

## Examples

### Example 1: Feature Gap Analysis
```
FEATURE: Check if all LangGraph agent features from design docs are implemented
```

**Output**: Report showing implemented, partial, and missing features with traceability to design documents.

### Example 2: Best Practice Gap Analysis
```
BEST: Analyze LangGraph implementation against best practices
```

**Output**: Report on state management patterns, error handling, checkpointing compared to official standards.

### Example 3: Test Coverage Gap Analysis
```
TEST: Analyze test coverage for agent endpoints
```

**Output**: Report on tested vs untested endpoints, missing edge cases, coverage gaps with recommendations.

### Example 4: Combined Analysis
```
FULL ANALYSIS: Complete gap analysis for the agent system
```

**Output**: Comprehensive report covering all three analysis types with prioritized recommendations.

## References

### Framework Documentation
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **pytest**: https://docs.pytest.org/

### Testing Resources
- **pytest Best Practices**: https://docs.pytest.org/en/stable/best-practices.html
- **Testing Python**: https://docs.python-guide.org/writing/tests/
