#!/usr/bin/env python3
"""
Agent Delegation and Audit Script

Delegates a task to a Worker Agent, then audits the result with an Auditor Agent.

Best Practice: Always use --output to save results to file.
This keeps terminal output concise and allows detailed review later.

Usage:
    python delegate_and_audit.py --task "Your task" --output results.json
"""

import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add project root to path for imports
# The script is at: .claude/skills/agent-delegation-auditor/scripts/delegate_and_audit.py
# Project root is 4 levels up from the script
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent.parent.parent  # Go up to project root (dataflow/)
sys.path.insert(0, str(project_root))

try:
    from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
    from claude_agent_sdk import AssistantMessage, ResultMessage, SystemMessage, TextBlock, ToolUseBlock, ToolResultBlock
except ImportError:
    print("Error: claude_agent_sdk not installed. Install with: pip install claude-agent-sdk")
    sys.exit(1)


# =============================================================================
# Task Document Helpers
# =============================================================================

def create_task_document(
    task_type: str,
    objective: str,
    context: str = "",
    requirements: list[str] | None = None,
    deliverables: list[str] | None = None,
    constraints: list[str] | None = None,
    success_criteria: list[str] | None = None,
    additional_context: str = ""
) -> str:
    """
    Create a structured task document from parameters.

    This helper function allows programmatic creation of well-structured task documents.

    Args:
        task_type: Type of task (Code, Analysis, Writing, Research, Other)
        objective: Clear statement of what needs to be accomplished
        context: Relevant background information
        requirements: List of specific requirements
        deliverables: List of expected deliverables
        constraints: List of constraints/limitations
        success_criteria: List of success criteria
        additional_context: Any other relevant information

    Returns:
        Formatted task document as string
    """
    sections = []

    sections.append(f"# Task Document\n")
    sections.append(f"## Task Type\n{task_type}\n")

    if objective:
        sections.append(f"## Objective\n{objective}\n")

    if context:
        sections.append(f"## Context\n{context}\n")

    if requirements:
        sections.append("## Requirements")
        for i, req in enumerate(requirements, 1):
            sections.append(f"{i}. {req}")
        sections.append("")

    if deliverables:
        sections.append("## Deliverables")
        for item in deliverables:
            sections.append(f"- {item}")
        sections.append("")

    if constraints:
        sections.append("## Constraints")
        for item in constraints:
            sections.append(f"- {item}")
        sections.append("")

    if success_criteria:
        sections.append("## Success Criteria")
        for item in success_criteria:
            sections.append(f"- {item}")
        sections.append("")

    if additional_context:
        sections.append(f"## Additional Context\n{additional_context}\n")

    return "\n".join(sections)


def create_minimal_task(task: str, context: str, requirements: list[str]) -> str:
    """
    Create a minimal task document for simple tasks.

    Args:
        task: One-line task description
        context: Brief background
        requirements: List of key requirements

    Returns:
        Formatted minimal task document
    """
    lines = [
        "## Task",
        task,
        "",
        "## Context",
        context,
        "",
        "## Requirements"
    ]
    for i, req in enumerate(requirements, 1):
        lines.append(f"{i}. {req}")

    return "\n".join(lines)


# Default System Prompts
DEFAULT_WORKER_SYSTEM_PROMPT = """You are a Task Worker Agent. Your role is to:

1. **Execute the assigned task** thoroughly and accurately
2. **Follow the user's instructions** precisely
3. **Provide detailed results** in a clear, structured format
4. **Be honest about limitations** - if you cannot complete the task, explain why

## Output Format

Provide your results in the following structure:

```
## Task Summary
[Brief description of what you did]

## Results
[Your main results here]

## Steps Taken
[Step-by-step explanation of your approach]

## Notes
[Any additional context, assumptions, or limitations]
```

## Important Guidelines

- Be thorough but concise
- Use markdown formatting for readability
- If you need to make assumptions, state them clearly
- If you encounter issues, describe them and suggest solutions
"""

DEFAULT_AUDITOR_SYSTEM_PROMPT = """You are a Result Auditor Agent. Your role is to:

1. **Review the worker agent's results** for accuracy, completeness, and quality
2. **Identify any issues** such as:
   - Factual errors or incorrect information
   - Missing requirements or incomplete work
   - Quality issues (poor structure, unclear explanations)
   - Assumptions that may not be valid
3. **Provide actionable feedback** to improve the results
4. **Rate the overall quality** of the work (1-10 scale)

## Verdict Options
- "PASS": Work meets quality standards, ready to use
- "FAIL": Work has critical issues that prevent acceptance
- "NEEDS_REVISION": Work has issues that should be addressed
- "APPROVED": Work is approved for use with minor notes
- "REJECTED": Work must be completely redone

## Rating Scale
- 1-3: Poor quality, major issues
- 4-6: Fair quality, significant issues
- 7-8: Good quality, minor issues
- 9-10: Excellent quality, ready for production

## CRITICAL: Output Format (You MUST Use Write Tool to Create Two Files)

You MUST use the **Write tool** to create two files after completing your audit.

IMPORTANT: Write files to the OUTPUT_DIR specified in the audit request.

### File 1: {OUTPUT_DIR}/audit_status.txt
Use the Write tool to create a file named exactly "audit_status.txt" in the OUTPUT_DIR with this content:
```
AUDIT_VERDICT=PASS
AUDIT_RATING=8
```

Use ONLY these verdict values: PASS, FAIL, NEEDS_REVISION, APPROVED, REJECTED
Rating must be an integer from 1 to 10.

### File 2: {OUTPUT_DIR}/audit_report_iteration_N_task_TASK_ID.md
Use the Write tool to create a detailed markdown report in the OUTPUT_DIR with your full analysis.

AFTER using the Write tool for BOTH files, you MUST say "Files written: audit_status.txt and audit_report_iteration_N_task_TASK_ID.md" to confirm completion.

IMPORTANT:
- Write ALL files to the OUTPUT_DIR specified in the audit request
- Replace N with the iteration number
- Replace TASK_ID with the task ID provided in the request
- You must ACTUALLY use the Write tool - do not just describe what you would write
- Do not say your response is complete until you have used the Write tool for BOTH files

## Important Guidelines

- Be objective and fair in your assessment
- Provide specific, actionable feedback
- Rate based on: accuracy, completeness, quality, and adherence to requirements
- If the work is excellent, acknowledge it
- If the work is inadequate, clearly explain what needs to be fixed
- ALWAYS write both files before finishing
"""

# Constants for file-based auditor output
AUDIT_STATUS_FILE = "audit_status.txt"
AUDIT_REPORT_PREFIX = "audit_report_iteration_"

# Output directory for audit reports and delegation results
OUTPUT_DIR_BASE = project_root / "temp" / "tasks" / "agent-delegation-auditor"


def get_output_dir(date_str: str | None = None) -> Path:
    """Get or create the output directory for this run.

    Args:
        date_str: Optional date string (YYYYMMDD format). If None, uses today's date.

    Returns:
        Path to the output directory
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")

    output_dir = OUTPUT_DIR_BASE / date_str
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_task_id() -> str:
    """Generate a short unique task ID (8 characters)."""
    return str(uuid.uuid4())[:8]


async def create_agent(
    system_prompt: str,
    tools: list[str] | None = None,
    permission_mode: str = "bypassPermissions",
    output_format: dict[str, Any] | None = None,
    model: str | None = None
) -> ClaudeSDKClient:
    """Create a Claude SDK agent with specified configuration."""
    # Temporarily override ANTHROPIC_MODEL environment variable if model is specified
    original_model = os.environ.get("ANTHROPIC_MODEL")
    if model:
        os.environ["ANTHROPIC_MODEL"] = model

    try:
        options = ClaudeAgentOptions(
            cwd=str(Path.cwd()),
            setting_sources=["project"],
            system_prompt=system_prompt,
            allowed_tools=tools or [],
            permission_mode=permission_mode,
            output_format=output_format,
        )

        return ClaudeSDKClient(options=options)
    finally:
        # Restore original model
        if model and original_model is not None:
            os.environ["ANTHROPIC_MODEL"] = original_model
        elif model and original_model is None:
            os.environ.pop("ANTHROPIC_MODEL", None)


def strip_markdown_code_blocks(text: str) -> str:
    """Strip markdown code blocks from text to extract raw JSON.

    Handles formats like:
    ```json
    {...}
    ```

    Or:
    ```
    {...}
    ```
    """
    text = text.strip()

    # Check if content is wrapped in markdown code blocks
    if text.startswith("```"):
        lines = text.split('\n')
        json_start = -1
        json_end = len(lines)

        for i, line in enumerate(lines):
            # Find the first line after the opening ```
            if json_start == -1 and line.strip().startswith("```"):
                json_start = i + 1
            # Find the closing ``` (but only after we've started)
            elif json_start != -1 and line.strip() == "```":
                json_end = i
                break

        if json_start != -1:
            return '\n'.join(lines[json_start:json_end])

    return text


async def run_auditor_agent(
    task: str,
    worker_result: Dict[str, Any],
    auditor_prompt: str,
    verbose: bool = False,
    iteration: int = 1,
    task_id: str = "",
    output_dir: Path | None = None
) -> Dict[str, Any]:
    """Run the auditor agent to review the worker's results.

    Uses file-based output: auditor writes audit_status.txt (for loop control)
    and audit_report_iteration_N_task_TASK_ID.md (for detailed review).

    Args:
        task: The original task description
        worker_result: The worker agent's results
        auditor_prompt: System prompt for the auditor agent
        verbose: If True, print full output
        iteration: Current iteration number
        task_id: Unique task ID
        output_dir: Directory to write audit files (defaults to OUTPUT_DIR_BASE/today)

    Returns:
        Dictionary with audit verdict, rating, and report content
    """
    if output_dir is None:
        output_dir = get_output_dir()
    output_dir = Path(output_dir)

    if verbose:
        print("=" * 60)
        print("🔍 AUDITOR AGENT - Reviewing Results")
        print("=" * 60)
    else:
        print("🔍 Auditor Agent: Reviewing results...", end="", flush=True)

    # Prepare audit request with iteration number, task ID, and output directory
    audit_request = f"""Please audit the following work:

## Original Task
{task}

## Worker Agent Results
{worker_result.get('content', worker_result.get('error', 'No results'))}

IMPORTANT: You are on iteration {iteration}. Your Task ID is: {task_id}

OUTPUT_DIR: {output_dir}

Write ALL files to: {output_dir}

Write your detailed report to: {output_dir / AUDIT_REPORT_PREFIX}{iteration}_task_{task_id}.md
"""

    # Auditor needs tools to write files - allow all tools for now
    client = await create_agent(auditor_prompt, tools=None)  # None = all tools allowed

    audit_result = {
        "verdict": "UNKNOWN",
        "rating": 0,
        "content": "",
        "report_file": str(output_dir / f"{AUDIT_REPORT_PREFIX}{iteration}_task_{task_id}.md"),
    }

    try:
        async with client:
            await client.query(audit_request)

            # Consume all messages
            debug_content = []
            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    if msg.error:
                        audit_result["error"] = msg.error
                        break

                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            debug_content.append(block.text)
                            if verbose:
                                print(block.text, end="", flush=True)

                elif isinstance(msg, ResultMessage):
                    break

            # Store raw response for debugging
            audit_result["raw_response"] = "\n".join(debug_content) if debug_content else "No text response"

        # Read audit_status.txt for verdict and rating
        status_file_path = output_dir / AUDIT_STATUS_FILE
        if status_file_path.exists():
            with open(status_file_path) as f:
                for line in f:
                    line = line.strip()
                    if "=" in line:
                        key, value = line.split("=", 1)
                        if key == "AUDIT_VERDICT":
                            audit_result["verdict"] = value
                        elif key == "AUDIT_RATING":
                            try:
                                audit_result["rating"] = int(value)
                            except ValueError:
                                audit_result["rating"] = 0

            # Clean up status file
            status_file_path.unlink()

        # Read detailed report if it exists
        report_file_path = output_dir / f"{AUDIT_REPORT_PREFIX}{iteration}_task_{task_id}.md"
        if report_file_path.exists():
            with open(report_file_path) as f:
                audit_result["content"] = f.read()
            audit_result["report_saved"] = True
        else:
            audit_result["content"] = "Report file not found. Auditor may not have completed the file write."
            audit_result["report_saved"] = False

        if verbose:
            print(f"\n✅ Audit complete: verdict={audit_result['verdict']}, rating={audit_result['rating']}/10")
            if audit_result.get("report_saved"):
                print(f"📄 Report saved to: {audit_result['report_file']}")

    except Exception as e:
        audit_result["error"] = str(e)
        if verbose:
            print(f"\n❌ Auditor Agent Error: {e}")

    if not verbose:
        print(f" ✓ (verdict: {audit_result['verdict']}, rating: {audit_result['rating']}/10)")

    return audit_result


def is_passing_verdict(verdict: str) -> bool:
    """Check if the verdict indicates passing work."""
    return verdict in ("PASS", "APPROVED", "PUBLISHED_READY", "MOSTLY_RELIABLE", "RELIABLE")


async def run_worker_agent(
    task: str,
    worker_prompt: str,
    verbose: bool = False,
    audit_feedback: str | None = None
) -> Dict[str, Any]:
    """Run the worker agent to complete the task."""
    if audit_feedback:
        if verbose:
            print("=" * 60)
            print(f"🔧 WORKER AGENT - Iteration Revision")
            print("=" * 60)
        else:
            print(f"🔧 Worker Agent: Fixing issues...", end="", flush=True)
    else:
        if verbose:
            print("=" * 60)
            print("🔧 WORKER AGENT - Executing Task")
            print("=" * 60)
        else:
            print("🔧 Worker Agent: Executing task...", end="", flush=True)

    client = await create_agent(worker_prompt, tools=[])

    worker_result = {
        "task": task,
        "summary": "",
        "content": "",
        "steps": "",
        "notes": "",
    }

    # If this is a revision, prepend audit feedback to the task
    if audit_feedback:
        revision_task = f"""You are revising your previous work based on audit feedback.

## Original Task
{task}

## Audit Feedback
{audit_feedback}

Please revise your work to address ALL issues identified in the audit. Focus on:
1. Fixing critical issues marked as high priority
2. Addressing all requirements that were not met
3. Correcting any errors or problems identified

Provide your revised work following the same output format.
"""
    else:
        revision_task = task

    try:
        async with client:
            await client.query(revision_task)

            content_parts = []
            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    if msg.error:
                        worker_result["error"] = msg.error
                        break

                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            content_parts.append(block.text)
                            if verbose:
                                print(block.text, end="", flush=True)

                elif isinstance(msg, ResultMessage):
                    break

            worker_result["content"] = "\n".join(content_parts)

    except Exception as e:
        worker_result["error"] = str(e)
        if verbose:
            print(f"\n❌ Worker Agent Error: {e}")

    if not verbose:
        print(" ✓")

    return worker_result


async def delegate_and_audit(
    task: str,
    worker_prompt: str | None = None,
    auditor_prompt: str | None = None,
    verbose: bool = False,
    max_iterations: int = 3,
    output_dir: Path | None = None
) -> Dict[str, Any]:
    """
    Main workflow: Delegate task to worker, audit, and iterate if needed.

    Iterates up to max_iterations times (default 3) if audit fails.
    Each iteration provides audit feedback to the worker for improvements.

    Args:
        task: The task description to delegate
        worker_prompt: Optional custom system prompt for worker agent
        auditor_prompt: Optional custom system prompt for auditor agent
        verbose: If True, print full agent output. If False, print concise status.
        max_iterations: Maximum number of worker-auditor cycles (default 3)
        output_dir: Directory to write audit files (defaults to OUTPUT_DIR_BASE/today)

    Returns:
        Dictionary containing all iterations, worker_result, audit_result, and summary
    """
    worker_prompt = worker_prompt or DEFAULT_WORKER_SYSTEM_PROMPT
    auditor_prompt = auditor_prompt or DEFAULT_AUDITOR_SYSTEM_PROMPT

    # Generate unique task ID for this workflow run
    task_id = generate_task_id()

    # Get output directory (create if needed)
    if output_dir is None:
        output_dir = get_output_dir()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        print("\n" + "=" * 60)
        print("🚀 AGENT DELEGATION AND AUDIT WORKFLOW")
        print("=" * 60)
        print(f"\n📋 Task: {task[:100]}{'...' if len(task) > 100 else ''}")
        print(f"📋 Max Iterations: {max_iterations}")
        print(f"🆔 Task ID: {task_id}")
        print(f"📁 Output: {output_dir}\n")
    else:
        print("\n🚀 Agent Delegation Workflow")
        print(f"📋 Task: {task[:80]}{'...' if len(task) > 80 else ''}")
        print(f"🔄 Max iterations: {max_iterations}")
        print(f"🆔 Task ID: {task_id}")
        print(f"📁 Output: {output_dir}")
        print()

    # Store all iterations
    iterations = []
    final_verdict = "UNKNOWN"
    final_rating = 0

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print("\n" + "─" * 60)
            print(f"ITERATION {iteration}/{max_iterations}")
            print("─" * 60)

        # Get audit feedback from previous iteration (if any)
        audit_feedback = None
        if iteration > 1:
            previous_audit = iterations[-1]["audit_result"]
            audit_feedback = previous_audit.get("content", "")
            if verbose:
                print(f"\n📋 Audit Feedback from Iteration {iteration - 1}:")
                print(audit_feedback[:500] + "..." if len(audit_feedback) > 500 else audit_feedback)
                print()

        # Step 1: Run Worker Agent
        worker_result = await run_worker_agent(task, worker_prompt, verbose, audit_feedback)

        # Step 2: Run Auditor Agent (with iteration, task_id, and output_dir)
        audit_result = await run_auditor_agent(task, worker_result, auditor_prompt, verbose, iteration, task_id, output_dir)

        # Extract verdict and rating from audit_result (now from file)
        verdict = audit_result.get("verdict", "UNKNOWN")
        rating = audit_result.get("rating", 0)

        # Store this iteration
        iteration_data = {
            "iteration": iteration,
            "worker_result": worker_result,
            "audit_result": audit_result,
            "verdict": verdict,
            "rating": rating,
        }
        iterations.append(iteration_data)

        final_verdict = verdict
        final_rating = rating

        # Check if we should stop (passed or last iteration)
        if is_passing_verdict(verdict):
            if verbose:
                print(f"\n✅ Iteration {iteration}: PASSED - Stopping early")
            else:
                print(f"✅ Iteration {iteration}/{max_iterations}: PASSED")
            break
        elif iteration < max_iterations:
            if verbose:
                print(f"\n⚠️  Iteration {iteration}: {verdict} - Continuing to next iteration...")
            else:
                print(f"⚠️  Iteration {iteration}/{max_iterations}: {verdict} - Retrying...")
        else:
            if verbose:
                print(f"\n❌ Iteration {iteration}: {verdict} - Max iterations reached")
            else:
                print(f"❌ Iteration {iteration}/{max_iterations}: {verdict} - Max iterations reached")

    # Compile final summary
    summary = {
        "task": task,
        "iterations": iterations,
        "total_iterations": len(iterations),
        "final_verdict": final_verdict,
        "final_rating": final_rating,
        "passed": is_passing_verdict(final_verdict),
        "timestamp": datetime.now().isoformat(),
        "max_iterations": max_iterations,
        "output_dir": str(output_dir),
    }

    # Print final summary
    print()
    print("=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"Total Iterations: {len(iterations)}/{max_iterations}")
    print(f"Quality Rating: {final_rating}/10")
    print(f"Final Verdict: {final_verdict}")
    print(f"Result: {'✅ PASSED' if is_passing_verdict(final_verdict) else '❌ DID NOT PASS'}")
    print(f"Output: {output_dir}")

    if not verbose:
        print("\n💡 Use --verbose to see full agent output")
        print("💡 Full details saved to output file")

    print()

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Delegate a task to a worker agent and audit the results with automatic retry on failure.",
        epilog="""
Examples:
  # Basic usage with auto-generated output file in temp/tasks/agent-delegation-auditor/
  %(prog)s --task "Write a fibonacci function"

  # Read task from file (convenient for task documents)
  %(prog)s --task-file path/to/task.md

  # Specify custom output file path
  %(prog)s --task "Analyze data" --output /path/to/results.json

  # Custom prompts from files
  %(prog)s -t "Task" -w worker.txt -a auditor.txt

  # Read task from file with custom prompts
  %(prog)s -T path/to/task.md -w worker.txt -a auditor.txt

  # Inline custom prompts
  %(prog)s -t "Task" --worker-text "You are..." --auditor-text "You are..."

  # Verbose mode (see full agent output in terminal)
  %(prog)s -t "Task" --verbose

  # Set max iterations (default 3)
  %(prog)s -t "Task" --max-iterations 5

Output Directory:
  By default, all outputs (audit reports and delegation results) are saved to:
    temp/tasks/agent-delegation-auditor/YYYYMMDD/

  Use --output to specify a custom location.

Iteration Workflow:
  If audit fails (FAIL/NEEDS_REVISION), the Worker Agent automatically
  retries with audit feedback. Stops when: (1) audit passes, or (2) max
  iterations reached. This improves quality through feedback loops.

Best Practice:
  Results are automatically saved to the temp/tasks directory.
  Use --verbose to see full agent output in terminal.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--task", "-t", help="The task to delegate (or use --task-file)")
    parser.add_argument("--task-file", "-T", help="Path to task document file to read")
    parser.add_argument("--worker-prompt", "-w", help="Path to worker system prompt file")
    parser.add_argument("--auditor-prompt", "-a", help="Path to auditor system prompt file")
    parser.add_argument("--output", "-o", help="Output JSON file path (OVERWRITE mode)")
    parser.add_argument("--worker-text", help="Direct worker system prompt text")
    parser.add_argument("--auditor-text", help="Direct auditor system prompt text")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print full agent output to terminal (default: concise mode)"
    )
    parser.add_argument(
        "--max-iterations", "-m",
        type=int,
        default=3,
        metavar="N",
        help="Maximum worker-auditor iterations if audit fails (default: 3)"
    )

    args = parser.parse_args()

    # Validate task argument (either --task or --task-file required)
    if not args.task and not args.task_file:
        parser.error("either --task/-t or --task-file/-T is required")
    if args.task and args.task_file:
        parser.error("cannot use both --task and --task-file together")

    # Load task from file if specified
    task = args.task
    if args.task_file:
        with open(args.task_file) as f:
            task = f.read()

    # Load prompts from file or use defaults
    worker_prompt = DEFAULT_WORKER_SYSTEM_PROMPT
    auditor_prompt = DEFAULT_AUDITOR_SYSTEM_PROMPT

    if args.worker_prompt:
        with open(args.worker_prompt) as f:
            worker_prompt = f.read()
    if args.auditor_prompt:
        with open(args.auditor_prompt) as f:
            auditor_prompt = f.read()

    if args.worker_text:
        worker_prompt = args.worker_text
    if args.auditor_text:
        auditor_prompt = args.auditor_text

    # Get output directory (create if needed)
    output_dir = get_output_dir()

    # Determine output file (auto-generate if not specified)
    output_file = args.output
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"delegation_result_{timestamp}.json"
    else:
        output_file = Path(output_file)

    # Run the workflow
    result = asyncio.run(delegate_and_audit(
        task=task,
        worker_prompt=worker_prompt,
        auditor_prompt=auditor_prompt,
        verbose=args.verbose,
        max_iterations=args.max_iterations,
        output_dir=output_dir
    ))

    # Save to file (OVERWRITE mode - each run replaces the file)
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"✅ Results saved to: {output_file}")

    # Print file location reminder
    print(f"\n💡 To review results: cat {output_file}")
    print(f"💡 Or ask Claude: 'Review the audit results in {output_file}'")
    print(f"💡 Iterations: {result['total_iterations']}/{result['max_iterations']}")

    # Exit with appropriate code
    if result['passed']:
        return 0
    else:
        return 1


if __name__ == "__main__":
    main()
