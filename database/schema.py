"""
database/schema.py
------------------
Represents database schema information, column data type mappings,
and sanitization utilities for converting DataFrames into SQLite tables.
"""

import re
from typing import Dict, List, Any, Optional
import pandas as pd


class SchemaColumn:
    """Represents a single database column and its SQLite data type."""

    def __init__(self, original_name: str, clean_name: str, sqlite_type: str, pandas_dtype: str):
        self.original_name = original_name
        self.clean_name = clean_name
        self.sqlite_type = sqlite_type
        self.pandas_dtype = pandas_dtype

    def to_dict(self) -> Dict[str, str]:
        return {
            "original_name": self.original_name,
            "clean_name": self.clean_name,
            "sqlite_type": self.sqlite_type,
            "pandas_dtype": self.pandas_dtype,
        }

    def __repr__(self):
        return f"SchemaColumn('{self.clean_name}', type='{self.sqlite_type}')"


class TableSchema:
    """Represents the complete database schema for a dataset table."""

    def __init__(self, table_name: str = "dataset"):
        self.table_name = table_name
        self.columns: List[SchemaColumn] = []
        self.row_count: int = 0
        self.column_count: int = 0

    def add_column(self, col: SchemaColumn):
        self.columns.append(col)
        self.column_count = len(self.columns)

    def get_column_names(self) -> List[str]:
        return [col.clean_name for col in self.columns]

    def get_column_types(self) -> Dict[str, str]:
        return {col.clean_name: col.sqlite_type for col in self.columns}

    def get_formatted_summary(self) -> str:
        """Returns a human-readable summary of the table schema for display in GUI."""
        if not self.columns:
            return "No schema detected (No table loaded)."

        lines = [f"Table Name: '{self.table_name}' ({self.row_count} rows, {self.column_count} columns)", "Columns & SQLite Data Types:"]
        for col in self.columns:
            lines.append(f"  • {col.clean_name:<20} -> {col.sqlite_type}")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_name": self.table_name,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns": [col.to_dict() for col in self.columns],
        }


def sanitize_column_name(col_name: str) -> str:
    """
    Sanitizes column names to be valid, safe SQLite identifiers.
    Replaces spaces and special characters with underscores.
    """
    if not col_name:
        return "column_unnamed"

    col_str = str(col_name).strip()
    # Replace invalid SQL characters (non-alphanumeric/underscore) with underscore
    clean = re.sub(r"[^\w]", "_", col_str)
    # Remove consecutive underscores
    clean = re.sub(r"_+", "_", clean).strip("_")

    # If starts with digit, prefix with col_
    if clean and clean[0].isdigit():
        clean = "col_" + clean

    if not clean:
        clean = "column_unnamed"

    return clean.lower()


def map_pandas_dtype_to_sqlite(dtype: str) -> str:
    """
    Maps Pandas column data types to standard SQLite data types.
    """
    dtype_str = str(dtype).lower()

    if "int" in dtype_str:
        return "INTEGER"
    elif "float" in dtype_str:
        return "REAL"
    elif "bool" in dtype_str:
        return "INTEGER"
    elif "date" in dtype_str or "time" in dtype_str:
        return "TEXT"
    else:
        return "TEXT"
