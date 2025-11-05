"""DAO for internal loss dataset."""
from typing import Dict, Any, Optional
from dao.base import BaseDAO


class InternalLossDAO(BaseDAO):
    """Data Access Object for internal loss dataset."""

    def __init__(self):
        super().__init__(dataset_name="internal_loss")

    def get_details(self, event_id: str) -> Optional[Dict[str, Any]]:
        return super().get_details(event_id)

    def trigger_issue_taxonomy(
        self,
        event_id: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            event_id,
            "issue_taxonomy",
            refresh,
        )

    def trigger_root_cause(
        self,
        event_id: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            event_id,
            "root_cause",
            refresh,
        )

    def trigger_enrichment(
        self,
        event_id: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            event_id,
            "enrichment",
            refresh,
        )
