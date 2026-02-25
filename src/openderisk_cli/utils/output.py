"""Output formatting utilities."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

console = Console()


class OutputFormatter:
    """Formatter for CLI output."""

    SUPPORTED_FORMATS = ["table", "json", "yaml", "csv"]

    def __init__(self, format_type: str = "table"):
        if format_type not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format_type}")
        self.format_type = format_type

    def format(
        self,
        data: Any,
        columns: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Union[str, Table]:
        """Format data for output.

        Args:
            data: Data to format (dict, list, or Pydantic model)
            columns: Columns to include for table format
            headers: Column header mappings

        Returns:
            Formatted string or Table object
        """
        items = self._normalize_data(data)

        if self.format_type == "json":
            return self._format_json(items)
        elif self.format_type == "yaml":
            return self._format_yaml(items)
        elif self.format_type == "csv":
            return self._format_csv(items, columns, headers)
        else:
            return self._format_table(items, columns, headers)

    def _normalize_data(self, data: Any) -> List[Dict[str, Any]]:
        """Normalize data to list of dicts."""
        if data is None:
            return []

        # Handle single Pydantic model
        if isinstance(data, BaseModel):
            return [data.model_dump()]

        # Handle list of Pydantic models
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], BaseModel):
            return [item.model_dump() for item in data]

        # Handle single dict
        if isinstance(data, dict):
            return [data]

        # Handle list of dicts
        if isinstance(data, list):
            return data

        return []

    def _format_json(self, items: List[Dict]) -> str:
        """Format as JSON."""

        # Handle datetime serialization
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return super().default(o)

        return json.dumps(items, indent=2, cls=DateTimeEncoder, ensure_ascii=False)

    def _format_yaml(self, items: List[Dict]) -> str:
        """Format as YAML."""
        return yaml.dump(items, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def _format_csv(
        self,
        items: List[Dict],
        columns: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """Format as CSV."""
        import csv
        import io

        if not items:
            return ""

        # Determine columns
        if columns is None:
            columns = list(items[0].keys())

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")

        # Write header with mapped names
        header_row = {col: headers.get(col, col) for col in columns} if headers else None
        writer.writerow(header_row or dict.fromkeys(columns, ""))

        for item in items:
            writer.writerow({k: v for k, v in item.items() if k in columns})

        return output.getvalue()

    def _format_table(
        self,
        items: List[Dict],
        columns: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Union[str, Table]:
        """Format as table using rich.Table for proper CJK alignment."""
        if not items:
            return "No data to display."

        if columns is None:
            columns = list(items[0].keys())

        table = Table(show_header=True, header_style="bold", show_edge=False, show_lines=False)

        for col in columns:
            header_name = headers.get(col, col) if headers else col
            max_width = 50 if col in ("app_describe", "description", "desc") else None
            table.add_column(header_name, max_width=max_width, overflow="ellipsis")

        for item in items:
            row = [self._format_value(item.get(col, "")) for col in columns]
            table.add_row(*row)

        return table

    def _format_value(self, value: Any) -> str:
        """Format a single value for display."""
        if value is None:
            return "-"
        if isinstance(value, bool):
            return "Yes" if value else "No"
        if isinstance(value, list):
            return f"[{len(value)} items]"
        if isinstance(value, dict):
            return f"{{{len(value)} keys}}"
        if isinstance(value, str) and len(value) > 50:
            return value[:47] + "..."
        return str(value)

    def print(
        self,
        data: Any,
        columns: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """Print formatted data to console."""
        output = self.format(data, columns, headers)
        console.print(output)


def format_output(
    data: Any,
    format_type: str = "table",
    columns: Optional[List[str]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Union[str, Table]:
    """Format data for output.

    Args:
        data: Data to format
        format_type: Output format (table/json/yaml/csv)
        columns: Columns to include
        headers: Column header mappings

    Returns:
        Formatted string or Table object
    """
    formatter = OutputFormatter(format_type)
    return formatter.format(data, columns, headers)
