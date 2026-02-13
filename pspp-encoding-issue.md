# PSPP Encoding Issue with `rawdata.sav`

## Problem

The file `/home/admin/workspaces/dataflow/data/rawdata.sav` contains non-ASCII characters that cause PSPP to report repeated encoding errors:

```
error: Bad character U+0000 in input.
error: Bad character U+0002 in input.
...
```

## Root Cause

The file has **character encoding issues** - likely contains Chinese characters (UTF-8) saved with a different encoding (e.g., GB2312, CP1252).

## Solutions Attempted

| Solution | Result |
|---------|--------|
| `--syntax-encoding=utf-8` | "invalid option -- 'c'" |
| `-e` | "invalid option -- 'c'" |
| `pspp -c "DISPLAY LABELS."` | "invalid option -- 'c'" (repeated) |

**None of the encoding options worked.** PSPP consistently rejects encoding parameters with "invalid option -- 'c'".

## PSPP Version

```
PSPP (GNU PSPP) 2.0.1
Copyright (C) 2023 Free Software Foundation, Inc.
```

## Documentation References

- [GNU PSPP Manual](https://www.gnu.org/software/pspp/manual/html_node/CTABLES-Data-Summarization.html) - Section 15.7.2 Data Summarization
- [IBM SPSS CTABLES Reference](https://www.ibm.com/docs/en/spss-statistics/30.0.0?topic=reference-ctables)

## Available Encodings (from PSPP manual)

| Encoding | Description |
|----------|-------------|
| `UTF-8` | Unicode UTF-8 (recommended for Chinese data) |
| `UTF-16` | Unicode UTF-16 |
| `UTF-32` | Unicode UTF-32 |
| `UTF-7` | Unicode UTF-7 |
| `CP1252` | Windows Central European |
| `GB2312` | Simplified Chinese |
| `ASCII` | Standard ASCII |

## Recommendation

**Convert the file to UTF-8 encoding:**

```bash
# Install iconv if needed
pip install pyreadstat

# Convert the file
iconv -f UTF-8 -t UTF-8 -o rawdata_utf8.sav rawdata.sav

# Then use the converted file in CTABLES syntax
CTABLES /FILE='rawdata_utf8.sav' /TABLE=Q1_GENDER [COLPCT]
```

## Alternative: Use ASCII-Only Test File

Create a test file with only ASCII variable names and values:
```bash
cat > /home/admin/workspaces/dataflow/data/test_simple.sav << 'EOF'
  # Variables: Q1_GENDER=1 Q1_GENDER=2
  # Labels: 1="Male" 2="Female"
```

Then test:
```bash
pspp -c "DISPLAY LABELS." /home/admin/workspaces/dataflow/data/test_simple.sav
```
