"""DAO for external loss dataset."""
from typing import Dict, Any, Optional
from dao.base import BaseDAO


class ExternalLossDAO(BaseDAO):
    """Data Access Object for external loss dataset."""

    def __init__(self):
        super().__init__(dataset_name="external_loss")

    def get_details(self, reference_id_code: str) -> Optional[Dict[str, Any]]:
        return super().get_details(reference_id_code)

    def trigger_issue_taxonomy(
        self,
        reference_id_code: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            reference_id_code,
            "issue_taxonomy",
            refresh,
        )

    def trigger_root_cause(
        self,
        reference_id_code: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            reference_id_code,
            "root_cause",
            refresh,
        )

    def trigger_enrichment(
        self,
        reference_id_code: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            reference_id_code,
            "enrichment",
            refresh,
        )
