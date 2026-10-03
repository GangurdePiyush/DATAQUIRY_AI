"""
database/db_manager.py
----------------------
Manages SQLite database connections, imports DataFrames into SQLite tables,
detects table schemas, and provides helper functions for querying.
"""

import os
import sqlite3
from typing import Tuple, Optional, Dict, Any, List
import pandas as pd

import config
from .schema import TableSchema, SchemaColumn, sanitize_column_name, map_pandas_dtype_to_sqlite


class DatabaseManager:
    """
    Handles SQLite database creation, table imports, schema detection,
    and connection management.
    """

    DEFAULT_TABLE_NAME = "dataset"

    def __init__(self, db_path: Optional[str] = None):
        """
        Initializes the DatabaseManager.
        Defaults to saving the database file at data/app.db.
        """
        if db_path is None:
            os.makedirs(config.DATA_DIR, exist_ok=True)
            self.db_path = os.path.join(config.DATA_DIR, "app.db")
        else:
            self.db_path = db_path

        self.table_name = self.DEFAULT_TABLE_NAME
        self.current_schema: Optional[TableSchema] = None
        self.database_ready = False

    def import_dataframe(self, df: pd.DataFrame, table_name: str = "dataset") -> Tuple[bool, str, Optional[TableSchema]]:
        """
        Converts a Pandas DataFrame into a SQLite table inside app.db.

        Parameters:
            df (pd.DataFrame): Target DataFrame to save to SQLite.
            table_name (str): Name of SQLite table (default 'dataset').

        Returns:
            Tuple[bool, str, Optional[TableSchema]]: (Success, Message, Schema Object)
        """
        if df is None or df.empty:
            return False, "Cannot import an empty DataFrame into SQLite.", None

        self.table_name = table_name

        try:
            # 1. Column Sanitization & Duplicate Prevention
            clean_df = df.copy()
            clean_cols = []
            seen_cols = {}

            for col in clean_df.columns:
                sanitized = sanitize_column_name(col)
                if sanitized in seen_cols:
                    seen_cols[sanitized] += 1
                    sanitized = f"{sanitized}_{seen_cols[sanitized]}"
                else:
                    seen_cols[sanitized] = 0
                clean_cols.append(sanitized)

            clean_df.columns = clean_cols

            # 2. Write DataFrame to SQLite using sqlite3 connection
            with sqlite3.connect(self.db_path) as conn:
                clean_df.to_sql(name=self.table_name, con=conn, if_exists="replace", index=False)

            # 3. Detect Schema from SQLite (PRAGMA table_info)
            schema = self.detect_schema(self.table_name)
            self.current_schema = schema
            self.database_ready = True

            msg = (
                f"Successfully imported dataset into SQLite database ('{os.path.basename(self.db_path)}'). "
                f"Table: '{self.table_name}' ({schema.row_count} rows, {schema.column_count} columns)."
            )
            return True, msg, schema

        except sqlite3.Error as se:
            self.database_ready = False
            return False, f"SQLite Database Error: {str(se)}", None
        except Exception as ex:
            self.database_ready = False
            return False, f"Failed to save dataset to SQLite database: {str(ex)}", None

    def detect_schema(self, table_name: str = "dataset") -> TableSchema:
        """
        Queries SQLite system tables (PRAGMA table_info) to detect schema details.

        Returns:
            TableSchema: Schema object containing columns, SQLite data types, and row count.
        """
        schema = TableSchema(table_name=table_name)

        if not os.path.exists(self.db_path):
            return schema

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get Row Count
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                schema.row_count = cursor.fetchone()[0]

                # Get Column Info via PRAGMA
                cursor.execute(f"PRAGMA table_info(`{table_name}`)")
                rows = cursor.fetchall()
                # PRAGMA tuple structure: (cid, name, type, notnull, dflt_value, pk)
                for row in rows:
                    col_name = row[1]
                    col_type = row[2] or "TEXT"
                    schema.add_column(
                        SchemaColumn(
                            original_name=col_name,
                            clean_name=col_name,
                            sqlite_type=col_type.upper(),
                            pandas_dtype=col_type,
                        )
                    )

        except Exception:
            pass

        return schema

    def get_connection(self) -> sqlite3.Connection:
        """Returns a connection object to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str, params: tuple = ()) -> Tuple[bool, List[str], List[tuple], str]:
        """
        Safely executes a SELECT query against the SQLite database.

        Returns:
            Tuple[bool, List[str], List[tuple], str]: (Success, Column names list, Rows list, Status message)
        """
        if not self.database_ready or not os.path.exists(self.db_path):
            return False, [], [], "Database is not ready or no dataset loaded."

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                return True, columns, rows, "Query executed successfully."
        except sqlite3.Error as se:
            return False, [], [], f"SQL Error: {str(se)}"
        except Exception as ex:
            return False, [], [], f"Execution Error: {str(ex)}"

    def get_schema(self) -> Optional[TableSchema]:
        """Returns current TableSchema object."""
        if self.current_schema is None and self.database_ready:
            self.current_schema = self.detect_schema(self.table_name)
        return self.current_schema

    def is_ready(self) -> bool:
        """Returns True if SQLite database has a dataset table loaded."""
        return self.database_ready and os.path.exists(self.db_path)
