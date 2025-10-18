"""
Automated NHL Post-Game Reports

Professional, automated post-game analysis reports for NHL games with realistic shot visualizations and comprehensive analytics.
"""

__version__ = "1.0.0"
__author__ = "Hockey Analytics Community"
__description__ = "Generate professional NHL post-game reports with realistic shot visualizations and comprehensive analytics"

from .comprehensive_report import create_comprehensive_report
from .quick_report import create_quick_report

__all__ = [
    "create_comprehensive_report",
    "create_quick_report",
    "__version__",
    "__author__",
    "__description__"
]
