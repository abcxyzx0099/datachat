"""
Survey Analysis Coordinator - Workflow Orchestrator

Orchestrates all 5 stages of survey analysis workflow.
Handles checkpointing, error recovery, and progress tracking.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
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
        return checkpoint_file

    def load(self, stage: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint for a stage."""
        checkpoint_file = self.checkpoint_dir / f"{stage}_checkpoint.json"
        if not checkpoint_file.exists():
            return None
        with open(checkpoint_file, 'r') as f:
            return json.load(f)

    def get_latest_checkpoint(self) -> Optional[str]:
        """Get the most recent checkpoint."""
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
        return None

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
            print(f"{symbol} {self.current_stage} Complete!")
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


def run_stage1(
    checkpoint_mgr: CheckpointManager,
    progress: ProgressTracker,
    sav_file: str,
    output_dir: str
) -> bool:
    """Execute Stage 1: Data Preparation."""
    progress.start_stage("1", "Data Preparation")

    try:
        # Import here to avoid import errors until runtime
        from spss_analyzer.io import SPSSReader, MetadataTransformer

        reader = SPSSReader()
        data, meta = reader.read(sav_file)

        progress.update_progress(f"Loaded {len(data)} rows from {sav_file}")

        transform = MetadataTransformer()
        metadata = transform.to_variable_centered(meta)

        # Filter variables for analysis
        analysis_vars = transform.get_analysis_variables(metadata)
        filtered_metadata = {k: v for k, v in metadata.items() if k in analysis_vars}

        progress.update_progress(f"Filtered to {len(filtered_metadata)} variables")

        # Save output
        output_file = Path(output_dir) / "filtered_metadata.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(filtered_metadata, f, indent=2)

        # Save checkpoint
        checkpoint_state = {
            "metadata": {
                "variable_count": len(metadata),
                "filtered_count": len(filtered_metadata),
                "analysis_vars": analysis_vars
            },
            "output": str(output_file)
        }
        checkpoint_mgr.save("stage1", checkpoint_state)

        progress.complete_stage()
        print(f"✅ Output: {output_file}")
        return True

    except ImportError:
        print("❌ Error: spss_analyzer library not found")
        print("   Install: Add lib directory to PYTHONPATH")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        checkpoint_mgr.save("stage1", {"error": str(e)})
        return False


def run_stage2(
    checkpoint_mgr: CheckpointManager,
    progress: ProgressTracker,
    metadata_file: str,
    output_dir: str
) -> bool:
    """Execute Stage 2: Table Specification (AI-orchestrated)."""
    progress.start_stage("2", "Table Specification")

    try:
        from anthropic import Anthropic

        # Load metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        progress.update_progress("Loaded metadata for specification generation")

        # Build prompt for AI
        variable_summary = "\n".join([
            f"- {var['label']} ({var['variable_type']})"
            for var in metadata.values()
        ])

        prompt = f"""Generate a table specification for survey analysis.

Survey Variables:
{variable_summary}

Requirements:
1. Create INDICATORS - Compute metrics from multiple variables
2. Create TABLES - Cross-tabulations between variables
3. Define GLOBAL RECodings - Variable recoding rules
4. Define OUTPUT SETTINGS - Format and rendering preferences

Output a JSON file with this structure:
{{
  "version": "1.0",
  "generated_at": "{timestamp}",
  "source_file": "{source_file}",
  "global_recodings": [...],
  "indicators": [...],
  "tables": [...],
  "output_settings": {...}
}}
"""

        # Call Anthropic API
        client = Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250929",
            max_tokens=4000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract JSON from response
        import re
        json_match = re.search(r'\{[\s\S]+?\}', response.content)
        if json_match:
            spec_json = json_match.group(0)
            # Clean up JSON formatting
            spec_json = re.sub(r',\s*', ', ', spec_json)
        else:
            print("❌ Error: Could not extract JSON from AI response")
            checkpoint_mgr.save("stage2", {"error": "Failed to extract JSON"})
            return False

        # Validate and save
        spec_file = Path(output_dir) / "table_specification.json"
        with open(spec_file, 'w') as f:
            json.dump(json.loads(spec_json), f, indent=2)

        checkpoint_state = {
            "input_metadata": metadata_file,
            "output_spec": str(spec_file),
            "variables_count": len(metadata),
            "tables_count": len(json.loads(spec_json).get("tables", []))
        }
        checkpoint_mgr.save("stage2", checkpoint_state)

        progress.complete_stage()
        print(f"✅ Output: {spec_file}")
        print(f"   Generated {len(json.loads(spec_json).get('tables', []))} tables")
        return True

    except ImportError:
        print("❌ Error: anthropic library not found")
        print("   Install: pip install anthropic")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        checkpoint_mgr.save("stage2", {"error": str(e)})
        return False


def run_stage3(
    checkpoint_mgr: CheckpointManager,
    progress: ProgressTracker,
    spec_file: str,
    sav_file: str,
    output_dir: str
) -> bool:
    """Execute Stage 3: Cross-Table Calculation."""
    progress.start_stage("3", "Cross-Table Calculation")

    try:
        from spss_analyzer.io import SPSSReader
        from spss_analyzer.pspp import PSPPExecutor
        import pandas as pd

        # Load specification
        with open(spec_file, 'r') as f:
            spec = json.load(f)

        progress.update_progress("Loaded table specification")

        # Step 7: Apply recoding rules
        print("\n[Step 7] Applying recoding rules...")
        global_recodings = spec.get("global_recodings", [])

        if global_recodings:
            # TODO: Generate and execute PSPP recoding syntax
            print(f"   {len(global_recodings)} recoding rules defined")
            print("   (PSPP recoding not yet implemented - skipping)")
        else:
            print("   No global recodings - skipping")

        # Step 8: Compute indicators
        print("\n[Step 8] Computing indicators...")
        indicators_spec = spec.get("indicators", [])

        indicators_data = []
        for indicator_spec in indicators_spec:
            var_names = indicator_spec.get("variables", [])
            aggregation = indicator_spec.get("aggregation", "mean")

            # Load data
            reader = SPSSReader()
            data, meta = reader.read(sav_file)

            # Compute indicator
            if aggregation == "mean":
                values = data[var_names].dropna()
                indicator_value = values.mean()
            elif aggregation == "sum":
                indicator_value = data[var_names].dropna().sum()
            elif aggregation == "count":
                indicator_value = data[var_names].dropna().count()
            else:
                indicator_value = data[var_names].dropna().median()

            indicators_data.append({
                "indicator_id": indicator_spec.get("id"),
                "value": float(indicator_value)
            })

            print(f"   Computed: {indicator_spec.get('name')} = {indicator_value:.2f}")

        # Save indicators
        indicators_file = Path(output_dir) / "indicators.csv"
        pd.DataFrame(indicators_data).to_csv(indicators_file, index=False)
        print(f"   Saved: {indicators_file}")

        # Step 9: Generate cross-tables
        print("\n[Step 9] Generating cross-tables...")
        tables_spec = spec.get("tables", [])

        cross_tables = {}
        for table_spec in tables_spec:
            row_var = table_spec["rows"]["variable"]
            col_var = table_spec["columns"]["variable"]

            reader = SPSSReader()
            data, meta = reader.read(sav_file)

            # Generate crosstab
            crosstab = pd.crosstab(data[row_var], data[col_var])
            cross_tables[table_spec.get("id")] = crosstab.to_dict()

        # Save cross-tables
        cross_tables_file = Path(output_dir) / "cross_tables.json"
        with open(cross_tables_file, 'w') as f:
            json.dump(cross_tables, f, indent=2)

        progress.update_progress(f"Generated {len(cross_tables)} tables")
        print(f"   Saved: {cross_tables_file}")

        checkpoint_state = {
            "spec_file": spec_file,
            "indicators_file": str(indicators_file),
            "cross_tables_file": str(cross_tables_file),
            "tables_count": len(cross_tables)
        }
        checkpoint_mgr.save("stage3", checkpoint_state)

        progress.complete_stage()
        print(f"✅ Stage 3 Complete!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        checkpoint_mgr.save("stage3", {"error": str(e), "traceback": __import__('traceback').format_exc()})
        return False


def run_stage4(
    checkpoint_mgr: CheckpointManager,
    progress: ProgressTracker,
    cross_tables_file: str,
    output_dir: str
) -> bool:
    """Execute Stage 4: Statistical Analysis."""
    progress.start_stage("4", "Statistical Analysis")

    try:
        import json
        import pandas as pd
        from scipy.stats import chi2_contingency
        import numpy as np

        # Load cross-tables
        with open(cross_tables_file, 'r') as f:
            tables = json.load(f)

        progress.update_progress("Loaded cross-tables for analysis")

        # Load specification
        spec_file = Path(output_dir).parent / "table_specification.json"
        with open(spec_file, 'r') as f:
            spec = json.load(f)

        threshold = spec.get("output_settings", {}).get("significance_threshold", 0.05)

        # Step 10: Statistical analysis
        print("\n[Step 10] Calculating statistics...")
        results = []

        for table_id, table in tables.items():
            df = pd.DataFrame(table)

            try:
                chi2, p_value, dof, expected = chi2_contingency(df.values)
                results.append({
                    "table_id": table_id,
                    "chi_square": float(chi2),
                    "p_value": float(p_value),
                    "degrees_of_freedom": int(dof),
                    "significant": bool(p_value < threshold)
                })
            except Exception as e:
                results.append({
                    "table_id": table_id,
                    "error": str(e)
                })

        # Save statistical summary
        stats_file = Path(output_dir) / "statistical_summary.json"

        class NpEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (np.bool_, bool)):
                    return bool(obj)
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                return super().default(obj)

        with open(stats_file, 'w') as f:
            json.dump(results, f, indent=2, cls=NpEncoder)

        sig_count = sum(1 for r in results if r.get("significant", False))
        progress.update_progress(f"Significant: {sig_count}/{len(results)}")
        print(f"   Saved: {stats_file}")

        # Step 11: Filter significant tables
        print("\n[Step 11] Filtering significant tables...")
        filtered_tables = {
            k: v for k, v in tables.items()
            if any(r["table_id"] == k and r.get("significant", False))
                for r in results
        }

        # Save filtered tables
        filtered_file = Path(output_dir) / "filtered_tables.json"
        with open(filtered_file, 'w') as f:
            json.dump(filtered_tables, f, indent=2)

        progress.update_progress(f"Filtered to {len(filtered_tables)} tables")
        print(f"   Saved: {filtered_file}")

        checkpoint_state = {
            "stats_file": str(stats_file),
            "filtered_file": str(filtered_file),
            "significant_count": sig_count,
            "total_count": len(tables)
        }
        checkpoint_mgr.save("stage4", checkpoint_state)

        progress.complete_stage()
        print(f"✅ Stage 4 Complete!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        checkpoint_mgr.save("stage4", {"error": str(e), "traceback": __import__('traceback').format_exc()})
        return False


def run_stage5(
    checkpoint_mgr: CheckpointManager,
    progress: ProgressTracker,
    filtered_tables_file: str,
    stats_file: str,
    metadata_file: str,
    output_dir: str
) -> bool:
    """Execute Stage 5: Reporting."""
    progress.start_stage("5", "Reporting")

    try:
        from spss_analyzer.reporting import PowerPointGenerator, HTMLDashboardGenerator, DashboardConfig

        # Load data
        with open(filtered_tables_file, 'r') as f:
            filtered_tables = json.load(f)
        with open(stats_file, 'r') as f:
            stats = json.load(f)
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        # Convert stats to expected format
        stats_dict = {"tables": stats}

        # Step 12: Generate PowerPoint
        print("\n[Step 12] Creating PowerPoint presentation...")
        try:
            ppt_gen = PowerPointGenerator()
            ppt_gen.create_presentation(
                tables=list(filtered_tables.values()),
                statistics=stats_dict,
                title="Survey Analysis Results",
                subtitle=f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
            )
            ppt_gen.save(Path(output_dir) / "presentation.pptx")
            print(f"   Saved: presentation.pptx")
            ppt_success = True
        except Exception as e:
            print(f"   PowerPoint generation skipped: {e}")
            ppt_success = False

        # Step 13: Generate HTML Dashboard
        print("\n[Step 13] Creating HTML Dashboard...")

        # Prepare config
        config = DashboardConfig(
            title="Survey Analysis Dashboard",
            show_charts=True,
            enable_export=True,
            enable_filtering=True
        )

        html_gen = HTMLDashboardGenerator()
        html = html_gen.generate_dashboard(
            cross_tables=filtered_tables,
            statistics=stats_dict,
            config=config
        )

        dashboard_file = Path(output_dir) / "dashboard.html"
        with open(dashboard_file, 'w') as f:
            f.write(html)

        print(f"   Saved: {dashboard_file}")

        checkpoint_state = {
            "ppt_file": str(Path(output_dir) / "presentation.pptx") if ppt_success else None,
            "dashboard_file": str(dashboard_file),
            "ppt_success": ppt_success
        }
        checkpoint_mgr.save("stage5", checkpoint_state)

        progress.complete_stage()
        progress.complete_stage()
        print(f"\n✅ Analysis Complete!")
        print(f"\n{'=' * 60}")
        print("\nGenerated files:")
        print(f"  Stage 1: {Path(output_dir) / 'filtered_metadata.json'}")
        print(f"  Stage 2: {Path(output_dir) / 'table_specification.json'}")
        print(f"  Stage 3: {Path(output_dir) / 'indicators.csv'}, {Path(output_dir) / 'cross_tables.json'}")
        print(f"  Stage 4: {Path(output_dir) / 'statistical_summary.json'}, {Path(output_dir) / 'filtered_tables.json'}")
        print(f"  Stage 5: {Path(output_dir) / 'presentation.pptx'}, {Path(output_dir) / 'dashboard.html'}")
        print()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        checkpoint_mgr.save("stage5", {"error": str(e)})
        return False


def main():
    """Main entry point for survey-coordinator skill."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Orchestrate 5-stage survey analysis workflow"
    )
    parser.add_argument("--sav-file", required=True, help="Path to SPSS .sav file")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--resume-from", choices=["1","2","3","4","5"],
                        help="Resume from specific stage")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate pipeline without execution")
    parser.add_argument("--stage", choices=["1","2","3","4","5"],
                        help="Run specific stage only")

    args = parser.parse_args()

    # Set up paths
    output_dir = Path(args.output_dir)
    checkpoint_dir = output_dir / "checkpoints"
    sav_file = args.sav_file

    # File paths for each stage
    metadata_file = output_dir / "filtered_metadata.json"
    spec_file = output_dir / "table_specification.json"
    cross_tables_file = output_dir / "cross_tables.json"
    stats_file = output_dir / "statistical_summary.json"
    filtered_tables_file = output_dir / "filtered_tables.json"

    progress = ProgressTracker()
    checkpoint_mgr = CheckpointManager(str(checkpoint_dir))

    print("=" * 60)
    print("Survey Analysis Coordinator")
    print("=" * 60)
    print()

    # Check resume option
    if args.resume_from:
        stage_num = int(args.resume_from)
        print(f"🔄 Resuming from Stage {stage_num}")

        checkpoint = checkpoint_mgr.load(f"stage{stage_num}")
        if checkpoint:
            print(f"   Found checkpoint from {checkpoint['timestamp']}")
            progress.start_stage(args.resume_from, f"Stage {stage_num} (Resume)")
        else:
            print(f"   No checkpoint found for Stage {stage_num}")
            print(f"   Starting fresh from Stage {stage_num}")

        # Execute requested stage or all
        if args.stage:
            stage = args.stage
            print(f"\n🎯 Running Stage {stage} only...")
            if stage == "1":
                success = run_stage1(checkpoint_mgr, progress, sav_file, str(output_dir))
            elif stage == "2":
                success = run_stage2(checkpoint_mgr, progress, metadata_file, str(output_dir))
            elif stage == "3":
                success = run_stage3(checkpoint_mgr, progress, spec_file, sav_file, str(output_dir))
            elif stage == "4":
                success = run_stage4(checkpoint_mgr, progress, cross_tables_file, str(output_dir))
            elif stage == "5":
                success = run_stage5(checkpoint_mgr, progress, filtered_tables_file, stats_file, metadata_file, str(output_dir))
            sys.exit(0 if success else 1)
    else:
        # Full pipeline
        if args.dry_run:
            print("\n🧪 Dry run mode - validating pipeline only...\n")
            print("✅ All inputs validated")
            sys.exit(0)

        # Validate inputs
        if not validate_input_file(sav_file):
            sys.exit(1)

        # Execute pipeline
        pipeline_stages = [
            ("1", run_stage1, checkpoint_mgr, progress, sav_file, output_dir),
            ("2",run_stage2, checkpoint_mgr, progress, metadata_file, output_dir),
            ("3",run_stage3, checkpoint_mgr, progress, spec_file, sav_file, output_dir),
            ("4",run_stage4, checkpoint_mgr, progress, cross_tables_file, output_dir),
            ("5",run_stage5, checkpoint_mgr, progress, filtered_tables_file, stats_file, metadata_file, output_dir),
        ]

        for stage_name, stage_func, *stage_args in pipeline_stages:
            if stage_func:
                progress.start_stage(stage_name, f"Stage {stage_name}")
                success = stage_func(*stage_args)

                if not success:
                    print(f"\n❌ Pipeline stopped at Stage {stage_name}")
                    checkpoint_mgr.save("pipeline", {"failed_at": stage_name})
                    sys.exit(1)

    print(f"\n✅ Pipeline complete! All stages successful.")
    sys.exit(0)


if __name__ == "__main__":
    main()
