"""
query/sql_executor.py
---------------------
Handles execution of validated read-only SQL queries against the local SQLite database (data/app.db).
Converts query results into structured data and Pandas DataFrames cleanly.
"""

import os
import sqlite3
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd

from .nl_to_sql import is_safe_sql


class SQLExecutor:
    """
    Executes read-only SQL queries against SQLite database files safely.
    """

    def __init__(self):
        pass

    def execute_sql(self, sql_query: str, db_handler) -> Dict[str, Any]:
        """
        Executes a SQL query against the database managed by db_handler.

        Parameters:
            sql_query (str): Target SQL query string to execute.
            db_handler: Instance of DatabaseHandler.

        Returns:
            Dict containing success, row_count, column_count, columns, rows, dataframe, error, message.
        """
        if not sql_query or not sql_query.strip():
            return {
                "success": False,
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "rows": [],
                "dataframe": None,
                "error": "Please enter or generate a SQL query.",
                "message": "Please enter or generate a SQL query.",
            }

        # Step 1: Security Validation
        is_safe, security_msg = is_safe_sql(sql_query)
        if not is_safe:
            return {
                "success": False,
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "rows": [],
                "dataframe": None,
                "error": security_msg,
                "message": f"Execution Blocked: {security_msg}",
            }

        # Step 2: Check Database Readiness
        if not db_handler or not db_handler.is_ready():
            return {
                "success": False,
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "rows": [],
                "dataframe": None,
                "error": "Please upload a dataset file first.",
                "message": "Please upload a dataset file first.",
            }

        db_path = db_handler.db_manager.db_path
        if not os.path.exists(db_path):
            return {
                "success": False,
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "rows": [],
                "dataframe": None,
                "error": f"Database file not found at '{db_path}'.",
                "message": "Database file missing. Please upload a dataset file first.",
            }

        # Step 3: Execute Query against SQLite Database using sqlite3 connection & Pandas
        try:
            with sqlite3.connect(db_path) as conn:
                df_result = pd.read_sql_query(sql_query, con=conn)

            columns = list(df_result.columns)
            df_display = df_result.fillna("NaN")
            rows = df_display.values.tolist()

            row_cnt = len(df_result)
            col_cnt = len(columns)

            if row_cnt == 0:
                msg = "No records found."
            else:
                msg = f"Query executed successfully ({row_cnt} records found)."

            return {
                "success": True,
                "row_count": row_cnt,
                "column_count": col_cnt,
                "columns": columns,
                "rows": rows,
                "dataframe": df_result,
                "error": None,
                "message": msg,
            }

        except pd.errors.DatabaseError as de:
            err_text = str(de)
            clean_err = err_text.replace("Execution failed on sql '", "").split("':")[-1].strip()
            return {
                "success": False,
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "rows": [],
                "dataframe": None,
                "error": clean_err,
                "message": f"SQL Execution Error: {clean_err}",
            }
        except sqlite3.Error as se:
            return {
                "success": False,
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "rows": [],
                "dataframe": None,
                "error": str(se),
                "message": f"SQLite Error: {str(se)}",
            }
        except Exception as ex:
            return {
                "success": False,
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "rows": [],
                "dataframe": None,
                "error": str(ex),
                "message": f"Execution Failure: {str(ex)}",
            }
