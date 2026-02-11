# Project-Level Skills vs User-Level Skills

## Overview

Skills in Claude Code can be organized at two levels:

| Level | Location | Ownership | Use Case |
|-------|----------|-----------|----------|
| **Project-level** | `{project}/.claude/skills/` | Project/team | Domain-specific, shared |
| **User-level** | `~/.claude/skills/` | Personal | Personal shortcuts, tools |

## Recommended Directory Structure

```
/home/admin/workspaces/datachat/          # Project root
├── .claude/                               # Project-level Claude config
│   ├── skills/                            # ← Project skills (version controlled)
│   │   └── datachat/
│   │       ├── SKILL.md
│   │       └── scripts/
│   │           └── run_analysis.py
│   ├── keybindings.json                   # Project-specific keybindings
│   └── settings.json                      # Project-specific settings
│
├── agent/                                 # Source code
├── docs/
├── tests/
└── (rest of project)
```

## Skill Discovery Priority

Claude Code searches for skills in this order:

```
1. .claude/skills/           # Project-level (highest priority)
   └── Found first, used immediately

2. ~/.claude/skills/         # User-level (fallback)
   └─ Only used if not found at project level
```

## Why Project-Level Skills?

| Benefit | Explanation |
|---------|-------------|
| **Version Control** | Skills are tracked with project code |
| **Team Sharing** | All team members get the same skills automatically |
| **Context Awareness** | Skills are co-located with the code they operate on |
| **Portability** | Project works the same on any machine after clone |
| **Priority** | Project skills override user-level (avoid conflicts) |

## Team Workflow

### Developer Clones Project

```bash
git clone https://github.com/org/datachat.git
cd datachat

# Skills are immediately available at:
# .claude/skills/datachat/

# No manual setup needed!
```

### Developer Works on Project

```bash
cd /home/admin/workspaces/datachat

# Claude Code automatically finds:
# - .claude/skills/datachat/SKILL.md (project-level)
# NOT ~/.claude/skills/datachat (user-level)

# When user types:
claude "Analyze survey.sav"

# Claude Code uses project skill automatically
```

### Committing Skills

```bash
# Skills are part of project
git add .claude/skills/datachat/
git commit -m "Update datachat skill with new analysis options"
git push
```

## Comparison: Project vs User Skills

| Aspect | Project-Level | User-Level |
|--------|---------------|------------|
| **Location** | `{project}/.claude/skills/` | `~/.claude/skills/` |
| **Version Control** | ✅ Yes (in project repo) | ❌ No (personal) |
| **Team Sharing** | ✅ Automatic | ❌ Manual setup |
| **Priority** | Higher (checked first) | Lower (fallback) |
| **Use Case** | Domain-specific, business logic | Personal shortcuts, tools |
| **Examples** | datachat, project-specific workflows | personal keybindings, generic tools |

## AionUi Integration

AionUi still uses symlinks for its skills:

```bash
~/.config/AionUi/skills/datachat → /home/admin/workspaces/datachat/.claude/skills/datachat
```

This allows:
- **Single source of truth** in project repository
- **Automatic availability** to AionUi via symlink
- **Clean separation** between AionUi config and project skills

## When to Use Each Type

### Use Project-Level Skills When:

- ✅ Skill is specific to your project's domain
- ✅ Skill should be shared with team
- ✅ Skill operates on project code
- ✅ Skill defines business logic or workflows

**Examples:**
- `datachat` - SPSS analysis workflow
- `project-builder` - Custom build process
- `api-tester` - Project-specific API testing

### Use User-Level Skills When:

- ✅ Skill is personal to you
- ✅ Skill is generic/reusable across projects
- ✅ Skill defines personal preferences
- ✅ You don't want to share with team

**Examples:**
- `my-shortcuts` - Your personal keyboard shortcuts
- `personal-todos` - Your personal task management
- `my-snippets` - Your code snippets

## Migration Guide

### Moving from User-Level to Project-Level

```bash
# 1. Create project directory
mkdir -p /path/to/project/.claude/skills

# 2. Move skill
mv ~/.claude/skills/your-skill /path/to/project/.claude/skills/

# 3. Update symlinks if using AionUi
ln -sf /path/to/project/.claude/skills/your-skill ~/.config/AionUi/skills/your-skill

# 4. Commit to version control
cd /path/to/project
git add .claude/skills/your-skill
git commit -m "Add project-level skill: your-skill"
```

## File Structure Summary

```
Project Repository (datachat/)
├── .claude/
│   └── skills/
│       ├── datachat/              ← Full workflow (versioned)
│       │   ├── SKILL.md
│       │   └── scripts/
│       │       └── run_analysis.py
│       │
│       ├── spss-statistics/       ← Statistics only
│       │   └── SKILL.md
│       ├── spss-filter/           ← Filtering only
│       │   └── SKILL.md
│       ├── spss-pspp/             ← PSPP syntax & execution
│       │   └── SKILL.md
│       └── spss-reports/          ← Report generation
│           └── SKILL.md
│
User Home Directory (~/.claude/)
└── skills/
    ├── my-shortcuts/             ← User skill (personal)
    └── personal-tools/           ← User skill (personal)

AionUi Config (~/.config/AionUi/)
└── skills/
    └── datachat → ../../workspaces/datachat/.claude/skills/datachat  ← Required: for AionUi
```

## Available Skills

### Full Workflow

| Skill | Description | Use When |
|-------|-------------|----------|
| `datachat` | Complete 22-step SPSS analysis workflow | Analyze .sav files end-to-end |

### Modular Skills (Library Wrappers)

| Skill | Module | Use When |
|-------|--------|----------|
| `spss-statistics` | Statistics Calculator | Compute Chi-square and Cramer's V |
| `spss-filter` | Significance Filter | Filter tables by p-value, effect size |
| `spss-pspp` | PSPP Syntax & Executor | Generate RECODE/CTABLES syntax |
| `spss-reports` | Report Generator | Create PowerPoint and HTML reports |

### Skill Usage Matrix

```
┌─────────────┬───────────────┬──────────────┬──────────────┬──────────────┐
│   Task       │ spss-stat     │ spss-filter   │ spss-pspp     │ spss-reports │
├─────────────┼───────────────┼──────────────┼──────────────┼──────────────┤
│ Calc χ²      │       ✓       │              │              │              │
│ Filter sig   │               │       ✓      │              │              │
│ Recode vars  │               │              │       ✓      │              │
│ CTABLES      │               │              │       ✓      │              │
│ PowerPoint  │               │              │              │       ✓      │
│ HTML Dashboard│              │              │              │       ✓      │
│ Full workflow│   datachat ✓   │   datachat ✓   │   datachat ✓   │   datachat ✓   │
└─────────────┴───────────────┴──────────────┴──────────────┴──────────────┘
```

## Best Practices

1. **Default to project-level** for any project-specific skill
2. **Keep user-level for personal tools** only
3. **Document skill purpose** in SKILL.md frontmatter
4. **Use descriptive names** to avoid conflicts
5. **Version control** project skills with your code
6. **Test locally first** before committing project skills

---

**Decision Date**: 2026-02-09
**Status**: Implemented - datachat skill now at project-level
