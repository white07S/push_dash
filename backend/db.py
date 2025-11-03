"""Database connection and initialization using APSW."""
import apsw
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database connection manager using APSW."""

    def __init__(self, db_path: str = "dashboard.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.connection = None
        self.init_db()

    def init_db(self):
        """Initialize database connection and set pragmas."""
        self.connection = apsw.Connection(self.db_path)

        # Set SQLite pragmas for performance
        pragmas = [
            "PRAGMA journal_mode=WAL;",
            "PRAGMA synchronous=NORMAL;",
            "PRAGMA temp_store=MEMORY;",
            "PRAGMA mmap_size=268435456;",  # 256MB
            "PRAGMA cache_size=-200000;",     # ~200MB
        ]

        cursor = self.connection.cursor()
        for pragma in pragmas:
            cursor.execute(pragma)

        # Create tables if they don't exist
        self.create_tables()

    def create_tables(self):
        """Create all necessary tables for the dashboard."""
        cursor = self.connection.cursor()

        # Define datasets and their keys
        datasets = {
            'controls': 'control_id',
            'external_loss': 'ext_loss_id',
            'internal_loss': 'loss_id',
            'issues': 'issue_id'
        }

        # AI function tables for each dataset
        ai_functions = [
            'ai_taxonomy',
            'ai_root_causes',
            'ai_enrichment',
            'similar_controls'
        ]

        for dataset, key_field in datasets.items():
            # Create raw table for each dataset
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {dataset}_raw (
                    {key_field} TEXT PRIMARY KEY,
                    description TEXT,
                    nfr_taxonomy TEXT,
                    raw_data JSON,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create index on nfr_taxonomy for filtering
            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_{dataset}_nfr_taxonomy
                ON {dataset}_raw(nfr_taxonomy)
            ''')

            # Create FTS5 virtual table for text search (optional, for future expansion)
            # Check if FTS table exists first
            cursor.execute(f'''
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='{dataset}_fts'
            ''')
            if not cursor.fetchone():
                cursor.execute(f'''
                    CREATE VIRTUAL TABLE {dataset}_fts
                    USING fts5(
                        {key_field} UNINDEXED,
                        description,
                        content={dataset}_raw,
                        tokenize='porter ascii'
                    )
                ''')

            # Create AI function tables
            for func in ai_functions:
                # Adjust function name for datasets other than controls
                if func == 'similar_controls' and dataset != 'controls':
                    func_name = f'similar_{dataset}'
                else:
                    func_name = func

                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {dataset}_{func_name} (
                        {key_field} TEXT PRIMARY KEY,
                        payload JSON,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY({key_field}) REFERENCES {dataset}_raw({key_field})
                    )
                ''')

        # Create taxonomy normalization tables (optional, for normalized taxonomy storage)
        for dataset, key_field in datasets.items():
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {dataset}_taxonomy_map (
                    {key_field} TEXT,
                    taxonomy_token TEXT,
                    PRIMARY KEY({key_field}, taxonomy_token),
                    FOREIGN KEY({key_field}) REFERENCES {dataset}_raw({key_field})
                )
            ''')

            cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_{dataset}_taxonomy_map_token
                ON {dataset}_taxonomy_map(taxonomy_token)
            ''')

        # APSW is in autocommit mode by default, no commit needed

    def get_connection(self) -> apsw.Connection:
        """Get database connection."""
        return self.connection

    def execute(self, query: str, params: tuple = ()) -> apsw.Cursor:
        """Execute a query with parameters."""
        cursor = self.connection.cursor()
        return cursor.execute(query, params)

    def executemany(self, query: str, params_list: List[tuple]) -> apsw.Cursor:
        """Execute a query with multiple parameter sets."""
        cursor = self.connection.cursor()
        return cursor.executemany(query, params_list)

    def fetchone(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Execute query and fetch one row."""
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute query and fetch all rows."""
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def insert_json(self, table: str, key_field: str, key_value: str,
                   payload: Dict[str, Any], created_at: Optional[str] = None) -> bool:
        """Insert or update a JSON payload in an AI function table."""
        if created_at is None:
            created_at = datetime.utcnow().isoformat() + 'Z'

        query = f'''
            INSERT OR REPLACE INTO {table} ({key_field}, payload, created_at)
            VALUES (?, ?, ?)
        '''

        try:
            self.execute(query, (key_value, json.dumps(payload), created_at))
            # APSW is in autocommit mode by default, no commit needed
            return True
        except Exception as e:
            logger.error(f"Error inserting JSON into {table}: {e}")
            return False

    def get_json(self, table: str, key_field: str, key_value: str) -> Optional[Dict[str, Any]]:
        """Get JSON payload from an AI function table."""
        query = f'''
            SELECT payload, created_at FROM {table}
            WHERE {key_field} = ?
        '''

        result = self.fetchone(query, (key_value,))
        if result:
            payload, created_at = result
            return {
                'payload': json.loads(payload),
                'created_at': created_at
            }
        return None

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

# Global database instance
_db_instance = None

def get_db() -> Database:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance