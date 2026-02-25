"""
Unified Table Specification Module

Big Bang implementation - single source of truth for table specification.
All stages update the same table_specification.jsonc file.

Structure:
    metadata          - Project info, stage tracking
    questions         - Array of questions with nested indicators
    filter_clause     - Filtering rules
    weight_indicator  - Weighting variable

Stages:
    Stage 2: Add questions with empty indicators array
    Stage 3: Add indicators to each question
    Stage 4: Add is_row/is_column to indicators
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import os

try:
    from zai import ZhipuAiClient
    ZAI_SDK_AVAILABLE = True
except ImportError:
    ZAI_SDK_AVAILABLE = False


class UnifiedTableSpec:
    """
    Unified table specification - single source of truth.

    All stages update this single file:
    - Stage 2: Creates structure with questions (indicators = [])
    - Stage 3: Adds indicators to each question
    - Stage 4: Adds is_row/is_column classification
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4.7"):
        """Initialize the unified table specification."""
        self.spec = None
        self.file_path = None
        self.api_key = api_key
        self.model = model
        self.client = None

        if ZAI_SDK_AVAILABLE:
            self._init_llm()

    def _init_llm(self):
        """Initialize LLM client for Stage 4 classification."""
        load_dotenv()
        self.api_key = self.api_key or os.getenv("GLM_API_KEY") or os.getenv("ZHIPU_API_KEY")
        if self.api_key:
            self.client = ZhipuAiClient(api_key=self.api_key)

    # ========================================================================
    # File Operations
    # ========================================================================

    def create(self, file_path: str, **metadata) -> Dict[str, Any]:
        """
        Create a new unified table specification file.

        Args:
            file_path: Path to save table_specification.jsonc
            **metadata: Additional metadata (project_id, dataset_id, source_file, etc.)

        Returns:
            The created specification dictionary
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        self.spec = {
            "metadata": {
                "spec_id": f"tablespec_{metadata.get('project_id', 'proj')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "project_id": metadata.get("project_id", "proj_survey"),
                "dataset_id": metadata.get("dataset_id", "ds_survey_data"),
                "source_file": metadata.get("source_file", "unknown.sav"),
                "case_count": metadata.get("case_count", 0),
                "stage": "initialized",
                "generated_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "stage_history": []
            },
            "questions": [],
            "filter_clause": {
                "exclude_incomplete": True,
                "valid_cases_only": True
            },
            "weight_indicator": None
        }

        self._save()
        return self.spec

    def load(self, file_path: str) -> Dict[str, Any]:
        """
        Load existing table specification file.

        Args:
            file_path: Path to table_specification.jsonc

        Returns:
            The loaded specification dictionary
        """
        self.file_path = Path(file_path)

        with open(self.file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Strip JSONC comments
            lines = [line for line in content.split("\n") if not line.strip().startswith("//")]
            content = "\n".join(lines)
            self.spec = json.loads(content)

        return self.spec

    def save(self) -> None:
        """Save the current specification to file."""
        if not self.file_path:
            raise ValueError("No file_path set. Call create() or load() first.")

        self.spec["metadata"]["last_updated"] = datetime.now().isoformat()
        self._save()

    def _save(self) -> None:
        """Internal save method."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("// ============================================\n")
            f.write("// Unified Table Specification\n")
            f.write("// Single source of truth for all stages\n")
            f.write("// ============================================\n\n")
            json.dump(self.spec, f, indent=2, ensure_ascii=False)
            f.write("\n")

    # ========================================================================
    # Stage Helpers
    # ========================================================================

    def update_stage(self, stage: int, stage_name: str) -> None:
        """Update the stage in metadata."""
        self.spec["metadata"]["stage"] = stage_name

        # Add to history if not already there
        history = self.spec["metadata"].get("stage_history", [])
        if not any(h.get("stage") == stage for h in history):
            history.append({
                "stage": stage,
                "name": stage_name,
                "completed_at": datetime.now().isoformat()
            })
        self.spec["metadata"]["stage_history"] = history

    # ========================================================================
    # Stage 2: Add Questions
    # ========================================================================

    def add_questions(
        self,
        questions: List[Dict[str, Any]]
    ) -> None:
        """
        Stage 2: Add questions to the specification.

        Args:
            questions: List of question dicts with:
                - question_code: str
                - question_type: str
                - question_text: str
                - original_variables: List[str]
        """
        for q in questions:
            # Check if question already exists
            existing = self._find_question(q["question_code"])
            if existing:
                continue

            # Add new question with empty indicators array
            self.spec["questions"].append({
                "question_code": q["question_code"],
                "question_type": q.get("question_type", ""),
                "question_text": q.get("question_text", ""),
                "original_variables": q.get("original_variables", []),
                "indicators": []
            })

        self.update_stage(2, "questions_extracted")
        self.save()

        print(f"✓ Added {len(questions)} questions")
        print(f"  Total questions: {len(self.spec['questions'])}")

    # ========================================================================
    # Stage 3: Add Indicators
    # ========================================================================

    def add_indicator(
        self,
        question_code: str,
        indicator: Dict[str, Any]
    ) -> None:
        """
        Stage 3: Add an indicator to a specific question.

        Args:
            question_code: The question code
            indicator: Indicator dict with:
                - indicator_code: str
                - indicator_label: str
                - indicator_variables: List[str]
                - transformation: str or null
                - tabulation_type: str
                - tabulation_metric: str
                - indicator_value_labels: dict or null
        """
        question = self._find_question(question_code)
        if not question:
            raise ValueError(f"Question {question_code} not found")

        # Add indicator without is_row/is_column (added in Stage 4)
        question["indicators"].append({
            "indicator_code": indicator["indicator_code"],
            "indicator_label": indicator.get("indicator_label", ""),
            "indicator_variables": indicator.get("indicator_variables", []),
            "transformation": indicator.get("transformation"),
            "tabulation_type": indicator.get("tabulation_type", "categorical"),
            "tabulation_metric": indicator.get("tabulation_metric", "column_percent"),
            "indicator_value_labels": indicator.get("indicator_value_labels")
        })

        self.update_stage(3, "indicators_generated")
        self.save()

    def add_indicators_batch(
        self,
        indicators: List[Dict[str, Any]]
    ) -> None:
        """
        Stage 3: Add multiple indicators.

        Args:
            indicators: List of indicator dicts, each with question_code
        """
        added = 0
        for ind in indicators:
            question_code = ind.get("question_code")
            indicator_data = {k: v for k, v in ind.items() if k != "question_code"}

            try:
                self.add_indicator(question_code, indicator_data)
                added += 1
            except ValueError:
                pass  # Question not found yet

        print(f"✓ Added {added} indicators")

    # ========================================================================
    # Stage 4: Classification (is_row/is_column)
    # ========================================================================

    def classify_indicators(self) -> None:
        """
        Stage 4: Classify indicators as row or column using LLM.

        Adds is_row and is_column fields to each indicator.
        """
        if not self.client:
            raise ValueError("LLM client not available. Cannot classify indicators.")

        # Collect all indicators for classification
        all_indicators = []
        for question in self.spec["questions"]:
            for ind in question["indicators"]:
                all_indicators.append({
                    "indicator_code": ind["indicator_code"],
                    "indicator_label": ind.get("indicator_label", ""),
                    "question_type": question.get("question_type", "")
                })

        # Classify using LLM
        classifications = self._llm_classify(all_indicators)

        # Apply classifications
        for question in self.spec["questions"]:
            for ind in question["indicators"]:
                code = ind["indicator_code"]
                if code in classifications:
                    ind["is_row"] = classifications[code]["is_row"]
                    ind["is_column"] = classifications[code]["is_column"]
                else:
                    # Default to row indicator
                    ind["is_row"] = True
                    ind["is_column"] = False

        self.update_stage(4, "classification_complete")
        self.save()

        # Print summary
        row_count = sum(1 for q in self.spec["questions"]
                       for ind in q["indicators"] if ind.get("is_row"))
        col_count = sum(1 for q in self.spec["questions"]
                       for ind in q["indicators"] if ind.get("is_column"))

        print(f"✓ Classification complete")
        print(f"  Row indicators: {row_count}")
        print(f"  Column indicators: {col_count}")

    # ========================================================================
    # Query Helpers
    # ========================================================================

    def get_row_indicators(self) -> List[Dict[str, Any]]:
        """Get all indicators where is_row = true."""
        return [
            {**ind, "question_code": q["question_code"]}
            for q in self.spec["questions"]
            for ind in q.get("indicators", [])
            if ind.get("is_row")
        ]

    def get_column_indicators(self) -> List[Dict[str, Any]]:
        """Get all indicators where is_column = true."""
        return [
            {**ind, "question_code": q["question_code"]}
            for q in self.spec["questions"]
            for ind in q.get("indicators", [])
            if ind.get("is_column")
        ]

    def get_indicator_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Find an indicator by its code."""
        for q in self.spec["questions"]:
            for ind in q.get("indicators", []):
                if ind["indicator_code"] == code:
                    return {**ind, "question_code": q["question_code"]}
        return None

    def get_all_indicators(self) -> List[Dict[str, Any]]:
        """Get all indicators with their question codes."""
        return [
            {**ind, "question_code": q["question_code"]}
            for q in self.spec["questions"]
            for ind in q.get("indicators", [])
        ]

    # ========================================================================
    # Internal Helpers
    # ========================================================================

    def _find_question(self, code: str) -> Optional[Dict[str, Any]]:
        """Find a question by code."""
        for q in self.spec.get("questions", []):
            if q["question_code"] == code:
                return q
        return None

    def _llm_classify(self, indicators: List[Dict]) -> Dict[str, Dict[str, bool]]:
        """Classify indicators using LLM."""
        # Build prompt
        indicators_text = json.dumps(indicators, ensure_ascii=False, indent=2)
        user_prompt = self._get_user_prompt().format(indicators_list=indicators_text)

        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
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

    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM classification."""
        prompt_file = Path(__file__).parent / "classification_prompt.md"
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")
            if lines[0].startswith("#"):
                return "\n".join(lines[1:]).strip()
            return content.strip()

        return self._get_default_system_prompt()

    def _get_user_prompt(self) -> str:
        """Get user prompt template for LLM classification."""
        prompt_file = Path(__file__).parent / "user_prompt.md"
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")
            if lines[0].startswith("#"):
                content = "\n".join(lines[1:])
            return content.strip()

        return self._get_default_user_prompt()

    def _get_default_system_prompt(self) -> str:
        """Default system prompt for classification."""
        return """You are an expert in survey data analysis and cross-tabulation design. Classify indicators as row or column.

## Classification Rules

### Row Indicators (`is_row=true`, `is_column=false`)
Main research topics and questions:
- Purchase intention and behavior
- Usage patterns and frequency
- Satisfaction ratings
- Brand perceptions
- Feature importance
- Attitude and opinion questions
- Questions typically starting with Q

### Column Indicators (`is_row=false`, `is_column=true`)
Demographic and segmentation variables:
- Gender, Age, City Tier
- Income, Education, Occupation
- Marital Status, Household Size
- Questions typically starting with S (screener) or F (family)

### Both (`is_row=true`, `is_column=true`)
Variables that can serve both purposes:
- Vehicle Type, Buyer Type

Return ONLY valid JSON, no markdown."""

    def _get_default_user_prompt(self) -> str:
        """Default user prompt for classification."""
        return """Classify these indicators:

```json
{indicators_list}
```

For each indicator, set:
- `is_row`: true if main research topic
- `is_column`: true if demographic/segmentation

Return ONLY JSON:
```json
{{
  "classifications": [
    {{"indicator_code": "CODE1", "is_row": true, "is_column": false}},
    {{"indicator_code": "CODE2", "is_row": false, "is_column": true}}
  ]
}}
```"""


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Unified table specification")
    parser.add_argument("--create", type=str, help="Create new spec file")
    parser.add_argument("--load", type=str, help="Load existing spec file")
    parser.add_argument("--save", action="store_true", help="Save current spec")
    args = parser.parse_args()

    spec = UnifiedTableSpec()

    if args.create:
        spec.create(args.create)
        print(f"✓ Created: {args.create}")
    elif args.load:
        spec.load(args.load)
        print(f"✓ Loaded: {args.load}")
        print(f"  Questions: {len(spec.spec.get('questions', []))}")


if __name__ == "__main__":
    main()
