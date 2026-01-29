# Agno Delphi Collaboration Guide

## Introduction

This guide demonstrates how to use **Agno** (Python AI agent framework) to facilitate team discussions and collaboration using the **Delphi Method** approach. The Delphi Method is a structured communication technique where multiple experts (AI agents in this case) independently evaluate a topic, discuss findings, and reach consensus through a coordinator.

---

## Delphi Method Overview

The Delphi Method implemented with Agno follows a three-round process:

```
ROUND 1: Independent Evaluation
├── Evaluator 1 (Model: Provider A)
├── Evaluator 2 (Model: Provider B)
├── Evaluator 3 (Model: Provider C)
└── ... Each evaluates independently without seeing others' work

ROUND 2: Discussion Phase
├── Each evaluator reviews others' findings
├── Identifies areas of agreement/disagreement
└── Revises their position based on new insights

ROUND 3: Consensus Synthesis
└── Coordinator synthesizes all inputs into final verdict
```

---

## The Script

### Main Script: `team_evaluator.py`

```python
#!/usr/bin/env python3
"""
Agno Delphi Panel for Collaborative Evaluation

This script implements the Delphi Method with multiple evaluators:
1. Round 1: Independent evaluation by each panel member
2. Round 2: Discussion - members review and discuss each other's findings
3. Round 3: Coordinator synthesizes consensus and final verdict

Usage:
    python team_evaluator.py

Output:
    - Console summary with health status
    - Full report at docs/reports/evaluation-{timestamp}.md
"""

import os
from datetime import datetime
from pathlib import Path
from textwrap import dedent

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai.like import OpenAILike

# =============================================================================
# Load Configuration from .env
# =============================================================================

SKILL_DIR = Path(__file__).parent.parent
load_dotenv(dotenv_path=SKILL_DIR / ".env", override=True)

# =============================================================================
# Configuration
# =============================================================================

# Input/Output paths
INPUT_PATH = Path(os.getenv("INPUT_PATH", "docs/input/document-to-evaluate.md"))
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "docs/reports"))

# Debug directory for saving prompts
DEBUG_DIR = Path(os.getenv("DEBUG_DIR", "docs/reports/debug"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"

# Coordinator provider (kimi, deepseek, zhipu, etc.)
COORDINATOR_PROVIDER = os.getenv("COORDINATOR_PROVIDER", "kimi")

# =============================================================================
# Debug Logging Functions
# =============================================================================

def save_debug_prompt(round_name: str, agent_name: str, prompt: str, response: str = None) -> Path:
    """Save prompt and optionally response to debug directory."""
    if not DEBUG_MODE:
        return None

    DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = agent_name.replace(" ", "_").lower()
    filename = f"{timestamp}_{round_name}_{safe_name}.md"
    debug_path = DEBUG_DIR / filename

    content = f"""# Debug: {round_name} - {agent_name}

**Timestamp**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Prompt Length**: {len(prompt):,} characters

---

## PROMPT SENT TO AGENT

{prompt}

---

## RESPONSE FROM AGENT

{response if response else "(Response will be added after agent completes)"}
"""

    debug_path.write_text(content)
    return debug_path


def log_debug_info(message: str, data: dict = None):
    """Print debug information to console."""
    if not DEBUG_MODE:
        return

    print(f"\n{'🔍' if data else '📝'} DEBUG: {message}")
    if data:
        for key, value in data.items():
            if isinstance(value, str):
                print(f"  {key}: {value[:100]}{'...' if len(value) > 100 else ''}")
            else:
                print(f"  {key}: {value}")
    print()

# =============================================================================
# Build Evaluator Models from Provider Configuration
# =============================================================================

def get_evaluator_configs() -> list:
    """Build evaluator configurations from provider environment variables."""
    evaluators = []

    # Kimi (Moonshot AI)
    kimi_model = os.getenv("KIMI_MODEL")
    if kimi_model:
        evaluators.append({
            "name": "Kimi",
            "model_id": kimi_model,
            "api_key": os.getenv("KIMI_API_KEY"),
            "base_url": os.getenv("KIMI_BASE_URL"),
        })

    # DeepSeek
    deepseek_model = os.getenv("DEEPSEEK_MODEL")
    if deepseek_model:
        evaluators.append({
            "name": "DeepSeek",
            "model_id": deepseek_model,
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "base_url": os.getenv("DEEPSEEK_BASE_URL"),
        })

    # Zhipu GLM
    zhipu_model = os.getenv("ZHIPU_MODEL")
    if zhipu_model:
        evaluators.append({
            "name": "Zhipu GLM",
            "model_id": zhipu_model,
            "api_key": os.getenv("ZHIPU_API_KEY"),
            "base_url": os.getenv("ZHIPU_BASE_URL"),
        })

    return evaluators


EVALUATOR_CONFIGS = get_evaluator_configs()

# =============================================================================
# Evaluator Agent Role (Same for all panel members)
# =============================================================================

EVALUATOR_ROLE = dedent("""\
    You are an Expert Evaluator on a Delphi Panel.

    Your responsibility is to perform a COMPREHENSIVE evaluation of the
    provided content based on the evaluation criteria.

    **Evaluation Approach**:
    1. Review the content systematically
    2. Identify strengths and weaknesses
    3. Provide specific, actionable feedback
    4. Support your assessments with evidence

    **Output Format**:
    ### Issues Found
    List each issue with:
    - Category/Topic
    - Issue description
    - Severity (CRITICAL/HIGH/MEDIUM/LOW)
    - Evidence (specific reference)
    - Recommendation

    ### Positive Findings
    What aspects are well-designed or executed?

    ### Overall Assessment
    Based on your findings, classify as: EXCELLENT / GOOD / NEEDS IMPROVEMENT / CRITICAL

    ### Priority Recommendations
    Top 3-5 most important actions needed.
""")

# =============================================================================
# Delphi Panel Members
# =============================================================================

evaluators = []
for config in EVALUATOR_CONFIGS:
    evaluator = Agent(
        name=f"Evaluator_{config['name']}",
        role=EVALUATOR_ROLE,
        model=OpenAILike(
            id=config['model_id'],
            api_key=config['api_key'],
            base_url=config['base_url'],
        ),
        instructions=[
            "Evaluate comprehensively across all criteria.",
            "Be thorough and systematic.",
            "Always cite specific evidence for findings.",
            "Provide specific, actionable recommendations.",
        ],
        markdown=True,
    )
    evaluators.append(evaluator)

# =============================================================================
# Coordinator Agent (Synthesizes final consensus)
# =============================================================================

def get_coordinator_config():
    """Get coordinator configuration based on COORDINATOR_PROVIDER."""
    provider = COORDINATOR_PROVIDER.lower()

    if provider == "kimi":
        return {
            "model_id": os.getenv("KIMI_MODEL", "kimi-k2-turbo-preview"),
            "api_key": os.getenv("KIMI_API_KEY"),
            "base_url": os.getenv("KIMI_BASE_URL"),
        }
    elif provider == "deepseek":
        return {
            "model_id": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "base_url": os.getenv("DEEPSEEK_BASE_URL"),
        }
    elif provider == "zhipu":
        return {
            "model_id": os.getenv("ZHIPU_MODEL", "glm-4.7"),
            "api_key": os.getenv("ZHIPU_API_KEY"),
            "base_url": os.getenv("ZHIPU_BASE_URL"),
        }
    else:
        # Default to Kimi
        return {
            "model_id": os.getenv("KIMI_MODEL", "kimi-k2-turbo-preview"),
            "api_key": os.getenv("KIMI_API_KEY"),
            "base_url": os.getenv("KIMI_BASE_URL"),
        }


COORDINATOR_CONFIG = get_coordinator_config()

coordinator = Agent(
    name="Coordinator",
    role=dedent("""\
        You are the Delphi Panel Coordinator.

        Your responsibility is to:
        1. Review all independent evaluations from panel members
        2. Identify areas of agreement and disagreement
        3. Synthesize findings into a consensus report
        4. Generate actionable recommendations
        5. Provide final assessment

        **Output Structure**:

        ## Executive Summary
        | Metric | Value |
        |--------|-------|
        | Status | EXCELLENT / GOOD / NEEDS IMPROVEMENT / CRITICAL |
        | Critical Issues | N |
        | High Issues | N |
        | Medium Issues | N |
        | Panel Agreement | % (agreement level among evaluators) |

        ## Critical Issues
        ### [Category] - [Issue Name]
        **Severity**: CRITICAL
        **Evidence**: [Specific reference]
        **Panel Agreement**: [X/Y evaluators identified this issue]
        **Recommendation**: [Specific action]

        ## High Issues
        [Same format]

        ## Medium/Low Issues
        [Same format]

        ## Consensus Recommendations
        Prioritized action items based on panel agreement.

        ## Strengths
        What the panel agreed is well-done.

        ## Disagreements
        Issues where evaluators had different opinions (if any).

        ## Final Verdict
        [Overall assessment with rationale]

        **Guidelines**:
        - Prioritize issues mentioned by multiple evaluators
        - Note areas of disagreement for further review
        - Provide clear, actionable next steps
        - Be specific about recommendations
    """),
    model=OpenAILike(
        id=COORDINATOR_CONFIG['model_id'],
        api_key=COORDINATOR_CONFIG['api_key'],
        base_url=COORDINATOR_CONFIG['base_url'],
    ),
    instructions=[
        "Synthesize findings from all panel members objectively.",
        "Highlight areas of agreement and disagreement.",
        "Prioritize issues identified by multiple evaluators.",
        "Provide clear final assessment.",
        "Include specific recommendations for prioritized issues.",
    ],
    markdown=True,
)

# =============================================================================
# Main Execution
# =============================================================================

def load_input_content() -> str:
    """Load the input content file."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}\n"
            "Please ensure the input file exists."
        )
    return INPUT_PATH.read_text()


def create_evaluation_task(content: str) -> str:
    """Create the evaluation task for Round 1."""
    task = dedent(f"""\
        # Delphi Panel Evaluation - Round 1: Independent Assessment

        You are evaluating content for quality and completeness.

        **Source File**: {INPUT_PATH}
        **Content Length**: {len(content):,} characters

        ## Your Task

        Perform a comprehensive evaluation across ALL relevant dimensions.

        ## Content to Evaluate

        {content}

        ## Required Output

        Provide your independent assessment in the format specified in your role.
        Work systematically through the entire content. Be thorough.
    """)

    return task


def create_discussion_task(evaluations: list, current_index: int) -> str:
    """Create discussion task for an evaluator to review others' findings."""
    other_evaluations = []
    for i, eval_result in enumerate(evaluations):
        if i != current_index:
            config = EVALUATOR_CONFIGS[i]
            other_evaluations.append(f"## {config['name']} Assessment\n\n{eval_result}\n")

    other_findings = "\n".join(other_evaluations)
    current_config = EVALUATOR_CONFIGS[current_index]

    task = dedent(f"""\
        # Delphi Panel - Round 2: Discussion Phase

        You are {current_config['name']} (Evaluator {current_index + 1}). Below are the assessments from your fellow panel members.

        ## Other Evaluators' Findings

        {other_findings}

        ## Your Task

        1. **Review**: Read through your colleagues' assessments
        2. **Compare**: How do their findings compare to yours?
        3. **Identify**:
           - Issues you agree on (multiple evaluators found)
           - Issues unique to your assessment
           - Issues where you disagree

        4. **Update**: Based on this discussion, provide your:
           - **Revised position** on each issue (confirm or revise)
           - **New insights** gained from reviewing others' work
           - **Final assessment** (EXCELLENT / GOOD / NEEDS IMPROVEMENT / CRITICAL)

        ## Required Output

        ### Agreement Analysis
        - Issues with consensus (2+ evaluators agree)
        - Issues only you found
        - Issues where you disagree with others

        ### Revised Assessment
        Your final position after discussion.

        Be objective - updating your position based on evidence is a strength.
    """)

    return task


def create_synthesis_task(evaluations: list, discussions: list) -> str:
    """Create synthesis task for the coordinator."""
    all_inputs = []
    for i, config in enumerate(EVALUATOR_CONFIGS):
        all_inputs.append(dedent(f"""\
            ## {config['name']} (Evaluator {i+1})

            ### Initial Assessment
            {evaluations[i]}

            ### Discussion Position
            {discussions[i]}
        """))

    all_evaluator_input = "\n".join(all_inputs)

    task = dedent(f"""\
        # Delphi Panel - Round 3: Consensus Synthesis

        You are the Coordinator. Below are all evaluator assessments and discussions.

        ## Complete Panel Input

        {all_evaluator_input}

        ## Your Task

        Synthesize the panel's work into a final consensus report as specified in your role.
        Be fair to all evaluators while providing clear, actionable guidance.
    """)

    return task


def save_report(coordinator_output: str) -> Path:
    """Save the evaluation report to disk."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = REPORTS_DIR / f"evaluation-{timestamp}.md"

    header = dedent(f"""\
        # Delphi Panel Evaluation Report

        **Source**: {INPUT_PATH}
        **Evaluated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        **Method**: Delphi Panel ({len(EVALUATOR_CONFIGS)} evaluators)
        **Process**: Independent evaluation → Discussion → Consensus

        ---

    """)

    report_content = header + coordinator_output
    report_path.write_text(report_content)
    return report_path


def print_console_summary(coordinator_output: str, rounds_log: list) -> None:
    """Print console summary."""
    import re

    critical_match = re.search(r'Critical\s+Issues\s*\|\s*(\d+)', coordinator_output, re.IGNORECASE)
    high_match = re.search(r'High\s+Issues\s*\|\s*(\d+)', coordinator_output, re.IGNORECASE)
    medium_match = re.search(r'Medium\s+Issues\s*\|\s*(\d+)', coordinator_output, re.IGNORECASE)
    status_match = re.search(r'Status\s*\|\s*(EXCELLENT|GOOD|NEEDS\s+IMPROVEMENT|CRITICAL)', coordinator_output, re.IGNORECASE)
    agreement_match = re.search(r'Agreement\s*\|\s*(\d+)%', coordinator_output, re.IGNORECASE)

    critical = int(critical_match.group(1)) if critical_match else 0
    high = int(high_match.group(1)) if high_match else 0
    medium = int(medium_match.group(1)) if medium_match else 0
    status = status_match.group(1) if status_match else "UNKNOWN"
    agreement = int(agreement_match.group(1)) if agreement_match else 0

    total_issues = critical + high + medium

    print("\n" + "=" * 60)
    print("DELPHI PANEL EVALUATION COMPLETE")
    print("=" * 60)
    print(f"\nPanel Size:      {len(EVALUATOR_CONFIGS)} evaluators")
    print(f"Panel Agreement: {agreement}%")
    print(f"\nStatus:          {status}")
    print(f"Issues Found:    {total_issues} total")
    print(f"                 {critical} critical, {high} high, {medium} medium")

    print(f"\nRounds Completed:")
    for i, log in enumerate(rounds_log, 1):
        print(f"  {i}. {log}")

    print(f"\nFull report:     {REPORTS_DIR}/evaluation-*.md")
    print("=" * 60 + "\n")


def main():
    """Main execution function."""
    # Check if evaluators are configured
    if not EVALUATOR_CONFIGS:
        print("\n" + "=" * 60)
        print("ERROR: No evaluators configured")
        print("=" * 60)
        print("\nPlease configure at least one model provider in .env:")
        print("  - KIMI_MODEL, KIMI_API_KEY, KIMI_BASE_URL")
        print("  - DEEPSEEK_MODEL, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL")
        print("  - ZHIPU_MODEL, ZHIPU_API_KEY, ZHIPU_BASE_URL")
        print("=" * 60 + "\n")
        return

    print("=" * 60)
    print(f"Delphi Panel Evaluation ({len(evaluators)} Evaluators)")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"\nEvaluators:")
    for config in EVALUATOR_CONFIGS:
        print(f"  - {config['name']}: {config['model_id']}")
        print(f"    → {config['base_url']}")
    print(f"\nCoordinator:")
    print(f"  - {COORDINATOR_PROVIDER.capitalize()}: {COORDINATOR_CONFIG['model_id']}")
    print(f"    → {COORDINATOR_CONFIG['base_url']}")
    print(f"\nSource:")
    print(f"    {INPUT_PATH}")

    # Load input content
    print(f"\nLoading input from: {INPUT_PATH}")
    content = load_input_content()
    print(f"Loaded {len(content.splitlines()):,} lines")

    # Create evaluation task
    task = create_evaluation_task(content)

    rounds_log = []
    actual_panel_size = len(evaluators)

    # ========================================================================
    # ROUND 1: Independent Evaluation
    # ========================================================================
    print("\n" + "-" * 60)
    print("ROUND 1: Independent Evaluation")
    print("-" * 60)

    log_debug_info("Starting Round 1", {
        "Evaluators": actual_panel_size,
        "Task length": f"{len(task):,} characters",
    })

    independent_evaluations = []
    for i, evaluator in enumerate(evaluators, 1):
        config = EVALUATOR_CONFIGS[i - 1]
        print(f"\n{config['name']} evaluating...")

        # Save debug prompt for Round 1
        debug_path = save_debug_prompt("round1", config['name'], task)

        response = evaluator.run(task)
        independent_evaluations.append(response.content)

        # Update debug file with response
        if debug_path and DEBUG_MODE:
            file_content = debug_path.read_text()
            file_content = file_content.replace("(Response will be added after agent completes)", response.content)
            debug_path.write_text(file_content)
            print(f"  ✓ {config['name']} complete (debug: {debug_path.name})")
        else:
            print(f"  ✓ {config['name']} complete")

    rounds_log.append(f"Independent evaluation ({actual_panel_size} assessors)")

    # ========================================================================
    # ROUND 2: Discussion Phase
    # ========================================================================
    print("\n" + "-" * 60)
    print("ROUND 2: Discussion Phase")
    print("-" * 60)

    log_debug_info("Starting Round 2", {
        "Each evaluator sees": "Other evaluators' Round 1 findings",
    })

    discussion_positions = []
    for i, evaluator in enumerate(evaluators, 1):
        config = EVALUATOR_CONFIGS[i - 1]
        print(f"\n{config['name']} reviewing colleagues' findings...")
        discussion_task = create_discussion_task(independent_evaluations, i - 1)

        # Save debug prompt for Round 2
        debug_path = save_debug_prompt("round2", config['name'], discussion_task)

        response = evaluator.run(discussion_task)
        discussion_positions.append(response.content)

        # Update debug file with response
        if debug_path and DEBUG_MODE:
            file_content = debug_path.read_text()
            file_content = file_content.replace("(Response will be added after agent completes)", response.content)
            debug_path.write_text(file_content)
            print(f"  ✓ {config['name']} discussion complete (debug: {debug_path.name})")
        else:
            print(f"  ✓ {config['name']} discussion complete")

    rounds_log.append("Discussion and position revision")

    # ========================================================================
    # ROUND 3: Consensus Synthesis
    # ========================================================================
    print("\n" + "-" * 60)
    print("ROUND 3: Consensus Synthesis")
    print("-" * 60)

    print(f"\n{COORDINATOR_PROVIDER.capitalize()} synthesizing panel findings...")
    synthesis_task = create_synthesis_task(independent_evaluations, discussion_positions)

    # Save debug prompt for Round 3
    debug_path = save_debug_prompt("round3", COORDINATOR_PROVIDER.capitalize(), synthesis_task)

    coordinator_response = coordinator.run(synthesis_task)

    # Update debug file with response
    if debug_path and DEBUG_MODE:
        file_content = debug_path.read_text()
        file_content = file_content.replace("(Response will be added after agent completes)", coordinator_response.content)
        debug_path.write_text(file_content)
        print(f"  ✓ Coordinator complete (debug: {debug_path.name})")

    rounds_log.append("Consensus synthesis by coordinator")

    # Save report
    report_path = save_report(coordinator_response.content)
    print(f"\n✓ Report saved to: {report_path}")

    if DEBUG_MODE:
        print(f"\n📁 Debug prompts saved to: {DEBUG_DIR}/")

    # Print summary
    print_console_summary(coordinator_response.content, rounds_log)


if __name__ == "__main__":
    main()
```

---

## Environment Configuration

### `.env` File

Create a `.env` file in your project directory:

```bash
# =============================================================================
# API Keys (Required)
# =============================================================================

# Kimi (Moonshot AI)
KIMI_API_KEY=your_kimi_api_key_here
KIMI_BASE_URL=https://api.moonshot.cn/v1
KIMI_MODEL=kimi-k2-turbo-preview

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Zhipu GLM
ZHIPU_API_KEY=your_zhipu_api_key_here
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4
ZHIPU_MODEL=glm-4.7

# =============================================================================
# Delphi Panel Configuration
# =============================================================================

# Coordinator provider: kimi, deepseek, or zhipu
COORDINATOR_PROVIDER=kimi

# Input/Output paths
INPUT_PATH=docs/input/document-to-evaluate.md
REPORTS_DIR=docs/reports

# =============================================================================
# Debug Mode (Optional)
# =============================================================================

# Enable/disable debug prompt saving (true/false)
DEBUG_MODE=true

# Directory for saving debug prompts
DEBUG_DIR=docs/reports/debug
```

---

## Debug Mode

The script includes built-in debug mode that saves all prompts and responses to disk for inspection.

### Enabling Debug Mode

```bash
# In .env file
DEBUG_MODE=true
DEBUG_DIR=docs/reports/debug
```

### Debug Output Format

For each round and evaluator, a markdown file is created:

```markdown
# Debug: round1 - Kimi

**Timestamp**: 2026-01-26 14:30:45
**Prompt Length**: 15,234 characters

---

## PROMPT SENT TO AGENT

[Full prompt content here...]

---

## RESPONSE FROM AGENT

[Full agent response here...]
```

### Debug File Naming Convention

```
{timestamp}_{round}_{agent_name}.md

Examples:
- 20260126-143045_round1_kimi.md
- 20260126-143102_round1_deepseek.md
- 20260126-143201_round2_kimi.md
- 20260126-143510_round3_coordinator.md
```

---

## Installation

### 1. Install Dependencies

```bash
pip install python-dotenv agno
```

Or create a `requirements.txt`:

```txt
python-dotenv>=1.0.0
agno>=0.1.0
```

Then install:

```bash
pip install -r requirements.txt
```

---

## Usage Examples

### Example 1: Document Evaluation

```bash
# Set input path in .env
INPUT_PATH=docs/design/architecture-decision.md

# Run evaluation
python team_evaluator.py
```

### Example 2: Code Review

```bash
# Set input path to code file
INPUT_PATH=src/module/implementation.py

# Run evaluation
python team_evaluator.py
```

### Example 3: Custom Evaluation Criteria

Modify the `EVALUATOR_ROLE` variable to define custom evaluation criteria:

```python
EVALUATOR_ROLE = dedent("""\
    You are a Security Review Evaluator.

    **Evaluation Dimensions**:
    1. SQL Injection vulnerabilities
    2. XSS risks
    3. Authentication/Authorization
    4. Input validation
    5. Error handling (information disclosure)
    ...
""")
```

---

## Adaptation Guide

### Customizing for Different Use Cases

#### 1. Change Input Format

Modify `load_input_content()` to accept different input sources:

```python
def load_input_content() -> str:
    """Load content from URL, database, or API."""
    import requests

    url = os.getenv("INPUT_URL")
    response = requests.get(url)
    return response.text
```

#### 2. Change Evaluation Criteria

Customize the `EVALUATOR_ROLE` to match your domain:

```python
# For UX evaluation
EVALUATOR_ROLE = "You are a UX evaluator..."

# For security evaluation
EVALUATOR_ROLE = "You are a security auditor..."

# For performance evaluation
EVALUATOR_ROLE = "You are a performance analyst..."
```

#### 3. Add More Evaluators

Add more providers in `get_evaluator_configs()`:

```python
# Add Anthropic Claude
anthropic_model = os.getenv("ANTHROPIC_MODEL")
if anthropic_model:
    evaluators.append({
        "name": "Claude",
        "model_id": anthropic_model,
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "base_url": os.getenv("ANTHROPIC_BASE_URL"),
    })
```

#### 4. Modify Output Format

Customize the coordinator role to produce different outputs:

```python
# JSON output instead of markdown
coordinator = Agent(
    role="Output results in JSON format...",
    ...
)

# HTML report
coordinator = Agent(
    role="Output results as HTML report...",
    ...
)
```

---

## Key Concepts

### 1. Independent Evaluation (Round 1)

Each evaluator works independently without seeing others' work. This prevents bias and ensures diverse perspectives.

### 2. Discussion Phase (Round 2)

Evaluators review each other's findings and revise their positions. This allows:
- Identification of consensus issues
- Discovery of unique findings
- Recognition of disagreements

### 3. Consensus Synthesis (Round 3)

The coordinator synthesizes all inputs into:
- Executive summary
- Prioritized issues
- Actionable recommendations
- Final verdict

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `No evaluators configured` | Add at least one provider's API keys to `.env` |
| `401 Unauthorized` | Check API key validity |
| `File not found` | Verify `INPUT_PATH` in `.env` points to existing file |
| `Module not found` | Run `pip install -r requirements.txt` |

---

## Advanced: Debug Mode Script

For standalone debugging, you can create a separate debug script:

```python
#!/usr/bin/env python3
"""
Debug mode runner for Delphi Panel evaluation.
Saves all prompts and responses for detailed inspection.
"""

import os
from pathlib import Path

# Force debug mode ON
os.environ["DEBUG_MODE"] = "true"

# Import and run the main script
from team_evaluator import main

if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING IN DEBUG MODE")
    print("=" * 60)
    print("All prompts will be saved to docs/reports/debug/\n")
    main()
```

Save this as `team_evaluator_debug.py` and run:

```bash
python team_evaluator_debug.py
```

---

## References

- **Agno Documentation**: https://github.com/agno-ai/agno
- **Delphi Method**: A forecasting method based on the results of questionnaires sent to a panel of experts
- **OpenAI-Compatible APIs**: Most modern LLM providers support the OpenAI API format
