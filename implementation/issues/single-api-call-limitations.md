# Single API Call Limitations for Survey Analysis

## Issue Description

When attempting to generate the complete table specification for survey analysis using a single API call, we encountered significant limitations with current AI models.

### Expected Behavior

- Input: Full metadata containing 345 variables
- Expected Output: Complete table specification with all indicators generated in one API call
- API Configuration: `max_tokens` or `max_completion_tokens` set to 100,000

### Actual Results

| Model | Context Window | Input Tokens | Output Tokens Generated | Indicators Generated | Finish Reason |
|-------|---------------|--------------|------------------------|---------------------|---------------|
| GLM-4.7 | 128K | 53,093 | Truncated at ~16,000 | Partial (incomplete) | `length` |
| Kimi K2 Turbo | 256K | 38,815 | 12,899 | 68/345 (~20%) | `stop` |

## Root Causes

### GLM-4.7 (Zhipu AI)

- **Maximum output limit**: 16,384 tokens
- **Problem**: Response was truncated due to exceeding this limit
- **Estimated requirement**: 58,325 output tokens needed for full specification
- **Result**: JSON parse error due to incomplete response

### Kimi K2 Turbo (Moonshot AI)

- **Context window**: 256K tokens (theoretically sufficient)
- **Maximum output requested**: 100,000 tokens
- **Actual output**: Only 12,899 tokens generated
- **Problem**: Model stopped prematurely with `finish_reason: stop`
- **Root cause**: Appears to be an internal processing limitation for complex JSON generation tasks, not a token limit

## Technical Details

### Response Characteristics

- **Kimi response length**: 35,868 characters
- **Indicators in response**: 68 (out of 345 required)
- **Completion percentage**: ~20%
- **JSON validity**: Valid structure but incomplete (truncated mid-string)

### Observed Behavior

The Kimi API returned `finish_reason: stop` indicating the model voluntarily terminated generation, not due to hitting a token limit. This suggests:

1. Internal timeout for complex generation tasks
2. Difficulty handling large Chinese text datasets in JSON format
3. Hidden character limit independent of token settings
4. Model optimization that prioritizes shorter responses

## Required Actions

### 1. Test Alternative Models

Evaluate models with higher context windows and proven long-form generation capabilities:

| Model | Context | Status | Priority |
|-------|---------|--------|----------|
| Claude 3.5 Sonnet | 200K | Not tested | High |
| GPT-4o | 128K | Not tested | High |
| DeepSeek-V3 | 64K+ | Configured | Medium |
| Gemini 1.5 Pro | 1M+ | Not tested | Medium |

### 2. Test Alternative API Parameters

- Experiment with different `max_tokens` / `max_completion_tokens` values
- Test `temperature` settings that might affect completion behavior
- Try streaming responses to detect early termination
- Implement retry logic with incremental continuation prompts

### 3. Architectural Alternatives

If single-call approach proves infeasible across all tested models:

- Implement continuation mechanism (detect incomplete response, request continuation)
- Use structured output APIs if available (e.g., OpenAI's Structured Outputs)
- Consider hybrid approaches with model orchestration

## Success Criteria

A model/API combination is considered viable for single-call processing if it can:

1. Process all 345 variables in one API call
2. Generate complete, valid JSON without truncation
3. Maintain consistent structure across all indicators
4. Return `finish_reason: stop` only after full completion
5. Complete within reasonable time (< 60 seconds)

## Current Status

- **Date Identified**: 2025-02-25
- **Status**: Open - Awaiting model testing
- **Impact**: Blocks direct single-call implementation approach
- **Workaround Available**: Yes (GLM-4.7 with batch processing generates 351/345 indicators successfully)

## Notes

- The Kimi K2 Turbo model has excellent context window (256K) but internal generation limitations
- GLM-4.7 has lower output limit (16K) but more predictable behavior
- Character count (~35K) suggests non-token-based limitation may exist
- Chinese text processing may be a factor in early termination
