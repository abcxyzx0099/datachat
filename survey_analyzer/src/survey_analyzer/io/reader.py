"""
SPSS File Reader

Provides a clean interface for reading SPSS (.sav) files using pyreadstat.

Example:
    >>> reader = SPSSReader()
    >>> data, metadata = reader.read("survey.sav")
    >>> print(metadata["file_label"])
    >>> print(data.head())
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

try:
    import pyreadstat
except ImportError:
    pyreadstat = None

logger = logging.getLogger(__name__)


class SPSSReader:
    """
    Reader for SPSS (.sav) files.

    Wraps pyreadstat to provide a consistent interface for reading
    SPSS files and extracting both data and metadata.

    Attributes:
        encoding: File encoding (default: None = auto-detect from SPSS file)
        apply_value_formats: Whether to convert values to labels (default: False)

    Example:
        >>> reader = SPSSReader()
        >>> df, metadata = reader.read("survey.sav")
        >>> print(f"Loaded {len(df)} rows, {len(metadata['variable_labels'])} variables")
    """

    def __init__(
        self,
        encoding: Optional[str] = None,
        apply_value_formats: bool = False,
    ):
        """
        Initialize the SPSS reader.

        Args:
            encoding: File encoding for reading SPSS files (None = auto-detect from file)
            apply_value_formats: If True, convert coded values to labels
        """
        if pyreadstat is None:
            raise ImportError(
                "pyreadstat is required. Install with: pip install pyreadstat"
            )

        self.encoding = encoding
        self.apply_value_formats = apply_value_formats

    def read(
        self,
        file_path: str | Path,
        metadata_only: bool = False,
    ) -> Tuple[Optional[Any], Dict[str, Any]]:
        """
        Read an SPSS (.sav) file.

        Args:
            file_path: Path to the .sav file
            metadata_only: If True, only read metadata (faster for large files)

        Returns:
            Tuple of (dataframe, metadata_dict):
                - dataframe: pandas DataFrame (None if metadata_only=True)
                - metadata_dict: Dictionary with:
                    - file_name: Original file name
                    - file_label: File description
                    - variable_labels: Dict mapping var names to labels
                    - value_labels: Nested dict of value labels per variable
                    - variable_types: Dict mapping var names to types
                    - notes: List of file notes (if any)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid SPSS file

        Example:
            >>> reader = SPSSReader()
            >>> df, metadata = reader.read("survey.sav")
            >>> print(metadata["file_name"])
            'survey.sav'
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"SPSS file not found: {file_path}")

        logger.info(f"Reading SPSS file: {file_path}")

        try:
            # Read the file
            df, meta = pyreadstat.read_sav(
                str(file_path),
                encoding=self.encoding,
                apply_value_formats=self.apply_value_formats,
                metadataonly=metadata_only,
            )

            # Build metadata dictionary (pass df for column name mapping)
            metadata = self._build_metadata(meta, file_path, df)

            logger.info(
                f"Successfully read SPSS file: "
                f"{len(df) if df is not None else 0} rows, "
                f"{len(metadata['variable_labels'])} variables"
            )

            return df, metadata

        except Exception as e:
            raise ValueError(f"Error reading SPSS file: {e}") from e

    def _build_metadata(
        self,
        meta: Any,
        file_path: Path,
        df: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Build standardized metadata dictionary from pyreadstat metadata.

        Args:
            meta: pyreadstat metadata object
            file_path: Path to the source file
            df: DataFrame (for column name mapping)

        Returns:
            Standardized metadata dictionary
        """
        # Convert value_labels to variable-centered format
        variable_value_labels = {}

        for var_name, labels in meta.variable_value_labels.items():
            # labels is dict {code: label}
            variable_value_labels[var_name] = {
                str(code): label for code, label in labels.items()
            }

        # Get column labels - these contain the actual question text
        # column_labels is a list where index corresponds to column position
        var_labels = {}
        if hasattr(meta, 'column_labels') and meta.column_labels and df is not None:
            # Map column_labels to variable names using dataframe columns
            column_names = df.columns.tolist()
            for i, label in enumerate(meta.column_labels):
                if i < len(column_names):
                    var_name = column_names[i]
                    # Use the label if it's not "None", otherwise use variable name
                    var_labels[var_name] = label if label and str(label).lower() != "none" else var_name
        elif hasattr(meta, 'column_labels') and meta.column_labels:
            # No dataframe available, use value_labels keys
            var_names = list(variable_value_labels.keys())
            if len(meta.column_labels) == len(var_names):
                for i, label in enumerate(meta.column_labels):
                    if i < len(var_names):
                        var_labels[var_names[i]] = label if label and str(label).lower() != "none" else var_names[i]

        # Fallback to old method if column_labels didn't work
        if not var_labels:
            # Handle different pyreadstat versions
            # variable_labels in older versions, variable_to_label in newer versions
            var_labels = getattr(meta, 'variable_to_label', None) or getattr(meta, 'variable_labels', None) or {}

        # Get variable types if available
        variable_types = {}
        if hasattr(meta, 'variable_measurement'):
            var_names = list(var_labels.keys()) if var_labels else []
            for var_name in var_names:
                var_type = getattr(meta.variable_measurement, 'get', lambda x: None)(var_name)
                if var_type:
                    variable_types[var_name] = str(var_type)

        return {
            "file_name": file_path.name,
            "file_label": meta.file_label,
            "variable_labels": var_labels or {},
            "value_labels": variable_value_labels,
            "variable_types": variable_types,
            "notes": meta.notes or [],
            "original_variable_names": list(var_labels.keys())
                if var_labels else [],
        }

    def get_variable_info(
        self,
        metadata: Dict[str, Any],
        variable_name: str,
    ) -> Dict[str, Any]:
        """
        Get information about a specific variable.

        Args:
            metadata: Metadata dictionary from read()
            variable_name: Name of the variable

        Returns:
            Dictionary with variable info:
                - variable_name: Variable name
                - variable_label: Variable label
                - value_labels: Dict of value labels
        """
        return {
            "variable_name": variable_name,
            "variable_label": metadata["variable_labels"].get(variable_name, ""),
            "value_labels": metadata["value_labels"].get(variable_name, {}),
        }


def read_spss(file_path: str) -> Tuple[Any, Dict[str, Any]]:
    """
    Convenience function to read an SPSS file.

    Args:
        file_path: Path to the .sav file

    Returns:
        Tuple of (dataframe, metadata_dict)

    Example:
        >>> df, metadata = read_spss("survey.sav")
    """
    reader = SPSSReader()
    return reader.read(file_path)
