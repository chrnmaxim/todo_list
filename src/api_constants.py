"""Модуль констант."""

# MARK: Security
from sqlalchemy import TextClause, text

CORS_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ORIGINS: list[str] = ["*"]

# MARK: Database
DB_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
DEFAULT_QUERY_OFFSET: int = 0
DEFAULT_QUERY_LIMIT: int = 100
CURRENT_TIMESTAMP_UTC: TextClause = text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')")
