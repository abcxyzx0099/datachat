"""
Tracing Module

This module provides decorators and utilities for LangSmith tracing,
which allows monitoring and debugging of LangGraph workflows.
"""

import functools
import logging
from typing import Any, Callable, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

P = ParamSpec('P')
T = TypeVar('T')


def trace_node(node_name: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator that adds LangSmith tracing to a node function.

    This decorator wraps node functions to provide:
    - Entry/exit logging
    - LangSmith tracing integration
    - Error tracking and propagation

    Args:
        node_name: Human-readable name for the node (e.g., "Step 1: Extract Data")

    Returns:
        Decorated function with tracing enabled

    Example:
        @trace_node("Step 1: Extract SPSS Data")
        def extract_spss_node(state: WorkflowState) -> WorkflowState:
            # Node implementation
            return state
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            logger.info(f"→ Entering: {node_name}")

            try:
                result = func(*args, **kwargs)
                logger.info(f"✓ Completed: {node_name}")
                return result

            except Exception as e:
                logger.error(f"✗ Failed: {node_name} - {type(e).__name__}: {e}")
                raise

        return wrapper
    return decorator
