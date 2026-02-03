"""
Unit Tests for PSPP Wrapper Module

This module tests the PSPP wrapper utilities for executing PSPP statistical software:
- agent/utils/pspp_wrapper.py: PSPP command execution and output parsing

Test Coverage:
1. PSPP Path Resolution (get_pspp_path)
2. PSPP Installation Verification (verify_pspp_installation)
3. PSPP Syntax Execution (execute_pspp_syntax)
4. Error Message Parsing (_parse_pspp_error)
5. Edge Cases and Error Scenarios
6. Mock-based tests for CI/CD compatibility

All tests use mocks to work without PSPP installation in CI/CD environments.
"""

import sys
from pathlib import Path

# Add agent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import subprocess
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock, mock_open
from typing import Dict, Any

# Import module under test
from agent.utils.pspp_wrapper import (
    get_pspp_path,
    verify_pspp_installation,
    execute_pspp_syntax,
    _parse_pspp_error,
)


# =============================================================================
# PSPP Command Execution Tests
# =============================================================================

class TestGetPsppPath:
    """Tests for get_pspp_path() function."""

    def test_returns_default_pspp_command(self):
        """Test that default 'pspp' command is returned when not configured."""
        with patch('agent.utils.pspp_wrapper.DEFAULT_CONFIG', {}):
            with patch('agent.utils.pspp_wrapper.shutil.which') as mock_which:
                mock_which.return_value = "/usr/bin/pspp"
                result = get_pspp_path()
                assert result == "/usr/bin/pspp"
                mock_which.assert_called_once_with("pspp")

    def test_returns_configured_path(self):
        """Test that configured PSPP path is returned when set."""
        custom_path = "/custom/path/to/pspp"
        with patch('agent.utils.pspp_wrapper.DEFAULT_CONFIG', {"pspp_path": custom_path}):
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = True
                result = get_pspp_path()
                assert result == custom_path

    def test_raises_file_not_found_for_invalid_path(self):
        """Test FileNotFoundError for non-existent configured path."""
        invalid_path = "/nonexistent/path/to/pspp"
        with patch('agent.utils.pspp_wrapper.DEFAULT_CONFIG', {"pspp_path": invalid_path}):
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = False
                with pytest.raises(FileNotFoundError) as exc_info:
                    get_pspp_path()
                assert "PSPP executable not found" in str(exc_info.value)
                assert invalid_path in str(exc_info.value)

    def test_finds_pspp_in_path(self):
        """Test finding PSPP in system PATH when only command name provided."""
        with patch('agent.utils.pspp_wrapper.DEFAULT_CONFIG', {"pspp_path": "pspp"}):
            with patch('agent.utils.pspp_wrapper.shutil.which') as mock_which:
                mock_which.return_value = "/usr/bin/pspp"
                result = get_pspp_path()
                assert result == "/usr/bin/pspp"

    def test_returns_command_when_not_found_in_path(self):
        """Test that command name is returned even when not found (allows later failure)."""
        with patch('agent.utils.pspp_wrapper.DEFAULT_CONFIG', {"pspp_path": "custom-pspp"}):
            with patch('agent.utils.pspp_wrapper.shutil.which') as mock_which:
                mock_which.return_value = None
                result = get_pspp_path()
                # Should return the command name for later error during execution
                assert result == "custom-pspp"

    def test_absolute_path_without_separator(self):
        """Test handling of absolute path that doesn't contain os.sep."""
        # Edge case: some systems might have absolute paths without separator in config
        absolute_path = "pspp"
        with patch('agent.utils.pspp_wrapper.DEFAULT_CONFIG', {"pspp_path": absolute_path}):
            with patch('agent.utils.pspp_wrapper.shutil.which') as mock_which:
                mock_which.return_value = "/usr/bin/pspp"
                result = get_pspp_path()
                assert result == "/usr/bin/pspp"


class TestVerifyPsppInstallation:
    """Tests for verify_pspp_installation() function."""

    def test_successful_verification(self):
        """Test successful PSPP installation verification."""
        mock_version_output = "PSPP 2.0.1\nCopyright (C) 2024 Free Software Foundation"
        with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
            mock_get_path.return_value = "/usr/bin/pspp"
            with patch('subprocess.run') as mock_run:
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = mock_version_output
                mock_run.return_value = mock_result

                result = verify_pspp_installation()
                assert result is True
                mock_run.assert_called_once_with(
                    ["/usr/bin/pspp", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

    def test_pspp_not_found(self):
        """Test handling when PSPP executable is not found."""
        with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
            mock_get_path.side_effect = FileNotFoundError("PSPP not found")

            result = verify_pspp_installation()
            assert result is False

    def test_non_zero_exit_code(self):
        """Test handling when PSPP returns non-zero exit code."""
        with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
            mock_get_path.return_value = "/usr/bin/pspp"
            with patch('subprocess.run') as mock_run:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stdout = ""
                mock_run.return_value = mock_result

                result = verify_pspp_installation()
                assert result is False

    def test_timeout_during_verification(self):
        """Test handling when PSPP --version times out."""
        with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
            mock_get_path.return_value = "/usr/bin/pspp"
            with patch('subprocess.run') as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired("pspp", 10)

                result = verify_pspp_installation()
                assert result is False

    def test_unexpected_exception(self):
        """Test handling of unexpected exceptions during verification."""
        with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
            mock_get_path.side_effect = PermissionError("Access denied")

            result = verify_pspp_installation()
            assert result is False


# =============================================================================
# Output Parsing Tests
# =============================================================================

class TestParsePsppError:
    """Tests for _parse_pspp_error() function."""

    def test_file_not_found_error(self):
        """Test parsing of 'File not found' error."""
        stderr = "error: opening /path/to/file.sav: No such file or directory"
        result = _parse_pspp_error(stderr, "")
        # The error parser will fall through to generic error: message extraction
        assert "PSPP error" in result or "error:" in result.lower()

    def test_cannot_open_error(self):
        """Test parsing of 'cannot open' error."""
        stderr = "error: cannot open output file"
        result = _parse_pspp_error(stderr, "")
        assert "could not open" in result.lower()

    def test_syntax_error(self):
        """Test parsing of 'syntax error'."""
        stderr = "error: syntax error on line 15"
        result = _parse_pspp_error(stderr, "")
        assert "syntax error" in result.lower()

    def test_undefined_variable_error(self):
        """Test parsing of 'undefined variable' error."""
        stderr = "error: undefined variable 'age_group'"
        result = _parse_pspp_error(stderr, "")
        assert "variable" in result.lower() and "exist" in result.lower()

    def test_out_of_range_error(self):
        """Test parsing of 'out of range' error."""
        stderr = "error: value out of range"
        result = _parse_pspp_error(stderr, "")
        assert "range" in result.lower()

    def test_division_by_zero_error(self):
        """Test parsing of 'division by zero' error."""
        stderr = "error: division by zero"
        result = _parse_pspp_error(stderr, "")
        assert "division" in result.lower() or "mathematical" in result.lower()

    def test_insufficient_memory_error(self):
        """Test parsing of 'insufficient memory' error."""
        stderr = "error: insufficient memory"
        result = _parse_pspp_error(stderr, "")
        assert "memory" in result.lower()

    def test_generic_error_with_error_colon(self):
        """Test parsing of generic error containing 'error:'."""
        stderr = "error: something went wrong"
        result = _parse_pspp_error(stderr, "")
        assert "PSPP error" in result

    def test_error_in_stdout(self):
        """Test that errors in stdout are also parsed."""
        stdout = "error: syntax error on line 10"
        result = _parse_pspp_error("", stdout)
        assert "syntax error" in result.lower()

    def test_mixed_stderr_and_stdout(self):
        """Test parsing errors that appear in both stderr and stdout."""
        stderr = "error: cannot open"
        stdout = "Additional error details"
        result = _parse_pspp_error(stderr, stdout)
        assert "open" in result.lower()

    def test_unknown_error_returns_generic_message(self):
        """Test that unknown errors return generic message."""
        stderr = "Some unknown error occurred"
        result = _parse_pspp_error(stderr, "")
        assert "PSPP encountered an error" in result

    def test_case_insensitive_pattern_matching(self):
        """Test that pattern matching is case-insensitive."""
        stderr = "ERROR: SYNTAX ERROR ON LINE 5"
        result = _parse_pspp_error(stderr, "")
        assert "syntax error" in result.lower()

    def test_empty_error_output(self):
        """Test handling of empty error output."""
        result = _parse_pspp_error("", "")
        # Should return generic message or None
        assert result is None or "PSPP" in result


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestExecutePsppSyntaxErrorHandling:
    """Tests for error handling in execute_pspp_syntax()."""

    def test_syntax_file_not_found(self):
        """Test handling when syntax file doesn't exist."""
        result = execute_pspp_syntax(
            syntax_file_path="/nonexistent/syntax.sps",
            input_file="/path/to/input.sav",
            output_file="/path/to/output.txt"
        )

        assert result["success"] is False
        assert result["return_code"] == -1
        assert "not found" in result["error"].lower()
        assert "user_message" in result

    def test_input_file_not_found(self):
        """Test handling when input data file doesn't exist."""
        # Create a temporary syntax file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        try:
            result = execute_pspp_syntax(
                syntax_file_path=syntax_path,
                input_file="/nonexistent/input.sav",
                output_file="/path/to/output.txt"
            )

            assert result["success"] is False
            assert result["return_code"] == -1
            assert "not found" in result["error"].lower()
            assert "input" in result["error"].lower() or "data" in result["error"].lower()
        finally:
            os.unlink(syntax_path)

    def test_pspp_executable_not_found(self):
        """Test handling when PSPP executable is not found."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.side_effect = FileNotFoundError("PSPP not found")

                result = execute_pspp_syntax(
                    syntax_file_path=syntax_path,
                    input_file=input_path,
                    output_file="/tmp/output.txt"
                )

                assert result["success"] is False
                assert result["return_code"] == -1
                assert "PSPP" in result["user_message"]
                assert "not installed" in result["user_message"].lower()
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_timeout_during_execution(self):
        """Test handling when PSPP execution times out."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_run.side_effect = subprocess.TimeoutExpired("pspp", 300)

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is False
                    assert result["return_code"] == -1
                    assert "timed out" in result["error"].lower()
                    assert "timed out" in result["user_message"].lower()
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_unexpected_exception_during_execution(self):
        """Test handling of unexpected exceptions during PSPP execution."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_run.side_effect = PermissionError("Access denied")

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is False
                    assert result["return_code"] == -1
                    assert "unexpected error" in result["user_message"].lower()
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_output_directory_creation_failure(self):
        """Test handling when output directory cannot be created."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        # Try to write to a directory we can't create
        output_path = "/root/nonexistent/output.txt"

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('os.makedirs') as mock_makedirs:
                    mock_makedirs.side_effect = OSError("Permission denied")

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file=output_path
                    )

                    assert result["success"] is False
                    assert result["return_code"] == -1
                    assert "output directory" in result["error"].lower()
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)


# =============================================================================
# PSPP Command Execution Tests (Successful)
# =============================================================================

class TestExecutePsppSyntaxSuccess:
    """Tests for successful PSPP execution scenarios."""

    def test_successful_execution(self):
        """Test successful PSPP execution with exit code 0."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            output_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = "PSPP processing complete"
                    mock_result.stderr = ""
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file=output_path
                    )

                    assert result["success"] is True
                    assert result["return_code"] == 0
                    assert result["output"] == "PSPP processing complete"
                    assert result["error"] == ""
                    assert result["user_message"] is None

                    # Verify subprocess was called correctly
                    mock_run.assert_called_once()
                    call_args = mock_run.call_args
                    assert call_args[0][0] == ["/usr/bin/pspp", "-o", output_path, syntax_path]
                    assert call_args[1]["capture_output"] is True
                    assert call_args[1]["text"] is True
                    assert call_args[1]["timeout"] == 300
        finally:
            # Cleanup
            for path in [syntax_path, input_path, output_path]:
                if os.path.exists(path):
                    os.unlink(path)

    def test_successful_execution_with_output_directory_creation(self):
        """Test successful execution when output directory needs to be created."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        # Create a temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "subdir", "output.txt")

            try:
                with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                    mock_get_path.return_value = "/usr/bin/pspp"
                    with patch('subprocess.run') as mock_run:
                        mock_result = Mock()
                        mock_result.returncode = 0
                        mock_result.stdout = ""
                        mock_result.stderr = ""
                        mock_run.return_value = mock_result

                        result = execute_pspp_syntax(
                            syntax_file_path=syntax_path,
                            input_file=input_path,
                            output_file=output_path
                        )

                        assert result["success"] is True
                        # Verify directory was created
                        assert os.path.exists(os.path.dirname(output_path))
            finally:
                os.unlink(syntax_path)
                os.unlink(input_path)

    def test_execution_with_non_zero_exit_code(self):
        """Test PSPP execution with non-zero exit code (error)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 1
                    mock_result.stdout = ""
                    mock_result.stderr = "error: syntax error on line 10"
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is False
                    assert result["return_code"] == 1
                    assert "syntax error" in result["user_message"].lower()
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_execution_parses_error_from_stdout(self):
        """Test that errors are parsed from stdout when stderr is empty."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 1
                    mock_result.stdout = "error: undefined variable 'age'"
                    mock_result.stderr = ""
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is False
                    assert "variable" in result["user_message"].lower()
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)


# =============================================================================
# File Path Handling Tests
# =============================================================================

class TestFilePathHandling:
    """Tests for file path handling in PSPP wrapper."""

    def test_relative_syntax_file_path(self):
        """Test handling of relative file paths."""
        with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
            mock_get_path.return_value = "/usr/bin/pspp"
            with patch('subprocess.run') as mock_run:
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = ""
                mock_result.stderr = ""
                mock_run.return_value = mock_result

                # Use relative paths that exist
                result = execute_pspp_syntax(
                    syntax_file_path="tests/conftest.py",  # Existing file
                    input_file="tests/conftest.py",  # Existing file
                    output_file="/tmp/output.txt"
                )

                assert result["success"] is True

    def test_absolute_file_paths(self):
        """Test handling of absolute file paths."""
        # Create temporary files with absolute paths
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = os.path.abspath(f.name)
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = os.path.abspath(f.name)

        output_path = os.path.abspath("/tmp/test_pspp_output.txt")

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = ""
                    mock_result.stderr = ""
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file=output_path
                    )

                    assert result["success"] is True
                    # Verify absolute paths were passed correctly
                    call_args = mock_run.call_args[0][0]
                    assert syntax_path in call_args
                    assert output_path in call_args
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_output_directory_creation_with_nested_paths(self):
        """Test creating nested output directories."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        with tempfile.TemporaryDirectory() as temp_dir:
            # Nested directory path
            nested_path = os.path.join(temp_dir, "level1", "level2", "level3", "output.txt")

            try:
                with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                    mock_get_path.return_value = "/usr/bin/pspp"
                    with patch('subprocess.run') as mock_run:
                        mock_result = Mock()
                        mock_result.returncode = 0
                        mock_result.stdout = ""
                        mock_result.stderr = ""
                        mock_run.return_value = mock_result

                        result = execute_pspp_syntax(
                            syntax_file_path=syntax_path,
                            input_file=input_path,
                            output_file=nested_path
                        )

                        assert result["success"] is True
                        # Verify nested directories were created
                        assert os.path.exists(os.path.dirname(nested_path))
            finally:
                os.unlink(syntax_path)
                os.unlink(input_path)


# =============================================================================
# Mock Tests for CI/CD Compatibility
# =============================================================================

class TestMockBasedTests:
    """Tests using mocks for CI/CD environments without PSPP."""

    @pytest.fixture
    def mock_successful_pspp_run(self):
        """Fixture that mocks successful PSPP execution."""
        with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
            mock_get_path.return_value = "/usr/bin/pspp"
            with patch('subprocess.run') as mock_run:
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = "Processing complete"
                mock_result.stderr = ""
                mock_run.return_value = mock_result
                yield mock_run

    @pytest.fixture
    def mock_failed_pspp_run(self):
        """Fixture that mocks failed PSPP execution."""
        with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
            mock_get_path.return_value = "/usr/bin/pspp"
            with patch('subprocess.run') as mock_run:
                mock_result = Mock()
                mock_result.returncode = 1
                mock_result.stdout = ""
                mock_result.stderr = "error: syntax error"
                mock_run.return_value = mock_result
                yield mock_run

    def test_mocked_success_scenario(self, mock_successful_pspp_run):
        """Test successful execution with mocked PSPP."""
        result = execute_pspp_syntax(
            syntax_file_path="tests/conftest.py",
            input_file="tests/conftest.py",
            output_file="/tmp/output.txt"
        )

        assert result["success"] is True
        assert result["return_code"] == 0

    def test_mocked_failure_scenario(self, mock_failed_pspp_run):
        """Test failed execution with mocked PSPP."""
        result = execute_pspp_syntax(
            syntax_file_path="tests/conftest.py",
            input_file="tests/conftest.py",
            output_file="/tmp/output.txt"
        )

        assert result["success"] is False
        assert result["return_code"] == 1
        assert "syntax error" in result["user_message"].lower()

    def test_mocked_various_exit_codes(self):
        """Test behavior with various PSPP exit codes."""
        for exit_code in [1, 2, 127, 255]:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = exit_code
                    mock_result.stdout = f"Exit code {exit_code}"
                    mock_result.stderr = "error occurred"
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path="tests/conftest.py",
                        input_file="tests/conftest.py",
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is False
                    assert result["return_code"] == exit_code

    def test_mocked_various_stderr_outputs(self):
        """Test error parsing with various stderr outputs."""
        test_cases = [
            ("error: undefined variable", "variable"),
            ("error: syntax error", "syntax"),
            ("error: cannot open file", "open"),
            ("error: File not found", "found"),
            ("error: division by zero", "division"),
        ]

        for stderr, expected_keyword in test_cases:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 1
                    mock_result.stdout = ""
                    mock_result.stderr = stderr
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path="tests/conftest.py",
                        input_file="tests/conftest.py",
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is False
                    assert expected_keyword in result["user_message"].lower()


# =============================================================================
# Integration-style Tests (with temp files)
# =============================================================================

class TestIntegrationStyleTests:
    """Integration-style tests using temporary files."""

    def test_valid_pspp_syntax_file_content(self):
        """Test that valid PSPP syntax can be written and executed."""
        # Create a temporary PSPP syntax file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            # Write valid PSPP syntax
            f.write("* PSPP Syntax File\n")
            f.write("GET FILE='/path/to/data.sav'.\n")
            f.write("EXECUTE.\n")
            f.write("RECODE age (18 THRU 35=1) (35 THRU 50=2) (50 THRU HI=3) INTO age_group.\n")
            f.write("VARIABLE LABELS age_group 'Age Group'.\n")
            f.write("VALUE LABELS age_group 1 'Young' 2 'Middle' 3 'Older'.\n")
            f.write("EXECUTE.\n")
            f.write("SAVE OUTFILE='/path/to/output.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            # Verify file exists and is readable
            assert os.path.exists(syntax_path)
            with open(syntax_path, 'r') as f:
                content = f.read()
                assert "RECODE" in content
                assert "age_group" in content

            # Test with mocked execution
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = ""
                    mock_result.stderr = ""
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is True
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_file_cleanup_after_test(self):
        """Test that temporary files are properly cleaned up."""
        temp_files = []

        # Create temporary files
        for suffix in ['.sps', '.sav', '.txt']:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
                temp_files.append(f.name)

        # Verify files exist
        for file_path in temp_files:
            assert os.path.exists(file_path)

        # Cleanup
        for file_path in temp_files:
            os.unlink(file_path)

        # Verify files are deleted
        for file_path in temp_files:
            assert not os.path.exists(file_path)


# =============================================================================
# Edge Cases and Boundary Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_syntax_file(self):
        """Test handling of empty syntax file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            # Write empty file

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    # PSPP might fail with empty syntax
                    mock_result = Mock()
                    mock_result.returncode = 1
                    mock_result.stdout = ""
                    mock_result.stderr = "error: no commands to execute"
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is False
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_very_long_file_paths(self):
        """Test handling of very long file paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a deeply nested path
            long_path = temp_dir
            for i in range(10):
                long_path = os.path.join(long_path, f"subdir_{i}")

            output_path = os.path.join(long_path, "output.txt")

            with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
                syntax_path = f.name
                f.write("GET FILE='data.sav'.\n")

            with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
                input_path = f.name

            try:
                with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                    mock_get_path.return_value = "/usr/bin/pspp"
                    with patch('subprocess.run') as mock_run:
                        mock_result = Mock()
                        mock_result.returncode = 0
                        mock_result.stdout = ""
                        mock_result.stderr = ""
                        mock_run.return_value = mock_result

                        result = execute_pspp_syntax(
                            syntax_file_path=syntax_path,
                            input_file=input_path,
                            output_file=output_path
                        )

                        assert result["success"] is True
            finally:
                os.unlink(syntax_path)
                os.unlink(input_path)

    def test_special_characters_in_file_paths(self):
        """Test handling of special characters in file paths."""
        # Create files with spaces and special characters
        with tempfile.NamedTemporaryFile(mode='w', suffix=' test file.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix=' data-test.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = ""
                    mock_result.stderr = ""
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output test.txt"
                    )

                    assert result["success"] is True
        finally:
            if os.path.exists(syntax_path):
                os.unlink(syntax_path)
            if os.path.exists(input_path):
                os.unlink(input_path)

    def test_unicode_content_in_syntax_file(self):
        """Test handling of Unicode characters in syntax file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False, encoding='utf-8') as f:
            syntax_path = f.name
            f.write("* PSPP Syntax with Unicode: café, naïve, 日本語\n")
            f.write("VARIABLE LABELS var 'Étiquette en français'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = ""
                    mock_result.stderr = ""
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file="/tmp/output.txt"
                    )

                    assert result["success"] is True
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)

    def test_output_in_root_directory(self):
        """Test output path with no directory (just filename)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sps', delete=False) as f:
            syntax_path = f.name
            f.write("GET FILE='data.sav'.\n")

        with tempfile.NamedTemporaryFile(suffix='.sav', delete=False) as f:
            input_path = f.name

        # Output file with no directory prefix
        output_path = "output.txt"

        try:
            with patch('agent.utils.pspp_wrapper.get_pspp_path') as mock_get_path:
                mock_get_path.return_value = "/usr/bin/pspp"
                with patch('subprocess.run') as mock_run:
                    mock_result = Mock()
                    mock_result.returncode = 0
                    mock_result.stdout = ""
                    mock_result.stderr = ""
                    mock_run.return_value = mock_result

                    result = execute_pspp_syntax(
                        syntax_file_path=syntax_path,
                        input_file=input_path,
                        output_file=output_path
                    )

                    assert result["success"] is True
        finally:
            os.unlink(syntax_path)
            os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
