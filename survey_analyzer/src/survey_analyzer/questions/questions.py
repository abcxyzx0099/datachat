"""
Question Extraction Module (Unified)

Extracts question codes from SPSS variable names and groups variables by question.
Creates/updates the unified table_specification.jsonc file.

This is Stage 2 of the 7-stage workflow.
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class QuestionExtractor:
    """
    Extract question codes from variable names and group variables by question.

    Question code is defined as the letters before the first underscore in a variable name.
    Examples:
        Q2A_1_bin → Q2A
        S0_cat → S0
        weight_var → weight_var (no underscore, use full name)
    """

    def __init__(self, unified_spec: Optional[Any] = None):
        """
        Initialize the QuestionExtractor.

        Args:
            unified_spec: Optional UnifiedTableSpec instance for direct updates
        """
        self.unified_spec = unified_spec

    def extract_question_code(self, variable_name: str) -> str:
        """
        Extract question code from variable name.

        The question code is the portion before the first underscore.
        If no underscore exists, the full variable name is used.
        """
        if "_" in variable_name:
            return variable_name.split("_")[0]
        return variable_name

    def extract_questions(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract questions from filtered metadata.

        Args:
            metadata: Contents of filtered_metadata.json

        Returns:
            List of question dictionaries
        """
        # Get variable names from metadata
        if "variable_names" in metadata:
            variable_names = metadata.get("variable_names", [])
        else:
            # Dictionary format: keys are variable names
            variable_names = [k for k in metadata.keys()
                           if isinstance(metadata[k], dict)
                           and "variable_name" in metadata[k]]

        # Group variables by question code
        questions_dict: defaultdict = defaultdict(list)
        for var_name in variable_names:
            question_code = self.extract_question_code(var_name)
            questions_dict[question_code].append(var_name)

        # Build questions list (sorted by question_code)
        questions = [
            {
                "question_code": code,
                "question_type": "",  # Will be filled by LLM
                "question_text": "",   # Will be filled by LLM
                "original_variables": sorted(vars)
            }
            for code, vars in sorted(questions_dict.items())
        ]

        return questions

    def extract_from_file(
        self,
        metadata_file: str,
        output_spec: str = "output/table_specification.jsonc"
    ) -> Dict[str, Any]:
        """
        Load metadata from file, extract questions, and save to unified table_specification.jsonc.

        This is the main entry point for Stage 2.

        Args:
            metadata_file: Path to filtered_metadata.json
            output_spec: Path to save table_specification.jsonc

        Returns:
            The updated specification dictionary
        """
        # Read metadata
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Extract questions
        questions = self.extract_questions(metadata)

        # Create or update unified spec
        if self.unified_spec:
            # Using unified spec instance
            try:
                self.unified_spec.load(output_spec)
            except FileNotFoundError:
                # Create new spec
                source_file = metadata.get("source_file", Path(metadata_file).name)
                case_count = metadata.get("case_count", 0)
                self.unified_spec.create(
                    output_spec,
                    source_file=source_file,
                    case_count=case_count
                )

            # Add questions
            self.unified_spec.add_questions(questions)
            return self.unified_spec.spec

        else:
            # Direct file operations (without UnifiedTableSpec)
            spec_path = Path(output_spec)

            # Try to load existing, or create new
            if spec_path.exists():
                with open(spec_path, "r", encoding="utf-8") as f:
                    # Strip JSONC comments
                    content = f.read()
                    lines = [line for line in content.split("\n") if not line.strip().startswith("//")]
                    content = "\n".join(lines)
                    spec = json.loads(content)
            else:
                # Create new spec
                source_file = metadata.get("source_file", Path(metadata_file).name)
                case_count = metadata.get("case_count", 0)
                spec = {
                    "metadata": {
                        "spec_id": f"tablespec_proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "project_id": "proj_survey",
                        "dataset_id": "ds_survey_data",
                        "source_file": source_file,
                        "case_count": case_count,
                        "stage": "questions_extracted",
                        "generated_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat()
                    },
                    "questions": [],
                    "filter_clause": {"exclude_incomplete": True},
                    "weight_indicator": None
                }
                spec_path.parent.mkdir(parents=True, exist_ok=True)

            # Add questions
            for q in questions:
                # Check if already exists
                if not any(qq["question_code"] == q["question_code"] for qq in spec.get("questions", [])):
                    spec["questions"].append(q)

            # Save
            with open(spec_path, "w", encoding="utf-8") as f:
                f.write("// Unified Table Specification\n")
                f.write("// Stage 2: Questions extracted\n\n")
                json.dump(spec, f, indent=2, ensure_ascii=False)
                f.write("\n")

            print(f"✓ Extracted {len(questions)} questions")
            print(f"  Total questions in spec: {len(spec['questions'])}")
            print(f"  Saved to: {output_spec}")

            return spec

    def save_questions(self, questions: List[Dict[str, Any]], output_path: str) -> None:
        """
        Save questions to standalone JSON file (optional backup).

        This creates the optional questions.json backup file.
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_questions": len(questions)
                },
                "questions": questions
            }, f, indent=2, ensure_ascii=False)


def main():
    """CLI entry point for question extraction."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract questions from filtered metadata (Stage 2)"
    )
    parser.add_argument(
        "--metadata-file",
        required=True,
        help="Path to filtered_metadata.json"
    )
    parser.add_argument(
        "--output-spec",
        default="output/table_specification.jsonc",
        help="Output table specification file (default: output/table_specification.jsonc)"
    )
    parser.add_argument(
        "--backup-file",
        help="Optional: Also save questions.json backup"
    )

    args = parser.parse_args()

    # Extract questions
    extractor = QuestionExtractor()
    spec = extractor.extract_from_file(
        args.metadata_file,
        output_spec=args.output_spec
    )

    # Optional: save backup
    if args.backup_file:
        questions = spec.get("questions", [])
        extractor.save_questions(questions, args.backup_file)
        print(f"  Backup saved: {args.backup_file}")


if __name__ == "__main__":
    main()
