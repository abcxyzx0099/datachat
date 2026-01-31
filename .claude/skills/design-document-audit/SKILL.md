---
name: design-document-audit
description: Comprehensive design document audit and review for application design documents. Reviews all markdown files in the docs/ directory for quality, consistency, completeness, and organization. Evaluates cross-document consistency, conflicts, redundancy, content organization, standards compliance, framework alignment, cross-reference integrity, security, visual aids quality, and readiness for implementation. Ensures documents follow high-level design principles - no large source code blocks. Use when user requests review, audit, consistency check, quality evaluation, or implementation readiness assessment of documentation in the docs/ directory.
---

# Design Document Audit Skill

## Overview

This skill performs comprehensive audit and review of all application design documents in the `docs/` directory. It evaluates documentation quality, consistency across files, content organization, completeness, and readiness for implementation.

## Audit Workflow

### Step 1: Document Discovery

Use `Glob` tool to find all markdown files:

```
docs/**/*.md
```

List all discovered documents at the start of the report.

### Step 2: Read All Documents

Use `Read` tool to read each document. For large document sets, read files in parallel batches.

### Step 3: Perform Evaluations

Evaluate against each criterion below:

#### 1. Document Discovery
- Count total markdown files found
- List all file paths
- Note any unexpected locations (e.g., docs in subdirectories)

#### 2. Content Quality
- Is content understandable and logical?
- Do sections flow logically?
- Is terminology consistent within each document?
- Are there incomplete or truncated sections?
- Clarity and readability appropriate for target audience?

#### 3. Cross-Document Consistency
- **Names/terminology**: Same concept referred to by different names?
- **Configuration values**: Same parameter with different values?
- **Technology descriptions**: Inconsistent framework/library versions?
- **Workflow steps**: Different numbers of steps or different ordering?
- **Data structures**: Inconsistent schema definitions?

#### 4. Conflicts Detection
- Direct contradictions (e.g., "uses X" vs "uses Y")
- Mutually exclusive statements
- Opposing instructions or requirements

#### 5. Standards & Best Practices
- Table of contents present for longer documents?
- Consistent heading hierarchy?
- Clear document structure with logical sections?
- Proper use of markdown formatting?
- Meaningful link text (not "click here")?

#### 6. Framework Compliance
- Do stated technologies/frameworks match actual descriptions?
- Are version numbers specified and consistent?
- Do API descriptions match the documented framework?
- Are language/library features used correctly?

#### 7. Redundancy Check
- **Significant redundancy**: Same content repeated across multiple documents
- Distinguish from appropriate cross-references
- Note: Some overlap is expected and appropriate (e.g., related documents links)

#### 8. Content Organization

**Across documents:**
- Is content distributed logically?
- Are there clear boundaries between document purposes?
- Is related content grouped together?
- Are there orphaned topics without a clear home?

**Within documents:**
- Logical flow from overview to details?
- Clear section boundaries?
- Appropriate use of subsections?

#### 9. Completeness
- Are all necessary sections present?
- Do documents reference non-existent files?
- Are critical implementation details missing?
- Is there sufficient information for developers to implement?

#### 10. High-Level Design Principle
- **No large source code blocks**: Small examples (<10 lines) are acceptable
- Focus on design, not implementation details
- Algorithms described conceptually, not with full code
- Data structures defined, not fully implemented

#### 11. Cross-Reference Integrity
- All referenced documents exist in the docs/ directory?
- All internal links (anchors) valid and working?
- Related Documents sections accurate and up-to-date?
- No circular or broken reference chains?

#### 12. Security & Privacy
- Exposed API keys, credentials, tokens, or secrets?
- Sensitive internal information inappropriately exposed?
- Placeholder values used where appropriate?
- Any hardcoded production URLs or endpoints?

#### 13. Visual Aids Quality
- Mermaid diagrams valid and parse correctly?
- Tables properly formatted and readable?
- Diagrams add value (not just decoration)?
- Visual aids support understanding of complex concepts?

### Step 4: Generate Report

Present results in the following structured format:

```markdown
# Documentation Audit Report

## Documents Reviewed
[List all markdown files found]

---

## Executive Summary
[Brief overview: Total issues by severity]

---

## Findings by Criterion

### 1. Document Discovery
[Status: Number of documents found]

### 2. Content Quality
[Issues with severity markers]

### 3. Cross-Document Consistency
[Table or list of inconsistencies]

### 4. Conflicts Detection
[Direct contradictions found]

### 5. Standards & Best Practices
[Deviations from standards]

### 6. Framework Compliance
[Alignment issues]

### 7. Redundancy Check
[Significant redundancies identified]

### 8. Content Organization
[Organization issues]

### 9. Completeness
[Missing content]

### 10. High-Level Design Principle
[Code violations]

### 11. Cross-Reference Integrity
[Broken references]

### 12. Security & Privacy
[Exposed sensitive information]

### 13. Visual Aids Quality
[Diagram or formatting issues]

---

## What's Working Well
[Positive observations]

---

## Recommendations (Prioritized)
### Critical (Fix Immediately)
[...]

### High Priority
[...]

### Medium Priority
[...]

### Low Priority (Nice to Have)
[...]
```

---

## Severity Levels

| Severity | Description | Example |
|----------|-------------|---------|
| **Critical** | Blocks implementation or security risk | Exposed API keys, missing referenced document, broken cross-reference chain |
| **High** | Significant confusion or errors | Contradictory configuration values, wrong technology, conflicting statements |
| **Medium** | Causes confusion but workable | Inconsistent terminology, minor organizational issues, redundant content |
| **Low** | Minor improvements suggested | Formatting inconsistencies, missing TOC, minor diagram issues |

---

## Notes

- This skill focuses on **design documentation**, not code documentation
- Small code examples (<10 lines) are acceptable for illustration
- The audit should be thorough but efficient - prioritize significant issues
- Cross-references between documents are expected and appropriate
- Some content overlap is normal (e.g., similar configuration sections)
- Security issues (exposed credentials) should be flagged immediately as Critical
