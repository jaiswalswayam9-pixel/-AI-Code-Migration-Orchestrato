"""
Report Generator (spec section 25 & 36).

Formats and exports migration reports in JSON and Markdown formats.
"""
from typing import Any


class ReportGenerator:
    @staticmethod
    def format_markdown(report_data: dict[str, Any]) -> str:
        return report_data.get("markdown", "# Migration Report\n\nNo report data available.")

    @staticmethod
    def format_json(report_data: dict[str, Any]) -> dict[str, Any]:
        return report_data
