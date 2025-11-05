"""Base DAO class for dataset access."""
import json
from typing import Any, Dict, List, Optional, Tuple

from dataset_config import get_dataset_config, DatasetConfig
from db import get_db
from services.resolver import get_resolver


class BaseDAO:
    """Base Data Access Object for datasets."""

    def __init__(self, dataset_name: str):
        """Initialize base DAO."""
        self.dataset_name = dataset_name
        self.config: DatasetConfig = get_dataset_config(dataset_name)
        self.key_field = self.config.key_field
        self.table_name = self.config.table
        self.db = get_db()
        self.resolver = get_resolver()

    # ------------------------------------------------------------------ helpers
    def _row_to_item(self, row: Tuple[Any, ...]) -> Dict[str, Any]:
        """Convert a raw database row into a serializable dictionary."""
        record = json.loads(row[5]) if row[5] else {}
        item: Dict[str, Any] = {
            self.key_field: row[0],
            "title": row[1],
            "category": row[2],
            "risk_theme": row[3],
            "risk_subtheme": row[4],
            "record": record,
            "ai_status": self._get_ai_presence(row[0]),
        }

        # Expose dataset-specific column names for convenience
        item[self.config.title_field] = record.get(self.config.title_field, row[1])
        if self.config.category_field:
            item[self.config.category_field] = record.get(self.config.category_field, row[2])
        item[self.config.theme_field] = record.get(self.config.theme_field, row[3])
        item[self.config.subtheme_field] = record.get(self.config.subtheme_field, row[4])

        return item

    def _get_ai_presence(self, id_value: str) -> Dict[str, bool]:
        """Return a mapping of AI function name -> availability."""
        status: Dict[str, bool] = {}

        for func in self.config.ai_functions:
            table = f"{self.dataset_name}_{func}"
            query = f"SELECT 1 FROM {table} WHERE {self.key_field} = ?"
            status[func] = bool(self.db.fetchone(query, (id_value,)))

        return status

    # ---------------------------------------------------------------- operations
    def search_by_id(self, id_value: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Search for items by ID or title."""
        search_pattern = f"%{id_value}%"
        query = f"""
            SELECT {self.key_field}, title, category, risk_theme, risk_subtheme, raw_data
            FROM {self.table_name}
            WHERE LOWER({self.key_field}) LIKE LOWER(?)
               OR LOWER(title) LIKE LOWER(?)
            ORDER BY {self.key_field}
            LIMIT ?
        """

        rows = self.db.fetchall(query, (search_pattern, search_pattern, limit))
        return [self._row_to_item(row) for row in rows]

    def list_all(self, offset: int = 0, limit: int = 100) -> Tuple[List[Dict[str, Any]], int]:
        """List all items with pagination."""
        count_query = f"SELECT COUNT(*) FROM {self.table_name}"
        total = self.db.fetchone(count_query)[0]

        query = f"""
            SELECT {self.key_field}, title, category, risk_theme, risk_subtheme, raw_data
            FROM {self.table_name}
            ORDER BY {self.key_field}
            LIMIT ? OFFSET ?
        """

        rows = self.db.fetchall(query, (limit, offset))
        return [self._row_to_item(row) for row in rows], total

    def get_details(self, id_value: str) -> Optional[Dict[str, Any]]:
        """Get full details for an item including AI results."""
        query = f"""
            SELECT {self.key_field}, title, category, risk_theme, risk_subtheme, raw_data
            FROM {self.table_name}
            WHERE {self.key_field} = ?
        """

        row = self.db.fetchone(query, (id_value,))
        if not row:
            return None

        record = json.loads(row[5]) if row[5] else {}

        ai_results = self.resolver.get_all_results(self.dataset_name, id_value)
        ai_payloads: Dict[str, Any] = {}
        for func in self.config.ai_functions:
            result = ai_results.get(func)
            ai_payloads[func] = result["payload"] if result else None

        raw_payload: Dict[str, Any] = {
            self.key_field: row[0],
            "title": row[1],
            "category": row[2],
            "risk_theme": row[3],
            "risk_subtheme": row[4],
            "record": record,
        }

        raw_payload[self.config.title_field] = record.get(self.config.title_field, row[1])
        if self.config.category_field:
            raw_payload[self.config.category_field] = record.get(self.config.category_field, row[2])
        raw_payload[self.config.theme_field] = record.get(self.config.theme_field, row[3])
        raw_payload[self.config.subtheme_field] = record.get(self.config.subtheme_field, row[4])

        return {
            "raw": raw_payload,
            "ai": ai_payloads,
        }

    def trigger_ai_function(
        self,
        id_value: str,
        function_name: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger an AI function for an item."""
        return self.resolver.resolve(
            dataset=self.dataset_name,
            func=function_name,
            id=id_value,
            description=description,
            refresh=refresh,
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        count_query = f"SELECT COUNT(*) FROM {self.table_name}"
        total = self.db.fetchone(count_query)[0]

        theme_query = f"""
            SELECT COALESCE(risk_theme, ''), COUNT(*)
            FROM {self.table_name}
            GROUP BY risk_theme
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """
        theme_rows = self.db.fetchall(theme_query)
        themes = [{"risk_theme": row[0], "count": row[1]} for row in theme_rows]

        subtheme_query = f"""
            SELECT COALESCE(risk_subtheme, ''), COUNT(*)
            FROM {self.table_name}
            GROUP BY risk_subtheme
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """
        subtheme_rows = self.db.fetchall(subtheme_query)
        subthemes = [{"risk_subtheme": row[0], "count": row[1]} for row in subtheme_rows]

        ai_coverage: Dict[str, Dict[str, Any]] = {}
        for func in self.config.ai_functions:
            table = f"{self.dataset_name}_{func}"
            query = f"SELECT COUNT(*) FROM {table}"
            try:
                count = self.db.fetchone(query)[0]
            except Exception:
                count = 0

            ai_coverage[func] = {
                "computed": count,
                "percentage": f"{(count / total * 100):.1f}%" if total > 0 else "0%",
            }

        return {
            "total_items": total,
            "risk_theme_top": themes,
            "risk_subtheme_top": subthemes,
            "ai_coverage": ai_coverage,
        }
