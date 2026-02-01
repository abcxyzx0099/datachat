"""
Logging Configuration Module

This module provides structured logging configuration for the DataChat
workflow, supporting multiple log levels, timestamped log files, and PSPP
log capture.

Log Levels:
    - DEBUG: Detailed execution trace for troubleshooting
    - INFO: Step start, completion, key outputs
    - WARNING: Validation failures, skipped items
    - ERROR: Exceptions, failures

Log File Locations:
    - Standard logs: output/logs/{timestamp}.log
    - Debug logs: output/logs/debug/{timestamp}.log
    - PSPP logs: output/pspp_logs.txt
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional
import subprocess


# Global flag to ensure setup_logging is only called once
_logging_configured = False


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "output/logs"
) -> logging.Logger:
    """
    Configure and initialize structured logging for the DataChat workflow.

    This function sets up three log handlers:
    1. File handler for standard logs (INFO and above) -> output/logs/{timestamp}.log
    2. Debug file handler for all logs (DEBUG and above) -> output/logs/debug/{timestamp}.log
    3. Console handler for stdout (configured level)

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
                   Defaults to INFO. Can be overridden by LOG_LEVEL env variable.
        log_dir: Directory for log files. Defaults to "output/logs".

    Returns:
        Configured logger instance with name "datachat".

    Raises:
        ValueError: If log_level is not a valid logging level.

    Example:
        >>> from utils.logging import setup_logging
        >>> logger = setup_logging()
        >>> logger.info("Workflow started")
        2024-01-31 14:30:22 - INFO - datachat - Workflow started
    """
    global _logging_configured

    # Read LOG_LEVEL from environment if available
    env_log_level = os.getenv("LOG_LEVEL", "").upper()
    if env_log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        log_level = env_log_level

    # Validate log level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}. Must be DEBUG, INFO, WARNING, or ERROR.")

    # Prevent duplicate configuration
    if _logging_configured:
        return logging.getLogger("datachat")

    # Create log directories
    os.makedirs(log_dir, exist_ok=True)
    debug_log_dir = os.path.join(log_dir, "debug")
    os.makedirs(debug_log_dir, exist_ok=True)

    # Generate timestamp for log files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create logger
    logger = logging.getLogger("datachat")
    logger.setLevel(logging.DEBUG)  # Capture all levels, handlers control output

    # Remove any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Define log format
    log_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Standard file handler (INFO and above)
    standard_log_file = os.path.join(log_dir, f"{timestamp}.log")
    standard_handler = logging.FileHandler(standard_log_file, encoding="utf-8")
    standard_handler.setLevel(logging.INFO)
    standard_handler.setFormatter(log_format)
    logger.addHandler(standard_handler)

    # 2. Debug file handler (DEBUG and above)
    debug_log_file = os.path.join(debug_log_dir, f"{timestamp}.log")
    debug_handler = logging.FileHandler(debug_log_file, encoding="utf-8")
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(log_format)
    logger.addHandler(debug_handler)

    # 3. Console handler (configured level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    # Mark as configured
    _logging_configured = True

    logger.info(f"Logging initialized: Level={log_level}, Standard={standard_log_file}, Debug={debug_log_file}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name, using the DataChat logging configuration.

    This function returns a child logger that inherits the configuration
    from the main "datachat" logger. Use this for module-specific logging.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        Configured logger instance.

    Example:
        >>> from utils.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing step 1")
        2024-01-31 14:30:22 - INFO - agent.nodes.phase1_extraction - Processing step 1
    """
    # Ensure logging is configured
    if not _logging_configured:
        setup_logging()

    # Return child logger with the specified name
    return logging.getLogger(f"datachat.{name}")


def capture_pspp_logs(
    pspp_output_dir: str = "output",
    log_file: str = "pspp_logs.txt"
) -> subprocess.Popen:
    """
    Capture PSPP subprocess output to a dedicated log file.

    This function creates a file object that can be used to redirect
    PSPP stdout and stderr to output/pspp_logs.txt.

    Args:
        pspp_output_dir: Directory for PSPP log file. Defaults to "output".
        log_file: Name of the PSPP log file. Defaults to "pspp_logs.txt".

    Returns:
        File object for writing PSPP output.

    Example:
        >>> from utils.logging import setup_logging, capture_pspp_logs
        >>> logger = setup_logging()
        >>> pspp_log = capture_pspp_logs()
        >>> # Use with subprocess
        >>> subprocess.run(["pspp", "-o", "out.txt", "syntax.sps"],
        ...                stdout=pspp_log, stderr=pspp_log)
        >>> pspp_log.close()
    """
    # Ensure output directory exists
    os.makedirs(pspp_output_dir, exist_ok=True)

    # Create log file path
    log_path = os.path.join(pspp_output_dir, log_file)

    # Open file for writing (overwrites previous PSPP logs)
    log_file_obj = open(log_path, "w", encoding="utf-8")

    return log_file_obj


def redirect_pspp_output(
    command: list,
    pspp_output_dir: str = "output",
    log_file: str = "pspp_logs.txt"
) -> dict:
    """
    Execute PSPP command and capture all output to log file.

    This is a convenience function that runs a PSPP command and
    automatically captures stdout and stderr to the PSPP log file.

    Args:
        command: PSPP command as a list (e.g., ["pspp", "-o", "out.txt", "syntax.sps"])
        pspp_output_dir: Directory for PSPP log file. Defaults to "output".
        log_file: Name of the PSPP log file. Defaults to "pspp_logs.txt".

    Returns:
        Dict with keys:
            - success (bool): True if return code is 0
            - return_code (int): Process exit code
            - log_file (str): Path to PSPP log file

    Example:
        >>> from utils.logging import redirect_pspp_output
        >>> result = redirect_pspp_output(["pspp", "-o", "out.txt", "syntax.sps"])
        >>> if result["success"]:
        ...     print("PSPP executed successfully")
    """
    log_path = os.path.join(pspp_output_dir, log_file)

    with open(log_path, "w", encoding="utf-8") as log_file_obj:
        try:
            result = subprocess.run(
                command,
                stdout=log_file_obj,
                stderr=subprocess.STDOUT,  # Combine stderr into stdout
                text=True,
                timeout=300  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "log_file": log_path
            }

        except subprocess.TimeoutExpired:
            log_file_obj.write("\n[ERROR] PSPP execution timed out after 5 minutes\n")
            return {
                "success": False,
                "return_code": -1,
                "log_file": log_path
            }
        except Exception as e:
            log_file_obj.write(f"\n[ERROR] PSPP execution failed: {e}\n")
            return {
                "success": False,
                "return_code": -1,
                "log_file": log_path
            }
