"""
Deprecated shim.

The canonical implementation is `team_report_generator.py` at repo root.
This file exists only to prevent import ambiguity and silent drift.
"""

try:
    from team_report_generator import TeamReportGenerator  # type: ignore
except Exception:
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from team_report_generator import TeamReportGenerator  # type: ignore
