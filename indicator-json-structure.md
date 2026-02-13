# Indicator JSON Structure

```json
{
  "indicators": [
    {
      "indicator_code": "string",
      "question_type": "MultiSelect | Frequency | Rating | Single | Matrix | Ranking | Numeric",
      "indicator_label": "string",
      "source_variables": {
        "var_code": "var_label"
      },
      "transformation_needed": false,
      "transformation_type": "grouping | recoding | range | null",
      "transformation_rules": null | [
        {
          "source_values": ["value1", "value2"] | {"min": number, "max": number},
          "target_value": "string",
          "target_label": "string",
          "hide_categories": boolean
        }
      ]
    }
  ]
}
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `indicator_code` | string | Unique identifier (base variable name) |
| `question_type` | enum | Question/response type |
| `indicator_label` | string | Question text |
| `source_variables` | object | Map of SPSS variable code → variable label |
| `transformation_needed` | boolean | Whether transformation is required |
| `transformation_type` | enum or null | Type of transformation |
| `transformation_rules` | array or null | Transformation rule items with 4 fields |

## Transformation Rules (4 Fields)

| Field | Type | Description |
|-------|------|-------------|
| `source_values` | array or object | Source values: `["1", "2"]` or `{"min": 18, "max": 25}` |
| `target_value` | string | Target value code |
| `target_label` | string | Target value label |
| `hide_categories` | boolean | Hide component categories in output |

## Question Types

| Value | Description |
|-------|-------------|
| `MultiSelect` | Checkboxes (each var has single "1.0" value) |
| `Frequency` | "How often?" (daily/weekly/每天/每周) |
| `Rating` | 3-7 point identical scale |
| `Single` | Standalone categorical |
| `Matrix` | Grid with double suffix (`_1_1`, `_1_2`) |
| `Ranking` | Rank order (rank/first/排名/第一) |
| `Numeric` | Continuous data (empty value_labels) |

## Transformation Types

| Value | `source_values` Format |
|-------|----------------------|
| `grouping` | `["1.0", "2.0", "3.0"]` |
| `recoding` | `["1.0", "2.0"]` |
| `range` | `{"min": 25, "max": 35}` |

## Examples

### No Transformation
```json
{
  "indicator_code": "Q5",
  "question_type": "MultiSelect",
  "indicator_label": "请问您通常通过哪些渠道获取信息？",
  "source_variables": {
    "Q5_1": "电视广告",
    "Q5_2": "报纸/杂志"
  },
  "transformation_needed": false,
  "transformation_type": null,
  "transformation_rules": null
}
```

### Range Transformation (Age Grouping)
```json
{
  "indicator_code": "S1_AGE_GROUP",
  "question_type": "Numeric",
  "indicator_label": "请问您的年龄是？",
  "source_variables": {
    "S1": "请问您的年龄是？"
  },
  "transformation_needed": true,
  "transformation_type": "range",
  "transformation_rules": [
    {
      "source_values": {"min": 18, "max": 25},
      "target_value": "1",
      "target_label": "18-25岁",
      "hide_categories": false
    },
    {
      "source_values": {"min": 26, "max": 35},
      "target_value": "2",
      "target_label": "26-35岁",
      "hide_categories": false
    }
  ]
}
```

### Grouping Transformation (Rating Scale)
```json
{
  "indicator_code": "Q5_SATISFACTION_GROUPED",
  "question_type": "Rating",
  "indicator_label": "请评价您对产品的满意度",
  "source_variables": {
    "Q5": "请评价您对产品的满意度"
  },
  "transformation_needed": true,
  "transformation_type": "grouping",
  "transformation_rules": [
    {
      "source_values": ["1", "2"],
      "target_value": "1",
      "target_label": "不满意",
      "hide_categories": true
    },
    {
      "source_values": ["3"],
      "target_value": "2",
      "target_label": "中立",
      "hide_categories": false
    },
    {
      "source_values": ["4", "5"],
      "target_value": "3",
      "target_label": "满意",
      "hide_categories": true
    }
  ]
}
```

### Geographic Grouping
```json
{
  "indicator_code": "S0XA_REGION",
  "question_type": "Single",
  "indicator_label": "请问您居住的省/区或直辖市。",
  "source_variables": {
    "S0XA": "请问您居住的省/区或直辖市。"
  },
  "transformation_needed": true,
  "transformation_type": "grouping",
  "transformation_rules": [
    {
      "source_values": ["1.0", "2.0", "3.0"],
      "target_value": "1.0",
      "target_label": "直辖市",
      "hide_categories": true
    },
    {
      "source_values": ["4.0", "5.0", "6.0"],
      "target_value": "2.0",
      "target_label": "华东地区",
      "hide_categories": true
    }
  ]
}
```

## PSPP Syntax Generation

### Option 1: Generate New Variables
```spss
DO IF (S1 >= 18 AND S1 <= 25).
  COMPUTE S1_AGE_GROUP = 1.
ELSE IF (S1 >= 26 AND S1 <= 35).
  COMPUTE S1_AGE_GROUP = 2.
END IF.
VARIABLE LABELS S1_AGE_GROUP "1 18-25岁 2 26-35岁".
VALUE LABELS S1_AGE_GROUP 1 "18-25岁" 2 "26-35岁".
```

### Option 2: Use Subtotals in CTABLES
```spss
CTABLES
  /TABLE=S1 BY Q1
  /CATEGORIES VARIABLES=S1 [18 THRU 25 SUBTOTAL='18-25岁' HIDECATEGORIES, 26 THRU 35 SUBTOTAL='26-35岁' HIDECATEGORIES].
```

The `hide_categories` field controls whether to include `HIDECATEGORIES` keyword in the subtotal definition.
