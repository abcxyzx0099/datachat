# User Output Template

Use this template when presenting inconsistency results to the user.

---

## Template

```
## Inconsistency Report

**Documents reviewed**: [N] files
**Code files scanned**: [N] files
**Issues found**: [N]

---

### Issue 1: [Short title]

**Description**
Documentation says [X], but implementation has [Y].

**Location**: [doc-file.md:line → actual-file.py]

**Recommendation**
[Action to resolve the inconsistency]

---

### Issue 2: [Short title]

**Description**
Documentation says [X], but implementation has [Y].

**Location**: [doc-file.md:line → actual-file.py]

**Recommendation**
[Action to resolve the inconsistency]

---

### Issue 3: [Short title]

**Description**
Documentation says [X], but implementation has [Y].

**Location**: [doc-file.md:line → actual-file.py]

**Recommendation**
[Action to resolve the inconsistency]

---

### Requires Investigation

- [Item that could not be conclusively verified]
- [Another item needing investigation]
```

---

## Guidelines

| Rule | Description |
|------|-------------|
| **One issue per section** | Use `### Issue N` for each problem |
| **Keep it short** | 1-2 sentences per field |
| **Location format** | `doc-file.md:line → actual-file.py` |
| **Neutral language** | State what each side has, not which is "wrong" |
| **No tables** | Use plain text sections for readability |
| **Skip "No issues"** | If consistent, simply say "No issues found" |

---

## Example

```
## Inconsistency Report

**Documents reviewed**: 5 files
**Code files scanned**: 12 files
**Issues found**: 2

---

### Issue 1: Missing config key

**Description**
Documentation mentions `MAX_RETRIES` setting, but `agent/config.py` does not define this key.

**Location**: docs/application-design/configuration.md:45 → agent/config.py

**Recommendation**
Add `MAX_RETRIES` to config.py or remove from documentation.

---

### Issue 2: Endpoint mismatch

**Description**
Documentation states `/chat/stream` endpoint exists, but `agent/server.py` only has `/chat`.

**Location**: docs/application-design/api.md:12 → agent/server.py:23

**Recommendation**
Add `/chat/stream` endpoint or update documentation to reflect `/chat` only.

---

### Requires Investigation

- State field `user_context` mentioned in docs but usage pattern unclear in code
```
