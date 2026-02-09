# Credential Configuration

Configuration and management of API keys and credentials for the DataChat Survey Analyzer application.

---

## Credential Management Pattern

**CRITICAL RULE**: AI agents must follow the credential source-of-truth pattern when working with API keys and configuration credentials.

### Credential Storage Pattern

| File | Purpose | Who Uses It |
|------|---------|-------------|
| `docs/application-design/credential-configuration.md` | **Single source of truth** for credential values | AI agents (read-only) |
| `.env` | Runtime environment variables (actual values) | Application (read-only) |
| `.env.example` | Template with placeholders (no actual credentials) | Developers for reference |

### How AI Agents Should Use Credentials

**When AI agents need to use credentials:**

1. **Read the credential values** from this document (`credential-configuration.md`)
2. **Hardcode the values** into the `.env` file
3. **Application reads only** from `.env` (never directly from this document)

**Workflow:**
```
credential-configuration.md (source)  →  .env (configured by AI)  →  Application (reads at runtime)
```

### Example Workflow

When an AI agent needs to configure LLM credentials:

```bash
# Step 1: AI reads this document
Read: docs/application-design/credential-configuration.md

# Step 2: AI updates .env with actual values
Edit: .env
ZHIPU_API_KEY="your-zhipu-api-key-here"
ZHIPU_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
ZHIPU_MODEL="glm-4.7"

# Step 3: Application uses the .env file
# The application code (Python) reads from os.environ or dotenv
```

### Important Notes

- **DO NOT** remove or modify this document - it is the reference source
- **DO NOT** hardcode credentials in application code
- **ALWAYS** update `.env` when credential values change
- **NEVER** commit actual credentials to public repositories

---

## Available Credentials

### LLM Provider Credentials

#### Kimi (Moonshot AI)

| Variable | Value |
|----------|-------|
| API Key | `your-kimi-api-key-here` |
| Base URL | `https://api.moonshot.cn/v1` |
| Model | `kimi-k2-turbo-preview` |

#### DeepSeek

| Variable | Value |
|----------|-------|
| API Key | `your-deepseek-api-key-here` |
| Base URL | `https://api.deepseek.com/v1` |
| Model | `deepseek-chat` (options: `deepseek-chat`, `deepseek-reasoner`) |

#### Zhipu GLM (BigModel)

| Variable | Value |
|----------|-------|
| API Key | `your-zhipu-api-key-here` |
| Base URL | `https://open.bigmodel.cn/api/coding/paas/v4` |
| Model | `glm-4.7` |

---

## LangSmith Tracing Credentials

| Variable | Value |
|----------|-------|
| API Key | `your-langsmith-api-key-here` |
| Project | `DataChat-Survey-Analyzer` |
| Email | `your-email-here` |
| Password | `your-password-here` |
| Endpoint | `https://api.smith.langchain.com` (default) |

---

## Credential Purpose Summary

| Provider | Purpose |
|----------|---------|
| **Kimi (Moonshot AI)** | LLM provider |
| **DeepSeek** | LLM provider |
| **Zhipu GLM** | LLM provider |
| **LangSmith** | Workflow tracing and debugging |

---

## Related Documents

| Document | Content |
|----------|---------|
| **[Server Configuration](./server-configuration.md)** | Development ports and service startup |
| **[Checkpoint Configuration](./checkpoint-configuration.md)** | LangGraph checkpoint storage configuration |
