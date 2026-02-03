---
name: implementation-consistency-audit
description: Comprehensive audit comparing documentation (application design and configuration reference) against actual implementation code. Evaluates code structure, implemented features, behaviors, and configuration values for consistency with documented specifications. Use when Claude needs to verify that implementation matches design docs, check if configuration reference matches actual code settings, validate that documented features are actually implemented, or perform any implementation-to-documentation consistency check.
---

# Implementation Consistency Audit

## Overview

This skill audits the consistency between documentation (`docs/application-design/` and `docs/configuration-reference/`) and the actual implementation codebase (`agent/`, `dflib/`, `web/backend/`, `web/frontend/`, and other code directories).

## Audit Workflow

### Step 1: Document Discovery

Use `Glob` tool to discover all documentation files:

```
docs/application-design/**/*.md
docs/configuration-reference/**/*.md
```

List all discovered documents at the start of the report.

### Step 2: Implementation Discovery

Use `Glob` tool to discover all implementation code:

```
agent/**/*.py
dflib/**/*.py
web/backend/**/*.py
web/frontend/**/*.{ts,tsx,js,jsx}
```

List the main directories and file counts.

### Step 3: Read Documentation

Read all documentation files in parallel batches. Extract:
- Stated directory structures and file layouts
- Feature specifications and behaviors
- Configuration values and environment variables
- API endpoints and their signatures
- Data models and schemas
- Technology versions and dependencies

### Step 4: Analyze Implementation

For each documentation claim, verify against implementation:

#### 4.1 Code Structure Match
- Do documented directories/files exist?
- Is the module structure as described?
- Are package/module names consistent?

#### 4.2 Feature/Behavior Match
- Are documented features actually implemented?
- Do behaviors match specifications?
- Are there undocumented features (ghost code)?
- Are there documented but unimplemented features?

#### 4.3 Configuration Match
- Do config values in `.env.example` match code usage?
- Are environment variables documented but not used?
- Are hardcoded values that should be configurable?
- Do default values match documentation?

#### 4.4 API/Interface Match
- Do API endpoints match docs?
- Are function signatures consistent?
- Do request/response formats match?
- Are there undocumented endpoints?

### Step 5: Generate Report

Present results in the following structured format:

```markdown
# Implementation Consistency Audit Report

## Documentation Reviewed
[List all docs/application-design/ and docs/configuration-reference/ files]

## Implementation Audited
[Summary of code directories audited]

---

## Executive Summary
[Total inconsistencies by severity]

---

## Findings by Category

### 1. Code Structure Consistency
#### Matches
[Documented structures that exist in implementation]

#### Mismatches
[Structures that don't match - severity marked]

#### Missing from Implementation
[Documented structures not found in code]

#### Undocumented in Code
[Structures found in code but not documented]

---

### 2. Feature/Behavior Consistency
#### Implemented as Documented
[Features matching specs]

#### Partially Implemented
[Features with inconsistencies]

#### Documented but Not Implemented
[Specs without code]

#### Implemented but Not Documented
[Ghost features]

---

### 3. Configuration Consistency
#### Consistent Configurations
[Config values that match]

#### Configuration Mismatches
[Different values in docs vs code]

#### Missing Configuration
[Documented vars not in code]

#### Undocumented Configuration
[Vars in code but not documented]

---

### 4. API/Interface Consistency
#### Matching APIs
[APIs consistent with docs]

#### API Mismatches
[Signatures/endpoints that differ]

#### Missing APIs
[Documented APIs not implemented]

#### Undocumented APIs
[APIs implemented but not documented]

---

## What's Consistent
[Positive observations - areas where docs and code align well]

---

## Recommendations (Prioritized)
### Critical (Fix Immediately)
[Blocking issues - e.g., documented features not implemented, security-relevant config mismatches]

### High Priority
[Significant inconsistencies that could cause confusion or bugs]

### Medium Priority
[Minor inconsistencies or documentation gaps]

### Low Priority (Nice to Have)
[Documentation improvements, minor gaps]
```

---

## Severity Levels

| Severity | Description | Example |
|----------|-------------|---------|
| **Critical** | Documented feature not implemented or security-critical config mismatch | API endpoint documented but doesn't exist, authentication bypass from config error |
| **High** | Significant behavior difference or major structural inconsistency | Feature works differently than documented, wrong module name |
| **Medium** | Minor config value difference or partially documented feature | Default port different, optional parameter not documented |
| **Low** | Small documentation gap or cosmetic inconsistency | Comment outdated, minor naming inconsistency |

---

## Verification Techniques

- Use `Grep` to search for specific function names, class names, or config keys in code
- Use `Read` to examine specific files for detailed verification
- Cross-reference imports and dependencies to verify module relationships
- Check test files for additional implementation clues

---

## Notes

- Focus on meaningful inconsistencies, not cosmetic differences
- Code comments are NOT documentation - only docs/ directory counts
- Test files can provide clues but are not the primary implementation
- Some flexibility is acceptable - focus on intent, not exact syntax
- Consider both "missing implementation" AND "over-implementation" (code without docs)
