"""Database connection and initialization."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

import apsw
import yaml

from dataset_config import DATASET_CONFIG

logger = logging.getLogger(__name__)


def _load_db_config() -> Dict[str, Any]:
    """Load database configuration from config.yaml."""
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:  # pragma: no cover - defensive
            logger.exception("Failed to load config.yaml for database configuration")
    return {}


_DB_CONFIG: Dict[str, Any] = _load_db_config()


class _PGCursorResult:
    """Minimal cursor-like wrapper for asyncpg execute results."""

    def __init__(self, rowcount: int):
        self.rowcount = rowcount


class Database:
    """Database connection manager with PostgreSQL primary and SQLite fallback."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection."""
        self._config: Dict[str, Any] = _DB_CONFIG
        self._db_cfg: Dict[str, Any] = self._config.get("database", {})

        # Determine SQLite DB path
        if db_path is None:
            self.db_path = self._db_cfg.get("path", "dashboard.db")
        else:
            self.db_path = db_path

        self.connection = None  # Used for SQLite
        self.backend: Optional[str] = None  # "postgres" or "sqlite"

        # AsyncPG state (used when backend == "postgres")
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._loop_thread: Optional[threading.Thread] = None
        self._pg_pool: Any = None

        self._lock = threading.Lock()
        self.init_db()

    # ------------------------------------------------------------------ init
    def init_db(self) -> None:
        """Initialize database connection, preferring PostgreSQL with SQLite fallback."""
        preferred = (
            str(self._db_cfg.get("backend", os.getenv("DB_BACKEND", "postgres")))
            .strip()
            .lower()
        )

        if preferred in ("postgres", "postgresql", "pg"):
            if self._init_postgres():
                return
            logger.warning("Falling back to SQLite (APSW) after PostgreSQL initialization failure")

        # Default / fallback: SQLite
        self._init_sqlite()

    def _init_postgres(self) -> bool:
        """Attempt to initialize a PostgreSQL connection using asyncpg. Returns True on success."""
        try:
            import asyncpg  # type: ignore[import]
        except ImportError:
            logger.warning("asyncpg is not installed; skipping PostgreSQL initialization")
            return False

        pg_cfg: Dict[str, Any] = self._db_cfg.get("postgres", {})

        user = os.getenv("POSTGRES_USER", pg_cfg.get("user", "preetam"))
        password = os.getenv("POSTGRES_PASSWORD", pg_cfg.get("password", "preetam123"))
        dbname = os.getenv("POSTGRES_DB", pg_cfg.get("db", "main"))
        host = os.getenv("POSTGRES_HOST", pg_cfg.get("host", "localhost"))
        port = int(os.getenv("POSTGRES_PORT", pg_cfg.get("port", 5432)))
        timeout = int(
            os.getenv("POSTGRES_CONNECT_TIMEOUT", pg_cfg.get("connect_timeout", 5))
        )

        # Start a dedicated event loop in a background thread for asyncpg
        loop = asyncio.new_event_loop()

        def _run_loop() -> None:
            asyncio.set_event_loop(loop)
            loop.run_forever()

        thread = threading.Thread(target=_run_loop, daemon=True)
        thread.start()

        self._loop = loop
        self._loop_thread = thread

        async def _setup() -> bool:
            try:
                pool = await asyncpg.create_pool(  # type: ignore[attr-defined]
                    user=user,
                    password=password,
                    database=dbname,
                    host=host,
                    port=port,
                    timeout=timeout,
                )
                self._pg_pool = pool

                async with pool.acquire() as conn:
                    # Ensure analytics schema exists and becomes the default search path
                    await conn.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
                    await conn.execute("SET search_path TO analytics, public;")
                    await self._create_tables_postgres(conn)

                return True
            except Exception as exc:  # pragma: no cover - defensive
                logger.error("PostgreSQL (asyncpg) initialization failed: %s", exc)
                return False

        try:
            fut = asyncio.run_coroutine_threadsafe(_setup(), loop)
            ok = fut.result(timeout=timeout + 10)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("PostgreSQL (asyncpg) setup failed: %s", exc)
            ok = False

        if not ok:
            # Tear down loop / pool if setup failed
            self._pg_pool = None
            if self._loop is not None:
                self._loop.call_soon_threadsafe(self._loop.stop)
            if self._loop_thread is not None:
                self._loop_thread.join(timeout=5)
            self._loop = None
            self._loop_thread = None
            return False

        self.backend = "postgres"
        logger.info("Connected to PostgreSQL database '%s' (schema: analytics)", dbname)
        return True

    def _init_sqlite(self) -> None:
        """Initialize SQLite (APSW) connection."""
        self.connection = apsw.Connection(self.db_path)
        self.backend = "sqlite"

        # Set SQLite pragmas for performance
        pragmas_cfg: Dict[str, Any] = self._db_cfg.get("pragmas", {})
        pragmas = [
            f"PRAGMA journal_mode={pragmas_cfg.get('journal_mode', 'WAL')};",
            f"PRAGMA synchronous={pragmas_cfg.get('synchronous', 'NORMAL')};",
            f"PRAGMA temp_store={pragmas_cfg.get('temp_store', 'MEMORY')};",
            f"PRAGMA mmap_size={int(pragmas_cfg.get('mmap_size', 268435456))};",
            f"PRAGMA cache_size={int(pragmas_cfg.get('cache_size', -200000))};",
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

    async def _create_tables_postgres(self, conn: Any) -> None:
        """Create all necessary tables for PostgreSQL."""
        for dataset, config in DATASET_CONFIG.items():
            key_field = config.key_field
            table = config.table

            # Create raw table for each dataset
            await conn.execute(
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
            await conn.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{dataset}_risk_theme
                ON {table}(risk_theme)
                """
            )

            await conn.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_{dataset}_risk_subtheme
                ON {table}(risk_subtheme)
                """
            )

            # Create AI function tables
            for func in config.ai_functions:
                table_name = f"{dataset}_{func}"

                await conn.execute(
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

    def _replace_placeholders(self, query: str, param_count: int) -> str:
        """Convert SQLite-style ? placeholders to asyncpg-style $1, $2, ..."""
        if param_count <= 0 or "?" not in query:
            return query

        adapted = query
        for idx in range(1, param_count + 1):
            adapted = adapted.replace("?", f"${idx}", 1)
        return adapted

    def _adapt_query_for_postgres(self, query: str, param_count: int) -> str:
        """Adapt SQLite-oriented SQL to PostgreSQL (upserts + placeholders)."""
        adapted = query
        upper = adapted.upper()

        if "INSERT OR REPLACE" in upper:
            adapted = self._adapt_insert_or_replace(adapted)
        if "INSERT OR IGNORE" in upper:
            adapted = self._adapt_insert_or_ignore(adapted)

        adapted = self._replace_placeholders(adapted, param_count)
        return adapted

    def _pg_run(self, coro, timeout: int = 30):
        """Run an asyncpg coroutine on the dedicated event loop and wait for the result."""
        if self._loop is None:
            raise RuntimeError("PostgreSQL event loop is not initialized")
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return fut.result(timeout=timeout)

    def _pg_execute(self, query: str, params: tuple) -> _PGCursorResult:
        """Execute a non-SELECT statement and return a minimal cursor-like result."""
        if self._pg_pool is None:
            raise RuntimeError("PostgreSQL pool is not initialized")

        async def _exec():
            async with self._pg_pool.acquire() as conn:
                result = await conn.execute(query, *params)
                return result

        result: str = self._pg_run(_exec())
        # asyncpg returns strings like "INSERT 0 1" or "DELETE 0 3"
        parts = result.split()
        rowcount = int(parts[-1]) if parts and parts[-1].isdigit() else 0
        return _PGCursorResult(rowcount=rowcount)

    def _pg_fetchone(self, query: str, params: tuple) -> Optional[tuple]:
        """Execute a SELECT and fetch one row."""
        if self._pg_pool is None:
            raise RuntimeError("PostgreSQL pool is not initialized")

        async def _fetchone():
            async with self._pg_pool.acquire() as conn:
                row = await conn.fetchrow(query, *params)
                return tuple(row) if row is not None else None

        return self._pg_run(_fetchone())

    def _pg_fetchall(self, query: str, params: tuple) -> List[tuple]:
        """Execute a SELECT and fetch all rows."""
        if self._pg_pool is None:
            raise RuntimeError("PostgreSQL pool is not initialized")

        async def _fetchall():
            async with self._pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                return [tuple(row) for row in rows]

        return self._pg_run(_fetchall())

    # ------------------------------------------------------------------ public API
    def get_connection(self):
        """Get underlying database connection."""
        return self.connection

    def execute(self, query: str, params: tuple = ()) :
        """Execute a query with parameters."""
        if self.backend == "postgres":
            param_count = len(params)
            sql = self._adapt_query_for_postgres(query, param_count)
            return self._pg_execute(sql, params)

        if self.connection is None:
            raise RuntimeError("SQLite connection is not initialized")

        with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            return cursor

    def executemany(self, query: str, params_list: List[tuple]):
        """Execute a query with multiple parameter sets."""
        if self.backend == "postgres":
            if not params_list:
                return _PGCursorResult(rowcount=0)
            param_count = len(params_list[0])
            sql = self._adapt_query_for_postgres(query, param_count)

            if self._pg_pool is None:
                raise RuntimeError("PostgreSQL pool is not initialized")

            async def _execmany():
                async with self._pg_pool.acquire() as conn:
                    result = await conn.executemany(sql, params_list)
                    return result

            result: str = self._pg_run(_execmany())
            parts = result.split()
            rowcount = int(parts[-1]) if parts and parts[-1].isdigit() else 0
            return _PGCursorResult(rowcount=rowcount)

        if self.connection is None:
            raise RuntimeError("SQLite connection is not initialized")

        with self._lock:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            return cursor

    def fetchone(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Execute query and fetch one row."""
        if self.backend == "postgres":
            param_count = len(params)
            sql = self._adapt_query_for_postgres(query, param_count)
            return self._pg_fetchone(sql, params)

        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute query and fetch all rows."""
        if self.backend == "postgres":
            param_count = len(params)
            sql = self._adapt_query_for_postgres(query, param_count)
            return self._pg_fetchall(sql, params)

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
        if self.backend == "postgres":
            # Close asyncpg resources
            if self._pg_pool is not None and self._loop is not None:
                async def _close_pool():
                    await self._pg_pool.close()

                try:
                    self._pg_run(_close_pool(), timeout=10)
                except Exception:  # pragma: no cover - defensive
                    logger.exception("Error while closing PostgreSQL pool")

            if self._loop is not None:
                self._loop.call_soon_threadsafe(self._loop.stop)
            if self._loop_thread is not None:
                self._loop_thread.join(timeout=5)

            self._pg_pool = None
            self._loop = None
            self._loop_thread = None

        if self.connection:
            try:
                self.connection.close()
            except Exception:  # pragma: no cover - defensive
                logger.exception("Error while closing SQLite connection")


# Global database instance
_db_instance: Optional[Database] = None


def get_db() -> Database:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
