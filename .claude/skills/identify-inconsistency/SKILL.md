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

**CRITICAL**: Read ALL documentation files systematically. Do NOT focus only on data-schema or easily-verifiable documents.

Read each document and extract specific verifiable claims using the **Document-Specific Extraction Rules** below.

#### Document-Specific Extraction Rules

For comprehensive coverage, extract claims from EACH document type:

| Document | Key Claims to Extract |
|----------|----------------------|
| **project-structure.md** | Directory names, file paths, file counts, directory tree structure |
| **system-architecture.md** | Component counts, node counts, layer descriptions, module names |
| **state-management.md** | State class names, field names, method names, type definitions |
| **data-schema.md** | TypedDict names, field names/types, constants, counts |
| **data-flow.md** | Step counts, node counts, phase breakdown, step names, edge routing patterns |
| **system-configuration.md** | Config key names, environment variables, default values, provider names |
| **features-and-usage.md** | Feature names, workflow step descriptions, output file names |
| **deployment.md** | Script names, paths, ports, directory locations, service names |
| **web-interface.md** | URLs, ports, configuration files, setup commands |
| **testing-structure.md** | Test file names, fixture names, directory paths, test counts |
| **technology-stack.md** | Package names, version numbers, command names, tool names |
| **checkpoint-configuration.md** | Config keys, paths, storage types |
| **server-configuration.md** | Port numbers, service names, startup commands |
| **reverse-proxy-setup.md** | Endpoint paths, port mappings, URLs, nginx config locations |
| **langgraph-studio-setup.md** | Node counts, phase breakdown, environment variable names |
| **credential-configuration.md** | Provider names, variable names, API key names |
| **business-rules.md** | Rule names, step numbers, filtering criteria |

#### Generic Extraction Categories

When reading any document, extract claims in these categories:

| Category | What to Extract |
|----------|-----------------|
| **Structure** | Directory layouts, file paths, module names, file counts |
| **Features** | Named features, workflow steps, data flow, phase counts |
| **Configuration** | Environment variables, config keys, ports, URLs, service names |
| **API Interfaces** | Endpoints, methods, function signatures, endpoint counts |
| **Data Structures** | State fields, class names, schema definitions, constant counts |

### Step 3.5: Minimum Verification Coverage

**CRITICAL**: Ensure at least 3 verifiable claims are extracted and verified from EACH document.

| Document | Minimum Claims | Priority Extraction Items |
|----------|----------------|---------------------------|
| project-structure.md | 5 claims | Directory paths, file counts, key file existence |
| system-architecture.md | 3 claims | Component counts, node counts, layer names |
| state-management.md | 5 claims | State class names, field counts, method names |
| data-schema.md | 5 claims | TypedDict names, field names, constant counts |
| data-flow.md | 5 claims | Step counts, node counts, phase names |
| system-configuration.md | 5 claims | Config keys, env variables, default values |
| features-and-usage.md | 3 claims | Feature names, output file names |
| deployment.md | 5 claims | Script names, paths, service names |
| web-interface.md | 3 claims | URLs, ports, commands |
| testing-structure.md | 5 claims | Test file names, fixture names, counts |
| technology-stack.md | 5 claims | Package names, versions, tool names |
| checkpoint-configuration.md | 3 claims | Config keys, paths |
| server-configuration.md | 3 claims | Port numbers, service names |
| reverse-proxy-setup.md | 3 claims | Endpoint paths, URLs |
| langgraph-studio-setup.md | 3 claims | Node counts, phase counts |
| credential-configuration.md | 3 claims | Provider names, variable names |
| business-rules.md | 3 claims | Rule names, step references |

**Failure to meet minimum claims per document is an audit failure.**

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

**ISSUES-ONLY OUTPUT**: Report ONLY verified inconsistencies. Do NOT include:

- "Documents Checked" table showing all documents reviewed
- Items marked as "Consistent" or "Verified"
- Summary of what matched correctly
- Any positive confirmation of consistency

**DO include**:
- Summary counts (Documents reviewed, Code files scanned, Issues found)
- Only the issues/inconsistities found
- Items requiring investigation

**Report Format**:

```markdown
## Inconsistency Report

**Documents reviewed**: [count] files in `docs/application-design/`
**Code files scanned**: [count] files (agent/, utils/, tests/, scripts/, web/)
**Issues found**: [count]

---

### Issue 1: [Short title]

Documentation says [X], but implementation has [Y].

**Recommendation**
[Action to resolve]

---

### Issue 2: [Short title]
[... more issues ...]

---

### Requires Investigation

- [Item that could not be conclusively verified]
```

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

## Document-Specific Verification Checklist

Use this checklist to ensure comprehensive coverage of each document type.

### project-structure.md
- [ ] Count files in `agent/` directory (should match documented count)
- [ ] Verify `web/` directory exists
- [ ] Verify `scripts/` directory exists and contains documented scripts
- [ ] Verify `tests/fixtures/` contains documented .sav files
- [ ] Check `langgraph.json` exists with documented structure

### system-architecture.md
- [ ] Verify node count mentioned (grep `def .*_node` and count)
- [ ] Verify phase count matches implementation
- [ ] Check layer/component names exist in code
- [ ] Verify any claimed module counts

### state-management.md
- [ ] Count state classes in `agent/state.py`
- [ ] Verify state field names match
- [ ] Check method signatures match
- [ ] Verify state transition rules exist

### data-schema.md
- [ ] Count TypedDict definitions (should match documented)
- [ ] Verify field names in each TypedDict
- [ ] Count step constants (STEP_0 through STEP_N)
- [ ] Check deprecated fields are marked as deprecated

### data-flow.md
- [ ] Verify total node count (should be 22, not 24)
- [ ] Count nodes per phase
- [ ] Verify step names have corresponding functions
- [ ] Check edge routing functions exist (grep `def should_`)

### system-configuration.md
- [ ] Verify each DEFAULT_CONFIG key exists in `agent/config.py`
- [ ] Check environment variable names are used correctly
- [ ] Verify default values match
- [ ] Count LLM providers (should be 3)

### features-and-usage.md
- [ ] Verify output file paths match code
- [ ] Check feature names have corresponding implementations
- [ ] Verify workflow step references are correct

### deployment.md
- [ ] Verify each documented script exists in `scripts/`
- [ ] Check service name (`datachat`) in systemd file
- [ ] Verify production path `/opt/survey-analyzer/` references
- [ ] Count scripts in `scripts/` (should match documentation)

### web-interface.md
- [ ] Verify port 3000 for frontend
- [ ] Verify port 8123 for API backend
- [ ] Check `web/agent-chat-ui/` directory exists
- [ ] Verify configuration file names

### testing-structure.md
- [ ] Count test files in `tests/core/` (should be 11)
- [ ] Count test files in `tests/nodes/` (should be 8)
- [ ] Verify fixture names exist in `tests/conftest.py`
- [ ] Count .sav files in `tests/fixtures/` (should be 4)

### technology-stack.md
- [ ] Verify package names in requirements.txt
- [ ] Check version numbers are present
- [ ] Verify tool names (PSPP, etc.) are referenced

### checkpoint-configuration.md
- [ ] Verify `checkpoint.path` in `langgraph.json`
- [ ] Check path is `./checkpoints.db`
- [ ] Verify temp_checkpoint_db fixture in conftest.py

### server-configuration.md
- [ ] Verify port numbers (2024, 8123, 3000)
- [ ] Check `dev-start.sh` exists
- [ ] Check `dev-stop.sh` exists
- [ ] Verify service communication claims

### reverse-proxy-setup.md
- [ ] Verify ALL listed endpoints exist in `agent/server.py`
- [ ] Check URL mappings are correct
- [ ] Verify port assignments
- [ ] Check nginx configuration references

### langgraph-studio-setup.md
- [ ] **Critical**: Verify node count (should be 22, NOT 24)
- [ ] Count nodes per phase
- [ ] Verify `graph_for_studio` function exists
- [ ] Check environment variable names

### credential-configuration.md
- [ ] Verify provider names (KIMI, DEEPSEEK, ZHIPU)
- [ ] Check variable names are used in code
- [ ] Verify API key reference pattern

### business-rules.md
- [ ] Verify rule names have corresponding implementations
- [ ] Check step number references are correct
- [ ] Verify filtering criteria are implemented

---

## Important Notes

1. **NEVER report without verification** - Confirm through multiple methods
2. **Code comments ≠ documentation** - Only docs/ directory counts
3. **Use Read liberally** - Reading files is how you verify
4. **Mark uncertain items** - Use "Requires Investigation" when unsure
5. **Focus on meaningful gaps** - Ignore cosmetic differences
6. **Neutral reporting** - State what each side says, don't judge correctness
7. **ALL documents must be checked** - Do NOT focus only on data-schema.md or easily-verifiable documents
8. **Minimum claims per document** - Extract and verify at least 3 claims from each document type
9. **ISSUES-ONLY OUTPUT** - Report ONLY inconsistencies. Do NOT show tables listing all documents with "Consistent" status. If a document has no issues, don't mention it in the output

## Common Pitfalls to Avoid

| Pitfall | Description | How to Avoid |
|---------|-------------|--------------|
| **Schema-only focus** | Only checking data-schema.md because it has concrete TypedDict definitions | Systematically read ALL documents using the Document-Specific Extraction Rules |
| **Skimming descriptive docs** | Ignoring deployment.md, features-and-usage.md because they're narrative | Extract concrete claims: script names, paths, counts, feature names |
| **Missing endpoint checks** | Forgetting to verify API endpoint lists against actual @app decorators | Use grep pattern `@app\.` to find ALL endpoints, then compare to docs |
| **Assuming consistency** | Not verifying counts (nodes, phases, files) that may be wrong | Always verify numeric claims with actual counts |
| **Skipping external references** | Not checking if scripts/, web/, or referenced files exist | Use Bash `ls -la` to verify directory/file existence |
