"""
Indicator Generator Module

Generates table specification indicators using LLM (GLM-4.7) API.
Stage 3: Creates indicators without is_row/is_column fields.
These fields are added later by Stage 4: tablespec.TableSpec.

Classes:
    IndicatorGenerator: Generate indicators for a single question using LLM
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

try:
    from zai import ZhipuAiClient
    ZAI_SDK_AVAILABLE = True
except ImportError:
    ZAI_SDK_AVAILABLE = False


class IndicatorGenerator:
    """
    Generate table specification indicators using GLM-4.7 LLM.

    This class handles:
    1. Loading configuration from .env file
    2. Calling GLM-4.7 API to generate indicators for a question
    3. Parsing and validating the LLM response
    4. Returning indicator WITHOUT is_row/is_column fields (added in Stage 4)

    Configuration via .env file:
        ZHIPU_API_KEY=your_api_key_here
        # or
        GLM_API_KEY=your_api_key_here

    Uses the new zai-sdk (ZhipuAiClient).
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4.7"):
        """
        Initialize the IndicatorGenerator.

        Args:
            api_key: GLM API key (if None, loads from .env file)
            model: Model name to use (default: "glm-4.7")

        Raises:
            ImportError: If zai-sdk is not installed
            ValueError: If API key is not provided or found in .env
        """
        if not ZAI_SDK_AVAILABLE:
            raise ImportError(
                "zai-sdk package is required for IndicatorGenerator. "
                "Install with: pip install zai-sdk"
            )

        # Load API key from parameter or .env file
        # Try to find .env file by searching upward from current directory
        load_dotenv()
        # Also try loading from project root if not found
        if not (os.getenv("GLM_API_KEY") or os.getenv("ZHIPU_API_KEY")):
            # Try to find .env in parent directories
            current_dir = Path.cwd()
            for _ in range(5):  # Search up to 5 levels up
                env_file = current_dir / ".env"
                if env_file.exists():
                    load_dotenv(env_file)
                    break
                current_dir = current_dir.parent

        self.api_key = api_key or os.getenv("GLM_API_KEY") or os.getenv("ZHIPU_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Zhipu API key not found. "
                "Set ZHIPU_API_KEY (or GLM_API_KEY) in .env file or pass as parameter."
            )

        self.model = model
        self.client = ZhipuAiClient(api_key=self.api_key)

        # Load prompts from files
        self.system_prompt = self._load_system_prompt()
        self.user_prompt_template = self._load_user_prompt_template()

    def generate_for_question(
        self,
        question_code: str,
        variables: List[str],
        metadata: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate indicator(s) for a single question.

        Args:
            question_code: Question code (e.g., "Q2A")
            variables: List of variable names for this question
            metadata: Full filtered_metadata dictionary
            system_prompt: Optional custom system prompt

        Returns:
            Dictionary with generated indicator(s). Structure:
                {
                    "indicator_code": "Q2A_USAGE",
                    "indicator_label": "...",
                    "question_code": "Q2A",
                    "question_type": "Multiple Choice",
                    "tabulation_type": "categorical",
                    "tabulation_metric": "column_percent",
                    "base_variables": {"Q2A_1_bin": "...", "Q2A_2_bin": "..."},
                    "base_variables_transformations": null,
                    "base_variables_value_labels": {"1": "是", "0": "否"}
                }

        Note: is_row and is_column fields are NOT added here.
        They are added later by Stage 4: analyzer-tablespec.

        Raises:
            Exception: If LLM API call fails
        """
        # Build variable details for the prompt
        variable_details = self._build_variable_details(variables, metadata)

        # Build the user prompt
        user_prompt = self._build_prompt(question_code, variable_details)

        # Use provided system prompt or load from file
        if system_prompt is None:
            system_prompt = self.system_prompt

        # Call LLM API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

        # Parse response
        content = response.choices[0].message.content
        indicator = self._parse_response(content, question_code)

        # Return indicator WITHOUT is_row/is_column fields
        # Those fields are added by Stage 4: analyzer-tablespec
        return indicator

    def _get_prompts_dir(self) -> Path:
        """Get the prompts directory (same directory as this module)."""
        # Prompts are co-located with the indicators module
        return Path(__file__).parent

    def _load_system_prompt(self) -> str:
        """Load system prompt from file."""
        prompts_dir = self._get_prompts_dir()
        system_prompt_file = prompts_dir / "system_prompt.md"

        if system_prompt_file.exists():
            with open(system_prompt_file, "r", encoding="utf-8") as f:
                content = f.read()
            # Remove the title/header line if present
            lines = content.split("\n")
            if lines[0].startswith("#"):
                return "\n".join(lines[1:]).strip()
            return content.strip()

        # Fallback to hardcoded prompt
        return self._get_default_system_prompt()

    def _load_user_prompt_template(self) -> str:
        """Load user prompt template from file."""
        prompts_dir = self._get_prompts_dir()
        user_prompt_file = prompts_dir / "user_prompt.md"

        if user_prompt_file.exists():
            with open(user_prompt_file, "r", encoding="utf-8") as f:
                content = f.read()
            # Remove the title/header line if present
            lines = content.split("\n")
            if lines[0].startswith("#"):
                content = "\n".join(lines[1:])

            # Load and insert examples using placeholder replacement
            examples = self._load_examples()
            content = content.replace("{EXAMPLES_PLACEHOLDER}", examples)
            return content.strip()

        # Fallback to hardcoded prompt (for backward compatibility)
        examples = self._load_examples()
        return """Please generate a table specification indicator for the following question:

**Question Code:** {question_code}

**Variables:**
```json
{variable_details}
```

""" + examples + """

## Your Task

Generate the indicator specification in JSON format with the following structure:

```json
{{
  "indicator_code": "DESCRIPTIVE_CODE",
  "indicator_label": "Question text from variable_label",
  "question_code": "{question_code}",
  "question_type": "Single Choice or Multiple Choice or Matrix or Rating Scale",
  "tabulation_type": "categorical or scalar",
  "tabulation_metric": "column_percent or descriptive_statistics",
  "base_variables": {{"VAR_NAME": "Label from variable_label or value_labels", ...}},
  "base_variables_transformations": null or "SPSS transformation syntax",
  "base_variables_value_labels": {{"value": "label", ...}}
}}
```

Return ONLY valid JSON, no additional text."""

    def _load_examples(self) -> str:
        """Load examples from examples.jsonc file."""
        prompts_dir = self._get_prompts_dir()
        examples_file = prompts_dir / "examples.jsonc"

        if examples_file.exists():
            with open(examples_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse JSONC (strip comments before parsing)
            import re
            # Remove single-line comments (// ...)
            content_no_comments = re.sub(r'//.*', '', content)
            # Remove multi-line comments (/* ... */)
            content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)

            try:
                data = json.loads(content_no_comments)

                # Extract examples from unified indicators section
                examples = []

                if "indicators" in data:
                    # Use all examples from the indicators section
                    for idx, indicator in enumerate(data["indicators"], 1):
                        examples.append(self._format_example(idx, indicator))

                return "\n\n".join(examples)

            except json.JSONDecodeError:
                # If parsing fails, fall back to embedded examples
                pass

        # Fallback: return embedded examples
        return """## Examples

### Example 1: Single Choice (Gender)
```json
{{
  "indicator_code": "GENDER",
  "indicator_label": "请问您的性别是？(单选)",
  "question_code": "S0",
  "question_type": "Single Choice",
  "tabulation_type": "categorical",
  "tabulation_metric": "column_percent",
  "base_variables": {{
    "S0": "请问您的性别是？(单选)"
  }},
  "base_variables_transformations": null,
  "base_variables_value_labels": {{
    "1.0": "男",
    "2.0": "女"
  }}
}}
```

### Example 2: Multiple Choice (Usage)
```json
{{
  "indicator_code": "Q2A_USAGE",
  "indicator_label": "Q2A - 请问您要购买的新车通常将如何使用？",
  "question_code": "Q2A",
  "question_type": "Multiple Choice",
  "tabulation_type": "categorical",
  "tabulation_metric": "column_percent",
  "base_variables": {{
    "Q2A_1_bin": "上/下班用",
    "Q2A_2_bin": "和家庭成员/朋友/同事一起出外娱乐聚餐",
    "Q2A_3_bin": "去购物"
  }},
  "base_variables_transformations": null,
  "base_variables_value_labels": {{
    "1": "是",
    "0": "否"
  }}
}}
```"""

    def _format_example(self, idx: int, indicator: Dict[str, Any]) -> str:
        """Format a single indicator example for the prompt."""
        question_type = indicator.get("question_type", "Unknown")

        # Create description based on question type
        description = f"{question_type}"
        if question_type == "Single Choice":
            var_count = len(indicator.get("base_variables", {}))
            description += f" - {var_count} variable with {len(indicator.get('base_variables_value_labels', {}))} categories"
        elif question_type == "Multiple Choice":
            var_count = len(indicator.get("base_variables", {}))
            description += f" - {var_count} binary variables (0/1, Yes/No)"
        elif question_type == "Rating Scale":
            var_count = len(indicator.get("base_variables", {}))
            description += f" - {var_count} attribute(s)"

        example_json = json.dumps(indicator, ensure_ascii=False, indent=2)

        return f"""### Example {idx}: {description}

```json
{example_json}
```"""

    def _build_variable_details(
        self,
        variables: List[str],
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build variable details list for the prompt."""
        details = []
        for var_name in variables:
            if var_name in metadata:
                var_info = metadata[var_name]
                details.append({
                    "variable_name": var_name,
                    "variable_label": var_info.get("variable_label", ""),
                    "value_labels": var_info.get("value_labels", {})
                })
        return details

    def _build_prompt(
        self,
        question_code: str,
        variable_details: List[Dict[str, Any]]
    ) -> str:
        """Build the user prompt for LLM."""
        # Format variable details for the prompt
        vars_text = json.dumps(variable_details, ensure_ascii=False, indent=2)

        # Use loaded prompt template (already includes examples)
        return self.user_prompt_template.format(
            question_code=question_code,
            variable_details=vars_text
            # examples are already included in user_prompt_template
        )

    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for LLM."""
        return """You are an expert in survey data analysis and SPSS data processing. Your task is to generate table specification indicators for cross-tabulation analysis.

Rules:
1. indicator_code: Use uppercase, descriptive name (e.g., "Q2A_USAGE", "GENDER")
2. indicator_label: Use the full question text from variable_label
3. question_type: Determine from variable structure:
   - Single Choice: One variable with multiple categories
   - Multiple Choice: Multiple binary variables (0/1, Yes/No)
   - Matrix: Multiple related variables with same scale
   - Rating Scale: Variables with ordered categories (1-5, 1-7, etc.)
4. tabulation_type: Use "categorical" for choice questions, "scalar" for numeric ratings
5. tabulation_metric: Use "column_percent" for categorical, "descriptive_statistics" for scalar
6. base_variables: Map variable names to their labels
7. base_variables_transformations: Use null unless recoding is needed
8. base_variables_value_labels: Include all value labels from the variables

Return ONLY valid JSON, no markdown formatting, no additional text."""

    def _parse_response(self, content: str, question_code: str) -> Dict[str, Any]:
        """
        Parse the LLM response and extract JSON.

        Args:
            content: Raw response content from LLM
            question_code: Question code for error messages

        Returns:
            Parsed indicator dictionary

        Raises:
            ValueError: If response cannot be parsed as valid JSON
        """
        # Try to extract JSON from response
        content = content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Parse JSON
        try:
            indicator = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse LLM response for question '{question_code}' as JSON. "
                f"Error: {e}. Response content: {content[:500]}..."
            )

        # Validate required fields
        required_fields = [
            "indicator_code", "indicator_label", "question_code",
            "question_type", "tabulation_type", "tabulation_metric",
            "base_variables", "base_variables_value_labels"
        ]
        for field in required_fields:
            if field not in indicator:
                raise ValueError(
                    f"Missing required field '{field}' in indicator for question '{question_code}'"
                )

        return indicator


def main() -> None:
    """CLI entry point for testing indicator generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate indicator for a single question using GLM-4.7"
    )
    parser.add_argument(
        "--question-code",
        required=True,
        help="Question code (e.g., Q2A)"
    )
    parser.add_argument(
        "--metadata-file",
        required=True,
        help="Path to filtered_metadata.json"
    )
    parser.add_argument(
        "--variables",
        nargs="+",
        help="List of variable names for this question"
    )
    parser.add_argument(
        "--output-file",
        help="Output JSON file (optional)"
    )

    args = parser.parse_args()

    # Load metadata
    with open(args.metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Generate indicator
    generator = IndicatorGenerator()
    indicator = generator.generate_for_question(
        args.question_code,
        args.variables or [],
        metadata
    )

    # Output
    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as f:
            json.dump(indicator, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved indicator to: {args.output_file}")
    else:
        print(json.dumps(indicator, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
