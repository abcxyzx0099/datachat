# Task: Fix Documentation Issues from Design Audit

**Status**: pending

---

## Task

Fix four documentation issues identified in the design document audit: (1) Update API key documentation in system-configuration.md to use pseudo-code referencing .env file variables instead of exposed keys, (2) Remove all references to non-existent implementation-specifications.md, (3) Fix Chinese text in data-schema.md, (4) Verify PSPP manual link is correct.

## Context

A design document audit identified several issues that need fixing:

1. **Security Issue**: `system-configuration.md` contains what appear to be real API keys (lines 53, 61, 69, 281, 288, 295). Instead of simple placeholders, the user wants these updated to pseudo-code that references environment variables from the `.env` file - this makes the existence of the `.env` file visible to AI agents.

2. **Broken References**: Four documents reference `implementation-specifications.md` which no longer exists.

3. **Inconsistent Language**: `data-schema.md` contains Chinese text that should be English.

4. **Link Verification**: Verify the PSPP manual reference link is correct (user confirms the file exists).

## Scope

- Directories: `docs/`
- Files:
  - `docs/system-configuration.md` (API key documentation)
  - `docs/data-flow.md` (line 313 - remove implementation-specifications.md reference)
  - `docs/system-architecture.md` (line 184 - remove implementation-specifications.md reference)
  - `docs/features-and-usage.md` (line 234 - remove implementation-specifications.md reference)
  - `docs/web-interface.md` (line 258 - remove implementation-specifications.md reference)
  - `docs/data-schema.md` (line 634 - fix Chinese text)
  - `docs/technology-stack.md` (line 219 - verify PSPP link)
  - `docs/useful-references.md` (line 11 - verify PSPP link)
- Dependencies: None

## Requirements

1. **Update API Key Documentation in system-configuration.md**:
   - Lines 53, 61, 69: Update the "Example" column in the provider configuration tables
   - Lines 281, 288, 295: Update the .env file example section
   - Replace exposed API keys with pseudo-code like `${KIMI_API_KEY}` or `$KIMI_API_KEY` that references environment variables
   - Ensure the `.env` file's existence and purpose is clear to AI agents reading the documentation

2. **Remove implementation-specifications.md References**:
   - In `data-flow.md` (line 313): Remove the reference from the Related Documents section or update if alternative document exists
   - In `system-architecture.md` (line 184): Remove the reference from the Related Documents section
   - In `features-and-usage.md` (line 234): Remove the reference from Document Navigation section
   - In `web-interface.md` (line 258): Remove the reference from Related Documents section

3. **Fix Chinese Text in data-schema.md**:
   - Line 634: Translate "不需要的变量" to English (e.g., "variables not requiring recoding")

4. **Verify PSPP Manual Link**:
   - The file exists at: `reference/external-official-manual/PSPP-syntax/pspp_manual.txt`
   - Verify the relative link `../reference/external-official-manual/PSPP-syntax/pspp_manual.txt` is correct from both `technology-stack.md` and `useful-references.md` (both in `docs/` directory)
   - Update link if incorrect (should be correct as-is, but verify)

## Deliverables

1. Updated `docs/system-configuration.md` with environment variable pseudo-code for API keys
2. Four files with implementation-specifications.md references removed
3. Updated `docs/data-schema.md` with English text instead of Chinese
4. Confirmation that PSPP manual link is correct (or updated if needed)

## Constraints

1. Maintain existing markdown formatting and document structure
2. Keep all other content unchanged - only modify the specific items identified
3. For Related Documents sections: maintain formatting and list structure when removing items
4. The pseudo-code for API keys should be clear and consistent - use a pattern like `${VARIABLE_NAME}` or `$VARIABLE_NAME`

## Success Criteria

1. API key examples in system-configuration.md use environment variable references (not exposed keys or plain placeholders)
2. No references to `implementation-specifications.md` exist in any documentation files
3. All text in data-schema.md is in English
4. PSPP manual link correctly points to existing file at `reference/external-official-manual/PSPP-syntax/pspp_manual.txt`
5. All markdown files remain valid with proper formatting

## Worker Investigation Instructions

**CRITICAL: You MUST do your own deep investigation before implementing.**

1. **Read all affected files** to understand current state:
   - Read `docs/system-configuration.md` - locate all API key examples (lines ~53, 61, 69, 281, 288, 295)
   - Read `docs/data-flow.md` - find the implementation-specifications.md reference in Related Documents
   - Read `docs/system-architecture.md` - find the reference in Related Documents
   - Read `docs/features-and-usage.md` - find the reference in Document Navigation
   - Read `docs/web-interface.md` - find the reference in Related Documents
   - Read `docs/data-schema.md` - locate the Chinese text around line 634
   - Read `docs/technology-stack.md` and `docs/useful-references.md` - verify PSPP link context

2. **Understand the .env file pattern**:
   - Check if there's a `.env.example` file in project root that shows expected format
   - The goal is to show API keys as environment variable references like `${KIMI_API_KEY}` not bare values

3. **Verify PSPP link path**:
   - Confirm `docs/` is at correct level for `../reference/` to work
   - File exists at: `/home/admin/workspaces/datachat/reference/external-official-manual/PSPP-syntax/pspp_manual.txt`

4. **Identify all changes needed** before making any edits - create a complete change list

5. **After implementing**, verify:
   - Use grep to confirm no references to `implementation-specifications.md` remain
   - Confirm Chinese text is replaced
   - Confirm API key documentation uses variable references
