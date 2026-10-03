"""
query/query_engine.py
---------------------
Core Query Engine facade integrating Natural Language to SQL generation,
security validation, and SQL query execution.
"""

from typing import Tuple, Optional, Dict, Any
from database.schema import TableSchema
from .nl_to_sql import NLToSQLConverter, is_safe_sql
from .sql_executor import SQLExecutor


class QueryEngine:
    """
    Facade class managing natural language translation, security checks, and SQL execution.
    """

    def __init__(self, ollama_url: Optional[str] = None, model_name: Optional[str] = None):
        self.converter = NLToSQLConverter(ollama_url=ollama_url, model_name=model_name)
        self.executor = SQLExecutor()

    def process_question(self, user_question: str, schema: TableSchema) -> Dict[str, Any]:
        """
        Translates a natural language question into SQL.
        """
        success, sql_query, message = self.converter.generate_sql(user_question, schema)

        return {
            "success": success,
            "question": user_question,
            "sql": sql_query,
            "message": message,
        }

    def execute_sql(self, sql_query: str, db_handler) -> Dict[str, Any]:
        """
        Executes a SQL query against the database managed by db_handler.
        """
        return self.executor.execute_sql(sql_query, db_handler)

    def validate_sql(self, sql_str: str) -> Tuple[bool, str]:
        """Validates that a SQL query is read-only and secure."""
        return is_safe_sql(sql_str)
