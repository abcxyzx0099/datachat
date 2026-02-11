"""
Survey Specification Generator Skill

Generates a consolidated table specification document for SPSS survey analysis.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from anthropic import Anthropic

# Add library path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib"))

from spss_analyzer.specification import (
    TableSpecificationDocument,
    create_empty_spec,
    validate_spec_structure,
)

logger = logging.getLogger(__name__)


class SpecificationGenerator:
    """Generates table specification from metadata using AI."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize generator with Anthropic client."""
        self.client = Anthropic(api_key=api_key)

    def generate(
        self,
        metadata: Dict[str, Any],
        source_file: str = "",
        instructions: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 16000,
    ) -> TableSpecificationDocument:
        """
        Generate table specification from metadata.

        Args:
            metadata: Filtered variable metadata from SPSS file
            source_file: Name of source .sav file
            instructions: Additional instructions for generation
            model: Anthropic model to use
            max_tokens: Maximum tokens in response

        Returns:
            TableSpecificationDocument
        """
        # Create the prompt
        prompt = self._build_prompt(metadata, source_file, instructions)

        # Call Claude
        message = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        # Extract JSON from response
        response_text = message.content[0].text
        spec_dict = self._extract_json(response_text)

        # Validate structure
        errors = validate_spec_structure(spec_dict)
        if errors:
            logger.warning(f"Generated spec has structural issues: {errors}")
            # Still return, user can fix via validation skill

        # Parse into document
        spec = TableSpecificationDocument.from_dict(spec_dict)
        spec.source_file = source_file

        return spec

    def _build_prompt(
        self,
        metadata: Dict[str, Any],
        source_file: str,
        instructions: Optional[str],
    ) -> str:
        """Build the prompt for Claude."""
        prompt_parts = [
            "# Generate Table Specification for SPSS Survey Analysis",
            "",
            "You are an expert market research analyst. Generate a consolidated table ",
            "specification document for analyzing SPSS survey data.",
            "",
            "## Input Data",
            "",
            f"**Source File:** {source_file}",
            "",
            "### Variable Metadata",
            "",
            "```json",
            json.dumps(metadata, indent=2),
            "```",
            "",
        ]

        if instructions:
            prompt_parts.extend([
                "",
                "## Additional Instructions",
                "",
                instructions,
            ])

        prompt_parts.extend([
            "",
            "## Output Requirements",
            "",
            "Generate a JSON document with the following structure:",
            "",
            "```json",
            "{",
            '  "metadata": {',
            '    "version": "1.0",',
            '    "generated_at": "<timestamp>",',
            '    "source_file": "' + source_file + '"',
            "  },",
            '  "global_recodings": [...],  // Recoding rules for variables',
            '  "indicators": [...],       // Indicator definitions',
            '  "tables": [...],           // Table specifications',
            '  "output_settings": {...}    // Output configuration',
            "}",
            "```",
            "",
            "## Guidelines",
            "",
            "### Indicators",
            "- Group related variables (e.g., q1-q5 satisfaction questions)",
            "- Use appropriate aggregation (mean for ratings, sum for counts)",
            "- Include recoding if values need transformation",
            "",
            "### Recoding Rules",
            "- Age: Group into meaningful ranges (18-25, 26-40, 41-50, 51+)",
            "- Rating scales: Consider reverse coding if needed",
            "- Consolidate small categories into 'Other'",
            "",
            "### Tables",
            "- 15-25 tables total (not excessive)",
            "- Include:",
            "  - Demographic crosstabs (key metrics by age, gender, region)",
            "  - Indicator comparisons (indicators by demographics)",
            "  - Frequency distributions (key categorical variables)",
            "- Each table needs: id, title, type, rows/columns, metrics",
            "",
            "### Metrics",
            "- Standard set: count (n), row_percent (Row %), column_percent (Column %)",
            "- For summary tables: mean, median, std_dev",
            "",
            "### Output Settings",
            "- significance_threshold: 0.05",
            "- include_powerpoint: true",
            "- include_html_dashboard: true",
            "- max_tables_ppt: 20 (significant tables only)",
            "",
            "## Response Format",
            "",
            "Respond ONLY with valid JSON. No markdown, no explanations, just the JSON.",
            "",
        ])

        return "\n".join(prompt_parts)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from response text."""
        # Remove markdown code blocks if present
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.rfind("```")
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.rfind("```")
            text = text[start:end].strip()

        return json.loads(text)


def main():
    """CLI entry point for testing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate table specification from SPSS metadata"
    )
    parser.add_argument(
        "metadata_file",
        help="Path to filtered_metadata.json file",
    )
    parser.add_argument(
        "--source-file",
        default="survey_data.sav",
        help="Source .sav file name",
    )
    parser.add_argument(
        "--instructions",
        help="Additional instructions for generation",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="table_specification.json",
        help="Output file path",
    )
    parser.add_argument(
        "--api-key",
        help="Anthropic API key (default: from ANTHROPIC_API_KEY env var)",
    )

    args = parser.parse_args()

    # Read metadata
    with open(args.metadata_file) as f:
        metadata = json.load(f)

    # Generate specification
    generator = SpecificationGenerator(api_key=args.api_key)
    spec = generator.generate(
        metadata=metadata,
        source_file=args.source_file,
        instructions=args.instructions,
    )

    # Save specification
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(spec.to_dict(), f, indent=2)

    print(f"Table specification saved to: {output_path}")
    print(f"  - {len(spec.indicators)} indicators")
    print(f"  - {len(spec.tables)} tables")
    print(f"  - {len(spec.global_recodings)} recoding rules")


if __name__ == "__main__":
    main()
