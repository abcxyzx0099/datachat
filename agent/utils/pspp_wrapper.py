"""
PSPP Wrapper Module

This module provides utilities for executing PSPP statistical software
via subprocess and parsing its output.

PSPP is a free replacement for the proprietary program SPSS.
"""

import subprocess
import logging
import os
from typing import Dict, Optional

from agent.config import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


def get_pspp_path() -> str:
    """
    Return PSPP path from config or default /usr/bin/pspp.

    Returns:
        Path to PSPP executable

    Raises:
        FileNotFoundError: If PSPP path does not exist
    """
    pspp_path = DEFAULT_CONFIG.get("pspp_path", "pspp")

    # If it's just the command name (not absolute path), verify it's available
    if os.path.sep not in pspp_path:
        # Try to find the full path using 'which' equivalent
        full_path = shutil.which(pspp_path)
        if full_path:
            return full_path
        # Fall through to validation below
    elif not os.path.exists(pspp_path):
        raise FileNotFoundError(
            f"PSPP executable not found at configured path: {pspp_path}"
        )

    return pspp_path


def verify_pspp_installation() -> bool:
    """
    Check if PSPP is available via pspp --version.

    Returns:
        True if PSPP is installed and accessible, False otherwise
    """
    try:
        pspp_path = get_pspp_path()
        result = subprocess.run(
            [pspp_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            # Log PSPP version (first line of output)
            version_line = result.stdout.split('\n')[0]
            logger.info(f"PSPP installation verified: {version_line.strip()}")
            return True
        else:
            logger.warning(f"PSPP --version returned non-zero exit code: {result.returncode}")
            return False
    except FileNotFoundError:
        logger.warning("PSPP executable not found in system PATH")
        return False
    except subprocess.TimeoutExpired:
        logger.warning("PSPP --version command timed out")
        return False
    except Exception as e:
        logger.warning(f"Error verifying PSPP installation: {e}")
        return False


def execute_pspp_syntax(
    syntax_file_path: str,
    input_file: str,
    output_file: str
) -> Dict:
    """
    Run PSPP in batch mode with the given syntax file.

    Executes: pspp -o output_file syntax_file_path

    Args:
        syntax_file_path: Path to .sps PSPP syntax file
        input_file: Path to input .sav file (used for validation)
        output_file: Path where PSPP output will be written

    Returns:
        Dict with keys:
            - success (bool): True if PSPP executed successfully
            - output (str): Standard output from PSPP
            - error (str): Standard error from PSPP
            - return_code (int): PSPP process exit code
            - user_message (str): User-friendly error message (if applicable)

    Example:
        >>> result = execute_pspp_syntax(
        ...     "temp/pspp_syntax/recoding.sps",
        ...     "data/survey.sav",
        ...     "output/pspp_output.txt"
        ... )
        >>> if result["success"]:
        ...     print("PSPP execution completed")
    """
    # Validate input files exist
    if not os.path.exists(syntax_file_path):
        return {
            "success": False,
            "output": "",
            "error": f"Syntax file not found: {syntax_file_path}",
            "return_code": -1,
            "user_message": f"The PSPP syntax file could not be found: {syntax_file_path}"
        }

    if not os.path.exists(input_file):
        return {
            "success": False,
            "output": "",
            "error": f"Input file not found: {input_file}",
            "return_code": -1,
            "user_message": f"The input data file could not be found: {input_file}"
        }

    # Get PSPP path
    try:
        pspp_path = get_pspp_path()
    except FileNotFoundError as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "return_code": -1,
            "user_message": "PSPP statistical software is not installed or not configured correctly."
        }

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            return {
                "success": False,
                "output": "",
                "error": f"Cannot create output directory: {e}",
                "return_code": -1,
                "user_message": f"Cannot create output directory: {output_dir}"
            }

    # Execute PSPP in batch mode
    logger.info(f"Executing PSPP: {pspp_path} -o {output_file} {syntax_file_path}")

    try:
        result = subprocess.run(
            [pspp_path, "-o", output_file, syntax_file_path],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        # Parse PSPP error messages for user-friendly output
        user_message = None
        if result.returncode != 0:
            user_message = _parse_pspp_error(result.stderr, result.stdout)

        logger.info(
            f"PSPP execution completed with return code: {result.returncode}"
        )

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode,
            "user_message": user_message
        }

    except subprocess.TimeoutExpired:
        logger.error("PSPP execution timed out after 5 minutes")
        return {
            "success": False,
            "output": "",
            "error": "PSPP execution timed out after 5 minutes",
            "return_code": -1,
            "user_message": "The PSPP analysis took too long to complete and timed out."
        }
    except Exception as e:
        logger.error(f"Error executing PSPP: {e}")
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "return_code": -1,
            "user_message": f"An unexpected error occurred while running PSPP: {e}"
        }


def _parse_pspp_error(stderr: str, stdout: str) -> Optional[str]:
    """
    Parse PSPP error messages to provide user-friendly output.

    Args:
        stderr: Standard error output from PSPP
        stdout: Standard output from PSPP

    Returns:
        User-friendly error message, or None if no specific error identified
    """
    error_output = stderr + stdout

    # Common PSPP error patterns
    error_patterns = {
        "File not found": "The data file specified in the syntax could not be found.",
        "cannot open": "PSPP could not open one of the required files.",
        "syntax error": "There is a syntax error in the PSPP commands.",
        "undefined variable": "A variable referenced in the syntax does not exist in the data file.",
        "out of range": "A value is outside the valid range for the operation.",
        "division by zero": "A mathematical operation resulted in division by zero.",
        "insufficient memory": "PSPP ran out of memory during processing.",
    }

    error_output_lower = error_output.lower()

    for pattern, message in error_patterns.items():
        if pattern.lower() in error_output_lower:
            return f"{message} Please check the PSPP syntax and data files."

    # Check for specific PSPP error codes
    if "error:" in error_output_lower:
        # Extract the first error line
        for line in error_output.split('\n'):
            if 'error:' in line.lower():
                return f"PSPP error: {line.strip()}"

    # Generic message
    return "PSPP encountered an error while processing the syntax file. Please check the syntax and try again."


# Import shutil at module level for get_pspp_path
import shutil
