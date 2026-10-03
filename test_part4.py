"""
test_part4.py
-------------
Automated test suite for Part 4 Natural Language to SQL Generation & Security.
"""

import os
from dataset import DatasetHandler
from database import DatabaseHandler
from query import QueryEngine, NLToSQLConverter, is_safe_sql


def run_tests():
    print("==========================================")
    print("RUNNING PART 4 NL TO SQL & SECURITY VERIFICATION")
    print("==========================================")

    # Initialize handlers & load test dataset
    dataset_handler = DatasetHandler()
    db_handler = DatabaseHandler()

    csv_path = os.path.abspath("data/sample_employees.csv")
    dataset_handler.load_dataset(csv_path)
    df = dataset_handler.get_dataframe()
    db_handler.import_dataframe(df, table_name="dataset")
    schema = db_handler.get_schema()

    query_engine = QueryEngine()

    # Test 1: Simple Count Question ("How many records are there?")
    print("\n[Test 1] Simple Count Question:")
    q1 = "How many records are there?"
    res1 = query_engine.process_question(q1, schema)
    print(f"  Question: '{q1}'")
    print(f"  SQL Output: {res1['sql']}")
    print(f"  Status   : {res1['message']}")
    assert "COUNT(" in res1["sql"].upper(), "SQL output should contain COUNT!"
    assert is_safe_sql(res1["sql"])[0] is True, "Query should be safe!"

    # Test 2: Filtering Question ("Show employees whose age is greater than 30")
    print("\n[Test 2] Filtering Question:")
    q2 = "Show employees whose age is greater than 30"
    res2 = query_engine.process_question(q2, schema)
    print(f"  Question: '{q2}'")
    print(f"  SQL Output: {res2['sql']}")
    print(f"  Status   : {res2['message']}")
    assert "WHERE" in res2["sql"].upper(), "SQL output should contain WHERE!"
    assert "> 30" in res2["sql"], "SQL output should contain '> 30'!"
    assert is_safe_sql(res2["sql"])[0] is True, "Query should be safe!"

    # Test 3: Average Aggregation Question ("What is the average salary?")
    print("\n[Test 3] Average Aggregation Question:")
    q3 = "What is the average salary?"
    res3 = query_engine.process_question(q3, schema)
    print(f"  Question: '{q3}'")
    print(f"  SQL Output: {res3['sql']}")
    print(f"  Status   : {res3['message']}")
    assert "AVG(" in res3["sql"].upper(), "SQL output should contain AVG!"
    assert is_safe_sql(res3["sql"])[0] is True, "Query should be safe!"

    # Test 4: Security Violation / Dangerous Query ("DROP TABLE dataset")
    print("\n[Test 4] Security Enforcement Check:")
    dangerous_sqls = [
        "DROP TABLE dataset;",
        "DELETE FROM dataset WHERE age > 20;",
        "UPDATE dataset SET salary = 0;",
        "INSERT INTO dataset VALUES (1, 'Hacker');",
        "ALTER TABLE dataset ADD COLUMN leaked TEXT;"
    ]

    for d_sql in dangerous_sqls:
        safe, reason = is_safe_sql(d_sql)
        print(f"  Query : '{d_sql}'")
        print(f"  Result: Safe={safe} | Reason: {reason}")
        assert safe is False, f"Dangerous query '{d_sql}' was NOT blocked!"

    # Test 5: Ollama Unavailable Offline Handling
    print("\n[Test 5] Ollama Offline Resilience Check:")
    # Point converter to an invalid port to simulate disconnected Ollama server
    offline_converter = NLToSQLConverter(ollama_url="http://localhost:99999/api/generate")
    success_off, sql_off, msg_off = offline_converter.generate_sql("Custom unrecognized query xyz", schema)
    print(f"  Offline Result: Success={success_off}")
    print(f"  SQL/Error Msg : {sql_off}")
    print(f"  Status Message: {msg_off}")
    assert "Local AI service is not available" in msg_off or "offline" in msg_off.lower() or "Ollama" in msg_off, "Offline message should be user friendly!"

    print("\n==========================================")
    print("ALL PART 4 NL TO SQL VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==========================================")


if __name__ == "__main__":
    run_tests()
