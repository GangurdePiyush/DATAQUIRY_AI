"""
database/db_handler.py
-----------------------
High-level manager wrapping DatabaseManager for SQLite operations.
Exposes clean methods for importing DataFrames, accessing connections,
and fetching schema objects.
"""

from typing import Tuple, Optional, Dict, Any, List
import sqlite3
import pandas as pd

from .db_manager import DatabaseManager
from .schema import TableSchema


class DatabaseHandler:
    """
    High-level handler for SQLite database integration in the application.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_manager = DatabaseManager(db_path=db_path)

    def import_dataframe(self, df: pd.DataFrame, table_name: str = "dataset") -> Tuple[bool, str, Optional[TableSchema]]:
        """
        Converts a Pandas DataFrame into a SQLite table inside app.db.
        """
        return self.db_manager.import_dataframe(df, table_name=table_name)

    def is_ready(self) -> bool:
        """Returns True if database table is ready."""
        return self.db_manager.is_ready()

    def get_schema(self) -> Optional[TableSchema]:
        """Returns the detected TableSchema."""
        return self.db_manager.get_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection object."""
        return self.db_manager.get_connection()

    def execute_query(self, query: str, params: tuple = ()) -> Tuple[bool, List[str], List[tuple], str]:
        """Executes a SQL query against the database."""
        return self.db_manager.execute_query(query, params)

    def close(self):
        """No-op for SQLite connection manager."""
        pass
