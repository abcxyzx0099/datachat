"""
File I/O Module

This module provides utilities for reading and writing various file formats
used in the survey analysis workflow, including SPSS .sav files, CSV, and JSON.
"""

import json
import logging
import os
from typing import Dict, Tuple

import pandas as pd
import pyreadstat

logger = logging.getLogger(__name__)


def read_spss_file(file_path: str) -> Tuple[pd.DataFrame, Dict]:
    """
    Read an SPSS .sav file using pyreadstat.

    Args:
        file_path: Path to the .sav file

    Returns:
        Tuple of (dataframe, metadata) where:
            - dataframe: pandas DataFrame with the data
            - metadata: Dictionary with column labels, value labels, etc.

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read due to permissions
        ValueError: If the file is not a valid SPSS file

    Example:
        >>> df, metadata = read_spss_file("data/survey.sav")
        >>> print(metadata['column_labels'])
        {'q1': 'Question 1', 'q2': 'Question 2'}
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"SPSS file not found: {file_path}")

    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read SPSS file (permission denied): {file_path}")

    try:
        df, metadata = pyreadstat.read_sav(file_path, apply_value_formats=True)

        logger.info(
            f"Successfully read SPSS file: {file_path} "
            f"({len(df)} rows, {len(df.columns)} columns)"
        )

        return df, metadata

    except FileNotFoundError:
        raise
    except PermissionError:
        raise
    except pyreadstat.pyreadstat.ReaderError as e:
        raise ValueError(f"Invalid SPSS file format: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error reading SPSS file: {e}")
        raise


def write_json(data: dict, file_path: str, indent: int = 2) -> None:
    """
    Write a dictionary to a JSON file with proper formatting.

    Args:
        data: Dictionary to write
        file_path: Path to the output JSON file
        indent: Number of spaces for indentation (default: 2)

    Raises:
        IOError: If the file cannot be written
        TypeError: If the data contains non-serializable objects

    Example:
        >>> write_json({"name": "survey", "count": 100}, "output/data.json")
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(file_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            raise IOError(f"Cannot create output directory: {e}") from e

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

        logger.info(f"Successfully wrote JSON file: {file_path}")

    except TypeError as e:
        raise TypeError(f"Data contains non-serializable objects: {e}") from e
    except UnicodeEncodeError as e:
        raise IOError(f"Encoding error writing JSON file: {e}") from e
    except Exception as e:
        raise IOError(f"Error writing JSON file: {e}") from e


def read_json(file_path: str) -> dict:
    """
    Read a JSON file and return its contents as a dictionary.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary with the JSON contents

    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file contains invalid JSON
        PermissionError: If the file cannot be read

    Example:
        >>> data = read_json("output/data.json")
        >>> print(data['name'])
        'survey'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read JSON file (permission denied): {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Successfully read JSON file: {file_path}")

        return data

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise
    except UnicodeDecodeError as e:
        raise IOError(f"Encoding error reading JSON file: {e}") from e
    except Exception as e:
        raise IOError(f"Error reading JSON file: {e}") from e


def write_csv(df: pd.DataFrame, file_path: str, **kwargs) -> None:
    """
    Write a pandas DataFrame to a CSV file.

    Args:
        df: DataFrame to write
        file_path: Path to the output CSV file
        **kwargs: Additional arguments passed to pandas.DataFrame.to_csv()

    Raises:
        IOError: If the file cannot be written

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        >>> write_csv(df, "output/data.csv")
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(file_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            raise IOError(f"Cannot create output directory: {e}") from e

    # Default options
    default_kwargs = {
        'index': False,
        'encoding': 'utf-8',
    }
    default_kwargs.update(kwargs)

    try:
        df.to_csv(file_path, **default_kwargs)
        logger.info(f"Successfully wrote CSV file: {file_path} ({len(df)} rows)")

    except UnicodeEncodeError as e:
        # Retry with utf-8-sig (BOM) for better Excel compatibility
        try:
            default_kwargs['encoding'] = 'utf-8-sig'
            df.to_csv(file_path, **default_kwargs)
            logger.info(f"Successfully wrote CSV file with UTF-8 BOM: {file_path}")
        except Exception as e2:
            raise IOError(f"Encoding error writing CSV file: {e}") from e
    except Exception as e:
        raise IOError(f"Error writing CSV file: {e}") from e


def read_csv(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Read a CSV file and return its contents as a pandas DataFrame.

    Args:
        file_path: Path to the CSV file
        **kwargs: Additional arguments passed to pandas.read_csv()

    Returns:
        DataFrame with the CSV contents

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read

    Example:
        >>> df = read_csv("output/data.csv")
        >>> print(df.head())
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Cannot read CSV file (permission denied): {file_path}")

    # Default options
    default_kwargs = {
        'encoding': 'utf-8',
    }
    default_kwargs.update(kwargs)

    try:
        df = pd.read_csv(file_path, **default_kwargs)
        logger.info(
            f"Successfully read CSV file: {file_path} "
            f"({len(df)} rows, {len(df.columns)} columns)"
        )
        return df

    except UnicodeDecodeError as e:
        # Try common encodings
        encodings = ['utf-8-sig', 'latin-1', 'iso-8859-1', 'cp1252']
        for encoding in encodings:
            try:
                default_kwargs['encoding'] = encoding
                df = pd.read_csv(file_path, **default_kwargs)
                logger.info(
                    f"Successfully read CSV file with {encoding} encoding: {file_path}"
                )
                return df
            except Exception:
                continue
        raise IOError(f"Could not read CSV file with any common encoding: {e}") from e
    except pd.errors.EmptyDataError:
        raise ValueError(f"CSV file is empty: {file_path}")
    except pd.errors.ParserError as e:
        raise ValueError(f"Invalid CSV format: {e}") from e
    except Exception as e:
        raise IOError(f"Error reading CSV file: {e}") from e


def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Path to the directory

    Raises:
        IOError: If the directory cannot be created

    Example:
        >>> ensure_directory("output/tables")
    """
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except OSError as e:
            raise IOError(f"Cannot create directory: {e}") from e
