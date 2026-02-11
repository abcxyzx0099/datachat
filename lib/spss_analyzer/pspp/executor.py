"""
PSPP Executor

Execute PSPP syntax files and extract results.

Example:
    >>> executor = PSPPExecutor()
    >>> result = executor.execute_syntax("recoding.sps", "input.sav", "output.sav")
    >>> if result.success:
    ...     print(f"Created {result.output_file}")
"""

import logging
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class PSPPResult:
    """
    Result of a PSPP execution.

    Attributes:
        success: Whether execution succeeded
        exit_code: Process exit code (0 = success)
        output_file: Path to output .sav file (if created)
        output_json: Path to output .json file (if created)
        stdout: Standard output from PSPP
        stderr: Standard error from PSPP
        error_message: Error message if execution failed
        execution_time: Execution time in seconds
    """
    success: bool
    exit_code: int
    output_file: Optional[str] = None
    output_json: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    error_message: Optional[str] = None
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "output_file": self.output_file,
            "output_json": self.output_json,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
        }


@dataclass
class PSPPConfig:
    """
    Configuration for PSPP execution.

    Attributes:
        pspp_path: Path to pspp CLI executable (default: 'pspp')
        timeout: Maximum execution time in seconds (default: 300)
        work_dir: Working directory for execution
        encoding: Character encoding (default: 'UTF-8')
    """
    pspp_path: str = "pspp"
    timeout: int = 300
    work_dir: Optional[str] = None
    encoding: str = "UTF-8"


class PSPPExecutor:
    """
    Execute PSPP syntax files with input/output management.

    Supports:
    - Reading SPSS files
    - Applying transformations (RECODE, COMPUTE, etc.)
    - Generating CTABLES output
    - Exporting to various formats

    Example:
        >>> executor = PSPPExecutor()
        >>> result = executor.execute_syntax(
        ...     syntax_file="recoding.sps",
        ...     input_file="original.sav",
        ...     output_file="recoded.sav"
        ... )
    """

    def __init__(
        self,
        config: Optional[PSPPConfig] = None,
    ):
        """
        Initialize the executor.

        Args:
            config: PSPP configuration (uses defaults if None)
        """
        self.config = config or PSPPConfig()

    def execute_syntax(
        self,
        syntax_file: str,
        input_file: Optional[str] = None,
        output_file: Optional[str] = None,
        output_json: Optional[str] = None,
    ) -> PSPPResult:
        """
        Execute a PSPP syntax file.

        Args:
            syntax_file: Path to .sps syntax file
            input_file: Optional path to input .sav file
            output_file: Optional path for output .sav file
            output_json: Optional path for output .json file

        Returns:
            PSPPResult with execution details

        Example:
            >>> executor = PSPPExecutor()
            >>> result = executor.execute_syntax(
            ...     "recoding.sps",
            ...     "original.sav",
            ...     "recoded.sav"
            ... )
        """
        start_time = datetime.now()

        # Build command
        cmd = self._build_command(syntax_file, input_file, output_file)

        logger.info(f"Executing PSPP: {' '.join(cmd)}")

        try:
            # Execute
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                cwd=self.config.work_dir,
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            # Check result
            success = completed.returncode == 0

            # Check output file exists
            actual_output = None
            if output_file and success:
                output_path = Path(output_file)
                if output_path.exists():
                    actual_output = str(output_path.absolute())
                else:
                    logger.warning(f"Output file not created: {output_file}")

            return PSPPResult(
                success=success,
                exit_code=completed.returncode,
                output_file=actual_output,
                stdout=completed.stdout,
                stderr=completed.stderr,
                execution_time=execution_time,
            )

        except subprocess.TimeoutExpired:
            execution_time = (datetime.now() - start_time).total_seconds()
            return PSPPResult(
                success=False,
                exit_code=-1,
                error_message=f"PSPP execution timed out after {self.config.timeout} seconds",
                execution_time=execution_time,
            )

        except FileNotFoundError:
            return PSPPResult(
                success=False,
                exit_code=-1,
                error_message=f"PSPP executable not found: {self.config.pspp_path}",
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return PSPPResult(
                success=False,
                exit_code=-1,
                error_message=f"Unexpected error: {str(e)}",
                execution_time=execution_time,
            )

    def _build_command(
        self,
        syntax_file: str,
        input_file: Optional[str],
        output_file: Optional[str],
    ) -> List[str]:
        """Build PSPP command line."""
        cmd = [self.config.pspp_path]

        # Output format (if specified)
        if output_file:
            cmd.extend(["-o", output_file])

        # Input file (if specified)
        if input_file:
            cmd.append(input_file)

        # Syntax file
        cmd.append(syntax_file)

        return cmd

    def check_pspp_available(self) -> bool:
        """
        Check if PSPP is available on the system.

        Returns:
            True if PSPP can be executed
        """
        try:
            result = subprocess.run(
                [self.config.pspp_path, "--version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_pspp_version(self) -> Optional[str]:
        """
        Get PSPP version string.

        Returns:
            Version string or None if PSPP not available
        """
        try:
            result = subprocess.run(
                [self.config.pspp_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                # Parse version from output
                for line in result.stdout.splitlines():
                    if "version" in line.lower():
                        return line.strip()
            return None

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None


def execute_pspp(
    syntax_file: str,
    input_file: Optional[str] = None,
    output_file: Optional[str] = None,
) -> PSPPResult:
    """
    Convenience function to execute PSPP syntax.

    Args:
        syntax_file: Path to .sps file
        input_file: Optional input .sav file
        output_file: Optional output .sav file

    Returns:
        PSPPResult

    Example:
        >>> result = execute_pspp("recoding.sps", "data.sav", "new_data.sav")
        >>> if result.success:
        ...     print("Recoding complete!")
    """
    executor = PSPPExecutor()
    return executor.execute_syntax(syntax_file, input_file, output_file)
