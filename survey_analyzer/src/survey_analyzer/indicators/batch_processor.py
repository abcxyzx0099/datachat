"""
Batch Processor Module (Unified)

Processes multiple questions to generate indicators.
Updates the unified table_specification.jsonc file directly.

This is Stage 3 of the 7-stage workflow.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import logging

from .generator import IndicatorGenerator


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Process questions in batch to generate indicators.

    Updates the unified table_specification.jsonc file directly.
    Each question's indicators are added to the questions array.

    Usage:
        processor = BatchProcessor()
        processor.process_all(
            spec_file="table_specification.jsonc",
            metadata_file="filtered_metadata.json"
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "glm-4.7",
        continue_on_error: bool = True
    ):
        """Initialize the BatchProcessor."""
        self.generator = IndicatorGenerator(api_key=api_key, model=model)
        self.continue_on_error = continue_on_error

    def process_all(
        self,
        spec_file: str,
        metadata_file: str,
        question_codes: Optional[List[str]] = None,
        resume: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Process all questions and generate indicators.

        Args:
            spec_file: Path to table_specification.jsonc
            metadata_file: Path to filtered_metadata.json
            question_codes: Optional list of question codes to process (default: all)
            resume: If True, skip questions that already have indicators
            progress_callback: Optional callback(current, total, question_code)

        Returns:
            The updated specification dictionary
        """
        # Load unified spec
        spec = self._load_spec(spec_file)

        # Load metadata
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Get questions to process
        questions = spec.get("questions", [])
        if question_codes:
            question_set = set(question_codes)
            questions = [q for q in questions if q["question_code"] in question_set]
            logger.info(f"Processing specific questions: {', '.join(question_codes)}")
        else:
            logger.info(f"Processing all {len(questions)} questions")

        # Process questions
        processed = 0
        skipped = 0
        errors = []

        total = len(questions)
        for idx, question in enumerate(questions):
            question_code = question["question_code"]
            original_variables = question.get("original_variables", [])

            # Skip if resume and already has indicators
            if resume and question.get("indicators"):
                logger.info(f"[{idx + 1}/{total}] Skipping {question_code} (already has indicators)")
                skipped += 1
                if progress_callback:
                    progress_callback(idx + 1, total, question_code)
                continue

            # Process question
            try:
                logger.info(f"[{idx + 1}/{total}] Processing {question_code} ({len(original_variables)} variables)")

                # Generate indicators for this question
                indicators = self.generator.generate_for_question(
                    question_code,
                    original_variables,
                    metadata
                )

                # Add indicators to the question
                question["indicators"] = indicators if isinstance(indicators, list) else [indicators]

                # Save checkpoint
                self._save_spec(spec, spec_file)

                processed += 1
                logger.info(f"  ✓ Generated {len(question['indicators'])} indicator(s)")

                if progress_callback:
                    progress_callback(idx + 1, total, question_code)

            except Exception as e:
                error_msg = f"Error processing {question_code}: {str(e)}"
                logger.error(f"  ✗ {error_msg}")
                errors.append({"question_code": question_code, "error": str(e)})

                if not self.continue_on_error:
                    logger.error("Stopping due to error (continue_on_error=False)")
                    raise

                # Still save checkpoint after error
                self._save_spec(spec, spec_file)

        # Update metadata
        spec["metadata"]["stage"] = "indicators_generated"
        spec["metadata"]["last_updated"] = datetime.now().isoformat()

        # Add to history
        history = spec["metadata"].get("stage_history", [])
        if not any(h.get("stage") == 3 for h in history):
            history.append({
                "stage": 3,
                "name": "indicators_generated",
                "completed_at": datetime.now().isoformat(),
                "summary": {
                    "processed": processed,
                    "skipped": skipped,
                    "errors": len(errors)
                }
            })
        spec["metadata"]["stage_history"] = history

        # Final save
        self._save_spec(spec, spec_file)

        # Generate summary
        total_indicators = sum(
            len(q.get("indicators", []))
            for q in spec.get("questions", [])
        )

        logger.info(f"\n[Batch Processing Complete]")
        logger.info(f"  Processed: {processed}")
        logger.info(f"  Skipped: {skipped}")
        logger.info(f"  Errors: {len(errors)}")
        logger.info(f"  Total indicators: {total_indicators}")
        logger.info(f"  Output: {spec_file}")

        return spec

    def _load_spec(self, spec_file: str) -> Dict[str, Any]:
        """Load unified spec file."""
        with open(spec_file, "r", encoding="utf-8") as f:
            content = f.read()
            # Strip JSONC comments
            lines = [line for line in content.split("\n") if not line.strip().startswith("//")]
            content = "\n".join(lines)
            return json.loads(content)

    def _save_spec(self, spec: Dict[str, Any], spec_file: str) -> None:
        """Save unified spec file with JSONC comments."""
        spec_path = Path(spec_file)
        spec_path.parent.mkdir(parents=True, exist_ok=True)

        with open(spec_path, "w", encoding="utf-8") as f:
            f.write("// ============================================\n")
            f.write("// Unified Table Specification\n")
            f.write("// Stage 3: Indicators generated\n")
            f.write("// ============================================\n\n")
            json.dump(spec, f, indent=2, ensure_ascii=False)
            f.write("\n")


def main():
    """CLI entry point for batch processing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate indicators for questions (Stage 3)"
    )
    parser.add_argument(
        "--spec-file",
        required=True,
        help="Path to table_specification.jsonc"
    )
    parser.add_argument(
        "--metadata-file",
        required=True,
        help="Path to filtered_metadata.json"
    )
    parser.add_argument(
        "--questions",
        help="Comma-separated list of question codes to process (default: all)"
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Process all questions even if they already have indicators"
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop processing on first error"
    )
    parser.add_argument(
        "--backup-file",
        help="Optional: Also save indicators.json backup"
    )

    args = parser.parse_args()

    # Parse question codes if provided
    question_codes = None
    if args.questions:
        question_codes = [q.strip() for q in args.questions.split(",")]

    # Progress callback
    def progress_callback(current: int, total: int, question_code: str) -> None:
        print(f"[{current}/{total}] {question_code}")

    # Process
    processor = BatchProcessor(continue_on_error=not args.stop_on_error)
    spec = processor.process_all(
        spec_file=args.spec_file,
        metadata_file=args.metadata_file,
        question_codes=question_codes,
        resume=not args.no_resume,
        progress_callback=progress_callback
    )

    # Optional: save backup
    if args.backup_file:
        # Extract all indicators for backup
        all_indicators = []
        for q in spec.get("questions", []):
            for ind in q.get("indicators", []):
                all_indicators.append({**ind, "question_code": q["question_code"]})

        backup_data = {
            "metadata": {
                "source_spec": str(Path(args.spec_file).absolute()),
                "generated_at": datetime.now().isoformat(),
                "total_indicators": len(all_indicators)
            },
            "indicators": all_indicators
        }

        backup_path = Path(args.backup_file)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Backup saved: {args.backup_file}")

    print(f"\n✓ Updated: {args.spec_file}")
    print(f"✓ Ready for Stage 4: Classification")


if __name__ == "__main__":
    main()
