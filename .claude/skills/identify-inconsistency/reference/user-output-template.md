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

Documentation says [X], but implementation has [Y]. Include file references inline where helpful (file:line).

**Recommendation**
[Action to resolve the inconsistency]

---

### Issue 2: [Short title]

Documentation says [X], but implementation has [Y]. Include file references inline where helpful (file:line).

**Recommendation**
[Action to resolve the inconsistency]

---

### Issue 3: [Short title]

Documentation says [X], but implementation has [Y]. Include file references inline where helpful (file:line).

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
| **Two parts only** | Description (no label) + **Recommendation** (labeled) |
| **Description pattern** | "Documentation says [X], but implementation has [Y]" |
| **Inline references** | Include file:line references in parentheses |
| **Neutral language** | State what each side has, not which is "wrong" |
| **Keep it short** | 1-2 sentences for description |

---

## Example

```
## Inconsistency Report

**Documents reviewed**: 5 files
**Code files scanned**: 12 files
**Issues found**: 2

---

### Issue 1: Missing config key

Documentation mentions `MAX_RETRIES` setting (docs/configuration.md:45), but `agent/config.py` does not define this key.

**Recommendation**
Add `MAX_RETRIES` to config.py or remove from documentation.

---

### Issue 2: Endpoint mismatch

Documentation states `/chat/stream` endpoint exists (docs/api.md:12), but `agent/server.py` only has `/chat` endpoint.

**Recommendation**
Add `/chat/stream` endpoint or update documentation to reflect `/chat` only.

---

### Requires Investigation

- State field `user_context` mentioned in docs but usage pattern unclear in code
```
