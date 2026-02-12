"""
Stage 2: Table Specification - AI-Orchestrated

Generates consolidated table_specification.json from survey metadata.
Uses Anthropic Claude API for AI-orchestrated specification generation.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    from anthropic import Anthropic
except ImportError:
    print("❌ Error: anthropic library not found")
    print("   Install: pip install anthropic")
    sys.exit(1)


def build_prompt(metadata: Dict[str, Any]) -> str:
    """Build prompt for Claude to generate table specification."""

    variable_summary = []
    for var_name, var_info in metadata.items():
        var_type = var_info.get("variable_type", "unknown")
        value_labels = var_info.get("value_labels", {})

        if var_type == "categorical":
            label = var_info.get("label", var_name)
            values_desc = ", ".join(f"{k}: {v}" for k, v in value_labels.items())
            variable_summary.append(f"- **{var_name}** ({label}): {var_type}, values: {values_desc}")
        elif var_type == "ordinal":
            label = var_info.get("label", var_name)
            values_desc = ", ".join(f"{k}: {v}" for k, v in value_labels.items())
            variable_summary.append(f"- **{var_name}** ({label}): {var_type}, ordered values: {values_desc}")
        else:
            label = var_info.get("label", var_name)
            variable_summary.append(f"- **{var_name}** ({label}): {var_type}")

    variables_text = "\n".join(variable_summary)

    prompt = f"""Generate a table specification for survey analysis.

Survey Variables:
{variables_text}

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

Generate practical indicators and tables for market research analysis.
Include recoding rules for data cleaning.
Apply appropriate statistical significance thresholds.
"""

    return prompt


def extract_json_from_response(response_text: str) -> Optional[str]:
    """Extract JSON from Claude API response.

    Handles various JSON extraction patterns:
    - JSON code blocks with ```json...```
    - Direct JSON objects
    - JSON embedded in text
    """
    # Try code block pattern first
    code_block_match = re.search(r'```json\s*([\s\S]+?)\s*```', response_text)
    if code_block_match:
        return code_block_match.group(1).strip()

    # Try direct JSON object
    # Look for opening brace and extract until matching closing brace
    json_start = response_text.find('{')
    if json_start != -1:
        brace_count = 0
        for char in response_text[json_start:]:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            if brace_count == 0:
                json_end = response_text.find('}', json_start) + 1
                return response_text[json_start:json_end + 1]

    # Try array pattern
    array_match = re.search(r'\[[\s\S]+?\s*(?:\s*,\s*[\s\S]+?\s*)\s*\]', response_text)
    if array_match:
        return array_match.group(0)

    return None


def validate_spec_json(spec_json: str) -> tuple[bool, Optional[str]]:
    """Validate the generated specification JSON."""
    try:
        spec = json.loads(spec_json)

        # Basic structure validation
        required_fields = ["version", "generated_at", "source_file"]
        for field in required_fields:
            if field not in spec:
                return False, f"Missing required field: {field}"

        # Validate arrays exist
        if "global_recodings" not in spec:
            spec["global_recodings"] = []
        if "indicators" not in spec:
            spec["indicators"] = []
        if "tables" not in spec:
            spec["tables"] = []

        # Validate content has meaningful data
        if not spec.get("indicators") and not spec.get("tables"):
            return False, "No indicators or tables defined"

        return True, None

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def main():
    """Main entry point for stage2-spec-gen skill."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate table_specification.json (AI-orchestrated)"
    )
    parser.add_argument("--metadata-file", required=True,
                        help="Path to filtered_metadata.json from Stage 1")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory")
    parser.add_argument("--api-key", help="Anthropic API key (or ANTHROPIC_API_KEY env var)")
    parser.add_argument("--model", default="claude-sonnet-4-20250929",
                        help="Claude model to use")

    args = parser.parse_args()

    # Set up paths
    metadata_file = args.metadata_file
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    spec_file = output_dir / "table_specification.json"

    # Get API key
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not set")
        print("   Set environment variable or pass --api-key")
        sys.exit(1)

    print("📋 Stage 2: Table Specification")
    print("=" * 60)

    # Load metadata
    print("\n📖 Loading filtered metadata...")
    if not Path(metadata_file).exists():
        print(f"❌ Error: Metadata file not found: {metadata_file}")
        print(f"   Run Stage 1 first: stage1-data-prep")
        sys.exit(1)

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    print(f"   Loaded {len(metadata)} variables")

    # Build prompt
    print("\n🤖 Building AI prompt...")
    prompt = build_prompt(metadata)

    # Call Anthropic API
    print("\n🌐 Calling Claude API...")
    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=args.model,
            max_tokens=4000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract JSON from response
        response_text = response.content[0].text
        spec_json = extract_json_from_response(response_text)

        if not spec_json:
            print("❌ Error: Could not extract JSON from response")
            print(f"   Response: {response_text[:500]}...")
            sys.exit(1)

        # Validate specification
        print("\n✅ Validating specification...")
        is_valid, error_msg = validate_spec_json(spec_json)

        if not is_valid:
            print(f"❌ Validation failed: {error_msg}")
            print("\n💡 Suggestion: Review the prompt and try again")
            sys.exit(1)

        # Add metadata to specification
        spec = json.loads(spec_json)
        spec["generated_at"] = None  # Will be set by save
        spec["source_file"] = metadata.get("source_file", "unknown")

        # Save specification
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(spec_file, 'w') as f:
            json.dump(spec, f, indent=2)

        print(f"\n✅ Table specification generated!")
        print(f"   Indicators: {len(spec.get('indicators', []))}")
        print(f"   Tables: {len(spec.get('tables', []))}")
        print(f"   Output: {spec_file}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
