# User Prompt for Indicator Classification

Please classify the following indicators as row or column for cross-tabulation analysis.

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
- All indicators must be classified
