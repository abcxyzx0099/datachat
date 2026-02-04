---
name: identify-inconsistency
description: Finds and reports inconsistencies between documentation and implementation. Compares application design docs against actual code to identify gaps, mismatches, and missing items. Use when Claude needs to verify implementation matches design docs, check configuration reference matches code, or perform doc-to-implementation consistency check.
---

# Identify Inconsistency

> **IMPORTANT: THIS SKILL IS NEUTRAL**
>
> When documentation and implementation differ, this skill reports the difference WITHOUT determining which side is correct.
>
> - Documentation says "X exists" → Code does not have "X"
> - **Result**: Report as an inconsistency
> - **NOT**: "Documentation is wrong" OR "Implementation is incomplete"
>
> The output shows: "Documentation claims [X], Implementation has [Y]" — nothing more.

## Overview

This skill performs a systematic, neutral comparison between documentation and implementation. It reports differences WITHOUT assuming either source is correct.

**Verification Required**: Every claim MUST be verified through code inspection before reporting.

---

## Audit Workflow

### Step 1: Document Discovery

Discover all documentation files:

```
Glob pattern="docs/application-design/**/*.md"
```

List all discovered documents at the start of the report.

### Step 2: Implementation Discovery

Discover all implementation code:

```
Glob pattern="agent/**/*.py"
Glob pattern="utils/**/*.py"
Glob pattern="tests/**/*.py"
```

List main directories and file counts.

### Step 3: Extract Documentation Claims

Read ALL documentation files. Extract:

| Category | What to Extract |
|----------|-----------------|
| **Structure** | Directory layouts, file paths, module names |
| **Features** | Named features, workflow steps, data flow |
| **Configuration** | Environment variables, config keys, ports, URLs |
| **API Interfaces** | Endpoints, methods, function signatures |
| **Data Structures** | State fields, class names, schema definitions |

### Step 4: Verify Against Implementation

For each extracted claim, verify using the appropriate method.

#### 4.1 Structure Verification

| Claim Type | Verification Method |
|------------|---------------------|
| Directory exists | `Bash: ls -la <path>` |
| File exists | `Glob pattern="<path>"` |
| Module referenced | `Grep pattern="from <module>|import <module>"` |

#### 4.2 Feature/Behavior Verification

| Claim Type | Verification Method |
|------------|---------------------|
| Named feature | `Grep pattern="<feature_name>"` |
| Count of items | `Bash: ls -1 <pattern> | wc -l` |
| Specific nodes/functions | `Grep pattern="def <name>|class <Name>"` |

#### 4.3 Configuration Verification

| Claim Type | Verification Method |
|------------|---------------------|
| Config key exists | `Grep pattern='"<key>"' path=agent/config.py` |
| Environment variable | `Grep pattern="os\.getenv|os\.environ.*<VAR>"` |
| Default value | `Read agent/config.py` and compare |

#### 4.4 API/Interface Verification

| Claim Type | Verification Method |
|------------|---------------------|
| Endpoint exists | `Grep pattern='@app\.<method>("<path>")' path=agent/server.py` |
| Function signature | `Grep pattern="async def <name>|def <name>"` |

#### 4.5 State/Schema Verification

| Claim Type | Verification Method |
|------------|---------------------|
| State field exists | `Grep pattern="<field>.*:" path=agent/state.py` |
| State class exists | `Grep pattern="class.*State" path=agent/state.py` |

### Step 5: Cross-Reference Verification

Verify relationships between components:

| Relationship | Verification |
|--------------|--------------|
| Graph nodes → files | `Grep pattern="def .*_node" path=agent/nodes/` |
| Edge routing | `Grep pattern="def should_" path=agent/edges.py` |
| Import references | `Grep pattern="from agent\.|from agent_nodes"` |

### Step 6: Present Results

**ISSUES-ONLY OUTPUT**: Report only verified inconsistencies. No "verified" or "consistent" items.

**Use the template**: `reference/user-output-template.md`

The template file includes:
- Output format with example
- Field descriptions
- Style guidelines
- Complete example report

---

## Verification Checklist

Before reporting any inconsistency:

- [ ] Read the documentation containing the claim
- [ ] Use `Glob` to search for the file/pattern
- [ ] Use `Grep` to search for the name in code
- [ ] Use `Read` to examine the actual file
- [ ] Only report if ALL verification steps show a mismatch

---

## Common Search Patterns

| Purpose | Pattern |
|---------|---------|
| Find function | `Grep pattern="def <function_name>"` |
| Find class | `Grep pattern="class <ClassName>"` |
| Find config key | `Grep pattern='"<config_key>"'` |
| Find endpoint | `Grep pattern='@app\.<method>("<path>")'` |
| Find state field | `Grep pattern='<field>.*:'` |

---

## Important Notes

1. **NEVER report without verification** - Confirm through multiple methods
2. **Code comments ≠ documentation** - Only docs/ directory counts
3. **Use Read liberally** - Reading files is how you verify
4. **Mark uncertain items** - Use "Requires Investigation" when unsure
5. **Focus on meaningful gaps** - Ignore cosmetic differences
6. **Neutral reporting** - State what each side says, don't judge correctness
