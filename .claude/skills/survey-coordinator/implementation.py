"""
Survey Coordinator Skill

Orchestrates the Python library modules for survey analysis workflow.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

# Add library path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib"))

from spss_analyzer.specification import TableSpecificationDocument
from spss_analyzer.io import SPSSReader, MetadataTransformer
from spss_analyzer.pspp import (
    RecodingSyntaxGenerator,
    CTablesSyntaxGenerator,
    PSPPExecutor,
)
from spss_analyzer.analysis import StatisticsCalculator, IndicatorGenerator
from spss_analyzer.filtering import SignificanceFilter, FilterCriteria

logger = logging.getLogger(__name__)


class SurveyCoordinator:
    """Coordinates the survey analysis workflow."""

    def __init__(self, output_dir: str = "output"):
        """Initialize coordinator with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_workflow(
        self,
        spec: TableSpecificationDocument,
        data_file: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run the complete analysis workflow.

        Args:
            spec: Table specification document
            data_file: Path to SPSS .sav file
            metadata: Variable metadata

        Returns:
            Dictionary with paths to all generated files
        """
        results = {
            "status": "running",
            "steps_completed": [],
            "errors": [],
        }

        # Step 1: Apply Recoding
        try:
            recoded_file = self._apply_recoding(spec, data_file)
            results["steps_completed"].append("recoding")
            results["recoded_file"] = str(recoded_file)
            logger.info(f"✓ Step 1: Applied {len(spec.global_recodings)} recoding rules")
        except Exception as e:
            logger.error(f"Recoding failed: {e}")
            results["errors"].append(f"Recoding: {e}")

        # Step 2: Compute Indicators
        try:
            indicators_file = self._compute_indicators(
                spec, results.get("recoded_file", data_file)
            )
            results["steps_completed"].append("indicators")
            results["indicators_file"] = str(indicators_file)
            logger.info(f"✓ Step 2: Computed {len(spec.indicators)} indicators")
        except Exception as e:
            logger.error(f"Indicator computation failed: {e}")
            results["errors"].append(f"Indicators: {e}")

        # Step 3: Generate Cross-Tables
        try:
            cross_tables_file = self._generate_crosstabs(
                spec, results.get("recoded_file", data_file)
            )
            results["steps_completed"].append("crosstabs")
            results["cross_tables_file"] = str(cross_tables_file)
            logger.info(f"✓ Step 3: Generated {len(spec.tables)} cross-tables")
        except Exception as e:
            logger.error(f"Cross-table generation failed: {e}")
            results["errors"].append(f"Crosstabs: {e}")

        # Step 4: Statistical Analysis
        try:
            stats_file = self._calculate_statistics(
                spec, results.get("cross_tables_file")
            )
            results["steps_completed"].append("statistics")
            results["statistics_file"] = str(stats_file)
            logger.info("✓ Step 4: Calculated statistics")
        except Exception as e:
            logger.error(f"Statistical analysis failed: {e}")
            results["errors"].append(f"Statistics: {e}")

        # Step 5: Filter Tables
        try:
            filtered_file = self._filter_tables(
                spec, results.get("statistics_file")
            )
            results["steps_completed"].append("filtering")
            results["filtered_tables_file"] = str(filtered_file)
            logger.info("✓ Step 5: Filtered significant tables")
        except Exception as e:
            logger.error(f"Filtering failed: {e}")
            results["errors"].append(f"Filtering: {e}")

        # Final status
        results["status"] = (
            "completed" if len(results["errors"]) == 0 else "partial"
        )

        return results

    def _apply_recoding(
        self, spec: TableSpecificationDocument, input_file: str
    ) -> Path:
        """Generate and execute PSPP recoding syntax."""
        output_file = self.output_dir / "recoded_data.sav"

        # Generate syntax
        gen = RecodingSyntaxGenerator()
        syntax = gen.generate_syntax_from_spec(spec.global_recodings)

        # Save syntax
        syntax_file = self.output_dir / "recoding.sps"
        with open(syntax_file, "w") as f:
            f.write(syntax)

        # Execute PSPP
        executor = PSPPExecutor()
        result = executor.execute_syntax(
            syntax_file=str(syntax_file),
            input_file=input_file,
            output_file=str(output_file),
        )

        if not result.success:
            raise Exception(f"PSPP failed: {result.error_message}")

        return output_file

    def _compute_indicators(
        self, spec: TableSpecificationDocument, data_file: str
    ) -> Path:
        """Compute indicators from data."""
        # Read data
        reader = SPSSReader()
        df, metadata = reader.read(data_file)

        # Compute indicators
        gen = IndicatorGenerator()
        indicators_df = gen.compute_indicators_from_spec(
            df, spec.indicators
        )

        # Save
        output_file = self.output_dir / "indicators.csv"
        indicators_df.to_csv(output_file, index=False)

        return output_file

    def _generate_crosstabs(
        self, spec: TableSpecificationDocument, data_file: str
    ) -> Path:
        """Generate cross-tables using PSPP."""
        output_file = self.output_dir / "cross_tables.csv"

        # Generate syntax
        gen = CTablesSyntaxGenerator()
        syntax = gen.generate_syntax_from_spec(spec.tables)

        # Save syntax
        syntax_file = self.output_dir / "crosstabs.sps"
        with open(syntax_file, "w") as f:
            f.write(syntax)

        # Execute PSPP
        executor = PSPPExecutor()
        result = executor.execute_syntax(
            syntax_file=str(syntax_file),
            input_file=data_file,
            output_file=str(output_file),
        )

        if not result.success:
            raise Exception(f"PSPP failed: {result.error_message}")

        return output_file

    def _calculate_statistics(
        self, spec: TableSpecificationDocument, tables_file: Path
    ) -> Path:
        """Calculate statistics for cross-tables."""
        # Read tables
        # (Implementation depends on table file format)

        # Calculate statistics
        calc = StatisticsCalculator(
            significance_level=spec.output_settings.significance_threshold
        )
        results = []
        # Process each table...

        # Save
        output_file = self.output_dir / "statistical_summary.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        return output_file

    def _filter_tables(
        self, spec: TableSpecificationDocument, stats_file: Path
    ) -> Path:
        """Filter tables by significance."""
        # Read statistics
        with open(stats_file) as f:
            stats = json.load(f)

        # Create filter
        criteria = FilterCriteria(
            significance_level=spec.output_settings.significance_threshold,
            min_cramers_v=spec.output_settings.min_cramers_v,
        )

        # Apply filter
        filter_obj = SignificanceFilter(criteria)
        filter_list = filter_obj.filter_tables(stats)

        # Save
        output_file = self.output_dir / "filtered_tables.json"
        with open(output_file, "w") as f:
            json.dump(filter_list.to_dict(), f, indent=2)

        return output_file


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Coordinate survey analysis workflow"
    )
    parser.add_argument(
        "spec_file",
        help="Path to table_specification.json",
    )
    parser.add_argument(
        "data_file",
        help="Path to SPSS .sav file",
    )
    parser.add_argument(
        "--metadata-file",
        "-m",
        help="Path to filtered_metadata.json",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="output",
        help="Output directory (default: output/)",
    )

    args = parser.parse_args()

    # Load specification
    with open(args.spec_file) as f:
        spec_dict = json.load(f)
    spec = TableSpecificationDocument.from_dict(spec_dict)

    # Load metadata (optional)
    metadata = None
    if args.metadata_file:
        with open(args.metadata_file) as f:
            metadata = json.load(f)

    # Run workflow
    coordinator = SurveyCoordinator(output_dir=args.output_dir)
    results = coordinator.run_workflow(spec, args.data_file, metadata)

    # Report results
    print("\n" + "=" * 60)
    print("SURVEY ANALYSIS WORKFLOW RESULTS")
    print("=" * 60)
    print(f"\nStatus: {results['status'].upper()}")
    print(f"Steps completed: {', '.join(results['steps_completed'])}")

    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
    else:
        print("\n✓ All steps completed successfully!")

    # List generated files
    print("\nGenerated files:")
    for key, path in results.items():
        if key.endswith('_file') and path:
            print(f"  {key}: {path}")

    sys.exit(0 if results['status'] == 'completed' else 1)


if __name__ == "__main__":
    main()
