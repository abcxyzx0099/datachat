# Recoding Rules Review

**Status**: Pending Your Review

## Summary
- Total Rules: 2
- Source Variables: satisfaction
- Target Variables: satisfaction_group, satisfaction_top2box
- Iteration: 0

## Validation Result
- **Status**: Passed ✓
- Errors: 0
- Warnings: 0

## Recoding Rules

### Rule 1: satisfaction → satisfaction_group

- **Transformation Type**: range_grouping
- **Source Variable**: satisfaction
- **Target Variable**: satisfaction_group

**Rules**:

| Source Range | Target Value | Label |
|--------------|--------------|-------|
| N/A | 1 |  |
| N/A | 2 |  |
| N/A | 3 |  |

### Rule 2: satisfaction → satisfaction_top2box

- **Transformation Type**: top_bottom_box
- **Source Variable**: satisfaction
- **Target Variable**: satisfaction_top2box

**Rules**:

| Source | Target | Label |
|--------|--------|-------|
| N/A | N/A |  |
| N/A | N/A |  |

## Actions

Please review and select an action:

- [ ] **Approve** - Rules look correct, proceed to PSPP syntax generation
- [ ] **Reject with Feedback** - Rules need revision, provide feedback below
- [ ] **Modify** - You will manually edit the rules

**Your Feedback**:

[Enter your feedback here]

---

**Common feedback examples**:

- Add recoding rule for variable 'age'
- Change ranges for 'income' to use quintiles
- Consolidate categories 7-9 into 'Other'
- Use different transformation type for 'satisfaction'
