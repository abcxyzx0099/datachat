# Task: Add PowerPoint Chart Generation Functionality

**Status**: pending

---

## Task

Implement complete PowerPoint slide generation with visual charts (bar charts, stacked bar charts) for cross-tabulation survey data tables.

## Context

During a review of the survey analysis workflow documentation, gaps were identified in the detailed specifications document (`docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`). Section 7.2 (PowerPoint Generation) currently only creates slides with:
- Slide titles
- Statistical summary text (Chi-square, p-value, Cramer's V)
- Metadata tracking

The **critical missing piece** is the actual chart generation - no visual charts (bar charts, stacked bar charts) are created on the slides. This is essential for market research presentations where visual representation of cross-tabulation data is standard.

The workflow already has:
- State management defined in `workflow/state.py` (Phase 7: Presentation fields)
- Significance filtering that produces `significant_tables` JSON
- Statistical summary with Chi-square and Cramer's V values
- Table data structure from cross-tabulation

## Scope

- Directories:
  - `workflow/nodes/` - Create or update `presentation.py` for PowerPoint generation node
  - `workflow/` - May need helper functions or utilities
  - `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md` - Update Section 7.2 with complete implementation

- Files:
  - `workflow/state.py` - Reference for state structure
  - `workflow/nodes/__init__.py` - Export new node function
  - `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md` - Documentation update

- Dependencies:
  - `python-pptx` library (already specified in docs)
  - `matplotlib` or similar for chart generation
  - Existing state fields: `significant_tables`, `statistical_summary`

## Requirements

1. **Chart Generation Function**: Create a function that generates visual charts from cross-tabulation table data:
   - Support bar charts for categorical vs categorical data
   - Support stacked bar charts for showing percentages
   - Handle 2x2 tables (simple binary comparisons)
   - Handle larger tables (multi-category comparisons)
   - Export chart as image that can be embedded in PowerPoint

2. **Slide Layout Enhancement**: Update `generate_powerpoint_node` to:
   - Create proper slide layout with title, chart area, and statistics summary
   - Add the generated chart image to each slide
   - Position elements appropriately (chart at top/center, statistics below)
   - Handle varying aspect ratios for different table sizes

3. **Chart Data Preparation**: Implement data transformation logic:
   - Convert cross-tabulation data to chart-friendly format
   - Extract labels, values, and categories from table structure
   - Handle missing/NaN values gracefully
   - Support both count and percentage displays

4. **Error Handling**: Add robust error handling:
   - Handle tables with insufficient data
   - Handle image generation failures
   - Log warnings for skipped tables
   - Continue processing even if individual charts fail

5. **Configuration Support**: Allow configuration options:
   - Chart type (bar, stacked bar, horizontal bar)
   - Color scheme (professional market research colors)
   - Chart size/dimensions
   - Whether to show counts, percentages, or both

6. **Helper Functions**: Create reusable functions:
   - `add_chart_to_slide()` - Embed chart image into slide
   - `generate_chart_image()` - Create chart from table data
   - `prepare_chart_data()` - Transform table data for charting

## Deliverables

1. **Implementation File**: `workflow/nodes/presentation.py` containing:
   - Complete `generate_powerpoint_node()` function with chart generation
   - Helper functions for chart creation and embedding
   - Proper imports and type hints
   - Integration with existing state structure

2. **Updated Documentation**: Complete rewrite of Section 7.2 in `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md`:
   - Full implementation code (no placeholders)
   - Chart generation examples
   - Helper function implementations
   - Usage examples

3. **Updated Module Export**: Add function to `workflow/nodes/__init__.py`

4. **Test Example**: Optional simple test demonstrating chart generation with sample data

## Constraints

1. **Language**: Python 3.10+
2. **Libraries**:
   - Use `python-pptx` for PowerPoint manipulation
   - Use `matplotlib` for chart generation (preferred) or `plotly`
   - Use `pandas` for data manipulation
3. **Compatibility**: Must integrate with existing LangGraph state structure in `workflow/state.py`
4. **State Fields**: Must use existing state fields: `significant_tables_json_path`, `statistical_summary_path`, `powerpoint_path`, `charts_generated`
5. **File Locations**:
   - Node function goes in `workflow/nodes/presentation.py`
   - Export through `workflow/nodes/__init__.py`
6. **Code Style**: Follow existing patterns in `workflow/nodes/` directory

## Success Criteria

1. **Functional Requirements**:
   - PowerPoint is generated with visual charts on each slide
   - Charts accurately represent cross-tabulation data
   - Statistical summary appears below each chart
   - No placeholder comments or incomplete code

2. **Data Accuracy**:
   - Chart values match table data
   - Labels are correctly applied
   - Colors are distinct and professional

3. **Code Quality**:
   - No placeholder code like `# TODO: add chart`
   - Proper error handling with try/except blocks
   - Type hints on all function signatures
   - Docstrings explaining purpose and parameters

4. **Documentation**:
   - Section 7.2 in detailed specs is complete with full code
   - No ellipsis (`...`) or placeholder comments in implementation

5. **Verification**:
   - Generated .pptx file can be opened in LibreOffice Impress or PowerPoint
   - Each slide contains: title, chart image, statistical summary
   - Charts are visually clear and readable

## Worker Investigation Instructions

**CRITICAL**: Before implementing, you MUST conduct deep investigation:

1. **Understand Data Structure**:
   - Read `workflow/state.py` to understand state fields
   - Investigate what `significant_tables` JSON structure looks like
   - Check `docs/SURVEY_ANALYSIS_DETAILED_SPECIFICATIONS.md` for table data format
   - Understand how cross-tabulation data is organized

2. **Research python-pptx**:
   - Check official documentation: https://python-pptx.readthedocs.io/
   - Understand how to add pictures/images to slides
   - Learn positioning APIs (Inches, left, top, width, height)
   - Find best practices for slide layout

3. **Research matplotlib to PowerPoint**:
   - Search for "matplotlib save image to PowerPoint python-pptx"
   - Understand how to save matplotlib figure as PNG/temp file
   - Learn how to embed image in PowerPoint slide
   - Find examples of professional chart styling

4. **Review Existing Patterns**:
   - Read files in `workflow/nodes/` directory to understand code patterns
   - Check how other nodes handle state updates
   - Follow existing error handling patterns
   - Match type hint and docstring styles

5. **Chart Design Research**:
   - What chart types work best for cross-tabulation data?
   - How should 2x2 tables be displayed vs 5x5 tables?
   - What color schemes are appropriate for professional presentations?
   - How to handle stacked bar charts for percentage display?

6. **Identify Edge Cases**:
   - What if table has only 1 row or 1 column?
   - What if all values are 0?
   - What if statistical summary is missing?
   - How to handle very large category counts (>10 categories)?

7. **Create Sample Data**:
   - Generate sample `significant_tables` JSON for testing
   - Create various table sizes (2x2, 3x4, 5x5)
   - Test with different data distributions

**DO NOT proceed with implementation until you have:**
- Full understanding of python-pptx picture insertion API
- Clear plan for chart generation approach (matplotlib vs alternatives)
- Sample data structure understood
- Existing code patterns reviewed
