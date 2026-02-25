# User Prompt Template for Indicator Generation

Please generate a table specification indicator for the following question:

**Question Code:** {question_code}

**Variables:**
```json
{variable_details}
```

{EXAMPLES_PLACEHOLDER}

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

Return ONLY valid JSON, no additional text.
