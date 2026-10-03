"""
dataset/dataset_loader.py
-------------------------
Dedicated module for reading and validating CSV and Excel files using Pandas.
Handles error checks (empty files, corrupted data, invalid extensions) cleanly.
"""

import os
from typing import Optional, Dict, Any, Tuple, List
import pandas as pd


class DatasetLoader:
    """
    Handles reading CSV and Excel files into Pandas DataFrames.
    Separates file-parsing logic cleanly from the Tkinter GUI.
    """

    ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

    def __init__(self):
        self._dataframe: Optional[pd.DataFrame] = None
        self._filepath: Optional[str] = None
        self._filename: Optional[str] = None
        self._error_message: Optional[str] = None

    def load_file(self, filepath: str) -> Tuple[bool, str]:
        """
        Loads a CSV or Excel dataset file into a Pandas DataFrame.

        Parameters:
            filepath (str): Full path to the target dataset file.

        Returns:
            Tuple[bool, str]: (Success status, Message describing result or error)
        """
        self._reset()

        if not filepath or not isinstance(filepath, str):
            self._error_message = "Invalid file path provided."
            return False, self._error_message

        if not os.path.exists(filepath):
            self._error_message = f"File not found: '{filepath}'"
            return False, self._error_message

        # Validate File Extension
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        if ext not in self.ALLOWED_EXTENSIONS:
            self._error_message = (
                f"Unsupported file format '{ext}'. "
                f"Supported formats are: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            )
            return False, self._error_message

        # Check for empty file (0 bytes)
        if os.path.getsize(filepath) == 0:
            self._error_message = "The selected file is completely empty (0 bytes)."
            return False, self._error_message

        # Attempt to load file using Pandas
        try:
            if ext == ".csv":
                # Read CSV with Pandas
                df = pd.read_csv(filepath)
            elif ext == ".xlsx":
                # Read Excel (.xlsx) using openpyxl engine
                df = pd.read_excel(filepath, engine="openpyxl")
            elif ext == ".xls":
                # Read Excel (.xls) using xlrd engine
                df = pd.read_excel(filepath, engine="xlrd")
            else:
                self._error_message = f"Unsupported file extension: {ext}"
                return False, self._error_message

            # Validate DataFrame Content
            if df.empty:
                self._error_message = "Dataset was read successfully, but it contains no rows or columns."
                return False, self._error_message

            # Clean column names (strip leading/trailing whitespace, convert unnamed columns)
            df.columns = [str(col).strip() for col in df.columns]

            self._dataframe = df
            self._filepath = filepath
            self._filename = os.path.basename(filepath)

            row_count, col_count = df.shape
            success_msg = f"Successfully loaded '{self._filename}' ({row_count} rows, {col_count} columns)."
            return True, success_msg

        except pd.errors.EmptyDataError:
            self._error_message = "The selected CSV file has no headers or data (Empty Data Error)."
            return False, self._error_message
        except pd.errors.ParserError as pe:
            self._error_message = f"CSV Parsing Error: File formatting is corrupted or malformed.\nDetails: {pe}"
            return False, self._error_message
        except Exception as ex:
            self._error_message = f"Failed to load dataset file.\nError details: {str(ex)}"
            return False, self._error_message

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Returns the loaded Pandas DataFrame object, or None if no dataset is loaded."""
        return self._dataframe

    def is_loaded(self) -> bool:
        """Returns True if a valid DataFrame is currently loaded."""
        return self._dataframe is not None and not self._dataframe.empty

    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns a dictionary summary of the loaded dataset metadata.
        """
        if not self.is_loaded():
            return {
                "is_loaded": False,
                "filename": "N/A",
                "filepath": "N/A",
                "row_count": 0,
                "column_count": 0,
                "columns": [],
                "missing_values": 0,
                "error": self._error_message or "No dataset loaded",
            }

        df = self._dataframe
        missing_count = int(df.isna().sum().sum())

        return {
            "is_loaded": True,
            "filename": self._filename,
            "filepath": self._filepath,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": missing_count,
            "error": None,
        }

    def get_preview_rows(self, max_rows: int = 15) -> Tuple[List[str], List[List[Any]]]:
        """
        Returns column names and preview row values formatted for table widgets (Tkinter Treeview).

        Parameters:
            max_rows (int): Maximum number of rows to include in the preview.

        Returns:
            Tuple[List[str], List[List[Any]]]: (List of column titles, List of row value lists)
        """
        if not self.is_loaded():
            return [], []

        df = self._dataframe.head(max_rows)
        columns = list(df.columns)

        # Replace NaN/null values with empty string or 'NaN' representation for clean GUI display
        df_preview = df.fillna("NaN")
        rows = df_preview.values.tolist()

        return columns, rows

    def _reset(self):
        """Resets internal state."""
        self._dataframe = None
        self._filepath = None
        self._filename = None
        self._error_message = None
