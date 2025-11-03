"""DAO for issues dataset."""
from typing import Dict, Any, List, Optional
from dao.base import BaseDAO

class IssuesDAO(BaseDAO):
    """Data Access Object for issues dataset."""

    def __init__(self):
        """Initialize issues DAO."""
        super().__init__(dataset_name='issues', key_field='issue_id')

    def search_by_id(self, issue_id: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Search issues by ID."""
        results = super().search_by_id(issue_id, limit)
        # Rename 'id' to 'issue_id' for consistency
        for item in results:
            item['issue_id'] = item.pop('id')
        return results

    def get_details(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """Get full issue details including AI results."""
        return super().get_details(issue_id)

    def trigger_ai_taxonomy(
        self,
        issue_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI taxonomy generation for an issue."""
        return self.trigger_ai_function(
            issue_id,
            'ai_taxonomy',
            description,
            refresh
        )

    def trigger_ai_root_causes(
        self,
        issue_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI root cause analysis for an issue."""
        return self.trigger_ai_function(
            issue_id,
            'ai_root_causes',
            description,
            refresh
        )

    def trigger_ai_enrichment(
        self,
        issue_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger AI enrichment for an issue."""
        return self.trigger_ai_function(
            issue_id,
            'ai_enrichment',
            description,
            refresh
        )

    def trigger_similar_issues(
        self,
        issue_id: str,
        description: Optional[str] = None,
        refresh: bool = False
    ) -> Dict[str, Any]:
        """Trigger similar issues identification."""
        return self.trigger_ai_function(
            issue_id,
            'similar_issues',
            description,
            refresh
        )

    def list_all(self, offset: int = 0, limit: int = 100):
        """List all issues with pagination."""
        items, total = super().list_all(offset, limit)
        # Rename 'id' to 'issue_id' for consistency
        for item in items:
            item['issue_id'] = item.pop('id')
        return items, total

    def search_by_taxonomy(self, taxonomy_token: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search issues by taxonomy token."""
        results = super().search_by_taxonomy(taxonomy_token, limit)
        # Rename 'id' to 'issue_id' for consistency
        for item in results:
            item['issue_id'] = item.pop('id')
        return results