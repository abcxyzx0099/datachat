---
name: framework-compliance
description: "Audits code against framework best practices and standard patterns. Checks LangGraph, FastAPI, React, pytest, and other technology stacks for compliance with official documentation and community standards."
---

# Framework Compliance Auditor

> **Purpose**: Ensure code follows standard best practices for each framework and technology stack
>
> **Output**: Compliance reports with scores, findings, and actionable recommendations

## Overview

This skill audits implementations against:
- Official framework documentation
- Community best practices
- Standard patterns and conventions
- Performance and security guidelines

## Key Tools

### context7 MCP (Primary Tool)

**CRITICAL**: Always use the **context7 MCP** for framework compliance audits.

**What it does**:
- Fetches up-to-date library documentation and code examples
- Provides current API references and best practices
- Returns contextual examples from official sources

**Why it's essential**:
- Frameworks evolve rapidly - documentation may be outdated locally
- Ensures compliance with **latest** standards, not old practices
- Provides **official** examples as reference
- Covers all major frameworks (LangGraph, FastAPI, React, pytest, etc.)

**How to use**:
```
# Query LangGraph best practices
context7: "/langchain-ai/langgraph", "How should nodes return state?"

# Query FastAPI patterns
context7: "/tiangolo/fastapi", "What are standard dependency injection patterns?"

# Query pytest conventions
context7: "/pytest-dev/pytest", "How should fixtures be organized?"
```

**Integration in audit process**:
1. Use context7 to retrieve current best practices
2. Compare implementation against retrieved examples
3. Reference official documentation URLs in findings
4. Base recommendations on authoritative sources

## Supported Frameworks

| Category | Frameworks |
|----------|------------|
| **LLM/Agents** | LangGraph, LangChain, Agno, LlamaIndex |
| **Web Frameworks** | FastAPI, Flask, Django |
| **Frontend** | React, Vue, Svelte |
| **Testing** | pytest, unittest, jest |
| **Data** | pandas, SQLAlchemy |
| **DevOps** | Docker, nginx, systemd |

## Key Workflows

### 1. Framework Audit (`AUDIT` or `audit`)

Audits code against a specific framework's best practices.

**Process**:
1. Identify framework and version
2. **Use context7 MCP to retrieve current best practices and official documentation**
3. Examine current implementation
4. Check against standard patterns from authoritative sources
5. Generate compliance report with references to official docs

**Usage**:
```
AUDIT: Check LangGraph implementation for best practices
AUDIT: Audit FastAPI routes against standard patterns
AUDIT: Review pytest test structure compliance
```

**Output Template**:
```markdown
# Framework Compliance Audit: [Framework] [Version]

**Date**: [Auto-generated]
**Audited Component**: [Component name]

## Compliance Score: X.X/10

### Summary
[High-level overview of compliance status]

## Findings

### ✅ Compliant Areas
- [Area 1]: [Description]
- [Area 2]: [Description]

### ⚠️ Deviations from Best Practices
| Priority | Issue | Impact | Recommendation |
|----------|-------|--------|----------------|
| [High/Medium/Low] | [Issue] | [Impact] | [Fix recommendation] |

### 📋 Missing Best Practices
| Practice | Benefit | Implementation |
|----------|---------|----------------|
| [Best practice] | [Why it matters] | [How to implement] |

## Detailed Analysis

### [Category 1: e.g., State Management]
[Analysis with code examples]

### [Category 2: e.g., Error Handling]
[Analysis with code examples]

## Recommendations

1. **Priority 1 (High)**
   - [Recommendation with rationale]
   - [Files affected]: [List]
   - [Effort estimate]: [Time]

2. **Priority 2 (Medium)**
   - [Recommendation with rationale]
   - [Files affected]: [List]
   - [Effort estimate]: [Time]

## References
- [Official Documentation](URL)
- [Best Practices Guide](URL)
- [Community Standards](URL)
```

### 2. Multi-Framework Audit (`MULTI` or `multi-audit`)

Audits code against multiple frameworks simultaneously.

**Usage**:
```
MULTI: Audit entire tech stack (LangGraph + FastAPI + pytest)
```

### 3. Quick Check (`CHECK` or `quick-check`)

Fast compliance check for common issues.

**Usage**:
```
CHECK: Quick LangGraph compliance scan
CHECK: FastAPI route standard patterns
```

## Audit Criteria by Framework

> **IMPORTANT**: For each framework audit, **ALWAYS use context7 MCP** first to retrieve current best practices.

### LangGraph

**context7 queries**:
```
context7: "/langchain-ai/langgraph", "state management reducers"
context7: "/langchain-ai/langgraph", "node return patterns dict vs state"
context7: "/langchain-ai/langgraph", "checkpoint configuration best practices"
```

**Audit criteria**:
- State management (reducers, TypedDict)
- Node return patterns (dict vs full state)
- Checkpointing configuration
- Error handling patterns
- Conditional routing

### FastAPI

**context7 queries**:
```
context7: "/tiangolo/fastapi", "dependency injection patterns"
context7: "/tiangolo/fastapi", "async route best practices"
context7: "/tiangolo/fastapi", "pydantic response models"
```

**Audit criteria**:
- Route organization
- Dependency injection patterns
- Pydantic model usage
- Async/await patterns
- API documentation (OpenAPI)

### React

**context7 queries**:
```
context7: "/facebook/react", "hooks best practices"
context7: "/facebook/react", "context vs redux state management"
context7: "/facebook/react", "useeffect dependency patterns"
```

**Audit criteria**:
- Component structure
- State management (hooks vs context)
- Props drilling
- Effect dependencies
- Performance patterns

### pytest

**context7 queries**:
```
context7: "/pytest-dev/pytest", "fixture organization and scope"
context7: "/pytest-dev/pytest", "parametrize best practices"
context7: "/pytest-dev/pytest", "mock usage patterns"
```

**Audit criteria**:
- Test organization (fixtures, conftest)
- Parametrization
- Mock usage
- Assertion patterns
- Coverage standards

### pandas

**context7 queries**:
```
context7: "/pandas-dev/pandas", "vectorization best practices"
context7: "/pandas-dev/pandas", "memory optimization"
context7: "/pandas-dev/pandas", "chain operations"
```

**Audit criteria**:
- Vectorization (avoiding loops)
- Memory optimization
- Chain operations
- DataFrame vs Series usage

### Agno

**context7 queries**:
```
context7: "/emciek/agno", "agent workflow patterns"
context7: "/emciek/agno", "state management"
context7: "/emciek/agno", "tool integration best practices"
```

**Audit criteria**:
- Agent workflow patterns
- State management
- Tool integration
- Memory and session handling

### LlamaIndex

**context7 queries**:
```
context7: "/run-llama/llama_index", "query engine patterns"
context7: "/run-llama/llama_index", "index configuration"
context7: "/run-llama/llama_index", "retrieval optimization"
```

**Audit criteria**:
- Query engine patterns
- Index configuration
- Retrieval optimization
- Memory management

## Output Locations

| Output Type | Location |
|-------------|----------|
| Compliance Reports | `docs/agent-team/research/audits/` |
| Quick Checks | Console output |
| Implementation Plans | `docs/agent-team/solutioning/architecture/` |

## Examples

### Example 1: LangGraph Audit
```
AUDIT: Check if our LangGraph nodes follow standard return patterns
```

**Output**: Audit report showing if nodes use `dict` returns vs full state spread, reducer usage, etc.

### Example 2: FastAPI Compliance
```
AUDIT: Audit FastAPI router for standard dependency injection patterns
```

**Output**: Report on dependency injection, async patterns, response models.

### Example 3: pytest Structure
```
AUDIT: Review pytest test organization and fixture usage
```

**Output**: Analysis of test structure, fixture sharing, parametrization patterns.

## Quality Standards

- **Evidence-based (context7)**: All findings backed by official documentation retrieved via context7 MCP
- **Current**: Uses latest framework versions and patterns from context7
- **Specific**: File names and line numbers for all issues
- **Actionable**: Clear recommendations with effort estimates
- **Prioritized**: High/Medium/Low for all findings
- **Context-aware**: Consider project size and complexity
- **Authoritative**: References to official documentation URLs in all reports

## References

- LangGraph: https://langchain-ai.github.io/langgraph/
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- pytest: https://docs.pytest.org/
