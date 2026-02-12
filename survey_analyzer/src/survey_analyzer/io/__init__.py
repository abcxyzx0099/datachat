"""
SPSS I/O Module

Provides functions for reading SPSS (.sav) files and transforming metadata.

Classes:
    SPSSReader: Read SPSS files and extract data/metadata
    MetadataTransformer: Convert between metadata formats
"""

from .reader import SPSSReader
from .metadata import MetadataTransformer

__all__ = ["SPSSReader", "MetadataTransformer"]
