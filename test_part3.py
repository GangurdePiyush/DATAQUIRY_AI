"""
test_part3.py
-------------
Automated test suite for Part 3 SQLite Integration & Schema Detection.
"""

import os
import sqlite3
import pandas as pd

from dataset import DatasetHandler
from database import DatabaseHandler, DatabaseManager, sanitize_column_name


def run_tests():
    print("==========================================")
    print("RUNNING PART 3 SQLITE INTEGRATION VERIFICATION")
    print("==========================================")

    # Test 1: Column Sanitization Utility
    print("\n[Test 1] Column Sanitization Check:")
    raw_cols = ["Employee ID", "Full Name!", "Salary ($)", "123_count", "  department  "]
    clean_cols = [sanitize_column_name(c) for c in raw_cols]
    print(f"  Raw Columns  : {raw_cols}")
    print(f"  Clean Columns: {clean_cols}")
    assert clean_cols == ["employee_id", "full_name", "salary", "col_123_count", "department"]

    # Test 2: Import CSV into SQLite
    csv_path = os.path.abspath("data/sample_employees.csv")
    dataset_handler = DatasetHandler()
    db_handler = DatabaseHandler()

    success, msg = dataset_handler.load_dataset(csv_path)
    assert success is True, "Dataset loading failed!"

    df = dataset_handler.get_dataframe()
    assert df is not None, "DataFrame is None!"

    db_success, db_msg, schema = db_handler.import_dataframe(df, table_name="dataset")
    print("\n[Test 2] Import CSV to SQLite ('data/app.db'):")
    print(f"  Success: {db_success}")
    print(f"  Message: {db_msg}")
    assert db_success is True, "SQLite import failed!"
    assert schema is not None, "Schema is None!"

    print(f"  Detected Table : '{schema.table_name}'")
    print(f"  Detected Rows  : {schema.row_count}")
    print(f"  Detected Cols  : {schema.column_count}")
    col_types = schema.get_column_types()
    print(f"  Column Types   : {col_types}")
    assert schema.row_count == 10, "Row count mismatch in SQLite!"
    assert col_types["employeeid"] == "INTEGER", "employeeid should be INTEGER!"
    assert col_types["salary"] in ["INTEGER", "REAL"], "salary should be numeric!"

    # Test 3: SQL Execution via DatabaseHandler
    print("\n[Test 3] Execute SELECT Query on SQLite Database:")
    ok, cols, rows, sql_msg = db_handler.execute_query("SELECT employeeid, name, salary FROM dataset LIMIT 3")
    print(f"  Success: {ok}")
    print(f"  Columns: {cols}")
    print(f"  Rows Returned: {len(rows)}")
    for r in rows:
        print(f"    -> {r}")
    assert ok is True, "SELECT query execution failed!"
    assert len(rows) == 3, "Expected 3 rows!"

    # Test 4: Overwrite SQLite Table with Excel Upload
    xlsx_path = os.path.abspath("data/sample_sales.xlsx")
    dataset_handler.load_dataset(xlsx_path)
    df_excel = dataset_handler.get_dataframe()

    db_success, db_msg, new_schema = db_handler.import_dataframe(df_excel, table_name="dataset")
    print("\n[Test 4] Overwrite SQLite Table with Excel Dataset:")
    print(f"  Success: {db_success}")
    print(f"  Message: {db_msg}")
    assert db_success is True, "Excel overwrite failed!"
    assert new_schema.row_count == 5, "Excel row count mismatch in SQLite!"
    excel_cols = new_schema.get_column_names()
    print(f"  New SQLite Columns: {excel_cols}")
    assert "orderid" in excel_cols, "'orderid' missing in SQLite schema!"

    print("\n==========================================")
    print("ALL PART 3 SQLITE VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==========================================")


if __name__ == "__main__":
    run_tests()
