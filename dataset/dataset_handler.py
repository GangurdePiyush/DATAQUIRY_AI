"""
dataset/dataset_handler.py
--------------------------
Handles dataset operations by wrapping DatasetLoader.
Maintains backward compatibility with Part 1 while exposing clean interfaces
for future modules (e.g. SQLite database conversion in Part 3).
"""

from typing import Optional, Dict, Any, Tuple, List
import pandas as pd
from .dataset_loader import DatasetLoader


class DatasetHandler:
    """
    High-level manager for dataset operations in the application.
    Integrates DatasetLoader to process and manage Pandas DataFrames.
    """

    def __init__(self):
        self.loader = DatasetLoader()

    def load_dataset(self, file_path: str) -> Tuple[bool, str]:
        """
        Loads a CSV or Excel dataset file into memory.

        Returns:
            Tuple[bool, str]: (Success status boolean, Message string)
        """
        return self.loader.load_file(file_path)

    def is_loaded(self) -> bool:
        """Returns True if a valid dataset is loaded."""
        return self.loader.is_loaded()

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Returns the loaded Pandas DataFrame object for processing in later parts."""
        return self.loader.get_dataframe()

    def get_dataset_info(self) -> Dict[str, Any]:
        """Returns metadata dictionary summary of the currently loaded dataset."""
        return self.loader.get_metadata()

    def get_preview_table(self, max_rows: int = 15) -> Tuple[List[str], List[List[Any]]]:
        """Returns column headers and rows formatted for GUI table display."""
        return self.loader.get_preview_rows(max_rows=max_rows)
