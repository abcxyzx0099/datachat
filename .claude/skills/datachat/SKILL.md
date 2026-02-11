---
name: datachat
description: 'SPSS Survey Analysis - Complete workflow for analyzing SPSS survey data through extraction, recoding, indicator generation, cross-tables, statistics, filtering, and report generation (PowerPoint + HTML dashboard). Use when user needs to analyze .sav files, generate survey reports, or process statistical survey data.'
license: Apache-2.0
---

# DataChat - SPSS Survey Analysis Skill

Complete LangGraph-based workflow for SPSS survey data analysis.

## Overview

DataChat processes SPSS (.sav) survey files through a 22-step workflow:
1. **Extract** SPSS data and metadata
2. **Transform** to variable-centered format
3. **Filter** variables requiring recoding
4. **Generate** AI-powered recoding rules
5. **Validate** recoding rules
6. **Review** and approve recoding
7. **Execute** PSPP recoding
8. **Generate** statistical indicators
9. **Validate** indicators
10. **Review** and approve indicators
11. **Generate** cross-table specifications
12. **Validate** table specifications
13. **Review** and approve tables
14. **Execute** PSPP crosstabs
15. **Generate** Python statistics scripts
16. **Execute** statistical analysis
17. **Generate** significance filter list
18. **Apply** filter to tables
19. **Generate** PowerPoint presentation
20. **Generate** HTML dashboard

## Usage

### Quick Analysis

```bash
# Run complete analysis on SPSS file
python scripts/run_analysis.py path/to/survey.sav
```

### With Thread ID (Resumable)

```bash
# Run with thread ID for checkpointing
python scripts/run_analysis.py path/to/survey.sav --thread-id analysis-1
```

### Resume Interrupted Analysis

```bash
# Resume from checkpoint
python scripts/run_analysis.py --resume --thread-id analysis-1
```

## Output Files

The analysis generates:

| File | Description |
|------|-------------|
| `new_data.sav` | Recoded dataset |
| `cross_table.tab` | Cross-tabulation results |
| `statistics_results.json` | Chi-square, Cramer's V |
| `presentation.pptx` | Executive summary PowerPoint |
| `dashboard.html` | Full interactive dashboard |

## Integration with AionUi

This skill integrates with the LangGraph backend running on port 8123.

### API Endpoints

- `POST /threads` - Create new analysis thread
- `POST /threads/{thread_id}/invoke` - Start analysis with file
- `GET /threads/{thread_id}/state` - Check analysis status
- `POST /threads/{thread_id}/feedback` - Submit human feedback
- `POST /threads/{thread_id}/resume` - Resume interrupted analysis
- `GET /health` - Health check

## Example Session

```
User: Analyze my survey data at /data/survey.sav

Assistant: I'll analyze your SPSS survey file. This will:
1. Extract and validate the data
2. Generate AI-powered recoding rules
3. Create statistical indicators
4. Generate cross-tables and statistics
5. Filter significant results
6. Create PowerPoint and HTML reports

Starting analysis now...
[Analysis running...]

Your analysis is complete! Results:
- Recoded dataset: new_data.sav
- Cross-tables: 23 tables generated
- Significant findings: 18 tables passed chi-square test
- PowerPoint: presentation.pptx
- Dashboard: dashboard.html
```

## Requirements

- Python 3.11+
- PSPP installed
- LangGraph API running on port 8123
- Input file: SPSS .sav format

## Error Handling

Common errors:

| Error | Solution |
|-------|----------|
| "File not found" | Check .sav file path |
| "PSPP not found" | Install PSPP: `sudo apt-get install pspp` |
| "LangGraph API unreachable" | Start API: `python -m agent.server` |
| "Checkpoint not found" | Use correct thread_id or start new analysis |

## Advanced Options

```bash
# Custom configuration
python scripts/run_analysis.py survey.sav \
  --thread-id custom-1 \
  --api-url http://localhost:8123
```
