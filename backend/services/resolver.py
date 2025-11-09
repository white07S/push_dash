"""Resolver utility for cache-or-compute pattern."""
import inspect
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from dataset_config import get_dataset_config
from db import get_db
from services import mock_ai
from services.llm_client import create_mock_llm_client

logger = logging.getLogger(__name__)


class FunctionResolver:
    """Resolve function results using cache-or-compute pattern."""

    def __init__(self, llm_client_factory=None):
        self.db = get_db()
        self._llm_client_factory = llm_client_factory or create_mock_llm_client
        self._llm_clients: Dict[Tuple[str, str], Any] = {}

        # Map dataset and function names to mock AI functions
        self.function_map: Dict[str, Dict[str, Any]] = {
            "controls": {
                "controls_taxonomy": mock_ai.get_controls_taxonomy,
                "root_cause": mock_ai.get_controls_root_cause,
                "enrichment": mock_ai.get_controls_enrichment,
                "slow_enrichment": mock_ai.get_delayed_enrichment,
            },
            "external_loss": {
                "issue_taxonomy": mock_ai.get_external_loss_taxonomy,
                "root_cause": mock_ai.get_external_loss_root_cause,
                "enrichment": mock_ai.get_external_loss_enrichment,
                "slow_enrichment": mock_ai.get_delayed_enrichment,
            },
            "internal_loss": {
                "issue_taxonomy": mock_ai.get_internal_loss_taxonomy,
                "root_cause": mock_ai.get_internal_loss_root_cause,
                "enrichment": mock_ai.get_internal_loss_enrichment,
                "slow_enrichment": mock_ai.get_delayed_enrichment,
            },
            "issues": {
                "issue_taxonomy": mock_ai.get_issues_taxonomy,
                "root_cause": mock_ai.get_issues_root_cause,
                "enrichment": mock_ai.get_issues_enrichment,
                "slow_enrichment": mock_ai.get_delayed_enrichment,
            },
        }

    # ------------------------------------------------------------------ helpers
    def _get_cached_result(
        self,
        table: str,
        key_field: str,
        id_value: str,
    ) -> Optional[Dict[str, Any]]:
        """Get cached result from database."""
        query = f"SELECT payload, created_at FROM {table} WHERE {key_field} = ?"
        result = self.db.fetchone(query, (id_value,))

        if result:
            payload, created_at = result
            return {
                "payload": json.loads(payload),
                "created_at": created_at,
            }
        return None

    def _store_result(
        self,
        table: str,
        key_field: str,
        id_value: str,
        payload: Any,
        created_at: str,
    ) -> None:
        """Store result in database."""
        query = f"""
            INSERT OR REPLACE INTO {table} ({key_field}, payload, created_at)
            VALUES (?, ?, ?)
        """
        self.db.execute(query, (id_value, json.dumps(payload), created_at))

    # ---------------------------------------------------------------- operations
    def get_llm_client(self, session_id: str, user_id: str) -> Any:
        """Return a cached LLM client instance for the session/user pair."""
        key = (session_id, user_id)
        if key not in self._llm_clients:
            self._llm_clients[key] = self._llm_client_factory(session_id=session_id, user_id=user_id)
        return self._llm_clients[key]

    def set_llm_client_factory(self, factory) -> None:
        """Override the LLM client factory and reset cached clients."""
        self._llm_client_factory = factory or create_mock_llm_client
        self._llm_clients.clear()

    async def resolve(
        self,
        dataset: str,
        func: str,
        id: str,
        session_id: str,
        user_id: str,
        refresh: bool = False,
        llm_client: Any | None = None,
    ) -> Dict[str, Any]:
        """Resolve function result using cache-or-compute pattern."""
        if dataset not in self.function_map:
            raise ValueError(f"Invalid dataset: {dataset}")

        if func not in self.function_map[dataset]:
            raise ValueError(f"Invalid function '{func}' for dataset '{dataset}'")

        config = get_dataset_config(dataset)
        key_field = config.key_field
        raw_query = f"""
            SELECT raw_data, title, category, risk_theme, risk_subtheme
            FROM {config.table}
            WHERE {key_field} = ?
        """
        raw_result = self.db.fetchone(raw_query, (id,))

        if not raw_result:
            raise ValueError(f"ID '{id}' not found in {dataset}")
        raw_data_json, title, category, risk_theme, risk_subtheme = raw_result

        if raw_data_json:
            raw_record = json.loads(raw_data_json)
        else:
            raw_record = {
                config.key_field: id,
                config.title_field: title,
                config.theme_field: risk_theme,
            }
            if config.category_field:
                raw_record[config.category_field] = category
            if config.subtheme_field:
                raw_record[config.subtheme_field] = risk_subtheme

        table_name = f"{dataset}_{func}"

        if not refresh:
            cached = self._get_cached_result(table_name, key_field, id)
            if cached:
                return {
                    "status": "ok",
                    "source": "cache",
                    "payload": cached["payload"],
                    "created_at": cached["created_at"],
                }

        compute_func = self.function_map[dataset][func]
        signature = inspect.signature(compute_func)
        kwargs: Dict[str, Any] = {}
        if "llm_client" in signature.parameters:
            kwargs["llm_client"] = llm_client or self.get_llm_client(session_id, user_id)

        try:
            payload = compute_func(id, session_id, user_id, raw_record, **kwargs)
            if inspect.isawaitable(payload):
                payload = await payload
        except Exception as exc:  # pragma: no cover - logging side-effect
            logger.error("Error computing %s for %s: %s", func, id, exc)
            raise RuntimeError(f"Failed to compute {func}: {exc}") from exc

        created_at = datetime.utcnow().isoformat() + "Z"
        self._store_result(table_name, key_field, id, payload, created_at)

        return {
            "status": "ok",
            "source": "computed",
            "payload": payload,
            "created_at": created_at,
        }

    def get_all_results(
        self,
        dataset: str,
        id: str
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get all AI function results for an ID."""
        if dataset not in self.function_map:
            raise ValueError(f"Invalid dataset: {dataset}")

        config = get_dataset_config(dataset)
        key_field = config.key_field
        results: Dict[str, Optional[Dict[str, Any]]] = {}

        for func in self.function_map[dataset]:
            table_name = f"{dataset}_{func}"
            results[func] = self._get_cached_result(table_name, key_field, id)

        return results

    def clear_cache(
        self,
        dataset: str,
        func: Optional[str] = None,
        id: Optional[str] = None
    ) -> int:
        """Clear cached results."""
        if dataset not in self.function_map:
            raise ValueError(f"Invalid dataset: {dataset}")

        config = get_dataset_config(dataset)
        key_field = config.key_field
        cleared = 0

        functions = [func] if func else list(self.function_map[dataset].keys())

        for function_name in functions:
            table_name = f"{dataset}_{function_name}"

            if id:
                query = f"DELETE FROM {table_name} WHERE {key_field} = ?"
                cursor = self.db.execute(query, (id,))
            else:
                query = f"DELETE FROM {table_name}"
                cursor = self.db.execute(query)

            cleared += cursor.rowcount

        return cleared


_resolver_instance: Optional[FunctionResolver] = None


def get_resolver() -> FunctionResolver:
    """Get or create resolver instance."""
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = FunctionResolver()
    return _resolver_instance
