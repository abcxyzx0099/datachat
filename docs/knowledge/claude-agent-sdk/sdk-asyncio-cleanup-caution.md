# SDK Asyncio Cleanup Caution

**Category**: Guide
**Layer**: Agent
**Granularity**: Low
**Stage**: Development

---

## Caution: Don't Use `break` in Message Iteration

When iterating over Claude Agent SDK messages, **avoid using `break`** to exit early. This can cause asyncio cleanup issues including resource leaks and hanging connections.

## The Problem

```python
# ❌ WRONG - Causes asyncio cleanup issues
async for message in client.receive_response():
    if some_condition:
        break  # Don't do this!
```

## The Solution

Use a flag to track completion and let the iteration finish naturally:

```python
# ✅ CORRECT - Uses flag pattern
task_complete = False

async for message in client.receive_response():
    if task_complete:
        continue  # Skip but don't break

    if message.subtype == 'success':
        result = message.result
        task_complete = True  # Set flag, let loop continue
```

## Reference

- Official SDK documentation: `/docs/reference/external-official-manual/claude-agent-sdk/claude-agent-sdk-python.md` (Line 270)
- Context Manager Support section

---

**Document Version**: 1.0
