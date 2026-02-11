# AionUi Migration Evaluation: LangGraph → Claude Code Skills

**Date**: 2026-02-09
**Evaluation**: Can datachat replace LangGraph with AionUi + Claude Code skills?

---

## Executive Summary

**Verdict**: ⚠️ **PARTIALLY FEASIBLE** with significant architectural changes and trade-offs.

| Aspect | Feasibility | Effort | Risk |
|--------|-------------|--------|------|
| Replace chat interface | ✅ High | Medium | Low |
| Convert nodes to skills | ⚠️ Medium | High | Medium |
| Maintain workflow orchestration | ❌ Low | Very High | High |
| Keep data processing logic | ✅ High | Low | Low |

---

## Current Architecture: LangGraph-based datachat

### Core Components

```
LangGraph StateGraph (22 nodes, 8 phases)
├── State Management
│   ├── WorkflowState (10 sub-states)
│   ├── TypedDict with reducers
│   └── SQLite checkpointer
├── Graph Orchestration
│   ├── Linear edges (sequential flow)
│   ├── Conditional edges (3 feedback loops)
│   └── Three-node pattern (Generate → Validate → Review)
└── 22 Processing Nodes
    ├── Phase 1: Extraction (Steps 1-3)
    ├── Phase 2: Recoding (Steps 4-8)
    ├── Phase 3: Indicators (Steps 9-11)
    ├── Phase 4: Tables (Steps 12-16)
    ├── Phase 5: Statistics (Steps 17-18)
    ├── Phase 6: Filtering (Steps 19-20)
    ├── Phase 7: PowerPoint (Step 21)
    └── Phase 8: HTML Dashboard (Step 22)
```

### Key Features of LangGraph Implementation

1. **State Management**: Complex nested state with 10 sub-states
2. **Checkpointing**: SQLite-based persistence for resumable workflows
3. **Conditional Routing**: Dynamic path selection based on validation results
4. **Human-in-the-Loop**: Three-node pattern for review/approval
5. **Retry Logic**: Automatic self-correction with iteration limits
6. **Traceability**: Full execution history and state snapshots

### Current Node Implementation

Each node:
- Accepts `WorkflowState` as input
- Returns dict with state updates
- Has structured error handling
- Includes tracing decorators
- Processes SPSS data, generates artifacts, validates results

---

## AionUi + Claude Code Capabilities

### What AionUi Provides

| Feature | Description | Relevance to datachat |
|---------|-------------|----------------------|
| **ACP Client** | Connects to Claude Code via Agent Client Protocol | ✅ Can use Claude Code for AI |
| **Skills System** | Markdown-based skill definitions with JS/Python scripts | ✅ Could encapsulate node logic |
| **WebUI Mode** | Browser-based interface, remote access | ✅ Replaces current UI |
| **MCP Integration** | Model Context Protocol for tool access | ⚠️ Different from current approach |
| **Multi-Model Support** | Gemini, Claude, OpenAI, local models | ✅ Flexibility |
| **No Workflow Engine** | No built-in state machine or orchestration | ❌ **Critical Gap** |

### AionUi Skills Pattern

```
skills/
├── docx/SKILL.md         # Word document operations
├── pdf/SKILL.md          # PDF processing
├── pptx/html2pptx.md     # PowerPoint generation
└── mermaid/SKILL.md      # Diagram generation
```

Each skill:
1. Markdown description with `name`, `description`, `license`
2. Trigger conditions (when Claude should use it)
3. Implementation scripts (JS/Python)
4. Dependencies and requirements

### AionUi Assistant Pattern

```
assistant/
├── social-job-publisher/
│   └── social-job-publisher.md    # Goals, intake, output, quality
├── game-3d/
│   └── game-3d.md
└── moltbook/
    └── moltbook.md
```

Each assistant:
1. Markdown-based definition
2. Goals and scope
3. Intake process (what to extract)
4. Output specifications
5. Quality guidelines

---

## Feasibility Analysis

### ✅ What CAN Be Migrated

| Component | Migration Approach | Effort |
|-----------|-------------------|--------|
| **Chat UI** | Use AionUi WebUI mode | Low |
| **SPSS Extraction** | Create `spss/SKILL.md` with pyreadstat | Medium |
| **PowerPoint Generation** | Use existing `pptx` skill | Low |
| **HTML Dashboard** | Create new skill or use templates | Medium |
| **Document Operations** | Use existing `docx`, `pdf` skills | Low |

### ⚠️ What Requires Adaptation

| Component | Challenge | Mitigation |
|-----------|-----------|------------|
| **State Management** | AionUi has no WorkflowState equivalent | Use file-based state or implement custom |
| **Checkpointing** | No built-in resume capability | Implement SQLite persistence separately |
| **Conditional Routing** | No graph-based routing | Implement in Claude Code with if/else logic |
| **Validation Logic** | Needs structured validation | Create validation skills with clear error formats |
| **Three-Node Pattern** | No built-in retry/review pattern | Implement via conversation flow design |

### ❌ What Would Be Lost

| Feature | Impact | Workaround |
|---------|--------|------------|
| **Visual Graph** | No LangGraph Studio visualization | Use AionUi's session history |
| **Automatic Retry** | Manual intervention needed | Claude Code must implement retry logic |
| **State Snapshots** | No built-in checkpoint inspection | Custom logging/state dump |
| **Edge Routing** | Conditional logic must be in prompts | More complex prompt engineering |

---

## Proposed Migration Strategy

### Option 1: Hybrid Approach (Recommended)

**Keep LangGraph backend, use AionUi as UI**

```
┌─────────────────┐     ACP      ┌─────────────────┐
│   AionUi WebUI  │ ◄────────────► │  Claude Code    │
│   (Chat UI)     │               │  (AI Agent)     │
└─────────────────┘               └────────┬────────┘
                                            │
                                            │ API Calls
                                            ▼
                                   ┌─────────────────┐
                                   │  LangGraph API  │
                                   │  (Current)      │
                                   └─────────────────┘
```

**Pros:**
- Preserves all workflow orchestration
- Minimal code changes
- Better UI experience
- AionUi just becomes a client

**Cons:**
- Still depends on LangGraph
- Two systems to maintain

### Option 2: Full Migration (High Risk)

**Replace LangGraph with Claude Code + Skills**

```
┌─────────────────┐     ACP      ┌─────────────────┐
│   AionUi WebUI  │ ◄────────────► │  Claude Code    │
│   (Chat UI)     │               │  + Skills       │
└─────────────────┘               └────────┬────────┘
                                            │
                                            │ Skill Execution
                                            ▼
                                   ┌─────────────────┐
                                   │  Python Scripts  │
                                   │  (Former nodes)  │
                                   └─────────────────┘
```

**Requirements:**
1. Create 10+ skills for each processing step
2. Implement state management in Claude Code
3. Build orchestration logic in prompts
4. Create custom checkpoint system

**Pros:**
- Single system
- No LangGraph dependency
- More flexible UI

**Cons:**
- Very high effort
- Loss of visual workflow
- Complex prompt engineering
- Higher risk of bugs

### Option 3: Minimal Integration

**Use AionUi only as alternative chat interface**

- Keep current LangGraph setup
- Add AionUi as another frontend option
- No migration of workflow logic

---

## Recommendations

### Short Term (0-3 months)

1. **Adopt Option 1 (Hybrid)**
   - Integrate AionUi as chat UI
   - Keep LangGraph backend
   - Use ACP to connect Claude Code

2. **Create datachat skill for AionUi**
   - Single skill that calls LangGraph API
   - Leverages existing infrastructure

### Long Term (3-6 months)

1. **Evaluate AionUi roadmap**
   - Check if workflow engine is planned
   - Monitor ACP protocol evolution

2. **Incremental skill migration**
   - Start with independent operations (SPSS extraction, PPTX)
   - Keep orchestration in LangGraph initially

3. **Build custom state management**
   - If full migration needed
   - SQLite-based checkpoint system

---

## Critical Considerations

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Loss of workflow control | High | High | Keep LangGraph for orchestration |
| State serialization issues | Medium | Medium | Use file-based state |
| Performance degradation | Low | Medium | Benchmark before migration |
| Skill discoverability | Medium | Low | Clear skill descriptions |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| User confusion from new interface | Medium | Low | Gradual rollout, training |
| Lost functionality during migration | High | High | Thorough testing checklist |
| Increased maintenance burden | Medium | Medium | Document new patterns |

---

## Effort Estimation

### Option 1: Hybrid (Recommended)

| Task | Effort |
|------|--------|
| AionUi WebUI setup | 2 days |
| ACP integration with Claude Code | 3 days |
| Create single datachat skill | 2 days |
| Testing and validation | 3 days |
| **Total** | **~2 weeks** |

### Option 2: Full Migration

| Task | Effort |
|------|--------|
| Create 10+ processing skills | 2-3 weeks |
| Implement state management | 1-2 weeks |
| Build checkpoint system | 1 week |
| Orchestration prompt engineering | 2-3 weeks |
| Testing and validation | 2 weeks |
| **Total** | **~2-3 months** |

---

## Conclusion

**Recommendation**: Proceed with **Option 1 (Hybrid Approach)**

This path:
- Provides immediate UI benefits
- Minimizes technical risk
- Preserves existing workflow logic
- Allows gradual evaluation of AionUi
- Keeps door open for future full migration

AionUi is an excellent chat interface but lacks the workflow orchestration capabilities that LangGraph provides. For a complex, multi-step data processing pipeline like datachat, maintaining LangGraph as the backend while using AionUi as the frontend is the most prudent approach.

---

## Next Steps

1. ✅ Set up AionUi WebUI mode on server
2. ✅ Configure ACP connection to Claude Code
3. ⏳ Create `datachat` skill that wraps LangGraph API
4. ⏳ Test integration with sample analysis
5. ⏳ Document usage patterns

---

**Evaluation by**: Claude (AI Assistant)
**Status**: Ready for review
