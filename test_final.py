"""
test_final.py
--------------
Master automated integration test suite for the Simple Dataset Upload & Query System (Parts 1-7).
Verifies all 15 core application workflows programmatically.
"""

import os
from dataset import DatasetHandler
from database import DatabaseHandler
from query import QueryEngine, NLToSQLConverter, SQLExecutor, is_safe_sql
from voice import VoiceHandler


def run_master_tests():
    print("==========================================================")
    print("RUNNING MASTER INTEGRATION TEST SUITE (PARTS 1-7)")
    print("==========================================================")

    dataset_handler = DatasetHandler()
    db_handler = DatabaseHandler()
    query_engine = QueryEngine()
    voice_handler = VoiceHandler()

    # ----------------------------------------------------
    # 13. Test No Dataset Uploaded Case
    # ----------------------------------------------------
    print("\n[Scenario 1] No Dataset Uploaded Case:")
    res_no_db = query_engine.execute_sql("SELECT * FROM dataset", db_handler)
    print(f"  Result Message: '{res_no_db['message']}'")
    assert res_no_db["success"] is False
    assert "upload a dataset" in res_no_db["message"].lower()

    # ----------------------------------------------------
    # 1. Test Upload CSV Dataset & 3. Schema Detection
    # ----------------------------------------------------
    print("\n[Scenario 2] Upload CSV Dataset & Detect Schema:")
    csv_path = os.path.abspath("data/sample_employees.csv")
    csv_ok, csv_msg = dataset_handler.load_dataset(csv_path)
    print(f"  CSV Load Status: {csv_ok} | {csv_msg}")
    assert csv_ok is True, "Failed to load sample CSV dataset!"

    df_csv = dataset_handler.get_dataframe()
    db_ok, db_msg, schema_csv = db_handler.import_dataframe(df_csv, table_name="dataset")
    print(f"  SQLite Import  : {db_ok} | {db_msg}")
    assert db_ok is True, "Failed to import CSV into SQLite!"
    assert schema_csv.row_count == 10, "Row count mismatch!"
    print(f"  Detected SQLite Schema: {schema_csv.get_column_types()}")

    # ----------------------------------------------------
    # 2. Test Upload Excel Dataset
    # ----------------------------------------------------
    print("\n[Scenario 3] Upload Excel Dataset:")
    xlsx_path = os.path.abspath("data/sample_sales.xlsx")
    excel_ok, excel_msg = dataset_handler.load_dataset(xlsx_path)
    print(f"  Excel Load Status: {excel_ok} | {excel_msg}")
    assert excel_ok is True, "Failed to load sample Excel dataset!"

    df_excel = dataset_handler.get_dataframe()
    db_excel_ok, db_excel_msg, schema_excel = db_handler.import_dataframe(df_excel, table_name="dataset")
    assert db_excel_ok is True, "Failed to overwrite SQLite table with Excel!"
    assert schema_excel.row_count == 5, "Excel row count mismatch!"

    # Reload CSV for remaining query tests
    dataset_handler.load_dataset(csv_path)
    db_handler.import_dataframe(dataset_handler.get_dataframe(), table_name="dataset")
    schema = db_handler.get_schema()

    # ----------------------------------------------------
    # 4. Text Question, 5. SQL Generation, 6. SQL Preview
    # ----------------------------------------------------
    print("\n[Scenario 4] Text Question -> SQL Generation -> SQL Preview:")
    q_text = "Show employees whose age is greater than 30"
    gen_res = query_engine.process_question(q_text, schema)
    print(f"  Question  : '{q_text}'")
    print(f"  Gen SQL   : '{gen_res['sql']}'")
    print(f"  Gen Status: '{gen_res['message']}'")
    assert gen_res["sql"].strip() != "", "Generated SQL should not be empty!"

    # ----------------------------------------------------
    # 7. SQL Execution & 8. Result Table
    # ----------------------------------------------------
    print("\n[Scenario 5] SQL Execution & Result Table:")
    exec_res = query_engine.execute_sql(gen_res["sql"], db_handler)
    print(f"  Exec Status : {exec_res['success']}")
    print(f"  Rows Count  : {exec_res['row_count']}")
    print(f"  Cols List   : {exec_res['columns']}")
    assert exec_res["success"] is True, "SQL query execution failed!"
    assert exec_res["row_count"] == 7, f"Expected 7 rows where age > 30, got {exec_res['row_count']}"

    # ----------------------------------------------------
    # 9. Voice Input & 15. Voice Unavailable Case
    # ----------------------------------------------------
    print("\n[Scenario 6] Voice Input & Microphone Hardware Resilience:")
    stt_ok, stt_text, stt_msg = voice_handler.listen_and_recognize()
    print(f"  STT Listen Status: {stt_ok} | Msg: '{stt_msg}'")
    # Must return boolean status gracefully without crashing
    assert isinstance(stt_ok, bool)

    # ----------------------------------------------------
    # 10. Voice Output (TTS Result Summary)
    # ----------------------------------------------------
    print("\n[Scenario 7] Voice Output (Text-to-Speech Result Summary):")
    spoken_summary = voice_handler.speak_query_result(exec_res)
    print(f"  Generated Spoken Audio Summary: '{spoken_summary}'")
    assert "returned 7 records" in spoken_summary

    # ----------------------------------------------------
    # 11. Invalid Question Handling
    # ----------------------------------------------------
    print("\n[Scenario 8] Empty / Invalid Question Handling:")
    invalid_q_res = query_engine.process_question("", schema)
    print(f"  Empty Q Result: Success={invalid_q_res['success']} | Message='{invalid_q_res['message']}'")
    assert invalid_q_res["success"] is False

    # ----------------------------------------------------
    # 12. Invalid SQL Handling
    # ----------------------------------------------------
    print("\n[Scenario 9] Invalid SQL Syntax Error Handling:")
    invalid_sql_res = query_engine.execute_sql("SELECT non_existent_column FROM dataset", db_handler)
    print(f"  Invalid SQL Result: Success={invalid_sql_res['success']} | Error='{invalid_sql_res['error']}'")
    assert invalid_sql_res["success"] is False
    assert "no such column" in invalid_sql_res["error"].lower()

    # ----------------------------------------------------
    # Security Enforcement Check
    # ----------------------------------------------------
    print("\n[Scenario 10] Dangerous SQL Security Rejection Check:")
    dangerous_sql = "DROP TABLE dataset;"
    sec_res = query_engine.execute_sql(dangerous_sql, db_handler)
    print(f"  Dangerous Query: '{dangerous_sql}'")
    print(f"  Block Status   : Success={sec_res['success']} | Error='{sec_res['error']}'")
    assert sec_res["success"] is False
    assert "Security Violation" in sec_res["error"]

    # ----------------------------------------------------
    # 14. Local AI Unavailable Case
    # ----------------------------------------------------
    print("\n[Scenario 11] Local AI (Ollama) Disconnected Resilience Check:")
    offline_converter = NLToSQLConverter(ollama_url="http://localhost:99999/api/generate")
    off_ok, off_sql, off_msg = offline_converter.generate_sql("Unrecognized question zzz", schema)
    print(f"  Offline Result: Success={off_ok}")
    print(f"  Status Notice : '{off_msg}'")
    assert "Local AI service is not available" in off_msg or "offline" in off_msg.lower() or "Ollama" in off_msg

    print("\n==========================================================")
    print("ALL 15 MASTER INTEGRATION TEST SCENARIOS PASSED SUCCESSFULLY!")
    print("==========================================================")


if __name__ == "__main__":
    run_master_tests()
