"""Resolver utility for cache-or-compute pattern."""
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from db import get_db
from services import mock_ai

logger = logging.getLogger(__name__)

class FunctionResolver:
    """Resolve function results using cache-or-compute pattern."""

    def __init__(self):
        """Initialize resolver."""
        self.db = get_db()

        # Map dataset and function names to mock AI functions
        self.function_map = {
            'controls': {
                'ai_taxonomy': mock_ai.get_controls_ai_taxonomy,
                'ai_root_causes': mock_ai.get_controls_ai_root_causes,
                'ai_enrichment': mock_ai.get_controls_ai_enrichment,
                'similar_controls': mock_ai.get_controls_similar_controls
            },
            'external_loss': {
                'ai_taxonomy': mock_ai.get_external_loss_ai_taxonomy,
                'ai_root_causes': mock_ai.get_external_loss_ai_root_causes,
                'ai_enrichment': mock_ai.get_external_loss_ai_enrichment,
                'similar_external_loss': mock_ai.get_external_loss_similar_external_loss
            },
            'internal_loss': {
                'ai_taxonomy': mock_ai.get_internal_loss_ai_taxonomy,
                'ai_root_causes': mock_ai.get_internal_loss_ai_root_causes,
                'ai_enrichment': mock_ai.get_internal_loss_ai_enrichment,
                'similar_internal_loss': mock_ai.get_internal_loss_similar_internal_loss
            },
            'issues': {
                'ai_taxonomy': mock_ai.get_issues_ai_taxonomy,
                'ai_root_causes': mock_ai.get_issues_ai_root_causes,
                'ai_enrichment': mock_ai.get_issues_ai_enrichment,
                'similar_issues': mock_ai.get_issues_similar_issues
            }
        }

        # Map dataset to key field
        self.key_fields = {
            'controls': 'control_id',
            'external_loss': 'ext_loss_id',
            'internal_loss': 'loss_id',
            'issues': 'issue_id'
        }

    def resolve(
        self,
        dataset: str,
        func: str,
        id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Resolve function result using cache-or-compute pattern.

        Args:
            dataset: Dataset name (controls, external_loss, internal_loss, issues)
            func: Function name (ai_taxonomy, ai_root_causes, etc.)
            id: Item ID
            description: Optional description (will be fetched if not provided)
            refresh: Force recompute even if cached

        Returns:
            Dictionary with status, source, payload, and created_at
        """
        # Validate dataset and function
        if dataset not in self.function_map:
            raise ValueError(f"Invalid dataset: {dataset}")

        if func not in self.function_map[dataset]:
            raise ValueError(f"Invalid function '{func}' for dataset '{dataset}'")

        key_field = self.key_fields[dataset]

        # Check if ID exists in raw table
        raw_query = f"SELECT description FROM {dataset}_raw WHERE {key_field} = ?"
        raw_result = self.db.fetchone(raw_query, (id,))

        if not raw_result:
            raise ValueError(f"ID '{id}' not found in {dataset}")

        # Use provided description or fetch from raw table
        if description is None:
            description = raw_result[0]

        # Determine table name
        table_name = f"{dataset}_{func}"

        # Check cache unless refresh is requested
        if not refresh:
            cached = self._get_cached_result(table_name, key_field, id)
            if cached:
                return {
                    "status": "ok",
                    "source": "cache",
                    "payload": cached['payload'],
                    "created_at": cached['created_at']
                }

        # Compute result
        try:
            compute_func = self.function_map[dataset][func]
            payload = compute_func(id, description)

            # Store in cache
            created_at = datetime.utcnow().isoformat() + 'Z'
            self._store_result(table_name, key_field, id, payload, created_at)

            return {
                "status": "ok",
                "source": "computed",
                "payload": payload,
                "created_at": created_at
            }

        except Exception as e:
            logger.error(f"Error computing {func} for {id}: {e}")
            raise RuntimeError(f"Failed to compute {func}: {str(e)}")

    def _get_cached_result(
        self,
        table: str,
        key_field: str,
        id: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached result from database.

        Args:
            table: Table name
            key_field: Key field name
            id: Item ID

        Returns:
            Cached result or None
        """
        query = f"SELECT payload, created_at FROM {table} WHERE {key_field} = ?"
        result = self.db.fetchone(query, (id,))

        if result:
            payload, created_at = result
            return {
                'payload': json.loads(payload),
                'created_at': created_at
            }

        return None

    def _store_result(
        self,
        table: str,
        key_field: str,
        id: str,
        payload: Dict[str, Any],
        created_at: str
    ) -> bool:
        """Store result in database.

        Args:
            table: Table name
            key_field: Key field name
            id: Item ID
            payload: Result payload
            created_at: Creation timestamp

        Returns:
            Success status
        """
        query = f'''
            INSERT OR REPLACE INTO {table} ({key_field}, payload, created_at)
            VALUES (?, ?, ?)
        '''

        try:
            self.db.execute(query, (id, json.dumps(payload), created_at))
            # APSW is in autocommit mode by default, no commit needed
            return True
        except Exception as e:
            logger.error(f"Error storing result in {table}: {e}")
            return False

    def get_all_results(
        self,
        dataset: str,
        id: str
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get all AI function results for an ID.

        Args:
            dataset: Dataset name
            id: Item ID

        Returns:
            Dictionary mapping function names to results
        """
        if dataset not in self.function_map:
            raise ValueError(f"Invalid dataset: {dataset}")

        key_field = self.key_fields[dataset]
        results = {}

        for func in self.function_map[dataset]:
            table_name = f"{dataset}_{func}"
            cached = self._get_cached_result(table_name, key_field, id)
            results[func] = cached

        return results

    def clear_cache(
        self,
        dataset: str,
        func: Optional[str] = None,
        id: Optional[str] = None
    ) -> int:
        """Clear cached results.

        Args:
            dataset: Dataset name
            func: Optional function name (clear all if None)
            id: Optional ID (clear all if None)

        Returns:
            Number of records cleared
        """
        if dataset not in self.function_map:
            raise ValueError(f"Invalid dataset: {dataset}")

        key_field = self.key_fields[dataset]
        cleared = 0

        functions = [func] if func else list(self.function_map[dataset].keys())

        for function_name in functions:
            if func and function_name != func:
                continue

            table_name = f"{dataset}_{function_name}"

            if id:
                query = f"DELETE FROM {table_name} WHERE {key_field} = ?"
                cursor = self.db.execute(query, (id,))
            else:
                query = f"DELETE FROM {table_name}"
                cursor = self.db.execute(query)

            cleared += cursor.rowcount

        # APSW is in autocommit mode by default, no commit needed
        return cleared

# Global resolver instance
_resolver_instance = None

def get_resolver() -> FunctionResolver:
    """Get or create resolver instance."""
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = FunctionResolver()
    return _resolver_instance