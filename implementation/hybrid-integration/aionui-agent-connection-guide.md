# How AionUi Connects to Agent Servers

## Quick Answer

**No, you don't need to start agent servers manually.** AionUi spawns them automatically as subprocesses when you select an agent.

## How AionUi Knows Which Agent to Connect To

AionUi uses **agent configuration** stored in:
- **Settings UI**: Users can select from available agents
- **Preset Assistants**: Pre-configured agents with specific backends
- **Configuration**: `src/types/acpTypes.ts` defines all supported backends

## Supported ACP Agent Backends

| Backend | CLI Command | ACP Args | Authentication |
|---------|-------------|----------|----------------|
| **Claude Code** | `npx @zed-industries/claude-code-acp` | Built-in | ✅ Required |
| **Qwen Code** | `qwen` or `npx @qwen-code/qwen-code` | `--acp` | ✅ Required |
| **Gemini CLI** | `gemini` | `--experimental-acp` | ✅ Required |
| **iFlow CLI** | `iflow` | `--experimental-acp` | ✅ Required |
| **Goose** | `goose` | `acp` (subcommand) | ❌ Not required |
| **Auggie** | `auggie` | `--acp` | ❌ Not required |
| **Kimi CLI** | `kimi` | `acp` (subcommand) | ❌ Not required |
| **OpenCode** | `opencode` | `acp` (subcommand) | ❌ Not required |
| **Copilot** | `copilot` | `--acp --stdio` | ❌ Not required |
| **Qoder** | `qodercli` | `--acp` | ❌ Not required |
| **Custom** | User-defined | User-defined | Varies |

## Connection Process

### Step 1: User Selects Agent
```
User clicks: "Claude Code" in AionUi UI
```

### Step 2: AionUi Spawns Agent Process
```javascript
// For Claude Code, AionUi runs:
npx @zed-industries/claude-code-acp

// For Qwen Code, AionUi runs:
qwen --acp

// For Goose, AionUi runs:
goose acp
```

### Step 3: ACP Communication Established
```
┌─────────────────┐     stdio/stdout     ┌─────────────────┐
│   AionUi        │ ◄────────────────────► │   Claude Code   │
│   (Host/Client) │   JSON-RPC bidirectional │   (Agent)       │
└─────────────────┘                         └─────────────────┘
```

## For Claude Code Specifically

### What AionUi Does

```javascript
// From: src/agent/acp/AcpConnection.ts
async connectClaude(workingDir: string) {
  const spawnCommand = isWindows ? 'npx.cmd' : 'npx';
  const spawnArgs = ['@zed-industries/claude-code-acp'];

  this.child = spawn(spawnCommand, spawnArgs, {
    cwd: workingDir,
    stdio: ['pipe', 'pipe', 'pipe'],  // Bidirectional JSON-RPC
    env: cleanEnv,
    shell: isWindows,
  });
}
```

### What You Need to Have Installed

1. **Node.js** (for NPX)
2. **Claude Code ACP bridge** (auto-installed via NPX)
3. **Anthropic API key** in environment or settings

### Claude Code Package

AionUi uses the official Claude Code ACP bridge:
- **Package**: `@zed-industries/claude-code-acp`
- **Source**: Zed Industries (maintainer of Claude Code)
- **Installation**: Automatic via NPX

## Authentication Flow

### For Agents That Require Authentication

```
┌──────────┐     Select     ┌──────────┐     Check     ┌──────────┐
│   User   │ ─────────────► │  AionUi  │ ───────────► │  Config   │
│          │               │          │              │          │
└──────────┘               └──────────┘              └──────────┘
                                                           │
                                                           ▼
                                                    ┌──────────────────┐
                                                    │  Has API Key?   │
                                                    └──────────────────┘
                                                           │
                                        ┌──────────────────┴──────────────────┐
                                        │                                     │
                                   ▼                                     ▼
                            ┌──────────────┐                    ┌──────────────┐
                            │  Spawn with  │                    │  Show Auth   │
                            │  existing key│                    │  Prompt      │
                            └──────────────┘                    └──────────────┘
```

### Claude Code Authentication

**Sources for Claude API key** (in order of precedence):

1. **AionUi Settings** → Environment Variables
2. **`~/.claude/settings.json`** → Credentials stored by Claude Code CLI
3. **Environment variables**: `ANTHROPIC_API_KEY`

## AionUi WebUI Mode on Headless Server

### Setup Process

```bash
# 1. Start AionUi in WebUI mode
cd /home/admin/workspaces/AionUi
npm run webui:remote

# 2. Access via browser
http://your-server:3000
```

### What Happens When User Selects Claude Code

```
Browser (AionUi WebUI)          Server (AionUi Backend)          Agent Process
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│ User clicks      │             │                  │             │                  │
│ "Claude Code"    │ ─────────► │ Spawns process   │ ─────────► │ npx claude-code  │
│                  │             │                  │             │ --experimental-acp │
└──────────────────┘             └──────────────────┘             └──────────────────┘
```

## Configuration Locations

### AionUi Agent Settings

```
~/.config/AionUi/
├── aionui-config.txt          # Main config
├── .aionui-env                 # Environment variables
└── assistants/                 # Preset assistants
    ├── claude.md               # Claude preset
    ├── datachat.md            # datachat preset (your custom)
    └── ...
```

### Claude Code Credentials

```
~/.claude/
├── settings.json               # Claude Code settings
├── skills/                     # Skills (including datachat)
│   └── datachat → ../../workspaces/datachat/implementation/skills/datachat
└── ...
```

## Example: Using datachat with Claude Code in AionUi

### 1. User Opens AionUi WebUI
```
http://your-server:3000
```

### 2. User Selects "DataChat" Preset
- AionUi loads preset configuration from `~/.config/AionUi/assistants/datachat.md`
- Preset specifies `backend: claude` and `enabledSkills: ['datachat']`

### 3. User Types: "Analyze survey.sav"
- AionUi spawns Claude Code: `npx @zed-industries/claude-code-acp`
- Claude Code loads datachat skill from `~/.claude/skills/datachat/`
- Skill documentation provides analysis workflow
- Claude Code recognizes user request and calls LangGraph API
- LangGraph API (port 8123) processes the analysis

### 4. Results Displayed in AionUi
- Progress updates via ACP protocol
- Final results with file paths
- User can download/view outputs

## Troubleshooting

### Agent Not Starting

```bash
# Check if Node.js is installed
node --version

# Check if NPX works
npx --version

# Check for Claude ACP bridge
npx @zed-industries/claude-code-acp --help
```

### Authentication Issues

```bash
# Check Claude Code settings
cat ~/.claude/settings.json

# Set API key if needed
export ANTHROPIC_API_KEY=sk-...
```

### AionUi WebUI Not Accessible

```bash
# Check if WebUI is running
curl http://localhost:3000

# Check firewall
sudo ufw status
sudo ufw allow 3000/tcp
```

---

**Summary**: AionUi handles everything automatically. Just:
1. ✅ Install AionUi dependencies (Node.js, npm)
2. ✅ Have Claude Code ACP bridge available (via NPX)
3. ✅ Configure API keys
4. ✅ Start AionUi in WebUI mode
5. ✅ Select agent and start working
