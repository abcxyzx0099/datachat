"""
Question Extraction Module

Extracts question codes from SPSS variable names and groups variables by question.

Classes:
    QuestionExtractor: Extract and group variables by question code
"""

from .questions import QuestionExtractor

__all__ = ["QuestionExtractor"]
