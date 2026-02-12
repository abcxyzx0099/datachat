"""
Reporting Module

Generate reports from analysis results.

Classes:
    PowerPointGenerator: Generate PowerPoint presentations
    HTMLDashboardGenerator: Generate interactive HTML dashboards
"""

from .powerpoint import PowerPointGenerator, ChartType, create_powerpoint
from .dashboard import HTMLDashboardGenerator, DashboardConfig, create_dashboard

__all__ = [
    "PowerPointGenerator",
    "ChartType",
    "create_powerpoint",
    "HTMLDashboardGenerator",
    "DashboardConfig",
    "create_dashboard",
]
