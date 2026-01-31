# Progress Document Template

This template defines the structure for progress tracking document.

## Progress Document Structure (Minimal Story-Based Tracking)

**Story files**: Each user story is a self-contained document (`phase-{NN}-story-{MM}-{title}.md`)

**This progress document** provides a simple view of story completion status.

```markdown
# Implementation Progress

**Wave**: {Wave Name} | **Last Updated**: {Date}

## Progress Summary

| Phase | Status | Stories |
|-------|--------|---------|
| 01 | ⚪ Not Started | 0/3 |
| 02 | ⚪ Not Started | 0/2 |
| 03 | ⚪ Not Started | 0/4 |
| {NN} | ⚪ Not Started | 0/X |

**Legend**: ⚪ Not Started | 🔄 In Progress | ⚠️ Partial | ✅ Complete | ⚠️ Blocked | ❌ Failed

**Column meanings**:
- **Status**: Overall phase status (derived from stories)
- **Stories**: Count of completed stories (e.g., "2/3" = 2 of 3 stories complete)

---

## All Stories

| Story File | Title | Status | Notes |
|------------|-------|--------|-------|
| `phase-01-story-01-*.md` | {Story title} | ⚪ Not Started | |
| `phase-01-story-02-*.md` | {Story title} | ⚪ Not Started | |
| `phase-01-story-03-*.md` | {Story title} | ⚪ Not Started | |
| `phase-02-story-01-*.md` | {Story title} | ⚪ Not Started | |
| `phase-02-story-02-*.md` | {Story title} | ⚪ Not Started | |
| `phase-03-story-01-*.md` | {Story title} | ⚪ Not Started | |

**Status meanings**:
- ⚪ Not Started: No work begun
- 🔄 In Progress: Work in progress
- ⚠️ Partial: Work done but loose ends remain (tests failing, bugs, etc.)
- ✅ Complete: Fully complete with ALL acceptance criteria met and tests passing
- ⚠️ Blocked: Cannot proceed due to blocker
- ❌ Failed: Task failed

> **Note**: For detailed task breakdown (Backend, Frontend, Testing layers), see individual story documents.

---

## Phase 01: {Phase Name}

**Status**: ⚪ Not Started (0/3 stories)

| Story File | Title | Status | Notes |
|------------|-------|--------|-------|
| `phase-01-story-01-*.md` | {Story title} | ⚪ Not Started | |
| `phase-01-story-02-*.md` | {Story title} | ⚪ Not Started | |
| `phase-01-story-03-*.md` | {Story title} | ⚪ Not Started | |

---

## Phase 02: {Phase Name}

**Status**: ⚪ Not Started (0/2 stories)

| Story File | Title | Status | Notes |
|------------|-------|--------|-------|
| `phase-02-story-01-*.md` | {Story title} | ⚪ Not Started | |
| `phase-02-story-02-*.md` | {Story title} | ⚪ Not Started | |

---

## Phase {NN}: {Phase Name}

**Status**: ⚪ Not Started (0/X stories)

| Story File | Title | Status | Notes |
|------------|-------|--------|-------|
| `phase-{NN}-story-01-*.md` | {Story title} | ⚪ Not Started | |

---

## Blockers & Issues

| ID | Story | Issue | Status | Created |
|----|-------|-------|--------|---------|
| | | | | |

## Statistics

| Metric | Value |
|--------|-------|
| Total Phases | {N} |
| Total Stories | {0} |
| Stories Completed | {0}/{0} |
| Overall Completion | {0}% |
```

## Status Values

| Status | Meaning | When to Use |
|--------|---------|-------------|
| ⚪ Not Started | Story not yet begun | Initial state |
| 🔄 In Progress | Story currently being worked on | During implementation |
| ⚠️ Partial | Story partially complete (loose ends remain) | Tests failing, bugs, deferred work |
| ✅ Complete | Story finished and verified | After acceptance criteria met AND all tests passing |
| ⚠️ Blocked | Story cannot proceed (issue logged) | When blocker exists |
| ❌ Failed | Story failed (error logged) | On error |

## Partial Status Criteria (⚠️ Partial)

The **⚠️ Partial** status is used when work has been done but is NOT fully complete. This prevents misleading "Complete" markings.

| Scenario | Status | Example |
|----------|--------|---------|
| Tests written but failing | ⚠️ Partial | "Tests written, 4/13 passing (auth tests pass, data tests need fixture fixes)" |
| Feature implemented with known bugs | ⚠️ Partial | "UI complete, but edge case causes crash on rare input" |
| Tests skipped/deferred | ⚠️ Partial | "Unit tests skipped: Extensive UI mocking required; deferred" |
| Code complete but not tested | ⚠️ Partial | "Implementation done, integration tests not yet written" |
| Waiting for external dependency | ⚠️ Blocked (not Partial) | Use Blocked when waiting on others, Partial for own work remaining |

**IMPORTANT**: Never mark a story as ✅ Complete if:
- Any tests are failing
- Tests were skipped/deferred (unless explicitly agreed to skip)
- Known bugs exist
- Documentation is incomplete (if required)
- Acceptance criteria not fully met

## Story Status Logic

```
Story Status = f(All tasks in story document)

Story criteria (derived from Backend + Frontend + Testing tasks):
- ✅ Complete: ALL tasks in story are ✅ Complete
- 🔄 In Progress: ANY task is 🔄 In Progress (but none blocked/failed)
- ⚠️ Partial: SOME tasks complete, some incomplete (no blockers/failures)
- ⚠️ Blocked: ANY task is ⚠️ Blocked
- ❌ Failed: ANY task is ❌ Failed
- ⚪ Not Started: ALL tasks are ⚪ Not Started
```

## Phase-Level Status Logic

```
Phase Status = f(Stories in phase)

Stories column: "X/Y Complete" where X = completed stories, Y = total stories

if ALL stories ✅ Complete:
    Status = ✅ Complete
elif ANY story is ⚠️ Blocked or ❌ Failed:
    Status = ⚠️ Blocked
elif ANY story is ⚠️ Partial or 🔄 In Progress:
    Status = 🔄 In Progress (or ⚠️ Partial if mostly partial)
else:
    Status = ⚪ Not Started
```

## Blocker Logging

When a story is blocked, add an entry to the Blockers & Issues table:

| ID | Story | Issue | Status | Created |
|----|-------|-------|--------|---------|
| B001 | phase-01-story-02 | PSPP installation failed - missing dependency | ⚠️ Active | 2026-01-20 10:45 |

**Blocker IDs**: Use format `B###` (B001, B002, etc.)

**Blocker Status**:
- ⚠️ Active: Currently blocking progress
- ✅ Resolved: Blocker fixed, can proceed

## Notes Format

The Notes column can contain:
- Brief implementation details
- Links to relevant commits/PRs
- Dependencies on other tasks
- Technical decisions made
- Error messages or issues encountered

Examples:
- "Implemented on 2026-01-20, commit: abc123"
- "Depends on story: phase-01-story-01"
- "Used OAuth2 library: python-oauth2"
- "Error: Connection timeout, needs retry logic"

## Updating Progress

**When to Update**:
1. At start: Mark story as 🔄 In Progress
2. On success: Mark story as ✅ Complete
3. On blocker: Mark story as ⚠️ Blocked, log issue
4. On failure: Mark story as ❌ Failed, log error
5. After each story: Update progress document

**Update Frequency**: After each story completion, never batch updates

## Statistics Calculation

```python
total_phases = number of phases
total_stories = sum of all user stories across all phases
stories_completed = count of ✅ Complete stories
completion_percentage = (stories_completed / total_stories) * 100
```
