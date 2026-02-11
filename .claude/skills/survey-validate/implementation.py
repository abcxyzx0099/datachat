"""
Survey Specification Validator Skill

Validates a table specification document against schema, references, and business logic.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add library path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib"))

from spss_analyzer.specification import (
    TableSpecificationValidator,
    validate_specification,
    ValidationResult,
)

logger = logging.getLogger(__name__)


def format_validation_result(result: ValidationResult) -> str:
    """Format validation result as readable text."""
    lines = [
        "=" * 60,
        "TABLE SPECIFICATION VALIDATION REPORT",
        "=" * 60,
        "",
        f"Status: {'✓ VALID' if result.is_valid else '✗ INVALID'}",
        f"Errors: {len(result.errors)}",
        f"Warnings: {len(result.warnings)}",
        "",
    ]

    if result.errors:
        lines.extend([
            "=" * 60,
            "ERRORS",
            "=" * 60,
            "",
        ])
        for error in result.errors:
            lines.append(f"  [{error.category.upper()}] {error}")
            lines.append(f"    Location: {error.location}")
            lines.append(f"    Message: {error.message}")
            lines.append("")

    if result.warnings:
        lines.extend([
            "=" * 60,
            "WARNINGS",
            "=" * 60,
            "",
        ])
        for warning in result.warnings:
            lines.append(f"  [{warning.category.upper()}] {warning}")
            lines.append(f"    Location: {warning.location}")
            lines.append(f"    Message: {warning.message}")
            lines.append("")

    lines.extend([
        "=" * 60,
        "",
    ])

    return "\n".join(lines)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate table specification document"
    )
    parser.add_argument(
        "spec_file",
        help="Path to table_specification.json file",
    )
    parser.add_argument(
        "--metadata-file",
        "-m",
        help="Path to filtered_metadata.json for reference validation",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings as well as errors",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Save validation report to file",
    )

    args = parser.parse_args()

    # Read specification
    with open(args.spec_file) as f:
        spec = json.load(f)

    # Read metadata if provided
    metadata = None
    if args.metadata_file:
        with open(args.metadata_file) as f:
            metadata = json.load(f)

    # Validate
    result = validate_specification(
        spec=spec,
        metadata=metadata,
        strict=args.strict,
    )

    # Format and output
    report = format_validation_result(result)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Validation report saved to: {args.output}")
    else:
        print(report)

    # Exit with appropriate code
    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
