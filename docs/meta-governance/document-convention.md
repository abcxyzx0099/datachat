# Document Convention

## Project Structure Documentation Principle

When documenting project structure, follow these guidelines:

### 1. Show Directory Levels

Display the directory hierarchy and subdirectory structure:

```
parent-directory/
├── subdirectory-one/
│   └── nested-subdirectory/
└── subdirectory-two/
```

### 2. List Individual Files Only When:

**a) Important standalone files at project root**

Examples: `.env`, `langgraph.json`, `pyproject.toml`, `requirements.txt`, `checkpoints.db`

```
project-root/
├── agent/
├── .env
├── langgraph.json
├── pyproject.toml
└── requirements.txt
```

**b) Directory contains only files (no subdirectories)**

If a directory only contains files and no subdirectories, list the files with brief descriptions.

### 3. Do Not List Files When:

- Directory contains both files and subdirectories
- Files are implementation details
- Files can be discovered by exploring the directory

### Summary

| Structure | Action |
|-----------|--------|
| Root level with subdirs | Show directories + important standalone files only |
| Directory with subdirs | Show subdirectories only |
| Directory with files only | Show files with descriptions |
| Nested structure | Show directory hierarchy only |
