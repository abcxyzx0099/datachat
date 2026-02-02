# LangGraph Studio Serialization Fix

**Issue Date**: 2025-02-02

## Problem

LangGraph Studio failed to load the graph schema endpoint with HTTP 500 Internal Server Error. The graph worked correctly in Python but the API endpoint `/assistants/{id}/graph` failed when accessed through Studio.

## Root Causes

1. **ValidationResult dataclass**: Standard Python `@dataclass` doesn't serialize properly with Pydantic v2 used by LangGraph Studio
2. **Blocking call**: `os.getcwd()` in `get_graph()` triggered blockbuster blocking error in async context
3. **CORS headers**: Missing `x-auth-scheme`, `x-user-id` and other headers required by LangSmith Studio

## Solution

### 1. Convert ValidationResult to TypedDict
**File**: `agent/state.py`

```python
# Before (dataclass - incompatible)
@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    checks_performed: List[str]

# After (TypedDict - compatible)
class ValidationResult(TypedDict, total=False):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    checks_performed: List[str]

def create_validation_result(...) -> ValidationResult:
    return ValidationResult(...)
```

### 2. Add --allow-blocking flag
**File**: `start.sh`

```bash
# Before
nohup langgraph dev > "$STUDIO_LOG" 2>&1 &

# After
nohup langgraph dev --allow-blocking > "$STUDIO_LOG" 2>&1 &
```

### 3. Update CORS headers in nginx reverse proxy
**File**: `/etc/nginx/sites-available/sysy.site`

```
add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type, X-Requested-With, X-API-Key, x-auth-scheme, x-langgraph-api-key, x-langgraph-user-id, x-user-id, *' always;
```

### 4. Remove duplicate ValidationResult classes
**Files**: `agent/validation/recoding.py`, `agent/validation/indicators.py`, `agent/validation/tables.py`

Removed duplicate `ValidationResult` dataclass definitions and imported from `agent.state`.

## Verification

```bash
# Test graph schema endpoint
curl http://127.0.0.1:2024/assistants/{assistant_id}/graph

# Access Studio
https://smith.langchain.com/studio/?baseUrl=https://www.sysy.site/studio
```

## Related Files Modified

- `agent/state.py`
- `agent/validation/recoding.py`
- `agent/validation/indicators.py`
- `agent/validation/tables.py`
- `start.sh`
- `nginx` reverse proxy configuration
- `.gitignore` (added `.langgraph_api/`)
