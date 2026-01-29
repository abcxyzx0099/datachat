#!/usr/bin/env python3
"""
Debug Mode Runner for Agno Delphi Panel Evaluation

This script forces debug mode ON and saves all prompts and responses
for detailed inspection during development and troubleshooting.

Usage:
    python team_evaluator_debug.py

Output:
    - All prompts and responses saved to DEBUG_DIR
    - Same console output as standard mode
"""

import os
import sys
from pathlib import Path

# =============================================================================
# Force Debug Mode ON
# =============================================================================

# Set debug mode environment variables before importing main script
os.environ["DEBUG_MODE"] = "true"

# Allow override of debug directory via command line
if len(sys.argv) > 1:
    debug_dir = sys.argv[1]
    os.environ["DEBUG_DIR"] = debug_dir
    print(f"Using custom debug directory: {debug_dir}")

# =============================================================================
# Import and Run Main Script
# =============================================================================

# Add the scripts directory to path if needed
script_dir = Path(__file__).parent
if (script_dir / "team_evaluator.py").exists():
    sys.path.insert(0, str(script_dir))

print("=" * 60)
print("DELPHI PANEL - DEBUG MODE")
print("=" * 60)
print("All prompts and responses will be saved to disk")
print("for detailed inspection and analysis.\n")

try:
    from team_evaluator import main
    main()
except ImportError as e:
    print(f"\nERROR: Could not import team_evaluator.py")
    print(f"Ensure team_evaluator.py is in the same directory.")
    print(f"\nImport error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("DEBUG MODE COMPLETE")
print("=" * 60)
print("\nTo inspect the prompts and responses:")
print(f"  cd {os.getenv('DEBUG_DIR', 'docs/reports/debug')}")
print("  ls -la")
print("=" * 60)
