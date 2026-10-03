"""
voice/text_to_speech.py
-----------------------
Handles offline Text-to-Speech (TTS) audio feedback using pyttsx3.
Generates concise spoken summaries for dataset query results.
"""

import threading
from typing import Dict, Any, Optional

# Safe import of pyttsx3
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    pyttsx3 = None
    TTS_AVAILABLE = False


class TextToSpeechEngine:
    """
    Offline Text-to-Speech synthesizer wrapper.
    Converts query summaries and text messages into spoken audio without blocking the GUI.
    """

    def __init__(self):
        self.tts_available = TTS_AVAILABLE

    def is_tts_available(self) -> bool:
        """Returns True if pyttsx3 is installed and initialized."""
        return self.tts_available

    def speak(self, text: str) -> bool:
        """
        Speaks the given text string using pyttsx3 in a non-blocking background thread.

        Parameters:
            text (str): Text string to synthesize as speech.

        Returns:
            bool: True if speech synthesis thread was launched successfully.
        """
        if not self.tts_available or not text or not text.strip():
            return False

        # Run speech synthesis in a background thread to prevent GUI freezing
        thread = threading.Thread(target=self._speak_worker, args=(text,), daemon=True)
        thread.start()
        return True

    def _speak_worker(self, text: str):
        """Worker thread executing pyttsx3 speech loop."""
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 165)  # Speaking rate (words per minute)
            engine.setProperty("volume", 0.9)  # Volume (0.0 to 1.0)
            engine.say(text)
            engine.runAndWait()
        except Exception:
            # Catch all TTS errors silently so application never crashes
            pass

    def format_query_result_summary(self, result_dict: Dict[str, Any]) -> str:
        """
        Generates a concise spoken summary for a query result dictionary.
        Does NOT speak every row for large tables; produces short summaries instead.

        Parameters:
            result_dict (Dict[str, Any]): Result dictionary returned by SQLExecutor.

        Returns:
            str: Spoken summary string.
        """
        if not result_dict or not result_dict.get("success"):
            error_msg = result_dict.get("error") if result_dict else "No query result available."
            return f"Query error: {error_msg}"

        row_cnt = result_dict.get("row_count", 0)
        col_cnt = result_dict.get("column_count", 0)
        rows = result_dict.get("rows", [])

        if row_cnt == 0:
            return "Query executed successfully, but returned zero matching records."

        # Case 1: Single cell result (e.g., SELECT COUNT(*) or SELECT AVG(salary))
        if row_cnt == 1 and col_cnt == 1 and rows:
            val = rows[0][0]
            col_name = result_dict.get("columns", ["result"])[0]
            # Clean display formatting
            if isinstance(val, float):
                val_str = f"{val:,.2f}"
            else:
                val_str = str(val)
            return f"The {col_name} is {val_str}."

        # Case 2: Single row result
        if row_cnt == 1:
            return f"Query returned 1 record with {col_cnt} columns."

        # Case 3: Multiple rows result
        return f"Query executed successfully and returned {row_cnt} records."
