# Web Interface

This document describes the web interface for the Survey Analysis & Visualization Workflow using LangGraph's official Agent Chat UI.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Agent Chat UI](#2-agent-chat-ui)
3. [Installation](#3-installation)
4. [Configuration](#4-configuration)
5. [Usage](#5-usage)
6. [Features](#6-features)

---

## 1. Overview

The Survey Analysis & Visualization Workflow uses LangGraph's **Agent Chat UI** as its web interface. Agent Chat UI is an official, open-source Next.js application that provides a conversational interface for interacting with LangGraph agents.

### 1.1 Architecture

```
┌─────────────────────┐      ┌──────────────────────┐      ┌─────────────────────┐
│                     │      │                      │      │                     │
│   Agent Chat UI     │ ───► │  LangGraph Server    │ ───► │   Survey Workflow   │
│   (Next.js/React)   │ REST │  (Local/Cloud)       │      │   (LangGraph)       │
│                     │ API  │                      │      │                     │
└─────────────────────┘      └──────────────────────┘      └─────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Technology | Responsibility |
|-----------|------------|----------------|
| **Agent Chat UI** | Next.js, React | Web interface, chat UI, visualization |
| **LangGraph Server** | Python, LangGraph | Workflow execution, state management |
| **Survey Workflow** | LangGraph, PSPP | Survey analysis processing |

---

## 2. Agent Chat UI

### 2.1 What is Agent Chat UI?

Agent Chat UI is LangGraph's official web interface for interacting with agents. It provides:

| Feature | Description |
|---------|-------------|
| **Conversational Interface** | Chat-based interaction with your workflow |
| **Tool Visualization** | See what tools/steps are being executed |
| **Time-Travel Debugging** | Inspect and navigate through workflow states |
| **State Forking** | Branch workflow execution for exploration |
| **Real-Time Updates** | Stream results as they are generated |
| **Human-in-the-Loop Support** | Handle workflow interrupts and review points |

### 2.2 Repository

- **GitHub**: https://github.com/langchain-ai/agent-chat-ui
- **License**: Open-source
- **Framework**: Next.js (React)

---

## 3. Installation

### 3.1 Quick Start

```bash
# Option 1: Clone the repository
git clone https://github.com/langchain-ai/agent-chat-ui.git
cd agent-chat-ui

# Option 2: Create a new project
npx create-agent-chat-app --project-name datachat-ui
cd datachat-ui

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

### 3.2 Development Mode

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development server on http://localhost:3000 |
| `pnpm build` | Build for production |
| `pnpm start` | Start production server |
| `pnpm lint` | Run linting |

---

## 4. Configuration

### 4.1 Connect to Your Workflow

After starting Agent Chat UI, configure the connection:

| Setting | Description | Example |
|---------|-------------|---------|
| **Graph ID** | Name of your graph from `langgraph.json` | `survey_analysis` |
| **Server URL** | LangGraph server endpoint | `http://localhost:2024` |
| **API Key** | LangSmith API key (optional) | `lsv2_...` |

### 4.2 Configuration File

Create a `.env.local` file in the Agent Chat UI directory:

```bash
# LangGraph Server
NEXT_PUBLIC_LANGGRAPH_URL=http://localhost:2024

# Optional: LangSmith for deployed agents
NEXT_PUBLIC_LANGSMITH_API_KEY=lsv2_your_api_key_here
```

### 4.3 LangGraph Server Setup

For local development, start your LangGraph server:

```bash
# In your datachat project
cd /home/admin/workspaces/datachat

# Start LangGraph server (if using langgraph-cli)
langgraph dev

# Or use Python directly
python -m workflow.graph --server
```

---

## 5. Usage

### 5.1 Basic Workflow

1. **Start the LangGraph server** with your survey workflow
2. **Start Agent Chat UI** with `pnpm dev`
3. **Open** http://localhost:3000 in your browser
4. **Configure** connection to your workflow
5. **Upload** your `.sav` survey file
6. **Interact** with the workflow through chat

### 5.2 Chat Interface

```
┌─────────────────────────────────────────────────────────────┐
│  Survey Analysis Chat                          [Status]     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User: Please analyze customer_survey.sav                    │
│                                                              │
│  Assistant: I'll analyze your survey file. This will        │
│            involve:                                          │
│            1. Extracting and filtering variables             │
│            2. Generating recoding rules (your review)        │
│            3. Creating indicators (your review)              │
│            4. Building cross-tables (your review)            │
│            5. Statistical analysis                           │
│            6. Generating PowerPoint and dashboard            │
│                                                              │
│  [Step 1/22] Extracting SPSS file... ✓                      │
│  [Step 2/22] Transforming metadata... ✓                     │
│  [Step 3/22] Filtering variables... ✓                        │
│                                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                              │
│  🔔 Review Required: Recoding Rules                         │
│                                                              │
│  [View Rules] [Approve] [Reject with Feedback]              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Human Review in Chat

When the workflow reaches a review point, Agent Chat UI displays:

- **The artifact** to review (recoding rules, indicators, or table specs)
- **Validation results** (passed checks, errors, warnings)
- **Action buttons** for Approve or Reject

**Approve**: Click "Approve" to continue

**Reject**: Click "Reject" and provide feedback:
```
Please regroup satisfaction questions by top-2-box scoring
instead of individual categories.
```

### 5.4 Progress Tracking

The chat interface shows real-time progress:

| Stage | Steps | Status |
|-------|-------|--------|
| **Data Preparation** | 1-8 | ⏳ In progress |
| **Analysis** | 9-20 | Pending |
| **Reporting** | 21-22 | Pending |

---

## 6. Features

### 6.1 Tool Visualization

See exactly what the workflow is doing:

- **Current step** being executed
- **PSPP commands** being run
- **LLM prompts** and responses
- **Validation checks** and results

### 6.2 Time-Travel Debugging

Navigate through workflow history:

- **View past states** of the workflow
- **Inspect artifacts** at any point
- **Compare** different execution branches

### 6.3 State Forking

Explore alternative paths:

- **Branch** from any workflow state
- **Test different** recoding rules or indicators
- **Compare outputs** side by side

### 6.4 Streaming Updates

Real-time feedback as the workflow executes:

- **Step-by-step** progress updates
- **Live statistics** on completion
- **Immediate error** reporting

### 6.5 File Upload

Upload survey files directly through the interface:

- **Drag and drop** `.sav` files
- **Validate** file format before processing
- **Preview** metadata and variables

---

## Related Documents

- **[Product Features and Usage](./user-guide.md)** - Product introduction for end users
- **[Configuration](./configuration.md)** - Configuration options and settings
- **[System Architecture](./system-architecture.md)** - System components and architecture
- **[Deployment](./deployment.md)** - Installation and environment setup
