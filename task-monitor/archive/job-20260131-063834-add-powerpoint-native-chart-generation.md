# Task: Add Native PowerPoint Chart Generation (Editable)

**Status**: pending

---

## Task

Implement complete PowerPoint slide generation with **native editable charts** using python-pptx's `add_chart()` method for cross-tabulation survey data tables.

## Context

During a review of the survey analysis workflow documentation, gaps were identified in the detailed specifications document (`docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`). Section 7.2 (PowerPoint Generation) currently only creates slides with:
- Slide titles
- Statistical summary text (Chi-square, p-value, Cramer's V)
- Metadata tracking

The **critical missing piece** is the actual chart generation - no visual charts are created on the slides.

**IMPORTANT**: Charts must be **native PowerPoint charts** (editable), NOT static images. Users need to be able to:
- Modify data directly in PowerPoint
- Change chart type (bar → line, etc.)
- Adjust styling, colors, fonts
- Edit labels and titles

## Scope

- Directories:
  - `workflow/nodes/` - Create or update `presentation.py` for PowerPoint generation node
  - `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md` - Update Section 7.2 with complete implementation

- Files:
  - `workflow/state.py` - Reference for state structure
  - `workflow/nodes/__init__.py` - Export new node function

- Dependencies:
  - `python-pptx` library with `add_chart()` and `ChartData` API
  - Existing state fields: `significant_tables`, `statistical_summary`

## Requirements

1. **Native Chart Generation**: Use python-pptx's native chart API:
   - `slide.shapes.add_chart()` - Create native chart objects
   - `CategoryChartData()` - Define chart data structure
   - Supported chart types: `XL_CHART_TYPE.BAR_CLUSTERED`, `XL_CHART_TYPE.BAR_STACKED_100`, `XL_CHART_TYPE.COLUMN_CLUSTERED`
   - Charts must be editable in PowerPoint/LibreOffice Impress

2. **Chart Data Preparation**: Implement data transformation from cross-tabulation to ChartData:
   - Extract categories (row labels) from table data
   - Create series for each column category
   - Map counts/values to series data
   - Handle both count and percentage displays

3. **Slide Layout**: Each slide should contain:
   - Title (table name)
   - Native chart (top/center, prominent)
   - Statistical summary text box (below chart)
   - Proper positioning using `Inches`

4. **Chart Configuration**:
   - Bar charts for standard cross-tabs (rows vs columns)
   - Stacked 100% bar charts for percentage distributions
   - Horizontal bar charts for long category labels
   - Professional colors (market research standard palette)
   - Axis labels and chart titles

5. **Error Handling**:
   - Handle tables with insufficient data gracefully
   - Log warnings for skipped tables
   - Continue processing even if individual charts fail
   - Validate data structure before chart creation

6. **Helper Functions**: Create reusable functions:
   - `create_native_chart()` - Generate native PowerPoint chart from table data
   - `prepare_chart_data()` - Transform cross-tab data to CategoryChartData format
   - `add_chart_to_slide()` - Position and configure chart on slide
   - `get_chart_type_for_table()` - Determine appropriate chart type based on table dimensions

## Deliverables

1. **Implementation File**: `workflow/nodes/presentation.py` containing:
   - Complete `generate_powerpoint_node()` function with native chart generation
   - Helper functions using python-pptx chart API (NO matplotlib)
   - Proper imports and type hints
   - Integration with existing state structure

2. **Updated Documentation**: Complete rewrite of Section 7.2 in `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`:
   - Full implementation code using `add_chart()` API
   - No placeholder comments
   - Examples of ChartData structure preparation
   - Native chart creation examples

3. **Updated Module Export**: Add function to `workflow/nodes/__init__.py`

## Constraints

1. **Language**: Python 3.10+
2. **Library**: Use `python-pptx` native chart API only:
   - `from pptx import Presentation`
   - `from pptx.util import Inches`
   - `from pptx.enum.chart import XL_CHART_TYPE`
   - `from pptx.chart.data import CategoryChartData`
   - **DO NOT use matplotlib** - no image export needed
3. **Compatibility**: Must integrate with existing LangGraph state structure
4. **State Fields**: Use existing state fields: `significant_tables_json_path`, `statistical_summary_path`, `powerpoint_path`, `charts_generated`
5. **File Locations**:
   - Node function: `workflow/nodes/presentation.py`
   - Export: `workflow/nodes/__init__.py`
6. **Chart Requirements**:
   - Must be editable in PowerPoint/LibreOffice Impress
   - No 3D chart types (not supported by python-pptx)
   - Professional styling appropriate for market research

## Success Criteria

1. **Functional Requirements**:
   - PowerPoint is generated with native editable charts
   - Charts can be opened and modified in PowerPoint/LibreOffice
   - Each slide contains: title, editable chart, statistical summary
   - No placeholder code or comments

2. **Chart Quality**:
   - Data accurately represents cross-tabulation values
   - Labels and categories correctly applied
   - Professional color scheme
   - Appropriate chart type for data dimensions

3. **Code Quality**:
   - Uses `add_chart()` API, not image embedding
   - Proper type hints and docstrings
   - Error handling with try/except blocks
   - Follows existing code patterns in `workflow/nodes/`

4. **Documentation**:
   - Section 7.2 is complete with full native chart implementation
   - No ellipsis or placeholder comments

5. **Verification**:
   - Generated .pptx opens in LibreOffice Impress or PowerPoint
   - Charts are selectable and editable objects
   - Right-click → "Edit Data" works in PowerPoint
   - Chart type can be changed after generation

## Worker Investigation Instructions

**CRITICAL**: Before implementing, you MUST conduct deep investigation:

1. **Understand python-pptx Chart API**:
   - Read [Working with charts — python-pptx documentation](https://python-pptx.readthedocs.io/en/latest/user/charts.html)
   - Study [SlideShapes.add_chart() API](https://python-pptx.readthedocs.io/en/latest/dev/analysis/cht-add-chart.html)
   - Understand `CategoryChartData` structure
   - Learn available chart types (XL_CHART_TYPE enum)
   - Find examples of creating bar and stacked bar charts

2. **Understand Data Structure**:
   - Read `workflow/state.py` for state fields
   - Investigate `significant_tables` JSON structure
   - Check `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md` for table format
   - Understand cross-tabulation data organization

3. **Chart Data Preparation**:
   - How to convert table rows → chart categories?
   - How to convert table columns → chart series?
   - How to handle counts vs percentages?
   - What format does `CategoryChartData` expect?

4. **Review Existing Patterns**:
   - Read files in `workflow/nodes/` for code style
   - Check how other nodes handle state updates
   - Follow error handling patterns
   - Match type hint and docstring styles

5. **Chart Design Decisions**:
   - When to use bar vs column vs stacked charts?
   - How to handle many categories (>10)?
   - What color scheme for professional presentations?
   - How to set axis labels and titles programmatically?

6. **Identify Edge Cases**:
   - 2x2 tables (simple binary)
   - Single row or single column tables
   - Tables with zero values
   - Very large tables (10+ categories)

7. **Test Editability**:
   - Verify generated charts are editable, not images
   - Test in PowerPoint if available, or LibreOffice Impress
   - Confirm "Edit Data" option is available

**DO NOT proceed until you have:**
- Full understanding of `add_chart()` and `CategoryChartData` API
- Clear data transformation plan (table → chart data)
- Sample data structure understood
- Existing code patterns reviewed
- Knowledge of chart type selection logic

**Key Resources**:
- [python-pptx Charts Documentation](https://python-pptx.readthedocs.io/en/latest/user/charts.html)
- [CategoryChartData API](https://python-pptx.readthedocs.io/en/latest/api/chart.html)
