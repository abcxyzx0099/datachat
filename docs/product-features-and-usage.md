# Product Features & Usage Guide

## What is DataChat?

DataChat is an automated survey analysis tool that helps you understand your survey data quickly. You upload your SPSS survey file, and DataChat creates professional presentations and interactive dashboards showing the key findings.

**What it does for you:**
- Analyzes relationships between survey questions automatically
- Creates PowerPoint presentations ready for stakeholder meetings
- Builds interactive dashboards for deeper exploration
- Identifies statistically significant patterns in your data

---

## Key Features

### Automatic Analysis

DataChat examines your survey data and finds relationships between questions. It tests these relationships using statistical methods and highlights only the meaningful findings.

**What gets analyzed:**
- Cross-tabulations between categorical questions
- Statistical significance testing
- Effect size measurements
- Sample size validation

### Human-in-the-Loop Review

You stay in control. DataChat pauses at key points to let you review its work before continuing:

| Review Point | What You Review |
|--------------|-----------------|
| Recoding Rules | How categories are grouped |
| Indicators | Which questions combine into measures |
| Table Specifications | Which tables appear in your report |

### Professional Outputs

| Output | Best For |
|--------|----------|
| **PowerPoint Presentation** | Executive summaries, stakeholder meetings |
| **HTML Dashboard** | Interactive exploration, deeper analysis |
| **Statistical Summary** | Technical documentation, verification |

---

## How to Use DataChat

### Step 1: Prepare Your Survey File

Ensure your survey file is in SPSS format (`.sav` file). The file should contain:
- Survey questions and responses
- Variable labels (descriptions of what each question means)
- Value labels (descriptions of what each response means)

### Step 2: Run the Analysis

**Your Request**: "Run DataChat with my survey file"

```bash
python -m agent.graph --input data/input/my_survey.sav
```

That's it! DataChat will:
1. Read your survey file
2. Analyze the data
3. Ask for your review at key points (see Step 3)
4. Create your outputs

### Step 3: Review and Approve

When DataChat pauses for review, you'll see a file like `output/reviews/recoding_rules_review.md`

**To approve and continue:**
```bash
approve
```

**To request changes:**
```bash
reject Group satisfaction by top-2-box instead
```

DataChat will regenerate with your feedback.

### Step 4: Access Your Results

When analysis completes, find your outputs in the `output/` directory:

| File | Description |
|------|-------------|
| `presentation.pptx` | PowerPoint with key findings |
| `dashboard.html` | Interactive dashboard |
| `statistical_summary.json` | Detailed statistical results |

---

## Understanding Your Results

### PowerPoint Presentation

The presentation contains only statistically significant findings:

- **Title slide**: Analysis name, date, sample size
- **Result slides**: One slide per significant relationship
  - Visual chart (bar graph)
  - Data table with counts and percentages
  - Statistics: Chi-square, p-value, Cramer's V
- **Summary slide**: Total tables analyzed, significant relationships found

### HTML Dashboard

Open `dashboard.html` in any web browser to:
- Browse all tables (not just significant ones)
- Click column headers to sort
- Filter by significance or effect size
- View interactive charts for each table
- See detailed statistics

### Interpreting Statistics

| Statistic | What It Means |
|-----------|---------------|
| **p-value < 0.05** | The relationship is statistically significant (not due to chance) |
| **Cramer's V** | Effect size: how strong is the relationship? (0 = none, 1 = very strong) |
| **Chi-square** | Statistical test result used to calculate significance |

---

## Common Use Cases

### Use Case 1: Customer Satisfaction Survey

**Goal**: Understand what drives customer satisfaction

**Process:**
1. Upload your satisfaction survey `.sav` file
2. DataChat analyzes relationships between satisfaction and demographics, usage patterns, etc.
3. Review which indicators DataChat created (e.g., "overall satisfaction index")
4. Get a presentation showing which factors relate to satisfaction

### Use Case 2: Employee Engagement Survey

**Goal**: Identify engagement drivers across departments

**Process:**
1. Upload employee engagement survey
2. Review recoding rules to ensure department groupings match your structure
3. Approve table specifications
4. Present findings to management with ready-made PowerPoint

### Use Case 3: Market Research Study

**Goal**: Analyze consumer preferences by segment

**Process:**
1. Upload market research survey
2. Use the HTML dashboard for deep-dive analysis across segments
3. Export PowerPoint slides for client presentation
4. Reference statistical summary for methodology documentation

---

## Quick Reference

### Getting Started

```bash
# Run analysis
python -m agent.graph --input data/input/survey.sav

# Custom output folder
python -m agent.graph --input data/input/survey.sav --output-dir results/

# Skip review (automatic mode)
python -m agent.graph --input data/input/survey.sav --no-human-review
```

### Review Commands

```bash
approve                    # Accept and continue
reject Your feedback here  # Request changes with specific feedback
```

### Resume After Interruption

```bash
# Resume from where you left off
python -m agent.graph --thread-id <thread-id> --resume
```

---

## Tips for Best Results

| Tip | Why It Helps |
|-----|--------------|
| **Use labeled data** | Ensure your `.sav` file has variable and value labels |
| **Review carefully** | The human review steps ensure results match your intent |
| **Check sample sizes** | Small samples may not produce significant results |
| **Use the dashboard** | The HTML dashboard shows all tables, not just significant ones |
| **Iterate if needed** | You can reject and provide feedback to refine the analysis |

---

## What DataChat Cannot Do

| Limitation | Notes |
|------------|-------|
| **Open-ended text analysis** | Only analyzes categorical (multiple choice) questions |
| **Time series analysis** | Does not track changes over time across surveys |
| **Predictive modeling** | Identifies relationships, but does not make predictions |
| **Very small samples** | Requires sufficient data for statistical testing |

---

## Getting Help

If you encounter issues:

1. Check the `output/logs/` directory for detailed error messages
2. Verify your `.sav` file opens correctly in SPSS or PSPP
3. Ensure you have an active OpenAI API key configured
4. For technical documentation, see [Deployment](./deployment.md)

---

## Document Navigation

- **[Deployment](./deployment.md)** - Installation, deployment, and troubleshooting
- **[Configuration](./configuration.md)** - Configuration options and usage examples
- **[Web Interface](./web-interface.md)** - Agent Chat UI setup and usage
- **[Implementation Specifications](./implementation-specifications.md)** - Technical implementation details
