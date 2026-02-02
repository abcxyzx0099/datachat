"""
Security Module

This module provides security utilities for file path validation, JSON sanitization,
and executable path validation to prevent path traversal, command injection, XSS,
and prototype pollution attacks.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def validate_file_path(
    file_path: str,
    allowed_extensions: Optional[List[str]] = None,
    allow_absolute: bool = False
) -> str:
    """
    Validate a file path to prevent path traversal attacks.

    Args:
        file_path: The file path to validate
        allowed_extensions: List of allowed file extensions (e.g., ['.sav', '.json'])
        allow_absolute: Whether to allow absolute paths

    Returns:
        The normalized file path

    Raises:
        ValueError: If the path contains dangerous patterns or invalid extensions
    """
    if not file_path:
        raise ValueError("File path cannot be empty")

    # Normalize the path
    normalized = os.path.normpath(file_path)

    # Check for path traversal attempts
    if '../' in normalized or '..\\' in normalized:
        raise ValueError(f"Path traversal detected in: {file_path}")

    # Check for null bytes
    if '\x00' in file_path:
        raise ValueError("Null byte detected in file path")

    # Reject URLs or remote paths
    if re.match(r'^https?://', file_path):
        raise ValueError(f"URLs are not allowed as file paths: {file_path}")

    # Check for shell metacharacters that could be used for injection
    dangerous_chars = ['|', '&', ';', '$', '`', '(', ')', '<', '>', '\n', '\r']
    if any(char in file_path for char in dangerous_chars):
        raise ValueError(f"Dangerous characters detected in file path: {file_path}")

    # Validate extension if provided
    if allowed_extensions:
        # Normalize extensions to include leading dot
        normalized_extensions = [
            ext if ext.startswith('.') else f'.{ext}'
            for ext in allowed_extensions
        ]

        file_ext = Path(normalized).suffix.lower()
        if file_ext not in [ext.lower() for ext in normalized_extensions]:
            raise ValueError(
                f"File extension '{file_ext}' not allowed. "
                f"Allowed: {', '.join(normalized_extensions)}"
            )

    return normalized


def validate_executable_path(path: str) -> str:
    """
    Validate an executable path to prevent command injection.

    Args:
        path: Path to the executable

    Returns:
        The validated, normalized path

    Raises:
        ValueError: If the path contains dangerous patterns
        FileNotFoundError: If the executable doesn't exist
    """
    if not path:
        raise ValueError("Executable path cannot be empty")

    # Check for shell injection patterns
    dangerous_patterns = ['|', '&', ';', '$', '`', '(', ')', '<', '>', '\n', '\r', '\x00']
    if any(pattern in path for pattern in dangerous_patterns):
        raise ValueError(f"Dangerous characters detected in executable path: {path}")

    # If it's just a command name (no path separator), return as-is
    # This allows things like "pspp" or "python" which will be found in PATH
    if os.sep not in path and '/' not in path:
        return path

    # Normalize the path
    normalized = os.path.normpath(path)

    # Resolve to absolute path
    absolute = os.path.abspath(normalized)

    # Check for path traversal
    if '../' in absolute or '..\\' in absolute:
        raise ValueError(f"Path traversal detected in: {path}")

    # Verify the file exists and is executable
    if not os.path.exists(absolute):
        raise FileNotFoundError(f"Executable not found: {absolute}")

    if not os.path.isfile(absolute):
        raise ValueError(f"Path is not a file: {absolute}")

    return absolute


def sanitize_json_output(data: Any) -> Any:
    """
    Sanitize JSON data for output to prevent XSS attacks.

    This function recursively sanitizes string values in JSON-serializable data
    by escaping HTML special characters.

    Args:
        data: The data to sanitize (dict, list, or primitive)

    Returns:
        Sanitized data with HTML special characters escaped in strings
    """
    if isinstance(data, str):
        # Escape HTML special characters to prevent XSS
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
            '/': '&#x2F;',
        }
        for char, escaped in replacements.items():
            data = data.replace(char, escaped)
        return data

    elif isinstance(data, dict):
        return {key: sanitize_json_output(value) for key, value in data.items()}

    elif isinstance(data, list):
        return [sanitize_json_output(item) for item in data]

    else:
        # Numbers, booleans, None - return as-is
        return data


def sanitize_json_input(data: Any) -> Any:
    """
    Sanitize JSON input to prevent prototype pollution and other attacks.

    This function removes dangerous keys that could be used for prototype
    pollution attacks and validates the structure of the input.

    Args:
        data: The JSON data to sanitize

    Returns:
        Sanitized data with dangerous keys removed

    Raises:
        ValueError: If the data contains dangerous structures
    """
    # Dangerous keys for prototype pollution
    dangerous_keys = {
        '__proto__',
        'constructor',
        'prototype',
        '__defineGetter__',
        '__defineSetter__',
        '__lookupGetter__',
        '__lookupSetter__',
    }

    def _sanitize(obj: Any, path: str = 'root') -> Any:
        if isinstance(obj, dict):
            sanitized = {}
            for key, value in obj.items():
                # Check for prototype pollution attempts
                if key in dangerous_keys:
                    continue  # Skip dangerous keys

                # Check for nested keys with dots (could be used for pollution)
                if '.' in key and '__proto__' in key.lower():
                    continue

                sanitized[key] = _sanitize(value, f"{path}.{key}")
            return sanitized

        elif isinstance(obj, list):
            return [_sanitize(item, f"{path}[]") for item in obj]

        else:
            # Primitives are safe
            return obj

    return _sanitize(data)
