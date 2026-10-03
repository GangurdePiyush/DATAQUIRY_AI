"""
query/nl_to_sql.py
------------------
Translates natural-language user questions into safe, read-only SQLite SQL queries
using a Local LLM architecture (Ollama HTTP API). Includes safety validation and offline fallbacks.
"""

import re
from typing import Tuple, Optional, Dict, Any
import requests

import config
from database.schema import TableSchema


def is_safe_sql(sql_str: str) -> Tuple[bool, str]:
    """
    Validates that a generated or user-provided SQL query is strictly read-only.

    Forbidden statements:
        DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, ATTACH, DETACH, PRAGMA, EXEC, TRUNCATE, REPLACE

    Returns:
        Tuple[bool, str]: (Is safe boolean, Error explanation message if unsafe)
    """
    if not sql_str or not sql_str.strip():
        return False, "SQL query is empty."

    sql_clean = sql_str.strip()
    sql_upper = sql_clean.upper()

    # List of dangerous/forbidden SQL keywords
    FORBIDDEN_KEYWORDS = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE",
        "ATTACH", "DETACH", "PRAGMA", "EXEC", "TRUNCATE", "REPLACE",
        "GRANT", "REVOKE"
    ]

    # Check for forbidden keywords using word boundaries
    for kw in FORBIDDEN_KEYWORDS:
        pattern = r"\b" + kw + r"\b"
        if re.search(pattern, sql_upper):
            return False, f"Security Violation: Forbidden SQL statement '{kw}' detected. Only read-only queries are permitted."

    # Must begin with SELECT or WITH
    if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
        return False, "Security Violation: Query must begin with a read-only SELECT or WITH statement."

    return True, "Query passed security checks."


class NLToSQLConverter:
    """
    Converts natural-language questions into valid SQLite queries using local Ollama AI.
    """

    def __init__(self, ollama_url: Optional[str] = None, model_name: Optional[str] = None):
        self.ollama_url = ollama_url or config.OLLAMA_URL
        self.model_name = model_name or config.OLLAMA_MODEL
        self.timeout = config.OLLAMA_TIMEOUT

    def generate_sql(self, question: str, schema: TableSchema) -> Tuple[bool, str, str]:
        """
        Translates a user question into SQL.

        Parameters:
            question (str): User natural-language question.
            schema (TableSchema): Detected database schema.

        Returns:
            Tuple[bool, str, str]: (Success status, Generated SQL or Error, Source/Status message)
        """
        if not question or not question.strip():
            return False, "-- Empty question provided --", "Please enter a question."

        if not schema or not schema.columns:
            return False, "-- No database loaded --", "Please upload a dataset to create a database first."

        # Step 1: Attempt to generate query using Local Ollama AI Model
        success_ai, sql_ai, msg_ai = self._query_ollama(question, schema)
        if success_ai:
            return True, sql_ai, f"Generated via Local AI ('{self.model_name}')"

        # Step 2: Fallback to local pattern-matching engine if Ollama is offline/unavailable
        success_pattern, sql_pattern, msg_pattern = self._fallback_pattern_match(question, schema)
        if success_pattern:
            return True, sql_pattern, f"Generated via Smart Pattern Matcher ({msg_ai})"

        # Step 3: Return graceful offline notice if both AI and pattern matching fail
        error_display = (
            f"-- Local AI Service Unavailable --\n"
            f"-- {msg_ai}\n\n"
            f"-- You can type or edit SQL queries manually below."
        )
        return False, error_display, "Local AI service is not available. Please start Ollama or use SQL mode."

    def _query_ollama(self, question: str, schema: TableSchema) -> Tuple[bool, str, str]:
        """
        Sends prompt to local Ollama API endpoint.
        """
        prompt = self._build_prompt(question, schema)

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for deterministic SQL output
            }
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                raw_text = data.get("response", "").strip()

                # Extract and clean SQL string
                clean_sql = self._clean_raw_sql(raw_text)

                # Security check
                is_safe, err_msg = is_safe_sql(clean_sql)
                if is_safe:
                    return True, clean_sql, "Success"
                else:
                    return False, f"-- Generated query blocked by security filter --\n-- {err_msg}", err_msg
            else:
                return False, "", f"Ollama HTTP {response.status_code}"

        except requests.exceptions.ConnectionError:
            return False, "", "Ollama service is not running on localhost:11434"
        except requests.exceptions.Timeout:
            return False, "", "Ollama request timed out"
        except Exception as ex:
            return False, "", f"Ollama error: {str(ex)}"

    def _build_prompt(self, question: str, schema: TableSchema) -> str:
        """Constructs schema-aware system prompt for local LLM."""
        col_list = [f"- {col.clean_name} ({col.sqlite_type})" for col in schema.columns]
        cols_formatted = "\n".join(col_list)

        prompt = (
            f"You are a SQLite SQL generator.\n"
            f"Convert the user question into a single valid read-only SQLite SQL statement.\n\n"
            f"DATABASE SCHEMA:\n"
            f"Table Name: '{schema.table_name}'\n"
            f"Columns & Types:\n"
            f"{cols_formatted}\n\n"
            f"USER QUESTION: {question}\n\n"
            f"RULES:\n"
            f"1. Use ONLY the table name '{schema.table_name}'.\n"
            f"2. Use ONLY column names defined in the schema above.\n"
            f"3. Return ONLY a single read-only SELECT or WITH statement.\n"
            f"4. Do NOT output markdown code blocks (```), backticks, or explanations.\n"
            f"5. Output raw SQL only.\n\n"
            f"SQL QUERY:"
        )
        return prompt

    def _clean_raw_sql(self, text: str) -> str:
        """Strips markdown code block fences and extra commentary from LLM output."""
        if not text:
            return ""

        # Remove markdown code blocks ```sql ... ```
        cleaned = re.sub(r"```sql\s*", "", text, flags=re.IGNORECASE)
        cleaned = re.sub(r"```\s*", "", cleaned)
        cleaned = cleaned.strip()

        # If multiple lines, grab the line starting with SELECT or WITH
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        for line in lines:
            line_upper = line.upper()
            if line_upper.startswith("SELECT") or line_upper.startswith("WITH"):
                return line

        return cleaned

    def _fallback_pattern_match(self, question: str, schema: TableSchema) -> Tuple[bool, str, str]:
        """
        Smart offline pattern matcher for standard queries when local LLM is unreachable.
        Handles common college project questions:
        - "Show the first 10 rows"
        - "How many records are there?"
        - "What is the average salary?"
        - "Show employees whose age is greater than 30"
        """
        q_lower = question.strip().lower()
        tbl = schema.table_name
        cols = schema.get_column_names()
        col_types = schema.get_column_types()

        # Pattern 1: Count / How many records
        if any(phrase in q_lower for phrase in ["how many", "count", "total records", "number of rows"]):
            return True, f"SELECT COUNT(*) AS total_records FROM `{tbl}`;", "Ollama offline fallback"

        # Pattern 2: First N rows / limit N
        match_limit = re.search(r"(?:first|top|show|display)\s+(\d+)\s+rows", q_lower)
        if match_limit:
            n = match_limit.group(1)
            return True, f"SELECT * FROM `{tbl}` LIMIT {n};", "Ollama offline fallback"

        if "first" in q_lower or "preview" in q_lower:
            return True, f"SELECT * FROM `{tbl}` LIMIT 10;", "Ollama offline fallback"

        # Pattern 3: Average of a numeric column ("What is the average salary?")
        if "average" in q_lower or "avg" in q_lower or "mean" in q_lower:
            for col_name in cols:
                if col_name in q_lower:
                    return True, f"SELECT AVG(`{col_name}`) AS average_{col_name} FROM `{tbl}`;", "Ollama offline fallback"
            # Default to first numeric column if specific column name not found in string
            for col_name, ctype in col_types.items():
                if ctype in ["INTEGER", "REAL"]:
                    return True, f"SELECT AVG(`{col_name}`) AS average_{col_name} FROM `{tbl}`;", "Ollama offline fallback"

        # Pattern 4: Filtering comparison ("Show employees whose age is greater than 30")
        match_filter = re.search(r"(\w+)\s+(?:is\s+)?(greater than|>|more than|older than)\s+(\d+)", q_lower)
        if match_filter:
            target_word = match_filter.group(1)
            val = match_filter.group(3)
            # Find matching column
            matched_col = None
            for col_name in cols:
                if col_name in target_word or target_word in col_name:
                    matched_col = col_name
                    break
            if not matched_col:
                # check if target_word matches any numeric column
                for col_name, ctype in col_types.items():
                    if ctype in ["INTEGER", "REAL"] and col_name in q_lower:
                        matched_col = col_name
                        break
            if matched_col:
                return True, f"SELECT * FROM `{tbl}` WHERE `{matched_col}` > {val};", "Ollama offline fallback"

        # Pattern 5: Show all columns
        if any(phrase in q_lower for phrase in ["show all", "list all", "get all"]):
            return True, f"SELECT * FROM `{tbl}`;", "Ollama offline fallback"

        return False, "", "No pattern match"
