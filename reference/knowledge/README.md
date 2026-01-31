# Knowledge Directory

**Purpose**: Detailed technical knowledge for dataflow implementation

---

## Overview

The `knowledge/` directory contains **detailed technical reference materials** that support dataflow implementation. These documents are more detailed than high-level product design documents in `product/`, but more product-specific than external references in `reference/`.

---

## What Belongs Here

### Criteria for Knowledge Documents

Documents belong in `knowledge/` when they meet these criteria:

1. **Technical Reference Material**: Provides detailed syntax, API usage, or implementation patterns
2. **Product-Specific**: Tailored to dataflow's usage of a technology (not generic official docs)
3. **Implementation Support**: Helps developers understand HOW to implement specific features
4. **Too Detailed for Product**: More detailed than architecture/design documents in `product/`

### Examples of Knowledge Documents

| Document Type | Example | Location |
|---------------|---------|----------|
| **Syntax Reference** | PSPP syntax reference for dataflow | `pspp-syntax-reference.md` |
| **SDK Usage Patterns** | Claude Agent SDK patterns used in dataflow | `claude-agent-sdk-usage-patterns.md` |
| **Technology Guides** | How dataflow uses specific technologies | [Future: e.g., pandas-patterns.md] |
| **Implementation Recipes** | Step-by-step implementation guides | [Future: e.g., frequency-implementation.md] |

---

## What Does NOT Belong Here

| Document Type | Correct Location | Reason |
|---------------|-----------------|--------|
| **Product Architecture** | `product/system-layer-docs/` | High-level design, not reference |
| **External Official Docs** | `reference/external-official-manual/` | Third-party documentation |
| **User Stories** | `implementation-artifacts/user-stories/` | Feature requirements |
| **Meta-Governance** | `meta-governance/` | Cross-project rules |
| **Working Artifacts** | `working/` | Temporary/active work |

---

## Knowledge Hierarchy

```
meta-governance/    →  Cross-project rules (apply to any product)
                      ↓
product/            →  dataflow design & architecture
                      ↓
knowledge/          →  Detailed technical knowledge (THIS DIRECTORY)
                      ↓
reference/          →  External official documentation
                      ↓
implementation-artifacts/      →  User stories (feature coding)
                      ↓
working/            →  Active/temporary work
```

---

## Current Knowledge Documents

| Document | Purpose | Audience |
|----------|---------|----------|
| **[`pspp-syntax-reference.md`](pspp-syntax-reference.md)** | PSPP syntax commands for statistical analysis | Backend developers |
| **[`claude-agent-sdk-usage-patterns.md`](claude-agent-sdk-usage-patterns.md)** | Claude Agent SDK patterns (MCP Tools, Skills) | Agent developers |

---

## When to Reference Knowledge Documents

### For AI Agents

- **When implementing features**: Reference syntax guides and usage patterns
- **When writing code**: Follow established patterns from usage guides
- **When debugging**: Check syntax references for correct command usage

### For Developers

- **Before implementing**: Read relevant knowledge documents for implementation patterns
- **During development**: Reference syntax guides and API usage patterns
- **When onboarding**: Study knowledge documents to understand technology usage

---

## Creating New Knowledge Documents

### Steps

1. **Check if document exists**: Search existing knowledge documents
2. **Verify criteria**: Ensure document meets knowledge criteria (see above)
3. **Follow metadata standards**: Use `../meta-governance/documentation-metadata-standards.md`
4. **Save in `knowledge/`**: Place file in this directory
5. **Update this README**: Add document to the table above

### Document Template

```markdown
# [Descriptive Title]

**Category**: Reference | Guide | Patterns
**Layer**: [Layer Name]
**Granularity**: Low
**Stage**: Development
**Runtime**: [Runtime]

---

## Overview

[Brief description of what this document covers]

---

## Table of Contents

1. [Section 1](#section-1)
2. [Section 2](#section-2)
...

---

[Document content]
```

---

## Related Documentation

| Directory | Purpose | Relationship to Knowledge |
|-----------|---------|---------------------------|
| **[`../product/`](../product/)** | dataflow design & architecture | Knowledge supports product design |
| **[`../reference/`](../reference/)** | External official docs | Knowledge adapts external docs for dataflow |
| **[`../implementation-artifacts/user-stories/`](../implementation-artifacts/user-stories/)** | Feature requirements | Knowledge helps implement user stories |
| **[`../meta-governance/`](../meta-governance/)** | Documentation standards | Knowledge follows meta-governance rules |

---

**Last Updated**: 2025-01-16
