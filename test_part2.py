"""
test_part2.py
-------------
Automated test suite to verify Part 2 dataset loading and error handling.
"""

import os
from dataset import DatasetHandler, DatasetLoader

def run_tests():
    print("==========================================")
    print("RUNNING PART 2 DATASET LOADER VERIFICATION")
    print("==========================================")

    handler = DatasetHandler()

    # Test 1: Valid CSV Loading
    csv_path = os.path.abspath("data/sample_employees.csv")
    success, msg = handler.load_dataset(csv_path)
    print(f"\n[Test 1] Load CSV ({os.path.basename(csv_path)}):")
    print(f"  Success: {success}")
    print(f"  Message: {msg}")
    assert success is True, "CSV loading failed!"
    meta = handler.get_dataset_info()
    print(f"  Rows: {meta['row_count']}, Columns: {meta['column_count']}")
    print(f"  Column List: {meta['columns']}")
    assert meta["row_count"] == 10, "Incorrect row count for sample CSV!"
    assert len(meta["columns"]) == 6, "Incorrect column count for sample CSV!"
    cols, rows = handler.get_preview_table(max_rows=5)
    assert len(rows) == 5, "Preview table row count mismatch!"

    # Test 2: Valid Excel Loading (.xlsx)
    xlsx_path = os.path.abspath("data/sample_sales.xlsx")
    success, msg = handler.load_dataset(xlsx_path)
    print(f"\n[Test 2] Load Excel (.xlsx) ({os.path.basename(xlsx_path)}):")
    print(f"  Success: {success}")
    print(f"  Message: {msg}")
    assert success is True, "Excel (.xlsx) loading failed!"
    meta = handler.get_dataset_info()
    print(f"  Rows: {meta['row_count']}, Columns: {meta['column_count']}")
    print(f"  Column List: {meta['columns']}")
    assert meta["row_count"] == 5, "Incorrect row count for sample Excel!"
    assert len(meta["columns"]) == 6, "Incorrect column count for sample Excel!"

    # Test 3: Empty CSV Error Handling
    empty_path = os.path.abspath("data/empty_test.csv")
    success, msg = handler.load_dataset(empty_path)
    print(f"\n[Test 3] Empty File Handling ({os.path.basename(empty_path)}):")
    print(f"  Success: {success} (Expected: False)")
    print(f"  Message: {msg}")
    assert success is False, "Empty file should return success=False!"

    # Test 4: Unsupported File Extension Error Handling
    invalid_ext_path = os.path.abspath("README.md")
    success, msg = handler.load_dataset(invalid_ext_path)
    print(f"\n[Test 4] Unsupported Extension (.md):")
    print(f"  Success: {success} (Expected: False)")
    print(f"  Message: {msg}")
    assert success is False, "Unsupported extension should return success=False!"

    print("\n==========================================")
    print("ALL PART 2 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==========================================")

if __name__ == "__main__":
    run_tests()
