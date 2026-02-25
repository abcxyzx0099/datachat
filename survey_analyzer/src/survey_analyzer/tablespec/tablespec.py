"""
Table Specification Module (Unified)

Stage 4: Classify indicators as row/column using LLM.
Updates the unified table_specification.jsonc file by adding is_row/is_column fields.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

try:
    from zai import ZhipuAiClient
    ZAI_SDK_AVAILABLE = True
except ImportError:
    ZAI_SDK_AVAILABLE = False


class TableSpec:
    """
    Table Specification - Stage 4 Classification.

    Uses LLM to classify indicators as row or column.
    Updates the unified table_specification.jsonc file directly.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4.7"):
        """Initialize the TableSpec classifier."""
        if not ZAI_SDK_AVAILABLE:
            raise ImportError("zai-sdk package is required. Install with: pip install zai-sdk")

        # Load API key
        load_dotenv()
        self.api_key = api_key or os.getenv("GLM_API_KEY") or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError("Zhipu API key not found. Set ZHIPU_API_KEY or GLM_API_KEY in .env")

        self.model = model
        self.client = ZhipuAiClient(api_key=self.api_key)

        # Load prompts
        self.system_prompt = self._load_system_prompt()
        self.user_prompt_template = self._load_user_prompt_template()

    def classify_from_file(
        self,
        spec_file: str,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Stage 4: Classify all indicators in the spec file.

        Adds is_row and is_column fields to each indicator.

        Args:
            spec_file: Path to table_specification.jsonc
            output_file: Output path (default: same as spec_file)

        Returns:
            The updated specification dictionary
        """
        if output_file is None:
            output_file = spec_file

        # Load spec
        spec = self._load_spec(spec_file)

        # Collect all indicators
        all_indicators = []
        for question in spec.get("questions", []):
            for ind in question.get("indicators", []):
                all_indicators.append({
                    "indicator_code": ind["indicator_code"],
                    "indicator_label": ind.get("indicator_label", ""),
                    "question_type": question.get("question_type", "")
                })

        print(f"Loaded {len(all_indicators)} indicators for classification")

        # Classify using LLM
        classifications = self._classify_with_llm(all_indicators)

        # Apply classifications
        row_count = 0
        col_count = 0
        both_count = 0

        for question in spec.get("questions", []):
            for ind in question.get("indicators", []):
                code = ind["indicator_code"]
                if code in classifications:
                    cls = classifications[code]
                    ind["is_row"] = cls["is_row"]
                    ind["is_column"] = cls["is_column"]

                    if cls["is_row"] and cls["is_column"]:
                        both_count += 1
                    elif cls["is_row"]:
                        row_count += 1
                    elif cls["is_column"]:
                        col_count += 1
                else:
                    # Default to row indicator
                    ind["is_row"] = True
                    ind["is_column"] = False
                    row_count += 1

        # Update metadata
        spec["metadata"]["stage"] = "classification_complete"
        spec["metadata"]["last_updated"] = datetime.now().isoformat()

        # Add to history
        history = spec["metadata"].get("stage_history", [])
        if not any(h.get("stage") == 4 for h in history):
            history.append({
                "stage": 4,
                "name": "classification_complete",
                "completed_at": datetime.now().isoformat(),
                "summary": {
                    "row_indicators": row_count,
                    "column_indicators": col_count,
                    "both_indicators": both_count
                }
            })
        spec["metadata"]["stage_history"] = history

        # Save
        self._save_spec(spec, output_file)

        # Print summary
        print(f"\n[Classification Complete]")
        print(f"  Row indicators: {row_count}")
        print(f"  Column indicators: {col_count}")
        print(f"  Both (row & column): {both_count}")
        print(f"  ✓ Saved to: {output_file}")

        return spec

    def _classify_with_llm(self, indicators: List[Dict]) -> Dict[str, Dict[str, bool]]:
        """Classify indicators using LLM."""
        # Build prompt
        indicators_text = json.dumps(indicators, ensure_ascii=False, indent=2)
        user_prompt = self.user_prompt_template.format(indicators_list=indicators_text)

        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

        # Parse response
        content = response.choices[0].message.content
        return self._parse_classification_response(content)

    def _parse_classification_response(self, content: str) -> Dict[str, Dict[str, bool]]:
        """Parse LLM classification response."""
        import re

        # Remove markdown code blocks
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse LLM response as JSON: {content[:500]}...")

        # Extract classifications
        classifications = {}
        if "classifications" in data:
            for item in data["classifications"]:
                code = item.get("indicator_code")
                is_row = item.get("is_row", False)
                is_column = item.get("is_column", False)
                if code:
                    classifications[code] = {"is_row": is_row, "is_column": is_column}

        return classifications

    def _load_spec(self, spec_file: str) -> Dict[str, Any]:
        """Load unified spec file."""
        with open(spec_file, "r", encoding="utf-8") as f:
            content = f.read()
            # Strip JSONC comments
            lines = [line for line in content.split("\n") if not line.strip().startswith("//")]
            content = "\n".join(lines)
            return json.loads(content)

    def _save_spec(self, spec: Dict[str, Any], output_path: str) -> None:
        """Save unified spec file with JSONC comments."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("// ============================================\n")
            f.write("// Unified Table Specification\n")
            f.write("// Stage 4: Classification complete\n")
            f.write("// ============================================\n\n")
            json.dump(spec, f, indent=2, ensure_ascii=False)
            f.write("\n")

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        prompt_dir = Path(__file__).parent
        prompt_file = prompt_dir / "classification_prompt.md"

        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")
            if lines[0].startswith("#"):
                return "\n".join(lines[1:]).strip()
            return content.strip()

        return self._get_default_system_prompt()

    def _load_user_prompt_template(self) -> str:
        """Load user prompt template from file."""
        prompt_dir = Path(__file__).parent
        prompt_file = prompt_dir / "user_prompt.md"

        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")
            if lines[0].startswith("#"):
                content = "\n".join(lines[1:])
            return content.strip()

        return self._get_default_user_prompt()

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt."""
        return """You are an expert in survey data analysis and cross-tabulation design. Classify survey indicators as either row indicators or column indicators.

## Classification Rules

### Row Indicators (`is_row=true`, `is_column=false`)
These are the **main research topics and questions** being analyzed:
- Purchase intention and behavior questions
- Usage patterns and frequency
- Satisfaction ratings
- Brand perceptions and preferences
- Feature importance ratings
- Attitude and opinion questions
- Questions typically starting with **Q** (research questions)

### Column Indicators (`is_row=false`, `is_column=true`)
These are **demographic and segmentation variables** used to break down the data:
- Gender, Age, City Tier
- Income, Education, Occupation
- Marital Status, Household Size
- Car Ownership, Buyer Type
- Questions typically starting with **S** (screener/demographics) or **F** (family/household)

### Both (`is_row=true`, `is_column=true`)
Variables that can serve both purposes:
- Vehicle Type Preference (can be a research topic OR segmentation)
- First Time Buyer (can be analyzed OR used as segment)

Return ONLY valid JSON, no markdown formatting, no additional text."""

    def _get_default_user_prompt(self) -> str:
        """Get default user prompt."""
        return """Please classify the following indicators as row or column for cross-tabulation analysis.

## Indicators to Classify

```json
{indicators_list}
```

## Your Task

For each indicator above, determine:
- **`is_row`**: Set to `true` if this is a main research topic/question (content variable)
- **`is_column`**: Set to `true` if this is a demographic/segmentation variable

### Guidelines:
- Questions about purchase intent, usage, satisfaction, preferences → **Row**
- Questions about gender, age, income, education, location → **Column**
- Some variables can be both (e.g., vehicle type, buyer type)

## Required Output Format

Return ONLY valid JSON in this exact format:

```json
{{
  "classifications": [
    {{"indicator_code": "CODE1", "is_row": true, "is_column": false}},
    {{"indicator_code": "CODE2", "is_row": false, "is_column": true}},
    {{"indicator_code": "CODE3", "is_row": true, "is_column": true}}
  ]
}}
```

**Important:**
- Return ONLY the JSON, no markdown code blocks
- No additional text or explanations
- All indicators must be classified"""


def main():
    """CLI entry point for classification."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Classify indicators as row/column (Stage 4)"
    )
    parser.add_argument(
        "--spec-file",
        required=True,
        help="Path to table_specification.jsonc"
    )
    parser.add_argument(
        "--output-file",
        help="Output path (default: same as spec-file)"
    )

    args = parser.parse_args()

    # Classify
    classifier = TableSpec()
    classifier.classify_from_file(
        spec_file=args.spec_file,
        output_file=args.output_file
    )


if __name__ == "__main__":
    main()
