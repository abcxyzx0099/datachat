"""
Survey Coordinator - Workflow Orchestrator

Orchestrates all 5 stages of survey analysis workflow.
Uses semantic library operations - no processing logic in skill.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class CheckpointManager:
    """Manage workflow checkpoints for resume capability."""

    def __init__(self, checkpoint_dir: str = "output/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save(self, stage: str, state: Dict[str, Any]) -> None:
        """Save checkpoint for a stage."""
        checkpoint_file = self.checkpoint_dir / f"{stage}_checkpoint.json"
        checkpoint_data = {
            "stage": stage,
            "timestamp": datetime.now().isoformat(),
            "state": state
        }
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        print(f"   Checkpoint saved: {checkpoint_file.name}")

    def load(self, stage: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint for a stage."""
        checkpoint_file = self.checkpoint_dir / f"{stage}_checkpoint.json"
        if not checkpoint_file.exists():
            return None
        with open(checkpoint_file, 'r') as f:
            return json.load(f)

    def get_latest_checkpoint(self) -> Optional[str]:
        """Get most recent checkpoint."""
        checkpoints = list(self.checkpoint_dir.glob("*_checkpoint.json"))
        if not checkpoints:
            return None
        checkpoints.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        latest = checkpoints[0]
        return latest.stem.replace("_checkpoint.json", "")


class ProgressTracker:
    """Track and display progress for workflow execution."""

    STAGE_SYMBOLS = {
        "stage1": "📁",
        "stage2": "📋",
        "stage3": "📊",
        "stage4": "📈",
        "stage5": "📑"
    }

    def __init__(self):
        self.current_stage = None
        self.total_stages = 5

    def start_stage(self, stage: str, stage_name: str) -> None:
        """Start tracking a new stage."""
        self.current_stage = stage
        symbol = self.STAGE_SYMBOLS.get(stage, "🔷")
        print(f"\n{symbol} {stage_name}")
        print(f"{'=' * 60}")

    def update_progress(self, message: str, percent: Optional[int] = None) -> None:
        """Update progress within current stage."""
        if percent is not None:
            bar = "█" * int(percent / 5)
            empty = "░" * (20 - int(percent / 5))
            print(f"{bar}{empty} {percent}%")
        else:
            print(f"  {message}")

    def complete_stage(self) -> None:
        """Mark current stage as complete."""
        if self.current_stage:
            symbol = self.STAGE_SYMBOLS.get(self.current_stage, "✅")
            print(f"{symbol} Stage Complete!")
            self.current_stage = None


def validate_input_file(file_path: str) -> bool:
    """Validate that input file exists and is readable."""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ Error: File not found: {file_path}")
        return False
    if not path.is_file():
        print(f"❌ Error: Not a file: {file_path}")
        return False
    return True


def run_workflow(
    sav_file: str,
    output_dir: str = "output",
    skip_stages: Optional[str] = None
) -> bool:
    """Run complete 5-stage analysis workflow using library CLI.

    Args:
        sav_file: Path to SPSS .sav file
        output_dir: Output directory for all results
        skip_stages: Stages to skip (e.g., "3,4")

    Returns:
        True if workflow completed successfully
    """
    from spss_analyzer.cli import all as workflow

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    checkpoint_mgr = CheckpointManager(str(output_path / "checkpoints"))
    progress = ProgressTracker()

    print("=" * 60)
    print("📊 SPSS Survey Analysis - 5-Stage Workflow")
    print("=" * 60)

    # Run workflow using library CLI
    skip_list = skip_stages.split(',') if skip_stages else []

    success = workflow.run_workflow(
        sav_file=sav_file,
        output_dir=output_dir,
        skip_stages=skip_stages
    )

    if success:
        print("\n" + "=" * 60)
        print("✅ All stages completed successfully!")
        print(f"📂 Results saved to: {output_dir}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Workflow did not complete successfully")
        print("=" * 60)

    return success


def main():
    """CLI entry point for survey coordinator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Survey Analysis Coordinator - Orchestrate 5-stage workflow"
    )

    parser.add_argument("--sav-file", required=True,
                        help="Path to SPSS .sav file")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory (default: output/)")
    parser.add_argument("--skip", default=None,
                        help="Comma-separated stages to skip (e.g., '3,4')")

    args = parser.parse_args()

    return 0 if run_workflow(args.sav_file, args.output_dir, args.skip) else 1


if __name__ == "__main__":
    sys.exit(main())
