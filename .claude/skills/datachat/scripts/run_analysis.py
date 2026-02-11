#!/usr/bin/env python3
"""
DataChat Analysis Runner - API Integration Script

This script provides a command-line interface to the DataChat LangGraph API,
allowing AionUi to trigger and manage survey analysis workflows.

Usage:
    python run_analysis.py <input_file> [--thread-id ID]
    python run_analysis.py --resume --thread-id ID
    python run_analysis.py --status --thread-id ID
"""

import argparse
import json
import sys
import time
import requests
from pathlib import Path
from typing import Optional


# Default API configuration
DEFAULT_API_URL = "http://localhost:8123"
DEFAULT_CHECKPOINT_DB = "checkpoints.db"


def analyze_file(
    input_file: str,
    thread_id: str = "default",
    api_url: str = DEFAULT_API_URL,
) -> dict:
    """
    Start a new survey analysis on an SPSS file.

    Args:
        input_file: Path to .sav file
        thread_id: Thread ID for checkpointing
        api_url: LangGraph API URL

    Returns:
        Analysis result dictionary
    """
    # Validate input file
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Create thread first
    thread_response = requests.post(f"{api_url}/threads", json={}, timeout=10)
    thread_response.raise_for_status()
    thread_data = thread_response.json()

    # Use provided thread_id or the generated one
    actual_thread_id = thread_id if thread_id != "default" else thread_data["thread_id"]

    # Upload file and invoke analysis
    files = {"file": (input_path.name, open(input_path, "rb"), "application/octet-stream")}
    params = {"stream": "false"}

    try:
        response = requests.post(
            f"{api_url}/threads/{actual_thread_id}/invoke",
            files=files,
            params=params,
            timeout=300  # 5 minutes for analysis
        )
        response.raise_for_status()
        return response.json()
    finally:
        files["file"][1].close()


def resume_analysis(
    thread_id: str,
    api_url: str = DEFAULT_API_URL,
) -> dict:
    """
    Resume an interrupted analysis from checkpoint.

    Args:
        thread_id: Thread ID to resume
        api_url: LangGraph API URL

    Returns:
        Analysis result dictionary
    """
    response = requests.post(f"{api_url}/threads/{thread_id}/resume", timeout=300)
    response.raise_for_status()
    return response.json()


def get_status(
    thread_id: str,
    api_url: str = DEFAULT_API_URL,
) -> dict:
    """
    Get the current status of an analysis.

    Args:
        thread_id: Thread ID to check
        api_url: LangGraph API URL

    Returns:
        Status dictionary with current step, state, etc.
    """
    response = requests.get(f"{api_url}/threads/{thread_id}/state", timeout=10)
    response.raise_for_status()
    return response.json()


def submit_feedback(
    thread_id: str,
    approved: bool,
    feedback: Optional[str] = None,
    api_url: str = DEFAULT_API_URL,
) -> dict:
    """
    Submit feedback for a review step.

    Args:
        thread_id: Thread ID
        approved: Whether to approve or reject
        feedback: Optional feedback message
        api_url: LangGraph API URL

    Returns:
        Response dictionary
    """
    payload = {"approved": approved}
    if feedback:
        payload["feedback"] = feedback

    response = requests.post(
        f"{api_url}/threads/{thread_id}/feedback",
        json=payload,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def health_check(api_url: str = DEFAULT_API_URL) -> dict:
    """
    Check if the API is healthy.

    Args:
        api_url: LangGraph API URL

    Returns:
        Health status dictionary
    """
    response = requests.get(f"{api_url}/health", timeout=10)
    response.raise_for_status()
    return response.json()


def format_progress_bar(current: int, total: int, width: int = 40) -> str:
    """Format a progress bar showing completion status."""
    if total == 0:
        return "[" + "=" * width + "]"

    filled = int(width * current / total)
    bar = "=" * filled + ">" * (1 if filled < width else 0) + " " * (width - filled - 1)
    return f"[{bar}] {current}/{total} ({100 * current // total}%)"


def extract_step_number(step_name: str) -> int:
    """Extract step number from step name like 'step_1_extract_spss'."""
    try:
        if step_name.startswith("step_"):
            return int(step_name.split("_")[1])
        return 0
    except:
        return 0


def print_status(status: dict):
    """Print formatted status information."""
    current_step = status.get("current_step", "unknown")
    requires_review = status.get("requires_human_review", False)
    summary = status.get("summary", {})

    errors_count = summary.get("errors_count", 0)
    warnings_count = summary.get("warnings_count", 0)

    print(f"\n📊 Analysis Status:")
    print(f"   Current Step: {current_step}")
    print(f"   Requires Review: {'⚠️  YES' if requires_review else '✅ No'}")
    print(f"   Errors: {errors_count}")
    print(f"   Warnings: {warnings_count}")


def print_results(result: dict):
    """Print formatted results information."""
    status = result.get("status", "unknown")
    summary = result.get("summary", {})
    result_data = result.get("result", {})

    print(f"\n✅ Analysis {status}!")

    if status == "completed":
        print(f"\n📁 Output Files:")

        if result_data.get("new_data_file"):
            print(f"   • Recoded Dataset: {result_data['new_data_file']}")

        if result_data.get("cross_table_file"):
            print(f"   • Cross-Tables: {result_data['cross_table_file']}")

        if result_data.get("statistics_script"):
            print(f"   • Statistics Script: {result_data['statistics_script']}")

        if result_data.get("powerpoint_file"):
            print(f"   • PowerPoint: {result_data['powerpoint_file']}")

        if result_data.get("html_dashboard_file"):
            print(f"   • HTML Dashboard: {result_data['html_dashboard_file']}")

        print(f"\n📈 Statistics:")
        print(f"   • Tables Evaluated: {summary.get('total_tables_evaluated', 'N/A')}")
        print(f"   • Significant Tables: {summary.get('significant_tables_count', 'N/A')}")
        print(f"   • Filtering Valid: {'✅ Yes' if summary.get('filtering_valid', True) else '❌ No'}")


def main():
    parser = argparse.ArgumentParser(
        description="DataChat SPSS Survey Analysis - CLI Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start new analysis
  python run_analysis.py survey_data.sav

  # Start with custom thread ID
  python run_analysis.py survey_data.sav --thread-id my-analysis

  # Resume interrupted analysis
  python run_analysis.py --resume --thread-id my-analysis

  # Check status
  python run_analysis.py --status --thread-id my-analysis

  # Submit feedback (approve)
  python run_analysis.py --feedback --approve --thread-id my-analysis

  # Submit feedback (reject with message)
  python run_analysis.py --feedback --reject --feedback "Fix these issues" --thread-id my-analysis

  # Wait for completion with progress
  python run_analysis.py survey_data.sav --wait
        """
    )

    # Input arguments
    parser.add_argument("input_file", nargs="?", help="Path to SPSS .sav file")

    # Operation mode
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--status", action="store_true", help="Check analysis status")
    parser.add_argument("--feedback", action="store_true", help="Submit feedback for review step")
    parser.add_argument("--health", action="store_true", help="Check API health")

    # Feedback options
    parser.add_argument("--approve", action="store_true", help="Approve current artifact")
    parser.add_argument("--reject", action="store_true", help="Reject current artifact")
    parser.add_argument("--feedback-text", help="Feedback message")

    # Options
    parser.add_argument("--thread-id", default="default", help="Thread ID for checkpointing")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="LangGraph API URL")
    parser.add_argument("--wait", action="store_true", help="Wait for completion and show progress")

    args = parser.parse_args()

    try:
        if args.health:
            # Health check
            health = health_check(args.api_url)
            print(f"✅ API is healthy")
            print(f"   Graph ID: {health.get('graph_id')}")
            print(f"   Version: {health.get('version')}")

        elif args.status:
            # Get and print status
            status = get_status(args.thread_id, args.api_url)
            print_status(status)

        elif args.feedback:
            # Submit feedback
            if not args.approve and not args.reject:
                parser.error("--feedback requires --approve or --reject")

            approved = args.approve
            feedback = args.feedback_text

            print(f"📝 Submitting feedback for thread: {args.thread_id}")
            print(f"   Decision: {'✅ Approve' if approved else '❌ Reject'}")
            if feedback:
                print(f"   Feedback: {feedback}")

            result = submit_feedback(args.thread_id, approved, feedback, args.api_url)
            print(f"   Message: {result.get('message', 'Feedback submitted')}")

        elif args.resume:
            # Resume analysis
            print(f"🔄 Resuming analysis: {args.thread_id}")
            result = resume_analysis(args.thread_id, args.api_url)
            print_results(result)

        elif args.input_file:
            # Start new analysis
            print(f"🚀 Starting analysis on: {args.input_file}")
            print(f"   Thread ID: {args.thread_id}")
            print(f"   API: {args.api_url}")
            print()

            result = analyze_file(
                args.input_file,
                args.thread_id,
                args.api_url
            )

            # Update thread_id from response
            actual_thread_id = result.get("thread_id", args.thread_id)
            print(f"   Thread ID: {actual_thread_id}")

            if args.wait:
                # Wait for completion and show progress
                print("\n⏳ Waiting for analysis to complete...")
                last_step = None

                while True:
                    try:
                        status = get_status(actual_thread_id, args.api_url)
                        current_step = status.get("current_step")

                        if current_step != last_step:
                            step_num = extract_step_number(current_step)
                            print(f"   {format_progress_bar(step_num, 22)} {current_step}")
                            last_step = current_step

                        # Check if complete or waiting for review
                        requires_review = status.get("requires_human_review", False)
                        if requires_review:
                            print(f"\n⚸  Waiting for human review at: {current_step}")
                            print(f"   Approve: python run_analysis.py --feedback --approve --thread-id {actual_thread_id}")
                            print(f"   Reject: python run_analysis.py --feedback --reject --thread-id {actual_thread_id}")
                            break

                        # Check if complete (step 22 is last)
                        step_num = extract_step_number(current_step)
                        if step_num >= 22:
                            # Analysis complete
                            final_result = {"result": status.get("state", {}), "summary": status.get("summary", {}), "status": "completed"}
                            print_results(final_result)
                            break

                        time.sleep(2)

                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 404:
                            # Thread not found yet, still initializing
                            time.sleep(1)
                            continue
                        raise
            else:
                print_results(result)

        else:
            parser.error("Must specify input_file or one of --resume, --status, --feedback, --health")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to LangGraph API at {args.api_url}", file=sys.stderr)
        print(f"   Make sure the API is running: python -m agent.server", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e.response.status_code}", file=sys.stderr)
        try:
            error_detail = e.response.json()
            print(f"   Detail: {error_detail.get('detail', e.response.text)}", file=sys.stderr)
        except:
            print(f"   Detail: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled")
        sys.exit(130)


if __name__ == "__main__":
    main()
