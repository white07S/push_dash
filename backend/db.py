"""Database connection and initialization."""
from __future__ import annotations

import json
import logging
import os
import re
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

import apsw

from dataset_config import DATASET_CONFIG

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager with PostgreSQL primary and SQLite fallback."""

    def __init__(self, db_path: str = "dashboard.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.connection = None
        self.backend: Optional[str] = None  # "postgres" or "sqlite"
        self._lock = threading.Lock()
        self.init_db()

    # ------------------------------------------------------------------ init
    def init_db(self) -> None:
        """Initialize database connection, preferring PostgreSQL with SQLite fallback."""
        preferred = os.getenv("DB_BACKEND", "postgres").lower()

        if preferred in ("postgres", "postgresql", "pg"):
            if self._init_postgres():
                return
            logger.warning("Falling back to SQLite (APSW) after PostgreSQL initialization failure")

        # Default / fallback: SQLite
        self._init_sqlite()

    def _init_postgres(self) -> bool:
        """Attempt to initialize a PostgreSQL connection. Returns True on success."""
        try:
            import psycopg2
        except ImportError:
            logger.warning("psycopg2 is not installed; skipping PostgreSQL initialization")
            return False

        user = os.getenv("POSTGRES_USER", "preetam")
        password = os.getenv("POSTGRES_PASSWORD", "preetam123")
        dbname = os.getenv("POSTGRES_DB", "main")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = int(os.getenv("POSTGRES_PORT", "5432"))
        timeout = int(os.getenv("POSTGRES_CONNECT_TIMEOUT", "5"))

        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port,
                connect_timeout=timeout,
            )
            # Autocommit to match APSW behaviour
            conn.autocommit = True
            self.connection = conn
            self.backend = "postgres"

            with conn.cursor() as cursor:
                # Ensure analytics schema exists and becomes the default search path
                cursor.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
                cursor.execute("SET search_path TO analytics, public;")

            self._create_tables_postgres()
            logger.info("Connected to PostgreSQL database '%s' (schema: analytics)", dbname)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("PostgreSQL initialization failed: %s", exc)
            self.connection = None
            self.backend = None
            return False

    def _init_sqlite(self) -> None:
        """Initialize SQLite (APSW) connection."""
        self.connection = apsw.Connection(self.db_path)
        self.backend = "sqlite"

        # Set SQLite pragmas for performance
        pragmas = [
            "PRAGMA journal_mode=WAL;",
            "PRAGMA synchronous=NORMAL;",
            "PRAGMA temp_store=MEMORY;",
            "PRAGMA mmap_size=268435456;",  # 256MB
            "PRAGMA cache_size=-200000;",  # ~200MB
        ]

        cursor = self.connection.cursor()
        for pragma in pragmas:
            cursor.execute(pragma)

        self._create_tables_sqlite()
        logger.info("Connected to SQLite database at %s", self.db_path)

    # ------------------------------------------------------------------ schema
    def _create_tables_sqlite(self) -> None:
        """Create all necessary tables for SQLite."""
        cursor = self.connection.cursor()

        for dataset, config in DATASET_CONFIG.items():
            key_field = config.key_field
            table = config.table

            # Create raw table for each dataset
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    {key_field} TEXT PRIMARY KEY,
                    title TEXT,
                    category TEXT,
                    risk_theme TEXT,
                    risk_subtheme TEXT,
                    raw_data JSON,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Create index on risk theme for filtering
            cursor.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{dataset}_risk_theme
                ON {table}(risk_theme)
                """
            )

            cursor.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{dataset}_risk_subtheme
                ON {table}(risk_subtheme)
                """
            )

            # Create FTS5 virtual table for text search (optional, for future expansion)
            cursor.execute(
                f"""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='{dataset}_fts'
                """
            )
            if not cursor.fetchone():
                cursor.execute(
                    f"""
                    CREATE VIRTUAL TABLE {dataset}_fts
                    USING fts5(
                        {key_field} UNINDEXED,
                        title,
                        category,
                        content={table},
                        tokenize='porter ascii'
                    )
                    """
                )

            # Create AI function tables
            for func in config.ai_functions:
                table_name = f"{dataset}_{func}"

                cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {key_field} TEXT PRIMARY KEY,
                        payload JSON,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY({key_field}) REFERENCES {table}({key_field})
                    )
                    """
                )

        # APSW is in autocommit mode by default, no commit needed

    def _create_tables_postgres(self) -> None:
        """Create all necessary tables for PostgreSQL."""
        cursor = self.connection.cursor()

        for dataset, config in DATASET_CONFIG.items():
            key_field = config.key_field
            table = config.table

            # Create raw table for each dataset
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    {key_field} TEXT PRIMARY KEY,
                    title TEXT,
                    category TEXT,
                    risk_theme TEXT,
                    risk_subtheme TEXT,
                    raw_data TEXT,
                    created_at TEXT
                )
                """
            )

            # Create index on risk theme for filtering
            cursor.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{dataset}_risk_theme
                ON {table}(risk_theme)
                """
            )

            cursor.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{dataset}_risk_subtheme
                ON {table}(risk_subtheme)
                """
            )

            # Create AI function tables
            for func in config.ai_functions:
                table_name = f"{dataset}_{func}"

                cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {key_field} TEXT PRIMARY KEY,
                        payload TEXT,
                        created_at TEXT,
                        FOREIGN KEY({key_field}) REFERENCES {table}({key_field})
                    )
                    """
                )

        logger.info("Ensured PostgreSQL tables exist in schema 'analytics'")

    # ------------------------------------------------------------------ helpers
    def _get_key_field_for_table(self, table: str) -> Optional[str]:
        """Infer the primary key field for a given table name."""
        for dataset, config in DATASET_CONFIG.items():
            if config.table == table or table.startswith(f"{dataset}_"):
                return config.key_field
        return None

    def _adapt_insert_or_ignore(self, query: str) -> str:
        """Translate SQLite INSERT OR IGNORE into PostgreSQL ON CONFLICT DO NOTHING."""
        token = "INSERT OR IGNORE INTO"
        upper = query.upper()
        idx = upper.find(token)
        if idx == -1:
            return query

        after = query[idx + len(token) :]
        after_strip = after.lstrip()
        table = ""
        for ch in after_strip:
            if ch.isspace() or ch == "(":
                break
            table += ch

        key_field = self._get_key_field_for_table(table)
        if not key_field:
            logger.warning(
                "Could not resolve key field for table '%s' when adapting INSERT OR IGNORE", table
            )
            return query.replace("INSERT OR IGNORE", "INSERT", 1)

        base = query.replace("INSERT OR IGNORE", "INSERT", 1).rstrip(";\n ")
        return f"{base} ON CONFLICT ({key_field}) DO NOTHING"

    def _adapt_insert_or_replace(self, query: str) -> str:
        """Translate SQLite INSERT OR REPLACE into PostgreSQL ON CONFLICT DO UPDATE."""
        token = "INSERT OR REPLACE INTO"
        upper = query.upper()
        idx = upper.find(token)
        if idx == -1:
            return query

        # Determine table name
        after = query[idx + len(token) :]
        after_strip = after.lstrip()
        table = ""
        for ch in after_strip:
            if ch.isspace() or ch == "(":
                break
            table += ch

        key_field = self._get_key_field_for_table(table)
        if not key_field:
            logger.warning(
                "Could not resolve key field for table '%s' when adapting INSERT OR REPLACE", table
            )
            return query.replace("INSERT OR REPLACE", "INSERT", 1)

        # Extract column list between first pair of parentheses after INTO
        try:
            start_cols = query.index("(", idx)
            end_cols = query.index(")", start_cols)
        except ValueError:
            logger.warning(
                "Could not locate column list when adapting INSERT OR REPLACE for table '%s'",
                table,
            )
            return query.replace("INSERT OR REPLACE", "INSERT", 1)

        columns_str = query[start_cols + 1 : end_cols]
        columns = [col.strip() for col in columns_str.split(",") if col.strip()]
        non_key_columns = [col for col in columns if col != key_field]

        base = query.replace("INSERT OR REPLACE", "INSERT", 1).rstrip(";\n ")
        if non_key_columns:
            assignments = ", ".join(f"{col} = EXCLUDED.{col}" for col in non_key_columns)
            conflict = f" ON CONFLICT ({key_field}) DO UPDATE SET {assignments}"
        else:
            conflict = f" ON CONFLICT ({key_field}) DO NOTHING"

        return f"{base}{conflict}"

    def _adapt_query_for_postgres(self, query: str) -> str:
        """Adapt SQLite-oriented SQL to PostgreSQL (upserts + placeholders)."""
        adapted = query

        if "INSERT OR REPLACE" in adapted:
            adapted = self._adapt_insert_or_replace(adapted)
        if "INSERT OR IGNORE" in adapted:
            adapted = self._adapt_insert_or_ignore(adapted)

        # Convert SQLite-style ? placeholders to psycopg2-style %s
        if "?" in adapted:
            adapted = adapted.replace("?", "%s")

        return adapted

    # ------------------------------------------------------------------ public API
    def get_connection(self):
        """Get underlying database connection."""
        return self.connection

    def execute(self, query: str, params: tuple = ()) :
        """Execute a query with parameters."""
        if self.connection is None:
            raise RuntimeError("Database connection is not initialized")

        with self._lock:
            cursor = self.connection.cursor()
            if self.backend == "postgres":
                sql = self._adapt_query_for_postgres(query)
                cursor.execute(sql, params or None)
            else:
                cursor.execute(query, params)
            return cursor

    def executemany(self, query: str, params_list: List[tuple]):
        """Execute a query with multiple parameter sets."""
        if self.connection is None:
            raise RuntimeError("Database connection is not initialized")

        with self._lock:
            cursor = self.connection.cursor()
            if self.backend == "postgres":
                sql = self._adapt_query_for_postgres(query)
                cursor.executemany(sql, params_list)
            else:
                cursor.executemany(query, params_list)
            return cursor

    def fetchone(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Execute query and fetch one row."""
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute query and fetch all rows."""
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def insert_json(
        self,
        table: str,
        key_field: str,
        key_value: str,
        payload: Dict[str, Any],
        created_at: Optional[str] = None,
    ) -> bool:
        """Insert or update a JSON payload in an AI function table."""
        if created_at is None:
            created_at = datetime.utcnow().isoformat() + "Z"

        query = f"""
            INSERT OR REPLACE INTO {table} ({key_field}, payload, created_at)
            VALUES (?, ?, ?)
        """

        try:
            self.execute(query, (key_value, json.dumps(payload), created_at))
            return True
        except Exception as e:  # pragma: no cover - logging side-effect
            logger.error("Error inserting JSON into %s: %s", table, e)
            return False

    def get_json(self, table: str, key_field: str, key_value: str) -> Optional[Dict[str, Any]]:
        """Get JSON payload from an AI function table."""
        query = f"""
            SELECT payload, created_at FROM {table}
            WHERE {key_field} = ?
        """

        result = self.fetchone(query, (key_value,))
        if result:
            payload, created_at = result
            return {
                "payload": json.loads(payload),
                "created_at": created_at,
            }
        return None

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:  # pragma: no cover - defensive
                logger.exception("Error while closing database connection")


# Global database instance
_db_instance: Optional[Database] = None


def get_db() -> Database:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
