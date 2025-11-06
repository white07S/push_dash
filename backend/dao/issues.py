"""DAO for issues dataset."""
from typing import Dict, Any, Optional
from dao.base import BaseDAO


class IssuesDAO(BaseDAO):
    """Data Access Object for issues dataset."""

    def __init__(self):
        super().__init__(dataset_name="issues")

    def get_details(self, issue_id: str) -> Optional[Dict[str, Any]]:
        return super().get_details(issue_id)

    def trigger_issue_taxonomy(
        self,
        issue_id: str,
        session_id: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            issue_id,
            "issue_taxonomy",
            session_id,
            refresh,
        )

    def trigger_root_cause(
        self,
        issue_id: str,
        session_id: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            issue_id,
            "root_cause",
            session_id,
            refresh,
        )

    def trigger_enrichment(
        self,
        issue_id: str,
        session_id: str,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        return self.trigger_ai_function(
            issue_id,
            "enrichment",
            session_id,
            refresh,
        )
