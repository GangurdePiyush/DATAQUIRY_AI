"""
test_part5.py
-------------
Automated test suite for Part 5 SQL Execution & Query Results Rendering.
"""

import os
from dataset import DatasetHandler
from database import DatabaseHandler
from query import SQLExecutor, QueryEngine


def run_tests():
    print("==========================================")
    print("RUNNING PART 5 SQL EXECUTION VERIFICATION")
    print("==========================================")

    # Initialize handlers & load sample dataset into SQLite database
    dataset_handler = DatasetHandler()
    db_handler = DatabaseHandler()

    csv_path = os.path.abspath("data/sample_employees.csv")
    dataset_handler.load_dataset(csv_path)
    df = dataset_handler.get_dataframe()
    db_handler.import_dataframe(df, table_name="dataset")

    executor = SQLExecutor()

    # Test 1: SELECT * FROM dataset
    print("\n[Test 1] Execute 'SELECT * FROM dataset':")
    q1 = "SELECT * FROM dataset;"
    res1 = executor.execute_sql(q1, db_handler)
    print(f"  Success  : {res1['success']}")
    print(f"  Rows     : {res1['row_count']}, Columns: {res1['column_count']}")
    print(f"  Cols List: {res1['columns']}")
    assert res1["success"] is True, "SELECT * failed!"
    assert res1["row_count"] == 10, "Row count mismatch!"
    assert res1["column_count"] == 6, "Column count mismatch!"

    # Test 2: COUNT Aggregation Query
    print("\n[Test 2] Execute 'SELECT COUNT(*) AS total FROM dataset':")
    q2 = "SELECT COUNT(*) AS total FROM dataset;"
    res2 = executor.execute_sql(q2, db_handler)
    print(f"  Success: {res2['success']}")
    print(f"  Rows   : {res2['rows']}")
    assert res2["success"] is True, "COUNT query failed!"
    assert res2["rows"][0][0] == 10, "Count value mismatch!"

    # Test 3: AVG Aggregation Query
    print("\n[Test 3] Execute 'SELECT AVG(salary) AS avg_sal FROM dataset':")
    q3 = "SELECT AVG(salary) AS avg_sal FROM dataset;"
    res3 = executor.execute_sql(q3, db_handler)
    print(f"  Success: {res3['success']}")
    print(f"  Rows   : {res3['rows']}")
    assert res3["success"] is True, "AVG query failed!"

    # Test 4: WHERE Condition Query
    print("\n[Test 4] Execute 'SELECT name, age, salary FROM dataset WHERE age > 30':")
    q4 = "SELECT name, age, salary FROM dataset WHERE age > 30;"
    res4 = executor.execute_sql(q4, db_handler)
    print(f"  Success  : {res4['success']}")
    print(f"  Rows Count: {res4['row_count']}")
    assert res4["success"] is True, "WHERE query failed!"
    assert res4["row_count"] == 7, f"Expected 7 rows where age > 30, got {res4['row_count']}"

    # Test 5: ORDER BY & LIMIT Clause Query
    print("\n[Test 5] Execute 'SELECT name, salary FROM dataset ORDER BY salary DESC LIMIT 3':")
    q5 = "SELECT name, salary FROM dataset ORDER BY salary DESC LIMIT 3;"
    res5 = executor.execute_sql(q5, db_handler)
    print(f"  Success : {res5['success']}")
    print(f"  Rows    : {res5['rows']}")
    assert res5["success"] is True, "ORDER BY / LIMIT query failed!"
    assert res5["row_count"] == 3, "Expected 3 rows for LIMIT 3!"
    assert res5["rows"][0][0] == "Diana Prince", "Top salary earner mismatch!"

    # Test 6: Invalid SQL Syntax Error Handling
    print("\n[Test 6] Invalid SQL Syntax Error Handling:")
    q6 = "SELECT non_existent_col FROM dataset;"
    res6 = executor.execute_sql(q6, db_handler)
    print(f"  Success (Expected False): {res6['success']}")
    print(f"  Error Message           : {res6['error']}")
    assert res6["success"] is False, "Invalid SQL should return success=False!"
    assert "no such column" in res6["error"].lower(), "Expected column missing error!"

    # Test 7: Security Rejection Check
    print("\n[Test 7] Security Block Check for Dangerous SQL:")
    q7 = "DROP TABLE dataset;"
    res7 = executor.execute_sql(q7, db_handler)
    print(f"  Success (Expected False): {res7['success']}")
    print(f"  Security Block Message  : {res7['error']}")
    assert res7["success"] is False, "Dangerous query was NOT blocked!"
    assert "Security Violation" in res7["error"], "Expected Security Violation error!"

    print("\n==========================================")
    print("ALL PART 5 SQL EXECUTION TESTS PASSED SUCCESSFULLY!")
    print("==========================================")


if __name__ == "__main__":
    run_tests()
